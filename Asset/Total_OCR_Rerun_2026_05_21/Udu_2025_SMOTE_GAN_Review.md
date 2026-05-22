Received 4 April 2025, accepted 20 June 2025, date of publication 1 July 2025, date of current version 9 July 2025.
Digital Object Identifier 10.1109/ACCESS.2025.3584532
Emerging SMOTE and GAN Variants for Data
Augmentation in Imbalance Machine Learning
Tasks: A Review
AMADI G. UDU
1,2, MARWAH T. SALMAN
1,3, (Member, IEEE), MARYAM K. GHALATI1,
ANDREA LECCHINI-VISINTINI
4, DAVID R. SIDDLE
1, AND HONGBIAO DONG
1
1School of Engineering, University of Leicester, LE1 7RH Leicester, U.K.
2Air Force Institute of Technology, Kaduna PMB 2104, Nigeria
3School of Engineering, Wasit University, Wasit 52001, Iraq
4School of Electronics and Computer Science, University of Southampton, SO17 1BJ Southampton, U.K.
Corresponding author: Amadi G. Udu (agu1@le.ac.uk)
This work was supported in part by the Iraqi Prime Minister’s Office, the Higher Committee of Education and Development in Iraq
(HCED), the Petroleum Technology Development Fund, Nigeria; and in part by the NISCO U.K. Research Centre, School of Engineering,
University of Leicester.
ABSTRACT Class imbalance is a pervasive challenge in real-world machine learning (ML) applications,
where the minority class, often the class of interest, is significantly underrepresented. This imbalance can
degrade model performance, result in misleading evaluation metrics, and complicate validation processes.
Two prominent data-augmentation techniques to address class imbalance are the Synthetic Minority
Oversampling Technique (SMOTE) and Generative Adversarial Networks (GAN). However, both techniques
have inherent limitations, motivating the emergence of novel variants designed to overcome these challenges.
While previous reviews have typically focused on specific domains, conventional methodologies, or broad
strategy overviews, this review presents a unified taxonomy that outlines the causes, types, and implications
of class imbalance across diverse ML tasks. It further examines emerging trends in the application of
SMOTE and GAN techniques, their limitations, and hybrid adaptations. By categorising imbalance types and
analysing models, metrics, datasets, and comparative approaches, this review provides actionable insights
and identifies future research directions for practitioners and researchers working to address class imbalance
in real-world ML tasks.
INDEX TERMS Class imbalance, data-augmentation, generative adversarial networks, machine learning,
SMOTE.
I. INTRODUCTION
A dataset with a skewed distribution between majority and
minority samples is often described as exhibiting class
imbalance. This issue is prevalent in many real-world
scenarios, such as in fraud detection [1], [2], where fraudulent
transactions are much rarer than legitimate ones; medical
diagnosis [3], [4], [5], [6], where some diseases occur
infrequently; aero-engine fault prediction [7], [8], [9], [10];
and industrial material forecasting [11], [12], [13], [14],
[15]. Class imbalance poses significant challenges during
The associate editor coordinating the review of this manuscript and
approving it for publication was Vlad Diaconita
.
model training, often biasing the model towards the majority
class. This reduces the model’s ability to accurately predict
instances of the minority class, ultimately diminishing the
overall performance of machine learning (ML) models.
Addressing class imbalance is critical because key factors
that impact model performance, evaluation metrics, and
validation process. ML models are typically optimised for
balanced datasets, making them inherently biased towards
the majority class [16], [17]. This bias can lead to poor
performance in recognising patterns in the minority class.
For example, in medical diagnosis, a model might accurately
identify common conditions but struggle to detect rare
diseases, resulting in missed diagnoses or false negatives.
113838
 2025 The Authors. This work is licensed under a Creative Commons Attribution 4.0 License.
