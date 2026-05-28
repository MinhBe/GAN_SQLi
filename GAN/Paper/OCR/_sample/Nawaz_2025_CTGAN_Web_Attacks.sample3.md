Improving Credit Card Fraud Detection through Transformer-Enhanced GAN Oversampling
Kashaf ul Emaan, kashafe4@gmail.com +923028147884
Abstract
Detection of credit card fraud is an acute issue of financial security because transaction datasets are highly
lopsided, with fraud cases being only a drop in the ocean. Balancing datasets using the most popular
methods of traditional oversampling such as the Synthetic Minority Oversampling Technique (SMOTE)
generally create simplistic synthetic samples that are not readily applicable to complex fraud patterns.
Recent industry advances that include Conditional Tabular Generative Adversarial Networks (CTGAN) and
Tabular Variational Autoencoders (TVAE) have demonstrated increased efficiency in tabular synthesis, yet
all these models still exhibit issues with high-dimensional dependence modelling.
Now we will present our hybrid approach where we use a Generative Adversarial Network (GAN) with a
Transformer encoder block to produce realistic fraudulent transactions samples. The GAN architecture
allows training realistic generators adversarial, and the Transformer allows the model to learn rich feature
interactions by self-attention. Such a hybrid strategy overcomes the limitations of SMOTE, CTGAN, and
TVAE by producing a variety of high-quality synthetic minority classes samples.
We test our algorithm on the publicly-available Credit Card Fraud Detection dataset and compare it to
conventional and generative resampling strategies with a variety of classifiers, such as Logistic Regression
(LR), Random Forest (RF), Extreme Gradient Boosting (XGBoost), and Support Vector Machine (SVM).
Findings indicate that our Transformer-based GAN shows substantial gains in Recall, F1-score and Area
Under the Receiver Operating Characteristic Curve (AUC), which indicates that it is effective in overcoming
the severe class imbalance inherent in the task of fraud detection.
1. INTRODUCTION
The use of digital transaction has rapidly
increased in recent decades and as a result, the
fraudulent cases inside the financial sector have
increased rapidly [1]. Heavy use of credit cards
specifically has become an issue of concern to
banks, merchants, and consumers alike given
credit card frauds financial implications and the
fact that it remains hard to detect [2]. Industry
reports indicate that fraudulent credit card
activities cost the industry billions of dollars
annually, and fraud detection is a highly pressing
research topic in both academia and the
industry. The main problem in CGM building
fraud detection systems correctly is the severe
lack of equal representation between the
classes: on most datasets, the baseline of fraud


---

agreements does not exceed 0.2 percent of all
transactions [3]. Such an imbalance causes the
classic machine learning models to be biased by
the
majority
group
(non-fraudulent
transactions), which in many cases reduces the
quality of the model on the minority group
(fraudulent transactions) [4].
1.1 Challenges of Class Imbalance in Fraud
Detection
One already documented problem in supervised
learning problems includes imbalance of classes.
In a dataset where more samples are of one type
[5], machine learning optimizing strategies tend
to favor the general accuracy of a system by
focusing on the dominant one, at the expense of
the other smaller type. To illustrate this point, a
model that predicts all transactions are valid may
obtain an accuracy of above 99 but will result in
a complete failure in detecting fraud in a fraud
money task [6]. This shows the weakness of
accuracy as a performance measure on
imbalanced data and the significance in
considering performance measures like Recall,
Precision, F1-score, and Area Under the Receiver
Operating Characteristic Curve (AUC) [7].
Remembering is particularly imperative in
detecting fraud since any failure to detect a fraud
directly equates to loss of money [8].
1.2 Existing Oversampling Approaches
A few oversampling methods have been
suggested to deal with the imbalance problem.
One of the oldest and the most popular
techniques
is
the
Synthetic
Minority
Oversampling Technique (SMOTE) [9]. SMOTE
creates synthetic samples of the minority set, by
interpolating between the existing minority
examples [10]. Although the use of SMOTE is
useful in boosting the share of minority samples,
it does have its disadvantages [11]. The method
is more likely to produce simplistic data that
cannot reflect the distributions of the fraudulent
transactions. In addition, due to the fact that
SMOTE is based on linear interpolation, it can
generate unrealistic or noisy samples [12].
The recent advances in generative models have
brought with them more advanced data
synthesis approaches [13]. Conditional Tabular
Generative Adversarial Network (CTGAN) is an
adversarial model that is trained to learn the
distribution of tabular data conditioned on
discrete variables. It has been demonstrated that
CTGAN yields more realistic samples of minority
classes than traditional oversampling techniques
[14].
Similarly,
the
Tabular
Variational
Autoencoder (TVAE) adopts the variational
autoencoder framework to learn synthesis of
image-like data to tabular data, so that the latent
data distribution can be sampled to produce
synthetically generated records. Both CTGAN and
TVAE enhance the performance of SMOTE by
being able to capture nonlinear dependencies,
although they do not perform well on highly


---

imbalanced, high-dimensional tasks like fraud
detection [15].
1.3 Hybrid GAN–Transformer Approach
GANs have been demonstrated to be robust
models that generate high-dimensional and
realistic data. In a typical GAN architecture, a
generator network is tasked with the problem of
generating fake samples that resemble real data,
whereas a discriminator network is tasked with
the problem of differentiating between real and
fake samples [16]. Both networks are optimized
through adversarial training which yields very
realistic synthetic data. But typical GAN
architectures are poorly suited to capturing longrange relationships and interactions between
tabular features.
Transformer
models
have
enabled
the
revolutionization of natural language processing
by relying on self-attention to extract contextual
dependencies through sequences [5]. Based on
this success, we augment a Transformer encoder
block to the GAN architecture to detect fraud.
The hybrid Transformer based GAN (T-GAN)
relies on the Transformer component to improve
the capacity of the generator. It capture complex
relationships of features of transactions, and the
adversarial
structure
to
produce
realistic
samples of minority classes [15]. It is hoped that
this strategy will perform better than both
traditional
oversampling
(SMOTE)
and
generative baselines (CTGAN and TVAE) because
it will result in a variety of high-quality fraudulent
transaction
data
that
trains
downstream
classifiers more effectively [9].
1.4 Contributions of this Study
Principal
findings
of
this
research
are
summarized like following:
•
Hybrid GAN-Transformer Architecture:
We introduce a new type of architecture
that combines a Transformer encoder
with a GAN architecture to enhance the
production of minority classes sample to
detect credit card fraud.
•
Comparative Evaluation: We perform a
comparative evaluation of the proposed
model in comparison to the existing
oversampling methods, such as SMOTE,
CTGAN, and TVAE, in terms of several
machine learning classifiers.
•
Universal Metrics: We evaluate the
performance on Recall, Precision, F1-
score & AUC metrics, and show the
benefit of the proposed approach in
highly
unbalanced
scenario
where
traditional accuracy is not suitable.
•
Practical Implications: We show how the
suggested
approach
enhances
the
performance of the fraud detector and
explain how it may be applied to realworld financial systems.
2. RELATED WORK
Fraudulent credit card detection has been
extensively studied in the last 20 years because it
directly affects both financial institutions and
