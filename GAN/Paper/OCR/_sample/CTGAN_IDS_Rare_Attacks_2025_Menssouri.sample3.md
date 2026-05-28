A Conditional Tabular GAN-Enhanced Intrusion
Detection System for Rare Attacks in IoT Networks
Safaa Menssouri, and El Mehdi Amhoud
College of computing, Mohammed VI Polytechnic University, Ben Guerir, Morocco
{safaa.menssouri, elmehdi.amhoud}@um6p.ma
Abstract—Internet of things (IoT) networks, boosted by 6G
technology, are transforming various industries. However, their
widespread adoption introduces significant security risks, particularly in detecting rare but potentially damaging cyber-attacks.
This makes the development of robust intrusion detection systems
(IDS) crucial for monitoring network traffic and ensuring their
safety. Traditional IDS often struggle with detecting rare attacks
due to severe class imbalances in IoT data. In this paper, we
propose a novel two-stage system called conditional tabular
generative synthetic minority data generation with deep neural
network (CTGSM-DNN). In the first stage, a conditional tabular
generative adversarial network (CTGAN) is employed to generate
synthetic data for rare attack classes. In the second stage, the
SMOTEENN method is applied to improve dataset quality. The
full study was conducted using the CSE-CIC-IDS2018 dataset,
and we assessed the performance of the proposed IDS using different evaluation metrics. The experimental results demonstrated
the effectiveness of the proposed multiclass classifier, achieving
an overall accuracy of 99.90% and 80% accuracy in detecting
rare attacks.
Index Terms—intrusion detection, IoT networks, rare attacks,
conditional tabular GAN, SMOTEENN
I. INTRODUCTION
The proliferation of internet of things (IoT) networks,
coupled with the emergence of 6G technology [1], are transforming numerous aspects of modern life, from smart homes
and cities to industrial automation and healthcare systems.
IoT networks comprise a vast array of interconnected devices
that collect, exchange, and analyze data to facilitate intelligent
decision-making and automation. This interconnected ecosystem enhances efficiency, productivity, and convenience, driving
the rapid adoption of IoT technologies across various domains.
However, the widespread deployment of IoT devices within
the high-speed, low-latency framework of 6G introduces substantial security challenges. The heterogeneous nature of these
networks, combined with their large-scale and distributed
architecture, makes them vulnerable to a variety of cyber
threats [2]. Traditional security measures are often inadequate
for addressing the unique requirements and vulnerabilities inherent in IoT environments. Thus, robust and adaptive security
solutions, such as intrusion detection systems (IDS) [3], are
essential for monitoring network traffic, detecting anomalies,
and safeguarding against potential security breaches.
Although there are different types of IDS, in our research
work we are interested in anomaly-based IDS (AIDS) [4].
These systems aim to detect both known and unknown attacks,
providing a more comprehensive detection capability than
other IDS.
One of the significant challenges in developing effective
anomaly-based IDS is the issue of imbalanced data. In many
real-world scenarios, the number of normal instances vastly
outweighs the number of anomalous ones, creating a class
imbalance problem. This imbalance is particularly problematic
when dealing with rare classes of attacks.
Rare attacks are a type of security breach that occur
infrequently and have a low number of instances, making
them less familiar and more challenging to detect. They often
account for only a small fraction of the normal data, and when
using a single machine learning (ML) model for classification,
the classifier tends to favor the majority class of data and
misclassify the rare-class attack data.
Despite their rarity, these attacks can indicate more sophisticated and potentially damaging threats. As a result, developing
effective techniques to detect rare intrusion events is crucial
for maintaining the security and integrity of IoT networks.
In this work, we aim at enhancing the detection capabilities
for rare attacks by exploring novel approaches and leveraging
advanced ML techniques. While several previous studies have
focused on using generative adversarial networks (GANs) for
data augmentation to address the challenge of imbalanced
datasets, our approach is distinguished by the use of conditional tabular GAN (CTGAN). Unlike traditional GANs, which
can struggle with discrete data characteristics, CTGAN excels
at capturing the nuances of rare attack classes.
The main contributions of this paper are summarized as
follows:
' We develop a novel two-stage methodology that first
employs CTGAN to generate synthetic data for rare attack
classes, followed by the SMOTEENN method to enhance
the detection of attacks in IoT networks.
' We validate our proposed system on one of the largest
public datasets (CSE-CIC-IDS2018) for IDS, and we conduct comprehensive comparisons with existing methods.
' The experiments demonstrate that our proposed solution
significantly improves the detection accuracy of rare
attack instances, achieving up to 80% accuracy for rare
attacks while maintaining 99.90% overall classification
accuracy.
The remainder of the paper is organized as follows:
arXiv:2502.06031v1 [cs.CR] 9 Feb 2025


---

