Enhancing Network Intrusion Detection Performance using Generative
Adversarial Networks
Xinxing Zhao∗, Kar Wai Fok and Vrizlynn L. L. Thing
ST Engineering, Singapore.
A R T I C L E I N F O
Keywords:
Generative Adversarial Networks
Network Intrusion Detection System
Deep Learning
Resampling
A B S T R A C T
Network intrusion detection systems (NIDS) play a pivotal role in safeguarding critical digital
infrastructures against cyber threats. Machine learning-based detection models applied in NIDS are
prevalent today. However, the effectiveness of these machine learning-based models is often limited
by the evolving and sophisticated nature of intrusion techniques as well as the lack of diverse
and updated training samples. In this research, a novel approach for enhancing the performance
of an NIDS through the integration of Generative Adversarial Networks (GANs) is proposed. By
harnessing the power of GANs in generating synthetic network traffic data that closely mimics real-
world network behavior, we address a key challenge associated with NIDS training datasets, which
is the data scarcity. Three distinct GAN models (Vanilla GAN, Wasserstein GAN and Conditional
Tabular GAN) are implemented in this work to generate authentic network traffic patterns specifically
tailored to represent the anomalous activity. We demonstrate how this synthetic data resampling
technique can significantly improve the performance of the NIDS model for detecting such activity.
By conducting comprehensive experiments using the CIC-IDS2017 benchmark dataset, augmented
with GAN-generated data, we offer empirical evidence that shows the effectiveness of our proposed
approach. Our findings show that the integration of GANs into NIDS can lead to enhancements in
intrusion detection performance for attacks with limited training data, making it a promising avenue for
bolstering the cybersecurity posture of organizations in an increasingly interconnected and vulnerable
digital landscape.
1. Introduction
The proliferation of devices and the ever-expanding In-
ternet of Things (IoT) ecosystem nowadays have led to an
unprecedented level of connectivity. From smartphones and
laptops to smart refrigerators and industrial machinery, an
increasingly diverse array of devices are constantly generat-
ing massive amounts of data. While this interconnectedness
has ushered in remarkable convenience and innovation, it
has also exposed us to a growing threat: malicious network
intrusion. The more devices we connect to networks, the
larger the attack surface becomes [1]. Attackers are quick
to capitalize on this expanded attack surface, targeting vul-
nerabilities in both traditional and IoT devices [2, 3].
These malicious actors launch various types of attacks,
such as botnet traffic [4], malware infections [5], zero-day
exploits [6], man-in-the-middle attacks [7]. NIDS are spe-
cialized tools designed to monitor network traffic, analyze
data packets, and identify any suspicious or unauthorized
activities, and they play a pivotal role in safeguarding net-
works against evolving threats. The widespread integration
of machine learning models into NIDS [8] is evident today
and brings forth many capabilities. These models empower
NIDS to deliver real-time [9], adaptive [10], and exception-
ally effective [11] threat detection, therefore serving as a
defence mechanism to shield the more vulnerable devices
within the interconnected landscape and fortify the security
of the invaluable data.
∗Corresponding author
xinxing.zhao@stengg.com (X. Zhao); fok.karwai@stengg.com (K.W.
Fok); vriz@ieee.org (V.L.L. Thing)
ORCID(s): 0000-0001-5815-043X (X. Zhao)
In addition to the well-recognized challenges that NIDS
face, such as handling encrypted traffic [12], combating ad-
vanced evasion techniques [13], addressing scalability con-
cerns [14], and navigating the complexities of network traffic
patterns [15], there are still significant obstacles that exist
during the NIDS training process, such as sample scarcity
and class imbalance [16]. Sample scarcity refers to the
scarcity of relevant data, particularly when it comes to cap-
turing anomalous network traffic indicative of cyberattacks.
This scarcity is rooted in the fact that real-world network at-
tacks occur less frequently in comparison to the vast volume
of normal network traffic. Consequently, the task of collect-
ing a sufficiently robust dataset for training an effective intru-
sion detection model becomes a challenge. Class imbalance
arises because normal network traffic, which is abundant
in most datasets, significantly outweighs the occurrence of
attack instances. This disproportion can be problematic, as
machine learning algorithms tend to exhibit a bias towards
the majority class when faced with imbalanced datasets.
This bias can lead to NIDS models being less sensitive to
detecting network attacks since they predominantly focus on
the abundant normal traffic class.
Existing literature offers several strategies to deal with
the challenges posed by sample scarcity and class imbal-
ance, such as data augmentation techniques [17], resam-
pling methods [18], ensemble learning approaches [19],
and sophisticated feature engineering [20]. In this research,
we focus on the problem of data scarcity and propose a
method leveraging the capabilities of generative AI, and,
in particular, GAN models to generate attack samples in
Page 1 of 12
arXiv:2404.07464v1  [cs.CR]  11 Apr 2024


---

