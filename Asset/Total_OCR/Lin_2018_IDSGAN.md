Sample-Eﬃcient Imitation Learning via Generative Adversarial Nets
Lionel Blondé
lionel.blonde@etu.unige.ch
Alexandros Kalousis
alexandros.kalousis@hesge.ch
University of Geneva, Switzerland
Geneva School of Business Administration, HES-SO
Abstract
GAIL is a recent successful imitation learn-
ing architecture that exploits the adversar-
ial training procedure introduced in GANs.
Albeit successful at generating behaviours
similar to those demonstrated to the agent,
GAIL suﬀers from a high sample complexity
in the number of interactions it has to carry
out in the environment in order to achieve
satisfactory performance. We dramatically
shrink the amount of interactions with the
environment necessary to learn well-behaved
imitation policies, by up to several orders of
magnitude. Our framework, operating in the
model-free regime, exhibits a signiﬁcant in-
crease in sample-eﬃciency over previous meth-
ods by simultaneously a) learning a self-tuned
adversarially-trained surrogate reward and b)
leveraging an oﬀ-policy actor-critic architec-
ture. We show that our approach is simple
to implement and that the learned agents
remain remarkably stable, as shown in our
experiments that span a variety of continuous
control tasks. Video visualisations available
at: https://youtu.be/-nCsqUJnRKU.
1
Introduction
Reinforcement learning (RL) is a powerful and exten-
sive framework enabling a learner to tackle complex con-
tinuous control tasks (Sutton and Barto, 1998). Lever-
aging strong function approximators such as multi-layer
neural networks, deep reinforcement learning alleviates
the customary preliminary workload consisting in hand-
crafting relevant features for the learning agent to work
on. While being freed from this engineering burden
Proceedings of the 22nd International Conference on Ar-
tiﬁcial Intelligence and Statistics (AISTATS) 2019, Naha,
Okinawa, Japan. PMLR: Volume 89. Copyright 2019 by
the author(s).
opens up the framework to an even broader range of
complex control and planning tasks, RL remains hin-
dered by its reliance on reward design, referred to as
reward shaping. Albeit appealing in theory, shaping
often requires an intimidating amount of engineering
via trial and error to yield natural-looking behaviours
and makes the system prone to premature convergence
to local minima (Ng et al., 1999).
Imitation learning breaks free from the preliminary
reward function hand-crafting step as it does not need
access to a reinforcement signal. Instead, imitation
learning learns to perform a task directly from ex-
pert demonstrations. The emerging policies mimic the
behaviour displayed by the expert in those demonstra-
tions. Learning from demonstrations (LfD) has enabled
signiﬁcant advances in robotics (Billard et al., 2008)
and autonomous driving (Pomerleau, 1989, 1990). Such
models were ﬁt from the expert demonstrations alone
in a supervised fashion, without gathering new data
in simulation. Albeit eﬃcient when data is abundant,
they tend to be frail as the agent strays from the expert
trajectories. The ensuing compounding of errors causes
a covariate shift (Ross and Bagnell, 2010; Ross et al.,
2011). This approach, referred to as behavioral cloning,
is therefore poorly adapted for imitation. Those limita-
tions stem from the sequential nature of the problem.
The caveats of behavioral cloning have recently been
successfully addressed by Ho and Ermon (Ho and Er-
mon, 2016) who introduced a model-free imitation
learning method called Generative Adversarial Imi-
tation Learning (GAIL). Leveraging Generative Adver-
sarial Networks (GAN) (Goodfellow et al., 2014), GAIL
alleviates the limitations of the supervised approach
by a) learning a reward surrogate that explains the
behaviour shown in the demonstrations and b) follow-
ing an RL procedure in an inner loop, consisting in
performing rollouts in a simulated environment with
the learned surrogate as reinforcement signal. Several
works have built on GAIL to overcome the weaknesses
it inherits from GANs, with a particular emphasis on
avoiding mode collapse (Li et al., 2017; Hausman et al.,
2017; Kueﬂer and Kochenderfer, 2017), causing policies
arXiv:1809.02064v3  [cs.LG]  8 Mar 2019


---

