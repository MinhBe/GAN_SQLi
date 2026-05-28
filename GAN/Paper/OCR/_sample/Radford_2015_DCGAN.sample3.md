Under review as a conference paper at ICLR 2016
UNSUPERVISED REPRESENTATION LEARNING
WITH DEEP CONVOLUTIONAL
GENERATIVE ADVERSARIAL NETWORKS
Alec Radford & Luke Metz
indico Research
Boston, MA
{alec,luke}@indico.io
Soumith Chintala
Facebook AI Research
New York, NY
soumith@fb.com
ABSTRACT
In recent years, supervised learning with convolutional networks (CNNs) has
seen huge adoption in computer vision applications. Comparatively, unsupervised
learning with CNNs has received less attention. In this work we hope to help
bridge the gap between the success of CNNs for supervised learning and unsupervised learning. We introduce a class of CNNs called deep convolutional generative
adversarial networks (DCGANs), that have certain architectural constraints, and
demonstrate that they are a strong candidate for unsupervised learning. Training
on various image datasets, we show convincing evidence that our deep convolutional adversarial pair learns a hierarchy of representations from object parts to
scenes in both the generator and discriminator. Additionally, we use the learned
features for novel tasks - demonstrating their applicability as general image representations.
1
INTRODUCTION
Learning reusable feature representations from large unlabeled datasets has been an area of active
research. In the context of computer vision, one can leverage the practically unlimited amount of
unlabeled images and videos to learn good intermediate representations, which can then be used on
a variety of supervised learning tasks such as image classification. We propose that one way to build
good image representations is by training Generative Adversarial Networks (GANs) (Goodfellow
et al., 2014), and later reusing parts of the generator and discriminator networks as feature extractors
for supervised tasks. GANs provide an attractive alternative to maximum likelihood techniques.
One can additionally argue that their learning process and the lack of a heuristic cost function (such
as pixel-wise independent mean-square error) are attractive to representation learning. GANs have
been known to be unstable to train, often resulting in generators that produce nonsensical outputs.
There has been very limited published research in trying to understand and visualize what GANs
learn, and the intermediate representations of multi-layer GANs.
In this paper, we make the following contributions
• We propose and evaluate a set of constraints on the architectural topology of Convolutional
GANs that make them stable to train in most settings. We name this class of architectures
Deep Convolutional GANs (DCGAN)
• We use the trained discriminators for image classification tasks, showing competitive performance with other unsupervised algorithms.
• We visualize the filters learnt by GANs and empirically show that specific filters have
learned to draw specific objects.
1
arXiv:1511.06434v2 [cs.LG] 7 Jan 2016


---

Under review as a conference paper at ICLR 2016
• We show that the generators have interesting vector arithmetic properties allowing for easy
manipulation of many semantic qualities of generated samples.
2
RELATED WORK
2.1
REPRESENTATION LEARNING FROM UNLABELED DATA
Unsupervised representation learning is a fairly well studied problem in general computer vision
research, as well as in the context of images. A classic approach to unsupervised representation
learning is to do clustering on the data (for example using K-means), and leverage the clusters for
improved classification scores. In the context of images, one can do hierarchical clustering of image
patches (Coates & Ng, 2012) to learn powerful image representations. Another popular method
is to train auto-encoders (convolutionally, stacked (Vincent et al., 2010), separating the what and
where components of the code (Zhao et al., 2015), ladder structures (Rasmus et al., 2015)) that
encode an image into a compact code, and decode the code to reconstruct the image as accurately
as possible. These methods have also been shown to learn good feature representations from image
pixels. Deep belief networks (Lee et al., 2009) have also been shown to work well in learning
hierarchical representations.
2.2
GENERATING NATURAL IMAGES
Generative image models are well studied and fall into two categories: parametric and nonparametric.
The non-parametric models often do matching from a database of existing images, often matching
patches of images, and have been used in texture synthesis (Efros et al., 1999), super-resolution
(Freeman et al., 2002) and in-painting (Hays & Efros, 2007).
Parametric models for generating images has been explored extensively (for example on MNIST
digits or for texture synthesis (Portilla & Simoncelli, 2000)). However, generating natural images
of the real world have had not much success until recently. A variational sampling approach to
generating images (Kingma & Welling, 2013) has had some success, but the samples often suffer
from being blurry. Another approach generates images using an iterative forward diffusion process
(Sohl-Dickstein et al., 2015). Generative Adversarial Networks (Goodfellow et al., 2014) generated
images suffering from being noisy and incomprehensible. A laplacian pyramid extension to this
approach (Denton et al., 2015) showed higher quality images, but they still suffered from the objects
looking wobbly because of noise introduced in chaining multiple models. A recurrent network
approach (Gregor et al., 2015) and a deconvolution network approach (Dosovitskiy et al., 2014) have
also recently had some success with generating natural images. However, they have not leveraged
the generators for supervised tasks.
2.3
VISUALIZING THE INTERNALS OF CNNS
One constant criticism of using neural networks has been that they are black-box methods, with little
understanding of what the networks do in the form of a simple human-consumable algorithm. In the
context of CNNs, Zeiler et. al. (Zeiler & Fergus, 2014) showed that by using deconvolutions and
filtering the maximal activations, one can find the approximate purpose of each convolution filter in
the network. Similarly, using a gradient descent on the inputs lets us inspect the ideal image that
activates certain subsets of filters (Mordvintsev et al.).
3
APPROACH AND MODEL ARCHITECTURE
Historical attempts to scale up GANs using CNNs to model images have been unsuccessful. This
motivated the authors of LAPGAN (Denton et al., 2015) to develop an alternative approach to iteratively upscale low resolution generated images which can be modeled more reliably. We also
encountered difficulties attempting to scale GANs using CNN architectures commonly used in the
supervised literature. However, after extensive model exploration we identified a family of archi-
2


