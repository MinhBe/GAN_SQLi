1
Effective Intrusion Detection in Highly Imbalanced
IoT Networks with Lightweight S2CGAN-IDS
Caihong Wang, Du Xu, Zonghang Li, Dusit Niyato, Fellow IEEE,
Abstract—Since the advent of the Internet of Things (IoT), exchanging vast amounts of information has increased the number
of security threats in networks. As a result, intrusion detection
based on deep learning (DL) has been developed to achieve high
throughput and high precision. Unlike general deep learningbased scenarios, IoT networks contain benign traffic far more
than abnormal traffic, with some rare attacks. However, most
existing studies have been focused on sacrificing the detection
rate of the majority class in order to improve the detection
rate of the minority class in class-imbalanced IoT networks.
Although this way can reduce the false negative rate of minority
classes, it both wastes resources and reduces the credibility of
the intrusion detection systems. To address this issue, we propose
a lightweight framework named S2CGAN-IDS. The proposed
framework leverages the distribution characteristics of network
traffic to expand the number of minority categories in both data
space and feature space, resulting in a substantial increase in
the detection rate of minority categories while simultaneously
ensuring the detection precision of majority categories. To reduce
the impact of sparsity on the experiments, the CICIDS2017
numeric dataset is utilized to demonstrate the effectiveness of
the proposed method. The experimental results indicate that our
proposed approach outperforms the superior method in both
Precision and Recall, particularly with a 10.2% improvement in
the F1-score.
Index Terms—Deep learning, class imbalance, intrusion detection, generative adversarial networks, internet of things
I. INTRODUCTION
The emergence of the 5G era has brought new challenges
to cybersecurity due to the proliferation of the Internet of
Things (IoT). IoT devices are known to harbor a significant
amount of private information and are often secured with
simple encryption. As a result, a considerable number of these
devices may be rendered as zombie hosts or utilized as mining
tools, with some users even falling prey to cyber extortionists.
Intrusion detection systems (IDS) [1] constitute a pivotal
component of firewalls and can detect viruses before they
reach IoT devices. As such, IDS has become an indispensable
preventive measure for ensuring the security of IoT networks.
Conventional intrusion detection technologies heavily rely on
manually crafted rules and signatures. The creation and upkeep
of these rules and signatures require significant time and
labor. However, the contemporary proliferation of traffic and
Caihong Wang, Du Xu, and Zonghang Li are with School of Information
and Communication Engineering, University of Electronic Science and Technology of China, Chengdu, China.
Dusit Niyato is with School of Computer Science and Engineering,
Nanyang Technological University, Singapore.
The corresponding author: Du Xu. (Email: xudu@uestc.edu.cn)
This work was partially supported by the National Natural Science Foundation of China (62171085).
the rising prevalence of attacks stemming from the IoT have
rendered these traditional methods relatively ineffective.
To overcome the limitations of traditional intrusion detection methods, deep learning (DL) has surfaced as a promising
approach. DL algorithms, including deep belief networks
(DBN) [2], convolutional neural networks (CNN) [3], and
recurrent neural networks (RNN) [4], can automatically learn
complex patterns and anomalies from raw network traffic.
This enables more accurate automatic detection of potential
threats. Additionally, DL algorithms can effectively leverage
massive network traffic to identify potential attacks and adapt
to changing attack patterns, thereby significantly enhancing
the detection accuracy of the IDS.
DL algorithm has exhibited high accuracy in detecting network attacks [5]. However, to operate effectively, DL models
require an adequate number of training examples. In comparison to the abundance of benign network traffic examples,
certain attack categories are scarce in number. Consequently,
DL-based intrusion detection models encounter the challenge
of a high false-negative rate [6], [7], [8].
In the realm of class imbalance, researchers have endeavored to optimize the efficiency of deep learning techniques, including data-level approaches [9], [10], algorithm-level strategies [11], [12], integrated learning [13], [14], transfer learning
[15], [16], and evaluation metrics [17], with the primary aim
of mitigating the false-negative rate of intrusion detection
systems (IDS). However, this objective often comes at the
expense of precision for majority classes, while improving the
detection rate of minority attacks. Therefore, these methods
may ultimately not only compromise the reliability of the
system but also waste resources.
The motivation of this paper is to enhance the detection
rate of minority categories in IoT networks while minimizing
the impact on the detection rate of majority categories. By
focusing on the distinctive characteristics of attack frequency,
we try to pay more attention to the extremely rare attacks
and foster the advancement and innovation of this field from
different angles.
In response to the aforementioned concerns, we present
a proficient and lightweight S2CGAN-IDS framework that
leverages the distribution characteristics of traffic categories
within IoT networks. Our framework extends the original
imbalanced training data by considering two distinct perspectives: data space and feature space. This approach aims
to enhance the detection rate of underrepresented categories
while maintaining satisfactory detection rates for the majority
classes.
arXiv:2306.03707v1 [cs.CR] 6 Jun 2023


