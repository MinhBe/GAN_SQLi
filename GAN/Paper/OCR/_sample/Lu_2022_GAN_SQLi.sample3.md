A GAN-based Method for Generating SQL
Injection Attack Samples
Dongzhe Lu1 ,Jinlong Fei1,2,Long Liu1,2*,Zecun Li1
1. Information Engineering University, Zhengzhou, China
2. State Key Laboratory of Mathematical Engineering and Advanced Computing, Zhengzhou, China
906188591@qq.com, feijinlong@126.com, 164192607@qq.com, 1137509133@qq.com
Abstract—Due to the simplicity of implementation and
high threat level, SQL injection attacks are one of the oldest,
most prevalent, and most destructive types of security attacks
on Web-based information systems. With the continuous
development
and
maturity
of
artificial
intelligence
technology, it has been a general trend to use AI technology
to detect SQL injection. The selection of the sample set is the
deciding factor of whether AI algorithms can achieve good
results, but dataset with tagged specific category labels are
difficult to obtain. This paper focuses on data augmentation
to learn similar feature representations from the original
data to improve the accuracy of classification models. In this
paper, deep convolutional generative adversarial networks
combined with genetic algorithms are applied to the field of
Web vulnerability attacks, aiming to solve the problem of
insufficient number of SQL injection samples. This method
is also expected to be applied to sample generation for other
types of vulnerability attacks.
Keywords—SQL injection; data augmentation; generative
adversarial network; genetic algorithm; Web vulnerability
I.
INTRODUCTION
The Internet provides more and more interactive online
applications. Problems such as flaws in development
languages, limitations in the professionalism of some
developers, and lack of awareness of web security have led
to malicious attacks on so many websites. When a web
application passes SQL statements to the backend database
without strict filtering of user input parameters, attackers
can insert SQL commands into a web form submission,
URL, or the query string of page request. Change the SQL
statement execution logic to gain access to resources or
change data stored in the database (as shown in Fig. 1).
Simply put, the essence is to execute the input data as code,
violating the principle of data-code separation.
Existing security systems are unable to fully detect and
stop increasingly sophisticated and highly mischievous
hacks, and deep learning methods are widely used in
cybersecurity to help solve these problems [1]. One of the
difficulties in this area is the lack of a recognized traffic
dataset with complete information labeling, while being
able to guarantee diversity. On the one hand, many of these
datasets are internal, cannot be shared due to privacy
concerns, such as anomalous data traffic captured by
security companies or internal datasets used for certain
research purposes. On the other hand, a portion of the
datasets are highly anonymized and do not reflect the full
picture, such as research datasets involving user behavior.
Web server
Database
SQL Query
SQL Response
HTTP Request
Internet
Users
Network Traffic

Fig. 1.
SQL Database statement execution logic.
As network behaviors change, the outdated datasets
cannot fully meet the needs of detection, such as the classic
datasets KDD-CUP99 [2] and NSL-KDD [3] used for
intrusion detection. In contrast, the CIC-IDS2017 and CIC-
IDS2018 datasets from the Communications Security
Establishment (CSE) and the Canadian Institute for
Cybersecurity (CIC) collaborative project are relatively
new and close to real data [4]. But there is less data
available for SQL injection detection. Therefore, it is
necessary to expand the samples based on the existing data
according to the actual needs, and try to make the sample
set with complete information annotation and ensure the
diversity, in order to improve the classification results of
the detection algorithm.
Generative adversarial network (GAN) is composed of
generators and discriminators that play against each other
[5]. The input data is obtained by random sampling in the
latent space and passed to the generative network. GAN, a
network synthesis-based approach, generates more diverse
samples compared to traditional data augmentation
techniques [6] although the process is more complex.
In this paper, generative adversarial network is applied
to the field of Web vulnerability attacks. On the basis of the
principles and semantics of SQL injection attack statements,
false samples close to the payload of SQL injection attacks
are generated to complete the data expansion of the original
small number of samples, avoid overfitting of AI detection
models, and enhance the generalization performance of the
models.
The work in the related area is outlined in Section II.
Section III demonstrates the method for generating injected
samples, and Section IV presents the overall flow and
results of the experiments. Finally, Section V briefly
discusses the experimental conclusions and future work.
IEEE ITAIC(ISSN:2693-2865)
978-1-6654-2207-9/22/$31.00 ©2022 IEEE
1827
2022 IEEE 10th Joint International Information Technology and Artificial Intelligence Conference (ITAIC) | 978-1-6654-2207-9/22/$31.00 ©2022 IEEE | DOI: 10.1109/ITAIC54216.2022.9836726
Authorized licensed use limited to: Naresuan University provided by UniNet. Downloaded on November 11,2022 at 10:43:27 UTC from IEEE Xplore. Restrictions apply.


