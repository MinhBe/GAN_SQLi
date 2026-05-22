Published as a conference paper at ICLR 2018
SPECTRAL NORMALIZATION
FOR GENERATIVE ADVERSARIAL NETWORKS
Takeru Miyato1, Toshiki Kataoka1, Masanori Koyama2, Yuichi Yoshida3
{miyato, kataoka}@preferred.jp
koyama.masanori@gmail.com
yyoshida@nii.ac.jp
1Preferred Networks, Inc. 2Ritsumeikan University 3National Institute of Informatics
ABSTRACT
One of the challenges in the study of generative adversarial networks is the insta-
bility of its training. In this paper, we propose a novel weight normalization tech-
nique called spectral normalization to stabilize the training of the discriminator.
Our new normalization technique is computationally light and easy to incorporate
into existing implementations. We tested the efﬁcacy of spectral normalization on
CIFAR10, STL-10, and ILSVRC2012 dataset, and we experimentally conﬁrmed
that spectrally normalized GANs (SN-GANs) is capable of generating images of
better or equal quality relative to the previous training stabilization techniques.
The code with Chainer (Tokui et al., 2015), generated images and pretrained mod-
els are available at https://github.com/pfnet-research/sngan_
projection.
1
INTRODUCTION
Generative adversarial networks (GANs) (Goodfellow et al., 2014) have been enjoying considerable
success as a framework of generative models in recent years, and it has been applied to numerous
types of tasks and datasets (Radford et al., 2016; Salimans et al., 2016; Ho & Ermon, 2016; Li et al.,
2017). In a nutshell, GANs are a framework to produce a model distribution that mimics a given
target distribution, and it consists of a generator that produces the model distribution and a discrimi-
nator that distinguishes the model distribution from the target. The concept is to consecutively train
the model distribution and the discriminator in turn, with the goal of reducing the difference be-
tween the model distribution and the target distribution measured by the best discriminator possible
at each step of the training. GANs have been drawing attention in the machine learning community
not only for its ability to learn highly structured probability distribution but also for its theoretically
interesting aspects. For example, (Nowozin et al., 2016; Uehara et al., 2016; Mohamed & Laksh-
minarayanan, 2017) revealed that the training of the discriminator amounts to the training of a good
estimator for the density ratio between the model distribution and the target. This is a perspective
that opens the door to the methods of implicit models (Mohamed & Lakshminarayanan, 2017; Tran
et al., 2017) that can be used to carry out variational optimization without the direct knowledge of
the density function.
A persisting challenge in the training of GANs is the performance control of the discriminator. In
high dimensional spaces, the density ratio estimation by the discriminator is often inaccurate and
unstable during the training, and generator networks fail to learn the multimodal structure of the
target distribution. Even worse, when the support of the model distribution and the support of the
target distribution are disjoint, there exists a discriminator that can perfectly distinguish the model
distribution from the target (Arjovsky & Bottou, 2017). Once such discriminator is produced in
this situation, the training of the generator comes to complete stop, because the derivative of the
so-produced discriminator with respect to the input turns out to be 0. This motivates us to introduce
some form of restriction to the choice of the discriminator.
In this paper, we propose a novel weight normalization method called spectral normalization that
can stabilize the training of discriminator networks. Our normalization enjoys following favorable
properties.
1
arXiv:1802.05957v1  [cs.LG]  16 Feb 2018


---

Published as a conference paper at ICLR 2018
• Lipschitz constant is the only hyper-parameter to be tuned, and the algorithm does not
require intensive tuning of the only hyper-parameter for satisfactory performance.
• Implementation is simple and the additional computational cost is small.
In fact, our normalization method also functioned well even without tuning Lipschitz constant,
which is the only hyper parameter. In this study, we provide explanations of the effectiveness of
spectral normalization for GANs against other regularization techniques, such as weight normaliza-
tion (Salimans & Kingma, 2016), weight clipping (Arjovsky et al., 2017), and gradient penalty (Gul-
rajani et al., 2017). We also show that, in the absence of complimentary regularization techniques
(e.g., batch normalization, weight decay and feature matching on the discriminator), spectral nor-
malization can improve the sheer quality of the generated images better than weight normalization
and gradient penalty.
2
METHOD
In this section, we will lay the theoretical groundwork for our proposed method. Let us consider a
simple discriminator made of a neural network of the following form, with the input x:
f(x, θ) = W L+1aL(W L(aL−1(W L−1(. . . a1(W 1x) . . . )))),
(1)
where θ := {W 1, . . . , W L, W L+1} is the learning parameters set, W l ∈Rdl×dl−1, W L+1 ∈
R1×dL, and al is an element-wise non-linear activation function. We omit the bias term of each
layer for simplicity. The ﬁnal output of the discriminator is given by
D(x, θ) = A(f(x, θ)),
(2)
where A is an activation function corresponding to the divergence of distance measure of the user’s
choice. The standard formulation of GANs is given by
min
G max
D V (G, D)
where min and max of G and D are taken over the set of generator and discriminator func-
tions, respectively.
The conventional form of V (G, D) (Goodfellow et al., 2014) is given by
Ex∼qdata[log D(x)] + Ex′∼pG[log(1 −D(x′))], where qdata is the data distribution and pG is the
(model) generator distribution to be learned through the adversarial min-max optimization. The ac-
tivation function A that is used in the D of this expression is some continuous function with range
[0, 1] (e.g, sigmoid function). It is known that, for a ﬁxed generator G, the optimal discriminator for
this form of V (G, D) is given by D∗
G(x) := qdata(x)/(qdata(x) + pG(x)).
The machine learning community has been pointing out recently that the function space from which
the discriminators are selected crucially affects the performance of GANs. A number of works (Ue-
hara et al., 2016; Qi, 2017; Gulrajani et al., 2017) advocate the importance of Lipschitz continuity
in assuring the boundedness of statistics. For example, the optimal discriminator of GANs on the
above standard formulation takes the form
D∗
G(x) =
qdata(x)
qdata(x) + pG(x) = sigmoid(f ∗(x)), where f ∗(x) = log qdata(x) −log pG(x), (3)
and its derivative
∇xf ∗(x) =
1
qdata(x)∇xqdata(x) −
1
pG(x)∇xpG(x)
(4)
can be unbounded or even incomputable. This prompts us to introduce some regularity condition to
the derivative of f(x).
A particularly successful works in this array are (Qi, 2017; Arjovsky et al., 2017; Gulrajani et al.,
2017), which proposed methods to control the Lipschitz constant of the discriminator by adding
regularization terms deﬁned on input examples x. We would follow their footsteps and search for
the discriminator D from the set of K-Lipschitz continuous functions, that is,
arg max
∥f∥Lip≤K
V (G, D),
(5)
2


---

Published as a conference paper at ICLR 2018
where we mean by ∥f∥Lip the smallest value M such that ∥f(x) −f(x′)∥/∥x −x′∥≤M for any
x, x′, with the norm being the ℓ2 norm.
While input based regularizations allow for relatively easy formulations based on samples, they also
suffer from the fact that, they cannot impose regularization on the space outside of the supports of
the generator and data distributions without introducing somewhat heuristic means. A method we
would introduce in this paper, called spectral normalization, is a method that aims to skirt this issue
by normalizing the weight matrices using the technique devised by Yoshida & Miyato (2017).
2.1
SPECTRAL NORMALIZATION
Our spectral normalization controls the Lipschitz constant of the discriminator function f by literally
constraining the spectral norm of each layer g : hin 7→hout. By deﬁnition, Lipschitz norm ∥g∥Lip
is equal to suph σ(∇g(h)), where σ(A) is the spectral norm of the matrix A (L2 matrix norm of A)
σ(A) := max
h:h̸=0
∥Ah∥2
∥h∥2
= max
∥h∥2≤1 ∥Ah∥2,
(6)
which is equivalent to the largest singular value of A. Therefore, for a linear layer g(h) = Wh, the
norm is given by ∥g∥Lip = suph σ(∇g(h)) = suph σ(W) = σ(W). If the Lipschitz norm of the
activation function ∥al∥Lip is equal to 1 1, we can use the inequality ∥g1◦g2∥Lip ≤∥g1∥Lip·∥g2∥Lip
to observe the following bound on ∥f∥Lip:
∥f∥Lip ≤∥(hL 7→W L+1hL)∥Lip · ∥aL∥Lip · ∥(hL−1 7→W LhL−1)∥Lip
· · · ∥a1∥Lip · ∥(h0 7→W 1h0)∥Lip =
L+1
Y
l=1
∥(hl−1 7→W lhl−1)∥Lip =
L+1
Y
l=1
σ(W l).
(7)
Our spectral normalization normalizes the spectral norm of the weight matrix W so that it satisﬁes
the Lipschitz constraint σ(W) = 1:
¯WSN(W) := W/σ(W).
(8)
If we normalize each W l using (8), we can appeal to the inequality (7) and the fact that
σ
  ¯WSN(W)