Leveraging GANs for IDS Enhancement
enhancing the NIDS detection performance based on the
CIC-IDS2017 dataset [21].
The primary contributions of the research are outlined
below: Firstly, this study addresses a critical challenge
within intrusion detection systems: the limited availability of
representative attack samples for training IDS. To overcome
this challenge, three distinct GAN models are employed to
generate additional attack samples, based on the relatively
new CIC-IDS2017 dataset. Secondly, different from the
majority of the related studies in the literature, several
mechanisms have been applied in assessing the quality of the
generated attack samples. To ensure confidence in the GAN
models and underscores their reliability, we have employed
metrics and methodologies to assess the closeness and
likeness between the initial samples and the subsequently
generated ones. Thirdly, in contrast to previous studies,
this study explores the generation of varying quantities of
attack samples and their subsequent integration into the
original dataset. Through comprehensive experimentation
and rigorous testing on these augmented datasets, it is
demonstrated that with more data samples generated, im-
provements in intrusion detection system performance can
be achieved. Notably, our approach outperforms the existing
advanced techniques in terms of precision, recall, and F1-
score metrics. The rest of this paper is organized in the fol-
lowing manner. Section 2 describes GANs-related research
on network intrusion. Section 3 introduces the methodology
and three GAN models applied in this research. Section 4
describes the experiments and performance enhancement
by these generated attack samples. Section 5 provides the
discussions and section 6 presents the conclusions.
2. Related Work
There are three primary types of network intrusion de-
tection systems. The first type comprises signature-based
systems [22], they evaluate incoming traffic against a pre-
established database containing recognized attack patterns.
If a match is found, an alert will be triggered. This method is
effective in identifying known threats, however, may strug-
gle with novel attacks [23].
The second type of systems is anomaly-based [24].
Anomaly-based NIDS establishes a baseline of normal net-
work behavior by continuously monitoring network traffic
and system activities and comparing them to this baseline.
When any deviation or anomaly is detected, an alert will
be triggered. This detection approach is highly effective in
recognizing novel or previously unencountered threats that
lack established signatures. However, it does come with
certain drawbacks, including the need for complex config-
urations and substantial computational resource demands.
One highly related and complementary aspect to anomaly-
based detection in NIDS is classification [25]. Anomaly
detection focuses on identifying outliers or suspicious pat-
terns, whereas classification specializes in categorizing the
identified anomalies into specific threat types, and once
anomalies are detected, classification models can be applied
to classify the nature of the threat, providing more detailed
insights into the specific attack type. Therefore, the fusion
of these two elements can improve the overall performance
of the system and provides more actionable information to
security teams. And lastly, hybrid systems [26], combining
the strengths of both previous mentioned two approaches,
are more adaptable and offer a balanced approach to threat
detection. They increase the accuracy of identifying both
known and unknown threats.
Generative Adversarial Networks [27], a relatively re-
cent advancement in the realm of machine learning, are
applied in unsupervised learning tasks that primarily fo-
cused on generating data that resembles a given dataset.
They have found applications in many fields and industries
such as computer vision [28], natural language processing
[29], generative art [30], and anomaly detection[31]. GAN
models can be integrated into these intrusion detection sys-
tems to enhance their capabilities, as they can generate syn-
thetic data for training [32], improve feature extraction [33],
and address some of the challenges associated with both
signature-based and anomaly-based methods. For instance,
GANs offer the capability to produce varied synthetic attack
data. This empowers signature-based systems to adjust to
emerging attack patterns, thereby enhancing their accuracy
in identifying variations of known attacks. GANs can also
create synthetic normal traffic data, which can be used to
enrich the baseline of normal behavior in anomaly-based
systems.
GANs also have been utilized directly as network intru-
sion detection mechanisms. For instance, Patil et al. [34] in-
troduced a framework that leverages a bidirectional GAN for
anomaly detection. This framework was assessed using the
KDDCUP-99 dataset [35] and was subsequently compared
with other deep learning models to evaluate its performance.
Truong et al. [36] adopted two GAN models with newly de-
veloped neural networks for generators and discriminators.
They carried out extensive experiments based on datasets
such as CIC-IDS 2017 and UNSW-NB15 [37] to assess the
effectiveness of GANs, comparing them with established
unsupervised detection methods.
GAN models are also increasingly employed to generate
network traffic that closely mimics normal patterns but is, in
fact, malicious in nature, with the intent of evading intrusion
detection systems. For instance, Chauhan et al. [38] intro-
duced a GAN model for generating synthetic DDoS traffic.
This model dynamically alters the number of attack features
and swaps features with unused attack features in the training
set. As a result, the attacks they generated can effectively
evade detection by the IDS. Lin et al. [39] introduced a
framework based on GANs that possesses the ability to
transform original malicious network traffic into traffic that
mimics normal behavior while preserving the attack func-
tionalities.This framework dynamically learns the function-
ing of a real-time black-box detection system and employs
the modified attack traffic to effectively evade such detection
systems. In another study, Mustapha et al. [4] employed
a GAN model to align DDoS functional features with the
Page 2 of 12


---

Leveraging GANs for IDS Enhancement
distribution of benign sample features, effectively perturbing
the data. Their conclusion highlighted that the introduction
of perturbations in the input features significantly decreased
the performance of the IDS.
GANs have also demonstrated their applicability in
NIDS as a means to enhance their performance and ro-
bustness. For instance, Lee et al. [18] applied GANs to
generate network traffic, specifically targeting the mitigation
of the class imbalance problem commonly encountered in
NIDS datasets. Their research findings favored GANs over
conventional techniques like SMOTE [40]. Shahriar et al.
[32] employed an ANN-based GAN model for generating
synthetic samples. They then trained an IDS on both the syn-
thetic samples and the original ones, utilizing the NSL-KDD
dataset[41]. Their investigation revealed that the IDS model
incorporating GAN functions outperforms a standalone IDS
significantly in detecting attacks. Bourou et al. [42] used CT-
GAN [43], CopulaGAN [44], and TableGAN [45] models to
generate synthetic DoS attacks using the NSL-KDD datase
and concluded that the generated datasets are suitable for
training various machine learning models. In this ongoing
research, the primary focus lies in harnessing the power
of GAN models to improve the classification effectiveness
of an IDS. This approach involves the generation of larger
sets of attack samples, which are subsequently employed
to train the IDS. The current research distinguishes itself
from other related and recent studies in the literature such
as [18, 32, 42] in three significant ways. First, a relatively
new and highly advantageous dataset, CIC-IDS2017 is
leveraged. This dataset offers several key benefits, including
the inclusion of realistic network traffic, a substantial volume
of network data, and a wide spectrum of attack scenarios,
aligning closely with real-world conditions. Second, this
research utilizes multiple GAN models for generating spe-
cific attack samples. These generated attack samples are
further being assessed for their closeness to the original
samples, subjecting them to various testing and comparison
methodologies. Notably, the newly generated samples are
employed independently for training the IDS, and their
impact on enhancing IDS classification is evaluated. Third,
an exploration is conducted into the generation of diverse
quantities of attack samples, which are then integrated
separately into the CIC-IDS2017 dataset. This approach
facilitates the observation of scalability in IDS performance
enhancements across different sample sizes.
The adoption of this threefold approach distinguishes
the current research and contributes to a more compre-
hensive understanding of intrusion detection system perfor-
mance within the context of GAN-generated attack samples.
By broadening the scope of attack samples through GAN-
generated data, the aim is to create a more robust and
adaptive IDS, enhancing its capability to safeguard network
integrity and security against evolving and sophisticated
intrusion attempts.
3. Methodology
We start by introducing the CIC-IDS2017 dataset, out-
lining data processing methods, and categorizing (regroup-
ing) it into broader classes. Following this, we present an
IDS designed to classify these general classes, thereby es-
tablishing a baseline for the IDS’s performance. We then
delve into the fundamentals of GANs and describe three
GAN models that we’ve implemented in this study. Sub-
sequently, we elaborate on our approach to handling the
Botnet samples within the CIC-IDS2017 dataset and explain
how we generate new Botnet samples based on the original
dataset. Then, we outline the methodology employed to
assess the similarity between the generated and the original
samples. We subsequently integrate the newly generated
Botnet samples into the original dataset and observe the
resulting performance enhancements of the IDS. Figure 1
illustrates the entire process of enhancing the NIDS with
additional attack samples generated using GANs.
Dataset
CICIDS-2017
IDS Training
and Classification 
Generated Qualified
Botnet Samples
Trained IDS Testing on
Original Botnet Samples 
Performance
 Enhancements 
Botnet
Classification Results
Similarity Test (Original
VS Generated)
IDS Baseline Result
Identifying Augmentable 
Classes 
Gan Models Generating
Botnet Samples 
CICIDS-2017
w/o Original Botnet Samples
IDS Trainings and
Classifications
Figure 1: The Flow of Enhancing NIDS Performance with
GANs
3.1. The Dataset
The dataset employed in this research, namely the CIC-
IDS2017, is a publicly accessible dataset specifically de-
signed for evaluating and benchmarking intrusion detection
systems and network security solutions.
We have chosen the CIC-IDS2017 dataset for our re-
search experiments for several compelling reasons. Firstly,
this dataset is relatively new and encompasses a wide spec-
trum of network activities, including various types of attacks
and benign traffic. Given that our research primarily revolves
around generating a specific class of network attack samples
to enhance the classification performance of a multi-class
IDS, CIC-IDS2017 proves to be an ideal choice. Secondly,
CIC-IDS2017 has been available for a considerable amount
of time and has remained unchanged, ensuring stability and
consistency. This unchanging nature of the dataset serves
Page 3 of 12


---

