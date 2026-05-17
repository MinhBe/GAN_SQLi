 
 
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
Authorized licensed use limited to: Naresuan University provided by UniNet. Downloaded on November 11,2022 at 10:43:27 UTC from IEEE Xplore.  Restrictions apply. 


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
evolution. It’s a method to search for the optimal solution 
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
𝑆𝐺𝐴= (𝐶, 𝐸, 𝑃0, 𝑀, ∅, Γ, Ψ, 𝑇)       (1) 
Where, 𝐶 is the coding method used by the individual. 
𝐸 is the fitness function used to evaluate the individual. 𝑃0 
is the initial population. 𝑀 is the population size. ∅ is the 
selection operator. 𝛤 is the crossover operator. 𝛹 is the 
variation operator. 𝑇 is the termination condition of the 
operation. 
1828
Authorized licensed use limited to: Naresuan University provided by UniNet. Downloaded on November 11,2022 at 10:43:27 UTC from IEEE Xplore.  Restrictions apply. 


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
Noise z～p(z)
Generator G(z,θ)
Discriminator D(x,φ)
Real
Fake
Pdata(x)
 
Fig. 3.  
The structure of Generative Adversarial Network. 
Hypothesis, real data  𝑥~𝑝𝑑𝑎𝑡𝑎(𝑥)  and random 
noise 𝑧~𝑝(𝑧). The objective of the 𝐷 is to distinguish 
whether the samples come from the true distribution 𝑝(𝑥) 
or the generative model, denoted by 𝑦= 1 and 𝑦= 0, 
respectively, which is essentially a binary classifier, then 
there is 
𝑝(𝑦= 1|𝑥) = 𝐷(𝑥, Φ)           (2) 
and 
𝑝(𝑦= 0|𝑥) = 1 −𝐷(𝑥, Φ)          (3) 
The optimization objective function 𝑉(𝐷, 𝐺) is 
min
𝐺max
𝐷
𝑉(𝐷, 𝐺) = 𝐸𝑥~𝑝𝑑𝑎𝑡𝑎(𝑥)[𝑙𝑜𝑔𝐷(𝑥)] +
𝐸𝑧~𝑝𝑛𝑜𝑖𝑠𝑒(𝑧)[log (1 −𝐷(𝐺(𝑧)))]       (4) 
where  𝑝𝑑𝑎𝑡𝑎(𝑥)  denotes the distribution of real 
samples, and 𝑝𝑛𝑜𝑖𝑠𝑒(𝑧) is the noise distribution defined in 
the lower dimension. 
That is to say, the objective function of the 
discriminator is 
max (
𝜙
𝐸𝑥~𝑝𝑑𝑎𝑡𝑎(𝑥)[𝑙𝑜𝑔𝐷(𝑥, 𝜙)] +
𝐸𝑧~𝑝𝑛𝑜𝑖𝑠𝑒(𝑧)[log (1 −𝐷(𝐺(𝑧, 𝜃), 𝜙))])             (5) 
The objective function of the generator is 
max (
𝜃
𝐸𝑧~𝑝𝑛𝑜𝑖𝑠𝑒(𝑧)[log (𝐷(𝐺(𝑧, 𝜃), 𝜙)])    (6) 
where 𝜑 and 
𝜃 are the parameters of the 
discriminative and generative networks, respectively. 
When and only  𝑝𝑑𝑎𝑡𝑎= 𝑝𝑔, the maximization 
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
Authorized licensed use limited to: Naresuan University provided by UniNet. Downloaded on November 11,2022 at 10:43:27 UTC from IEEE Xplore.  Restrictions apply. 


---

 
 
added to both the generator and the discriminator. (3) 
Removed the fully connected layer to speed up training. (4) 
The output layer of the generator uses the Tanh activation 
function, and the other layers use RELU. (5) All layers of 
the discriminator are activated with the LeakyReLU. The 
architecture and workflow of our method is shown in Fig. 
4. 
Noise z～N
Initialization
Generation
Evaluation
Selection
Crossover
Mutation
Generator
Real/Fake
Discriminator
Fig. 4.  
The architecture and workflow of our method. 
Unlike E-GAN [22], the population is not generated by 
noise, but is composed of a self-defined list of genes. After 
evolution, the noise is then applied to individuals to 
generate more diverse attack samples using GAN and 
tamper scripts. 
Specifically, there are some details designed in the 
training process. (a) For the samples used for training, only 
the data are scaled to [-1,1], which is also the range of tanh 
values. (b) The model is trained using a batch size 500 
random gradient descent method. The weights are 
initialized using random variables satisfying a Gaussian 
distribution with mean of 0 and variance of 0.03. (c) The 
LeakyReLU is used, and the S-type activation function is 
retained in the last layer, which helps to solve the gradient 
disappearance problem. (d) The training process in this 
paper uses adam optimizer for hyperparameter tuning. The 
learning rate is used 0.0002 and the momentum is taken as 
0.5, which makes the training more stable. (Wilson et al [23] 
argued that training a GAN should not focus on the 
optimization problem and that Adam may be well suited for 
this case.) (e) KL scatter is usually used to measure the 
distance between distributions, but KL scatter is 
asymmetric, which means that the overall loss decline tends 
to be in a particular direction, which can easily cause 
pattern collapse [24]. We use the W distance, which is 
stable and effective to calculate the distance between two 
distributions, circumventing the problem of uncorrelated 
and unstable, as defined below. 
𝑊(𝑃𝑑𝑎𝑡𝑎, 𝑃𝑔) =
inf
𝛾~ ∏(𝑃𝑑𝑎𝑡𝑎,𝑃𝑔) 𝐸(𝑥,𝑦)~𝛾[‖𝑥−𝑦‖]  (7) 
Where, ∏(𝑃𝑑𝑎𝑡𝑎, 𝑃𝑔) are the set of all possible joint 
distributions after the combination 𝑃𝑑𝑎𝑡𝑎and 𝑃𝑔. 
Then, the loss function of 𝐺 is 
−𝐸𝑧~𝑃𝑔[𝐷(𝐺(𝑧))]               (8) 
The loss function of 𝐷 is 
𝐸𝑥~𝑃𝑔[𝐷(𝑥)] −𝐸𝑥~𝑃𝑑𝑎𝑡𝑎[𝐷(𝑥)]       (9) 
When using gradient descent method to optimize 
parameters, KL scatter and JS scatter cannot provide 
reasonable gradient information. In contrast, W distance 
not only reflects the distance, but also provides reliable 
gradient information, which solves the problem of pattern 
collapse and gradient disappearance from the theoretical 
level. 
IV. EXPERIMENTS 
A. Samples collection 
In order to generate SQL injection attack samples closer 
to the real environment, our initial traffic samples come 
from the replication of real vulnerabilities published by 
CVE, CNVD and exploit-db in recent years. The payloads 
in the HTTP traffic are extracted after crawling the 
corresponding attack traffic. Most of the attack locations 
are in the parameter part of the URI of GET requests and 
the request body of POST requests, and a few attacks 
appear in other locations in the header, such as: user-agent, 
referer, X-Forwarded-For. Write scripts to extract valid 
attack payloads from http traffic. From the vulnerability 
information from 2015 to the present, more than 2,000 
payloads have been collected after data cleaning. These 
statement injection methods cover Boolean blind injection, 
time blind injection, joint query injection, error reporting 
injection and many others. 
It should be noted that there are many repetitive or 
similar expressions for each attack, for example, 
reduplicative attacks, as long as there is a perpetual true 
expression in the condition. But there are infinitely many 
such expressions, and it is meaningless to list them, so we 
have to eliminate these cases when cleaning the data. 
1830
Authorized licensed use limited to: Naresuan University provided by UniNet. Downloaded on November 11,2022 at 10:43:27 UTC from IEEE Xplore.  Restrictions apply. 


---

 
 
B. Pre-processing  
The purpose of sample preprocessing is to perform 
generalization and decoding to remove unnecessary noise 
(including inline annotations) from the training data. It is 
worth noting that the payloads obtained from reproduction 
of the vulnerabilities do not resemble deliberately created 
competition questions, most of which do not apply strange 
and complex obfuscations. 
According to the analysis of SQL injection attack, in the 
payload, symbols such as text, white space characters, 
quotation marks, etc. are specially customized and should 
not be generalized. In contrast, library names, table names 
and column names, etc., change with database settings and 
do not affect the syntactic nature of the attack payload, so 
they should be generalized. 
C. Sample generation 
1) GA 
Initialization. The most important part of this process 
is the selection of the gene list. Token is the most basic 
element in SQL syntax, if only a random permutation of 
token is combined, the generated statement is not 
necessarily a sequence with definite semantics and syntax. 
A list of genes is selected with different granularity 
sizes, which include: annotators, select statements, where 
statements, and/or, order by statements, group by 
statements, update statements, delete statements, drop, 
create, count, etc. We randomly selected genes from the 
gene list and generated individuals, initially choosing the 
number of genes to be 5. 100 individuals were generated 
per generation. 
Assessment. In this process, we evaluate the generated 
statements based on the syntactic nature of the SQL 
statement, i.e., whether the keywords in the statement can 
be accurately identified and later be successfully 
disassembled into a syntactic parse tree. 
SQLParse is a python-based non-validating SQL parser 
with the ability to parse, split, and format SQL statements. 
SQLParse has three basic functions: split (splitting strings 
containing multiple SQL statements into a list of SQL 
statements); format (formatting SQL statements); and 
parse (returning the result of SQL syntax parsing). 
The result of the statement "select * from foo where id 
in (select id from bar);" is as follows. 
stmt.tokens(<DML 'select' at 0x9b63c34>,  
  <Whitespace ' ' at 0x9b63e8c>,  
  <Operator '*' at 0x9b63e64>,   
  <Whitespace ' ' at 0x9b63c5c>,   
  <Keyword 'from' at 0x9b63c84>,   
  <Whitespace ' ' at 0x9b63cd4>,   
  <Identifier '"somes...' at 0x9b5c62c>,  
  <Whitespace ' ' at 0x9b63f04>,   
  <Where 'where ...' at 0x9b5caac>) 