= 1 to see that ∥f∥Lip is bounded from above by 1.
Here, we would like to emphasize the difference between our spectral normalization and spectral
norm ”regularization” introduced by Yoshida & Miyato (2017). Unlike our method, spectral norm
”regularization” penalizes the spectral norm by adding explicit regularization term to the objective
function. Their method is fundamentally different from our method in that they do not make an
attempt to ‘set’ the spectral norm to a designated value. Moreover, when we reorganize the derivative
of our normalized cost function and rewrite our objective function (12), we see that our method
is augmenting the cost function with a sample data dependent regularization function. Spectral
norm regularization, on the other hand, imposes sample data independent regularization on the cost
function, just like L2 regularization and Lasso.
2.2
FAST APPROXIMATION OF THE SPECTRAL NORM σ(W)
As we mentioned above, the spectral norm σ(W) that we use to regularize each layer of the dis-
criminator is the largest singular value of W. If we naively apply singular value decomposition
to compute the σ(W) at each round of the algorithm, the algorithm can become computationally
heavy. Instead, we can use the power iteration method to estimate σ(W) (Golub & Van der Vorst,
2000; Yoshida & Miyato, 2017). With power iteration method, we can estimate the spectral norm
with very small additional computational time relative to the full computational cost of the vanilla
GANs. Please see Appendix A for the detail method and Algorithm 1 for the summary of the actual
spectral normalization algorithm.
1For examples, ReLU (Jarrett et al., 2009; Nair & Hinton, 2010; Glorot et al., 2011) and leaky ReLU (Maas
et al., 2013) satisﬁes the condition, and many popular activation functions satisfy K-Lipschitz constraint for
some predeﬁned K as well.
3


---

Published as a conference paper at ICLR 2018
2.3
GRADIENT ANALYSIS OF THE SPECTRALLY NORMALIZED WEIGHTS
The gradient2 of ¯WSN(W) with respect to Wij is:
∂¯WSN(W)
∂Wij
=
1
σ(W)Eij −
1
σ(W)2
∂σ(W)
∂Wij
W =
1
σ(W)Eij −[u1vT
1 ]ij
σ(W)2 W
(9)
=
1
σ(W)
 Eij −[u1vT
1 ]ij ¯WSN

,
(10)
where Eij is the matrix whose (i, j)-th entry is 1 and zero everywhere else, and u1 and v1 are
respectively the ﬁrst left and right singular vectors of W. If h is the hidden layer in the network to
be transformed by ¯WSN, the derivative of the V (G, D) calculated over the mini-batch with respect
to W of the discriminator D is given by:
∂V (G, D)
∂W
=
1
σ(W)
 ˆE

δhT
−
 ˆE

δT ¯WSNh

u1vT
1

(11)
=
1
σ(W)
 ˆE

δhT
−λu1vT
1

(12)
where δ :=
 ∂V (G, D)/∂
  ¯WSNh
T, λ := ˆE

δT   ¯WSNh

, and ˆE[·] represents empirical expec-
tation over the mini-batch. ∂V
∂W = 0 when ˆE[δhT] = ku1vT
1 for some k ∈R.
We would like to comment on the implication of (12). The ﬁrst term ˆE

δhT
is the same as the
derivative of the weights without normalization. In this light, the second term in the expression
can be seen as the regularization term penalizing the ﬁrst singular components with the adaptive
regularization coefﬁcient λ. λ is positive when δ and ¯WSNh are pointing in similar direction, and
this prevents the column space of W from concentrating into one particular direction in the course
of the training. In other words, spectral normalization prevents the transformation of each layer
from becoming to sensitive in one direction. We can also use spectral normalization to devise a
new parametrization for the model. Namely, we can split the layer map into two separate train-
able components: spectrally normalized map and the spectral norm constant. As it turns out, this
parametrization has its merit on its own and promotes the performance of GANs (See Appendix E).
3
SPECTRAL NORMALIZATION VS OTHER REGULARIZATION TECHNIQUES
The weight normalization introduced by Salimans & Kingma (2016) is a method that normalizes the
ℓ2 norm of each row vector in the weight matrix. Mathematically, this is equivalent to requiring the
weight by the weight normalization ¯WWN:
σ1( ¯WWN)2 + σ2( ¯WWN)2 + · · · + σT ( ¯WWN)2 = do, where T = min(di, do),
(13)
where σt(A) is a t-th singular value of matrix A. Therefore, up to a scaler, this is same as the
Frobenius normalization, which requires the sum of the squared singular values to be 1. These
normalizations, however, inadvertently impose much stronger constraint on the matrix than intended.
If ¯WWN is the weight normalized matrix of dimension di × do, the norm ∥¯WWNh∥2 for a ﬁxed unit
vector h is maximized at ∥¯WWNh∥2 = √do when σ1( ¯WWN) = √do and σt( ¯WWN) = 0 for
t = 2, . . . , T, which means that ¯WWN is of rank one. Similar thing can be said to the Frobenius
normalization (See the appendix for more details). Using such ¯WWN corresponds to using only one
feature to discriminate the model probability distribution from the target. In order to retain as much
norm of the input as possible and hence to make the discriminator more sensitive, one would hope
to make the norm of ¯WWNh large. For weight normalization, however, this comes at the cost of
reducing the rank and hence the number of features to be used for the discriminator. Thus, there is a
conﬂict of interests between weight normalization and our desire to use as many features as possible
to distinguish the generator distribution from the target distribution. The former interest often reigns
over the other in many cases, inadvertently diminishing the number of features to be used by the
discriminators. Consequently, the algorithm would produce a rather arbitrary model distribution
2Indeed, when the spectrum has multiplicities, we would be looking at subgradients here. However, the
probability of this happening is zero (almost surely), so we would continue discussions without giving consid-
erations to such events.
4


---

Published as a conference paper at ICLR 2018
that matches the target distribution only at select few features. Weight clipping (Arjovsky et al.,
2017) also suffers from same pitfall.
Our spectral normalization, on the other hand, do not suffer from such a conﬂict in interest. Note
that the Lipschitz constant of a linear operator is determined only by the maximum singular value.
In other words, the spectral norm is independent of rank. Thus, unlike the weight normalization,
our spectral normalization allows the parameter matrix to use as many features as possible while
satisfying local 1-Lipschitz constraint. Our spectral normalization leaves more freedom in choosing
the number of singular components (features) to feed to the next layer of the discriminator.
Brock et al. (2016) introduced orthonormal regularization on each weight to stabilize the training of
GANs. In their work, Brock et al. (2016) augmented the adversarial objective function by adding
the following term:
∥W TW −I∥2
F .
(14)
While this seems to serve the same purpose as spectral normalization, orthonormal regularization
are mathematically quite different from our spectral normalization because the orthonormal regular-
ization destroys the information about the spectrum by setting all the singular values to one. On the
other hand, spectral normalization only scales the spectrum so that the its maximum will be one.
Gulrajani et al. (2017) used Gradient penalty method in combination with WGAN. In their work,
they placed K-Lipschitz constant on the discriminator by augmenting the objective function with
the regularizer that rewards the function for having local 1-Lipschitz constant (i.e. ∥∇ˆxf∥2 = 1)
at discrete sets of points of the form ˆx := ϵ˜x + (1 −ϵ)x generated by interpolating a sample ˜x
from generative distribution and a sample x from the data distribution. While this rather straight-
forward approach does not suffer from the problems we mentioned above regarding the effective
dimension of the feature space, the approach has an obvious weakness of being heavily dependent
on the support of the current generative distribution. As a matter of course, the generative distribu-
tion and its support gradually changes in the course of the training, and this can destabilize the effect
of such regularization. In fact, we empirically observed that a high learning rate can destabilize the
performance of WGAN-GP. On the contrary, our spectral normalization regularizes the function the
operator space, and the effect of the regularization is more stable with respect to the choice of the
batch. Training with our spectral normalization does not easily destabilize with aggressive learning
rate. Moreover, WGAN-GP requires more computational cost than our spectral normalization with
single-step power iteration, because the computation of ∥∇ˆxf∥2 requires one whole round of for-
ward and backward propagation. In the appendix section, we compare the computational cost of the
two methods for the same number of updates.
4
EXPERIMENTS
In order to evaluate the efﬁcacy of our approach and investigate the reason behind its efﬁcacy, we
conducted a set of extensive experiments of unsupervised image generation on CIFAR-10 (Torralba
et al., 2008) and STL-10 (Coates et al., 2011), and compared our method against other normalization
techniques. To see how our method fares against large dataset, we also applied our method on
ILSVRC2012 dataset (ImageNet) (Russakovsky et al., 2015) as well. This section is structured as
follows. First, we will discuss the objective functions we used to train the architecture, and then
we will describe the optimization settings we used in the experiments. We will then explain two
performance measures on the images to evaluate the images produced by the trained generators.
Finally, we will summarize our results on CIFAR-10, STL-10, and ImageNet.
As for the architecture of the discriminator and generator, we used convolutional neural networks.
Also, for the evaluation of the spectral norm for the convolutional weight W ∈Rdout×din×h×w, we
treated the operator as a 2-D matrix of dimension dout ×(dinhw)3. We trained the parameters of the
generator with batch normalization (Ioffe & Szegedy, 2015). We refer the readers to Table 3 in the
appendix section for more details of the architectures.
3Note that, since we are conducting the convolution discretely, the spectral norm will depend on the size of
the stride and padding. However, the answer will only differ by some predeﬁned K.
5


---

