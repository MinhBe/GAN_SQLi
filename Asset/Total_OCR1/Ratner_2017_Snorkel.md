Snorkel: Rapid Training Data Creation
with Weak Supervision
Alexander Ratner
Stephen H. Bach
Henry Ehrenberg
Jason Fries
Sen Wu
Christopher R´e
Stanford University
Stanford, CA, USA
{ajratner, bach, henryre, jfries, senwu, chrismre}@cs.stanford.edu
ABSTRACT
Labeling training data is increasingly the largest bottleneck
in deploying machine learning systems. We present Snorkel,
a ﬁrst-of-its-kind system that enables users to train state-
of-the-art models without hand labeling any training data.
Instead, users write labeling functions that express arbi-
trary heuristics, which can have unknown accuracies and
correlations.
Snorkel denoises their outputs without ac-
cess to ground truth by incorporating the ﬁrst end-to-end
implementation of our recently proposed machine learning
paradigm, data programming. We present a ﬂexible inter-
face layer for writing labeling functions based on our ex-
perience over the past year collaborating with companies,
agencies, and research labs. In a user study, subject mat-
ter experts build models 2.8× faster and increase predictive
performance an average 45.5% versus seven hours of hand la-
beling. We study the modeling tradeoﬀs in this new setting
and propose an optimizer for automating tradeoﬀdecisions
that gives up to 1.8× speedup per pipeline execution. In
two collaborations, with the U.S. Department of Veterans
Aﬀairs and the U.S. Food and Drug Administration, and
on four open-source text and image data sets representa-
tive of other deployments, Snorkel provides 132% average
improvements to predictive performance over prior heuris-
tic approaches and comes within an average 3.60% of the
predictive performance of large hand-curated training sets.
PVLDB Reference Format:
A. Ratner, S. H. Bach, H. Ehrenberg, J. Fries, S. Wu, C. R´e.
Snorkel: Rapid Training Data Creation with Weak Supervision.
PVLDB, 11 (3): x-yyyy, 2017.
DOI: 10.14778/3157794.3157797
1.
INTRODUCTION
In the last several years, there has been an explosion of
interest in machine-learning-based systems across industry,
government, and academia, with an estimated spend this
year of $12.5 billion [1].
A central driver has been the
Permission to make digital or hard copies of all or part of this work for
personal or classroom use is granted without fee provided that copies are
not made or distributed for proﬁt or commercial advantage and that copies
bear this notice and the full citation on the ﬁrst page. To copy otherwise, to
republish, to post on servers or to redistribute to lists, requires prior speciﬁc
permission and/or a fee. Articles from this volume were invited to present
their results at The 44th International Conference on Very Large Data Bases,
August 2018, Rio de Janeiro, Brazil.
Proceedings of the VLDB Endowment, Vol. 11, No. 3
Copyright 2017 VLDB Endowment 2150-8097/17/11... $ 10.00.
DOI: 10.14778/3157794.3157797
!"#$%&#&'( '$)$
#$%&#(*+!,-&(.
#$%&#(*+!,-&(/
.001(234526
.1(234526
$778937:;(<0=
!
$778937:;(>0=
Figure 1:
In Example 1.1, training data is labeled
by sources of diﬀering accuracy and coverage. Two
key challenges arise in using this weak supervision
eﬀectively. First, we need a way to estimate the un-
known source accuracies to resolve disagreements.
Second, we need to pass on this critical lineage in-
formation to the end model being trained.
advent of deep learning techniques, which can learn task-
speciﬁc representations of input data, obviating what used
to be the most time-consuming development task: feature
engineering. These learned representations are particularly
eﬀective for tasks like natural language processing and image
analysis, which have high-dimensional, high-variance input
that is impossible to fully capture with simple rules or hand-
engineered features [14, 17]. However, deep learning has a
major upfront cost: these methods need massive training
sets of labeled examples to learn from—often tens of thou-
sands to millions to reach peak predictive performance [47].
Such training sets are enormously expensive to create, es-
pecially when domain expertise is required. For example,
reading scientiﬁc papers, analyzing intelligence data, and in-
terpreting medical images all require labeling by trained sub-
ject matter experts (SMEs). Moreover, we observe from our
engagements with collaborators like research labs and ma-
jor technology companies that modeling goals such as class
deﬁnitions or granularity change as projects progress, neces-
sitating re-labeling. Some big companies are able to absorb
this cost, hiring large teams to label training data [12,16,31].
However, the bulk of practitioners are increasingly turn-
ing to weak supervision: cheaper sources of labels that are
noisier or heuristic. The most popular form is distant su-
pervision, in which the records of an external knowledge
base are heuristically aligned with data points to produce
noisy labels [4,7,32]. Other forms include crowdsourced la-
bels [37, 50], rules and heuristics for labeling data [39, 52],
and others [29, 30, 30, 46, 51]. While these sources are inex-
pensive, they often have limited accuracy and coverage.
269
269-282


---

Ideally, we would combine the labels from many weak su-
pervision sources to increase the accuracy and coverage of
our training set. However, two key challenges arise in do-
ing so eﬀectively.
First, sources will overlap and conﬂict,
and to resolve their conﬂicts we need to estimate their ac-
curacies and correlation structure, without access to ground
truth. Second, we need to pass on critical lineage informa-
tion about label quality to the end model being trained.
Example 1.1. In Figure 1, we obtain labels from a high
accuracy, low coverage Source 1, and from a low accuracy,
high coverage Source 2, which overlap and disagree (split-
color points).
If we take an unweighted majority vote to
resolve conﬂicts, we end up with null (tie-vote) labels.
If
we could correctly estimate the source accuracies, we would
resolve conﬂicts in the direction of Source 1.
We would still need to pass this information on to the end
model being trained. Suppose that we took labels from Source
1 where available, and otherwise took labels from Source 2.
Then, the expected training set accuracy would be 60.3%—
only marginally better than the weaker source. Instead we
should represent training label lineage in end model training,
weighting labels generated by high-accuracy sources more.
In recent work, we developed data programming as a
paradigm for addressing both of these challenges by model-
ing multiple label sources without access to ground truth,
and generating probabilistic training labels representing the
lineage of the individual labels. We prove that, surprisingly,
we can recover source accuracy and correlation structure
without hand-labeled training data [5, 38]. However, there
are many practical aspects of implementing and applying
this abstraction that have not been previously considered.
We present Snorkel, the ﬁrst end-to-end system for com-
bining weak supervision sources to rapidly create training
data. We built Snorkel as a prototype to study how people
could use data programming, a fundamentally new approach
to building machine learning applications. Through weekly
hackathons and oﬃce hours held at Stanford University over
the past year, we have interacted with a growing user com-
munity around Snorkel’s open source implementation.1 We
have observed SMEs in industry, science, and government
deploying Snorkel for knowledge base construction, image
analysis, bioinformatics, fraud detection, and more. From
this experience, we have distilled three principles that have
shaped Snorkel’s design:
1. Bring All Sources to Bear: The system should en-
able users to opportunistically use labels from all available
weak supervision sources.
2. Training Data as the Interface to ML: The system
should model label sources to produce a single, proba-
bilistic label for each data point and train any of a wide
range of classiﬁers to generalize beyond those sources.
3. Supervision as Interactive Programming: The sys-
tem should provide rapid results in response to user su-
pervision. We envision weak supervision as the REPL-like
interface for machine learning.
Our work makes the following technical contributions:
A Flexible Interface for Sources: We observe that the
heterogeneity of weak supervision strategies is a stumbling
block for developers.
Diﬀerent types of weak supervision
1http://snorkel.stanford.edu
operate on diﬀerent scopes of the input data. For example,
distant supervision has to be mapped programmatically to
speciﬁc spans of text. Crowd workers and weak classiﬁers
often operate over entire documents or images.
Heuristic
rules are open ended; they can leverage information from
multiple contexts simultaneously, such as combining infor-
mation from a document’s title, named entities in the text,
and knowledge bases. This heterogeneity was cumbersome
enough to completely block users of early versions of Snorkel.
To address this challenge, we built an interface layer
around the abstract concept of a labeling function (LF). We
developed a ﬂexible language for expressing weak supervi-
sion strategies and supporting data structures. We observed
accelerated user productivity with these tools, which we val-
idated in a user study where SMEs build models 2.8× faster
and increase predictive performance an average 45.5% ver-
sus seven hours of hand labeling.
Tradeoﬀs in Modeling of Sources: Snorkel learns the
accuracies of weak supervision sources without access to
ground truth using a generative model [38]. Furthermore,
it also learns correlations and other statistical dependencies
among sources, correcting for dependencies in labeling func-
tions that skew the estimated accuracies [5]. This paradigm
gives rise to previously unexplored tradeoﬀspaces between
predictive performance and speed. The natural ﬁrst ques-
tion is: when does modeling the accuracies of sources im-
prove predictive performance? Further, how many depen-
dencies, such as correlations, are worth modeling?
We study the tradeoﬀs between predictive performance
and training time in generative models for weak supervision.
While modeling source accuracies and correlations will not
hurt predictive performance, we present a theoretical anal-
ysis of when a simple majority vote will work just as well.
Based on our conclusions, we introduce an optimizer for de-
ciding when to model accuracies of labeling functions, and
when learning can be skipped in favor of a simple majority
vote.
Further, our optimizer automatically decides which
correlations to model among labeling functions. This opti-
mizer correctly predicts the advantage of generative mod-
eling over majority vote to within 2.16 accuracy points on
average on our evaluation tasks, and accelerates pipeline ex-
ecutions by up to 1.8×. It also enables us to gain 60%–70%
of the beneﬁt of correlation learning while saving up to 61%
of training time (34 minutes per execution).
First End-to-End System for Data Programming:
Snorkel is the ﬁrst system to implement our recent work on
data programming [5,38]. Previous ML systems that we and
others developed [52] required extensive feature engineering
and model speciﬁcation, leading to confusion about where
to inject relevant domain knowledge. While programming
weak supervision seems superﬁcially similar to feature engi-
neering, we observe that users approach the two processes
very diﬀerently. Our vision—weak supervision as the sole
port of interaction for machine learning—implies radically
diﬀerent workﬂows, requiring a proof of concept.
Snorkel demonstrates that this paradigm enables users
to develop high-quality models for a wide range of tasks.
We report on two deployments of Snorkel, in collaboration
with the U.S. Department of Veterans Aﬀairs and Stanford
Hospital and Clinics, and the U.S. Food and Drug Admin-
istration, where Snorkel improves over heuristic baselines
by an average 110%. We also report results on four open-
270


---

!"#$%&%'()!*+,$"&%'()!-*+.&,)
/0'()!#112#3#/&%'()4
!"#$%&'()
*+,
-'##$%&,).)
/01#02&'%0$,
324'0&)
5$6%0,#01,
!56&7*"#-%)08)/9:&);)
%60$-,)<&)6#27-&%%4'
=$<%&/);
=$<%&/)>
=$<%&/)5
!"#$%&'(")*+&+,-%&,')."&
Document
Sentence
Span
Entity
.,-/"0/%1+")#).12
3#4"3+-5%6'-./+,-%+-/")6#."
Ontology(ctd, [A, B, -C])
Pattern(“{{0}}causes{{1}}”)
CustomFn(x,y : heuristic(x,y))
!
3#4"3%
7#/)+0
7,8"3+-5%
,(/+7+9")
!"
!#
!$
%
5"-")#/+*"%
7,8"3
(),4#4+3+&/+.%
/)#+-+-5%8#/#
%&
8+&.)+7+-#/+*"%
7,8"3
7$),#6/8)')9'#0$&#):;2)<$1'4$)
:;<=>?@ABC?D '=#$%)9'%$&#$%'()E<CFBG?;E
'/40&0,#%'#02&)=2%)@>BBDA<E@G?<H
7$),#6/8)')9'#0$&#):;2)<$1'4$)
:;<=>?@ABC?D '=#$%)9'%$&#$%'()E<CFBG?;E
'/40&0,#%'#02&)=2%)@>BBDA<E@G?<H
'-3#4"3"8%8#/#
7$),#6/8)')9'#0$&#):;2)<$1'4$)
:;<=>?@ABC?D '=#$%)9'%$&#$%'()E<CFBG?;E
'/40&0,#%'#02&)=2%)@>BBDA<E@G?<H
&-,)$"3
Figure 2: An overview of the Snorkel system.
(1) SME users write labeling functions (LFs) that express
weak supervision sources like distant supervision, patterns, and heuristics. (2) Snorkel applies the LFs over
unlabeled data and learns a generative model to combine the LFs’ outputs into probabilistic labels.
(3)
Snorkel uses these labels to train a discriminative classiﬁcation model, such as a deep neural network.
source datasets that are representative of other Snorkel de-
ployments, including bioinformatics, medical image analysis,
and crowdsourcing; on which Snorkel beats heuristics by an
average 153% and comes within an average 3.60% of the
predictive performance of large hand-curated training sets.
2.
SNORKEL ARCHITECTURE
Snorkel’s workﬂow is designed around data programming
[5,38], a fundamentally new paradigm for training machine
learning models using weak supervision, and proceeds in
three main stages (Figure 2):
1. Writing
Labeling
Functions:
Rather
than
hand-labeling training data, users of Snorkel write label-
ing functions, which allow them to express various weak
supervision sources such as patterns, heuristics, external
knowledge bases, and more.
This was the component
most informed by early interactions (and mistakes) with
users over the last year of deployment, and we present a
ﬂexible interface and supporting data model.
2. Modeling
Accuracies
and
Correlations:
Next,
Snorkel automatically learns a generative model over the
labeling functions, which allows it to estimate their accu-
racies and correlations. This step uses no ground-truth
data, learning instead from the agreements and disagree-
ments of the labeling functions. We observe that this step
improves end predictive performance 5.81% over Snorkel
with unweighted label combination, and anecdotally that
it streamlines the user development experience by provid-
ing actionable feedback about labeling function quality.
3. Training a Discriminative Model:
The output of
Snorkel is a set of probabilistic labels that can be used to
train a wide variety of state-of-the-art machine learning
models, such as popular deep learning models. While the
generative model is essentially a re-weighted combination
of the user-provided labeling functions—which tend to be
precise but low-coverage—modern discriminative models
can retain this precision while learning to generalize be-
yond the labeling functions, increasing coverage and ro-
bustness on unseen data.
Next we set up the problem Snorkel addresses and de-
scribe its main components and design decisions.
Setup: Our goal is to learn a parameterized classiﬁcation
model hθ that, given a data point x ∈X, predicts its la-
bel y ∈Y, where the set of possible labels Y is discrete.
For simplicity, we focus on the binary setting Y = {−1, 1},
though we include a multi-class application in our experi-
ments. For example, x might be a medical image, and y
a label indicating normal versus abnormal. In the relation
extraction examples we look at, we often refer to x as a can-
didate. In a traditional supervised learning setup, we would
learn hθ by ﬁtting it to a training set of labeled data points.
However, in our setting, we assume that we only have access
to unlabeled data for training. We do assume access to a
small set of labeled data used during development, called the
development set, and a blind, held-out labeled test set for
evaluation. These sets can be orders of magnitudes smaller
than a training set, making them economical to obtain.
The user of Snorkel aims to generate training labels by
providing a set of labeling functions, which are black-box
functions, λ : X →Y ∪{∅}, that take in a data point
and output a label where we use ∅to denote that the la-
beling functions abstains. Given m unlabeled data points
and n labeling functions, Snorkel applies the labeling func-
tions over the unlabeled data to produce a matrix of label-
ing function outputs Λ ∈(Y ∪{∅})m×n. The goal of the
remaining Snorkel pipeline is to synthesize this label matrix
Λ—which may contain overlapping and conﬂicting labels for
each data point—into a single vector of probabilistic train-
ing labels ˜Y = (˜y1, ..., ˜ym), where ˜yi ∈[0, 1]. These training
labels can then be used to train a discriminative model.
Next, we introduce the running example of a text relation
extraction task as a proxy for many real-world knowledge
base construction and data analysis tasks:
Example 2.1. Consider the task of extracting mentions
of adverse chemical-disease relations from the biomedical lit-
erature (see CDR task, Section 4.1). Given documents with
mentions of chemicals and diseases tagged, we refer to each
co-occuring (chemical, disease) mention pair as a candidate
extraction, which we view as a data point to be classiﬁed as
either true or false. For example, in Figure 2, we would have
two candidates with true labels y1 = True and y2 = False:
x 1
= Causes("magnesium", " quadriplegic ")
x 2
= Causes("magnesium", " preeclampsia ")
271