Leveraging GANs for IDS Enhancement
Table 1
Processed CICIDS-2017 dataset.
Classes
Instances
Benign
2271320
DoS Hulk
230124
PortScan
158804
DDoS
128025
DoS GoldenEye
10293
FTP-Patator
7935
SSH-Patator
5897
DoS slowloris
5796
DoS Slowhttptest
5499
Bot
1956
Web Attack: Brute Force
1507
Web Attack: XSS
652
Infiltration
36
Web Attack: Sql Injection
21
Heartbleed
11
Table 2
Grouping of original classes into more general classes.
New Classes
Original Classes
Benign
Benign
Botnet
Bot
Brute Force
FTP-Patator
SSH-Patator
DDoS
DDoS
DoS
DoS GoldenEye
DoS Hulk
DoS Slowhttptest
DoS Slowloris
Heartbleed
Probe
ProtScan
Web Attack
Web Attack: Brute Force
Web Attack: SQL Injection
Web Attack: XSS
Infiltration
Infiltration
as a reliable reference point for our research. Lastly, CIC-
IDS2017 has gained widespread acceptance within the re-
search community. This widespread adoption facilitates easy
comparison of our results with the work of other researchers,
fostering knowledge sharing in the field.
After checking for and handling null values and infinity
values in the dataset - dropping any rows that contained NaN,
Null or Inf values - different class of network activities and
number of their instances are presented in Table 1.
To reduce the class imbalance issue within this dataset,
we adopted a similar approach as a prior study related
to CIC-IDS2017 [46]. This involved the re-labeling and
grouping of classes to create new (more general) classes.
The reasoning behind this choice arises from the observa-
tion that certain attack types share strong similarities, such
as Dos GoldenEye, Dos Hulk, DoS Slowloris, and DoS
Slowhttptest, which we grouped into a unified "Dos" class.
Additionally, even after this regrouping, we still had eight
distinct classes available for further researching in our study.
Table 3
New classes and their instances.
New Classes
Number of Instances
Benign
2271320
DoS
251723
Probe
158804
DDoS
128025
Brute Force
13832
Web Attack
2180
Botnet
1956
Infiltration
36
Table 4
Baseline IDS Classification performance.
New Classes
Precision
Recall
F1-Score
Benign
1.00
1.00
1.00
DoS
0.98
1.00
0.99
Probe
0.99
1.00
1.00
DDoS
1.00
1.00
1.00
Brute Force
1.00
1.00
1.00
Web Attack
0.99
0.97
0.98
Botnet
0.87
0.46
0.60
Infiltration
1.00
0.67
0.80
Table 2 shows how to form new classes based on the
original classes while Table 3 shows the new classes and
their number of instances.
3.2. The IDS Baseline and Motivation
Previous research [47, 48, 49] has established that the
utilization of Random Forest (RF) models as classifiers
can result in robust classification performance on the CIC-
IDS2017 dataset. In this study, a RF model is adopted as
well, for classifying the newly formed multiple classes. The
chi-squared (chi2) statistical test is employed as the scoring
function to select the top 32 features. In this baseline (the
ratio between the training set and testing set is 8 to 2), the
RF model reaches a classification accuracy of 0.9972, which
aligns closely with the findings of a prior investigation [49].
Table 4 offers further elaboration on the performance of
the IDS (the RF model), with metrics such as Precision, Re-
call, and F1-Score. It can be observed the IDS delivered high
classification performance for six out of the eight classes.
The two classes with lower classification performance are
Botnet and Infiltration, with precision, recall, and F1-score
values of 0.87, 0.46, 0.60 and 1.00, 0.67, 0.80, respectively.
From Table 3, it is observed that the instances for these two
classes are significant lesser than most of the other classes.
This highlights a significant challenge within the field of ma-
chine learning: the scarcity of available data. This scarcity
of data can pose a significant obstacle to achieving optimal
model performance. For the Infiltration class, there may
still be room for improvement in both recall and F1-score.
However, as previously mentioned, our strategy involves
utilizing GAN models to generate additional instances based
on original samples to enhance the IDS. Given that the
Infiltration class contains only 36 instances, when the dataset
Page 4 of 12


---

Leveraging GANs for IDS Enhancement
(CIC-IDS2017) has 78 features [50], therefore our ability to
enhance performance is constrained by the limited amount of
available data, as it poses a serious challenge (At least a few
hundred Infiltration samples which are several multiples of
the number of features may be needed to generate realistic
attack samples.) for GAN models to be able to effectively
acquire the knowledge required to generate convincing and
realistic samples.
On the other hand, the Botnet class consists of 1956
instances, presents a promising opportunity for enhancing
its classification performance. As a result, our primary focus
is directed toward this class, and we intend to harness GAN
models to generate additional synthetic instances exclusively
within this category.
3.3. The Basic GANs
A GAN consists of two neural networks, a generator and
a discriminator. The generator network is responsible for
producing new data instances that mimic a provided dataset.
The discriminator network evaluates whether a given data
instance belongs to the authentic dataset (real) or if it was
generated by the generator (fake).
During the training process of a GAN, a competitive
minimax game occurs between the generator and discrimi-
nator networks. The generator tries to produce data that is in-
creasingly more realistic to deceive the discriminator, while
the discriminator aims to improve its ability to differentiate
between real and fake data. As a result of this adversarial
process, the generator generates data that becomes progres-
sively more convincing over time and ultimately it is almost
indistinguishable from genuine data.
3.3.1. Vanilla GAN (GAN)
A GAN model that utilizes binary cross-entropy as its
loss function is commonly known as a Vanilla GAN [51] or
simply a GAN. In this model, the discriminator is tasked with
discerning between real and generated data. It produces an
output 𝐷(𝑥), which represents the probability that the input
𝑥is real (as opposed to generated). The discriminator’s loss
function is often represented as follows:
𝐿𝐷= −𝔼𝑥∼𝑝data(𝑥)[log 𝐷(𝑥)]−𝔼𝑥∼𝑝gen(𝑥)[log(1−𝐷(𝑥))] (1)
−𝔼𝑥∼𝑝data(𝑥)[log 𝐷(𝑥)] represents the expected value of
the logarithm of the discriminator’s output for real data.
It encourages the discriminator to assign high probabilities
(close to 1) to real data. While −𝔼𝑥∼𝑝gen(𝑥)[log(1 −𝐷(𝑥))]
represents the expected value of the logarithm of the com-
plement of the discriminator’s output for generated data.
It encourages the discriminator to assign low probabilities
(close to 0) to generated data.
The generator’s objective is to minimize the probability
that the discriminator correctly classifies the generated data
as fake, which is essentially the flip side of the discrimina-
tor’s objective. So, the generator’s loss function is:
𝐿𝐺= −𝔼𝑥∼𝑝gen(𝑥)[log 𝐷(𝑥)]
(2)
The generator tries to minimize the expected value of the
logarithm of the discriminator’s output for generated data.
Where:
𝐿𝐷= Discriminator’s loss
𝐿𝐺= Generator’s loss
𝑥= Data samples
𝑝data(𝑥) = Real data distribution
𝑝gen(𝑥) = Generated data distribution
𝐷(𝑥) = Discriminator’s output for data sample 𝑥
3.3.2. Wasserstein GAN (WGAN)
A WGAN [52] is a variant of traditional GANs that
introduces a new loss function. In a standard GAN, the
training process tries to minimize the binary cross-entropy
loss for discriminator and generator networks. However,
standard GANs can be challenging to train, as they suffer
from problems like mode collapse and vanishing gradients.
Wasserstein GANs address some of these challenges by
using the Wasserstein distance, alternatively recognized as
the Earth-Mover’s distance (EMD), serves as a loss func-
tion. This distance quantifies the lowest expense required to
transform one probability distribution into another.
The EMD between distributions 𝑃and 𝑄is defined as:
EMD(𝑃, 𝑄) = min
∑∑
𝑑(𝑖, 𝑗) ⋅𝑓(𝑖, 𝑗)
(3)
Where:
EMD(𝑃, 𝑄) = Earth-Mover’s Distance between 𝑃and 𝑄
𝑑(𝑖, 𝑗) = distance between data points (𝑖, 𝑗) from 𝑃and 𝑄
𝑓(𝑖, 𝑗) = amount of mass to be moved from 𝑖to 𝑗
(𝑖in 𝑃and 𝑗in 𝑄)
Utilizing the Wasserstein distance as the loss function in
GANs offers several advantages. First, it introduces contin-
uous and smooth gradients into the training process, thereby
enhancing training stability and mitigating issues like van-
ishing gradients. Moreover, the Wasserstein loss provides a
more informative metric for training evaluation. By quanti-
fying how closely the generated distribution aligns with the
real data distribution, it equips the generator with a clearer
objective: to produce samples that not only appear authentic
but also capture the underlying data distribution faithfully.
Additionally, Wasserstein GANs exhibit increased stability
throughout the training process. This enhanced stability
translates into faster convergence, ensuring that the model
learns more efficiently.
3.3.3. Wasserstein GAN with Gradient Penalty
(WGAN-GP)
A WGAN-GP model is a refinement of the WGAN
model. WGAN-GP replaces weight clipping with a gradient
penalty to enforce the Lipschitz constraint. This constraint
Page 5 of 12