Published as a conference paper at ICLR 2018
For all methods other than WGAN-GP, we used the following standard objective function for the
adversarial loss:
V (G, D) :=
E
x∼qdata(x)[log D(x)] +
E
z∼p(z)[log(1 −D(G(z)))],
(15)
where z ∈Rdz is a latent variable, p(z) is the standard normal distribution N(0, I), and G : Rdz →
Rd0 is a deterministic generator function. We set dz to 128 for all of our experiments. For the updates
of G, we used the alternate cost proposed by Goodfellow et al. (2014) −Ez∼p(z)[log(D(G(z)))] as
used in Goodfellow et al. (2014) and Warde-Farley & Bengio (2017). For the updates of D, we used
the original cost deﬁned in (15). We also tested the performance of the algorithm with the so-called
hinge loss, which is given by
VD( ˆG, D) =
E
x∼qdata(x) [min (0, −1 + D(x))] +
E
z∼p(z)
h
min

0, −1 −D

ˆG(z)
i
(16)
VG(G, ˆD) = −
E
z∼p(z)
h
ˆD (G(z))
i
,
(17)
respectively for the discriminator and the generator. Optimizing these objectives is equivalent to
minimizing the so-called reverse KL divergence : KL[pg||qdata]. This type of loss has been already
proposed and used in Lim & Ye (2017); Tran et al. (2017). The algorithm based on the hinge
loss also showed good performance when evaluated with inception score and FID. For Wasserstein
GANs with gradient penalty (WGAN-GP) (Gulrajani et al., 2017), we used the following objective
function: V (G, D) := Ex∼qdata[D(x)]−Ez∼p(z)[D(G(z))]−λ Eˆx∼pˆ
x[(∥∇ˆxD(ˆx)∥2−1)2], where
the regularization term is the one we introduced in the appendix section D.4.
For quantitative assessment of generated examples, we used inception score (Salimans et al., 2016)
and Fr´echet inception distance (FID) (Heusel et al., 2017). Please see Appendix B.1 for the details
of each score.
4.1
RESULTS ON CIFAR10 AND STL-10
In this section, we report the accuracy of the spectral normalization (we use the abbreviation: SN-
GAN for the spectrally normalized GANs) during the training, and the dependence of the algo-
rithm’s performance on the hyperparmeters of the optimizer. We also compare the performance
quality of the algorithm against those of other regularization/normalization techniques for the dis-
criminator networks, including: Weight clipping (Arjovsky et al., 2017), WGAN-GP (Gulrajani
et al., 2017), batch-normalization (BN) (Ioffe & Szegedy, 2015), layer normalization (LN) (Ba et al.,
2016), weight normalization (WN) (Salimans & Kingma, 2016) and orthonormal regularization (or-
thonormal) (Brock et al., 2016). In order to evaluate the stand-alone efﬁcacy of the gradient penalty,
we also applied the gradient penalty term to the standard adversarial loss of GANs (15). We would
refer to this method as ‘GAN-GP’. For weight clipping, we followed the original work Arjovsky
et al. (2017) and set the clipping constant c at 0.01 for the convolutional weight of each layer. For
gradient penalty, we set λ to 10, as suggested in Gulrajani et al. (2017). For orthonormal, we initial-
ized the each weight of D with a randomly selected orthonormal operator and trained GANs with
the objective function augmented with the regularization term used in Brock et al. (2016). For all
comparative studies throughout, we excluded the multiplier parameter γ in the weight normalization
method, as well as in batch normalization and layer normalization method. This was done in order
to prevent the methods from overtly violating the Lipschitz condition. When we experimented with
different multiplier parameter, we were in fact not able to achieve any improvement.
For optimization, we used the Adam optimizer Kingma & Ba (2015) in all of our experiments. We
tested with 6 settings for (1) ndis, the number of updates of the discriminator per one update of
the generator and (2) learning rate α and the ﬁrst and second order momentum parameters (β1, β2)
of Adam. We list the details of these settings in Table 1 in the appendix section. Out of these 6
settings, A, B, and C are the settings used in previous representative works. The purpose of the
settings D, E, and F is to the evaluate the performance of the algorithms implemented with more
aggressive learning rates. For the details of the architectures of convolutional networks deployed
in the generator and the discriminator, we refer the readers to Table 3 in the appendix section. The
number of updates for GAN generator were 100K for all experiments, unless otherwise noted.
Firstly, we inspected the spectral norm of each layer during the training to make sure that our spectral
normalization procedure is indeed serving its purpose. As we can see in the Figure 9 in the C.1,
6


---

Published as a conference paper at ICLR 2018
Table 1: Hyper-parameter settings we tested in our experiments. †, ‡ and ⋆are the hyperparameter
settings following Gulrajani et al. (2017), Warde-Farley & Bengio (2017) and Radford et al. (2016),
respectively.
Setting
α
β1
β2
ndis
A†
0.0001
0.5
0.9
5
B‡
0.0001
0.5
0.999
1
C⋆
0.0002
0.5
0.999
1
D
0.001
0.5
0.9
5
E
0.001
0.5
0.999
5
F
0.001
0.9
0.999
5
Weight clip.
GAN-GP
WGAN-GP
BN
LN
WN
Orthonormal
SN
0
1
2
3
4
5
6
7
8
Inception score
A
B
C
D
E
F
(a) CIFAR-10
Weight clip.
WGAN-GP
LN
WN
Orthonormal
SN
0
1
2
3
4
5
6
7
8
9
Inception score
A
B
C
D
E
F
(b) STL-10
Figure 1: Inception scores on CIFAR-10 and STL-10 with different methods and hyperparameters
(higher is better).
the spectral norms of these layers ﬂoats around 1–1.05 region throughout the training. Please see
Appendix C.1 for more details.
In Figures 1 and 2 we show the inception scores of each method with the settings A–F. We can see
that spectral normalization is relatively robust with aggressive learning rates and momentum param-
eters. WGAN-GP fails to train good GANs at high learning rates and high momentum parameters
on both CIFAR-10 and STL-10. Orthonormal regularization performed poorly for the setting E on
the STL-10, but performed slightly better than our method with the optimal setting. These results
suggests that our method is more robust than other methods with respect to the change in the set-
ting of the training. Also, the optimal performance of weight normalization was inferior to both
WGAN-GP and spectral normalization on STL-10, which consists of more diverse examples than
CIFAR-10. Best scores of spectral normalization are better than almost all other methods on both
CIFAR-10 and STL-10.
In Tables 2, we show the inception scores of the different methods with optimal settings on CIFAR-
10 and STL-10 dataset. We see that SN-GANs performed better than almost all contemporaries
on the optimal settings. SN-GANs performed even better with hinge loss (17).4. For the training
with same number of iterations, SN-GANs fell behind orthonormal regularization for STL-10. For
more detailed comparison between orthonormal regularization and spectral normalization, please
see section 4.1.2.
In Figure 6 we show the images produced by the generators trained with WGAN-GP, weight nor-
malization, and spectral normalization. SN-GANs were consistently better than GANs with weight
normalization in terms of the quality of generated images. To be more precise, as we mentioned
in Section 3, the set of images generated by spectral normalization was clearer and more diverse
than the images produced by the weight normalization. We can also see that WGAN-GP failed to
train good GANs with high learning rates and high momentums (D,E and F). The generated images
4As for STL-10, we also ran SN-GANs over twice time longer iterations because it did not seem to converge.
Yet still, this elongated training sequence still completes before WGAN-GP with original iteration size because
the optimal setting of SN-GANs (setting B, ndis = 1) is computationally light.
7


---

Published as a conference paper at ICLR 2018
Weight clip.
GAN-GP
WGAN-GP
BN
LN
WN
Orthonormal
SN
10
2
FID
A
B
C
D
E
F
(a) CIFAR-10
Weight clip.
WGAN-GP
LN
WN
Orthonormal
SN
10
1
10
2
FID
A
B
C
D
E
F
(b) STL-10
Figure 2: FIDs on CIFAR-10 and STL-10 with different methods and hyperparameters (lower is
better).
Table 2: Inception scores and FIDs with unsupervised image generation on CIFAR-10. † (Radford
et al., 2016) (experimented by Yang et al. (2017)), ‡ (Yang et al., 2017), ∗(Warde-Farley & Bengio,
2017), †† (Gulrajani et al., 2017)
Method
Inception score
FID
CIFAR-10
STL-10
CIFAR-10
STL-10
Real data
11.24±.12
26.08±.26
7.8
7.9
-Standard CNN-
Weight clipping
6.41±.11
7.57±.10
42.6
64.2
GAN-GP
6.93±.08
37.7
WGAN-GP
6.68±.06
8.42±.13
40.2
55.1
Batch Norm.
6.27±.10
56.3
Layer Norm.
7.19±.12
7.61±.12
33.9
75.6
Weight Norm.
6.84±.07
7.16±.10
34.7
73.4
Orthonormal
7.40±.12
8.56±.07
29.0
46.7
(ours) SN-GANs
7.42±.08
8.28±.09
29.3
53.1
Orthonormal (2x updates)
8.67±.08
44.2
(ours) SN-GANs (2x updates)
8.69±.09
47.5
(ours) SN-GANs, Eq.(17)
7.58±.12
25.5
(ours) SN-GANs, Eq.(17) (2x updates)
8.79±.14
43.2
-ResNet-5
Orthonormal, Eq.(17)
7.92±.04
8.72±.06
23.8±.58
42.4±.99
(ours) SN-GANs, Eq.(17)
8.22±.05
9.10±.04
21.7±.21
40.1±.50
DCGAN†
6.64±.14
7.84±.07
LR-GANs‡
7.17±.07
Warde-Farley et al.∗
7.72±.13
8.51±.13
WGAN-GP (ResNet)††
7.86±.08
with GAN-GP, batch normalization, and layer normalization is shown in Figure 12 in the appendix
section.
We also compared our algorithm against multiple benchmark methods ans summarized the results
on the bottom half of the Table 2. We also tested the performance of our method on ResNet based
GANs used in Gulrajani et al. (2017). Please note that all methods listed thereof are all different
in both optimization methods and the architecture of the model. Please see Table 4 and 5 in the
appendix section for the detail network architectures. Our implementation of our algorithm was
able to perform better than almost all the predecessors in the performance.
5For our ResNet experiments, we trained the same architecture with multiple random seeds for weight
initialization and produced models with different parameters. We then generated 5000 images 10 times and
computed the average inception score for each model. The values for ResNet on the table are the mean and
standard deviation of the score computed over the set of models trained with different seeds.
8


