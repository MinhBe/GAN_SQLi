"""Generator policies for SeqGAN SQLi.

GeneratorLSTM            — 3-layer unidirectional LSTM (V1-V3)
GeneratorBiLSTMEncoder   — BiLSTM encoder + unidirectional LSTM decoder (V4)
    Teacher request: "3LSTM, BBI" = bidirectional context encoder.
    Decoder stays unidirectional so autoregressive generation remains valid.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple

from .utils import NUM_SQLI_TYPES


class GeneratorLSTM(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 128, hidden_dim: int = 512,
                 num_layers: int = 3, dropout: float = 0.2,
                 num_conditions: int = NUM_SQLI_TYPES, cond_embed_dim: int = None):
        super().__init__()
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_conditions = num_conditions
        if cond_embed_dim is None:
            cond_embed_dim = embed_dim
        self.cond_embed_dim = cond_embed_dim

        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.cond_embed = nn.Embedding(num_conditions, cond_embed_dim)

        lstm_input_dim = embed_dim + cond_embed_dim if cond_embed_dim != embed_dim else embed_dim
        self.lstm = nn.LSTM(lstm_input_dim, hidden_dim, num_layers,
                            batch_first=True, dropout=dropout if num_layers > 1 else 0.0)
        self.dropout = nn.Dropout(dropout)
        self.proj = nn.Linear(hidden_dim, vocab_size)

    def _merge_cond(self, x: torch.Tensor, cond: Optional[torch.Tensor]) -> torch.Tensor:
        if cond is None:
            return x
        cond_vec = self.cond_embed(cond).unsqueeze(1)  # (B, 1, E)
        if self.cond_embed_dim == x.size(-1):
            return x + cond_vec
        cond_vec = cond_vec.expand(-1, x.size(1), -1)
        return torch.cat([x, cond_vec], dim=-1)

    def forward(self, input_ids: torch.Tensor,
                hidden: Optional[Tuple] = None,
                cond: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, Tuple]:
        x = self.dropout(self.embed(input_ids))
        x = self._merge_cond(x, cond)
        out, hidden = self.lstm(x, hidden)
        logits = self.proj(self.dropout(out))
        return logits, hidden

    def init_hidden(self, batch_size: int, device: torch.device) -> Tuple:
        h = torch.zeros(self.num_layers, batch_size, self.hidden_dim, device=device)
        c = torch.zeros(self.num_layers, batch_size, self.hidden_dim, device=device)
        return h, c

    def sample(self, batch_size: int, max_len: int, device: torch.device,
               sos_id: int = 2, eos_id: int = 3,
               temperature: float = 1.0,
               cond: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Autoregressive sampling. Returns (token_ids, log_probs), both (B, T)."""
        hidden = self.init_hidden(batch_size, device)
        token = torch.full((batch_size, 1), sos_id, dtype=torch.long, device=device)
        tokens_list, logprob_list = [], []
        finished = torch.zeros(batch_size, dtype=torch.bool, device=device)

        for _ in range(max_len):
            logits, hidden = self.forward(token, hidden, cond)  # (B, 1, V)
            logits = logits[:, -1, :] / temperature
            log_probs = F.log_softmax(logits, dim=-1)
            probs = torch.exp(log_probs)
            next_token = torch.multinomial(probs, 1)  # (B, 1)
            step_logprob = log_probs.gather(1, next_token)  # (B, 1)

            finished = finished | (next_token.squeeze(1) == eos_id)
            tokens_list.append(next_token)
            logprob_list.append(step_logprob)
            token = next_token

            if finished.all():
                break

        tokens = torch.cat(tokens_list, dim=1)   # (B, T)
        logprobs = torch.cat(logprob_list, dim=1)  # (B, T)
        return tokens, logprobs

    def get_hidden_last(self, input_ids: torch.Tensor,
                        cond: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Return last hidden state for baseline input."""
        _, (h, _) = self.forward(input_ids, cond=cond)
        return h[-1]  # (B, hidden_dim)


class GeneratorBiLSTMEncoder(nn.Module):
    """BiLSTM context encoder + unidirectional LSTM decoder.

    Architecture (teacher request: 'BiLSTM'):
      - BiLSTM encoder: processes [type_embedding ⊕ SOS] → rich initial hidden state
      - LSTM decoder: autoregressive token-by-token generation (unidirectional)

    Why encoder-decoder instead of pure BiLSTM:
      - BiLSTM requires future tokens → cannot generate autoregressively
      - Encoder reads conditioning context (attack type), decoder generates tokens
      - Standard seq2seq approach that honors teacher's BiLSTM suggestion
    """

    def __init__(self, vocab_size: int, embed_dim: int = 128, hidden_dim: int = 512,
                 enc_layers: int = 2, dec_layers: int = 2, dropout: float = 0.2,
                 num_conditions: int = NUM_SQLI_TYPES, cond_embed_dim: int = 64):
        super().__init__()
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        self.dec_layers = dec_layers
        self.num_conditions = num_conditions
        self.cond_embed_dim = cond_embed_dim

        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.cond_embed = nn.Embedding(num_conditions, cond_embed_dim)
        self.dropout = nn.Dropout(dropout)

        # BiLSTM Encoder: processes [SOS_embed ⊕ type_embed] to produce context
        enc_input_size = embed_dim + cond_embed_dim
        self.encoder = nn.LSTM(
            input_size=enc_input_size,
            hidden_size=hidden_dim // 2,   # bidirectional → hidden_dim total
            num_layers=enc_layers,
            bidirectional=True,
            batch_first=True,
            dropout=dropout if enc_layers > 1 else 0.0,
        )
        self.enc_layers = enc_layers

        # Project encoder final state → decoder initial state
        self.enc_to_dec_h = nn.Linear(hidden_dim, hidden_dim)
        self.enc_to_dec_c = nn.Linear(hidden_dim, hidden_dim)

        # Unidirectional LSTM Decoder
        self.decoder = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=dec_layers,
            batch_first=True,
            dropout=dropout if dec_layers > 1 else 0.0,
        )
        self.proj = nn.Linear(hidden_dim, vocab_size)

    # ------------------------------------------------------------------
    def _encode_context(self, cond: Optional[torch.Tensor],
                        batch_size: int, device: torch.device) -> Tuple:
        """BiLSTM encode [SOS ⊕ type_embed] → decoder initial (h, c)."""
        sos_emb = self.embed(
            torch.full((batch_size, 1), 2, dtype=torch.long, device=device)  # sos_id=2
        )                                                                       # (B, 1, embed_dim)

        if cond is not None:
            cond_vec = self.cond_embed(cond).unsqueeze(1)  # (B, 1, cond_embed_dim)
            enc_input = torch.cat([sos_emb, cond_vec], dim=-1)  # (B, 1, embed+cond)
        else:
            # No conditioning: pad with zeros
            pad_c = torch.zeros(batch_size, 1, self.cond_embed_dim, device=device)
            enc_input = torch.cat([sos_emb, pad_c], dim=-1)

        _, (h_enc, c_enc) = self.encoder(enc_input)
        # h_enc: (2*enc_layers, B, hidden_dim//2)
        # Take last encoder layer: concat forward ([-2]) + backward ([-1])
        h_last = torch.cat([h_enc[-2], h_enc[-1]], dim=-1)  # (B, hidden_dim)
        c_last = torch.cat([c_enc[-2], c_enc[-1]], dim=-1)

        # Project and expand to dec_layers
        dec_h = self.enc_to_dec_h(h_last)  # (B, hidden_dim)
        dec_c = self.enc_to_dec_c(c_last)
        dec_h = dec_h.unsqueeze(0).expand(self.dec_layers, -1, -1).contiguous()
        dec_c = dec_c.unsqueeze(0).expand(self.dec_layers, -1, -1).contiguous()
        return dec_h, dec_c

    def init_hidden(self, batch_size: int, device: torch.device,
                    cond: Optional[torch.Tensor] = None) -> Tuple:
        """Initialize decoder hidden via BiLSTM encoder. If cond=None, zeros."""
        if cond is not None:
            return self._encode_context(cond, batch_size, device)
        h = torch.zeros(self.dec_layers, batch_size, self.hidden_dim, device=device)
        c = torch.zeros(self.dec_layers, batch_size, self.hidden_dim, device=device)
        return h, c

    def forward(self, input_ids: torch.Tensor,
                hidden: Optional[Tuple] = None,
                cond: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, Tuple]:
        """Decoder forward pass. If hidden=None and cond provided, encode context first."""
        x = self.dropout(self.embed(input_ids))  # (B, T, embed_dim)
        if hidden is None:
            hidden = self._encode_context(cond, input_ids.size(0), input_ids.device)
        out, new_hidden = self.decoder(x, hidden)
        logits = self.proj(self.dropout(out))   # (B, T, vocab_size)
        return logits, new_hidden

    def sample(self, batch_size: int, max_len: int, device: torch.device,
               sos_id: int = 2, eos_id: int = 3,
               temperature: float = 1.0,
               cond: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Autoregressive sampling. Returns (token_ids, log_probs), both (B, T)."""
        hidden = self._encode_context(cond, batch_size, device) if cond is not None \
            else self.init_hidden(batch_size, device)
        token = torch.full((batch_size, 1), sos_id, dtype=torch.long, device=device)
        tokens_list, logprob_list = [], []
        finished = torch.zeros(batch_size, dtype=torch.bool, device=device)

        for _ in range(max_len):
            logits, hidden = self.forward(token, hidden, cond=None)  # cond already in hidden
            logits = logits[:, -1, :] / max(temperature, 1e-6)
            log_probs = F.log_softmax(logits, dim=-1)
            probs = torch.exp(log_probs)
            next_token = torch.multinomial(probs, 1)
            step_logprob = log_probs.gather(1, next_token)

            finished = finished | (next_token.squeeze(1) == eos_id)
            tokens_list.append(next_token)
            logprob_list.append(step_logprob)
            token = next_token

            if finished.all():
                break

        tokens = torch.cat(tokens_list, dim=1)
        logprobs = torch.cat(logprob_list, dim=1)
        return tokens, logprobs

    def get_hidden_last(self, input_ids: torch.Tensor,
                        cond: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Return last decoder hidden state for baseline input."""
        _, (h, _) = self.forward(input_ids, cond=cond)
        return h[-1]  # (B, hidden_dim)