---

Under review as a conference paper at ICLR 2016
tectures that resulted in stable training across a range of datasets and allowed for training higher
resolution and deeper generative models.
Core to our approach is adopting and modifying three recently demonstrated changes to CNN architectures.
The first is the all convolutional net (Springenberg et al., 2014) which replaces deterministic spatial
pooling functions (such as maxpooling) with strided convolutions, allowing the network to learn
its own spatial downsampling. We use this approach in our generator, allowing it to learn its own
spatial upsampling, and discriminator.
Second is the trend towards eliminating fully connected layers on top of convolutional features.
The strongest example of this is global average pooling which has been utilized in state of the
art image classification models (Mordvintsev et al.). We found global average pooling increased
model stability but hurt convergence speed. A middle ground of directly connecting the highest
convolutional features to the input and output respectively of the generator and discriminator worked
well. The first layer of the GAN, which takes a uniform noise distribution Z as input, could be called
fully connected as it is just a matrix multiplication, but the result is reshaped into a 4-dimensional
tensor and used as the start of the convolution stack. For the discriminator, the last convolution layer
is flattened and then fed into a single sigmoid output. See Fig. 1 for a visualization of an example
model architecture.
Third is Batch Normalization (Ioffe & Szegedy, 2015) which stabilizes learning by normalizing the
input to each unit to have zero mean and unit variance. This helps deal with training problems that
arise due to poor initialization and helps gradient flow in deeper models. This proved critical to get
deep generators to begin learning, preventing the generator from collapsing all samples to a single
point which is a common failure mode observed in GANs. Directly applying batchnorm to all layers
however, resulted in sample oscillation and model instability. This was avoided by not applying
batchnorm to the generator output layer and the discriminator input layer.
The ReLU activation (Nair & Hinton, 2010) is used in the generator with the exception of the output
layer which uses the Tanh function. We observed that using a bounded activation allowed the model
to learn more quickly to saturate and cover the color space of the training distribution. Within the
discriminator we found the leaky rectified activation (Maas et al., 2013) (Xu et al., 2015) to work
well, especially for higher resolution modeling. This is in contrast to the original GAN paper, which
used the maxout activation (Goodfellow et al., 2013).
Architecture guidelines for stable Deep Convolutional GANs
• Replace any pooling layers with strided convolutions (discriminator) and fractional-strided
convolutions (generator).
• Use batchnorm in both the generator and the discriminator.
• Remove fully connected hidden layers for deeper architectures.
• Use ReLU activation in generator for all layers except for the output, which uses Tanh.
• Use LeakyReLU activation in the discriminator for all layers.
4
DETAILS OF ADVERSARIAL TRAINING
We trained DCGANs on three datasets, Large-scale Scene Understanding (LSUN) (Yu et al., 2015),
Imagenet-1k and a newly assembled Faces dataset. Details on the usage of each of these datasets
are given below.
No pre-processing was applied to training images besides scaling to the range of the tanh activation
function [-1, 1]. All models were trained with mini-batch stochastic gradient descent (SGD) with
a mini-batch size of 128. All weights were initialized from a zero-centered Normal distribution
with standard deviation 0.02. In the LeakyReLU, the slope of the leak was set to 0.2 in all models.
While previous GAN work has used momentum to accelerate training, we used the Adam optimizer
(Kingma & Ba, 2014) with tuned hyperparameters. We found the suggested learning rate of 0.001,
to be too high, using 0.0002 instead. Additionally, we found leaving the momentum term β1 at the
3