---

Published as a conference paper at ICLR 2018
0
13
26
Index of 
0.0
0.2
0.4
0.6
0.8
1.0
2
Layer : 1
0
32
63
0
.
0
0
.
2
0
.
4
0
.
6
0
.
8
1
.
0
Layer : 2
0
64
127
0
.
0
0
.
2
0
.
4
0
.
6
0
.
8
1
.
0
Layer : 3
0
64
127
0
.
0
0
.
2
0
.
4
0
.
6
0
.
8
1
.
0
Layer : 4
0
128
255
0
.
0
0
.
2
0
.
4
0
.
6
0
.
8
1
.
0
Layer : 5
0
128
255
0
.
0
0
.
2
0
.
4
0
.
6
0
.
8
1
.
0
Layer : 6
0
256
511
0
.
0
0
.
2
0
.
4
0
.
6
0
.
8
1
.
0
Layer : 7
WC
WN
SN
(a) CIFAR-10
0
13
26
Index of 
0.0
0.2
0.4
0.6
0.8
1.0
2
Layer : 1
0
32
63
0
.
0
0
.
2
0
.
4
0
.
6
0
.
8
1
.
0
Layer : 2
0
64
127
0
.
0
0
.
2
0
.
4
0
.
6
0
.
8
1
.
0
Layer : 3
0
64
127
0
.
0
0
.
2
0
.
4
0
.
6
0
.
8
1
.
0
Layer : 4
0
128
255
0
.
0
0
.
2
0
.
4
0
.
6
0
.
8
1
.
0
Layer : 5
0
128
255
0
.
0
0
.
2
0
.
4
0
.
6
0
.
8
1
.
0
Layer : 6
0
256
511
0
.
0
0
.
2
0
.
4
0
.
6
0
.
8
1
.
0
Layer : 7
WC
WN
SN
(b) STL-10
Figure 3: Squared singular values of weight matrices trained with different methods: Weight clip-
ping (WC), Weight Normalization (WN) and Spectral Normalization (SN). We scaled the singular
values so that the largest singular values is equal to 1. For WN and SN, we calculated singular values
of the normalized weight matrices.
4.1.1
ANALYSIS OF SN-GANS
Singular values analysis on the weights of the discriminator D
In Figure 3, we show the
squared singular values of the weight matrices in the ﬁnal discriminator D produced by each method
using the parameter that yielded the best inception score. As we predicted in Section 3, the singular
values of the ﬁrst to ﬁfth layers trained with weight clipping and weight normalization concentrate
on a few components. That is, the weight matrices of these layers tend to be rank deﬁcit. On the
other hand, the singular values of the weight matrices in those layers trained with spectral normal-
ization is more broadly distributed. When the goal is to distinguish a pair of probability distributions
on the low-dimensional nonlinear data manifold embedded in a high dimensional space, rank deﬁ-
ciencies in lower layers can be especially fatal. Outputs of lower layers have gone through only a
few sets of rectiﬁed linear transformations, which means that they tend to lie on the space that is
linear in most parts. Marginalizing out many features of the input distribution in such space can
result in oversimpliﬁed discriminator. We can actually conﬁrm the effect of this phenomenon on the
generated images especially in Figure 6b. The images generated with spectral normalization is more
diverse and complex than those generated with weight normalization.
Training time
On CIFAR-10, SN-GANs is slightly slower than weight normalization (about 110
∼120% computational time), but signiﬁcantly faster than WGAN-GP. As we mentioned in Sec-
tion 3, WGAN-GP is slower than other methods because WGAN-GP needs to calculate the gradient
of gradient norm ∥∇xD∥2. For STL-10, the computational time of SN-GANs is almost the same as
vanilla GANs, because the relative computational cost of the power iteration (18) is negligible when
compared to the cost of forward and backward propagation on CIFAR-10 (images size of STL-10 is
larger (48 × 48)). Please see Figure 10 in the appendix section for the actual computational time.
4.1.2
COMPARISON BETWEEN SN-GANS AND ORTHONORMAL REGULARIZATION
In order to highlight the difference between our spectral normalization and orthonormal regulariza-
tion, we conducted an additional set of experiments. As we explained in Section 3, orthonormal
regularization is different from our method in that it destroys the spectral information and puts equal
emphasis on all feature dimensions, including the ones that ’shall’ be weeded out in the training
process. To see the extent of its possibly detrimental effect, we experimented by increasing the di-
9


---

Published as a conference paper at ICLR 2018
0.51.0
2.0
4.0
6.0
8.0
Relative size of feature map dimension (original=1.0)
7.9
8.0
8.1
8.2
8.3
8.4
8.5
8.6
Inception score
SN-GANs
Orthonormal
Figure 4:
The effect on the performance on STL-10 induced by the change of the feature map
dimension of the ﬁnal layer. The width of the highlighted region represents standard deviation of the
results over multiple seeds of weight initialization. The orthonormal regularization does not perform
well with large feature map dimension, possibly because of its design that forces the discriminator
to use all dimensions including the ones that are unnecessary. For the setting of the optimizers’
hyper-parameters, We used the setting C, which was optimal for “orthonormal regularization”
0.0
1.0
2.0
3.0
4.04.5
iteration
1e5
10
12
14
16
18
20
22
inception score
SN-GANs
Orthnormal
Figure 5:
Learning curves for conditional image generation in terms of Inception score for SN-
GANs and GANs with orthonormal regularization on ImageNet.
mension of the feature space 6, especially at the ﬁnal layer (7th conv) for which the training with our
spectral normalization prefers relatively small feature space (dimension < 100; see Figure 3b). As
for the setting of the training, we selected the parameters for which the orthonormal regularization
performed optimally. The ﬁgure 4 shows the result of our experiments. As we predicted, the per-
formance of the orthonormal regularization deteriorates as we increase the dimension of the feature
maps at the ﬁnal layer. Our SN-GANs, on the other hand, does not falter with this modiﬁcation of
the architecture. Thus, at least in this perspective, we may such that our method is more robust with
respect to the change of the network architecture.
4.2
IMAGE GENERATION ON IMAGENET
To show that our method remains effective on a large high dimensional dataset, we also applied
our method to the training of conditional GANs on ILRSVRC2012 dataset with 1000 classes, each
consisting of approximately 1300 images, which we compressed to 128×128 pixels. Regarding the
adversarial loss for conditional GANs, we used practically the same formulation used in Mirza &
Osindero (2014), except that we replaced the standard GANs loss with hinge loss (17). Please see
Appendix B.3 for the details of experimental settings.
6More precisely, we simply increased the input dimension and the output dimension by the same factor. In
Figure 4, ‘relative size’ = 1.0 implies that the layer structure is the same as the original.
10


---