In section II, we introduce the related work. In section III,
we detail the architecture of our proposed model along with a
description of the dataset. In section IV, we present our simulation results, and we discuss the observations and findings.
Finally, in section V, we conclude and outline our perspectives.
II. RELATED WORK
Intrusion detection systems play a crucial role in safeguarding IoT networks. Numerous studies have focused on developing effective IDS for IoT networks, employing a variety of
techniques ranging from traditional signature-based methods to
more advanced ML approaches. Notably, supervised learning
algorithms, such as k-nearest neighbors (KNN), naïve bayes,
and support vector machines (SVM) [5], have been extensively
studied for their effectiveness in detecting anomalies. In [6],
the authors conducted several experiments to evaluate the
efficiency and performance of various ML classifiers, such
as random forest, random tree, decision table, naive Bayes,
and Bayes network. All the tests were conducted using the
KDD dataset. The experiments demonstrated that there is no
single ML model that can handle efficiently all the types
of attacks. Furthermore, deep learning (DL) techniques, such
as convolutional neural networks (CNN) or long short-term
memory (LSTM) [7] are widely used in IDS.
The use of a single ML model has inherent limitations [8].
Thus, in recent years, various learning algorithms have been
combined to enhance performance of IDS [9]. For instance,
in [10] the authors proposed an IDS that combines the powerful learning ability of LSTM in time series data with CNN's
ability to extract spatial features. The model was trained using
KDD CUP99, NSL-KDD, and UNSW-NB15 classic datasets,
the results show good convergence and performance.
Despite these advancements, a significant challenge remains
in dealing with imbalanced datasets, particularly regarding rare
attacks detection. Traditional and even some advanced ML
models often struggle to accurately detect rare attacks due to
their scarcity in the training data. Xu et al. [11] presented a
recurrent neural network based IDS. Their approach, tested
on the NSL-KDD and KDD Cup'99 datasets, demonstrated
promising results compared to other methodologies. However,
it has a limitation in detecting minority attack classes, such
as U2R and R2L, resulting in lower detection rates for these
specific classes. Other works, such as [12], have utilized
ensemble learning with feature selection technique to enhance
IDS performance on the CSE-CIC-IDS2018 dataset. While
the overall detection accuracy has been improved, rare attack
classes like SQL Injection and Brute Force were not well
classified. Additionally, the infiltration attack class showed
lower performance, revealing challenges in detecting these
types of attacks. Moreover, in [13] the authors proposed
a Bagging-DNN-based IDS that addresses class imbalance
by incorporating class weights and leveraging deep neural
networks (DNN) as core estimators. Their method achieved
high performance across four datasets, with accuracy reaching
98.90%, demonstrating effective detection of both known and
Benign
DoS attacks-Hulk
Bot
Infilteration
Brute Force -XSS
SQL Injection
Class Name
0
100000
200000
300000
400000
Number of samples
446653
434873
282310
92380
79
53
Benign
DoS attacks-Hulk
Bot
Infilteration
Brute Force -XSS
SQL Injection
Fig. 1: Class distribution of the dataset.
Table I: Selected files from the CSE-CIC-IDS2018 dataset
File name
Class types
Friday-16-02-2018 TrafficForML CICFlowMeter.csv
Benign
DoS attacks–Hulk
Thursday-22-02-2018 TrafficForML CICFlowMeter.csv
Brute Force–XSS
Friday-23-02-2018 TrafficForML CICFlowMeter.csv
SQL Injection
Thursday-01-03-2018 TrafficForML CICFlowMeter.csv
Infilteration
Friday-02-03-2018 TrafficForML CICFlowMeter.csv
Bot
unknown attacks. However, their experiments were limited to
binary classification, which may restrict its applicability in
multiclass scenarios, particularly for detecting rare attacks.
Existing works address the issue of imbalanced data by employing class-weighting techniques, undersampling, or oversampling. Class weighting effectively enhances rare attack
detection without introducing redundancy, but it may lead to
trade-offs in majority class performance and struggles with
extremely rare classes. On the other hand, undersampling can
lead to the loss of valuable information, while oversampling
can introduce redundancy and overfitting. Alternatively, some
approaches employ ensemble models to improve rare attack
detection, although these methods can be computationally
complex, especially when dealing with large dataset.
III. METHODOLOGY
A. CSE-CIC-IDS2018 Dataset
In our study, we employed the open-source CSE-CIC-
IDS2018 dataset, created by the Canadian Institute for Cybersecurity [14]. This dataset was selected for its comprehensive
and up-to-date nature, meeting essential criteria such as extensive traffic data, a variety of attack types, and detailed labeling.
It encompasses seven distinct attack scenarios: Brute Force,
Heartbleed, Botnet, DoS, DDoS, Web attacks, and network
infilteration, as well as the benign data. Importantly, the CSE-


---

