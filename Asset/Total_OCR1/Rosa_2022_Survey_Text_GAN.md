arXiv:2212.11119v1  [cs.CL]  20 Dec 2022
A Survey on Text Generation using Generative
Adversarial Networks
Gustavo H. de Rosa∗, Jo˜ao P. Papa
Department of Computing
S˜ao Paulo State University
Bauru, Brazil
Abstract
This work presents a thorough review concerning recent studies and text gen-
eration advancements using Generative Adversarial Networks.
The usage of
adversarial learning for text generation is promising as it provides alternatives
to generate the so-called “natural” language.
Nevertheless, adversarial text
generation is not a simple task as its foremost architecture, the Generative Ad-
versarial Networks, were designed to cope with continuous information (image)
instead of discrete data (text).
Thus, most works are based on three possi-
ble options, i.e., Gumbel-Softmax diﬀerentiation, Reinforcement Learning, and
modiﬁed training objectives. All alternatives are reviewed in this survey as they
present the most recent approaches for generating text using adversarial-based
techniques. The selected works were taken from renowned databases, such as
Science Direct, IEEEXplore, Springer, Association for Computing Machinery,
and arXiv, whereas each selected work has been critically analyzed and assessed
to present its objective, methodology, and experimental results.
Keywords:
Text Generation, Generative Adversarial Networks, Machine
Learning, Language Modeling, Natural Language Processing
∗Corresponding author
Email addresses: gustavo.rosa@unesp.br (Gustavo H. de Rosa), joao.papa@unesp.br
(Jo˜ao P. Papa)
Preprint submitted to Pattern Recognition
December 22, 2022


---

1. Introduction
Deep Learning has received the spotlight due to its capacity to solve human-
like tasks through hierarchical learning. Nevertheless, such an area depends on
proper representation learning to obtain high-quality performance and accom-
plish the intended task. For instance, Zhang et al. [1] presented a survey on
an eﬀective paradigm for representation learning denoted as Concept Factor-
ization, which is widely used to correlate data points and concepts as linear
combinations. Furthermore, Zhang et al. [2] introduced a novel approach to en-
hance optical character recognition with residual-based representation learning,
achieving state-of-the-art results using dense Convolutional Neural Networks.
Such applications are also extensible to the Natural Language Processing
(NLP) area, which also depends on precise representation learning to understand
how humans communicate using voice- and text-based patterns. Essentially, its
ultimate goal is to create algorithms capable of interpreting the human language
and between machines and humans.
A common task NLP-based task denoted as Language Modeling aims to un-
derstand the general text structure by learning its grammatical, syntactic, and
semantical rules. From a computational point of view, this task aims at pre-
dicting a t + 1 timestep based on previous t timesteps, where each timestep can
be composed of characters, words, or even sentences. Thus, a well-learned lan-
guage model can reproduce the training text structure by predicting new data
based on past information, e.g., text generation. For example, imagine that
a ﬁctitious language composed of three tokens follows this structure: <sub-
ject> <verb> <noun>. If a language model is capable of learning such struc-
ture, it is also capable of predicting a <verb> token based on input <sub-
ject> token, as well as predicting a <noun> token based on input <sub-
ject> and <verb> tokens.
One may realize that such a task is notably diﬀerent from traditional Ma-
chine Learning ones as it employs a new dependency, i.e., the time itself. In
other words, tokens (characters, words, sentences) are interpreted as sequences,
2


---

where each piece represents a particular timestep. Additionally, previous se-
quences must be carried to the future during learning, as the language model
predicts data based on past information [3]. Traditionally, researchers focus on
solving such a problem using Recurrent Neural Networks (RNN) [4], which can
re-use prior knowledge to learn future information. Even though RNNs seem to
be the ideal structure to tackle text generation problems, they are still suscepti-
ble to adversarial manipulation [5]. In other words, such models are vulnerable
to slight modiﬁcations in data that were not introduced in the learning process,
resulting in mispredictions and ineﬃcient performance. This vulnerability rep-
resents potential security threats and may compromise real-world applications,
remaining as an open research ﬁeld.
Goodfellow et al. [6] proposed the Generative Adversarial Networks (GAN)
and achieved several hallmarks concerning adversarial learning. Some recent
works [7, 8, 9] revealed their capability of learning data distributions and plau-
sibly generating artiﬁcial image-based data. Notwithstanding, such networks
were designed to deal with continuous information instead of discrete data [10],
i.e., they are not suitable when applied with sequences of texts. Thus, several
works attempt to tackle such an issue by employing Gumbel-Softmax diﬀerentia-
tion [11], Reinforcement Learning (RL) [12], or modiﬁed training objectives [13].
This paper proposes to survey and discuss the approaches mentioned above ap-
plied explicitly to text generation tasks.
Additionally, it aims to provide a
comprehensive source of text-based GAN advancements, where architectures
are critically analyzed in terms of datasets, objectives, evaluation metrics, and
experimental results.
The remainder of this paper is organized as follows. Section 2 presents the
survey structure, related surveys, and how surveyed works were selected. Sec-
tion 3 presents some theoretical background concerning Natural Language Pro-
cessing, Language Modeling, Generative Adversarial Networks, as well as some
text generation datasets and topmost evaluation metrics. Section 4 discusses
and provides an in-depth analysis of the surveyed works. Finally, Section 5
states overall conclusions and future insights regarding the surveyed context.
3


---

2. Survey Structure
2.1. Related Surveys
Text generation, formerly known as natural language generation, has re-
ceived a great deal of attention throughout the last years, mainly due to the
advance of computational power and Deep Learning-based architectures. Gatt
et al. [14] presented a survey regarding the advancements of natural language
generation. They categorized and discussed state-of-the-art data-driven archi-
tectures and presented the main drawbacks related to the synergy between nat-
ural language generation and other Artiﬁcial Intelligence areas. Nevertheless,
their survey aims to provide an overview of the task instead of diving into the
models’ architecture and their advantages/disadvantages.
A recent survey presented by Lu et al. [15] reviews and critically analyzes
adversarial-based text models’ development.
Even though their survey only
focuses on comparing six state-of-the-art architectures and the Maximum Like-
lihood Estimation over two benchmarking datasets, the authors established a
reference for those wanting to work with text-based adversarial learning. Fur-
thermore, Zhang et al. [16] proposed a survey in the context of adversarial
attacks on Deep Learning models in Natural Language Processing, where they
targeted on summarizing and discussing the types of adversarial attacks in-
stead of discussing the latest advancements regarding Generative Adversarial
Networks applied to text-based generation.
Therefore, the presented survey aims to fulﬁll the literature’s blank spots and
provide a unique reference of adversarial-based models applied to text genera-
tion. Extensive research has been conducted across several renowned databases
to identify the most promising text-based Generative Adversarial Networks.
Additionally, the selected models have been critically analyzed and discussed in
terms of objective, methodology, experimental results, and evaluation metrics.
Finally, the present work intends to categorize the text-based adversarial models
4


---

according to their diﬀerentiability strategy1, e.g., Gumbel-Softmax diﬀerentia-
tion, Reinforcement Learning, and modiﬁed training objectives.
2.2. Paper Selection
Initially, we performed an extensive search at renowned databases, such as
Science Direct, IEEEXplore, Springer, Association for Computing Machinery
(ACM), and arXiv, to deﬁne the starting year of the surveyed works. As the
Generative Adversarial Networks had been proposed in 2014 and the Gumbel-
Softmax approach had been proposed in 2016, we could only ﬁnd GAN-based
text generation with Gumbel-Softmax references beyond 2016. Additionally, no
work addressed GAN-based text generation with Reinforcement Learning and
modiﬁed training objectives before 2017.
3%
20%
29%
31%
17%
2016
2017
2018
2019
2020
Figure 1: Percentage of considered publications per publishing period.
With that in mind, we considered two keywords for performing the search:
(i) “generative adversarial network”, and (ii) “text generation”, and gathered
1It is essential to remember that Generative Adversarial Networks were not designed to
work with discrete data.
5


---

the resulting works that have been cited at least one time and that were relevant
to this survey context (GAN-based text generation). Furthermore, we veriﬁed
their authors’ background to check whether they were active researchers from
truthful laboratories and universities. Thus, the following publication period is
covered by the current survey: 2016 (1 work), 2017 (7 works), 2018 (10 works),
2019 (11 works), and 2020 (6 works), as illustrated by Figure 1.
3. Theoretical Background
This section presents a brief theoretical background regarding Natural Lan-
guage Processing, Language Modeling, Generative Adversarial Networks, Rein-
forcement Learning, and Gumbel-Softmax diﬀerentiation-based strategies. Ad-
ditionally, it describes an overview concerning the four most commonly employed
text generation datasets and some topmost evaluation metrics.
3.1. Natural Language Processing
Most human communication is performed through voice and text, i.e., vital
sources of information used to predict behavioral characteristics.
Neverthe-
less, it is hard to predict human-based communication because each individual
possesses particular traits in its written and verbal language, e.g., pitch, word
selection, vocabulary, and accent.
An area that arises in tackling such a problem is Natural Language Pro-
cessing, responsible for modeling and comprehending the interaction between
humans and machines through natural language usage. Deep Learning has re-
cently achieved several hallmarks regarding NLP-based tasks [17], introducing
state-of-the-art models for a wide variety of tasks, such as language modeling,
grammatical analysis, and named entity recognition, among others.
Nonetheless, one may perceive that NLP is often complicated due to lan-
guage’s intrinsic features (morphology, syntax, semantic) and the requirement
of knowledge to connect sequences of characters and words. Even though hu-
mans quickly learn and master languages, machines still struggle in such a task,
leaving it as an open research problem for the community.
6