---

Document
Sentence
Span
Entity
!"#$%&$'()%*+*!(,
Candidate(A,B)
Figure 3:
Labeling functions take as input a
Candidate object, representing a data point to be
classiﬁed. Each Candidate is a tuple of Context ob-
jects, which are part of a hierarchy representing the
local context of the Candidate.
Data Model: A design challenge is managing complex,
unstructured data in a way that enables SMEs to write la-
beling functions over it. In Snorkel, input data is stored in a
context hierarchy. It is made up of context types connected
by parent/child relationships, which are stored in a rela-
tional database and made available via an object-relational
mapping (ORM) layer built with SQLAlchemy.2 Each con-
text type represents a conceptual component of data to be
processed by the system or used when writing labeling func-
tions; for example a document, an image, a paragraph, a sen-
tence, or an embedded table. Candidates—i.e., data points
x—are then deﬁned as tuples of contexts (Figure 3).
Example 2.2. In our running CDR example, the input
documents can be represented in Snorkel as a hierarchy con-
sisting
of
Documents,
each
containing
one
or
more
Sentences, each containing one or more Spans of text. These
Spans may also be tagged with metadata, such as Entity
markers identifying them as chemical or disease mentions
(Figure 3). A candidate is then a tuple of two Spans.
2.1
A Language for Weak Supervision
Snorkel uses the core abstraction of a labeling function
to allow users to specify a wide range of weak supervi-
sion sources such as patterns, heuristics, external knowledge
bases, crowdsourced labels, and more. This higher-level, less
precise input is more eﬃcient to provide (see Section 4.2),
and can be automatically denoised and synthesized, as de-
scribed in subsequent sections.
In this section, we describe our design choices in building
an interface for writing labeling functions, which we envi-
sion as a unifying programming language for weak supervi-
sion. These choices were informed to a large degree by our
interactions—primarily through weekly oﬃce hours—with
Snorkel users in bioinformatics, defense, industry, and other
areas over the past year.3 For example, while we initially
intended to have a more complex structure for labeling func-
tions, with manually speciﬁed types and correlation struc-
ture, we quickly found that simplicity in this respect was
critical to usability (and not empirically detrimental to our
ability to model their outputs). We also quickly discovered
that users wanted either far more expressivity or far less of
it, compared to our ﬁrst library of function templates. We
thus trade oﬀexpressivity and eﬃciency by allowing users to
write labeling functions at two levels of abstraction: custom
Python functions and declarative operators.
2https://www.sqlalchemy.org/
3http://snorkel.stanford.edu#users
Hand-Deﬁned Labeling Functions:
In its most gen-
eral form, a labeling function is just an arbitrary snippet
of code, usually written in Python, which accepts as input
a Candidate object and either outputs a label or abstains.
Often these functions are similar to extract-transform-load
scripts, expressing basic patterns or heuristics, but may use
supporting code or resources and be arbitrarily complex.
Writing labeling functions by hand is supported by the ORM
layer, which maps the context hierarchy and associated meta-
data to an object-oriented syntax, allowing the user to easily
traverse the structure of the input data.
Example 2.3. In our running example, we can write a
labeling function that checks if the word “causes” appears
between the chemical and disease mentions.
If it does, it
outputs True if the chemical mention is ﬁrst and False if
the disease mention is ﬁrst. If “causes” does not appear, it
outputs None, indicating abstention:
def
LF causes (x):
cs , ce = x.chemical. get word range ()
ds , de = x.disease. get word range ()
if ce < ds and "causes" in x.parent.words[ce +1: ds]:
return
True
if de < cs and "causes" in x.parent.words[de +1: cs]:
return
False
return
None
We could also write this with Snorkel’s declarative interface:
LF causes
=
lf search ("{{1}}.∗\ Wcauses\W.∗{{2}}",
reverse args =False)
Declarative Labeling Functions: Snorkel includes a li-
brary of declarative operators that encode the most common
weak supervision function types, based on our experience
with users over the last year.
These functions capture a
range of common forms of weak supervision, for example:
• Pattern-based:
Pattern-based heuristics embody the
motivation of soliciting higher information density input
from SMEs.
For example, pattern-based heuristics en-
compass feature annotations [51] and pattern-bootstrapping
approaches [18,20] (Example 2.3).
• Distant supervision: Distant supervision generates train-
ing labels by heuristically aligning data points with an
external knowledge base, and is one of the most popular
forms of weak supervision [4,22,32].
• Weak classiﬁers: Classiﬁers that are insuﬃcient for our
task—e.g., limited coverage, noisy, biased, and/or trained
on a diﬀerent dataset—can be used as labeling functions.
• Labeling function generators: One higher-level ab-
straction that we can build on top of labeling functions
in Snorkel is labeling function generators, which generate
multiple labeling functions from a single resource, such as
crowdsourced labels and distant supervision from struc-
tured knowledge bases (Example 2.4).
Example 2.4. A challenge in traditional distant supervi-
sion is that diﬀerent subsets of knowledge bases have diﬀer-
ent levels of accuracy and coverage. In our running exam-
ple, we can use the Comparative Toxicogenomics Database
(CTD)4 as distant supervision, separately modeling diﬀerent
subsets of it with separate labeling functions. For example,
4http://ctdbase.org/
272


