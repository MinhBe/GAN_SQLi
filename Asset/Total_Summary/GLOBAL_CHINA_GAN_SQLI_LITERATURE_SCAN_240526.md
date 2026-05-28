# Global and China GAN/SQLi Literature Scan

Date searched: 2026-05-24

Scope: quick scan for scientific papers outside the current local corpus, with emphasis on China and then other countries. Focus is on GAN, SQL injection, WAF/adversarial payloads, Text2SQL/LLM-era SQLi, and GAN-based cybersecurity.

## China: High-Value Findings

China has a strong cluster around SQLi adversarial generation, Text2SQL injection, and GAN-assisted SQLi detection.

| Priority | Paper | Country / Institution Signal | Why it matters | Status in local PDF set |
|---|---|---|---|---|
| Very high | `AdvSQLi: Generating Adversarial SQL Injections against Real-world WAF-as-a-service` | China; Zhejiang University/NESA publication page lists the work; authors include Zhenqing Qu, Xiang Ling, Ting Wang, Xiang Chen, Shouling Ji, Chunming Wu. | Strong adversarial SQLi/WAF-as-a-service benchmark. Not GAN, but a core non-GAN baseline for payload mutation and WAF evasion. | Already downloaded as `Qu_2024_AdvSQLi.pdf`. |
| Very high | `AIA: Autoregression-Based Injection Attacks Against Text2SQL Models` | China/US collaboration; AAAI page lists Zhejiang University, Institute of Software CAS, and Stony Brook University. | Important AI-era SQLi paper for Text2SQL models; evaluates adversarial inputs that cause Text2SQL models to emit target attack payloads. | Already downloaded as `Li_2025_AIA_Text2SQL_Injection.pdf`. |
| High | `SSQLi: A Black-Box Adversarial Attack Method for SQL Injection Based on Reinforcement Learning` | China; School of Cyber Science and Engineering, Sichuan University. | RL-based black-box adversarial SQLi generator; useful comparator against GAN/LLM payload generation. | Already downloaded as `Guan_2023_SSQLi_RL.pdf`. |
| High | `A GAN-based Method for Generating SQL Injection Attack Samples` | China; IEEE ITAIC 2022, Chongqing, China; authors Lu, Fei, Liu, Li. | Direct GAN-based SQLi sample generation. This is one of the most direct bridges between GAN and SQL injection. | Already present in `Total_PDF1` as `Lu_2022_GAN_SQLi.pdf`; OCR exists. |
| High | `Research on SQL injection attacks detection method based on BERT-GAN` / `基于BERT-GAN的SQL注入攻击检测方法研究` | China; Chinese-language journal page lists LUO Yiming, TAN Yubo, LI Jianping. | Direct Chinese paper using BERT + GAN for SQLi detection; useful because it is not just English-language IEEE/arXiv material. | Not yet in local PDF set. PDF preview found. |
| Medium-high | `CTTGAN: Traffic Data Synthesizing Scheme Based on Conditional GAN` | China; National University of Defense Technology, Hefei. | GAN/CTGAN for imbalanced traffic synthesis; includes CIC-IDS2017 where Web Attack SQL Injection is a minority class. Broader IDS rather than payload-level SQLi. | Not yet in local PDF set. |

Useful Chinese-language/China links:

- BERT-GAN SQLi page: https://www.spacejournal.cn/cn/article/id/59361be7-e3c0-458c-80b8-270677b739a4
- BERT-GAN PDF preview: https://mc.spacejournal.cn/cn/article/pdf/preview/10.19304/J.ISSN1000-7180.2023.0721.pdf
- AdvSQLi arXiv: https://arxiv.org/abs/2401.02615
- AIA AAAI page: https://ojs.aaai.org/index.php/AAAI/article/view/34009
- SSQLi MDPI page: https://www.mdpi.com/1999-5903/15/4/133
- CTTGAN MDPI page: https://www.mdpi.com/1424-8220/22/14/5243

## Vietnam

| Priority | Paper | Institution signal | Why it matters | Status |
|---|---|---|---|---|
| Very high | `GSQLi: A GAN-based Approach for Adversarial SQL Injection Sample Generation against WAF` | Vietnam National University Ho Chi Minh City, University of Information Technology. | Direct GAN-based adversarial SQLi sample generation against WAF/detectors; very aligned with the project. | Already present as `Le_2024_GSQLi.pdf` in `Total_PDF1`; should remain a central related-work anchor. |

Links:

- UIT lab page: https://inseclab.uit.edu.vn/gsqli-a-gan-based-approach-for-adversarial-sql-injection-sample-generation-against-waf/
- J-GLOBAL metadata: https://jglobal.jst.go.jp/en/detail?JGLOBAL_ID=202502253379913897

## United States

