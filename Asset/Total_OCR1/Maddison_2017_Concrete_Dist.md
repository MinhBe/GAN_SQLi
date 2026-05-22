Published as a conference paper at ICLR 2017
THE CONCRETE DISTRIBUTION:
A CONTINUOUS RELAXATION OF
DISCRETE RANDOM VARIABLES
Chris J. Maddison1,2, Andriy Mnih1, & Yee Whye Teh1
1DeepMind, London, United Kingdom
2University of Oxford, Oxford, United Kingdom
cmaddis@stats.ox.ac.uk
ABSTRACT
The reparameterization trick enables optimizing large scale stochastic computa-
tion graphs via gradient descent. The essence of the trick is to refactor each
stochastic node into a differentiable function of its parameters and a random vari-
able with ﬁxed distribution. After refactoring, the gradients of the loss propa-
gated by the chain rule through the graph are low variance unbiased estimators
of the gradients of the expected loss. While many continuous random variables
have such reparameterizations, discrete random variables lack useful reparame-
terizations due to the discontinuous nature of discrete states. In this work we
introduce CONCRETE random variables—CONtinuous relaxations of disCRETE
random variables.
The Concrete distribution is a new family of distributions
with closed form densities and a simple reparameterization. Whenever a discrete
stochastic node of a computation graph can be refactored into a one-hot bit rep-
resentation that is treated continuously, Concrete stochastic nodes can be used
with automatic differentiation to produce low-variance biased gradients of objec-
tives (including objectives that depend on the log-probability of latent stochastic
nodes) on the corresponding discrete graph. We demonstrate the effectiveness of
Concrete relaxations on density estimation and structured prediction tasks using
neural networks.
1
INTRODUCTION
Software libraries for automatic differentiation (AD) (Abadi et al., 2015; Theano Development
Team, 2016) are enjoying broad use, spurred on by the success of neural networks on some of
the most challenging problems of machine learning. The dominant mode of development in these
libraries is to deﬁne a forward parametric computation, in the form of a directed acyclic graph, that
computes the desired objective. If the components of the graph are differentiable, then a backwards
computation for the gradient of the objective can be derived automatically with the chain rule. The
ease of use and unreasonable effectiveness of gradient descent has led to an explosion in the di-
versity of architectures and objective functions. Thus, expanding the range of useful continuous
operations can have an outsized impact on the development of new models. For example, a topic of
recent attention has been the optimization of stochastic computation graphs from samples of their
states. Here, the observation that AD “just works” when stochastic nodes1 can be reparameterized
into deterministic functions of their parameters and a ﬁxed noise distribution (Kingma & Welling,
2013; Rezende et al., 2014), has liberated researchers in the development of large complex stochastic
architectures (e.g. Gregor et al., 2015).
Computing with discrete stochastic nodes still poses a signiﬁcant challenge for AD libraries. Deter-
ministic discreteness can be relaxed and approximated reasonably well with sigmoidal functions or
the softmax (see e.g., Grefenstette et al., 2015; Graves et al., 2016), but, if a distribution over discrete
states is needed, there is no clear solution. There are well known unbiased estimators for the gradi-
1For our purposes a stochastic node of a computation graph is just a random variable whose distribution
depends in some deterministic way on the values of the parent nodes.
1
arXiv:1611.00712v3  [cs.LG]  5 Mar 2017


---

Published as a conference paper at ICLR 2017
ents of the parameters of a discrete stochastic node from samples. While these can be made to work
with AD, they involve special casing and deﬁning surrogate objectives (Schulman et al., 2015), and
even then they can have high variance. Still, reasoning about discrete computation comes naturally
to humans, and so, despite the difﬁculty associated, many modern architectures incorporate discrete
stochasticity (Mnih et al., 2014; Xu et al., 2015; Koˇcisk´y et al., 2016).
This work is inspired by the observation that many architectures treat discrete nodes continuously,
and gradients rich with counterfactual information are available for each of their possible states.
We introduce a CONtinuous relaxation of disCRETE random variables, CONCRETE for short, which
allow gradients to ﬂow through their states. The Concrete distribution is a new parametric family
of continuous distributions on the simplex with closed form densities. Sampling from the Concrete
distribution is as simple as taking the softmax of logits perturbed by ﬁxed additive noise. This
reparameterization means that Concrete stochastic nodes are quick to implement in a way that “just
works” with AD. Crucially, every discrete random variable corresponds to the zero temperature
limit of a Concrete one. In this view optimizing an objective over an architecture with discrete
stochastic nodes can be accomplished by gradient descent on the samples of the corresponding
Concrete relaxation. When the objective depends, as in variational inference, on the log-probability
of discrete nodes, the Concrete density is used during training in place of the discrete mass. At test
time, the graph with discrete nodes is evaluated.
The paper is organized as follows. We provide a background on stochastic computation graphs and
their optimization in Section 2. Section 3 reviews a reparameterization for discrete random vari-
ables, introduces the Concrete distribution, and discusses its application as a relaxation. Section 4
reviews related work. In Section 5 we present results on a density estimation task and a structured
prediction task on the MNIST and Omniglot datasets. In Appendices C and F we provide details
on the practical implementation and use of Concrete random variables. When comparing the effec-
tiveness of gradients obtained via Concrete relaxations to a state-of-the-art-method (VIMCO, Mnih
& Rezende, 2016), we ﬁnd that they are competitive—occasionally outperforming and occasionally
underperforming—all the while being implemented in an AD library without special casing.
2
BACKGROUND
2.1
OPTIMIZING STOCHASTIC COMPUTATION GRAPHS
Stochastic computation graphs (SCGs) provide a formalism for specifying input-output mappings,
potentially stochastic, with learnable parameters using directed acyclic graphs (see Schulman et al.
(2015) for a review). The state of each non-input node in such a graph is obtained from the states
of its parent nodes by either evaluating a deterministic function or sampling from a conditional
distribution. Many training objectives in supervised, unsupervised, and reinforcement learning can
be expressed in terms of SCGs.
To optimize an objective represented as a SCG, we need estimates of its parameter gradients. We will
concentrate on graphs with some stochastic nodes (backpropagation covers the rest). For simplicity,
we restrict our attention to graphs with a single stochastic node X. We can interpret the forward
pass in the graph as ﬁrst sampling X from the conditional distribution pφ(x) of the stochastic node
given its parents, then evaluating a deterministic function fθ(x) at X. We can think of fθ(X) as a
noisy objective, and we are interested in optimizing its expected value L(θ, φ) = EX∼pφ(x)[fθ(X)]
w.r.t. parameters θ, φ.
In general, both the objective and its gradients are intractable. We will side-step this issue by esti-
mating them with samples from pφ(x). The gradient w.r.t. to the parameters θ has the form
∇θL(θ, φ) = ∇θEX∼pφ(x)[fθ(X)] = EX∼pφ(x)[∇θfθ(X)]
(1)
and can be easily estimated using Monte Carlo sampling:
∇θL(θ, φ) ≃1
S
XS
s=1 ∇θfθ(Xs),
(2)
where Xs ∼pφ(x) i.i.d. The more challenging task is to compute the gradient w.r.t. the parameters
φ of pφ(x). The expression obtained by differentiating the expected objective,
∇φL(θ, φ) = ∇φ
Z
pφ(x)fθ(x) dx =
Z
fθ(x)∇φpφ(x) dx,
(3)
2


---