---

we might write one labeling function to label a candidate
True if it occurs in the “Causes” subset, and another to la-
bel it False if it occurs in the “Treats” subset. We can write
this using a labeling function generator,
LFs CTD
= Ontology(ctd ,
{"Causes": True , "Treats": False})
which creates two labeling functions. In this way, generators
can be connected to large resources and create hundreds of
labeling functions with a line of code.
2.2
Generative Model
The core operation of Snorkel is modeling and integrat-
ing the noisy signals provided by a set of labeling func-
tions. Using the recently proposed approach of data pro-
gramming [5, 38], we model the true class label for a data
point as a latent variable in a probabilistic model. In the
simplest case, we model each labeling function as a noisy
“voter” which is independent—i.e., makes errors that are
uncorrelated with the other labeling functions. This deﬁnes
a generative model of the votes of the labeling functions as
noisy signals about the true label.
We can also model statistical dependencies between the
labeling functions to improve predictive performance. For
example, if two labeling functions express similar heuristics,
we can include this dependency in the model and avoid a
“double counting” problem. We observe that such pairwise
correlations are the most common, so we focus on them in
this paper (though handling higher order dependencies is
straightforward). We use our structure learning method for
generative models [5] to select a set C of labeling function
pairs (j, k) to model as correlated (see Section 3.2).
Now we can construct the full generative model as a factor
graph. We ﬁrst apply all the labeling functions to the unla-
beled data points, resulting in a label matrix Λ, where Λi,j =
λj(xi). We then encode the generative model pw(Λ, Y ) us-
ing three factor types, representing the labeling propensity,
accuracy, and pairwise correlations of labeling functions:
φLab
i,j (Λ, Y ) = 1{Λi,j ̸= ∅}
φAcc
i,j (Λ, Y ) = 1{Λi,j = yi}
φCorr
i,j,k(Λ, Y ) = 1{Λi,j = Λi,k}
(j, k) ∈C
For a given data point xi, we deﬁne the concatenated vector
of these factors for all the labeling functions j = 1, ..., n and
potential correlations C as φi(Λ, Y ), and the corresponding
vector of parameters w ∈R2n+|C|. This deﬁnes our model:
pw(Λ, Y ) = Z−1
w exp
 m
X
i=1
wT φi(Λ, yi)
!
,
where Zw is a normalizing constant. To learn this model
without access to the true labels Y , we minimize the negative
log marginal likelihood given the observed label matrix Λ:
ˆw = arg min
w
−log
X
Y
pw(Λ, Y ) .
We optimize this objective by interleaving stochastic gra-
dient descent steps with Gibbs sampling ones, similar to
contrastive divergence [21]; for more details, see [5,38]. We
use the Numbskull library,5 a Python NUMBA-based Gibbs
sampler.
We then use the predictions, ˜Y = p ˆ
w(Y |Λ), as
probabilistic training labels.
5https://github.com/HazyResearch/numbskull
2.3
Discriminative Model
The end goal in Snorkel is to train a model that gen-
eralizes beyond the information expressed in the labeling
functions. We train a discriminative model hθ on our prob-
abilistic labels ˜Y by minimizing a noise-aware variant of the
loss l(hθ(xi), y), i.e., the expected loss with respect to ˜Y :
ˆθ = arg min
θ
m
X
i=1
Ey∼˜Y [l(hθ(xi), y)] .
A formal analysis shows that as we increase the amount
of unlabeled data, the generalization error of discriminative
models trained with Snorkel will decrease at the same asymp-
totic rate as traditional supervised learning models do with
additional hand-labeled data [38], allowing us to increase
predictive performance by adding more unlabeled data. In-
tuitively, this property holds because as more data is pro-
vided, the discriminative model sees more features that co-
occur with the heuristics encoded in the labeling functions.
Example 2.5. The CDR data contains the sentence,
“Myasthenia gravis presenting as weakness after magnesium
administration.” None of the 33 labeling functions we devel-
oped
vote
on
the
corresponding
Causes(magnesium,
myasthenia gravis) candidate, i.e., they all abstain. How-
ever, a deep neural network trained on probabilistic training
labels from Snorkel correctly identiﬁes it as a true mention.
Snorkel provides connectors for popular machine learning
libraries such as TensorFlow [2], allowing users to exploit
commodity models like deep neural networks that do not
require hand-engineering of features and have robust pre-
dictive performance across a wide range of tasks.
3.
WEAK SUPERVISION TRADEOFFS
We study the fundamental question of when—and at what
level of complexity—we should expect Snorkel’s generative
model to yield the greatest predictive performance gains.
Understanding these performance regimes can help guide
users, and introduces a tradeoﬀspace between predictive
performance and speed. We characterize this space in two
parts: ﬁrst, by analyzing when the generative model can be
approximated by an unweighted majority vote, and second,
by automatically selecting the complexity of the correlation
structure to model. We then introduce a two-stage, rule-
based optimizer to support fast development cycles.
3.1
Modeling Accuracies
The natural ﬁrst question when studying systems for weak
supervision is, “When does modeling the accuracies of
sources improve end-to-end predictive performance?”
We
study that question in this subsection and propose a heuris-
tic to identify settings in which this modeling step is most
beneﬁcial.
3.1.1
Tradeoff Space
We start by considering the label density dΛ of the label
matrix Λ, deﬁned as the mean number of non-abstention
labels per data point. In the low-density setting, sparsity
of labels will mean that there is limited room for even an
optimal weighting of the labeling functions to diverge much
from the majority vote.
Conversely, as the label density
273


---