For more information, see https://creativecommons.org/licenses/by/4.0/
VOLUME 13, 2025


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
Similarly, in fraud detection, the model may frequently
overlook fraudulent transactions because the dataset is
dominated by legitimate ones, thereby increasing the risk of
undetected fraud.
Standard performance metrics such as accuracy can be
misleading in the presence of class imbalance. A model
might achieve high overall accuracy simply by consistently
predicting the majority class, while failing to identify
instances from the minority class. For instance, in a credit
scoring system where defaults are rare, a model might report
high accuracy yet fail to predict actual defaults, making it
ineffective for risk management. This example illustrates how
relying solely on accuracy can obscure the true performance
of a model in critical areas. Validating models in the
presence of class imbalance presents significant challenges,
especially where there exists a scarcity in minority class
samples in the validation set. In wildlife monitoring, for
example, models may appear to perform well simply because
the dataset is dominated by common species, while rare,
endangered species remain underrepresented and poorly
predicted. This can cause the model to rely on the majority
class (non-endangered species) for its predictions, inflating
the perception of its ability to generalise to unseen data.
Even metrics designed for imbalanced datasets may fail to
fully address this issue, as they might not effectively capture
the model’s effectiveness on minority classes (endangered
species) [18], [19].
Multiple strategies have been proposed for addressing class
imbalance in ML problems and these can be divided into
two primary categories, namely algorithm-level and data-
level methods. Algorithm-level techniques [20], [21] focus on
modifying how the model learns from the dataset and evalu-
ation metrics in tackling issues that influence model perfor-
mance due to imbalance. Techniques under algorithm-level
include cost-sensitive learning [22], [23], [24], [25], [26]
boundary shifting, multi-objective optimisations, ensemble
and kernel specific methods. Algorithm-level techniques
however risk overfitting the minority class and faces
challenges in accurately quantifying misclassification costs,
while ensemble methods can become computationally expen-
sive and still struggle with extreme imbalances [27], [28].
These limitations highlight the need for data-augmentation
techniques, and hybrid approaches that leverage the strengths
of algorithm-level techniques in generating synthetic samples
to balance datasets, improving model generalisation, and
reducing overfitting, thus providing a more effective solution
for handling class imbalance in real-world ML tasks [29],
[30]. Two emerging techniques that have received signif-
icant focus for addressing class imbalance in ML tasks
are Synthetic Minority Oversampling Technique (SMOTE)
and Generative Adversarial Networks (GAN). This review
not only considers the characteristics and applications of
SMOTE and GAN but also delves into their limitations,
hybrid variants, and emerging trends, offering fresh insights
into their potential for addressing class imbalance in ML
tasks.
While previous reviews have significantly advanced the
understanding of class imbalance, many have understandably
concentrated on specific application domains, such as
medicine or fault diagnosis, or have focused on particular
strategies like cost-sensitive learning [22], [31], [32]. Broader
surveys and more recent reviews [33], [34], [35], [36]
have provided valuable overviews of current approaches.
However, these often offer limited coverage of emerging
data-augmentation techniques—such as SMOTE and GAN
variants—and do not fully consolidate foundational insights
into the causes, types, and implications of class imbalance.
This review fills that gap by presenting a harmonised
taxonomy that captures the underlying characteristics of
imbalance—its origins, forms, and effects—across diverse
ML contexts. To the best of our knowledge, this is the first
review to systematically establish these concepts alongside an
in-depth exploration of emerging SMOTE and GAN variants.
This approach not only clarifies key foundational issues but
also lays the groundwork for more informed applications of
data-augmentation strategies in real-world ML tasks.
The rest of this work is structured as follows: Section II
highlights the strategy and research questions that guides
the review, while Section III presents a taxonomy of class
imbalance, outlining its causes, types, and implications. Data-
augmentation techniques are discussed in Section IV and
performance metrics for evaluating models for the emerging
variants are presented in Section V. Discussion and future
studies are provided in Sections VI, with conclusions in
Section VII.
II. REVIEW STRATEGY
This review explores the growing field of data augmentation
for class imbalance in ML, with a specific focus on emerging
SMOTE and GAN variants. To ensure a comprehensive and
current analysis, studies were sourced from leading academic
databases, including IEEE Xplore, SpringerLink, Elsevier
(ScienceDirect), MDPI, Scopus, and Google Scholar. The
review emphasises recent advancements, prioritising works
published between 2020 and 2024 to capture the latest inno-
vations and insights. The search process employed targeted
keywords such as ‘‘class imbalance,’’ ‘‘imbalanced data,’’
‘‘data augmentation,’’ ‘‘SMOTE,’’ ‘‘GAN,’’ ‘‘synthetic sam-
ple generation,’’ ‘‘oversampling,’’ ‘‘undersampling,’’ ‘‘hybrid
techniques,’’ and ‘‘imbalanced classification.’’ A total of
61 peer-reviewed studies were selected, many of which are
indexed in high-impact journals listed in Scimago Journal
Rank (ScimagoJR), ensuring both quality and relevance.
These references encompass foundational methods, recent
adaptations, and domain-specific innovations, offering a
well-rounded and in-depth overview of the field. This strategy
not only presents a clear picture of the current state of
data augmentation in imbalanced learning tasks but also
highlights existing research gaps, setting the stage for future
exploration.
This study addresses key research questions (RQ) that
encompass critical aspects of the imbalanced data problem
VOLUME 13, 2025
113839


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
and the role of emerging SMOTE and GAN variants in data
augmentation:
1) RQ1: What are the causes, types, and implications of
class imbalance in ML?
2) RQ2: What are the emerging trends in SMOTE and
GAN-based data augmentation for addressing class
imbalance in real-world ML tasks?
3) RQ3: How do SMOTE and GAN-based variants
compare in terms of effectiveness, adaptability, and
performance when applied to imbalanced ML tasks
across different domains?
4) RQ4: How is the performance of emerging data-
augmentation variants evaluated, and what practical
limitations and opportunities for future research have
been identified?
Section III of this review answers the RQ1, while Section IV
offers insights into RQ2 and RQ3. Finally, Sections V
and VI of the review addresses RQ4 by highlighting how
performance is measured and outlining potential areas for
continued research.
III. TAXONOMY OF IMBALANCE: CAUSES, TYPES, AND
IMPLICATIONS
Class imbalance in real-world scenarios arises from various
factors tied to the characteristics of specific application
domains. The rarity of certain events or conditions—such as
diseases, manufacturing defects, or fraudulent transactions—
naturally leads to fewer instances of the minority class [1],
[2], [3]. In the medical domain, for example, datasets often
overrepresent prevalent conditions while underrepresenting
rarer but clinically significant ones [3], [5]. Similarly, in fraud
detection, the vast majority of transactions are legitimate,
resulting in highly skewed datasets [1], [2]. Data collection
practices can also introduce or exacerbate imbalance. These
include oversampling of majority classes or under-sampling
of minority classes—either intentionally for efficiency or
inadvertently during preprocessing. In high-risk domains
such as aero-engine fault diagnosis, collecting real-world
fault data is particularly resource-intensive, which limits the
availability of minority class samples [7], [9], [10].
In
some
cases,
events
like
seasonal
illnesses
or
context-specific fraud occur only under particular conditions,
resulting in temporary or situational imbalances if the data
collection is not comprehensive. Other domains, such as
customer segmentation or object detection, may exhibit
intrinsic or evolving imbalance. For instance, a small subset
of customers may account for most purchases, or some
object categories may occur much less frequently in visual
datasets [16]. Recognising these domain-specific causes of
class imbalance is critical for selecting appropriate data-
augmentation strategies, ensuring robust and generalisable
ML models.
From a typological standpoint, one form of imbalance
is known as Intrinsic imbalance, which stems from the
natural occurrence of the dataset being studied. This is
especially common in medical datasets, where the number
of healthy patients far exceeds those diagnosed with a
specific condition. Also, certain disease condition being
studied (e.g. Huntington’s disease) are inherently rare when
compared to more common conditions like hypertension
[37], [38]. In such cases, the imbalance in the dataset
reflects the actual distribution of conditions in the real-
world. By contrast, Extrinsic imbalance is introduced by
external factors related to data collection or preprocessing
methods [39], [40]. For instance, an online survey may
disproportionately attract younger participants who are more
familiar with digital platforms, thereby underrepresenting
older individuals. In this scenario, the imbalance is introduced
by the data collection method rather than the underlying data
distribution.
TABLE 1. Sample distribution for global imbalance.
Two other notable categories are binary imbalance and
multi-class imbalance. Binary imbalance occurs in datasets
with only two classes, where one class significantly out-
numbers the other. A typical example of binary imbalance
is spam detection, where spam emails (the minority class)
occur far less frequently than legitimate emails (the majority
class) [41]. In contrast, Multi-class imbalance arises in
datasets with more than two class distribution, where one
or more classes are significantly underrepresented. For
example, in a facial recognition system trained to identify
individuals from different ethnic groups [42], [43], [44],
certain ethnic groups may be underrepresented in the training
data. This imbalance can result in biased models that
perform poorly for those groups [45], [46]. A common
approach to handling multi-class imbalance is to convert
the problem into a series of binary tasks using a one-vs-
all strategy [47], [48], [49]. In this method, samples from
a single class are compared against samples from all the
other classes combined. However, studies have shown that
this strategy is not easily applicable to multi-class imbalance
scenarios due to certain unique characteristics of multi-
class distributions. For instance, a class may be considered
a minority when compared to one class but a majority
when compared to another class with comparatively fewer
samples. Additionally, there might exist severe overlap in the
boundaries of class samples, making the baseline one-vs-all
strategies ineffective. In such cases, and with a severe rarity
of class samples, applying data-augmentation techniques
may be either prove ineffective or even degrade model
performance [50], [51], [52], [53].
In multi-class problems, class imbalance can be cat-
egorised as global or local. Global imbalance refers to
disparities that exists across the entire dataset, while Local
imbalance occurs only under certain data conditions or
113840
VOLUME 13, 2025


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
TABLE 2. Sample distribution for local imbalance.
subsets [19], [20]. Consider a synthetically generated dataset
of engine fault detection in TABLE 1 as an illustration.
Globally, Class N is the dominant class, vastly outnumbering
Classes A, B, and C. Among the fault classes, Class A
is most common, while Class C is extremely rare. Global
imbalance here means that the model is likely to become
biased towards predicting Class N, potentially leading to
higher rate of missed detections for the rare but critical faults
in Class C. To address global imbalance, techniques such as
oversampling Classes A, B, and C or undersampling Class
N can be employed. These strategies help the model pay
appropriate attention to the rarer but important classes, such
as Class C.
Local imbalance can be illustrated by considering a
synthetically generated aero-engine fault detection dataset
with different operating regions/conditions, as shown in
TABLE 2. In Region 2, Class N dominates with 300 instances
making the 10 instances in Class C almost negligible.
Although Class C is already globally underrepresented, it is
also locally scarce in Region 2. A visual depiction of this
imbalance is shown in Fig. 1. In Region 3, Class B appears
more frequently than Class C, but Class N remains the
dominant class. Again, the model may struggle to correctly
identify faults in Class C, as the very low number of samples
contributes to local imbalance [54], [55] Locally targeting
oversampling in Regions 2 and 3, where Class C is severely
underrepresented, can enable the model more effectively
recognise faults under specific operating conditions.
Class imbalance is also characterised as absolute and
relative. Relative imbalance occurs when the minority class
instances are significantly fewer to the other classes, often
expressed as a low ratio of m/N, where m is the number
of minority class samples and N is the total number of
validation samples. Conversely, Absolute imbalance refers to
the scarcity of minority class instances in an absolute sense,
where m is intrinsically low in value, regardless of the dataset
size [18], [19], [22]
In Static imbalance, the degree of imbalance remains con-
stant over time. This can be seen in medical imaging dataset,
where the proportion of healthy to diseased samples stays
consistent throughout the dat collection period. In contrast,
Dynamic imbalance refers to datasets, where the imbalance
changes over time or across different contexts. For instance,
in social media streaming data, certain topics may become
dominant only during specific events or periods, leading to
time-dependent fluctuations in class distributions [56], [57].
IV. DATA-AUGMENTATION TECHNIQUES
A. COMMONLY USED TECHNIQUES
A common approach of handling class-imbalance problems is
undersampling, which reduces the number of majority class
samples to match the size of the minority class by randomly
selecting a subset. However, this method can lead to a loss
of valuable information and is only practical when dealing
with very large datasets where such a loss is acceptable.
An alternative technique is oversampling, in which elements
of the minority class are duplicated until they match the
majority class. This method involves directly replicating
samples and does not reflect model generalisability. It is
also known to be prone to overfitting [36]. Another common
method divides the majority class into three subsets and trains
three separate models, each paired with the full minority
class. The final prediction is then obtained through a majority
vote among the three models. This ensemble-based approach
aims to reduce the impact of imbalance while preserving
more of the original data [58].
B. SMOTE
SMOTE is one of the most widely used solutions in
addressing class-imbalance. New synthetic samples of the
minority class are constructed by interpolating minority
classes in the same neighbourhood [59]. To achieve this,
SMOTE randomly selects a minority class sample (xi) from
the minority class X and determines the nearest minority class
sample (x′
i) in the surrounding neighbourhood: where x′
i ∈X.
Thereafter, a line is computed between the xi and x′
i, where a
new minority class instance xnew is created using the formula:
xnew = xi + (x′
i −xi) · δ,
δ ∈[0, 1]
(1)
where δ is a random number between 0 and 1. An illustration
of SMOTE is shown in Fig. 2.
A potential drawback of SMOTE however is that the
minority instances are generated without reference to the
majority class. Another challenge is the introduction of noise
by generating data that does not exist in the domain [59],
[60], [61], [62]. This necessitates variants of SMOTE that
addresses this challenge. György Kovács [63] developed an
open-source Python package featuring 85 SMOTE variants
and 61 compatible multi-class oversampling techniques.
The package includes cross-validation and evaluation tools,
enhancing data preprocessing for imbalanced datasets.
It enables efficient benchmarking by comparing emerging
data-augmentation methods with established techniques,
improving robustness and flexibility in ML workflows. Some
well-established SMOTE variants included in the package
are SMOTE-Edited Nearest Neighbour (ENN), Borderline-
SMOTE (B-SMOTE), Support Vector Machine (SVM)-
SMOTE and Adaptive Synthetic sampling (ADASYN) [64],
[65], [66], [67]. Emerging data-augmentation techniques
VOLUME 13, 2025
113841


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
FIGURE 1. Illustration of local class imbalance on aero-engine fault detection dataset.
FIGURE 2. An illustration of data-augmentation using SMOTE.
have mostly featured variants of SMOTE [68], [69] and
GAN [70], [71], [72], [73] as the backbone of the proposed
frameworks in balancing the data distribution, while ensuring
high-quality samples. These variants are discussed in the
following subsection.
C. SMOTE VARIANTS
Numerous approaches have been proposed that combine
SMOTE with undersampling, oversampling, ensemble, and
algorithm-level techniques. These include widely adopted
methods such as SMOTE-Tomek Links (SMOTE-TL),
SMOTE with Rough Set Theory (SMOTE+RSB), SMOTE-
WENN, and Safe-Level SMOTE [65], [74], [75], [76],
as well as more recent variants like WSMOTER, OM-
SMOTE, and SMOTE-kTLNN [77], [78], [79]. He et al.
[78] proposed OM-SMOTE that offers better generalisation,
while minimising intra-class imbalance on 32 datasets.
The technique reduces class overlap by avoiding synthetic
data generation in overlapping regions. Kwat et al. [80]
applied a hybrid technique that combines SMOTE-TL, VAE
and conditional diffusion with deep learning models for
augmenting ECG data. By incorporating MobileNetV2 and
transformer models, they significantly improve classification
performance, particularly for minority classes, making the
system more effective for arrhythmia detection. Chitra et al.
[81] proposed a two-phase framework to address imbalanced
multi-label data. While Borderline MLSMOTE generates
synthetic samples for minority classes in regions of high class
overlap, an adaptive weighted L21-norm regularised logistic
regression is then applied to enhance the prediction perfor-
mance on the balanced dataset. An oversampling technique
HHACO-FSOTe which generates synthetic minority samples
using feature similarity was proposed by Sreeja et al. [82].
The technique considers all minority instances rather than
choosing few neighbours for interpolation and is effective
for low, high-dimensional and noisy datasets. Sun et al.
[79] tackles noise associated with SMOTE by applying a
two-layer nearest neighbour classifier (SMOTE-kTLNN) to
an iterative-partition filter. After oversampling the minority
class, kTLNN is used to filter noisy data, ensuring more
accurate classification. Guo et al. [83] proposed an adaptive
support vector-based B-SMOTE method that maps the dataset
into a kernel-induced feature space and uses an SVM to
identify support vectors. Minority class oversampling is
performed by identifying neighbors based on kernel-defined
distances. The SVM decision function is then constructed
using kernel similarity values between samples, avoiding
the need to explicitly generate synthetic data points in the
high-dimensional space. A noted drawback of their method,
however, is the relatively high execution time when dealing
with large datasets. An ensemble of SMOTE, RF and SHAP
was applied by Huang et al. [84] to identify and predict
113842
VOLUME 13, 2025


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
decision-making mechanisms and susceptibility of slope
geohazards. Chachoui et al. [85] leveraged on the strengths
of four oversampling techniques, namely, SMOTE, B-
SMOTE, SMOTE-ENN and ADASYN to enrich the training
data, while applying balanced bagging to generate multiple
sub-models from the balanced subsets of the oversampled
data. Being a combination of various SMOTE variants,
the approach also incorporates their respective potential
limitations and biases. Wen et al. [86] combined graph-based
SMOTE with GNN and transformer-based feature extraction
to address class imbalance in fraud detection. The method
enhances node representations by integrating both structural
and attribute features and uses synthetic node generation
to improve minority class detection. Several works [87],
[88], [89], [90] have also highlighted some clustering based
oversampling method to tackle noise issues associated with
SMOTE. Chen et al. [89] proposed an adaptive sampling
with clustering and filtering noisy oversampling (ASCFNO)
technique that combines clustering and noise filtering to
address between-class and within-class imbalance issues.
By utilising a density peak clustering with improved noise
filter algorithm, the method effectively identifies and removes
noisy and overlapping data before oversampling, lead-
ing to improved performance in imbalanced classification
tasks. In addressing multi-class imbalance, Abdi et al.
[53] introduced MDOBoost, which integrates Mahalanobis
distance-based oversampling (MDO) with AdaBoost to
improve classification performance. The MDO component
generates synthetic samples that preserve the Mahalanobis
distance (a statistical measure that accounts for class variance
and feature correlation) from the class mean. This approach
helps retain the underlying structure of each class, improving
the model’s ability to learn from imbalanced data. Han et al.
[51] developed a global-local-based oversampling (GLOS)
method to address multi-class imbalance by using three
strategies: instance selection, partitioning, and oversampling.
The method generates synthetic instances for isolated minor-
ity classes by accounting for the covariance and mean of
all majority classes, ensuring equal distance to multiple
majority class means. It also adapts instance generation
through linear interpolation, shifting decision boundaries
towards majority classes based on local density, and applies
radial-based random oversampling within sub-clusters to
expand the local space of minority classes. In the field
of anomaly detection, Manokaran et al. [62] proposed a
hybrid balancing technique that combines SMOTE with
PPFCM to the noise of SMOTE. In their work, they clustered
pre-processed datasets using PPFCM and hybridise the
optimum cluster samples with SMOTE to create a balanced
dataset. They considered other anomaly detection studies
which addressed class imbalance. Ye et al. [91] proposed an
oversampling framework that uses Laplacian eigenmaps—a
nonlinear dimensionality reduction technique that preserves
the local structure of data—to project the dataset into a
lower-dimensional space where class separation is enhanced.
This helps reduce the noise often introduced by SMOTE.
Building on this, a hybrid system combining SVM and
Apache Spark was introduced [92], in which BSMOTE and
Tomek links are applied during preprocessing to address
class imbalance, followed by classification using SVM
within Spark’s distributed computing framework. In terms
of clustering-based techniques, Zhao et al. [93] proposed a
clustering-based oversampling algorithm (COM) to handle
multi-class imbalance learning. In order to avoid the loss
of important information, COM clusters the minority class
based on the structural characteristics of the instances, among
which rare instances and outliers are carefully portrayed
through assigning a sampling weight, to each of the clusters.
A summary of the highlighted emerging SMOTE variants
for tackling imbalance is presented in TABLE 3. The
corresponding abbreviations used for models, techniques, and
metrics are defined in the Supplementary Material (Table S1).
FIGURE 3. An illustration of GAN for data-augmentation.
D. GAN VARIANTS
GAN models comprises two neural networks: the generator
(G) and the discriminator (D), in which G produces synthetics
data based on a random input noise vector z, such that the
generated data mimics the real data sample distribution [70],
[105]. Evaluation of input data is achieved by D, which also
classifies the data as either real (i.e. coming from the true data
distribution) or fake (produced by the G). The training process
is adversarial, whereby G, focuses on enhancing the quality
of data that can fool D. Accordingly, D continually sharpens
its ability to correctly distinguish between real and synthetic
samples, leading to a dynamic in which both networks
iteratively improves through a process of adversarial learning.
The adversarial optimisation problem can be formulated as a
min max game between G and D, with the objective function
governing the process expressed as:
min
G max
D V(D, G) = Ex∼Pdata(x)[log D(x)]
+ Ez∼Pz(z)[log(1 −D(G(z)))]
(2)
where, x represents real data samples, G(z) is the data
generated by G from random noise z, and Pdata(x) and PZ(z)
denote real data and noise distribution inputs respectively.
The illustration in Fig. 3 visually represents the adversarial
relationship between the generator (G) and discriminator
(D) in GANs. It highlights how G produces synthetic data
resembling real samples, while D evaluates and classifies
data as real or fake. Through this iterative process, both
VOLUME 13, 2025
113843


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
TABLE 3. Summary of notable SMOTE variants for imbalance learning.
113844
VOLUME 13, 2025


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
TABLE 3. (Continued.) Summary of notable SMOTE variants for imbalance learning.
networks improve, ultimately enabling the generation of
realistic synthetic data for tasks such as data augmentation.
Several variants such as WGAN-GP, LSGAN, HingeGAN
have been proposed for addressing class imbalance [106],
[107], [108], [109], while enhancing sample generation,
improving model performance and optimisation in various
settings. Ahmed et al. [110] applied association rule in
optimising majority class samples, while generating minority
class data using a modified TGAN. Liu et al. [111]
integrated wavelet transforms and capsule networks in
enhancing fault diagnosis in imbalanced bearing datasets.
Their method preserves essential signal features, while
generating synthetic samples.Pu et al. [112] proposed a
technique called Generative Adversarial One-off Diagnosis
(GAOSD) to reduce the dependence on large datasets in
fault diagnosis. They used a Bidirectional GAN for both
feature extraction and data generation on healthy samples,
as standard GANs are not well-suited for handling time-
series data. Wang et al. [113] introduced a dual-module
multi-head spatiotemporal joint network for addressing class
imbalance in wind turbine fault detection. The work com-
bines auxiliary classifier GAN for generating high-quality
fault samples and integrates CNN and LTS for spatiotemporal
representation. Furthermore, Gu et al. [114] introduced
CSWGAN which improves the generative process and
results by integrating cosine similarity-based penalty terms
to regulate the optimisation objectives. Das [115] proposed
the combination of undersampling and oversampling based
on rule mining and GAN i.e., majority class duplicates
are eliminated using rule mining while minority class are
resampled using TableGAN. Thus, addressing the risk of
overfitting and data loss characterised by the former methods.
The superiority of their method is compared with emerging
data-augmentation techniques [6], [116], [117]. Lin et al. [8]
developed a novel multiple correlation analysis (MCA) which
integrates several coefficients for redundancy and sensitivity
analysis for selecting key features in high-dimensional,
highly-imbalanced data. They combined MCA with a devel-
oped GAN variant (1DWGANGP) for data-augmentation
in tackling imbalance and predicting the interval ranges of
vibration in an aero-engine assembly dataset. Ding et al.
[118] proposed LEGAN to address issues of intraclass model
collapse associated with GAN during sample generation.
A summary of GAN variants for highlighted is presented in
TABLE 4.
E. COMPARISON OF SMOTE AND GAN VARIANTS FOR
DATA-AUGMENTATION
While both SMOTE and GAN variants aim to enrich datasets
and improve model performance, they differ significantly
in their methodologies, strengths, and limitations. TABLE 5
provides a detailed comparison between SMOTE and GAN
variants for data augmentation, focusing on their methods,
applicability, strengths, and limitations across different
criteria.
GAN-based
methods
have
shown
advantages
over
SMOTE-based variants in modelling complex or multi-modal
class distributions, particularly in high-dimensional or
unstructured datasets [9], [72], [105], [111]. They often
generate more diverse and realistic synthetic samples that
can help improve classifier generalisation [71], [111],
[114], [118]. However, their performance is sensitive to
training configurations and typically requires more data
and computational resources, along with a risk of mode
collapse if not properly tuned [70], [71], [105]. In contrast,
SMOTE and its variants remain effective and efficient for
lower-dimensional, tabular data, offering fast preprocessing
and ease of integration into existing pipelines [31], [59],
[60], [63]. These methods are especially useful when
training speed, interpretability, or limited computational
budgets are primary concerns. Overall, the choice between
SMOTE-based and GAN-based augmentation should depend
VOLUME 13, 2025
113845


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
TABLE 4. Summary of notable GAN variants for imbalance learning.
on the nature of the dataset and the specific goals of the
application.
V. EVALUATION METRICS FOR IMBALANCE PROBLEMS
Aside conventional metrics like Accuracy (Acc.), precision
(prec.), specificity (spec.), recall (rec.), F1-score/F-measure.
Metrics adopted in evaluating model performance where
class-imbalance exist include AUC, Mean Area Under the
Curve, Discreteness-based Imbalanced Degree, Geometric
mean, Extended Geometric mean, Matthews Correlation
Coefficient and Imbalanced Multi-class Classification Per-
formance.
A. AREA UNDER THE RECEIVER OPERATOR
CHARACTERISTICS CURVE
The Area Under the Receiver Operating Characteristic Curve
(AUC) is derived from the confusion matrix but differs from
other metrics in that it is independent of any specific decision
threshold. Instead, it evaluates model performance across all
possible thresholds by plotting the True Positive Rate (TPR)
against the False Positive Rate (FPR) [18], [125]. Since both
TPR and FPR are computed from the confusion matrix, AUC
still reflects the model’s classification behaviour. A higher
AUC indicates a better balance between TPR and FPR, with
a value of 1 representing a perfect classifier. The ROC curve
visualises how these rates change with different classification
thresholds. These rates are defined as:
TPR = Sensitivity =
TP
TP + FN
(3)
FPR = 1 −Specificity =
FP
FP + TN
(4)
where TP (True Positive) and TN (True Negative) represents
the cases where the model correctly predicts the positive and
negative classes respectively; while FP (False Positive) and
FN (False Negative) are cases where the model incorrectly
predicts the positive and negative instances.
113846
VOLUME 13, 2025


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
TABLE 5. A detailed comparison of SMOTE and GAN variants for data augmentation.
B. MEAN AREA UNDER THE CURVE
Mean Area Under the Curve (MAUC) or M-measure [125]
is an extension of the AUC metric designed for multi-
class classification. It generalises to multi-class problems by
averaging the AUC across all class pairs, offering a single
metric that captures the classifier’s ability to distinguish
between multiple classes and expressed as:
MAUC =
2
n(n −1)
n−1
X
i=1
n
X
j=i+1
AUC(i, j)
(5)
where n and AUC(i, j) are the number of classes and the AUC
score for the pair of classes i and j, respectively.
C. DISCRETENESS-BASED IMBALANCED DEGREE
Han et al. [51] introduced a discreteness-based imbalanced
degree (DID) metric designed to clearly differentiate between
majority and minority classes. This metric also dynamically
adjusts the number of synthetic instances generated for each
minority class instance. By doing so, it aims to avoid the
production of excessive redundant instances that could result
in overfitting, while simultaneously improving the quality of
the synthetic instances to the greatest extent possible. It is
expressed as:
DID =
m
X
j=1
θj
Cj
N
(6)
where Cj is the number of instances in class j, N is the
total number of instances, and θj reflects how spread out the
samples are within class j. A lower θj indicates that the class
is more sparsely distributed, making it more difficult for the
model to learn from. DID uses this information to adapt the
number of synthetic samples generated for each class, helping
to reduce overfitting while improving sample quality.
D. GEOMETRIC MEAN
The G-mean, or geometric mean, is commonly employed in
binary classification tasks to ensure balanced performance
between the positive and negative classes. It is calculated by
taking the square root of the product of the true positive rate
(sensitivity) and the true negative rate (specificity).
G-mean =
√
TPR · TNR
(7)
with TNR defined as:
TNR =
TN
TN + FP
(8)
G-mean is effective in ensuring that a model performs well
on both classes, particularly in imbalanced datasets where
accuracy alone might be misleading. A higher G-mean, closer
to 1, indicates that the model is performing well on both
classes, striking a balance between identifying minority class
instances and correctly classifying majority class instances.
E. EXTENDED G-MEAN
The extended G-mean is a modified version of the G-mean
tailored for multi-class classification problems. Unlike the
standard G-mean, which is designed for binary classification,
the extended G-mean broadens this concept to accommodate
multiple classes. This metric generally involves calculating
the G-mean for each class individually, considering the
model’s performance across all classes, and then combining
these results. In a multi-class setting, the extended G-mean
can be computed by taking the geometric mean of the
sensitivity for each class and is given as:
Extended G-mean =
 n