Published as a conference paper at ICLR 2017
does not have the form of an expectation w.r.t. x and thus does not directly lead to a Monte Carlo
gradient estimator. However, there are two ways of getting around this difﬁculty which lead to the
two classes of estimators we will now discuss.
2.2
SCORE FUNCTION ESTIMATORS
The score function estimator (SFE, Fu, 2006), also known as the REINFORCE (Williams, 1992) or
likelihood-ratio estimator (Glynn, 1990), is based on the identity ∇φpφ(x) = pφ(x)∇φ log pφ(x),
which allows the gradient in Eq. 3 to be written as an expectation:
∇φL(θ, φ) = EX∼pφ(x) [fθ(X)∇φ log pφ(X)] .
(4)
Estimating this expectation using naive Monte Carlo gives the estimator
∇φL(θ, φ) ≃1
S
XS
s=1 fθ(Xs)∇φ log pφ(Xs),
(5)
where Xs ∼pφ(x) i.i.d. This is a very general estimator that is applicable whenever log pφ(x)
is differentiable w.r.t. φ. As it does not require fθ(x) to be differentiable or even continuous as a
function of x, the SFE can be used with both discrete and continuous random variables.
Though the basic version of the estimator can suffer from high variance, various variance reduc-
tion techniques can be used to make the estimator much more effective (Greensmith et al., 2004).
Baselines are the most important and widely used of these techniques (Williams, 1992). A number
of score function estimators have been developed in machine learning (Paisley et al., 2012; Gregor
et al., 2013; Ranganath et al., 2014; Mnih & Gregor, 2014; Titsias & L´azaro-Gredilla, 2015; Gu
et al., 2016), which differ primarily in the variance reduction techniques used.
2.3
REPARAMETERIZATION TRICK
In many cases we can sample from pφ(x) by ﬁrst sampling Z from some ﬁxed distribution
q(z) and then transforming the sample using some function gφ(z).
For example, a sample
from Normal(µ, σ2) can be obtained by sampling Z from the standard form of the distribution
Normal(0, 1) and then transforming it using gµ,σ(Z) = µ + σZ. This two-stage reformulation of
the sampling process, called the reparameterization trick, allows us to transfer the dependence on φ
from p into f by writing fθ(x) = fθ(gφ(z)) for x = gφ(z), making it possible to reduce the problem
of estimating the gradient w.r.t. parameters of a distribution to the simpler problem of estimating the
gradient w.r.t. parameters of a deterministic function.
Having reparameterized pφ(x), we can now express the objective as an expectation w.r.t. q(z):
L(θ, φ) = EX∼pφ(x)[fθ(X)] = EZ∼q(z)[fθ(gφ(Z))].
(6)
As q(z) does not depend on φ, we can estimate the gradient w.r.t. φ in exactly the same way we
estimated the gradient w.r.t. θ in Eq. 1. Assuming differentiability of fθ(x) w.r.t. x and of gφ(z)
w.r.t. φ and using the chain rule gives
∇φL(θ, φ) = EZ∼q(z)[∇φfθ(gφ(Z))] = EZ∼q(z) [f ′
θ(gφ(Z))∇φgφ(Z)] .
(7)
The reparameterization trick, introduced in the context of variational inference independently by
Kingma & Welling (2014), Rezende et al. (2014), and Titsias & L´azaro-Gredilla (2014), is usu-
ally the estimator of choice when it is applicable. For continuous latent variables which are not
directly reparameterizable, new hybrid estimators have also been developed, by combining partial
reparameterizations with score function estimators (Ruiz et al., 2016; Naesseth et al., 2016).
2.4
APPLICATION: VARIATIONAL TRAINING OF LATENT VARIABLE MODELS
We will now see how the task of training latent variable models can be formulated in the SCG
framework. Such models assume that each observation x is obtained by ﬁrst sampling a vector
of latent variables Z from the prior pθ(z) before sampling the observation itself from pθ(x | z).
Thus the probability of observation x is pθ(x) = P
z pθ(z)pθ(x | z). Maximum likelihood train-
ing of such models is infeasible, because the log-likelihood (LL) objective L(θ) = log pθ(x) =
3


---

Published as a conference paper at ICLR 2017
G2
G2
+
log ↵1
log ↵1 log ↵2
log ↵2 log ↵3
log ↵3
argmaxi{xi}
argmaxi{xi}
G1
G1
G3
G3
(a) Discrete(α)
G2
G2
+
λ
exp(xi/λ)
P
i exp(xi/λ)
exp(xi/λ)
P
i exp(xi/λ)
log ↵1
log ↵1 log ↵2
log ↵2 log ↵3
log ↵3
G1
G1
G3
G3
(b) Concrete(α, λ)
Figure 1: Visualization of sampling graphs for 3-ary discrete D ∼Discrete(α) and 3-ary Con-
crete X ∼Concrete(α, λ). White operations are deterministic, blue are stochastic, rounded are
continuous, square discrete. The top node is an example state; brightness indicates a value in [0,1].
log EZ∼pθ(z)[pθ(x | Z)] is typically intractable and does not ﬁt into the above framework due to the
expectation being inside the log. The multi-sample variational objective (Burda et al., 2016),
Lm(θ, φ) =
E
Zi∼qφ(z|x)
"
log
 
1
m
m
X
i=1
pθ(Zi, x)
qφ(Zi | x)
!#
.
(8)
provides a convenient alternative which has precisely the form we considered in Section 2.1. This ap-
proach relies on introducing an auxiliary distribution qφ(z | x) with its own parameters, which serves
as approximation to the intractable posterior pθ(z | x). The model is trained by jointly maximizing
the objective w.r.t. to the parameters of p and q. The number of samples used inside the objective m
allows trading off the computational cost against the tightness of the bound. For m = 1, Lm(θ, φ)
becomes is the widely used evidence lower bound (ELBO, Hoffman et al., 2013) on log pθ(x), while
for m > 1, it is known as the importance weighted bound (Burda et al., 2016).
3
THE CONCRETE DISTRIBUTION
3.1
DISCRETE RANDOM VARIABLES AND THE GUMBEL-MAX TRICK
To motivate the construction of Concrete random variables, we review a method for sampling from
discrete distributions called the Gumbel-Max trick (Luce, 1959; Yellott, 1977; Papandreou & Yuille,
2011; Hazan & Jaakkola, 2012; Maddison et al., 2014). We restrict ourselves to a representation of
discrete states as vectors d ∈{0, 1}n of bits that are one-hot, or Pn
k=1 dk = 1. This is a ﬂexible
representation in a computation graph; to achieve an integral representation take the inner product
of d with (1, . . . , n), and to achieve a point mass representation in Rm take Wd where W ∈Rm×n.
Consider an unnormalized parameterization (α1, . . . , αn) where αk ∈(0, ∞) of a discrete distribu-
tion D ∼Discrete(α)—we can assume that states with 0 probability are excluded. The Gumbel-
Max trick proceeds as follows: sample Uk ∼Uniform(0, 1) i.i.d. for each k, ﬁnd k that maximizes
{log αk −log(−log Uk)}, set Dk = 1 and the remaining Di = 0 for i ̸= k. Then
P(Dk = 1) =
αk
Pn
i=1 αi
.
(9)
In other words, the sampling of a discrete random variable can be refactored into a deterministic
function—componentwise addition followed by argmax—of the parameters log αk and ﬁxed dis-
tribution −log(−log Uk). See Figure 1a for a visualization.
The apparently arbitrary choice of noise gives the trick its name, as −log(−log U) has a Gumbel
distribution. This distribution features in extreme value theory (Gumbel, 1954) where it plays a
central role similar to the Normal distribution: the Gumbel distribution is stable under max opera-
tions, and for some distributions, the order statistics (suitably normalized) of i.i.d. draws approach
the Gumbel in distribution. The Gumbel can also be recognized as a −log-transformed exponen-
tial random variable. So, the correctness of (9) also reduces to a well known result regarding the
argmin of exponential random variables. See (Hazan et al., 2016) for a collection of related work,
and particularly the chapter (Maddison, 2016) for a proof and generalization of this trick.
4


---

Published as a conference paper at ICLR 2017
(a) λ = 0
(b) λ = 1/2
(c) λ = 1
(d) λ = 2
Figure 2: A discrete distribution with unnormalized probabilities (α1, α2, α3) = (2, 0.5, 1) and
three corresponding Concrete densities at increasing temperatures λ. Each triangle represents the
set of points (y1, y2, y3) in the simplex ∆2 = {(y1, y2, y3) | yk ∈(0, 1), y1 + y2 + y3 = 1}. For
λ = 0 the size of white circles represents the mass assigned to each vertex of the simplex under the
discrete distribution. For λ ∈{2, 1, 0.5} the intensity of the shading represents the value of pα,λ(y).
3.2
CONCRETE RANDOM VARIABLES
The derivative of the argmax is 0 everywhere except at the boundary of state changes, where it is
undeﬁned. For this reason the Gumbel-Max trick is not a suitable reparameterization for use in SCGs
with AD. Here we introduce the Concrete distribution motivated by considering a graph, which is
the same as Figure 1a up to a continuous relaxation of the argmax computation, see Figure 1b. This
will ultimately allow the optimization of parameters αk via gradients.
The argmax computation returns states on the vertices of the simplex ∆n−1 = {x ∈Rn | xk ∈
[0, 1], Pn
k=1 xk = 1}. The idea behind Concrete random variables is to relax the state of a discrete
variable from the vertices into the interior where it is a random probability vector—a vector of
numbers between 0 and 1 that sum to 1. To sample a Concrete random variable X ∈∆n−1 at
temperature λ ∈(0, ∞) with parameters αk ∈(0, ∞), sample Gk ∼Gumbel i.i.d. and set
Xk =
exp((log αk + Gk)/λ)
Pn
i=1 exp((log αi + Gi)/λ).
(10)
The softmax computation of (10) smoothly approaches the discrete argmax computation as λ →0
while preserving the relative order of the Gumbels log αk + Gk. So, imagine making a series of
forward passes on the graphs of Figure 1. Both graphs return a stochastic value for each forward
pass, but for smaller temperatures the outputs of Figure 1b become more discrete and eventually
indistinguishable from a typical forward pass of Figure 1a.
The distribution of X sampled via (10) has a closed form density on the simplex. Because there may
be other ways to sample a Concrete random variable, we take the density to be its deﬁnition.
Deﬁnition 1 (Concrete Random Variables). Let α ∈(0, ∞)n and λ ∈(0, ∞). X ∈∆n−1 has a
Concrete distribution X ∼Concrete(α, λ) with location α and temperature λ, if its density is:
pα,λ(x) = (n −1)! λn−1
n
Y
k=1
 