---

3.1.1. Language Modeling
Language Modeling tasks stand for learning probabilistic models that can
predict a t + 1 timestep given t timesteps, e.g., predict the next word given
a sequence of words. A language model learns the probability of token occur-
rences based on examples, where simpler models might look at sequences of
characters or words, while larger models may learn sequences of sentences or
paragraphs. Notwithstanding, such tasks are often complicated as models need
to learn natural languages’ underlying traits, such as grammar, syntax, and se-
mantic. Additionally, as its learning procedure is based on a set of examples, it
poorly performs when employed with unknown data, e.g., not-learned tokens.
Most language models are used as root architectures for larger NLP tasks,
such as speech recognition, optical character recognition, machine translation,
and spelling correction.
On the other hand, a trained language model can
generate new text according to the structure it has already learned. Recently,
most language models are fostered by neural networks, achieving state-of-the-art
results due to their capacity for generalization. Furthermore, it is common to use
pre-trained embeddings, i.e., real-valued vectors that encode high-dimensional
representations of tokens (characters or words) in a projected vector space, to
tackle the curse of dimensionality2.
One may perceive that an interesting approach is to use RNNs, as they
can re-use their previous hidden states, where neurons are fed with recurrent
connections and learn a so-called “memory”. For example, a feed-forward net-
work is not ﬁt to create a probabilistic distribution capable of knowing that a
<noun> should come after a <verb>, as it only looks into the “future”. On the
other hand, recurrent networks can look into their past “memory” and decide
their subsequent output based on previous inputs.
2Curse of dimensionality happens when vast vocabularies are used, producing sparse rep-
resentations.
7


---

3.1.2. How to Generate Text?
A properly trained language model encodes features and rules from the
text it was trained.
In other words, the model has learned a probabilistic
distribution that represents the training data and samples new data.
Let
P(wt|wt−1, wt−2, . . . , wt−n) be the probability distribution of a token at t
timestep, given an n-sized sequence of previous tokens. The language model
estimates the probabilities of a token wt given a previous sequence of tokens,
allowing it to be sampled into a new token. Afterward, in t + 1 timestep, the
probability distribution tries to represent wt+1 given wt, wt−1, . . . , wt−n+1. The
process is repeated until a convergence criterion is satisﬁed, such as the number
of generated tokens. Finally, the resulting tokens are sequentially arranged to
form the generated text.
3.2. Generative Adversarial Networks
Szegedy et al. [18] found in their work that several Machine Learning archi-
tectures, including state-of-the-art, are vulnerable to adversarial manipulation,
i.e., these models could not correctly classify when fed with slightly diﬀerent
learning data. Years ago, Goodfellow et al. [6] introduced the Generative Adver-
sarial Networks as an alternative to the adversarial problem. It is implemented
as a two-neural networks system, where the networks compete in a zero-sum ap-
proach. Namely, the idea is to have a discriminative and a generative network,
where the generative one is in charge of producing fake data, and the discrimi-
native one is in charge of estimating the probability of the fake data being real.
Figure 2 illustrates an example of a standard Generative Adversarial Network.
Generator
Discriminator
Real
data
Fake
data
Noise
vector
Figure 2: Standard architecture of a Generative Adversarial Network.
8


---