Y
i=1
Sensitivityi
! 1
n
(9)
where n is the number of classes and Sensitivityi is the
sensitivity of class i.
F. MATTHEWS CORRELATION COEFFICIENT
Matthews Correlation Coefficient (MCC) is a robust eval-
uation metric in binary classification, suited for scenarios
involving class imbalance. The MCC takes into account all
four quadrants of a confusion matrix: true positives (TP),
true negatives (TN), false positives (FP), and false negatives
(FN), to produce a single coefficient that reflects the balance
between the positive and negative classes. it is approximated
as:
MCC =
(TP · TN) −(FP · FN)
√(TP + FP)(TP + FN)(TN + FP)(TN + FN)
(10)
Since MCC accounts for both correct and incorrect
predictions across all classes, MCC delivers a balanced
VOLUME 13, 2025
113847


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
evaluation even when one class significantly outweighs
the other. This makes it a more dependable alternative to
commonly used metrics like accuracy or F1 score, offering
a comprehensive reflection of a model’s true predictive
capability in imbalanced learning environments.
G. IMBALANCED MULTI-CLASS CLASSIFICATION
PERFORMANCE
Imbalanced Multi-class Classification Performance (IMCP)
is an open-source Python package by Aguilar-Ruiz et al.
[126] designed to evaluate and visualise model perfor-
mance on multi-class imbalanced datasets. Unlike AUC,
IMCP directly handles multi-class datasets without requir-
ing extensions like one-vs-all or one-vs-one strategies.
It uses prediction probabilities instead of confusion matrices,
emphasising minority classes to provide a more accurate
assessment of classifier performance. The IMCP curve
integrates class distribution and Hellinger distance, with
contributions inversely proportional to class size, offering
clearer insights into how classifiers manage imbalanced data.
Further analysis is needed to validate its effectiveness across
diverse datasets and imbalance severities.
VI. DISCUSSION AND FUTURE STUDIES
The recently developed SMOTE variants demonstrate the
versatility and adaptability of the original technique in
addressing imbalanced datasets across various domains.
By avoiding regions where classes overlap and by pair-
ing SMOTE with more advanced models, researchers are
reducing intra-class imbalance and filtering out noise more
effectively. The application of ensemble methods further
highlights the importance of combining variants in mitigating
the shortcomings of SMOTE. Despite their effectiveness,
some of these SMOTE variants still pose challenges in
terms of computational complexity and resource expense,
especially with high-dimensional and large datasets. Inter-
estingly, recent findings in radiomics [127] reveal that
applying the common SMOTE variants did not consistently
improve predictive performance across datasets. Although
slight improvements (e.g., +0.015 in AUC) were observed
in specific cases, the overall impact was minimal. This calls
attention to the need for context-specific evaluation of data
augmentation techniques.
Given the increasing use of emerging SMOTE and
GAN variants, it is crucial to investigate whether such
trends hold true on them, especially in complex and data-
sensitive domains. Future studies could therefore compare
SMOTE-based resampling techniques with GAN-based data
generation methods to determine whether these emerging
variants offer measurable and consistent benefits, or if
their impact similarly varies across datasets. Although,
computationally expensive, the employment of GAN vari-
ants with careful training offers promising capability in
handling multi-modal unstructured and structured data,
when compared to its SMOTE counterparts. However, chal-
lenges such as computational complexity, model collapse,
non-convergence on multi-class large-scale high-dimensional
datasets remain.
The aspect of mode collapse [128], where the generator
ends up producing repetitive outputs and fails to represent
the full diversity of the data, especially in minority classes is
an area requiring significant attention. This not only affects
how reliable the model is but also raises concerns about how
well these techniques scale. The challenge becomes more
pronounced when GANs are applied to other data types,
such as tabular, time-series, or text. In these contexts, limited
sample diversity can amplify domain-specific biases and
obscure critical class distinctions. It is therefore important to
focus on designing GAN variants that can preserve diversity
while adapting to different data domains.
To advance the field of class imbalance handling in ML,
key areas should be the focus of future research:
1) Scalability and large-scale datasets: Enhancing the
scalability and generalisation capabilities of existing
approaches is crucial for managing large-scale datasets
effectively. Future work should aim to reduce com-
putational complexity, making them more practical in
real-world use. Expanding the techniques to address
multi-class issues could significantly broaden their
applicability. By overcoming these limitations, the
proposed methods can become more adaptable and
efficient in handling class imbalances across a variety
of datasets.
2) Impact of data quality: The effectiveness of class
imbalance solutions is often influenced by the quality
of the original dataset. High levels of noise or errors
can diminish the optimisation and synthesis phases
of algorithms. Future studies should explore strategies
to mitigate the negative effects of poor-quality data,
such as implementing robust preprocessing steps or
developing algorithms resilient to noise and errors.
3) Integration with standard SMOTE variants: While
many new methods claim superiority over standard
techniques like SMOTE, it is essential to incorporate
these approaches within a unified framework for direct
comparison. Integrating each technique into a pipeline
similar to that of SMOTE and conducting statistical
tests across different application domains can provide
deeper insights into their effectiveness. This compar-
ative analysis would help identify the most robust
methods, specificity towards domain requirements and
potentially reveal synergistic effects when combining
techniques.
4) Training Stability and Diversity: Developing GAN
variants that effectively address challenges like mode
collapse, non-convergence, and scalability in multi-
class, high-dimensional datasets is still a prevailing
issue. Emphasis should be placed on preserving data
diversity and adapting generative models to com-
plex domains such as tabular, time-series, and text
data, where maintaining class distinction is critical.
Comparative evaluations with conventional resampling
113848
VOLUME 13, 2025


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
methods will be key to validating their effectiveness
and domain applicability.
5)
Comprehensive evaluation of IMCP performance: A
thorough analysis is necessary to build confidence in
the performance of the IMCP curve across diverse
datasets and varying degrees of class imbalance. Future
research should involve extensive testing to assess
the robustness and reliability of IMCP in different
scenarios. Such an evaluation would not only validate
its effectiveness but also help in understanding its
limitations and areas for improvement.
6) Enhance model validation performance in rarity con-
ditions: A robust validation framework and alternate
metrics that specifically account for randomness and
chance in minority sample rarity conditions could be
developed. The data-augmentation techniques could
also be tailored to rare class scenarios that reduce
the effect of randomness. These advancements will
improve the effectiveness of ML models in criti-
cal real-world applications where imbalance exists.
By addressing these research areas, the field can
develop more robust, scalable, and adaptable solutions
for class imbalance, ultimately enhancing the perfor-
mance of ML models in numerous applications.
VII. CONCLUSION
Class imbalance often biases models towards majority
classes, resulting in poor recognition of patterns in minority
classes. This review explores emerging data-augmentation
techniques, specifically SMOTE and GAN, which have
gained attention for addressing imbalance and overcoming
limitations of common approaches. Reliable evaluation met-
rics for varying imbalance scenarios are also discussed. While
significant progress has been made, future research should
prioritise improving scalability, validation under rare sample
conditions, and the integration of hybrid techniques and
noise-resilient algorithms to address real-world challenges.
This review offers new insights and identifies directions for
informing future solutions to class imbalance in ML tasks.
REFERENCES
[1] Z. S. Rubaidi, B. B. Ammar, and M. B. Aouicha, ‘‘Fraud detection using
large-scale imbalance dataset,’’ Int. J. Artif. Intell. Tools, vol. 31, no. 8,
Dec. 2022, Art. no. 2250037, doi: 10.1142/s0218213022500373.
[2] Z. Li, M. Huang, G. Liu, and C. Jiang, ‘‘A hybrid method with dynamic
weighted entropy for handling the problem of class imbalance with
overlap in credit card fraud detection,’’ Expert Syst. Appl., vol. 175,
Aug. 2021, Art. no. 114750, doi: 10.1016/j.eswa.2021.114750.
[3] B. Ozturk, T. Lawton, S. L. Smith, and I. Habli, ‘‘Balancing acts: Tackling
data imbalance in machine learning for predicting myocardial infarction
in type 2 diabetes,’’ Stud. Health Technol. Inform., pp. 626–630,
Aug. 2024, doi: 10.3233/shti240491.
[4] N. Wahler, B. Kaabachi, B. Kulynych, J. Despraz, C. Simon, and
J. L. Raisaro, ‘‘Evaluating synthetic data augmentation to correct for data
imbalance in realistic clinical prediction settings,’’ Stud. Health Technol.
Inform., vol. 316, pp. 929–933, Aug. 2024, doi: 10.3233/shti240563.
[5] J. Zhu, S. Pu, J. He, D. Su, W. Cai, X. Xu, and H. Liu, ‘‘Processing
imbalanced medical data at the data level with assisted eproduction data
as an example,’’ BioData Min., vol. 17, no. 1, p. 29, Sep. 2024, doi:
10.1186/s13040-024-00384-y.
[6] M. Zohair, R. Chandra, S. Tiwari, and S. Agarwal, ‘‘A model fusion
approach for severity prediction of diabetes with respect to binary
and multiclass classification,’’ Int. J. Inf. Technol., vol. 16, no. 3,
pp. 1955–1965, Mar. 2024, doi: 10.1007/s41870-023-01463-9.
[7] P. Shen, F. Bi, X. Bi, M. Guo, and R. Jin, ‘‘Generative transfer learning
method for extreme class imbalance problem and applied to piston aero
engine fault cross domain diagnosis,’’ IEEE Trans. Reliab., vol. 74, no. 1,
pp. 2434–2447, Mar. 2025, doi: 10.1109/TR.2024.3403660.
[8] L. Lin, C. Tong, F. Guo, S. Fu, L. Zu, and Z. Yan, ‘‘A highly imbalanced
assembly vibration prediction of aero-engine using feature selection and
data augmentation,’’ J. Vib. Eng. Technol., vol. 12, no. 4, pp. 5545–5570,
Apr. 2024, doi: 10.1007/s42417-023-01199-7.
[9] J. Chen, Z. Yan, C. Lin, B. Yao, and H. Ge, ‘‘Aero-engine high speed
bearing fault diagnosis for data imbalance: A sample enhanced diagnostic
method based on pre-training WGAN-GP,’’ Measurement, vol. 213,
May 2023, Art. no. 112709, doi: 10.1016/j.measurement.2023.112709.
[10] Z. Liao, K. Zhan, H. Zhao, Y. Deng, J. Geng, X. Chen, and Z. Song,
‘‘Addressing class-imbalanced learning in real-time aero-engine gas-path
fault diagnosis via feature filtering and mapping,’’ Rel. Eng. Syst. Saf.,
vol. 249, Sep. 2024, Art. no. 110189, doi: 10.1016/j.ress.2024.110189.
[11] M. K. Ghalati, J. Zhang, G. M. A. M. El-Fallah, B. Nenchev, and H. Dong,
‘‘Toward learning steelmaking—A review on machine learning for basic
oxygen furnace process,’’ Mater. Genome Eng. Adv., vol. 1, no. 1, p. e6,
Sep. 2023, doi: 10.1002/mgea.6.
[12] N. Osa-uwagboe, A. G. Udu, V. V. Silberschmidt, K. P. Baxevanakis,
and E. Demirci, ‘‘Effects of seawater on mechanical performance
of composite sandwich structures: A machine learning framework,’’
Materials, vol. 17, no. 11, p. 2549, May 2024, doi: 10.3390/ma17112549.
[13] P. Guo, Q. Zhu, J. Kang, Y. Wang, and W. Hu, ‘‘Quality assessment of
RSW based on transfer learning and imbalanced multi-class classification
algorithm,’’ IEEE Access, vol. 10, pp. 113619–113630, 2022, doi:
10.1109/ACCESS.2022.3212410.
[14] W. Dai, D. Li, D. Tang, H. Wang, and Y. Peng, ‘‘Deep learning
approach for defective spot welds classification using small and class-
imbalanced datasets,’’ Neurocomputing, vol. 477, pp. 46–60, Mar. 2022,
doi: 10.1016/j.neucom.2022.01.004.
[15] Q. H. Doan, S.-H. Mai, Q. T. Do, and D.-K. Thai, ‘‘A cluster-based
data splitting method for small sample and class imbalance problems in
impact damage classification,’’ Appl. Soft Comput., vol. 120, May 2022,
Art. no. 108628, doi: 10.1016/j.asoc.2022.108628.
[16] K. Oksuz, B. C. Cam, S. Kalkan, and E. Akbas, ‘‘Imbalance
problems in object detection: A review,’’ IEEE Trans. Pattern Anal.
Mach. Intell., vol. 43, no. 10, pp. 3388–3415, Oct. 2021, doi:
10.1109/TPAMI.2020.2981890.
[17] A. N. Tarekegn, M. Giacobini, and K. Michalak, ‘‘A review of methods
for imbalanced multi-label classification,’’ Pattern Recognit., vol. 118,
Oct. 2021, Art. no. 107965, doi: 10.1016/j.patcog.2021.107965.
[18] S. Kang, ‘‘Model validation failure in class imbalance problems,’’
Expert
Syst.
Appl.,
vol.
146,
May
2020,
Art. no. 113190,
doi:
10.1016/j.eswa.2020.113190.
[19] A. G. Udu, A. Lecchini-Visintini, and H. Dong, ‘‘On chance performance
in high-dimensional class-imbalance problems,’’ in Proc. UKACC
14th Int. Conf. Control (CONTROL), Apr. 2024, pp. 254–255, doi:
10.1109/control60310.2024.10531841.
[20] X.-J. Lv, L.-W. Huang, and Y.-H. Shao, ‘‘Geometric relative mar-
gin machine for heterogeneous distribution and imbalanced clas-
sification,’’ Inf. Sci., vol. 689, Jan. 2025, Art. no. 121430, doi:
10.1016/j.ins.2024.121430.
[21] F. Yang, Z.-W. Gao, S. Lu, and Y. Liu, ‘‘Federated learning for
decentralized fault diagnosis of a sucker-rod pumping system with
class imbalance data,’’ Control Eng. Pract., vol. 152, Nov. 2024,
Art. no. 106050, doi: 10.1016/j.conengprac.2024.106050.
[22] I. Araf, A. Idri, and I. Chairi, ‘‘Cost-sensitive learning for imbalanced
medical data: A review,’’ Artif. Intell. Rev., vol. 57, no. 4, p. 80, Mar. 2024,
doi: 10.1007/s10462-023-10652-8.
[23] Y. Chen, X. Yang, and H.-L. Dai, ‘‘Cost-sensitive continuous ensemble
kernel learning for imbalanced data streams with concept drift,’’
Knowledge-Based Syst., vol. 284, Jan. 2024, Art. no. 111272, doi:
10.1016/j.knosys.2023.111272.
[24] R. Guido, M. C. Groccia, and D. Conforti, ‘‘A hyper-parameter
tuning approach for cost-sensitive support vector machine classifiers,’’
Soft Comput., vol. 27, no. 18, pp. 12863–12881, Sep. 2023, doi:
10.1007/s00500-022-06768-8.
VOLUME 13, 2025
113849


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
[25] P. Shan, J. Chen, C. Fu, L. Cao, M. Tie, and C.-W. Sham, ‘‘Automatic
skin lesion classification using a novel densely connected convo-
lutional network integrated with an attention module,’’ J. Ambient
Intell. Human Comput., vol. 14, no. 7, p. 8943, 2023, doi: 10.1007/
s12652-022-04400-z.
[26] M.
Galar,
A.
Fernandez,
E.
Barrenechea,
H.
Bustince,
and
F. Herrera, ‘‘A review on ensembles for the class imbalance problem:
Bagging-, Boosting-, and hybrid-based approaches,’’ IEEE Trans.
Syst., Man, Cybern., C, vol. 42, no. 4, pp. 463–484, Jul. 2012, doi:
10.1109/TSMCC.2011.2161285.
[27] B. Krawczyk, ‘‘Learning from imbalanced data: Open challenges and
future directions,’’ Prog. Artif. Intell., vol. 5, no. 4, pp. 221–232,
Nov. 2016, doi: 10.1007/s13748-016-0094-0.
[28] S. Das, S. S. Mullick, and I. Zelinka, ‘‘On supervised class-imbalanced
learning: An updated perspective and some key challenges,’’ IEEE
Trans. Artif. Intell., vol. 3, no. 6, pp. 973–993, Dec. 2022, doi:
10.1109/TAI.2022.3160658.
[29] C. Fjellström and K. Nyström, ‘‘Deep learning, stochastic gradient
descent and diffusion maps,’’ J. Comput. Math. Data Sci., vol. 4,
Aug. 2022, Art. no. 100054.
[30] Y. Wu, G. Mei, and K. Shao, ‘‘Revealing influence of meteorological
conditions and flight factors on delays using XGBoost,’’ J. Comput. Math.
Data Sci., vol. 3, Mar. 2022, Art. no. 100030.
[31] M. Salmi, D. Atif, D. Oliva, A. Abraham, and S. Ventura, ‘‘Handling
imbalanced medical datasets: Review of a decade of research,’’ Artif.
Intell. Rev., vol. 57, no. 10, p. 273, Sep. 2024, doi: 10.1007/s10462-024-
10884-2.
[32] H. Chen, J. Wei, H. Huang, Y. Yuan, and J. Wang, ‘‘Review of
imbalanced fault diagnosis technology based on generative adversarial
networks,’’ J. Comput. Des. Eng., vol. 11, no. 5, p. 99, Oct. 2024, doi:
10.1093/jcde/qwae075.
[33] A. A. Khan, O. Chaudhari, and R. Chandra, ‘‘A review of ensemble
learning and data augmentation models for class imbalanced problems:
Combination, implementation and evaluation,’’ Expert Syst. Appl.,
vol. 244, Jun. 2024, Art. no. 122778, doi: 10.1016/j.eswa.2023.122778.
[34] J. M. Johnson and T. M. Khoshgoftaar, ‘‘Survey on deep learning
with class imbalance,’’ J. Big Data, vol. 6, 2019, Art. no. 27, doi:
10.1186/s40537-019-0192-5.
[35] S. Rezvani and X. Wang, ‘‘A broad review on class imbalance learning
techniques,’’ Appl. Soft Comput., vol. 143, Aug. 2023, Art. no. 110415,
doi: 10.1016/j.asoc.2023.110415.
[36] M. Altalhan, A. Algarni, and M. Turki-Hadj Alouane, ‘‘Imbalanced
data problem in machine learning: A review,’’ IEEE Access, vol. 13,
pp. 13686–13699, 2025, doi: 10.1109/ACCESS.2025.3531662.
[37] X. Yuan, S. Chen, C. Sun, and L. Yuwen, ‘‘A novel early diagnostic
framework for chronic diseases with class imbalance,’’ Sci. Rep., vol. 12,
no. 1, pp. 1–16, May 2022, doi: 10.1038/s41598-022-12574-x.
[38] Y.-C.
Wang
and
C.-H.
Cheng,
‘‘A
multiple
combined
method
for
rebalancing
medical
data
with
class
imbalances,’’
Comput. Biol. Med., vol. 134, Jul. 2021, Art. no. 104527, doi:
10.1016/j.compbiomed.2021.104527.
[39] H. He and E. A. Garcia, ‘‘Learning from imbalanced data,’’ IEEE
Trans. Knowl. Data Eng., vol. 21, no. 9, pp. 1263–1284, Sep. 2009, doi:
10.1109/TKDE.2008.239.
[40] J. N. Victorino, S. Inoue, and T. Shibata, ‘‘Handling class imbalance
in forecasting Parkinson s disease wearing-off with fitness tracker
dataset,’’ in Proc. Neural Inf. Process. Singapore: Springer, 2024,
pp. 564–578.
[41] G. Andresini, A. Iovine, R. Gasbarro, M. Lomolino, M. d. Gemmis, and
A. Appice, ‘‘EUPHORIA: A neural multi-view approach to combine
content and behavioral features in review spam detection,’’ J. Comput.
Math. Data Sci., vol. 3, Apr. 2022, Art. no. 100036.
[42] Y. Li, B. Wu, Y. Zhao, H. Yao, and Q. Ji, ‘‘Handling missing labels
and class imbalance challenges simultaneously for facial action unit
recognition,’’ Multimedia Tools Appl., vol. 78, no. 14, pp. 20309–20332,
Jul. 2019, doi: 10.1007/s11042-018-6836-1.
[43] R. Soleymani, E. Granger, and G. Fumera, ‘‘Progressive boosting for
class imbalance and its application to face re-identification,’’ Expert Syst.
Appl., vol. 101, pp. 271–291, Jul. 2018, doi: 10.1016/j.eswa.2018.01.023.
[44] C. Huang, Y. Li, C. C. Loy, and X. Tang, ‘‘Deep imbalanced learning
for face recognition and attribute prediction,’’ IEEE Trans. Pattern
Anal. Mach. Intell., vol. 42, no. 11, pp. 2781–2794, Nov. 2020, doi:
10.1109/TPAMI.2019.2914680.
[45] P. Terhörst, M. L. Tran, N. Damer, F. Kirchbuchner, and A. Kuijper,
‘‘Comparison-level mitigation of ethnic bias in face recognition,’’ in Proc.
8th Int. Workshop Biometrics Forensics (IWBF), Apr. 2020, pp. 1–6, doi:
10.1109/IWBF49977.2020.9107956.
[46] A. Sumsion, S. Torrie, D.-J. Lee, and Z. Sun, ‘‘Surveying racial bias in
facial recognition: Balancing datasets and algorithmic enhancements,’’
Electronics, vol. 13, no. 12, p. 2317, Jun. 2024, doi: 10.3390/electron-
ics13122317.
[47] M. Galar, A. Fernández, E. Barrenechea, H. Bustince, and F. Herrera,
‘‘An overview of ensemble methods for binary classifiers in multi-class
problems: Experimental study on one-vs-one and one-vs-all schemes,’’
Pattern Recognit., vol. 44, no. 8, pp. 1761–1776, Aug. 2011, doi:
10.1016/j.patcog.2011.01.017.
[48] J. Yan, Z. Zhang, K. Lin, F. Yang, and X. Luo, ‘‘A hybrid scheme-
based one-vs-all decision trees for multi-class classification tasks,’’
Knowledge-Based Syst., vol. 198, Jun. 2020, Art. no. 105922, doi:
10.1016/j.knosys.2020.105922.
[49] X. Gao, Y. He, M. Zhang, X. Diao, X. Jing, B. Ren, and W. Ji,
‘‘A multiclass classification using one-versus-all approach with the
differential partition sampling ensemble,’’ Eng. Appl. Artif. Intell., vol. 97,
Jan. 2021, Art. no. 104034, doi: 10.1016/j.engappai.2020.104034.
[50] V. López, A. Fernández, S. García, V. Palade, and F. Herrera, ‘‘An
insight into classification with imbalanced data: Empirical results and
current trends on using data intrinsic characteristics,’’ Inf. Sci., vol. 250,
pp. 113–141, Nov. 2013, doi: 10.1016/j.ins.2013.07.007.
[51] M. Han, H. Guo, J. Li, and W. Wang, ‘‘Global-local information based
oversampling for multi-class imbalanced data,’’ Int. J. Mach. Learn.
Cybern., vol. 14, no. 6, pp. 2071–2086, Jun. 2023, doi: 10.1007/s13042-
022-01746-w.
[52] X. Yang, Q. Kuang, W. Zhang, and G. Zhang, ‘‘AMDO: An over-
sampling technique for multi-class imbalanced problems,’’ IEEE Trans.
Knowl. Data Eng., vol. 30, no. 9, pp. 1672–1685, Sep. 2018, doi:
10.1109/TKDE.2017.2761347.
[53] L. Abdi and S. Hashemi, ‘‘To combat multi-class imbalanced problems by
means of over-sampling and boosting techniques,’’ Soft Comput., vol. 19,
no. 12, pp. 3369–3385, Dec. 2015, doi: 10.1007/s00500-014-1291-z.
[54] L. Wang, S. Xu, X. Wang, and Q. Zhu, ‘‘Addressing class imbalance in
federated learning,’’ in Proc. 35th AAAI Conf. Artif. Intell. (AAAI), vol. 35,
May 2021, pp. 10165–10173, doi: 10.1609/aaai.v35i11.17219.
[55] C. Huang, C. C. Loy, and X. Tang, ‘‘Learning deep representation for
mood classification in microblog,’’ in Proc. IEEE Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jun. 2016, pp. 1–21.
[56] S. Pang, L. Zhu, G. Chen, A. Sarrafzadeh, T. Ban, and D. Inoue,
‘‘Dynamic class imbalance learning for incremental LPSVM,’’ Neural
Netw., vol. 44, p. 87, Aug. 2013, doi: 10.1016/j.neunet.2013.02.007.
[57] S. Wang, L. L. Minku, and X. Yao, ‘‘A systematic study of online
class imbalance learning with concept drift,’’ IEEE Trans. Neural
Netw. Learn. Syst., vol. 29, no. 10, pp. 4802–4821, Oct. 2018, doi:
10.1109/TNNLS.2017.2771290.
[58] G. Lemaitre, F. Nogueira, and C. K. Aridas, ‘‘Imbalanced-learn: A Python
toolbox to tackle the curse of imbalanced datasets in machine learning,’’
J. Mach. Learn. Res., vol. 18, pp. 1–5, Jan. 2016.
[59] D.
Elreedy
and
A.
F.
Atiya,
‘‘A
comprehensive
analysis
of
synthetic minority oversampling technique (SMOTE) for handling
class imbalance,’’ Inf. Sci., vol. 505, pp. 32–64, Dec. 2019, doi:
10.1016/j.ins.2019.07.070.
[60] A. Fernandez, S. Garcia, F. Herrera, and N. V. Chawla, ‘‘SMOTE for
learning from imbalanced data: Progress and challenges, marking the
15-year anniversary,’’ J. Artif. Intell. Res., vol. 61, pp. 863–905,
Apr. 2018, doi: 10.1613/jair.1.11192.
[61] Asniar, N. U. Maulidevi, and K. Surendro, ‘‘SMOTE-LOF for noise
identification in imbalanced data classification,’’ J. King Saud Univ.
- Comput. Inf. Sci., vol. 34, no. 6, pp. 3413–3423, Jun. 2022, doi:
10.1016/j.jksuci.2021.01.014.
[62] J. Manokaran, G. Vairavel, and J. Vijaya, ‘‘PPFCM-SMOTE: A novel
balancing system for anomaly detection in IoT edge using probabilistic
possibilistic fuzzy clustering and SMOTE,’’ Int. J. Inf. Technol., vol. 13,
pp. 1–20, Aug. 2024, doi: 10.1007/s41870-024-02129-w.
[63] G. Kovács, ‘‘Smote-variants: A Python implementation of 85 minority
oversampling techniques,’’ Neurocomputing, vol. 366, pp. 352–354,
Nov. 2019, doi: 10.1016/j.neucom.2019.06.100.
113850
VOLUME 13, 2025


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
[64] H. M. Nguyen, E. W. Cooper, and K. Kamei, ‘‘Borderline over-sampling
for imbalanced data classification,’’ Int. J. Knowl. Eng. Soft Data
Paradigms, vol. 3, no. 1, p. 4, 2011, doi: 10.1504/ijkesdp.2011.039875.
[65] G. E. A. P. A. Batista, R. C. Prati, and M. C. Monard, ‘‘A study of
the behavior of several methods for balancing machine learning training
data,’’ ACM SIGKDD Explorations Newslett., vol. 6, no. 1, pp. 20–29,
Jun. 2004, doi: 10.1145/1007730.1007735.
[66] H. He, Y. Bai, E. A. Garcia, and S. Li, ‘‘ADASYN: Adaptive
synthetic sampling approach for imbalanced learning,’’ in Proc.
IEEE Int. Joint Conf. Neural Netw., Jun. 2008, pp. 1322–1328, doi:
10.1109/IJCNN.2008.4633969.
[67] H. Han, W. Wang, and B. Mao, ‘‘Borderline-SMOTE: A new over-
sampling method in imbalanced data sets learning,’’ in Proc. Adv. Intell.
Comput., Jan. 2005, pp. 878–887, doi: 10.1007/11538059_91.
[68] C.-Y. Lee and E. D. C. Maceren, ‘‘Wind energy system fault classification
using deep CNN and improved PSO-tuned extreme gradient boosting,’’
IET Renew. Power Gener., vol. 18, no. 14, pp. 2496–2511, Oct. 2024, doi:
10.1049/rpg2.13091.
[69] A. M. Eid, B. Soudan, A. B. Nassif, and M. Injadat, ‘‘Comparative study
of ML models for IIoT intrusion detection: Impact of data preprocessing
and balancing,’’ Neural Comput. Appl., vol. 36, no. 13, pp. 6955–6972,
May 2024, doi: 10.1007/s00521-024-09439-x.
[70] I. Goodfellow, J. Pouget-Abadie, M. Mirza, B. Xu, D. Warde-Farley,
S. Ozair, A. Courville, and Y. Bengio, ‘‘Generative adversarial networks,’’
Commun. ACM, vol. 63, no. 11, p. 139, Nov. 2020, doi: 10.1145/3422622.
[71] A. Aggarwal, M. Mittal, and G. Battineni, ‘‘Generative adversarial
network: An overview of theory and applications,’’ Int. J. Inf. Man-
age. Data Insights, vol. 1, no. 1, Apr. 2021, Art. no. 100004, doi:
10.1016/j.jjimei.2020.100004.
[72] J. Park, S. Choi, and Y. Feng, ‘‘Predicting startup success using two
bias-free machine learning: Resolving data imbalance using generative
adversarial networks,’’ J. Big Data, vol. 11, no. 1, p. 122, Sep. 2024, doi:
10.1186/s40537-024-00993-8.
[73] M. Irtaza, A. Ali, M. Gulzar, and A. Wali, ‘‘Multi-label classification
of lung diseases using deep learning,’’ IEEE Access, vol. 12, 2024,
Art. no. 124062, doi: 10.1109/ACCESS.2024.3454537.
[74] C. Bunkhumpornpat, K. Sinapiromsaran, and C. Lursinsap, ‘‘Safe-
Level-SMOTE: Safe-Level-synthetic minority over-sampling technique
for handling the class imbalanced problem,’’ in Proc. Adv. Knowl.
Discovery Data Mining, vol. 5476. Cham, Switzerland: Springer, 2009,
pp. 475–482, doi: 10.1007/978-3-642-01307-2.
[75] E. Ramentol, Y. Caballero, R. Bello, and F. Herrera, ‘‘SMOTE-
RSB : A hybrid preprocessing approach based on oversampling and
undersampling for high imbalanced data-sets using SMOTE and rough
sets theory,’’ Knowl. Inf. Syst., vol. 33, no. 2, pp. 245–265, Nov. 2012,
doi: 10.1007/s10115-011-0465-6.
[76] H. Guan, Y. Zhang, M. Xian, H. D. Cheng, and X. Tang, ‘‘SMOTE-
WENN: Solving class imbalance and small sample problems by
oversampling and distance scaling,’’ Int. J. Speech Technol., vol. 51, no. 3,
pp. 1394–1409, Mar. 2021, doi: 10.1007/s10489-020-01852-8.
[77] L. Camacho and F. Bacao, ‘‘WSMOTER: A novel approach for
imbalanced regression,’’ Int. J. Speech Technol., vol. 54, no. 19,
pp. 8789–8799, Oct. 2024, doi: 10.1007/s10489-024-05608-6.
[78] Y. He, X. Lu, P. Fournier-Viger, and J. Z. Huang, ‘‘A novel overlap-
ping minimization SMOTE algorithm for imbalanced classification,’’
Frontiers Inf. Technol. Electron. Eng., vol. 25, no. 9, pp. 1266–1281,
Sep. 2024, doi: 10.1631/fitee.2300278.
[79] P. Sun, Z. Wang, L. Jia, and Z. Xu, ‘‘SMOTE-kTLNN: A hybrid re-
sampling method based on SMOTE and a two-layer nearest neighbor
classifier,’’ Expert Syst. Appl., vol. 238, Mar. 2024, Art. no. 121848, doi:
10.1016/j.eswa.2023.121848.
[80] J. Kwak and J. Jung, ‘‘Classification of imbalanced ECGs through
segmentation models and augmented by conditional diffusion model,’’
PeerJ Comput. Sci., vol. 10, p. 2299, Sep. 2024, doi: 10.7717/peerj-
cs.2299.
[81] P. K. A. Chitra, S. A. Balamurugan, S. Geetha, S. Kadry, J. Kim, and
K. Han, ‘‘A novel framework for learning and classifying the imbalanced
multi-label data,’’ Comput. Syst. Sci. Eng., vol. 48, no. 5, pp. 1367–1385,
2024, doi: 10.32604/csse.2023.034373.
[82] N. K. Sreeja and N. K. Sreelaja, ‘‘A hierarchical heterogeneous ant colony
optimization based oversampling algorithm using feature similarity
for classification of imbalanced data,’’ Appl. Soft Comput., vol. 166,
Nov. 2024, Art. no. 112186, doi: 10.1016/j.asoc.2024.112186.
[83] J. Guo, H. Wu, X. Chen, and W. Lin, ‘‘Adaptive SV-borderline
SMOTE-SVM algorithm for imbalanced data classification,’’ Appl.
Soft Comput., vol. 150, Jan. 2024, Art. no. 110986, doi: 10.1016/
j.asoc.2023.110986.
[84] J. Huang, H. Wen, J. Hu, B. Liu, X. Zhou, and M. Liao, ‘‘Deciphering
decision-making mechanisms for the susceptibility of different slope
geohazards: A case study on a SMOTE-RF-SHAP hybrid model,’’ J. Rock
Mech. Geotechnical Eng., vol. 17, no. 3, pp. 1612–1630, Mar. 2025, doi:
10.1016/j.jrmge.2024.03.008.
[85] Y. Chachoui, N. Azizi, R. Hotte, and T. Bensebaa, ‘‘Enhancing
algorithmic assessment in education: Equi-fused-data-based SMOTE for
balanced learning,’’ Comput. Educ., Artif. Intell., vol. 6, Jun. 2024,
Art. no. 100222, doi: 10.1016/j.caeai.2024.100222.
[86] J. Wen, X. Tang, and J. Lu, ‘‘An imbalanced learning method based on
graph tran-smote for fraud detection,’’ Sci. Rep., vol. 14, no. 1, p. 16560,
Jul. 2024, doi: 10.1038/s41598-024-67550-4.
[87] J. Li and Q. Zhu, ‘‘OALDPC: Oversampling approach based on
local density peaks clustering for imbalanced classification,’’ Int. J.
Speech Technol., vol. 53, no. 24, pp. 30987–31017, Dec. 2023, doi:
10.1007/s10489-023-05030-4.
[88] Y.-J. Park and K.-Y. Cheng, ‘‘A cluster impurity-based hybrid resampling
for imbalanced classification problems,’’ Int. J. Speech Technol., vol. 54,
no. 20, pp. 9671–9684, Oct. 2024, doi: 10.1007/s10489-024-05644-2.
[89] W. Chen, W. Guo, and W. Mao, ‘‘An adaptive over-sampling method for
imbalanced data based on simultaneous clustering and filtering noisy,’’
Int. J. Speech Technol., vol. 54, no. 22, pp. 11430–11449, Nov. 2024, doi:
10.1007/s10489-024-05754-x.
[90] F. Li, B. Wang, P. Wang, M. Jiang, and Y. Li, ‘‘An imbalanced
ensemble learning method based on dual clustering and stage-wise hybrid
sampling,’’ Appl. Intell., vol. 53, pp. 21167–21191, Sep. 2023, doi:
10.1007/s10489-023-04650-0.
[91] X. Ye, H. Li, A. Imakura, and T. Sakurai, ‘‘An oversampling
framework for imbalanced classification based on Laplacian eigen-
maps,’’ Neurocomputing, vol. 399, pp. 107–116, Jul. 2020, doi:
10.1016/j.neucom.2020.02.081.
[92] Z. J. Lee, C. Y. Lee, S. T. Chou, W.-Ping Ma, F. Ye, and Z. Chen, ‘‘A
hybrid system for imbalanced data mining,’’ Microsyst. Technol., vol. 26,
pp. 3043–3047, 2020, doi: 10.1007/s00542-019-04566-1.
[93] H. Zhao and J. Wu, ‘‘Clustering-based oversampling algorithm for multi-
class imbalance learning,’’ J. Classification, vol. 42, no. 1, pp. 205–220,
Mar. 2025, doi: 10.1007/s00357-024-09491-1.
[94] S. Li, Y. Peng, G. Bin, Y. Shen, Y. Guo, B. Li, Y. Jiang, and C. Fan,
‘‘Research on bearing fault diagnosis method based on cjbm with semi-
supervised and imbalanced data,’’ Nonlinear Dyn., vol. 112, p. 19759,
2024, doi: 10.1007/s11071-024-10073-4.
[95] J. Sun, M. Zhao, and C. Lei, ‘‘Class-imbalanced dynamic financial
distress prediction based on random forest from the perspective of
concept drift,’’ Risk Manage., vol. 26, no. 4, p. 19, Dec. 2024, doi:
10.1057/s41283-024-00150-8.
[96] M. H. L. Louk and B. A. Tama, ‘‘Revisiting gradient boosting-based
approaches for learning imbalanced data: A case of anomaly detection on
power grids,’’ Big Data Cognit. Comput., vol. 6, no. 2, p. 41, Apr. 2022,
doi: 10.3390/bdcc6020041.
[97] T. Wu, H. Fan, H. Zhu, C. You, H. Zhou, and X. Huang, ‘‘Intrusion detec-
tion system combined enhanced random forest with SMOTE algorithm,’’
EURASIP J. Adv. Signal Process., vol. 2022, p. 39, May 2022, Art. no. 39,
doi: 10.1186/s13634-022-00871-6.
[98] J. Manokaran and G. Vairavel, ‘‘GIWRF-SMOTE: Gini impurity-based
weighted random forest with SMOTE for effective malware attack and
anomaly detection in IoT-edge,’’ Smart Sci., vol. 11, no. 2, pp. 276–292,
Apr. 2023, doi: 10.1080/23080477.2022.2152933.
[99] A. Sarkar, H. S. Sharma, and M. M. Singh, ‘‘A supervised machine
learning-based solution for efficient network intrusion detection using
ensemble learning based on hyperparameter optimization,’’ Int. J. Inf.
Technol., vol. 15, no. 1, pp. 423–434, Jan. 2023, doi: 10.1007/s41870-
022-01115-4.
[100] T. Zhao, X. Zhang, and S. Wang, ‘‘Imbalanced node classification with
synthetic over-sampling,’’ IEEE Trans. Knowl. Data Eng., vol. 36, no. 12,
pp. 8515–8528, Dec. 2024, doi: 10.1109/TKDE.2024.3443160.
[101] J. Nanda and J. K. Chhabra, ‘‘SSHM: SMOTE-stacked hybrid model
for improving severity classification of code smell,’’ Int. J. Inf. Technol.,
vol. 14, no. 5, pp. 2701–2707, Aug. 2022, doi: 10.1007/s41870-022-
00943-8.
VOLUME 13, 2025
113851


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
[102] Z. Xu, D. Shen, T. Nie, Y. Kou, N. Yin, and X. Han, ‘‘A cluster-
based oversampling algorithm combining SMOTE and k-means for
imbalanced medical data,’’ Inf. Sci., vol. 572, pp. 574–589, Sep. 2021,
doi: 10.1016/j.ins.2021.02.056.
[103] W. D. Bae, S. Alkobaisi, and S. Bankar, ‘‘CIncremental SMOTE with
control coefficient for classifiers in data starved medical applications,’’
in
Big
Data
Analytics
and
Knowledge
Discovery,
vol.
14912.
Cham,
Switzerland:
Springer,
2024,
p. 112,
doi:
10.1007/978-3-
031-68323-7.
[104] S. K. Singh, S. Kumar, and D. Chakravarty, ‘‘Predicting the stability of
rock slopes in the presence of diverse joint networks and external factors
using machine learning algorithms,’’ Mining, Metall. Exploration, vol. 41,
no. 5, pp. 2421–2440, Oct. 2024, doi: 10.1007/s42461-024-01060-9.
[105] J. Gui, Z. Sun, Y. Wen, D. Tao, and J. Ye, ‘‘A review on generative
adversarial networks: Algorithms, theory, and applications,’’ IEEE Trans.
Knowl. Data Eng., vol. 35, no. 4, pp. 3313–3332, Apr. 2023, doi:
10.1109/TKDE.2021.3130191.
[106] I. Gulrajani, F. Ahmed, M. Arjovsky, V. Dumoulin, and A. Courville,
‘‘Improved training of Wasserstein GANs,’’ in Proc. 31st Int. Conf.
Neural Inf. Process. Syst. (NIPS), Long Beach, CA, USA, 2017,
p. 576.
[107] X. Mao, Q. Li, H. Xie, R. Y. K. Lau, Z. Wang, and S. P. Smolley,
‘‘Least squares generative adversarial networks,’’ in Proc. IEEE Int.
Conf. Comput. Vis. (ICCV), Venice, Italy, Oct. 2017, pp. 2813–2821, doi:
10.1109/ICCV.2017.304.
[108] J.
Hyun
Lim
and
J.
Chul
Ye,
‘‘Geometric
GAN,’’
2017,
arXiv:1705.02894.
[109] J. Wu, G. Liu, X. Wang, H. Tang, and Y. Qian, ‘‘GAN-GA: Infrared
and visible image fusion generative adversarial network based on global
awareness,’’ Int. J. Speech Technol., vol. 54, nos. 13–14, pp. 7296–7316,
Jul. 2024, doi: 10.1007/s10489-024-05561-4.
[110] Z. Ahmed and S. Das, ‘‘A novel hybrid resampling approach to address
class-imbalanced issues,’’ Social Netw. Comput. Sci., vol. 5, no. 7, p. 865,
Sep. 2024, doi: 10.1007/s42979-024-03227-z.
[111] Y. Liu, H. Jiang, C. Liu, W. Yang, and W. Sun, ‘‘Data-augmented
wavelet capsule generative adversarial network for rolling bearing fault
diagnosis,’’ Knowledge-Based Syst., vol. 252, Sep. 2022, Art. no. 109439,
doi: 10.1016/j.knosys.2022.109439.
[112] Z. Pu, D. Cabrera, Y. Bai, and C. Li, ‘‘Generative adversarial one-
shot diagnosis of transmission faults for industrial robots,’’ Robot.
Computer-Integrated Manuf., vol. 83, Oct. 2023, Art. no. 102577, doi:
10.1016/j.rcim.2023.102577.
[113] T.
Wang
and
L.
Yin,
‘‘Dual-module
multi-head
spatiotemporal
joint network with SACGA for wind turbines fault detection,’’
Energy, vol. 308, Nov. 2024, Art. no. 132906, doi: 10.1016/j.energy.
2024.132906.
[114] X. Gu, Y. Yu, L. Guo, H. Gao, and M. Luo, ‘‘CSWGAN-GP:
A new method for bearing fault diagnosis under imbalanced con-
dition,’’ Measurement, vol. 217, Aug. 2023, Art. no. 113014, doi:
10.1016/j.measurement.2023.113014.
[115] S. Das, ‘‘A new technique for classification method with imbalanced
training data,’’ Int. J. Inf. Technol., vol. 16, no. 4, pp. 2177–2185,
Apr. 2024, doi: 10.1007/s41870-024-01740-1.
[116] P. Vuttipittayamongkol, E. Elyan, A. Petrovski, and C. Jayne, ‘‘Overlap-
based undersampling for improving imbalanced data classification,’’
in Intelligent Data Engineering and Automated Learning (IDEAL),
vol. 11314. Cham, Switzerland: Springer, 2018, p. 68, doi: 10.1007/978-
3-030-03493-1.
[117] H. L. Le, D. Landa-Silva, M. Galar, S. Garcia, and I. Triguero, ‘‘EUSC:
A clustering-based surrogate model to accelerate evolutionary under-
sampling in imbalanced classification,’’ Appl. Soft Comput., vol. 101,
Mar. 2021, Art. no. 107033, doi: 10.1016/j.asoc.2020.107033.
[118] H. Ding, N. Huang, Y. Wu, and X. Cui, ‘‘LEGAN: Address-
ing intraclass imbalance in GAN-based medical image augmen-
tation for improved imbalanced data classification,’’ IEEE Trans.
Instrum. Meas., vol. 73, 2024, Art. no. 2517914, doi: 10.1109/TIM.
2024.3396853.
[119] H. Chen, J. Wei, H. Huang, L. Wen, Y. Yuan, and J. Wu, ‘‘Novel
imbalanced fault diagnosis method based on generative adversar-
ial networks with balancing serial CNN and transformer (BCT-
GAN),’’ Expert Syst. Appl., vol. 258, Dec. 2024, Art. no. 125171, doi:
10.1016/j.eswa.2024.125171.
[120] X. Jiang, J. Zheng, Z. Chen, Z. Ge, Z. Song, and X. Ma, ‘‘Leveraging
transfer learning for data augmentation in fault diagnosis of imbalanced
time-frequency images,’’ IEEE Trans. Autom. Sci. Eng., vol. 22,
pp. 6762–6772, 2025, doi: 10.1109/TASE.2024.3454418.
[121] A. S. Dina, A. B. Siddique, and D. Manivannan, ‘‘Effect of bal-
ancing data using synthetic data on the performance of machine
learning classifiers for intrusion detection in computer networks,’’ IEEE
Access, vol. 10, pp. 96731–96747, 2022, doi: 10.1109/ACCESS.2022.
3205337.
[122] H. Ding, L. Chen, L. Dong, Z. Fu, and X. Cui, ‘‘Imbalanced data
classification: A KNN and generative adversarial networks-based hybrid
approach for intrusion detection,’’ Future Gener. Comput. Syst., vol. 131,
pp. 240–254, Jun. 2022, doi: 10.1016/j.future.2022.01.026.
[123] M. Jamoos, A. M. Mora, M. AlKhanafseh, and O. Surakhi, ‘‘A new
data-balancing approach based on generative adversarial network for
network intrusion detection system,’’ Electronics, vol. 12, no. 13, 2023,
Art. no. 2851, doi: 10.3390/electronics12132851.
[124] A. G. Udu, A. Lecchini-Visintini, M. K. Ghalati, and H. Dong,
‘‘Addressing class imbalance in aeroengine fault detection,’’ in Proc. Int.
Conf. Mach. Learn. Appl. (ICMLA), Jacksonville, FL, USA, Dec. 2023,
pp. 1072–1077, doi: 10.1109/icmla58977.2023.00159.
[125] D. J. Hand and R. J. Till, ‘‘A simple generalisation of the area under
the ROC curve for multiple class classification problems,’’ Mach. Learn.,
vol. 45, no. 2, pp. 171–186, 2001, doi: 10.1023/a:1010920819831.
[126] J. S. Aguilar-Ruiz, M. Michalak, and Ł. Wróbel, ‘‘IMCP: A Python
package for imbalanced and multiclass data classifier performance
comparison,’’ SoftwareX, vol. 28, Dec. 2024, Art. no. 101877, doi:
10.1016/j.softx.2024.101877.
[127] A. Demircioğlu, ‘‘The effect of data resampling methods in radiomics,’’
Sci. Rep., vol. 14, no. 1, p. 2858, Feb. 2024, doi: 10.1038/s41598-024-
53491-5.
[128] S. Ayoub, Y. Gulzar, J. Rustamov, A. Jabbari, F. A. Reegu, and
S. Turaev, ‘‘Adversarial approaches to tackle imbalanced data in machine
learning,’’ Sustainability, vol. 15, no. 9, p. 7097, Apr. 2023, doi:
10.3390/su15097097.
AMADI G. UDU received the Ph.D. degree from
the University of Leicester. He contributed to
autonomous aircraft and missile systems devel-
opment with the Air Force Research and Devel-
opment Centre. He was a Lecturer with the Air
Force Institute of Technology, where he also
held various academic positions. His research
interests include the applications of artificial
intelligence and machine learning in aero-engine
fault diagnosis, structural damage morphology,
and manufacturing.
MARWAH T. SALMAN (Member, IEEE) received the B.Sc. degree
in electronic and communications engineering and the M.Sc. degree in
modern wireless communications engineering from Al-Nahrain University,
in 2010 and 2013, respectively. She is currently pursuing the Ph.D. degree
in signal processing and machine learning for wireless communications with
the University of Leicester. Prior to beginning her Ph.D. studies, she was
a Lecturer with the University of Wasit, Middle Technical University, and
Al-Kut University College. Since July 2022, she has been actively engaged in
research focused on Li-Fi technology and the integration of deep learning and
machine learning in wireless communications. Her primary research interests
include the application of machine learning and artificial intelligence
in signal processing for next-generation visible light communication
systems.
113852
VOLUME 13, 2025