αkx−λ−1
k
Pn
i=1 αix−λ
i
!
.
(11)
Proposition 1 lists a few properties of the Concrete distribution. (a) is conﬁrmation that our def-
inition corresponds to the sampling routine (10). (b) conﬁrms that rounding a Concrete random
variable results in the discrete random variable whose distribution is described by the logits log αk,
(c) conﬁrms that taking the zero temperature limit of a Concrete random variable is the same as
rounding. Finally, (d) is a convexity result on the density. We prove these results in Appendix A.
Proposition 1 (Some Properties of Concrete Random Variables). Let X ∼Concrete(α, λ) with
location parameters α ∈(0, ∞)n and temperature λ ∈(0, ∞), then
(a) (Reparameterization) If Gk ∼Gumbel i.i.d., then Xk
d=
exp((log αk+Gk)/λ)
Pn
i=1 exp((log αi+Gi)/λ),
(b) (Rounding) P (Xk > Xi for i ̸= k) = αk/(Pn
i=1 αi),
(c) (Zero temperature) P (limλ→0 Xk = 1) = αk/(Pn
i=1 αi),
5


---

Published as a conference paper at ICLR 2017
(a) λ = 0
(b) λ = 1/2
(c) λ = 1
(d) λ = 2
Figure 3: A visualization of the binary special case. (a) shows the discrete trick, which works by
passing a noisy logit through the unit step function. (b), (c), (d) show Concrete relaxations; the
horizontal blue densities show the density of the input distribution and the vertical densities show
the corresponding Binary Concrete density on (0, 1) for varying λ.
(d) (Convex eventually) If λ ≤(n −1)−1, then pα,λ(x) is log-convex in x.
The binary case of the Gumbel-Max trick simpliﬁes to passing additive noise through a step func-
tion. The corresponding Concrete relaxation is implemented by passing additive noise through a
sigmoid—see Figure 3. We cover this more thoroughly in Appendix B, along with a cheat sheet
(Appendix F) on the density and implementation of all the random variables discussed in this work.
3.3
CONCRETE RELAXATIONS
Concrete random variables may have some intrinsic value, but we investigate them simply as surro-
gates for optimizing a SCG with discrete nodes. When it is computationally feasible to integrate over
the discreteness, that will always be a better choice. Thus, we consider the use case of optimizing a
large graph with discrete stochastic nodes from samples.
First, we outline our proposal for how to use Concrete relaxations by considering a variational
autoencoder with a single discrete latent variable. Let Pa(d) be the mass function of some n-
dimensional one-hot discrete random variable with unnormalized probabilities a ∈(0, ∞)n and
pθ(x|d) some distribution over a data point x given d ∈(0, 1)n one-hot. The generative model is
then pθ,a(x, d) = pθ(x|d)Pa(d). Let Qα(d|x) be an approximating posterior over d ∈(0, 1)n one-
hot whose unnormalized probabilities α(x) ∈(0, ∞)n depend on x. All together the variational
lowerbound we care about stochastically optimizing is
L1(θ, a, α) =
E
D∼Qα(d|x)

log pθ(x|D)Pa(D)
Qα(D|x)

,
(12)
with respect to θ, a, and any parameters of α.
First, we relax the stochastic computation
D ∼Discrete(α(x)) by replacing D with a Concrete random variable Z ∼Concrete(α(x), λ1)
with density qα,λ1(z|x).
Simply replacing every instance of D with Z in Eq.
12 will re-
sult in a non-interpretable objective, which does not necessarily lowerbound log p(x), because
EZ∼qα,λ1(a|x)[−log Qα(Z|x)/Pa(Z)] is not a KL divergence. Thus we propose “relaxing” the
terms Pa(d) and Qα(d|x) to reﬂect the true sampling distribution. Thus, the relaxed objective is:
L1(θ, a, α)
relax
⇝
E
Z∼qα,λ1(z|x)

log pθ(x|Z)pa,λ2(Z)
qα,λ1(Z|x)

(13)
where pa,λ2(z) is a Concrete density with location a and temperature λ2. At test time we evaluate
the discrete lowerbound L1(θ, a, α). Naively implementing Eq. 13 will result in numerical issues.
We discuss this and other details in Appendix C.
Thus, the basic paradigm we propose is the following: during training replace every discrete node
with a Concrete node at some ﬁxed temperature (or with an annealing schedule). The graphs are
identical up to the softmax / argmax computations, so the parameters of the relaxed graph and
discrete graph are the same. When an objective depends on the log-probability of discrete variables
in the SCG, as the variational lowerbound does, we propose that the log-probability terms are also
“relaxed” to represent the true distribution of the relaxed node. At test time the original discrete loss
is evaluated. This is possible, because the discretization of any Concrete distribution has a closed
form mass function, and the relaxation of any discrete distribution into a Concrete distribution has a
closed form density. This is not always possible. For example, the multinomial probit model—the
Gumbel-Max trick with Gaussians replacing Gumbels—does not have a closed form mass.
The success of Concrete relaxations will depend on the choice of temperature during training. It is
important that the relaxed nodes are not able to represent a precise real valued mode in the interior
6


---

Published as a conference paper at ICLR 2017
of the simplex as in Figure 2d. If this is the case, it is possible for the relaxed random variable
to communicate much more than log2(n) bits of information about its α parameters. This might
lead the relaxation to prefer the interior of the simplex to the vertices, and as a result there will be
a large integrality gap in the overall performance of the discrete graph. Therefore Proposition 1
(d) is a conservative guideline for generic n-ary Concrete relaxations; at temperatures lower than
(n −1)−1 we are guaranteed not to have any modes in the interior for any α ∈(0, ∞)n. We discuss
the subtleties of choosing the temperatures in more detail in Appendix C. Ultimately the best choice
of λ and the performance of the relaxation for any speciﬁc n will be an empirical question.
4
RELATED WORK
Perhaps the most common distribution over the simplex is the Dirichlet with density pα(x) ∝
Qn
k=1 xαk−1
k
on x ∈∆n−1. The Dirichlet can be characterized by strong independence proper-
ties, and a great deal of work has been done to generalize it (Connor & Mosimann, 1969; Aitchison,
1985; Rayens & Srinivasan, 1994; Favaro et al., 2011). Of note is the Logistic Normal distribution
(Atchison & Shen, 1980), which can be simulated by taking the softmax of n −1 normal random
variables and an nth logit that is deterministically zero. The Logistic Normal is an important dis-
tribution, because it can effectively model correlations within the simplex (Blei & Lafferty, 2006).
To our knowledge the Concrete distribution does not fall completely into any family of distribu-
tions previously described. For λ ≤1 the Concrete is in a class of normalized inﬁnitely divisible
distributions (S. Favaro, personal communication), and the results of Favaro et al. (2011) apply.
The idea of using a softmax of Gumbels as a relaxation for a discrete random variable was concur-
rently considered by (Jang et al., 2016), where it was called the Gumbel-Softmax. They do not use
the density in the relaxed objective, opting instead to compute all aspects of the graph, including
discrete log-probability computations, with the relaxed stochastic state of the graph. In the case of
variational inference, this relaxed objective is not a lower bound on the marginal likelihood of the
observations, and care needs to be taken when optimizing it. The idea of using sigmoidal functions
with additive input noise to approximate discreteness is also not a new idea. (Frey, 1997) introduced
nonlinear Gaussian units which computed their activation by passing Gaussian noise with the mean
and variance speciﬁed by the input to the unit through a nonlinearity, such as the logistic function.
Salakhutdinov & Hinton (2009) binarized real-valued codes of an autoencoder by adding (Gaussian)
noise to the logits before passing them through the logistic function. Most recently, to avoid the dif-
ﬁculty associated with likelihood-ratio methods (Koˇcisk´y et al., 2016) relaxed the discrete sampling
operation by sampling a vector of Gaussians instead and passing those through a softmax.
There is another family of gradient estimators that have been studied in the context of training
neural networks with discrete units. These are usually collected under the umbrella of straight-
through estimators (Bengio et al., 2013; Raiko et al., 2014). The basic idea they use is passing
forward discrete values, but taking gradients through the expected value. They have good empirical
performance, but have not been shown to be the estimators of any loss function. This is in contrast
to gradients from Concrete relaxations, which are biased with respect to the discrete graph, but
unbiased with respect to the continuous one.
5
EXPERIMENTS
5.1
PROTOCOL
The aim of our experiments was to evaluate the effectiveness of the gradients of Concrete relax-
ations for optimizing SCGs with discrete nodes. We considered the tasks in (Mnih & Rezende,
2016): structured output prediction and density estimation. Both tasks are difﬁcult optimization
problems involving ﬁtting probability distributions with hundreds of latent discrete nodes.
We
compared the performance of Concrete reparameterizations to two state-of-the-art score function
estimators: VIMCO (Mnih & Rezende, 2016) for optimizing the multisample variational objec-
tive (m > 1) and NVIL (Mnih & Gregor, 2014) for optimizing the single-sample one (m = 1).
We performed the experiments using the MNIST and Omniglot datasets. These are datasets of
28 × 28 images of handwritten digits (MNIST) or letters (Omniglot). For MNIST we used the ﬁxed
binarization of Salakhutdinov & Murray (2008) and the standard 50,000/10,000/10,000 split into
7