Published as a conference paper at ICLR 2018
GANs without normalization and GANs with layer normalization collapsed in the beginning of
training and failed to produce any meaningful images. GANs with orthonormal normalization Brock
et al. (2016) and our spectral normalization, on the other hand, was able to produce images. The
inception score of the orthonormal normalization however plateaued around 20Kth iterations, while
SN kept improving even afterward (Figure 5.) To our knowledge, our research is the ﬁrst of its kind
in succeeding to produce decent images from ImageNet dataset with a single pair of a discrimina-
tor and a generator (Figure 7). To measure the degree of mode-collapse, we followed the footstep
of Odena et al. (2017) and computed the intra MS-SSIM Odena et al. (2017) for pairs of indepen-
dently generated GANs images of each class. We see that our SN-GANs ((intra MS-SSIM)=0.101)
is suffering less from the mode-collapse than AC-GANs ((intra MS-SSIM)∼0.25).
To ensure that the superiority of our method is not limited within our speciﬁc setting, we also com-
pared the performance of SN-GANs against orthonormal regularization on conditional GANs with
projection discriminator (Miyato & Koyama, 2018) as well as the standard (unconditional) GANs.
In our experiments, SN-GANs achieved better performance than orthonormal regularization for the
both settings (See Figure 13 in the appendix section).
5
CONCLUSION
This paper proposes spectral normalization as a stabilizer of training of GANs. When we apply spec-
tral normalization to the GANs on image generation tasks, the generated examples are more diverse
than the conventional weight normalization and achieve better or comparative inception scores rela-
tive to previous studies. The method imposes global regularization on the discriminator as opposed
to local regularization introduced by WGAN-GP, and can possibly used in combinations. In the
future work, we would like to further investigate where our methods stand amongst other methods
on more theoretical basis, and experiment our algorithm on larger and more complex datasets.
ACKNOWLEDGMENTS
We would like to thank the members of Preferred Networks, Inc., particularly Shin-ichi Maeda,
Eiichi Matsumoto, Masaki Watanabe and Keisuke Yahata for insightful comments and discussions.
We also would like to thank anonymous reviewers and commenters on the OpenReview forum for
insightful discussions.
REFERENCES
Martin Arjovsky and L´eon Bottou. Towards principled methods for training generative adversarial networks.
In ICLR, 2017.
Martin Arjovsky, Soumith Chintala, and L´eon Bottou. Wasserstein generative adversarial networks. In ICML,
pp. 214–223, 2017.
Devansh Arpit, Yingbo Zhou, Bhargava U Kota, and Venu Govindaraju. Normalization propagation: A para-
metric technique for removing internal covariate shift in deep networks. In ICML, pp. 1168–1176, 2016.
Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton.
Layer normalization.
arXiv preprint
arXiv:1607.06450, 2016.
Andrew Brock, Theodore Lim, James M Ritchie, and Nick Weston. Neural photo editing with introspective
adversarial networks. arXiv preprint arXiv:1609.07093, 2016.
Adam Coates, Andrew Ng, and Honglak Lee. An analysis of single-layer networks in unsupervised feature
learning. In AISTATS, pp. 215–223, 2011.
Harm de Vries, Florian Strub, J´er´emie Mary, Hugo Larochelle, Olivier Pietquin, and Aaron C Courville. Mod-
ulating early visual processing by language. In NIPS, pp. 6576–6586, 2017.
DC Dowson and BV Landau. The fr´echet distance between multivariate normal distributions. Journal of
Multivariate Analysis, 12(3):450–455, 1982.
Vincent Dumoulin, Jonathon Shlens, and Manjunath Kudlur. A learned representation for artistic style. In
ICLR, 2017.
Xavier Glorot, Antoine Bordes, and Yoshua Bengio. Deep sparse rectiﬁer neural networks. In AISTATS, pp.
315–323, 2011.
Gene H Golub and Henk A Van der Vorst. Eigenvalue computation in the 20th century. Journal of Computa-
tional and Applied Mathematics, 123(1):35–65, 2000.
Ian Goodfellow, Jean Pouget-Abadie, Mehdi Mirza, Bing Xu, David Warde-Farley, Sherjil Ozair, Aaron
Courville, and Yoshua Bengio. Generative adversarial nets. In NIPS, pp. 2672–2680, 2014.
11


---

Published as a conference paper at ICLR 2018
Ishaan Gulrajani, Faruk Ahmed, Martin Arjovsky, Vincent Dumoulin, and Aaron Courville. Improved training
of wasserstein GANs. arXiv preprint arXiv:1704.00028, 2017.
Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition. In
CVPR, pp. 770–778, 2016.
Martin Heusel, Hubert Ramsauer, Thomas Unterthiner, Bernhard Nessler, G¨unter Klambauer, and Sepp
Hochreiter. GANs trained by a two time-scale update rule converge to a nash equilibrium. arXiv preprint
arXiv:1706.08500, 2017.
Jonathan Ho and Stefano Ermon. Generative adversarial imitation learning. In NIPS, pp. 4565–4573, 2016.
Sergey Ioffe and Christian Szegedy. Batch normalization: Accelerating deep network training by reducing
internal covariate shift. In ICML, pp. 448–456, 2015.
Kevin Jarrett, Koray Kavukcuoglu, Marc’Aurelio Ranzato, and Yann LeCun. What is the best multi-stage
architecture for object recognition? In ICCV, pp. 2146–2153, 2009.
Kui Jia, Dacheng Tao, Shenghua Gao, and Xiangmin Xu. Improving training of deep neural networks via
singular value bounding. In CVPR, 2017.
Diederik Kingma and Jimmy Ba. Adam: A method for stochastic optimization. In ICLR, 2015.
Jiwei Li, Will Monroe, Tianlin Shi, Alan Ritter, and Dan Jurafsky. Adversarial learning for neural dialogue
generation. In EMNLP, pp. 2147–2159, 2017.
Jae Hyun Lim and Jong Chul Ye. Geometric GAN. arXiv preprint arXiv:1705.02894, 2017.
Andrew L Maas, Awni Y Hannun, and Andrew Y Ng. Rectiﬁer nonlinearities improve neural network acoustic
models. In ICML Workshop on Deep Learning for Audio, Speech and Language Processing, 2013.
Mehdi Mirza and Simon Osindero. Conditional generative adversarial nets. arXiv preprint arXiv:1411.1784,
2014.
Takeru Miyato and Masanori Koyama. cGANs with projection discriminator. In ICLR, 2018.
Shakir Mohamed and Balaji Lakshminarayanan. Learning in implicit generative models. NIPS Workshop on
Adversarial Training, 2017.
Vinod Nair and Geoffrey E Hinton. Rectiﬁed linear units improve restricted boltzmann machines. In ICML,
pp. 807–814, 2010.
Sebastian Nowozin, Botond Cseke, and Ryota Tomioka. f-GAN: Training generative neural samplers using
variational divergence minimization. In NIPS, pp. 271–279, 2016.
Augustus Odena, Christopher Olah, and Jonathon Shlens. Conditional image synthesis with auxiliary classiﬁer
GANs. In ICML, pp. 2642–2651, 2017.
Guo-Jun Qi.
Loss-sensitive generative adversarial networks on lipschitz densities.
arXiv preprint
arXiv:1701.06264, 2017.
Alec Radford, Luke Metz, and Soumith Chintala. Unsupervised representation learning with deep convolutional
generative adversarial networks. In ICLR, 2016.
Olga Russakovsky, Jia Deng, Hao Su, Jonathan Krause, Sanjeev Satheesh, Sean Ma, Zhiheng Huang, Andrej
Karpathy, Aditya Khosla, Michael Bernstein, Alexander C. Berg, and Li Fei-Fei. Imagenet large scale visual
recognition challenge. International Journal of Computer Vision, 115(3):211–252, 2015.
Masaki Saito, Eiichi Matsumoto, and Shunta Saito. Temporal generative adversarial nets with singular value
clipping. In ICCV, 2017.
Tim Salimans and Diederik P Kingma. Weight normalization: A simple reparameterization to accelerate train-
ing of deep neural networks. In NIPS, pp. 901–909, 2016.
Tim Salimans, Ian Goodfellow, Wojciech Zaremba, Vicki Cheung, Alec Radford, and Xi Chen. Improved
techniques for training GANs. In NIPS, pp. 2226–2234, 2016.
Christian Szegedy, Wei Liu, Yangqing Jia, Pierre Sermanet, Scott Reed, Dragomir Anguelov, Dumitru Erhan,
Vincent Vanhoucke, and Andrew Rabinovich. Going deeper with convolutions. In CVPR, pp. 1–9, 2015.
Seiya Tokui, Kenta Oono, Shohei Hido, and Justin Clayton. Chainer: a next-generation open source framework
for deep learning. In Proceedings of workshop on machine learning systems (LearningSys) in the twenty-
ninth annual conference on neural information processing systems (NIPS), 2015.
Antonio Torralba, Rob Fergus, and William T Freeman. 80 million tiny images: A large data set for nonpara-
metric object and scene recognition. IEEE Transactions on Pattern Analysis and Machine Intelligence, 30
(11):1958–1970, 2008.
Dustin Tran, Rajesh Ranganath, and David M Blei. Deep and hierarchical implicit models. arXiv preprint
arXiv:1702.08896, 2017.
Masatoshi Uehara, Issei Sato, Masahiro Suzuki, Kotaro Nakayama, and Yutaka Matsuo. Generative adversarial
nets from a density ratio estimation perspective. NIPS Workshop on Adversarial Training, 2016.
David Warde-Farley and Yoshua Bengio. Improving generative adversarial networks with denoising feature
matching. In ICLR, 2017.
Sitao Xiang and Hao Li. On the effect of batch normalization and weight normalization in generative adversarial
networks. arXiv preprint arXiv:1704.03971, 2017.
Jianwei Yang, Anitha Kannan, Dhruv Batra, and Devi Parikh. LR-GAN: Layered recursive generative adver-
sarial networks for image generation. ICLR, 2017.
Yuichi Yoshida and Takeru Miyato. Spectral norm regularization for improving the generalizability of deep
learning. arXiv preprint arXiv:1705.10941, 2017.
12


---

Published as a conference paper at ICLR 2018
(a) CIFAR-10
(b) STL-10
Figure 6: Generated images on different methods: WGAN-GP, weight normalization, and spectral
normalization on CIFAR-10 and STL-10.
13


---

Published as a conference paper at ICLR 2018
Figure 7:
128x128 pixel images generated by SN-GANs trained on ILSVRC2012 dataset. The
inception score is 21.1±.35.
14


---

