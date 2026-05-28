# Additional GAN and SQL Injection Literature Search

Date searched: 2026-05-24

Scope: papers not obviously present in `Asset/Total_OCR1` by filename. I prioritized papers that are useful for a GAN-SQLi thesis/project: SQLi payload generation, adversarial SQLi/WAF evasion, SQLi detection with ML/DL, and missing GAN/text-GAN foundations.

## Highest Priority Additions

| # | Paper | Year | Why it matters | Link |
|---|---:|---:|---|---|
| 1 | AdvSQLi: Generating Adversarial SQL Injections against Real-world WAF-as-a-service | 2024 | Very relevant to adversarial SQLi payload generation and WAF evaluation. Uses tree representation, grammar mutation, and search rather than GAN, so it is a strong non-GAN baseline/comparator. | https://arxiv.org/abs/2401.02615 |
| 2 | SSQLi: A Black-Box Adversarial Attack Method for SQL Injection Based on Reinforcement Learning | 2023 | Strong RL baseline for SQLi detector/WAF evasion; useful to compare against GAN/RL-style payload mutation. | https://www.mdpi.com/1999-5903/15/4/133 |
| 3 | DeepSQLi: Deep Semantic Learning for Testing SQL Injection | 2020 | Generates SQLi test cases using deep NLP; important bridge between SQLi fuzzing and neural sequence generation. | https://arxiv.org/abs/2005.11728 |
| 4 | Generative Adversarial Network (GAN)-Based Autonomous Penetration Testing for Web Applications | 2023 | Directly uses GAN/CGAN for web attack payload generation and WAF testing. Focuses more on XSS but discusses SQLi-relevant WAF behavior and future expansion. | https://www.mdpi.com/1424-8220/23/18/8014 |
| 5 | Enhancing SQL Injection Detection and Prevention Using Generative Models | 2025 | Recent arXiv work on generative models for SQLi detection/prevention; potentially useful as current related work. | https://arxiv.org/abs/2502.04786 |
| 6 | Adversarial SQL Injection Generation with LLM-Based Architectures | 2026 | Very recent LLM-based SQLi generation paper; useful for positioning GAN work against current LLM approaches. | https://arxiv.org/abs/2605.11188 |
| 7 | AIA: Autoregression-Based Injection Attacks Against Text2SQL Models | 2025 | Related injection/SQL security angle for Text2SQL systems; not classic SQLi, but relevant if discussing modern SQL-generating systems. | https://ojs.aaai.org/index.php/AAAI/article/view/34009 |

## SQLi Detection, Testing, and Survey Papers

| # | Paper | Year | Why it matters | Link |
|---|---:|---:|---|---|
| 8 | Deep Learning-Based Detection Technology for SQL Injection Research and Implementation | 2023 | TextCNN/LSTM/attention SQLi detection model; useful detector baseline for generated payload evaluation. | https://www.mdpi.com/2076-3417/13/16/9466 |
| 9 | Deep Learning Architecture for Detecting SQL Injection Attacks Based on RNN Autoencoder Model | 2023 | Autoencoder-based SQLi detector; useful anomaly-detection baseline. | https://www.mdpi.com/2227-7390/11/15/3286 |
| 10 | A deep learning approach based on multi-view consensus for SQL injection detection | 2024 | Multi-view BiLSTM-CNN detection architecture; useful for modern detector comparison. | https://link.springer.com/article/10.1007/s10207-023-00791-y |
| 11 | Detecting Structured Query Language Injections in Web Microservices Using Machine Learning | 2024 | Applied ML SQLi detection in microservices; useful deployment-oriented related work. | https://www.mdpi.com/2227-9709/11/2/15 |
| 12 | Securing web applications against XSS and SQLi attacks using a novel deep learning approach | 2024 | Joint XSS/SQLi detection; useful if using mixed web-attack datasets. | https://www.nature.com/articles/s41598-023-48845-4 |
| 13 | Detection of SQL Injection Attack Using Machine Learning Techniques: A Systematic Literature Review | 2022 | SLR of ML SQLi detection; useful for taxonomy and references. | https://www.mdpi.com/2624-800X/2/4/39 |
| 14 | SQL injection attacks - a systematic review | 2019 | Broader SQLi taxonomy and prevention review. | https://www.inderscience.com/info/inarticle.php?artid=101937 |
| 15 | A novel method for SQL injection attack detection based on removing SQL query attribute values | 2012 | Classical structure-based SQLi detection; useful as non-neural baseline context. | https://www.sciencedirect.com/science/article/pii/S0895717711000689 |
| 16 | Detection and Prevention of SQL Injection Attacks | 2007 | Foundational survey chapter covering classic methods such as AMNESIA. | https://viterbi-web.usc.edu/~halfond/papers/halfond07springer.pdf |
| 17 | pSigene: Webcrawling to Generalize SQL Injection Signatures | 2014 | Signature generalization for SQLi; useful as a classical WAF/signature-generation baseline. | https://engineering.purdue.edu/dcsl/publications/papers/2014/psigene_dsn14.pdf |