Sample-Eﬃcient Imitation Learning via Generative Adversarial Nets
to fail at displaying the diversity of demonstrated be-
haviours or skills (Goodfellow, 2017). However, as the
authors point out in the original paper ((Ho and Ermon,
2016), Section 7), GAIL suﬀers from severe sample
ineﬃciency. It is this limitation of GAIL that we ad-
dress in this paper. “Sample-eﬃcient” here means that
we focus on limiting the number of agent-environment
interactions, in contrast with reducing the number of
demonstrations needed by the agent. Although learning
from fewer demonstrations is not the primary focus of
this work, our experiments span a spectrum of demon-
stration dataset sizes.
Failures of previous works to address the exceeding
sample complexity stems from the on-policy nature
of the RL procedure they employ. In such methods,
every interaction in a given rollout typically is used
to compute the Monte Carlo estimate of the state
value by summing the rewards accumulated during
the current trajectory. The experienced transitions are
then discarded. Holding on to past trajectories to carry
out more than a single optimization step might appear
viable but often results in destructively large policy
updates (Schulman et al., 2017). Gradients based on
those estimates therefore suﬀer from high variance,
which can be reduced by sampling more intensively,
hence the deterring sample complexity.
In this work, we introduce a novel method that suc-
cessfully addresses the impeding sample ineﬃciency in
the number of simulator queries suﬀered by previous
methods. By designing an oﬀ-policy learning proce-
dure relying on the use of retained past experiences, we
considerably shrink the amount of interactions neces-
sary to learn good imitation policies. Despite involving
an adversarial training procedure and an actor-critic
method, both notorious for being prone to instabili-
ties and prohibitively diﬃcult to train, our technique
demonstrates consistent stability, as shown in the ex-
perimental section. Additionally, our reliance on the
deterministic policy gradients allows us to exploit fur-
ther information about the learned reward function,
such as its gradient. Previous methods either ignore it
by treating the reward signal as a scalar in a model-free
fashion or train a forward model to exploit it. Our
method achieves the best of both worlds as it can per-
form a backward pass from the discriminator to the
generator (policy) while remaining model-free.
2
Related Work
Imitation learning aims to learn how to perform tasks
solely from expert demonstrations. Two approaches are
typically adopted to tackle imitation learning problems:
a) behavioral cloning (BC) (Pomerleau, 1989, 1990),
which learns a policy via regression on the state-action
pairs from the expert trajectories, and b) apprentice-
ship learning (AL) (Abbeel and Ng, 2004), which posits
the existence of some unknown reward function under
which the expert policy is optimal and learns a policy
by i) recovering the reward that the expert is assumed
to maximise (an approach called inverse reinforcement
learning (IRL)) and ii) running an RL procedure with
this recovered signal. As a supervised approach, BC is
limited to the available demonstrations to learn a re-
gression model, whose predictions worsen dramatically
as the agent strays from the demonstrated trajectories.
It then becomes increasingly diﬃcult for the model to
recover as the errors compound (Ross and Bagnell, 2010;
Ross et al., 2011; Bagnell, 2015). Only the presence
of correcting behaviour in the demonstration dataset
can allow BC to produce robust policies. AL allevi-
ates this weakness by entangling learning the reward
function and learning the mimicking policy, leveraging
the return of the latter to adjust the parameters of
the former. Models are trained on traces of interaction
with the environment rather than on a ﬁxed state pool,
leading to greater generalization to states absent from
the demonstrations. Albeit preventing errors from com-
pounding, IRL comes with a high computational cost,
as both modelling the reward function and solving the
ensuing RL problem (per learning iteration) can be re-
source intensive (Syed et al., 2008; Syed and Schapire,
2008; Ho et al., 2016; Levine et al., 2011).
In an attempt to overcome the shortcomings of IRL, Ho
and Ermon (Ho and Ermon, 2016) managed to bypass
the need for learning the reward function assumed to
have been optimised by the expert when collecting the
demonstrations. The proposed approach to AL, Gen-
erative Adversarial Imitation Learning (GAIL), relies
on an essential step consisting in learning a surrogate
function measuring the similarity between the learned
policy and the expert policy, using Generative Adver-
sarial Networks (GAN) (Goodfellow et al., 2014). The
learned similarity metric is then employed as a reward
proxy to carry out the RL step, inherent to the AL
scheme. Recently, connections have been drawn be-
tween GANs, RL (Pfau and Vinyals, 2016) and IRL
(Finn et al., 2016). In this work, we extend GAIL to fur-
ther exploit the connections between those frameworks
and overcome a limitation that was left unaddressed:
the burdensome sample ineﬃciency of the method.
GANs involve a generator and a discriminator, each
represented by a neural network, making the associated
computational graph fully diﬀerentiable. The gradient
of the discriminator with respect to the output of the
generator is of primary importance as it indicates how
the generator should change its output to have better
chances at fooling the discriminator at the next itera-
tion. In GAIL, the generator’s role is carried out by


---

Lionel Blondé, Alexandros Kalousis
a stochastic policy, causing the computational graph
to no longer be diﬀerentiable end-to-end. Following a
model-based approach, (Baram et al., 2017) recovers
the gradient of the discriminator with respect to ac-
tions (via reparametrization tricks) and with respect
to states (via a forward model), making the compu-
tational graph fully diﬀerentiable.
In contrast, the
method introduced in this work can, by operating over
deterministic policies and leveraging the deterministic
policy gradient theorem (Silver et al., 2014), directly
wield the gradient of the discriminator with respect
to the actions, without requiring gradient estimation
techniques (e.g. reparametrization trick (Kingma and
Welling, 2013), Gumbel-Softmax trick (Jang et al.,
2017; Maddison et al., 2017)). Since we stick to the
model-free setting, states remain stochastic nodes and
therefore block (backward) gradient ﬂows.
An independent endeavour to overcome the data inef-
ﬁciency of GAIL has very recently been reported in
(Kostrikov et al., 2018), in which the authors leverage
a similar architecture, yet rely on an arguably ad-hoc
preliminary preprocessing technique on the demonstra-
tions before the imitation begins.
In contrast, our
method does not rely on any preprocessing to yield
gains in sample eﬃciency by orders of magnitude.
3
Background
Setting
We address the problem of an agent learn-
ing to act in an environment in order to reproduce
the behaviour of an expert demonstrator. No direct
supervision is provided to the agent — she is never
directly told what the optimal action is — nor does she
receives a reinforcement signal from the environment
upon interaction. Instead, the agent is provided with
a pool of trajectories and must use them to guide its
learning process.
Preliminaries
We model this sequential interac-
tive problem over discrete timesteps as a Markov
decision process (MDP) M, formalised as a tuple
(S, A, ρ0, p, r, γ).
S and A respectively denote the
state and action spaces. The dynamics are deﬁned
by a transition distribution with conditional density
p(st+1|st, at), along with ρ0, the density of the distri-
bution from which the initial state is sampled. Finally,
γ ∈(0, 1] denotes the discount factor and r : S×A →R
the reward function.
We consider only the fully-
observable case, in which the current state can be
described with the current observation ot = st, allevi-
ating the need to involve the entire history of obser-
vations. Although our results are presented following
the previous inﬁnite-horizon MDP, the MDPs involved
in our experiments are episodic, with γ = 0 at episode
termination. In the theory, whenever we omit the dis-
count factor, we implicitly assume the existence of an
absorbing state along any agent-generated trajectory.
We formalise the sequential decision making process of
the agent by deﬁning a parameterised policy πθ, mod-
elled via a neural network with parameter θ. πθ(at|st)
designates the conditional probability density concen-
trated at action at when the agent is in state st. In line
with our setting, the agent interacts with M−, an MDP
comprising every element of M except its reward func-
tion r. Since our approach involves learning a surrogate
reward function, we use M+ to denote the MDP re-
sulting from the augmentation of M−with the learned
reward. We can therefore equivalently assume that
the agent interacts with M+. Trajectories are traces
of interaction between an agent and an MDP. Speciﬁ-
cally, we model trajectories as sequences of transitions
(st, at, rt, st+1), atomic units of interaction. Demon-
strations are provided to the agent through a set of
expert trajectories τe, generated by an expert policy
πe in M.
We now introduce additional concepts and notations
that will be used in the remainder of this work. The
return is the total discounted reward from timestep t
onwards: Rγ
t ≜P+∞
k=t γk−tr(sk, ak). The state-action
value, or Q-value, is the expected return after pick-
ing action at in state st, and thereafter following pol-
icy πθ: Qπθ(st, at) ≜E>t
πθ [Rγ
t ], where E>t
πθ [·] denotes
the expectation taken along trajectories generated
by πθ in M+ (respectively E>t
πe [·] for πe in M) and
looking onwards from state st and action at.
We
want our agent to ﬁnd a policy πθ that maximises
the expected return from the start state, which con-
stitutes our performance objective, J(π) ≜Eπ[Rγ
0],
i.e. πθ = argmaxπ J(π). To ease further notations,
we ﬁnally introduce the discounted state visitation dis-
tribution of a policy π, denoted by ρπ : S →[0, 1],
and deﬁned by ρπ(s) ≜P+∞
t=0 γtPρ0,π[st = s], where
Pρ0,π[st = s] is the probability of arriving at state s
at time step t when sampling the initial state from ρ0
and thereafter following policy π. In our experiments,
we omit the discount factor for state visitation, in line
with common practices.
Gail
Leveraging Generative Adversarial Networks
(Goodfellow et al., 2014), Generative Adversarial Imi-
tation Learning (Ho and Ermon, 2016) introduces an
extra neural network Dφ to play the role of discrimi-
nator, while the role of generator is carried out by the
agent’s policy πθ. Dφ tries to assert whether a given
state-action pair originates from trajectories of πθ or
πe, while πθ attempts to fool Dφ into believing her
state-action pairs come from πe. The situation can be
described as a minimax problem minθ maxφ V (θ, φ),
where the value of the two-player game is V (θ, φ) ≜