Published as a conference paper at ICLR 2018
A
THE ALGORITHM OF SPECTRAL NORMALIZATION
Let us describe the shortcut in Section 2.1 in more detail. We begin with vectors ˜u that is randomly
initialized for each weight. If there is no multiplicity in the dominant singular values and if ˜u is not
orthogonal to the ﬁrst left singular vectors7, we can appeal to the principle of the power method and
produce the ﬁrst left and right singular vectors through the following update rule:
˜v ←W T ˜u/∥W T ˜u∥2, ˜u ←W ˜v/∥W ˜v∥2.
(18)
We can then approximate the spectral norm of W with the pair of so-approximated singular vectors:
σ(W) ≈˜uTW ˜v.
(19)
If we use SGD for updating W, the change in W at each update would be small, and hence the
change in its largest singular value. In our implementation, we took advantage of this fact and reused
the ˜u computed at each step of the algorithm as the initial vector in the subsequent step. In fact,
with this ‘recycle’ procedure, one round of power iteration was sufﬁcient in the actual experiment
to achieve satisfactory performance. Algorithm 1 in the appendix summarizes the computation of
the spectrally normalized weight matrix ¯W with this approximation. Note that this procedure is
very computationally cheap even in comparison to the calculation of the forward and backward
propagations on neural networks. Please see Figure 10 for actual computational time with and
without spectral normalization.
Algorithm 1 SGD with spectral normalization
• Initialize ˜ul ∈Rdl for l = 1, . . . , L with a random vector (sampled from isotropic distri-
bution).
• For each update and each layer l:
1. Apply power iteration method to a unnormalized weight W l:
˜vl ←(W l)T ˜ul/∥(W l)T ˜ul∥2
(20)
˜ul ←W l˜vl/∥W l˜vl∥2
(21)
2. Calculate ¯WSN with the spectral norm:
¯W l
SN(W l) = W l/σ(W l), where σ(W l) = ˜uT
l W l˜vl
(22)
3. Update W l with SGD on mini-batch dataset DM with a learning rate α:
W l ←W l −α∇W lℓ( ¯W l
SN(W l), DM)
(23)
B
EXPERIMENTAL SETTINGS
B.1
PERFORMANCE MEASURES
Inception score is introduced originally by Salimans et al. (2016):
I({xn}N
n=1)
:=
exp(E[DKL[p(y|x)||p(y)]]), where p(y) is approximated by
1
N
PN
n=1 p(y|xn) and p(y|x) is the
trained Inception convolutional neural network (Szegedy et al., 2015), which we would refer to In-
ception model for short. In their work, Salimans et al. (2016) reported that this score is strongly
correlated with subjective human judgment of image quality. Following the procedure in Salimans
et al. (2016); Warde-Farley & Bengio (2017), we calculated the score for randomly generated 5000
examples from each trained generator to evaluate its ability to generate natural images. We repeated
each experiment 10 times and reported the average and the standard deviation of the inception scores.
Fr´echet inception distance (Heusel et al., 2017) is another measure for the quality of the generated
examples that uses 2nd order information of the ﬁnal layer of the inception model applied to the
7In practice, we are safe to assume that ˜u generated from uniform distribution on the sphere is not orthogonal
to the ﬁrst singular vectors, because this can happen with probability 0.
15


---

Published as a conference paper at ICLR 2018
examples. On its own, the Fre´chet distance Dowson & Landau (1982) is 2-Wasserstein distance
between two distribution p1 and p2 assuming they are both multivariate Gaussian distributions:
F(p1, p2) = ∥µp1 −µp2∥2
2 + trace

Cp1 + Cp2 −2(Cp1Cp2)1/2
,
(24)
where {µp1, Cp1}, {µp2, Cp2} are the mean and covariance of samples from q and p, respectively.
If f⊖is the output of the ﬁnal layer of the inception model before the softmax, the Fr´echet inception
distance (FID) between two distributions p1 and p2 on the images is the distance between f⊖◦p1 and
f⊖◦p2. We computed the Fr´echet inception distance between the true distribution and the generated
distribution empirically over 10000 and 5000 samples. Multiple repetition of the experiments did
not exhibit any notable variations on this score.
B.2
IMAGE GENERATION ON CIFAR-10 AND STL-10
For the comparative study, we experimented with the recent ResNet architecture of Gulrajani
et al. (2017) as well as the standard CNN. For this additional set of experiments, we used Adam
again for the optimization and used the very hyper parameter used in Gulrajani et al. (2017)
(α = 0.0002, β1 = 0, β2 = 0.9, ndis = 5). For our SN-GANs, we doubled the feature map in
the generator from the original, because this modiﬁcation achieved better results. Note that when
we doubled the dimension of the feature map for the WGAN-GP experiment, however, the perfor-
mance deteriorated.
B.3
IMAGE GENERATION ON IMAGENET
The images used in this set of experiments were resized to 128 × 128 pixels. The details of the
architecture are given in Table 6. For the generator network of conditional GANs, we used con-
ditional batch normalization (CBN) (Dumoulin et al., 2017; de Vries et al., 2017). Namely we
replaced the standard batch normalization layer with the CBN conditional to the label information
y ∈{1, . . . , 1000}. For the optimization, we used Adam with the same hyperparameters we used for
ResNet on CIFAR-10 and STL-10 dataset. We trained the networks with 450K generator updates,
and applied linear decay for the learning rate after 400K iterations so that the rate would be 0 at the
end.
B.4
NETWORK ARCHITECTURES
Table 3:
Standard CNN models for CIFAR-10 and STL-10 used in our experiments on image
Generation. The slopes of all lReLU functions in the networks are set to 0.1.
z ∈R128 ∼N(0, I)
dense →Mg × Mg × 512
4×4, stride=2 deconv. BN 256 ReLU
4×4, stride=2 deconv. BN 128 ReLU
4×4, stride=2 deconv. BN 64 ReLU
3×3, stride=1 conv. 3 Tanh
(a) Generator, Mg = 4 for SVHN and CIFAR10, and
Mg = 6 for STL-10
RGB image x ∈RM×M×3
3×3, stride=1 conv 64 lReLU
4×4, stride=2 conv 64 lReLU
3×3, stride=1 conv 128 lReLU
4×4, stride=2 conv 128 lReLU
3×3, stride=1 conv 256 lReLU
4×4, stride=2 conv 256 lReLU
3×3, stride=1 conv. 512 lReLU
dense →1
(b) Discriminator, M = 32 for SVHN and CIFAR10,
and M = 48 for STL-10
16


---

Published as a conference paper at ICLR 2018
BN
ReLU
Conv
BN
ReLU
Conv
Figure 8:
Res-
Block architecture.
For the discrimina-
tor we removed BN
layers in ResBlock.
Table 4: ResNet architectures for CIFAR10 dataset. We use similar archi-
tectures to the ones used in Gulrajani et al. (2017).
z ∈R128 ∼N(0, I)
dense, 4 × 4 × 256
ResBlock up 256
ResBlock up 256
ResBlock up 256
BN, ReLU, 3×3 conv, 3 Tanh
(a) Generator
RGB image x ∈R32×32×3
ResBlock down 128
ResBlock down 128
ResBlock 128
ResBlock 128
ReLU
Global sum pooling
dense →1
(b) Discriminator
Table 5: ResNet architectures for STL-10 dataset.
z ∈R128 ∼N(0, I)
dense, 6 × 6 × 512
ResBlock up 256
ResBlock up 128
ResBlock up 64
BN, ReLU, 3×3 conv, 3 Tanh
(a) Generator
RGB image x ∈R48×48×3
ResBlock down 64
ResBlock down 128
ResBlock down 256
ResBlock down 512
ResBlock 1024
ReLU
Global sum pooling
dense →1
(b) Discriminator
17


---

Published as a conference paper at ICLR 2018
Table 6: ResNet architectures for image generation on ImageNet dataset. For the generator of condi-
tional GANs, we replaced the usual batch normalization layer in the ResBlock with the conditional
batch normalization layer. As for the model of the projection discriminator, we used the same
architecture used in Miyato & Koyama (2018). Please see the paper for the details.
z ∈R128 ∼N(0, I)
dense, 4 × 4 × 1024
ResBlock up 1024
ResBlock up 512
ResBlock up 256
ResBlock up 128
ResBlock up 64
BN, ReLU, 3×3 conv 3
Tanh
(a) Generator
RGB image x ∈R128×128×3
ResBlock down 64
ResBlock down 128
ResBlock down 256
ResBlock down 512
ResBlock down 1024
ResBlock 1024
ReLU
Global sum pooling
dense →1
(b)
Discriminator for uncondi-
tional GANs.
RGB image x ∈R128×128×3
ResBlock down 64
ResBlock down 128
ResBlock down 256
Concat(Embed(y), h)
ResBlock down 512
ResBlock down 1024
ResBlock 1024
ReLU
Global sum pooling
dense →1
(c) Discriminator for conditional
GANs. For computational ease,
we embedded the integer label
y
∈
{0, . . . , 1000} into 128
dimension before concatenating
the vector to the output of the in-
termediate layer.
18


---