Figure 4:
A plot of the modeling advantage, i.e.,
the improvement in label accuracy from the gener-
ative model, as a function of the number of labeling
functions (equivalently, the label density) on a syn-
thetic dataset.7
We plot the advantage obtained by
a learned generative model (GM), Aw; by an optimal
model A∗; the upper bound ˜A∗used in our optimizer;
and the low-density bound (Proposition 1).
grows, known theory conﬁrms that the majority vote will
eventually be optimal [27]. It is the middle-density regime
where we expect to most beneﬁt from applying the genera-
tive model. We start by deﬁning a measure of the beneﬁt of
weighting the labeling functions by their true accuracies—in
other words, the predictions of a perfectly estimated gener-
ative model—versus an unweighted majority vote:
Definition 1. (Modeling Advantage) Let the weighted
majority vote of n labeling functions on data point xi be
denoted as fw = Pn
j=1 wjΛi,j, and denote an unweighted
majority vote (MV) as f1 = Pn
j=1 Λi,j. We then deﬁne the
modeling advantage Aw as the improvement in predictive
accuracy of fw over f1 for a dataset:
Aw(Λ, y) = 1
m
m
X
i=1
( {yifw(Λi) > 0 ∧yif1(Λi) ≤0}
−
{yifw(Λi) ≤0 ∧yif1(Λi) > 0})
In other words, Aw is the number of times fw correctly dis-
agrees with f1 on a label, minus the number of times it incor-
rectly disagrees. Furthermore, let the optimal advantage
A∗= Aw∗be the advantage of weighted majority vote using
the optimal weights w∗(WMV*).
To build intuition, we start by analyzing the optimal ad-
vantage for three regimes of label density (see Figure 4):
Low Label Density: In this sparse setting, very few data
points have more than one non-abstaining label; only a small
number have multiple conﬂicting labels. We have observed
this occurring, for example, in the early stages of applica-
tion development. We see that with non-adversarial label-
ing functions (w∗> 0), even an optimal generative model
(WMV*) can only disagree with MV when there are dis-
agreeing labels, which will occur infrequently. We see that
7We generate a class-balanced dataset of m = 1000 data points
with binary labels, and n independent labeling functions with
average accuracy 75% and a ﬁxed 10% probability of voting.
Table 1:
Modeling advantage Aw attained us-
ing a generative model for several applications in
Snorkel (Section 4.1), the upper bound ˜A∗used by
our optimizer, the modeling strategy selected by the
optimizer—either majority vote (MV) or generative
model (GM)—and the empirical label density dΛ.
Dataset
Aw (%)
˜A∗(%)
Modeling Strategy
dΛ
Radiology
7.0
12.4
GM
2.3
CDR
4.9
7.9
GM
1.8
Spouses
4.4
4.6
GM
1.4
Chem
0.1
0.3
MV
1.2
EHR
2.8
4.8
GM
1.2
the expected optimal advantage will have an upper bound
that falls quadratically with label density:
Proposition 1. (Low-Density Upper Bound) Assume
that P(Λi,j ̸= ∅) = pl ∀i, j, and w∗
j > 0 ∀j. Then, the ex-
pected label density is ¯d = npl, and
EΛ,y,w∗[A∗] = O
# ¯d2
(1)
Proof Sketch: We bound the advantage above by computing
the expected number of pairwise disagreements.
High Label Density:
In this setting, the majority of
the data points have a large number of labels.
For ex-
ample, we might be working in an extremely high-volume
crowdsourcing setting, or an application with many high-
coverage knowledge bases as distant supervision.
Under
modest assumptions—namely, that the average labeling func-
tion accuracy α∗is greater than 50%—it is known that the
majority vote converges exponentially to an optimal solu-
tion as the average label density ¯d increases, which serves as
an upper bound for the expected optimal advantage as well:
Theorem 1. (High-Density Upper Bound [27]) Assume
that P(Λi,j ̸= 0) = pl ∀i, j, and that α∗=
1
n
Pn
j=1 α∗
j =
1
n
Pn
j=1 1/(1 + exp(w∗
j )) > 1
2. Then:
EΛ,y,w∗[A∗] ≤e−2pl(α∗−1
2)
2 ¯
d
(2)
Proof: This follows from the result in [27] for the symmet-
ric Dawid-Skene model under constant probability sampling.
Medium Label Density: In this middle regime, we expect
that modeling the accuracies of the labeling functions will
deliver the greatest gains in predictive performance because
we will have many data points with a small number of dis-
agreeing labeling functions. For such points, the estimated
labeling function accuracies can heavily aﬀect the predicted
labels. We indeed see gains in the empirical results using an
independent generative model that only includes accuracy
factors φAcc
i,j
(Table 1). Furthermore, the guarantees in [38]
establish that we can learn the optimal weights, and thus
approach the optimal advantage.
3.1.2
Automatically Choosing a Modeling Strategy
The bounds in the previous subsection imply that there
are settings in which we should be able to safely skip mod-
eling the labeling function accuracies, simply taking the un-
weighted majority vote instead. However, in practice, the
274


---

overall label density dΛ is insuﬃciently precise to determine
the transition points of interest, given a user time-cost trade-
oﬀpreference (characterized by the advantage tolerance pa-
rameter γ in Algorithm 1). We show this in Table 1 using
our application data sets from Section 4.1. For example, we
see that the Chem and EHR label matrices have equivalent
label densities; however, modeling the labeling function ac-
curacies has a much greater eﬀect for EHR than for Chem.
Instead of simply considering the average label density dΛ,
we instead develop a best-case heuristic based on looking at
the ratio of positive to negative labels for each data point.
This heuristic serves as an upper bound to the true expected
advantage, and thus we can use it to determine when we can
safely skip training the generative model (see Algorithm 1).
Let cy(Λi) = Pn
j=1 1 {Λi,j = y}, in other words, the counts
of positive or negative labels for a given data point xi, and
assume that the true accuracies of the labeling functions lie
within a ﬁxed range, wj ∈[wmin, wmax] and have a mean
¯w.8 Then, deﬁne:
Φ(Λi, y) = 1 {cy(Λi)wmax > c−y(Λi)wmin}
˜A∗(Λ) = 1
m
m
X
i=1
X
y′∈±1
1

y′f1(Λi) < 0
	
Φ(Λi, y′)σ(−f ¯
w(Λi))
where σ(·) is the sigmoid function, f ¯
w is majority vote with
all weights set to the mean ¯w, and ˜A∗(Λ) is the predicted
modeling advantage used by our optimizer. Essentially, we
are taking the expected counts of instances in which a
weighted majority vote could possibly ﬂip the incorrect pre-
dictions of unweighted majority vote under best case condi-
tions, which is an upper bound for the expected advantage:
Proposition 2. (Optimizer Upper Bound) Assume
that the labeling functions have accuracy parameters (log-
odds weights) wj ∈[wmin, wmax], and have E[w] = ¯w. Then:
Ey,w∗[A∗| Λ] ≤˜A∗(Λ)
(3)
Proof Sketch: We upper-bound the modeling advantage by
the expected number of instances in which WMV* is correct
and MV is incorrect. We then upper-bound this by using
the best-case probability of the weighted majority vote be-
ing correct given (wmin, wmax).
We apply ˜A∗to a synthetic dataset and plot in Figure 4.
Next, we compute ˜A∗for the labeling matrices from ex-
periments in Section 4.1, and compare with the empirical
advantage of the trained generative models (Table 1). We
see that our approximate quantity ˜A∗serves as a correct
guide in all cases for determining which modeling strategy
to select, which for the mature applications reported on is
indeed most often the generative model. However, we see
that while EHR and Chem have equivalent label densities,
our optimizer correctly predicts that Chem can be modeled
with majority vote, speeding up each pipeline execution by
1.8×. We ﬁnd in our applications that the optimizer can
save execution time especially during the initial stages of it-
erative development (see full version).
8We ﬁx these at defaults of (wmin, ¯w, wmax) = (0.5, 1.0, 1.5),
which corresponds to assuming labeling functions have accuracies
between 62% and 82%, and an average accuracy of 73%.
3.2
Modeling Structure
In this subsection, we consider modeling additional sta-
tistical structure beyond the independent model. We study
the tradeoﬀbetween predictive performance and computa-
tional cost, and describe how to automatically select a good
point in this tradeoﬀspace.
Structure Learning. We observe many Snorkel users writ-
ing labeling functions that are statistically dependent. Ex-
amples we have observed include:
• Functions that are variations of each other, such as check-
ing for matches against similar regular expressions.
• Functions that operate on correlated inputs, such as raw
tokens of text and their lemmatizations.
• Functions that use correlated sources of knowledge, such
as distant supervision from overlapping knowledge bases.
Modeling such dependencies is important because they aﬀect
our estimates of the true labels. Consider the extreme case
in which not accounting for dependencies is catastrophic:
Example 3.1. Consider a set of 10 labeling functions,
where 5 are perfectly correlated, i.e., they vote the same way
on every data point, and 5 are conditionally independent
given the true label. If the correlated labeling functions have
accuracy α = 50% and the uncorrelated ones have accuracy
β = 99%, then the maximum likelihood estimate of their ac-
curacies according to the independent model is ˆα = 100%
and ˆβ = 50%.
Specifying a generative model to account for such depen-
dencies by hand is impractical for three reasons. First, it
is diﬃcult for non-expert users to specify these dependen-
cies.
Second, as users iterate on their labeling functions,
their dependency structure can change rapidly, like when a
user relaxes a labeling function to label many more candi-
dates. Third, the dependency structure can be dataset spe-
ciﬁc, making it impossible to specify a priori, such as when
a corpus contains many strings that match multiple regular
expressions used in diﬀerent labeling functions. We observed
users of earlier versions of Snorkel struggling for these rea-
sons to construct accurate and eﬃcient generative models
with dependencies. We therefore seek a method that can
quickly identify an appropriate dependency structure from
the labeling function outputs Λ alone.
Naively, we could include all dependencies of interest, such
as all pairwise correlations, in the generative model and per-
form parameter estimation. However, this approach is im-
practical. For 100 labeling functions and 10,000 data points,
estimating parameters with all possible correlations takes
roughly 45 minutes. When multiplied over repeated runs of
hyperparameter searching and development cycles, this cost
greatly inhibits labeling function development. We therefore
turn to our method for automatically selecting which depen-
dencies to model without access to ground truth [5]. It uses
a pseudolikelihood estimator, which does not require any
sampling or other approximations to compute the objective
gradient exactly. It is much faster than maximum likelihood
estimation, taking 15 seconds to select pairwise correlations
to be modeled among 100 labeling functions with 10,000
data points.
However, this approach relies on a selection
threshold hyperparameter ϵ which induces a tradeoﬀspace
between predictive performance and computational cost.
275


