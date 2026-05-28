Article
Not peer-reviewed version
Generative AI Driven Synthetic Attack
Augmentation for Enhanced Intrusion
Detection Using an Imbalanced Dataset
Mamoona Nawaz * , Shireen Tahira , Anum Yasmin
Posted Date: 17 December 2025
doi: 10.20944/preprints202512.1521.v1
Keywords: intrusion detection system; generative ai; machine learning; CTGAN; class imbalance
Preprints.org is a free multidisciplinary platform providing preprint service
that is dedicated to making early versions of research outputs permanently
available and citable. Preprints posted at Preprints.org appear in Web of
Science, Crossref, Google Scholar, Scilit, Europe PMC.
Copyright: This open access article is published under a Creative Commons CC BY 4.0
license, which permit the free download, distribution, and reuse, provided that the author
and preprint are cited in any reuse.


---


Article
Generative AI Driven Synthetic Attack
Augmentation for Enhanced Intrusion Detection
Using an Imbalanced Dataset
Mamoona Nawaz *, Shireen Tahira and Anum Yasmin
Department of Computer Science, IIU
* Correspondence: mamoonanawaz62@gmail.com
Abstract
Intrusion Detection Systems (IDS) are very important in ensuring the security of the modern network,
but persistent problems with severe class imbalance in the datasets of the real network traffic
conditions show that the minor types of attacks are highly underrepresented. Critical attacks present
in the popular dataset, including Brute Force and Web Attacks, are very infrequent compared to
regular traffic and high-volume attacks, which causes biased learning, high false-negativities, and
bad minority attacks detection. To overcome this problem, this paper suggests a Generative AI-based
synthetic attack augmentation model on Conditional Tabular Generative Adversarial Networks
(CTGAN) to improve the performance of the IDS in imbalanced jobs. The given strategy is aimed at
producing high-fidelity synthetic samples of minority attack classes without changing the statistical
properties and behavioral patterns of actual network traffic. Training and testing of augmented data
ensemble-based machine learning models, namely Random Forest and Extreme Gradient Boosting
(XGBoost) are performed using the augmented dataset. Experiments using the CICIDS2017 dataset
show that the detection in the minority attack is significantly improved. Synthetic augmentation
boosted Recall to Web Attacks by 28 to 91 with Random Forest and 32 to 94 with XGBoost, and Brute
Force detection Recall boosted by 45 to 95 and 55 to 98 respectively. Overall Recall and F1-score also
gained significantly and XGBoost obtained F1-score of 94% on the augmented dataset. These findings
support the hypothesis that Generative AI-based synthetic data augmentation works well in class
imbalance, false negative, and increases the resilience and reliability of intrusion detection systems
in real-life cybersecurity settings.
Keywords: intrusion detection system; generative ai; machine learning; CTGAN; class imbalance

1. Introduction
The IDS plays an essential role in the present-day cyber defense system, as it is the role of these
systems to trace the cases of unauthorized access and malevolent activity within the complicated
networks. With the growth in scale and complexity of cyberattacks due to the adoption of digital
infrastructures with cloud computing, IoT and edge systems, the conventional ability of IDS systems
to sustain consistent detection rates, especially those of infrequent attack types, has been put to the
test [Synthetic attack data generation model applying GAN for intrusion detection [1]. Given that
machine learning (ML) methods have been widely used to enhance the detection of anomalies, both
methods frequently have difficulties detecting a minority type of attack when the majority of traffic
or typical attacks are dominant, occupy long sequences, and are predominant in databases (when
compared to a minority attack) [2]. The problem of class imbalance is important and the high false
negatives when dealing with underrepresented attacks is devastating to the IDS performance [3].
Recent research has examined generative models including Generative Adversarial Networks
(GANs) and variants to produce real samples of attacks, which has greatly improved the IDS
performance of minority classes without negatively affecting the overall detection performance [4].
Preprints.org (www.preprints.org) | NOT PEER-REVIEWED | Posted: 17 December 2025
doi:10.20944/preprints202512.1521.v1
Disclaimer/Publisher's Note: The statements, opinions, and data contained in all publications are solely those of the individual author(s) and
contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to people or property resulting
from any ideas, methods, instructions, or products referred to in the content.
© 2025 by the author(s). Distributed under a Creative Commons CC BY license.


---


2 of 21

Based on these developments, our study takes advantage of Generative AI-based synthetic attack
augmentation by enhancing recall and robustness of IDS models that are trained on unbalanced
benchmark datasets.
In practical network conditions, low frequency attacks like Brute Force and Web-based
intrusions can be used with a multi-step process that is similar to the legitimate user behavior and
hence is hard to detect with the traditional IDS trained on unbalanced data. To give just one example,
in an enterprise web application, an attacker can perform a Brute Force login attack by making a few
credential tries with longer time intervals in order to avoid rate-based and anomaly-based detection
systems. Since the traffic of such attacks constitutes a small percentage of all traffic flows within the
network, the IDS models often end up categorizing this traffic as normal traffic [5]. This is seen to also
apply to Web Attacks where malicious people can take advantage of Web vulnerabilities like SQL
injection or cross-site scripting by incorporating malicious payloads in otherwise legitimate HTTP
requests [6].

Figure 1. Comprehensive workflow of a web-based cyber attack.
Research indicates that IDS may not be effective in detecting the initial phases of such attacks
because they are learned using imbalanced data and consequently, they consume more time before
detecting and therefore, more time before the breach is detected is exercised [7]. Synthetic attack
augmentation with the help of generative AI allows the formation of realistic samples that model
such step-wise attack behavior and enhance the capacity of the IDS to detect the slightest malicious
patterns during deployment [8]. These realistic attack sequences must therefore be incorporated into
the training data in order to make IDS resilient to actual cyber threat in the real world.
1.1. Problem Statement
Their functionality is greatly diminished when in training on highly-imbalanced datasets (which
is a typical feature of real-world network traffic statistics). In benchmark data like CICIDS2017, the
normal traffic and several prevalent types of attacks constitute most of the samples, whereas more
critical types of attacks, including Brute Force and Web Attacks, have a low frequency [9]. This bias
makes machine learning (ML) models be biased to majority classes and lead to misleading high
accuracy, and the inability to detect rare but serious attacks [10]. The incidents of minorities attacks
are usually incorrectly categorized as regular traffic or they are simply overlooked and hence high
rates of false-negative are experienced, which compromises the reliability of IDS in the real-world
settings [11]. These limitations are especially hazardous in any contemporary cyber infrastructures,
where even a single breach that will go undetected can result in the massive destruction. Solutions
that are currently available, like cost-sensitive learning and conventional oversampling methods have
not been very successful since they usually cannot maintain the complex statistical correlation
existing in network traffic data [12]. Consequently, there is a pressing need for advanced data-level
Preprints.org (www.preprints.org) | NOT PEER-REVIEWED | Posted: 17 December 2025
doi:10.20944/preprints202512.1521.v1
© 2025 by the author(s). Distributed under a Creative Commons CC BY license.
