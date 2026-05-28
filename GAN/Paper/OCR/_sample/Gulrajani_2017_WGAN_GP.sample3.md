Improved Training of Wasserstein GANs
Ishaan Gulrajani1∗, Faruk Ahmed1, Martin Arjovsky2, Vincent Dumoulin1, Aaron Courville1,3
1 Montreal Institute for Learning Algorithms
2 Courant Institute of Mathematical Sciences
3 CIFAR Fellow
igul222@gmail.com
{faruk.ahmed,vincent.dumoulin,aaron.courville}@umontreal.ca
ma4371@nyu.edu
Abstract
Generative Adversarial Networks (GANs) are powerful generative models, but
suffer from training instability. The recently proposed Wasserstein GAN (WGAN)
makes progress toward stable training of GANs, but sometimes can still generate
only poor samples or fail to converge. We find that these problems are often due
to the use of weight clipping in WGAN to enforce a Lipschitz constraint on the
critic, which can lead to undesired behavior. We propose an alternative to clipping
weights: penalize the norm of gradient of the critic with respect to its input. Our
proposed method performs better than standard WGAN and enables stable training of a wide variety of GAN architectures with almost no hyperparameter tuning,
including 101-layer ResNets and language models with continuous generators.
We also achieve high quality generations on CIFAR-10 and LSUN bedrooms. †
1
Introduction
Generative Adversarial Networks (GANs) [9] are a powerful class of generative models that cast
generative modeling as a game between two networks: a generator network produces synthetic data
given some noise source and a discriminator network discriminates between the generator's output
and true data. GANs can produce very visually appealing samples, but are often hard to train, and
much of the recent work on the subject [23, 19, 2, 21] has been devoted to finding ways of stabilizing
training. Despite this, consistently stable training of GANs remains an open problem.
In particular, [1] provides an analysis of the convergence properties of the value function being
optimized by GANs. Their proposed alternative, named Wasserstein GAN (WGAN) [2], leverages
the Wasserstein distance to produce a value function which has better theoretical properties than the
original. WGAN requires that the discriminator (called the critic in that work) must lie within the
space of 1-Lipschitz functions, which the authors enforce through weight clipping.
Our contributions are as follows:
1. On toy datasets, we demonstrate how critic weight clipping can lead to undesired behavior.
2. We propose gradient penalty (WGAN-GP), which does not suffer from the same problems.
3. We demonstrate stable training of varied GAN architectures, performance improvements
over weight clipping, high-quality image generation, and a character-level GAN language
model without any discrete sampling.
∗Now at Google Brain
†Code for our models is available at https://github.com/igul222/improved_wgan_training.
arXiv:1704.00028v3 [cs.LG] 25 Dec 2017


---

2
Background
2.1
Generative adversarial networks
The GAN training strategy is to define a game between two competing networks. The generator
network maps a source of noise to the input space. The discriminator network receives either a
generated sample or a true data sample and must distinguish between the two. The generator is
trained to fool the discriminator.
Formally, the game between the generator G and the discriminator D is the minimax objective:
min
G max
D
E
x∼Pr[log(D(x))] +
E
˜x∼Pg[log(1 −D(˜x))],
(1)
where Pr is the data distribution and Pg is the model distribution implicitly defined by ˜x =
G(z), z ∼p(z) (the input z to the generator is sampled from some simple noise distribution
p, such as the uniform distribution or a spherical Gaussian distribution).
If the discriminator is trained to optimality before each generator parameter update, then minimizing the value function amounts to minimizing the Jensen-Shannon divergence between Pr and Pg
[9], but doing so often leads to vanishing gradients as the discriminator saturates. In practice, [9]
advocates that the generator be instead trained to maximize E˜x∼Pg[log(D(˜x))], which goes some
way to circumvent this difficulty. However, even this modified loss function can misbehave in the
presence of a good discriminator [1].
2.2
Wasserstein GANs
[2] argues that the divergences which GANs typically minimize are potentially not continuous with
respect to the generator's parameters, leading to training difficulty. They propose instead using
the Earth-Mover (also called Wasserstein-1) distance W(q, p), which is informally defined as the
minimum cost of transporting mass in order to transform the distribution q into the distribution p
(where the cost is mass times transport distance). Under mild assumptions, W(q, p) is continuous
everywhere and differentiable almost everywhere.
The WGAN value function is constructed using the Kantorovich-Rubinstein duality [25] to obtain
min
G max
D∈D
E
x∼Pr

D(x)

−
E
˜x∼Pg

D(˜x))