---

Figure 5: Predictive performance of the generative model and number of learned correlations versus the
correlation threshold ϵ. The selected elbow point achieves a good tradeoﬀbetween predictive performance and
computational cost (linear in the number of correlations). Left: simulation of structure learning correcting
the generative model. Middle: the CDR task. Right: all user study labeling functions for the Spouses task.
3.2.1
Tradeoff Space
Such structure learning methods, whether pseudolikeli-
hood or likelihood-based, crucially depend on a selection
threshold ϵ for deciding which dependencies to add to the
generative model.
Fundamentally, the choice of ϵ deter-
mines the complexity of the generative model.9 We study
the tradeoﬀbetween predictive performance and computa-
tional cost that this induces. We ﬁnd that generally there is
an “elbow point” beyond which the number of correlations
selected—and thus the computational cost—explodes, and
that this point is a safe tradeoﬀpoint between predictive
performance and computation time.
Predictive Performance: At one extreme, a very large
value of ϵ will not include any correlations in the generative
model, making it identical to the independent model. As ϵ
is decreased, correlations will be added. At ﬁrst, when ϵ is
still high, only the strongest correlations will be included.
As these correlations are added, we observe that the gen-
erative model’s predictive performance tends to improve.
Figure 5, left, shows the result of varying ϵ in a simula-
tion where more than half the labeling functions are corre-
lated. After adding a few key dependencies, the generative
model resolves the discrepancies among the labeling func-
tions. Figure 5, middle, shows the eﬀect of varying ϵ for the
CDR task. Predictive performance improves as ϵ decreases
until the model overﬁts. Finally, we consider a large number
of labeling functions that are likely to be correlated. In our
user study (described in Section 4.2), participants wrote la-
beling functions for the Spouses task. We combined all 125
of their functions and studied the eﬀect of varying ϵ. Here,
we expect there to be many correlations since it is likely
that users wrote redundant functions. We see in Figure 5,
right, that structure learning surpasses the best performing
individual’s generative model (50.0 F1).
Computational Cost: Computational cost is correlated
with model complexity. Since learning in Snorkel is done
with a Gibbs sampler, the overhead of modeling additional
correlations is linear in the number of correlations.
The
dashed lines in Figure 5 show the number of correlations in-
cluded in each model versus ϵ. For example, on the Spouses
task, ﬁtting the parameters of the generative model at ϵ =
0.5 takes 4 minutes, and ﬁtting its parameters with ϵ = 0.02
9Speciﬁcally, ϵ is both the coeﬃcient of the ℓ1 regularization term
used to induce sparsity, and the minimum absolute weight in log
scale that a dependency must have to be selected.
takes 57 minutes. Further, parameter estimation is often run
repeatedly during development for two reasons: (i) ﬁtting
generative model hyperparameters using a development set
requires repeated runs, and (ii) as users iterate on their la-
beling functions, they must re-estimate the generative model
to evaluate them.
3.2.2
Automatically Choosing a Model
Based on our observations, we seek to automatically
choose a value of ϵ that trades oﬀbetween predictive perfor-
mance and computational cost using the labeling functions’
outputs Λ alone. Including ϵ as a hyperparameter in a grid
search over a development set is generally not feasible be-
cause of its large eﬀect on running time. We therefore want
to choose ϵ before other hyperparameters, without perform-
ing any parameter estimation. We propose using the num-
ber of correlations selected at each value of ϵ as an inex-
pensive indicator. The dashed lines in Figure 5 show that
as ϵ decreases, the number of selected correlations follows a
pattern. Generally, the number of correlations grows slowly
at ﬁrst, then hits an “elbow point” beyond which the num-
ber explodes, which ﬁts the assumption that the correlation
structure is sparse. In all three cases, setting ϵ to this el-
bow point is a safe tradeoﬀbetween predictive performance
and computational cost. In cases where performance grows
consistently (left and right), the elbow point achieves most
of the predictive performance gains at a small fraction of
the computational cost. For example, on Spouses (right),
choosing ϵ = 0.08 achieves a score of 56.6 F1—within one
point of the best score—but only takes 8 minutes for pa-
rameter estimation. In cases where predictive performance
eventually degrades (middle), the elbow point also selects
a relatively small number of correlations, giving an 0.7 F1
point improvement and avoiding overﬁtting.
Performing structure learning for many settings of ϵ is in-
expensive, especially since the search needs to be performed
only once before tuning the other hyperparameters. On the
large number of labeling functions in the Spouses task, struc-
ture learning for 25 values of ϵ takes 14 minutes. On CDR,
with a smaller number of labeling functions, it takes 30 sec-
onds. Further, if the search is started at a low value of ϵ and
increased, it can often be terminated early, when the num-
ber of selected correlations reaches a low value. Selecting the
elbow point itself is straightforward. We use the point with
greatest absolute diﬀerence from its neighbors, but more
sophisticated schemes can also be applied [43]. Our full op-
timization algorithm for choosing a modeling strategy and
(if necessary) correlations is shown in Algorithm 1.
276


---

Algorithm 1 Modeling Strategy Optimizer
Input: Label matrix Λ ∈(Y ∪{∅})m×n,
advantage tolerance γ, structure search resolution η
Output: Modeling strategy
if ˜A∗(Λ) < γ then
return MV
Structures ←[ ]
for i from 1 to
1
2η do
ϵ ←i · η
C ←LearnStructure(Λ, ϵ)
Structures.append(|C|, ϵ)
ϵ ←SelectElbowPoint(Structures)
return GMϵ
4.
EVALUATION
We evaluate Snorkel by drawing on deployments devel-
oped in collaboration with users. We report on two real-
world deployments and four tasks on open-source data sets
representative of other deployments. Our evaluation is de-
signed to support the following three main claims:
• Snorkel outperforms distant supervision baselines.
In distant supervision [32], one of the most popular forms
of weak supervision used in practice, an external knowl-
edge base is heuristically aligned with input data to serve
as noisy training labels. By allowing users to easily incor-
porate a broader, more heterogeneous set of weak super-
vision sources, Snorkel exceeds models trained via distant
supervision by an average of 132%.
• Snorkel approaches hand supervision. We see that
by writing tens of labeling functions, we were able to ap-
proach or match results using hand-labeled training data
which took weeks or months to assemble, coming within
2.11% of the F1 score of hand supervision on relation ex-
traction tasks and an average 5.08% accuracy or AUC on
cross-modal tasks, for an average 3.60% across all tasks.
• Snorkel enables a new interaction paradigm. We
measure Snorkel’s eﬃciency and ease-of-use by reporting
on a user study of biomedical researchers from across the
U.S. These participants learned to write labeling functions
to extract relations from news articles as part of a two-
day workshop on learning to use Snorkel, and matched
or outperformed models trained on hand-labeled training
data, showing the eﬃciency of Snorkel’s process even for
ﬁrst-time users.
We now describe our results in detail. First, we describe
the six applications that validate our claims. We then show
that Snorkel’s generative modeling stage helps to improve
the predictive performance of the discriminative model,
demonstrating that it is 5.81% more accurate when trained
on Snorkel’s probabilistic labels versus labels produced by
an unweighted average of labeling functions. We also val-
idate that the ability to incorporate many diﬀerent types
of weak supervision incrementally improves results with an
ablation study. Finally, we describe the protocol and results
of our user study.
4.1
Applications
To evaluate the eﬀectiveness of Snorkel, we consider sev-
eral real-world deployments and tasks on open-source datasets
Table 2: Number of labeling functions, fraction of
positive labels (for binary classiﬁcation tasks), num-
ber of training documents, and number of training
candidates for each task.
Task
# LFs
% Pos.
# Docs
# Candidates
Chem
16
4.1
1,753
65,398
EHR
24
36.8
47,827
225,607
CDR
33
24.6
900
8,272
Spouses
11
8.3
2,073
22,195
Radiology
18
36.0
3,851
3,851
Crowd
102
-
505
505
that are representative of other deployments in information
extraction, medical image classiﬁcation, and crowdsourced
sentiment analysis. Summary statistics of the tasks are pro-
vided in Table 2.
Discriminative Models: One of the key bets in Snorkel’s
design is that the trend of increasingly powerful, open-source
machine learning tools (e.g., models, pre-trained word em-
beddings and initial layers, automatic tuners, etc.)
will
only continue to accelerate. To best take advantage of this,
Snorkel creates probabilistic training labels for any discrim-
inative model with a standard loss function.
In the following experiments, we control for end model se-
lection by using currently popular, standard choices across
all settings. For text modalities, we choose a bidirectional
long short term memory (LSTM) sequence model [17], and
for the medical image classiﬁcation task we use a 50-layer
ResNet [19] pre-trained on the ImageNet object classiﬁca-
tion dataset [14]. Both models are implemented in Tensor-
ﬂow [2] and trained using the Adam optimizer [24], with
hyperparameters selected via random grid search using a
small labeled development set. Final scores are reported on
a held-out labeled test set. See full version for details.
A key takeaway of the following results is that the discrim-
inative model generalizes beyond the heuristics encoded in
the labeling functions (as in Example 2.5). In Section 4.1.1,
we see that on relation extraction applications the discrimi-
native model improves performance over the generative
model primarily by increasing recall by 43.15% on average.
In Section 4.1.2, the discriminative model classiﬁes entirely
new modalities of data to which the labeling functions can-
not be applied.
4.1.1
Relation Extraction from Text
We ﬁrst focus on four relation extraction tasks on text
data, as it is a challenging and common class of problems
that are well studied and for which distant supervision is
often considered. Predictive performance is summarized in
Table 3. We brieﬂy describe each task.
Scientiﬁc Articles (Chem): With modern online reposi-
tories of scientiﬁc literature, such as PubMed10 for biomed-
ical articles, research results are more accessible than ever
before. However, actually extracting ﬁne-grained pieces of
information in a structured format and using this data to
answer speciﬁc questions at scale remains a signiﬁcant open
challenge for researchers. To address this challenge in the
10https://www.ncbi.nlm.nih.gov/pubmed/
277