---

Sample-Eﬃcient Imitation Learning via Generative Adversarial Nets
Eπθ[log(1−Dφ(s, a))]+Eπe[log Dφ(s, a)]. We omit the
causal entropy term for brevity. The optimization is
however hindered by the stochasticity of πθ, causing
V (θ, φ) to be non-diﬀerentiable with respect to θ.
The solution proposed in (Ho and Ermon, 2016) con-
sists in alternating between a gradient step (Adam,
(Kingma and Ba, 2014)) on φ to increase V (θ, φ) with
respect to Dφ, and a policy optimization step (TRPO,
(Schulman et al., 2015)) on θ to decrease V (θ, φ) with
respect to πθ. In other words, while Dφ is trained as a
binary classiﬁer to predict if a given state-action pair is
real (from πe) or generated (from πθ), the policy πθ is
trained by being rewarded for successfully confusing Dφ
into believing that generated samples are coming from
πe, and treating this reward as if it were an external
analytically-unknown reward from the environment.
Actor-critic
Policy gradient methods with function
approximation (Sutton et al., 1999), referred to as
actor-critic (AC) methods, interleave policy evaluation
with policy iteration. Policy evaluation estimates the
state-action value function with a function approxima-
tor called critic Qψ ≈Qπθ, usually via either Monte-
Carlo (MC) estimation or Temporal Diﬀerence (TD)
learning. Policy iteration updates the policy πθ by
greedily optimising it against the estimated critic Qψ.
4
Algorithm
The approach in this paper, named Sample-eﬃcient
Adversarial Mimic (Sam), adopts an oﬀ-policy TD
learning paradigm. By storing past experiences and
replaying them in an uncorrelated fashion, Sam dis-
plays signiﬁcant gains in sample-eﬃciency, in line with
(Wang et al., 2016; Gu et al., 2016). To solve the diﬀer-
entiability bottleneck of (Ho and Ermon, 2016) caused
by the stochasticity of its generator, we operate over
deterministic policies. At a given state st, following
its deterministic policy µθ, an agent selects the action
at = µθ(st). Alternatively, we can obtain a determin-
istic policy from any stochastic policy πθ by system-
atically picking the average action for a given state:
µθ(st) = Ea[πθ(a|st)]. By relying on an oﬀ-policy actor-
critic architecture and wielding deterministic policies,
Sam builds on the Deep Deterministic Policy Gradi-
ents (DDPG) algorithm (Lillicrap et al., 2016), in the
context of Imitation Learning.
Sam is composed of three interconnected learning mod-
ules: a reward module (parameter φ), a policy mod-
ule (parameter θ), and a critic module (parameter ψ)
(Figure 1). The reward and policy modules are both
involved in a GAN’s adversarial training procedure,
while the policy and critic modules are trained as an
actor-critic architecture. As reminded recently in (Pfau
and Vinyals, 2016), GANs and actor-critic architectures
can be both framed as bilevel optimization problems,
each involving two competing components, which we
just listed out for both architectures. Interestingly,
the policy module plays a role in both problems, ty-
ing the two bilevel optimization problems together. In
one problem, the policy module is trained against the
reward module, while in the other, the policy mod-
ule is trained against the critic module. The reward
and critic modules can therefore be seen as serving
analogous roles in their respective bilevel optimization
problems: forging and maintaining a signal which en-
ables the reward-seeking policy to adopt the desired
behaviour. How each of these component is optimised
is described in the subsequent dedicated sections.
Figure 1: Inter-module relationships in diﬀerent neu-
ral architectures (the scope of this ﬁgure was inspired
from (Pfau and Vinyals, 2016)). Modules with distinct
loss functions are depicted with empty circles, while
ﬁlled circles designate environmental entities. Solid
and dotted arrows respectively represent (forward) ﬂow
of information and (backward) ﬂow of gradient. a)
Generative Adversarial Imitation Learning (Ho and Er-
mon, 2016) b) Actor-Critic architecture (Sutton et al.,
1999) c) Sam (this work). Note that in Sam, the critic
takes in information from the reward module, while
in the vanilla AC architecture, the critic receives the
reward from the environment. The gradient ﬂow from
the critic to the reward module must however be sealed.
Indeed, such a gradient ﬂow would allow the policy to
adjust its parameters to induce values of the reward
which yield low TD residuals, hence preventing both
critic and reward modules to be learned as intended.
As an oﬀ-policy method, Sam cycles through the follow-
ing steps: i) the agent uses πθ to interact with M+, ii)
stores the experienced transitions C in a replay buﬀer