---

Published as a conference paper at ICLR 2017
MNIST NLL
Omniglot NLL
binary
model
Test
Train
Test
Train
m
Concrete
VIMCO
Concrete
VIMCO
Concrete
VIMCO
Concrete
VIMCO
(200H
– 784V)
1
107.3
104.4
107.5
104.2
118.7
115.7
117.0
112.2
5
104.9
101.9
104.9
101.5
118.0
113.5
115.8
110.8
50
104.3
98.8
104.2
98.3
118.9
113.0
115.8
110.0
(200H
– 200H
– 784V)
1
102.1
92.9
102.3
91.7
116.3
109.2
114.4
104.8
5
99.9
91.7
100.0
90.8
116.0
107.5
113.5
103.6
50
99.5
90.7
99.4
89.7
117.0
108.1
113.9
103.6
(200H
∼784V)
1
92.1
93.8
91.2
91.5
108.4
116.4
103.6
110.3
5
89.5
91.4
88.1
88.6
107.5
118.2
101.4
102.3
50
88.5
89.3
86.4
86.5
108.1
116.0
100.5
100.8
(200H
∼200H
∼784V)
1
87.9
88.4
86.5
85.8
105.9
111.7
100.2
105.7
5
86.3
86.4
84.1
82.5
105.8
108.2
98.6
101.1
50
85.7
85.5
83.1
81.8
106.8
113.2
97.5
95.2
Table 1: Density estimation with binary latent variables. When m = 1, VIMCO stands for NVIL.
training/validation/testing sets. For Omniglot we sampled a ﬁxed binarization and used the stan-
dard 24,345/8,070 split into training/testing sets. We report the negative log-likelihood (NLL) of the
discrete graph on the test data as the performance metric.
All of our models were neural networks with layers of n-ary discrete stochastic nodes with values
on the corners of the hypercube {−1, 1}log2(n). The distributions were parameterized by n real val-
ues log αk ∈R, which we took to be the logits of a discrete random variable D ∼Discrete(α)
with n states. Model descriptions are of the form “(200V–200H∼784V)”, read from left to right.
This describes the order of conditional sampling, again from left to right, with each integer repre-
senting the number of stochastic units in a layer. The letters V and H represent observed and latent
variables, respectively. If the leftmost layer is H, then it was sampled unconditionally from some
parameters. Conditioning functions are described by {–, ∼}, where “–” means a linear function
of the previous layer and “∼” means a non-linear function. A “layer” of these units is simply the
concatenation of some number of independent nodes whose parameters are determined as a function
the previous layer. For example a 240 binary layer is a factored distribution over the {−1, 1}240
hypercube. Whereas a 240 8-ary layer can be seen as a distribution over the same hypercube where
each of the 80 triples of units are sampled independently from an 8 way discrete distribution over
{−1, 1}3. All models were initialized with the heuristic of Glorot & Bengio (2010) and optimized
using Adam (Kingma & Ba, 2014). All temperatures were ﬁxed throughout training. Appendix D
for hyperparameter details.
5.2
DENSITY ESTIMATION
Density estimation, or generative modelling, is the problem of ﬁtting the distribution of data. We
took the latent variable approach described in Section 2.4 and trained the models by optimizing the
variational objective Lm(θ, φ) given by Eq. 8 averaged uniformly over minibatches of data points
x. Both our generative models pθ(z, x) and variational distributions qφ(z | x) were parameterized
with neural networks as described above. We trained models with Lm(θ, φ) for m ∈{1, 5, 50} and
approximated the NLL with L50,000(θ, φ) averaged uniformly over the whole dataset.
The results are shown in Table 1. In general, VIMCO outperformed Concrete relaxations for linear
models and Concrete relaxations outperformed VIMCO for non-linear models. We also tested the
effectiveness of Concrete relaxations on generative models with n-ary layers on the L5(θ, φ) ob-
jective. The best 4-ary model achieved test/train NLL 86.7/83.3, the best 8-ary achieved 87.4/84.6
with Concrete relaxations, more complete results in Appendix E. The relatively poor performance
of the 8-ary model may be because moving from 4 to 8 results in a more difﬁcult objective without
much added capacity. As a control we trained n-ary models using logistic normals as relaxations of
discrete distributions (with retuned temperature hyperparameters). Because the discrete zero tem-
perature limit of logistic Normals is a multinomial probit whose mass function is not known, we
evaluated the discrete model by sampling from the discrete distribution parameterized by the logits
8


---

Published as a conference paper at ICLR 2017
binary
model
Test NLL
Train NLL
m Concrete VIMCO Concrete VIMCO
(392V–240H
–240H–392V)
1
58.5
61.4
54.2
59.3
5
54.3
54.5
49.2
52.7
50
53.4
51.8
48.2
49.6
(392V–240H
–240H–240H
–392V)
1
56.3
59.7
51.6
58.4
5
52.7
53.5
46.9
51.6
50
52.0
50.2
45.9
47.9
100
101
102
λ
101
102
103
NLL
prefers interior
prefers {−1, 1}
Continuous
Discrete
Figure 4: Results for structured prediction on MNIST comparing Concrete relaxations to VIMCO.
When m = 1 VIMCO stands for NVIL. The plot on the right shows the objective (lower is better)
for the continuous and discrete graph trained at temperatures λ. In the shaded region, units prefer to
communicate real values in the interior of (−1, 1) and the discretization suffers an integrality gap.
learned during training. The best 4-ary model achieved test/train NLL of 88.7/85.0, the best 8-ary
model achieved 89.1/85.1.
5.3
STRUCTURED OUTPUT PREDICTION
Structured output prediction is concerned with modelling the high-dimensional distribution of the
observation given a context and can be seen as conditional density estimation. We considered the
task of predicting the bottom half x1 of an image of an MNIST digit given its top half x2, as
introduced by Raiko et al. (2014). We followed Raiko et al. (2014) in using a model with layers of
discrete stochastic units between the context and the observation. Conditioned on the top half x2 the
network samples from a distribution pφ(z | x2) over layers of stochastic units z then predicts x1 by
sampling from a distribution pθ(x1 | z). The training objective for a single pair (x1, x2) is
LSP
m (θ, φ) =
E
Zi∼pφ(z|x2)
"
log
 
1
m
m
X
i=1
pθ(x1 | Zi)
!#
.
This objective is a special case of Lm(θ, φ) (Eq. 8) where we use the prior pφ(z|x2) as the variational
distribution. Thus, the objective is a lower bound on log pθ,φ(x1 | x2).
We trained the models by optimizing LSP
m (θ, φ) for m ∈{1, 5, 50} averaged uniformly over mini-
batches and evaluated them by computing LSP
100(θ, φ) averaged uniformly over the entire dataset. The
results are shown in Figure 4. Concrete relaxations more uniformly outperformed VIMCO in this
instance. We also trained n-ary (392V–240H–240H–240H–392V) models on the LSP
1 (θ, φ) objec-
tive using the best temperature hyperparameters from density estimation. 4-ary achieved a test/train
NLL of 55.4/46.0 and 8-ary achieved 54.7/44.8. As opposed to density estimation, increasing arity
uniformly improved the models. We also investigated the hypothesis that for higher temperatures
Concrete relaxations might prefer the interior of the interval to the boundary points {−1, 1}. Figure
4 was generated with binary (392V–240H–240H–240H–392V) model trained on LSP
1 (θ, φ).
6
CONCLUSION
We introduced the Concrete distribution, a continuous relaxation of discrete random variables. The
Concrete distribution is a new distribution on the simplex with a closed form density parameterized
by a vector of positive location parameters and a positive temperature. Crucially, the zero temper-
ature limit of every Concrete distribution corresponds to a discrete distribution, and any discrete
distribution can be seen as the discretization of a Concrete one. The application we considered was
training stochastic computation graphs with discrete stochastic nodes. The gradients of Concrete
relaxations are biased with respect to the original discrete objective, but they are low variance un-
biased estimators of a continuous surrogate objective. We showed in a series of experiments that
stochastic nodes with Concrete distributions can be used effectively to optimize the parameters of
a stochastic computation graph with discrete stochastic nodes. We did not ﬁnd that annealing or
automatically tuning the temperature was important for these experiments, but it remains interesting
and possibly valuable future work.
9