| Priority | Paper | Institution signal | Why it matters | Status |
|---|---|---|---|---|
| High | `Generative Adversarial Network (GAN)-Based Autonomous Penetration Testing for Web Applications` | Arizona State University; PubMed also lists 6sense Insights and ASU affiliations. | GAN/CGAN for web attack payload generation and WAF testing. More XSS-heavy but useful for autonomous pentesting framing. | Already downloaded as `Chowdhary_2023_GAN_Autonomous_Pentesting.pdf`; related `Chowdhary_2023_GAN_Pentesting.pdf` exists in `Total_PDF1`. |
| High | Classical SQLi defenses: `SQLrand`, `SQLCHECK`, `CANDID`, parse-tree validation, AMNESIA/Halfond taxonomy | Columbia, UC Davis, Illinois, Ohio State, Georgia Tech/USC lineage. | These form the classical defense taxonomy for SQLi before ML/DL. | SQLrand, SQLCHECK, CANDID, parse-tree validation downloaded; AMNESIA and Halfond 2006 taxonomy still need clean PDFs. |

Links:

- GAN autonomous pentesting PubMed: https://pubmed.ncbi.nlm.nih.gov/37766067/
- SQLrand: https://www1.cs.columbia.edu/~angelos/Papers/sqlrand.pdf
- SQLCHECK: https://www.cs.tufts.edu/comp/150BUGS/sqlcheck-2006.pdf
- CANDID: https://madhu.cs.illinois.edu/tissec09.pdf
- Parse tree validation: https://sivilotti.github.io/research/publications/sem05.pdf

## Portugal / EU

| Priority | Paper | Institution signal | Why it matters | Status |
|---|---|---|---|---|
| Very high | `Prompt-to-SQL Injections in LLM-Integrated Web Applications: Risks and Defenses` | INESC-ID / Instituto Superior Técnico, University of Lisbon. | Strong AI-era SQLi paper for LangChain/LlamaIndex applications; complements AIA and LLM SQLi generation. | Already downloaded as `Pedro_2025_Prompt_to_SQL_Injections.pdf`. |

Links:

- ICSE page: https://conf.researchr.org/details/icse-2025/icse-2025-research-track/31/Prompt-to-SQL-Injections-in-LLM-Integrated-Web-Applications-Risks-and-Defenses
- PDF: https://syssec.dpss.inesc-id.pt/papers/pedro_icse25.pdf

## United Kingdom / Europe-Linked Generative SQLi Work

| Priority | Paper | Institution signal | Why it matters | Status |
|---|---|---|---|---|
| High | `Enhancing SQL Injection Detection and Prevention Using Generative Models` | arXiv; authors Naga Sai Dasari, Atta Badii, Armin Moin, Ahmed Ashlam. Search results connect related SQL generation work to Aston University material, but author affiliations should be verified from PDF. | Uses VAE, CWGAN-GP, and U-Net for synthetic SQL query generation and detector augmentation. | Already downloaded as `Sakib_2025_Generative_Models_SQLi.pdf` / local naming should be checked against actual authors. |

Link:

- arXiv: https://arxiv.org/abs/2502.04786

## Turkey / LLM-Era SQLi

| Priority | Paper | Country signal | Why it matters | Status |
|---|---|---|---|---|
| High | `Adversarial SQL Injection Generation with LLM-Based Architectures` | Authors Ali Karakoc, H. Birkan Yilmaz; affiliation should be verified from PDF. | Recent 2026 paper comparing RADAGAS/RefleXQLi across rule-based, AI/ML, and commercial WAFs. | Already downloaded as `Adversarial_SQLi_LLM_2026.pdf`. |

Link:

- arXiv: https://arxiv.org/abs/2605.11188

## India / South Asia

India has many SQLi detection papers and WAF/ML papers, but in this quick scan I found fewer high-signal direct GAN+SQLi papers than China/Vietnam/US/EU. The strongest nearby items are:

- Hybrid DL SQLi/XSS detection with Indian authors in Scientific Reports, already downloaded as `Tadhani_2024_XSS_SQLi_Deep_Learning.pdf`.
- Many 2025 conference/journal items on ML/LSTM SQLi detection, but they appear less central than AdvSQLi/GSQLi/AIA/P2SQL.

Link:

- Scientific Reports SQLi/XSS DL paper: https://www.nature.com/articles/s41598-023-48845-4

## Broader GAN-in-Cybersecurity Surveys

These are useful if the thesis needs a world-level framing beyond SQLi payloads:

| Paper | Why it matters |
|---|---|
| `A comprehensive survey of generative adversarial networks (GANs) in cybersecurity intrusion detection` | Broad IDS/cybersecurity GAN taxonomy; useful for positioning GAN-SQLi as one branch of GAN-for-security. |
| `Generative Adversarial Networks for Intrusion Detection Systems: A Comprehensive Survey of Applications, Challenges, and Research Directions` | Recent IDS-specific survey; useful for architecture and dataset taxonomy. |
| `Generative Adversarial Networks (GANs) in networking: A comprehensive survey & evaluation` | Covers networking, IoT, physical layer, and cybersecurity uses of GAN. |
| `A Survey on the Application of Generative Adversarial Networks in Cybersecurity` | Broad arXiv survey around IDS, botnet, malware, mobile/network trespass. |

## Recommendation

For the next crawl, prioritize:

1. `Luo_2023_BERT_GAN_SQLi.pdf` from the Chinese Spacejournal PDF preview.
2. `Wang_2022_CTTGAN_Traffic_SQLi_Minority.pdf` from MDPI.
3. If available through library/proxy or author copies: AMNESIA ASE 2005 and Halfond 2006 taxonomy paper.
4. One or two recent GAN-cybersecurity survey papers to support the global framing.

