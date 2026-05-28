# Regional GAN/SQLi Literature Scan: Japan, Korea, India, Singapore, Europe

Date searched: 2026-05-24

Scope: follow-up scan for GAN, SQL injection, WAF/adversarial SQLi, RL SQLi, Text2SQL/LLM SQLi, and GAN-based cybersecurity outside the China-focused scan.

## Japan

Japan has relevant SQLi testing and analysis work, but I did not find a strong direct GAN+SQLi paper in this pass.

| Priority | Paper / Item | Why it matters | Link |
|---|---|---|---|
| High | `Generating Effective Attacks for Efficient and Precise Penetration Testing against SQL Injection` | Dynamic SQLi attack generation; useful pre-GAN payload-generation baseline. | https://www.jstage.jst.go.jp/article/ipsjtrans/4/0/4_0_43/_article/-char/ja/ |
| Medium-high | `SQL Injection Attack Phase Identification without Relying on Internal Information of Attack Targets` | SQLi attack-phase taxonomy/analysis for WAF logs and operational security. | https://cir.nii.ac.jp/crid/1390853651758714112 |
| Medium | `Detection of SQL Injection Vulnerability in Embedded SQL` | Program-analysis defense for embedded SQL in C/C++; indexed in Japanese venue. | https://www.jstage.jst.go.jp/article/transinf/E103.D/5/E103.D_2019EDL8143/_article |

## Korea

Korea has useful SQLi detection and GAN-for-cybersecurity/IDS papers. Direct GAN+SQLi payload generation was not obvious in this quick scan.

| Priority | Paper / Item | Why it matters | Link |
|---|---|---|---|
| High | `Data-mining based SQL injection attack detection using internal query trees` | Strong database-level SQLi detection baseline using internal query trees and SVM. | https://pure.korea.ac.kr/en/publications/data-mining-based-sql-injection-attack-detection-using-internal-q/ |
| Medium-high | `Two-Stage SQL Injection Detection Method Using Pattern Matching and Machine Learning` | Recent Korean SQLi detector combining pattern matching and ML. | https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART003297702 |
| Medium | `A Model Training Method for DDoS Detection Using CTGAN under 5GC Traffic` | Korean CTGAN cybersecurity/traffic augmentation; not SQLi-specific. | https://www.techscience.com/csse/v47n1/53041 |
| Medium-low | `Secure Coding for SQL Injection Prevention Using Generative AI` | Generative-AI secure coding angle; probably supporting rather than core. | https://journal.kci.go.kr/jksci/archive/articlePdf?artiId=ART003120945 |

## India

India has many SQLi detection papers and broad GAN cybersecurity surveys. I found fewer high-signal direct GAN+SQLi papers than China/Vietnam/Europe.

| Priority | Paper / Item | Why it matters | Link |
|---|---|---|---|
| High | `A Review of Generative Adversarial Networks for Security Applications` | India-origin GAN-for-cybersecurity survey; useful for global framing. | https://ph.pollub.pl/index.php/iapgos/article/view/5778 |
| Medium-high | `Generative Adversarial Networks based Approach for Intrusion Detection System` | GAN-assisted IDS; broader than SQLi. | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4295908 |
| Medium | `An early malware threat detection model using Conditional Tabular GAN` | CTGAN for cybersecurity data scarcity; broader than SQLi. | https://www.amrita.edu/publication/an-early-malware-threat-detection-model-using-conditional-tabular-generative-adversarial-network/ |
| Medium | `Securing web applications against XSS and SQLi attacks using a novel deep learning approach` | Strong DL SQLi/XSS detector; already in local PDF set. | https://www.nature.com/articles/s41598-023-48845-4 |

## Singapore

Singapore’s strongest related work is high-quality program analysis for SQLi/XSS rather than GAN+SQLi.