## Missing GAN/Text-GAN Foundations Worth Adding

| # | Paper | Year | Why it matters | Link |
|---|---:|---:|---|---|
| 18 | Conditional Generative Adversarial Nets | 2014 | Core CGAN paper; important because SQLi generation papers often condition on labels/classes. | https://arxiv.org/abs/1411.1784 |
| 19 | Unsupervised Representation Learning with Deep Convolutional Generative Adversarial Networks | 2015 | DCGAN foundation; relevant because Lu et al. use DCGAN-style ideas for SQLi sample generation. | https://arxiv.org/abs/1511.06434 |
| 20 | MaliGAN: Maximum-Likelihood Augmented Discrete Generative Adversarial Networks | 2017 | Important discrete-sequence GAN method; useful for text/payload generation discussion. | https://arxiv.org/abs/1702.07983 |
| 21 | RankGAN: A Maximum Margin Ranking GAN for Generating Language Descriptions | 2017 | Text GAN with ranking discriminator; useful related work for discrete payload generation. | https://arxiv.org/abs/1705.11001 |
| 22 | Adversarial Discrete Sequence Generation without Explicit Neural Networks as Discriminators | 2019 | Discrete sequence generation alternative; useful for discussing GAN instability/discrete-token issues. | https://proceedings.mlr.press/v89/li19g.html |
| 23 | Adversarial Feature Matching for Text Generation | 2017 | TextGAN-style feature matching; useful for text generation baseline discussion. | https://arxiv.org/abs/1706.03850 |
| 24 | Professor Forcing: A New Algorithm for Training Recurrent Networks | 2016 | Adversarial training for sequence models; relevant to sequence distribution matching even though not SQLi-specific. | https://arxiv.org/abs/1610.09038 |

## Notes on Already-Covered or Likely Duplicate Items

The existing OCR set already appears to include these important anchors, so I did not list them as additions: Goodfellow 2014 GAN, Arjovsky 2017 WGAN, Gulrajani 2017 WGAN-GP, Yu 2017 SeqGAN, Guo 2018 LeakGAN, Fedus 2018 MaskGAN, Nie 2019 RelGAN, Xu 2019 CTGAN, Lu 2022 GAN-SQLi, Lu 2022 GA-WGAN-SQLi, Le 2024 GSQLi, Demetrio 2020 WAF-A-MoLE, Lin 2018 IDSGAN, Jang 2017 Gumbel-Softmax, Maddison 2017 Concrete distribution, and Williams 1992 REINFORCE.

## Suggested Next Download/OCR Order

1. `AdvSQLi_2024`
2. `SSQLi_2023`
3. `DeepSQLi_2020`
4. `Chowdhary_2023_GAN_Pentesting` if the current OCR is incomplete, otherwise skip
5. `Tadhani_2024_SQLi_XSS_DL`
6. `Sun_2023_SQLi_TextCNN_LSTM_Attention`
7. `Radford_2015_DCGAN`
8. `Mirza_2014_CGAN`
9. `MaliGAN_2017`
10. `RankGAN_2017`