---

Leveraging GANs for IDS Enhancement
helps in achieving a more stable training process and allows
for meaningful Wasserstein distance computation. More de-
tails about WGAN-GP can be found in [53].
3.4. The GAN Models and Settings in This Study
In this study, three distinct GAN models have been
deployed for the purpose of generating new attack instances
based on the CIC-IDS2017 dataset. The initial two models
comprise a Vanilla GAN and a WGAN, utilizing cross-
entropy and Wasserstein distance respectively as their loss
functions. A specialized generative model designed specifi-
cally for tabular data, known as Conditional Tabular GAN
(CTGAN) [54], constitutes the final model in the series.
This model excels in enabling conditional data generation,
with a focus on maintaining the statistical characteristics and
dependencies inherent in the original tabular dataset. In this
model, the generator loss function is bases on the Maximum
Mean Discrepancy (MMD), which measures the distinctions
between two distributions. While the discriminator loss is
based on the principles of WGAN-GP, emphasizing the
preservation of data quality and integrity during the genera-
tion process.
3.4.1. Implementation and Settings for Vanilla GAN
The generator comprises three fully connected layers,
with the initial layer consisting of 25 neurons, accepting
noise as input, applying the ReLU activation function, and
initialized using the He uniform initializer.
The second layer has 50 neurons with ReLU activation.
The last layer has as many units as there are features in the
continuous scaled data (depends on the features used), and it
uses sigmoid activation, which is typical for the output layer
when generating data between 0 and 1.
The discriminator has also three layers: The first layer
comprises of 50 neurons, with ReLU activation, and takes
the shape of the real data as the input. The second layer
has 100 neurons and uses ReLU activation. Then the final
layer has 1 neuron and uses a sigmoid activation. It outputs
a single value, which is interpreted as the probability that the
input data is real (as opposed to generated).
3.4.2. Implementation and Settings for WGAN
The implemented WGAN model shared similar settings
as the Vanilla GAN in this study, except that it utilise the
Wasserstein distance as its loss function.
3.4.3. Implementation and Settings for CTGAN
We utilized and made modifications to a CTGAN model,
which is originally based on the code available at https://
github.com/ydataai/ydata-synthetic. The generator has one
input layer, three hidden layers and one output layer. The
noise and the label data concatenated together as the input.
The first hidden layer with neurons number equals to the
input dimensionality (dim) and with ReLU as the activation.
The second hidden layer with dim * 2 neurons and ReLU
activation and the third hidden layer with dim * 4 neurons
and ReLU activation. The output layer generates synthetic
data with the specified dimensionality (the output dimen-
sionality).
The discriminator has also one input layer, three hidden
layers and one output layer. Input data and label data are
concatenated together as the input. The first hidden layer
with dim * 4 neurons and ReLU activation. A dropout layer
with a dropout rate of 0.1 is applied after the first hidden
layer. The second hidden layer with dim * 2 neurons and
ReLU activation. Another dropout layer with a dropout rate
of 0.1 is applied after the second hidden layer. The third
hidden layer with dim neurons and ReLU activation. The
output layer with a single neuron and sigmoid activation.
3.5. Processing Botnet samples from CIC-IDS2017
and Generating New Samples
Following the initial data processing, the original Botnet
dataset consisted of 1956 samples. To enhance the genera-
tion of realistic network traffic samples using GAN models,
we recognized the necessity to further divide and categorize
these samples. Initially, we classified the original Botnet
samples into two primary groups based on their destination
ports: those linked to port 8080 and those associated with
non-8080 port numbers. The choice of destination ports
serves as an indicator of the application protocol, each of
which possesses its distinct feature boundaries within net-
work traffic. It’s worth noting that a significant portion of
the Botnet samples were associated with port 8080, which
serves as an alternative port for the Hypertext Transfer
Protocol (HTTP).
In further refining the approach, these two primary
groups are further divided into smaller, more focused seg-
ments. The criterion for this division was straightforward:
it is observed that certain columns in the dataset predom-
inantly contained just two or three distinct values. We
tailored the dataset divisions to align with these observed
patterns, creating smaller, more homogenous segments.
These resulting smaller segments exhibited simplified data
distributions. Subsequently, we employed the three GAN
models to generate additional Botnet samples based on these
refined, more homogenous segments.
3.6. The Evaluation for Closeness
Three ways in this study were employed to quantify
the similarity (closeness) between the synthetic Botnet data
and the Botnet data from the original CIC-IDS2017 dataset,
more details will be provided in the following.
3.6.1. The Cosine Similarity
Cosine similarity [55] is a metric employed to gauge
the similarity between two non-zero vectors within an inner
product space, and it finds relevance in our specific context.
The closer its value is to 1, the greater the proximity between
the two vectors. In fact, when the value equals 1, it signifies
that the two vectors align perfectly in direction, indicating
an absolute similarity.
Page 6 of 12


---