---

Published as a conference paper at ICLR 2017
ACKNOWLEDGMENTS
We thank Jimmy Ba for the excitement and ideas in the early days, Stefano Favarro for some analysis
of the distribution. We also thank Gabriel Barth-Maron and Roger Grosse.
REFERENCES
Mart´ın Abadi, Ashish Agarwal, Paul Barham, Eugene Brevdo, Zhifeng Chen, Craig Citro, Greg S.
Corrado, Andy Davis, Jeffrey Dean, Matthieu Devin, Sanjay Ghemawat, Ian Goodfellow, Andrew
Harp, Geoffrey Irving, Michael Isard, Yangqing Jia, Rafal Jozefowicz, Lukasz Kaiser, Manjunath
Kudlur, Josh Levenberg, Dan Man´e, Rajat Monga, Sherry Moore, Derek Murray, Chris Olah,
Mike Schuster, Jonathon Shlens, Benoit Steiner, Ilya Sutskever, Kunal Talwar, Paul Tucker, Vin-
cent Vanhoucke, Vijay Vasudevan, Fernanda Vi´egas, Oriol Vinyals, Pete Warden, Martin Watten-
berg, Martin Wicke, Yuan Yu, and Xiaoqiang Zheng. TensorFlow: Large-scale machine learning
on heterogeneous systems, 2015. URL http://tensorflow.org/. Software available from
tensorﬂow.org.
J Aitchison. A general class of distributions on the simplex. Journal of the Royal Statistical Society.
Series B (Methodological), pp. 136–146, 1985.
J Atchison and Sheng M Shen. Logistic-normal distributions: Some properties and uses. Biometrika,
67(2):261–272, 1980.
Yoshua Bengio, Nicholas L´eonard, and Aaron Courville.
Estimating or propagating gradients
through stochastic neurons for conditional computation. arXiv preprint arXiv:1308.3432, 2013.
David Blei and John Lafferty. Correlated topic models. 2006.
Yuri Burda, Roger Grosse, and Ruslan Salakhutdinov. Importance weighted autoencoders. ICLR,
2016.
Robert J Connor and James E Mosimann. Concepts of independence for proportions with a gener-
alization of the dirichlet distribution. Journal of the American Statistical Association, 64(325):
194–206, 1969.
Stefano Favaro, Georgia Hadjicharalambous, and Igor Pr¨unster. On a class of distributions on the
simplex. Journal of Statistical Planning and Inference, 141(9):2987 – 3004, 2011.
Brendan Frey. Continuous sigmoidal belief networks trained using slice sampling. In NIPS, 1997.
Michael C Fu. Gradient estimation. Handbooks in operations research and management science,
13:575–616, 2006.
Xavier Glorot and Yoshua Bengio. Understanding the difﬁculty of training deep feedforward neural
networks. In Aistats, volume 9, pp. 249–256, 2010.
Peter W Glynn. Likelihood ratio gradient estimation for stochastic systems. Communications of the
ACM, 33(10):75–84, 1990.
Alex Graves, Greg Wayne, Malcolm Reynolds, Tim Harley, Ivo Danihelka, Agnieszka Grabska-
Barwi´nska, Sergio G´omez Colmenarejo, Edward Grefenstette, Tiago Ramalho, John Agapiou,
et al. Hybrid computing using a neural network with dynamic external memory. Nature, 538
(7626):471–476, 2016.
Evan Greensmith, Peter L. Bartlett, and Jonathan Baxter. Variance reduction techniques for gradient
estimates in reinforcement learning. JMLR, 5, 2004.
Edward Grefenstette, Karl Moritz Hermann, Mustafa Suleyman, and Phil Blunsom. Learning to
transduce with unbounded memory. In Advances in Neural Information Processing Systems, pp.
1828–1836, 2015.
Karol Gregor, Ivo Danihelka, Andriy Mnih, Charles Blundell, and Daan Wierstra. Deep autoregres-
sive networks. arXiv preprint arXiv:1310.8499, 2013.
Karol Gregor, Ivo Danihelka, Alex Graves, Danilo Jimenez Rezende, and Daan Wierstra. Draw: A
recurrent neural network for image generation. arXiv preprint arXiv:1502.04623, 2015.
Shixiang Gu, Sergey Levine, Ilya Sutskever, and Andriy Mnih. MuProp: Unbiased backpropagation
for stochastic neural networks. ICLR, 2016.
Emil Julius Gumbel. Statistical theory of extreme values and some practical applications: a series
of lectures. Number 33. US Govt. Print. Ofﬁce, 1954.
Tamir Hazan and Tommi Jaakkola. On the partition function and random maximum a-posteriori
perturbations. In ICML, 2012.
10


---

Published as a conference paper at ICLR 2017
Tamir Hazan, George Papandreou, and Daniel Tarlow. Perturbation, Optimization, and Statistics.
MIT Press, 2016.
Matthew D Hoffman, David M Blei, Chong Wang, and John William Paisley. Stochastic variational
inference. JMLR, 14(1):1303–1347, 2013.
E. Jang, S. Gu, and B. Poole. Categorical Reparameterization with Gumbel-Softmax. ArXiv e-prints,
November 2016.
Diederik Kingma and Jimmy Ba. Adam: A method for stochastic optimization. arXiv preprint
arXiv:1412.6980, 2014.
Diederik P Kingma and Max Welling.
Auto-encoding variational bayes.
arXiv preprint
arXiv:1312.6114, 2013.
Diederik P Kingma and Max Welling. Auto-encoding variational bayes. ICLR, 2014.
Tom´aˇs Koˇcisk´y, G´abor Melis, Edward Grefenstette, Chris Dyer, Wang Ling, Phil Blunsom, and
Karl Moritz Hermann.
Semantic parsing with semi-supervised sequential autoencoders.
In
EMNLP, 2016.
R. Duncan Luce. Individual Choice Behavior: A Theoretical Analysis. New York: Wiley, 1959.
Chris J Maddison. A Poisson process model for Monte Carlo. In Tamir Hazan, George Papandreou,
and Daniel Tarlow (eds.), Perturbation, Optimization, and Statistics, chapter 7. MIT Press, 2016.
Chris J Maddison, Daniel Tarlow, and Tom Minka. A∗Sampling. In NIPS, 2014.
Andriy Mnih and Karol Gregor. Neural variational inference and learning in belief networks. In
ICML, 2014.
Andriy Mnih and Danilo Jimenez Rezende. Variational inference for monte carlo objectives. In
ICML, 2016.
Volodymyr Mnih, Nicolas Heess, Alex Graves, and koray kavukcuoglu. Recurrent Models of Visual
Attention. In NIPS, 2014.
Christian A Naesseth, Francisco JR Ruiz, Scott W Linderman, and David M Blei. Rejection sam-
pling variational inference. arXiv preprint arXiv:1610.05683, 2016.
John William Paisley, David M. Blei, and Michael I. Jordan. Variational bayesian inference with
stochastic search. In ICML, 2012.
George Papandreou and Alan L Yuille. Perturb-and-map random ﬁelds: Using discrete optimization
to learn and sample from energy models. In ICCV, 2011.
Tapani Raiko, Mathias Berglund, Guillaume Alain, and Laurent Dinh. Techniques for learning
binary stochastic feedforward neural networks. arXiv preprint arXiv:1406.2989, 2014.
Rajesh Ranganath, Sean Gerrish, and David M. Blei. Black box variational inference. In AISTATS,
2014.
William S Rayens and Cidambi Srinivasan. Dependence properties of generalized liouville distri-
butions on the simplex. Journal of the American Statistical Association, 89(428):1465–1470,
1994.
Danilo Jimenez Rezende, Shakir Mohamed, and Daan Wierstra. Stochastic backpropagation and
approximate inference in deep generative models. In ICML, 2014.
Francisco JR Ruiz, Michalis K Titsias, and David M Blei.
The generalized reparameterization
gradient. arXiv preprint arXiv:1610.02287, 2016.
Ruslan Salakhutdinov and Geoffrey Hinton. Semantic hashing. International Journal of Approxi-
mate Reasoning, 50(7):969–978, 2009.
Ruslan Salakhutdinov and Iain Murray. On the quantitative analysis of deep belief networks. In
ICML, 2008.
John Schulman, Nicolas Heess, Theophane Weber, and Pieter Abbeel. Gradient estimation using
stochastic computation graphs. In NIPS, 2015.
Theano Development Team. Theano: A Python framework for fast computation of mathematical
expressions. arXiv e-prints, abs/1605.02688, May 2016. URL http://arxiv.org/abs/
1605.02688.
Michalis Titsias and Miguel L´azaro-Gredilla. Doubly stochastic variational bayes for non-conjugate
inference. In Tony Jebara and Eric P. Xing (eds.), ICML, 2014.
11


---