Published as a conference paper at ICLR 2018
C
APPENDIX RESULTS
C.1
ACCURACY OF SPECTRAL NORMALIZATION
Figure 9 shows the spectral norm of each layer in the discriminator over the course of the training.
The setting of the optimizer is C in Table 1 throughout the training. In fact, they do not deviate by
more than 0.05 for the most part. As an exception, 6 and 7-th convolutional layers with largest rank
deviate by more than 0.1 in the beginning of the training, but the norm of this layer too stabilizes
around 1 after some iterations.
0
20000 40000 60000 80000100000
update
0.95
1.00
1.05
1.10
1.15
1.20
σ( ¯W)
conv0
conv1
conv2
conv3
conv4
conv5
conv6
Figure 9: Spectral norms of all seven convolutional layers in the standard CNN during course of the
training on CIFAR 10.
C.2
TRAINING TIME
WGAN-GP WN
SN
Vanilla
0
5
10
15
20
25
30
35
40
45
Seconds for 100 generator updates
(a) CIFAR-10 (image size:32 ×
32 × 3)
WGAN-GP WN
SN
Vanilla
0
20
40
60
80
100
Seconds for 100 generator updates
(b)
STL-10 (images size:48 ×
48 × 3)
Figure 10: Computational time for 100 updates. We set ndis = 5
C.3
THE EFFECT OF ndis ON SPECTRAL NORMALIZATION AND WEIGHT NORMALIZATION
Figure 11 shows the effect of ndis on the performance of weight normalization and spectral normal-
ization. All results shown in Figure 11 follows setting D, except for the value of ndis. For WN,
the performance deteriorates with larger ndis, which amounts to computing minimax with better
accuracy. Our SN does not suffer from this unintended effect.
19


---

Published as a conference paper at ICLR 2018
12
5
10
20
ndis
2
3
4
5
6
7
Inception score
Inception scores 
 after 10000 generator updates
SN
WN
Figure 11:
The effect of ndis on spectral normalization and weight normalization. The shaded
region represents the variance of the result over different seeds.
C.4
GENERATED IMAGES ON CIFAR10 WITH GAN-GP, LAYER NORMALIZATION AND
BATCH NORMALIZATION
Figure 12: Generated images with GAN-GP, Layer Norm and Batch Norm on CIFAR-10
20


---

Published as a conference paper at ICLR 2018
C.5
IMAGE GENERATION ON IMAGENET
0.0
1.0
2.0
3.0
4.04.5
iteration
1e5
10
11
12
13
14
15
16
inception score
SN-GANs
Orthnormal
(a) Unconditional GANs
0.0
1.0
2.0
3.0
4.04.5
iteration
1e5
10
15
20
25
30
inception score
SN-GANs
Orthnormal
(b) Conditional GANs with projection discriminator
Figure 13: Learning curves in terms of Inception score for SN-GANs and GANs with orthonormal
regularization on ImageNet. The ﬁgure (a) shows the results for the standard (unconditional) GANs,
and the ﬁgure (b) shows the results for the conditional GANs trained with projection discrimina-
tor (Miyato & Koyama, 2018)
D
SPECTRAL NORMALIZATION VS OTHER REGULARIZATION TECHNIQUES
This section is dedicated to the comparative study of spectral normalization and other regularization
methods for discriminators. In particular, we will show that contemporary regularizations including
weight normalization and weight clipping implicitly impose constraints on weight matrices that
places unnecessary restriction on the search space of the discriminator. More speciﬁcally, we will
show that weight normalization and weight clipping unwittingly favor low-rank weight matrices.
This can force the trained discriminator to be largely dependent on select few features, rendering the
algorithm to be able to match the model distribution with the target distribution only on very low
dimensional feature space.
D.1
WEIGHT NORMALIZATION AND FROBENIUS NORMALIZATION
The weight normalization introduced by Salimans & Kingma (2016) is a method that normalizes the
ℓ2 norm of each row vector in the weight matrix8:
¯WWN :=
 ¯wT
1 , ¯wT
2 , ..., ¯wT
do
T , where ¯wi(wi) := wi/∥wi∥2,
(25)
where ¯wi and wi are the ith row vector of ¯WWN and W, respectively.
Still another technique to regularize the weight matrix is to use the Frobenius norm:
¯WFN := W/∥W∥F ,
(26)
where ∥W∥F :=
p
tr(W TW) =
qP
i,j w2
ij.
Originally, these regularization techniques were invented with the goal of improving the generaliza-
tion performance of supervised training (Salimans & Kingma, 2016; Arpit et al., 2016). However,
recent works in the ﬁeld of GANs (Salimans et al., 2016; Xiang & Li, 2017) found their another
raison d’etat as a regularizer of discriminators, and succeeded in improving the performance of the
original.
8In the original literature, the weight normalization was introduced as a method for reparametrization of the
form ¯
WWN :=

γ1 ¯wT
1 , γ2 ¯wT
2 , ..., γdo ¯wT
do
T where γi ∈R is to be learned in the course of the training. In
this work, we deal with the case γi = 1 so that we can assess the methods under the Lipschitz constraint.
21


---

Published as a conference paper at ICLR 2018
These methods in fact can render the trained discriminator D to be K-Lipschitz for a some pre-
scribed K and achieve the desired effect to a certain extent. However, weight normalization (25)
imposes the following implicit restriction on the choice of ¯WWN:
σ1( ¯WWN)2 + σ2( ¯WWN)2 + · · · + σT ( ¯WWN)2 = do, where T = min(di, do),
(27)
where σt(A) is a t-th singular value of matrix A.
The above equation holds because
Pmin(di,do)
t=1
σt( ¯WWN)2 = tr( ¯WWN ¯W T
WN) = Pdo
i=1
wi
∥wi∥2
wT
i
∥wi∥2 = do. Under this restriction, the
norm ∥¯WWNh∥2 for a ﬁxed unit vector h is maximized at ∥¯WWNh∥2 = √do when σ1( ¯WWN) =
√do and σt( ¯WWN) = 0 for t = 2, . . . , T, which means that ¯WWN is of rank one. Using such
W corresponds to using only one feature to discriminate the model probability distribution from the
target. Similarly, Frobenius normalization requires σ1( ¯WFN)2+σ2( ¯WFN)2+· · ·+σT ( ¯WFN)2 = 1,
and the same argument as above follows.
Here, we see a critical problem in these two regularization methods. In order to retain as much
norm of the input as possible and hence to make the discriminator more sensitive, one would hope
to make the norm of ¯WWNh large. For weight normalization, however, this comes at the cost of
reducing the rank and hence the number of features to be used for the discriminator. Thus, there is a
conﬂict of interests between weight normalization and our desire to use as many features as possible
to distinguish the generator distribution from the target distribution. The former interest often reigns
over the other in many cases, inadvertently diminishing the number of features to be used by the
discriminators. Consequently, the algorithm would produce a rather arbitrary model distribution
that matches the target distribution only at select few features.
Our spectral normalization, on the other hand, do not suffer from such a conﬂict in interest. Note
that the Lipschitz constant of a linear operator is determined only by the maximum singular value.
In other words, the spectral norm is independent of rank. Thus, unlike the weight normalization,
our spectral normalization allows the parameter matrix to use as many features as possible while
satisfying local 1-Lipschitz constraint. Our spectral normalization leaves more freedom in choosing
the number of singular components (features) to feed to the next layer of the discriminator.
To see this more visually, we refer the reader to Figure (14). Note that spectral normalization allows
for a wider range of choices than weight normalization.
0
25
49
Index of s
0.0
0.2
0.4
0.6
0.8
1.0
s2
SN
WN
Figure 14:
Visualization of the difference between spectral normalization (Red) and weight
normalization (Blue) on possible sets of singular values. The possible sets of singular values
plotted in increasing order for weight normalization (Blue) and for spectral normalization (Red).
For the set of singular values permitted under the spectral normalization condition, we scaled ¯WWN
by 1/√do so that its spectral norm is exactly 1. By the deﬁnition of the weight normalization, the
area under the blue curves are all bound to be 1. Note that the range of choice for the weight
normalization is small.
In summary, weight normalization and Frobenius normalization favor skewed distributions of singu-
lar values, making the column spaces of the weight matrices lie in (approximately) low dimensional
vector spaces. On the other hand, our spectral normalization does not compromise the number
of feature dimensions used by the discriminator. In fact, we will experimentally show that GANs
22


---