---

2
The main contributions of this paper are summarized as
follows:
1) We have devised a lightweight S2CGAN-IDS framework
from a data-oriented perspective to address the issue
of class imbalance. This framework aims to improve
the detection rate of the underrepresented minority class
while maintaining accuracy for the majority class.
2) This paper presents an innovative feature extraction
method that combines Siamese networks and autoencoders to preserve class differences and significantly
accelerate the convergence speed of the adversarial generative network.
3) This paper presents a novel data augmentation technique, SCGAN, for categories exhibiting similar distribution profiles. The proposed approach, which combines
Siamese networks and autoencoders, accelerates the
convergence rate significantly.
4) This paper introduces a highly efficient data synthesis
approach named synthetic k neighbors (SKN) that utilizes feature space-based methods to generate samples
for categories that are extremely rare.
II. MOTIVATION
The class imbalance problem in IoT scenarios is of
paramount importance in ensuring IoT security [18]. This
problem stems from several key factors, including the extensive deployment of devices, the wide variety of malicious
behaviors, the limited resources of IoT devices, and the
heightened sensitivity of security requirements. These factors
collectively contribute to the scarcity of malicious behavior
data in IoT scenarios, making accurate detection of such
behaviors an urgent necessity [19]. Consequently, the effective
resolution of the class imbalance problem holds significant
significance in upholding IoT security.
After an extensive literature search, NSLKDD, UNSW-
NB15, and CICIDS2017 have emerged as the predominant
datasets utilized in this field over the past two decades. An
evaluation of attack frequency across these datasets reveals a
distinct gradient shift. Notably, CICIDS2017 exhibits a conspicuous step-like upgrade while possessing the most recent
and sparsest characteristics, aligning it more closely with
the traffic observed in real IoT network environments [20].
Consequently, CICIDS2017 has been chosen for subsequent
analysis and experimentation.
TABLE I: Some details of commonly used classic datasets.
Dataset
Year
Characteristics
Sparsity Frequency
NSLKDD
1999
Network-based,
real-world traffic,
KDD Cup 1999
Medium
Uniform
UNSW-NB15
2015
Network-based,
real-world traffic,
contains synthetic
and real data
High
Gradual
CICIDS2017
2017
Network-based,
real-world traffic,
contains IoT and
normal traffic
Low
Stepped
Based on the analysis mentioned above, the fundamental
issue that must be addressed by an effective IoT network
intrusion detection model is enhancing the detection rate of
the minority categories while maintaining the accuracy of the
majority categories. To tackle this problem, we conducted
Principal Component Analysis (PCA) on a widely used intrusion detection dataset and generated a scatterplot based on
the resulting PCA data (Fig. 1).
Fig. 1: The scatter of CICIDS2017 dataset.
Analysis of Fig. 1 reveals that categories located in the
upper-left region of the scatterplot possess an ample number
of samples and exhibit a complete distribution. Conversely, the
categories in the middle region are relatively scarce, and the
distribution outline is rather rough. Finally, categories situated
in the lower-right region contain only a few, scattered data
points.
Based on the observed characteristics in the scatter, we
calculate the imbalance ratio (IRi) for each class by nmax/ni,
where ni represents the number of the type-i attack, and nmax
represents the number of normal samples. Remarkably, our
calculations revealed a distinct step-wise distribution pattern
in the IRi values, which aligned with the visual representation
depicted in the scatter.
TABLE II: The labels, IRi values and quantity levels of the
CICIDS2017 dataset.
Subclass
Label
IRi
Level
BEINGN
BEINGN
DoS
DoS Hulk
DDoS
DoS GoldenEye
DoS/DDoS
5.98
ample
DoS slowloris
DoS Slowhttptest
PortScan
PortScan
14.31
FTP-Patator
Patator
SSH-Patator
164.33
Web Attack-Brute Force
Web Attack-XSS
Web Attack 1042.28
scarce
Web Attack-Sql Injection
Bot
Bot
1156.92
Infiltration
Infiltration
63141.03
rare
Heartbleed
Heartbleed
206645.18
By considering the step distribution of IRi values and its
coherence with the visual depiction of the scatter, we classify
intrusion detection traffic into ample-level, scarce-level, and
rare-level (as shown in Table II), and treat them differently
based on their respective attributes.