CIC-IDS2018 dataset exhibits imbalanced classes, with certain
rare attack types such as Brute Force-XSS and SQL Injection,
occurring less frequently than others. The distribution of the
dataset used in our analysis is illustrated in Fig. 1. From the
figure, we notice that the number of samples of Brute Force-
XSS and SQL Injection represent only 0.009% and 0.006%,
respectively, from the total number of samples of all attacks.
This rarity is crucial to our objective of developing an IDS
tailored for identifying rare attacks in IoT networks.
In addition, the dataset contains 80 features extracted from
network traffic and system logs. Although it comprises several
files, only a selected subset was used for this study based on
their relevance to the analysis. The chosen files and their corresponding class types are detailed in Table I. The preprocessing
step included merging these files, and the workflow is outlined
in the following subsections.
Algorithm 1 SMOTEENN method
1: Input: Dataset D with minority class samples Dmin
and majority class samples Dmaj, Number of synthetic
samples N, Number of nearest neighbors k
2: Output: Resampled set D1
3: S Ð H
4: for each xi P Dmin do
5:
Ni Ð k-nearest neighbors of xi from Dmin
6: end for
7: for each xi P Dmin do
8:
for j Ð 1 to N do
9:
Select xij P Ni
10:
xnew Ð xi ` λpxij ´ xiq where λ " Up0, 1q
11:
S Ð S Y txnewu
12:
end for
13: end for
14: D1 Ð D Y S
15: for each xi P D1 do
16:
Ni Ð k-nearest neighbors of xi
17:
if yi ‰ majority class in Ni then
18:
D1 Ð D1ztxiu
19:
end if
20: end for
B. SMOTEENN Method
SMOTEENN is a hybrid technique that combines synthetic minority over-sampling technique (SMOTE) [15] and
edited nearest neighbors technique (ENN) to tackle imbalanced
datasets [16]. Initially, SMOTE generates synthetic samples
of the minority class to balance the dataset. Following this,
the ENN method is applied to cleanse the data by removing
noisy and ambiguous samples. This dual approach not only
enhances the representation of rare attacks but also improves
dataset quality by eliminating misleading instances, thereby
enhancing the accuracy and reliability of intrusion detection.
The SMOTEENN method is formalized in Algorithm 1.
C. Conditional Tabular GAN (CTGAN)
CTGAN is a specialized GAN designed for realistic tabular
data generation [17], adept at handling mixed data types
and complex dependencies. It employs conditional modeling,
training-by-sampling techniques, and mode-specific normalization to optimize synthesis across categorical and continuous
variables, thereby enhancing data augmentation and effectively
addressing class imbalance. CTGAN's adversarial training
framework ensures continual improvement in generating realistic samples, making it ideal for various applications needing
precise synthetic data from tabular datasets. In CTGAN, the
generator G and discriminator D are trained simultaneously,
with the goal of G producing synthetic data that D cannot
distinguish from real data.
CTGAN employs mode-specific normalization using a Gaussian mixture model (GMM) for continuous variables and onehot encoding for categorical variables. The overall probability
density function ppxq of a continuous variable x is given by:
ppxq "
K
ÿ
k"1
πkN px | µk, σ2
kq,
(1)
where ppxq is formed by a weighted sum of K Gaussian
components. Each component is characterized by its mean µk,
variance σ2
k, and weight πk, which determines its contribution
to the mixture model. This ensures that the synthetic data
preserves the statistical properties of the original data.
D. CTGSM-DNN System
The proposed conditional tabular generative synthetic minority data generation with deep neural network (CTGSM-
DNN) intrusion detection system consists of several sequential
steps, as depicted in Fig. 2. We began by importing the CSE-
CIC-IDS2018 dataset and performing essential preprocessing
tasks, including data cleaning, encoding, and normalization. As
part of these steps, we also dropped the timestamp feature
from the dataset. To address the rarity of certain attacks,
we employed CTGAN model to generate synthetic samples
for the Brute Force-XSS and SQL Injection classes. This
is shown in step 2 in Fig. 2. This approach ensures the
generation of realistic and less biased synthetic data, enriching
the dataset with these rare attack instances. By incorporating
these synthetic samples into the existing data, we applied the
SMOTEENN method to balance the dataset, ensuring a cleaner
and more representative distribution. (this is shown in step 3
in Fig. 2). This combination of CTGAN and SMOTEENN
is motivated by the need to balance augmentation with data
quality. While CTGAN is effective at generating realistic
synthetic samples, excessive augmentation (e.g., increasing
from 30 to 100,000) can introduce redundancy or unrealistic
samples, potentially leading to model overfitting or degraded
performance. SMOTEENN addresses this issue by refining
the dataset, to ensure the generated data is high-quality and
representative, thereby enhancing training robustness.
Afterwards, in step 4, the resulting dataset is used to train the
DNN model.