Firstly, more than 2000 payloads are parsed using 
SQLParse to calculate an average value as the threshold for 
generating sample scores. Then the generated samples are 
parsed and the obtained scores are discarded if they are less 
than this threshold. 
Crossover. For two individuals, a point on each 
individual's gene is selected and swapped to obtain two new 
individuals. 
Mutation. That is, the mutation rate of individuals per 
generation. After experimental verification, this parameter 
did not have much influence on the final results, so we set 
it at 30%. 
2) GAN generation 
The validation of the effectiveness of the proposed 
algorithm was performed on a hardware platform 
configured with Intel(R) Core(TM) i7-9700 CPU 
@3.00GHz processor, 24GB RAM, and Windows 11 
operating system. The code implementation was performed 
under VS Code with python 3.6, keras 2.2.4, conda 4.11.0. 
Both the generator and discriminator use a neural 
network structure with four hidden layers. Similar to the 
deep learning model, there are many hyperparameters and 
model parameters that need to be adjusted. Try to achieve 
a balance between optimal parameters and computation 
time by random search. 
Table I shows the value of parameters used in the 
experiments. 
TABLE I. PARAMETERS USED IN THE EXPERIMENTS. 
params 
explaination 
values 
batch_size 
Number of samples used 
in a single training session 
500 
epoch 
The number of times all 
samples of the training set 
have been trained 
300 
dropout 
The probability of 
randomly discarding some 
neurons 
0.5 
activation 
function 
layer 
Providing nonlinearity for 
the network 
tanh/sigmoid/L
eakyReLU 
kernel_initia
lizer 
The weight matrix of the 
deep network is initialized 
glorot_uniform 
optimizer 
Gradient descent 
algorithm for optimization 
model 
Adam 
loss 
function 
binary classification loss 
(see previous 
section) 
Because a loss function image is output every 10 epochs 
in the experiment, there is no need to adjust the parameter 
epochs separately. As is shown in Fig. 5, the parameter 
settings of the control group (a) are chosen: LeakyReLU 
slope 0.2, batch size 500, and Adam optimizer learning rate 
0.0002. The parameters of the first experimental group (b) 
are set as follows: LeakyReLU slope 0.02. The parameters 
of the second experimental group (c) are set as follows: 
batch size 300. The parameters of the third experimental 
group (d) are set as follows: Adam optimizer learning rate 
0.002. We plot the loss function images of the generator 
1831
Authorized licensed use limited to: Naresuan University provided by UniNet. Downloaded on November 11,2022 at 10:43:27 UTC from IEEE Xplore.  Restrictions apply. 


