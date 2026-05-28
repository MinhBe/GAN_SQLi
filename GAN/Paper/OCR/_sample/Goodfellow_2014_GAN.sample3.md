Generative Adversarial Nets
Ian J. Goodfellow, Jean Pouget-Abadie∗, Mehdi Mirza, Bing Xu, David Warde-Farley,
Sherjil Ozair†, Aaron Courville, Yoshua Bengio‡
D´epartement d'informatique et de recherche op´erationnelle
Universit´e de Montr´eal
Montr´eal, QC H3C 3J7
Abstract
We propose a new framework for estimating generative models via an adversarial process, in which we simultaneously train two models: a generative model G
that captures the data distribution, and a discriminative model D that estimates
the probability that a sample came from the training data rather than G. The training procedure for G is to maximize the probability of D making a mistake. This
framework corresponds to a minimax two-player game. In the space of arbitrary
functions G and D, a unique solution exists, with G recovering the training data
distribution and D equal to 1
2 everywhere. In the case where G and D are defined
by multilayer perceptrons, the entire system can be trained with backpropagation.
There is no need for any Markov chains or unrolled approximate inference networks during either training or generation of samples. Experiments demonstrate
the potential of the framework through qualitative and quantitative evaluation of
the generated samples.
1
Introduction
The promise of deep learning is to discover rich, hierarchical models [2] that represent probability
distributions over the kinds of data encountered in artificial intelligence applications, such as natural
images, audio waveforms containing speech, and symbols in natural language corpora. So far, the
most striking successes in deep learning have involved discriminative models, usually those that
map a high-dimensional, rich sensory input to a class label [14, 22]. These striking successes have
primarily been based on the backpropagation and dropout algorithms, using piecewise linear units
[19, 9, 10] which have a particularly well-behaved gradient . Deep generative models have had less
of an impact, due to the difficulty of approximating many intractable probabilistic computations that
arise in maximum likelihood estimation and related strategies, and due to difficulty of leveraging
the benefits of piecewise linear units in the generative context. We propose a new generative model
estimation procedure that sidesteps these difficulties. 1
In the proposed adversarial nets framework, the generative model is pitted against an adversary: a
discriminative model that learns to determine whether a sample is from the model distribution or the
data distribution. The generative model can be thought of as analogous to a team of counterfeiters,
trying to produce fake currency and use it without detection, while the discriminative model is
analogous to the police, trying to detect the counterfeit currency. Competition in this game drives
both teams to improve their methods until the counterfeits are indistiguishable from the genuine
articles.
∗Jean Pouget-Abadie is visiting Universit´e de Montr´eal from Ecole Polytechnique.
†Sherjil Ozair is visiting Universit´e de Montr´eal from Indian Institute of Technology Delhi
‡Yoshua Bengio is a CIFAR Senior Fellow.
1All code and hyperparameters available at http://www.github.com/goodfeli/adversarial
1
arXiv:1406.2661v1 [stat.ML] 10 Jun 2014


---

This framework can yield specific training algorithms for many kinds of model and optimization
algorithm. In this article, we explore the special case when the generative model generates samples
by passing random noise through a multilayer perceptron, and the discriminative model is also a
multilayer perceptron. We refer to this special case as adversarial nets. In this case, we can train
both models using only the highly successful backpropagation and dropout algorithms [17] and
sample from the generative model using only forward propagation. No approximate inference or
Markov chains are necessary.
2
Related work
An alternative to directed graphical models with latent variables are undirected graphical models
with latent variables, such as restricted Boltzmann machines (RBMs) [27, 16], deep Boltzmann
machines (DBMs) [26] and their numerous variants.
The interactions within such models are
represented as the product of unnormalized potential functions, normalized by a global summation/integration over all states of the random variables. This quantity (the partition function) and
its gradient are intractable for all but the most trivial instances, although they can be estimated by
Markov chain Monte Carlo (MCMC) methods. Mixing poses a significant problem for learning
algorithms that rely on MCMC [3, 5].
Deep belief networks (DBNs) [16] are hybrid models containing a single undirected layer and several directed layers. While a fast approximate layer-wise training criterion exists, DBNs incur the
computational difficulties associated with both undirected and directed models.
Alternative criteria that do not approximate or bound the log-likelihood have also been proposed,
such as score matching [18] and noise-contrastive estimation (NCE) [13]. Both of these require the
learned probability density to be analytically specified up to a normalization constant. Note that
in many interesting generative models with several layers of latent variables (such as DBNs and
DBMs), it is not even possible to derive a tractable unnormalized probability density. Some models
such as denoising auto-encoders [30] and contractive autoencoders have learning rules very similar
to score matching applied to RBMs. In NCE, as in this work, a discriminative training criterion is
employed to fit a generative model. However, rather than fitting a separate discriminative model, the
generative model itself is used to discriminate generated data from samples a fixed noise distribution.
Because NCE uses a fixed noise distribution, learning slows dramatically after the model has learned
even an approximately correct distribution over a small subset of the observed variables.
Finally, some techniques do not involve defining a probability distribution explicitly, but rather train
a generative machine to draw samples from the desired distribution. This approach has the advantage
that such machines can be designed to be trained by back-propagation. Prominent recent work in this
area includes the generative stochastic network (GSN) framework [5], which extends generalized
denoising auto-encoders [4]: both can be seen as defining a parameterized Markov chain, i.e., one
learns the parameters of a machine that performs one step of a generative Markov chain. Compared
to GSNs, the adversarial nets framework does not require a Markov chain for sampling. Because
adversarial nets do not require feedback loops during generation, they are better able to leverage
piecewise linear units [19, 9, 10], which improve the performance of backpropagation but have
problems with unbounded activation when used ina feedback loop. More recent examples of training
a generative machine by back-propagating into it include recent work on auto-encoding variational
Bayes [20] and stochastic backpropagation [24].
3
Adversarial nets
The adversarial modeling framework is most straightforward to apply when the models are both
multilayer perceptrons. To learn the generator's distribution pg over data x, we define a prior on
input noise variables pz(z), then represent a mapping to data space as G(z; θg), where G is a
differentiable function represented by a multilayer perceptron with parameters θg. We also define a
second multilayer perceptron D(x; θd) that outputs a single scalar. D(x) represents the probability
that x came from the data rather than pg. We train D to maximize the probability of assigning the
correct label to both training examples and samples from G. We simultaneously train G to minimize
log(1 −D(G(z))):
2