---

3
To minimize the computational overhead while ensuring a
high detection rate for the majority category, we specifically
avoid processing the majority category (ample-level), which
already exhibits a complete distribution.
In the scenario addressed in this paper, a challenge arises
due to the significant disparity in the number of minority
samples. Solely relying on data space-based data augmentation
methods to generate minority samples may be ineffective for
rare-level categories, as depicted in the lower right part of
Fig. 1, where the scarcity of samples hinders the generation
of new instances. Conversely, employing only feature spacebased data enhancement methods to synthesize minority samples may result in synthetic samples that closely resemble the
original ones. Consequently, the performance of the scarcelevel categories in the middle part of Fig. 1 may be constrained.
Consequently, we partition the minority categories into
scarce-level and rare-level. For scarce-level categories, we
adopt advanced data space-based data augmentation methods,
while for rare-level categories, we rely on feature space-based
data enhancement techniques.
The remaining parts of this paper are organized as follows.
Section III gives the outline of our framework. Section IV
introduces the main algorithms used to design the proposed
S2CGAN. Section V presents a detailed explanation of the
architecture and results of the experiments conducted in this
study. Section VI reviews the literature on IDS and class
imbalance problems. followed by Section VII, which provides
concluding remarks and suggests avenues for future research.
III. METHODOLOY OVERVIEW
In this section, we present our lightweight intrusion detection framework, which comprises three primary components
as shown in Fig. 2.
These include dataset processing, the S2CGAN module,
and classifier training and testing. Our framework is designed
to improve the performance of intrusion detection systems
in highly imbalanced datasets by employing different data
augmentation techniques for different category levels. The
specific detection process of the IDS framework is as follows.
Dataset processing. The dataset is processed through the
following steps: normalization, and train-test split.
S2CGAN module. As a case study, we classify all categories
within this dataset into three levels based on the step-change
characteristics of their respective numbers. And employ the
S2CGAN module to enhance the dataset, Which is a data
generation model incorporating two techniques: SCGAN and
SKN. The SCGAN is utilized to generate scarce-level attacks,
while a filter is applied to the generated data to enhance the
consistency of generated samples and original samples. On
the other hand, SKN is used to generate rare-level attacks by
simulating potential rare-level attack distributions through the
KNN algorithm.
Training/testing. To evaluate the effectiveness of the proposed
data augmentation algorithm, we implemented it using a deep
neural network and trained an intrusion detection classifier
using the augmented dataset. The performance of the resulting
classifier was then verified using a separate test set.
Preprocessing
Training set
Testing set
Scarce
Rare
Ample
Siamese
autoencoder
network
Discriminator
z
SKN
Filter
Deep neural
network
Results
Enhanced
training data
Training
Testing
Generator
Imbalanced
dataset
S2CGAN
Module
Fig. 2: S2CGAN-IDS model framework. The framework diagram for the proposed algorithm consists of three primary
components: data preprocessing, data enhancement, and training and testing of the IDS classifier.
The S2CGAN module plays a central role in the algorithm
proposed in this paper. This module enhances the original data
set by operating in both the data and feature spaces, thus
improving the detection accuracy of minority categories in the
intrusion detection classifier. In the subsequent sections of this
paper, we will present a detailed exposition of the S2CGAN
(Algorithm 1).
IV. IMPLEMENTATION DETAILS OF S2CGAN
As demonstrated in the principal component analysis (PCA)
scatter plot of the CICIDS2017 dataset in Fig. 1, the data
distributions for ample-level categories are complete and can
be directly reserved in the augmented dataset. However,
scarce-level attacks have only approximate distribution. In this
situation, we utilize SCGAN to learn the original distribution
and generate missing data. Lastly, we employ SKN to expand
the original distribution as much as possible from the feature
space for rare-level attacks with only a few data points.
A. SCGAN for scarce-level attacks
This section is dedicated to the details of the SCGAN
module, which serves the purpose of generating scarce-level
categories. The SCGAN module consists of a Siamese autoencoder network (SAN) and a generative adversarial network
(GAN). Firstly, we introduce the SAN model to extract differential feature information for the SCGAN module. Algorithm
2 shows the detail.