---

Lionel Blondé, Alexandros Kalousis
R, iii) updates the reward module φ with an equal
mixture of uniformly sampled state-action pairs from
C and τe, iv) updates the reward module φ with an
equal mixture of uniformly sampled state-action pairs
from R and τe, and v) updates the policy module θ
and critic module ψ with transitions sampled from R.
Note that while sampling uniformly from C (iii) gives
states and actions distributed as ρπθ and πθ respec-
tively (on-policy), sampling uniformly from R (iv) gives
states and actions distributed as ρβ and β respectively,
where β denotes the oﬀ-policy sampling mixture distri-
bution corresponding to sampling transitions uniformly
from the replay buﬀer. A more detailed description
of the training procedure is laid out in the algorithm
pseudo-code (Algorithm 1).
Reward
We introduce a reward network with pa-
rameter vector φ, operating as the discriminator. The
cross-entropy loss used to train the reward network is:
Eπθ[−log(1 −Dφ(s, a))] + Eπe[−log Dφ(s, a)]
(1)
+ λRGP(φ)
(2)
where RGP(φ) is a penalty on the discriminator gradi-
ent, as introduced in (Gulrajani et al., 2017), Section
4. (Lucic et al., 2017) reports beneﬁts from applying
such regulariser to the non-saturated variant of the
discriminator loss, although it was initially introduced
for Wasserstein GANs (Arjovsky et al., 2017) in (Gul-
rajani et al., 2017). This penalty favours our method
by further improving its stability.
The reward is deﬁned as the negative of the generator
loss. The later has been declined in many variants,
which are thoroughly compared in (Lucic et al., 2017).
We can therefore analogously deﬁne a synthetic reward
for each of these forms. We go over and discuss major
ones in supplementary material. Additionally, (Fu et al.,
2018) proposes an extra variant in the context of IRL. In
the remainder, we use rφ(st, at) = −log(1−Dφ(st, at))
as synthetic reward. The reward network is trained,
each iteration, ﬁrst on the mini-batch most recently
collected by πθ, then on mini-batches sampled from
the replay buﬀer. Although (Pfau and Vinyals, 2016)
reports that using a replay buﬀer in GANs causes the
generation to be poor, we do not seem to suﬀer the
same detrimental eﬀect in the continuous control tasks
we tackle.
Critic
The loss optimised by the critic, noted ℓ(ψ),
involves three components: i) a 1-step Bellman residual
ℓ1(ψ), ii) a n-step Bellman residual ℓn(ψ), and iii) a
weight decay regulariser RWD(ψ). A similar loss is
employed in (Večerík et al., 2017) in the context of
Reinforcement Learning from Demonstrations. While
the authors use weight decay regularisers for both the
policy and the critic, we restrain from decaying the
policy’s weights since, in our setting, the policy plays a
role in two distinct optimization problems. We do not
apply a weight decay regulariser for the discriminator
either, as it was proven to cause the Wasserstein GAN
critic (name given to the discriminator in Wasserstein
GANs) to diverge (Gulrajani et al., 2017).
We deﬁne the critic loss as follows:
ℓ(ψ) = ℓ1(ψ) + ℓn(ψ) + νRWD(ψ)
(3)
where ν is a hyperparameter that determines how much
decay is used. The losses i) and ii) are deﬁned respec-
tively based on the 1-step and n-step lookahead versions
of the Bellman equation,
˜Q1
ψ(st, at) ≜rφ(st, at)
(4)
+ γQψ(st+1, µθ(st+1))
(5)
˜Qn
ψ(st, at) ≜
n−1
X
k=0
γkrφ(st+k, at+k)
(6)
+ γnQψ(st+n, µθ(st+n))
(7)
yielding the critic losses:
ℓ1(ψ) ≜Est∼ρβ,at∼β[( ˜Q1
ψ −Qψ)2(st, at)]
(8)
ℓn(ψ) ≜Est∼ρβ,at∼β[( ˜Qn
ψ −Qψ)2(st, at)]
(9)
where Est∼ρβ,,at∼β[·] signiﬁes that transitions are sam-
pled from the replay buﬀer R, using in eﬀect the oﬀ-
policy distribution β. Both Qψ and ˜Q·
ψ ((5), (7)) de-
pend on ψ, which might cause severe instability. In
order to prevent the critic from diverging, we use sepa-
rate target networks for both policy and critic (θ′, ψ′)
to calculate ˜Q·
ψ, which slowly track the learned param-
eters (θ, ψ). In line with results exhibited in the recent
ablation study (Rainbow (Hessel et al., 2017)) assess-
ing the inﬂuence of the various add-ons of DQN (Mnih
et al., 2013, 2015) on its performance, we studied the
inﬂuence of two add-ons that were transposable to Sam:
longer TD backups and replay prioritisation. n-step
returns not only played a signiﬁcant role in improving
the sample complexity, but also had a positive inﬂuence
on stability in the training regime. Prioritized Expe-
rience Replay (Schaul et al., 2016) however prevented
Sam from consistently learning well-behaved policies.
Being already prone to overﬁtting in its original setting
(Schaul et al., 2016), we conjecture this phenomenon is
ampliﬁed in our setting since the TD-errors, instrumen-
tal in the priority assignments, depend on rewards that
are themselves learned. Uniform experience replay of-
fers greater resilience against oversampling transitions
that have wrongfully been assigned high synthetic re-
wards by the adversarially-trained reward module.