Published as a conference paper at ICLR 2017
Michalis Titsias and Miguel L´azaro-Gredilla. Local expectation gradients for black box variational
inference. In NIPS, 2015.
Ronald J Williams. Simple statistical gradient-following algorithms for connectionist reinforcement
learning. Machine learning, 8(3-4):229–256, 1992.
Kelvin Xu, Jimmy Ba, Ryan Kiros, Kyunghyun Cho, Aaron Courville, Ruslan Salakhudinov, Rich
Zemel, and Yoshua Bengio. Show, attend and tell: Neural image caption generation with visual
attention. In ICML, 2015.
John I Yellott. The relationship between luce’s choice axiom, thurstone’s theory of comparative
judgment, and the double exponential distribution. Journal of Mathematical Psychology, 15(2):
109–144, 1977.
A
PROOF OF PROPOSITION 1
Let X ∼Concrete(α, λ) with location parameters α ∈(0, ∞)n and temperature λ ∈(0, ∞).
1. Let Gk ∼Gumbel i.i.d., consider
Yk =
exp((log αk + Gk)/λ)
Pn
i=1 exp((log αi + Gi)/λ)
Let Zk = log αk + Gk, which has density
αk exp(−zk) exp(−αk exp(−zk))
We will consider the invertible transformation
F(z1, . . . , zn) = (y1, . . . , yn−1, c)
where
yk = exp(zk/λ)c−1
c =
n
X
i=1
exp(zi/λ)
then
F −1(y1, . . . , yn−1, c) = (λ(log y1 + log c), . . . , λ(log yn−1 + log c), λ(log yn + log c))
where yn = 1 −Pn−1
i=1 yi. This has Jacobian


λy−1
1
0
0
0
. . .
0
λc−1
0
λy−1
2
0
0
. . .
0
λc−1
0
0
λy−1
3
0
. . .
0
λc−1
...
−λy−1
n
−λy−1
n
−λy−1
n
−λy−1
n
. . .
−λy−1
n
λc−1


by adding yi/yn times each of the top n−1 rows to the bottom row we see that this Jacobian
has the same determinant as


λy−1
1
0
0
0
. . .
0
λc−1
0
λy−1
2
0
0
. . .
0
λc−1
0
0
λy−1
3
0
. . .
0
λc−1
...
0
0
0
0
. . .
0
λ(cyn)−1


and thus the determinant is equal to
λn
c Qk
i=1 yi
12


---

Published as a conference paper at ICLR 2017
all together we have the density
λn Qn
k=1 αk exp(−λ log yk −λ log c) exp(−αk exp(−λ log yk −λ log c))
c Qn
i=1 yi
with r = log c change of variables we have density
λn Qn
k=1 αk exp(−λr) exp(−αk exp(−λ log yk −λr))
Qn
i=1 yλ+1
i
=
λn Qn
k=1 αk
Qn
i=1 yλ+1
i
exp(−nλr) exp(−
n
X
i=1
αi exp(−λ log yi −λr)) =
letting γ = log(Pn
n=1 αky−λ
k )
λn Qn
k=1 αk
Qn
i=1 yλ+1
i
exp(γ)
exp(−nλr + γ) exp(−exp(−λr + γ)) =
integrating out r
λn Qn
k=1 αk
Qn
i=1 yλ+1
i
exp(γ)
exp(−γn + γ)Γ(n)
λ

=
λn−1 Qn
k=1 αk
Qn
i=1 yλ+1
i
(exp(−γn)Γ(n)) =
(n −1)!λn−1
Qn
k=1 αky−λ−1
k
(Pn
n=1 αky−λ
k )n
Thus Y
d= X.
2. Follows directly from (a) and the Gumbel-Max trick (Maddison, 2016).
3. Follows directly from (a) and the Gumbel-Max trick (Maddison, 2016).
4. Let λ ≤(n −1)−1. The density of X can be rewritten as
pα,λ(x) ∝
n
Y
k=1
αky−λ−1
Pn
i=1 αiy−λ
i
=
n
Y
k=1
αkyλ(n−1)−1
k
Pn
i=1 αi
Q
j̸=i yλ
j
Thus, the log density is up to an additive constant C
log pα,λ(x) =
n
X
k=1
(λ(n −1) −1) log yk −n log


n
X
k=1
αk
Y
j̸=k
yλ
j

+ C
If λ ≤(n −1)−1, then the ﬁrst n terms are convex, because −log is convex. For the
last term, −log is convex and non-increasing and Q
j̸=k yλ
j is concave for λ ≤(n −1)−1.
Thus, their composition is convex. The sum of convex terms is convex, ﬁnishing the proof.
B
THE BINARY SPECIAL CASE
Bernoulli random variables are an important special case of discrete distributions taking states in
{0, 1}. Here we consider the binary special case of the Gumbel-Max trick from Figure 1a along
with the corresponding Concrete relaxation.
Let D ∼Discrete(α) for α ∈(0, ∞)2 be a two state discrete random variable on {0, 1}2 such that
D1 + D2 = 1, parameterized as in Figure 1a by α1, α2 > 0:
P(D1 = 1) =
α1
α1 + α2
(14)
13


---

Published as a conference paper at ICLR 2017
The distribution is degenerate, because D1 = 1 −D2. Therefore we consider just D1. Under
the Gumbel-Max reparameterization, the event that D1 = 1 is the event that {G1 + log α1 >
G2 + log α2} where Gk ∼Gumbel i.i.d. The difference of two Gumbels is a Logistic distribution
G1 −G2 ∼Logistic, which can be sampled in the following way, G1 −G2
d= log U −log(1 −U)
where U ∼Uniform(0, 1). So, if α = α1/α2, then we have
P(D1 = 1) = P(G1 + log α1 > G2 + log α2) = P(log U −log(1 −U) + log α > 0)
(15)
Thus, D1
d= H(log α + log U −log(1 −U)), where H is the unit step function.
Correspondingly, we can consider the Binary Concrete relaxation that results from this process.
As in the n-ary case, we consider the sampling routine for a Binary Concrete random variable
X ∈(0, 1) ﬁrst. To sample X, sample L ∼Logistic and set
X =
1
1 + exp(−(log α + L)/λ)
(16)
We deﬁne the Binary Concrete random variable X by its density on the unit interval.
Deﬁnition 2 (Binary Concrete Random Variables). Let α ∈(0, ∞) and λ ∈(0, ∞). X ∈(0, 1)
has a Binary Concrete distribution X ∼BinConcrete(α, λ) with location α and temperature λ, if
its density is:
pα,λ(x) = λαx−λ−1(1 −x)−λ−1
(αx−λ + (1 −x)−λ)2 .
(17)
We state without proof the special case of Proposition 1 for Binary Concrete distributions
Proposition
2
(Some
Properties
of
Binary
Concrete
Random
Variables).
Let
X
∼
BinConcrete(α, λ) with location parameter α ∈(0, ∞) and temperature λ ∈(0, ∞), then
(a) (Reparameterization) If L ∼Logistic, then X
d=
1
1+exp(−(log α+L)/λ),
(b) (Rounding) P (X > 0.5) = α/(1 + α),
(c) (Zero temperature) P (limλ→0 X = 1) = α/(1 + α),
(d) (Convex eventually) If λ ≤1, then pα,λ(x) is log-convex in x.
We can generalize the binary circuit beyond Logistic random variables. Consider an arbitrary ran-
dom variable X with inﬁnite support on R. If Φ : R →[0, 1] is the CDF of X, then
P(H(X) = 1) = 1 −Φ(0)
If we want this to have a Bernoulli distribution with probability α/(1+α), then we should solve the
equation
1 −Φ(0) =
α
1 + α.
This gives Φ(0) = 1/(1+α), which can be accomplished by relocating the random variable Y with
CDF Φ to be X = Y −Φ−1(1/(1 + α)).
C
USING CONCRETE RELAXATIONS
In this section we include some tips for implementing and using the Concrete distribution as a
relaxation. We use the following notation
σ(x) =
1
1 + exp(−x)
n
LΣE
k=1 {xk} = log
 n
X
k=1
exp(xk)
!
Both sigmoid and log-sum-exp are common operations in libraries like TensorFlow or theano.
14


---

Published as a conference paper at ICLR 2017
C.1
THE BASIC PROBLEM
For the sake of exposition, we consider a simple variational autoencoder with a single discrete
random variable and objective L1(θ, a, α) given by Eq. 8 for a single data point x. This scenario
will allow us to discuss all of the decisions one might make when using Concrete relaxations.
In particular, let Pa(d) be the mass function of some n-dimensional one-hot discrete D ∼
Discrete(a) with a ∈(0, ∞)n, let pθ(x|d) be some likelihood (possibly computed by a neural
network), which is a continuous function of d and parameters θ, let D ∼Discrete(α(x)) be a one-
hot discrete random variable in (0, 1)n whose unnormalized probabilities α(x) ∈(0, ∞)n are some
function (possible a neural net with its own parameters) of x. Let Qα(d|x) be the mass function of
D. Then, we care about optimizing
L1(θ, a, α) =
E
D∼Qα(d|x)