(2)
where D is the set of 1-Lipschitz functions and Pg is once again the model distribution implicitly
defined by ˜x = G(z), z ∼p(z). In that case, under an optimal discriminator (called a critic in the
paper, since it's not trained to classify), minimizing the value function with respect to the generator
parameters minimizes W(Pr, Pg).
The WGAN value function results in a critic function whose gradient with respect to its input is
better behaved than its GAN counterpart, making optimization of the generator easier. Empirically,
it was also observed that the WGAN value function appears to correlate with sample quality, which
is not the case for GANs [2].
To enforce the Lipschitz constraint on the critic, [2] propose to clip the weights of the critic to lie
within a compact space [−c, c]. The set of functions satisfying this constraint is a subset of the
k-Lipschitz functions for some k which depends on c and the critic architecture. In the following
sections, we demonstrate some of the issues with this approach and propose an alternative.
2.3
Properties of the optimal WGAN critic
In order to understand why weight clipping is problematic in a WGAN critic, as well as to motivate
our approach, we highlight some properties of the optimal critic in the WGAN framework. We prove
these in the Appendix.
2


---

Proposition 1. Let Pr and Pg be two distributions in X, a compact metric space. Then, there is a
1-Lipschitz function f ∗which is the optimal solution of max∥f∥L≤1 Ey∼Pr[f(y)] −Ex∼Pg[f(x)].
Let π be the optimal coupling between Pr and Pg, defined as the minimizer of: W(Pr, Pg) =
infπ∈Π(Pr,Pg) E(x,y)∼π [∥x −y∥] where Π(Pr, Pg) is the set of joint distributions π(x, y) whose
marginals are Pr and Pg, respectively. Then, if f ∗is differentiable‡, π(x = y) = 0§, and xt =
tx + (1 −t)y with 0 ≤t ≤1, it holds that P(x,y)∼π
h
∇f ∗(xt) =
y−xt
∥y−xt∥
i
= 1.
Corollary 1. f ∗has gradient norm 1 almost everywhere under Pr and Pg.
3
Difficulties with weight constraints
We find that weight clipping in WGAN leads to optimization difficulties, and that even when optimization succeeds the resulting critic can have a pathological value surface. We explain these
problems below and demonstrate their effects; however we do not claim that each one always occurs
in practice, nor that they are the only such mechanisms.
Our experiments use the specific form of weight constraint from [2] (hard clipping of the magnitude
of each weight), but we also tried other weight constraints (L2 norm clipping, weight normalization),
as well as soft constraints (L1 and L2 weight decay) and found that they exhibit similar problems.
To some extent these problems can be mitigated with batch normalization in the critic, which [2]
use in all of their experiments. However even with batch normalization, we observe that very deep
WGAN critics often fail to converge.
8 Gaussians
25 Gaussians
Swiss Roll
(a) Value surfaces of WGAN critics trained to optimality on toy datasets using (top) weight clipping
and (bottom) gradient penalty. Critics trained with
weight clipping fail to capture higher moments of the
data distribution. The 'generator' is held fixed at the
real data plus Gaussian noise.
13
10
7
4
1
Discriminator layer
−20
−10
0
10
Gradient norm (log scale)
Weight clipping (c = 0.001)
Weight clipping (c = 0.01)
Weight clipping (c = 0.1)
Gradient penalty
−0.02
−0.01
0.00
0.01
0.02
Weights
Weight clipping
−0.50
−0.25
0.00
0.25
0.50
Weights
Gradient penalty
(b) (left) Gradient norms of deep WGAN critics during training on the Swiss Roll dataset either explode
or vanish when using weight clipping, but not when
using a gradient penalty. (right) Weight clipping (top)
pushes weights towards two values (the extremes of
the clipping range), unlike gradient penalty (bottom).
Figure 1: Gradient penalty in WGANs does not exhibit undesired behavior like weight clipping.
3.1
Capacity underuse
Implementing a k-Lipshitz constraint via weight clipping biases the critic towards much simpler
functions. As stated previously in Corollary 1, the optimal WGAN critic has unit gradient norm
almost everywhere under Pr and Pg; under a weight-clipping constraint, we observe that our neural
network architectures which try to attain their maximum gradient norm k end up learning extremely
simple functions.
To demonstrate this, we train WGAN critics with weight clipping to optimality on several toy distributions, holding the generator distribution Pg fixed at the real distribution plus unit-variance Gaussian noise. We plot value surfaces of the critics in Figure 1a. We omit batch normalization in the
‡We can actually assume much less, and talk only about directional derivatives on the direction of the line;
which we show in the proof always exist. This would imply that in every point where f ∗is differentiable (and
thus we can take gradients in a neural network setting) the statement holds.
§This assumption is in order to exclude the case when the matching point of sample x is x itself. It is
satisfied in the case that Pr and Pg have supports that intersect in a set of measure 0, such as when they are
supported by two low dimensional manifolds that don't perfectly align [1].
3