---

Sample-Eﬃcient Imitation Learning via Generative Adversarial Nets
Policy
We update the policy µθ so as to maximise the
performance objective, deﬁned as the expected return
from the start state. To that end, the policy is updated
by taking a gradient ascent step along:
∇(1)
θ J(µθ) ≈Est∼ρβ [∇θQψ(st, µθ(st))]
(10)
= Est∼ρβ

∇θµθ(st)∇aQψ(st, a)|a=µθ(st)

(11)
where the partial derivative with respect to the state is
ignored since we consider the model-free setting. This
gradient estimation stems from the policy gradient
theorem proved by (Silver et al., 2014), and points
towards regions of the parameter space in which the
policy displays high similarity with the demonstrator.
We model the synthetic reward as a parametrised func-
tion that takes a state and an action as inputs. As
such, we can take the derivative of the reward with
respect to θ. By applying the chain rule, we obtain:
∇(2)
θ J(µθ) ≈Est∼ρβ [∇θrφ(st, µθ(st))]
(12)
= Est∼ρβ

∇θµθ(st)∇arφ(st, a)|a=µθ(st)

(13)
which constitutes another estimate of how to update the
policy parameters θ to increase the similarity between
the policy and the expert ((Sasaki and Kawaguchi,
2018) employs a similar estimate). Each estimate of
how well the agent is behaving, rφ and Qψ, is trained
via a diﬀerent policy evaluation method, each present-
ing its own advantages. The ﬁrst is updated by ad-
versarial training, providing an accurate estimate of
the immediate similarity with expert trajectories. The
second is trained via TD learning, enabling longer prop-
agation of rewards along trajectories and eﬀectively
tackling the credit assignment problem.
While our
formulation enables us to use either of these gradient
estimates, ∇(1)
θ J(µθ) is more suited to learn control
policies in environments inducing delayed rewards. As
the continuous control tasks we consider in this paper
belong to this category, we use ∇(1)
θ J(µθ) to update
the policy module. While we could use a mixture of
∇(1)
θ J(µθ) and ∇(2)
θ J(µθ) we found that the latter had
a detrimental eﬀect on the former, as it prevented the
policy to reason across timesteps, resulting in poor
reward propagation.
Exploration
Deterministic policies have zero vari-
ance in their predictions for a given state, translating
to no exploratory behaviour. The exploration problem
is therefore treated independently from how the policy
is modelled, by deﬁning a stochastic policy πθ from
the learned deterministic policy µθ. In this work, we
construct πθ via the combination of two fundamentally
diﬀerent techniques: a) by applying an adaptive pertur-
bation to the learned weights θ (exploration by noise-
injection in parameter space (Plappert et al., 2018;
Fortunato et al., 2017)) and b) by adding temporally-
correlated noise sampled from a Ornstein-Uhlenbeck
process OU (Lillicrap et al., 2016), well-suited for con-
trol tasks involving inertia (e.g. simulated robotics and
locomotion tasks). We denote the obtained policy by
πθ ≜µ˜θ + OU, where ˜θ results from applying a) to θ.
When interacting with the environment, Sam samples
from the conditional distribution πθ, and stores the
collected transitions in the replay buﬀer R. An interest-
ing result is that the reward is adversarially trained on
samples coming from the parameter-perturbed policy.
Rather than causing severe divergence, it seems that it
positively impacts the adversarial training procedure.
This observation directly echoes noise-injection tech-
niques from the GAN literature. The additive noise
applied to the output of our policy (which plays the
role of generator in our architecture) aligns with (Ar-
jovsky and Bottou, 2017) who add artiﬁcial noise to
the inputs of the discriminator (although we do not
perturb expert trajectories). Furthermore, perturbing
µθ in parameter space draws strong similarities with
(Zhao et al., 2017), in which the authors add Gaussian
noise to the layers of the generator.
5
Results
Our agents were trained in physics-based control en-
vironments, built with the MuJoCo physics engine
(Todorov et al., 2012), and wrapped via the OpenAI
Gym (Brockman et al., 2016) API. Tasks simulated in
the environments range from legacy balance-oriented
tasks to simulated robotics and locomotion tasks of
various complexities. In this work, we consider the
5 following environments, ordered by increasing com-
plexity (degrees of freedom in state and action spaces):
InvertedPendulum, InvertedDoublePendulum, Reacher,
Hopper, Walker2d. In the experiments presented in
Figure 2, we explore how the performance of SAM
and that of GAIL evolve as a function of the number
of interactions they have with the environment.
For each environment, an expert was designed by train-
ing an agent for 10M timesteps using the Proximal
Policy Optimization (PPO) algorithm (Schulman et al.,
2017). The episode horizon (maximum episode length)
was left to its default value per environment. We cre-
ated a dataset of expert trajectories per environment.
For every environment, we evaluated the performance
of the agents when provided with various quantities of
demonstrations, sampled for the demonstration dataset
associated with the environment. We do so in order
to explore how the two methods behave with respect
to the number of demonstrations to which they are


---