---


II.
RELATED WORK
A. Data augmentation
Data augmentation algorithm belongs to an important
part of data pre-processing. New samples are generated
based on limited training samples to increase the training
sample size. Theoretically, data augmentation methods are
based on the original training data distribution, defining the
neighborhood of the original data and extracting new
training samples in the domain.
In the image field, traditional data augmentation
methods include color transformation, horizontal flip,
rotation, luminance transformation, scaling, cropping,
adding noise, etc. Such methods based on geometric
transformation and pixel transformation can alleviate the
problem of overfitting of neural networks and improve the
generalization ability to a certain extent. However,
compared with the original data, the added data points do
not fundamentally solve the problem of insufficient data [6].
At the same time, the methods require artificially set
transformation functions and corresponding parameters,
which are generally based on empirical knowledge, and
optimal data augmentation is usually difficult to achieve, so
the generalization of the model can only be improved to a
limited extent.
Machine learning-based image data enhancement
methods are automatic data enhancement methods,
generative adversarial network-based data enhancement
methods, and data enhancement methods based on a
combination of automatic encoders and generative
adversarial networks. This network synthesis-based
method has its unique and irreplaceable advantages. [7]
developed a residual deep network model for multi-object
recognition, which achieves multi-object recognition
through migration learning of the residual network and
effectively solves the problems of insufficient number of
data sets, over-fitting of network models and memorizing
the exact details of training images. [8] used GAN to
synthesize data with semantic similarity and text diversity
compared to real data. [9] trained DCGAN on the face
dataset to achieve the purpose of improving the recognition
accuracy, indicating the practicability of this method in
unsupervised learning. [10] proposed the improved
DCGAN algorithm, and it is demonstrated that the clarity
and recognition rate are significantly improved compared
to the pre-improvement.
B. Genetic algorithm
Genetic Algorithm (GA) is a computational model that
simulates natural selection in Darwin's theory of biological
evolution. It's a method to search for the optimal solution
by simulating the natural evolutionary process. This
approach is iterative and extremely adaptable. Genetic
algorithms are an important part of intelligent computing
technology, and have already produced many fruitful
results in many fields, such as face recognition [11],
function combination optimization [12], knowledge
discovery [13], vulnerability mining [14]. Facing the
complex computing environment, the features of genetic
algorithm can be used for combinatorial optimization,
machine learning, signal processing, adaptive control and
artificial life synthesis, so as to ensure the security of
network operation [15].
C. Application of GAN
The emergence of GAN has revolutionized the field of
deep learning, and the cyber security field uses GAN for a
wide range of tasks, such as password guessing, spatial
image steganography, and anomaly detection. [16]
proposed a combination of generative adversarial network
and variational autoencoder, which followed a similar
model architecture as SSGAN but used a new encoder
network to generate better visually convincing images.
PassGAN [17] is used to learn the distribution of password
leaks from the RockYou dataset. The structure of the
generator and discriminator forms a series of residual
blocks with shortcut connections between layers, and the
training error decreases as the number of layers increases.
In [18], Cycle-GANs are used to learn the transitions
between host-based normal and abnormal data. It is used to
create synthetic anomalies from normal data to balance
instances of the ADFA-LD dataset. A large number of
works use BiGAN to detect anomalies/intrusions [19].
In this paper, we propose a sample generation method
based on genetic algorithm and deep convolutional
generative adversarial network, aiming to solve the
problem that real attack samples are difficult to collect and
have a single pattern. Certain random interference is
introduced to the generated samples to simulate the
complexity of real production environment and the
diversity of attack samples to improve the performance of
deep learning intrusion detection methods.
III.
METHODOLOGY
A. Genetic algorithm
Genetic algorithm provides a general framework for
solving optimization problems for complex systems,
independent of the domain and type of problem. The basic
genetic algorithm is an iterative search process that can be
typically defined as an 8-tuple.
𝑆𝐺𝐴= (𝐶, 𝐸, 𝑃0, 𝑀, ∅, Γ, Ψ, 𝑇) (1)
Where, 𝐶 is the coding method used by the individual.
𝐸 is the fitness function used to evaluate the individual. 𝑃0
is the initial population. 𝑀 is the population size. ∅ is the
selection operator. 𝛤 is the crossover operator. 𝛹 is the
variation operator. 𝑇 is the termination condition of the
operation.
1828
Authorized licensed use limited to: Naresuan University provided by UniNet. Downloaded on November 11,2022 at 10:43:27 UTC from IEEE Xplore. Restrictions apply.


