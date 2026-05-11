"""SQL-aware tokenizer with aggressive de-lexicalization for SeqGAN."""
import re
import json
from typing import List, Dict, Optional

PAD, UNK, SOS, EOS = '<PAD>', '<UNK>', '<SOS>', '<EOS>'
SPECIAL_TOKENS = [PAD, UNK, SOS, EOS]

# De-lex placeholder tokens
DELEX_TOKENS = {'__STR__', '__INT__', '__HEX__', '__FLOAT__', '__TIME__',
                '__TABLE__', '__COL__', '__DB__', '__FUNC__', '__IDENT__'}

SQL_KEYWORDS = {
    'select', 'from', 'where', 'and', 'or', 'not', 'null', 'is', 'in',
    'like', 'between', 'exists', 'union', 'all', 'distinct', 'insert',
    'into', 'values', 'update', 'set', 'delete', 'drop', 'create', 'alter',
    'table', 'index', 'view', 'database', 'schema', 'if', 'else', 'then',
    'case', 'when', 'end', 'as', 'join', 'inner', 'outer', 'left', 'right',
    'full', 'cross', 'on', 'having', 'group', 'by', 'order', 'asc', 'desc',
    'limit', 'offset', 'top', 'rownum', 'count', 'sum', 'avg', 'min', 'max',
    'substring', 'substr', 'length', 'len', 'upper', 'lower', 'concat',
    'char', 'ascii', 'hex', 'unhex', 'md5', 'sha1', 'sleep', 'benchmark',
    'load_file', 'outfile', 'dumpfile', 'version', 'user', 'exec', 'execute',
    'waitfor', 'delay', 'true', 'false', 'cast', 'convert', 'coalesce',
    'nullif', 'isnull', 'ifnull', 'nvl', 'decode', 'chr', 'char_length',
    'trim', 'ltrim', 'rtrim', 'replace', 'reverse', 'repeat', 'lpad', 'rpad',
    'floor', 'ceil', 'ceiling', 'round', 'abs', 'mod', 'power', 'sqrt',
    'now', 'sysdate', 'getdate', 'current_date', 'current_timestamp',
    'dual', 'null', 'rows', 'fetch', 'first', 'next', 'only',
}

# Structural/operator tokens kept as-is
OPERATOR_TOKENS = {
    '=', '<', '>', '!', '+', '-', '*', '/', '%', '|', '&', '^', '~',
    '(', ')', ',', ';', '.', '||', '&&', '!=', '<>', '<=', '>=',
    '--', '#', '/*', '*/', "'", '"', '\\',
}

# All tokens we keep without replacing
KEEP_TOKENS = SQL_KEYWORDS | OPERATOR_TOKENS | DELEX_TOKENS


def _split_on_operators(text: str) -> str:
    """Add spaces around SQL operators to ensure proper tokenization."""
    # Order matters: multi-char ops before single-char
    text = re.sub(r'\|\|', ' || ', text)
    text = re.sub(r'&&', ' && ', text)
    text = re.sub(r'!=', ' != ', text)
    text = re.sub(r'<>', ' <> ', text)
    text = re.sub(r'<=', ' <= ', text)
    text = re.sub(r'>=', ' >= ', text)
    text = re.sub(r'/\*', ' /* ', text)
    text = re.sub(r'\*/', ' */ ', text)
    text = re.sub(r'--', ' -- ', text)
    text = re.sub(r'([=<>!+\-*/%|&^~(),;])', r' \1 ', text)
    return text


def delex(text: str) -> str:
    """Aggressively de-lexicalize a SQL payload to a small fixed vocabulary."""
    result = text.lower().strip()

    # Preserve __TIME__ already in dataset
    result = re.sub(r'__time__', ' __TIME__ ', result, flags=re.IGNORECASE)

    # Step 1: replace quoted strings (must come before operator splitting to avoid quote confusion)
    result = re.sub(r"'[^']*'", ' __STR__ ', result)
    result = re.sub(r'"[^"]*"', ' __STR__ ', result)

    # Step 2: split on operators to separate e.g. ||chr( into || chr (
    result = _split_on_operators(result)

    # Step 3: normalize whitespace
    result = re.sub(r'\s+', ' ', result).strip()

    # Step 4: replace numbers/hex on clean tokens
    tokens = result.split()
    out = []
    for tok in tokens:
        if tok in KEEP_TOKENS:
            out.append(tok)
            continue
        # Replace hex
        if re.fullmatch(r'0x[0-9a-fA-F]+', tok):
            out.append('__HEX__')
            continue
        # Replace floats
        if re.fullmatch(r'\d+\.\d+', tok):
            out.append('__FLOAT__')
            continue
        # Replace pure integers
        if re.fullmatch(r'\d+', tok):
            out.append('__INT__')
            continue
        # Replace mixed tokens containing only digits after stripping non-alnum
        stripped = re.sub(r'[^a-z0-9]', '', tok)
        if stripped.isdigit():
            out.append('__INT__')
            continue
        # Pure alphabetic: check if SQL keyword
        alpha = re.sub(r'[^a-z]', '', tok)
        if alpha in SQL_KEYWORDS:
            out.append(alpha)
            continue
        # Starts with __ (already a de-lex placeholder)
        if tok.startswith('__') and tok.endswith('__'):
            out.append(tok)
            continue
        # Everything else: unknown identifier
        out.append('__IDENT__')

    return ' '.join(out)


def _word_tokenize(text: str) -> List[str]:
    """Split text into tokens, keeping multi-char operators together."""
    text = re.sub(r'\s+', ' ', text).strip()
    return text.split() if text else []


class SQLTokenizer:
    def __init__(self, vocab: Optional[Dict[str, int]] = None):
        self.token2id: Dict[str, int] = {}
        self.id2token: Dict[int, str] = {}
        if vocab is not None:
            self.token2id = vocab
            self.id2token = {v: k for k, v in vocab.items()}

    @property
    def vocab_size(self) -> int:
        return len(self.token2id)

    @property
    def pad_id(self) -> int:
        return self.token2id[PAD]

    @property
    def unk_id(self) -> int:
        return self.token2id[UNK]

    @property
    def sos_id(self) -> int:
        return self.token2id[SOS]

    @property
    def eos_id(self) -> int:
        return self.token2id[EOS]

    def build_vocab(self, texts: List[str], min_freq: int = 1) -> None:
        from collections import Counter
        counter: Counter = Counter()
        for text in texts:
            counter.update(_word_tokenize(text))
        self.token2id = {t: i for i, t in enumerate(SPECIAL_TOKENS)}
        idx = len(SPECIAL_TOKENS)
        for token, freq in counter.most_common():
            if freq >= min_freq:
                self.token2id[token] = idx
                idx += 1
        self.id2token = {v: k for k, v in self.token2id.items()}

    def encode(self, text: str, add_sos: bool = True, add_eos: bool = True) -> List[int]:
        tokens = _word_tokenize(text)
        ids = [self.token2id.get(t, self.unk_id) for t in tokens]
        if add_sos:
            ids = [self.sos_id] + ids
        if add_eos:
            ids = ids + [self.eos_id]
        return ids

    def decode(self, ids: List[int], skip_special: bool = True) -> str:
        special = {self.pad_id, self.sos_id, self.eos_id} if skip_special else set()
        tokens = [self.id2token.get(i, UNK) for i in ids if i not in special]
        return ' '.join(tokens)

    def save(self, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.token2id, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> 'SQLTokenizer':
        with open(path, 'r', encoding='utf-8') as f:
            vocab = json.load(f)
        return cls(vocab)