| Priority | Paper / Item | Why it matters | Link |
|---|---|---|---|
| High | `Mining SQL Injection and Cross Site Scripting Vulnerabilities using Hybrid Program Analysis` | Strong SQLi/XSS vulnerability-mining baseline; NTU + Luxembourg. | https://orbilu.uni.lu/handle/10993/1070 |
| High | `An integrated approach for effective injection vulnerability analysis of web applications through security slicing and hybrid constraint solving` | Strong injection vulnerability analysis; SMU + Luxembourg. | https://ink.library.smu.edu.sg/sis_research/4892 |

## Europe

Europe is very strong in adversarial SQLi/WAF, RL SQLi, and robust WAF learning.

| Priority | Paper / Item | Country / signal | Why it matters | Link |
|---|---|---|---|---|
| Very high | `ModSec-AdvLearn: Countering Adversarial SQL Injections with Robust Machine Learning` | France/Italy/Europe, EURECOM + Cagliari/Genova/Sapienza | Robust WAF learning and adversarial training for SQLi. | https://www.eurecom.eu/publication/8288/download/sec-publi-8288.pdf |
| Very high | `WAF-A-MoLE: Evading Web Application Firewalls through Adversarial Machine Learning` | Italy/Europe | Core adversarial SQLi/WAF evasion baseline; already in local corpus. | https://arxiv.org/abs/2001.01952 |
| High | `SQIRL: Grey-Box Detection of SQL Injection Vulnerabilities Using Reinforcement Learning` | Imperial College London | Strong RL SQLi vulnerability detection; useful comparator for generated payload/fuzzing. | https://www.usenix.org/conference/usenixsecurity23/presentation/al-wahaibi |
| High | `Simulating all archetypes of SQL injection vulnerability exploitation using reinforcement learning agents` | Europe/Norway signal | RL agents across SQLi archetypes; useful AI-era SQLi baseline. | https://link.springer.com/article/10.1007/s10207-023-00738-3 |
| High | `Prompt-to-SQL Injections in LLM-Integrated Web Applications` | Portugal, INESC-ID / IST | LLM/Text2SQL SQLi risk and defense; already downloaded. | https://syssec.dpss.inesc-id.pt/papers/pedro_icse25.pdf |
| Medium-high | `Combinatorial methods for dynamic gray-box SQL injection testing` | Austria, Salzburg University of Applied Sciences | Dynamic SQLi testing with attack grammars; strong pre-LLM/pre-GAN baseline. | https://pure.fh-salzburg.ac.at/en/publications/combinatorial-methods-for-dynamic-gray-box-sql-injection-testing/ |
| Medium-high | `SQL injection attack detection in network flow data` | Europe-linked open article | Flow-level SQLi detection; useful if evaluating network traces rather than only payload text. | https://www.sciencedirect.com/science/article/pii/S0167404823000032 |
| Medium | `Evolutionary Multi-Task Injection Testing on Web Application Firewalls` | Europe-linked arXiv | WAF fuzzing/generation across multiple injection classes. | https://arxiv.org/abs/2206.05743 |
| Medium | `Evaluating Prompt Injection Attacks with LSTM-Based GANs` | Spain, Comillas | Not SQLi, but useful if connecting prompt injection and sequence GANs. | https://www.iit.comillas.edu/publicacion/revista/es/2729/Evaluating_Prompt_Injection_Attacks_with_LSTM-Based_Generative_Adversarial_Networks%3A_A_Lightweight_Alternative_to_Large_Language_Models |

## Practical Next Download Priority

1. Europe: `ModSec-AdvLearn`, `SQIRL`, `RL SQLi archetypes`, Salzburg gray-box SQLi testing.
2. Singapore: NTU/Luxembourg hybrid program analysis and SMU/Luxembourg security slicing.
3. Japan: Sania SQLi attack generation and SQLi phase identification.
4. Korea: internal query-tree SQLi detection and two-stage SQLi detection.
5. India: one GAN-cybersecurity survey if global framing is needed.

## Takeaway

- Japan, Korea, and Singapore are valuable mainly for classical/software-security SQLi analysis and detection baselines.
- India is useful for broad GAN-in-cybersecurity framing and SQLi/XSS DL detection.
- Europe is the strongest target for more downloads because it directly complements the current corpus with adversarial SQLi/WAF and RL-based SQLi work.