---

 
 
and discriminator. In terms of code running time, except for 
(c) which has a slightly shorter running time, the other three 
groups have similar running time with a difference of no 
more than 3 minutes. In terms of the convergence effect of 
the loss function, (c) converges slowly, (b)(d) both fall 
short of the desired effect. However, (a) converges the 
fastest, with the loss value dropping rapidly from the 
beginning and remaining basically stable at about 0.693 
after fluctuations, with little noise. 
 
Fig. 5.  
The loss function image plotted after changing some hyperparameters. 
3) Variational operators 
After the above steps, a part of SQL injection 
statements has been generated. However, in real network 
environments, websites often deploy WAFs or IDSs for 
protection. In order to bypass the defense mechanism, 
obfuscation and mutation of statements are required to 
enhance the usability of the generated samples. Drawing 
on sqlmap's tamper script, combined with research on the 
interception rules of several WAF products (e.g., 
SafeDog), the following eight variant operators were 
designed to generate statements with more diversity 
(shown in Table II). 
TABLE II. VARIATIONAL OPERATORS AND SPECIFIC DESCRIPTIONS. 
Operators 
Explanation 
base64 
Base64-encodes all characters in a given 
payload 
Keywords 
Confusion of the capital and small letters of 
keywords 
Space 
Replaces space character (' ') with comments 
'/*/' 
UTF8 
Converts all (non-alphanum) characters in a 
given payload to overlong UTF8 (not 
processing already encoded) 
Apostrophe 
Replaces apostrophe character (') with its 
UTF-8 full width counterpart 
ASCII 
Unicode-URL-encodes all characters in a 
given payload (not processing already 
encoded) 
Interface 
Applies interference characters '/*x^x*/' to 
certain keywords 
Comment 
Encloses each keyword with versioned 
MySQL comment 
D. 
Evaluation 
SQLParse is used to do a check on the syntax of the 
generated statements. In this section, we build the 
application environment to verify the usability of the 
generated statements. The experimental environment is 
phpstudy2018, sqli-lab Range, and SafeDog V4.0 
official version. 
Specifically, the sqli-lab Range is first tested using 
the generated samples, and then the WAF is deployed on 
1832
Authorized licensed use limited to: Naresuan University provided by UniNet. Downloaded on November 11,2022 at 10:43:27 UTC from IEEE Xplore.  Restrictions apply. 


---

 
 
the website for further testing. It is worth noting that 
since our samples do not contain custom object variables 
such as table names, column names, library names, 
usernames, etc., this is taken into account when injecting. 
The results of our experiments are shown in the 
following Table III. 
TABLE III. EXPERIMENTAL RESULTS ON SQLI-LAB. 
Injection Type 
sqli-
lab 
sqli-
lab+Safe
Dog 
GET - Error based – 
Single/Double quotes - String 
√ 
√ 
GET - Error based - Intiger based 
√ 
√ 
POST - Double Injection - Single 
quotes- String -twist 
√ 
√ 
GET - Dump into outfile - String 
× 
× 
GET - Blind - Boolian Based - 
Single Quotes 
√ 
√ 
POST - Error Based – 
Single/Double quotes- String 
√ 
√ 
POST - Header Injection – User 
agent/Referer field - Error based 
√ 
√ 
Second Degree Injections  *Real 
treat* -Store Injections 
× 
× 
V. 
CONCLUSIONS 
In this paper, a variant of the genetic algorithm-based 
generative adversarial network model is used to generate 
SQL injection attack samples, which is enabled to 
expand the existing samples and solve the problems of 
missing, low and imperfect samples for SQL injection 
attacks to some extent. The gene granularity used in this 
paper is slightly coarse. By creating genes from injection 
codes used in actual vulnerability assessments, or by 
creating genes with smaller granularity, we are able to 
generate more complex and richer injection codes. 
In addition, we only evaluated the parsability of the 
scripts with SQLParse and checked the usability of the 
generated statements by web Range. Expectedly, the 
method could also be widely applied to other 
vulnerability attack samples, such as XSS scripts and 
command injection scripts. 
REFERENCES 
[1] Berman D S, Buczak A L, Chavis J S, et al. A survey of deep 
learning methods for cyber security[J]. Information, 2019, 10(4): 
122. 
[2] [EB/OL].https://tensorflow.google.cn/datasets/catalog/kddcup9
9. 
[3] [EB/OL].https://www.unb.ca/cic/datasets/nsl.html. 
[4] [EB/OL].https://www.unb.ca/cic/datasets/ids-2018.html. 
[5] Goodfellow I J, Warde-Farley D, Mirza M, et al. Maxout 
networks [C]. Proceedings of the 30th International Conference 
on Machine Learning (ICML), 2013: 1319-1327. 
[6] Feng XS, Shen Y, Wang DQ. A review of the development status 
of image-based data enhancement methods[J]. Computer 
Science and Application, 2021, 11: 370. 
[7] Wu Rui Xi, Xiao Qin Kun. Multi-object image recognition based 
on deep networks and data enhancement[J]. Foreign Electronic 
Measurement Technology, 2019, 5. 
[8] Zhang, X. F., Wu, G.. A data enhancement approach based on 
generative 
adversarial 
networks[J]. 
Computer 
Systems 
Applications, 2019, 28(10): 201-206. 
[9] Wu T-Y, Xu Y-C, Chao P-F. Research on data enhancement 
based on generative adversarial networks[J]. Optics and 
Optoelectronics Technology, 2020, 18(4): 47. 
[10] Gan Lan, Shen Hongfei, Wang Yao, et al. An improved 
DCGAN-based 
data enhancement 
method[J]. Computer 
Applications, 2021, 41(5): 1305. 
[11] Gong Hanyi, Su Fuwen, Gao Hanjun. A face recognition method 
based on improved genetic algorithm and BP neural network[J]. 
Journal of Wuhan University of Technology: Information and 
Management Engineering Edition, 2018, 40(5): 552-556. 
[12] Zhou, Yunpeng, Q. Justice. Application of genetic algorithm in 
combinatorial optimization[J]. Journal of Liaoning University of 
Engineering and Technology: Natural Science Edition, 
2005(z1):3. 
[13] Zhao Yuxiu. Research and application of knowledge discovery 
algorithm based on genetic algorithm[D]. Xi'an University of 
Architecture and Technology. 
[14] Wang Xiaohu, Wang Chao, Li Qun, et al. A black-box genetic 
algorithm-based approach to network security vulnerability 
mining in power systems[J]. Journal of Shenyang University of 
Technology, 2021, 43(5): 500-504. 
[15] Tang Y. Research on network security technology based on 
genetic algorithm[J]. Network Security Technology and 
Applications, 2021(9):3. 
[16] M. Sami and I. Mobin, "A comparative study on variational 
autoencoders and generative adversarial net- works," in 2019 
International Conference of Artificial Intelligence and 
Information Technology (ICAIIT), 2019, pp. 1-5. 
[17] B. Hitaj, P. Gasti, G. Ateniese, and F. Pérez-Cruz, "Passgan: A 
deep learning approach for password guessing," CoRR, 2017. 
Available: http://arxiv.org/abs/1709.00440 
[18] M. Salem, S. Taheri, and J. Yuan, "Anomaly generation using 
generative adversarial networks in host based intrusion detection, 
" CoRR, 2018. available: http://arxiv.org/abs/1812.04697 
[19] H. Chen and L. Jiang, "Gan-based method for cyberintrusion 
detection," CoRR, 
2019. 
Available: 
http://arxiv.org/abs/ 
1904.02426] [H. Chen and L. Jiang, "Gan-based method for 
cyber-intrusion 
detection," 
CoRR, 
2019. 
Available: 
http://arxiv .org/abs/1904.02426] 
[20] GOODFELLOW I J, POUGET-ABADIE J, MIRZA M, et al. 
Generative adversarial nets [C]// Proceedings of the 27th 
International Conference on Neural Information Processing 
Systems. Cambridge: MIT Press, 2014: 2672-2680. 
[21] RADFORD A, METZ L, CHINTALA S. Unsupervised 
representation learning with deep convolutional generative 
adversarial networks[J]. arXiv preprint arXiv:1511.06434, 2015. 
[22] C. Wang, C. Xu, X. Yao and D. Tao, "Evolutionary Generative 
Adversarial Networks," IEEE Transactions on Evolutionary 
Computation, vol. 23, no. 6, pp. 921 -934, Dec. 2019. 
[23] Wilson, Ashia C. et al. "The Marginal Value of Adaptive 
Gradient Methods in Machine Learning." arXiv abs/1705.08292 
(2017). 
[24] Goodfellow I. NIPS 2016 tutorial: generative adversarial 
networks. arXiv preprint arXiv: 1701.00160, 2016. 
1833
Authorized licensed use limited to: Naresuan University provided by UniNet. Downloaded on November 11,2022 at 10:43:27 UTC from IEEE Xplore.  Restrictions apply. 