---

Table 3:
Evaluation of Snorkel on relation extraction tasks from text. Snorkel’s generative and discriminative
models consistently improve over distant supervision, measured in F1, the harmonic mean of precision (P)
and recall (R). We compare with hand-labeled data when available, coming within an average of 1 F1 point.
Distant Supervision
Snorkel (Gen.)
Snorkel (Disc.)
Hand Supervision
Task
P
R
F1
P
R
F1
Lift
P
R
F1
Lift
P
R
F1
Chem
11.2
41.2
17.6
78.6
21.6
33.8
+16.2
87.0
39.2
54.1
+36.5
-
-
-
EHR
81.4
64.8
72.2
77.1
72.9
74.9
+2.7
80.2
82.6
81.4
+9.2
-
-
-
CDR
25.5
34.8
29.4
52.3
30.4
38.5
+9.1
38.8
54.3
45.3
+15.9
39.9
58.1
47.3
Spouses
9.9
34.8
15.4
53.5
62.1
57.4
+42.0
48.4
61.6
54.2
+38.8
47.8
62.5
54.2
context of drug safety research, Stanford and U.S. Food and
Drug Administration (FDA) collaborators used Snorkel to
develop a system for extracting chemical reagent and reac-
tion
product
relations
from
PubMed
abstracts.
The goal was to build a database of chemical reactions that
researchers at the FDA can use to predict unknown drug
interactions. We used the chemical reactions described in
the Metacyc database [8] for distant supervision.
Electronic Health Records (EHR): As patients’ clinical
records increasingly become digitized, researchers hope to
inform clinical decision making by retrospectively analyzing
large patient cohorts, rather than conducting expensive ran-
domized controlled studies. However, much of the valuable
information in electronic health records (EHRs)—such as
ﬁne-grained clinical details, practitioner notes, etc.—is not
contained in standardized medical coding systems, and is
thus locked away in the unstructured text notes sections. In
collaboration with researchers and clinicians at the U.S. De-
partment of Veterans Aﬀairs, Stanford Hospital and Clinics
(SHC), and the Stanford Center for Biomedical Informatics
Research, we used Snorkel to develop a system to extract
structured data from unstructured EHR notes. Speciﬁcally,
the system’s task was to extract mentions of pain levels at
precise anatomical locations from clinician notes, with the
goal of using these features to automatically assess patient
well-being and detect complications after medical interven-
tions like surgery.
To this end, our collaborators created
a cohort of 5,800 patients from SHC EHR data, with visit
dates between 1995 and 2015, resulting in 500K unstruc-
tured clinical documents.
Since distant supervision from
a knowledge base is not applicable, we compared against
regular-expression-based labeling previously developed for
this task.
Chemical-Disease Relations (CDR): We used the 2015
BioCreative chemical-disease relation dataset [49], where the
task is to identify mentions of causal links between chem-
icals and diseases in PubMed abstracts. We used all pairs
of chemical and disease mentions co-occuring in a sentence
as our candidate set. We used the Comparative Toxicoge-
nomics Database (CTD) [33] for distant supervision, and ad-
ditionally wrote labeling functions capturing language pat-
terns and information from the context hierarchy. To eval-
uate Snorkel’s ability to discover previously unknown infor-
mation, we randomly removed half of the relations in CTD
and evaluated on candidates not contained in the remaining
half.
Spouses: Our fourth task is to identify mentions of spouse
relationships in a set of news articles from the Signal Media
Table 4:
Evaluation on cross-modal experiments.
Labeling functions that operate on or represent one
modality (text, crowd workers) produce training la-
bels for models that operate on another modality
(images, text), and approach the predictive perfor-
mance of large hand-labeled training datasets.
Task
Snorkel (Disc.)
Hand Supervision
Radiology (AUC)
72.0
76.2
Crowd (Acc)
65.6
68.8
dataset [10]. We used all pairs of person mentions (tagged
with SpaCy’s NER module11) co-occuring in the same sen-
tence as our candidate set. To obtain hand-labeled data for
evaluation, we crowdsourced labels for the candidates via
Amazon Mechanical Turk, soliciting labels from three work-
ers for each example and assigning the majority vote. We
then wrote labeling functions that encoded language pat-
terns and distant supervision from DBpedia [26].
4.1.2
Cross-Modal: Images & Crowdsourcing
In the cross-modal setting, we write labeling functions
over one data modality (e.g., a text report, or the votes of
crowdworkers) and use the resulting labels to train a clas-
siﬁer deﬁned over a second, totally separate modality (e.g.,
an image or the text of a tweet).
This demonstrates the
ﬂexibility of Snorkel, in that the labeling functions (and by
extension, the generative model) do not need to operate over
the same domain as the discriminative model being trained.
Predictive performance is summarized in Table 4.
Abnormality Detection in Lung Radiographs (Rad):
In many real-world radiology settings, there are large repos-
itories of image data with corresponding narrative text re-
ports, but limited or no labels that could be used for training
an image classiﬁcation model. In this application, in collab-
oration with radiologists, we wrote labeling functions over
the text radiology reports, and used the resulting labels to
train an image classiﬁer to detect abnormalities in lung X-
ray images. We used a publicly available dataset from the
OpenI biomedical image repository12 consisting of 3,851 dis-
tinct radiology reports—composed of unstructured text and
Medical Subject Headings (MeSH)13 codes—and accompa-
nying X-ray images.
11https://spacy.io/
12http://openi.nlm.nih.gov/
13https://www.nlm.nih.gov/mesh/meshhome.html
278


---

Table 5: Comparison between training the discrimi-
native model on the labels estimated by the genera-
tive model, versus training on the unweighted aver-
age of the LF outputs. Predictive performance gains
show that modeling LF noise helps.
Disc. Model on
Task
Unweighted LFs
Disc. Model
Lift
Chem
48.6
54.1
+5.5
EHR
80.9
81.4
+0.5
CDR
42.0
45.3
+3.3
Spouses
52.8
54.2
+1.4
Crowd (Acc)
62.5
65.6
+3.1
Rad. (AUC)
67.0
72.0
+5.0
Crowdsourcing (Crowd): We trained a model to perform
sentiment analysis using crowdsourced annotations from the
weather sentiment task from Crowdﬂower.14
In this task,
contributors were asked to grade the sentiment of often-
ambiguous tweets relating to the weather, choosing between
ﬁve categories of sentiment.
Twenty contributors graded
each tweet, but due to the diﬃculty of the task and lack of
crowdworker ﬁltering, there were many conﬂicts in worker
labels.
We represented each crowdworker as a labeling
function—showing Snorkel’s ability to subsume existing
crowdsourcing modeling approaches—and then used the re-
sulting labels to train a text model over the tweets, for mak-
ing predictions independent of the crowd workers.
4.1.3
Effect of Generative Modeling
An important question is the signiﬁcance of modeling the
accuracies and correlations of the labeling functions on the
end predictive performance of the discriminative model (ver-
sus in Section 3, where we only considered the eﬀect on the
accuracy of the generative model).
We compare Snorkel
with a simpler pipeline that skips the generative modeling
stage and trains the discriminative model on an unweighted
average of the labeling functions’ outputs. Table 5 shows
that the discriminative model trained on Snorkel’s proba-
bilistic labels consistently predicts better, improving 5.81%
on average. These results demonstrate that the discrimina-
tive model eﬀectively learns from the additional signal con-
tained in Snorkel’s probabilistic training labels over simpler
modeling strategies.
4.1.4
Labeling Function Type Ablation
We also examine the impact of diﬀerent types of labeling
functions on end predictive performance, using the CDR
application as a representative example of three common
categories of labeling functions:
• Text Patterns: Basic word, phrase, and regular expression
labeling functions.
• Distant Supervision: External knowledge bases mapped
to candidates, either directly or ﬁltered by a heuristic.
• Structure-Based: Labeling functions expressing heuristics
over the context hierarchy, e.g., reasoning about position
in the document or relative to other candidates.
We show an ablation in Table 6, sorting by stand-alone
score.
We see that distant supervision adds recall at the
14https://www.crowdflower.com/data/weather-sentiment/
Table 6: Labeling function ablation study on CDR.
Adding diﬀerent types of labeling functions im-
proves predictive performance.
LF Type
P
R
F1
Lift
Text Patterns
42.3
42.4
42.3
+ Distant Supervision
37.5
54.1
44.3
+2.0
+ Structure-based
38.8
54.3
45.3
+1.0
cost of some precision, as we would expect, but ultimately
improves F1 score by 2 points; and that structure-based
labeling functions, enabled by Snorkel’s context hierarchy
data representation, add an additional F1 point.
4.2
User Study
We conducted a formal study of Snorkel to (i) evaluate
how quickly SME users could learn to write labeling func-
tions, and (ii) empirically validate the core hypothesis that
writing labeling functions is more time-eﬃcient than hand-
labeling data. Users were given instruction on Snorkel, and
then asked to write labeling functions for the Spouses task
described in the previous subsection.
Participants: In collaboration with the Mobilize Center
[25], an NIH-funded Big Data to Knowledge (BD2K) cen-
ter, we distributed a national call for applications to at-
tend a two-day workshop on using Snorkel for biomedical
knowledge base construction. Selection criteria included a
strong biomedical project proposal and little-to-no prior ex-
perience using Snorkel. In total, 15 researchers15 were in-
vited to attend out of 33 team applications submitted, with
varying backgrounds in bioinformatics, clinical informatics,
and data mining from universities, companies, and organiza-
tions around the United States. The education demograph-
ics included 6 bachelors, 4 masters, and 5 Ph.D. degrees.
All participants could program in Python, with 80% rating
their skill as intermediate or better; 40% of participants had
little-to-no prior exposure to machine learning; and 53-60%
had no prior experience with text mining or information ex-
traction applications. See full version for details.
Protocol: The ﬁrst day focused entirely on labeling func-
tions, ranging from theoretical motivations to details of the
Snorkel API. Over the course of 7 hours, participants were
instructed in a classroom setting on how to use and evalu-
ate models developed using Snorkel. Users were presented
with 4 tutorial Jupyter notebooks providing skeleton code
for evaluating labeling functions, along with a small labeled
development candidate set, and were given 2.5 hours of ded-
icated development time in aggregate to write their labeling
functions. All workshop materials are available online.16
Baseline: To compare our users’ performance against mod-
els trained on hand-labeled data, we collected a large hand-
labeled dataset via Amazon Mechanical Turk (the same set
used in the previous subsection). We then split this into 15
datasets representing 7 hours worth of hand-labeling time
15One participant declined to write labeling functions, so their
score is not included in our analysis.
16https://github.com/HazyResearch/snorkel/tree/master/
tutorials/workshop
279