Lionel Blondé, Alexandros Kalousis
Algorithm 1: Sample-eﬃcient Adversarial Mimic
Initialise replay buﬀer R
Initialise network parameters (φ, θ, ψ)
Initialise target network parameters (θ′, ψ′) as
respective copies of (θ, ψ)
for i ∈1, . . . , imax do
# Interact with environment
# and store collected transitions
for c ∈1, . . . , cmax do
Interact with environment following πθ and
collect the experienced transitions in C
augmented with synthetic rewards
Store C in the replay buﬀer R
end
for t ∈1, . . . , tmax do
# Update reward module
for d ∈1, . . . , dmax do
Sample uniformly a minibatch Bc of
state-action pairs pairs from C
Sample uniformly a minibatch Bc
e of
state-action pairs from the expert dataset
τe, with |Bc| = |Bc
e|
Update synthetic reward parameter φ with
the equal mixture Bc ∪Bc
e by following
the gradient: ˆEBc[∇φ log(1 −Dφ(s, a))] +
ˆEBce[∇φ log Dφ(s, a)] + λ∇φRGP(φ)
Sample uniformly a minibatch Bd of
state-action pairs from R
Sample uniformly a minibatch Bd
e of
state-action pairs from the expert dataset
τe, with |Bd| = |Bd
e|
Update synthetic reward parameter φ with
the equal mixture Bd ∪Bd
e by following
the gradient: ˆEBd[∇φ log(1 −Dφ(s, a))] +
ˆEBde[∇φ log Dφ(s, a)] + λ∇φRGP(φ)
end
# Update policy and critic modules
for g ∈1, . . . , gmax do
Sample uniformly a minibatch Bg of
transitions from R
Update policy parameter θ by following the
gradient: ˆEBg[∇θJ(µθ)]
Update critic parameters ψ by minimizing
critic loss: ˆEBg[ℓ(ψ)]
Update target network parameters (θ′, ψ′)
to slowly track (θ, ψ), respectively
end
end
end
Figure 2: Performance comparison between Sam and
GAIL in terms of episodic return. The horizontal axis
depicts, in logarithmic scale, the number of interactions
with the environment. While there is no ambiguity for
GAIL, we used the unperturbed Sam policy µθ (with-
out parameter noise and additive action noise) to collect
those returns during a per-iteration evaluation phase.
The ﬁgure shows that our method has a considerably
better sample-eﬃciency than GAIL in various continu-
ous control tasks, often by several orders of magnitude.
Red-colored lines and ﬁlled areas indicate the perfor-
mance range of the expert demonstrations present in
the training set. The meaning of the diﬀerent line styles
and colors is given in-text.


---

Sample-Eﬃcient Imitation Learning via Generative Adversarial Nets
exposed. Both models are shown the same set of se-
lected trajectories. We ensure that the two compared
models are trained on exactly the same subset of ex-
tracted trajectories by training them with the same
random seeds. We varied the cardinality of the set of
selected trajectories as a function of the environment’s
complexity. We ran every experiment on the same
range of 4 random seeds, namely {0, 1, 2, 3}. In Fig-
ure 2, we use scatter plots to visualise every episodic
return, for every random seed. Solid blue and green
lines represent the mean episodic return across the ran-
dom seeds for the given number of interactions. The
ﬁlled areas are conﬁdence intervals around the solid
lines, corresponding to a ﬁxed fraction of the standard
deviation around the mean for the given number of
interactions. Every item coloured in red relates to the
expert performance, for a given environment. The solid
red line corresponds to the mean episodic return of the
demonstrations present in the expert dataset associated
with the given environment. The ﬁlled red region is
a trust region whose width is equal to the standard
deviation of returns in the expert dataset. The dotted
line depicts the minimum return in the demonstration
dataset while the dashed line represents the maximum.
Having statistics about the demonstration datasets is
particularly insightful when evaluating the results of
experiments dealing with few demonstrations.
Every experiment runs with 4 parallel instantiations of
the same model, initialised with diﬀerent seeds. Each
instantiation has its own interaction with the environ-
ment, its own replay buﬀer and its own optimisers.
However, every iteration, the gradients are averaged
per module across instantiations and the averaged gra-
dients are distributed per module to every instantiation
and immediately used to update the respective module
parameters. Both Sam and GAIL experiments were
run under this setting. This vertical scalability played a
considerable role in speeding up training phases, equiva-
lently for both models. Since every instantiation has its
own random seed, the fairness of our performance com-
parison between Sam and GAIL is further strengthened
(Henderson et al., 2017).
We used layer normalisation (Ba et al., 2016) in the
policy module. Indeed, applying layer normalisation to
every layer of the policy was instrumental in yielding
better results, in line with the observations reported in
(Plappert et al., 2018). To ensure symmetry within the
actor-critic architecture, we also applied layer normal-
isation to the critic module. Pop-Art (van Hasselt
et al., 2016) was also useful to our architecture as
our learned reward would sometimes output scores
of various magnitudes.
Applying Pop-Art helped
in overcoming the various scales. Finally, note that
Sam and GAIL implementations use exactly the same
discriminator implementation.
We provide architecture, hyperparameter, implementa-
tion, and other details in the supplementary material.
We also provide video visualisations of learned poli-
cies at https://youtu.be/-nCsqUJnRKU, as well as
the code associated with this work at https://github.
com/lionelblonde/sam-tf.
The sample-eﬃciency we gain over GAIL is consider-
able: Sam needs one or two orders of magnitude less
interactions with the environment to attain asymp-
totic expert performance. Note that the horizontal axis
is scaled logarithmically. Additionally, we observe in
Figure 2 that GAIL agents sometimes fall short of
reaching the demonstrator’s asymptotic performance
(e.g. Reacher and InverseDoublePendulum).
While
GAIL requires full traces of agent–environment interac-
tion per iteration as it relies on Monte-Carlo estimates,
Sam only requires a couple of transitions per iteration
since it performs policy evaluation via Temporal Dif-
ference learning. Instead of sampling transitions from
the environment, performing an update and discarding
the transitions, Sam keeps experiential data in mem-
ory and can therefore leverage decorrelated transitions
collected in previous iterations to perform an oﬀ-policy
update. Our method therefore requires considerably
fewer new samples (interactions) per iteration, as it
can re-exploit the transitions previously experienced.
Since our approach trades interactions with the envi-
ronment with replays with past experiences to extract
more knowledge out of past interactions, echoing ﬁcti-
tious play in game theory, it generally takes a longer
wall-clock time to train imitation policies. However,
in real-world scenarios (e.g. robotic manipulation, au-
tonomous cars), reducing the required interaction with
the world is signiﬁcantly more desirable, for safety and
cost reasons.
6
Conclusion
In this work, we introduced a method, called Sample-
eﬃcient Adversarial Imitation Learning (Sam), that
meaningfully overcomes one considerable drawback of
GAIL (Ho and Ermon, 2016): the number of agent–
environment interactions it requires to learn expert-like
policies. We demonstrate that our method shrinks the
number of interactions by an order of magnitude, and
sometimes more. Leveraging an oﬀ-policy procedure
was key to that success.
Acknowledgments
This work was partially supported by the Swiss
National Science Foundation grant number CR-