Leveraging GANs for IDS Enhancement
Table 5
The Cosine Similarities Between Generated and Original Bot-
net Instances for 8 Features.
Features
GAN Models
Vallina GAN
WGAN
CTGAN
Feature 1
0.8979
0.8986
0.8295
Feature 2
0.7608
0.7607
0.5531
Feature 3
0.9673
0.9653
0.9147
Feature 4
0.9013
0.8977
0.8316
Feature 5
0.8962
0.8956
0.8520
Feature 6
0.9669
0.9655
0.8958
Feature 7
0.8750
0.8750
0.7001
Feature 8
0.9999
0.9999
0.9997
The generated samples exhibit a high level of similarity
to the originals, indicating the effectiveness of these mod-
els (the three GAN models) in preserving the key charac-
teristics of the original data. We have also observed that
Vanilla GAN and WGAN models exhibited similar per-
formance in terms of cosine similarity, and they outper-
formed the CTGAN model. In Table 5, we have provided
8 features (Flow_Duration, Total_Length_of_Fwd_Packets,
Flow_Packets_s, Fwd_ IAT_Mean, Bwd_IAT_Mean,
Fwd_Packets_s, Packet_Length_Mean, and
Init_Win_bytes_backward) and their corresponding cosine
similarity values between original Botnet samples and gener-
ated samples by GAN, WGAN and CTGAN models. While
there were more features available for selection, the primary
reason we chose these specific 8 features is their high degree
of representativeness.
3.6.2. Cumulative sums
Cumulative sums of a feature [56], achieved by ag-
gregating the values of a single feature, can also serve as
a means to quantify the closeness between generated and
initial samples. Upon comparing the cumulative sums of
features between the generated samples (produced by Vallila
GAN, WGAN, and CTGAN) and the original samples, we
observed a consistent close alignment. Furthermore, our
analysis led to the conclusion that Vallila GAN and WGAN
models exhibited similar performance in terms of cumula-
tive feature sums, surpassing the performance of CTGAN.
Figures 2 to 4 depict cumulative sums for the 8 features
we mentioned in the previous subsection (These are the same
eight features as presented in Table 5) within three distinct
groups.The blue lines are cumulative sums for samples
from the original Botnet samples while the orange lines are
cumulative sums for generated samples. We can observe
that, for WGAN and Vanilla GAN, the cumulative sums
of the eight selected features closely match between the
generated samples and the original Botnet data. However,
when considering CTGAN, there is a significant divergence
in the cumulative sums of certain features in comparison to
the original samples.
Figure 2: The cumulative sums for 8 features for GAN
generated and original Botnet samples.
3.6.3. Validating with ML Algorithms
Another approach in assessing the closeness between
generated samples and the original samples is to employ
machine learning algorithms. These algorithms (such as
Random Forest and Decision Tree) can provide valuable
insights into the quality and fidelity of the generated data
relative to the initial dataset.
We utilized GAN, WGAN, and CTGAN to generate
1,956 synthetic Botnet samples, mirroring our reference
dataset with the same number of original Botnet instances.
Additionally, we extracted two groups of 10,000 Benign
samples from the CIC-IDS2017 dataset.
In the first experiment, we combined 1,956 CTGAN-
generated samples with 10,000 Benign samples to form
a dataset (dataset 1). We also created another dataset by
combining the original 1,956 Botnet samples with another
set of 10,000 Benign samples (testing set). A random forest
model trained on 80% of dataset 1 achieved a precision,
recall, and F-score of 1.00. When tested on the testing set,
it maintained strong performance with a precision of 0.98,
recall of 0.94, and an F-score of 0.96.
The second experiment involved using 1,956 Vanilla
GAN-generated samples combined with the 10,000 Benign
samples (dataset 2). We applied the RF model with strong
Page 7 of 12


---

Leveraging GANs for IDS Enhancement
Figure 3: The cumulative sums for 8 features for WGAN
generated and original Botnet samples.
results: a precision of 1.00, a recall of 0.99, and an F-scores
of 1.00 on the remaining 20% of dataset 2. Applying the
model on the testing set yielded a precision of 0.99, recall
of 0.92, and an F-score of 0.95.
In the third experiment, we employed 1,956 WGAN-
generated samples combined with the 10,000 Benign sam-
ples(dataset 3). The RF model achieved all measure metrics
of 1.00 when tested on the remaining 20% of dataset 3.
Applying the model on the testing set resulted in a precision
of 0.99, recall of 0.96, and an F-score of 0.98.
Similar results were obtained using the Decision Tree
classifier. These experiments underscore the consistency of
the samples generated by the three GAN models, indicating
a high level of resemblance to the original samples.
4. Intrusion Detection Enhancement with
More Botnet Samples Generated
As we mentioned, we generate samples based on the
segments divided from the original Botnet samples. For
example, if we want to generate 1956 X 4 (4 times) Bot-
net samples with WGAN model. We will use the WGAN
model to generate proportionally more samples based on the
original divided segments. In this particular scenario, each
Figure 4: The cumulative sums for 8 features for CTGAN
generated and original Botnet samples.
segment of the samples will be generated four times in size
and subsequently assembled together.
We leveraged the three GAN models—WGAN, Vanilla
GAN, and CTGAN—to generate augmented sets of Botnet
samples. Each set comprised 1,956 samples, multiplied by
4, 49, and 99, respectively, were categorized into distinct
groups for the IDS enhancement evaluation.
4.1. Enhance with WGAN-Generated Samples
For the set which generated by the WGAN model sam-
ples, we separated these sample into three groups and eval-
uated them separately.
In the group I, we replaced the original 1,956 Botnet
samples in the processed CIC-IDS2017 dataset with four
times the originals (1956X4) of Botnet samples generated
by the WGAN model. Using the same RF model as in the
IDS baseline (as show in section 3.2, 8:2 ratio for training
and testing), we achieved strong Botnet classification re-
sults, with precision, recall, and F-score all exceeding 0.97.
Testing the RF model on the original 1,956 Botnet samples
resulted in a precision, recall and F-score of 1.00, 0.74 and
0.85, respectively.
In group II, here, we augmented the dataset with 49 times
the original number of samples, again replacing the 1,956
Page 8 of 12


---