---

each—based on the crowd-worker average of 10 seconds per
label—simulating
the
alternative
scenario
where
users
skipped both instruction and labeling function development
sessions and instead spent the full day hand-labeling data.
Results: Our key ﬁnding is that labeling functions written
in Snorkel, even by SME users, can match or exceed a tradi-
tional hand-labeling approach. The majority (8) of subjects
matched or outperformed these hand-labeled data models.
The average Snorkel user’s score was 30.4 F1, and the aver-
age hand-supervision score was 20.9 F1. The best perform-
ing user model scored 48.7 F1, 19.2 points higher than the
best supervised model using hand-labeled data. The worst
participant scored 12.0 F1, 0.3 points higher that the low-
est hand-labeled model. The full distribution of scores by
participant, and broken down by participant background,
compared against the baseline models trained with hand-
labeled data is available in the full version.
5.
RELATED WORK
This section is an overview of techniques for managing
weak supervision, many of which are subsumed in Snorkel.
We also contrast it with related forms of supervision.
Combining Weak Supervision Sources: The main chal-
lenge of weak supervision is how to combine multiple sources.
For example, if a user provides two knowledge bases for dis-
tant supervision, how should a data point that matches only
one knowledge base be labeled? Some researchers have used
multi-instance learning to reduce the noise in weak supervi-
sion sources [22,41], essentially modeling the diﬀerent weak
supervision sources as soft constraints on the true label, but
this approach is limited because it requires using a speciﬁc
end model that supports multi-instance learning.
Researchers have therefore considered how to estimate the
accuracy of label sources without a gold standard with which
to compare—a classic problem [13]—and combine these es-
timates into labels that can be used to train an arbitrary
end model. Much of this work has focused on crowdsourc-
ing, in which workers have unknown accuracy [11, 23, 53].
Such methods use generative probabilistic models to esti-
mate a latent variable—the true class label—based on noisy
observations.
Other methods use generative models with
hand-speciﬁed dependency structures to label data for spe-
ciﬁc modalities, such as topic models for text [4] or denois-
ing distant supervision sources [42, 48].
Other techniques
for estimating latent class labels given noisy observations
include spectral methods [35]. Snorkel is distinguished from
these approaches because its generative model supports a
wide range of weak supervision sources, and it learns the
accuracies and correlation structure among weak supervi-
sion sources without ground truth data.
Other Forms of Supervision: Work on semi-supervised
learning considers settings with some labeled data and a
much larger set of unlabeled data, and then leverages various
domain- and task-agnostic assumptions about smoothness,
low-dimensional structure, or distance metrics to heuristi-
cally label the unlabeled data [9]. Work on active learning
aims to automatically estimate which data points are opti-
mal to label, thereby hopefully reducing the total number of
examples that need to be manually annotated [45]. Trans-
fer learning considers the strategy of repurposing models
trained on diﬀerent datasets or tasks where labeled training
data is more abundant [34]. Another type of supervision is
self-training [3,44] and co-training [6], which involves train-
ing a model or pair of models on data that they labeled
themselves. Weak supervision is distinct in that the goal
is to solicit input directly from SMEs, however at a higher
level of abstraction and/or in an inherently noisier form.
Snorkel is focused on managing weak supervision sources,
but combing its methods with these other types of supervi-
sion is straightforward.
Related Data Management Problems:
Researchers
have considered related problems in data management, such
as data fusion [15,40] and truth discovery [28]. In these set-
tings, the task is to estimate the reliability of data sources
that provide assertions of facts and determine which facts
are likely true.
Many approaches to these problems use
probablistic graphical models that are related to Snorkel’s
generative model in that they represent the unobserved truth
as a latent variable, e.g., the latent truth model [54]. Our
setting diﬀers in that labeling functions assign labels to user-
provided data, and they may provide any label or abstain,
which we must model.
Work on data fusion has also ex-
plored how to model user-speciﬁed correlations among data
sources [36]. Snorkel automatically identiﬁes which correla-
tions among labeling functions to model.
6.
CONCLUSION
Snorkel provides a new paradigm for soliciting and manag-
ing weak supervision to create training data sets. In Snorkel,
users provide higher-level supervision in the form of label-
ing functions that capture domain knowledge and resources,
without having to carefully manage the noise and conﬂicts
inherent in combining weak supervision sources. Our evalua-
tions demonstrate that Snorkel signiﬁcantly reduces the cost
and diﬃculty of training powerful machine learning mod-
els while exceeding prior weak supervision methods and ap-
proaching the quality of large, hand-labeled training sets.
Snorkel’s deployments in industry, research labs, and gov-
ernment agencies show that it has real-world impact, oﬀer-
ing developers an improved way to build models.
Acknowledgments. Alison Callahan and Nigam Shah of Stan-
ford, and Nicholas Giori of the US Dept.
of Veterans Aﬀairs
developed the electronic health records application. Emily Mal-
lory, Ambika Acharya, and Russ Altman of Stanford, and Roselie
Bright and Elaine Johanson of the US Food and Drug Adminis-
tration developed the scientiﬁc articles application. Joy Ku of the
Mobilize Center organized the user study. Nishith Khandwala de-
veloped the radiograph application. We thank the contributors to
Snorkel including Bryan He, Theodoros Rekatsinas, and Braden
Hancock. We gratefully acknowledge the support of DARPA un-
der No. N66001-15-C-4043 (SIMPLEX), No. FA8750-17-2-0095
(D3M), No. FA8750-12-2-0335, and No. FA8750-13-2-0039, DOE
108845, NIH U54EB020405, ONR under No.
N000141210041
and No. N000141310129, the Moore Foundation, the Okawa Re-
search Grant, American Family Insurance, Accenture, Toshiba,
the Stanford Interdisciplinary Graduate and Bio-X fellowships,
and members of the Stanford DAWN project: Intel, Microsoft,
Teradata, and VMware.
The U.S. Government is authorized
to reproduce and distribute reprints for Governmental purposes
notwithstanding any copyright notation thereon. Any opinions,
ﬁndings, and conclusions or recommendations expressed in this
material are those of the authors and do not necessarily reﬂect
the views, policies, or endorsements, either expressed or implied,
of DARPA, DOE, NIH, ONR, or the U.S. Government.
280


---