Published as a conference paper at ICLR 2018
trained with our spectral normalization can generate a synthetic dataset with wider variety and higher
inception score than the GANs trained with other two regularization methods.
D.2
WEIGHT CLIPPING
Still another regularization technique is weight clipping introduced by Arjovsky et al. (2017) in their
training of Wasserstein GANs. Weight clipping simply truncates each element of weight matrices
so that its absolute value is bounded above by a prescribed constant c ∈R+. Unfortunately, weight
clipping suffers from the same problem as weight normalization and Frobenius normalization. With
weight clipping with the truncation value c, the value ∥Wx∥2 for a ﬁxed unit vector x is maximized
when the rank of W is again one, and the training will again favor the discriminators that use
only select few features. Gulrajani et al. (2017) refers to this problem as capacity underuse problem.
They also reported that the training of WGAN with weight clipping is slower than that of the original
DCGAN (Radford et al., 2016).
D.3
SINGULAR VALUE CLIPPING AND SINGULAR VALUE CONSTRAINT
One direct and straightforward way of controlling the spectral norm is to clip the singular val-
ues (Saito et al., 2017), (Jia et al., 2017). This approach, however, is computationally heavy because
one needs to implement singular value decomposition in order to compute all the singular values.
A similar but less obvious approach is to parametrize W ∈Rdo×di as follows from the get-go and
train the discriminators with this constrained parametrization:
W := USV T, subject to U TU = I, V TV = I, max
i
Sii = K,
(28)
where U ∈Rdo×P , V ∈Rdi×P , and S ∈RP ×P is a diagonal matrix. However, it is not a simple
task to train this model while remaining absolutely faithful to this parametrization constraint. Our
spectral normalization, on the other hand, can carry out the updates with relatively low computa-
tional cost without compromising the normalization constraint.
D.4
WGAN WITH GRADIENT PENALTY (WGAN-GP)
Recently, Gulrajani et al. (2017) introduced a technique to enhance the stability of the training of
Wasserstein GANs (Arjovsky et al., 2017). In their work, they endeavored to place K-Lipschitz
constraint (5) on the discriminator by augmenting the adversarial loss function with the following
regularizer function:
λ
E
ˆx∼pˆ
x
[(∥∇ˆxD(ˆx)∥2 −1)2],
(29)
where λ > 0 is a balancing coefﬁcient and ˆx is:
ˆx := ϵx + (1 −ϵ)˜x
(30)
where ϵ ∼U[0, 1], x ∼pdata, ˜x = G(z), z ∼pz.
(31)
Using this augmented objective function, Gulrajani et al. (2017) succeeded in training a GAN based
on ResNet (He et al., 2016) with an impressive performance. The advantage of their method in
comparison to spectral normalization is that they can impose local 1-Lipschitz constraint directly on
the discriminator function without a rather round-about layer-wise normalization. This suggest that
their method is less likely to underuse the capacity of the network structure.
At the same time, this type of method that penalizes the gradients at sample points ˆx suffers from
the obvious problem of not being able to regularize the function at the points outside of the support
of the current generative distribution. In fact, the generative distribution and its support gradually
changes in the course of the training, and this can destabilize the effect of the regularization itself.
On the contrary, our spectral normalization regularizes the function itself, and the effect of the
regularization is more stable with respect to the choice of the batch. In fact, we observed in the
experiment that a high learning rate can destabilize the performance of WGAN-GP. Training with
our spectral normalization does not falter with aggressive learning rate.
23


---

Published as a conference paper at ICLR 2018
Moreover, WGAN-GP requires more computational cost than our spectral normalization with
single-step power iteration, because the computation of ∥∇xD∥2 requires one whole round of
forward and backward propagation. In Figure 10, we compare the computational cost of the two
methods for the same number of updates.
Having said that, one shall not rule out the possibility that the gradient penalty can compliment
spectral normalization and vice versa. Because these two methods regularizes discriminators by
completely different means, and in the experiment section, we actually conﬁrmed that combina-
tion of WGAN-GP and reparametrization with spectral normalization improves the quality of the
generated examples over the baseline (WGAN-GP only).
E
REPARAMETRIZATION MOTIVATED BY THE SPECTRAL NORMALIZATION
We can take advantage of the regularization effect of the spectral normalization we saw above to
develop another algorithm. Let us consider another parametrization of the weight matrix of the
discriminator given by:
˜W := γ ¯WSN
(32)
where γ is a scalar variable to be learned. This parametrization compromises the 1-Lipschitz con-
straint at the layer of interest, but gives more freedom to the model while keeping the model from
becoming degenerate. For this reparametrization, we need to control the Lipschitz condition by
other means, such as the gradient penalty (Gulrajani et al., 2017). Indeed, we can think of analogous
versions of reparametrization by replacing ¯WSN in (32) with W normalized by other criterions. The
extension of this form is not new. In Salimans & Kingma (2016), they originally introduced weight
normalization in order to derive the reparametrization of the form (32) with ¯WSN replaced (32) by
WWN and vectorized γ.
E.1
EXPERIMENTS: COMPARISON OF REPARAMETRIZATION WITH DIFFERENT
NORMALIZATION METHODS
In this part of the addendum, we experimentally compare the reparametrizations derived from two
different normalization methods (weight normalization and spectral normalization). We tested the
reprametrization methods for the training of the discriminator of WGAN-GP. For the architecture
of the network in WGAN-GP, we used the same CNN we used in the previous section. For the
ResNet-based CNN, we used the same architecture provided by (Gulrajani et al., 2017) 9.
Tables 7, 8 summarize the result. We see that our method signiﬁcantly improves the inception score
from the baseline on the regular CNN, and slightly improves the score on the ResNet based CNN.
Figure 15 shows the learning curves of (a) critic losses, on train and validation sets and (b) the in-
ception scores with different reparametrization methods. We can see the beneﬁcial effect of spectral
normalization in the learning curve of the discriminator as well. We can verify in the ﬁgure 15a
that the discriminator with spectral normalization overﬁts less to the training dataset than the dis-
criminator without reparametrization and with weight normalization, The effect of overﬁtting can be
observed on inception score as well, and the ﬁnal score with spectral normalization is better than the
others. As for the best inception score achieved in the course of the training, spectral normalization
achieved 7.28, whereas the spectral normalization and vanilla normalization achieved 7.04 and 6.69,
respectively.
F
THE GRADIENT OF GENERAL NORMALIZATION METHOD
Let us denote ¯W := W/N(W) to be the normalized weight where N(W) to be a scalar normalized
coefﬁcient (e.g. Spectral norm or Frobenius norm). In general, we can write the derivative of loss
9We implement our method based on the open-sourced code provided by the author (Gulra-
jani et al., 2017) https://github.com/igul222/improved_wgan_training/blob/master/
gan_cifar_resnet.py
24


---

Published as a conference paper at ICLR 2018
Method
Inception score
FID
WGAN-GP (Standard CNN, Baseline)
6.68±.06
40.1
w/ Frobenius Norm.
N/A∗
N/A∗
w/ Weight Norm.
6.36±.04
42.4
w/ Spectral Norm.
7.20±.08
32.0
(WGAN-GP, ResNet, Gulrajani et al. (2017))
7.86±.08
WGAN-GP (ResNet, Baseline)
7.80±.11
24.5
w/ Spectral norm.
7.85±.06
23.6
w/ Spectral norm. (1.5x feature maps in D)
7.96±.06
22.5
Table 7: Inception scores with different reparametrization mehtods on CIFAR10 without label su-
pervisions. (*)We reported N/A for the inception score and FID of Frobenius normalization because
the training collapsed at the early stage.
Method (ResNet)
Inception score
FID
(AC-WGAN-GP, Gulrajani et al. (2017))
8.42±.10
AC-WGAN-GP (Baseline)
8.29±.12
19.5
w/ Spectral norm.
8.59±.12
18.6
w/ Spectral norm. (1.5x feature maps in D)
8.60±.08
17.5
Table 8: Inception scores and FIDs with different reparametrization methods on CIFAR10 with the
label supervision, by auxiliary classiﬁer (Odena et al., 2017).
with respect to unnormalized weight W as follows:
∂V (G, D(W))
∂W
=
1
N(W)
 
∂V
∂¯W −trace
  ∂V
∂¯W
T
¯W
!
∂(N(W))
∂W
!
(33)
=
1
N(W)
 ∇¯
W V −trace
 (∇¯
W V )T ¯W

∇W N

(34)
= α (∇¯
W V −λ∇W N) ,
(35)
where α := 1/N(W) and λ := trace
 (∇¯
W V )T ¯W

. The gradient ∇¯
W V is calculated by ˆE

δhT
where δ :=
 ∂V (G, D)/∂
  ¯Wh
T, h is the hidden node in the network to be transformed by ¯W
and ˆE represents empirical expectation over the mini-batch. When N(W) := ∥W∥F , the derivative
is:
∂V (G, D(W))
∂W
=
1
∥W∥F

ˆE

δhT
−trace

ˆE

δhTT ¯W

¯W

,
(36)
and when N(W) := ∥W∥2 = σ(W),
∂V (G, D(W))
∂W
=
1
σ(W)

ˆE

δhT
−trace

ˆE

δhTT ¯W

u1vT
1

.
(37)
Notice that, at least for the case N(W) := ∥W∥F or N(W) := ∥W∥2, the point of this gradient is
given by :
∇¯
W V = k∇W N.
(38)
where ∃k ∈R
25


---

Published as a conference paper at ICLR 2018
0
20000
40000
60000
80000 100000
Update of the generator
3.0
2.5
2.0
1.5
1.0
0.5
0.0
Critic loss
WGAN-GP (train)
WGAN-GP (valid)
WGAN-GP w/ WN (train)
WGAN-GP w/ WN (valid)
WGAN-GP w/ SN (train)
WGAN-GP w/ SN (valid)
(a) Critic loss
0
20000
40000
60000
80000
100000
Update of the generator
5.0
5.5
6.0
6.5
7.0
7.5
Inception score
WGAN-GP
WGAN-GP w/ WN
WGAN-GP w/ SN
(b) Inception score
Figure 15: Learning curves of (a) critic loss and (b) inception score on different reparametrization
method on CIFAR-10 ; weight normalization (WGAN-GP w/ WN), spectral normalization (WGAN-
GP w/ SN), and parametrization free (WGAN-GP).
26