---

Lionel Blondé, Alexandros Kalousis
SII5_177179 “Modeling pathological gait resulting from
motor impairment” and European Commission H2020
grant number #645220, RAWFIE.
References
Abbeel, P. and Ng, A. Y. (2004). Apprenticeship Learn-
ing via Inverse Reinforcement Learning. In Interna-
tional Conference on Machine Learning (ICML).
Arjovsky, M. and Bottou, L. (2017). Towards Princi-
pled Methods for Training Generative Adversarial
Networks. In International Conference on Learning
Representations (ICLR).
Arjovsky, M., Chintala, S., and Bottou, L. (2017).
Wasserstein GAN.
Ba, J. L., Kiros, J. R., and Hinton, G. E. (2016). Layer
Normalization.
Bagnell, J. A. (2015). An invitation to imitation. Tech-
nical report, Carnegie Mellon, Robotics Institute,
Pittsburgh.
Baram, N., Anschel, O., Caspi, I., and Mannor, S.
(2017). End-to-End Diﬀerentiable Adversarial Im-
itation Learning. In International Conference on
Machine Learning (ICML), pages 390–399.
Billard, A., Calinon, S., Dillmann, R., and Schaal,
S. (2008). Robot Programming by Demonstration.
In Bruno, S. and Oussama, K., editors, Springer
Handbook of Robotics, pages 1371–1394. Springer
Berlin Heidelberg.
Brockman, G., Cheung, V., Pettersson, L., Schneider,
J., Schulman, J., Tang, J., and Zaremba, W. (2016).
OpenAI Gym.
Finn, C., Christiano, P., Abbeel, P., and Levine, S.
(2016). A Connection between Generative Adversar-
ial Networks, Inverse Reinforcement Learning, and
Energy-Based Models.
Fortunato, M., Azar, M. G., Piot, B., Menick, J., Os-
band, I., Graves, A., Mnih, V., Munos, R., Hassabis,
D., Pietquin, O., Blundell, C., and Legg, S. (2017).
Noisy Networks for Exploration.
Fu, J., Luo, K., and Levine, S. (2018). Learning Robust
Rewards with Adversarial Inverse Reinforcement
Learning. In International Conference on Learning
Representations (ICLR).
Goodfellow, I. (2017). NIPS 2016 Tutorial: Generative
Adversarial Networks.
Goodfellow, I., Pouget-Abadie, J., Mirza, M., Xu, B.,
Warde-Farley, D., Ozair, S., Courville, A., and Ben-
gio, Y. (2014). Generative Adversarial Nets. In Neu-
ral Information Processing Systems (NIPS), pages
2672–2680.
Gu, S., Lillicrap, T., Ghahramani, Z., Turner, R. E.,
and Levine, S. (2016). Q-Prop: Sample-Eﬃcient
Policy Gradient with An Oﬀ-Policy Critic. In In-
ternational Conference on Learning Representations
(ICLR).
Gulrajani, I., Ahmed, F., Arjovsky, M., Dumoulin,
V., and Courville, A. (2017). Improved Training of
Wasserstein GANs. In Neural Information Processing
Systems (NIPS).
Hausman, K., Chebotar, Y., Schaal, S., Sukhatme, G.,
and Lim, J. (2017). Multi-Modal Imitation Learning
from Unstructured Demonstrations using Generative
Adversarial Nets. In Neural Information Processing
Systems (NIPS).
Henderson, P., Islam, R., Bachman, P., Pineau, J., Pre-
cup, D., and Meger, D. (2017). Deep Reinforcement
Learning that Matters.
Hessel, M., Modayil, J., van Hasselt, H., Schaul, T.,
Ostrovski, G., Dabney, W., Horgan, D., Piot, B.,
Azar, M., and Silver, D. (2017). Rainbow: Combining
Improvements in Deep Reinforcement Learning.
Ho, J. and Ermon, S. (2016). Generative Adversarial
Imitation Learning. In Neural Information Process-
ing Systems (NIPS).
Ho, J., Gupta, J. K., and Ermon, S. (2016). Model-Free
Imitation Learning with Policy Optimization.
Jang, E., Gu, S., and Poole, B. (2017). Categorical
Reparameterization with Gumbel-Softmax. In In-
ternational Conference on Learning Representations
(ICLR).
Kingma, D. P. and Ba, J. (2014). Adam: A Method
for Stochastic Optimization.
Kingma, D. P. and Welling, M. (2013). Auto-Encoding
Variational Bayes.
Kostrikov, I., Agrawal, K. K., Levine, S., and Tomp-
son, J. (2018). Addressing Sample Ineﬃciency and
Reward Bias in Inverse Reinforcement Learning.
Kueﬂer, A. and Kochenderfer, M. J. (2017). Burn-In
Demonstrations for Multi-Modal Imitation Learning.
Levine, S., Popovic, Z., and Koltun, V. (2011). Nonlin-
ear Inverse Reinforcement Learning with Gaussian
Processes. In Neural Information Processing Systems
(NIPS), pages 19–27.
Li, Y., Song, J., and Ermon, S. (2017). InfoGAIL: In-
terpretable Imitation Learning from Visual Demon-
strations. In Neural Information Processing Systems
(NIPS).
Lillicrap, T. P., Hunt, J. J., Pritzel, A., Heess, N.,
Erez, T., Tassa, Y., Silver, D., and Wierstra, D.
(2016). Continuous control with deep reinforcement
learning. In International Conference on Learning
Representations (ICLR).