log pθ(x|D)Pa(D)
Qα(D|x)

(18)
with respect to θ, a, and any parameters in α from samples of the SCG required to simulate an
estimator of L1(θ, a, α).
C.2
WHAT YOU MIGHT RELAX AND WHY
The ﬁrst consideration when relaxing an estimator of Eq. 18 is how to relax the stochastic computa-
tion. The only sampling required to simulate L1(θ, a, α) is D ∼Discrete(α(x)). The correspond-
ing Concrete relaxation is to sample Z ∼Concrete(α(x), λ1) with temperature λ1 and location
parameters are the the unnormalized probabilities α(x) of D. Let density qα,λ1(z|x) be the density
of Z. We get a relaxed objective of the form:
E
D∼Qα(d|x) [ · ] →
E
Z∼qα,λ1(z|x) [ · ]
(19)
This choice allows us to take derivatives through the stochastic computaitons of the graph.
The second consideration is which objective to put in place of [ · ] in Eq. 19. We will consider
the ideal scenario irrespective of numerical issues. In Subsection C.3 we address those numerical
issues. The central question is how to treat the expectation of the ratio Pa(D)/Qα(D|x) (which is
the KL component of the loss) when Z replaces D.
There are at least three options for how to modify the objective. They are, (20) replace the discrete
mass with Concrete densities, (21) relax the computation of the discrete log mass, (22) replace it
with the analytic discrete KL.
E
Z∼qα,λ1(z|x)

log pθ(x|Z) + log pa,λ2(Z)
qα,λ1(Z|x)

(20)
E
Z∼qα,λ1(z|x)
"
log pθ(x|Z) +
n
X
i=1
Zi log
Pa(d(i))
Qα(d(i)|x)
#
(21)
E
Z∼qα,λ1(z|x) [log pθ(x|Z)] +
n
X
i=1
Qα(d(i)|x) log
Pa(d(i))
Qα(d(i)|x)
(22)
where d(i) is a one-hot binary vector with d(i)
i
= 1 and pa,λ2(z) is the density of some Concrete
random variable with temperature λ2 with location parameters a. Although (22) or (21) is tempting,
we emphasize that these are NOT necessarily lower bounds on log p(x) in the relaxed model. (20)
is the only objective guaranteed to be a lower bound:
E
Z∼qα,λ1(z|x)

log pθ(x|Z) + log pa,λ2(Z)
qα,λ1(Z|x)

≤log
Z
pθ(x|z)pa,λ2(z) dx.
(23)
For this reason we consider objectives of the form (20). Choosing (22) or (21) is possible, but the
value of these objectives is not interpretable and one should early stop otherwise it will overﬁt to
the spurious “KL” component of the loss. We now consider practical issues with (20) and how to
address them. All together we can interpret qα,λ1(z|x) as the Concrete relaxation of the variational
posterior and pa,λ2(z) the relaxation of the prior.
15


---

Published as a conference paper at ICLR 2017
C.3
WHICH RANDOM VARIABLE TO TREAT AS THE STOCHASTIC NODE
When implementing a SCG like the variational autoencoder example, we need to compute log-
probabilities of Concrete random variables. This computation can suffer from underﬂow, so where
possible it’s better to take a different node on the relaxed graph as the stochastic node on which log-
likelihood terms are computed. For example, it’s tempting in the case of Concrete random variables
to treat the Gumbels as the stochastic node on which the log-likelihood terms are evaluated and
the softmax as downstream computation. This will be a looser bound in the context of variational
inference than the corresponding bound when treating the Concrete relaxed states as the node.
The solution we found to work well was to work with Concrete random variables in log-space.
Consider the following vector in Rn for location parameters α ∈(0, ∞)n and λ ∈(0, ∞) and
Gk ∼Gumbel,
Yk = log αk + Gk
λ
−
n
LΣE
i=1
log αi + Gi
λ

Y
∈
Rn has the property that exp(Y )
∼
Concrete(α, λ), therefore we call Y
an
ExpConcrete(α, λ). The advantage of this reparameterization is that the KL terms of a varia-
tional loss are invariant under invertible transformation. exp is invertible, so the KL between two
ExpConcrete random variables is the same as the KL between two Concrete random variables. The
log-density log κα,λ(y) of an ExpConcrete(α, λ) is also simple to compute:
log κα,λ(y) = log((n −1)!) + (n −1) log λ +
 n
X
k=1
log αk −λyk
!
−n
n
LΣE
k=1 {log αk −λyk}
for y ∈Rn such that LΣEn
k=1{yk} = 0. Note that the sample space of the ExpConcrete dis-
tribution is still interpretable in the zero temperature limit. In the limit of λ →0 ExpConcrete
random variables become discrete random variables over the one-hot vectors of d ∈{−∞, 0}n
where LΣEn
k=1{dk} = 0. exp(Y ) in this case results in the one-hot vectors in {0, 1}n.
C.3.1
n-ARY CONCRETE
Returning to our initial task of relaxing L1(θ, a, α), let Y ∼ExpConcrete(α(x), λ1) with density
κα,λ1(y|x) be the ExpConcrete latent variable corresponding to the Concrete relaxation qα,λ1(z|x)
of the variational posterior Qα(d|x). Let ρa,λ1(y) be the density of an ExpConcrete random variable
corresponding to the Concrete relaxation pa,λ2(z) of Pa(d). All together we can see that
E
Z∼qα,λ1(z|x)

log pθ(x|Z) + log pa,λ2(Z)
qα,λ1(Z|x)

=
E
Y ∼κα,λ1(y|x)

log pθ(x| exp(Y )) + log ρa,λ2(Y )
κα,λ1(Y |x)

(24)
Therefore, we used ExpConcrete random variables as the stochastic nodes and treated exp as a
downstream computation. The relaxation is then,
L1(θ, a, α)
relax
⇝
E
Y ∼κα,λ1(y|x)

log pθ(x| exp(Y )) + log ρa,λ2(Y )
κα,λ1(Y |x)

,
(25)
and the objective on the RHS is fully reparameterizable and what we chose to optimize.
C.3.2
BINARY CONCRETE
In the binary case, the logistic function is invertible, so it makes most sense to treat the logit plus
noise as the stochastic node. In particular, the binary random node was sample from:
Y = log α + log U −log(1 −U)
λ
(26)
where U ∼Uniform(0, 1) and always followed by σ as downstream computation. log U −log(1 −
U) is a Logistic random variable, details in the cheat sheet, and so the log-density log gα,λ(y) of this
node (before applying σ) is
log gα,λ(y) = log λ −λy + log α −2 log(1 + exp(−λy + log α))
16


---

Published as a conference paper at ICLR 2017
All together the relaxation in the binary special case would be
L1(θ, a, α)
relax
⇝
E
Y ∼gα,λ1(y|x)

log pθ(x|σ(Y )) + log fa,λ2(Y )
gα,λ1(Y |x)

,
(27)
where fa,λ2(y) is the density of a Logistic random variable sampled via Eq. 26 with location a and
temperature λ2.
This section had a dense array of densities, so we summarize the relevant ones, along with how to
sample from them, in Appendix F.
C.4
CHOOSING THE TEMPERATURE
The success of Concrete relaxations will depend heavily on the choice of temperature during train-
ing. It is important that the relaxed nodes are not able to represent a precise real valued mode
in the interior of the simplex as in Figure 2d. For example, choosing additive Gaussian noise
ϵ ∼Normal(0, 1) with the logistic function σ(x) to get relaxed Bernoullis of the form σ(ϵ + µ)
will result in a large mode in the centre of the interval. This is because the tails of the Gaussian
distribution drop off much faster than the rate at which σ squashes. Even including a temperature
parameter does not completely solve this problem; the density of σ((ϵ + µ)/λ) at any temperature
still goes to 0 as its approaches the boundaries 0 and 1 of the unit interval. Therefore (d) of Proposi-
tion 1 is a conservative guideline for generic n-ary Concrete relaxations; at temperatures lower than
(n −1)−1 we are guaranteed not to have any modes in the interior for any α ∈(0, ∞)n. In the case
of the Binary Concrete distribution, the tails of the Logistic additive noise are balanced with the
logistic squashing function and for temperatures λ ≤1 the density of the Binary Concrete distribu-
tion is log-convex for all parameters α, see Figure 3b. Still, practice will often disagree with theory
here. The peakiness of the Concrete distribution increases with n, so much higher temperatures are
tolerated (usually necessary).
For n = 1 temperatures λ ≤(n −1)−1 is a good guideline. For n > 1 taking λ ≤(n −1)−1 is
not necessarily a good guideline, although it will depend on n and the speciﬁc application. As
n →∞the Concrete distribution becomes peakier, because the random normalizing constant
Pn
k=1 exp((log αk + Gk)/λ) grows. This means that practically speaking the optimization can
tolerate much higher temperatures than (n −1)−1. We found in the cases n = 4 that λ = 1 was the
best temperature and in n = 8, λ = 2/3 was the best. Yet λ = 2/3 was the best single perform-
ing temperature across the n ∈{2, 4, 8} cases that we considered. We recommend starting in that
ball-park and exploring for any speciﬁc application.
When the loss depends on a KL divergence between two Concrete nodes, it’s possible to give the
nodes distinct temperatures. We found this to improve results quite dramatically. In the context of
our original problem and it’s relaxation:
L1(θ, a, α)
relax
⇝
E
Y ∼κα,λ1(y|x)