Leveraging GANs for IDS Enhancement
Table 6
Classification Performance of the IDS on Generated Botnet
Samples.
Model (Numbers)
Precision
Recall
F1-Score
WGAN(4 times)
0.97
1.00
0.98
WGAN(49 times)
1.00
1.00
1.00
WGAN(99 times)
1.00
1.00
1.00
Vanilla GAN (4 times)
0.98
0.99
0.98
Vanilla GAN (49 times)
1.00
1.00
1.00
Vanilla GAN (99 times)
1.00
1.00
1.00
CTGAN (4 times)
0.99
0.68
0.81
CTGAN (49 times)
0.97
0.92
0.95
CTGAN (99 times)
0.95
0.99
0.97
Table 7
Trained IDS Performance on Original Botnet Samples.
Model (Numbers)
Precision
Recall
F1-Score
WGAN(4 times)
1.00
0.74
0.85
WGAN(49 times)
1.00
0.76
0.87
WGAN(99 times)
1.00
0.82
0.90
Vanilla GAN (4 times)
1.00
0.66
0.80
Vanilla GAN (49 times)
1.00
0.76
0.87
Vanilla GAN (99 times)
1.00
0.81
0.90
CTGAN (4 times)
1.00
0.43
0.60
CTGAN (49 times)
1.00
0.76
0.86
CTGAN (99 times)
1.00
0.77
0.87
original Botnet samples in the processed CIC-IDS2017
datase.The RF model exhibited good performance on the
generated samples, with all metrics reaching 1.00. When
tested on the original 1,956 Botnet samples, the RF model
achieved a precision, recall and F-score of 1.00, 0.76 and
0.87, respectively.
In group III, we employed 99 times the original number
of samples, again replacing the 1,956 original Botnet sam-
ples in the processed CIC-IDS2017 datase. The RF model
consistently delivered good results for Botnet classification,
with all metrics reaching 1.00. Testing this model on the
original 1,956 Botnet samples yielded a precision, recall and
F-score of 1.00, 0.82 and 0.90, respectively. More details can
be found in Tables 6 and 7.
4.2. Enhance with Other Two GAN-Generated
Samples
We conducted parallel experiments with Vanilla GAN
and CTGAN generated samples following a similar protocol
as the WGAN experiments. Performance metrics for Botnet
classification were evaluated for each group, both on the
generated samples and the original 1,956 Botnet samples.
Additional details can be found in Tables 6 and 7.
5. Discussion
Based on the analysis of the preceding subsections, it
is evident that increasing the number of generated Botnet
samples in training, results in a significant performance im-
provement for classifying these generated Botnet instances.
These experiments aimed to demonstrate the potential of
augmenting the dataset with GAN-generated Botnet samples
to enhance intrusion detection. The results showcase the
increased volume of data and its impact on model perfor-
mance, with each GAN model offering distinct advantages.
For instance, when using both WGAN and Vanilla GAN
and augmenting the dataset with forty-nine and ninety-nine
times the generated samples, the IDS achieved flawless clas-
sification, with precision, recall, and F1-scores all reaching
the maximum value of 1. This trend can be observed from
Table 6, and note that in these cases, the IDS was trained
using augmented datasets and subsequently tested on the
generated datasets.
More importantly, with the generation of a larger vol-
ume of Botnet samples using the three GAN models, the
IDS demonstrated enhanced training effectiveness. Table
7 presents the classification results for the original 1956
Botnet samples, achieved by training the IDS with aug-
mented datasets of more generated Botnet samples using
three different GAN models. For example, upon incorpo-
rating ninety-nine Botnet samples (WGAN generated) into
the training dataset, the IDS exhibited considerable per-
formance improvements. These improvements were evident
in the precision score, which reached a perfect 1.00 (a
notable 13% enhancement), a recall of 0.81 (a substantial
35% improvement), and an F1-score of 0.90 (a substantial
30% improvement) when classifying the original set of 1956
Botnet samples. This represents a significant leap from the
baseline results, where precision was at 0.87, recall at 0.46,
and the F1-score at 0.60, as the results clearly indicate. These
findings underscore the substantial progress in the IDS’s
training, enabling it to successfully detect previously elusive
samples.
Another intriguing observation is that, in the cases of
both the WGAN and Vanilla GAN models, the IDS ex-
periences substantial improvement even when only four
times the number of samples are generated for training, as
compared to the IDS baseline. However, it’s noteworthy that
when we increased the volume to forty-nine and ninety-nine
times, the IDS’s performance demonstrated further enhance-
ments, although these improvements were not as substantial
as the initial fourfold increase. This trend could be attributed
to the diminishing returns associated with the increased vol-
ume of generated data, where the initial increase yields more
significant gains in performance compared to subsequent
increments.
Concerning the samples generated by CTGAN models,
a noticeable trend in IDS enhancement was also evident.
However, it is worth noting that these enhancements are
comparatively less pronounced when compared to the im-
provements seen with the samples generated by the other
two GAN models. It’s worth highlighting that when using
only four times the number of original samples (1956X4),
the improvement in IDS classification remains rather limited
when compared to the baseline. This could because CT-
GAN generated samples have less closeness or similarities
(implied in Table 5 and Figure 4) to the original Botnet
Page 9 of 12


---

Leveraging GANs for IDS Enhancement
samples from the CIC-IDS 2017, as compared to the WGAN
and Vanilla GAN models. Notably, when we increased the
volume to forty-nine times, the IDS exhibited significant
enhancements. However, it’s interesting to observe that the
incremental benefit of generating ninety-nine times the sam-
ples over the forty-nine times case was almost negligible.
The reduced efficacy (for IDS performance enhance-
ment) of the Botnet samples generated by CTGAN mod-
els, in contrast to the more effective results observed with
WGAN and Vanilla GAN models, can likely be attributed
to the specific approach employed in the generation pro-
cess. In our approach, the original Botnet samples were
divided into smaller segments, and new attack samples were
subsequently generated proportionally based on these frag-
mented components. Within each of these smaller segments,
it was common to encounter many columns with consistent,
singular values. These single values within the segments
contributes to the simplification of their distributions. The
increased sophistication of CTGAN model, in comparison
to WGAN and Vanilla GAN models, does not inherently
guarantee its effectiveness in handling simpler distributions
when contrasted with the capabilities of WGAN and Vanilla
GAN models.
We would like to underscore an important point: as
we augment our dataset by generating a larger volume of
samples and incorporating them into the original dataset
(CIC-IDS2017) for training our IDS, its performance in
identifying classes other than Botnet exhibits consistent
stability. Specifically, the Web Attack and Infiltration classes
are the only ones showing a marginal impact, with any
enhancements falling within a 4% range. This stable perfor-
mance holds true across all the scenarios involving different
GAN models and varying numbers of Botnet samples used
during IDS training. However, the marginal improvements
observed in these two classes may be more attributable to
the effects of an increased number of Botnet samples rather
than genuine performance enhancements. Table 8. shows
the classification performance when we generated 99 times
the original 1956 Botnet samples and replaced them with
the original 1956 samples in the dataset to train the IDS.
Comparing these results to those in Table 4, minor variations
in the Recall and F1-score metrics are noticeable for the
Infiltration class, alongside a slight modification in the Re-
call value for the Web Attack class. This observation holds
significant importance because if the IDS classification per-
formance for other classes had been impacted significantly
during the process, it could have raised questions about the
validity of our research methodology. However, since we
have confirmed that the IDS’s performance for other classes
remained stable, it reinforces our confidence in the feasibility
of creating more precise samples tailored to the Botnet class.
This, in turn, opens up an exciting opportunity to enhance the
IDS’s performance specifically for this class of cyber threats.
In the current research, an RF model was utilized as
the IDS, training it on the GAN-augmented CIC-IDS2017
dataset. This approach yielded outstanding results, with a
precision of 1.00, a recall of 0.82, and an F1-score of 0.90
Table 8
Classification performance with 1956X99 WGAN Generated
Botnet Samples.
Class
Precision
Recall
F1-Score
Benign
1.00
1.00
1.00
DoS
0.98
1.00
0.99
Probe
0.99
1.00
1.00
DDoS
1.00
1.00
1.00
Brute Force
1.00
1.00
1.00
Web Attack
0.99
0.98
0.98
Botnet
1.00
1.00
1.00
Infiltration
1.00
0.71
0.83
when applied to the original Botnet samples. These results
signify a noteworthy advancement and, to the best of our
knowledge, establish a new benchmark as the current best-
reported performance in the literature. For example, Ke-
serwani et al. [57] harnessed both Grey Wolf Optimization
and Particle Swarm Optimization to extract features from
the CIC-IDS2017 dataset. These extracted features were
then fed into an RF classifier, resulting with a precision of
1.00, a recall of 0.60, and an F1-score of 0.75 for Botnet
classification. Lee et al. [18] employed a GAN model to
generate 10,000 Botnet samples, which were integrated into
the CIC-IDS2017 dataset. Using an RF as their IDS, they
reached a precision of 0.86, a recall of 0.53, and an F1-score
of 0.66 for Botnet classification.
6. Conclusion
To address the critical challenge of data scarcity in NIDS
training datasets, we have introduced a novel approach that
integrates GANs into the NIDS framework. Our approach
involves the development and implementation of three dis-
tinct GAN models that generate synthetic network traffic
data, closely mimicking real-world network behavior while
targeting specific predefined anomalous activities. Through
extensive experimentation on a benchmark dataset (CIC-
IDS2017) and generated datasets, we have demonstrated the
efficacy of our proposed approach in NIDS classification
enhancement. Our findings indicate that the integration of
GANs into NIDS systems can lead to enhancements in
intrusion detection performance, enabling the detection of
previously undetected intrusion attempts. This research con-
tributes to the continuous evolution of NIDS and shows the
importance of adapting to the ever-changing landscape of
cyber threats. As cyberattacks become increasingly sophis-
ticated, the incorporation of GANs in NIDS represents a
proactive and effective strategy for enhancing the security
of digital infrastructures, thereby fortifying organizations
against potential intrusions and data breaches.
References
[1] B. Hussain, Q. Du, B. Sun, Z. Han, Deep learning-based ddos-
attack detection for cyber–physical system over 5g network, IEEE
Transactions on Industrial Informatics 17 (2) (2020) 860–870.
Page 10 of 12


