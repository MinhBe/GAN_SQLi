Active Deep Kernel Learning of Molecular Properties from Structural Embeddings

Ayana Ghosh*,1 Maxim Ziatdinov,2 Sergei V. Kalinin**2,3

1Computational Sciences and Engineering Division, Oak Ridge National Laboratory, Oak Ridge,
TN, 37831, USA
2Physical Sciences Division, Pacific Northwest National Lab, Richland, WA 99352, USA
3Department of Materials Science and Engineering, University of Knoxville, Knoxville, TN
37996 USA


Abstract:

As vast databases of chemical identities become increasingly available, the challenge shifts to how
we effectively explore and leverage these resources to study molecular properties. This paper
presents an active learning approach for molecular discovery using Deep Kernel Learning (DKL),
demonstrated on the QM9 dataset. DKL links structural embeddings directly to properties, creating
organized latent spaces that prioritize relevant property information. By iteratively recalculating
embedding vectors in alignment with target properties, DKL uncovers concentrated maxima
representing key molecular properties and reveals unexplored regions with potential for
innovation. This approach underscores DKL's potential in advancing molecular research and
discovery.


Email: *ghosha@ornl.gov; **sergei2@utk.edu


---

1. Introduction


In recent years, the field of molecular discovery1-8 has experienced a revolutionary
metamorphosis, driven by significant advancements in deep learning (DL) models. These
sophisticated algorithms have not only accelerated the pace of molecular research but also
discerned the advent of a new era in comprehending and forecasting molecular properties. Within
the realm of molecular discovery, DL demonstrates its proficiency in deciphering intricate
relationships between molecular structures and properties.8-18 This capability empowers
researchers to unravel complex mechanisms19-27 and expedite the discovery of novel compounds.

Examples abound in the successful application of DL to molecular discovery, particularly
in drug discovery.5,6,28-32 Deep learning models play a pivotal role in swiftly identifying potential
drug candidates by predicting their efficacy and safety profiles. These models analyze extensive
datasets of molecular structures and biological responses, providing valuable insights that
streamline the drug development23,24,31 process. Moreover, DL models prove invaluable in
predicting diverse molecular properties, including toxicity, solubility, and bioactivity. By learning
from diverse datasets that encompass molecular structures and experimental outcomes, these
models make accurate predictions, significantly economizing time and resources in experimental
validation.

The versatility and impact of these models extend across various domains such as quantum
chemistry, materials science, prediction of protein structures, and chemical reactions. They
moderate the need for computationally expensive quantum mechanical simulations and trial-anderror synthetic chemical routes for efficient exploration of complex molecular interactions, gaining
a deeper understanding of dynamic molecular processes. This efficiency is especially beneficial
for steering progress in both theoretical chemistry and planning of synthesis.


A typical roster of popular DL models33-38 includes, but is not restricted to, graph neural
networks (GNNs),39-42 recurrent neural networks (RNNs),22,43-45 convolutional neural networks
(CNNs),46 autoencoders,47,48 Long Short-Term Memory Networks (LSTMs),49,50 and attention
mechanisms.51-53 GNNs tend to excel in molecular discovery by representing molecules as graphs,
with atoms as nodes and chemical bonds as edges. These networks employ message-passing
mechanisms to iteratively update node representations based on their local neighborhoods,
enabling them to capture intricate relationships between atoms and predict molecular properties.
RNNs are well-suited for sequential data, making them valuable for tasks in molecular discovery
where molecular structures can be represented as sequences. CNNs prove effective in molecular
discovery when applied to molecular images or grids, using convolutional layers to extract spatial
features from molecular structures. Autoencoders contribute to molecular representation learning
by encoding molecular structures into a lower-dimensional space and then decoding them back to
the original space. This process encourages the model to learn meaningful and compact
representations of molecules. LSTMs find utility in predicting molecular behavior over time.
Attention mechanisms enhance the interpretability of DL models in molecular discovery by
assigning varying degrees of importance to different parts of the input, allowing the model to focus
on specific features crucial for the task at hand.

While these models are instrumental in unraveling complex relationships within molecular
data, active learning strategies54 complement them by addressing significant challenges and
optimizing the utilization of resources. They boost data efficiency by pinpointing the most
informative instances for labeling, thereby enhancing the efficacy of the learning process,
particularly when dealing with limited labeled data. This is especially advantageous in contexts


---

where experimental data collection proves to be both costly and time intensive. Active learning
mitigates annotation costs by concentrating on instances that yield the most substantial learning
improvements, resulting in noteworthy cost savings, especially in domains such as drug discovery
and materials science. Additionally, active learning55-57 adeptly manages imbalanced datasets,
navigates diverse regions within the chemical space, and adapts to concept drift over time. By
actively selecting demanding instances for annotation, active learning not only contributes to
fortifying model robustness but also facilitates transfer learning, amplifying the model's
adaptability to related tasks or properties. The iterative characteristic of active learning empowers
models to continually enhance their performance, establishing them as invaluable tools for
streamlined and effective molecular discovery.

Very importantly, the successes of all the DL models trained as static or within active
learning schemes, heavily rely on the molecular embeddings58-60 such as latent variables in VAEs.
These in turn are formed as a compression of static descriptors, for e.g., SMILES (Simplified
Molecular Input Line Entry System) and SELFIES (Self-referencing Embedded Strings) to
effectively represent and connect molecules to different properties. Active learning models
leverage these embeddings to select informative instances for labeling, using the condensed
representations to measure uncertainty and guide the labeling process toward the most valuable
data points, while enhancing data efficiency, reducing annotation costs, and exploring the chemical
space effectively.

However, for molecular discovery, it is crucial to leverage molecular embeddings in a
manner that establishes connections with the landscape of molecular properties. Therefore,
representing molecules in a low-dimensional latent space linked to specific properties becomes an
integral aspect. Autoencoders are often favored for encoding molecular structures into lowdimensional spaces, owing to their past successes. However, the latent representation generated
by autoencoders is not inherently linked to any molecular property; rather, it functions as a
compressed, abstract portrayal of the input molecular structure. In the autoencoder context, the
model is trained to encode a molecular structure into a lower-dimensional latent space and then
decode it back to the original structure, with the latent representation intended to capture essential
features in a more concise form.

Although the latent representation may encompass information relevant to molecular
properties, the autoencoder61 itself is not explicitly designed to learn or predict specific properties.
The typical training objective for an autoencoder is reconstruction, aiming to minimize the
difference between the input and the reconstructed output. Consequently, while the latent
representation62,63 may capture structural patterns, these patterns may not directly correlate with
explicit molecular properties such as atomization energy, molecular enthalpy, dipole moment.

In this study, we showcase the utilization of deep kernel learning (DKL)64,65 models with
molecular embeddings. Our primary objective is to evaluate the effectiveness of DKL models in
predicting molecular properties directly from SELFIES-based one-hot vector representations. We
perform this investigation both in standard supervised and active learning66-68 settings. By using
one-hot encodings of SELFIES strings as structural embeddings, we aim to establish a direct
mapping between molecular representations and target properties. In addition to property
prediction, we analyze the resulting DKL latent spaces to identify how specific molecular
properties organize and cluster, enabling the targeted selection or discovery of molecules with
desired characteristics.
The model architecture consist of both a deep neural network and a kernel function which
can be combined within a Gaussian process (GP).69-80 These models employ a hybrid architecture,