The network’s discriminator D is trained to maximize the probability of
classifying both training and generated data as real images. Simultaneously, the
network’s generator G is trained to minimize log(1−D(G(z)), i.e., the divergence
among both data distributions, where z denotes a noisy input. In other words,
the two neural-networks system compete in a zero-sum game, represented by
Equation 1:
min
G max
D C(D, G) = Ex[logD(x)] + Ez[log(1 −D(G(z))],
(1)
where C(D, G) is the loss function to be minimized, D(x) is the discriminator’s
estimated probability of a real sample x being real, Ex is the mathematical
expectancy over all samples from the real data set X, G(z) stands for the gen-
erated fake data given the noise vector z, D(G(z)) is the estimated probability
of a fake sample G(z) being real, and Ez is the mathematical expectancy over all
random generator inputs, i.e., the expected value over all fake samples generated
by G.
Nevertheless, a deriving problem from Equation 1 is that GANs can get
trapped in local optimums when the discriminator has an easy task. In other
words, at the beginning of the training, when G still does not generate proper
samples, D can reject fake samples with high probability, as they are incredibly
diﬀerent from the real data3. Thus, an alternative to such a problem is to train
G to maximize log(D(G(z)), which improves the initial gradient values.
3.2.1. Diﬀerentiating GANs with Gumbel-Softmax
During GANs training, both generator and discriminator need a diﬀeren-
tiable loss function to update their parameters. However, when using RNN-
based architectures as GANs generators, it is impossible to diﬀerentiate its
output, usually accomplished by sampling one-hot categorical values from a
Softmax distribution.
3Such a problem saturates the function log(1 −D(G(z)).
9


---

A solution to such a problem proposed by Jang et al. [11] consists of sampling
from the so-called Gumbel-Softmax, which is a continuous distribution that can
approximate samples from categorical distributions.
Essentially, the idea is
to employ the Softmax distribution along with a Gumbel distribution and a
temperature parameter, as follows:
˜y =
e
w+g
τ
P e
w+g
τ
,
(2)
where ˜y stands for the diﬀerentiable outputs, w is a vector of unnormalized log
probabilities, g is a vector sampled out of the Gumbel distribution, and τ is
the temperature parameter. As τ →0, ˜y approximates a one-hot categorical
distribution, while ˜y approximates a uniform distribution as τ →∞.
3.2.2. Reinforcing GANs Learning
As previously mentioned, GANs need a diﬀerentiable loss function in order
to perform their training. An alternative to the Gumbel-Softmax trick consists
of creating a Reinforcement Learning-based agent for the generator. Essentially,
an RL algorithm is deﬁned by a policy function π(a|s, θ) parameterized by θ,
which outputs a probability distribution over all actions a given the current state
s of an agent. Note that s stands for the state of the agent (text generated),
and a stands for its actions (text to be generated). In other words, an agent
generates text based on the policy π, where its actions are sampled according
to the distribution deﬁned by the same policy.
Therefore, it is possible to
optimize θ by employing policy gradient methods, such as the REINFORCE
algorithm [19], to build a good text generation agent.
Let y = (y1, y2, . . . , yT ) | y ∈Y depict the sequence generation problem,
where Y is the vocabulary of candidate tokens and T is the number of tokens to
be generated. Let the generative model G be parametrized by θG and generate
a state s for each time t, which corresponds to a generated token yt. Further,
let its next action, denoted by a, be the next token yt+1 to be chosen. There-
fore, the policy G(yt | y1:t−1; θG) is stochastic, such that the transition state is
10


---

deterministic after an action has been chosen, i.e., δa
s,˜s = 1 for the next state
˜s = y1:t if the current state s = y1:t−1 and the action a = yt.
Additionally, the discriminative model D, which is parameterized by θD,
guides the generator through a probability D(y) that indicates whether a se-
quence y belongs to real data or not. This discriminative model is trained by
positive (real data) and negative (artiﬁcial data) samples, providing a reward
signal to update the generative model’s gradients. Equation 3 describes the
reward signal obtention procedure:
QG
D(a; s) =





1
N
PN
n=1 D(yn) | yn ∈MC(y1:t; N)
for t < T
D(y)
for t = T
,
(3)
where QG
D(a; s) is the action-value function of a sequence, i.e., the reward signal
accumulated from state s given an action a, and N is the number of Monte
Carlo samplings.
3.3. Datasets
The Amazon Customer Reviews4 [20] dataset, commonly denoted as Prod-
uct Reviews, is composed of more than 233, 000, 00 users reviews, which have
expressed their opinion and described their experience amongst products bought
over Amazon’s website. Furthermore, the Chinese Poems5 [21] dataset is com-
posed of 284, 299 poems from several online sources, such as Tang Poems, Song
Poems, Song Ci, Ming Poems, Qing Poems, and Tai Poems.
The COCO Image Captions6 [22] dataset has been developed through the
capture of image captions belonging to the Microsoft Common Objects in Con-
text (MS COCO) dataset. In sum, humans created 1, 026, 459 captions from
the same data sets used by MS COCO and divided them across two sub-sets:
one with 5 reference sentences for each image and another one with 40 refer-
ence sentences for 5, 000 randomly chosen images. All candidate captions have
4https://nijianmo.github.io/amazon/index.html
5https://homepages.inf.ed.ac.uk/mlap/Data/EMNLP14
6https://cocodataset.org
11


---

been pre-processed and tokenized according to the Stanford PTBTokenizer, fol-
lowing the same protocols established by the Penn Treebank dataset.
After
pre-processing, all punctuation marks have been removed to standardize the
captions. Finally, the EMNLP2017 WMT News7 [23] dataset has been devel-
oped to foster machine translation tasks, being composed of pairs of documents,
such as sets of sentences amongst two distinct languages. Nevertheless, it is pos-
sible to adjust such a dataset to the natural language generation task and use
only sentences corresponding to the same language.
3.4. Evaluation Metrics
The task of natural language generation allows the machine to create arti-
ﬁcial information and understand natural languages. However, it is necessary
to assess such information’s quality and compare them against those created by
human beings. Therefore, the advent of algorithms focused on evaluation met-
rics allowed the estimation of how “relevant” the generated information is and
enabled ways to benchmark their quality between several language generation
architectures.
3.4.1. Bilingual Evaluation Understudy
Bilingual Evaluation Understudy (BLEU) [24] evaluates the quality of machine-
generated text and is structured by the correspondence of source text (written by
humans) and artiﬁcial text (generated by machines). Essentially, it is calculated
by the co-occurrence of n-grams between the reference and candidate sentences,
computing a type of precision between the sentences. Let Φ = {φ1, φ2, . . . , φκ}
be the reference sentences with κ tokens, while ˜Φ = {˜φ1, ˜φ2, . . . , ˜φω} is the
candidate sequence with ω tokens. Equation 4 describes its formula, as follows:
Pn =
P
k min(dk(˜φ), max dk(φ))
P
k dk(˜φ)
,
(4)
7http://statmt.org/wmt17/results.html
12


---

where dk(·) is the amount of occurrences of an n-gram and k is the maximum
number of possible n-grams. However, such formula inﬂates the metric’s value
for short sentences and needs a penalization factor according to Equation 5:
b =





1
if ω > κ
e1−κ
ω
if ω ≤κ
.
(5)
Therefore, the ﬁnal BLEU score is calculated by a geometric mean weighted
by the individual’s n-grams precision. Moreover, the metric’s value is within
the [0, 1] interval, where values close to 1 indicate a bigger similarity between
the sentences. Equation 6 describes such procedure, as follows:
BN = b · exp((
N
X
n=1
wn log(Pn))),
(6)
where n = 1, 2, 3, . . ., N and wn is a constant for all n values.
3.4.2. Negative Log-Likelihood
Negative Log-Likelihood (NLL) [25] is usually used as a loss function in
Machine Learning training algorithms and aims at maximizing the probability
of correct classiﬁcations. In other words, during a linguistic model training,
NLL is used to verify whether the network is learning to generate t + 1 tokens
given the previous t tokens.
Let K be the number of classes to be classiﬁed, i.e., the number of possible
generated tokens. The loss function is deﬁned according to Equation 7:
NLL = −1
n
X
x∈X
K
X
k=1
yk · eak,
(7)
where n is the number of samples in training set X, x is the input data, y is the
true label in one-hot encoding, and a is the network’s output. The NLL metric
is commonly used to evaluate a network’s learning quality and is restricted to a
positive interval, e.g., [0, +∞]. Additionally, as NLL tends to 0, the network can
learn the training set patterns, i.e., correctly predicting the training samples’
labels.
13


---

3.4.3. Perplexity
Perplexity (PPL) [26] is calculated by the exponentiation of NLL, furnishing
a more intuitive metric. Given that PPL is just the exponentiation of NLL,
its interval is restricted to [1, +∞], where smaller values correspond to a well-
trained network, and higher values correspond to a poor learning procedure.
4. Analysis and Discussion
This section presents the critical analysis and discussion regarding the com-
piled works, which are categorized as follows: (i) GAN-based text generation
with Gumbel-Softmax diﬀerentiation, (ii) GAN-based text generation with Re-
inforcement Learning, and (iii) GAN-based text generation with modiﬁed train-
ing objectives. Additionally, Figure 3 describes the methodological pipeline used
to conduct text generation with the mentioned approaches, and Table 1 de-
scribes an overview regarding the surveyed works, where the following columns
have depicted each work: reference, architecture, datasets, objectives, evalu-
ation metrics, and experimental results, while Table 2 comprehends a set of
architectures evaluated with the most common metric (BLEU-2) over the four
most common datasets: Amazon Reviews, Chinese Poems, COCO Image Cap-
tions, and EMNLP2017 WMT News.
Negative
Samples
Positive
Samples
Generator
Real Data
Discriminator
Discriminator
Generator
Reward
Reward
Reward
Reward
State
Action
Policy Gradient
Figure 3: Pipeline commonly used to conduct the adversarial-based text generation. Note
that for Gumbel-Softmax diﬀerentiation and modiﬁed training objectives, the discriminator
directly rewards the generator (without Reinforcement Learning) as their functions are diﬀer-
entiable.
14


---

Reference
Architecture
Dataset
Objectives
Metrics
Results
Kusner,
Hern´andez-
Lobato [27]
GSGAN
Context-Free
Gram-
mar
Gumbel-Softmax
with
discrete data.
Visual inspection
Samples similar to an
MLE-trained LSTM.
Nie et al. [28]
RelGAN
COCO
Image
Cap-
tions,
EMNLP2017
WMT News
Relational
Memory
generator and Gumbel-
Softmax distribution.
NLL, BLEU
Outperformed
mod-
els
when
RelGAN
pre-training was good.
Yin et al. [29]
Meta-CoTGAN
COCO
Image
Cap-
tions,
EMNLP2017
WMT News
Cooperative
approach
with an additional lan-
guage model.
NLL, BLEU
Positive
impact
of
cooperatively approach
and meta optimization.
Yu et al. [30]
SeqGAN
Chinese
Poems,
Nottingham
Mu-
sic,
Obama
Speech,
Synthetic Data
Stochastic
Reinforce-
ment Learning gradient
policy updates.
NLL, BLEU
First model to extend
GANs to discrete token
generation.
Lin et al. [31]
RankGAN
Chinese Poems, COCO
Image
Captions,
Shakespeare Plays
Ranked data instead of
real and fake.
BLEU
Could
not
compete
with
human-written
sentences.
Wang et al. [32]
VGAN
Taobao Reviews, Ama-
zon Review, Penn Tree-
bank
High-latent
variables
with
Variational
Au-
toEncoders (VAE).
NLL, BLEU
Successfully
applied
VAEs
to
adversarial-
based models.
Guimaraes et al. [33]
ORGAN
Molecules Dataset, Es-
sen Associative Code
Domain-speciﬁc objec-
tives
and
discrimina-
tor’s rewards.
Diversity, Validity
Generated
domain-
based data,
with RL
being essential.
Guo et al. [34]
LeakGAN
Chinese Poems, COCO
Image
Captions,
EMNLP2017
WMT
News, Synthetic Data
Leaked high-level fea-
tures from the discrim-
inator into the genera-
tor.
NLL, BLEU
Concluded that leaked
information is vital to
the network’s learning.
Hjelm et al. [10]
BGAN
Google
One
Billion
Words
Compute
importance
weights with diﬀerence
measures.
Visual Inspection
Scratch stable training
yet poor generation.
continues on next page
15


---

Fedus et al. [35]
MaskGAN
IMDB
Movie,
Penn
Treebank
Actor-critic conditional
architecture.
Percentage of Unique
n-Grams
Produced
reasonable
sentences,
yet not as
good
as
the
ground
truth.
Li et al. [36]
CS-GAN
Amazon Review, Emo-
tion, NEWS, Stanford
Sentiment
Treebank,
Yelp Review
Incorporated
sentence
category over the archi-
tecture.
NLL, Accuracy
Suﬀered
from
large
amounts of data and
binary labels.
Balagopalan et al. [37]
RE-GAN
Context-Free
Gram-
mar
Comparative study be-
tween
three
distinct
policy gradient meth-
ods.
Goodness Score
Needed
a
signiﬁcant
pre-training.
Shi et al. [38]
IRL
COCO
Image
Cap-
tions,
IMDB
Movie,
Synthetic Data
Inverse
RL
architec-
ture.
BLEU,
F-BLEU,
B-
BLEU, HM-BLEU
Alleviated the problem
of reward sparsity and
mode collapse.
Xu et al. [39]
DP-GAN
Amazon
Review,
OpenSubtitles
Dia-
logue, Yelp Review
Novel discriminator to
distinguish between re-
peated and novel text.
BLEU, Relevance, Di-
versity, Fluency
Produced more diverse
text, and better distin-
guished novel and re-
peated text.
Chen et al. [40]
CTGAN
Amazon
Review,
Film Review,
Obama
Speech, Yelp Review
Mimicked
human-
like
text
generation
by
introducing
new
features.
Similarity,
Diversity,
Word Frequency, Sub-
jectivity, Sentiment
Simpliﬁed text gener-
ation
process
outper-
formed baselines.
Wang, Wan [41]
SentiGAN,
C-
SentiGAN
BeerAdvocate,
Cus-
tomer Reviews, Emo-
tional Tweet, Stanford
Sentiment Treebank
Multiple
generators
with
a
penalty-based
objective.
Novelty, Diversity
Tagged
as
promising
approaches in domain-
based text generation.
Zhang et al. [42]
CD-GAN
Amazon Review, Yelp
Review
Annotated
data from
distinct
domains
to
generated
emotional
text.
Sentiment
Transfer
Strength,
Domain
Transfer Strength, Co-
sine Similarity,
Word
Overlap
Achieved
compara-
ble
results
to
the
compared
baselines
(sentiment
transfer
state-of-the-art).
continues on next page
16


---

Zhang et al. [43]
TranGAN
Penn Treebank
Transformer-based ar-
chitecture trained with
an actor-critic RL algo-
rithm.
Perplexity, Percentage
of
Unique
n-Grams,
BLEU
Processed discrete se-
quences
and
outper-
formed compared base-
lines.
Liu et al. [44]
BFGAN
Amazon Review, Chi-
nese Sentence Making
Corpus, DailyDialog
Backward and forward
generators
with
a
discriminator
capable
of guiding their joint
training.
BLEU, SLEU
Improved
quality
of
lexically-constrained
sequences, and did not
need additional labels.
Sun et al. [45]
QuGAN
Tibetan Q&A
QRNNs and improved
both reward and Monte
Carlo search strategies.
BLEU
Model with optimized
Monte
Carlo
search
and
BERT
outper-
formed
compared
models.
Rizzo, Van [46]
C-SeqGAN
Amazon
Review,
COCO
Image
Cap-
tions,
EMNLP2017
WMT News
Context
adaption
of
global
word
em-
beddings,
as
well
as
a
self-attention
discriminator.
BLEU,
Pos-BLEU,
Self-BLEU
Improved SeqGAN by
using
global
knowl-
edge
adapted
to
the
dataset’s domain.
Wu, Wang [47]
TG-SeqGAN
COCO Image Captions
Rewarded the genera-
tor with the distance
between real and fake
data.
NLL, Embedding Simi-
larity
Improved the training
convergence
and
the
text quality.
Zhou et al. [48]
SAL
COCO
Image
Cap-
tions,
EMNLP2017
WMT News, Synthetic
Data
Comparative discrimi-
nator instead of a bi-
nary one,
as well as
a self-improvement re-
ward mechanism.
NLL, BLEU, Perplex-
ity, Frechet Distance
Improved the rewards
system by reducing the
sparsity and mode col-
lapse, leading to a bet-
ter text generation.
Che et al. [13]
MaliGAN
Chinese Poems
Normalized
maximum
likelihood with impor-
tance
sampling
and
variation reduction.
BLEU, Perplexity
Created
distributions
with
lower
variances
and a better discrimi-
nator.
continues on next page
17


---

Zhang et al. [49]
TextGAN
Combined
data
from
BookCorpus
and
ArXiv
High-dimensional
latent
feature
distri-
bution with kernelized
discrepancy.
BLEU, Number of Ker-
nel Density Estimators
Learned
a
suitable
latent
representation
space
and
produced
realistic sentences.
Gulrajani et al. [50]
WGAN-GP
Google
One
Billion
Words
Gradient penalization.
Visual Inspection
Generated
discrete
data, yet not compara-
ble to baselines.
Press et al. [51]
AltGAN
Google
One
Billion
Words
Curriculum
learning
and slow teaching.
Percentage of Unique
n-grams
Adequately
trained
from scratch.
Chen et al. [52]
FM-GAN
COCO
Image
Cap-
tions, CUB Captions,
EMNLP2017
WMT
News
Latent
feature
distri-
butions with Feature-
Mover’s Distance.
Test-BLEU,
Self-
BLEU, Human Evalu-
ation
Produced
good
sen-
tences, yet still suﬀered
from mode collapse.
Donahue,
Rumshisky [53]
LaTextGAN
Toronto Book Corpus
AutoEncoder.
Human Discriminator,
BLEU, t-SNE Plots
t-SNE
plots
showed
that it could model the
latent space.
Li et al. [54]
JSD-GAN
Chinese Poems, COCO
Image
Captions,
EMNLP2017
WMT
News, Obama Speech
Optimize
Jensen-
Shannon Divergence.
BLEU
RL-free
with
direct
generator
optimiza-
tion,
yet
only
for
explicit
representa-
tions.
Haidar et al. [55]
TextKD-GAN
Google
One
Billion
Words, Stanford Natu-
ral Language Inference
Knowledge distillation
technique
based
on
teacher-student model.
BLEU
Smoother
text
repre-
sentations
and
out-
performed
traditional
GANs.
Ahamad [56]
STGAN
BookCorpus, CMU-SE
Encoder-decoder archi-
tecture inspired by the
skip-gram model.
BLEU
Skip-thought
embed-
dings
could
generate
discrete data.
Montahaei et al. [57]
DGSAN
Chinese Poems, COCO
Image
Captions,
EMNLP2017
WMT
News
Optimized closed-form
solution to ﬁnd an op-
timal discriminator.
NLL,
BLEU,
Self-
BLEU, MS-Jaccard
Outperformed
base-
lines
regarding
the
MS-Jaccard
metric,
yet
achieved
slightly
lower Self-BLEU.
continues on next page
18


---

Yang et al. [58]
FGGAN
Chinese Poems, COCO
Image Captions, Syn-
thetic Data
Feature guidance mod-
ule
and
a
new
vo-
cabulary mask to bet-
ter represent semantic
rules.
NLL, BLEU
Outperformed
current
baselines
and
gener-
ated more realistic sen-
tences due to token re-
striction.
Wu et al. [59]
TextGAIL
COCO
Image
Cap-
tions,
EMNLP2017
WMT News
Pre-trained
language
models
with
con-
trastive
discriminator
and
proximal
policy
optimization.
NLL,
BLEU,
Self-
BLEU, Perplexity
Generated diverse and
accurate
outputs
due
to the incorporation of
pre-trained GPT-2 and
pre-trained RoBERTa.
Table 1: Summarization of the works considered in this survey.
Architecture
Amazon Review
Chinese Poems
COCO Captions
WMT News
MLE
−
0.667
0.781
0.768
RNNLM
0.848
−
−
−
RelGAN
−
−
0.849
0.881
Meta-CoTGAN
−
−
0.858
0.882
SeqGAN
0.856
0.739
0.745
0.777
VGAN
0.868
−
−
−
RankGAN
−
0.812
0.743
0.727
LeakGAN
−
0.881
0.746
0.826
IRL
−
−
0.829
−
BFGAN
0.920
−
−
−
SAL
−
−
0.785
0.788
FGGAN
−
−
0.773
−
MaliGAN
−
0.741
−
−
JSD-GAN
−
0.536
0.894
0.943
Table 2: BLEU-2 benchmark regarding architectures that use such a metric to
evaluate the four most common datasets.
19


---

4.1. Text Generation using GANs and Gumbel-Softmax Diﬀerentiation
Continuous distributions that resemble categorical distributions, such as the
Gumbel-Softmax, tackled the diﬀerentiation problem and became alternatives
to enable proper backpropagations of GANs’ gradients. Initially, Kusner and
Hern´andez-Lobato [27] presented the Gumbel-Softmax Generative Adversarial
Network (GSGAN), a text-based GAN that uses the Gumbel-Softmax distribu-
tion for generating its outputs. Their work was conducted using 5, 000 samples
with a maximum length of 12 characters generated from a context-free gram-
mar (CFG) and evaluated by visual inspection of the generated data compared
with a standard Maximum Likelihood Estimation (MLE) pre-trained LSTM.
Nevertheless, such an architecture could only produce comparable results to the
pre-trained LSTM and was no match for the Relational Generative Adversarial
Network (RelGAN), introduced by Nie et al. [28].
The RelGAN introduced a Relational Memory-based generator, a Gumbel-
Softmax relaxation, and a multi-embedded representation discriminator to com-
pose their architecture. Their experiments were conducted using synthetic data
generated by an oracle LSTM [30] and real datasets, such as COCO Image
Captions and EMNLP2017 WMT News, being compared to state-of-the-art ar-
chitectures (MLE, SeqGAN, RankGAN, and LeakGAN). Its main advantage
lies in using a Relational Memory generator, which better extracts long-term
dependencies due to self-attention layers. In contrast, its main disadvantage lies
in needing a proper pre-training to generate feasible text, increasing the overall
system’s computational burden.
Nonetheless, adversarial-based models’ increasing problem was the mode
collapsing, where generators tend to sacriﬁce diversity for quality. In such a
context, the Meta Cooperative Training Paradigm Generative Adversarial Net-
work (Meta-CoTGAN), proposed by Yin et al. [29], attempted to slow the eﬀect
of mode collapsing. The authors evaluated the impact of the cooperative train-
ing language model and meta optimization using the same protocol proposed
by Nie et al. [28]. Although the authors eased the mode collapsing problem,
Meta-CoTGAN had a higher computational cost due to being trained with an
20


---

additional language model during the adversarial training.
With the mentioned architecture in mind, it is possible to observe that their
main disadvantage lies in pre-training both discriminator and generator ahead
of the adversarial training, burdening the computational powers. On the other
hand, one can perceive that Gumbel-Softmax distributions employ an additional
temperature parameter, which controls the generated text’s diversity and qual-
ity, thus being an interesting parameter to be ﬁne-tuned. Additionally, such
models mostly need a mathematical replacement in their output layer (from
Softmax to Gumbel-Softmax), which provides a straightforward implementa-
tion and a not so complex system.
4.2. Text Generation using GANs and Reinforcement Learning
Most Gumbel-Softmax-based approaches have a pre-training burden in ad-
vance to the adversarial training and directly rely on traditional GANs objec-
tives, which may cause premature collapsing and an inadequate equilibrium
between generator and discriminator. An alternative to tackling such a prob-
lem is to bypass the generator’s diﬀerentiation problem using stochastic gradient
policy updates. The idea is to acquire rewards signals from the discriminator
and pass them back to the generator in the same way a Reinforcement Learning
method would do, such as the REINFORCE algorithm.
The ﬁrst RL-based work has been introduced by Yu et al. [30], denoted as Se-
quence Generative Adversarial Network (SeqGAN). Their proposed architecture
uses the REINFORCE algorithm, and Monte Carlo searches to propagate the
discriminator’s gradients to the generator. SeqGAN was the ﬁrst RL-based work
and could only be compared to standard MLE-based training, yet it established
a hallmark for future RL-based research. Although SeqGAN tackled adversarial-
based text generation, the model lacked generalization power and produced text
with minimum diversity. With that in mind, an alternative suggested by Wang
et al. [32] employs additional features learned by Variational AutoEncoders to
represent text better. The so-called VGAN proposed to use high-level latent
random variables to model the variability of text, aiding traditional Recurrent
21


---

Neural Networks in learning well-structured data. Their combined model used
an RL-based approach to update the generator’s gradients and the same gra-
dient policy deﬁned by SeqGAN. Finally, VGAN outperformed the compared
benchmarks, such as recurrent-based Language Models and SeqGAN, over three
public literature datasets.
Another SeqGAN extension, denoted as Objective-Reinforced Generative
Adversarial Networks (ORGAN), attempted to improve the learning process
by including domain-speciﬁc objectives in addition to discriminator’s rewards.
In other words, ORGAN [33] proposed to extend the reward function through
a linear combination between the discriminator and domain-speciﬁc objectives
rewards, followed by a Wasserstein distance training. Their experimental results
outperformed standard baseline approaches, such as MLE and SeqGAN, while
the authors concluded that ORGAN could generate domain-based data and that
RL plays an essential role in the model’s learning.
Notwithstanding, such precedents enabled researchers to pursue new forms of
inputting external information and improving domain-related text generation.
In such a context, Li et al. [36] proposed the Category Sentence Generative
Adversarial Network (CS-GAN), which extends traditional text-based GANs
with additional category information. Essentially, they proposed both generator
and discriminator that incorporate the sentence category (label), allowing the
system to capture such information in its learning procedure and generate text
according to their category. On the other hand, Rizzo and Van [46] proposed an
extension of the standard SeqGAN by employing context adaptation of global
word embeddings and a self-attention discriminator. The so-called C-SeqGAN
aimed at using the contribution of global knowledge adapted to the dataset’s
domain and a self-attentive discriminator that slowly minimizes the loss function
and better provides feedback to the generator’s updates. The experiments were
performed under an extensive evaluation regarding short-, medium, and long-
length text datasets and outperformed diﬀerent SeqGAN-based baselines.
One can perceive the advantage of employing additional information, which
assists the network in learning domain-related structures and producing more
22


---

feasible texts.
Nevertheless, using domain-related information may result in
substantial mode collapses as the network will lose its diversity capability and
generate similar text. Some authors opted not to rely on external information
and employ variable reward signals to overcome such a problem. For instance,
the Generative Adversarial Network (RankGAN) [31] employs a ranking-based
architecture to produce high-quality generations. It evaluates and ranks col-
lections of human- and machine-written sequences over a reference group in-
stead of training a discriminator to learn binary predictions. One can perceive
that such an approach is inspired by the ranking steps commonly used in web
searches and allows the model to calculate the expectations given diﬀerent refer-
ences sampled across the reference space. To calculate such values, the authors
formulated a relevance score using cosine similarity followed by a softmax acti-
vation, which allowed them to compute a collective ranking score for an input
sequence. Alternatively, the Diversity-Promoting Generative Adversarial Net-
work (DP-GAN) [39] has been proposed to overcome the problem of generating
repetitive and “boring” text sequences. Essentially, DP-GAN assigns a low re-
ward value when generating text repeatedly while assigning high rewards when
generating novel text. One can observe that such an approach encourages the
generator to produce a more diverse text. Additionally, the authors proposed a
new discriminator, which is better at distinguishing between repeated and novel
text.
Moreover,
the
Boundary-Seeking
Generative
Adversarial
Network
(BGAN) [10] uses estimated diﬀerence measures from the discriminator
to compute importance weights for the generated samples, providing a policy
gradient for training the generator. In other words, BGAN models the strong
connection between the discriminator’s decision boundaries, allowing it to work
with continuous data.
BGAN uses f-divergences, such as Jensen-Shannon,
Kullback-Leibler (KL), Reverse KL, or Squared-Hellinger policy gradients and
rewards for the generator, being trained with the REINFORCE algorithm.
BGAN yielded stable training even though its generation was inadequate as
no pre-training was involved. The authors stated that they were not aware of
23


---

any previous work that could successfully train from scratch a non-continuous
architecture and that, although their generation was inadequate, the results
demonstrated the stability and capacity of BGANs working with discrete data.
A recurrent disadvantage of modifying the rewards signals occurs when net-
works can not provide feasible signals during the starting epochs, hampering the
learning process and preventing the generator from being adequately trained.
In such a context, few works attempted to present novel RL-based strategies
based on pre-training, joint rewards, and additional policy gradient algorithms.
Liu et al. [44] presented a novel architecture for generating lexically-constrained
sentences, denoted as Backward and Forward Generative Adversarial Network
(BFGAN). Speciﬁcally, their idea was to employ both backward and forward
generators with a discriminator that guides their joint training by assigning re-
ward signals, being pre-trained with MLE before the adversarial learning, and
then trained using the REINFORCE algorithm.
Regarding text-based GANs, policy gradient methods usually provide reward
functions that sample a token per timestep without considering their surround-
ings and being unfeasible when dealing with long sequences. Thus, Balagopalan
et al. [37] introduced a comparative study between three policy gradient alterna-
tives, i.e., REBAR, RELAX, and slightly diﬀerent REINFORCE. The proposed
methods denoted as REGANs, aim at providing distinct reward functions to
attain a probability distribution over all tokens generated by the generator. Ex-
periments were conducted using synthetic context-free grammar and compared
across REBAR, RELAX, and REINFORCE architectures. Alternatively, an In-
verse Reinforcement Learning [60] algorithm has been proposed for text-based
GANs, denoted as IRL [38]. The authors stated that their method has two
main advantages over the traditional RL algorithm: (i) the reward function
can produce denser reward signals, and (ii) an entropy regularized-based policy
gradient encourages the generation of diverse texts. Unlike traditional GANs,
IRL does not directly use a discriminator, where, instead, it uses a reward func-
tion that aims to increase the rewards from authentic texts and decrease the
rewards from the generated texts. Thus, the generator is trained via entropy
24


---

regularized policy gradients [61] by maximizing the expected rewards. The ex-
perimental results attest that the proposed method alleviated reward sparsity
and mode collapsing while achieving comparable results regarding the previous
state-of-the-art, e.g., LeakGAN.
Most approaches mentioned above struggled to generate human-like texts
and often faced a lack of diversity in the created sentences. With that in mind,
some authors attempted to mimic human-like text generation by using pre-
viously unused features, such as variable text length, emotion label (positive,
negative, or neutral), and controllable topic. The Conditional Text Generative
Adversarial Network (CTGAN) [40] is trained using the REINFORCE algo-
rithm and composed of a conditional LSTM generator that uses the emotion
label and the text as its input. Additionally, it employed a conditional discrim-
inator (standard CNN) to classify whether the text is real or generated. The
authors customized the text generation using speciﬁc keywords and automated
the word-level replacement strategy to extract the target word and replace it
with a similar one.
Instead of only using emotions as additional features, Wang and Wan [41]
extended the previous work by proposing both Sentimental Generative Adver-
sarial Network (SentiGAN) and Conditional Sentimental Generative Adversarial
Network (C-SentiGAN), which are capable of generating text with diﬀerent sen-
timent labels. In short, the idea is to train multiple generators simultaneously
and use a penalty-based objective function to force each generator in sampling
speciﬁc sentiment texts. Furthermore, a multi-class discriminator helps each
generator in generating its particular texts. Another architecture capable of
generating emotional text is the Cross-Domain Text Sentiment Transfer Gen-
erative Adversarial Network (CD-GAN) [42], which uses annotated data from
other domains and overcomes the problem of large-scale annotated data re-
quirement.
The CD-GAN aimed to combine adversarial RL and supervised
learning to extract sentiment transformation patterns and generate emotional
text. Its architecture comprises a Seq2Seq generator and two discriminators,
one accountable for sentiments and another for domains. Both discriminators
25


---

outputted rewards to update the generator’s gradients and enabled the gener-
ator to observe how good its generation is based on the input data sentiment
(non-labeled data) and related to the auxiliary domain (labeled data).
An alternative to traditional Reinforcement Learning methodologies is to
split their knowledge into additional modules, such as manager/worker and ac-
tor/critic. Such architectures’ advantage is their capacity to represent the policy
functions better as they consider past actions and compare them to baselines
to provide the reward signals.
In other words, it decides how much reward
should be given to a generator based on its previous text generations, guiding
the network to more feasible updates and hence, better quality text. With that
in mind, Guo et al. [34] proposed the Leaked Information Generative Adver-
sarial Network (LeakGAN), which allows the discriminator to leak high-level
extracted features to the generator and helps to guide the generator as it pro-
vides additional information through its learning steps. The idea is to split the
generative network into two modules, the MANAGER and WORKER, where
the MANAGER takes the leaked information from the discriminator and builds
a feature vector further to feed the WORKER module. Both MANAGER and
WORKER modules are distinct RNN-based architectures and trained via the
REINFORCE algorithm. Additionally, the authors proposed a Bootstrapped
Re-scaled Activation, where rewards are re-scaled to mitigate the vanishing
gradient problem. The experimental results showed that leaking information
is vital to the network’s learning process and better guides the generator in
generating long text, achieving performance improvements over the previous
state-of-the-art architectures.
Following the actor-critic-based architectures, Fedus et al. [35] introduced
the Mask Generative Adversarial Network (MaskGAN), which uses an actor-
critic conditional GAN to ﬁll in missing text conditioned on the surrounding
context. One can perceive that such a task is more challenging than text gener-
ation, helping the model reduce the generator’s risk competing with an almost-
perfect discriminator. Additionally, in-ﬁlling tasks might mitigate the problem
of mode collapsing as they provide rewards every timestep. The generator is
26


---

based on a Seq2Seq [62] architecture and is trained via policy gradients using the
REINFORCE algorithm. Furthermore, rewards are generated at each timestep,
and the maximum sequence length is increased upon satisfying a convergence
criterion. Also, to alleviate the REINFORCE variance problem, the authors pro-
posed generating rewards based on the whole generator’s distribution instead
of only using the sampled token.
On the other hand, Zhang et al. [43] im-
proved the standard actor-critic methodology by proposing a transformer-based
architecture for the generator, denoted as Transformer Generative Adversar-
ial Network (TranGAN). Essentially, an encoder-decoder system constitutes the
transformer-based architecture, where each layer is composed of multi-head self-
attention and feed-forward networks in an attempt to extract long-term depen-
dencies and information from the surrounding context. The proposed model,
TranGAN, was compared against a standard Seq2Seq architecture and SeqGAN,
outperforming both models in almost all metrics, while the authors concluded
that they could eﬀectively process discrete sequences through the actor-critic
training algorithm.
Despite already known several RL-based strategies, researchers often grap-
pled with the incapacity of generating long texts within a feasible amount of
computation burden.
Additionally, the lack of context (text semantics over
time) in most GAN-based text generation architectures fostered the necessity of
ﬁnding alternative improvements. Therefore, Sun et al. [45] presented a Quasi
Generative Adversarial Network (QuGAN) for Tibetan Question Answering cor-
pus generation, which extends traditional GANs by using the power of Quasi-
Recurrent Neural Networks (QRNN) and improving both reward and Monte
Carlo search strategies. As QRNNs are combinations of both RNNs and CNNs,
they are often used to deal with long sequences of data and data parallelization,
providing a faster text generation. Additionally, the authors employed a BERT
model after the text generation to correct the generator’s grammatical mis-
takes. Alternatively, by employing a truth-guided generator and self-attention-
based discriminators, Wu and Wang [47] proposed the Truth-Guided Sequential
Generative Adversarial Network (TG-SeqGAN) to improve text generation and
27


---

make it look closer to the real data.
The generator is essentially rewarded
with the distance between real and fake data, guiding its convergence, while
the discriminator network has a self-attention mechanism to capture long-term
dependencies.
Another general improvement, proposed by the Self-Adversarial Learning
(SAL) [48] architecture, is to employ a comparative discriminator capable of
comparing text quality among samples’ pairs. Moreover, throughout the train-
ing step, SAL rewards the generator when a generated sentence appears to be
better than the previously generated ones. Such an approach stands for a self-
improvement reward mechanism, which allows the model to receive more valu-
able feedback and avoid collapsing due to the limited number of real samples,
thus reducing reward sparsity and the risk of mode collapse.
Finally, some new works attempt to improve the text generation quality
by applying guidance functions to the discriminator’s signals. Essentially, the
idea is to provide more complex feedback and, consequently, a more feasible
reward signal from the discriminator to the generator, leading to better and
more diverse text. Yang et al. [58] introduced the Feature-Guiding Generative
Adversarial Network (FGGAN), which solves the insuﬃcient feedback guidance
from the discriminator through a feature guidance module. The module is a
CNN that considers both generated and real data and performs a series of
convolutional operations to extract a high-order feature vector and provide such
a vector in the form of a reward signal. Additionally, the generated tokens pass
through semantic rules to remove illogical tokens and improve the generated
text’s quality.
At the same time, the TextGAIL [59] attempts to improve the discriminator’s
guidance by combining large-scale pre-trained language models, i.e., RoBERTa
and GPT-2, with recent advancements in Reinforcement Learning, such as Gen-
erative Information Learning (GAIL) and proximal policy optimization (PPO).
The TextGAIL architecture extends the traditional adversarial learning with
GAIL and introduces an imitation replay method to stabilize the training, i.e.,
vocabulary sizes are often large and hampers the GAIL stability. Additionally,
28


---

ground truth sequences are ﬁlled in when training the generator, occasionally
forcing constant rewards and stabilizing the generator’s convergence. Their dis-
criminator uses a pre-trained RoBERTa model as the ﬁnal classiﬁer and uses a
contrastive-based approach that estimates the relative reality between generated
and real sequences, i.e., the discriminator estimates how much a real sentence is
more realistic than a generated sentence. As the discriminator is not stationary
during adversarial learning, the generator suﬀers from high variance gradients
and needs a type of policy optimization to stabilize its convergence, such as the
PPO.
4.3. Text Generation using GANs and Modiﬁed Training Objectives
An alternative to continuous distributions and Reinforcement Learning is
to propose new training objectives, hence withdrawing the necessity of dif-
ferentiable Softmax-like, policy reward functions, and pre-training pipelines.
The ﬁrst work that attempted to introduce such a novel was Che et al. [13],
which presented the Maximum-Likelihood Augmented Generative Adversarial
Network (MaliGAN). Essentially, they introduced a novel objective based on
the normalized maximum likelihood and importance sampling, which resem-
bles an MLE-like objective and brings more stability to the training procedure.
Additionally, one can observe that their variance reduction techniques assisted
create discriminators capable of detecting whether a generator has learned too
much noise.
A diﬀerent architecture that proposes variance reduction techniques and
aims at stabilizing the training procedure is the Improved Wasserstein Gener-
ative Adversarial Network (IWGAN) [50], which uses a gradient penalty tech-
nique instead of the standard weight clipping. Wasserstein networks commonly
use weight clipping to stabilize their training, yet in a hard-optimization task,
such a technique may not converge under a speciﬁc clipped value. In contrast,
a gradient penalization is an alternative method to enforce the Lipschitz con-
straint by introducing a penalization factor to the critic’s (discriminator) loss
function. Unfortunately, there were not enough baselines to compare and attest
29


---

whether IWGAN would scale with larger language models.
The literature also started to employ curriculum learning to mitigate the
variance noise, where the algorithm slowly teaches the model how to generate
increasing and variable-length sequences. Such a model denoted as AltGAN [51]
uses a continuous relaxation mechanism, where the softmax outputs are mul-
tiplied with their respective embeddings to provide a diﬀerentiable generator.
Their experimental results attested that their model could learn from scratch
without resorting to any pre-training, being the ﬁrst model to accomplish such
a fact.
Another alternative approach to modify the training objective is by encoding
sentences in latent feature distributions similar to AutoEncoders. The ﬁrst work
in such a category has been proposed by Zhang et al. [49], which introduced a
text-based Generative Adversarial Network (TextGAN) that matches the high-
dimensional latent feature distribution of real and fake sentences using a kernel-
ized discrepancy metric known as Reproducing Kernel Hilbert Space (RKHS).
Such a model used a soft-argmax operator [63] as well as several complementary
techniques, such as initialization strategies and discretization approximations, to
alleviate the mode collapse problem. Donahue and Rumshisky [53] extended the
previous work and proposed a latent-space text-based Generative Adversarial
Network (LaTextGAN), which uses an AutoEncoder and low-dimensional latent
spaces. In short, they attempt to remove the dimensionality curse and provide
an encoding-decoding system that can generate low-dimensional latent-based
spaces to discriminate the sequences better. Some plotted t-SNE embeddings
showed that LaTextGAN could adequately model the latent space, while inter-
polated sentences indicated that LaTextGAN could smoothly encode sentences
in the latent space.
Ahamad [56] introduced a Skip-Thought Vector Generative Adversarial Net-
work (STGAN), which uses an encoder-decoder architecture to generate sen-
tence embeddings. The proposed method does not resort to soft-diﬀerentiation
or RL, as it generates text by feeding continuous embedded samples. Addi-
tionally, it did not have a speciﬁc training objective, which allowed the au-
30


---

thors to compare and benchmark several training algorithms, such as mini-
batch discrimination, gradient penalty, WGAN, and WGAN-GP. Following the
STGAN proposal, the Text Knowledge Distillation Generative Adversarial Net-
work (TextKD-GAN) [55] also aimed at producing continuous text representa-
tion to replace the traditional one-hot encodings. Instead of only producing em-
beddings with AutoEncoders, the TextKD-GAN resorted to a teacher-student
model, feeding the data through an AutoEncoder and further reconstructing it.
Such an approach provides a more challenging problem to the discriminator and
increases the generator’s ability to fool the discriminator.
Alternatively, the literature suggested using distance-based functions instead
of encoder-decoder architectures to provide diﬀerentiable and straightforward
objectives. In such a context, the Feature Mover Generative Adversarial Net-
work (FM-GAN) [52] matches the latent feature distributions of real and fake
sentences using Feature-Mover’s Distance (FMD), leading to highly discrimina-
tive critics and RL-free approaches. The FMD is based on a variation of the
Earth-Mover’s Distance (EMD), which can be solved by the Inexact Proximal
algorithm and further be applied to model discrete data objectives. This ar-
chitecture could produce good sentences but still suﬀered from mode collapse
(low diversity), while the compared baselines produced high diversity yet low-
quality sentences.
In such a context, Li et al. [54] presented an alternative
distance-based architecture, the Jensen-Shannon Divergence Generative Adver-
sarial Network (JSD-GAN). Such a model optimizes the Jensen-Shannon Diver-
gence between the generator’s distribution and the empirical distribution over
the training data, i.e., an alternative to the min-max optimization, which uses a
closed-form solution for the discriminator. Although their architecture provides
an RL-free algorithm, they could only apply it to explicit representations, thus
hindering the number of beneﬁted tasks.
In contrast, some authors found out that using closed-form solutions directly
optimizes the training objectives. For instance, Montahaei et al. [57] introduced
the Discrete Generative Self-Adversarial Network (DGSAN), which uses an op-
timized closed-form solution to ﬁnd an optimal discriminator. Essentially, the
31


---

DGSAN combines both generator and discriminator powers in a single network,
where the information is encoded into a new objective that creates a relationship
between the current generator, the new generator, and the optimal discriminator
between them. In short, the proposed method takes advantage of not having to
calculate gradients, allowing for a direct sampling over an explicit distribution.
5. Conclusions and Future Insights
Throughout the last years, increasing demand for understanding and au-
tomating human communication fostered Natural Language Processing research.
Machine Learning and abundant computational power helped achieve several
hallmarks in a wide range of NLP-based tasks, thus becoming viable alterna-
tives for modeling human-machine interactions.
Nevertheless, such systems still struggle when dealing with adversarial or
unknown data, i.e., data that has been slightly modiﬁed or not present in the
original one. On the other hand, one can perceive that such a problem encour-
ages researchers to ﬁnd feasible alternatives, such as Adversarial Learning. In
essence, Adversarial Learning attempts to overcome the problem of adversarial
data by introducing noisy examples to an architecture’s learning process, aiding
in its robustness and performance. Moreover, since the advent of Generative
Adversarial Networks, it is now possible to learn the data’s distribution and
generate artiﬁcial data that resembles the original one.
This article presented a survey on the most recent studies concerning text
generation using Generative Adversarial Networks. This paper’s most signiﬁcant
contribution is to critically analyze and provide a unique source of recent GAN-
based text generation research, mostly ranging from 2016 to 2020. Additionally,
Table 1 presents an overview of the considered works, easing the reader’s needs
when looking for particular researches.
We have observed that GAN-based text generation works are brand new
(between 2016 and 2020); hence they still struggle with a lack of researches and
adequately deﬁned pipelines. GAN-based text generation’s primary challenges
32


---

are that GANs were not designed to work with discrete data, needing additional
tricks to subdue such a problem. Such data do not provide diﬀerentiable out-
puts, which inhibits gradients from being appropriately calculated and updated.
Therefore, most works attempt to override such a problem by employing modi-
ﬁed training objectives, Reinforcement Learning, or continuous-based outputs,
such as Soft-Argmax or Gumbel-Softmax distributions.
Another barrier regards the intrinsic features of a language, i.e., grammar,
syntax, and semantic properties.
To provide a feasible text generation, the
model needs to learn how characters and words connect between themselves,
often accomplished by sorts of memories and contexts (prior knowledge). We
believe that such problems can be dealt with in a more robust pre-learning step,
in which pre-trained embedding models guide networks instead of MLE, such
as BERT [64], ELECTRA [65], and GPT-2 [66], among others.
The advent of Transformer-based architectures, which provides substantial
methods that can generate plausible “natural” language, initially diverted GAN-
based systems’ attention; however, their outstanding performance might beneﬁt
GANs when applied as pre-training approaches or even as part of their architec-
tures. With that in mind, it seems that there are loads of blank spots that still
need to be appropriately addressed by the research community regarding GAN-
based text generation, whereas Transformer-based GANs look like promising
approaches to be conducted in 2021.
Acknowledgments
The authors are grateful to S˜ao Paulo Research Foundation (FAPESP)
grants #2013/07375-0, #2014/12236-1, #2019/07665-4, #2019/02205-5, and
#2020/12101-0, and to the Brazilian National Council for Research and Devel-
opment (CNPq) #307066/2017-7 and #427968/2018-6.
33


---

References
[1] Z. Zhang, Y. Zhang, M. Xu, L. Zhang, Y. Yang, S. Yan, A survey on concept
factorization: From shallow to deep representation learning, Information
Processing & Management 58 (3) (2021) 102534.
[2] Z. Zhang, Z. Tang, Y. Wang, Z. Zhang, C. Zhan, Z. Zha, M. Wang, Dense
residual network: Enhancing global dense feature ﬂow for character recog-
nition, Neural Networks 139 (2021) 77–85.
[3] T. Mikolov, M. Karaﬁ´at, L. Burget, J. ˇCernock`y, S. Khudanpur, Recurrent
neural network based language model, in: 11th Annual Conference of the
International Speech Communication Association, 2010.
[4] J. L. Elman, Finding structure in time, Cognitive science 14 (2) (1990)
179–211.
[5] B. Biggio, F. Roli, Wild patterns: Ten years after the rise of adversarial
machine learning, Pattern Recognition 84 (1) (2018) 317–331.
[6] I. Goodfellow, J. Pouget-Abadie, M. Mirza, B. Xu, D. Warde-Farley,
S. Ozair, A. Courville, Y. Bengio, Generative adversarial nets, in: Ad-
vances in Neural Information Processing Systems, 2014, pp. 2672–2680.
[7] X. Hu, P. Ma, Z. Mai, S. Peng, Z. Yang, L. Wang, Face hallucination from
low quality images using deﬁnition-scalable inference, Pattern Recognition
94 (1) (2019) 110–121.
[8] D. Li, C. Du, H. He, Semi-supervised cross-modal image generation
with generative adversarial networks, Pattern Recognition 100 (1) (2020)
107085.
[9] L. Liu, H. Zhang, X. Xu, Z. Zhang, S. Yan, Collocating clothes with gen-
erative adversarial networks cosupervised by categories and attributes: A
multidiscriminator framework, IEEE Transactions on Neural Networks and
Learning Systems 31 (9) (2020) 3540–3554.
34


---

[10] R. D. Hjelm, A. P. Jacob, T. Che, A. Trischler, K. Cho, Y. Bengio,
Boundary-seeking generative adversarial networks, in: 6th International
Conference on Learning Representations, 2018.
[11] E. Jang, S. Gu, B. Poole, Categorical reparameterization with gumbel-
softmax, in: 5th International Conference on Learning Representations,
ICLR 2017, Toulon, France, April 24-26, 2017, Conference Track Proceed-
ings, 2017.
[12] R. S. Sutton, A. G. Barto, et al., Introduction to reinforcement learning,
Vol. 135, MIT Press Cambridge, 1998.
[13] T. Che, Y. Li, R. Zhang, R. D. Hjelm, W. Li, Y. Song, Y. Bengio,
Maximum-likelihood augmented discrete generative adversarial networks
(2017). arXiv:1702.07983.
[14] A. Gatt, E. Krahmer, Survey of the state of the art in natural language
generation: Core tasks, applications and evaluation, Journal of Artiﬁcial
Intelligence Research 61 (2018) 65–170.
[15] S. Lu, Y. Zhu, W. Zhang, J. Wang, Y. Yu, Neural text generation: Past,
present and beyond (2018). arXiv:1803.07133.
[16] W. Zhang, Q. Sheng, A. Alhazmi, C. Li, Adversarial attacks on deep-
learning models in natural language processing: A survey, ACM Transac-
tions on Intelligent Systems and Technology 11 (3) (2020) 1–41.
[17] Y. Goldberg, A primer on neural network models for natural language
processing, Journal of Artiﬁcial Intelligence Research 57 (1) (2016) 345–
420.
[18] C. Szegedy, W. Zaremba, I. Sutskever, J. Bruna, D. Erhan, I. Goodfel-
low, R. Fergus, Intriguing properties of neural networks, in: International
Conference on Learning Representations, 2014.
35


---

[19] R. J. Williams, Simple statistical gradient-following algorithms for connec-
tionist reinforcement learning, Machine learning 8 (3-4) (1992) 229–256.
[20] J. Ni, J. Li, J. McAuley, Justifying recommendations using distantly-
labeled reviews and ﬁne-grained aspects, in: 9th International Joint Con-
ference on Natural Language Processing, 2019, pp. 188–197.
[21] X. Zhang, M. Lapata, Chinese poetry generation with recurrent neural
networks, in: Conference on Empirical Methods in Natural Language Pro-
cessing, 2014, pp. 670–680.
[22] X. Chen, H. Fang, T.-Y. Lin, R. Vedantam, S. Gupta, P. Dollar, C. L.
Zitnick, Microsoft coco captions: Data collection and evaluation server
(2015). arXiv:1504.00325.
[23] B. Ondrej, R. Chatterjee, F. Christian, G. Yvette, H. Barry, H. Matthias,
K. Philipp, L. Qun, L. Varvara, M. Christof, et al., Findings of the 2017
conference on machine translation (wmt17), in: 2nd Conference on Machine
Translation, 2017, pp. 169–214.
[24] K. Papineni, S. Roukos, T. Ward, W.-J. Zhu, Bleu: a method for automatic
evaluation of machine translation, in: 40th Annual Meeting on Association
for Computational Linguistics, 2002, pp. 311–318.
[25] I. Myung, Tutorial on maximum likelihood estimation, Journal of Mathe-
matical Psychology 47 (1) (2003) 90–100.
[26] P. Brown, S. D. Pietra, V. D. Pietra, J. Lai, R. Mercer, An estimate of an
upper bound for the entropy of english, Computational Linguistics 18 (1)
(1992) 31–40.
[27] M. J. Kusner, J. M. Hern´andez-Lobato, Gans for sequences of discrete
elements with the gumbel-softmax distribution (2016). arXiv:1611.04051.
[28] W. Nie, N. Narodytska, A. Patel, Relgan: Relational generative adversarial
networks for text generation, in: 7th International Conference on Learning
Representations, 2019.
36


---

[29] H. Yin, D. Li, X. Li, P. Li, Meta-cotgan: A meta cooperative training
paradigm for improving adversarial text generation, in: Proceedings of the
AAAI Conference on Artiﬁcial Intelligence, 2020, pp. 9466–9473.
[30] L. Yu, W. Zhang, J. Wang, Y. Yu, Seqgan: Sequence generative adver-
sarial nets with policy gradient, in: 31st AAAI Conference on Artiﬁcial
Intelligence, 2017.
[31] K. Lin, D. Li, X. He, Z. Zhang, M.-T. Sun, Adversarial ranking for lan-
guage generation, in: 31st International Conference on Neural Information
Processing Systems, 2017, p. 3158–3168.
[32] H. Wang, Z. Qin, T. Wan, Text generation based on generative adversarial
nets with latent variables, in: Advances in Knowledge Discovery and Data
Mining, Springer International Publishing, Cham, 2018, pp. 92–103.
[33] G. L. Guimaraes, B. Sanchez-Lengeling, C. Outeiral, P. L. C. Farias,
A. Aspuru-Guzik, Objective-reinforced generative adversarial networks (or-
gan) for sequence generation models (2018). arXiv:1705.10843.
[34] J. Guo, S. Lu, H. Cai, W. Zhang, Y. Yu, J. Wang, Long text generation via
adversarial training with leaked information, in: 32nd AAAI Conference
on Artiﬁcial Intelligence, 2018.
[35] W. Fedus, I. J. Goodfellow, A. M. Dai, Maskgan: Better text generation
via ﬁlling in the
, in: 6th International Conference on Learning Rep-
resentations, 2018.
[36] Y. Li, Q. Pan, S. Wang, T. Yang, E. Cambria, A generative model for
category text generation, Information Sciences 450 (1) (2018) 301–315.
[37] A.
Balagopalan,
S.
Gorti,
M.
Ravaut,
R.
Saqur,
Regan:
Re[lax—bar—inforce]
based
sequence
generation using
gans
(2018).
arXiv:1805.02788.
37


---

[38] Z. Shi, X. Chen, X. Qiu, X. Huang, Toward diverse text generation with
inverse reinforcement learning, in: 27th International Joint Conference on
Artiﬁcial Intelligence, 2018, p. 4361–4367.
[39] J. Xu, X. Ren, J. Lin, X. Sun, Diversity-promoting gan: A cross-entropy
based generative adversarial network for diversiﬁed text generation, in:
Conference on Empirical Methods in Natural Language Processing, 2018,
pp. 3940–3949.
[40] J. Chen, Y. Wu, C. Jia, H. Zheng, G. Huang, Customizable text genera-
tion via conditional text generative adversarial network, Neurocomputing
416 (1) (2020) 125–135.
[41] K. Wang, X. Wan, Automatic generation of sentimental texts via mixture
adversarial networks, Artiﬁcial Intelligence 275 (1) (2019) 540–558.
[42] R. Zhang, Z. Wang, K. Yin, Z. Huang, Emotional text generation based on
cross-domain sentiment transfer, IEEE Access 7 (2019) 100081–100089.
[43] C. Zhang, C. Xiong, L. Wang, A research on generative adversarial net-
works applied to text generation, in: 14th International Conference on
Computer Science Education (ICCSE), 2019, pp. 913–917.
[44] D. Liu, J. Fu, Q. Qu, J. Lv, Bfgan: Backward and forward generative adver-
sarial networks for lexically constrained sentence generation, IEEE/ACM
Transactions on Audio, Speech, and Language Processing 27 (12) (2019)
2350–2361.
[45] Y. Sun, C. Chen, T. Xia, X. Zhao, Qugan: Quasi generative adversarial
network for tibetan question answering corpus generation, IEEE Access 7
(2019) 116247–116255.
[46] G. Rizzo, T. H. M. Van, Adversarial text generation with context adapted
global knowledge and a self-attentive discriminator, Information Processing
& Management 57 (6) (2020) 102217.
38


---

[47] Y. Wu, J. Wang, Text generation service model based on truth-guided
seqgan, IEEE Access 8 (2020) 11880–11886.
[48] W. Zhou, T. Ge, K. Xu, F. Wei, M. Zhou, Self-adversarial learning with
comparative discrimination for text generation (2020). arXiv:2001.11691.
[49] Y. Zhang, Z. Gan, K. Fan, Z. Chen, R. Henao, D. Shen, L. Carin, Adversar-
ial feature matching for text generation, in: 34th International Conference
on Machine Learning, 2017, pp. 4006–4015.
[50] I. Gulrajani, F. Ahmed, M. Arjovsky, V. Dumoulin, A. C. Courville, Im-
proved training of wasserstein gans, in: Advances in Neural Information
Processing Systems, 2017, pp. 5767–5777.
[51] O. Press, A. Bar, B. Bogin, J. Berant, L. Wolf, Language generation
with recurrent generative adversarial networks without pre-training (2017).
arXiv:1706.01399.
[52] L. Chen, S. Dai, C. Tao, H. Zhang, Z. Gan, D. Shen, Y. Zhang, G. Wang,
R. Zhang, L. Carin, Adversarial text generation via feature-mover’s dis-
tance, in: Advances in Neural Information Processing Systems, 2018, pp.
4666–4677.
[53] D. Donahue, A. Rumshisky, Adversarial text generation without reinforce-
ment learning (2018). arXiv:1810.06640.
[54] Z. Li, T. Xia, X. Lou, K. Xu, S. Wang, J. Xiao, Adversarial discrete se-
quence generation without explicit neural networks as discriminators, in:
22nd International Conference on Artiﬁcial Intelligence and Statistics, 2019,
pp. 3089–3098.
[55] M. Haidar, M. Rezagholizadeh, A. D. Omri, A. Rashid, Latent code and
text-based generative adversarial networks for soft-text generation, in: 2019
Conference of the North American Chapter of the Association for Compu-
tational Linguistics, 2019, pp. 2248–2258.
39


---

[56] A. Ahamad, Generating text through adversarial training using skip-
thought vectors, in: Conference of the North American Chapter of the
Association for Computational Linguistics, 2019, pp. 53–60.
[57] E. Montahaei, D. Alihosseini, M. Soleymani Baghshah, Dgsan: Discrete
generative self-adversarial network, Neurocomputing 448 (2021) 364–379.
[58] Y. Yang, X. Dan, X. Qiu, Z. Gao, Fggan: Feature-guiding generative adver-
sarial networks for text generation, IEEE Access 8 (2020) 105217–105225.
[59] Q. Wu, L. Li, Z. Yu, Textgail: Generative adversarial imitation learning
for text generatio, in: Proceedings of the AAAI Conference on Artiﬁcial
Intelligence, AAAI Press, 2021.
[60] B. D. Ziebart, A. L. Maas, J. A. Bagnell, A. K. Dey, Maximum entropy
inverse reinforcement learning., in: 23rd National Conference on Artiﬁcial
Intelligence, Vol. 3, 2008, pp. 1433–1438.
[61] O. Nachum, M. Norouzi, K. Xu, D. Schuurmans, Bridging the gap between
value and policy based reinforcement learning, in: Proceedings of the 31st
International Conference on Neural Information Processing Systems, Red
Hook, NY, USA, 2017, p. 2772–2782.
[62] I. Sutskever, O. Vinyals, Q. V. Le, Sequence to sequence learning with
neural networks, in: Advances in Neural Information Processing Systems,
2014, pp. 3104–3112.
[63] Y. Zhang, Z. Gan, L. Carin, Generating text via adversarial training, in:
NIPS Workshop on Adversarial Training, Vol. 21, 2016.
[64] J. Devlin, M.-W. Chang, K. Lee, K. Toutanova, BERT: Pre-training of deep
bidirectional transformers for language understanding, in: Proceedings of
the 2019 Conference of the North American Chapter of the Association for
Computational Linguistics, Minneapolis, Minnesota, 2019, pp. 4171–4186.
40


---

[65] K. Clark, M.-T. Luong, Q. V. Le, C. D. Manning, Electra: Pre-training text
encoders as discriminators rather than generators, in: 8th International
Conference on Learning Representations, 2020.
[66] A. Radford, J. Wu, R. Child, D. Luan, D. Amodei, I. Sutskever, Language
models are unsupervised multitask learners, OpenAI Blog 1 (8) (2019) 1–9.
41