---

Leveraging GANs for IDS Enhancement
[2] B. Gupta, P. Chaudhary, X. Chang, N. Nedjah, Smart defense against
distributed denial of service attack in iot networks using supervised
learning classifiers, Computers & Electrical Engineering 98 (2022)
107726.
[3] V. Kampourakis, V. Gkioulos, S. Katsikas, A systematic literature
review on wireless security testbeds in the cyber-physical realm,
Computers & Security (2023) 103383.
[4] A. Mustapha, R. Khatoun, S. Zeadally, F. Chbib, A. Fadlallah,
W. Fahs, A. El Attar, Detecting ddos attacks using adversarial neural
network, Computers & Security 127 (2023) 103117.
[5] C. Beaman, A. Barkworth, T. D. Akande, S. Hakak, M. K. Khan, Ran-
somware: Recent advances, analysis, challenges and future research
directions, Computers & security 111 (2021) 102490.
[6] X. Zhao, C. S. Veerappan, P. K. Loh, Z. Tang, F. Tan, Multi-agent
cross-platform detection of meltdown and spectre attacks, in: 2018
15th International Conference on Control, Automation, Robotics and
Vision (ICARCV), IEEE, 2018, pp. 1834–1838.
[7] M. Conti, N. Dragoni, V. Lesyk, A survey of man in the middle
attacks, IEEE communications surveys & tutorials 18 (3) (2016)
2027–2051.
[8] Z. Ahmad, A. Shahid Khan, C. Wai Shiang, J. Abdullah, F. Ahmad,
Network intrusion detection system: A systematic study of machine
learning and deep learning approaches, Transactions on Emerging
Telecommunications Technologies 32 (1) (2021) e4150.
[9] M. Vishwakarma, N. Kesswani, Dids: A deep neural network based
real-time intrusion detection system for iot, Decision Analytics Jour-
nal 5 (2022) 100142.
[10] H. Chindove, D. Brown, Adaptive machine learning based network
intrusion detection, in: Proceedings of the International Conference
on Artificial Intelligence and its Applications, 2021, pp. 1–6.
[11] M. Injadat, A. Moubayed, A. B. Nassif, A. Shami, Multi-stage opti-
mized machine learning framework for network intrusion detection,
IEEE Transactions on Network and Service Management 18 (2)
(2020) 1803–1816.
[12] Z. Wang, V. L. Thing, Feature mining for encrypted malicious traffic
detection with deep learning and other machine learning algorithms,
Computers & Security 128 (2023) 103143.
[13] A. Afianian, S. Niksefat, B. Sadeghiyan, D. Baptiste, Malware dy-
namic analysis evasion techniques: A survey, ACM Computing Sur-
veys (CSUR) 52 (6) (2019) 1–28.
[14] G. Raja, S. Anbalagan, G. Vijayaraghavan, S. Theerthagiri, S. V.
Suryanarayan, X.-W. Wu, Sp-cids: Secure and private collaborative
ids for vanets, IEEE Transactions on Intelligent Transportation Sys-
tems 22 (7) (2020) 4385–4393.
[15] L. Yang, A. Moubayed, A. Shami, Mth-ids: A multitiered hybrid
intrusion detection system for internet of vehicles, IEEE Internet of
Things Journal 9 (1) (2021) 616–632.
[16] A. Binbusayyis, T. Vaiyapuri, Unsupervised deep learning approach
for network intrusion detection combining convolutional autoencoder
and one-class svm, Applied Intelligence 51 (10) (2021) 7094–7108.
[17] C. Liu, R. Antypenko, I. Sushko, O. Zakharchenko, Intrusion detec-
tion system after data augmentation schemes based on the vae and
cvae, IEEE Transactions on Reliability 71 (2) (2022) 1000–1010.
[18] J. Lee, K. Park, Gan-based imbalanced data intrusion detection sys-
tem, Personal and Ubiquitous Computing 25 (2021) 121–128.
[19] B. A. Tama, S. Lim, Ensemble learning for intrusion detection sys-
tems: A systematic mapping study and cross-benchmark evaluation,
Computer Science Review 39 (2021) 100357.
[20] A. Thakkar, R. Lohiya, A survey on intrusion detection system:
feature selection, model, performance measures, application perspec-
tive, challenges, and future research directions, Artificial Intelligence
Review 55 (1) (2022) 453–563.
[21] I. Sharafaldin, A. H. Lashkari, A. A. Ghorbani, Toward generating a
new intrusion detection dataset and intrusion traffic characterization.,
ICISSp 1 (2018) 108–116.
[22] N. Hubballi, V. Suryanarayanan, False alarm minimization techniques
in signature-based intrusion detection systems: A survey, Computer
Communications 49 (2014) 1–17.
[23] A. Khraisat, I. Gondal, P. Vamplew, J. Kamruzzaman, Survey of
intrusion detection systems: techniques, datasets and challenges, Cy-
bersecurity 2 (1) (2019) 1–22.
[24] J. Jabez, B. Muthukumar, Intrusion detection system (ids): Anomaly
detection using outlier detection approach, Procedia Computer Sci-
ence 48 (2015) 338–346.
[25] R. D. Ravipati, M. Abualkibash, Intrusion detection system classi-
fication using different machine learning algorithms on kdd-99 and
nsl-kdd datasets-a review paper, International Journal of Computer
Science & Information Technology (IJCSIT) Vol 11 (2019).
[26] A. K. Dalai, S. K. Jena, Hybrid network intrusion detection systems:
a decade’s perspective, in: Proceedings of the International Confer-
ence on Signal, Networks, Computing, and Systems: ICSNCS 2016,
Volume 1, Springer, 2017, pp. 341–349.
[27] I. Goodfellow, J. Pouget-Abadie, M. Mirza, B. Xu, D. Warde-Farley,
S. Ozair, A. Courville, Y. Bengio, Generative adversarial nets, Ad-
vances in neural information processing systems 27 (2014).
[28] M. A. Özkanoğlu, S. Ozer, Infragan: A gan architecture to transfer
visible images to infrared domain, Pattern Recognition Letters 155
(2022) 69–76.
[29] G. Liang, B.-W. On, D. Jeong, A. A. Heidari, H.-C. Kim, G. S. Choi,
Y. Shi, Q. Chen, H. Chen, A text gan framework for creative essay
recommendation, Knowledge-Based Systems 232 (2021) 107501.
[30] M. Civit, J. Civit-Masot, F. Cuadrado, M. J. Escalona, A systematic
review of artificial intelligence-based music generation: Scope, appli-
cations, and future trends, Expert Systems with Applications (2022)
118190.
[31] T. Schlegl, P. Seeböck, S. M. Waldstein, G. Langs, U. Schmidt-
Erfurth, f-anogan: Fast unsupervised anomaly detection with genera-
tive adversarial networks, Medical image analysis 54 (2019) 30–44.
[32] M. H. Shahriar, N. I. Haque, M. A. Rahman, M. Alonso, G-ids:
Generative adversarial networks assisted intrusion detection system,
in: 2020 IEEE 44th Annual Computers, Software, and Applications
Conference (COMPSAC), IEEE, 2020, pp. 376–385.
[33] Y. Zhu, L. Cui, Z. Ding, L. Li, Y. Liu, Z. Hao, Black box attack
and network intrusion detection using machine learning for malicious
traffic, Computers & Security 123 (2022) 102922.
[34] R. Patil, R. Biradar, V. Ravi, P. Biradar, U. Ghosh, Network traffic
anomaly detection using pca and bigan, Internet Technology Letters
5 (1) (2022) e235.
[35] M. Tavallaee, E. Bagheri, W. Lu, A. A. Ghorbani, A detailed analysis
of the kdd cup 99 data set, in: 2009 IEEE symposium on computa-
tional intelligence for security and defense applications, Ieee, 2009,
pp. 1–6.
[36] T. Truong-Huu, N. Dheenadhayalan, P. Pratim Kundu, V. Ramnath,
J. Liao, S. G. Teo, S. Praveen Kadiyala, An empirical study on
unsupervised network anomaly detection using generative adversarial
networks, in: Proceedings of the 1st ACM Workshop on Security and
Privacy on Artificial Intelligence, 2020, pp. 20–29.
[37] N. Moustafa, J. Slay, Unsw-nb15: a comprehensive data set for net-
work intrusion detection systems (unsw-nb15 network data set), in:
2015 military communications and information systems conference
(MilCIS), IEEE, 2015, pp. 1–6.
[38] R. Chauhan, S. S. Heydari, Polymorphic adversarial ddos attack
on ids using gan, in: 2020 International Symposium on Networks,
Computers and Communications (ISNCC), IEEE, 2020, pp. 1–6.
[39] Z. Lin, Y. Shi, Z. Xue, Idsgan: Generative adversarial networks for at-
tack generation against intrusion detection, in: Pacific-asia conference
on knowledge discovery and data mining, Springer, 2022, pp. 79–91.
[40] Y. Zhang, Q. Liu, On iot intrusion detection based on data aug-
mentation for enhancing learning on unbalanced samples, Future
Generation Computer Systems 133 (2022) 213–227.
[41] A. Tabassum, A. Erbad, W. Lebda, A. Mohamed, M. Guizani, Fedgan-
ids: Privacy-preserving ids using gan and federated learning, Com-
puter Communications 192 (2022) 299–310.
[42] S. Bourou, A. El Saer, T.-H. Velivassaki, A. Voulkidis, T. Zahariadis,
A review of tabular data synthesis using gans on an ids dataset,
Information 12 (09) (2021) 375.
Page 11 of 12