---

A. G. Udu et al.: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance ML Tasks
MARYAM K. GHALATI received the Ph.D. degree
in applied mathematics from the University of
Coimbra. She is currently a Lecturer in Digital
Manufacturing with the School of Engineering,
University of Leicester. Her research focuses on
the integration of data-driven approaches, math-
ematical modelling, and artificial intelligence to
improve the monitoring, control, and optimisation
of manufacturing processes. She is particularly
interested in applying machine learning and arti-
ficial intelligence techniques to real-world industrial case studies, with an
emphasis on sustainable and intelligent manufacturing systems.
ANDREA LECCHINI-VISINTINI received the
Laurea degree in information engineering, from
the University of Pavia, and the Ph.D. degree in
automatic control from the University of Brescia.
He is Associate Professor with the Cyber Physical
Systems Group, School of Electronics and Com-
puter Science, University of Southampton. His
current research interests are in systems modelling
with aerospace and biomedical applications, con-
trol systems, and Monte Carlo methods. Before
joining Southampton in 2022, he was a Lecturer with the Department of
Engineering, University of Leicester, and, previously, a Research Associate
with the Control Group, University of Cambridge, from 2003 to 2006, and a
Post-Doc Researcher at the Université Catholique de Louvain, Belgium, from
2001 to 2003. He has held visiting appointments at the Australian National
University, Canberra.
DAVID R. SIDDLE received the Ph.D. degree
from Birmingham University. Before, he became
a Lecturer with the School of Engineering,
University of Leicester, in 2005, where he has
published in a range of areas from long-range radio
communication to indoor wireless networking.
His current interests include machine learning
applications applied to Li-Fi communications.
HONGBIAO DONG received the Ph.D. degree
from the University of Oxford, U.K. He is a
Fellow of the Royal Academy of Engineering
and a Professor of materials engineering with
the University of Leicester, U.K. He is interna-
tionally renowned for digital manufacturing and
solidification modeling, and has made unique
contributions to the metals industry. His research
interests include the physics-based and data-driven
modeling of metal processing and the application
of artificial intelligence and machine learning for manufacturing.
VOLUME 13, 2025
113853