---


Generation
Evaluation
Selection
Crossover
Mutation
Alternation
Gene
Fig. 2.
The structure of Genetic Algorithm.
As is shown in Fig. 2, a population consists of a certain
number of individuals encoded by genes. After the initial
population is generated, it evolves generation by generation
to produce better and better approximate solutions
according to the principle of superiority and inferiority. At
each generation, individuals are selected according to their
fitness in the problem domain. Combining crossover and
mutation with the help of genetic operators of natural
genetics generates new populations.
B. Generative adversarial network
 GAN is trained by adversarial 𝐺 (Generator) and 𝐷
(Discriminator) to make the samples generated obey the
real data distribution, which is shown in Fig. 3.
Noise z~p(z)
Generator G(z,θ)
Discriminator D(x,φ)
Real
Fake
Pdata(x)

Fig. 3.
The structure of Generative Adversarial Network.
Hypothesis, real data 𝑥~𝑝𝑑𝑎𝑡𝑎(𝑥) and random
noise 𝑧~𝑝(𝑧). The objective of the 𝐷 is to distinguish
whether the samples come from the true distribution 𝑝(𝑥)
or the generative model, denoted by 𝑦= 1 and 𝑦= 0,
respectively, which is essentially a binary classifier, then
there is
𝑝(𝑦= 1|𝑥) = 𝐷(𝑥, Φ) (2)
and
𝑝(𝑦= 0|𝑥) = 1 −𝐷(𝑥, Φ) (3)
The optimization objective function 𝑉(𝐷, 𝐺) is
min
𝐺max
𝐷
𝑉(𝐷, 𝐺) = 𝐸𝑥~𝑝𝑑𝑎𝑡𝑎(𝑥)[𝑙𝑜𝑔𝐷(𝑥)] +
𝐸𝑧~𝑝𝑛𝑜𝑖𝑠𝑒(𝑧)[log (1 −𝐷(𝐺(𝑧)))] (4)
where 𝑝𝑑𝑎𝑡𝑎(𝑥) denotes the distribution of real
samples, and 𝑝𝑛𝑜𝑖𝑠𝑒(𝑧) is the noise distribution defined in
the lower dimension.
That is to say, the objective function of the
discriminator is
max (
𝜙
𝐸𝑥~𝑝𝑑𝑎𝑡𝑎(𝑥)[𝑙𝑜𝑔𝐷(𝑥, 𝜙)] +
𝐸𝑧~𝑝𝑛𝑜𝑖𝑠𝑒(𝑧)[log (1 −𝐷(𝐺(𝑧, 𝜃), 𝜙))]) (5)
The objective function of the generator is
max (
𝜃
𝐸𝑧~𝑝𝑛𝑜𝑖𝑠𝑒(𝑧)[log (𝐷(𝐺(𝑧, 𝜃), 𝜙)]) (6)
where 𝜑 and
𝜃 are the parameters of the
discriminative and generative networks, respectively.
When and only 𝑝𝑑𝑎𝑡𝑎= 𝑝𝑔, the maximization
minimization problem of 𝑉(𝐺, 𝐷) has a globally optimal
solution, i.e., a Nash equilibrium state is reached [20].
GAN as a generative method effectively solves the
problem of generating data that can establish naturalness
interpretation, especially for generating high-dimensional
data. The neural network structure used does not limit the
generation dimension, which greatly broadens the range of
generated data samples, and can integrate various types of
loss functions, increasing the freedom of design. The
generation process does not require cumbersome sampling
sequences and can directly sample and infer new samples,
which improves the efficiency of generating new samples,
and the adversarial training method abandons direct
replication or averaging of real data, increasing the
diversity of generated samples.
C. Our methods
In this paper, an improved DCGAN structure is chosen
[21]. DCGAN uses a convolutional neural network with
pooling layers removed to replace MLP in the basic GAN
model, and uses global pooling layers instead of fully
connected layers to reduce the computational effort in order
to improve the quality of generated samples and optimize
the training stability.
The improvements of DCGAN over GAN or normal
CNN include the following. (1) Use convolution and
deconvolution instead of pooling layers to avoid
information loss. (2) Batch normalization operations are
1829
Authorized licensed use limited to: Naresuan University provided by UniNet. Downloaded on November 11,2022 at 10:43:27 UTC from IEEE Xplore. Restrictions apply.