---

Leveraging GANs for IDS Enhancement
[43] L. Xu, M. Skoularidou, A. Cuesta-Infante, K. Veeramachaneni, Mod-
eling tabular data using conditional gan, in: Advances in Neural
Information Processing Systems, 2019.
[44] D. Upadhyay, Q. Luo, J. Manero, M. Zaman, S. Sampalli, Compar-
ative analysis of tabular generative adversarial network (gan) mod-
els for generation and validation of power grid synthetic datasets,
in: IEEE EUROCON 2023-20th International Conference on Smart
Technologies, IEEE, 2023, pp. 677–682.
[45] N. Park, M. Mohammadi, K. Gorde, S. Jajodia, H. Park, Y. Kim, Data
synthesis based on generative adversarial networks, Proceedings of
the VLDB Endowment 11 (10) (2018) 1071–1083.
[46] R. Panigrahi, S. Borah, A detailed analysis of cicids2017 dataset
for designing intrusion detection systems, International Journal of
Engineering & Technology 7 (3.24) (2018) 479–482.
[47] V. Priyanka, T. Gireesh Kumar, Performance assessment of ids based
on cicids-2017 dataset, in: Information and Communication Technol-
ogy for Competitive Strategies (ICTCS 2020) ICT: Applications and
Social Interfaces, Springer, 2022, pp. 611–621.
[48] B. Reis, E. Maia, I. Praça, Selection and performance analysis
of cicids2017 features importance, in: International Symposium on
Foundations and Practice of Security, Springer, 2019, pp. 56–71.
[49] D. Stiawan, M. Y. B. Idris, A. M. Bamhdi, R. Budiarto, et al., Cicids-
2017 dataset feature analysis with information gain for anomaly
detection, IEEE Access 8 (2020) 132911–132921.
[50] Y. Zhou, G. Cheng, S. Jiang, M. Dai, Building an efficient intrusion
detection system based on feature selection and ensemble classifier,
Computer networks 174 (2020) 107247.
[51] A. Dunmore, J. Jang-Jaccard, F. Sabrina, J. Kwak, A comprehensive
survey of generative adversarial networks (gans) in cybersecurity
intrusion detection, IEEE Access (2023).
[52] M. Arjovsky, S. Chintala, L. Bottou, Wasserstein generative adver-
sarial networks, in: International conference on machine learning,
PMLR, 2017, pp. 214–223.
[53] I. Gulrajani, F. Ahmed, M. Arjovsky, V. Dumoulin, A. C. Courville,
Improved training of wasserstein gans, Advances in neural informa-
tion processing systems 30 (2017).
[54] L. Xu, M. Skoularidou, A. Cuesta-Infante, K. Veeramachaneni, Mod-
eling tabular data using conditional gan, Advances in neural informa-
tion processing systems 32 (2019).
[55] Z. Wang, Z. Yang, X. Song, H. Zhang, B. Sun, J. Zhai, S. Yang,
Y. Xie, P. Liang, Raman spectrum model transfer method based on
cycle-gan, Spectrochimica Acta Part A: Molecular and Biomolecular
Spectroscopy 304 (2024) 123416.
[56] Z. Liu, J. Hu, Y. Liu, K. Roy, X. Yuan, J. Xu, Anomaly-based intrusion
on iot networks using aigan-a generative adversarial network, IEEE
Access (2023).
[57] P. K. Keserwani, M. C. Govil, E. S. Pilli, P. Govil, A smart anomaly-
based intrusion detection system for the internet of things (iot)
network using gwo–pso–rf model, Journal of Reliable Intelligent
Environments 7 (2021) 3–21.
Page 12 of 12