---

Sample-Eﬃcient Imitation Learning via Generative Adversarial Nets
Lucic, M., Kurach, K., Michalski, M., Gelly, S., and
Bousquet, O. (2017). Are GANs Created Equal? A
Large-Scale Study.
Maddison, C. J., Mnih, A., and Teh, Y. W. (2017). The
Concrete Distribution: A Continuous Relaxation of
Discrete Random Variables. In International Con-
ference on Learning Representations (ICLR).
Mnih, V., Kavukcuoglu, K., Silver, D., Graves, A.,
Antonoglou, I., Wierstra, D., and Riedmiller, M.
(2013).
Playing Atari with Deep Reinforcement
Learning.
Mnih, V., Kavukcuoglu, K., Silver, D., Rusu, A. A.,
Veness, J., Bellemare, M. G., Graves, A., Riedmiller,
M., Fidjeland, A. K., Ostrovski, G., Petersen, S.,
Beattie, C., Sadik, A., Antonoglou, I., King, H., Ku-
maran, D., Wierstra, D., Legg, S., and Hassabis, D.
(2015). Human-level control through deep reinforce-
ment learning. Nature, 518(7540):529–533.
Ng, A. Y., Harada, D., and Russell, S. (1999). Policy
invariance under reward transformations: Theory
and application to reward shaping. In International
Conference on Machine Learning (ICML), pages 278–
287.
Pfau, D. and Vinyals, O. (2016). Connecting Generative
Adversarial Networks and Actor-Critic Methods.
Plappert, M., Houthooft, R., Dhariwal, P., Sidor, S.,
Chen, R. Y., Chen, X., Asfour, T., Abbeel, P., and
Andrychowicz, M. (2018). Parameter Space Noise
for Exploration.
In International Conference on
Learning Representations (ICLR).
Pomerleau, D. (1989). ALVINN: An Autonomous Land
Vehicle in a Neural Network. In Neural Information
Processing Systems (NIPS), pages 305–313.
Pomerleau, D. (1990). Rapidly Adapting Artiﬁcial Neu-
ral Networks for Autonomous Navigation. In Neural
Information Processing Systems (NIPS), pages 429–
435.
Ross, S. and Bagnell, J. A. (2010). Eﬃcient Reductions
for Imitation Learning. In International Conference
on Artiﬁcial Intelligence and Statistics (AISTATS),
pages 661–668. jmlr.org.
Ross, S., Gordon, G. J., and Bagnell, J. A. (2011).
A Reduction of Imitation Learning and Structured
Prediction to No-Regret Online Learning. In Inter-
national Conference on Artiﬁcial Intelligence and
Statistics (AISTATS), pages 627–635. jmlr.org.
Sasaki, F. and Kawaguchi, A. (2018). Deterministic
Policy Imitation Gradient Algorithm.
Schaul, T., Quan, J., Antonoglou, I., and Silver, D.
(2016).
Prioritized Experience Replay.
In Inter-
national Conference on Learning Representations
(ICLR).
Schulman, J., Levine, S., Moritz, P., Jordan, M. I., and
Abbeel, P. (2015). Trust Region Policy Optimization.
In International Conference on Machine Learning
(ICML).
Schulman, J., Wolski, F., Dhariwal, P., Radford, A.,
and Oleg, K. (2017). Proximal Policy Optimization
Algorithms.
Silver, D., Lever, G., Heess, N., Degris, T., Wierstra,
D., and Riedmiller, M. (2014). Deterministic Policy
Gradient Algorithms. In International Conference
on Machine Learning (ICML), pages 387–395.
Sutton, R. S. and Barto, A. G. (1998). Reinforcement
Learning: An Introduction.
Sutton, R. S., McAllester, D. A., Singh, S. P., and
Mansour, Y. (1999). Policy Gradient Methods for Re-
inforcement Learning with Function Approximation.
In Neural Information Processing Systems (NIPS),
pages 1057–1063.
Syed, U., Bowling, M., and Schapire, R. E. (2008).
Apprenticeship Learning Using Linear Programming.
In International Conference on Machine Learning
(ICML), pages 1032–1039.
Syed, U. and Schapire, R. E. (2008). A Game-Theoretic
Approach to Apprenticeship Learning. In Neural
Information Processing Systems (NIPS), pages 1449–
1456.
Todorov, E., Erez, T., and Tassa, Y. (2012).
Mu-
JoCo: A physics engine for model-based control. In
IEEE/RSJ International Conference on Intelligent
Robots and Systems (IROS), pages 5026–5033.
van Hasselt, H., Guez, A., Hessel, M., Mnih, V., and
Silver, D. (2016). Learning values across many orders
of magnitude.
Večerík, M., Hester, T., Scholz, J., Wang, F., Pietquin,
O., Piot, B., Heess, N., Rothörl, T., Lampe, T., and
Riedmiller, M. (2017). Leveraging Demonstrations
for Deep Reinforcement Learning on Robotics Prob-
lems with Sparse Rewards.
Wang, Z., Bapst, V., Heess, N., Mnih, V., Munos, R.,
Kavukcuoglu, K., and de Freitas, N. (2016). Sample
Eﬃcient Actor-Critic with Experience Replay.
Zhao, J., Mathieu, M., and LeCun, Y. (2017). Energy-
based Generative Adversarial Network.
In Inter-
national Conference on Learning Representations
(ICLR).