log pθ(x| exp(Y )) + log ρa,λ2(Y )
κα,λ1(Y |x)

,
(28)
Both λ1 for the posterior temperature and λ2 for the prior temperature are tunable hyperparameters.
D
EXPERIMENTAL DETAILS
The basic model architectures we considered are exactly analogous to those in Burda et al. (2016)
with Concrete/discrete random variables replacing Gaussians.
D.1
— VS ∼
The conditioning functions we used were either linear or non-linear. Non-linear consisted of two
tanh layers of the same size as the preceding stochastic layer in the computation graph.
D.2
n-ARY LAYERS
All our models are neural networks with layers of n-ary discrete stochastic nodes with log2(n)-
dimensional states on the corners of the hypercube {−1, 1}log2(n).
For a generic n-ary node
17


---

Published as a conference paper at ICLR 2017
sampling proceeds as follows. Sample a n-ary discrete random variable D ∼Discrete(α) for
α ∈(0, ∞)n. If C is the log2(n)×n matrix, which lists the corners of the hypercube {−1, 1}log2(n)
as columns, then we took Y = CD as downstream computation on D. The corresponding Con-
crete relaxation is to take X ∼Concrete(α, λ) for some ﬁxed temperature λ ∈(0, ∞) and set
˜Y = CX. For the binary case, this amounts to simply sampling U ∼Uniform(0, 1) and taking
Y = 2H(log U −log(1 −U) + log α) −1. The corresponding Binary Concrete relaxation is
˜Y = 2σ((log U −log(1 −U) + log α)/λ) −1.
D.3
BIAS INITIALIZATION
All biases were initialized to 0 with the exception of the biases in the prior decoder distribution over
the 784 or 392 observed units. These were initialized to the logit of the base rate averaged over the
respective dataset (MNIST or Omniglot).
D.4
CENTERING
We also found it beneﬁcial to center the layers of the inference network during training. The activity
in (−1, 1)d of each stochastic layer was centered during training by maintaining a exponentially
decaying average with rate 0.9 over minibatches. This running average was subtracted from the
activity of the layer before it was updated. Gradients did not ﬂow throw this computation, so it
simply amounted to a dynamic offset. The averages were not updated during the evaluation.
D.5
HYPERPARAMETER SELECTION
All models were initialized with the heuristic of Glorot & Bengio (2010) and optimized using Adam
(Kingma & Ba, 2014) with parameters β1 = 0.9, β2 = 0.999 for 107 steps on minibatches of size
64. Hyperparameters were selected on the MNIST dataset by grid search taking the values that
performed best on the validation set. Learning rates were chosen from {10−4, 3 · 10−4, 10−3} and
weight decay from {0, 10−2, 10−1, 1}. Two sets of hyperparameters were selected, one for linear
models and one for non-linear models. The linear models’ hyperparameters were selected with
the 200H–200H–784V density model on the L5(θ, φ) objective. The non-linear models’ hyperpa-
rameters were selected with the 200H∼200H∼784V density model on the L5(θ, φ) objective. For
density estimation, the Concrete relaxation hyperparameters were (weight decay = 0, learning rate
= 3 · 10−4) for linear and (weight decay = 0, learning rate = 10−4) for non-linear. For structured
prediction Concrete relaxations used (weight decay = 10−3, learning rate = 3 · 10−4).
In addition to tuning learning rate and weight decay, we tuned temperatures for the Concrete relax-
ations on the density estimation task. We found it valuable to have different values for the prior
and posterior distributions, see Eq. 28. In particular, for binary we found that (prior λ2 = 1/2,
posterior λ1 = 2/3) was best, for 4-ary we found (prior λ2 = 2/3, posterior λ1 = 1) was best, and
(prior λ2 = 2/5, posterior λ1 = 2/3) for 8-ary. No temperature annealing was used. For structured
prediction we used just the corresponding posterior λ1 as the temperature for the whole graph, as
there was no variational posterior.
We performed early stopping when training with the score function estimators (VIMCO/NVIL) as
they were much more prone to overﬁtting.
18


---

Published as a conference paper at ICLR 2017
E
EXTRA RESULTS
MNIST NLL
Omniglot NLL
m
Test
Train
Test
Train
binary
(240H
∼784V)
1
91.9
90.7
108.0
102.2
5
89.0
87.1
107.7
100.0
50
88.4
85.7
109.0
99.1
4-ary
(240H
∼784V)
1
91.4
89.7
110.7
1002.7
5
89.4
87.0
110.5
100.2
50
89.7
86.5
113.0
100.0
8-ary
(240H
∼784V)
1
92.5
89.9
119.61
105.3
5
90.5
87.0
120.7
102.7
50
90.5
86.7
121.7
101.0
binary
(240H∼240H
∼784V)
1
87.9
86.0
106.6
99.0
5
86.6
83.7
106.9
97.1
50
86.0
82.7
108.7
95.9
4-ary
(240H∼240H
∼784V)
1
87.4
85.0
106.6
97.8
5
86.7
83.3
108.3
97.3
50
86.7
83.0
109.4
96.8
8-ary
(240H∼240H
∼784V)
1
88.2
85.9
111.3
102.5
5
87.4
84.6
110.5
100.5
50
87.2
84.0
111.1
99.5
Table 2: Density estimation using Concrete relaxations with distinct arity of layers.
19


---

Published as a conference paper at ICLR 2017
F
CHEAT SHEET
σ(x) =
1
1 + exp(−x)
n
LΣE
k=1 {xk} = log
 n
X
k=1
exp(xk)
!
log ∆n−1 =

x ∈Rn | xk ∈(−∞, 0),
n
LΣE
k=1 {xk} = 0

Distribution and Domains
Reparameterization/How To Sample
Mass/Density
G ∼Gumbel
G ∈R
G
d= −log(−log(U))
exp(−g −exp(−g))
L ∼Logistic
L ∈R
L
d= log(U) −log(1 −U)
exp(−l)
(1 + exp(−l))2
X ∼Logistic(µ, λ)
µ ∈R
λ ∈(0, ∞)
X
d= L + µ
λ
λ exp(−λx + µ)
(1 + exp(−λx + µ))2
X ∼Bernoulli(α)
X ∈{0, 1}
α ∈(0, ∞)
X
d=
1
if L + log α ≥0
0
otherwise
α
1 + α if x = 1
X ∼BinConcrete(α, λ)
X ∈(0, 1)
α ∈(0, ∞)
λ ∈(0, ∞)
X
d= σ((L + log α)/λ)
λαx−λ−1(1 −x)−λ−1
(αx−λ + (1 −x)−λ)2
X ∼Discrete(α)
X ∈{0, 1}n
Pn
k=1 Xk = 1
α ∈(0, ∞)n
Xk
d=
1
if log αk + Gk > log αi + Gi for i ̸= k
0
otherwise
αk
Pn
i=1 αi
if xk = 1
X ∼Concrete(α, λ)
X ∈∆n−1
α ∈(0, ∞)n
λ ∈(0, ∞)
Xk
d=
exp((log αk + Gk)/λ)
Pn
i=1 exp((log αk + Gi)/λ)
(n −1)!
λ−(n−1)
n
Y
k=1
αkx−λ−1
k
Pn
i=1 αix−λ
i
X ∼ExpConcrete(α, λ)
X ∈log ∆n−1
α ∈(0, ∞)n
λ ∈(0, ∞)
Xk
d= log αk + Gk
λ
−
n
LΣE
i=1
log αi + Gi
λ

(n −1)!
λ−(n−1)
n
Y
k=1
αk exp(−λxk)
Pn
i=1 αi exp(−λxi)
Table 3: Cheat sheet for the random variables we use in this work. Note that some of these are
atypical parameterizations, particularly the Bernoulli and Logistic random variables. The table only
assumes that you can sample uniform random numbers U ∼Uniform(0, 1). From there on it may
deﬁne random variables and reuse them later on. For example, L ∼Logistic is deﬁned in the
second row, and after that point L represents a Logistic random variable that can be replaced by
log U −log(1 −U). Whenever random variables are indexed, e.g. Gk, they represent separate
independent calls to a random number generator.
20