---

In other words, D and G play the following two-player minimax game with value function V (G, D):
min
G max
D V (D, G) = Ex∼pdata(x)[log D(x)] + Ez∼pz(z)[log(1 −D(G(z)))].
(1)
In the next section, we present a theoretical analysis of adversarial nets, essentially showing that
the training criterion allows one to recover the data generating distribution as G and D are given
enough capacity, i.e., in the non-parametric limit. See Figure 1 for a less formal, more pedagogical
explanation of the approach. In practice, we must implement the game using an iterative, numerical
approach. Optimizing D to completion in the inner loop of training is computationally prohibitive,
and on finite datasets would result in overfitting. Instead, we alternate between k steps of optimizing
D and one step of optimizing G. This results in D being maintained near its optimal solution, so
long as G changes slowly enough. This strategy is analogous to the way that SML/PCD [31, 29]
training maintains samples from a Markov chain from one learning step to the next in order to avoid
burning in a Markov chain as part of the inner loop of learning. The procedure is formally presented
in Algorithm 1.
In practice, equation 1 may not provide sufficient gradient for G to learn well. Early in learning,
when G is poor, D can reject samples with high confidence because they are clearly different from
the training data. In this case, log(1 −D(G(z))) saturates. Rather than training G to minimize
log(1 −D(G(z))) we can train G to maximize log D(G(z)). This objective function results in the
same fixed point of the dynamics of G and D but provides much stronger gradients early in learning.
x
z
...
(a)
(b)
(c)
(d)
Figure 1: Generative adversarial nets are trained by simultaneously updating the discriminative distribution
(D, blue, dashed line) so that it discriminates between samples from the data generating distribution (black,
dotted line) px from those of the generative distribution pg (G) (green, solid line). The lower horizontal line is
the domain from which z is sampled, in this case uniformly. The horizontal line above is part of the domain
of x. The upward arrows show how the mapping x = G(z) imposes the non-uniform distribution pg on
transformed samples. G contracts in regions of high density and expands in regions of low density of pg. (a)
Consider an adversarial pair near convergence: pg is similar to pdata and D is a partially accurate classifier.
(b) In the inner loop of the algorithm D is trained to discriminate samples from data, converging to D∗(x) =
pdata(x)
pdata(x)+pg(x). (c) After an update to G, gradient of D has guided G(z) to flow to regions that are more likely
to be classified as data. (d) After several steps of training, if G and D have enough capacity, they will reach a
point at which both cannot improve because pg = pdata. The discriminator is unable to differentiate between
the two distributions, i.e. D(x) = 1
2.
4
Theoretical Results
The generator G implicitly defines a probability distribution pg as the distribution of the samples
G(z) obtained when z ∼pz. Therefore, we would like Algorithm 1 to converge to a good estimator
of pdata, if given enough capacity and training time. The results of this section are done in a nonparametric setting, e.g. we represent a model with infinite capacity by studying convergence in the
space of probability density functions.
We will show in section 4.1 that this minimax game has a global optimum for pg = pdata. We will
then show in section 4.2 that Algorithm 1 optimizes Eq 1, thus obtaining the desired result.
3