7.
REFERENCES
[1] Worldwide semiannual cognitive/artiﬁcial intelligence
systems spending guide. Technical report, International
Data Corporation, 2017.
[2] M. Abadi, P. Barham, J. Chen, Z. Chen, A. Davis, J. Dean,
M. Devin, S. Ghemawat, G. Irving, M. Isard, et al.
TensorFlow: A system for large-scale machine learning. In
USENIX Symposium on Operating Systems Design and
Implementation (OSDI), 2016.
[3] A. K. Agrawala. Learning with a probabilistic teacher.
IEEE Transactions on Infomation Theory, 16:373–379,
1970.
[4] E. Alfonseca, K. Filippova, J.-Y. Delort, and G. Garrido.
Pattern learning for relation extraction with a hierarchical
topic model. In Meeting of the Association for
Computational Linguistics (ACL), 2012.
[5] S. H. Bach, B. He, A. Ratner, and C. R´e. Learning the
structure of generative models without labeled data. In
International Conference on Machine Learning (ICML),
2017.
[6] A. Blum and T. Mitchell. Combining labeled and unlabeled
data with co-training. In Workshop on Computational
Learning Theory (COLT), 1998.
[7] R. C. Bunescu and R. J. Mooney. Learning to extract
relations from the Web using minimal supervision. In
Meeting of the Association for Computational Linguistics
(ACL), 2007.
[8] R. Caspi, R. Billington, L. Ferrer, H. Foerster, C. A.
Fulcher, I. M. Keseler, A. Kothari, M. Krummenacker,
M. Latendresse, L. A. Mueller, Q. Ong, S. Paley,
P. Subhraveti, D. S. Weaver, and P. D. Karp. The MetaCyc
database of metabolic pathways and enzymes and the
BioCyc collection of pathway/genome databases. Nucleic
Acids Research, 44(D1):D471–D480, 2016.
[9] O. Chapelle, B. Sch¨olkopf, and A. Zien, editors.
Semi-Supervised Learning. Adaptive Computation and
Machine Learning. MIT Press, 2009.
[10] D. Corney, D. Albakour, M. Martinez, and S. Moussa.
What do a million news articles look like? In Workshop on
Recent Trends in News Information Retrieval, 2016.
[11] N. Dalvi, A. Dasgupta, R. Kumar, and V. Rastogi.
Aggregating crowdsourced binary ratings. In International
World Wide Web Conference (WWW), 2013.
[12] A. P. Davis et al. A CTD–Pﬁzer collaboration: Manual
curation of 88,000 scientiﬁc articles text mined for
drug–disease and drug–phenotype interactions. Database,
2013.
[13] A. P. Dawid and A. M. Skene. Maximum likelihood
estimation of observer error-rates using the EM algorithm.
Journal of the Royal Statistical Society C, 28(1):20–28,
1979.
[14] J. Deng, W. Dong, R. Socher, L.-J. Li, K. Li, and
L. Fei-Fei. Imagenet: A large-scale hierarchical image
database. In Computer Vision and Pattern Recognition,
IEEE Conference on (CVPR), 2009.
[15] X. L. Dong and D. Srivastava. Big Data Integration.
Synthesis Lectures on Data Management. Morgan &
Claypool Publishers, 2015.
[16] L. Eadicicco. Baidu’s Andrew Ng on the future of artiﬁcial
intelligence, 2017. Time [Online; posted 11-January-2017].
[17] A. Graves and J. Schmidhuber. Framewise phoneme
classiﬁcation with bidirectional LSTM and other neural
network architectures. Neural Networks, 18(5):602–610,
2005.
[18] S. Gupta and C. D. Manning. Improved pattern learning
for bootstrapped entity extraction. In CoNLL, 2014.
[19] K. He, X. Zhang, S. Ren, and J. Sun. Deep residual learning
for image recognition. CoRR, abs/1512.03385, 2015.
[20] M. A. Hearst. Automatic acquisition of hyponyms from
large text corpora. In Meeting of the Association for
Computational Linguistics (ACL), 1992.
[21] G. E. Hinton. Training products of experts by minimizing
contrastive divergence. Neural computation,
14(8):1771–1800, 2002.
[22] R. Hoﬀmann, C. Zhang, X. Ling, L. Zettlemoyer, and D. S.
Weld. Knowledge-based weak supervision for information
extraction of overlapping relations. In Meeting of the
Association for Computational Linguistics (ACL), 2011.
[23] M. Joglekar, H. Garcia-Molina, and A. Parameswaran.
Comprehensive and reliable crowd assessment algorithms.
In International Conference on Data Engineering (ICDE),
2015.
[24] D. Kingma and J. Ba. Adam: A method for stochastic
optimization. arXiv preprint arXiv:1412.6980, 2014.
[25] J. P. Ku, J. L. Hicks, T. Hastie, J. Leskovec, C. R´e, and
S. L. Delp. The Mobilize center: an NIH big data to
knowledge center to advance human movement research
and improve mobility. Journal of the American Medical
Informatics Association, 22(6):1120–1125, 2015.
[26] J. Lehmann, R. Isele, M. Jakob, A. Jentzsch,
D. Kontokostas, P. Mendes, S. Hellmann, M. Morsey,
P. van Kleef, S. Auer, and C. Bizer. DBpedia - A
large-scale, multilingual knowledge base extracted from
Wikipedia. Semantic Web Journal, 2014.
[27] H. Li, B. Yu, and D. Zhou. Error rate analysis of labeling
by crowdsourcing. In ICML Workshop: Machine Learning
Meets Crowdsourcing. Atalanta, Georgia, USA, 2013.
[28] Y. Li, J. Gao, C. Meng, Q. Li, L. Su, B. Zhao, W. Fan, and
J. Han. A survey on truth discovery. SIGKDD Explor.
Newsl., 17(2), 2015.
[29] P. Liang, M. I. Jordan, and D. Klein. Learning from
measurements in exponential families. In International
Conference on Machine Learning (ICML), 2009.
[30] G. S. Mann and A. McCallum. Generalized expectation
criteria for semi-supervised learning with weakly labeled
data. Journal of Machine Learning Research, 11:955–984,
2010.
[31] C. Metz. Google’s hand-fed AI now gives answers, not just
search results, 2016. Wired [Online; posted
29-November-2016].
[32] M. Mintz, S. Bills, R. Snow, and D. Jurafsky. Distant
supervision for relation extraction without labeled data. In
Meeting of the Association for Computational Linguistics
(ACL), 2009.
[33] D. A. P., C. J. Grondin, R. J. Johnson, D. Sciaky, B. L.
King, R. McMorran, J. Wiegers, T. Wiegers, and C. J.
Mattingly. The comparative toxicogenomics database:
update 2017. Nucleic Acids Research, 2016.
[34] S. J. Pan and Q. Yang. A survey on transfer learning.
IEEE Transactions on Knowledge and Data Engineering,
22(10):1345–1359, 2010.
[35] F. Parisi, F. Strino, B. Nadler, and Y. Kluger. Ranking and
combining multiple predictors without labeled data.
Proceedings of the National Academy of Sciences of the
USA, 111(4):1253–1258, 2014.
[36] R. Pochampally, A. Das Sarma, X. L. Dong, A. Meliou, and
D. Srivastava. Fusing data with correlations. In ACM
SIGMOD International Conference on Management of
Data (SIGMOD), 2014.
[37] A. J. Quinn and B. B. Bederson. Human computation: A
survey and taxonomy of a growing ﬁeld. In ACM SIGCHI
Conference on Human Factors in Computing Systems
(CHI), 2011.
[38] A. Ratner, C. De Sa, S. Wu, D. Selsam, and C. R´e. Data
programming: Creating large training sets, quickly. In
Neural Information Processing Systems (NIPS), 2016.
[39] T. Rekatsinas, X. Chu, I. F. Ilyas, and C. R´e. HoloClean:
Holistic data repairs with probabilistic inference. PVLDB,
10(11):1190–1201, 2017.
[40] T. Rekatsinas, M. Joglekar, H. Garcia-Molina,
A. Parameswaran, and C. R´e. SLiMFast: Guaranteed
results for data fusion and source reliability. In ACM
SIGMOD International Conference on Management of
Data (SIGMOD), 2017.
281


---

[41] S. Riedel, L. Yao, and A. McCallum. Modeling relations
and their mentions without labeled text. In European
Conference on Machine Learning and Knowledge
Discovery in Databases (ECML PKDD), 2010.
[42] B. Roth and D. Klakow. Combining generative and
discriminative model scores for distant supervision. In
Conference on Empirical Methods on Natural Language
Processing (EMNLP), 2013.
[43] V. Satopaa, J. Albrecht, D. Irwin, and B. Raghavan.
Finding a “kneedle” in a haystack: Detecting knee points
in system behavior. In International Conference on
Distributed Computing Systems Workshops, 2011.
[44] H. J. Scudder. Probability of error of some adaptive
pattern-recognition machines. IEEE Transactions on
Infomation Theory, 11:363–371, 1965.
[45] B. Settles. Active Learning. Synthesis Lectures on Artiﬁcial
Intelligence and Machine Learning. Morgan & Claypool
Publishers, 2012.
[46] R. Stewart and S. Ermon. Label-free supervision of neural
networks with physics and other domain knowledge. In
AAAI Conference on Artiﬁcial Intelligence (AAAI), 2017.
[47] C. Sun, A. Shrivastava, S. Singh, and A. Gupta. Revisiting
unreasonable eﬀectiveness of data in deep learning era.
arXiv preprint arXiv:1707.02968, 2017.
[48] S. Takamatsu, I. Sato, and H. Nakagawa. Reducing wrong
labels in distant supervision for relation extraction. In
Meeting of the Association for Computational Linguistics
(ACL), 2012.
[49] C.-H. Wei, Y. Peng, R. Leaman, D. A. P., C. J. Mattingly,
J. Li, T. Wiegers, and Z. Lu. Overview of the BioCreative
V chemical disease relation (CDR) task. In BioCreative
Challenge Evaluation Workshop, 2015.
[50] M.-C. Yuen, I. King, and K.-S. Leung. A survey of
crowdsourcing systems. In Privacy, Security, Risk and
Trust (PASSAT) and Inernational Conference on Social
Computing (SocialCom), 2011.
[51] O. F. Zaidan and J. Eisner. Modeling annotators: A
generative approach to learning from annotator rationales.
In Conference on Empirical Methods in Natural Language
Processing (EMNLP), 2008.
[52] C. Zhang, C. R´e, M. Cafarella, C. De Sa, A. Ratner,
J. Shin, F. Wang, and S. Wu. DeepDive: Declarative
knowledge base construction. Commun. ACM,
60(5):93–102, 2017.
[53] Y. Zhang, X. Chen, D. Zhou, and M. I. Jordan. Spectral
methods meet EM: A provably optimal algorithm for
crowdsourcing. Journal of Machine Learning Research,
17:1–44, 2016.
[54] B. Zhao, B. I. Rubinstein, J. Gemmell, and J. Han. A
Bayesian approach to discovering truth from conﬂicting
sources for data integration. PVLDB, 5(6):550–561, 2012.
282
