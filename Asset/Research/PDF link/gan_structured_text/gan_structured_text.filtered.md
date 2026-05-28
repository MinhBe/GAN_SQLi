# Research Paper Results

Total records: 487

## 1. Conditional Tabular GAN-Based Two-Stage Data Generation Scheme for Short-Term Load Forecasting

- Authors: Jaeuk Moon; Seungwon Jung; Sungwoo Park; Eenjun Hwang
- Year: 2020
- DOI: 10.1109/access.2020.3037063
- Venue: IEEE Access
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.1109/access.2020.3037063
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/8948470/09253644.pdf

Load forecasting is one of the critical tasks for enhancing the energy efficiency of smart grids. Even though recent deep learning-based load forecasting models have shown excellent forecasting performance, one of the common problems they faced was that their forecasting accuracy was highly dependent on the data quality and quantity available for the model training. Collecting a sufficient amount of high-quality data is expensive and time-consuming. Recently, a generative adversarial network (GAN) has shown its potential as a solution to the data shortage problem by generating virtual data based on a small amount of real data, and several studies have used GAN to generate electric load data for training forecasting models. However, due to the noise data problem of GANs, their predictive performance also deteriorated. To solve this problem, in this study, we propose a two-stage data generation scheme that more effectively generates input and output variables for short-term load forecasting. In the first stage, we generate virtual calendar and temperature data used as input variables using a conditional tabular GAN (CTGAN). In the second stage, we generate electric load data corresponding to the input variables using a deep learning-based regression model. Lastly, we construct our forecasting model by training another regression model using a mixture of generated data and real data. To verify the effectiveness of our scheme, we conducted extensive experiments using various datasets and data generation models. We report some of the results.

## 2. Enhanced Conditional GAN for High-Quality Synthetic Tabular Data Generation in Mobile-Based Cardiovascular Healthcare

- Authors: Malak Alqulaity; Po Yang
- Year: 2024
- DOI: 10.3390/s24237673
- Venue: Sensors
- Countries: GB
- Source: openalex
- URL: https://doi.org/10.3390/s24237673
- PDF: https://www.mdpi.com/1424-8220/24/23/7673/pdf?version=1732949839

The generation of synthetic tabular data has emerged as a critical task in various fields, particularly in healthcare, where data privacy concerns limit the availability of real datasets for research and analysis. This paper presents an enhanced Conditional Generative Adversarial Network (GAN) architecture designed for generating high-quality synthetic tabular data, with a focus on cardiovascular disease datasets that encompass mixed data types and complex feature relationships. The proposed architecture employs specialized sub-networks to process continuous and categorical variables separately, leveraging metadata such as Gaussian Mixture Model (GMM) parameters for continuous attributes and embedding layers for categorical features. By integrating these specialized pathways, the generator produces synthetic samples that closely mimic the statistical properties of the real data. Comprehensive experiments were conducted to compare the proposed architecture with two established models: Conditional Tabular GAN (CTGAN) and Tabular Variational AutoEncoder (TVAE). The evaluation utilized metrics such as the Kolmogorov-Smirnov (KS) test for continuous variables, the Jaccard coefficient for categorical variables, and pairwise correlation analyses. Results indicate that the proposed approach attains a mean KS statistic of 0.3900, demonstrating strong overall performance that outperforms CTGAN (0.4803) and is comparable to TVAE (0.3858). Notably, our approach shows lowest KS statistics for key continuous features, such as total cholesterol (KS = 0.0779), weight (KS = 0.0861), and diastolic blood pressure (KS = 0.0957), indicating its effectiveness in closely replicating real data distributions. Additionally, it achieved a Jaccard coefficient of 1.00 for eight out of eleven categorical variables, effectively preserving categorical distributions. These findings indicate that the proposed architecture captures both distributions and dependencies, providing a robust solution in supporting mobile personalized cardiovascular disease prevention systems.

## 3. GANs for Tabular Healthcare Data Generation: A Review on Utility and Privacy

- Authors: João Coutinho‐Almeida; Pedro Pereira Rodrigues; Ricardo Cruz‐Correia
- Year: 2021
- DOI: 10.1007/978-3-030-88942-5_22
- Venue: Lecture notes in computer science
- Countries: PT
- Source: openalex
- URL: https://doi.org/10.1007/978-3-030-88942-5_22

## 4. Synthetic tabular data generation using a VAE-GAN architecture

- Authors: Dmitry Anshelevich; Gilad Katz
- Year: 2025
- DOI: 10.1016/j.knosys.2025.113997
- Venue: Knowledge-Based Systems
- Countries: IL
- Source: openalex
- URL: https://doi.org/10.1016/j.knosys.2025.113997
- PDF: https://doi.org/10.1016/j.knosys.2025.113997

Synthetic data generation (SDG) can be used to augment an existing dataset or create a new dataset with statistical characteristics similar to the original. SDG for tabular data is challenging because of the need to model both continuous and categorical features and their correlations. multiple approaches for tabular SDG use generative adversarial networks (GAN) or variational autoencoders (VAEs). Generally, GAN-based architectures create high-quality samples but have greater difficulty modeling the distribution of the target dataset. VAE-based approaches accurately model the data distribution but sometimes produce lower-quality samples. In this study, we propose T-VAE-GAN, a novel solution for tabular SDG. Our approach hierarchically combines GANs and VAEs to enable the generation of high-quality samples while ensuring that the overall feature distribution is highly similar to that of the original dataset. Extensive evaluation on a large number of datasets shows that our approach either outperforms or achieves comparable results to leading approaches while also being more computationally efficient. • A hierarchical generative architecture for synthetic tabular data generation. • The approach outperforms current leading approaches in terms of sample quality. • The proposed solution is more computationally efficient than existing approaches.

## 5. Assessing the Potentials of LLMs and GANs as State-of-the-Art Tabular Synthetic Data Generation Methods

- Authors: Marko Miletic; Murat Sariyar
- Year: 2024
- DOI: 10.1007/978-3-031-69651-0_25
- Venue: Lecture notes in computer science
- Countries: CH
- Source: openalex
- URL: https://doi.org/10.1007/978-3-031-69651-0_25

## 6. Survey on Synthetic Data Generation, Evaluation Methods and GANs

- Authors: Álvaro Figueira; Bruno Vaz
- Year: 2022
- DOI: 10.3390/math10152733
- Venue: Mathematics
- Countries: PT
- Source: openalex
- URL: https://doi.org/10.3390/math10152733
- PDF: https://www.mdpi.com/2227-7390/10/15/2733/pdf?version=1660119151

Synthetic data consists of artificially generated data. When data are scarce, or of poor quality, synthetic data can be used, for example, to improve the performance of machine learning models. Generative adversarial networks (GANs) are a state-of-the-art deep generative models that can generate novel synthetic samples that follow the underlying data distribution of the original dataset. Reviews on synthetic data generation and on GANs have already been written. However, none in the relevant literature, to the best of our knowledge, has explicitly combined these two topics. This survey aims to fill this gap and provide useful material to new researchers in this field. That is, we aim to provide a survey that combines synthetic data generation and GANs, and that can act as a good and strong starting point for new researchers in the field, so that they have a general overview of the key contributions and useful references. We have conducted a review of the state-of-the-art by querying four major databases: Web of Sciences (WoS), Scopus, IEEE Xplore, and ACM Digital Library. This allowed us to gain insights into the most relevant authors, the most relevant scientific journals in the area, the most cited papers, the most significant research areas, the most important institutions, and the most relevant GAN architectures. GANs were thoroughly reviewed, as well as their most common training problems, their most important breakthroughs, and a focus on GAN architectures for tabular data. Further, the main algorithms for generating synthetic data, their applications and our thoughts on these methods are also expressed. Finally, we reviewed the main techniques for evaluating the quality of synthetic data (especially tabular data) and provided a schematic overview of the information presented in this paper.

## 7. Moving Conditional GAN Close to Data: Synthetic Tabular Data Generation and Its Experimental Evaluation

- Authors: Abdul Majeed; Seong Oun Hwang
- Year: 2024
- DOI: 10.1109/tbdata.2024.3442534
- Venue: IEEE Transactions on Big Data
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.1109/tbdata.2024.3442534

Recently, data has ousted oil as the most economical resource in the world, but most companies are reluctant to share customer/user data in pure form and on a large scale due to privacy concerns. Many innovative technologies (e.g., federated learning, split learning) are employed to meet the growing demand for privacy preservation. Despite these technologies, acquiring personal data in order to optimize utility, and then sharing it on a large scale, is still very challenging. Thanks to the rapid development of artificial intelligence (AI), a relatively new and promising solution to resolve these challenges is to generate synthetic data (SD) by mirroring the original dataset’s properties. SD is a promising solution to address growing privacy demands as well as the utility/analytics requirements of many industry stakeholders. In this paper, we propose and implement an SD generation method from a real dataset containing both numerical and categorical attributes by using an improved conditional generative adversarial network (CGAN), and we quantify the feasibility of SD on technical and theoretical grounds. We provide a detailed analysis of SD in original and anonymized forms with the help of multiple use cases, whereas prior research simply assumed that privacy issues in SD are small because AI models do not overfit or SD has a poor connection with real data. We provide insights into the characteristics of SD (distributions, value frequencies, correlations, etc.) produced by the CGAN in relation to the real data. To the best of our knowledge, this is the pioneering work that provides an experiment-based analysis of the quality, privacy, and utility of SD in relation to a real benchmark dataset.

## 8. A Review of Tabular Data Synthesis Using GANs on an IDS Dataset

- Authors: Stavroula Bourou; Andreas El Saer; Terpsichori-Helen Velivassaki; Artemis Voulkidis; Theodοre Zahariadis
- Year: 2021
- DOI: 10.3390/info12090375
- Venue: Information
- Countries: GR
- Source: openalex
- URL: https://doi.org/10.3390/info12090375
- PDF: https://www.mdpi.com/2078-2489/12/9/375/pdf?version=1641525245

Recent technological innovations along with the vast amount of available data worldwide have led to the rise of cyberattacks against network systems. Intrusion Detection Systems (IDS) play a crucial role as a defense mechanism in networks against adversarial attackers. Machine Learning methods provide various cybersecurity tools. However, these methods require plenty of data to be trained efficiently, which may be hard to collect or to use due to privacy reasons. One of the most notable Machine Learning tools is the Generative Adversarial Network (GAN), and it has great potential for tabular data synthesis. In this work, we start by briefly presenting the most popular GAN architectures, VanillaGAN, WGAN, and WGAN-GP. Focusing on tabular data generation, CTGAN, CopulaGAN, and TableGAN models are used for the creation of synthetic IDS data. Specifically, the models are trained and evaluated on an NSL-KDD dataset, considering the limitations and requirements that this procedure needs. Finally, based on certain quantitative and qualitative methods, we argue and evaluate the most prominent GANs for tabular network data synthesis.

## 9. Generation and Evaluation of Tabular Data in Different Domains Using Gans

- Authors: Persevearance Marecha; Lu Ye
- Year: 2023
- DOI: 10.9734/ajrcos/2023/v16i1331
- Venue: Asian Journal of Research in Computer Science
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.9734/ajrcos/2023/v16i1331
- PDF: https://journalajrcos.com/index.php/AJRCOS/article/download/331/658

Deep learning techniques like Generative Adversarial Networks (GANs) provide solutions in many domains where real data needs to be kept private. Synthesizing tabular data is difficult because of its high complexity. Tabular data usually contains a mixture of discrete and continuous data, which is not an easy model to build. The contributions made in this paper include training and generating data with the original Vanilla Gan, then CGan and WGan-Gp and WCGan-Gp which performs better than the former. The Adult Income Census dataset mainly focuses on predicting whether income exceeds 50,000 per year based on census data, then comparing the accuracy of machine learning models and calculating the F1 scores. Then the use of TimeGan on the stock dataset, comparing synthetic data vs real data. This paper will explore the use of GANs for generating and evaluating tabular data in different domains.

## 10. Tool/Dataset Paper: Realistic ABAC Data Generation using Conditional Tabular GAN

- Authors: Ritwik Rai; Shamik Sural
- Year: 2023
- DOI: 10.1145/3577923.3583635
- Venue: 
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.1145/3577923.3583635

Attribute-based Access Control (ABAC) is increasingly being used in a wide variety of applications that include cloud services, IoT, smart homes, healthcare and several others. Conducting systematic and reproducible experiments with benchmark realistic datasets, however, still remains a challenge. To address this shortcoming, in this paper we introduce a method called ConGRASS (Conditional Tabular GAN for Realistic ABAC Simulation Studies) for generating large ABAC datasets. Starting with a given real world dataset of (potentially) limited size, we first train a conditional tabular generative adversarial network for learning its distribution. The trained model is used to generate realistic datasets of arbitrarily large sizes having distribution similar to the original dataset. ConGRASS has been implemented as a free to use web-based tool in which a user can choose the name of a listed real dataset along with the desired dataset size. A CSV file containing ABAC data is generated as output. Extensive evaluation shows the ability of the model to faithfully learn the statistical properties of the selected real data. When such a dataset is used in an actual problem, significant improvement in performance is achieved, proving the utility of ConGRASS.

## 11. Synthetic Tabular Data Generation Using a Vae-Gan Architecture

- Authors: Dmitry Anshelevich; Gilad Katz
- Year: 2024
- DOI: 10.2139/ssrn.4902016
- Venue: SSRN Electronic Journal
- Countries: IL
- Source: openalex
- URL: https://doi.org/10.2139/ssrn.4902016
- PDF: https://doi.org/10.2139/ssrn.4902016

## 12. Distance Correlation GAN: Fair Tabular Data Generation with Generative Adversarial Networks

- Authors: Amirarsalan Rajabi; Özlem Özmen Garibay
- Year: 2023
- DOI: 10.1007/978-3-031-35891-3_26
- Venue: Lecture notes in computer science
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1007/978-3-031-35891-3_26

## 13. Imbalanced tabular data modelization using CTGAN and machine learning to improve IoT Botnet attacks detection

- Authors: Omar Habibi; Mohammed Chemmakha; Mohamed Lazaar
- Year: 2022
- DOI: 10.1016/j.engappai.2022.105669
- Venue: Engineering Applications of Artificial Intelligence
- Countries: MA
- Source: openalex
- URL: https://doi.org/10.1016/j.engappai.2022.105669

## 14. TabFairGAN: Fair Tabular Data Generation with Generative Adversarial Networks

- Authors: Amirarsalan Rajabi; Özlem Özmen Garibay
- Year: 2022
- DOI: 10.3390/make4020022
- Venue: Machine Learning and Knowledge Extraction
- Countries: US
- Source: openalex
- URL: https://doi.org/10.3390/make4020022
- PDF: https://www.mdpi.com/2504-4990/4/2/22/pdf?version=1652689073

With the increasing reliance on automated decision making, the issue of algorithmic fairness has gained increasing importance. In this paper, we propose a Generative Adversarial Network for tabular data generation. The model includes two phases of training. In the first phase, the model is trained to accurately generate synthetic data similar to the reference dataset. In the second phase we modify the value function to add fairness constraint, and continue training the network to generate data that is both accurate and fair. We test our results in both cases of unconstrained, and constrained fair data generation. We show that using a fairly simple architecture and applying quantile transformation of numerical attributes the model achieves promising performance. In the unconstrained case, i.e., when the model is only trained in the first phase and is only meant to generate accurate data following the same joint probability distribution of the real data, the results show that the model beats the state-of-the-art GANs proposed in the literature to produce synthetic tabular data. Furthermore, in the constrained case in which the first phase of training is followed by the second phase, we train the network and test it on four datasets studied in the fairness literature and compare our results with another state-of-the-art pre-processing method, and present the promising results that it achieves. Comparing to other studies utilizing GANs for fair data generation, our model is comparably more stable by using only one critic, and also by avoiding major problems of original GAN model, such as mode-dropping and non-convergence.

## 15. Generative AI for synthetic data across multiple medical modalities: A systematic review of recent developments and challenges

- Authors: Mahmoud Ibrahim; Yasmina Al Khalil; Sina Amirrajab; Chang Sun; Marcel Breeuwer; Josien P. W. Pluim; Bart Elen; Gökhan Ertaylan; Michel Dumontier
- Year: 2025
- DOI: 10.1016/j.compbiomed.2025.109834
- Venue: Computers in Biology and Medicine
- Countries: BE; NL
- Source: openalex
- URL: https://doi.org/10.1016/j.compbiomed.2025.109834
- PDF: https://doi.org/10.1016/j.compbiomed.2025.109834

This paper presents a comprehensive systematic review of generative models (GANs, VAEs, DMs, and LLMs) used to synthesize various medical data types, including imaging (dermoscopic, mammographic, ultrasound, CT, MRI, and X-ray), text, time-series, and tabular data (EHR). Unlike previous narrowly focused reviews, our study encompasses a broad array of medical data modalities and explores various generative models. Our aim is to offer insights into their current and future applications in medical research, particularly in the context of synthesis applications, generation techniques, and evaluation methods, as well as providing a GitHub repository as a dynamic resource for ongoing collaboration and innovation. Our search strategy queries databases such as Scopus, PubMed, and ArXiv, focusing on recent works from January 2021 to November 2023, excluding reviews and perspectives. This period emphasizes recent advancements beyond GANs, which have been extensively covered in previous reviews. The survey also emphasizes the aspect of conditional generation, which is not focused on in similar work. Key contributions include a broad, multi-modality scope that identifies cross-modality insights and opportunities unavailable in single-modality surveys. While core generative techniques are transferable, we find that synthesis methods often lack sufficient integration of patient-specific context, clinical knowledge, and modality-specific requirements tailored to the unique characteristics of medical data. Conditional models leveraging textual conditioning and multimodal synthesis remain underexplored but offer promising directions for innovation. Our findings are structured around three themes: (1) Synthesis applications, highlighting clinically valid synthesis applications and significant gaps in using synthetic data beyond augmentation, such as for validation and evaluation; (2) Generation techniques, identifying gaps in personalization and cross-modality innovation; and (3) Evaluation methods, revealing the absence of standardized benchmarks, the need for large-scale validation, and the importance of privacy-aware, clinically relevant evaluation frameworks. These findings emphasize the need for benchmarking and comparative studies to promote openness and collaboration.

## 16. A Hybrid GAN-Based Approach to Solve Imbalanced Data Problem in Recommendation Systems

- Authors: Wafa Shafqat; Yung-Cheol Byun
- Year: 2022
- DOI: 10.1109/access.2022.3141776
- Venue: IEEE Access
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.1109/access.2022.3141776
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/9668973/09676570.pdf

With the advent of information technology, the amount of online data generation has been massive. Recommendation systems have become an effective tool in filtering information and solving the problem of information overload. Machine learning algorithms to build these recommendation systems require well-balanced data in terms of class distribution, but real-world datasets are mostly imbalanced in nature. Imbalanced data imposes a classifier to focus more on the majority class, neglecting other classes of interests and thus hindering the predictive performance of any classification model. There exist many traditional techniques for oversampling minority classes. Still, generative adversarial networks (GAN) have been showing excellent results in generating realistic synthetic tabular data that keeps the probability distribution of the original data intact. In this paper, we propose a hybrid GAN approach to solve the data imbalance problem to enhance recommendation systems’ performance. We implemented conditional Wasserstein GAN with gradient penalty to generate tabular data containing both numerical and categorical values. We also augmented auxiliary classifier loss to enforce the model to explicitly generate data belonging to the minority class. We designed the discriminator architecture with the concept of PacGAN to receive m-packed samples as input instead of a single input. This inclusion of the PacGAN architecture eliminated the mode collapse problem in our proposed model. We did a two-fold evaluation of our model. Firstly based on the quality of the generated data and secondly on how different recommendation models perform using the generated data compared to original data.

## 17. GANBLR: A Tabular Data Generation Model

- Authors: Yishuo Zhang; Nayyar A. Zaidi; Jiahui Zhou; Gang Li
- Year: 2021
- DOI: 10.1109/icdm51629.2021.00103
- Venue: 2021 IEEE International Conference on Data Mining (ICDM)
- Countries: AU; CN
- Source: openalex
- URL: https://doi.org/10.1109/icdm51629.2021.00103
- PDF: https://figshare.com/articles/conference_contribution/GANBLR_A_Tabular_Data_Generation_Model/20617020

Generative Adversarial Network (GAN) models have shown to be effective in a wide range of machine learning applications, and tabular data generation process has not been an exception. Notably, some state-of-the-art models of tabular data generation, such as CTGAN, TableGan, MedGAN, etc. are based on GAN models. Even though these models have resulted in superiour performance in generating artificial data when trained on a range of datasets, there is a lot of room (and desire) for improvement. Not to mention that existing methods do have some weaknesses other than performance. E.g., the current methods focus only on the performance of the model, and limited emphasis is given to the interpretation of the model. Secondly, the current models operate on raw features only, and hence they fail to exploit any prior knowledge on explicit feature interactions that can be utilized during data generation process. To alleviate the two above-mentioned limitations, in this work, we propose a novel tabular data generation model– Generative Adversarial Network modelling inspired from Naive Bayes and Logistic Regression’s relationship (GANBLR), which can not only address the interpretation limitation in existing tabular GAN-based models but can provide capability to handle explicit feature interactions. By extensively evaluating on wide range of datasets, we demonstrate GANBLR’S superiour performance as well as better interpretable capability (explanation of feature importance in the synthetic generation process) as compared to existing state-of-the-art tabular data generation models.

## 18. DP-CTGAN: Differentially Private Medical Data Generation Using CTGANs

- Authors: Fang Mei; Devendra Singh Dhami; Kristian Kersting
- Year: 2022
- DOI: 10.1007/978-3-031-09342-5_17
- Venue: Lecture notes in computer science
- Countries: DE
- Source: openalex
- URL: https://doi.org/10.1007/978-3-031-09342-5_17

## 19. The Effectiveness of Zero-Day Attacks Data Samples Generated via GANs on Deep Learning Classifiers

- Authors: Νικόλαος Πεππές; Theodoros Alexakis; Evgenia Adamopoulou; Konstantinos Demestichas
- Year: 2023
- DOI: 10.3390/s23020900
- Venue: Sensors
- Countries: GR
- Source: openalex
- URL: https://doi.org/10.3390/s23020900
- PDF: https://www.mdpi.com/1424-8220/23/2/900/pdf?version=1673527835

Digitization of most of the services that people use in their everyday life has, among others, led to increased needs for cybersecurity. As digital tools increase day by day and new software and hardware launch out-of-the box, detection of known existing vulnerabilities, or zero-day as they are commonly known, becomes one of the most challenging situations for cybersecurity experts. Zero-day vulnerabilities, which can be found in almost every new launched software and/or hardware, can be exploited instantly by malicious actors with different motives, posing threats for end-users. In this context, this study proposes and describes a holistic methodology starting from the generation of zero-day-type, yet realistic, data in tabular format and concluding to the evaluation of a Neural Network zero-day attacks' detector which is trained with and without synthetic data. This methodology involves the design and employment of Generative Adversarial Networks (GANs) for synthetically generating a new and larger dataset of zero-day attacks data. The newly generated, by the Zero-Day GAN (ZDGAN), dataset is then used to train and evaluate a Neural Network classifier for zero-day attacks. The results show that the generation of zero-day attacks data in tabular format reaches an equilibrium after about 5000 iterations and produces data that are almost identical to the original data samples. Last but not least, it should be mentioned that the Neural Network model that was trained with the dataset containing the ZDGAN generated samples outperformed the same model when the later was trained with only the original dataset and achieved results of high validation accuracy and minimal validation loss.

## 20. Evaluation of Synthetic Categorical Data Generation Techniques for Predicting Cardiovascular Diseases and Post-Hoc Interpretability of the Risk Factors

- Authors: Clara García-Vicente; David Chushig-Muzo; Inmaculada Mora-Jiménez; Himar Fabelo; Inger Torhild Gram; Maja‐Lisa Løchen; Conceição Granja; Cristina Soguero-Ruíz
- Year: 2023
- DOI: 10.3390/app13074119
- Venue: Applied Sciences
- Countries: ES; NO
- Source: openalex
- URL: https://doi.org/10.3390/app13074119
- PDF: https://www.mdpi.com/2076-3417/13/7/4119/pdf?version=1679900852

Machine Learning (ML) methods have become important for enhancing the performance of decision-support predictive models. However, class imbalance is one of the main challenges for developing ML models, because it may bias the learning process and the model generalization ability. In this paper, we consider oversampling methods for generating synthetic categorical clinical data aiming to improve the predictive performance in ML models, and the identification of risk factors for cardiovascular diseases (CVDs). We performed a comparative study of several categorical synthetic data generation methods, including Synthetic Minority Oversampling Technique Nominal (SMOTEN), Tabular Variational Autoencoder (TVAE) and Conditional Tabular Generative Adversarial Networks (CTGANs). Then, we assessed the impact of combining oversampling strategies and linear and nonlinear supervised ML methods. Lastly, we conducted a post-hoc model interpretability based on the importance of the risk factors. Experimental results show the potential of GAN-based models for generating high-quality categorical synthetic data, yielding probability mass functions that are very close to those provided by real data, maintaining relevant insights, and contributing to increasing the predictive performance. The GAN-based model and a linear classifier outperform other oversampling techniques, improving the area under the curve by 2%. These results demonstrate the capability of synthetic data to help with both determining risk factors and building models for CVD prediction.

## 21. Utilizing TGAN and ConSinGAN for Improved Tool Wear Prediction: A Comparative Study with ED-LSTM, GRU, and CNN Models

- Authors: Milind Shah; Himanshu Borade; Vipul Dave; Hitesh Agrawal; Pranav Nair; Vinay Vakharia
- Year: 2024
- DOI: 10.3390/electronics13173484
- Venue: Electronics
- Countries: IN; SE
- Source: openalex
- URL: https://doi.org/10.3390/electronics13173484
- PDF: https://www.mdpi.com/2079-9292/13/17/3484/pdf?version=1725274161

Developing precise deep learning (DL) models for predicting tool wear is challenging, particularly due to the scarcity of experimental data. To address this issue, this paper introduces an innovative approach that leverages the capabilities of tabular generative adversarial networks (TGAN) and conditional single image GAN (ConSinGAN). These models are employed to generate synthetic data, thereby enriching the dataset and enhancing the robustness of the predictive models. The efficacy of this methodology was rigorously evaluated using publicly available milling datasets. The pre-processing of acoustic emission data involved the application of the Walsh-Hadamard transform, followed by the generation of spectrograms. These spectrograms were then used to extract statistical attributes, forming a comprehensive feature vector for model input. Three DL models—encoder-decoder long short-term memory (ED-LSTM), gated recurrent unit (GRU), and convolutional neural network (CNN)—were applied to assess their tool wear prediction capabilities. The application of 10-fold cross-validation across these models yielded exceptionally low RMSE and MAE values of 0.02 and 0.16, respectively, underscoring the effectiveness of this approach. The results not only highlight the potential of TGAN and ConSinGAN in mitigating data scarcity but also demonstrate significant improvements in the accuracy of tool wear predictions, paving the way for more reliable and precise predictive maintenance in manufacturing processes.

## 22. Assessment of differentially private synthetic data for utility and fairness in end-to-end machine learning pipelines for tabular data

- Authors: Mayana Pereira; Meghana Kshirsagar; Sumit Mukherjee; Rahul Dodhia; Juan Lavista Ferres; Rafael T. de Sousa
- Year: 2024
- DOI: 10.1371/journal.pone.0297271
- Venue: PLoS ONE
- Countries: BR; US
- Source: openalex
- URL: https://doi.org/10.1371/journal.pone.0297271
- PDF: https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0297271&type=printable

Differentially private (DP) synthetic datasets are a solution for sharing data while preserving the privacy of individual data providers. Understanding the effects of utilizing DP synthetic data in end-to-end machine learning pipelines impacts areas such as health care and humanitarian action, where data is scarce and regulated by restrictive privacy laws. In this work, we investigate the extent to which synthetic data can replace real, tabular data in machine learning pipelines and identify the most effective synthetic data generation techniques for training and evaluating machine learning models. We systematically investigate the impacts of differentially private synthetic data on downstream classification tasks from the point of view of utility as well as fairness. Our analysis is comprehensive and includes representatives of the two main types of synthetic data generation algorithms: marginal-based and GAN-based. To the best of our knowledge, our work is the first that: (i) proposes a training and evaluation framework that does not assume that real data is available for testing the utility and fairness of machine learning models trained on synthetic data; (ii) presents the most extensive analysis of synthetic dataset generation algorithms in terms of utility and fairness when used for training machine learning models; and (iii) encompasses several different definitions of fairness. Our findings demonstrate that marginal-based synthetic data generators surpass GAN-based ones regarding model training utility for tabular data. Indeed, we show that models trained using data generated by marginal-based algorithms can exhibit similar utility to models trained using real data. Our analysis also reveals that the marginal-based synthetic data generated using AIM and MWEM PGM algorithms can train models that simultaneously achieve utility and fairness characteristics close to those obtained by models trained with real data.

## 23. Comparison of tabular synthetic data generation techniques using propensity and cluster log metric

- Authors: Aryan Pathare; Ramchandra Mangrulkar; Kartik Suvarna; Aryan Parekh; Govind Thakur; Aruna Gawade
- Year: 2023
- DOI: 10.1016/j.jjimei.2023.100177
- Venue: International Journal of Information Management Data Insights
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.1016/j.jjimei.2023.100177
- PDF: https://doi.org/10.1016/j.jjimei.2023.100177

• Comparative evaluation of synthetic data generation models on different datasets. • The best performing model was found to be CART. • The worst performing model was Bayesian network. • RNN generates data with high utility, however its execution time is very high. • GANs gave subpar or mediocre results at best. In the 21st-century, data is as valuable as gold. Many data-centric applications are generating a vast amount of data. Businesses can use this generated data to pinpoint the various sources of problems, if any. In addition, the data can help enterprises to identify connections between what is happening in different areas, departments, and systems. However, having more data is not enough; the data should also be of high quality. For example, taking action based on unfamiliar evidence, speculative ideas, or observations could lead to the wastage of resources. Whereas using high-quality data will help achieve correct results. Synthetic data is artificially generated data. Synthetic data is generated by an algorithm and used to represent real-world data, test datasets, perform mathematical model validation, and, most importantly, for training of machine learning models. Synthetic data can also be used to preserve data privacy. It is considered a safe way to transfer sensitive data because it creates a transaction database that does not contain any confidential information. This paper compares the tabular synthetic data generation techniques using various datasets, viz. balanced datasets, unbalanced datasets, datasets with numerical attributes only, datasets with categorical attributes only and mixed datasets. The utility of the generated synthetic data is measured using the Propensity score metric and Cluster-Log metric. The main finding of this paper is that the Classification And Regression Tree (CART) model provides the best results for all types of datasets. At the same time, Generative Adversarial Networks (GANs) give subpar or mediocre results at best. This contradicts the common belief that GANs are the go-to models for producing synthetic data.

## 24. CasTGAN: Cascaded Generative Adversarial Network for Realistic Tabular Data Synthesis

- Authors: Abdallah Alshantti; Damiano Varagnolo; Adil Rasheed; A Rahmati; Frank Westad
- Year: 2024
- DOI: 10.1109/access.2024.3356913
- Venue: IEEE Access
- Countries: NO
- Source: openalex
- URL: https://doi.org/10.1109/access.2024.3356913
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/6514899/10410850.pdf

Generative adversarial networks (GANs) have drawn considerable attention in recent years for their proven capability in generating synthetic data which can be utilized for multiple purposes. While GANs have demonstrated tremendous successes in producing synthetic data samples that replicate the dynamics of the original datasets, the validity of the synthetic data and the underlying privacy concerns represent major challenges which are not sufficiently addressed. In this work, we design a cascaded tabular GAN framework (CasTGAN) for generating realistic tabular data with a specific focus on the validity of the output. In this context, validity refers to the the dependency between features that can be found in the real data, but is typically misrepresented by traditional generative models. Our key idea entails that employing a cascaded architecture in which a dedicated generator samples each feature, the synthetic output becomes more representative of the real data. Our experimental results demonstrate that our model is capable of generating synthetic tabular data that can be used for fitting machine learning models, as CasTGAN’s classification performance only falls under the real training data’s PR-AUC score by 4.88% on average for classification datasets, and exhibits an average reduction of the real training data’s R2 score by 0.139 for regression datasets. In addition, our model captures well the constraints and the correlations between the features of the real data, especially the high dimensional datasets. Assessing the generation of invalid records demonstrates that CasTGAN reduces the number of invalid data observations by up to 622% in comparison to the second best performing baseline tabular GAN model. Furthermore, we evaluate the risk of white-box privacy attacks on our model and subsequently show that applying some perturbations to the auxiliary learners in CasTGAN increases the overall robustness of our model against targeted attacks.

## 25. Synthetic Data Generation for Healthcare: Exploring Generative Adversarial Networks Variants for Medical Tabular Data

- Authors: Halal Abdulrahman Ahmed; Juan A. Nepomuceno; Belén Vega-Márquez; Isabel A. Nepomuceno-Chamorro
- Year: 2025
- DOI: 10.1007/s41060-025-00816-w
- Venue: International Journal of Data Science and Analytics
- Countries: ES
- Source: openalex
- URL: https://doi.org/10.1007/s41060-025-00816-w
- PDF: https://link.springer.com/content/pdf/10.1007/s41060-025-00816-w.pdf

Abstract Recently, the medical and healthcare fields have experienced significant improvements. However, the restrictions of ethical constraints, privacy regulations, and preservation for sharing sensitive personal information limit access to real patient data. Synthetic datasets with generative models are considered one of the most reliable solutions that meet strict data protection requirements. Synthetic data are created in a controlled environment but possess the same statistical and structural properties as real data. In this work, we generate synthetic data using six variations of generative adversarial networks (GANs): GAN, CGAN, CTGAN, CRAMER GAN, DRAGAN, and WGAN. We explore the efficacy of synthetic data in three distinct healthcare datasets: Breast Cancer Wisconsin (Diagnostic), Lung Cancer Patient, and Fetal Cardiotocography CTG. To evaluate the performance of these generated datasets in classification tasks, we employ two diverse classifiers, namely XGBoost and SVM. In addition, we employ correlation and statistical analyses to scrutinise GAN models, identifying optimal variants for specific data generation tasks. Our experimental framework encompasses the examination of original (real), synthetic, and hybrid (original and synthetic) datasets. Our findings highlight a notable improvement in classification accuracy when using advanced GAN models such as CGAN and CTGAN to generate tabular data. This research sheds light on the potential of synthetic data in bolstering data privacy while facilitating meaningful insights in the realm of healthcare analytics.

## 26. GAN-Based Tabular Data Generator for Constructing Synopsis in Approximate Query Processing: Challenges and Solutions

- Authors: Mohammadali Fallahian; Mohsen Dorodchi; Kyle Kreth
- Year: 2024
- DOI: 10.3390/make6010010
- Venue: Machine Learning and Knowledge Extraction
- Countries: US
- Source: openalex
- URL: https://doi.org/10.3390/make6010010
- PDF: https://www.mdpi.com/2504-4990/6/1/10/pdf?version=1705409960

In data-driven systems, data exploration is imperative for making real-time decisions. However, big data are stored in massive databases that are difficult to retrieve. Approximate Query Processing (AQP) is a technique for providing approximate answers to aggregate queries based on a summary of the data (synopsis) that closely replicates the behavior of the actual data; this can be useful when an approximate answer to queries is acceptable in a fraction of the real execution time. This study explores the novel utilization of a Generative Adversarial Network (GAN) for the generation of tabular data that can be employed in AQP for synopsis construction. We thoroughly investigate the unique challenges posed by the synopsis construction process, including maintaining data distribution characteristics, handling bounded continuous and categorical data, and preserving semantic relationships, and we then introduce the advancement of tabular GAN architectures that overcome these challenges. Furthermore, we propose and validate a suite of statistical metrics tailored for assessing the reliability of GAN-generated synopses. Our findings demonstrate that advanced GAN variations exhibit a promising capacity to generate high-fidelity synopses, potentially transforming the efficiency and effectiveness of AQP in data-driven systems.

## 27. SOS

- Authors: Jayoung Kim; Chaejeong Lee; Yehjin Shin; Sewon Park; Minjung Kim; Noseong Park; Jihoon Cho
- Year: 2022
- DOI: 10.1145/3534678.3539454
- Venue: Proceedings of the 28th ACM SIGKDD Conference on Knowledge Discovery and Data Mining
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.1145/3534678.3539454

Score-based generative models (SGMs) are a recent breakthrough in generating fake images. SGMs are known to surpass other generative models, e.g., generative adversarial networks (GANs) and variational autoencoders (VAEs). Being inspired by their big success, in this work, we fully customize them for generating fake tabular data. In particular, we are interested in oversampling minor classes since imbalanced classes frequently lead to sub-optimal training outcomes. To our knowledge, we are the first presenting a score-based tabular data oversampling method. Firstly, we re-design our own score network since we have to process tabular data. Secondly, we propose two options for our generation method: the former is equivalent to a style transfer for tabular data and the latter uses the standard generative policy of SGMs. Lastly, we define a fine-tuning method, which further enhances the oversampling quality. In our experiments with 6 datasets and 10 baselines, our method outperforms other oversampling methods in all cases.

## 28. Generation of Synthetic Tabular Healthcare Data Using Generative Adversarial Networks

- Authors: Alireza Nik; Michael A. Riegler; Pål Halvorsen; Andrea M. Storås
- Year: 2023
- DOI: 10.1007/978-3-031-27077-2_34
- Venue: Lecture notes in computer science
- Countries: NO
- Source: openalex
- URL: https://doi.org/10.1007/978-3-031-27077-2_34
- PDF: https://hdl.handle.net/10037/33130

## 29. GANs in the Panorama of Synthetic Data Generation Methods

- Authors: Bruno Vaz; Álvaro Figueira
- Year: 2024
- DOI: 10.1145/3657294
- Venue: ACM Transactions on Multimedia Computing Communications and Applications
- Countries: PT
- Source: openalex
- URL: https://doi.org/10.1145/3657294
- PDF: https://dl.acm.org/doi/pdf/10.1145/3657294

This article focuses on the creation and evaluation of synthetic data to address the challenges of imbalanced datasets in machine learning (ML) applications, using fake news detection as a case study. We conducted a thorough literature review on generative adversarial networks (GANs) for tabular data, synthetic data generation methods, and synthetic data quality assessment. By augmenting a public news dataset with synthetic data generated by different GAN architectures, we demonstrate the potential of synthetic data to improve ML models’ performance in fake news detection. Our results show a significant improvement in classification performance, especially in the underrepresented class. We also modify and extend a data usage approach to evaluate the quality of synthetic data and investigate the relationship between synthetic data quality and data augmentation performance in classification tasks. We found a positive correlation between synthetic data quality and performance in the underrepresented class, highlighting the importance of high-quality synthetic data for effective data augmentation.

## 30. Tab-VAE: A Novel VAE for Generating Synthetic Tabular Data

- Authors: Syed Tazwar; Max Knobbout; Enrique Vílchez Quesada; Mirela Popa
- Year: 2024
- DOI: 10.5220/0012302400003654
- Venue: 
- Countries: NL
- Source: openalex
- URL: https://doi.org/10.5220/0012302400003654
- PDF: https://doi.org/10.5220/0012302400003654

Variational Autoencoders (VAEs) suffer from a well-known problem of overpruning or posterior collapse due to strong regularization while working in a sufficiently high-dimensional latent space. When VAEs are used to generate tabular data, categorical one-hot encoded data expand the dimensionality of the feature space dramatically, making modeling multi-class categorical data challenging. In this paper, we propose Tab-VAE, a novel VAE-based approach to generate synthetic tabular data that tackles this challenge by introducing a sampling technique at inference for categorical variables. A detailed review of the current state-of-theart models shows that most of the tabular data generation approaches draw methodologies from Generative Adversarial Networks (GANs) while a simpler more stable VAE method is ignored. Our extensive evaluation of the Tab-VAE with other leading generative models shows Tab-VAE improves the state-of-the-art VAEs significantly. It also shows that Tab-VAE outperforms the best GAN-based tabular data generators, paving the way for a powerful and less computationally expensive tabular data generation model.

## 31. DATGAN: Integrating expert knowledge into deep learning for synthetic tabular data

- Authors: Gael Lederrey; Tim Hillel; Michel Bierlaire
- Year: 2022
- DOI: 10.48550/arxiv.2203.03489
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2203.03489
- PDF: https://arxiv.org/pdf/2203.03489

Synthetic data can be used in various applications, such as correcting bias datasets or replacing scarce original data for simulation purposes. Generative Adversarial Networks (GANs) are considered state-of-the-art for developing generative models. However, these deep learning models are data-driven, and it is, thus, difficult to control the generation process. It can, therefore, lead to the following issues: lack of representativity in the generated data, the introduction of bias, and the possibility of overfitting the sample's noise. This article presents the Directed Acyclic Tabular GAN (DATGAN) to address these limitations by integrating expert knowledge in deep learning models for synthetic tabular data generation. This approach allows the interactions between variables to be specified explicitly using a Directed Acyclic Graph (DAG). The DAG is then converted to a network of modified Long Short-Term Memory (LSTM) cells to accept multiple inputs. Multiple DATGAN versions are systematically tested on multiple assessment metrics. We show that the best versions of the DATGAN outperform state-of-the-art generative models on multiple case studies. Finally, we show how the DAG can create hypothetical synthetic datasets.

## 32. Stress testing electrical grids: Generative Adversarial Networks for load scenario generation

- Authors: Matteo Rizzato; Nicolas Morizet; William Maréchal; Christophe Geissler
- Year: 2022
- DOI: 10.1016/j.egyai.2022.100177
- Venue: Energy and AI
- Countries: 
- Source: openalex
- URL: https://doi.org/10.1016/j.egyai.2022.100177
- PDF: https://doi.org/10.1016/j.egyai.2022.100177

As the energy transition is upon us, the replacement of combustion engines by electrical ones will imply a greater stress on the electrical grid of different countries. Therefore, it is of paramount importance to simulate a great number of hypothetical multi-variant scenarios to correctly plan the roll-out of new grids. In this paper, we deploy Generative Adversarial Networks (GANs) to swiftly reproduce the non-Gaussian and multimodal distribution of real energy-related samples, making GANs a valuable tool for data generation in the field. In particular, we propose an original dataset deriving from the aggregation of two European providers including hourly electric inland generation from several European countries. This dataset also comes along with the corresponding season, day of the week, hour of the day and macro-economic variables aiming at unequivocally describing the country’s energetic profile. Finally, we evaluate the performance of our model via dedicated metrics capable of grasping the non-Gaussian nature of the data and compare it with the state-of-the-art model for tabular data generation.

## 33. Tabular transformer generative adversarial network for heterogeneous distribution in healthcare

- Authors: Ha Ye Jin Kang; Minsam Ko; Kwang Sun Ryu
- Year: 2025
- DOI: 10.1038/s41598-025-93077-3
- Venue: Scientific Reports
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.1038/s41598-025-93077-3
- PDF: https://www.nature.com/articles/s41598-025-93077-3.pdf

In healthcare, the most common type of data is tabular data, which holds high significance and potential in the field of medical AI. However, privacy concerns have hindered their widespread use. Despite the emergence of synthetic data as a viable solution, the generation of healthcare tabular data (HTD) is complex owing to the extensive interdependencies between the variables within each record that incorporate diverse clinical characteristics, including sensitive information. To overcome these issues, this study proposed a tabular transformer generative adversarial network (TT-GAN) to generate synthetic data that can effectively consider the relationships between variables potentially present in the HTD dataset. Transformers can consider the relationships between the columns in each record using a multi-attention mechanism. In addition, to address the potential risk of restoring sensitive data in patient information, a Transformer was employed in a generative adversarial network (GAN) architecture, to ensure an implicit-based algorithm. To consider the heterogeneous characteristics of the continuous variables in the HTD dataset, the discretization and converter methodology were applied. The experimental results confirmed the superior performance of the TT-GAN than the Conditional Tabular GAN (CTGAN) and copula GAN. Discretization and converters were proven to be effective using our proposed Transformer algorithm. However, the application of the same methodology to Transformer-based models without discretization and converters exhibited a significantly inferior performance. The CTGAN and copula GAN indicated minimal effectiveness with discretization and converter methodologies. Thus, the TT-GAN exhibited considerable potential in healthcare, demonstrating its ability to generate artificial data that closely resembled real healthcare datasets. The ability of the algorithm to handle different types of mixed variables efficiently, including polynomial, discrete, and continuous variables, demonstrated its versatility and practicality in health care research and data synthesis.

## 34. A Methodology and an Empirical Analysis to Determine the Most Suitable Synthetic Data Generator

- Authors: Ajmeera Kiran; Shubham Kumar
- Year: 2024
- DOI: 10.1109/access.2024.3354277
- Venue: IEEE Access
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.1109/access.2024.3354277
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/6514899/10400420.pdf

According to a report published by Gartner in 2021, a significant portion of Machine Learning (ML) training data will be artificially generated. This development has led to the emergence of various synthetic data generators (SDGs), particularly those based on Generative Adversarial Networks (GAN). All research endeavors so far have been exploratory, focused on specific objectives such as validating utility or disclosure control or assessing how generators can decrease or increase inherent bias with differential privacy. Hence, we aim to empirically identify an AI-based, data generator that can produce datasets that closely resemble real datasets, while also determining the hyper-parameters that enable a satisfactory balance between utility, privacy, and fairness in the datasets. To achieve this, we utilize the Synthetic Data Vault, Data Synthesizer, and Smartnoise-synth, which are three synthetic data generation packages that are accessible via Python. Different data generation models available within the package are presented with 13 tabular datasets iteratively as sample inputs to generate synthetic data. We generated synthetic data using every dataset and generator and investigated the goodness of the generator using five hypothetical scenarios. The utility and privacy offered by the generated data were compared with those of real data. The fairness in the ML model trained with synthetic data was used as a third metric for evaluation. Finally, we employ synthetic data to train regression and classification Machine Learning (ML) algorithms and evaluate their performance. After conducting experiments, analyzing metrics, and comparing ML scores across all 11 generators, we determined that the CTGAN from SDV and PATECTGAN from the SN-synth package were the most effective in mimicking real data for all 13 datasets utilized in our research.

## 35. <b>GANBLR++</b>: Incorporating Capacity to Generate Numeric Attributes and Leveraging Unrestricted Bayesian Networks

- Authors: Yishuo Zhang; Nayyar A. Zaidi; Jiahui Zhou; Gang Li
- Year: 2022
- DOI: 10.1137/1.9781611977172.34
- Venue: Society for Industrial and Applied Mathematics eBooks
- Countries: 
- Source: openalex
- URL: https://doi.org/10.1137/1.9781611977172.34

Generative Adversarial Networks (GAN) models have led to a major breakthrough in data generation of various sorts. Over the years, we have seen several applications of GAN-based learning for tabular data generation as well. Very recently, GAN-based learning by incorporating Bayesian Networks (BN) as generator and discriminator – GANBLR, has shown to lead to state-of-the-art (SOTA) results for tabular data generation. Despite the impressive performance, GANBLR has an inherent weakness that it can only generate data with categorical attributes. Additionally, the model is trained and tested only with a restricted Bayesian Network. In this work, we have proposed an extension over GANBLR framework – GANBLR++, that has the capacity to generate numeric attributes, by leveraging Dirichlet Mixture Model. We also leverage unrestricted BN in GANBLR framework, and discuss how the use of unrestricted BN can lead to better quality data, as well as more interpretable model. We evaluate the effectiveness of GANBLR++ on wide range of datasets by demonstrating that it generates data of better quality as compared to existing SOTA models for tabular (numeric and categorical) data generation such as CTGAN, MedGAN and TableGAN.

## 36. Synthetic Tabular Data Based on Generative Adversarial Networks in Health Care: Generation and Validation Using the Divide-and-Conquer Strategy

- Authors: Ha Ye Jin Kang; Erdenebileg Batbaatar; Dong‐Woo Choi; Kui Son Choi; Minsam Ko; Kwang Sun Ryu
- Year: 2023
- DOI: 10.2196/47859
- Venue: JMIR Medical Informatics
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.2196/47859
- PDF: https://medinform.jmir.org/2023/1/e47859/PDF

BACKGROUND: Synthetic data generation (SDG) based on generative adversarial networks (GANs) is used in health care, but research on preserving data with logical relationships with synthetic tabular data (STD) remains challenging. Filtering methods for SDG can lead to the loss of important information. OBJECTIVE: This study proposed a divide-and-conquer (DC) method to generate STD based on the GAN algorithm, while preserving data with logical relationships. METHODS: The proposed method was evaluated on data from the Korea Association for Lung Cancer Registry (KALC-R) and 2 benchmark data sets (breast cancer and diabetes). The DC-based SDG strategy comprises 3 steps: (1) We used 2 different partitioning methods (the class-specific criterion distinguished between survival and death groups, while the Cramer V criterion identified the highest correlation between columns in the original data); (2) the entire data set was divided into a number of subsets, which were then used as input for the conditional tabular generative adversarial network and the copula generative adversarial network to generate synthetic data; and (3) the generated synthetic data were consolidated into a single entity. For validation, we compared DC-based SDG and conditional sampling (CS)-based SDG through the performances of machine learning models. In addition, we generated imbalanced and balanced synthetic data for each of the 3 data sets and compared their performance using 4 classifiers: decision tree (DT), random forest (RF), Extreme Gradient Boosting (XGBoost), and light gradient-boosting machine (LGBM) models. RESULTS: The synthetic data of the 3 diseases (non-small cell lung cancer [NSCLC], breast cancer, and diabetes) generated by our proposed model outperformed the 4 classifiers (DT, RF, XGBoost, and LGBM). The CS- versus DC-based model performances were compared using the mean area under the curve (SD) values: 74.87 (SD 0.77) versus 63.87 (SD 2.02) for NSCLC, 73.31 (SD 1.11) versus 67.96 (SD 2.15) for breast cancer, and 61.57 (SD 0.09) versus 60.08 (SD 0.17) for diabetes (DT); 85.61 (SD 0.29) versus 79.01 (SD 1.20) for NSCLC, 78.05 (SD 1.59) versus 73.48 (SD 4.73) for breast cancer, and 59.98 (SD 0.24) versus 58.55 (SD 0.17) for diabetes (RF); 85.20 (SD 0.82) versus 76.42 (SD 0.93) for NSCLC, 77.86 (SD 2.27) versus 68.32 (SD 2.37) for breast cancer, and 60.18 (SD 0.20) versus 58.98 (SD 0.29) for diabetes (XGBoost); and 85.14 (SD 0.77) versus 77.62 (SD 1.85) for NSCLC, 78.16 (SD 1.52) versus 70.02 (SD 2.17) for breast cancer, and 61.75 (SD 0.13) versus 61.12 (SD 0.23) for diabetes (LGBM). In addition, we found that balanced synthetic data performed better. CONCLUSIONS: This study is the first attempt to generate and validate STD based on a DC approach and shows improved performance using STD. The necessity for balanced SDG was also demonstrated.

## 37. An Empirical Study on the Membership Inference Attack against Tabular Data Synthesis Models

- Authors: Jihyeon Hyeong; Jayoung Kim; Noseong Park; Sushil Jajodia
- Year: 2022
- DOI: 10.1145/3511808.3557546
- Venue: Proceedings of the 31st ACM International Conference on Information &amp; Knowledge Management
- Countries: KR; US
- Source: openalex
- URL: https://doi.org/10.1145/3511808.3557546

Tabular data typically contains private and important information; thus, precautions must be taken before they are shared with others. Although several methods (e.g., differential privacy and k-anonymity) have been proposed to prevent information leakage, in recent years, tabular data synthesis models have become popular because they can well trade-off between data utility and privacy. However, recent research has shown that generative models for image data are susceptible to the membership inference attack, which can determine whether a given record was used to train a victim synthesis model. In this paper, we investigate the membership inference attack in the context of tabular data synthesis. We conduct experiments on 4 state-of-the-art tabular data synthesis models under two attack scenarios (i.e., one black-box and one white-box attack), and find that the membership inference attack can seriously jeopardize these models. We next conduct experiments to evaluate how well two popular differentially-private deep learning training algorithms, DP-SGD and DP-GAN, can protect the models against the attack. Our key finding is that both algorithms can largely alleviate this threat by sacrificing the generation quality.

## 38. Generative Adversarial Networks for Dynamic Malware Behavior: A Comprehensive Review, Categorization, and Analysis

- Authors: Ghebrebrhan Weldit Gebrehans; Naveed Ilyas; Khouloud Eledlebi; Willian T. Lunardi; Martin Andreoni Lopez; Chan Yeob Yeun; Ernesto Damiani
- Year: 2025
- DOI: 10.1109/tai.2025.3537966
- Venue: IEEE Transactions on Artificial Intelligence
- Countries: AE; US
- Source: openalex
- URL: https://doi.org/10.1109/tai.2025.3537966
- PDF: https://doi.org/10.1109/tai.2025.3537966

This article highlights the critical role of machine learning (ML) in combating the dynamic nature of cybersecurity threats. Unlike previous studies focusing mainly on static analysis, this work surveys the literature on dynamic analysis-based malware generation and detection. The study addresses the complexities of applying GANs to tabular data with heavy-tailed and multimodal distributions. It also examines the challenges of generating sequential malware behavior data and categorizes GAN-based models and their primary use cases. Furthermore, the article evaluates adversarial losses and their limitations in generating dynamic malware behavior. Finally, it identifies existing metrics to assess GAN generalization in malware research and suggests future research directions based on identified limitations.

## 39. Synthesising Tabular Datasets Using Wasserstein Conditional GANS with Gradient Penalty (WCGAN-GP)

- Authors: Susan McKeever; Manhar Singh Walia
- Year: 2020
- DOI: 10.21427/e6wa-sz92
- Venue: Arrow - TU Dublin (Technological University Dublin)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.21427/e6wa-sz92
- PDF: https://arrow.tudublin.ie/cgi/viewcontent.cgi?article=1304&context=scschcomcon

Deep learning based methods based on Generative Adversarial Networks (GANs) have seen remarkable success in data synthesis of images and text. This study investigates the use of GANs for the generation of tabular mixed dataset. We apply Wasserstein Conditional Generative Adversarial Network (WCGAN-GP) to the task of generating tabular synthetic data that is indistinguishable from the real data, without incurring information leakage. The performance of WCGAN-GP is compared against both the ground truth datasets and SMOTE using three labelled real-world datasets from different domains. Our results for WCGAN-GP show that the synthetic data preserves distributions and relationships of the real data, outperforming the SMOTE approach on both class preservation and data protection metrics. Our work is a contribution towards the automated synthesis of tabular mixed data

## 40. Generating Synthetic Fermentation Data of Shindari, a Traditional Jeju Beverage, Using Multiple Imputation Ensemble and Generative Adversarial Networks

- Authors: Debapriya Hazra; Yung-Cheol Byun
- Year: 2021
- DOI: 10.3390/app11062787
- Venue: Applied Sciences
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.3390/app11062787
- PDF: https://www.mdpi.com/2076-3417/11/6/2787/pdf?version=1616227028

Fermentation is an age-old technique used to preserve food by restoring proper microbial balance. Boiled barley and nuruk are fermented for a short period to produce Shindari, a traditional beverage for the people of Jeju, South Korea. Shindari has been proven to be a drink of multiple health benefits if fermented for an optimal period. It is necessary to predict the ideal fermentation time required by each microbial community to keep the advantages of the microorganisms produced by the fermentation process in Shindari intact and to eliminate contamination. Prediction through machine learning requires past data but the process of obtaining fermentation data of Shindari is time consuming, expensive, and not easily available. Therefore, there is a need to generate synthetic fermentation data to explore various benefits of the drink and to reduce any risk from overfermentation. In this paper, we propose a model that takes incomplete tabular fermentation data of Shindari as input and uses multiple imputation ensemble (MIE) and generative adversarial networks (GAN) to generate synthetic fermentation data that can be later used for prediction and microbial spoilage control. For multiple imputation, we used multivariate imputation by chained equations and random forest imputation, and ensembling was done using the bagging and stacking method. For generating synthetic data, we remodeled the tabular GAN with skip connections and adapted the architecture of Wasserstein GAN with gradient penalty. We compared the performance of our model with other imputation and ensemble models using various evaluation metrics and visual representations. Our GAN model could overcome the mode collapse problem and converged at a faster rate than existing GAN models for synthetic data generation. Experiment results show that our proposed model executes with less error, is more accurate, and generates significantly better synthetic fermentation data compared to other models.

## 41. Discovering the Correlation Between Phishing Susceptibility Causing Data Biases and Big Five Personality Traits Using C-GAN

- Authors: Atta Ur Rahman; Feras Al‐Obeidat; Abdallah Tubaishat; Babar Shah; Sajid Anwar; Zahid Halim
- Year: 2022
- DOI: 10.1109/tcss.2022.3201153
- Venue: IEEE Transactions on Computational Social Systems
- Countries: AE; PK
- Source: openalex
- URL: https://doi.org/10.1109/tcss.2022.3201153

Recently, on social media, various kinds of social engineering (SE) have made individuals more susceptible to attacks. A phishing attempt is a widely used SE technique that takes advantage of people’s vulnerabilities to acquire personal or confidential information. These attempts are growing at an astonishing speed, causing harm to both individuals and corporations. According to the latest studies, certain individuals are more vulnerable to such kinds of attacks than others. However, the relationship between psychological characteristics and phishing attacks has not been adequately investigated. This study empirically explores the connection between phishing vulnerability that causes data biases and the Big Five personality traits. Recognizing personality traits that make people more vulnerable to phishing attempts is a key step in developing protection and safeguarding individuals. The individuals who scored high in some traits are more probable to suffer from such assault. To the best of our knowledge, no prior quantitative study has attempted to find many genuine phishing victims and their personality behavior. This problem lacks the availability of publically accessible data. It is also challenging to estimate the probability distribution of rows in tabular data and generate realistic synthetic data to train/test the model on more data. This work employs a conditional generative adversarial network (C-GAN) for both data generation and classification to find the correlation between personality traits and phishing attacks.

## 42. GAN-Based Novel Approach for Generating Synthetic Medical Tabular Data

- Authors: Rashid Nasimov; Nigorakhon Nasimova; Sanjar Mirzakhalilov; Gül Tokdemir; M. Rizwan; Akmalbek Abdusalomov; Young Im Cho
- Year: 2024
- DOI: 10.3390/bioengineering11121288
- Venue: Bioengineering
- Countries: IN; KR; TR; UZ
- Source: openalex
- URL: https://doi.org/10.3390/bioengineering11121288
- PDF: https://www.mdpi.com/2306-5354/11/12/1288/pdf?version=1734528936

The generation of synthetic medical data has become a focal point for researchers, driven by the increasing demand for privacy-preserving solutions. While existing generative methods heavily rely on real datasets for training, access to such data is often restricted. In contrast, statistical information about these datasets is more readily available, yet current methods struggle to generate tabular data solely from statistical inputs. This study addresses the gaps by introducing a novel approach that converts statistical data into tabular datasets using a modified Generative Adversarial Network (GAN) architecture. A custom loss function was incorporated into the training process to enhance the quality of the generated data. The proposed method is evaluated using fidelity and utility metrics, achieving "Good" similarity and "Excellent" utility scores. While the generated data may not fully replace real databases, it demonstrates satisfactory performance for training machine-learning algorithms. This work provides a promising solution for synthetic data generation when real datasets are inaccessible, with potential applications in medical data privacy and beyond.

## 43. TabSynDex: A Universal Metric for Robust Evaluation of Synthetic Tabular Data

- Authors: Vikram S Chundawat; Ayush K Tarun; Murari Mandal; Mukund Lahoti; Pratik Narang
- Year: 2022
- DOI: 10.48550/arxiv.2207.05295
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2207.05295
- PDF: https://arxiv.org/pdf/2207.05295

Synthetic tabular data generation becomes crucial when real data is limited, expensive to collect, or simply cannot be used due to privacy concerns. However, producing good quality synthetic data is challenging. Several probabilistic, statistical, generative adversarial networks (GANs), and variational auto-encoder (VAEs) based approaches have been presented for synthetic tabular data generation. Once generated, evaluating the quality of the synthetic data is quite challenging. Some of the traditional metrics have been used in the literature but there is lack of a common, robust, and single metric. This makes it difficult to properly compare the effectiveness of different synthetic tabular data generation methods. In this paper we propose a new universal metric, TabSynDex, for robust evaluation of synthetic data. The proposed metric assesses the similarity of synthetic data with real data through different component scores which evaluate the characteristics that are desirable for ``high quality'' synthetic data. Being a single score metric and having an implicit bound, TabSynDex can also be used to observe and evaluate the training of neural network based approaches. This would help in obtaining insights that was not possible earlier. We present several baseline models for comparative analysis of the proposed evaluation metric with existing generative models. We also give a comparative analysis between TabSynDex and existing synthetic tabular data evaluation metrics. This shows the effectiveness and universality of our metric over the existing metrics. Source Code: \url{https://github.com/vikram2000b/tabsyndex}

## 44. Evaluation of Synthetic Data Generation Techniques in the Domain of Anonymous Traffic Classification

- Authors: Drake Cullen; James R. Halladay; Nathan Briner; Ram B. Basnet; Jeremy M. Bergen; Tenzin Doleck
- Year: 2022
- DOI: 10.1109/access.2022.3228507
- Venue: IEEE Access
- Countries: CA; US
- Source: openalex
- URL: https://doi.org/10.1109/access.2022.3228507
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/6514899/09980373.pdf

Anonymous network traffic is more pervasive than ever due to the accessibility of services such as virtual private networks (VPN) and The Onion Router (Tor). To address the need to identify and classify this traffic, machine and deep learning solutions have become the standard. However, high-performing classifiers often scale poorly when applied to real-world traffic classification due to the heavily skewed nature of network traffic data. Prior research has found synthetic data generation to be effective at alleviating concerns surrounding class imbalance, though a limited number of these techniques have been applied to the domain of anonymous network traffic detection. This work compares the ability of a Conditional Tabular Generative Adversarial Network (CTGAN), Copula Generative Adversarial Network (CopulaGAN), Variational Autoencoder (VAE), and Synthetic Minority Over-sampling Technique (SMOTE) to create viable synthetic anonymous network traffic samples. Moreover, we evaluate the performance of several shallow boosting and bagging classifiers as well as deep learning models on the synthetic data. Ultimately, we amalgamate the data generated by the GANs, VAE, and SMOTE into a comprehensive dataset dubbed CMU-SynTraffic-2022 for future research on this topic. Our findings show that SMOTE consistently outperformed the other upsampling techniques, improving classifiers’ F1-scores over the control by ~7.5% for application type characterization. Among the tested classifiers, Light Gradient Boosting Machine achieved the highest F1-score of 90.3% on eight application types.

## 45. Using Generative Adversarial Networks for Handling Class Imbalance Problem

- Authors: Mürüvvet Aslı Aydin
- Year: 2021
- DOI: 10.1109/siu53274.2021.9477939
- Venue: 
- Countries: 
- Source: openalex
- URL: https://doi.org/10.1109/siu53274.2021.9477939

Having more samples belonging to one class than the samples of the other class in data used in a classification task is known as class imbalance problem. Handling class imbalance is crucial since the classifier's performance is highly affected. One of the solution approaches of this problem is to make the data balanced by generating synthetic data. Employing resampling methods is a common way of generating synthetic data. Although adversarial generative networks (GANs) are mainly designed to generate image data, they can also be an alternative to solve the class imbalance problem by generating tabular data. This work presents a comparative study of resampling methods with GANs based methods. The performance of machine learning methods improved by 27% if the data is balanced with resampling methods. However, similar performance results were observed with working on imbalanced data if the GANs based methods are employed for synthetic data generation.

## 46. Generating Time-Series Data Using Generative Adversarial Networks for Mobility Demand Prediction

- Authors: Subhajit Chatterjee; Yung-Cheol Byun
- Year: 2022
- DOI: 10.32604/cmc.2023.032843
- Venue: Computers, materials & continua/Computers, materials & continua (Print)
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.32604/cmc.2023.032843
- PDF: https://file.techscience.com/files/cmc/2023/TSP_CMC-74-3/TSP_CMC_32843/TSP_CMC_32843.pdf

The increasing penetration rate of electric kickboard vehicles has been popularized and promoted primarily because of its clean and efficient features. Electric kickboards are gradually growing in popularity in tourist and education-centric localities. In the upcoming arrival of electric kickboard vehicles, deploying a customer rental service is essential. Due to its free-floating nature, the shared electric kickboard is a common and practical means of transportation. Relocation plans for shared electric kickboards are required to increase the quality of service, and forecasting demand for their use in a specific region is crucial. Predicting demand accurately with small data is troublesome. Extensive data is necessary for training machine learning algorithms for effective prediction. Data generation is a method for expanding the amount of data that will be further accessible for training. In this work, we proposed a model that takes time-series customers’ electric kickboard demand data as input, pre-processes it, and generates synthetic data according to the original data distribution using generative adversarial networks (GAN). The electric kickboard mobility demand prediction error was reduced when we combined synthetic data with the original data. We proposed Tabular-GAN-Modified-WGAN-GP for generating synthetic data for better prediction results. We modified The Wasserstein GAN-gradient penalty (GP) with the RMSprop optimizer and then employed Spectral Normalization (SN) to improve training stability and faster convergence. Finally, we applied a regression-based blending ensemble technique that can help us to improve performance of demand prediction. We used various evaluation criteria and visual representations to compare our proposed model’s performance. Synthetic data generated by our suggested GAN model is also evaluated. The TGAN-Modified-WGAN-GP model mitigates the overfitting and mode collapse problem, and it also converges faster than previous GAN models for synthetic data creation. The presented model’s performance is compared to existing ensemble and baseline models. The experimental findings imply that combining synthetic and actual data can significantly reduce prediction error rates in the mean absolute percentage error (MAPE) of 4.476 and increase prediction accuracy.

## 47. Qualitative and Quantitative Evaluation of Multivariate Time-Series Synthetic Data Generated Using MTS-TGAN: A Novel Approach

- Authors: Parul Yadav; Manish Gaur; Nishat Fatima; Saqib Sarwar
- Year: 2023
- DOI: 10.3390/app13074136
- Venue: Applied Sciences
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.3390/app13074136
- PDF: https://www.mdpi.com/2076-3417/13/7/4136/pdf?version=1679896230

To obtain high performance, generalization, and accuracy in machine learning applications, such as prediction or anomaly detection, large datasets are a necessary prerequisite. Moreover, the collection of data is time-consuming, difficult, and expensive for many imbalanced or small datasets. These challenges are evident in collecting data for financial and banking services, pharmaceuticals and healthcare, manufacturing and the automobile, robotics car, sensor time-series data, and many more. To overcome the challenges of data collection, researchers in many domains are becoming more and more interested in the development or generation of synthetic data. Generating synthetic time-series data is far more complicated and expensive than generating synthetic tabular data. The primary objective of the paper is to generate multivariate time-series data (for continuous and mixed parameters) that are comparable and evaluated with real multivariate time-series synthetic data. After being trained to produce such data, a novel GAN architecture named as MTS-TGAN is proposed and then assessed using both qualitative measures namely t-SNE, PCA, discriminative and predictive scores as well as quantitative measures, for which an RNN model is implemented, which calculates MAE and MSLE scores for three training phases; Train Real Test Real, Train Real Test Synthetic and Train Synthetic Test Real. The model is able to reduce the overall error up to 13% and 10% in predictive and discriminative scores, respectively. The research’s objectives are met, and the outcomes demonstrate that MTS-TGAN is able to pick up on the distribution and underlying knowledge included in the attributes of the real data and it can serve as a starting point for additional research in the respective area.

## 48. Generation of Synthetic 5G Network Dataset Using Generative Adversarial Network (GAN)

- Authors: Muhammad Nur Aqmal Khatiman; Asma Abu-Samah; Muhammad Amin Azman; Rosdiadee Nordin; Nor Fadzilah Abdullah
- Year: 2023
- DOI: 10.1109/micc59384.2023.10419563
- Venue: 
- Countries: MY
- Source: openalex
- URL: https://doi.org/10.1109/micc59384.2023.10419563

While the Fifth Generation (5G) network is actively being deployed in most countries to create new possibilities for better lifestyle and economic development, it is a technology that is currently being a focal point for researchers across the world along with 6G. Starting from 3GPP Release-18, Artificial Intelligent (AI) and Machine Learning (ML) are identified as enabler towards intelligent network in 5G and beyond. Nevertheless, the models based on AI/ML need a sufficient amount of data for learning patterns and relationships, enabling them to provide precise predictions for unfamiliar data and situations. The existence of Generative Adversarial Network (GAN) helps solve the issue by generating fake data from an existing dataset to resemble real-world data to be used in training and testing of different algorithms. In this paper, the process of generating synthetic data of 5G network was demonstrated from an extensive test drive results that will encourage innovation in mobile communication. Generation of data use two types of GAN which are the Conditional Tabular GAN (CTGAN) and Topological Variational Autoencoder (TVAE). The two algorithms were compared based on statistical analysis such as the distribution and Pearson Correlation analysis. TVAE showed a better overall performance score (94.14%) over CTGAN (89.66%) when compared with the original data, but the CTGAN produced more similar distribution for certain individual columns.

## 49. Synthesizing Mixed-type Electronic Health Records using Diffusion Models

- Authors: Taha Ceritli; Ghadeer O. Ghosheh; Vinod Kumar Chauhan; Tingting Zhu; Andrew P. Creagh; David A. Clifton
- Year: 2023
- DOI: 10.48550/arxiv.2302.14679
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2302.14679
- PDF: https://arxiv.org/pdf/2302.14679

Electronic Health Records (EHRs) contain sensitive patient information, which presents privacy concerns when sharing such data. Synthetic data generation is a promising solution to mitigate these risks, often relying on deep generative models such as Generative Adversarial Networks (GANs). However, recent studies have shown that diffusion models offer several advantages over GANs, such as generation of more realistic synthetic data and stable training in generating data modalities, including image, text, and sound. In this work, we investigate the potential of diffusion models for generating realistic mixed-type tabular EHRs, comparing TabDDPM model with existing methods on four datasets in terms of data quality, utility, privacy, and augmentation. Our experiments demonstrate that TabDDPM outperforms the state-of-the-art models across all evaluation metrics, except for privacy, which confirms the trade-off between privacy and utility.

## 50. Enhancing IoT Intrusion Detection Systems Through Horizontal Federated Learning and Optimized WGAN-GP

- Authors: Wayoud Bouzeraib; Afifa Ghenai; Nadia Zeghib
- Year: 2025
- DOI: 10.1109/access.2025.3547255
- Venue: IEEE Access
- Countries: DZ
- Source: openalex
- URL: https://doi.org/10.1109/access.2025.3547255
- PDF: https://doi.org/10.1109/access.2025.3547255

The Internet of Things (IoT) ecosystem is fraught with substantial vulnerabilities, particularly in the realm of cybersecurity attacks. Network Intrusion Detection Systems (NIDS) stand as a pivotal element in mitigating these cybersecurity risks. This paper introduces an innovative approach to fortifying IoT security by effectively addressing the data limitations inherent in AI-based NIDS. We present a data generation model that harnesses Generative Adversarial Networks (GANs). Specifically, the GAN variant we employ is Wasserstein GAN with Gradient Penalty (WGAN-GP), which combines the Wasserstein loss formulation with a gradient norm penalty to stabilize training and improve the quality of generated data. The performance is optimized with Genetic Algorithms, focusing on hyper-parameter selection and federated learning for shared model weights. The model’s training is conducted on four well-established benchmark datasets: UNSW-NB15, IoT-23, CSE-CIC-IDS2018, and MQTT-IoT-IDS2020. We conduct a comprehensive comparative analysis between the generated synthetic data and real-world datasets, rigorously assessing their impact on training Machine Learning (ML) models. The findings underscore the efficacy of our approach, demonstrating a significant improvement in detection accuracy, achieving a 99% accuracy rate when combining the generated data with real datasets. This study highlights the paramount significance of innovative techniques in enhancing the security of IoT systems. Furthermore, it presents a promising avenue for generating high-quality synthetic tabular data, despite its complexity and time-consuming implementation. Such data can be leveraged across a large spectrum of applications, including training ML models, data augmentation, and privacy-preserving data sharing.

## 51. Generating Synthetic Data to Reduce Prediction Error of Energy Consumption

- Authors: Debapriya Hazra; Wafa Shafqat; Yung-Cheol Byun
- Year: 2021
- DOI: 10.32604/cmc.2022.020143
- Venue: Computers, materials & continua/Computers, materials & continua (Print)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.32604/cmc.2022.020143
- PDF: https://www.techscience.com/cmc/v70n2/44683/pdf

Renewable and nonrenewable energy sources are widely incorporated for solar and wind energy that produces electricity without increasing carbon dioxide emissions. Energy industries worldwide are trying hard to predict future energy consumption that could eliminate over or under contracting energy resources and unnecessary financing. Machine learning techniques for predicting energy are the trending solution to overcome the challenges faced by energy companies. The basic need for machine learning algorithms to be trained for accurate prediction requires a considerable amount of data. Another critical factor is balancing the data for enhanced prediction. Data Augmentation is a technique used for increasing the data available for training. Synthetic data are the generation of new data which can be trained to improve the accuracy of prediction models. In this paper, we propose a model that takes time series energy consumption data as input, pre-processes the data, and then uses multiple augmentation techniques and generative adversarial networks to generate synthetic data which when combined with the original data, reduces energy consumption prediction error. We propose TGAN-skip-Improved-WGAN-GP to generate synthetic energy consumption time series tabular data. We modify TGAN with skip connections, then improve WGAN-GP by defining a consistency term, and finally use the architecture of improved WGAN-GP for training TGAN-skip. We used various evaluation metrics and visual representation to compare the performance of our proposed model. We also measured prediction accuracy along with mean and maximum error generated while predicting with different variations of augmented and synthetic data with original data. The mode collapse problem could be handled by TGAN-skip-Improved-WGAN-GP model and it also converged faster than existing GAN models for synthetic data generation. The experiment result shows that our proposed technique of combining synthetic data with original data could significantly reduce the prediction error rate and increase the prediction accuracy of energy consumption.

## 52. Comparative Analysis of Generative AI Techniques for Addressing the Tabular Data Generation Problem in Medical Records

- Authors: S. S. Aravinth; S Srithar; K. Pranay Joseph; U. Gopala Anil Varma; G. Madhu Kiran; Venkatesh Jonna
- Year: 2023
- DOI: 10.1109/icraset59632.2023.10419886
- Venue: 
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.1109/icraset59632.2023.10419886

This research paper explores the use of Generative Artificial Intelligence (GAI) techniques to create synthetic medical datasets that balance data realism and privacy preservation. The sensitivity of medical records poses challenges for data access and sharing, making GAI a promising solution. The study evaluates five key approaches—StyleGAN2, CLIP, T5, ViT, and specialized Tabular GANs—across three critical dimensions: distribution fidelity, attribute correlation preservation, and pattern recognition accuracy. The results reveal the strengths and limitations of each technique in generating realistic medical data. StyleGAN2, CLIP, and T5 excel in all dimensions, making them ideal for various applications requiring high-quality synthetic medical datasets. ViT shows promise but may need fine-tuning for specific use cases, while specialized Tabular GANs demonstrate potential but vary in performance. This comparative analysis provides valuable insights for researchers and practitioners at the intersection of Generative AI and healthcare data generation. It underscores the potential of Generative AI in addressing the tabular data generation challenge in medical records, offering realistic and privacy-conscious alternatives for data utilization and model training.

## 53. Low-sample classification in NIDS using the EC-GAN method

- Authors: Marko Zekan; Igor Tomičić; Markus Schatten
- Year: 2022
- DOI: 10.3897/jucs.85703
- Venue: JUCS - Journal of Universal Computer Science
- Countries: 
- Source: openalex
- URL: https://doi.org/10.3897/jucs.85703
- PDF: https://lib.jucs.org/article/85703/download/pdf/

Numerous advanced methods have been applied throughout the years for the use in Network Intrusion Detection Systems (NIDS). Among these are various Deep Learning models, which have shown great success for attack classification. Nevertheless, false positive rate and detection rate of these systems remains a concern. This is mostly because of the low-sample, imbalanced nature of realistic datasets, which make models challenging to train. Considering this, we applied a novel semi-supervised EC-GAN method for network flow classifi- cation of CIC-IDS-2017 dataset. EC-GAN uses synthetic data to aid the training of a supervised classifier on low-sample data. To achieve this, we modified the original EC-GAN to work with tabular data. In our approach, WCGAN-GP is used for synthetic tabular data generation, while&amp;nbsp; a simple deep neural network is used for classification. The conditional nature of WCGAN-GP diminishes the class imbalance problem, while GAN itself solves the low-sample problem. This approach was successful in generating believable synthetic data, which was consequently used for training and testing the EC-GAN. To obtain our results, we trained a classifier on progressively smaller versions of the CIC-DIS-2017 dataset, first via a novel EC-GAN method and then in the conventional way, without the help of synthetic data. We then compared these two sets of results with another author&amp;rsquo;s results using accuracy, false positive rate, detection rate and macro F1 score as metrics. Our results showed that supervised classifier trained with EC-GAN can achieve significant results even when trained on as little as 25% of the original imbalanced dataset.

## 54. Tabular Transformer Generative Adversarial Network for Heterogeneous distribution in healthcare

- Authors: Ha Ye Jin Kang; Minsam Ko; Kwang Sun Ryu
- Year: 2024
- DOI: 10.21203/rs.3.rs-4134206/v1
- Venue: Research Square
- Countries: KR; US
- Source: openalex
- URL: https://doi.org/10.21203/rs.3.rs-4134206/v1
- PDF: https://www.researchsquare.com/article/rs-4134206/latest.pdf

## 55. CEHR-GPT: Generating Electronic Health Records with Chronological Patient Timelines

- Authors: Chao Pang; Xinzhuo Jiang; Nishanth Parameshwar Pavinkurve; Krishna S. Kalluri; Elise L. Minto; Jason Patterson; Linying Zhang; George Hripcsak; Gürsoy, Gamze; Noémie Elhadad; Karthik Natarajan
- Year: 2024
- DOI: 10.48550/arxiv.2402.04400
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2402.04400
- PDF: https://arxiv.org/pdf/2402.04400

Synthetic Electronic Health Records (EHR) have emerged as a pivotal tool in advancing healthcare applications and machine learning models, particularly for researchers without direct access to healthcare data. Although existing methods, like rule-based approaches and generative adversarial networks (GANs), generate synthetic data that resembles real-world EHR data, these methods often use a tabular format, disregarding temporal dependencies in patient histories and limiting data replication. Recently, there has been a growing interest in leveraging Generative Pre-trained Transformers (GPT) for EHR data. This enables applications like disease progression analysis, population estimation, counterfactual reasoning, and synthetic data generation. In this work, we focus on synthetic data generation and demonstrate the capability of training a GPT model using a particular patient representation derived from CEHR-BERT, enabling us to generate patient sequences that can be seamlessly converted to the Observational Medical Outcomes Partnership (OMOP) data format.

## 56. The Power of Generative AI: A Review of Requirements, Models, Input–Output Formats, Evaluation Metrics, and Challenges

- Authors: Ajay Bandi; Pydi Venkata Satya Ramesh Adapa; Yudu Eswar Vinay Pratap Kumar Kuchi
- Year: 2023
- DOI: 10.3390/fi15080260
- Venue: Future Internet
- Countries: US
- Source: openalex
- URL: https://doi.org/10.3390/fi15080260
- PDF: https://www.mdpi.com/1999-5903/15/8/260/pdf?version=1690812126

Generative artificial intelligence (AI) has emerged as a powerful technology with numerous applications in various domains. There is a need to identify the requirements and evaluation metrics for generative AI models designed for specific tasks. The purpose of the research aims to investigate the fundamental aspects of generative AI systems, including their requirements, models, input–output formats, and evaluation metrics. The study addresses key research questions and presents comprehensive insights to guide researchers, developers, and practitioners in the field. Firstly, the requirements necessary for implementing generative AI systems are examined and categorized into three distinct categories: hardware, software, and user experience. Furthermore, the study explores the different types of generative AI models described in the literature by presenting a taxonomy based on architectural characteristics, such as variational autoencoders (VAEs), generative adversarial networks (GANs), diffusion models, transformers, language models, normalizing flow models, and hybrid models. A comprehensive classification of input and output formats used in generative AI systems is also provided. Moreover, the research proposes a classification system based on output types and discusses commonly used evaluation metrics in generative AI. The findings contribute to advancements in the field, enabling researchers, developers, and practitioners to effectively implement and evaluate generative AI models for various applications. The significance of the research lies in understanding that generative AI system requirements are crucial for effective planning, design, and optimal performance. A taxonomy of models aids in selecting suitable options and driving advancements. Classifying input–output formats enables leveraging diverse formats for customized systems, while evaluation metrics establish standardized methods to assess model quality and performance.

## 57. A Comparison Study of Generative Adversarial Network Architectures for Malicious Cyber-Attack Data Generation

- Authors: Νικόλαος Πεππές; Theodoros Alexakis; Konstantinos Demestichas; Evgenia Adamopoulou
- Year: 2023
- DOI: 10.3390/app13127106
- Venue: Applied Sciences
- Countries: GR
- Source: openalex
- URL: https://doi.org/10.3390/app13127106
- PDF: https://www.mdpi.com/2076-3417/13/12/7106/pdf?version=1687245677

The digitization trend that prevails nowadays has led to increased vulnerabilities of tools and technologies of everyday life. One of the many different types of software vulnerabilities and attacks is botnets. Botnets enable attackers to gain remote control of the infected machines, often leading to disastrous consequences. Cybersecurity experts engage machine learning (ML) and deep learning (DL) technologies for designing and developing smart and proactive cybersecurity systems in order to tackle such infections. The development of such systems is, often, hindered by the lack of data that can be used to train them. Aiming to address this problem, this study proposes and describes a methodology for the generation of botnet-type data in tabular format. This methodology involves the design and development of two generative adversarial network (GAN) models, one with six layers and the other with eight layers, to identify the most efficient and reliable one in terms of the similarity of the generated data to the real ones. The two GAN models produce data in loops of 25, 50, 100, 250, 500 and 1000 epochs. The results are quite encouraging as, for both models, the similarity between the synthetic and the real data is around 80%. The eight-layer solution is slightly better as, after running for 1000 epochs, it achieved a similarity degree of 82%, outperforming the six-layer one, which achieved 77%. These results indicate that such solutions of data augmentation in the cybersecurity domain are feasible and reliable and can lead to new standards for developing and training trustworthy ML and DL solutions for detecting and tackling botnet attacks.

## 58. Design Target Achievement Index: A Differentiable Metric to Enhance Deep Generative Models in Multi-Objective Inverse Design

- Authors: Lyle Regenwetter; Faez Ahmed
- Year: 2022
- DOI: 10.1115/detc2022-91344
- Venue: 
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1115/detc2022-91344

Abstract Deep Generative Machine Learning Models have been growing in popularity across the design community thanks to their ability to learn and mimic complex data distributions. While early works are promising, further advancement will depend on addressing several critical considerations such as design quality, feasibility, novelty, and targeted inverse design. We propose the Design Target Achievement Index (DTAI), a differentiable, tunable metric that scores a design’s ability to achieve designer-specified minimum performance targets. We demonstrate that DTAI can drastically improve the performance of generated designs when directly used as a training loss in Deep Generative Models. We apply the DTAI loss to a Performance-Augmented Diverse GAN (PaDGAN) and demonstrate superior generative performance compared to a set of baseline Deep Generative Models including a Multi-Objective PaDGAN and specialized tabular generation algorithms like the Conditional Tabular GAN (CTGAN). We further enhance PaDGAN with an auxiliary feasibility classifier to encourage feasible designs. To evaluate methods, we propose a comprehensive set of evaluation metrics for generative methods that focus on feasibility, diversity, and satisfaction of design performance targets. Methods are tested on a challenging benchmarking problem: the FRAMED bicycle frame design dataset featuring mixed-datatype parametric data, heavily skewed and multimodal distributions, and ten competing performance objectives.

## 59. A Conditional GAN for Tabular Data Generation with Probabilistic Sampling of Latent Subspaces

- Authors: Leonidas Akritidis; Panayiotis Bozanis
- Year: 2025
- DOI: 10.48550/arxiv.2508.00472
- Venue: ArXiv.org
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2508.00472
- PDF: https://arxiv.org/pdf/2508.00472

The tabular form constitutes the standard way of representing data in relational database systems and spreadsheets. But, similarly to other forms, tabular data suffers from class imbalance, a problem that causes serious performance degradation in a wide variety of machine learning tasks. One of the most effective solutions dictates the usage of Generative Adversarial Networks (GANs) in order to synthesize artificial data instances for the under-represented classes. Despite their good performance, none of the proposed GAN models takes into account the vector subspaces of the input samples in the real data space, leading to data generation in arbitrary locations. Moreover, the class labels are treated in the same manner as the other categorical variables during training, so conditional sampling by class is rendered less effective. To overcome these problems, this study presents ctdGAN, a conditional GAN for alleviating class imbalance in tabular datasets. Initially, ctdGAN executes a space partitioning step to assign cluster labels to the input samples. Subsequently, it utilizes these labels to synthesize samples via a novel probabilistic sampling strategy and a new loss function that penalizes both cluster and class mis-predictions. In this way, ctdGAN is trained to generate samples in subspaces that resemble those of the original data distribution. We also introduce several other improvements, including a simple, yet effective cluster-wise scaling technique that captures multiple feature modes without affecting data dimensionality. The exhaustive evaluation of ctdGAN with 14 imbalanced datasets demonstrated its superiority in generating high fidelity samples and improving classification accuracy.

## 60. TabTransGAN: A hybrid approach integrating GAN and transformer architectures for tabular data synthesis

- Authors: Hanbing Zhang; Yinan Jing; Fei Zhang; Zhixin Li; X. Sean Wang; Zhenqiang Chen; Cheng Lv
- Year: 2025
- DOI: 10.1016/j.ipm.2025.104220
- Venue: Information Processing & Management
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1016/j.ipm.2025.104220

## 61. Improved Techniques for Training Tabular GANs Using Cramer’s V Statistics

- Authors: Melle Mendikowski; B. Schindler; Thomas Schmid; Ralf Möller; Mattis Hartwig
- Year: 2023
- DOI: 10.21428/594757db.4c0ffb71
- Venue: 
- Countries: DE
- Source: openalex
- URL: https://doi.org/10.21428/594757db.4c0ffb71
- PDF: https://caiac.pubpub.org/pub/0jwi0koo/download/pdf

Considering the growing global demand for machine learning training data, synthetic data generation is a reasonable way to address the versatile challenges in data acquisition. Conditional Tabular Generative Adversarial Network (CTGAN), an extension of the widely used Generative Adversarial Network (GAN), is considered one of the most promising techniques in the field of tabular data generation. Despite numerous successes of CTGAN, a lack of preserving categorical dependencies within the data has been identified. In prior work, the Cramerâs V (CV) as a natural metric for representing the correlation of categorical dependencies was proposed for hyperparameter tuning of CTGAN models. In this paper, we explore two novel strategies to directly integrate CV statistics of data batches within CTGAN training. The first approach is a generator loss term that penalizes differences between the CV statistics of the original and generated data. The second innovation is the extraction of the CV matrix as an additional feature for the critic. By applying our proposed methods to three benchmark datasets, we improve the averaged accuracy of supervised learning models trained on synthesized data by 11 % compared to the legacy CTGAN. We also outline the impact of CV statistics on preserving dependencies between categorical data columns in terms of integrity and contingency similarity, discuss existing challenges, and identify potential improvements.

## 62. Generating tabular datasets under differential privacy

- Authors: Gianluca Truda
- Year: 2023
- DOI: 10.48550/arxiv.2308.14784
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2308.14784
- PDF: https://arxiv.org/pdf/2308.14784

Machine Learning (ML) is accelerating progress across fields and industries, but relies on accessible and high-quality training data. Some of the most important datasets are found in biomedical and financial domains in the form of spreadsheets and relational databases. But this tabular data is often sensitive in nature. Synthetic data generation offers the potential to unlock sensitive data, but generative models tend to memorise and regurgitate training data, which undermines the privacy goal. To remedy this, researchers have incorporated the mathematical framework of Differential Privacy (DP) into the training process of deep neural networks. But this creates a trade-off between the quality and privacy of the resulting data. Generative Adversarial Networks (GANs) are the dominant paradigm for synthesising tabular data under DP, but suffer from unstable adversarial training and mode collapse, which are exacerbated by the privacy constraints and challenging tabular data modality. This work optimises the quality-privacy trade-off of generative models, producing higher quality tabular datasets with the same privacy guarantees. We implement novel end-to-end models that leverage attention mechanisms to learn reversible tabular representations. We also introduce TableDiffusion, the first differentially-private diffusion model for tabular data synthesis. Our experiments show that TableDiffusion produces higher-fidelity synthetic datasets, avoids the mode collapse problem, and achieves state-of-the-art performance on privatised tabular data synthesis. By implementing TableDiffusion to predict the added noise, we enabled it to bypass the challenges of reconstructing mixed-type tabular data. Overall, the diffusion paradigm proves vastly more data and privacy efficient than the adversarial paradigm, due to augmented re-use of each data batch and a smoother iterative training process.

## 63. Iterative Application of UMAP-Based Algorithms for Fully Synthetic Healthcare Tabular Data Generation

- Authors: Carla Lázaro; Cecilio Ángulo
- Year: 2024
- DOI: 10.3390/a17120591
- Venue: Algorithms
- Countries: ES
- Source: openalex
- URL: https://doi.org/10.3390/a17120591
- PDF: https://www.mdpi.com/1999-4893/17/12/591/pdf?version=1735021393

Building on a previously developed partially synthetic data generation algorithm utilizing data visualization techniques, this study extends the novel algorithm to generate fully synthetic tabular healthcare data. In this enhanced form, the algorithm serves as an alternative to conventional methods based on Generative Adversarial Networks (GANs) or Variational Autoencoders (VAEs). By iteratively applying the original methodology, the adapted algorithm employs UMAP (Uniform Manifold Approximation and Projection), a dimensionality reduction technique, to validate generated samples through low-dimensional clustering. This approach has been successfully applied to three healthcare domains: prostate cancer, breast cancer, and cardiovascular disease. The generated synthetic data have been rigorously evaluated for fidelity and utility. Results show that the UMAP-based algorithm outperforms GAN- and VAE-based generation methods across different scenarios. In fidelity assessments, it achieved smaller maximum distances between the cumulative distribution functions of real and synthetic data for different attributes. In utility evaluations, the UMAP-based synthetic datasets enhanced machine learning model performance, particularly in classification tasks. In conclusion, this method represents a robust solution for generating secure, high-quality synthetic healthcare data, effectively addressing data scarcity challenges.

## 64. Hierarchical Conditional Tabular GAN for Multi-Tabular Synthetic Data Generation

- Authors: Wilhelm Ågren; Victorio Úbeda Sosa
- Year: 2024
- DOI: 10.48550/arxiv.2411.07009
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2411.07009
- PDF: https://arxiv.org/pdf/2411.07009

The generation of synthetic data is a state-of-the-art approach to leverage when access to real data is limited or privacy regulations limit the usability of sensitive data. A fair amount of research has been conducted on synthetic data generation for single-tabular datasets, but only a limited amount of research has been conducted on multi-tabular datasets with complex table relationships. In this paper we propose the algorithm HCTGAN to synthesize multi-tabular data from complex multi-tabular datasets. We compare our results to the probabilistic model HMA1. Our findings show that our proposed algorithm can more efficiently sample large amounts of synthetic data for deep and complex multi-tabular datasets, whilst achieving adequate data quality and always guaranteeing referential integrity. We conclude that the HCTGAN algorithm is suitable for generating large amounts of synthetic data efficiently for deep multi-tabular datasets with complex relationships. We additionally suggest that the HMA1 model should be used on smaller datasets when emphasis is on data quality.

## 65. Improving irregular temporal modeling by integrating synthetic data to the electronic medical record using conditional GANs: a case study of fluid overload prediction in the intensive care unit

- Authors: Alireza Rafiei; Milad Ghiasi Rad; Andrea Sikora; Rishikesan Kamaleswaran
- Year: 2023
- DOI: 10.1101/2023.06.20.23291680
- Venue: medRxiv
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1101/2023.06.20.23291680
- PDF: https://www.medrxiv.org/content/medrxiv/early/2023/06/27/2023.06.20.23291680.full.pdf

Objective: The challenge of irregular temporal data, which is particularly prominent for medication use in the critically ill, limits the performance of predictive models. The purpose of this evaluation was to pilot test integrating synthetic data within an existing dataset of complex medication data to improve machine learning model prediction of fluid overload. Materials and Methods: 72 hours. Four machine learning algorithms to predict fluid overload after 48-72 hours of ICU admission were developed using the original dataset. Then, two distinct synthetic data generation methodologies (synthetic minority over-sampling technique (SMOTE) and conditional tabular generative adversarial network (CT-GAN)) were used to create synthetic data. Finally, a stacking ensemble technique designed to train a meta-learner was established. Models underwent training in three scenarios of varying qualities and quantities of datasets. Results: Training machine learning algorithms on the combined synthetic and original dataset overall increased the performance of the predictive models compared to training on the original dataset. The highest performing model was the metamodel trained on the combined dataset with 0.83 AUROC while it managed to significantly enhance the sensitivity across different training scenarios. Discussion: The integration of synthetically generated data is the first time such methods have been applied to ICU medication data and offers a promising solution to enhance the performance of machine learning models for fluid overload, which may be translated to other ICU outcomes. A meta-learner was able to make a trade-off between different performance metrics and improve the ability to identify the minority class.

## 66. Supporting Database Constraints in Synthetic Data Generation based on Generative Adversarial Networks

- Authors: Wanxin Li
- Year: 2020
- DOI: 10.1145/3318464.3384414
- Venue: 
- Countries: CA
- Source: openalex
- URL: https://doi.org/10.1145/3318464.3384414

With unprecedented development in machine learning algorithms, it is crucial to have available large amount of data to verify the correctness and efficiency of these algorithms. Due to privacy concerns, we may not always have enough real data to use. In our research, we focus on data synthesization for relational databases where the database constraints of the original data must be imposed to the generated data. To the best of our knowledge, no study has been conducted on supporting database constraints in synthetic data generation. We offer solutions by designing extensions to Tabular Generative Adversarial Network algorithm. We implemented a prototype for our approach, and compared the performance of different extensions by experiments. Related work on synthetic data generation includes classical statistical methods and neural network approaches. Synthetic Data Vault is developed using classical statistical methods. It uses Kolmogorov-Smirnov test to select the best statistical distribution to describe columnar data. TableGAN and Tabular GAN use neural networks to minimize cross entropy or Kullback-Leibler divergence on marginal distributions. The main challenges to our research problem are: Classical statistical distributions cannot describe complex and mixed distributions in relational databases. Database constraints are non-differentiable. Neural networks require loss functions to be differentiable.

## 67. A Comparative Analysis of GANs and Adaptive Bayesian Networks for Synthetic Tabular Data Generation

- Authors: T. Y. Lee; Xue-Ming Yuan
- Year: 2025
- DOI: 10.1145/3769002.3769989
- Venue: 
- Countries: SG
- Source: openalex
- URL: https://doi.org/10.1145/3769002.3769989

We present a comprehensive comparative analysis of Generative Adversarial Networks (GANs) and Adaptive Bayesian Networks (ABNs) for synthetic tabular data generation. Through systematic evaluation on benchmark datasets and real-world applications from healthcare, finance, and telecommunications, we compare these approaches across statistical fidelity, privacy preservation, computational efficiency, and downstream task performance. Key findings include: (1) ABNs demonstrate superior statistical fidelity on structured datasets with clear dependencies, (2) GANs generate more diverse samples but with higher privacy risk, and (3) computational requirements favor different methods based on dataset characteristics. Our analysis provides practical guidance for method selection and establishes benchmarking standards for synthetic data generation research.

## 68. HAR-CTGAN: A Mobile Sensor Data Generation Tool for Human Activity Recognition

- Authors: Joshua DeOliveira; Walter Gerych; Aruzhan Koshkarova; Elke A. Rundensteiner; Emmanuel Agu
- Year: 2022
- DOI: 10.1109/bigdata55660.2022.10020848
- Venue: 2022 IEEE International Conference on Big Data (Big Data)
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1109/bigdata55660.2022.10020848

Human activity recognition (HAR) is the process of using mobile sensor data to determine the physical activities performed by individuals. HAR is the backbone of many mobile healthcare applications, such as passive health monitoring systems, early diagnosing systems, and fall detection systems. Effective HAR models rely on deep learning architectures and big data in order to accurately classify activities. Unfortunately, HAR datasets are expensive to collect, are often mislabeled, and have large class imbalances. State-of-the-art approaches to address these challenges utilize Generative Adversarial Networks (GANs) for generating additional synthetic data along with their labels. Problematically, these HAR GANs only synthesize continuous features — features that are represented by real numbers — recorded from gyroscopes, accelerometers, and other sensors that produce continuous data. This is limiting since mobile sensor data commonly has discrete features that provide additional context such as device location and the time-of-day, which have been shown to substantially improve HAR classification. Hence, we studied Conditional Tabular Generative Adversarial Networks (CTGANs) for data generation to synthesize mobile sensor data containing both continuous and discrete features, a task never been done by state-of-the-art approaches. We show HAR-CTGANs generate data with greater realism resulting in allowing better downstream performance in HAR models, and when state-of-the-art models were modified with HAR-CTGAN characteristics, downstream performance also improves.

## 69. Large Language Models for Synthetic Tabular Health Data: A Benchmark Study

- Authors: Marko Miletic; Murat Sariyar
- Year: 2024
- DOI: 10.3233/shti240571
- Venue: Studies in health technology and informatics
- Countries: CH
- Source: openalex
- URL: https://doi.org/10.3233/shti240571
- PDF: https://ebooks.iospress.nl/pdf/doi/10.3233/SHTI240571

Synthetic tabular health data plays a crucial role in healthcare research, addressing privacy regulations and the scarcity of publicly available datasets. This is essential for diagnostic and treatment advancements. Among the most promising models are transformer-based Large Language Models (LLMs) and Generative Adversarial Networks (GANs). In this paper, we compare LLM models of the Pythia LLM Scaling Suite with varying model sizes ranging from 14M to 1B, against a reference GAN model (CTGAN). The generated synthetic data are used to train random forest estimators for classification tasks to make predictions on the real-world data. Our findings indicate that as the number of parameters increases, LLM models outperform the reference GAN model. Even the smallest 14M parameter models perform comparably to GANs. Moreover, we observe a positive correlation between the size of the training dataset and model performance. We discuss implications, challenges, and considerations for the real-world usage of LLM models for synthetic tabular data generation.

## 70. Trans-CTGAN: A Transformer-Enhanced GAN Model for Correlation-Preserving Tabular Data Generation

- Authors: Yuchen You; Jun Fang; Shuang Zhang
- Year: 2025
- DOI: 10.1109/ccet66260.2025.11199579
- Venue: 
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/ccet66260.2025.11199579

High-fidelity synthetic tabular data generation is crucial, given that downstream tasks and data analysis typically require large amounts of tabular data. However, existing methods struggle to model complex inter-feature correlations in tabular datasets (e.g., customer behavior logs or healthcare records). To address this challenge, we propose Trans-CTGAN, an improved GAN model integrating Transformer encoder. This model introduces multi-head attention mechanisms in both generator and discriminator to optimize global dependency modeling, enabling comprehensive capture of feature interactions. Extensive experiments on public datasets demonstrate superior performance: a 26.25 % average improvement in the <tex xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">$\mathbf{L 2}$</tex> distance of correlation matrices compared to baselines. This work provides a robust solution for generating high-fidelity synthetic tabular data with preserved feature correlations, offering both theoretical and practical value for data-sensitive applications.

## 71. Conditional Data Synthesis with Deep Generative Models for Imbalanced Dataset Oversampling

- Authors: Leonidas Akritidis; Athanasios Fevgas; Miltiadis Alamaniotis; Panayiotis Bozanis
- Year: 2023
- DOI: 10.1109/ictai59109.2023.00071
- Venue: 
- Countries: GR; US
- Source: openalex
- URL: https://doi.org/10.1109/ictai59109.2023.00071

The problem of data imbalance is defined as the uneven distribution of the training examples to the existing classes of a dataset. Among a wide variety of solutions, the oversampling techniques try to mitigate the problem by synthesizing artificial examples associated with the minority class. The huge success of Generative Adversarial Networks (GANs) rendered them an attractive choice for oversampling and numerous researchers proposed modifications of GANs for imbalanced datasets. Nevertheless, the existing models employ the entire minority class for sample generation, thus being vulnerable to outliers and noisy data instances. In addition, the majority of the relevant research concerns image classification tasks, leaving a large gap for research with tabular data. Finally, another powerful and popular generative model, the Variational Autoencoder (VAE) has been rather overlooked by the community in class imbalance solutions. In this paper we present SB-GAN and SB-VAE, two generative models that identify borderline and noisy samples before they are trained. In this manner SB-GAN and SB-VAE learn better class distributions that are not distorted by the existence of outliers. The experimental evaluation of SB-GAN and SB-VAE with 4 tabular datasets revealed a superior performance against 8 state-of-the-art oversampling techniques.

## 72. Generation of Synthetic Electronic Health Records Using a Federated GAN

- Authors: John E. Weldon; Tomás Ward; Eoin Brophy
- Year: 2021
- DOI: 10.48550/arxiv.2109.02543
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2109.02543
- PDF: https://arxiv.org/pdf/2109.02543

Sensitive medical data is often subject to strict usage constraints. In this paper, we trained a generative adversarial network (GAN) on real-world electronic health records (EHR). It was then used to create a data-set of "fake" patients through synthetic data generation (SDG) to circumvent usage constraints. This real-world data was tabular, binary, intensive care unit (ICU) patient diagnosis data. The entire data-set was split into separate data silos to mimic real-world scenarios where multiple ICU units across different hospitals may have similarly structured data-sets within their own organisations but do not have access to each other's data-sets. We implemented federated learning (FL) to train separate GANs locally at each organisation, using their unique data silo and then combining the GANs into a single central GAN, without any siloed data ever being exposed. This global, central GAN was then used to generate the synthetic patients data-set. We performed an evaluation of these synthetic patients with statistical measures and through a structured review by a group of medical professionals. It was shown that there was no significant reduction in the quality of the synthetic EHR when we moved between training a single central model and training on separate data silos with individual models before combining them into a central model. This was true for both the statistical evaluation (Root Mean Square Error (RMSE) of 0.0154 for single-source vs. RMSE of 0.0169 for dual-source federated) and also for the medical professionals' evaluation (no quality difference between EHR generated from a single source and EHR generated from multiple sources).

## 73. Predicting Spoilage Intensity Level in Sausage Products Using Explainable Machine Learning and GAN-Based Data Augmentation

- Authors: Volkan Ince; Mohamed Bader–El–Den; Ramazan Esmeli; Lalit Maurya; Omer Faruk Sari
- Year: 2025
- DOI: 10.1007/s11947-025-03971-x
- Venue: Food and Bioprocess Technology
- Countries: GB; KW; TR
- Source: openalex
- URL: https://doi.org/10.1007/s11947-025-03971-x
- PDF: https://link.springer.com/content/pdf/10.1007/s11947-025-03971-x.pdf

Abstract Spoilage in processed meat products, such as poultry and pork sausages, presents significant challenges for food safety, quality control, and waste reduction. This study presents a machine learning-based framework to classify spoilage intensity levels using sensory, physicochemical, and microbiological features. To overcome limitations caused by small datasets, we applied synthetic data augmentation using a tabular variational autoencoder (TVAE) to generate high-fidelity samples that enhance model generalization. Additionally, traditional oversampling techniques such as SMOTE and ADASYN were employed for comparative purposes and to further address class imbalance issues. Seven machine learning classifiers were evaluated logistic regression, support vector machine, K -nearest neighbors, random forest, gradient boosting, voting classifier, and multilayer perceptron. The best classification performance was achieved when models were trained on GAN-based synthetic data and tested on real samples. For poultry sausage spoilage prediction, the gradient boosting classifier reached the highest accuracy of 97%. For pork sausages, random forest achieved the highest accuracy of 95%. These results confirm the effectiveness of data augmentation in improving predictive robustness. To ensure model transparency, we integrated explainable AI techniques SHAP and LIME into the pipeline. These analyses revealed that sampling time, CO $$_2$$ <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML"> <mml:mmultiscripts> <mml:mrow/> <mml:mn>2</mml:mn> <mml:mrow/> </mml:mmultiscripts> </mml:math> concentration, pH, and microbial species such as Lactobacillus curvatus and Leuconostoc carnosum were among the most influential features in spoilage prediction. The combination of synthetic data generation and interpretable machine learning enables a reliable, scalable, and explainable approach to spoilage classification. This methodology has strong potential for enhancing quality control systems in the meat industry while reducing waste and improving safety along the food supply chain. Graphical abstract

## 74. Distributed Conditional GAN (discGAN) For Synthetic Healthcare Data Generation

- Authors: David Fuentes; Diana McSpadden; Sodiq Adewole
- Year: 2023
- DOI: 10.48550/arxiv.2304.04290
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2304.04290
- PDF: https://arxiv.org/pdf/2304.04290

In this paper, we propose a distributed Generative Adversarial Networks (discGANs) to generate synthetic tabular data specific to the healthcare domain. While using GANs to generate images has been well studied, little to no attention has been given to generation of tabular data. Modeling distributions of discrete and continuous tabular data is a non-trivial task with high utility. We applied discGAN to model non-Gaussian multi-modal healthcare data. We generated 249,000 synthetic records from original 2,027 eICU dataset. We evaluated the performance of the model using machine learning efficacy, the Kolmogorov-Smirnov (KS) test for continuous variables and chi-squared test for discrete variables. Our results show that discGAN was able to generate data with distributions similar to the real data.

## 75. Comparative Analysis of Tabular Generative Adversarial Network (GAN) Models for Generation and Validation of Power Grid Synthetic Datasets

- Authors: Darshana Upadhyay; Qiaodan Luo; Jaume Manero; Marzia Zaman; Srinivas Sampalli
- Year: 2023
- DOI: 10.1109/eurocon56442.2023.10199093
- Venue: 
- Countries: CA; ES
- Source: openalex
- URL: https://doi.org/10.1109/eurocon56442.2023.10199093

The demand for securing SCADA (Supervisory Control and Data Acquisition)-based power grid systems from cyber-attacks has been increasing significantly in the last few years. Current research trends widely adopt Machine Learning (ML) techniques to prevent attacks against such critical infrastructure. However, the efficiency of these techniques largely depends upon the availability of large datasets. Acquiring large data from such critical systems is not always feasible and this has inhibited the research progress in the development of advanced ML algorithms that can make a notable difference in the prediction of malicious events. Thus, there is a strong need for generating large synthetic yet realistic datasets from existing small datasets. This paper presents a comparative analysis of tabular Generative Adversarial Network (GAN) models for the generation and validation of synthetic datasets from existing datasets of power grids. Moreover, the synthetic datasets are validated using statistical analysis, and machine learning efficacy. These synthetic datasets open opportunities for the research community to explore advanced machine learning and deep learning methodologies for the protection of industrial systems.

## 76. Synthetic Data Meets Finance: Generative Models for Privacy Preserving Analytics

- Authors: Yongbin Yang; Jingyun Yang
- Year: 2026
- DOI: 10.55220/2576-6821.v10.928
- Venue: Journal of Banking and Financial Dynamics
- Countries: 
- Source: openalex
- URL: https://doi.org/10.55220/2576-6821.v10.928

The financial industry faces increasing pressure from privacy regulations, including the General Data Protection Regulation (GDPR) and sector-specific compliance frameworks, which restrict access to sensitive transaction data critical for training machine learning (ML) models. Synthetic data generation, powered by advances in generative artificial intelligence (AI), has emerged as a technically promising solution that balances analytical utility with formal privacy guarantees. This review surveys the landscape of generative models—including generative adversarial networks (GANs), variational autoencoders (VAEs), and diffusion models—applied to financial data synthesis encompassing tabular transaction records, time series price data, and sequential event streams. The integration of differential privacy (DP) mechanisms, federated learning (FL) compatibility, and downstream evaluation methodologies is examined in depth. Applications spanning fraud detection, credit risk modeling, anti-money laundering compliance, algorithmic trading simulation, and regulatory stress testing are reviewed against a backdrop of evolving privacy-preserving standards. Critical gaps in temporal fidelity, fairness-aware synthesis, and model interpretability are identified, and high-priority future research directions are charted. This synthesis demonstrates that no single generative paradigm dominates across all financial use cases, and that robust evaluation frameworks combining statistical fidelity with task-specific utility remain an open research priority of considerable practical urgency.

## 77. TAEGAN: Generating Synthetic Tabular Data For Data Augmentation

- Authors: Jiayu Li; Zilong Zhao; Kevin Yee; Uzair Javaid; Biplab Sikdar
- Year: 2024
- DOI: 10.48550/arxiv.2410.01933
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2410.01933
- PDF: https://arxiv.org/pdf/2410.01933

Synthetic tabular data generation has gained significant attention for its potential in data augmentation and privacy-preserving data sharing. While recent methods like diffusion and auto-regressive models (i.e., transformer) have advanced the field, generative adversarial networks (GANs) remain highly competitive due to their training efficiency and strong data generation capabilities. In this paper, we introduce Tabular Auto-Encoder Generative Adversarial Network (TAEGAN), a novel GAN-based framework that leverages a masked auto-encoder as the generator. TAEGAN is the first to incorporate self-supervised warmup training of generator into tabular GANs. It enhances GAN stability and exposes the generator to richer information beyond the discriminator's feedback. Additionally, we propose a novel sampling method tailored for imbalanced or skewed data and an improved loss function to better capture data distribution and correlations. We evaluate TAEGAN against seven state-of-the-art synthetic tabular data generation algorithms. Results from eight datasets show that TAEGAN outperforms all baselines on five datasets, achieving a 27% overall utility boost over the best-performing baseline while maintaining a model size less than 5% of the best-performing baseline model. Code is available at: https://github.com/BetterdataLabs/taegan.

## 78. MALLM-GAN: Multi-Agent Large Language Model as Generative Adversarial Network for Synthesizing Tabular Data

- Authors: Yaobin Ling; Xiaoqian Jiang; Yejin Kim
- Year: 2024
- DOI: 10.48550/arxiv.2406.10521
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2406.10521
- PDF: https://arxiv.org/pdf/2406.10521

In the era of big data, access to abundant data is crucial for driving research forward. However, such data is often inaccessible due to privacy concerns or high costs, particularly in healthcare domain. Generating synthetic (tabular) data can address this, but existing models typically require substantial amounts of data to train effectively, contradicting our objective to solve data scarcity. To address this challenge, we propose a novel framework to generate synthetic tabular data, powered by large language models (LLMs) that emulates the architecture of a Generative Adversarial Network (GAN). By incorporating data generation process as contextual information and utilizing LLM as the optimizer, our approach significantly enhance the quality of synthetic data generation in common scenarios with small sample sizes. Our experimental results on public and private datasets demonstrate that our model outperforms several state-of-art models regarding generating higher quality synthetic data for downstream tasks while keeping privacy of the real data.

## 79. A Model Training Method for DDoS Detection Using CTGAN under 5GC Traffic

- Authors: Yea-Sul Kim; Ye-Eun Kim; Hwankuk Kim
- Year: 2023
- DOI: 10.32604/csse.2023.039550
- Venue: Computer Systems Science and Engineering
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.32604/csse.2023.039550
- PDF: https://file.techscience.com/files/csse/2023/TSP_CSSE-47-1/TSP_CSSE_39550/TSP_CSSE_39550.pdf

With the commercialization of 5th-generation mobile communications (5G) networks, a large-scale internet of things (IoT) environment is being built. Security is becoming increasingly crucial in 5G network environments due to the growing risk of various distributed denial of service (DDoS) attacks across vast IoT devices. Recently, research on automated intrusion detection using machine learning (ML) for 5G environments has been actively conducted. However, 5G traffic has insufficient data due to privacy protection problems and imbalance problems with significantly fewer attack data. If this data is used to train an ML model, it will likely suffer from generalization errors due to not training enough different features on the attack data. Therefore, this paper aims to study a training method to mitigate the generalization error problem of the ML model that classifies IoT DDoS attacks even under conditions of insufficient and imbalanced 5G traffic. We built a 5G testbed to construct a 5G dataset for training to solve the problem of insufficient data. To solve the imbalance problem, synthetic minority oversampling technique (SMOTE) and generative adversarial network (GAN)-based conditional tabular GAN (CTGAN) of data augmentation were used. The performance of the trained ML models was compared and meaningfully analyzed regarding the generalization error problem. The experimental results showed that CTGAN decreased the accuracy and f1-score compared to the Baseline. Still, regarding the generalization error, the difference between the validation and test results was reduced by at least 1.7 and up to 22.88 times, indicating an improvement in the problem. This result suggests that the ML model training method that utilizes CTGANs to augment attack data for training data in the 5G environment mitigates the generalization error problem.

## 80. Synthetic Data Generation for Emergency Medical Systems: A Systematic Comparison of Tabular GAN Extensions

- Authors: Md Kabir; Md Nayem; Sven Tomforde
- Year: 2025
- DOI: 10.5220/0013307200003890
- Venue: Proceedings of the 17th International Conference on Agents and Artificial Intelligence
- Countries: 
- Source: crossref
- URL: https://doi.org/10.5220/0013307200003890

## 81. Synthetic Data Generation for Enhanced Model Efficiency: A GAN- Based Approach to Tabular Data

- Authors: Sunil Sangve; Kriya Oswal; Tejas Sarade; Omkar Tongare; Nilay Sangode; Qusai Shergardwala
- Year: 2025
- DOI: 10.1109/icctdc64446.2025.11157963
- Venue: 2025 International Conference on Computing Technologies &amp;amp; Data Communication (ICCTDC)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/icctdc64446.2025.11157963

## 82. A Comparative Study of GAN-Based Methods for Tabular Synthetic Data Generation

- Authors: Sony Hermawan; Chastine Fatichah; Imam Mustafa Kamal
- Year: 2025
- DOI: 10.1109/icts67612.2025.11369547
- Venue: 2025 15th International Conference on Information &amp;amp; Communication Technology and System (ICTS)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/icts67612.2025.11369547

## 83. Trust-Aware Benchmarking of GAN, VAE, and Diffusion Models for Synthetic Data in Image and Tabular Domains

- Authors: Anil Kumar Shukla
- Year: 2025
- DOI: 10.21203/rs.3.rs-7649434/v1
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.21203/rs.3.rs-7649434/v1

<title>Abstract</title>
                <p>Synthetic data generation using generative AI models offers a promising solution to challenges in data availability, privacy, and fairness. However, comparative insights across model families and data modalities remain limited, especially when trust-related dimensions such as fairness, privacy, and efficiency are considered alongside fidelity.This paper presents a trust-aware benchmarking study across both visual (CIFAR-10, MNIST) and tabular (Adult Income) domains, evaluating representative baselines—vanilla GAN/WGAN-GP, standard and β-VAE, DDPM and classifier-guided DDPM, and hybrids such as VAE-GAN and Latent Diffusion. Advanced models including StyleGAN2/3, BigGAN, CTGAN, Diffusion Transformers, and GigaGAN are acknowledged to situate the findings within the evolving landscape of foundation-scale generators.Performance is assessed using a multi-objective framework that integrates fidelity (FID, precision/recall), fairness (demographic parity), privacy leakage resistance, and computational efficiency. Results show that hybrid latent diffusion models achieve near-diffusion fidelity (FID 10.2 vs. 8.5 on CIFAR-10; 7.8 vs. 6.2 on MNIST) while reducing sampling time by over 70%. On tabular data, hybrids balance accuracy (84.7%) and fairness (0.93), whereas classical GANs and VAEs exhibit trade-offs between fidelity, efficiency, and fairness.To the best of our knowledge, this is the first study to benchmark GANs, VAEs, diffusion, and hybrid models across both image and tabular data using a unified, trust-aware evaluation framework. By providing reproducible, cross-domain comparisons, this work offers practical guidance for selecting and deploying generative models in trust-sensitive applications such as healthcare, finance, and autonomy.</p>

## 84. OOG- Optuna Optimized GAN Sampling Technique for Tabular Imbalanced Malware Data

- Authors: S. M Towhidul Islam Tonmoy; S. M Mehedi Zaman
- Year: 2022
- DOI: 10.1109/bigdata55660.2022.10020393
- Venue: 2022 IEEE International Conference on Big Data (Big Data)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/bigdata55660.2022.10020393

## 85. PrivTab-GAN: A privacy-preserving generative adversarial network for synthetic tabular agricultural data

- Authors: L. Nithya; L. Latha
- Year: 2025
- DOI: 10.1063/5.0301330
- Venue: AIP Advances
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1063/5.0301330
- PDF: https://pubs.aip.org/aip/adv/article-pdf/doi/10.1063/5.0301330/20828308/125114_1_5.0301330.pdf

<jats:p>The increasing demand for data-driven agricultural decision making is hindered by challenges such as data shortages, privacy difficulties, and the need for robust generalization across diverse farming situations. This paper introduces PrivTab-GAN, a privacy-preserving generative adversarial network developed for generating synthetic tabular agricultural data. Evaluation on three practical datasets, Crop Recommendation, Weather Prediction, and Water Irrigation, indicates that PrivTab-GAN surpasses prior models (conditional tabular-GAN, information-theoretic GAN, conditional tabular-GAN, and conditional Wasserstein-GAN), achieving K–S test values that are 6%–12% lower and Jaccard index scores that are 8%–15% higher. The proposed framework, which utilizes a domain-adversarial neural network, demonstrates remarkable generalization performance, attaining 94%–97% accuracy with a maximum reduction of 7.5% even under rigorous privacy constraints (ε = 0.5, σ = 2.0) across two evaluation perspectives (original-to-synthetic and synthetic-to-original training/testing). Moreover, PrivTab-GAN maintains 97.4% of the original data usefulness; however, trade-offs arise with heightened gradient clipping (C = 1.5), leading to a performance decline of up to 18%. These findings validate PrivTab-GAN as a scalable, privacy-preserving methodology for synthetic data-driven agricultural AI, enabling applications including crop planning, irrigation optimization, and climate-adaptive farming.</jats:p>

## 86. GDEGAN: Graphical Discriminative Embedding GAN for tabular data

- Authors: Dinh Anh Dung; Huynh Thi Thanh Binh
- Year: 2022
- DOI: 10.1109/dsaa54385.2022.10032445
- Venue: 2022 IEEE 9th International Conference on Data Science and Advanced Analytics (DSAA)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/dsaa54385.2022.10032445

## 87. CTAB-GAN+: enhancing tabular data synthesis

- Authors: Zilong Zhao; Aditya Kunar; Robert Birke; Hiek Van der Scheer; Lydia Y. Chen
- Year: 2024
- DOI: 10.3389/fdata.2023.1296508
- Venue: Frontiers in Big Data
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3389/fdata.2023.1296508

<jats:p>The usage of synthetic data is gaining momentum in part due to the unavailability of original data due to privacy and legal considerations and in part due to its utility as an augmentation to the authentic data. Generative adversarial networks (GANs), a paragon of generative models, initially for images and subsequently for tabular data, has contributed many of the state-of-the-art synthesizers. As GANs improve, the synthesized data increasingly resemble the real data risking to leak privacy. Differential privacy (DP) provides theoretical guarantees on privacy loss but degrades data utility. Striking the best trade-off remains yet a challenging research question. In this study, we propose CTAB-GAN+ a novel conditional tabular GAN. CTAB-GAN+ improves upon state-of-the-art by (i) adding downstream losses to conditional GAN for higher utility synthetic data in both classification and regression domains; (ii) using Wasserstein loss with gradient penalty for better training convergence; (iii) introducing novel encoders targeting mixed continuous-categorical variables and variables with unbalanced or skewed data; and (iv) training with DP stochastic gradient descent to impose strict privacy guarantees. We extensively evaluate CTAB-GAN+ on statistical similarity and machine learning utility against state-of-the-art tabular GANs. The results show that CTAB-GAN+ synthesizes privacy-preserving data with at least 21.9% higher machine learning utility (i.e., F1-Score) across multiple datasets and learning tasks under given privacy budget.</jats:p>

## 88. Soft Hierarchical Diffusion for Conditional Tabular Data Generation: Application to Travel Survey Entries

- Authors: Peisen Li; Tianming Liu; Yafeng Yin
- Year: 2026
- DOI: 10.2139/ssrn.6795000
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.2139/ssrn.6795000

<jats:p>Travel survey records are essential for travel demand modeling and transportation planning, but their collection is increasingly constrained by cost, declining response rates, and privacy concerns. These challenges motivate methods that can synthesize realistic data conditional on observed traveler characteristics. While deep generative approaches such as GANs and VAEs have demonstrated promising results, they also face limitations in training difficulty and quality. In this paper, we propose a conditional tabular generative framework --- the discrete denoising diffusion model with a soft conditioned cascade chain transformer (D3PM-SC3T) for conditional data generation. The proposed framework uses discrete diffusion as the generative backbone for mixed-type tabular variables to enable realistic diffusion-based generation. Furthermore, it introduces a soft hierarchical conditioning structure to incorporate prior knowledge from travel demand modeling to guide generation through meaningful dependencies while preserving flexibility through learnable soft connections. Experiments on a real-world household travel survey dataset show that D3PM-SC3T effectively learns conditional travel patterns, improves the joint distributional fidelity of dependent entry attributes, and maintains competitive performance in individual-variable generation and logical validity. Sensitivity analyses further suggest that the framework remains robust under limited training data, highlighting its potential for travel survey augmentation and synthesis in data-scarce settings. By enabling realistic conditional synthesis of travel diary entries from limited survey data, this work offers a practical path toward richer behavioral datasets for transportation planning, policy analysis, and demand modeling.</jats:p>

## 89. CTGAN-ENN: A tabular GAN-based Hybrid Sampling Method for Imbalanced and Overlapped Data in Customer Churn Prediction

- Authors: I Nyoman Mahayasa Adiputra; Paweena Wanchai
- Year: 2023
- DOI: 10.21203/rs.3.rs-3644024/v1
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.21203/rs.3.rs-3644024/v1

<title>Abstract</title>
        <p>Class imbalance is one of many problems of customer churn datasets. One of the common problems is class overlap, where the data have a similar instance between classes. The prediction task of customer churn becomes more challenging when there is class overlap in the data training. In this research, we suggested a hybrid method based on tabular GANs, called CTGAN-ENN, to address class overlap and imbalanced data in datasets of customers that churn. We used five different customer churn datasets from an open platform. CTGAN is a tabular GAN-based oversampling to address class imbalance but has a class overlap problem. We combined CTGAN with the ENN under-sampling technique to overcome the class overlap. CTGAN-ENN reduced the number of class overlaps by each feature in all datasets. We investigated how effective CTGAN-ENN is in each machine learning technique. Based on our experiments, CTGAN-ENN achieved satisfactory results in KNN, GBM, and XGB machine learning performance for customer churn predictions. We compared CTGAN-ENN with common over-sampling and hybrid sampling methods, and CTGAN-ENN achieved outperform results compared with other sampling methods. We provide a time consumption algorithm between CTGAN and CTGAN-ENN. CTGAN-ENN achieved less time consumption than CTGAN. Our research work provides a new framework to handle customer churn prediction problems with several types of imbalanced datasets and can be useful in real-world data from customer churn prediction.</p>

## 90. Bi-Discriminator Gan for Tabular Data Synthesis

- Authors: MOHAMMAD ESMAEILPOUR; Nourhene Chaalia; Adel Abusitta; François-Xavier Devailly; Wissem Maazoun; Patrick Cardinal
- Year: 2021
- DOI: 10.2139/ssrn.3985434
- Venue: SSRN Electronic Journal
- Countries: 
- Source: crossref
- URL: https://doi.org/10.2139/ssrn.3985434

## 91. A Comparative Analysis of GAN and VAE based Synthetic Data Generators for High Dimensional, Imbalanced Tabular data

- Authors: A Kiran; S Saravana Kumar
- Year: 2023
- DOI: 10.1109/inocon57975.2023.10101315
- Venue: 2023 2nd International Conference for Innovation in Technology (INOCON)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/inocon57975.2023.10101315

## 92. Exploring Innovative Approaches to Synthetic Tabular Data Generation

- Authors: Eugenia Papadaki; Aristidis G. Vrahatis; Sotiris Kotsiantis
- Year: 2024
- DOI: 10.3390/electronics13101965
- Venue: Electronics
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3390/electronics13101965

<jats:p>The rapid advancement of data generation techniques has spurred innovation across multiple domains. This comprehensive review delves into the realm of data generation methodologies, with a keen focus on statistical and machine learning-based approaches. Notably, novel strategies like the divide-and-conquer (DC) approach and cutting-edge models such as GANBLR have emerged to tackle a spectrum of challenges, spanning from preserving intricate data relationships to enhancing interpretability. Furthermore, the integration of generative adversarial networks (GANs) has sparked a revolution in data generation across sectors like healthcare, cybersecurity, and retail. This review meticulously examines how these techniques mitigate issues such as class imbalance, data scarcity, and privacy concerns. Through a meticulous analysis of evaluation metrics and diverse applications, it underscores the efficacy and potential of synthetic data in refining predictive models and decision-making software. Concluding with insights into prospective research trajectories and the evolving role of synthetic data in propelling machine learning and data-driven solutions across disciplines, this work provides a holistic understanding of the transformative power of contemporary data generation methodologies.</jats:p>

## 93. Conditional Wasserstein GAN-based oversampling of tabular data for imbalanced learning

- Authors: Justin Engelmann; Stefan Lessmann
- Year: 2021
- DOI: 10.1016/j.eswa.2021.114582
- Venue: Expert Systems with Applications
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1016/j.eswa.2021.114582

## 94. Mitigating Class Imbalance in Tabular Data through Neural Network-based Synthetic Data Generation: A Comprehensive Survey and Library

- Authors: Omar A. Mures; Javier Taibo; Emilio J Padrón; Jose A Iglesias-Guitian
- Year: 2025
- DOI: 10.36227/techrxiv.175607141.19092617/v1
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.36227/techrxiv.175607141.19092617/v1

<jats:p>
                  Imbalanced datasets often bias downstream models towards favoring majority classes, posing a critical challenge in deep learning, where extensive data is pivotal for optimal performance. Traditional solutions, such as classical data augmentation, often struggle with nuanced data traits and lack adaptability. The emergence of deep learning techniques like Auto Encoders (AEs), Generative Adversarial Networks (GANs), Diffusion Models (DMs), and Large Language Models (LLMs) opens promising avenues for addressing class imbalance through synthetic data generation. This paper presents a comprehensive survey of generative AI techniques for mitigating class imbalance in tabular datasets. These methods have the potential to improve the performance and efficiency of data-driven models across multiple domains. We evaluate their effectiveness in applications like handball play classification, income level prediction, and used car evaluation. We not only assess their efficacy in these real-world applications but also introduce computational efficiency tests, an often-overlooked aspect in this field. In addition to the survey, we present 'GenTab,' a synthetic tabular data generation library to facilitate the implementation and evaluation of the discussed approaches. GenTab is accessible on
                  <jats:ext-link xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="https://github.com/omaralvarez/gentab">GitHub</jats:ext-link>
                  and offers a user-friendly framework for practitioners to leverage cutting-edge generative models for synthetic tabular dataset creation or augmentation.
                </jats:p>

## 95. Synthetic Electricity Consumption Data Generation Using Tabular Generative Adversarial Networks

- Authors: Thet Paing Tun; Ioana Pisica
- Year: 2023
- DOI: 10.1109/upec57427.2023.10294666
- Venue: 2023 58th International Universities Power Engineering Conference (UPEC)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/upec57427.2023.10294666

## 96. Synthetic Data Augmentation for Imbalanced Tabular Data: A Comparative Study of Generation Methods

- Authors: Dong-Hyun Won; Kwang-Seong Shin; Sungkwan Youm
- Year: 2026
- DOI: 10.3390/electronics15040883
- Venue: Electronics
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3390/electronics15040883

<jats:p>Class imbalance in tabular datasets poses a challenge for machine learning classification tasks, often leading to biased models that underperform in predicting minority class instances. This study presents a comparative analysis of synthetic data generation methods for addressing class imbalance in tabular data. We evaluate four augmentation approaches—Synthetic Minority Over-sampling Technique (SMOTE), Gaussian Copula, Tabular Variational Autoencoder (TVAE), and Conditional Tabular Generative Adversarial Network (CTGAN)—using the University of California Irvine (UCI) Bank Marketing dataset, which exhibits a class imbalance ratio of approximately 7.88:1. Our experimental framework assesses each method across three dimensions: statistical fidelity to the original data distribution evaluated through four complementary metrics (marginal numerical similarity, categorical distribution similarity, correlation structure preservation, and Kolmogorov–Smirnov test), machine learning utility measured through classification performance, and minority class detection capability. Results indicate that all augmentation methods achieved statistically significant improvements over the baseline (p&lt;0.05). SMOTE achieved the highest recall (54.2%, a 117.6% relative improvement over the baseline) and F1-Score (0.437, +22.4% over the baseline) for minority class detection, while Gaussian Copula provided the highest composite fidelity score (0.930) with competitive predictive performance. A weak negative correlation (ρ=−0.30) between composite fidelity and classification performance was observed, suggesting that higher statistical fidelity does not necessarily translate to better downstream task performance. Deep learning-based methods (TVAE, CTGAN) showed statistically significant improvements over the baseline (recall: +58% to +63%) but underperformed compared to simpler methods under default configurations, suggesting the need for larger training samples or more extensive hyperparameter tuning. These findings offer reference points for practitioners working with moderately imbalanced tabular data with limited minority class samples, supporting the selection of generation strategies based on specific requirements regarding data fidelity and classification objectives.</jats:p>

## 97. CTGAN-ENN: a tabular GAN-based hybrid sampling method for imbalanced and overlapped data in customer churn prediction

- Authors: I Nyoman Mahayasa Adiputra; Paweena Wanchai
- Year: 2024
- DOI: 10.1186/s40537-024-00982-x
- Venue: Journal of Big Data
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1186/s40537-024-00982-x
- PDF: https://link.springer.com/content/pdf/10.1186/s40537-024-00982-x.pdf

## 98. Multi-objective evolutionary GAN for tabular data synthesis

- Authors: Nian Ran; Bahrul Nasution; Claire Little; Richard Allmendinger; Mark Elliot
- Year: 2024
- DOI: 10.1145/3638529.3654052
- Venue: Proceedings of the Genetic and Evolutionary Computation Conference
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1145/3638529.3654052

## 99. Oversampling method based on GAN for tabular binary classification problems

- Authors: Jie Yang; Zhenhao Jiang; Tingting Pan; Yueqi Chen; Witold Pedrycz
- Year: 2023
- DOI: 10.3233/ida-220383
- Venue: Intelligent Data Analysis
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3233/ida-220383

<jats:p>Data-imbalanced problems are present in many applications. A big gap in the number of samples in different classes induces classifiers to skew to the majority class and thus diminish the performance of learning and quality of obtained results. Most data level imbalanced learning approaches generate new samples only using the information associated with the minority samples through linearly generating or data distribution fitting. Different from these algorithms, we propose a novel oversampling method based on generative adversarial networks (GANs), named OS-GAN. In this method, GAN is assigned to learn the distribution characteristics of the minority class from some selected majority samples but not random noise. As a result, samples released by the trained generator carry information of both majority and minority classes. Furthermore, the central regularization makes the distribution of all synthetic samples not restricted to the domain of the minority class, which can improve the generalization of learning models or algorithms. Experimental results reported on 14 datasets and one high-dimensional dataset show that OS-GAN outperforms 14 commonly used resampling techniques in terms of G-mean, accuracy and F1-score.</jats:p>

## 100. Beyond Noise: Incorporating Pre-Trained Contractive Autoencoders for Enhanced GAN-based Tabular Data Creation

- Authors: Hesam Fallahian; Mohsen Dorodchi; Kyle Kreth
- Year: 2024
- DOI: 10.1109/icict62343.2024.00026
- Venue: 2024 7th International Conference on Information and Computer Technologies (ICICT)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/icict62343.2024.00026

## 101. Exploring Use of Data Topology in Improving Gan-Generated Tabular Synthetic Data

- Authors: Gopendu Sen; Nailya Sultanova; Jamila Mustafina; Paridah Daud
- Year: 2025
- DOI: 10.1007/978-981-96-7749-8_11
- Venue: Lecture Notes on Data Engineering and Communications Technologies
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1007/978-981-96-7749-8_11

## 102. Bi-discriminator GAN for tabular data synthesis

- Authors: Mohammad Esmaeilpour; Nourhene Chaalia; Adel Abusitta; Franşois-Xavier Devailly; Wissem Maazoun; Patrick Cardinal
- Year: 2022
- DOI: 10.1016/j.patrec.2022.05.023
- Venue: Pattern Recognition Letters
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1016/j.patrec.2022.05.023

## 103. Interpretable tabular data generation

- Authors: Yishuo Zhang; Nayyar Zaidi; Jiahui Zhou; Gang Li
- Year: 2023
- DOI: 10.1007/s10115-023-01834-5
- Venue: Knowledge and Information Systems
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1007/s10115-023-01834-5
- PDF: https://link.springer.com/content/pdf/10.1007/s10115-023-01834-5.pdf

<jats:title>Abstract</jats:title><jats:p>Generative adversarial network () models have been successfully utilized in a wide range of machine learning applications, and tabular data generation domain is not an exception. Notably, some state-of-the-art models of tabular data generation, such as ,  , , etc. are based on  models. Even though these models have resulted in superior performance in generating artificial data when trained on a range of datasets, there is a lot of room (and desire) for improvement. Not to mention that existing methods do have some weaknesses other than performance. For example, the current methods focus only on the performance of the model, and limited emphasis is given on the interpretation of the model. Secondly, the current models operate on raw features only, and hence they fail to exploit any prior knowledge on explicit feature interactions that can be utilized during data generation process. To alleviate the two above-mentioned limitations, in this work, we propose a novel tabular data generation model—<jats:bold><jats:italic>G</jats:italic></jats:bold><jats:italic>enerative</jats:italic><jats:bold><jats:italic>A</jats:italic></jats:bold><jats:italic>dversarial Network modelling inspired from</jats:italic><jats:bold><jats:italic>N</jats:italic></jats:bold><jats:italic>aive</jats:italic><jats:bold><jats:italic>B</jats:italic></jats:bold><jats:italic>ayes and</jats:italic><jats:bold><jats:italic>L</jats:italic></jats:bold><jats:italic>ogistic</jats:italic><jats:bold><jats:italic>R</jats:italic></jats:bold><jats:italic>egression’s relationship</jats:italic> (<jats:inline-formula><jats:alternatives><jats:tex-math>$${ { \texttt {GANBLR} } }$$</jats:tex-math><mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML">
                  <mml:mi>GANBLR</mml:mi>
                </mml:math></jats:alternatives></jats:inline-formula>), which not only address the interpretation limitation of existing tabular -based models but provides capability to handle explicit feature interactions as well. Through extensive evaluations on wide range of datasets, we demonstrate <jats:inline-formula><jats:alternatives><jats:tex-math>$${ { \texttt {GANBLR} } }$$</jats:tex-math><mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML">
                  <mml:mi>GANBLR</mml:mi>
                </mml:math></jats:alternatives></jats:inline-formula>’s superior performance as well as better interpretable capability (explanation of feature importance in the synthetic generation process) as compared to existing state-of-the-art tabular data generation models.</jats:p>

## 104. Diffusion Models for Tabular Data Imputation and Synthetic Data Generation

- Authors: Mario Villaizán-Vallelado; Matteo Salvatori; Carlos Segura; Ioannis Arapakis
- Year: 2025
- DOI: 10.1145/3742435
- Venue: ACM Transactions on Knowledge Discovery from Data
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1145/3742435

<jats:p>Data imputation and data generation have important applications across many domains where incomplete or missing data can hinder accurate analysis and decision-making. Diffusion models have emerged as powerful generative models capable of capturing complex data distributions across various data modalities such as image, audio, and time series. Recently, they have been also adapted to generate tabular data. In this article, we propose a diffusion model for tabular data that introduces three key enhancements: (1) a conditioning attention mechanism, (2) an encoder–decoder transformer as the denoising network, and (3) dynamic masking. The conditioning attention mechanism is designed to improve the model’s ability to capture the relationship between the condition and synthetic data. The transformer layers help model interactions within the condition (encoder) or synthetic data (decoder), while dynamic masking enables our model to efficiently handle both missing data imputation and synthetic data generation tasks within a unified framework. We conduct a comprehensive evaluation by comparing the performance of diffusion models with transformer conditioning against state-of-the-art techniques such as Variational Autoencoders, Generative Adversarial Networks, and Diffusion Models, on benchmark datasets. Our evaluation focuses on the assessment of the generated samples with respect to three important criteria, namely: (1) machine learning efficiency, (2) statistical similarity, and (3) privacy risk mitigation. For the task of data imputation, we consider the efficiency of the generated samples across different levels of missing features. The results demonstrate average superior machine learning efficiency and statistical accuracy compared to the baselines, while maintaining privacy risks at a comparable level, particularly showing increased performance in datasets with a large number of features. By conditioning the data generation on a desired target variable, the model can mitigate systemic biases, generate augmented datasets to address data imbalance issues, and improve data quality for subsequent analysis. This has significant implications for domains such as healthcare and finance, where accurate, unbiased, and privacy-preserving data are critical for informed decision-making and fair model outcomes.</jats:p>

## 105. Conditional Wasserstein GAN with Gradient Penalty for Tabular Data Oversampling

- Authors: Ketut Arda Putra Mahotama Sadha; Chastine Fatichah; Imam Mustafa Kamal
- Year: 2025
- DOI: 10.1109/icts67612.2025.11369545
- Venue: 2025 15th International Conference on Information &amp;amp; Communication Technology and System (ICTS)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/icts67612.2025.11369545

## 106. Benchmarking Generative Adversarial Networks for Realistic Tabular Data Generation

- Authors: J.Shanthini; V.Priya; L.R.Sujithra; P.Sarvesh; C.S.Madhumathi
- Year: 2025
- DOI: 10.1109/icrteect67512.2025.11448644
- Venue: 2025 2nd International Conference on Recent Trends in Electrical, Electronics and Computing Technologies (ICRTEECT)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/icrteect67512.2025.11448644

## 107. Tabular GAN-Based Oversampling of Imbalanced Time-to-Event Data for Survival Prediction

- Authors: Huaning Tan; Renxing Chen; Meng Qin; Lining Tang; Zhibing Wu; Qianlin Luo; Yujuan Quan
- Year: 2023
- DOI: 10.1109/icccbda56900.2023.10154883
- Venue: 2023 8th International Conference on Cloud Computing and Big Data Analytics (ICCCBDA)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/icccbda56900.2023.10154883

## 108. ETGAN: A Hybrid GAN Ensemble for Synthesizing Time-Dependent and Static Tabular Data

- Authors: Harshitha Parsi; Varun Bhargava; Kaushik Das; Milind Jadhav
- Year: 2024
- DOI: 10.1109/ic-etite58242.2024.10493613
- Venue: 2024 Second International Conference on Emerging Trends in Information Technology and Engineering (ICETITE)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/ic-etite58242.2024.10493613

## 109. Distributed GAN with Swift Learning Mechanism for Scalable Multi-Party Tabular Data Synthesis

- Authors: Imam Mustafa Kamal; Chastine Fatichah
- Year: 2024
- DOI: 10.1109/itis64716.2024.10845341
- Venue: 2024 IEEE 10th Information Technology International Seminar (ITIS)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/itis64716.2024.10845341

## 110. Synthetic Tabular Data Generation Under Horizontal Federated Learning Environments in Acute Myeloid Leukemia: Case-Based Simulation Study (Preprint)

- Authors: Imanol Isasa; Mikel Catalina; Gorka Epelde; Naiara Aginako; Andoni Beristain
- Year: 2025
- DOI: 10.2196/preprints.74116
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.2196/preprints.74116

<sec>
                    <title>BACKGROUND</title>
                        <p>Data scarcity and dispersion pose significant obstacles in biomedical research, particularly when addressing rare diseases. In such scenarios, synthetic data generation (SDG) has emerged as a promising path to mitigate the first issue. Concurrently, federated learning is a machine learning paradigm where multiple nodes collaborate to create a centralized model with knowledge that is distilled from the data in different nodes, but without the need for sharing it. This research explores the combination of SDG and federated learning technologies in the context of acute myeloid leukemia, a rare hematological disorder, evaluating their combined impact and the quality of the generated artificial datasets.</p>
                </sec>
                                <sec>
                    <title>OBJECTIVE</title>
                        <p>This study aims to evaluate the privacy- and fidelity-related impact of horizontally federating SDG models in different data distribution scenarios and with different numbers of nodes, comparing them with centralized baseline SDG models.</p>
                </sec>
                                <sec>
                    <title>METHODS</title>
                        <p>Two state-of-the-art generative models, conditional tabular generative adversarial network and FedTabDiff, were trained considering four different scenarios: (1) a nonfederated baseline with all the data available, (2) a federated scenario where the data were evenly distributed among different nodes, (3) a federated scenario where the data were unevenly and randomly distributed (imbalanced data), and (4) a federated scenario with nonindependent and identically distributed data distributions. For each of the federated scenarios, a fixed set of node quantities (3, 5, 7, 10) was considered to assess its impact, and the generated data were evaluated, attending to a fidelity-privacy trade-off.</p>
                </sec>
                                <sec>
                    <title>RESULTS</title>
                        <p>The computed fidelity metrics exhibited statistically significant deteriorations (&lt;i&gt;P&lt;/i&gt;&amp;lt;.001) up to 21% in the conditional tabular generative adversarial network and up to 62% in the FedTabDiff model due to the federation process. When comparing federated experiments trained with diverse numbers of nodes, no strong tendencies were observed, even if specific comparisons resulted in significative differences. Privacy metrics were mainly maintained while obtaining maximum improvements of 55% and maximum deteriorations of 26% between both models, although they were not statistically significant.</p>
                </sec>
                                <sec>
                    <title>CONCLUSIONS</title>
                        <p>Within the scope of the use case scenario in this paper, the act of horizontally federating SDG algorithms results in a loss of data fidelity compared to the nonfederated baseline while maintaining privacy levels. However, this deterioration does not significantly increase as the number of nodes used to train the models grows, even though significative differences were found in specific comparisons. The different data partition distribution configurations had no significant effect on the metrics, as similar tendencies were found for all scenarios.</p>
                </sec>
                                <sec>
                    <title>CLINICALTRIAL</title>
                        <p/>
                </sec>

## 111. A CNN-Based Novel Approach for Classification of Sacral Hiatus with GAN-Powered Tabular Data Set

- Authors: Ferhat Kilic; Murat Korkmaz; Orhan Er; Cemil Altin
- Year: 2023
- DOI: 10.5755/j02.eie.33852
- Venue: Elektronika ir Elektrotechnika
- Countries: 
- Source: crossref
- URL: https://doi.org/10.5755/j02.eie.33852
- PDF: https://eejournal.ktu.lt/index.php/elt/article/download/33852/15857

<jats:p>Caudal epidural anaesthesia is usually the most well-known technique in obstetrics to deal with chronic back pain. Due to variations in the shape and size of the sacral hiatus (SH), its classification is a crucial and challenging task. Clinically, it is required in trauma, where surgeons must make fast and correct selections. Past studies have focused on morphometric and statistical analysis to classify it. Therefore, it is vital to automatically and accurately classify SH types through deep learning methods. To this end, we proposed the Multi-Task Process (MTP), a novel classification approach to classify the SH MTP that initially uses a small medical tabular data set obtained by manual feature extraction on computed tomography scans of the sacrums. Second, it augments the data set synthetically through a Generative Adversarial Network (GAN). In addition, it adapts a two-dimensional (2D) embedding algorithm to convert tabular features into images. Finally, it feeds images into Convolutional Neural Networks (CNNs). The application of MTP to six CNN models achieved remarkable classification success rates of approximately 90 % to 93 %. The proposed MTP approach eliminates the small medical tabular data problem that results in bone classification on deep models.</jats:p>

## 112. MolGAN: An implicit generative model for small molecular graphs

- Authors: Nicola De Cao; Thomas Kipf
- Year: 2018
- DOI: 10.48550/arxiv.1805.11973
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1805.11973
- PDF: https://arxiv.org/pdf/1805.11973

Deep generative models for graph-structured data offer a new angle on the problem of chemical synthesis: by optimizing differentiable models that directly generate molecular graphs, it is possible to side-step expensive search procedures in the discrete and vast space of chemical structures. We introduce MolGAN, an implicit, likelihood-free generative model for small molecular graphs that circumvents the need for expensive graph matching procedures or node ordering heuristics of previous likelihood-based methods. Our method adapts generative adversarial networks (GANs) to operate directly on graph-structured data. We combine our approach with a reinforcement learning objective to encourage the generation of molecules with specific desired chemical properties. In experiments on the QM9 chemical database, we demonstrate that our model is capable of generating close to 100% valid compounds. MolGAN compares favorably both to recent proposals that use string-based (SMILES) representations of molecules and to a likelihood-based method that directly generates graphs, albeit being susceptible to mode collapse. Code at https://github.com/nicola-decao/MolGAN

## 113. Artificial Intelligence and COVID-19: Deep Learning Approaches for Diagnosis and Treatment

- Authors: Mohammad Jamshidi; Ali Lalbakhsh; Jakub Talla; Zdeněk Peroutka; Farimah Hadjilooei; Pedram Lalbakhsh; Morteza Jamshidi; Luigi La Spada; Mirhamed Mirmozafari; Mojgan Dehghani; Asal Sabet; Saeed Roshani; Sobhan Roshani; Nima Bayat-Makou; Bahare Mohamadzade; Zahra Malek; Alireza Jamshidi; Sara Kiani; Hamed Hashemi‐Dezaki; Wahab Mohyuddin
- Year: 2020
- DOI: 10.1109/access.2020.3001973
- Venue: IEEE Access
- Countries: AU; CA; CN; CZ; GB; IR; PK; US
- Source: openalex
- URL: https://doi.org/10.1109/access.2020.3001973
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/8948470/09115663.pdf

COVID-19 outbreak has put the whole world in an unprecedented difficult situation bringing life around the world to a frightening halt and claiming thousands of lives. Due to COVID-19's spread in 212 countries and territories and increasing numbers of infected cases and death tolls mounting to 5,212,172 and 334,915 (as of May 22 2020), it remains a real threat to the public health system. This paper renders a response to combat the virus through Artificial Intelligence (AI). Some Deep Learning (DL) methods have been illustrated to reach this goal, including Generative Adversarial Networks (GANs), Extreme Learning Machine (ELM), and Long/Short Term Memory (LSTM). It delineates an integrated bioinformatics approach in which different aspects of information from a continuum of structured and unstructured data sources are put together to form the user-friendly platforms for physicians and researchers. The main advantage of these AI-based platforms is to accelerate the process of diagnosis and treatment of the COVID-19 disease. The most recent related publications and medical reports were investigated with the purpose of choosing inputs and targets of the network that could facilitate reaching a reliable Artificial Neural Network-based tool for challenges associated with COVID-19. Furthermore, there are some specific inputs for each platform, including various forms of the data, such as clinical data and medical imaging which can improve the performance of the introduced approaches toward the best responses in practical applications.

## 114. Adversarial Ranking for Language Generation

- Authors: Kevin Lin; Dianqi Li; Xiaodong He; Zhengyou Zhang; Ming–Ting Sun
- Year: 2017
- DOI: 10.48550/arxiv.1705.11001
- Venue: arXiv (Cornell University)
- Countries: GB; US
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1705.11001
- PDF: https://arxiv.org/pdf/1705.11001

Generative adversarial networks (GANs) have great successes on synthesizing data. However, the existing GANs restrict the discriminator to be a binary classifier, and thus limit their learning capacity for tasks that need to synthesize output with rich structures such as natural language descriptions. In this paper, we propose a novel generative adversarial network, RankGAN, for generating high-quality language descriptions. Rather than training the discriminator to learn and assign absolute binary predicate for individual data sample, the proposed RankGAN is able to analyze and rank a collection of human-written and machine-written sentences by giving a reference group. By viewing a set of data samples collectively and evaluating their quality through relative ranking scores, the discriminator is able to make better assessment which in turn helps to learn a better generator. The proposed RankGAN is optimized through the policy gradient technique. Experimental results on multiple public datasets clearly demonstrate the effectiveness of the proposed approach.

## 115. Data synthesis using dual discriminator conditional generative adversarial networks for imbalanced fault diagnosis of rolling bearings

- Authors: Taisheng Zheng; Lei Song; Jianxing Wang; Wei Teng; Xiaoli Xu; Chao Ma
- Year: 2020
- DOI: 10.1016/j.measurement.2020.107741
- Venue: Measurement
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1016/j.measurement.2020.107741

## 116. Modeling the Influence of Data Structure on Learning in Neural Networks: The Hidden Manifold Model

- Authors: Sebastian Goldt; Marc Mézard; Florent Krzakala; Lenka Zdeborová
- Year: 2020
- DOI: 10.1103/physrevx.10.041044
- Venue: Physical Review X
- Countries: FR
- Source: openalex
- URL: https://doi.org/10.1103/physrevx.10.041044
- PDF: http://link.aps.org/pdf/10.1103/PhysRevX.10.041044

Understanding the reasons for the success of deep neural networks trained using stochastic gradientbased methods is a key open problem for the nascent theory of deep learning. The types of data where these networks are most successful, such as images or sequences of speech, are characterized by intricate correlations. Yet, most theoretical work on neural networks does not explicitly model training data or assumes that elements of each data sample are drawn independently from some factorized probability distribution. These approaches are, thus, by construction blind to the correlation structure of real-world datasets and their impact on learning in neural networks. Here, we introduce a generative model for structured datasets that we call the hidden manifold model. The idea is to construct high-dimensional inputs that lie on a lower-dimensional manifold, with labels that depend only on their position within this manifold, akin to a single-layer decoder or generator in a generative adversarial network. We demonstrate that learning of the hidden manifold model is amenable to an analytical treatment by proving a "Gaussian equivalence property" (GEP), and we use the GEP to show how the dynamics of two-layer neural networks trained using one-pass stochastic gradient descent is captured by a set of integro-differential equations that track the performance of the network at all times. This approach permits us to analyze in detail how a neural network learns functions of increasing complexity during training, how its performance depends on its size, and how it is impacted by parameters such as the learning rate or the dimension of the hidden manifold.

## 117. Data Generation Using Generative Adversarial Network with Twin Normalization

- Authors: Xiuqing Mao; Lei Sun; Zhiyin Kong; Min Zhao
- Year: 2023
- DOI: 10.21203/rs.3.rs-3644206/v1
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.21203/rs.3.rs-3644206/v1

<title>Abstract</title>
                <p>Traditional generative adversarial networks require a large number of samples during training. When generating high-resolution images, it may suffer to mode collapse, resulting in lower quality outputs. This paper proposes a generative adversarial network data generation method (Twin-Norm-GAN) based on twin normalization, which is expected to relief the problem of mode collapse when generating high-resolution images with few samples. The method first normalizes the gradient of the discriminator, that is, imposes gradient norm constraints, which further prevents the phenomenon of mode collapse; then adds a normalized attention module to the generator and discriminator to suppress less significant weights, a weight sparsity penalty is applied to the attention module, which improves the quality of the generated images. Experiments are conducted using standard datasets such as FFHQ, Panda, and art paintings, and compared with the current state-of-the-art GAN model (FastGAN) for generating high-fidelity images with few samples through qualitative and IS, FID quantitative evaluation methods, the experiments show that compared with the contrast model, this method can generate higher quality images. And the classification experiments prove that the data generated by this method are available for the training of downstream task models.</p>

## 118. Dctgain: Dual Conditional Tabular Generative Adversarial Imputation Network for Missing Data

- Authors: Liu Xin; Dai Sicong; Jian Yu; Ying Qian
- Year: 2024
- DOI: 10.2139/ssrn.4691088
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.2139/ssrn.4691088

## 119. Detracking Autoencoding Conditional Generative Adversarial Network: Improved Generative Adversarial Network Method for Tabular Missing Value Imputation

- Authors: Jingrui Liu; Zixin Duan; Xinkai Hu; Jingxuan Zhong; Yunfei Yin
- Year: 2024
- DOI: 10.3390/e26050402
- Venue: Entropy
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3390/e26050402

<jats:p>Due to various reasons, such as limitations in data collection and interruptions in network transmission, gathered data often contain missing values. Existing state-of-the-art generative adversarial imputation methods face three main issues: limited applicability, neglect of latent categorical information that could reflect relationships among samples, and an inability to balance local and global information. We propose a novel generative adversarial model named DTAE-CGAN that incorporates detracking autoencoding and conditional labels to address these issues. This enhances the network’s ability to learn inter-sample correlations and makes full use of all data information in incomplete datasets, rather than learning random noise. We conducted experiments on six real datasets of varying sizes, comparing our method with four classic imputation baselines. The results demonstrate that our proposed model consistently exhibited superior imputation accuracy.</jats:p>

## 120. Dctgan: Double Conditional Tabular Generative Adversarial Network for Missing Data Imputation

- Authors: Liu Xin; Dai Sicong; Chen Hongyu
- Year: 2023
- DOI: 10.2139/ssrn.4327153
- Venue: SSRN Electronic Journal
- Countries: 
- Source: crossref
- URL: https://doi.org/10.2139/ssrn.4327153

## 121. An Application of Generative Adversarial Network in Natural Language Generation

- Authors: Pradnya Borkar; Reena Thakur; Parul Bhanarkar
- Year: 2023
- DOI: 10.1201/9781003203964-8
- Venue: Generative Adversarial Networks and Deep Learning
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1201/9781003203964-8

## 122. Synthesizing Tabular Data using Generative Adversarial Networks

- Authors: Lei Xu; Kalyan Veeramachaneni
- Year: 2018
- DOI: 10.48550/arxiv.1811.11264
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1811.11264
- PDF: https://arxiv.org/pdf/1811.11264

Generative adversarial networks (GANs) implicitly learn the probability distribution of a dataset and can draw samples from the distribution. This paper presents, Tabular GAN (TGAN), a generative adversarial network which can generate tabular data like medical or educational records. Using the power of deep neural networks, TGAN generates high-quality and fully synthetic tables while simultaneously generating discrete and continuous variables. When we evaluate our model on three datasets, we find that TGAN outperforms conventional statistical generative models in both capturing the correlation between columns and scaling up for large datasets.

## 123. Synthetic tabular data: copulas vs enhanced GANs

- Authors: Vincent Granville
- Year: 2024
- DOI: 10.1016/b978-0-44-321857-6.00014-x
- Venue: Elsevier eBooks
- Countries: 
- Source: openalex
- URL: https://doi.org/10.1016/b978-0-44-321857-6.00014-x

## 124. Evaluating the Utility of GAN Generated Synthetic Tabular Data for Class Balancing and Low Resource Settings

- Authors: Nagarjuna Venkata Chereddy; Bharath Kumar Bolla
- Year: 2023
- DOI: 10.1007/978-3-031-36402-0_4
- Venue: Lecture notes in computer science
- Countries: GB; IN; US
- Source: openalex
- URL: https://doi.org/10.1007/978-3-031-36402-0_4
- PDF: https://arxiv.org/pdf/2306.13929

## 125. CTAB-GAN: Effective Table Data Synthesizing

- Authors: Zilong Zhao; Aditya Kunar; Hiek Van der Scheer; Robert Birke; Lydia Y. Chen
- Year: 2021
- DOI: 10.48550/arxiv.2102.08369
- Venue: arXiv (Cornell University)
- Countries: CH; NL
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2102.08369
- PDF: https://arxiv.org/pdf/2102.08369

While data sharing is crucial for knowledge development, privacy concerns and strict regulation (e.g., European General Data Protection Regulation (GDPR)) unfortunately limit its full effectiveness. Synthetic tabular data emerges as an alternative to enable data sharing while fulfilling regulatory and privacy constraints. The state-of-the-art tabular data synthesizers draw methodologies from generative Adversarial Networks (GAN) and address two main data types in the industry, i.e., continuous and categorical. In this paper, we develop CTAB-GAN, a novel conditional table GAN architecture that can effectively model diverse data types, including a mix of continuous and categorical variables. Moreover, we address data imbalance and long-tail issues, i.e., certain variables have drastic frequency differences across large values. To achieve those aims, we first introduce the information loss and classification loss to the conditional GAN. Secondly, we design a novel conditional vector, which efficiently encodes the mixed data type and skewed distribution of data variable. We extensively evaluate CTAB-GAN with the state of the art GANs that generate synthetic tables, in terms of data similarity and analysis utility. The results on five datasets show that the synthetic data of CTAB-GAN remarkably resembles the real data for all three types of variables and results into higher accuracy for five machine learning algorithms, by up to 17%.

## 126. Synthetic Data as a Proxy for Real-World Electronic Health Records in the Patient Length of Stay Prediction

- Authors: Dominik Bietsch; Robert Stahlbock; Stefan Voß
- Year: 2023
- DOI: 10.3390/su151813690
- Venue: Sustainability
- Countries: DE
- Source: openalex
- URL: https://doi.org/10.3390/su151813690
- PDF: https://www.mdpi.com/2071-1050/15/18/13690/pdf?version=1694615896

While generative artificial intelligence has gained popularity, e.g., for the creation of images, it can also be used for the creation of synthetic tabular data. This bears great potential, especially for the healthcare industry, where data are often scarce and underlie privacy restrictions. For instance, the creation of synthetic electronic health records (EHR) promises to improve the usage of machine learning algorithms, which usually work with large amounts of data. This also applies for the prediction of the patient length of stay (LOS), a key measure for hospitals. Thereby, the LOS represents one of the core tools for decision makers to plan the allocation of resources. Thus, this paper aims to add to the still-young research concerning the application of generative adversarial nets (GAN) on tabular EHR. It does that with the intention to leverage the advantages of synthetic data for the prediction of the LOS in order to contribute to the efficiency-enhancing and cost-saving aspirations of hospitals and insurance companies. Therefore, the applicability of synthetic data that is generated using GANs as a proxy for scarce real-world EHR for the patient LOS multi-class classification task is examined. In this context, the Conditional Tabular GAN (CTGAN) and the Copula GAN are selected as the underlying models as they are state-of-the-art GAN architectures designed for generating synthetic tabular data. The CTGAN is found to be the superior model for the underlying use case. Nevertheless, the paper shows that there is still room for improvement when applying state-of-the-art GAN architectures to clinical healthcare data.

## 127. Enhancing Small Tabular Clinical Trial Dataset through Hybrid Data Augmentation: Combining SMOTE and WCGAN-GP

- Authors: Winston Wang; Tun‐Wen Pai
- Year: 2023
- DOI: 10.3390/data8090135
- Venue: Data
- Countries: TW
- Source: openalex
- URL: https://doi.org/10.3390/data8090135
- PDF: https://www.mdpi.com/2306-5729/8/9/135/pdf?version=1692777717

This study addressed the challenge of training generative adversarial networks (GANs) on small tabular clinical trial datasets for data augmentation, which are known to pose difficulties in training due to limited sample sizes. To overcome this obstacle, a hybrid approach is proposed, combining the synthetic minority oversampling technique (SMOTE) to initially augment the original data to a more substantial size for improving the subsequent GAN training with a Wasserstein conditional generative adversarial network with gradient penalty (WCGAN-GP), proven for its state-of-art performance and enhanced stability. The ultimate objective of this research was to demonstrate that the quality of synthetic tabular data generated by the final WCGAN-GP model maintains the structural integrity and statistical representation of the original small dataset using this hybrid approach. This focus is particularly relevant for clinical trials, where limited data availability due to privacy concerns and restricted accessibility to subject enrollment pose common challenges. Despite the limitation of data, the findings demonstrate that the hybrid approach successfully generates synthetic data that closely preserved the characteristics of the original small dataset. By harnessing the power of this hybrid approach to generate faithful synthetic data, the potential for enhancing data-driven research in drug clinical trials become evident. This includes enabling a robust analysis on small datasets, supplementing the lack of clinical trial data, facilitating its utility in machine learning tasks, even extending to using the model for anomaly detection to ensure better quality control during clinical trial data collection, all while prioritizing data privacy and implementing strict data protection measures.

## 128. Generative Adversarial Networks for Synthetic Data Generation: A Comparative Study

- Authors: Claire Little; Mark Elliot; Richard Allmendinger; Sahel Shariati Samani
- Year: 2021
- DOI: 10.48550/arxiv.2112.01925
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2112.01925
- PDF: https://arxiv.org/pdf/2112.01925

Generative Adversarial Networks (GANs) are gaining increasing attention as a means for synthesising data. So far much of this work has been applied to use cases outside of the data confidentiality domain with a common application being the production of artificial images. Here we consider the potential application of GANs for the purpose of generating synthetic census microdata. We employ a battery of utility metrics and a disclosure risk metric (the Targeted Correct Attribution Probability) to compare the data produced by tabular GANs with those produced using orthodox data synthesis methods.

## 129. Improving GAN with inverse cumulative distribution function for tabular data synthesis

- Authors: Ban Li; Senlin Luo; Xiaonan Qin; Limin Pan
- Year: 2021
- DOI: 10.1016/j.neucom.2021.05.098
- Venue: Neurocomputing
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1016/j.neucom.2021.05.098

## 130. CTAB-GAN+: Enhancing Tabular Data Synthesis

- Authors: Zilong Zhao; Aditya Kunar; Robert Birke; Lydia Y. Chen
- Year: 2022
- DOI: 10.48550/arxiv.2204.00401
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2204.00401
- PDF: https://arxiv.org/pdf/2204.00401

While data sharing is crucial for knowledge development, privacy concerns and strict regulation (e.g., European General Data Protection Regulation (GDPR)) limit its full effectiveness. Synthetic tabular data emerges as alternative to enable data sharing while fulfilling regulatory and privacy constraints. State-of-the-art tabular data synthesizers draw methodologies from Generative Adversarial Networks (GAN). As GANs improve the synthesized data increasingly resemble the real data risking to leak privacy. Differential privacy (DP) provides theoretical guarantees on privacy loss but degrades data utility. Striking the best trade-off remains yet a challenging research question. We propose CTAB-GAN+ a novel conditional tabular GAN. CTAB-GAN+ improves upon state-of-the-art by (i) adding downstream losses to conditional GANs for higher utility synthetic data in both classification and regression domains; (ii) using Wasserstein loss with gradient penalty for better training convergence; (iii) introducing novel encoders targeting mixed continuous-categorical variables and variables with unbalanced or skewed data; and (iv) training with DP stochastic gradient descent to impose strict privacy guarantees. We extensively evaluate CTAB-GAN+ on data similarity and analysis utility against state-of-the-art tabular GANs. The results show that CTAB-GAN+ synthesizes privacy-preserving data with at least 48.16% higher utility across multiple datasets and learning tasks under different privacy budgets.

## 131. Mixed Data Imputation Using Generative Adversarial Networks

- Authors: Wasif Khan; Nazar Zaki; Amir Ahmad; Mohammad Mehedy Masud; Luqman Ali; Nasloon Ali; Luai A. Ahmed
- Year: 2022
- DOI: 10.1109/access.2022.3218067
- Venue: IEEE Access
- Countries: AE
- Source: openalex
- URL: https://doi.org/10.1109/access.2022.3218067
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/6514899/09932604.pdf

Missing values are common in real-world datasets and pose a significant challenge to the performance of statistical and machine learning models. Generally, missing values are imputed using statistical methods, such as the mean, median, mode, or machine learning approaches. These approaches are limited to either numerical or categorical data. Imputation in mixed datasets that contain both numerical and categorical attributes is challenging and has received little attention. Machine learning-based imputation algorithms usually require a large amount of training data. However, obtaining such data is difficult. Furthermore, no considerate work has been conducted in the literature that focuses on the effects of the training and testing size with an increasing amount of missing data. To address this gap, we propose that increasing the amount of training data will improve the imputation performance. We first used generative adversarial network (GAN) methods to increase the amount of training data. We considered two state-of-the-art GANs (tabular and conditional tabular) to add synthetic samples using observed data with different synthetic sample ratios. We then used three state-of-the-art imputation models that can handle mixed data: MissForest, multivariate imputation by chained equations, and denoising auto encoder (DAE). We propose a robust experimental setup on four publicly available datasets with different training-testing data divisions that have increasing missingness ratios. Extensive experimental results show that incorporating synthetic samples with training data achieves better performance compared to the baseline methods for mixed data imputation in both categorical and numerical variables, especially for large missingness ratios.

## 132. DECAF: Generating Fair Synthetic Data Using Causally-Aware Generative Networks

- Authors: Boris van Breugel; Trent Kyono; Jeroen Berrevoets; Mihaela van der Schaar
- Year: 2021
- DOI: 10.48550/arxiv.2110.12884
- Venue: arXiv (Cornell University)
- Countries: GB; US
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2110.12884
- PDF: https://arxiv.org/pdf/2110.12884

Machine learning models have been criticized for reflecting unfair biases in the training data. Instead of solving for this by introducing fair learning algorithms directly, we focus on generating fair synthetic data, such that any downstream learner is fair. Generating fair synthetic data from unfair data - while remaining truthful to the underlying data-generating process (DGP) - is non-trivial. In this paper, we introduce DECAF: a GAN-based fair synthetic data generator for tabular data. With DECAF we embed the DGP explicitly as a structural causal model in the input layers of the generator, allowing each variable to be reconstructed conditioned on its causal parents. This procedure enables inference time debiasing, where biased edges can be strategically removed for satisfying user-defined fairness requirements. The DECAF framework is versatile and compatible with several popular definitions of fairness. In our experiments, we show that DECAF successfully removes undesired bias and - in contrast to existing methods - is capable of generating high-quality synthetic data. Furthermore, we provide theoretical guarantees on the generator's convergence and the fairness of downstream models.

## 133. Permutation-Invariant Tabular Data Synthesis

- Authors: Yujin Zhu; Zilong Zhao; Robert Birke; Lydia Y. Chen
- Year: 2022
- DOI: 10.1109/bigdata55660.2022.10020639
- Venue: 2022 IEEE International Conference on Big Data (Big Data)
- Countries: IT; NL
- Source: openalex
- URL: https://doi.org/10.1109/bigdata55660.2022.10020639
- PDF: https://repository.tudelft.nl/file/File_8382174c-c0d7-4499-a740-1e8d78473eb4

Tabular data synthesis is an emerging approach to circumvent strict regulations on data privacy while discovering knowledge through big data. Although state-of-the-art AI-based tabular data synthesizers, e.g., table-GAN, CTGAN, TVAE, and CTAB-GAN, are effective at generating synthetic tabular data, their training is sensitive to column permutations of input data. In this paper, we first c onduct a n e xtensive e mpirical s tudy to disclose such a property of permutation invariance and an in-depth analysis of the existing synthesizers. We show that changing the input column order worsens the statistical difference between real and synthetic data by up to 38.67% due to the encoding of tabular data and the network architectures. To fully unleash the potential of big synthetic tabular data, we propose two solutions: (i) AE-GAN, a synthesizer that uses an autoencoder network to represent the tabular data and GAN networks to synthesize the latent representation, and (ii) a feature sorting algorithm to find t he s uitable c olumn o rder o f i nput d ata f or CNN-based synthesizers. We evaluate the proposed solutions on five datasets in terms of the sensitivity to the column permutation, the quality of synthetic data, and the utility in downstream analyses. Our results show that we enhance the property of permutation-invariance when training synthesizers and further improve the quality and utility of synthetic data, up to 22%, compared to the existing synthesizers.

## 134. POSTER

- Authors: Pei-Hsuan Lu; Chia-Mu Yu
- Year: 2017
- DOI: 10.1145/3133956.3138823
- Venue: 
- Countries: TW
- Source: openalex
- URL: https://doi.org/10.1145/3133956.3138823

Many differentially private data release solutions have been proposed for different types of data with the sacrifice of inherent correlation structure. Here, we propose a unified framework of releasing differentially private data. In particular, our proposed generative adversarial network (GAN)-based framework learns the input distribution, irrespective of tabular data and graphs, and generates synthetic data in a differentially private manner. Our preliminary results show the acceptable utility of the synthetic dataset.

## 135. PriveTAB

- Authors: Anantaa Kotal; Aritran Piplai; Sai Sree Laya Chukkapalli; Anupam Joshi
- Year: 2022
- DOI: 10.1145/3510548.3519377
- Venue: 
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1145/3510548.3519377
- PDF: https://doi.org/10.13016/m2xuey-qhp9

Machine Learning has increased our ability to model large quantities of data efficiently in a short time. Machine learning approaches in many application domains require collecting large volumes of data from distributed sources and combining them. However, sharing of data from multiple sources leads to concerns about privacy. Privacy regulations like European Union's General Data Protection Regulation (GDPR) have specific requirements on when and how such data can be shared. Even when there are no specific regulations, organizations may have concerns about revealing their data. For example in cybersecurity, organizations are reluctant to share their network-related data to permit machine learning-based intrusion detectors to be built. This has, in particular, hampered academic research. We need an approach to make confidential data widely available for accurate data analysis without violating the privacy of the data subjects. Privacy in shared data has been discussed in prior work focusing on anonymization and encryption of data. An alternate approach to make data available for analysis without sharing sensitive information is by replacing sensitive information with synthetic data that behave as original data for all analytical purposes. Generative Adversarial Networks (GANs) are one of the well-known models to generate synthetic samples that can have the same distributional characteristics as the original data. However, modeling tabular data using GAN is a non-trivial task. Tabular data contain a mix of categorical and continuous variables and require specialized constraints as described in the CTGAN model. In this paper, we propose a framework to generate privacy-preserving synthetic data suitable for release for analytical purposes. The data is generated using the CTGAN approach, and so is analytically similar to the original dataset. To ensure that the generated data meet the privacy requirements, we use the principle of t-closeness. We ensure that the distribution of attributes in the released dataset is within a certain threshold distance from the real dataset. We also encrypt sensitive values in the final released version of the dataset to minimize information leakage. We show that in a variety of cases, models trained on this synthetic data instead of the real data perform nearly as well when tested on the real data. Specifically, we show that the machine learning models used for network event/attack recognition tasks do not have a significant loss in accuracy when trained on data generated from our framework in place of the real dataset.

## 136. GLSTM: A novel approach for prediction of real &amp; synthetic PID diabetes data using GANs and LSTM classification model

- Authors: Sushma Jaiswal; Priyanka Gupta
- Year: 2023
- DOI: 10.52756/ijerr.2023.v30.004
- Venue: International Journal of experimental research and review
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.52756/ijerr.2023.v30.004
- PDF: https://doi.org/10.52756/ijerr.2023.v30.004

Generative Adversarial Network (GAN) is a revolution in modern artificial systems. Deep learning-based Generative adversarial networks generate realistic synthetic tabular data. Synthetic data are used to enhance the size of a relatively small training dataset while ensuring the confidentiality of the original data. In this context, we implemented the GAN framework for generating diabetes data to help the health care professional in more clinical applications. GAN is used to validate the Pima Indian Diabetes (PID) Dataset. Various preprocessing techniques, such as handling missing values, outliers and data imbalance problems, enhance data quality. Some exploratory data analyses, such as heat maps, bar graphs and histograms, are used for data visualisation. We employed hypothesis testing to examine the resemblance between real data and GAN-generated synthetic data. In this study, we proposed a GAN-Long Short-Term Memory (GLSTM) system, in which GAN is used for data augmentation, and LSTM is used for diabetes classification. Additionally, various GAN models such as CTGAN, Vanilla GAN, Coupula GAN, Gaussian Coupula GAN, and TVAE GAN are used to generate the synthetic dataset. Experiments were conducted on real data, synthetic data, and by combining real and synthetic data. The model that used both real and synthetic data obtained a substantially better accuracy of 97% compared to 92% when only real data was used. We also observed that synthetic data could be used in place of real data, as the mean correlation between synthetic and real data is 0.93. Our study's findings outperformed when compared to state-of-the-art methodologies.

## 137. Leveraging synthetic data for AI bias mitigation

- Authors: Ajay M. Patrikar; Arjuna Mahenthiran; Ahmad Yasir Md Said
- Year: 2023
- DOI: 10.1117/12.2662276
- Venue: 
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1117/12.2662276

Widespread adoption of artificial intelligence (AI) in civilian and defense government agencies requires the stakeholders to have trust in AI solutions. One of the five principles of ethical AI, identified by the Department of Defense, emphasizes that AI solutions be equitable. The AI system involves a series of choices from data selection to model definition, each of which is subject to human and algorithmic biases and can lead to unintended consequences. This paper focuses on allowing AI bias mitigation with the use of synthetic data. The proposed technique, named Fair-GAN, builds upon the recently developed Fair-SMOTE approach, which used synthesized data to fix class and other imbalances caused by protected attributes such as race and gender. Fair-GAN uses Generative Adversarial Networks (GAN) instead of the Synthetic Minority Oversampling Technique (SMOTE). While SMOTE can only synthesize tabular and numerical data, GAN can synthesize tabular data with numerical, binary, and categorical variables. GAN can also synthesize other data forms such as images, audio and text. In our experiments, we use the Synthetic Data Vault (SDV), which implements approaches such as conditional tabular GAN (CTGAN) and tabular variational autoencoders (TVAE). We show the applicability of Fair-GAN to several benchmark problems, which are used to evaluate the efficacy of AI bias mitigation algorithms. It is shown that Fair-GAN leads to significant improvements in metrics used for evaluating AI fairness such as the statistical parity difference, disparate impact, average odds difference, and equal opportunities difference.

## 138. Deep learning assisted cancer disease prediction from gene expression data using WT-GAN

- Authors: U Ravindran; C. Gunavathi
- Year: 2024
- DOI: 10.1186/s12911-024-02712-y
- Venue: BMC Medical Informatics and Decision Making
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.1186/s12911-024-02712-y
- PDF: https://link.springer.com/content/pdf/10.1186/s12911-024-02712-y.pdf

Several diverse fields including the healthcare system and drug development sectors have benefited immensely through the adoption of deep learning (DL), which is a subset of artificial intelligence (AI) and machine learning (ML). Cancer makes up a significant percentage of the illnesses that cause early human mortality across the globe, and this situation is likely to rise in the coming years, especially when non-communicable illnesses are not considered. As a result, cancer patients would greatly benefit from precise and timely diagnosis and prediction. Deep learning (DL) has become a common technique in healthcare due to the abundance of computational power. Gene expression datasets are frequently used in major DL-based applications for illness detection, notably in cancer therapy. The quantity of medical data, on the other hand, is often insufficient to fulfill deep learning requirements. Microarray gene expression datasets are used for training procedures despite their extreme dimensionality, limited volume of data samples, and sparsely available information. Data augmentation is commonly used to expand the training sample size for gene data. The Wasserstein Tabular Generative Adversarial Network (WT-GAN) model is used for the data augmentation process for generating synthetic data in this proposed work. The correlation-based feature selection technique selects the most relevant characteristics based on threshold values. Deep FNN and ML algorithms train and classify the gene expression samples. The augmented data give better classification results (> 97%) when using WT-GAN for cancer diagnosis.

## 139. Teacher-Student Compression with Generative Adversarial Networks

- Authors: Ruishan Liu; Nicolò Fusi; Lester Mackey
- Year: 2018
- DOI: 10.48550/arxiv.1812.02271
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1812.02271
- PDF: https://arxiv.org/pdf/1812.02271

More accurate machine learning models often demand more computation and memory at test time, making them difficult to deploy on CPU- or memory-constrained devices. Teacher-student compression (TSC), also known as distillation, alleviates this burden by training a less expensive student model to mimic the expensive teacher model while maintaining most of the original accuracy. However, when fresh data is unavailable for the compression task, the teacher's training data is typically reused, leading to suboptimal compression. In this work, we propose to augment the compression dataset with synthetic data from a generative adversarial network (GAN) designed to approximate the training data distribution. Our GAN-assisted TSC (GAN-TSC) significantly improves student accuracy for expensive models such as large random forests and deep neural networks on both tabular and image datasets. Building on these results, we propose a comprehensive metric---the TSC Score---to evaluate the quality of synthetic datasets based on their induced TSC performance. The TSC Score captures both data diversity and class affinity, and we illustrate its benefits over the popular Inception Score in the context of image classification.

## 140. Synthesizing Property & Casualty Ratemaking Datasets using Generative Adversarial Networks.

- Authors: Marie‐Pier Côté; Brian Hartman; Olaf Mercier; Joshua Meyers; Jared Cummings; Elijah Harmon
- Year: 2020
- DOI: 
- Venue: arXiv (Cornell University)
- Countries: US
- Source: openalex
- URL: https://openalex.org/W3049742357
- PDF: https://arxiv.org/pdf/2008.06110

Due to confidentiality issues, it can be difficult to access or share interesting datasets for methodological development in actuarial science, or other fields where personal data are important. We show how to design three different types of generative adversarial networks (GANs) that can build a synthetic insurance dataset from a confidential original dataset. The goal is to obtain synthetic data that no longer contains sensitive information but still has the same structure as the original dataset and retains the multivariate relationships. In order to adequately model the specific characteristics of insurance data, we use GAN architectures adapted for multi-categorical data: a Wassertein GAN with gradient penalty (MC-WGAN-GP), a conditional tabular GAN (CTGAN) and a Mixed Numerical and Categorical Differentially Private GAN (MNCDP-GAN). For transparency, the approaches are illustrated using a public dataset, the French motor third party liability data. We compare the three different GANs on various aspects: ability to reproduce the original data structure and predictive models, privacy, and ease of use. We find that the MC-WGAN-GP synthesizes the best data, the CTGAN is the easiest to use, and the MNCDP-GAN guarantees differential privacy.

## 141. Fake it till you make it: Synthetic data for emerging carsharing programs

- Authors: Tobias Albrecht; Robert Keller; Dominik Rebholz; Maximilian Röglinger
- Year: 2024
- DOI: 10.1016/j.trd.2024.104067
- Venue: Transportation Research Part D Transport and Environment
- Countries: DE
- Source: openalex
- URL: https://doi.org/10.1016/j.trd.2024.104067
- PDF: https://doi.org/10.1016/j.trd.2024.104067

Carsharing is an integral part of the transformation toward flexible and sustainable mobility. New carsharing programs are entering the market to challenge large operators by offering innovative services. This study investigates the use of generative machine learning models for creating synthetic data to support carsharing decision–making when data access is limited. To this end, it explores the evaluation, selection, and implementation of leading-edge methods, such as generative adversarial networks (GANs) and variational autoencoders (VAEs), to generate synthetic tabular transaction data of carsharing trips. The study analyzes usage data of an emerging carsharing program that is expanding its services to include free-floating electric vehicles (EVs). The results show that augmenting real training data with synthetic samples improves predictive modeling of upcoming trips by up to 4.63%. These results support carsharing researchers and practitioners in generating and leveraging synthetic mobility data to develop solutions to real-world decision support problems in carsharing.

## 142. FCT-GAN: Enhancing Global Correlation of Table Synthesis via Fourier Transform

- Authors: Zilong Zhao; Robert Birke; Lydia Y. Chen
- Year: 2023
- DOI: 10.1145/3583780.3615202
- Venue: 
- Countries: IT; NL
- Source: openalex
- URL: https://doi.org/10.1145/3583780.3615202
- PDF: https://repository.tudelft.nl/file/File_89ac2949-7b71-433e-9743-93b3b79b4738

An alternative method for sharing knowledge while complying with strict data access regulations, such as the European General Data Protection Regulation (GDPR), is the emergence of synthetic tabular data. Mainstream table synthesizers utilize methodologies derived from Generative Adversarial Networks (GAN). Although several state-of-the-art (SOTA) tabular GAN algorithms inherit Convolutional Neural Network (CNN)-based architectures, which have proven effective for images, they tend to overlook two critical properties of tabular data: (i) the global correlation across columns, and (ii) the semantic invariance to the column order. Permuting columns in a table does not alter the semantic meaning of the data, but features extracted by CNNs can change significantly due to their limited convolution filter kernel size. To address the above problems, we propose FCT-GAN the first conditional tabular GAN to adopt Fourier networks into table synthesis. FCT-GAN enhances permutation invariant GAN training by strengthening the learning of global correlations via Fourier layers. Extensive evaluation on benchmarks and real-world datasets show that FCT-GAN can synthesize tabular data with better (up to 27.8%) machine learning utility (i.e. a proxy of global correlations) and higher (up to 26.5%) statistical similarity to real data. FCT-GAN also has the least variation on synthetic data quality among 7 SOTA baselines on 3 different training-data column orders.

## 143. COVID-19 Hierarchical Classification Using a Deep Learning Multi-Modal

- Authors: Albatoul S. Althenayan; Shada Alsalamah; Sherin Aly; Thamer Nouh; Bassam Mahboub; Laila Salameh; Metab Alkubeyyer; Abdulrahman Mirza
- Year: 2024
- DOI: 10.3390/s24082641
- Venue: Sensors
- Countries: AE; CH; EG; SA
- Source: openalex
- URL: https://doi.org/10.3390/s24082641
- PDF: https://www.mdpi.com/1424-8220/24/8/2641/pdf?version=1713608283

Coronavirus disease 2019 (COVID-19), originating in China, has rapidly spread worldwide. Physicians must examine infected patients and make timely decisions to isolate them. However, completing these processes is difficult due to limited time and availability of expert radiologists, as well as limitations of the reverse-transcription polymerase chain reaction (RT-PCR) method. Deep learning, a sophisticated machine learning technique, leverages radiological imaging modalities for disease diagnosis and image classification tasks. Previous research on COVID-19 classification has encountered several limitations, including binary classification methods, single-feature modalities, small public datasets, and reliance on CT diagnostic processes. Additionally, studies have often utilized a flat structure, disregarding the hierarchical structure of pneumonia classification. This study aims to overcome these limitations by identifying pneumonia caused by COVID-19, distinguishing it from other types of pneumonia and healthy lungs using chest X-ray (CXR) images and related tabular medical data, and demonstrate the value of incorporating tabular medical data in achieving more accurate diagnoses. Resnet-based and VGG-based pre-trained convolutional neural network (CNN) models were employed to extract features, which were then combined using early fusion for the classification of eight distinct classes. We leveraged the hierarchal structure of pneumonia classification within our approach to achieve improved classification outcomes. Since an imbalanced dataset is common in this field, a variety of versions of generative adversarial networks (GANs) were used to generate synthetic data. The proposed approach tested in our private datasets of 4523 patients achieved a macro-avg F1-score of 95.9% and an F1-score of 87.5% for COVID-19 identification using a Resnet-based structure. In conclusion, in this study, we were able to create an accurate deep learning multi-modal to diagnose COVID-19 and differentiate it from other kinds of pneumonia and normal lungs, which will enhance the radiological diagnostic process.

## 144. Privacy Re‐Identification Attacks on Tabular GANs

- Authors: Abdallah Alshantti; Adil Rasheed; Frank Westad
- Year: 2024
- DOI: 10.1002/spy2.469
- Venue: Security and Privacy
- Countries: NO
- Source: openalex
- URL: https://doi.org/10.1002/spy2.469
- PDF: https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/spy2.469

ABSTRACT Generative models are effective in producing realistic tabular synthetic data that resembles the properties and distribution of real datasets. While synthetic data has numerous applications across various domains, generative models are susceptible to overfitting, which can lead to the leakage of sensitive information from training data. Privacy attacks exacerbate this issue by attempting to identify original data records from synthetic data, especially when the attacker possesses some knowledge about the generative model. In this work, we investigate the privacy risks associated with using generative adversarial networks (GANs) to create tabular synthetic datasets. More specifically, we develop privacy reconstruction attacks designed to identify training samples by minimizing their proximity to synthetic records. Our experimental analysis considers various scenarios of reconstruction attacks, in which attackers have different levels of access to the generative models. Additionally, we propose multi‐objective optimization using evolutionary algorithms to perturb synthetic samples closer to original training data points. The experimental results show that reconstruction attacks can effectively identify training samples, with privacy threats significantly increasing when attackers have access to the generative model. Furthermore, our findings indicate that using evolutionary algorithms in reconstruction attacks further heightens the risk of identifying confidential samples. Comparing our attacks against state‐of‐the‐art privacy attacks on tabular GANs further reveals that our reconstructions attacks are considerably more effective in recovering real data records.

## 145. CG-TGAN: Conditional Generative Adversarial Networks with Graph Neural Networks for Tabular Data Synthesizing

- Authors: Seung Chul Lee; Moohong Min
- Year: 2025
- DOI: 10.1609/aaai.v39i17.33996
- Venue: Proceedings of the AAAI Conference on Artificial Intelligence
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.1609/aaai.v39i17.33996
- PDF: https://ojs.aaai.org/index.php/AAAI/article/download/33996/36151

Data sharing is necessary for AI to be widely used, but sharing sensitive data with others with privacy is risky. To solve these problems, it is necessary to synthesize realistic tabular data. In many cases, tabular data contains a mixture of continuous, mixed, categorical columns. Moreover, columns of the same type may have multimodal distribution or be highly imbalanced. These issues make it challenging to synthesize tabular data. The synthesized tabular data should reflect the relational meaning between columns of tabular data, so modeling the probability distribution of tabular data is a non-trivial task. Traditional tabular data synthesizing models are based on GAN or diffusion models and are built using fully connected or convolutional layers. However, fully connected layers have the disadvantage of low inductive bias, and convolutional layers are not invariant to the column order of tabular data. Therefore, we assume that converting tabular data into graph-structured data and using a graph neural network would produce better synthetic data than using fully connected layers or convolutional layers. Our study aims to show that GANs constructed with graph neural networks can outperform existing GAN models using fully connected layers or convolutional layers. We propose CG-TGAN, a conditional GAN built using graph neural networks. To learn how to synthesize realistic data, the graph neural networks in the discriminator and generator learn graph-level tasks and node-level tasks together. The discriminator of CG-TGAN learns a graph-level task to distinguish between real and synthetic data and node-level tasks to predict the value of the target node. CG-TGAN’s generator learns a graph-level task to synthesize an overall graph similar to real data and node-level tasks to learn how to synthesize a fake graph with the proper relation between nodes. In this paper, we show that CG-TGAN outperforms GAN-based models and is comparable to diffusion-based models.

## 146. VT-GAN: Cooperative Tabular Data Synthesis using Vertical Federated Learning

- Authors: Zilong Zhao; Han Wu; Aad van Moorsel; Lydia Y. Chen
- Year: 2023
- DOI: 10.48550/arxiv.2302.01706
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2302.01706
- PDF: https://arxiv.org/pdf/2302.01706

This paper presents the application of Vertical Federated Learning (VFL) to generate synthetic tabular data using Generative Adversarial Networks (GANs). VFL is a collaborative approach to train machine learning models among distinct tabular data holders, such as financial institutions, who possess disjoint features for the same group of customers. In this paper we introduce the VT-GAN framework, Vertical federated Tabular GAN, and demonstrate that VFL can be successfully used to implement GANs for distributed tabular data in privacy-preserving manner, with performance close to centralized GANs that assume shared data. We make design choices with respect to the distribution of GAN generator and discriminator models and introduce a training-with-shuffling technique so that no party can reconstruct training data from the GAN conditional vector. The paper presents (1) an implementation of VT-GAN, (2) a detailed quality evaluation of the VT-GAN-generated synthetic data, (3) an overall scalability examination of VT-GAN framework, (4) a security analysis on VT-GAN's robustness against Membership Inference Attack with different settings of Differential Privacy, for a range of datasets with diverse distribution characteristics. Our results demonstrate that VT-GAN can consistently generate high-fidelity synthetic tabular data of comparable quality to that generated by a centralized GAN algorithm. The difference in machine learning utility can be as low as 2.7%, even under extremely imbalanced data distributions across clients or with different numbers of clients.

## 147. DTGAN: Differential Private Training for Tabular GANs

- Authors: Aditya Kunar; Robert Birke; Zilong Zhao; Lydia Y. Chen
- Year: 2021
- DOI: 10.48550/arxiv.2107.02521
- Venue: arXiv (Cornell University)
- Countries: CH; NL
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2107.02521
- PDF: https://arxiv.org/pdf/2107.02521

Tabular generative adversarial networks (TGAN) have recently emerged to cater to the need of synthesizing tabular data -- the most widely used data format. While synthetic tabular data offers the advantage of complying with privacy regulations, there still exists a risk of privacy leakage via inference attacks due to interpolating the properties of real data during training. Differential private (DP) training algorithms provide theoretical guarantees for training machine learning models by injecting statistical noise to prevent privacy leaks. However, the challenges of applying DP on TGAN are to determine the most optimal framework (i.e., PATE/DP-SGD) and neural network (i.e., Generator/Discriminator)to inject noise such that the data utility is well maintained under a given privacy guarantee. In this paper, we propose DTGAN, a novel conditional Wasserstein tabular GAN that comes in two variants DTGAN_G and DTGAN_D, for providing a detailed comparison of tabular GANs trained using DP-SGD for the generator vs discriminator, respectively. We elicit the privacy analysis associated with training the generator with complex loss functions (i.e., classification and information losses) needed for high quality tabular data synthesis. Additionally, we rigorously evaluate the theoretical privacy guarantees offered by DP empirically against membership and attribute inference attacks. Our results on 3 datasets show that the DP-SGD framework is superior to PATE and that a DP discriminator is more optimal for training convergence. Thus, we find (i) DTGAN_D is capable of maintaining the highest data utility across 4 ML models by up to 18% in terms of the average precision score for a strict privacy budget, epsilon = 1, as compared to the prior studies and (ii) DP effectively prevents privacy loss against inference attacks by restricting the success probability of membership attacks to be close to 50%.

## 148. Real-time earthquake magnitude prediction using designed machine learning ensemble trained on real and CTGAN generated synthetic data

- Authors: Anushka Joshi; Balasubramanian Raman; C. Krishna Mohan
- Year: 2025
- DOI: 10.1016/j.geog.2024.10.001
- Venue: Geodesy and Geodynamics
- Countries: 
- Source: openalex
- URL: https://doi.org/10.1016/j.geog.2024.10.001
- PDF: https://doi.org/10.1016/j.geog.2024.10.001

The earthquake early warning (EEW) system provides advance notice of potentially damaging ground shaking. In EEW, early estimation of magnitude is crucial for timely rescue operations. A set of thirty-four features is extracted using the primary wave earthquake precursor signal and site-specific information. In Japan's earthquake magnitude dataset, there is a chance of a high imbalance concerning the earthquakes above strong impact. This imbalance causes a high prediction error while training advanced machine learning or deep learning models. In this work, Conditional Tabular Generative Adversarial Networks (CTGAN), a deep machine learning tool, is utilized to learn the characteristics of the first arrival of earthquake P-waves and generate a synthetic dataset based on this information. The result obtained using actual and mixed (synthetic and actual) datasets will be used for training the stacked ensemble magnitude prediction model, MagPred, designed specifically for this study. There are 13295, 3989, and 1710 records designated for training, testing, and validation. The mean absolute error of the test dataset for single station magnitude detection using early three, four, and five seconds of P wave are 0.41, 0.40, and 0.38 MJMA. The study demonstrates that the Generative Adversarial Networks (GANs) can provide a good result for single-station magnitude prediction. The study can be effective where less seismic data is available. The study shows that the machine learning method yields better magnitude detection results compared with the several regression models. The multi-station magnitude prediction study has been conducted on prominent Osaka, Off Fukushima, and Kumamoto earthquakes. Furthermore, to validate the performance of the model, an inter-region study has been performed on the earthquakes of the India or Nepal region. The study demonstrates that GANs can discover effective magnitude estimation compared with non-GAN-based methods. This has a high potential for wide application in earthquake early warning systems.

## 149. Advancing student outcome predictions through generative adversarial networks

- Authors: Helia Farhood; Ibrahim Joudah; Amin Beheshti; Samuel Müller
- Year: 2024
- DOI: 10.1016/j.caeai.2024.100293
- Venue: Computers and Education Artificial Intelligence
- Countries: AU
- Source: openalex
- URL: https://doi.org/10.1016/j.caeai.2024.100293
- PDF: https://doi.org/10.1016/j.caeai.2024.100293

Predicting student outcomes is essential in educational analytics for creating personalised learning experiences. The effectiveness of these predictive models relies on having access to sufficient and accurate data. However, privacy concerns and the lack of student consent often restrict data collection, limiting the applicability of predictive models. To tackle this obstacle, we employ Generative Adversarial Networks, a type of Generative AI, to generate tabular data replicating and enlarging the dimensions of two distinct publicly available student datasets. The ‘Math dataset’ has 395 observations and 33 features, whereas the ‘Exam dataset’ has 1000 observations and 8 features. Using advanced Python libraries, Conditional Tabular Generative Adversarial Networks and Copula Generative Adversarial Networks, our methodology consists of two phases. First, a mirroring approach where we produce synthetic data matching the volume of the real datasets, focusing on privacy and evaluating predictive accuracy. Second, augmenting the real datasets with newly created synthetic observations to fill gaps in datasets that lack student data. We validate the synthetic data before employing these approaches using Correlation Analysis, Density Analysis, Correlation Heatmaps, and Principal Component Analysis. We then compare the predictive accuracy of whether students will pass or fail their exams across original, synthetic, and augmented datasets. Employing Feedforward Neural Networks, Convolutional Neural Networks, and Gradient-boosted Neural Networks, and using Bayesian optimisation for hyperparameter tuning, this research methodically examines the impact of synthetic data on prediction accuracy. We implement and optimize these models using Python. Our mirroring approach aims to achieve accuracy rates that closely align with the original data. Meanwhile, our augmenting approach seeks to reach a slightly higher accuracy level than when solely learning from the original data. Our findings provide actionable insights into leveraging advanced Generative AI techniques to enhance educational outcomes and meet our objectives successfully. • Generative AI is used to generate privacy-preserving synthetic data that resemble real student datasets. • Predictive models for student outcomes can be improved by the integration of synthetic and actual data. • Synthetic data has been validated via correlation analysis, density analysis, heatmaps, and PCA. • Three neural networks were used to evaluate the accuracy of student outcome predictions using synthetic and original data. • The study emphasises the importance of dataset structure, training duration, and GAN selection in synthetic data quality.

## 150. Towards Addressing the Spatial Sparsity of MDT Reports to Enable Zero Touch Network Automation

- Authors: Joel Shodamola; Haneya Naeem Qureshi; Usama Masood; Ali Imran
- Year: 2021
- DOI: 10.1109/globecom46510.2021.9686011
- Venue: 2021 IEEE Global Communications Conference (GLOBECOM)
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1109/globecom46510.2021.9686011

Minimization of Drive Test (MDT) reports are a key enabler for Machine Learning (ML)-based zero-touch automation envisioned for emerging cellular networks. However, due to numerous factors, the MDT reports are spatially sparse in nature. This sparsity undermines the performance of ML models that are built on the MDT data to estimate and optimize network KPIs. In this paper, we present and evaluate a framework to address this challenge. We leverage generative models, specifically, Gener-ative Adversarial Networks (GAN) and Variational Autoencoders (VAE) to augment the sparse multi-dimensional MDT data. Unlike image data where the quality of synthetic images produced by the generative models can be evaluated visually, establishing the authenticity of tabular synthetic data is a more complex problem. We address this problem by leveraging a tripartite approach: 1) We use several statistical measures to quantify the resemblance of synthetic data with original data. 2) We compare the performance of an ensemble learning model trained on augmented data, with that of trained on original data only 3) We benchmark the performance of the generative models with several classical ML models. This analysis is carried out for varying levels of sparsity and reveals insights about robustness of generative models against training data sparsity as well as on suitability of various methods for evaluating the quality of the generated synthetic tabular data. Results show GAN performs considerably better compared to other approaches. The presented solution thus can be used to overcome the sparsity problem in MDT reports thereby enabling ML-based automation use cases.

## 151. An intra-class distribution-focused generative adversarial network approach for imbalanced tabular data learning

- Authors: Qiuling Chen; Ayong Ye; Yuexin Zhang; Jianwei Chen; Chuan Huang
- Year: 2024
- DOI: 10.1007/s13042-023-02048-5
- Venue: International Journal of Machine Learning and Cybernetics
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1007/s13042-023-02048-5

## 152. Addressing Data Imbalance in Crash Data: Evaluating Generative Adversarial Network’s Efficacy Against Conventional Methods

- Authors: Bei Zhou; Qianxi Zhou; Zongzhi Li
- Year: 2024
- DOI: 10.1109/access.2024.3524620
- Venue: IEEE Access
- Countries: CN; US
- Source: openalex
- URL: https://doi.org/10.1109/access.2024.3524620
- PDF: https://doi.org/10.1109/access.2024.3524620

In the realm of traffic safety analysis, the inherent imbalance in crash datasets, particularly in terms of injury severity, poses a significant challenge for machine learning-based classification models. This study delves into the efficacy of Generative Adversarial Networks (GANs), with a specific focus on Conditional Tabular GAN (CTGAN), for synthesizing minority crash data to address this imbalance. Utilizing traffic crash data from Chicago spanning 2020 to 2022, the research evaluates the capabilities of CTGAN against three traditional data resampling methods, as well as an additional cost-sensitive learning approach. These methods are evaluated across various injury severity classification scenarios (2-class, 3-class, and 4-class) using five commonly applied injury severity classification models. The study’s dual evaluation approach encompasses both the quality of synthetic data and the enhancement of classification model performance. The pivotal findings reveal that: 1) CTGAN markedly outperforms other data resampling techniques in generating superior quality synthetic data, particularly for the least represented injury severity category; 2) While CTGAN demonstrates substantial improvements over traditional data resampling methods in classification model performance, this advantage diminishes as the number of injury categories increases; 3) Surprisingly, CTGAN’s superior data quality does not result in better classification performance compared to cost-sensitive learning, especially in more complex classification scenarios. Cost-sensitive learning combined with LightGBM achieves the best classification performance across all scenarios. Given the significantly lower computational resources required by cost-sensitive learning, this approach is recommended for handling imbalanced injury severity data.

## 153. Bridging Stability and Utility in Synthetic Tabular Data: The sTableGAN Model

- Authors: Mustafa Hakan Bozkurt
- Year: 2025
- DOI: 10.2139/ssrn.5573443
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.2139/ssrn.5573443

## 154. On the Quality of Synthetic Generated Tabular Data

- Authors: Erica Espinosa; Alvaro Figueira
- Year: 2023
- DOI: 10.3390/math11153278
- Venue: Mathematics
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3390/math11153278

<jats:p>Class imbalance is a common issue while developing classification models. In order to tackle this problem, synthetic data have recently been developed to enhance the minority class. These artificially generated samples aim to bolster the representation of the minority class. However, evaluating the suitability of such generated data is crucial to ensure their alignment with the original data distribution. Utility measures come into play here to quantify how similar the distribution of the generated data is to the original one. For tabular data, there are various evaluation methods that assess different characteristics of the generated data. In this study, we collected utility measures and categorized them based on the type of analysis they performed. We then applied these measures to synthetic data generated from two well-known datasets, Adults Income, and Liar+. We also used five well-known generative models, Borderline SMOTE, DataSynthesizer, CTGAN, CopulaGAN, and REaLTabFormer, to generate the synthetic data and evaluated its quality using the utility measures. The measurements have proven to be informative, indicating that if one synthetic dataset is superior to another in terms of utility measures, it will be more effective as an augmentation for the minority class when performing classification tasks.</jats:p>

## 155. Evaluating Fidelity and Machine Learning Utility of Synthetic Tabular Data Generated Using Generative Models

- Authors: Aaditya Kumar Dhaka; Apash Roy; S Shrivallabha
- Year: 2025
- DOI: 10.21203/rs.3.rs-7287372/v1
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.21203/rs.3.rs-7287372/v1

<title>Abstract</title>
        <p>Synthetic tabular data offers a promising solution for enabling privacy-preserving machine learning in sensitive domains such as healthcare. However, assessing the fidelity and utility of such data remains challenging. In this study, we evaluate four generative models—CTGAN, TVAE, Gaussian Copula, and CopulaGAN—on a benchmark dataset for stroke prediction. We propose a two-phase generation and evaluation framework that combines statistical diagnostics with feature-level fidelity analysis and downstream classification performance. Our findings highlight significant variation across models, with TVAE and Gaussian Copula achieving superior fidelity and generalization. The results demonstrate that high structural similarity does not always guarantee practical machine learning utility.</p>

## 156. Probabilistic vs Deep Generative Models: A Fairness Centred Evaluation of Synthetic Healthcare Tabular Data

- Authors: Dima Alattal; Barbara Draghi; Puja Myles; Richard Branson; Allan Tucker
- Year: 2025
- DOI: 10.21203/rs.3.rs-7565139/v1
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.21203/rs.3.rs-7565139/v1

<title>Abstract</title>
        <p><bold>Purpose: </bold>Synthetic data offers a promising avenue for addressing privacy, scarcity, and fairness challenges in healthcare datasets. However, there is limited evaluation of how different generation methods balance fidelity, utility, and fairness, particularly for underrepresented subgroups. This study addresses this gap by comparing representative generative modelling techniques, both probabilistic and deep approaches, that are popular in the research literature.
<bold>Methods:</bold> We empirically evaluate BayesBoost, CTGAN, TVAE, CopulaGAN, and DECAF on two healthcare datasets containing numerical, binary, and categorical features. Each model’s performance is assessed along three axes: data fidelity, machine learning utility, and fairness (using Accuracy Parity, Equalised Odds, and Predictive Rate Parity).
<bold>Results:</bold> BayesBoost consistently achieved superior fidelity, utility, and fairness preservation, particularly when paired with Random Forest classifiers. Deep generative models, while effective in capturing complex structures, often degraded fairness, especially for underrepresented groups. VAE outperformed other generative models in fairness preservation especially for equalised odds, but at some cost to fidelity and utility.
<bold>Conclusion:</bold> Synthetic data generation for healthcare must move beyond fidelity evaluations to explicitly assess fairness and subgroup impacts. Probabilistic models like BayesBoost show strong potential for ethical deployment, while deep generative models require further adaptation for fairness-sensitive applications.</p>

## 157. Bridging stability and utility in synthetic tabular data: The sTableGAN model

- Authors: Mustafa Hakan Bozkurt
- Year: 2026
- DOI: 10.1016/j.knosys.2026.115303
- Venue: Knowledge-Based Systems
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1016/j.knosys.2026.115303

## 158. Improving Liver Disease Diagnosis Through Generative Adversarial Network Driven Synthetic Tabular Data

- Authors: Mahendran. S; Venkatasekhar. D; Shanmugasundaram. G
- Year: 2024
- DOI: 10.1109/silcon63976.2024.10910379
- Venue: 2024 IEEE Silchar Subsection Conference (SILCON 2024)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/silcon63976.2024.10910379

## 159. Techniques to Improve the Utility of Synthetic Data Using XAI and Tabular GAN-Based Approaches

- Authors: Minchae Song
- Year: 2025
- DOI: 10.1007/978-3-031-94953-1_1
- Venue: Communications in Computer and Information Science
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1007/978-3-031-94953-1_1

## 160. Generating Realistic Synthetic Traffic Data using Conditional Tabular Generative Adversarial Networks for Intelligent Transportation Systems

- Authors: Archana Nigam; Sanjay Srivastava
- Year: 2023
- DOI: 10.1109/itsc57777.2023.10422234
- Venue: 2023 IEEE 26th International Conference on Intelligent Transportation Systems (ITSC)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/itsc57777.2023.10422234

## 161. The Effect of Combined Synthetic Tabular Data Generated Using CTGAN Model with Actual Data on Performance of DHF, Varicella, and COVID-19 Recognition Model

- Authors: Husni Iskandar Pohan
- Year: 2024
- DOI: 10.52783/jes.2913
- Venue: Journal of Electrical Systems
- Countries: 
- Source: crossref
- URL: https://doi.org/10.52783/jes.2913
- PDF: https://journal.esrgroups.org/jes/article/download/2913/2309

<jats:p>There are several quickly spreading illnesses such as DHFs spread by mosquitoes, COVID-19 spreads through respiratory droplets and contact with contaminated surfaces, and Varicella spreads by direct touch. The transmission rate of these diseases can be reduced if medical services can identify them early. However, the performance of the prediction model based on the machine learning approach is limited by the availability of labeled patient datasets.  This study showed some empirical evidence of the use of synthetic data generated using actual medical records as the basis to improve the performance of the prediction model. The empirical results showed that the Decision Tree algorithm which is trained using a mixed synthetic and actual dataset can achieve 91.98% average accuracy which is higher than model performance which is trained using real dataset only. The results of model interpretation using Shapley Additive Explanations have the advantage of measuring the overall dominant features and indicating that the top five most important features are vThrombocyte, vTemp, vCough, vSpot, and vNauseous.  </jats:p>

## 162. The Effect of Combined Synthetic Tabular Data Generated Using CTGAN Model with Actual Data on Performance of DHF, Varicella, and COVID-19 Recognition Model

- Authors: Husni Iskandar Pohan
- Year: 2024
- DOI: 10.52783/jes.3797
- Venue: Journal of Electrical Systems
- Countries: 
- Source: crossref
- URL: https://doi.org/10.52783/jes.3797
- PDF: https://journal.esrgroups.org/jes/article/download/3797/2863

<jats:p>There are several quickly spreading illnesses such as DHFs spread by mosquitoes, COVID-19 spreads through respiratory droplets and contact with contaminated surfaces, and Varicella spreads by direct touch. The transmission rate of these diseases can be reduced if medical services can identify them early. However, the performance of the prediction model based on the machine learning approach is limited by the availability of labelled patient datasets.  This study showed some empirical evidence of the use of synthetic data generated using actual medical records as the basis to improve the performance of the prediction model. The empirical results showed that the Decision Tree algorithm which is trained using a mixed synthetic and actual dataset can achieve 91.98% average accuracy which is higher than model performance which is trained using real dataset only. The results of model interpretation using Shapley Additive Explanations have the advantage of measuring the overall dominant features and indicating that the top five most important features are Thrombocyte, Temp, Cough, Spot, and Nauseous .</jats:p>

## 163. Privacy-Preserving Synthetic Data Generation Using Conditional Tabular Generative Adversarial Networks

- Authors: Virezo Georgian; Yudhistira Nugraha; Muhammad Erza Aminanto
- Year: 2025
- DOI: 10.1109/icicyta68677.2025.11362835
- Venue: 2025 5th International Conference on Intelligent Cybernetics Technology &amp;amp; Applications (ICICyTA)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/icicyta68677.2025.11362835

## 164. Conditional Tabular Generative Adversarial Network-based Synthetic Data Generation for Model Generalisation Improvement

- Authors: Yuhanis Yusof; Fathima Fajila
- Year: 2026
- DOI: 10.32890/jict2026.25.1.1
- Venue: Journal of Information and Communication Technology
- Countries: 
- Source: crossref
- URL: https://doi.org/10.32890/jict2026.25.1.1

<jats:p>Accessing extensive and varied datasets is essential for developing strong predictive models in data analytics. However, many real-world applications suffer from small and imbalanced datasets, leading to overfitting, poor generalisation, and low model performance. Traditional data augmentation techniques are often unsuitable for tabular data, as they fail to preserve complex feature relationships. To address this challenge, this study adapts the Conditional Tabular Generative Adversarial Network (CTGAN) for synthetic data generation. The proposed approach involves five phases: (1) Data Acquisition, 2) Data Preparation, (3) Model Training, (4) Synthetic Data Generation, and (5) Evaluation.  Experimental results on three benchmark datasets show that the proposed work produced data that closely adheres to the statistical distribution of the original dataset, with Wasserstein Distance &lt; 0.05 for numerical features and Jensen-Shannon Divergence &lt; 0.08 for categorical features. Additionally, models trained on datasets including synthetic and real data achieved up to 15% improvement in classification accuracy compared to those trained on real and small datasets alone. Training on a combination of real and synthetic data for the minority class in large datasets significantly improves the F1-score, with gains of approximately 9–10%. This approach also yields a modest increase in overall accuracy (around 1.5%), suggesting enhanced model generalisation. These results indicate that the adapted CTGAN is a viable option for data augmentation, addressing problems with limited and imbalanced data for machine learning data training.</jats:p>

## 165. Conditional Hybrid GAN for Sequence Generation

- Authors: Yi Yu; Abhishek Srivastava; Rajiv Ratn Shah
- Year: 2020
- DOI: 10.48550/arxiv.2009.08616
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2009.08616
- PDF: https://arxiv.org/pdf/2009.08616

Conditional sequence generation aims to instruct the generation procedure by conditioning the model with additional context information, which is a self-supervised learning issue (a form of unsupervised learning with supervision information from data itself). Unfortunately, the current state-of-the-art generative models have limitations in sequence generation with multiple attributes. In this paper, we propose a novel conditional hybrid GAN (C-Hybrid-GAN) to solve this issue. Discrete sequence with triplet attributes are separately generated when conditioned on the same context. Most importantly, relational reasoning technique is exploited to model not only the dependency inside each sequence of the attribute during the training of the generator but also the consistency among the sequences of attributes during the training of the discriminator. To avoid the non-differentiability problem in GANs encountered during discrete data generation, we exploit the Gumbel-Softmax technique to approximate the distribution of discrete-valued sequences.Through evaluating the task of generating melody (associated with note, duration, and rest) from lyrics, we demonstrate that the proposed C-Hybrid-GAN outperforms the existing methods in context-conditioned discrete-valued sequence generation.

## 166. A Systematic Review of Synthetic Data Generation Techniques Using Generative AI

- Authors: Mandeep Goyal; Qusay H. Mahmoud
- Year: 2024
- DOI: 10.3390/electronics13173509
- Venue: Electronics
- Countries: CA
- Source: openalex
- URL: https://doi.org/10.3390/electronics13173509
- PDF: https://www.mdpi.com/2079-9292/13/17/3509/pdf?version=1725441340

Synthetic data are increasingly being recognized for their potential to address serious real-world challenges in various domains. They provide innovative solutions to combat the data scarcity, privacy concerns, and algorithmic biases commonly used in machine learning applications. Synthetic data preserve all underlying patterns and behaviors of the original dataset while altering the actual content. The methods proposed in the literature to generate synthetic data vary from large language models (LLMs), which are pre-trained on gigantic datasets, to generative adversarial networks (GANs) and variational autoencoders (VAEs). This study provides a systematic review of the various techniques proposed in the literature that can be used to generate synthetic data to identify their limitations and suggest potential future research areas. The findings indicate that while these technologies generate synthetic data of specific data types, they still have some drawbacks, such as computational requirements, training stability, and privacy-preserving measures which limit their real-world usability. Addressing these issues will facilitate the broader adoption of synthetic data generation techniques across various disciplines, thereby advancing machine learning and data-driven solutions.

## 167. BAGAN: Effective Data Generation Based on GAN Augmented 3D Synthesizing

- Authors: Yan Ma; Kang Liu; Zhi-Bin Guan; Xin-Kai Xu; Xu Qian; Hong Bao
- Year: 2018
- DOI: 10.20944/preprints201811.0252.v1
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.20944/preprints201811.0252.v1

<jats:p>Augment reality (AR) is crucial for immersive human-computer interaction (HCI) and vision of artificial intelligence (AI). Labeled data drove object recognition in AR. However, manual annotating data is expensive and labor-intensive, and furthermore, scanty labeled data limits the application of AR. Aiming at solving the problem of insufficient training data in AR object recognition, an automated vision data synthesis method called BAGAN is proposed in this paper based on the 3D modeling and GAN algorithm. Our approach has been validated to have better performance than other methods through image recognition task on natural image database ObjectNet3D. This study can shorten the algorithm development time of AR and expand the application scope of AR, which is of great significance to immersive interactive systems.</jats:p>

## 168. VAE-GAN-Guided Cross-Class Generation: A Class Imbalance Data Augmentation Method for Network Intrusion Detection

- Authors: Fuyuan Kang; Tao Feng; Jiaqi Lin
- Year: 2025
- DOI: 10.3390/electronics14112103
- Venue: Electronics
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3390/electronics14112103

<jats:p>Network intrusion datasets often face class imbalance issues in intrusion detection tasks, where the number of majority class samples is much higher than minority class samples. Current solutions face notable limitations: traditional normalization weakens the multimodal distribution of continuous features, while mainstream generative models focus excessively on minority class mining while neglecting majority class information. To address these issues, we propose M2M-VAEGAN, which innovatively incorporates a Variational Gaussian Mixture (VGM) model to preserve multimodal characteristics of continuous features. We design a transfer learning framework, pre-training on majority classes to capture general attack patterns, followed by fine-tuning with balanced batches of majority and minority samples to prevent catastrophic forgetting. Additionally, we enhance the VAEGAN architecture with an auxiliary classifier to strengthen conditional information learning. On the NSL-KDD and CIC-IDS2017 datasets, M2M-VAEGAN outperforms methods such as SMOTE, CTGAN, and CTABGAN, achieving a 1.25% to 6.42% improvement in minority class recall. These results demonstrate the effectiveness of the proposed approach.</jats:p>

## 169. Synthesizing electronic health records using improved generative adversarial networks

- Authors: Mrinal Kanti Baowaly; Chia-Ching Lin; Chao-Lin Liu; Kuan-Ta Chen
- Year: 2018
- DOI: 10.1093/jamia/ocy142
- Venue: Journal of the American Medical Informatics Association
- Countries: TW
- Source: openalex
- URL: https://doi.org/10.1093/jamia/ocy142
- PDF: https://academic.oup.com/jamia/article-pdf/26/3/228/27642536/ocy142.pdf

Objective: The aim of this study was to generate synthetic electronic health records (EHRs). The generated EHR data will be more realistic than those generated using the existing medical Generative Adversarial Network (medGAN) method. Materials and Methods: We modified medGAN to obtain two synthetic data generation models-designated as medical Wasserstein GAN with gradient penalty (medWGAN) and medical boundary-seeking GAN (medBGAN)-and compared the results obtained using the three models. We used 2 databases: MIMIC-III and National Health Insurance Research Database (NHIRD), Taiwan. First, we trained the models and generated synthetic EHRs by using these three 3 models. We then analyzed and compared the models' performance by using a few statistical methods (Kolmogorov-Smirnov test, dimension-wise probability for binary data, and dimension-wise average count for count data) and 2 machine learning tasks (association rule mining and prediction). Results: We conducted a comprehensive analysis and found our models were adequately efficient for generating synthetic EHR data. The proposed models outperformed medGAN in all cases, and among the 3 models, boundary-seeking GAN (medBGAN) performed the best. Discussion: To generate realistic synthetic EHR data, the proposed models will be effective in the medical industry and related research from the viewpoint of providing better services. Moreover, they will eliminate barriers including limited access to EHR data and thus accelerate research on medical informatics. Conclusion: The proposed models can adequately learn the data distribution of real EHRs and efficiently generate realistic synthetic EHRs. The results show the superiority of our models over the existing model.

## 170. Anonymization Through Data Synthesis Using Generative Adversarial Networks (ADS-GAN)

- Authors: Jinsung Yoon; Lydia N. Drumright; Mihaela van der Schaar
- Year: 2020
- DOI: 10.1109/jbhi.2020.2980262
- Venue: IEEE Journal of Biomedical and Health Informatics
- Countries: GB; SS; US
- Source: openalex
- URL: https://doi.org/10.1109/jbhi.2020.2980262

The medical and machine learning communities are relying on the promise of artificial intelligence (AI) to transform medicine through enabling more accurate decisions and personalized treatment. However, progress is slow. Legal and ethical issues around unconsented patient data and privacy is one of the limiting factors in data sharing, resulting in a significant barrier in accessing routinely collected electronic health records (EHR) by the machine learning community. We propose a novel framework for generating synthetic data that closely approximates the joint distribution of variables in an original EHR dataset, providing a readily accessible, legally and ethically appropriate solution to support more open data sharing, enabling the development of AI solutions. In order to address issues around lack of clarity in defining sufficient anonymization, we created a quantifiable, mathematical definition for "identifiability". We used a conditional generative adversarial networks (GAN) framework to generate synthetic data while minimize patient identifiability that is defined based on the probability of re-identification given the combination of all data on any individual patient. We compared models fitted to our synthetically generated data to those fitted to the real data across four independent datasets to evaluate similarity in model performance, while assessing the extent to which original observations can be identified from the synthetic data. Our model, ADS-GAN, consistently outperformed state-of-the-art methods, and demonstrated reliability in the joint distributions. We propose that this method could be used to develop datasets that can be made publicly available while considerably lowering the risk of breaching patient confidentiality.

## 171. Generating synthetic mixed-type longitudinal electronic health records for artificial intelligent applications

- Authors: Jin Li; Benjamin J. Cairns; Jingsong Li; Tingting Zhu
- Year: 2023
- DOI: 10.1038/s41746-023-00834-7
- Venue: npj Digital Medicine
- Countries: CN; GB
- Source: openalex
- URL: https://doi.org/10.1038/s41746-023-00834-7
- PDF: https://www.nature.com/articles/s41746-023-00834-7.pdf

The recent availability of electronic health records (EHRs) have provided enormous opportunities to develop artificial intelligence (AI) algorithms. However, patient privacy has become a major concern that limits data sharing across hospital settings and subsequently hinders the advances in AI. Synthetic data, which benefits from the development and proliferation of generative models, has served as a promising substitute for real patient EHR data. However, the current generative models are limited as they only generate single type of clinical data for a synthetic patient, i.e., either continuous-valued or discrete-valued. To mimic the nature of clinical decision-making which encompasses various data types/sources, in this study, we propose a generative adversarial network (GAN) entitled EHR-M-GAN that simultaneously synthesizes mixed-type timeseries EHR data. EHR-M-GAN is capable of capturing the multidimensional, heterogeneous, and correlated temporal dynamics in patient trajectories. We have validated EHR-M-GAN on three publicly-available intensive care unit databases with records from a total of 141,488 unique patients, and performed privacy risk evaluation of the proposed model. EHR-M-GAN has demonstrated its superiority over state-of-the-art benchmarks for synthesizing clinical timeseries with high fidelity, while addressing the limitations regarding data types and dimensionality in the current generative models. Notably, prediction models for outcomes of intensive care performed significantly better when training data was augmented with the addition of EHR-M-GAN-generated timeseries. EHR-M-GAN may have use in developing AI algorithms in resource-limited settings, lowering the barrier for data acquisition while preserving patient privacy.

## 172. A Survey of Generative Adversarial Networks for Synthesizing Structured Electronic Health Records

- Authors: Ghadeer O. Ghosheh; Jin Li; Tingting Zhu
- Year: 2023
- DOI: 10.1145/3636424
- Venue: ACM Computing Surveys
- Countries: CN; GB
- Source: openalex
- URL: https://doi.org/10.1145/3636424
- PDF: https://dl.acm.org/doi/pdf/10.1145/3636424

Electronic Health Records (EHRs) are a valuable asset to facilitate clinical research and point of care applications; however, many challenges such as data privacy concerns impede its optimal utilization. Deep generative models, particularly Generative Adversarial Networks (GANs), show great promise in generating synthetic EHR data by learning underlying data distributions while achieving excellent performance and addressing these challenges. This work aims to survey the major developments in various applications of GANs for EHRs and provides an overview of the proposed methodologies. For this purpose, we combine perspectives from healthcare applications and machine learning techniques in terms of source datasets and the fidelity and privacy evaluation of the generated synthetic datasets. We also compile a list of the metrics and datasets used by the reviewed works, which can be utilized as benchmarks for future research in the field. We conclude by discussing challenges in GANs for EHRs development and proposing recommended practices. We hope that this work motivates novel research development directions in the intersection of healthcare and machine learning.

## 173. Natural language generation for electronic health records

- Authors: Scott Lee
- Year: 2018
- DOI: 10.1038/s41746-018-0070-0
- Venue: npj Digital Medicine
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1038/s41746-018-0070-0
- PDF: https://www.nature.com/articles/s41746-018-0070-0.pdf

One broad goal of biomedical informatics is to generate fully-synthetic, faithfully representative electronic health records (EHRs) to facilitate data sharing between healthcare providers and researchers and promote methodological research. A variety of methods existing for generating synthetic EHRs, but they are not capable of generating unstructured text, like emergency department (ED) chief complaints, history of present illness, or progress notes. Here, we use the encoder-decoder model, a deep learning algorithm that features in many contemporary machine translation systems, to generate synthetic chief complaints from discrete variables in EHRs, like age group, gender, and discharge diagnosis. After being trained end-to-end on authentic records, the model can generate realistic chief complaint text that appears to preserve the epidemiological information encoded in the original record-sentence pairs. As a side effect of the model's optimization goal, these synthetic chief complaints are also free of relatively uncommon abbreviation and misspellings, and they include none of the personally identifiable information (PII) that was in the training data, suggesting that this model may be used to support the de-identification of text in EHRs. When combined with algorithms like generative adversarial networks (GANs), our model could be used to generate fully-synthetic EHRs, allowing healthcare providers to share faithful representations of multimodal medical data without compromising patient privacy. This is an important advance that we hope will facilitate the development of machine-learning methods for clinical decision support, disease surveillance, and other data-hungry applications in biomedical informatics.

## 174. Leveraging Generative AI Models for Synthetic Data Generation in Healthcare: Balancing Research and Privacy

- Authors: Aryan Jadon; Shashank Kumar
- Year: 2023
- DOI: 10.1109/smartnets58706.2023.10215825
- Venue: 
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1109/smartnets58706.2023.10215825

The widespread adoption of electronic health records and digital healthcare data has created a demand for data-driven insights to enhance patient outcomes, diagnostics, and treatments. However, using real patient data presents privacy and regulatory challenges, including compliance with HIPAA [1] and GDPR [2]. Synthetic data generation, using generative AI models like GANs [3] and VAEs [4], offers a promising solution to balance valuable data access and patient privacy protection. In this paper, we examine generative AI models for creating realistic, anonymized patient data for research and training [5], explore synthetic data applications in healthcare, and discuss its benefits, challenges, and future research directions. Synthetic data has the potential to revolutionize healthcare by providing anonymized patient data while preserving privacy and enabling versatile applications.

## 175. SMOOTH-GAN: Towards Sharp and Smooth Synthetic EHR Data Generation

- Authors: Sina Rashidian; Fusheng Wang; Richard A. Moffitt; Víctor García; Anurag Dutt; Wei Chang; Vishwam Pandya; Janos Hajagos; Mary Saltz; Joel Saltz
- Year: 2020
- DOI: 10.1007/978-3-030-59137-3_4
- Venue: Lecture notes in computer science
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1007/978-3-030-59137-3_4

## 176. Generating sequential electronic health records using dual adversarial autoencoder

- Authors: Dongha Lee; Hwanjo Yu; Xiaoqian Jiang; Deevakar Rogith; Meghana Gudala; Mubeen Tejani; Qiuchen Zhang; Li Xiong
- Year: 2020
- DOI: 10.1093/jamia/ocaa119
- Venue: Journal of the American Medical Informatics Association
- Countries: KR; US
- Source: openalex
- URL: https://doi.org/10.1093/jamia/ocaa119
- PDF: https://www.ncbi.nlm.nih.gov/pmc/articles/7647348

OBJECTIVE: Recent studies on electronic health records (EHRs) started to learn deep generative models and synthesize a huge amount of realistic records, in order to address significant privacy issues surrounding the EHR. However, most of them only focus on structured records about patients' independent visits, rather than on chronological clinical records. In this article, we aim to learn and synthesize realistic sequences of EHRs based on the generative autoencoder. MATERIALS AND METHODS: We propose a dual adversarial autoencoder (DAAE), which learns set-valued sequences of medical entities, by combining a recurrent autoencoder with 2 generative adversarial networks (GANs). DAAE improves the mode coverage and quality of generated sequences by adversarially learning both the continuous latent distribution and the discrete data distribution. Using the MIMIC-III (Medical Information Mart for Intensive Care-III) and UT Physicians clinical databases, we evaluated the performances of DAAE in terms of predictive modeling, plausibility, and privacy preservation. RESULTS: Our generated sequences of EHRs showed the comparable performances to real data for a predictive modeling task, and achieved the best score in plausibility evaluation conducted by medical experts among all baseline models. In addition, differentially private optimization of our model enables to generate synthetic sequences without increasing the privacy leakage of patients' data. CONCLUSIONS: DAAE can effectively synthesize sequential EHRs by addressing its main challenges: the synthetic records should be realistic enough not to be distinguished from the real records, and they should cover all the training patients to reproduce the performance of specific downstream tasks.

## 177. Continuous Patient-Centric Sequence Generation via Sequentially Coupled Adversarial Learning

- Authors: Lu Wang; Wei Zhang; Xiaofeng He
- Year: 2019
- DOI: 10.1007/978-3-030-18579-4_3
- Venue: Lecture notes in computer science
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1007/978-3-030-18579-4_3

## 178. Generating Synthetic Electronic Health Record Data Using Generative Adversarial Networks: Tutorial

- Authors: Chao Yan; Ziqi Zhang; Steve Nyemba; Zhuohang Li
- Year: 2024
- DOI: 10.2196/52615
- Venue: JMIR AI
- Countries: US
- Source: openalex
- URL: https://doi.org/10.2196/52615
- PDF: https://doi.org/10.2196/52615

Synthetic electronic health record (EHR) data generation has been increasingly recognized as an important solution to expand the accessibility and maximize the value of private health data on a large scale. Recent advances in machine learning have facilitated more accurate modeling for complex and high-dimensional data, thereby greatly enhancing the data quality of synthetic EHR data. Among various approaches, generative adversarial networks (GANs) have become the main technical path in the literature due to their ability to capture the statistical characteristics of real data. However, there is a scarcity of detailed guidance within the domain regarding the development procedures of synthetic EHR data. The objective of this tutorial is to present a transparent and reproducible process for generating structured synthetic EHR data using a publicly accessible EHR data set as an example. We cover the topics of GAN architecture, EHR data types and representation, data preprocessing, GAN training, synthetic data generation and postprocessing, and data quality evaluation. We conclude this tutorial by discussing multiple important issues and future opportunities in this domain. The source code of the entire process has been made publicly available.

## 179. Generative Adversarial Networks for Electronic Health Records: A Framework for Exploring and Evaluating Methods for Predicting Drug-Induced Laboratory Test Trajectories

- Authors: Alexandre Yahi; R. Vanguri; Noémie Elhadad; Nicholas P. Tatonetti
- Year: 2017
- DOI: 10.48550/arxiv.1712.00164
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1712.00164
- PDF: https://arxiv.org/pdf/1712.00164

Generative Adversarial Networks (GANs) represent a promising class of generative networks that combine neural networks with game theory. From generating realistic images and videos to assisting musical creation, GANs are transforming many fields of arts and sciences. However, their application to healthcare has not been fully realized, more specifically in generating electronic health records (EHR) data. In this paper, we propose a framework for exploring the value of GANs in the context of continuous laboratory time series data. We devise an unsupervised evaluation method that measures the predictive power of synthetic laboratory test time series. Further, we show that when it comes to predicting the impact of drug exposure on laboratory test data, incorporating representation learning of the training cohorts prior to training GAN models is beneficial.

## 180. Multi-Label Clinical Time-Series Generation via Conditional GAN

- Authors: Chang Lü; Chandan K. Reddy; Ping Wang; Dong Nie; Yue Ning
- Year: 2023
- DOI: 10.1109/tkde.2023.3310909
- Venue: IEEE Transactions on Knowledge and Data Engineering
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1109/tkde.2023.3310909

In recent years, deep learning has been successfully adopted in a wide range of applications related to electronic health records (EHRs) such as representation learning and clinical event prediction. However, due to privacy constraints, limited access to EHR becomes a bottleneck for deep learning research. To mitigate these concerns, generative adversarial networks (GANs) have been successfully used for generating EHR data. However, there are still challenges in high-quality EHR generation, including generating time-series EHR data and imbalanced uncommon diseases. In this work, we propose a <bold xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">M</b> ulti-label <bold xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">T</b> ime-series <bold xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">GAN</b> (MTGAN) to generate EHR and simultaneously improve the quality of uncommon disease generation. The generator of MTGAN uses a gated recurrent unit (GRU) with a smooth conditional matrix to generate sequences and uncommon diseases. The critic gives scores using Wasserstein distance to recognize real samples from synthetic samples by considering both data and temporal features. We also propose a training strategy to calculate temporal features for real data and stabilize GAN training. Furthermore, we design multiple statistical metrics and prediction tasks to evaluate the generated data. Experimental results demonstrate the quality of the synthetic data and the effectiveness of MTGAN in generating realistic sequential EHR data, especially for uncommon diseases.

## 181. CorGAN: Correlation-Capturing Convolutional Generative Adversarial\n Networks for Generating Synthetic Healthcare Records

- Authors: Amirsina Torfi; Edward A. Fox
- Year: 2020
- DOI: 10.48550/arxiv.2001.09346
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2001.09346
- PDF: https://arxiv.org/pdf/2001.09346

Deep learning models have demonstrated high-quality performance in areas such\nas image classification and speech processing. However, creating a deep\nlearning model using electronic health record (EHR) data, requires addressing\nparticular privacy challenges that are unique to researchers in this domain.\nThis matter focuses attention on generating realistic synthetic data while\nensuring privacy. In this paper, we propose a novel framework called\ncorrelation-capturing Generative Adversarial Network (CorGAN), to generate\nsynthetic healthcare records. In CorGAN we utilize Convolutional Neural\nNetworks to capture the correlations between adjacent medical features in the\ndata representation space by combining Convolutional Generative Adversarial\nNetworks and Convolutional Autoencoders. To demonstrate the model fidelity, we\nshow that CorGAN generates synthetic data with performance similar to that of\nreal data in various Machine Learning settings such as classification and\nprediction. We also give a privacy assessment and report on statistical\nanalysis regarding realistic characteristics of the synthetic data. The\nsoftware of this work is open-source and is available at:\nhttps://github.com/astorfi/cor-gan.\n

## 182. A review of Generative Adversarial Networks for Electronic Health Records: applications, evaluation measures and data sources

- Authors: Ghadeer Ghosheh; Jin Li; Tingting Zhu
- Year: 2022
- DOI: 10.48550/arxiv.2203.07018
- Venue: arXiv (Cornell University)
- Countries: GB
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2203.07018
- PDF: https://arxiv.org/pdf/2203.07018

Electronic Health Records (EHRs) are a valuable asset to facilitate clinical research and point of care applications; however, many challenges such as data privacy concerns impede its optimal utilization. Deep generative models, particularly, Generative Adversarial Networks (GANs) show great promise in generating synthetic EHR data by learning underlying data distributions while achieving excellent performance and addressing these challenges. This work aims to review the major developments in various applications of GANs for EHRs and provides an overview of the proposed methodologies. For this purpose, we combine perspectives from healthcare applications and machine learning techniques in terms of source datasets and the fidelity and privacy evaluation of the generated synthetic datasets. We also compile a list of the metrics and datasets used by the reviewed works, which can be utilized as benchmarks for future research in the field. We conclude by discussing challenges in GANs for EHRs development and proposing recommended practices. We hope that this work motivates novel research development directions in the intersection of healthcare and machine learning.

## 183. Bt-GAN: Generating Fair Synthetic Healthdata via Bias-transforming Generative Adversarial Networks

- Authors: Resmi Ramachandranpillai; Md Fahim Sikder; David Bergström; Fredrik Heintz
- Year: 2024
- DOI: 10.1613/jair.1.15317
- Venue: Journal of Artificial Intelligence Research
- Countries: SE; US
- Source: openalex
- URL: https://doi.org/10.1613/jair.1.15317
- PDF: https://jair.org/index.php/jair/article/download/15317/27031

Synthetic data generation offers a promising solution to enhance the usefulness of Electronic Healthcare Records (EHR) by generating realistic de-identified data. However, the existing literature primarily focuses on the quality of synthetic health data, neglecting the crucial aspect of fairness in downstream predictions. Consequently, models trained on synthetic EHR have faced criticism for producing biased outcomes in target tasks. These biases can arise from either spurious correlations between features or the failure of models to accurately represent sub-groups. To address these concerns, we present Bias-transforming Generative Adversarial Networks (Bt-GAN), a GAN-based synthetic data generator specifically designed for the healthcare domain. In order to tackle spurious correlations (i), we propose an information-constrained Data Generation Process (DGP) that enables the generator to learn a fair deterministic transformation based on a well-defined notion of algorithmic fairness. To overcome the challenge of capturing exact sub-group representations (ii), we incentivize the generator to preserve sub-group densities through score-based weighted sampling. This approach compels the generator to learn from underrepresented regions of the data manifold. To evaluate the effectiveness of our proposed method, we conduct extensive experiments using the Medical Information Mart for Intensive Care (MIMIC-III) database. Our results demonstrate that Bt-GAN achieves state-of-the-art accuracy while significantly improving fairness and minimizing bias amplification. Furthermore, we perform an in-depth explainability analysis to provide additional evidence supporting the validity of our study. In conclusion, our research introduces a novel and professional approach to addressing the limitations of synthetic data generation in the healthcare domain. By incorporating fairness considerations and leveraging advanced techniques such as GANs, we pave the way for more reliable and unbiased predictions in healthcare applications.

## 184. Natural Language Generation for Electronic Health Records

- Authors: Scott Lee
- Year: 2018
- DOI: 10.48550/arxiv.1806.01353
- Venue: arXiv (Cornell University)
- Countries: US
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1806.01353
- PDF: https://doi.org/10.48550/arxiv.1806.01353

A variety of methods existing for generating synthetic electronic health records (EHRs), but they are not capable of generating unstructured text, like emergency department (ED) chief complaints, history of present illness or progress notes. Here, we use the encoder-decoder model, a deep learning algorithm that features in many contemporary machine translation systems, to generate synthetic chief complaints from discrete variables in EHRs, like age group, gender, and discharge diagnosis. After being trained end-to-end on authentic records, the model can generate realistic chief complaint text that preserves much of the epidemiological information in the original data. As a side effect of the model's optimization goal, these synthetic chief complaints are also free of relatively uncommon abbreviation and misspellings, and they include none of the personally-identifiable information (PII) that was in the training data, suggesting it may be used to support the de-identification of text in EHRs. When combined with algorithms like generative adversarial networks (GANs), our model could be used to generate fully-synthetic EHRs, facilitating data sharing between healthcare providers and researchers and improving our ability to develop machine learning methods tailored to the information in healthcare data.

## 185. Propensity score synthetic augmentation matching using generative adversarial networks (PSSAM-GAN)

- Authors: Shantanu Ghosh; Christina Boucher; Jiang Bian; Mattia Prosperi
- Year: 2021
- DOI: 10.1016/j.cmpbup.2021.100020
- Venue: Computer Methods and Programs in Biomedicine Update
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1016/j.cmpbup.2021.100020
- PDF: https://doi.org/10.1016/j.cmpbup.2021.100020

Understanding causality is of crucial importance in biomedical sciences, where developing prediction models is insufficient because the models need to be actionable. However, data sources, such as electronic health records, are observational and often plagued with various types of biases, e.g. confounding. Although randomized controlled trials are the gold standard to estimate the causal effects of treatment interventions on health outcomes, they are not always possible. Propensity score matching (PSM) is a popular statistical technique for observational data that aims at balancing the characteristics of the population assigned either to a treatment or to a control group, making treatment assignment and outcome independent upon these characteristics. However, matching subjects can reduce the sample size. Inverse probability weighting (IPW) maintains the sample size, but extreme values can lead to instability. While PSM and IPW have been historically used in conjunction with linear regression, machine learning methods -including deep learning with propensity dropout- have been proposed to account for nonlinear treatment assignments. In this work, we propose a novel deep learning approach -the Propensity Score Synthetic Augmentation Matching using Generative Adversarial Networks (PSSAM-GAN)- that aims at keeping the sample size, without IPW, by generating synthetic matches. PSSAM-GAN can be used in conjunction with any other prediction method to estimate treatment effects. Experiments performed on both semi-synthetic (perinatal interventions) and real-world observational data (antibiotic treatments, and job interventions) show that the PSSAM-GAN approach effectively creates balanced datasets, relaxing the weighting/dropout needs for downstream methods, and providing competitive performance in effects estimation as compared to simple GAN and in conjunction with other deep counterfactual learning architectures, e.g. TARNet.

## 186. Realistic Data Synthesis Using Enhanced Generative Adversarial Networks

- Authors: Mrinal Kanti Baowaly; Chao-Lin Liu; Kuan-Ta Chen
- Year: 2019
- DOI: 10.1109/aike.2019.00057
- Venue: 
- Countries: TW
- Source: openalex
- URL: https://doi.org/10.1109/aike.2019.00057

Real data with privacy and confidentiality concerns are not often available or are too expensive to afford in respect of both time and money. In this situation, it is a good alternative to use synthetic data. The objective of this research is to generate realistic synthetic data so that people can use it freely. We propose a synthetic data generation model based on boundary-seeking generative adversarial networks (BGANs)-designated as medical BGAN or medBGAN and compare its performances with an existing method medical GAN (medGAN). We aim to perform the investigation on several datasets in two different domains: electronic health records (EHRs) in the medical domain and a crime dataset in the City of Los Angeles Police Department. Firstly, we train the models and generate synthetic data by using these trained models. We then analyze and compare the models' performance by applying some statistical methods (dimension-wise average and Kolmogorov-Smirnov test) and two machine learning tasks (association rule mining and prediction). The comprehensive analysis of this study shows that the proposed model is more efficient in generating realistic synthetic data than those generated using medGAN.

## 187. Generating Longitudinal Synthetic EHR Data with Recurrent Autoencoders and Generative Adversarial Networks

- Authors: Siao Sun; Fusheng Wang; Sina Rashidian; Tahsin Kurç; Kayley Abell-Hart; Janos Hajagos; Wei Zhu; Mary Saltz; Joel Saltz
- Year: 2021
- DOI: 10.1007/978-3-030-93663-1_12
- Venue: Lecture notes in computer science
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1007/978-3-030-93663-1_12

## 188. Grouped Correlational Generative Adversarial Networks for Discrete Electronic Health Records

- Authors: Fan Yang; Zhongping Yu; Yunfan Liang; Xiaolu Gan; Kaibiao Lin; Quan Zou; Yifeng Zeng
- Year: 2019
- DOI: 10.1109/bibm47256.2019.8983215
- Venue: 
- Countries: CH; CN; GB
- Source: openalex
- URL: https://doi.org/10.1109/bibm47256.2019.8983215

Using Generative Adversarial Networks (GANs) to generate synthetic Electronic Health Records (EHR) has attracted increasing attention. However, in existing approaches, the events in EHRs are treated as separate variables which are indiscriminately entered into the model, without taking into account the meaning and grouping of them. Besides, the efficacy of treatment is often neglected. In this paper, we first embed the efficacy information into the disease diagnosis, and then propose Grouped Correlational GAN (GcGAN) to explicitly learn inherent correlations between different groups of variables. We also introduce a dense connection to strengthen the generator capacity in GcGAN. Experimental results on real-world data demonstrate that the generated data from GcGAN are able to simulate real-world data in terms of distribution statistics. The results on multi-label treatment recommendation tasks show that GcGAN can boost the performances by augmenting the training dataset with the generated data and outperforms state-of-the-art approaches. It can also automatically distinguish between disease-specific drugs and adjuvant drugs, which enhances the model interpretability.

## 189. Generating unseen diseases patient data using ontology enhanced generative adversarial networks

- Authors: Chang Sun; Michel Dumontier
- Year: 2025
- DOI: 10.1038/s41746-024-01421-0
- Venue: npj Digital Medicine
- Countries: NL
- Source: openalex
- URL: https://doi.org/10.1038/s41746-024-01421-0
- PDF: https://www.nature.com/articles/s41746-024-01421-0.pdf

Generating realistic synthetic health data (e.g., electronic health records), holds promise for fundamental research, AI model development, and enhancing data privacy safeguards. Generative Adversarial Networks (GANs) have been employed for this purpose, but their performance is largely constrained by their reliance on training data, rendering them inadequate for rare or previously unseen diseases. This study proposes Onto-CGAN, a novel generative framework that combines knowledge from disease ontologies with GANs to generate unseen diseases that are not present in the training data. The quality of the generated data is evaluated using variable distributions, correlation coefficients, and machine learning model performance. Our findings demonstrate that Onto-CGAN generates unseen diseases with statistical characteristics comparable to the real data, and significantly improves the training of machine learning models. This innovative approach addresses the scarcity of data for rare diseases, offering valuable applications in data augmentation, hypothesis generation, and preclinical validation of clinical models.

## 190. Leveraging Generative AI Models for Synthetic Data Generation in Healthcare: Balancing Research and Privacy

- Authors: Aryan Jadon; Shashank Kumar
- Year: 2023
- DOI: 10.48550/arxiv.2305.05247
- Venue: arXiv (Cornell University)
- Countries: US
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2305.05247
- PDF: https://arxiv.org/pdf/2305.05247

The widespread adoption of electronic health records and digital healthcare data has created a demand for data-driven insights to enhance patient outcomes, diagnostics, and treatments. However, using real patient data presents privacy and regulatory challenges, including compliance with HIPAA and GDPR. Synthetic data generation, using generative AI models like GANs and VAEs offers a promising solution to balance valuable data access and patient privacy protection. In this paper, we examine generative AI models for creating realistic, anonymized patient data for research and training, explore synthetic data applications in healthcare, and discuss its benefits, challenges, and future research directions. Synthetic data has the potential to revolutionize healthcare by providing anonymized patient data while preserving privacy and enabling versatile applications.

## 191. MedDiffusion: Boosting Health Risk Prediction via Diffusion-based Data Augmentation

- Authors: Yuan Zhong; Suhan Cui; Jiaqi Wang; Xiaochen Wang; Ziyi Yin; Yaqing Wang; Houping Xiao; Mengdi Huai; Ting Wang; Fenglong Ma
- Year: 2024
- DOI: 10.1137/1.9781611978032.58
- Venue: Society for Industrial and Applied Mathematics eBooks
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1137/1.9781611978032.58
- PDF: https://pmc.ncbi.nlm.nih.gov/articles/PMC11469648/pdf/nihms-1982402.pdf

Health risk prediction aims to forecast the potential health risks that patients may face using their historical Electronic Health Records (EHR). Although several effective models have developed, data insufficiency is a key issue undermining their effectiveness. Various data generation and augmentation methods have been introduced to mitigate this issue by expanding the size of the training data set through learning underlying data distributions. However, the performance of these methods is often limited due to their task-unrelated design. To address these shortcomings, this paper introduces a novel, end-to-end diffusion-based risk prediction model, named MedDiffusion. It enhances risk prediction performance by creating synthetic patient data during training to enlarge sample space. Furthermore, MedDiffusion discerns hidden relationships between patient visits using a step-wise attention mechanism, enabling the model to automatically retain the most vital information for generating high-quality data. Experimental evaluation on four real-world medical datasets demonstrates that MedDiffusion outperforms 14 cutting-edge baselines in terms of PR-AUC, F1, and Cohen's Kappa. We also conduct ablation studies and benchmark our model against GAN-based alternatives to further validate the rationality and adaptability of our model design. Additionally, we analyze generated data to offer fresh insights into the model's interpretability. The source code is available via https://shorturl.at/aerT0.

## 192. Synthetic Health-related Longitudinal Data with Mixed-type Variables Generated using Diffusion Models

- Authors: Nicholas I-Hsien Kuo; Louisa Jorm; Sebastiano Barbieri
- Year: 2023
- DOI: 10.48550/arxiv.2303.12281
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2303.12281
- PDF: https://arxiv.org/pdf/2303.12281

This paper presents a novel approach to simulating electronic health records (EHRs) using diffusion probabilistic models (DPMs). Specifically, we demonstrate the effectiveness of DPMs in synthesising longitudinal EHRs that capture mixed-type variables, including numeric, binary, and categorical variables. To our knowledge, this represents the first use of DPMs for this purpose. We compared our DPM-simulated datasets to previous state-of-the-art results based on generative adversarial networks (GANs) for two clinical applications: acute hypotension and human immunodeficiency virus (ART for HIV). Given the lack of similar previous studies in DPMs, a core component of our work involves exploring the advantages and caveats of employing DPMs across a wide range of aspects. In addition to assessing the realism of the synthetic datasets, we also trained reinforcement learning (RL) agents on the synthetic data to evaluate their utility for supporting the development of downstream machine learning models. Finally, we estimated that our DPM-simulated datasets are secure and posed a low patient exposure risk for public access.

## 193. A Multifaceted Benchmarking of Synthetic Electronic Health Record Generation Models

- Authors: Chao Yan; Yan Yao; Zhiyu Wan; Ziqi Zhang; Larsson Omberg; Justin Guinney; Sean D. Mooney; Bradley Malin
- Year: 2022
- DOI: 10.48550/arxiv.2208.01230
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2208.01230
- PDF: https://arxiv.org/pdf/2208.01230

Synthetic health data have the potential to mitigate privacy concerns when sharing data to support biomedical research and the development of innovative healthcare applications. Modern approaches for data generation based on machine learning, generative adversarial networks (GAN) methods in particular, continue to evolve and demonstrate remarkable potential. Yet there is a lack of a systematic assessment framework to benchmark methods as they emerge and determine which methods are most appropriate for which use cases. In this work, we introduce a generalizable benchmarking framework to appraise key characteristics of synthetic health data with respect to utility and privacy metrics. We apply the framework to evaluate synthetic data generation methods for electronic health records (EHRs) data from two large academic medical centers with respect to several use cases. The results illustrate that there is a utility-privacy tradeoff for sharing synthetic EHR data. The results further indicate that no method is unequivocally the best on all criteria in each use case, which makes it evident why synthetic data generation methods need to be assessed in context.

## 194. Multi-Label Clinical Time-Series Generation via Conditional GAN

- Authors: Chang Lü; Chandan K. Reddy; Ping Wang; Dong Nie; Yue Ning
- Year: 2022
- DOI: 10.48550/arxiv.2204.04797
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2204.04797
- PDF: https://arxiv.org/pdf/2204.04797

In recent years, deep learning has been successfully adopted in a wide range of applications related to electronic health records (EHRs) such as representation learning and clinical event prediction. However, due to privacy constraints, limited access to EHR becomes a bottleneck for deep learning research. To mitigate these concerns, generative adversarial networks (GANs) have been successfully used for generating EHR data. However, there are still challenges in high-quality EHR generation, including generating time-series EHR data and imbalanced uncommon diseases. In this work, we propose a Multi-label Time-series GAN (MTGAN) to generate EHR and simultaneously improve the quality of uncommon disease generation. The generator of MTGAN uses a gated recurrent unit (GRU) with a smooth conditional matrix to generate sequences and uncommon diseases. The critic gives scores using Wasserstein distance to recognize real samples from synthetic samples by considering both data and temporal features. We also propose a training strategy to calculate temporal features for real data and stabilize GAN training. Furthermore, we design multiple statistical metrics and prediction tasks to evaluate the generated data. Experimental results demonstrate the quality of the synthetic data and the effectiveness of MTGAN in generating realistic sequential EHR data, especially for uncommon diseases.

## 195. Computationally efficient and stable real-world synthetic emergency room electronic health record data generation: high similarity and privacy preserving diffusion model approach: A retrospective cohort study

- Authors: Javier Aguirre; Jae Yong Yu; Kyu-Hwan Jung; Jinsung Yoon; Won Chul
- Year: 2024
- DOI: 10.23838/pfm.2024.00030
- Venue: Precision and Future Medicine
- Countries: KR; US
- Source: openalex
- URL: https://doi.org/10.23838/pfm.2024.00030
- PDF: https://www.pfmjournal.org/upload/pdf/pfm-2024-00030.pdf

Purpose: This study aimed to develop real-world synthetic electronic health record (EHR) for emergency departments using computationally efficient and stable diffusion probabilistic models. Methods: In this study, we compared the performance of diffusion models and state-ofthe-art generative adversarial networks (GANs) in terms of statistical similarity, privacy, medical usefulness, and the feasibility of using synthetic data for machine learning purposes.Results: Our results demonstrate that diffusion models are significantly more computationally efficient than GANs and perform comparably or slightly better in terms of similarity, privacy, and utility. We also found that the data quality of the diffusion model is statistically very similar for both categorical and continuous values and can address class imbalance precisely. Moreover, the usefulness of synthetic data is almost identical to that of real EHR data. Our privacy analysis showed that the synthetic data generated by the diffusion models were private.Conclusion: These findings have significant implications for improving the efficiency of emergency settings and enabling real-time emergency room data modeling. This demonstrates the potential of diffusion models for generating computationally efficient high-quality synthetic data. The study concluded that diffusion models can generate real-world synthetic EHRs that are computationally efficient, private, and high-quality, and can be used for machine learning purposes in emergency settings.

## 196. Generative AI in clinical (2020–2025): a mini-review of applications, emerging trends, and clinical challenges

- Authors: Nafiz Fahad; Riadul Islam Rabbi; Sumayea Benta Hasan; Fariya Sultana Prity; Rasel Ahmed; Farhana Ahmed; Md. Jakir Hossen; Tze Hui Liew; Md Shohel Sayeed; Michael Kah Ong Goh
- Year: 2025
- DOI: 10.3389/fdgth.2025.1653369
- Venue: Frontiers in Digital Health
- Countries: BD; CN; MY
- Source: openalex
- URL: https://doi.org/10.3389/fdgth.2025.1653369
- PDF: https://public-pages-files-2025.frontiersin.org/journals/digital-health/articles/10.3389/fdgth.2025.1653369/pdf

Generative artificial intelligence (G-AI) has moved from proof-of-concept demonstrations to practical tools that augment radiology, dermatology, genetics, drug discovery, and electronic-health-record analysis. This mini-review synthesizes fifteen studies published between 2020 and 2025 that collectively illustrate three dominant trends: data augmentation for imbalanced or privacy-restricted datasets, automation of expert-intensive tasks such as radiology reporting, and generation of new biomedical knowledge ranging from molecular scaffolds to fairness insights. Image-centric work still dominates, with GANs, diffusion models, and Vision-Language Models expanding limited datasets and accelerating diagnosis. Yet narrative (EHR) and molecular design domains are rapidly catching up. Despite demonstrated accuracy gains, recurring challenges persist: synthetic samples may overlook rare pathologies, large multimodal systems can hallucinate clinical facts, and demographic biases can be amplified. Robust validation, interpretability techniques, and governance frameworks therefore, remain essential before G-AI can be safely embedded in routine care.

## 197. AUGMENTED AND SYNTHETIC DATA IN ARTIFICIAL INTELLIGENCE

- Authors: Philip de Melo
- Year: 2025
- DOI: 10.5121/ijaia.2025.16307
- Venue: International Journal of Artificial Intelligence & Applications
- Countries: US
- Source: openalex
- URL: https://doi.org/10.5121/ijaia.2025.16307
- PDF: https://doi.org/10.5121/ijaia.2025.16307

High-quality data is essential for hospitals, public health agencies, and governments to improve services, train AI models, and boost efficiency. However, real data comes with challenges: strict privacy laws, high storage costs, legal constraints, and issues like bias or incompleteness. These can reduce the reliability of AI systems. As a result, artificial datasets are gaining importance. Synthetic and augmented data offer alternatives, yet their differences and potential are not fully understood. This paper examines how both types of data are generated and used, showcasing their characteristics through practical examples. Data generation techniques—such as Gaussian Mixture Models (GMM), Generative Adversarial Networks (GANs), and Gibbs sampling—enable the creation of realistic, privacy-preserving patient records that mimic the statistical properties of real data. Data augmentation, commonly used in image and signal analysis, is increasingly applied to structured electronic health records (EHRs), laboratory values, and time-series data to enhance model robustness and generalizability. This paper explores mathematical foundations, methodological frameworks, and real-world applications of synthetic and augmented data in healthcare. We highlight how these techniques improve disease prediction, mitigate bias, and enable high-performance machine learning models, particularly in lowresource or imbalanced clinical domains. By expanding the effective size and diversity of training datasets, synthetic and augmented data serve as critical enablers for equitable, scalable, and data-driven healthcare systems.

## 198. Subpopulation-Specific Synthetic EHR for Better Mortality Prediction

- Authors: Oriel Perets; Nadav Rappoport
- Year: 2023
- DOI: 10.48550/arxiv.2305.16363
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2305.16363
- PDF: https://arxiv.org/pdf/2305.16363

Electronic health records (EHR) often contain different rates of representation of certain subpopulations (SP). Factors like patient demographics, clinical condition prevalence, and medical center type contribute to this underrepresentation. Consequently, when training machine learning models on such datasets, the models struggle to generalize well and perform poorly on underrepresented SPs. To address this issue, we propose a novel ensemble framework that utilizes generative models. Specifically, we train a GAN-based synthetic data generator for each SP and incorporate synthetic samples into each SP training set. Ultimately, we train SP-specific prediction models. To properly evaluate this method, we design an evaluation pipeline with 2 real-world use case datasets, queried from the MIMIC database. Our approach shows increased model performance over underrepresented SPs. Our code and models are given as supplementary and will be made available on a public repository.

## 199. Deploying Secure and Interpretable Medical AI Models on Edge Devices: A 6G-Enabled FL-GAN Framework

- Authors: N. Meenakshisundaram; G. Sajiv
- Year: 2025
- DOI: 10.1109/icesc65114.2025.11212235
- Venue: 
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.1109/icesc65114.2025.11212235

Next-generation healthcare demands real-time, privacy-preserving, and interpretable AI solutions capable of functioning efficiently on edge devices. A novel 6G-enabled Federated Learning-Generative Adversarial Network (FLGAN) framework is proposed that integrates fuzzy logic, blockchain, and explainable AI to enhance diagnostic accuracy, data security, and transparency in medical AI systems. The architecture is designed to operate across distributed edge environments such as wearable devices, hospital servers, and research laboratories, enabling seamless integration of multimodal healthcare data including electronic health records (EHRs), medical images, and genomic profiles. Conditional GANs are employed for synthetic augmentation of underrepresented clinical cases, while federated learning ensures that sensitive patient data remains localized to each institution. Blockchain provides secure and tamper-proof logging of AI model updates, and SHAP-based explainability modules deliver interpretable risk factor insights for clinicians. Experimental validation using three benchmark datasets-MIMIC-III (EHR), ChestX-ray14 (imaging), and GSE96058 (genomics)-demonstrates superiority in model robustness, fairness, and scalability. This framework paves the way for deploying trustworthy and intelligent medical AI applications over future 6 G infrastructures, thereby advancing personalized and decentralized digital health systems.

## 200. Multimodal Fusion for AI-Driven Healthcare: Integrating Genomic, EHR, and Wearable Sensor Data in a Federated 6G Framework with Explainable AI

- Authors: M. Archana; Jarina Raihan A; B. Jothilakshmi; C. Parthasarathy; T. Dinesh Kumar; T. Lakshmibai
- Year: 2025
- DOI: 10.1109/icimia67127.2025.11200547
- Venue: 
- Countries: BN; IN
- Source: openalex
- URL: https://doi.org/10.1109/icimia67127.2025.11200547

The convergence of artificial intelligence (AI) and multimodal healthcare data is transforming proactive and precision medicine by enabling more comprehensive, timely, and personalized care. This paper presents a novel framework that integrates genomic data, electronic health records (EHRs), and real-time wearable sensor data within a federated, 6G-enabled infrastructure to facilitate decentralized and privacy-preserving health intelligence. The proposed approach employs transformer-based attention mechanisms to achieve effective modality alignment, while generative adversarial networks (GANs) are used for synthetic multimodal data augmentation, thereby improving the robustness, diversity, and generalizability of disease prediction models. To enhance trust and transparency, explainable AI (XAI) techniques, including SHAP value analysis and attention visualizations, are incorporated to quantify feature importance across modalities and provide actionable insights for clinical decision-making. The framework is evaluated using a multimodal health dataset targeting early cardiovascular disease detection, achieving superior results in accuracy, latency, interpretability, and cross-device compatibility. This work contributes a scalable, secure, and interpretable AI pipeline that addresses performance, privacy, and interoperability requirements of next-generation 6G healthcare systems.

## 201. Generating synthetic electronic health record data: a methodological scoping review with benchmarking on phenotype data and open-source software

- Authors: Xingran Chen; Zhenke Wu; Xu Shi; Hyunghoon Cho; Bhramar Mukherjee
- Year: 2025
- DOI: 10.1093/jamia/ocaf082
- Venue: Journal of the American Medical Informatics Association
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1093/jamia/ocaf082
- PDF: https://arxiv.org/pdf/2411.04281

OBJECTIVES: To conduct a scoping review (ScR) of existing approaches for synthetic Electronic Health Records (EHR) data generation, to benchmark major methods, and to provide an open-source software and offer recommendations for practitioners. MATERIALS AND METHODS: We search three academic databases for our scoping review. Methods are benchmarked on open-source EHR datasets, Medical Information Mart for Intensive Care III and IV (MIMIC-III/IV). Seven existing methods covering major categories and two baseline methods are implemented and compared. Evaluation metrics concern data fidelity, downstream utility, privacy protection, and computational cost. RESULTS: Forty-eight studies are identified and classified into five categories. Seven open-source methods covering all categories are selected, trained on MIMIC-III, and evaluated on MIMIC-III or MIMIC-IV for transportability considerations. Among them, Generative Adversarial Network (GAN)-based methods demonstrate competitive performance in fidelity and utility on MIMIC-III, rule-based methods excel in privacy protection. Similar findings are observed on MIMIC-IV, except that GAN-based methods further outperform the baseline methods in preserving fidelity. DISCUSSION: Method choice is governed by the relative importance of the evaluation metrics in downstream use cases. We provide a decision tree to guide the choice among the benchmarked methods. An extensible Python package, "SynthEHRella", is provided to facilitate streamlined evaluations. CONCLUSION: GAN-based methods excel when distributional shifts exist between the training and testing populations. Otherwise, CorGAN and MedGAN are most suitable for association modeling and predictive modeling, respectively. Future research should prioritize enhancing fidelity of the synthetic data while controlling privacy exposure, and comprehensive benchmarking of longitudinal or conditional generation methods.

## 202. Generating Patient’s Electronic Health Records with Unseen Diseases Using Ontology-enhanced Generative Adversarial Networks

- Authors: Chang Sun; Michel Dumontier
- Year: 2024
- DOI: 10.21203/rs.3.rs-5043150/v1
- Venue: Research Square
- Countries: NL
- Source: openalex
- URL: https://doi.org/10.21203/rs.3.rs-5043150/v1
- PDF: https://www.researchsquare.com/article/rs-5043150/latest.pdf

## 203. Key Contributions in Clinical Research Informatics

- Authors: Christel Daniel; Ali Bellamine; Dipak Kalra; Section Editors of the IMIA Yearbook Section on Clinical Research Informatics
- Year: 2021
- DOI: 10.1055/s-0041-1726514
- Venue: Yearbook of Medical Informatics
- Countries: BE; FR
- Source: openalex
- URL: https://doi.org/10.1055/s-0041-1726514
- PDF: http://www.thieme-connect.de/products/ejournals/pdf/10.1055/s-0041-1726514.pdf

OBJECTIVES: To summarize key contributions to current research in the field of Clinical Research Informatics (CRI) and to select best papers published in 2020. METHOD: A bibliographic search using a combination of Medical Subject Headings (MeSH) descriptors and free-text terms on CRI was performed using PubMed, followed by a double-blind review in order to select a list of candidate best papers to be then peer-reviewed by external reviewers. After peer-review ranking, a consensus meeting between two section editors and the editorial team was organized to finally conclude on the selected four best papers. RESULTS: Among the 877 papers published in 2020 and returned by the search, there were four best papers selected. The first best paper describes a method for mining temporal sequences from clinical documents to infer disease trajectories and enhancing high-throughput phenotyping. The authors of the second best paper demonstrate that the generation of synthetic Electronic Health Record (EHR) data through Generative Adversarial Networks (GANs) could be substantially improved by more appropriate training and evaluation criteria. The third best paper offers an efficient advance on methods to detect adverse drug events by computer-assisting expert reviewers with annotated candidate mentions in clinical documents. The large-scale data quality assessment study reported by the fourth best paper has clinical research informatics implications, in terms of the trustworthiness of inferences made from analysing electronic health records. CONCLUSIONS: The most significant research efforts in the CRI field are currently focusing on data science with active research in the development and evaluation of Artificial Intelligence/Machine Learning (AI/ML) algorithms based on ever more intensive use of real-world data and especially EHR real or synthetic data. A major lesson that the coronavirus disease 2019 (COVID-19) pandemic has already taught the scientific CRI community is that timely international high-quality data-sharing and collaborative data analysis is absolutely vital to inform policy decisions.

## 204. Generative AI in Medical Practice: In-Depth Exploration of Privacy and Security Challenges

- Authors: Yan Chen; Pouyan Esmaeilzadeh
- Year: 2024
- DOI: 10.2196/53008
- Venue: Journal of Medical Internet Research
- Countries: US
- Source: openalex
- URL: https://doi.org/10.2196/53008
- PDF: https://www.jmir.org/2024/1/e53008/PDF

As advances in artificial intelligence (AI) continue to transform and revolutionize the field of medicine, understanding the potential uses of generative AI in health care becomes increasingly important. Generative AI, including models such as generative adversarial networks and large language models, shows promise in transforming medical diagnostics, research, treatment planning, and patient care. However, these data-intensive systems pose new threats to protected health information. This Viewpoint paper aims to explore various categories of generative AI in health care, including medical diagnostics, drug discovery, virtual health assistants, medical research, and clinical decision support, while identifying security and privacy threats within each phase of the life cycle of such systems (ie, data collection, model development, and implementation phases). The objectives of this study were to analyze the current state of generative AI in health care, identify opportunities and privacy and security challenges posed by integrating these technologies into existing health care infrastructure, and propose strategies for mitigating security and privacy risks. This study highlights the importance of addressing the security and privacy threats associated with generative AI in health care to ensure the safe and effective use of these systems. The findings of this study can inform the development of future generative AI systems in health care and help health care organizations better understand the potential benefits and risks associated with these systems. By examining the use cases and benefits of generative AI across diverse domains within health care, this paper contributes to theoretical discussions surrounding AI ethics, security vulnerabilities, and data privacy regulations. In addition, this study provides practical insights for stakeholders looking to adopt generative AI solutions within their organizations.

## 205. Computationally Efficient and Stable Real-World Synthetic Emergency Room EHR Data Generation: High Similarity and Privacy Preserving Diffusion Model Approach

- Authors: J. Aguirre; Jae Yong Yu; Kyu-Hwan Jung; Jinsung Yoon; Won Chul Cha
- Year: 2023
- DOI: 10.21203/rs.3.rs-3653078/v1
- Venue: Research Square
- Countries: KR; US
- Source: openalex
- URL: https://doi.org/10.21203/rs.3.rs-3653078/v1
- PDF: https://www.researchsquare.com/article/rs-3653078/latest.pdf

Abstract Objective : This study aims to develop real-world synthetic electronic health record (EHR) for emergency departments using computationally efficient and stable diffusion probabilistic models. Materials and Methods : In this research, we compare the performance of diffusion models and state-of-the-art generative adversarial networks (GANs) in terms of statistical similarity, privacy, medical usefulness, and the feasibility of using the synthetic data for machine learning purposes. Results : Our results demonstrate that diffusion models are significantly more computationally efficient than GANs and perform comparably or slightly better in terms of similarity, privacy, and utility. We also found that the data quality of the diffusion model is statistically very similar for both categorical and continuous values and can address class imbalance precisely. Moreover, the machine learning usefulness of the synthetic data is almost identical to real EHR data. Our privacy analysis shows that the synthetic data generated by diffusion models is private. Discussion : These findings have significant implications for improving the efficiency of emergency settings such as disasters and enabling real-time emergency room data modeling. Therefore, it demonstrates the potential of diffusion models to generate computationally efficient high-quality synthetic data. Conclusion : The study concludes that diffusion models can generate real-world synthetic EHRs that are computationally efficient, private, and high-quality, which can be used for machine learning purposes in emergency settings.

## 206. Generating Synthetic Electronic Health Record Data Using Generative Adversarial Networks: Tutorial (Preprint)

- Authors: Chao Yan; Ziqi Zhang; Steve Nyemba; Zhuohang Li
- Year: 2023
- DOI: 10.2196/preprints.52615
- Venue: 
- Countries: 
- Source: openalex
- URL: https://doi.org/10.2196/preprints.52615
- PDF: http://dx.doi.org/10.2196/preprints.52615

<sec> <title>UNSTRUCTURED</title> Synthetic electronic health record (EHR) data generation has been increasingly recognized as an important solution to expand the accessibility and maximize the value of private health data on a large scale. Recent advances in machine learning have facilitated more accurate modeling for complex and high-dimensional data, thereby greatly enhancing the data quality of synthetic EHR data. Among various approaches, generative adversarial networks (GANs) have become the main technical path in the literature due to their ability to capture the statistical characteristics of real data. However, there is a scarcity of detailed guidance within the domain regarding the development procedures of synthetic EHR data. The objective of this tutorial is to present a transparent and reproducible process for generating structured synthetic EHR data using a publicly accessible EHR data set as an example. We cover the topics of GAN architecture, EHR data types and representation, data preprocessing, GAN training, synthetic data generation and postprocessing, and data quality evaluation. We conclude this tutorial by discussing multiple important issues and future opportunities in this domain. The source code of the entire process has been made publicly available. </sec>

## 207. Electronic Health Data in the Context of Patient Length-of-Stay Prediction: Using Generative Adversarial Nets for Synthetic Data Creation

- Authors: Dominik Bietsch; Robert Stahlbock; Stefan Voß
- Year: 2023
- DOI: 10.1109/csce60160.2023.00262
- Venue: 
- Countries: DE
- Source: openalex
- URL: https://doi.org/10.1109/csce60160.2023.00262

While generative artificial intelligence has gained popularity (e.g., for the creation of images) it can also be used for the creation of synthetic tabular data. This bears great potential, especially for the healthcare industry where data is oftentimes scarce and underlies privacy restrictions. For instance, the creation of synthetic electronic health records (EHR) promises to improve the usage of machine learning (ML) algorithms, which normally work with large amounts of data. This also applies for the prediction of the patient length of stay (LOS), a key measure for hospitals. Thereby, the LOS represents one of the core tools for decision-makers to plan the allocation of resources. This paper aims to add to the young research concerning the application of generative adversarial nets (GAN) on tabular EHR. The intention is to leverage the advantages of synthetic data for the prediction of the LOS in order to contribute to the efficiency -enhancing and cost-saving aspirations of hospitals and insurance companies. Therefore, the applicability of synthetic data generated by GANs as a proxy for scarce real-world EHR for the patient LOS multi-class classification task is examined. In this context the Conditional Tabular GAN (CTGAN) and the Copula GAN are selected. The CTGAN is found to be the superior model for the underlying use case. Nevertheless, the paper shows that there is still room for improvement when applying state-of-the-art GAN architectures to EHR.

## 208. MedDiffusion: Boosting Health Risk Prediction via Diffusion-based Data Augmentation

- Authors: Yuan Zhong; Suhan Cui; Jiaqi Wang; Xiaochen Wang; Ziyi Yin; Yaqing Wang; Houping Xiao; Mengdi Huai; Ting Wang; Fenglong Ma
- Year: 2023
- DOI: 10.48550/arxiv.2310.02520
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2310.02520
- PDF: https://arxiv.org/pdf/2310.02520

Health risk prediction is one of the fundamental tasks under predictive modeling in the medical domain, which aims to forecast the potential health risks that patients may face in the future using their historical Electronic Health Records (EHR). Researchers have developed several risk prediction models to handle the unique challenges of EHR data, such as its sequential nature, high dimensionality, and inherent noise. These models have yielded impressive results. Nonetheless, a key issue undermining their effectiveness is data insufficiency. A variety of data generation and augmentation methods have been introduced to mitigate this issue by expanding the size of the training data set through the learning of underlying data distributions. However, the performance of these methods is often limited due to their task-unrelated design. To address these shortcomings, this paper introduces a novel, end-to-end diffusion-based risk prediction model, named MedDiffusion. It enhances risk prediction performance by creating synthetic patient data during training to enlarge sample space. Furthermore, MedDiffusion discerns hidden relationships between patient visits using a step-wise attention mechanism, enabling the model to automatically retain the most vital information for generating high-quality data. Experimental evaluation on four real-world medical datasets demonstrates that MedDiffusion outperforms 14 cutting-edge baselines in terms of PR-AUC, F1, and Cohen's Kappa. We also conduct ablation studies and benchmark our model against GAN-based alternatives to further validate the rationality and adaptability of our model design. Additionally, we analyze generated data to offer fresh insights into the model's interpretability.

## 209. LTGAN: Multi-label Time-Series GAN with Constraints for Electronic Health Records Generation

- Authors: Yi Luo; Ming Sheng; Xianbo Liu; Kaiyuan Wang; Yong Zhang; Huiying Zhao
- Year: 2025
- DOI: 10.1007/978-981-96-5597-7_4
- Venue: Lecture notes in computer science
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1007/978-981-96-5597-7_4

## 210. Deep Learning in Medicine

- Authors: Samuel P. Heilbroner; Riccardo Miotto
- Year: 2023
- DOI: 10.2215/cjn.0000000000000080
- Venue: Clinical Journal of the American Society of Nephrology
- Countries: GB; US
- Source: openalex
- URL: https://doi.org/10.2215/cjn.0000000000000080
- PDF: https://www.ncbi.nlm.nih.gov/pmc/articles/10103223

Medicine is in a new era where clinical decisions are influenced by analysis on large quantities of data. However, making full use of biomedical data such as electronic health records (EHRs), -omics biobanks, clinical images, and wearable measurements is challenging, owing to their high dimensionality, heterogeneity, temporal dependency, sparsity, redundancy, bias, and irregularity.1 A common approach is to have a domain expert specify the phenotype of interest in an ad hoc manner. However, this approach scales poorly and misses opportunities to discover novel patterns. Advances in machine learning (ML) can be exploited to overcome these limitations. ML is a general-purpose paradigm that learns relationships from the data without the need to define them a priori.2 For decades, constructing an ML system required careful engineering and domain expertise to transform the raw data into a suitable internal representation that facilitates learning such relationships. By contrast, a deep learning system uses neural networks to automatically develop its own representations from the raw data. Neural network layers are typically arranged sequentially and composed of a large number of basic, nonlinear operations, such that the representation of one layer (beginning with the raw data input) is fed into the next layer and transformed into a more abstract representation. As data flow through the layers of the system, the input space is iteratively reshaped until attributes of interest become distinguishable.3 The use of deep learning in medicine has been increasing since 2012, with several models successfully going from research to clinical deployment.4 These models can scale to very large datasets, mostly because of their ability to run on specialized computing hardware, and continue to improve with more data, enabling them to outperform many classical ML approaches. Another advantage of deep learning models is their ability to naturally ingest multimodal data (e.g., EHRs, medical images, and genomic data), leading to frameworks that can holistically represent a patient's clinical status. Several types of neural networks are available as building blocks of deep learning architectures. In the bag-of-data-points scenario, a fully connected network can capture correlations among different features. If data have a natural and invariant adjacency structure, such as images, a convolutional neural network (CNN) can take advantage of that structure by emphasizing local relationships, especially in early layers of the model. When data have a strong temporal component (e.g., time series), recurrent neural networks (RNNs) can model the time sequences of the events. Both RNNs and CNNs, however, struggle to perceive dependencies between data points that are temporally or spatially far from each other. Attention-based architectures such as transformers more efficiently account for these distant interactions and are quickly becoming the state of the art in a number of applications. Deep architectures are trained in different ways using variations of the back-propagation algorithm. A typical scenario is the supervised learning paradigm, where models learn to map an input (e.g., a chest x-ray scan or a group of laboratory test results) to a label (e.g., a diagnosis of pneumonia or the prediction of the onset of a metabolic condition). There are several potential applications of supervised learning in medicine for adverse event detection, medical image classification and segmentation, and patient risk stratification.1 For example, deep learning was used to predict AKI from EHRs5 and classify kidney biopsy images of patients with diabetic nephropathy.6 Training using supervised learning requires datasets in which each input is annotated with its corresponding label. These are commonly derived manually and must be of high quality (gold label) to obtain generalizable models that can effectively assign one of the labels to new data points. Given the time and expense associated with this process, it is often advantageous to use weak supervision, which defines silver labels that are not perfect but are strongly correlated with the gold values. In medicine, billing codes are an abundant source of silver labels, with the advantage of also being regularly updated, leading to annotations that account for changes in the population. In cases where silver labeling is not possible, a significant logistical and financial investment is often necessary to acquire reliable labels. Another option is unsupervised learning. Unsupervised learning is used to draw inferences from datasets consisting of input data without any labeled annotation. In medicine, the goal is often to cluster patients according to their clinical characteristics to identify novel disease subtypes and phenotypes (namely, patient stratification), which can inform more personalized clinical care or provide avenues for future research. As an example, unsupervised learning was used to subphenotype patients with sepsis-induced AKI in ways that informed the underlying physiology and patient mortality.7 Self-supervised learning is another type of unsupervised learning. In this paradigm, a first phase pretrains models in a preparation task using large-scale unlabeled datasets. Preparation tasks could be defined by occluding portions of the data and expecting the model to predict what was hidden or by providing two samples from the same distribution and training the model to associate them strongly (contrastive learning). After such preliminary training, these general architectures can be fine-tuned on a much smaller set of labeled examples for various supervised learning tasks. This pretraining phase is valuable because the model can learn how to find relevant attributes in large-scale data, even before seeing any labeled data, and has led to significant improvements in scalability and performance. Self-supervised learning has been used in medicine with pathology slides, electrocardiograms, clinical notes, EHRs, and x-ray scans.8 Different neural network architectures and learning strategies are used in unsupervised learning. Denoising autoencoders derive compressed representations of data, which focus only on areas of real value, and are trained to recreate the original data from a corrupted input. Variational autoencoders also recreate the original data while enforcing a probability distribution on the model's internal representation. Generative adversarial networks (GANs) are composed of two networks: a generator and a discriminator. The generator is trained to create realistic synthetic examples that can trick the discriminator, whereas the discriminator is trained to correctly separate real examples from synthetic ones. All of these models can augment downstream ML efforts. Consider the task of classifying magnetic resonance imaging slices: A GAN could be used to generate additional training examples, while autoencoders could generate useful feature representations for supervised modeling. In the medical domain, ethical, legal, and logistical hurdles make it challenging to aggregate data from across institutions into something large enough to train a deep learning model. Deidentification can smooth the path to data aggregation and access. Another strategy is federated learning. ML models are trained across multiple institutions, such that data from each institution never leave their own servers—alleviating some of the ethical and legal challenges related to aggregating datasets. It is important to consider how deep architectures can be obtained from the literature into the real world,9 a challenge highlighted by how few of these models are currently used to improve patient care. The level of evidence required to bring an ML model into clinical practice depends on the specific risks and benefits of that model and its use case. In an ideal world, all models would be validated using a randomized controlled trial (RCT), where clinical practice is aided by a model for a randomly selected group of patients and their outcomes are compared with the controls. However, many algorithms used in clinical practice today did not reach this bar. For example, the ubiquitous CHADS-Vasc score has never been validated with an RCT. There is no one-size-fits-all approach, and this decision should be made with a multidisciplinary team of ML scientists, engineers, practitioners (e.g., nurses, clinicians), hospital administration, and the patients themselves. It is also necessary that these changes be embedded in the system without disrupting it, following the regulatory frameworks provided by the Food and Drug Administration. At minimum, all ML models should undergo rigorous validation, which estimates how a model would actually perform in the real world. This is typically done by measuring model performance against a test set (data that the model was not trained on). Performance on the testing set is not affected by overfitting, a process in which the model memorizes individual training examples without abstracting the general concepts necessary to make future inferences. The simplest way to generate a test set is by randomly dividing the data into separate training and testing subsets. This does not work when the model is applied to data from a different population, such as patients from a different hospital. In this case, scientists often use out-of-sample validation, in which the external data are used for additional testing. Because unsupervised models are trained without an objective, they are harder to overfit. However, the process of extracting insights from results of an unsupervised analysis is subject to the very human bias to see patterns, which is itself a form of overfitting. Because there are no labels, it is also more difficult to design a validation experiment, resulting in laxer validation standards. Although these models are often created without an initial hypothesis, the insights generated can actually be thoughtfully validated, even if the process is less formulaic than for supervised learning. Taking patient stratification as an example, an unsupervised model can be used to classify patients into disease subtypes identified by clustering. Ideally, these subtypes have statistically and clinically significant differences in their attributes, and clinicians could use this information to inform treatment decisions. An RCT, where patients who have treatment decisions informed by their subtype membership are compared with the standard of care, can then also be used to formally test this hypothesis. Several barriers such as interpretability and robustness to all populations also stand between deep learning and wide adoption in medicine.10 While the steps outlined above to move deep learning into the clinic represent significant challenges, we envision that there will be an increasing number of success stories in the foreseeable future, leading to new sets of practices and tools that will significantly affect patient health and clinical practice.

## 211. Subpopulation-specific synthetic electronic health records can increase mortality prediction performance

- Authors: Oriel Perets; Nadav Rappoport
- Year: 2025
- DOI: 10.1093/jamiaopen/ooaf091
- Venue: JAMIA Open
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1093/jamiaopen/ooaf091
- PDF: https://academic.oup.com/jamiaopen/article-pdf/8/4/ooaf091/63980360/ooaf091.pdf

<jats:title>Abstract</jats:title>
               <jats:sec>
                  <jats:title>Objective</jats:title>
                  <jats:p>To address biased representation in Electronic Health Records (EHRs) across subpopulations (SPs), which leads to predictive models underperforming for underrepresented groups, we propose a framework to enhance equitable predictive performance.</jats:p>
               </jats:sec>
               <jats:sec>
                  <jats:title>Materials and Methods</jats:title>
                  <jats:p>We developed a framework using generative adversarial networks (GANs) to create SP-specific synthetic data, which augments the original training datasets. Subsequently, we employed an ensemble approach, training distinct prediction models tailored to each SP.</jats:p>
               </jats:sec>
               <jats:sec>
                  <jats:title>Results</jats:title>
                  <jats:p>The proposed framework was evaluated on two datasets derived from the MIMIC database, achieving a performance improvement in Receiver Operating Characteristics Area Under Curve (ROCAUC) ranging from 8% to 31% for underrepresented SPs.</jats:p>
               </jats:sec>
               <jats:sec>
                  <jats:title>Discussion</jats:title>
                  <jats:p>The results indicate that targeted synthetic data augmentation and SP-specific model training significantly mitigate the performance disparities observed in conventional predictive models trained on imbalanced EHR data.</jats:p>
               </jats:sec>
               <jats:sec>
                  <jats:title>Conclusion</jats:title>
                  <jats:p>Our novel GAN-based framework, combined with an ensemble prediction approach, effectively enhances predictive equity across SPs. The code and ensemble models developed in this study are publicly available, supporting further research and practical adoption of equitable predictive analytics in healthcare.</jats:p>
               </jats:sec>

## 212. Strategies for Generating Synthetic Health Records Using Generative Artificial Intelligence

- Authors: Geetha Manoharan; Subhashini Durai
- Year: 2025
- DOI: 10.4018/979-8-3373-5641-9.ch004
- Venue: Advances in Synthetic Healthcare Data
- Countries: 
- Source: crossref
- URL: https://doi.org/10.4018/979-8-3373-5641-9.ch004

<jats:p>This chapter digs into the methods for creating synthetic health records using generative artificial intelligence (AI) approaches, stressing its critical role in improving healthcare research while protecting patient privacy. Synthetic health data are intentionally manufactured datasets that closely resemble real-world electronic health records but do not include actual patient information, allowing for safe data exchange and analysis. The chapter examines popular generative AI techniques such as generative adversarial networks and variational autoencoders, demonstrating how these models capture complicated statistical characteristics and correlations in healthcare data. It examines the use of synthetic EHRs in medical AI research, clinical simulations, and software testing. Furthermore, the chapter discusses data quality issues, ethical concerns, and balancing privacy and usefulness. Overall, generative AI is a transformational tool for overcoming data accessibility hurdles and encouraging innovation in health informatics.</jats:p>

## 213. A survey on text generation using generative adversarial networks

- Authors: Gustavo Henrique de Rosa; João Paulo Papa
- Year: 2021
- DOI: 10.1016/j.patcog.2021.108098
- Venue: Pattern Recognition
- Countries: BR
- Source: openalex
- URL: https://doi.org/10.1016/j.patcog.2021.108098
- PDF: https://arxiv.org/pdf/2212.11119

## 214. RelGAN: Relational Generative Adversarial Networks for Text Generation.

- Authors: Weili Nie; Nina Narodytska; Ankit Patel
- Year: 2018
- DOI: 
- Venue: International Conference on Learning Representations
- Countries: 
- Source: openalex
- URL: https://openalex.org/W2908747729

## 215. Diversity-Promoting GAN: A Cross-Entropy Based Generative Adversarial Network for Diversified Text Generation

- Authors: Jingjing Xu; Xuancheng Ren; Junyang Lin; Xu Sun
- Year: 2018
- DOI: 10.18653/v1/d18-1428
- Venue: 
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.18653/v1/d18-1428
- PDF: https://www.aclweb.org/anthology/D18-1428.pdf

Existing text generation methods tend to produce repeated and "boring" expressions. To tackle this problem, we propose a new text generation model, called Diversity-Promoting Generative Adversarial Network (DP-GAN). The proposed model assigns low reward for repeatedly generated text and high reward for "novel" and fluent text, encouraging the generator to produce diverse and informative text. Moreover, we propose a novel languagemodel based discriminator, which can better distinguish novel text from repeated text without the saturation problem compared with existing classifier-based discriminators. The experimental results on review generation and dialogue generation tasks demonstrate that our model can generate substantially more diverse and informative text than existing baselines. 1

## 216. GAN computers generate arts? A survey on visual arts, music, and literary text generation using generative adversarial network

- Authors: Sakib Shahriar
- Year: 2022
- DOI: 10.1016/j.displa.2022.102237
- Venue: Displays
- Countries: AE
- Source: openalex
- URL: https://doi.org/10.1016/j.displa.2022.102237

## 217. Customizable text generation via conditional text generative adversarial network

- Authors: Jinyin Chen; Yangyang Wu; Chengyu Jia; Haibin Zheng; Guohan Huang
- Year: 2019
- DOI: 10.1016/j.neucom.2018.12.092
- Venue: Neurocomputing
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1016/j.neucom.2018.12.092

## 218. CatGAN: Category-Aware Generative Adversarial Networks with Hierarchical Evolutionary Learning for Category Text Generation

- Authors: Zhiyue Liu; Jiahai Wang; Zhiwei Liang
- Year: 2020
- DOI: 10.1609/aaai.v34i05.6361
- Venue: Proceedings of the AAAI Conference on Artificial Intelligence
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1609/aaai.v34i05.6361
- PDF: https://ojs.aaai.org/index.php/AAAI/article/download/6361/6217

Generating multiple categories of texts is a challenging task and draws more and more attention. Since generative adversarial nets (GANs) have shown competitive results on general text generation, they are extended for category text generation in some previous works. However, the complicated model structures and learning strategies limit their performance and exacerbate the training instability. This paper proposes a category-aware GAN (CatGAN) which consists of an efficient category-aware model for category text generation and a hierarchical evolutionary learning algorithm for training our model. The category-aware model directly measures the gap between real samples and generated samples on each category, then reducing this gap will guide the model to generate high-quality category samples. The Gumbel-Softmax relaxation further frees our model from complicated learning strategies for updating CatGAN on discrete data. Moreover, only focusing on the sample quality normally leads the mode collapse problem, thus a hierarchical evolutionary learning algorithm is introduced to stabilize the training procedure and obtain the trade-off between quality and diversity while training CatGAN. Experimental results demonstrate that CatGAN outperforms most of the existing state-of-the-art methods.

## 219. FGGAN: Feature-Guiding Generative Adversarial Networks for Text Generation

- Authors: Yang Yang; Xiaodong Dan; Xuesong Qiu; Zhipeng Gao
- Year: 2020
- DOI: 10.1109/access.2020.2993928
- Venue: IEEE Access
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/access.2020.2993928
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/8948470/09091179.pdf

Text generation is a basic work of natural language processing, which plays an important role in dialogue system and intelligent translation. As a kind of deep learning framework, Generative Adversarial Networks (GAN) has been widely used in text generation. In combination with reinforcement learning, GAN uses the output of discriminator as reward signal of reinforcement learning to guide generator training, but the reward signal is a scalar and the guidance is weak. This paper proposes a text generation model named Feature-Guiding Generative Adversarial Networks (FGGAN). To solve the problem of insufficient feedback guidance from the discriminator network, FGGAN uses a feature guidance module to extract text features from the discriminator network, convert them into feature guidance vectors and feed them into the generator network for guidance. In addition, sampling is required to complete the sequence before feeding it into the discriminator to get feedback signal in text generation. However, the randomness and insufficiency of the sampling method lead to poor quality of generated text. This paper formulates text semantic rules to restrict the token of the next time step in the sequence generation process and remove semantically unreasonable tokens to improve the quality of generated text. Finally, text generation experiments are performed on different datasets and the results verify the effectiveness and superiority of FGGAN.

## 220. A Research on Generative Adversarial Networks Applied to Text Generation

- Authors: Chao Zhang; Caiquan Xiong; Lingyun Wang
- Year: 2019
- DOI: 10.1109/iccse.2019.8845453
- Venue: 
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/iccse.2019.8845453

Using deep learning methods to generate text, a sequence-to-sequence model is typically used. This kind of models is very effective in dealing with tasks that have a strong correspondence between input and output, such as machine translation. Generative Adversarial Networks(GAN) is a generation model that has been proposed in recent years, which has achieved good results in generating continuous and divisible data such as images. This paper proposes an improved model based on GAN, specifically using the transformer network structure instead of the original general Convolutional Neural Network or Recurrent Neural Networks as generator, and using the reinforcement learning algorithm Actor-Critic to improve the model training method. By comparing experiments, and selecting the perplexity, the BLEU score, and the percentages of unique n-gram to evaluate the quality of the generated sentences. The results show that the improved model proposed in this paper perform better than comparative models on above three evaluation indexes. This verifies its effectiveness in text generation.

## 221. Generative adversarial network for Table-to-Text generation

- Authors: Jianyu Zhao; Zhiqiang Zhan; Tong Li; Rang Li; Changjian Hu; Siyun Wang; Yang Zhang
- Year: 2021
- DOI: 10.1016/j.neucom.2021.04.036
- Venue: Neurocomputing
- Countries: CN; US
- Source: openalex
- URL: https://doi.org/10.1016/j.neucom.2021.04.036

## 222. Text Generation to Aid Depression Detection: A Comparative Study of Conditional Sequence Generative Adversarial Networks

- Authors: ML Tlachac; Walter Gerych; Kratika Agrawal; Benjamin Roger Litterer; Nicholas Jurovich; Saitheeraj Thatigotla; Jidapa Thadajarassiri; Elke A. Rundensteiner
- Year: 2022
- DOI: 10.1109/bigdata55660.2022.10020224
- Venue: 2022 IEEE International Conference on Big Data (Big Data)
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1109/bigdata55660.2022.10020224

Corpuses of unstructured textual data, such as text messages between individuals, are often predictive of medical issues such as depression. The text data usually used in healthcare applications has high value and great variety, but is typically small in volume. Generating labeled unstructured text data is important to improve models by augmenting these small datasets, as well as to facilitate anonymization. While methods for labeled data generation exist, not all of them generalize well to small datasets. In this work, we thus perform a much needed systematic comparison of conditional text generation models that are promising for small datasets due to their unified architectures. We identify and implement a family of nine conditional sequence generative adversarial networks for text generation, which we collectively refer to as cSeqGAN models. These models are characterized along two orthogonal design dimensions: weighting strategies and feedback mechanisms. We conduct a comparative study evaluating the generation ability of the nine cSeqGAN models on three diverse text datasets with depression and sentiment labels. To assess the quality and realism of the generated text, we use standard machine learning metrics as well as human assessment via a user study. While the unconditioned models produced predictive text, the cSeqGAN models produced more realistic text. Our comparative study lays a solid foundation and provides important insights for further text generation research, particularly for the small datasets common within the healthcare domain.

## 223. TextKD-GAN: Text Generation Using Knowledge Distillation and Generative Adversarial Networks

- Authors: Md. Akmal Haidar; Mehdi Rezagholizadeh
- Year: 2019
- DOI: 10.1007/978-3-030-18305-9_9
- Venue: Lecture notes in computer science
- Countries: CA
- Source: openalex
- URL: https://doi.org/10.1007/978-3-030-18305-9_9
- PDF: https://arxiv.org/pdf/1905.01976

## 224. Synthetic dataset generation for text recognition with generative adversarial networks

- Authors: Valeria Efimova; Viacheslav Shalamov; Andrey Filchenkov
- Year: 2020
- DOI: 10.1117/12.2558271
- Venue: 
- Countries: RU
- Source: openalex
- URL: https://doi.org/10.1117/12.2558271

Automated text recognition is used in autonomous driving systems, search engines, document analysis, and many other applications. There are many techniques to extract text information from scanned documents, but text recognition from arbitrary images is a much harder task. Recently suggested deep learning approaches have demonstrated highquality results, but they require a huge amount of data to achieve them. The process of collecting and labelling training data to train a deep learning network is costly. In this paper, we suggest an approach for automatic dataset generation for text recognition for arbitrary languages. We use a generative adversarial network structure, which is adapted to generate readable and clear text looking naturally on the image background. We evaluate our approach using SegLink and Textboxes++ text localization models, which were trained on examples generated by SynthText and by variations of our method. The comparison showed the superiority of our method on a subset of the ICDAR 2017 dataset for English and Arabic languages.

## 225. Objective-Reinforced Generative Adversarial Networks (ORGAN) for Sequence Generation Models

- Authors: Gabriel Lima Guimaraes; Benjamín Sánchez-Lengeling; Outeiral, Carlos; Pedro Luis Cunha Farias; Alán Aspuru‐Guzik
- Year: 2017
- DOI: 10.48550/arxiv.1705.10843
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1705.10843
- PDF: https://arxiv.org/pdf/1705.10843

In unsupervised data generation tasks, besides the generation of a sample based on previous observations, one would often like to give hints to the model in order to bias the generation towards desirable metrics. We propose a method that combines Generative Adversarial Networks (GANs) and reinforcement learning (RL) in order to accomplish exactly that. While RL biases the data generation process towards arbitrary metrics, the GAN component of the reward function ensures that the model still remembers information learned from data. We build upon previous results that incorporated GANs and RL in order to generate sequence data and test this model in several settings for the generation of molecules encoded as text sequences (SMILES) and in the context of music generation, showing for each case that we can effectively bias the generation process towards desired metrics.

## 226. Research and Application Status of Text Generation Tasks Based on Generative Adversarial Network

- Authors: Weiqi Wang; Dan Jiang; Shaozhong Cao
- Year: 2023
- DOI: 10.1007/978-981-99-3618-2_11
- Venue: Lecture notes in operations research
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1007/978-981-99-3618-2_11

## 227. GAN Computers Generate Arts? A Survey on Visual Arts, Music, and Literary Text Generation using Generative Adversarial Network

- Authors: Sakib Shahriar
- Year: 2021
- DOI: 10.48550/arxiv.2108.03857
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2108.03857
- PDF: https://arxiv.org/pdf/2108.03857

"Art is the lie that enables us to realize the truth." - Pablo Picasso. For centuries, humans have dedicated themselves to producing arts to convey their imagination. The advancement in technology and deep learning in particular, has caught the attention of many researchers trying to investigate whether art generation is possible by computers and algorithms. Using generative adversarial networks (GANs), applications such as synthesizing photorealistic human faces and creating captions automatically from images were realized. This survey takes a comprehensive look at the recent works using GANs for generating visual arts, music, and literary text. A performance comparison and description of the various GAN architecture are also presented. Finally, some of the key challenges in art generation using GANs are highlighted along with recommendations for future work.

## 228. Unsupervised Text Embedding Space Generation Using Generative Adversarial Networks for Text Synthesis

- Authors: Jun-Min Lee; Tae-Bin Ha
- Year: 2023
- DOI: 10.3384/nejlt.2000-1533.2023.4855
- Venue: Northern European Journal of Language Technology
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.3384/nejlt.2000-1533.2023.4855
- PDF: https://nejlt.ep.liu.se/article/download/4855/4040

Generative Adversarial Networks (GAN) is a model for data synthesis, which creates plausible data through the competition of generator and discriminator. Although GAN application to image synthesis is extensively studied, it has inherent limitations to natural language generation. Because natural language is composed of discrete tokens, a generator has difficulty updating its gradient through backpropagation; therefore, most text-GAN studies generate sentences starting with a random token based on a reward system. Thus, the generators of previous studies are pre-trained in an autoregressive way before adversarial training, causing data memorization that synthesized sentences reproduce the training data. In this paper, we synthesize sentences using a framework similar to the original GAN. More specifically, we propose Text Embedding Space Generative Adversarial Networks (TESGAN) which generate continuous text embedding spaces instead of discrete tokens to solve the gradient backpropagation problem. Furthermore, TESGAN conducts unsupervised learning which does not directly refer to the text of the training data to overcome the data memorization issue. By adopting this novel method, TESGAN can synthesize new sentences, showing the potential of unsupervised learning for text synthesis. We expect to see extended research combining Large Language Models with a new perspective of viewing text as an continuous space.

## 229. CatGAN: Category-aware Generative Adversarial Networks with Hierarchical Evolutionary Learning for Category Text Generation

- Authors: Zhiyue Liu; Jiahai Wang; Zhiwei Liang
- Year: 2019
- DOI: 10.48550/arxiv.1911.06641
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1911.06641
- PDF: https://arxiv.org/pdf/1911.06641

Generating multiple categories of texts is a challenging task and draws more and more attention. Since generative adversarial nets (GANs) have shown competitive results on general text generation, they are extended for category text generation in some previous works. However, the complicated model structures and learning strategies limit their performance and exacerbate the training instability. This paper proposes a category-aware GAN (CatGAN) which consists of an efficient category-aware model for category text generation and a hierarchical evolutionary learning algorithm for training our model. The category-aware model directly measures the gap between real samples and generated samples on each category, then reducing this gap will guide the model to generate high-quality category samples. The Gumbel-Softmax relaxation further frees our model from complicated learning strategies for updating CatGAN on discrete data. Moreover, only focusing on the sample quality normally leads the mode collapse problem, thus a hierarchical evolutionary learning algorithm is introduced to stabilize the training procedure and obtain the trade-off between quality and diversity while training CatGAN. Experimental results demonstrate that CatGAN outperforms most of the existing state-of-the-art methods.

## 230. MaskGAN: Better Text Generation via Filling in the______

- Authors: William Fedus; Ian Goodfellow; Andrew M. Dai
- Year: 2018
- DOI: 10.48550/arxiv.1801.07736
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1801.07736
- PDF: https://arxiv.org/pdf/1801.07736

Neural text generation models are often autoregressive language models or seq2seq models. These models generate text by sampling words sequentially, with each word conditioned on the previous word, and are state-of-the-art for several machine translation and summarization benchmarks. These benchmarks are often defined by validation perplexity even though this is not a direct measure of the quality of the generated text. Additionally, these models are typically trained via maxi- mum likelihood and teacher forcing. These methods are well-suited to optimizing perplexity but can result in poor sample quality since generating text requires conditioning on sequences of words that may have never been observed at training time. We propose to improve sample quality using Generative Adversarial Networks (GANs), which explicitly train the generator to produce high quality samples and have shown a lot of success in image generation. GANs were originally designed to output differentiable values, so discrete language generation is challenging for them. We claim that validation perplexity alone is not indicative of the quality of text generated by a model. We introduce an actor-critic conditional GAN that fills in missing text conditioned on the surrounding context. We show qualitatively and quantitatively, evidence that this produces more realistic conditional and unconditional text samples compared to a maximum likelihood trained model.

## 231. Penalty-based Sequence Generative Adversarial Networks with Enhanced Transformer for Text Generation

- Authors: Mingjun Duan; Yubai Li
- Year: 2020
- DOI: 10.1109/ijcnn48605.2020.9207725
- Venue: 
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/ijcnn48605.2020.9207725

In this paper, we propose a new model to solve the problem of text generation, which is based on the concept of seqGAN, combines self-attention with modeling localness, and introduces the penalty-based objective function. This model has much better performance than the original model. In the original model, the generator's ability of the text feature extraction is insufficient. We introduce self-attention with modeling localness, which greatly enhances its ability to capture long distance and shortrange dependencies. In addition, we use the penalty-based objective function instead of the loss function of the original model to solve the problem of mode collapse. Experimental results demonstrate that our model consistently outperforms several state-of-the-art text generation methods in the quality of generated texts.

## 232. SparseGAN: Sparse Generative Adversarial Network for Text Generation

- Authors: Liping Yuan; Jiehang Zeng; Xiaoqing Zheng
- Year: 2021
- DOI: 10.48550/arxiv.2103.11578
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2103.11578
- PDF: https://arxiv.org/pdf/2103.11578

It is still a challenging task to learn a neural text generation model under the framework of generative adversarial networks (GANs) since the entire training process is not differentiable. The existing training strategies either suffer from unreliable gradient estimations or imprecise sentence representations. Inspired by the principle of sparse coding, we propose a SparseGAN that generates semantic-interpretable, but sparse sentence representations as inputs to the discriminator. The key idea is that we treat an embedding matrix as an over-complete dictionary, and use a linear combination of very few selected word embeddings to approximate the output feature representation of the generator at each time step. With such semantic-rich representations, we not only reduce unnecessary noises for efficient adversarial training, but also make the entire training process fully differentiable. Experiments on multiple text generation datasets yield performance improvements, especially in sequence-level metrics, such as BLEU.

## 233. Advancements in Generative AI: A Comprehensive Review of GANs, GPT, Autoencoders, Diffusion Model, and Transformers

- Authors: Staphord Bengesi; Hoda El-Sayed; Md Kamruzzaman Sarker; Yao Houkpati; John Irungu; Timothy Oladunni
- Year: 2024
- DOI: 10.1109/access.2024.3397775
- Venue: IEEE Access
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1109/access.2024.3397775
- PDF: https://doi.org/10.1109/access.2024.3397775

The launch of ChatGPT in 2022 garnered global attention, marking a significant milestone in the Generative Artificial Intelligence (GAI) field. While GAI has been in effect for the past decade, the introduction of ChatGPT sparked a new wave of research and innovation in the Artificial Intelligence (AI) domain. This surge has led to the development and release of numerous cutting-edge tools, such as Bard, Stable Diffusion, DALL-E, Make-A-Video, Runway ML, and Jukebox, among others. These tools exhibit remarkable capabilities, encompassing tasks ranging from text generation and music composition, image creation, video production, code generation, and even scientific work. They are built upon various state-of-the-art models, including Stable Diffusion, transformer models like GPT-3 (recent GPT-4), variational autoencoders, and generative adversarial networks. This advancement in GAI presents a wealth of exciting opportunities across various sectors, such as business, healthcare, education, entertainment, and media. However, concurrently, it poses unprecedented challenges such as impersonation, job displacement, privacy breaches, security vulnerabilities, and misinformation. To addressing these challenges requires a new direction for research to develop solutions and refine existing products. In our endeavor to contribute profound insights to society and advance research on GAI, we present a comprehensive journal which explores the theoretical and mathematical foundations of GAI state-of-the-art models, exploring the diverse spectrum of tasks they can perform, examining the challenges they entail, and discussing the promising prospects for the future of GAI.

## 234. CTGGAN: Controllable Text Generation with Generative Adversarial Network

- Authors: Zhe Yang; Yi Huang; Yaqin Chen; Xiaoting Wu; Junlan Feng; Chao Deng
- Year: 2024
- DOI: 10.3390/app14073106
- Venue: Applied Sciences
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.3390/app14073106
- PDF: https://www.mdpi.com/2076-3417/14/7/3106/pdf?version=1712538759

Controllable Text Generation (CTG) aims to modify the output of a Language Model (LM) to meet specific constraints. For example, in a customer service conversation, responses from the agent should ideally be soothing and address the user’s dissatisfaction or complaints. This imposes significant demands on controlling language model output. However, demerits exist among traditional methods. Promoting and fine-tuning language models exhibit the “hallucination” phenomenon and cannot guarantee complete adherence to constraints. Conditional language models (CLM), which map control codes into LM representations or latent space, require training the modified language models from scratch and a high amount of customized dataset is demanded. Decoding-time methods employ Bayesian Rules to modify the output of the LM or model constraints as a combination of energy functions and update the output along the low-energy direction. Both methods are confronted with the efficiency sampling problem. Moreover, there are no methods that consider the relation between constraints weights and the contexts, as is essential in actual applications such as customer service scenarios. To alleviate the problems mentioned above, we propose Controllable Text Generation with Generative Adversarial Networks (CTGGAN), which utilizes a language model with logits bias as the Generator to produce constrained text and employs the Discriminator with learnable constraint weight combinations to score and update the generation. We evaluate the method in the text completion task and Chinese customer service dialogues scenario, and our method shows superior performance in metrics such as PPL and Dist-3. In addition, CTGGAN also exhibits efficient decoding compared to other methods.

## 235. Penalty based Sentimental Text Generation Framework using Generative Adversarial Networks

- Authors: K. Chitra; G. Kavitha; P. Latchoumy
- Year: 2022
- DOI: 10.1109/icacrs55517.2022.10029135
- Venue: 2022 International Conference on Automation, Computing and Renewable Systems (ICACRS)
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.1109/icacrs55517.2022.10029135

Emotional Intelligence is the technology where computers are trained to handle, use, understand and manage emotions. Emotional Intelligence (EI) is used in sentimental text generation where sentimental texts like positive, negative and neutral texts are generated. Sentimental text generation is used in many Artificial Intelligence application such as Google Assistant, Siri, Chatbots and so on. Many Deep learning algorithms such as LSTM, Bi-LSTM, RNN and CNN focus on generation of sentimental texts. The research work proposed herein uses Generative Adversarial Networks (GAN) for generating texts based on the training dataset. The GAN network has 2 models; generator model which generates the text and discriminator model which evaluates the text and both are trained using Bi-LSTM algorithm. The model is trained using Amazon customer review dataset and the system generates sentimental text such as positive, negative and neutral text for a given product. The existing system uses LSTM algorithm for prediction, but the performance and quality of generated text is low. The proposed system uses the Bi-LSTM algorithm which increases the accuracy of the generated sentimental text. The performance of the framework is evaluated in terms of fluency, sentimental accuracy and context relevance and is compared to the existing system of Automatic Generation of Sentimental Texts using Mixture Adversarial Networks.

## 236. Automatic text generation system for endangered languages based on conditional generative adversarial networks

- Authors: Zhong Luo
- Year: 2025
- DOI: 10.1016/j.sasc.2025.200306
- Venue: Systems and Soft Computing
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1016/j.sasc.2025.200306
- PDF: https://doi.org/10.1016/j.sasc.2025.200306

This paper explores the application of Conditional Generative Adversarial Networks (CGANs) in the field of endangered language text generation. The focus is on overcoming challenges associated with discrete data handling in natural language generation by utilizing an improved CGAN model. We introduce a specialized Loss function, based on the MaliGAN model, which directs the discriminator to guide the generator towards producing texts that not only align closely with individual word accuracy but also maintain overall semantic coherence. Additionally, a beam search decoding strategy is implemented to enhance the global semantic information and diversity of the text output. Our experimental evaluations across multiple datasets, including the Tujia language, Image_COCO, and EMNLP2017 WMT News, demonstrate significant improvements. The LFMGAN model, a variant of CGANs, notably increased BLEU-4 scores by up to 50.7 % for the Tujia language and achieved ROUGE-L score enhancements of up to 86.3 % in the Image_COCO dataset. These results underscore the model's robustness and its potential in preserving linguistic diversity. We discuss integrating advanced models like GPT-2 and RoBERTa to address training instability and gradient explosion challenges. Future research directions include optimizing CGAN parameters using algorithms like particle swarm optimization, refining discriminator outputs in loss calculations, and incorporating cultural and linguistic features specific to endangered languages to improve the quality of the generated texts.

## 237. Latent Code and Text-based Generative Adversarial Networks for Soft-text Generation

- Authors: Md. Akmal Haidar; Mehdi Rezagholizadeh; Alan Do-Omri; Ahmad Rashid
- Year: 2019
- DOI: 10.18653/v1/n19-1234
- Venue: 
- Countries: 
- Source: openalex
- URL: https://doi.org/10.18653/v1/n19-1234
- PDF: https://doi.org/10.18653/v1/n19-1234

Md. Akmal Haidar, Mehdi Rezagholizadeh, Alan Do Omri, Ahmad Rashid. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers). 2019.

## 238. Research on Handwriting Text Generation Algorithm Based on Generative Adversarial Network

- Authors: Fuchang Zhao
- Year: 2024
- DOI: 10.54097/kt3yem44
- Venue: Academic Journal of Science and Technology
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.54097/kt3yem44
- PDF: https://drpress.org/ojs/index.php/ajst/article/download/18570/18108

The main task of this paper is to study the handwriting text generation method based on deep learning. Through understanding the development status of the research, It can be found that the current research on the generation of different handwriting styles still has some obvious defects, such as the need for manual intervention in character segmentation, failure to capture the global handwriting style, style collapse, failure to generate arbitrary length characters, and text. Finally, this paper proposes a handwritten text generation algorithm combining advantages of convolutional network and Transformer. Specifically, this paper first constructs a lightweight backbone network and uses lightweight MobileNetv3 network as the backbone network to realize feature extraction of input images. The Efficient Channel Attention module is introduced to replace the SE attention module of MobileNetv3, which makes the network pay more attention to the global and local style features of handwritten images. In the feature extraction part, the network reduces the number of parameters, calculation amount and video memory occupation. It can also extract rich feature information. The FID and KID indexes of this algorithm obtained 20.28 and 9.07×10-3 respectively, and the generation effect of handwritten pictures was excellent, which could effectively imitate the writing style of writers.

## 239. Development of an End-to-End Deep Learning Framework for Sign Language Recognition, Translation, and Video Generation

- Authors: B Natarajan; E. Rajalakshmi; R Elakkiya; Ketan Kotecha; Ajith Abraham; Lubna A. Gabralla; V. Subramaniyaswamy
- Year: 2022
- DOI: 10.1109/access.2022.3210543
- Venue: IEEE Access
- Countries: IN; SA; US
- Source: openalex
- URL: https://doi.org/10.1109/access.2022.3210543
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/6514899/09905589.pdf

The recent developments in deep learning techniques evolved to new heights in various domains and applications. The recognition, translation, and video generation of Sign Language (SL) still face huge challenges from the development perspective. Although numerous advancements have been made in earlier approaches, the model performance still lacks recognition accuracy and visual quality. In this paper, we introduce novel approaches for developing the complete framework for handling SL recognition, translation, and production tasks in real-time cases. To achieve higher recognition accuracy, we use the MediaPipe library and a hybrid Convolutional Neural Network + Bi-directional Long Short Term Memory (CNN + Bi-LSTM) model for pose details extraction and text generation. On the other hand, the production of sign gesture videos for given spoken sentences is implemented using a hybrid Neural Machine Translation (NMT) + MediaPipe + Dynamic Generative Adversarial Network (GAN) model. The proposed model addresses the various complexities present in the existing approaches and achieves above 95% classification accuracy. In addition to that, the model performance is tested in various phases of development, and the evaluation metrics show noticeable improvements in our model. The model has been experimented with using different multilingual benchmark sign corpus and produces greater results in terms of recognition accuracy and visual quality. The proposed model has secured a 38.06 average Bilingual Evaluation Understudy (BLEU) score, remarkable human evaluation scores, 3.46 average Fréchet Inception Distance to videos (FID2vid) score, 0.921 average Structural Similarity Index Measure (SSIM) values, 8.4 average Inception Score, 29.73 average Peak Signal-to-Noise Ratio (PSNR) score, 14.06 average Fréchet Inception Distance (FID) score, and an average 0.715 Temporal Consistency Metric (TCM) Score which is evidence of the proposed work.

## 240. Adversarial Text Generation via Feature-Mover's Distance

- Authors: Li‐Qun Chen; Shuyang Dai; Chenyang Tao; Dinghan Shen; Zhe Gan; Haichao Zhang; Yizhe Zhang; Lawrence Carin
- Year: 2018
- DOI: 10.48550/arxiv.1809.06297
- Venue: arXiv (Cornell University)
- Countries: CN; US
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1809.06297
- PDF: https://arxiv.org/pdf/1809.06297

Generative adversarial networks (GANs) have achieved significant success in generating real-valued data. However, the discrete nature of text hinders the application of GAN to text-generation tasks. Instead of using the standard GAN objective, we propose to improve text-generation GAN via a novel approach inspired by optimal transport. Specifically, we consider matching the latent feature distributions of real and synthetic sentences using a novel metric, termed the feature-mover's distance (FMD). This formulation leads to a highly discriminative critic and easy-to-optimize objective, overcoming the mode-collapsing and brittle-training problems in existing methods. Extensive experiments are conducted on a variety of tasks to evaluate the proposed model empirically, including unconditional text generation, style transfer from non-parallel text, and unsupervised cipher cracking. The proposed model yields superior performance, demonstrating wide applicability and effectiveness.

## 241. A Review of Generative Adversarial Networks in Text Generation

- Authors: Jaden Cohen
- Year: 2024
- DOI: 10.58445/rars.975
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.58445/rars.975

## 242. Generation of novel Diels-Alder reactions using a generative adversarial network

- Authors: Sheng Li; Xinqiao Wang; Yejian Wu; Hongliang Duan; Lan Tang
- Year: 2022
- DOI: 10.26434/chemrxiv-2022-679c4
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.26434/chemrxiv-2022-679c4

<jats:p>Deep learning has enormous potential in the chemical and pharmaceutical fields. Among these, Generative Adversarial Network, as an excellent generative model, has shown its remarkable performance in the field of molecular generation, but it has few applications in organic chemistry. Therefore, we attempt to apply GAN as a generative model for the task of reaction generation to expand the application of GAN in chemistry. In this work, we used the MaskGAN model trained with 14092 Diels-Alder reactions, and we finally generated 1441 novel Diels-Alder reactions that learn reaction rules in-depth, which demonstrates that reaction generation can be used in the field of chemistry, and helps chemists explore novel reactions.</jats:p>

## 243. Advancements in Handwritten Bangla Text Generation using Generative Adversarial Networks: A Focus on Complete Text Recovery

- Authors: Md. Robiul Islam Niloy
- Year: 2024
- DOI: 10.1145/3723178.3723229
- Venue: Proceedings of the 3rd International Conference on Computing Advancements
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1145/3723178.3723229

## 244. Text Generation in Civil Aviation Radiotelephony Communication Using Generative Adversarial Network

- Authors: 意 邱
- Year: 2018
- DOI: 10.12677/csa.2018.812208
- Venue: Computer Science and Application
- Countries: 
- Source: crossref
- URL: https://doi.org/10.12677/csa.2018.812208

## 245. Text Generation Service Model Based on Truth-Guided SeqGAN

- Authors: Yuxi Wu; Junli Wang
- Year: 2020
- DOI: 10.1109/access.2020.2966291
- Venue: IEEE Access
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/access.2020.2966291
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/8948470/08957565.pdf

The Generative Adversarial Networks (GAN) has been successfully applied to the generation of text content such as poetry and speech, and it is a hot topic in the field of text generation. However, GAN has been facing the problem of training and convergence. For the generation model, this paper redefines on the loss function. The truth-guided method has been added to make the generated text closer to the real data. For the discriminant model, this paper designs a more suitable network structure. The self-attention mechanism has been added to the discrimination network to obtain richer semantic information. Finally, some experiments under different model structures and different parameters indicates the model with truth-guided and self-attention mechanism gets better results.

## 246. Investigation of the Batch Size Influence on the Quality of Text Generation by the SeqGAN Neural Network

- Authors: Nikolay Krivosheev; Ksenia Vik; Yulia Ivanova; В.Г. Спицын
- Year: 2021
- DOI: 10.20948/graphicon-2021-3027-1005-1010
- Venue: 
- Countries: RU
- Source: openalex
- URL: https://doi.org/10.20948/graphicon-2021-3027-1005-1010
- PDF: https://doi.org/10.20948/graphicon-2021-3027-1005-1010

One of the problems of text generation using the LSTM neural network is a decrease in the quality of generation with an increase in the length of the generated text. There are various solutions to improve the quality of text generation based on generative adversarial neural networks. This work uses preliminary training of the LSTM neural network based on the MLE approach and further training based on the SeqGAN neural network. Based on the presented results, we can conclude that the SeqGAN-based approach allows to increase the quality of text generation according to the NLL and BLEU metrics. The study of the influence of the batch size, in the process of competitive training of the SeqGAN neural network, on the quality of text generation has been carried out. It is shown that with an increase in the batch size, in the process of adversarial learning, the quality of LSTM neural network training increases. In this work, the Monte Carlo algorithm is not used in the training process of the SeqGAN neural network. For training and testing algorithms, image captions from the COCO Image Captions data sample are used. The quality of text generation based on the NLL and BLEU metrics has been assessed. Examples of the results of generating texts with an assessment of the quality of examples according to the BLEU metric are given,

## 247. Automatic generation of short texts based on the use of neural networks LSTM and SeqGAN

- Authors: Nikolay Krivosheev; Yulia Ivanova; В.Г. Спицын
- Year: 2021
- DOI: 10.17223/19988605/57/13
- Venue: Vestnik Tomskogo gosudarstvennogo universiteta Upravlenie vychislitel naya tekhnika i informatika
- Countries: 
- Source: openalex
- URL: https://doi.org/10.17223/19988605/57/13

## 248. SeqGAN: Sequence Generative Adversarial Nets with Policy Gradient

- Authors: Lantao Yu; Weinan Zhang; Jun Wang; Yong Yu
- Year: 2017
- DOI: 10.1609/aaai.v31i1.10804
- Venue: Proceedings of the AAAI Conference on Artificial Intelligence
- Countries: CN; GB
- Source: openalex
- URL: https://doi.org/10.1609/aaai.v31i1.10804
- PDF: https://ojs.aaai.org/index.php/AAAI/article/download/10804/10663

As a new way of training generative models, Generative Adversarial Net (GAN) that uses a discriminative model to guide the training of the generative model has enjoyed considerable success in generating real-valued data. However, it has limitations when the goal is for generating sequences of discrete tokens. A major reason lies in that the discrete outputs from the generative model make it difficult to pass the gradient update from the discriminative model to the generative model. Also, the discriminative model can only assess a complete sequence, while for a partially generated sequence, it is non-trivial to balance its current score and the future one once the entire sequence has been generated. In this paper, we propose a sequence generation framework, called SeqGAN, to solve the problems. Modeling the data generator as a stochastic policy in reinforcement learning (RL), SeqGAN bypasses the generator differentiation problem by directly performing gradient policy update. The RL reward signal comes from the GAN discriminator judged on a complete sequence, and is passed back to the intermediate state-action steps using Monte Carlo search. Extensive experiments on synthetic data and real-world tasks demonstrate significant improvements over strong baselines.

## 249. Text Generation Based on Generative Adversarial Nets with Latent Variables

- Authors: Heng Wang; Zengchang Qin; Tao Wan
- Year: 2018
- DOI: 10.1007/978-3-319-93037-4_8
- Venue: Lecture notes in computer science
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1007/978-3-319-93037-4_8

## 250. Chinese Medicine Prescription Recommendation Using Generative Adversarial Network

- Authors: Chuitian Rong; Xueyan Li; Xuemei Sun; Huabo Sun
- Year: 2022
- DOI: 10.1109/access.2022.3143797
- Venue: IEEE Access
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/access.2022.3143797
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/9668973/09682726.pdf

The theory of traditional Chinese medicine (TCM) is an important part of Chinese culture. In the long history, there are a large number of excellent prescriptions, whose laws have been explored by many studies, but few works directly studied the generation of prescriptions. With the rapid development of deep learning, many applications of text generation using neural networks have emerged. Prescriptions are the doctors’ clinical experience and the results of neural networks also come from the accumulated experience. So, it is very feasible to apply deep learning techniques to the recommendation on TCM prescriptions. GAN and its variants have been applied in text generation recently. It has advantages in many aspects, such as the rapid speed of computation, the update of parameters by back propagation without Markov chain and more real data generation with two-players game. We attempted to know the important attributes of prescriptions and use these contents as the training data for variants of GAN to generate prescriptions. Specifically, we attempted to apply SeqGAN (Sequence Generative Adversarial Nets) and CGAN (Conditional Generative Adversarial Nets) to prescription generations. By underlying the knowledge of TCM, the prescriptions with different characteristics can be successfully generated. In the experiments, we conducted the comparative evaluations on the original data with other models. The results showed that applications in the innovation of prescription sequence generations have certain feasibility and significance, even can provide some reference values for the innovation of TCM.

## 251. AI-Lyricist

- Authors: Xichu Ma; Ye Wang; Min‐Yen Kan; Wee Sun Lee
- Year: 2021
- DOI: 10.1145/3474085.3475502
- Venue: 
- Countries: SG
- Source: openalex
- URL: https://doi.org/10.1145/3474085.3475502
- PDF: https://dl.acm.org/doi/pdf/10.1145/3474085.3475502

We propose AI-Lyricist: a system to generate novel yet meaningful lyrics given a required vocabulary and a MIDI file as inputs. This task involves multiple challenges, including automatically identifying the melody and extracting a syllable template from multi-channel music, generating creative lyrics that match the input music's style and syllable alignment, and satisfying vocabulary constraints. To address these challenges, we propose an automatic lyrics generation system consisting of four modules: (1) A music structure analyzer to derive the musical structure and syllable template from a given MIDI file, utilizing the concept of expected syllable number to better identify the melody, (2) a SeqGAN-based lyrics generator optimized by multi-adversarial training through policy gradients with twin discriminators for text quality and syllable alignment, (3) a deep coupled music-lyrics embedding model to project music and lyrics into a joint space to allow fair comparison of both melody and lyric constraints, and a module called (4) Polisher, to satisfy vocabulary constraints by applying a mask to the generator and substituting the words to be learned. We trained our model on a dataset of over 7,000 music-lyrics pairs, enhanced with manually annotated labels in terms of theme, sentiment and genre. Both objective and subjective evaluations show AI-Lyricist's superior performance against the state-of-the-art for the proposed tasks.

## 252. Well log data generation and imputation using sequence based generative adversarial networks

- Authors: Abdulrahman Al‐Fakih; Ardiansyah Koeshidayatullah; Tapan Mukerji; Sadam Al-Azani; SanLinn I. Kaka
- Year: 2025
- DOI: 10.1038/s41598-025-95709-0
- Venue: Scientific Reports
- Countries: SA; US
- Source: openalex
- URL: https://doi.org/10.1038/s41598-025-95709-0
- PDF: https://www.nature.com/articles/s41598-025-95709-0.pdf

Well log analysis is significant for hydrocarbon exploration, providing detailed insights into subsurface geological formations. However, gaps and inaccuracies in well log data, often due to equipment limitations, operational challenges, and harsh subsurface conditions, can introduce significant uncertainties in reservoir evaluation. Addressing these challenges requires effective methods for both synthetic data generation and precise imputation of missing data, ensuring data completeness and reliability. This study introduces a novel framework utilizing sequence-based generative adversarial networks (GANs) specifically designed for well log data generation and imputation. The framework integrates two distinct sequence-based GAN models: time series GAN (TSGAN) for generating synthetic well log data and sequence GAN (SeqGAN) for imputing missing data. Both models were tested on a dataset from the North Sea, Netherlands region. For the imputation task, the input comprises logs with missing values and the output is the corresponding imputed logs; for the synthetic data generation task, the input is complete real logs and the output is synthetic logs that mimic the statistical properties of the original data. All log measurements are normalized to a 0-1 range using min-max scaling, and error metrics are reported in these normalized units. Different sections of 5, 10, and 50 data points were used. Experimental results demonstrate that this approach achieves superior accuracy in filling data gaps compared to other deep learning models for spatial series analysis. The imputation method yielded [Formula: see text] values of 0.92, 0.86, and 0.57, with corresponding mean absolute percentage error (MAPE) values of 8.320, 0.005, and 166.6, and mean absolute error (MAE) values of 0.012, 0.002, and 0.03, respectively. The synthetic generation yielded [Formula: see text] of 0.92, MAE, of 0.35, and MRLE of 0.01. These results set a new benchmark for data integrity and utility in geosciences, particularly in well log data analysis.

## 253. Melody-Conditioned Lyrics Generation with SeqGANs

- Authors: Yihao Chen; Alexander Lerch
- Year: 2020
- DOI: 10.1109/ism.2020.00040
- Venue: 
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1109/ism.2020.00040

Automatic lyrics generation has received attention from both music and AI communities for years. Early rule-based approaches have -due to increases in computational power and evolution in data-driven models mostly been replaced with deep-learning-based systems. Many existing approaches, however, either rely heavily on prior knowledge in music and lyrics writing or oversimplify the task by largely discarding melodic information and its relationship with the text. We propose an end-to-end melody-conditioned lyrics generation system based on Sequence Generative Adversarial Networks (SeqGAN), which generates a line of lyrics given the corresponding melody as the input. Furthermore, we investigate the performance of the generator with an additional input condition: the theme or overarching topic of the lyrics to be generated. We show that the input conditions have no negative impact on the evaluation metrics while enabling the network to produce more meaningful results.

## 254. Long Text Generation via Adversarial Training with Leaked Information

- Authors: Jiaxian Guo; Sidi Lu; Han Cai; Weinan Zhang; Yong Yu; Jun Wang
- Year: 2018
- DOI: 10.1609/aaai.v32i1.11957
- Venue: Proceedings of the AAAI Conference on Artificial Intelligence
- Countries: CN; GB
- Source: openalex
- URL: https://doi.org/10.1609/aaai.v32i1.11957
- PDF: https://ojs.aaai.org/index.php/AAAI/article/download/11957/11816

Automatically generating coherent and semantically meaningful text has many applications in machine translation, dialogue systems, image captioning, etc. Recently, by combining with policy gradient, Generative Adversarial Nets(GAN) that use a discriminative model to guide the training of the generative model as a reinforcement learning policy has shown promising results in text generation. However, the scalar guiding signal is only available after the entire text has been generated and lacks intermediate information about text structure during the generative process. As such, it limits its success when the length of the generated text samples is long (more than 20 words). In this paper, we propose a new framework, called LeakGAN, to address the problem for long text generation. We allow the discriminative net to leak its own high-level extracted features to the generative net to further help the guidance. The generator incorporates such informative signals into all generation steps through an additional MANAGER module, which takes the extracted features of current generated words and outputs a latent vector to guide the WORKER module for next-word generation.Our extensive experiments on synthetic data and various real-world tasks with Turing test demonstrate that LeakGAN is highly effective in long text generation and also improves the performance in short text generation scenarios. More importantly, without any supervision, LeakGAN would be able to implicitly learn sentence structures only through the interaction between MANAGER and WORKER.

## 255. The analysis of generative adversarial network in sports education based on deep learning

- Authors: Eerdenisuyila Eerdenisuyila; Hongming Li; Wei Chen
- Year: 2024
- DOI: 10.1038/s41598-024-81107-5
- Venue: Scientific Reports
- Countries: AU; CN; US
- Source: openalex
- URL: https://doi.org/10.1038/s41598-024-81107-5
- PDF: https://www.nature.com/articles/s41598-024-81107-5.pdf

The importance of mental health is increasingly emphasized in modern society. The assessment of mental health qualities among college and university students as the future workforce holds significant significance. Therefore, this study, aiming to streamline the process of writing quality evaluations and enhance the fairness of assessment comments, explores the use of Generative Adversarial Network (GAN) technology in deep learning to evaluate the mental health qualities of college and university students through the unique avenue of sports. Firstly, GAN and Sequence Generative Adversarial Network (SeqGAN) models are introduced. Secondly, GAN is employed to construct a model for generating evaluation texts, encompassing the construction of a generator and discriminator, along with the introduction of a reward function. Finally, the constructed model is utilized to train on evaluation texts related to the mental health qualities of college and university students engaged in sports, validating the effectiveness of the model. The results indicate: (1) The pre-training of the generator in the constructed text generation model stabilizes after the 10th epoch. In contrast, the pre-training of the discriminator gradually stabilizes after the 35th epoch, demonstrating overall good training effectiveness. (2) When the generator's update speed surpasses that of the discriminator, the model's loss does not converge. However, with a reduction in the ratio of rounds between the two, there is a noticeable improvement in the convergence of the model. (3) The mean score of adaptability quality is the highest among the four indicators, suggesting a strong correlation between comment generation and adaptability quality. The results validate the effectiveness of the proposed text generation model in semantic control. This study aims to advance the level of mental health education among college and university students in the sports domain, providing theoretical references for enhancing the effectiveness of quality education assessments in other subjects as well.

## 256. SeqGAN: Sequence Generative Adversarial Nets with Policy Gradient

- Authors: Lantao Yu; Weinan Zhang; Jun Wang; Yong Yu
- Year: 2016
- DOI: 10.48550/arxiv.1609.05473
- Venue: arXiv (Cornell University)
- Countries: CN; GB
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1609.05473
- PDF: https://arxiv.org/pdf/1609.05473

As a new way of training generative models, Generative Adversarial Nets (GAN) that uses a discriminative model to guide the training of the generative model has enjoyed considerable success in generating real-valued data. However, it has limitations when the goal is for generating sequences of discrete tokens. A major reason lies in that the discrete outputs from the generative model make it difficult to pass the gradient update from the discriminative model to the generative model. Also, the discriminative model can only assess a complete sequence, while for a partially generated sequence, it is non-trivial to balance its current score and the future one once the entire sequence has been generated. In this paper, we propose a sequence generation framework, called SeqGAN, to solve the problems. Modeling the data generator as a stochastic policy in reinforcement learning (RL), SeqGAN bypasses the generator differentiation problem by directly performing gradient policy update. The RL reward signal comes from the GAN discriminator judged on a complete sequence, and is passed back to the intermediate state-action steps using Monte Carlo search. Extensive experiments on synthetic data and real-world tasks demonstrate significant improvements over strong baselines.

## 257. Comparison between SeqGaN and Conditional GAN Generation of Text on IMDb Movie Reviews

- Authors: Khet Khet Win; Khin Mar Soe
- Year: 2026
- DOI: 10.1109/icca69280.2026.11485771
- Venue: 
- Countries: MM
- Source: openalex
- URL: https://doi.org/10.1109/icca69280.2026.11485771

Generative Adversarial Networks (GANs) have also played a critical role in continuous generation, although this technology is not easily applicable to discrete natural language because of non-differentiability and long-range dependencies. This paper will offer an empirical comparison of SeqGAN and a simple Conditional GAN (CGAN trained on IMDB movie review dataset. Both SeqGAN and CGAN models receive exactly the same MLE pretraining and limited adversarial fine-tuning. Our models are tested with the help of BLEU, Reverse-BLEU, Self-BLEU, Distinct-n, bigram KL divergence, and, in the case of CGAN, the accuracy of our sentiment classifier. Findings indicate that the two models produce text with a high level of diversity and low overlap, BLEU scores are close to zero and distributional alignment is weak (bigram KL > 14). CGAN marginally increases diversity scores but does not do conditional generation substantially (classifier accuracy <tex xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">$\sim 49.75 \%$</tex>). Qualitative analysis demonstrates that there is a high frequency of incoherence above <tex xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">$\sim 30$</tex> tokens. The experiment found that early GAN-based text generation is still acutely underperforming on highentropy tasks, including IMDB, even with controlled and optimized training conditions, and that modern autoregressive and diffusion-based LLMs are indeed superior.

## 258. Short Text Generation Based on Adversarial Graph Attention Networks

- Authors: Meng Chen
- Year: 2021
- DOI: 10.1145/3495018.3501202
- Venue: 2021 3rd International Conference on Artificial Intelligence and Advanced Manufacture
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1145/3495018.3501202

Text generation has attracted more and more attention in the field of natural language. Recently, GAN (Generative Adversarial Networks) have been widely used in text generation, among which the GAN-based models, such as SeqGAN and SentiGAN, have shown remarkable effects in text generation. However, previous text generation models simply use CNN (Convolutional Neural Networks) as discriminators and ignore relationships between the same-label texts. Meanwhile, most models only consider using a single generator to generate a single species text, not for multispecies texts. To meet the requirements, in this paper, we propose a novel framework model-SGATGAN, which applies GAT (Generative Attention Nets) as the discriminator to establish the connection between the texts of the same type. It also provides a method of generating multispecies texts using a single generator. In this model, the graph attention neural network is used as the discriminator via the feedback to guide the generator in a specific location to generate a specific type of short text. Experimental results on two benchmarks show that our model significantly outperforms previous methods, giving state-of-the-art results in short text generation.

## 259. Toward learning better metrics for sequence generation training with policy gradient

- Authors: Joji Toyama; Yusuke Iwasawa; Kotaro Nakayama; Yutaka Matsuo
- Year: 2018
- DOI: 
- Venue: 
- Countries: JP
- Source: openalex
- URL: https://openalex.org/W2787188308

Designing a metric manually for unsupervised sequence generation tasks, such as text generation, is essentially difficult. In a such situation, learning a metric of a sequence from data is one possible solution. The previous study, SeqGAN, proposed the framework for unsupervised sequence generation, in which a metric is learned from data, and a generator is optimized with regard to the learned metric with policy gradient, inspired by generative adversarial nets (GANs) and reinforcement learning. In this paper, we make two proposals to learn better metric than SeqGAN's: partial reward function and expert-based reward function training. The partial reward function is a reward function for a partial sequence of a certain length. SeqGAN employs a reward function for completed sequence only. By combining long-scale and short-scale partial reward functions, we expect a learned metric to be able to evaluate a partial correctness as well as a coherence of a sequence, as a whole. In expert-based reward function training, a reward function is trained to discriminate between an expert (or true) sequence and a fake sequence that is produced by editing an expert sequence. Expert-based reward function training is not a kind of GAN frameworks. This makes the optimization of the generator easier. We examine the effect of the partial reward function and expert-based reward function training on synthetic data and real text data, and show improvements over SeqGAN and the model trained with MLE. Specifically, whereas SeqGAN gains 0.42 improvement of NLL over MLE on synthetic data, our best model gains 3.02 improvement, and whereas SeqGAN gains 0.029 improvement of BLEU over MLE, our best model gains 0.250 improvement.

## 260. Recurrent Convolution Attention Model (RCAM) for Text Generation based on Title

- Authors: Jianglin Yuan; Guo Zhigang; Gang Chen
- Year: 2019
- DOI: 10.1088/1742-6596/1168/5/052049
- Venue: Journal of Physics Conference Series
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1088/1742-6596/1168/5/052049
- PDF: https://doi.org/10.1088/1742-6596/1168/5/052049

Natural Language Generation (NLG) is one of the most important part in Natural Language Processing (NLP). Recently, generating text automatically with deep learning method has been improved a lot. While there are lots of defects in text generation such as the quality is not satisfied and the text of title is not clear. The paper used the recurrent convolution attention model with LSTM (Long Short-Term Memory) cells for text generation by giving a title. The result proved that it can generate sentence according with the title and make the text express more fluently. Moreover, it uses less time to train by contrast with the SeqGAN (Sequence Generative Adversarial Networks). At the same time, the result is better than other attention mechanism with LSTM models. Therefore, it has more significance for NLP research.

## 261. Text Generation Based on Generative Adversarial Nets with Latent Variable

- Authors: Heng Wang; Zengchang Qin; Tao Wan
- Year: 2017
- DOI: 10.48550/arxiv.1712.00170
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1712.00170
- PDF: https://arxiv.org/pdf/1712.00170

In this paper, we propose a model using generative adversarial net (GAN) to generate realistic text. Instead of using standard GAN, we combine variational autoencoder (VAE) with generative adversarial net. The use of high-level latent random variables is helpful to learn the data distribution and solve the problem that generative adversarial net always emits the similar data. We propose the VGAN model where the generative model is composed of recurrent neural network and VAE. The discriminative model is a convolutional neural network. We train the model via policy gradient. We apply the proposed model to the task of text generation and compare it to other recent neural network based models, such as recurrent neural network language model and SeqGAN. We evaluate the performance of the model by calculating negative log-likelihood and the BLEU score. We conduct experiments on three benchmark datasets, and results show that our model outperforms other previous models.

## 262. An Approach to Generate Topic Similar Document by Seed Extraction-Based SeqGAN Training for Bait Document

- Authors: Shuanshuan Pang; Wenjia Niu; Jiqiang Liu; Yingxiao Xiang; Yingdi Wang
- Year: 2018
- DOI: 10.1109/dsc.2018.00129
- Venue: 
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/dsc.2018.00129

In recent years, topic similar document generation has drawn more and more attention in both academia and industry. Especially, bait document generation is very important for security. For more-like and fast bait document generation, we proposed the topic similar document generation model based on SeqGAN model (TSDG-SeqGAN). In the training phrase, we used jieba word segmentation tool for training text to greatly reduce the training time. In the generation phrase, we extract keywords and key sentence from the subject document as seeds, and then enter the seeds into the trained generation network. Next, we get keyword-based documents and documents based on key sentences from generation network. Finally, we output documents that are most similar to the subject document as the final result. Experiments show the effectiveness of our model.

## 263. Evaluating Prompt Injection Attacks with LSTM-Based Generative Adversarial Networks: A Lightweight Alternative to Large Language Models

- Authors: Sharaf Rashid; Edson Bollis; Lucas Francisco Amaral Orosco Pellicer; Darian Rabbani; Rafael Palacios; Aneesh Gupta; Aneesh Gupta; Amar Gupta; Amar Gupta
- Year: 2025
- DOI: 10.3390/make7030077
- Venue: Machine Learning and Knowledge Extraction
- Countries: BR; ES; US
- Source: openalex
- URL: https://doi.org/10.3390/make7030077
- PDF: https://www.mdpi.com/2504-4990/7/3/77/pdf?version=1754474437

Generative Adversarial Networks (GANs) using Long Short-Term Memory (LSTM) provide a computationally cheaper approach for text generation compared to large language models (LLMs). The low hardware barrier of training GANs poses a threat because it means more bad actors may use them to mass-produce prompt attack messages against LLM systems. Thus, to better understand the threat of GANs being used for prompt attack generation, we train two well-known GAN architectures, SeqGAN and RelGAN, on prompt attack messages. For each architecture, we evaluate generated prompt attack messages, comparing results with each other, with generated attacks from another computationally cheap approach, a 1-billion-parameter Llama 3.2 small language model (SLM), and with messages from the original dataset. This evaluation suggests that GAN architectures like SeqGAN and RelGAN have the potential to be used in conjunction with SLMs to readily generate malicious prompts that impose new threats against LLM-based systems such as chatbots. Analyzing the effectiveness of state-of-the-art defenses against prompt attacks, we also find that GAN-generated attacks can deceive most of these defenses with varying levels of success with the exception of Meta’s PromptGuard. Further, we suggest an improvement of prompt attack defenses based on the analysis of the language quality of the prompts, which we found to be the weakest point of GAN-generated messages.

## 264. A Framework for Few-Shot Network Threats Based on Generative Adversarial Networks

- Authors: Long Chen; Yanqing Song; Jianguo Chen
- Year: 2023
- DOI: 10.1109/iscc58397.2023.10217901
- Venue: 
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/iscc58397.2023.10217901

A small amount of malicious logs is confusing and unbalanced for a large number of normal logs. We proposed a framework of network threats sample based on Generative Adversarial Networks(GAN). This paper solves the imbalance problem of multidimensional sample data such as logs, traffic, programs, and feature spaces in the field of cyberspace security by generating confrontation networks. We carried out a large-scale confrontation generation experiment of security event logs based on SeqGAN and generated corresponding log text for data enhancement, which effectively solve the problem of few-shot. The results in this section show that the use of the AC-GAN augmentation dataset is enhanced compared to the original non-equilibrium dataset using the artificial synthesis of the SMOTE dataset Network traffic data set to improve the performance of supervised learning classification. It has inestimable effects on threat detection, various types of offensive to defensive, and cryptography algorithms.

## 265. Differentiated Distribution Recovery for Neural Text Generation

- Authors: Jianing Li; Yanyan Lan; Jiafeng Guo; Jun Xu; Xueqi Cheng
- Year: 2019
- DOI: 10.1609/aaai.v33i01.33016682
- Venue: Proceedings of the AAAI Conference on Artificial Intelligence
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1609/aaai.v33i01.33016682
- PDF: https://ojs.aaai.org/index.php/AAAI/article/download/4639/4517

Neural language models based on recurrent neural networks (RNNLM) have significantly improved the performance for text generation, yet the quality of generated text represented by Turing Test pass rate is still far from satisfying. Some researchers propose to use adversarial training or reinforcement learning to promote the quality, however, such methods usually introduce great challenges in the training and parameter tuning processes. Through our analysis, we find the problem of RNNLM comes from the usage of maximum likelihood estimation (MLE) as the objective function, which requires the generated distribution to precisely recover the true distribution. Such requirement favors high generation diversity which restricted the generation quality. This is not suitable when the overall quality is low, since high generation diversity usually indicates lot of errors rather than diverse good samples. In this paper, we propose to achieve differentiated distribution recovery, DDR for short. The key idea is to make the optimal generation probability proportional to the β-th power of the true probability, where β &gt; 1. In this way, the generation quality can be greatly improved by sacrificing diversity from noises and rare patterns. Experiments on synthetic data and two public text datasets show that our DDR method achieves more flexible quality-diversity trade-off and higher Turing Test pass rate, as compared with baseline methods including RNNLM, SeqGAN and LeakGAN.

## 266. ReGAN: RE[LAX|BAR|INFORCE] based Sequence Generation using GANs

- Authors: Aparna Balagopalan; Satya Krishna Gorti; Mathieu Ravaut; Raeid Saqur
- Year: 2018
- DOI: 10.48550/arxiv.1805.02788
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1805.02788
- PDF: https://arxiv.org/pdf/1805.02788

Generative Adversarial Networks (GANs) have seen steep ascension to the peak of ML research zeitgeist in recent years. Mostly catalyzed by its success in the domain of image generation, the technique has seen wide range of adoption in a variety of other problem domains. Although GANs have had a lot of success in producing more realistic images than other approaches, they have only seen limited use for text sequences. Generation of longer sequences compounds this problem. Most recently, SeqGAN (Yu et al., 2017) has shown improvements in adversarial evaluation and results with human evaluation compared to a MLE based trained baseline. The main contributions of this paper are three-fold: 1. We show results for sequence generation using a GAN architecture with efficient policy gradient estimators, 2. We attain improved training stability, and 3. We perform a comparative study of recent unbiased low variance gradient estimation techniques such as REBAR (Tucker et al., 2017), RELAX (Grathwohl et al., 2018) and REINFORCE (Williams, 1992). Using a simple grammar on synthetic datasets with varying length, we indicate the quality of sequences generated by the model.

## 267. Data Augmentation for Sentiment Analysis Using Sentence Compression-Based SeqGAN With Data Screening

- Authors: Jiawei Luo; Mondher Bouazizi; Tomoaki Ohtsuki
- Year: 2021
- DOI: 10.1109/access.2021.3094023
- Venue: IEEE Access
- Countries: JP
- Source: openalex
- URL: https://doi.org/10.1109/access.2021.3094023
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/9312710/09469749.pdf

Sentiment analysis refers to the process of automatically identifying the emotions expressed by people. Its accuracy is highly dependent on the amount of training data. However, it takes time and cost for humans to collect a large number of data. Many research works used generative models to generate a large amount of data based on a small amount of data for sentiment analysis. However, training on long texts and inaccurate sentiment information that might be generated are two severe challenges. It is difficult to improve the sentiment analysis accuracy effectively. In this paper, we propose a novel data augmentation framework based on Sequence generative adversarial networks (SeqGAN) to improve the sentiment analysis accuracy when the dataset already has a certain amount of data and contains long texts. Penalty-based SeqGAN is used to generate high-quality and diversified text data. Long short-term memory (LSTM) networks with attention mechanisms are used to conduct sentence compression for the training data of SeqGAN. A sentiment dictionary is used to retain the sentiment words for compressed data. We also propose a data screening method to obtain more accurate data from the generated data. The results of the usability, novelty, and diversity of the generated data show that the proposed sentence compression method can help SeqGAN learn more information from the long text data. The data generated by the proposed framework improve the classification accuracy of four classifiers applied on two distinct text datasets.

## 268. Learning to Encode Text as Human-Readable Summaries using Generative Adversarial Networks

- Authors: Yau-Shian Wang; Hung-yi Lee
- Year: 2018
- DOI: 10.18653/v1/d18-1451
- Venue: 
- Countries: TW
- Source: openalex
- URL: https://doi.org/10.18653/v1/d18-1451
- PDF: https://www.aclweb.org/anthology/D18-1451.pdf

Auto-encoders compress input data into a latent-space representation and reconstruct the original data from the representation. This latent representation is not easily interpreted by humans. In this paper, we propose training an auto-encoder that encodes input text into human-readable sentences, and unpaired abstractive summarization is thereby achieved. The auto-encoder is composed of a generator and a reconstructor. The generator encodes the input text into a shorter word sequence, and the reconstructor recovers the generator input from the generator output. To make the generator output human-readable, a discriminator restricts the output of the generator to resemble human-written sentences. By taking the generator output as the summary of the input text, abstractive summarization is achieved without document-summary pairs as training data. Promising results are shown on both English and Chinese corpora.

## 269. Retracted: SeqGAN-APG: Sequential Generative Adversarial Networks for Automatic Patch Generation

- Authors: Dhruv Gargi; Raghuvar Arora
- Year: 2021
- DOI: 10.1109/stcr51658.2021.9587929
- Venue: 2021 Smart Technologies, Communication and Robotics (STCR)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/stcr51658.2021.9587929

## 270. Retraction Notice: SeqGAN-APG: Sequential Generative Adversarial Networks for Automatic Patch Generation

- Authors: Dhruv Gargi; Raghuvar Arora
- Year: 2021
- DOI: 10.1109/stcr51658.2021.10339795
- Venue: 2021 Smart Technologies, Communication and Robotics (STCR)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/stcr51658.2021.10339795

## 271. Emotional Human Machine Conversation Generation Based on SeqGAN

- Authors: Xiao Sun; Xinmiao Chen; Zhengmeng Pei; Fuji Ren
- Year: 2018
- DOI: 10.1109/aciiasia.2018.8470388
- Venue: 2018 First Asian Conference on Affective Computing and Intelligent Interaction (ACII Asia)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/aciiasia.2018.8470388

## 272. A novel oversampling method based on SeqGAN for imbalanced text classification

- Authors: Yin Luo; Haishan Feng; Xuanlong Weng; Ke Huang; Huang Zheng
- Year: 2019
- DOI: 10.1109/bigdata47090.2019.9006138
- Venue: 2019 IEEE International Conference on Big Data (Big Data)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/bigdata47090.2019.9006138

## 273. A Novel SeqGAN-LSTM Load Forecasting Framework for Electric Vehicle Charging Stations with Missing Data

- Authors: Xiaohai Ge; Xin Zhang; Dehong Xu
- Year: 2024
- DOI: 10.1109/pedg61800.2024.10667370
- Venue: 2024 IEEE 15th International Symposium on Power Electronics for Distributed Generation Systems (PEDG)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/pedg61800.2024.10667370

## 274. Poetry Generation for Indonesian Pantun: Comparison Between SeqGAN and GPT-2

- Authors: Emmanuella Anggi Siallagan; Ika Alfina
- Year: 2023
- DOI: 10.21609/jiki.v16i1.1113
- Venue: Jurnal Ilmu Komputer dan Informasi
- Countries: 
- Source: crossref
- URL: https://doi.org/10.21609/jiki.v16i1.1113
- PDF: https://jiki.cs.ui.ac.id/index.php/jiki/article/download/1113/488

<jats:p>Pantun is a traditional Malay poem consisting of four lines: two lines of deliverance and two lines of messages. Each ending-line word in pantun forms an ABAB rhyme pattern. In this work, we compare the performance of Sequence Generative Adversarial Nets (SeqGAN) and Generative Pre-trained Transformer 2 (GPT-2) in automatically generating Indonesian pantun. We also created the first publicly available Indonesian pantun dataset that consists of 7.8K pantun. We evaluated how well each model produced pantun by its lexical richness and its formedness. We introduced the evaluation of pantun with two aspects: structure and rhyme. GPT-2 performs better with a margin of 29.40% than SeqGAN in forming the structure, 35.20% better in making rhyming patterns, and 0.04 difference in giving richer vocabulary to its generated pantun.</jats:p>

## 275. Research on Data Generation Model Based on Improved SeqGAN

- Authors: Jian Dou; Shuang Qie; Jizhe Lu; Yi Ren
- Year: 2021
- DOI: 10.1145/3457784.3457791
- Venue: 2021 10th International Conference on Software and Computer Applications
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1145/3457784.3457791

## 276. En-SeqGAN: An Efficient Sequence Generation Model for Deceiving URL Classifiers

- Authors: Tuan Dung Pham; Thi Thanh Thuy Pham; Viet Cuong Ta
- Year: 2022
- DOI: 10.1007/978-981-19-8234-7_37
- Venue: Communications in Computer and Information Science
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1007/978-981-19-8234-7_37

## 277. Variable speed trajectory prediction method of dynamic prosthesis based on improved SeqGAN

- Authors: Haowei Han; Honglei An; Hongxu Ma; Qing Wei
- Year: 2021
- DOI: 10.1109/cac53003.2021.9727962
- Venue: 2021 China Automation Congress (CAC)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/cac53003.2021.9727962

## 278. ENIPFuzz: A SeqGAN-based EtherNet/IP Protocol Fuzzing Test Framework

- Authors: Honggang Wu; Li Gong; Ao Liu; Yi Zhang; Jianwei Yang
- Year: 2022
- DOI: 10.1109/icet55676.2022.9824256
- Venue: 2022 IEEE 5th International Conference on Electronics Technology (ICET)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/icet55676.2022.9824256

## 279. A Binary Protocol Fuzzing Method Based on SeqGAN

- Authors: Yihao Li; Shenmei Zhang; Lifa Wu; Peihong Lin; Zhenji Zhou
- Year: 2020
- DOI: 10.1109/itaic49862.2020.9339152
- Venue: 2020 IEEE 9th Joint International Information Technology and Artificial Intelligence Conference (ITAIC)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/itaic49862.2020.9339152

## 280. Symbolic Music Generation with Transformer-GANs

- Authors: Aashiq Muhamed; Liang Li; Xingjian Shi; Suri Yaddanapudi; Wayne Chi; Dylan Jackson; Rahul Suresh; Zachary C. Lipton; Alex Smola
- Year: 2021
- DOI: 10.1609/aaai.v35i1.16117
- Venue: Proceedings of the AAAI Conference on Artificial Intelligence
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1609/aaai.v35i1.16117
- PDF: https://ojs.aaai.org/index.php/AAAI/article/download/16117/15924

Autoregressive models using Transformers have emerged as the dominant approach for music generation with the goal of synthesizing minute-long compositions that exhibit large-scale musical structure. These models are commonly trained by minimizing the negative log-likelihood (NLL) of the observed sequence in an autoregressive manner. Unfortunately, the quality of samples from these models tends to degrade significantly for long sequences, a phenomenon attributed to exposure bias. Fortunately, we are able to detect these failures with classifiers trained to distinguish between real and sampled sequences, an observation that motivates our exploration of adversarial losses to complement the NLL objective. We use a pre-trained Span-BERT model for the discriminator of the GAN, which in our experiments helped with training stability. We use the Gumbel-Softmax trick to obtain a differentiable approximation of the sampling process. This makes discrete sequences amenable to optimization in GANs. In addition, we break the sequences into smaller chunks to ensure that we stay within a given memory budget. We demonstrate via human evaluations and a new discriminative metric that the music generated by our approach outperforms a baseline trained with likelihood maximization, the state-of-the-art Music Transformer, and other GANs used for sequence generation. 57% of people prefer music generated via our approach while 43% prefer Music Transformer.

## 281. TILGAN: Transformer-based Implicit Latent GAN for Diverse and Coherent Text Generation

- Authors: Shizhe Diao; Xinwei Shen; Kashun Shum; Yan Song; Tong Zhang
- Year: 2021
- DOI: 10.18653/v1/2021.findings-acl.428
- Venue: 
- Countries: CN; HK
- Source: openalex
- URL: https://doi.org/10.18653/v1/2021.findings-acl.428
- PDF: https://aclanthology.org/2021.findings-acl.428.pdf

Conventional autoregressive models have achieved great success in text generation but suffer from the exposure bias problem in that token sequences in the training and in the generation stages are mismatched. While generative adversarial networks (GANs) can remedy this problem, existing implementations of GANs directly on discrete outputs tend to be unstable and lack diversity. In this work, we propose TILGAN, a Transformerbased Implicit Latent GAN, which combines a Transformer autoencoder and GAN in the latent space with a novel design and distribution matching based on the Kullback-Leibler (KL) divergence. Specifically, to improve local and global coherence, we explicitly introduce a multi-scale discriminator to capture the semantic information at varying scales among the sequence of hidden representations encoded by Transformer. Moreover, the decoder is enhanced by an additional KL loss to be consistent with the latent-generator. Experimental results on three benchmark datasets demonstrate the validity and effectiveness of our model, by obtaining significant improvements and a better quality-diversity trade-off in automatic and human evaluation for both unconditional and conditional generation tasks.

## 282. Feature-aware conditional GAN for category text generation

- Authors: Xinze Li; Kezhi Mao; Fanfan Lin; Zijian Feng
- Year: 2023
- DOI: 10.1016/j.neucom.2023.126352
- Venue: Neurocomputing
- Countries: SG
- Source: openalex
- URL: https://doi.org/10.1016/j.neucom.2023.126352
- PDF: https://arxiv.org/pdf/2308.00939

## 283. Data augmentation of credit default swap transactions based on a sequence GAN

- Authors: Fan Xi; Xin Guo; Qi Chen; Yishuang Chen; Tongyao Wang; Yuxin Zhang
- Year: 2022
- DOI: 10.1016/j.ipm.2022.102889
- Venue: Information Processing & Management
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1016/j.ipm.2022.102889
- PDF: https://doi.org/10.1016/j.ipm.2022.102889

Credit default swap transaction data repositories are frequently applied with credit default swap spread estimation and financial market risk assessment. However, in practical applications, there is poor liquidity, some missing data, and inaccurate definitions. Small samples tend to lead to poor prediction accuracy and poor adaptability of the statistical algorithm. Data generation can effectively increase the sample size and improve the effect of the risk assessment model. In this paper, a credit default swap data generation algorithm based on a sequence generative adversarial network (SeqGAN) is proposed, and the policy gradient algorithm in reinforcement learning is introduced to optimize the traditional generative adversarial network (GAN) algorithm to solve the gradient disappearance and poor data adaptability problems in the traditional algorithm. Gradient disappearance is due to the generator network in GAN being designed to be able to adjust the output continuously, which does not work on discrete data generation. The optimization algorithm proposed in this paper is used to train randomly distributed sequence data and generate credit default swap transactions with diversity and good model applicability. The credit default swap data generated in this paper are verified by the synthetic ranking agreement (SRA) index. The results show that SeqGAN can effectively synthesize various simulation samples, which can provide support for the risk discrimination model.

## 284. Packet-Level Adversarial Network Traffic Crafting using Sequence Generative Adversarial Networks

- Authors: Qiumei Cheng; Shiying Zhou; Yi Shen; Dezhang Kong; Chunming Wu
- Year: 2021
- DOI: 10.48550/arxiv.2103.04794
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2103.04794
- PDF: https://arxiv.org/pdf/2103.04794

The surge in the internet of things (IoT) devices seriously threatens the current IoT security landscape, which requires a robust network intrusion detection system (NIDS). Despite superior detection accuracy, existing machine learning or deep learning based NIDS are vulnerable to adversarial examples. Recently, generative adversarial networks (GANs) have become a prevailing method in adversarial examples crafting. However, the nature of discrete network traffic at the packet level makes it hard for GAN to craft adversarial traffic as GAN is efficient in generating continuous data like image synthesis. Unlike previous methods that convert discrete network traffic into a grayscale image, this paper gains inspiration from SeqGAN in sequence generation with policy gradient. Based on the structure of SeqGAN, we propose Attack-GAN to generate adversarial network traffic at packet level that complies with domain constraints. Specifically, the adversarial packet generation is formulated into a sequential decision making process. In this case, each byte in a packet is regarded as a token in a sequence. The objective of the generator is to select a token to maximize its expected end reward. To bypass the detection of NIDS, the generated network traffic and benign traffic are classified by a black-box NIDS. The prediction results returned by the NIDS are fed into the discriminator to guide the update of the generator. We generate malicious adversarial traffic based on a real public available dataset with attack functionality unchanged. The experimental results validate that the generated adversarial samples are able to deceive many existing black-box NIDS.

## 285. Adversarial Discrete Sequence Generation without Explicit NeuralNetworks as Discriminators

- Authors: Zhongliang Li; Tian Xia; Xingyu Lou; Kaihe Xu; Shaojun Wang; Jing Xiao
- Year: 2019
- DOI: 
- Venue: 
- Countries: US
- Source: openalex
- URL: https://openalex.org/W2921705182

This paper presents a novel approach to train GANs for discrete sequence generation without resorting to an explicit neural network as the discriminator. We show that when an alternative mini-max optimization procedure is performed for the value function where a closed form solution for the discriminator exists in the maximization step, it is equivalent to directly optimizing the Jenson-Shannon divergence (JSD) between the generator’s distribution and the empirical distribution over the training data without sampling from the generator, thus optimizing the JSD becomes computationally tractable to train the generator that generates sequences of discrete data. Extensive experiments on synthetic data and real-world tasks demonstrate significant improvements over existing methods to train GANs that generate discrete sequences.

## 286. CST-GANs: A Generative Adversarial Network Based on CST Parameterization for the Generation of Smooth Airfoils

- Authors: Jinxing Lin; Chenliang Zhang; Xiaoye Xie; Xingyu Shi; Xiaoyu Xu; Yanhui Duan
- Year: 2022
- DOI: 10.1109/icus55513.2022.9987080
- Venue: 2022 IEEE International Conference on Unmanned Systems (ICUS)
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/icus55513.2022.9987080

Generative adversarial networks (GANs) are well-known for their powerful generation ability. In recent years, GANs have been applied in the field of aerodynamic shape optimization (ASO). However, the existing airfoil generation methods based on GANs can only generate a discrete sequence of coordinates corresponding to fixed abscissas, and cannot be applied to the scenarios that generate airfoils directly. In this paper, class function / shape function transformation (CST), a parameterization method of the airfoil that forms a good representation of the geometric shape of the airfoil, is combined with GANs. Therefore, a CST-GANs method is proposed that can directly generate the CST parameterized variables of the airfoil instead of a sequence of airfoil points. Given the abscissa and parameterized variables, the corresponding coordinate can be calculated by CST expression. On the other hand, CST-GANs can generate airfoil geometry with smooth surface without intro-ducing the Bézier curve or the Savitzky-Golay filter. Experiments show that CST-GANs is a promising model, which can not only generate smoother airfoils with fewer neural network parameters but also generate more diverse airfoils.

## 287. Polyphonic Music Generation with Sequence Generative Adversarial Networks

- Authors: Sang-gil Lee; Uiwon Hwang; Seonwoo Min; Sungroh Yoon
- Year: 2017
- DOI: 10.48550/arxiv.1710.11418
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1710.11418
- PDF: https://arxiv.org/pdf/1710.11418

We propose an application of sequence generative adversarial networks (SeqGAN), which are generative adversarial networks for discrete sequence generation, for creating polyphonic musical sequences. Instead of a monophonic melody generation suggested in the original work, we present an efficient representation of a polyphony MIDI file that simultaneously captures chords and melodies with dynamic timings. The proposed method condenses duration, octaves, and keys of both melodies and chords into a single word vector representation, and recurrent neural networks learn to predict distributions of sequences from the embedded musical word space. We experiment with the original method and the least squares method to the discriminator, which is known to stabilize the training of GANs. The network can create sequences that are musically coherent and shows an improved quantitative and qualitative measures. We also report that careful optimization of reinforcement learning signals of the model is crucial for general application of the model.

## 288. ACtuAL: Actor-Critic Under Adversarial Learning

- Authors: Anirudh Goyal; Nan Rosemary Ke; Alex Lamb; R Devon Hjelm; Chris Pal; Joëlle Pineau; Yoshua Bengio
- Year: 2017
- DOI: 10.48550/arxiv.1711.04755
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1711.04755
- PDF: https://arxiv.org/pdf/1711.04755

Generative Adversarial Networks (GANs) are a powerful framework for deep generative modeling. Posed as a two-player minimax problem, GANs are typically trained end-to-end on real-valued data and can be used to train a generator of high-dimensional and realistic images. However, a major limitation of GANs is that training relies on passing gradients from the discriminator through the generator via back-propagation. This makes it fundamentally difficult to train GANs with discrete data, as generation in this case typically involves a non-differentiable function. These difficulties extend to the reinforcement learning setting when the action space is composed of discrete decisions. We address these issues by reframing the GAN framework so that the generator is no longer trained using gradients through the discriminator, but is instead trained using a learned critic in the actor-critic framework with a Temporal Difference (TD) objective. This is a natural fit for sequence modeling and we use it to achieve improvements on language modeling tasks over the standard Teacher-Forcing methods.

## 289. Robotic Musicianship Based on Least Squares and Sequence Generative Adversarial Networks

- Authors: Mu‐Yen Chen; Wei Wei; Han‐Chieh Chao; Yi-Fen Li
- Year: 2021
- DOI: 10.1109/jsen.2021.3066200
- Venue: IEEE Sensors Journal
- Countries: TW
- Source: openalex
- URL: https://doi.org/10.1109/jsen.2021.3066200

Robotic musicianship research aims to the configuration of robots can analyze, reason, and generate music autonomous. The goal of this research is to achieve the inspiring and meaningful musical interactions between humans and artificially creative robots. This research presents a new model of automatic music generation which is based on least squares and generative adversarial networks (GANs). This research specifies classical piano as the music source and uses the sensors as the context-awareness technology to sense and receive the input audio in human-robot interaction. Therefore, this research applies sequence generation adversarial network (SeqGAN) techniques that are better able to address discrete issues in generating samples of classical piano melodies and datasets. Modifying the SeqGAN approach, this research presented the Least Squares SeqGAN (LS-SeqGAN) method to create melody units on different chords and generates a set of music pieces as testing dataset. In this research, we implement the original method and use the least squares method to stabilize the training of GANs. The performance evaluation shows that proposed LS-SeqGAN method can fulfill the need both of music quality and creativity. It offers a robust infrastructure for the human-robotic interaction that can be used to promote the related robotic applications.

## 290. SFCWGAN-BiTCN with Sequential Features for Malware Detection

- Authors: Bona Xuan; Jin Li; Yafei Song
- Year: 2023
- DOI: 10.3390/app13042079
- Venue: Applied Sciences
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.3390/app13042079
- PDF: https://www.mdpi.com/2076-3417/13/4/2079/pdf?version=1676558002

In the field of adversarial attacks, the generative adversarial network (GAN) has shown better performance. There have been few studies applying it to malware sample supplementation, due to the complexity of handling discrete data. More importantly, unbalanced malware family samples interfere with the analytical power of malware detection models and mislead malware classification. To address the problem of the impact of malware family imbalance on accuracy, a selection feature conditional Wasserstein generative adversarial network (SFCWGAN) and bidirectional temporal convolutional network (BiTCN) are proposed. First, we extract the features of malware Opcode and API sequences and use Word2Vec to represent features, emphasizing the semantic logic between API tuning and Opcode calling sequences. Second, the Spearman correlation coefficient and the whale optimization algorithm extreme gradient boosting (WOA-XGBoost) algorithm are combined to select features, filter out invalid features, and simplify structure. Finally, we propose a GAN-based sequence feature generation algorithm. Samples were generated using the conditional Wasserstein generative adversarial network (CWGAN) on the imbalanced malware family dataset, added to the trainset to supplement the samples, and trained on BiTCN. In comparison, in tests on the Kaggle and DataCon datasets, the model achieved detection accuracies of 99.56% and 96.93%, respectively, which were 0.18% and 2.98% higher than the models of other methods.

## 291. SocialInteractionGAN: Multi-Person Interaction Sequence Generation

- Authors: Louis Airale; Dominique Vaufreydaz; Xavier Alameda-Pineda
- Year: 2022
- DOI: 10.1109/taffc.2022.3171719
- Venue: IEEE Transactions on Affective Computing
- Countries: FR
- Source: openalex
- URL: https://doi.org/10.1109/taffc.2022.3171719
- PDF: https://arxiv.org/pdf/2103.05916

Prediction of human actions in social interactions has important applications in the design of social robots or artificial avatars. In this paper, we focus on a unimodal representation of interactions and propose to tackle interaction generation in a data-driven fashion. In particular, we model human interaction generation as a discrete multi-sequence generation problem and present SocialInteractionGAN, a novel adversarial architecture for conditional interaction generation. Our model builds on a recurrent encoder-decoder generator network and a dual-stream discriminator, that jointly evaluates the realism of interactions and individual action sequences and operates at different time scales. Crucially, contextual information on interacting participants is shared among agents and reinjected in both the generation and the discriminator evaluation processes. Experiments show that albeit dealing with low dimensional data, SocialInteractionGAN succeeds in producing high realism action sequences of interacting people, comparing favorably to a diversity of recurrent and convolutional discriminator baselines, and we argue that this work will constitute a first stone towards higher dimensional and multimodal interaction generation. Evaluations are conducted using classical GAN metrics, that we specifically adapt for discrete sequential data. Our model is shown to properly learn the dynamics of interaction sequences, while exploiting the full range of available actions.

## 292. Electrocardiogram generation with a bidirectional LSTM-CNN generative adversarial network

- Authors: Fei Zhu; Fei Ye; Yuchen Fu; Quan Liu; Bairong Shen
- Year: 2019
- DOI: 10.1038/s41598-019-42516-z
- Venue: Scientific Reports
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1038/s41598-019-42516-z
- PDF: https://www.nature.com/articles/s41598-019-42516-z.pdf

Heart disease is a malignant threat to human health. Electrocardiogram (ECG) tests are used to help diagnose heart disease by recording the heart's activity. However, automated medical-aided diagnosis with computers usually requires a large volume of labeled clinical data without patients' privacy to train the model, which is an empirical problem that still needs to be solved. To address this problem, we propose a generative adversarial network (GAN), which is composed of a bidirectional long short-term memory(LSTM) and convolutional neural network(CNN), referred as BiLSTM-CNN,to generate synthetic ECG data that agree with existing clinical data so that the features of patients with heart disease can be retained. The model includes a generator and a discriminator, where the generator employs the two layers of the BiLSTM networks and the discriminator is based on convolutional neural networks. The 48 ECG records from individuals of the MIT-BIH database were used to train the model. We compared the performance of our model with two other generative models, the recurrent neural network autoencoder(RNN-AE) and the recurrent neural network variational autoencoder (RNN-VAE). The results showed that the loss function of our model converged to zero the fastest. We also evaluated the loss of the discriminator of GANs with different combinations of generator and discriminator. The results indicated that BiLSTM-CNN GAN could generate ECG data with high morphological similarity to real ECG recordings.

## 293. A Fault Data Generation Algorithm Based on GAN and Policy Gradient Mechanism

- Authors: Yonghua Huo; Yingjun Shang; Bo Xu; Yuting Li; Yang Yang
- Year: 2021
- DOI: 10.1109/bmsb53066.2021.9547152
- Venue: 
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/bmsb53066.2021.9547152

Generative adversarial networks(GAN) are widely used in various fields. However, when generating text data with contextual correlation characteristics such as fault data, GAN has many limitations. On the one hand, discrete data output makes it difficult to pass gradient updates from the discriminator to the generator; on the other hand, it is difficult for the discriminator to process incompletely generated sequences. In this paper, we propose a fault data generation algorithm based on GAN and policy gradient mechanism. Using the reinforcement learning method aims to solve the gradient update transfer problem, and the policy gradient algorithm is used to directly update the parameters of the generator; at the same time, by using the Upper Confidence Bound Apply to Tree(UCT) algorithm to simulate the incomplete sequence into a complete sequence so that the discriminator can evaluate its reward value. The simulation results show that our fault data generation algorithm based on GAN and policy gradient mechanism performs better in the fault data generation task.

## 294. Self-Attention Mechanism in GANs for Molecule Generation

- Authors: Sandeep Chinnareddy; Pranav Grandhi; Apurva Narayan
- Year: 2021
- DOI: 10.1109/icmla52953.2021.00017
- Venue: 2021 20th IEEE International Conference on Machine Learning and Applications (ICMLA)
- Countries: CA; IN
- Source: openalex
- URL: https://doi.org/10.1109/icmla52953.2021.00017

In discrete sequence based Generative Adversarial Networks (GANs), it is important to both land the samples in the initial distribution and drive the generation towards desirable properties. However, in the case of longer molecules, the existing models seem to under-perform in producing new molecules. In this work, we propose the use of Self-Attention mechanism for Generative Adversarial Networks to allow long range dependencies. Self-Attention mechanism has produced improved rewards in novelty and promising results in generating molecules.

## 295. A de novo molecular generation method using latent vector based generative adversarial network

- Authors: Oleksii Prykhodko; Simon Johansson; Panagiotis-Christos Kotsias; Josep Arús‐Pous; Esben Jannik Bjerrum; Ola Engkvist; Hongming Chen
- Year: 2019
- DOI: 10.1186/s13321-019-0397-9
- Venue: Journal of Cheminformatics
- Countries: CH; CN; DE; FI; JP; SE
- Source: openalex
- URL: https://doi.org/10.1186/s13321-019-0397-9
- PDF: https://jcheminf.biomedcentral.com/track/pdf/10.1186/s13321-019-0397-9

Deep learning methods applied to drug discovery have been used to generate novel structures. In this study, we propose a new deep learning architecture, LatentGAN, which combines an autoencoder and a generative adversarial neural network for de novo molecular design. We applied the method in two scenarios: one to generate random drug-like compounds and another to generate target-biased compounds. Our results show that the method works well in both cases. Sampled compounds from the trained model can largely occupy the same chemical space as the training set and also generate a substantial fraction of novel compounds. Moreover, the drug-likeness score of compounds sampled from LatentGAN is also similar to that of the training set. Lastly, generated compounds differ from those obtained with a Recurrent Neural Network-based generative model approach, indicating that both methods can be used complementarily.

## 296. GaitSyn-GAN: Synthetic Gait Sequence Generation for Improved Cross-View Generalisation

- Authors: Pranesh Vijayakumar; N. Sivakumar
- Year: 2026
- DOI: 10.1109/ccic68129.2026.11486247
- Venue: 2026 Contemporary Computing Innovations Conference (CCIC)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/ccic68129.2026.11486247

## 297. Design of an Improved Model for Music Sequence Generation Using Conditional Variational Autoencoder and Conditional GAN

- Authors: Pallavi Ganorkar; Anagha Rathkanthiwar
- Year: 2024
- DOI: 10.1109/idicaiei61867.2024.10842669
- Venue: 2024 2nd DMIHER International Conference on Artificial Intelligence in Healthcare, Education and Industry (IDICAIEI)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/idicaiei61867.2024.10842669

## 298. ULME-GAN: a generative adversarial network for micro-expression sequence generation

- Authors: Ju Zhou; Sirui Sun; Haolin Xia; Xinyu Liu; Hanpu Wang; Tong Chen
- Year: 2023
- DOI: 10.1007/s10489-023-05213-z
- Venue: Applied Intelligence
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1007/s10489-023-05213-z
- PDF: https://link.springer.com/content/pdf/10.1007/s10489-023-05213-z.pdf

## 299. Generate Sequence Data using Reinforcement Learning with GAN

- Authors: Maria Wang
- Year: 2023
- DOI: 10.31237/osf.io/ny4h8
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.31237/osf.io/ny4h8

<p>This paper is based on the framework of SeqGAN[1]. I am trying to implement some simple improvements on it. SeqGAN is an algorithm to generate sequences of discrete tokens, which is widely used in NLP. Modeling the data generator as a stochastic policy in reinforcement learning (RL), SeqGAN bypasses the generator differentiation problem by directly performing gradient policy update. The RL reward signal comes from the GAN discriminator judged on a complete sequence, and is passed back to the intermediate state-action steps using Monte Carlo search. It uses REINFORCE to get the gradient of the objective function. There are some possible places that could be improved. I considered WGAN which uses Earth Mover's distance instead of KL divergece which might provide a better guidance for the generator to improve. We consider proximal policy optimization as well to help the generator get a better performance.</p>

## 300. Adversarial Machine Learning in Text Processing: A Literature Survey

- Authors: Izzat Alsmadi; Nura Aljaafari; Mahmoud Nazzal; Shadan Alhamed; Ahmad Sawalmeh; Conrado P. Vizcarra; Abdallah Khreishah; Muhammad Anan; Abdulelah Algosaibi; Mohammed Al-Naeem; Adel Aldalbahi; Abdulaziz Alhumam
- Year: 2022
- DOI: 10.1109/access.2022.3146405
- Venue: IEEE Access
- Countries: SA; US
- Source: openalex
- URL: https://doi.org/10.1109/access.2022.3146405
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/9668973/09693527.pdf

Machine learning algorithms represent the intelligence that controls many information systems and applications around us. As such, they are targeted by attackers to impact their decisions. Text created by machine learning algorithms has many types of applications, some of which can be considered malicious especially if there is an intention to present machine-generated text as human-generated. In this paper, we surveyed major subjects in adversarial machine learning for text processing applications. Unlike adversarial machine learning in images, text problems and applications are heterogeneous. Thus, each problem can have its own challenges. We focused on some of the evolving research areas such as: malicious versus genuine text generation metrics, defense against adversarial attacks, and text generation models and algorithms. Our study showed that as applications of text generation will continue to grow in the near future, the type and nature of attacks on those applications and their machine learning algorithms will continue to grow as well. Literature survey indicated an increasing trend in using pre-trained models in machine learning. Word/sentence embedding models and transformers are examples of those pre-trained models. Adversarial models may utilize same or similar pre-trained models as well. In another trend related to text generation models, literature showed effort to develop universal text perturbations to be used in both black-and white-box attack settings. Literature showed also using conditional GANs to create latent representation for writing types. This usage will allow for a seamless lexical and grammatical transition between various writing styles. In text generation metrics, research trends showed developing successful automated or semi-automated assessment metrics that may include human judgement. Literature showed also research trends of designing and developing new memory models that increase performance and memory utilization efficiency without validating real-time constraints. Many research efforts evaluate different defense model approaches and algorithms. Researchers evaluated different types of targeted attacks, and methods to distinguish human versus machine generated text.

## 301. Meta-CoTGAN: A Meta Cooperative Training Paradigm for Improving Adversarial Text Generation

- Authors: Haiyan Yin; Dingcheng Li; Xu Li; Ping Li
- Year: 2020
- DOI: 10.1609/aaai.v34i05.6490
- Venue: Proceedings of the AAAI Conference on Artificial Intelligence
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1609/aaai.v34i05.6490
- PDF: https://ojs.aaai.org/index.php/AAAI/article/download/6490/6346

Training generative models that can generate high-quality text with sufficient diversity is an important open problem for Natural Language Generation (NLG) community. Recently, generative adversarial models have been applied extensively on text generation tasks, where the adversarially trained generators alleviate the exposure bias experienced by conventional maximum likelihood approaches and result in promising generation quality. However, due to the notorious defect of mode collapse for adversarial training, the adversarially trained generators face a quality-diversity trade-off, i.e., the generator models tend to sacrifice generation diversity severely for increasing generation quality. In this paper, we propose a novel approach which aims to improve the performance of adversarial text generation via efficiently decelerating mode collapse of the adversarial training. To this end, we introduce a cooperative training paradigm, where a language model is cooperatively trained with the generator and we utilize the language model to efficiently shape the data distribution of the generator against mode collapse. Moreover, instead of engaging the cooperative update for the generator in a principled way, we formulate a meta learning mechanism, where the cooperative update to the generator serves as a high level meta task, with an intuition of ensuring the parameters of the generator after the adversarial update would stay resistant against mode collapse. In the experiment, we demonstrate our proposed approach can efficiently slow down the pace of mode collapse for the adversarial text generators. Overall, our proposed method is able to outperform the baseline approaches with significant margins in terms of both generation quality and diversity in the testified domains.

## 302. 敵対生成ネットワークによる文書生成

- Authors: Kazuki Iwata
- Year: 2020
- DOI: 10.57314/00000689
- Venue: Institutional Repositories DataBase (IRDB)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.57314/00000689
- PDF: https://tfulib.repo.nii.ac.jp/records/739

Automatic text generation using generative adversarial networks （GANs） such as SeqGAN, TestGAN, and LeakGAN has attracted substantial attention. There are numerous studies regarding the automatic generation of English and Chinese texts using Gans or related algorithms. Moreover, methods to generate sentences automatically based on the speeches delivered by the former US president Barack Obama, captions of images, or Chinese poems have been realized. However, there are only a few reports regarding the generation of text from Japanese sentences. In this study, to investigate the differences in generating text in different languages, we generate sentences form the Japanese novel Botchan," which was written by Soseki Natsume, using maximum likelihood estimation, SeqGAN, TextGAN, and LeakGAN. Furthermore, we evaluate the generated text using the metrics of negative log-likelihood loss, 2-gram BLEU, and embedding similarity. Consequently, it is concluded that LeakGAN can generate the most natural text and that, for unknown reasons, TextGAN does not perform well with regard to automatic text generation."

## 303. Making Use of Latent Space in Language GANs for Generating Diverse Text without Pre-training

- Authors: Takeshi Kojima; Yusuke Iwasawa; Yutaka Matsuo
- Year: 2021
- DOI: 10.18653/v1/2021.eacl-srw.23
- Venue: 
- Countries: JP
- Source: openalex
- URL: https://doi.org/10.18653/v1/2021.eacl-srw.23
- PDF: https://aclanthology.org/2021.eacl-srw.23.pdf

Generating diverse texts is an important factor for unsupervised text generation. One approach is to produce the diversity of texts conditioned by the sampled latent code. Although several generative adversarial networks (GANs) have been proposed thus far, these models still suffer from mode-collapsing if the models are not pre-trained. In this paper, we propose a GAN model that aims to improve the approach to generating diverse texts conditioned by the latent space. The generator of our model uses Gumbel-Softmax distribution for the word sampling process. To ensure that the text is generated conditioned upon the sampled latent code, reconstruction loss is introduced in our objective function. The discriminator of our model iteratively inspects incomplete partial texts and learns to distinguish whether they are real or fake by using the standard GAN objective function. Experimental results using the COCO Image Captions dataset show that, although our model is not pre-trained, the performance of our model is quite competitive with the existing baseline models, which requires pre-training.

## 304. Log Message Anomaly Detection with Oversampling

- Authors: Amir Farzad; T. Aaron Gulliver
- Year: 2020
- DOI: 10.5121/ijaia.2020.11405
- Venue: International Journal of Artificial Intelligence & Applications
- Countries: CA
- Source: openalex
- URL: https://doi.org/10.5121/ijaia.2020.11405
- PDF: https://doi.org/10.5121/ijaia.2020.11405

Imbalanced data is a significant challenge in classification with machine learning algorithms. This is particularly important with log message data as negative logs are sparse so this data is typically imbalanced. In this paper, a model to generate text log messages is proposed which employs a SeqGAN network. An Autoencoder is used for feature extraction and anomaly detection is done using a GRU network. The proposed model is evaluated with three imbalanced log data sets, namely BGL, OpenStack, and Thunderbird. Results are presented which show that appropriate oversampling and data balancing improves anomaly detection accuracy.

## 305. An Assisted Teaching Method of College English Translation Using Generative Adversarial Network

- Authors: Lin Zhang
- Year: 2022
- DOI: 10.1155/2022/5408309
- Venue: Mobile Information Systems
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1155/2022/5408309
- PDF: https://downloads.hindawi.com/journals/misy/2022/5408309.pdf

College English translation instruction is an important part of developing students’ English application skills. The generation network in GAN (generative adversarial network) is combined with reinforcement learning technology in this paper to create a basic text generation model that solves the problem that the original GAN model cannot handle discrete data. The correctness of students’ English translation ability is analyzed using a neural network model trained by PSO (particle swarm optimization), which can help teachers estimate students’ translation ability and provide a reference for the next teaching. The results show that the proposed model’s accuracy rate is clearly higher than the comparison model’s, with a maximum accuracy rate of over 85%. The findings indicate that this research model has the potential to improve the quality of English translation instruction.

## 306. Improving Conditional Sequence Generative Adversarial Networks by Stepwise Evaluation

- Authors: Yi-Lin Tuan; Hung-yi Lee
- Year: 2018
- DOI: 10.48550/arxiv.1808.05599
- Venue: arXiv (Cornell University)
- Countries: TW
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1808.05599
- PDF: https://arxiv.org/pdf/1808.05599

Sequence generative adversarial networks (SeqGAN) have been used to improve conditional sequence generation tasks, for example, chit-chat dialogue generation. To stabilize the training of SeqGAN, Monte Carlo tree search (MCTS) or reward at every generation step (REGS) is used to evaluate the goodness of a generated subsequence. MCTS is computationally intensive, but the performance of REGS is worse than MCTS. In this paper, we propose stepwise GAN (StepGAN), in which the discriminator is modified to automatically assign scores quantifying the goodness of each subsequence at every generation step. StepGAN has significantly less computational costs than MCTS. We demonstrate that StepGAN outperforms previous GAN-based methods on both synthetic experiment and chit-chat dialogue generation.

## 307. Differentially Private Synthetic Data Generation Using Context-Aware GANs

- Authors: Anantaa Kotal; Anupam Joshi
- Year: 2024
- DOI: 10.1109/bigdata62323.2024.10826047
- Venue: 
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1109/bigdata62323.2024.10826047
- PDF: https://arxiv.org/pdf/2512.08869

The widespread use of big data across various sectors has brought significant privacy concerns, particularly when sensitive information is shared or analyzed. Regulations like GDPR and HIPAA impose strict controls on handling data, making it difficult to balance the need for insights with privacy requirements. Synthetic data offers a promising solution, enabling the creation of artificial datasets that mirror real-world patterns without exposing sensitive information. For instance, synthetic data can simulate patient records or network flows for training machine learning models to conduct research without violating privacy laws. However, traditional synthetic data generation methods often fail to capture complex, implicit rules that relate different elements of the data and are essential in specific domains like healthcare. While these methods might replicate explicit patterns from the training data, they often overlook domain-specific rules that are not directly stated but are critical for maintaining realism and utility. For example, prescription guidelines, such as avoiding certain medications for patients with specific conditions or preventing harmful drug interactions, may not be explicitly represented in the original data. Synthetic data generated without accounting for these implicit rules can lead to medically inappropriate or unrealistic patient profiles. To address these limitations, we propose a framework called Context-Aware Differentially Private Generative Adversarial Network (ContextGAN). Our framework integrates domain-specific rules using a constraint matrix that explicitly encodes both explicit and implicit domain knowledge. The constraint-aware discriminator evaluates synthetic data against these rules, ensuring the generated data adheres to domain constraints. Furthermore, the discriminator is differentially private, ensuring privacy preservation by protecting sensitive details from the original data. We validate ContextGAN across multiple domains, including healthcare, security, and finance, demonstrating that it produces high-quality synthetic data that respects domain-specific rules while preserving privacy. Our results show that ContextGAN significantly improves the realism and utility of synthetic data by enforcing domain constraints, making it suitable for use in scenarios requiring both compliance with explicit patterns and implicit rules, all under strict privacy guarantees.

## 308. Personalized Sentence Generation using Generative Adversarial Networks with Author-Specific Word Usage

- Authors: Chenhan Yuan; Yi Chin Huang
- Year: 2020
- DOI: 10.13053/cys-1-1-3350
- Venue: Computación y Sistemas
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.13053/cys-1-1-3350
- PDF: https://www.cys.cic.ipn.mx/ojs/index.php/CyS/article/view/3350/2765

The author-specific word usage is a vital feature to let readers perceive the writing style of the author. In this work, a personalized sentence generation method based on generative adversarial networks (GANs) is proposed to cope with this issue. The frequently used function word and content word are incorporated not only as the input features but also as the sentence structure constraint for the GAN training. For the sentence generation with the related topics decided by the user, the Named Entity Recognition (NER) information of the input words is also used in the network training. We compared the proposed method with the GAN-based sentence generation methods, and the experimental results showed that the generated sentences using our method are more similar to the original sentences of the same author based on the objective evaluation such as BLEU and SimHash score.

## 309. Performance comparison of data balancing techniques on hate speech detection in Turkish

- Authors: Habibe Karayiğit; Ali Akdağlı; Çiğdem İnan Acı
- Year: 2024
- DOI: 10.5505/pajes.2023.40072
- Venue: Pamukkale University Journal of Engineering Sciences
- Countries: TR; US
- Source: openalex
- URL: https://doi.org/10.5505/pajes.2023.40072
- PDF: https://dergipark.org.tr/tr/download/article-file/4322415

Increasing hate speech on social media platforms causes psychological disorders and deep and negative effects. Automatic language classification models are needed to detect hate speech. When testing language models for hate speech, imbalanced datasets where one data class is represented much more frequently than the other can be a problem in language datasets. When the dataset is imbalanced, the classifier may be biased towards the majority class and may not perform well in the minority class. This can lead to incorrect or unreliable classification results. To solve this problem, data level balancing methods such as oversampling or undersampling are used to balance the class distribution before classifying the dataset. This study, it is aimed to achieve a successful classification model combination that detects hate speech by using data-level balancing methods. For this, a comprehensive study was carried out by applying the balancing method at eight data levels (random oversampling, Synthetic Minority Oversampling Technique (SMOTE), K-means SMOTE, Localized Random Affine Shadow Sample (LoRAS), Text-based Generative AdversarialNetwork (TextGAN), Nearmiss, Tomek Links ve Clustering-based) to the Abusive Turkish Comments (ATC) dataset, which has an imbalanced distribution of labels, obtained from Instagram. Classification performances of data level balancing methods were evaluated with Basic Machine Learning (BML) and Convolutional Neural Network (CNN) methods. It has been observed that the CBoW+CNN model based on the TextGAN data-level balancing method, as well as the Skip-gram CNN model, exhibited the best classification performance with a MacroAveraged F1 score of 0.972.

## 310. Stochastic Parrots Looking for Stochastic Parrots: LLMs are Easy to Fine-Tune and Hard to Detect with other LLMs

- Authors: Da Silva Gameiro Henrique; Andrei Kucharavy; Rachid Guerraoui
- Year: 2023
- DOI: 10.48550/arxiv.2304.08968
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2304.08968
- PDF: https://arxiv.org/pdf/2304.08968

The self-attention revolution allowed generative language models to scale and achieve increasingly impressive abilities. Such models - commonly referred to as Large Language Models (LLMs) - have recently gained prominence with the general public, thanks to conversational fine-tuning, putting their behavior in line with public expectations regarding AI. This prominence amplified prior concerns regarding the misuse of LLMs and led to the emergence of numerous tools to detect LLMs in the wild. Unfortunately, most such tools are critically flawed. While major publications in the LLM detectability field suggested that LLMs were easy to detect with fine-tuned autoencoders, the limitations of their results are easy to overlook. Specifically, they assumed publicly available generative models without fine-tunes or non-trivial prompts. While the importance of these assumptions has been demonstrated, until now, it remained unclear how well such detection could be countered. Here, we show that an attacker with access to such detectors' reference human texts and output not only evades detection but can fully frustrate the detector training - with a reasonable budget and all its outputs labeled as such. Achieving it required combining common "reinforcement from critic" loss function modification and AdamW optimizer, which led to surprisingly good fine-tuning generalization. Finally, we warn against the temptation to transpose the conclusions obtained in RNN-driven text GANs to LLMs due to their better representative ability. These results have critical implications for the detection and prevention of malicious use of generative language models, and we hope they will aid the designers of generative models and detectors.

## 311. Oversampling Log Messages using A Sequence Generative Adversarial Network for Anomaly Detection and Classification

- Authors: Amir Farzad; T. Aaron Gulliver
- Year: 2020
- DOI: 10.5121/csit.2020.100515
- Venue: 
- Countries: CA
- Source: openalex
- URL: https://doi.org/10.5121/csit.2020.100515
- PDF: https://doi.org/10.5121/csit.2020.100515

Dealing with imbalanced data is one of the main challenges in machine/deep learning algorithms for classification. This issue is more important with log message data as it is typically very imbalanced and negative logs are rare. In this paper, a model is proposed to generate text log messages using a SeqGAN network. Then features are extracted using an Autoencoder and anomaly detection is done using a GRU network. The proposed model is evaluated with two imbalanced log data sets, namely BGL and Openstack. Results are presented which show that oversampling and balancing data increases the accuracy of anomaly detection and classification.

## 312. Mirroring Privacy Risks with Digital Twins: When Pieces of Personal Data Suddenly Fit Together

- Authors: Frederik Simon Bäumer; Sergej Schultenkämper; Michaela Geierhos; Yeong Su Lee
- Year: 2024
- DOI: 10.1007/s42979-024-03413-z
- Venue: SN Computer Science
- Countries: DE
- Source: openalex
- URL: https://doi.org/10.1007/s42979-024-03413-z
- PDF: https://link.springer.com/content/pdf/10.1007/s42979-024-03413-z.pdf

Abstract With the proliferation of social media, more personal information is being shared online than ever before, raising significant privacy concerns. This paper presents a novel approach to identify and mitigate privacy risks by generating digital twins from social media data. We propose a comprehensive framework that includes data collection, processing, and analysis, with special attention to data standardization, pseudonymization, and the use of synthetic data to ensure privacy compliance. We apply and evaluate state-of-the-art techniques such as Large Language Models, Generative Adversarial Networks, and Vision-Language Models to generate synthetic but realistic social media data that support the construction of accurate and representative digital twins while ensuring strict privacy compliance. Our approach demonstrates the potential for digital twins to help identify and mitigate privacy risks associated with social media use. We discuss the value and feasibility of this concept and suggest that further refinement of the techniques and conditions involved is needed.

## 313. Sentence Generation Method by Extension of MolGAN Using Sentence Graph

- Authors: Natsuki SAWASAKI; Satoshi Endo; Naruaki Toma; Kôji Yamada; Yuhei Akamine
- Year: 2020
- DOI: 10.3156/jsoft.32.2_668
- Venue: Journal of Japan Society for Fuzzy Theory and Intelligent Informatics
- Countries: JP
- Source: openalex
- URL: https://doi.org/10.3156/jsoft.32.2_668
- PDF: https://www.jstage.jst.go.jp/article/jsoft/32/2/32_668/_pdf

Deep learning solves many classification problems. However, it is difficult to solve problems with imbalanced data. Therefore, the data volume is increased for the purpose of balancing. This is called data augmentation. Generally, the method of image data augmentation uses noise addition, rotation, and the like. Recently, images are generated using the generative adversary network: GAN. However, data augmentation methods are difficult in natural language processing. In addition, manual data augmentation is burdensome and requires mechanical methods. Mechanical text augmentation is more difficult than images. Because it is difficult to analyze the feature of sentences. This paper proposes a sentence generation method by machine learning focusing on graph information. The graph information obtained by CaboCha is processed by graph Convolution. The proposed GAN was used to generate sentences, and then three experiments were performed to evaluate its effectiveness.

## 314. Personalized sentence generation using generative adversarial networks with author-specific word usage

- Authors: Chenhan Yuan; Yi‐Chin Huang
- Year: 2019
- DOI: 10.48550/arxiv.1904.09442
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1904.09442
- PDF: https://arxiv.org/pdf/1904.09442

The author-specific word usage is a vital feature to let readers perceive the writing style of the author. In this work, a personalized sentence generation method based on generative adversarial networks (GANs) is proposed to cope with this issue. The frequently used function word and content word are incorporated not only as the input features but also as the sentence structure constraint for the GAN training. For the sentence generation with the related topics decided by the user, the Named Entity Recognition (NER) information of the input words is also used in the network training. We compared the proposed method with the GAN-based sentence generation methods, and the experimental results showed that the generated sentences using our method are more similar to the original sentences of the same author based on the objective evaluation such as BLEU and SimHash score.

## 315. Bio-informed Protein Sequence Generation for Multi-class Virus Mutation Prediction

- Authors: Yuyang Wang; Prakarsh Yadav; Rishikesh Magar; Amir Barati Farimani
- Year: 2020
- DOI: 10.1101/2020.06.11.146167
- Venue: bioRxiv (Cold Spring Harbor Laboratory)
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1101/2020.06.11.146167
- PDF: https://www.biorxiv.org/content/biorxiv/early/2020/06/12/2020.06.11.146167.full.pdf

Abstract Viral pandemics are emerging as a serious global threat to public health, like the recent outbreak of COVID-19. Viruses, especially those belonging to a large family of +ssRNA viruses, have a high possibility of mutating by inserting, deleting, or substituting one or multiple genome segments. It is of great importance for human health worldwide to predict the possible virus mutations, which can effectively avoid the potential second outbreak. In this work, we develop a GAN-based multi-class protein sequence generative model, named ProteinSeqGAN. Given the viral species, the generator is modeled on RNNs to predict the corresponding antigen epitope sequences synthesized by viral genomes. Additionally, a Graphical Protein Autoencoder (GProAE) built upon VAE is proposed to featurize proteins bioinformatically. GProAE, as a multi-class discriminator, also learns to evaluate the goodness of protein sequences and predict the corresponding viral species. Further experiments show that our ProteinSeqGAN model can generate valid antigen protein sequences from both bioinformatics and statistics perspectives, which can be promising predictions of virus mutations.

## 316. Generative AI based Customized Contract Clause Recommendation System for Game Content License Agreement

- Authors: Hyunsoo Kim; Chang-Jun Choi; YongJoon Joe; Dong-Myung Shin
- Year: 2024
- DOI: 10.29056/jsav.2024.12.18
- Venue: Journal of Software Assessment and Valuation
- Countries: 
- Source: openalex
- URL: https://doi.org/10.29056/jsav.2024.12.18
- PDF: https://doi.org/10.29056/jsav.2024.12.18

This paper proposes an AI-based system for generating license agreement clauses customized to the characteristics of different game genres.Game content possesses unique traits depending on its genre, and these differences significantly influence contract terms, potentially increasing the probability of legal disputes.In this study, we fine-tuned a generative AI model, GPT-4o, to create personalized contract clauses optimized for specific game genres and contractual purposes.To achieve this, we analyzed publicly available standard contracts and addressed the lack of training data by expanding the dataset using TextGAN.Experimental results showed that the fine-tuned model, optimized through hyperparameter adjustments, achieved a decrease in Training Loss to 0.4635 and demonstrated improved performance in generating clauses suitable for game content license agreements compared to the base GPT-4o model.This system is expected to enhance the efficiency of contract drafting and reduce the potential for legal disputes.

## 317. Generative Adversarial Nets for Multiple Text Corpora

- Authors: Baiyang Wang; Diego Klabjan
- Year: 2017
- DOI: 10.48550/arxiv.1712.09127
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1712.09127
- PDF: https://arxiv.org/pdf/1712.09127

Generative adversarial nets (GANs) have been successfully applied to the artificial generation of image data. In terms of text data, much has been done on the artificial generation of natural language from a single corpus. We consider multiple text corpora as the input data, for which there can be two applications of GANs: (1) the creation of consistent cross-corpus word embeddings given different word embeddings per corpus; (2) the generation of robust bag-of-words document embeddings for each corpora. We demonstrate our GAN models on real-world text data sets from different corpora, and show that embeddings from both models lead to improvements in supervised learning problems.

## 318. Counter-Contrastive Learning for Language GANs

- Authors: Yekun Chai; Haidong Zhang; Qiyue Yin; Junge Zhang
- Year: 2021
- DOI: 10.18653/v1/2021.findings-emnlp.415
- Venue: 
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.18653/v1/2021.findings-emnlp.415
- PDF: https://aclanthology.org/2021.findings-emnlp.415.pdf

Generative Adversarial Networks (GANs) have achieved great success in image synthesis, but have proven to be difficult to generate natural language. Challenges arise from the uninformative learning signals passed from the discriminator. In other words, the poor learning signals limit the learning capacity for generating languages with rich structures and semantics. In this paper, we propose to adopt the counter-contrastive learning (CCL) method to support the generator's training in language GANs. In contrast to standard GANs that adopt a simple binary classifier to discriminate whether a sample is real or fake, we employ a counter-contrastive learning signal that advances the training of language synthesizers by (1) pulling the language representations of generated and real samples together and (2) pushing apart representations of real samples to compete with the discriminator and thus prevent the discriminator from being overtrained. We evaluate our method on both synthetic and real benchmarks and yield competitive performance compared to previous GANs for adversarial sequence generation.

## 319. Learning Implicit Text Generation via Feature Matching

- Authors: Inkit Padhi; Pierre Dognin; Ke Bai; Cícero Nogueira dos Santos; Vijil Chenthamarakshan; Youssef Mroueh; Payel Das
- Year: 2020
- DOI: 10.18653/v1/2020.acl-main.354
- Venue: 
- Countries: DE; US
- Source: openalex
- URL: https://doi.org/10.18653/v1/2020.acl-main.354
- PDF: https://www.aclweb.org/anthology/2020.acl-main.354.pdf

Inkit Padhi, Pierre Dognin, Ke Bai, Cícero Nogueira dos Santos, Vijil Chenthamarakshan, Youssef Mroueh, Payel Das. Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics. 2020.

## 320. Neural Text-to-Text Generation Systemusing Generative Adversarial Network andMonte Carlo Policy Gradient

- Authors: Seemanthini Narasimha Moorthy
- Year: 2020
- DOI: 
- Venue: NORMA
- Countries: 
- Source: openalex
- URL: https://openalex.org/W3092889484
- PDF: https://norma.ncirl.ie/4301/1/seemanthininarasimhamoorthy.pdf

Text-to-text generation is a fundamental task in natural language processing. Traditional models rely on standalone recurrant neural networks like Long Short Term Memory(LSTM) and Gated Recurrent Units(GRU). Generative Adversarial Networks (GAN) have found little success in generating discrete valued data like text. Major drawbacks lies in the failure to pass discrete output from generator model to discriminator model, and the inability of the discriminator model to assess incomplete sentences. This research strengthens the use of Generative Adversarial Networks combining it with Monte Carlo Policy Gradient, where the gradient policy update comes directly from the discriminator model and is passed back as the reward signal by using Monte Carlo Search algorithm. The results show that by combining Generative Adversarial Networks and Reinforce Algorithm, significant results can be obtained comparative to baseline models using evaluation metric called Bilingual Evaluation Understudy Score -N (BLEU-N). A BLEU score of 0.3 was achieved overall through different experiments. Keywords: Natural Language Processing, Long Short Term Memory(LSTM), Gated Recurrent Units(GRU), Generative Adversarial Networks(GAN), Monte Carlo Policy Gradient

## 321. Unsupervised Text Embedding Space Generation Using Generative Adversarial Networks for Text Synthesis

- Authors: Jun-Min Lee; Tae-Bin Ha
- Year: 2023
- DOI: 10.48550/arxiv.2306.17181
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2306.17181
- PDF: https://arxiv.org/pdf/2306.17181

Generative Adversarial Networks (GAN) is a model for data synthesis, which creates plausible data through the competition of generator and discriminator. Although GAN application to image synthesis is extensively studied, it has inherent limitations to natural language generation. Because natural language is composed of discrete tokens, a generator has difficulty updating its gradient through backpropagation; therefore, most text-GAN studies generate sentences starting with a random token based on a reward system. Thus, the generators of previous studies are pre-trained in an autoregressive way before adversarial training, causing data memorization that synthesized sentences reproduce the training data. In this paper, we synthesize sentences using a framework similar to the original GAN. More specifically, we propose Text Embedding Space Generative Adversarial Networks (TESGAN) which generate continuous text embedding spaces instead of discrete tokens to solve the gradient backpropagation problem. Furthermore, TESGAN conducts unsupervised learning which does not directly refer to the text of the training data to overcome the data memorization issue. By adopting this novel method, TESGAN can synthesize new sentences, showing the potential of unsupervised learning for text synthesis. We expect to see extended research combining Large Language Models with a new perspective of viewing text as an continuous space.

## 322. GPTGAN: Utilizing the GPT language model and GAN to enhance adversarial text generation

- Authors: Omid Hajipoor; Ahmad Nickabadi; Mohammad Mehdi Homayounpour
- Year: 2024
- DOI: 10.1016/j.neucom.2024.128865
- Venue: Neurocomputing
- Countries: IR
- Source: openalex
- URL: https://doi.org/10.1016/j.neucom.2024.128865

## 323. SentiGAN: Generating Sentimental Texts via Mixture Adversarial Networks

- Authors: Ke Wang; Xiaojun Wan
- Year: 2018
- DOI: 10.24963/ijcai.2018/618
- Venue: 
- Countries: CN; CZ; MM
- Source: openalex
- URL: https://doi.org/10.24963/ijcai.2018/618
- PDF: https://www.ijcai.org/proceedings/2018/0618.pdf

Generating texts of different sentiment labels is getting more and more attention in the area of natural language generation. Recently, Generative Adversarial Net (GAN) has shown promising results in text generation. However, the texts generated by GAN usually suffer from the problems of poor quality, lack of diversity and mode collapse. In this paper, we propose a novel framework - SentiGAN, which has multiple generators and one multi-class discriminator, to address the above problems. In our framework, multiple generators are trained simultaneously, aiming at generating texts of different sentiment labels without supervision. We propose a penalty based objective in the generators to force each of them to generate diversified examples of a specific sentiment label. Moreover, the use of multiple generators and one multi-class discriminator can make each generator focus on generating its own examples of a specific sentiment label accurately. Experimental results on four datasets demonstrate that our model consistently outperforms several state-of-the-art text generation methods in the sentiment accuracy and quality of generated texts.

## 324. Long Text Generation via Adversarial Training with Leaked Information

- Authors: Jiaxian Guo; Sidi Lu; Han Cai; Weinan Zhang; Yong Yu; Jun Wang
- Year: 2017
- DOI: 10.48550/arxiv.1709.08624
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1709.08624
- PDF: https://arxiv.org/pdf/1709.08624

Automatically generating coherent and semantically meaningful text has many applications in machine translation, dialogue systems, image captioning, etc. Recently, by combining with policy gradient, Generative Adversarial Nets (GAN) that use a discriminative model to guide the training of the generative model as a reinforcement learning policy has shown promising results in text generation. However, the scalar guiding signal is only available after the entire text has been generated and lacks intermediate information about text structure during the generative process. As such, it limits its success when the length of the generated text samples is long (more than 20 words). In this paper, we propose a new framework, called LeakGAN, to address the problem for long text generation. We allow the discriminative net to leak its own high-level extracted features to the generative net to further help the guidance. The generator incorporates such informative signals into all generation steps through an additional Manager module, which takes the extracted features of current generated words and outputs a latent vector to guide the Worker module for next-word generation. Our extensive experiments on synthetic data and various real-world tasks with Turing test demonstrate that LeakGAN is highly effective in long text generation and also improves the performance in short text generation scenarios. More importantly, without any supervision, LeakGAN would be able to implicitly learn sentence structures only through the interaction between Manager and Worker.

## 325. On Accurate Evaluation of GANs for Language Generation

- Authors: Stanislau Semeniuta; Aliaksei Severyn; Sylvain Gelly
- Year: 2018
- DOI: 10.48550/arxiv.1806.04936
- Venue: arXiv (Cornell University)
- Countries: DE; US
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1806.04936
- PDF: https://arxiv.org/pdf/1806.04936

Generative Adversarial Networks (GANs) are a promising approach to language generation. The latest works introducing novel GAN models for language generation use n-gram based metrics for evaluation and only report single scores of the best run. In this paper, we argue that this often misrepresents the true picture and does not tell the full story, as GAN models can be extremely sensitive to the random initialization and small deviations from the best hyperparameter choice. In particular, we demonstrate that the previously used BLEU score is not sensitive to semantic deterioration of generated texts and propose alternative metrics that better capture the quality and diversity of the generated samples. We also conduct a set of experiments comparing a number of GAN models for text with a conventional Language Model (LM) and find that neither of the considered models performs convincingly better than the LM.

## 326. DP-GAN: Diversity-Promoting Generative Adversarial Network for Generating Informative and Diversified Text

- Authors: Jingjing Xu; Xuancheng Ren; Junyang Lin; Xu Sun
- Year: 2018
- DOI: 10.48550/arxiv.1802.01345
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1802.01345
- PDF: https://arxiv.org/pdf/1802.01345

Existing text generation methods tend to produce repeated and "boring" expressions. To tackle this problem, we propose a new text generation model, called Diversity-Promoting Generative Adversarial Network (DP-GAN). The proposed model assigns low reward for repeatedly generated text and high reward for "novel" and fluent text, encouraging the generator to produce diverse and informative text. Moreover, we propose a novel language-model based discriminator, which can better distinguish novel text from repeated text without the saturation problem compared with existing classifier-based discriminators. The experimental results on review generation and dialogue generation tasks demonstrate that our model can generate substantially more diverse and informative text than existing baselines. The code is available at https://github.com/lancopku/DPGAN

## 327. Neural Text Generation: Past, Present and Beyond

- Authors: Sidi Lu; Yaoming Zhu; Weinan Zhang; Jun Wang; Yong Yu
- Year: 2018
- DOI: 10.48550/arxiv.1803.07133
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1803.07133
- PDF: https://arxiv.org/pdf/1803.07133

This paper presents a systematic survey on recent development of neural text generation models. Specifically, we start from recurrent neural network language models with the traditional maximum likelihood estimation training scheme and point out its shortcoming for text generation. We thus introduce the recently proposed methods for text generation based on reinforcement learning, re-parametrization tricks and generative adversarial nets (GAN) techniques. We compare different properties of these models and the corresponding techniques to handle their common problems such as gradient vanishing and generation diversity. Finally, we conduct a benchmarking experiment with different types of neural text generation models on two well-known datasets and discuss the empirical results along with the aforementioned model properties.

## 328. TextGAIL: Generative Adversarial Imitation Learning for Text Generation

- Authors: Qingyang Wu; Lei Li; Zhou Yu
- Year: 2021
- DOI: 10.1609/aaai.v35i16.17656
- Venue: Proceedings of the AAAI Conference on Artificial Intelligence
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1609/aaai.v35i16.17656
- PDF: https://ojs.aaai.org/index.php/AAAI/article/download/17656/17463

Generative Adversarial Networks (GANs) for text generation have recently received many criticisms, as they perform worse than their MLE counterparts. We suspect previous text GANs' inferior performance is due to the lack of a reliable guiding signal in their discriminators. To address this problem, we propose a generative adversarial imitation learning framework for text generation that uses large pre-trained language models to provide more reliable reward guidance. As previous text GANs suffer from high variance of gradients, we apply contrastive discriminator, and proximal policy optimization (PPO) to stabilize and improve text generation performance. For evaluation, we conduct experiments on a diverse set of unconditional and conditional text generation tasks. Experimental results show that TextGAIL achieves better performance in terms of both quality and diversity than the MLE baseline. We also validate our intuition that TextGAIL's discriminator demonstrates the capability of providing reasonable rewards with an additional task.

## 329. Language GANs Falling Short

- Authors: M. Caccia; Lucas Caccia; William Fedus; Hugo Larochelle; Joëlle Pineau; Laurent Charlin
- Year: 2018
- DOI: 10.48550/arxiv.1811.02549
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1811.02549
- PDF: https://arxiv.org/pdf/1811.02549

Generating high-quality text with sufficient diversity is essential for a wide range of Natural Language Generation (NLG) tasks. Maximum-Likelihood (MLE) models trained with teacher forcing have consistently been reported as weak baselines, where poor performance is attributed to exposure bias (Bengio et al., 2015; Ranzato et al., 2015); at inference time, the model is fed its own prediction instead of a ground-truth token, which can lead to accumulating errors and poor samples. This line of reasoning has led to an outbreak of adversarial based approaches for NLG, on the account that GANs do not suffer from exposure bias. In this work, we make several surprising observations which contradict common beliefs. First, we revisit the canonical evaluation framework for NLG, and point out fundamental flaws with quality-only evaluation: we show that one can outperform such metrics using a simple, well-known temperature parameter to artificially reduce the entropy of the model's conditional distributions. Second, we leverage the control over the quality / diversity trade-off given by this parameter to evaluate models over the whole quality-diversity spectrum and find MLE models constantly outperform the proposed GAN variants over the whole quality-diversity space. Our results have several implications: 1) The impact of exposure bias on sample quality is less severe than previously thought, 2) temperature tuning provides a better quality / diversity trade-off than adversarial training while being easier to train, easier to cross-validate, and less computationally expensive. Code to reproduce the experiments is available at github.com/pclucas14/GansFallingShort

## 330. Generative Deep Learning for Internet of Things Network Traffic Generation

- Authors: Mustafizur R. Shahid; Grégory Blanc; Houda Jmila; Zonghua Zhang; Hervé Debar
- Year: 2020
- DOI: 10.1109/prdc50213.2020.00018
- Venue: 
- Countries: FR
- Source: openalex
- URL: https://doi.org/10.1109/prdc50213.2020.00018

The rapid development of the Internet of Things (IoT) has prompted a recent interest into realistic IoT network traffic generation. Security practitioners need IoT network traffic data to develop and assess network-based intrusion detection systems (NIDS). Emulating realistic network traffic will avoid the costly physical deployment of thousands of smart devices. From an attacker's perspective, generating network traffic that mimics the legitimate behavior of a device can be useful to evade NIDS. As network traffic data consist of sequences of packets, the problem is similar to the generation of sequences of categorical data, like word by word text generation. Many solutions in the field of natural language processing have been proposed to adapt a Generative Adversarial Network (GAN) to generate sequences of categorical data. In this paper, we propose to combine an autoencoder with a GAN to generate sequences of packet sizes that correspond to bidirectional flows. First, the autoencoder is trained to learn a latent representation of the real sequences of packet sizes. A GAN is then trained on the latent space, to learn to generate latent vectors that can be decoded into realistic sequences. For experimental purposes, bidirectional flows produced by a Google Home Mini are used, and the autoencoder is combined with a Wassertein GAN. Comparison of different network characteristics shows that our proposed approach is able to generate sequences of packet sizes that behave closely to real bidirectional flows. We also show that the synthetic bidirectional flows are close enough to the real ones that they can fool anomaly detectors into labeling them as legitimate.

## 331. Emotional Text Generation Based on Cross-Domain Sentiment Transfer

- Authors: Rui Zhang; Zhenyu Wang; Kai Yin; Zhenhua Huang
- Year: 2019
- DOI: 10.1109/access.2019.2931036
- Venue: IEEE Access
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/access.2019.2931036
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/8600701/08772090.pdf

Emotional intelligence plays an important role in human intelligence and is a recent research hotspot. With the rapid development of deep learning techniques in recent years, several neural network-based emotional text generation methods have been investigated. However, the existing emotional text generation approaches often suffer from the problem of requiring large-scale annotated data. Generative adversarial network (GAN) has shown promising results in natural language generation and data enhancement. In order to solve the above problem, this paper proposes a GAN-based cross-domain text sentiment transfer model, which uses annotated data from other domains to assist in the training of emotional text generation network. By combining adversarial reinforcement learning with supervised learning, our model is able to extract patterns of sentiment transformation and apply them in emotional text generation. The experimental results have shown that our approach outperforms the state-of-the-art methods and is able to generate high-quality emotional text while maintaining the consistency of domain information and content semantics.

## 332. Evaluating Text GANs as Language Models

- Authors: Guy Tevet; Gavriel Habib; Vered Shwartz; Jonathan Berant
- Year: 2018
- DOI: 10.48550/arxiv.1810.12686
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1810.12686
- PDF: https://arxiv.org/pdf/1810.12686

Generative Adversarial Networks (GANs) are a promising approach for text generation that, unlike traditional language models (LM), does not suffer from the problem of ``exposure bias''. However, A major hurdle for understanding the potential of GANs for text generation is the lack of a clear evaluation metric. In this work, we propose to approximate the distribution of text generated by a GAN, which permits evaluating them with traditional probability-based LM metrics. We apply our approximation procedure on several GAN-based models and show that they currently perform substantially worse than state-of-the-art LMs. Our evaluation procedure promotes better understanding of the relation between GANs and LMs, and can accelerate progress in GAN-based text generation.

## 333. DANCin SEQ2SEQ: Fooling Text Classifiers with Adversarial Text Example Generation

- Authors: Catherine Wong
- Year: 2017
- DOI: 10.48550/arxiv.1712.05419
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1712.05419
- PDF: https://arxiv.org/pdf/1712.05419

Machine learning models are powerful but fallible. Generating adversarial examples - inputs deliberately crafted to cause model misclassification or other errors - can yield important insight into model assumptions and vulnerabilities. Despite significant recent work on adversarial example generation targeting image classifiers, relatively little work exists exploring adversarial example generation for text classifiers; additionally, many existing adversarial example generation algorithms require full access to target model parameters, rendering them impractical for many real-world attacks. In this work, we introduce DANCin SEQ2SEQ, a GAN-inspired algorithm for adversarial text example generation targeting largely black-box text classifiers. We recast adversarial text example generation as a reinforcement learning problem, and demonstrate that our algorithm offers preliminary but promising steps towards generating semantically meaningful adversarial text examples in a real-world attack scenario.

## 334. Music Generation System for Adversarial Training Based on Deep Learning

- Authors: Junying Min; Zhaoqi Liu; Lei Wang; Dongyang Li; Maoqing Zhang; Yantai Huang
- Year: 2022
- DOI: 10.3390/pr10122515
- Venue: Processes
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.3390/pr10122515
- PDF: https://www.mdpi.com/2227-9717/10/12/2515/pdf?version=1669775109

With the rapid development of artificial intelligence, the application of this new technology to music generation has attracted more attention and achieved gratifying results. This study proposes a method for combining the transformer deep-learning model with generative adversarial networks (GANs) to explore a more competitive music generation algorithm. The idea of text generation in natural language processing (NLP) was used for reference, and a unique loss function was designed for the model. The training process solves the problem of a nondifferentiable gradient in generating music. Compared with the problem that LSTM cannot deal with long sequence music, the model based on transformer and GANs can extract the relationship in the notes of long sequence music samples and learn the rules of music composition well. At the same time, the optimized transformer and GANs model has obvious advantages in the complexity of the system and the accuracy of generating notes.

## 335. Generative Adversarial Network Training is a Continual Learning Problem

- Authors: Kevin J Liang; Chunyuan Li; Guoyin Wang; Lawrence Carin
- Year: 2018
- DOI: 10.48550/arxiv.1811.11083
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1811.11083
- PDF: https://arxiv.org/pdf/1811.11083

Generative Adversarial Networks (GANs) have proven to be a powerful framework for learning to draw samples from complex distributions. However, GANs are also notoriously difficult to train, with mode collapse and oscillations a common problem. We hypothesize that this is at least in part due to the evolution of the generator distribution and the catastrophic forgetting tendency of neural networks, which leads to the discriminator losing the ability to remember synthesized samples from previous instantiations of the generator. Recognizing this, our contributions are twofold. First, we show that GAN training makes for a more interesting and realistic benchmark for continual learning methods evaluation than some of the more canonical datasets. Second, we propose leveraging continual learning techniques to augment the discriminator, preserving its ability to recognize previous generator samples. We show that the resulting methods add only a light amount of computation, involve minimal changes to the model, and result in better overall performance on the examined image and text generation tasks.

## 336. Rigorous Experimental Analysis of Tabular Data Generated using TVAE and CTGAN

- Authors: Parul Yadav; Manish Gaur; Rahul Kumar Madhukar; Verma Gaurav; Pankaj Kumar; Nishat Fatima; Saqib Sarwar; Yash Raj Dwivedi
- Year: 2024
- DOI: 10.14569/ijacsa.2024.01504125
- Venue: International Journal of Advanced Computer Science and Applications
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.14569/ijacsa.2024.01504125
- PDF: http://thesai.org/Downloads/Volume15No4/Paper_125-Rigorous_Experimental_Analysis_of_Tabular_Data_Generated.pdf

Synthetic data generation research has been progressing at a rapid pace and novel methods are being designed every now and then. Earlier, statistical methods were used to learn the distributions of real data and then sample synthetic data from those distributions. Recent advances in generative models have led to more efficient modeling of complex high-dimensional datasets. Also, privacy concerns have led to the development of robust models with lesser risk of privacy breaches. Firstly, the paper presents a comprehensive survey of existing techniques for tabular data generation and evaluation matrices. Secondly, it elaborates on a comparative analysis of state-of- the-art synthetic data generation techniques, specifically CTGAN and TVAE for small, medium, and large-scale datasets with varying data distributions. It further evaluates the synthetic data using quantitative and qualitative metrics/techniques. Finally, this paper presents the outcomes and also highlights the issues and shortcomings which are still need to be addressed.

## 337. Optimizing Rare Disease Gait Classification through Data Balancing and Generative AI: Insights from Hereditary Cerebellar Ataxia

- Authors: Dante Trabassi; Stefano Filippo Castiglia; Fabiano Bini; Franco Marinozzi; Arash Ajoudani; Marta Lorenzini; Giorgia Chini; Tiwana Varrecchia; Alberto Ranavolo; Roberto De Icco; Carlo Casali; Mariano Serrao
- Year: 2024
- DOI: 10.3390/s24113613
- Venue: Sensors
- Countries: IT
- Source: openalex
- URL: https://doi.org/10.3390/s24113613
- PDF: https://www.mdpi.com/1424-8220/24/11/3613/pdf?version=1717417995

The interpretability of gait analysis studies in people with rare diseases, such as those with primary hereditary cerebellar ataxia (pwCA), is frequently limited by the small sample sizes and unbalanced datasets. The purpose of this study was to assess the effectiveness of data balancing and generative artificial intelligence (AI) algorithms in generating synthetic data reflecting the actual gait abnormalities of pwCA. Gait data of 30 pwCA (age: 51.6 ± 12.2 years; 13 females, 17 males) and 100 healthy subjects (age: 57.1 ± 10.4; 60 females, 40 males) were collected at the lumbar level with an inertial measurement unit. Subsampling, oversampling, synthetic minority oversampling, generative adversarial networks, and conditional tabular generative adversarial networks (ctGAN) were applied to generate datasets to be input to a random forest classifier. Consistency and explainability metrics were also calculated to assess the coherence of the generated dataset with known gait abnormalities of pwCA. ctGAN significantly improved the classification performance compared with the original dataset and traditional data augmentation methods. ctGAN are effective methods for balancing tabular datasets from populations with rare diseases, owing to their ability to improve diagnostic models with consistent explainability.

## 338. Conditional Tabular Generative Adversarial Based Intrusion Detection System for Detecting Ddos and Dos Attacks on the Internet of Things Networks

- Authors: Basim Ahmad Alabsi; Mohammed Anbar; Shaza Dawood Ahmed Rihan
- Year: 2023
- DOI: 10.3390/s23125644
- Venue: Sensors
- Countries: MY; SA
- Source: openalex
- URL: https://doi.org/10.3390/s23125644
- PDF: https://www.mdpi.com/1424-8220/23/12/5644/pdf?version=1687226406

The increasing use of Internet of Things (IoT) devices has led to a rise in Distributed Denial of Service (DDoS) and Denial of Service (DoS) attacks on these networks. These attacks can have severe consequences, resulting in the unavailability of critical services and financial losses. In this paper, we propose an Intrusion Detection System (IDS) based on a Conditional Tabular Generative Adversarial Network (CTGAN) for detecting DDoS and DoS attacks on IoT networks. Our CGAN-based IDS utilizes a generator network to produce synthetic traffic that mimics legitimate traffic patterns, while the discriminator network learns to differentiate between legitimate and malicious traffic. The syntactic tabular data generated by CTGAN is employed to train multiple shallow machine-learning and deep-learning classifiers, enhancing their detection model performance. The proposed approach is evaluated using the Bot-IoT dataset, measuring detection accuracy, precision, recall, and F1 measure. Our experimental results demonstrate the accurate detection of DDoS and DoS attacks on IoT networks using the proposed approach. Furthermore, the results highlight the significant contribution of CTGAN in improving the performance of detection models in machine learning and deep learning classifiers.

## 339. TGAN and CTGAN: A Comparative Analysis for Augmenting COVID 19 Tabular Data

- Authors: Eman Kamal Al-Bwana; Mohammad Alauthman; Ikbel Sayahi; Mohamed Ali Mahjoub
- Year: 2025
- DOI: 10.5220/0013483200003929
- Venue: 
- Countries: TN
- Source: openalex
- URL: https://doi.org/10.5220/0013483200003929
- PDF: https://doi.org/10.5220/0013483200003929

## 340. Peak and ultimate stress-strain model of confined ultra-high-performance concrete (UHPC) using hybrid machine learning model with conditional tabular generative adversarial network

- Authors: Tadesse G. Wakjira; M. Shahria Alam
- Year: 2024
- DOI: 10.1016/j.asoc.2024.111353
- Venue: Applied Soft Computing
- Countries: CA
- Source: openalex
- URL: https://doi.org/10.1016/j.asoc.2024.111353
- PDF: https://doi.org/10.1016/j.asoc.2024.111353

Ultra-high-performance concrete (UHPC) has gained prominence owing to its exceptional physical and mechanical properties and improved sustainability, making it ideal for large-scale structural applications. While numerous analytical studies have focused on predicting the stress-strain response of unconfined UHPC, there remains a lack of a reliable model for predicting the stress-strain response of confined UHPC, which poses challenges to efficient design and broader adoption, particularly in seismically active regions. To bridge this gap, the present study introduces a framework that implements machine learning (ML) models augmented by a state-of-the-art conditional tabular generative adversarial network (CTGAN) and Optuna, which a next-generation optimization framework, to accurately predict the peak and ultimate axial stress-strain responses of UHPC confined with either normal-strength steel or high-strength steel. The Optuna-optimized CTGAN is employed to address the issue of limited data by generating synthetic datasets of hypothetical confined UHPC specimens. A comprehensive database of confined UHPC stress-strain responses was compiled from existing literature and used to condition the CTGAN. The augmented database is then leveraged to develop a hybrid ML model that integrates extreme gradient boosting, gradient boosting machine, support vector regression, and K-nearest neighbors for predicting peak and ultimate stress-strain responses of confined UHPC. The predictive accuracy of the proposed hybrid ML model is evaluated and compared with a diverse set of ML models of varying complexity, and the results demonstrate its superior performance in predicting the peak and ultimate stress-strain response of confined UHPC. Furthermore, a graphical user interface of the proposed model is developed to facilitate its practical implementation and provide a rapid, autonomous, and accurate prediction of the stress-strain response of confined UHPC at both peak and ultimate states.

## 341. A New Ensemble Machine-Learning Framework for Searching Sweet Spots in Shale Reservoirs

- Authors: Jizhou Tang; Bo Fan; Lizhi Xiao; Shouceng Tian; Fengshou Zhang; Liyuan Zhang; David A. Weitz
- Year: 2020
- DOI: 10.2118/204224-pa
- Venue: SPE Journal
- Countries: CN; IL; KR; US
- Source: openalex
- URL: https://doi.org/10.2118/204224-pa

Summary Knowing the location of sweet spots benefits the horizontal well drilling and the selection of perforation clusters. Generally, geoscientists determine sweet spots from the well-logging interpretation. In this paper, a group of prevalent classifiers [extreme gradient boosting (XGBoost), unbiased boosting with categorical features (CatBoost), and light gradient boosting machine (LightGBM)] based on gradient-boosting decision trees (GBDTs) are introduced to automatically determine sweet spots based on well-log data sets. Compared with linear support vector machines (SVMs), these robust algorithms can deal with comparative scales of features and learn nonlinear decision boundaries. Moreover, they are less influenced by the presence of outliers. Another prevailing approach, named generative adversarial networks (GANs), is implemented to augment the training data set by using a small number of training samples. An extensive application has been built for the field cases in a certain oilfield. We randomly select 73 horizontal wells for training, and 13 features are chosen from well-log data sets. Compared with conventional SVMs, the agreement rates of interpretation by XGBoost and CatBoost are significantly improved. Without special preprocessing of the input data sets and conditional tabular GAN (CTGAN) model fine tuning, the fake data set could still bring a relatively low agreement rate for all detections. Finally, we propose an ensemble-learning framework concatenating multilevels of classifiers and improve agreement rate. In this paper, we illustrate a new tool for categorizing the reservoir quality by using GBDTs and ensemble models, which further helps search and identify sweet spots automatically. This tool enables us to integrate experts’ knowledge to the developed model, identify logging curves more efficiently, and cover more sweet spots during the drilling and completion treatment, which immensely decrease the cost of log interpretation.

## 342. Composite Travel Generative Adversarial Networks for Tabular and Sequential Population Synthesis

- Authors: Godwin Badu-Marfo; Bilal Farooq; Zachary Patterson
- Year: 2022
- DOI: 10.1109/tits.2022.3168232
- Venue: IEEE Transactions on Intelligent Transportation Systems
- Countries: CA
- Source: openalex
- URL: https://doi.org/10.1109/tits.2022.3168232

Agent-based microsimulation has become the standard to analyze intelligent transportation systems, using disaggregate travel demand data for entire populations, data that are not typically readily available. Population synthesis approaches are thus needed. We present Composite Travel Generative Adversarial Network (CTGAN), a novel deep generative model to estimate the underlying joint distribution of a population, that is capable of reconstructing composite synthetic agents having tabular (e.g. age and sex) as well as sequential mobility data (e.g. trip trajectory and sequence). The CTGAN model is compared with other recently proposed methods such as the Variational Autoencoders (VAE) method, which has shown success in high dimensional tabular population synthesis. We evaluate the performance of the synthesized outputs based on distribution similarity, multi-variate correlations and spatio-temporal metrics. The results show the consistent and accurate generation of synthetic populations and their tabular and spatially sequential attributes, generated over varying spatial scales and dimensions.

## 343. Improving Intrusion Detection for Imbalanced Network Traffic using Generative Deep Learning

- Authors: Amani A. Alqarni; El-Sayed M. El-Alfy
- Year: 2022
- DOI: 10.14569/ijacsa.2022.01304109
- Venue: International Journal of Advanced Computer Science and Applications
- Countries: SA
- Source: openalex
- URL: https://doi.org/10.14569/ijacsa.2022.01304109
- PDF: http://thesai.org/Downloads/Volume13No4/Paper_109-Improving_Intrusion_Detection_for_Imbalanced_Network_Traffic.pdf

Network security has become a serious issue since networks are vulnerable and subject to increasing intrusive activities. Therefore, network intrusion detection systems (IDSs) are an essential component to defend against these activities. One of the biggest issues encountered by IDSs is the class imbalance problem which leads to a biased performance by most machine learning models to normal activities (majority class). Several techniques were proposed to overcome the class-imbalance problem such as resampling, cost-sensitive, and en-semble learning techniques. Other issues related to intrusion detection data include mixed data types, and non-Gaussian and multimodal distributions. In this study, we employed a conditional tabular generative adversarial network (CTGAN) model with common machine learning algorithms to construct more effective detection systems while addressing the imbalance issue. CTGAN can generate samples of the minority class during training to make the dataset more balanced. To assess the effectiveness of the proposed IDS, we combined CTGAN with three machine learning algorithms: support vector machine (SVM), K-nearest neighbor (KNN), and decision tree (DT). The imbalanced NSL-KDD dataset was used and several experiments were conducted. The results showed that CTGAN can improve the performance of imbalance learning for intrusion detection with SVM and DT. On the other hand, KNN showed no improvement in the performance since it is less sensitive to the class imbalance problem. Moreover, the results proved that CTGAN can capture the distribution of discrete features better than continuous features.

## 344. A Multi-Agent Intrusion Detection System Optimized by a Deep Reinforcement Learning Approach with a Dataset Enlarged Using a Generative Model to Reduce the Bias Effect

- Authors: Matthieu Mouyart; Guilherme Medeiros Machado; Jae‐Yun Jun
- Year: 2023
- DOI: 10.3390/jsan12050068
- Venue: Journal of Sensor and Actuator Networks
- Countries: FR
- Source: openalex
- URL: https://doi.org/10.3390/jsan12050068
- PDF: https://www.mdpi.com/2224-2708/12/5/68/pdf?version=1695117988

Intrusion detection systems can defectively perform when they are adjusted with datasets that are unbalanced in terms of attack data and non-attack data. Most datasets contain more non-attack data than attack data, and this circumstance can introduce biases in intrusion detection systems, making them vulnerable to cyberattacks. As an approach to remedy this issue, we considered the Conditional Tabular Generative Adversarial Network (CTGAN), with its hyperparameters optimized using the tree-structured Parzen estimator (TPE), to balance an insider threat tabular dataset called the CMU-CERT, which is formed by discrete-value and continuous-value columns. We showed through this method that the mean absolute errors between the probability mass functions (PMFs) of the actual data and the PMFs of the data generated using the CTGAN can be relatively small. Then, from the optimized CTGAN, we generated synthetic insider threat data and combined them with the actual ones to balance the original dataset. We used the resulting dataset for an intrusion detection system implemented with the Adversarial Environment Reinforcement Learning (AE-RL) algorithm in a multi-agent framework formed by an attacker and a defender. We showed that the performance of detecting intrusions using the framework of the CTGAN and the AE-RL is significantly improved with respect to the case where the dataset is not balanced, giving an F1-score of 0.7617.

## 345. Generating Synthetic Dataset for ML-Based IDS Using CTGAN and Feature Selection to Protect Smart IoT Environments

- Authors: Saleh Alabdulwahab; Young-Tak Kim; Aria Seo; Yunsik Son
- Year: 2023
- DOI: 10.3390/app131910951
- Venue: Applied Sciences
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.3390/app131910951
- PDF: https://www.mdpi.com/2076-3417/13/19/10951/pdf?version=1696405900

Networks within the Internet of Things (IoT) have some of the most targeted devices due to their lightweight design and the sensitive data exchanged through smart city networks. One way to protect a system from an attack is to use machine learning (ML)-based intrusion detection systems (IDSs), significantly improving classification tasks. Training ML algorithms require a large network traffic dataset; however, large storage and months of recording are required to capture the attacks, which is costly for IoT environments. This study proposes an ML pipeline using the conditional tabular generative adversarial network (CTGAN) model to generate a synthetic dataset. Then, the synthetic dataset was evaluated using several types of statistical and ML metrics. Using a decision tree, the accuracy of the generated dataset reached 0.99, and its lower complexity reached 0.05 s training and 0.004 s test times. The results show that synthetic data accurately reflect real data and are less complex, making them suitable for IoT environments and smart city applications. Thus, the generated synthetic dataset can further train models to secure IoT networks and applications.

## 346. Evaluating the effect of curing conditions on the glass transition of the structural adhesive using conditional tabular generative adversarial networks

- Authors: Songbo Wang; Haixin Yang; Tim Stratford; Jiayi He; Biao Li; Jun Su
- Year: 2023
- DOI: 10.1016/j.engappai.2023.107796
- Venue: Engineering Applications of Artificial Intelligence
- Countries: CN; GB
- Source: openalex
- URL: https://doi.org/10.1016/j.engappai.2023.107796
- PDF: https://www.research.ed.ac.uk/files/404455372/j2024_1.pdf

## 347. Searching for Optimal Oversampling to Process Imbalanced Data: Generative Adversarial Networks and Synthetic Minority Over-Sampling Technique

- Authors: Gayeong Eom; Haewon Byeon
- Year: 2023
- DOI: 10.3390/math11163605
- Venue: Mathematics
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.3390/math11163605
- PDF: https://www.mdpi.com/2227-7390/11/16/3605/pdf?version=1692672852

Classification problems due to data imbalance occur in many fields and have long been studied in the machine learning field. Many real-world datasets suffer from the issue of class imbalance, which occurs when the sizes of classes are not uniform; thus, data belonging to the minority class are likely to be misclassified. It is particularly important to overcome this issue when dealing with medical data because class imbalance inevitably arises due to incidence rates within medical datasets. This study adjusted the imbalance ratio (IR) within the National Biobank of Korea dataset “Epidemiologic data of Parkinson’s disease dementia patients” to values of 6.8 (raw data), 9, and 19 and compared four traditional oversampling methods with techniques using the conditional generative adversarial network (CGAN) and conditional tabular generative adversarial network (CTGAN). The results showed that when the classes were balanced with CGAN and CTGAN, they showed a better classification performance than the more traditional oversampling techniques based on the AUC and F1-score. We were able to expand the application scope of GAN, widely used in unstructured data, to structured data. We also offer a better solution for the imbalanced data problem and suggest future research directions.

## 348. Imbalanced Disk Failure Data Processing Method Based on CTGAN

- Authors: Jingbo Jia; Peng Wu; Kai Zhang; Zhong Ji
- Year: 2022
- DOI: 10.1007/978-3-031-13829-4_55
- Venue: Lecture notes in computer science
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1007/978-3-031-13829-4_55

## 349. Data augmentation guided breast cancer diagnosis and prognosis using an integrated deep-generative framework based on breast tumor’s morphological information

- Authors: Muhammad Sakib Khan Inan; Sohrab Hossain; Mohammed Nazim Uddin
- Year: 2023
- DOI: 10.1016/j.imu.2023.101171
- Venue: Informatics in Medicine Unlocked
- Countries: BD
- Source: openalex
- URL: https://doi.org/10.1016/j.imu.2023.101171
- PDF: https://doi.org/10.1016/j.imu.2023.101171

Breast cancer is the world’s second-largest cause of cancer mortality among women. With the progress of artificial intelligence (AI) in healthcare, the survival rate of breast cancer patients has risen in recent years due to early diagnosis and effective prognosis. However, substantial AI research necessitates a large quantity of high-quality data to perform credible state-of-the-art research. To that end, this study investigates the potentiality of deep generative models including, the tabular variational autoencoder (TVAE) and the conditional generative adversarial network (CTGAN), to generate high-quality synthetic tabular data of breast tumors and support the diagnosis and prognosis of breast cancer. Additionally, this study proposes an integrated interpretable deep-learning framework that includes the synthetic generation of breast cancer data leading to the classification of breast cancer using the interpretable deep attention-based model TabNet based on the domain of breast cancer research at every stage of the research framework. The research findings are justified using benchmark breast cancer datasets. After rigorous investigation, it was found that the TVAE model outperformed the synthetic generation of breast tumor data with a Chi-Squared test(CS test) score of 0.916 (prognosis) and 0.964 (diagnosis) and a Kolmogorov Smirnov test(KS test) score of 0.887 (prognosis) and 0.928 (diagnosis). In the classification stage, despite being trained with only synthetically generated data, the interpretable TabNet architecture outperformed all other machine-learning and deep-learning classifiers with an accuracy of 96.66 % in diagnosis and 82.83 % in prognosis.

## 350. Data Augmentation of a Corrosion Dataset for Defect Growth Prediction of Pipelines Using Conditional Tabular Generative Adversarial Networks

- Authors: Haonan Ma; Mengying Geng; Fan Wang; Wenyue Zheng; Yibo Ai; Weidong Zhang
- Year: 2024
- DOI: 10.3390/ma17051142
- Venue: Materials
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.3390/ma17051142
- PDF: https://www.mdpi.com/1996-1944/17/5/1142/pdf?version=1709255585

Due to corrosion characteristics, there are data scarcity and uneven distribution in corrosion datasets, and collecting high-quality data is time-consuming and sometimes difficult. Therefore, this work introduces a novel data augmentation strategy using a conditional tabular generative adversarial network (CTGAN) for enhancing corrosion datasets of pipelines. Firstly, the corrosion dataset is subjected to data cleaning and variable correlation analysis. The CTGAN is then used to generate external environmental factors as input variables for corrosion growth prediction, and a hybrid model based on machine learning is employed to generate corrosion depth as an output variable. The fake data are merged with the original data to form the synthetic dataset. Finally, the proposed data augmentation strategy is verified by analyzing the synthetic dataset using different visualization methods and evaluation indicators. The results show that the synthetic and original datasets have similar distributions, and the data augmentation strategy can learn the distribution of real corrosion data and sample fake data that are highly similar to the real data. Predictive models trained on the synthetic dataset perform better than predictive models trained using only the original dataset. In comparative tests, the proposed strategy outperformed other data generation methods.

## 351. Privacy-Preserving Synthetic Data Generation Method for IoT-Sensor Network IDS Using CTGAN

- Authors: Saleh Alabdulwahab; Young-Tak Kim; Yunsik Son
- Year: 2024
- DOI: 10.3390/s24227389
- Venue: Sensors
- Countries: KR; US
- Source: openalex
- URL: https://doi.org/10.3390/s24227389
- PDF: https://www.mdpi.com/1424-8220/24/22/7389/pdf?version=1732091181

The increased usage of IoT networks brings about new privacy risks, especially when intrusion detection systems (IDSs) rely on large datasets for machine learning (ML) tasks and depend on third parties for storing and training the ML-based IDS. This study proposes a privacy-preserving synthetic data generation method using a conditional tabular generative adversarial network (CTGAN) aimed at maintaining the utility of IoT sensor network data for IDS while safeguarding privacy. We integrate differential privacy (DP) with CTGAN by employing controlled noise injection to mitigate privacy risks. The technique involves dynamic distribution adjustment and quantile matching to balance the utility-privacy tradeoff. The results indicate a significant improvement in data utility compared to the standard DP method, achieving a KS test score of 0.80 while minimizing privacy risks such as singling out, linkability, and inference attacks. This approach ensures that synthetic datasets can support intrusion detection without exposing sensitive information.

## 352. CTCN: a novel credit card fraud detection method based on Conditional Tabular Generative Adversarial Networks and Temporal Convolutional Network

- Authors: Xiaoyan Zhao; Shaopeng Guan
- Year: 2023
- DOI: 10.7717/peerj-cs.1634
- Venue: PeerJ Computer Science
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.7717/peerj-cs.1634
- PDF: https://doi.org/10.7717/peerj-cs.1634

Credit card fraud can lead to significant financial losses for both individuals and financial institutions. In this article, we propose a novel method called CTCN, which uses Conditional Tabular Generative Adversarial Networks (CTGAN) and temporal convolutional network (TCN) for credit card fraud detection. Our approach includes an oversampling algorithm that uses CTGAN to balance the dataset, and Neighborhood Cleaning Rule (NCL) to filter out majority class samples that overlap with the minority class. We generate synthetic minority class samples that conform to the original data distribution, resulting in a balanced dataset. We then employ TCN to analyze transaction sequences and capture long-term dependencies between data, revealing potential relationships between transaction sequences, thus achieving accurate credit card fraud detection. Experiments on three public datasets demonstrate that our proposed method outperforms current machine learning and deep learning methods, as measured by recall, F1-Score, and AUC-ROC.

## 353. Fault Diagnosis Method of Box-Type Substation Based on Improved Conditional Tabular Generative Adversarial Network and AlexNet

- Authors: Yong Liu; Jialin Zhou; Dong Zhang; Shaoyu Wei; Mingshun Yang; Xinqin Gao
- Year: 2024
- DOI: 10.3390/app14073112
- Venue: Applied Sciences
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.3390/app14073112
- PDF: https://www.mdpi.com/2076-3417/14/7/3112/pdf?version=1712558279

To solve the problem of low diagnostic accuracy caused by the scarcity of fault samples and class imbalance in the fault diagnosis task of box-type substations, a fault diagnosis method based on self-attention improvement of conditional tabular generative adversarial network (CTGAN) and AlexNet was proposed. The self-attention mechanism is introduced into the generator of CTGAN to maintain the correlation between the indicators of the input data, and a large amounts of high-quality data are generated according to the small number of fault samples. The generated data are input into the AlexNet model for fault diagnosis. The experimental results demonstrate that compared with the SMOTE and CTGAN methods, the dataset generated by the self-attention-conditional tabular generative adversarial network (SA-CTGAN) model has better data relevance. The accuracy of fault diagnosis by the proposed method reaches 94.81%, which is improved by about 11% compared with the model trained on the original data.

## 354. Enhancing Crop Classification Accuracy through Synthetic SAR-Optical Data Generation Using Deep Learning

- Authors: Ali Mirzaei; Hossein Bagheri; Iman Khosravi
- Year: 2023
- DOI: 10.3390/ijgi12110450
- Venue: ISPRS International Journal of Geo-Information
- Countries: IR
- Source: openalex
- URL: https://doi.org/10.3390/ijgi12110450
- PDF: https://www.mdpi.com/2220-9964/12/11/450/pdf?version=1698912454

Crop classification using remote sensing data has emerged as a prominent research area in recent decades. Studies have demonstrated that fusing synthetic aperture radar (SAR) and optical images can significantly enhance the accuracy of classification. However, a major challenge in this field is the limited availability of training data, which adversely affects the performance of classifiers. In agricultural regions, the dominant crops typically consist of one or two specific types, while other crops are scarce. Consequently, when collecting training samples to create a map of agricultural products, there is an abundance of samples from the dominant crops, forming the majority classes. Conversely, samples from other crops are scarce, representing the minority classes. Addressing this issue requires overcoming several challenges and weaknesses associated with the traditional data generation methods. These methods have been employed to tackle the imbalanced nature of training data. Nevertheless, they still face limitations in effectively handling minority classes. Overall, the issue of inadequate training data, particularly for minority classes, remains a hurdle that the traditional methods struggle to overcome. In this research, we explore the effectiveness of a conditional tabular generative adversarial network (CTGAN) as a synthetic data generation method based on a deep learning network, for addressing the challenge of limited training data for minority classes in crop classification using the fusion of SAR-optical data. Our findings demonstrate that the proposed method generates synthetic data with a higher quality, which can significantly increase the number of samples for minority classes, leading to a better performance of crop classifiers. For instance, according to the G-mean metric, we observed notable improvements in the performance of the XGBoost classifier of up to 5% for minority classes. Furthermore, the statistical characteristics of the synthetic data were similar to real data, demonstrating the fidelity of the generated samples. Thus, CTGAN can be employed as a solution for addressing the scarcity of training data for minority classes in crop classification using SAR–optical data.

## 355. CTTGAN: Traffic Data Synthesizing Scheme Based on Conditional GAN

- Authors: Jiayu Wang; Xuehu Yan; Lintao Liu; Longlong Li; Yongqiang Yu
- Year: 2022
- DOI: 10.3390/s22145243
- Venue: Sensors
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.3390/s22145243
- PDF: https://www.mdpi.com/1424-8220/22/14/5243/pdf?version=1657711617

Most machine learning algorithms only have a good recognition rate on balanced datasets. However, in the field of malicious traffic identification, benign traffic on the network is far greater than malicious traffic, and the network traffic dataset is imbalanced, which makes the algorithm have a low identification rate for small categories of malicious traffic samples. This paper presents a traffic sample synthesizing model named Conditional Tabular Traffic Generative Adversarial Network (CTTGAN), which uses a Conditional Tabular Generative Adversarial Network (CTGAN) algorithm to expand the small category traffic samples and balance the dataset in order to improve the malicious traffic identification rate. The CTTGAN model expands and recognizes feature data, which meets the requirements of a machine learning algorithm for training and prediction data. The contributions of this paper are as follows: first, the small category samples are expanded and the traffic dataset is balanced; second, the storage cost and computational complexity are reduced compared to models using image data; third, discrete variables and continuous variables in traffic feature data are processed at the same time, and the data distribution is described well. The experimental results show that the recognition rate of the expanded samples is more than 0.99 in MLP, KNN and SVM algorithms. In addition, the recognition rate of the proposed CTTGAN model is better than the oversampling and undersampling schemes.

## 356. Reducing overfitting in deep learning intrusion detection for power systems with CTGAN

- Authors: Lalit Agarwal; Bhavnesh Jaint; Anup Kumar Mandpura
- Year: 2024
- DOI: 10.1016/j.chaos.2024.115603
- Venue: Chaos Solitons & Fractals
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.1016/j.chaos.2024.115603

## 357. Data-driven estimates of the strength and failure modes of CFRP-steel bonded joints by implementing the CTGAN method

- Authors: Songbo Wang; Tim Stratford; Yang Li; Biao Li
- Year: 2024
- DOI: 10.1016/j.engfracmech.2024.109962
- Venue: Engineering Fracture Mechanics
- Countries: CN; GB
- Source: openalex
- URL: https://doi.org/10.1016/j.engfracmech.2024.109962
- PDF: https://www.research.ed.ac.uk/files/427226057/j2024_2.pdf

## 358. A K-means Improved CTGAN Oversampling Method for Data Imbalance Problem

- Authors: Chunsheng An; Jingtong Sun; Yifeng Wang; Qingjie Wei
- Year: 2021
- DOI: 10.1109/qrs54544.2021.00097
- Venue: 2021 IEEE 21st International Conference on Software Quality, Reliability and Security (QRS)
- Countries: CN; US
- Source: openalex
- URL: https://doi.org/10.1109/qrs54544.2021.00097

CTGAN is a tabular data synthesis method for privacy preservation, which is used in this paper for data imbalance problem. This paper proposes a method for dealing with imbalanced data sets that combines K-means clustering and CTGAN to address the imbalanced distribution of minority class examples that result from oversampling with CTGAN. By conducting experiments with the LightGBM algorithm on home loan and online shopping datasets, it is demonstrated that the CTGAN method achieves superior learning results in f1-score and G-mean metrics compared to the interpolation-based oversampling technique represented by SMOTE. The preceding results indicate that by applying the method described in this paper to handle an imbalanced dataset, one can obtain a dataset with more examples, a more uniform distribution, and less overfitting while still satisfying the original dataset's probability distribution.

## 359. Oversampling based on generative adversarial networks to overcome imbalance data in predicting fraud insurance claim

- Authors: Ranu A. Nugraha; Hilman F. Pardede; Agus Subekti
- Year: 2022
- DOI: 10.48129/kjs.splml.19119
- Venue: Kuwait Journal of Science
- Countries: ID
- Source: openalex
- URL: https://doi.org/10.48129/kjs.splml.19119
- PDF: https://journalskuwait.org/kjs/index.php/KJS/article/download/19119/949

Fraud on health insurance impacts cost overruns and a quality decline in health services in the long term. The use of machine learning to detect fraud on health insurance is increasingly popular. However, one challenge in predicting health insurance fraud is the data imbalance. The data imbalance can cause a bias towards the majority class in many machine learning methods. Oversampling is a solution for data imbalance by augmenting new data based on the existing minority class data. Recently, there has been growing interest in employing deep learning for data augmentation. One of them is using Generative Adversarial Networks (GAN). This paper proposes using GAN as an oversampling method to generate additional data for minority classes. Since data for detecting health insurance fraud are tabular, we adopt Conditional Tabular GAN (CTGAN) architecture where the generator is conditioned to adjust the tabular data input and receive additional information to produce samples according to the specified class conditions. The new balanced data are used to train 17 classification algorithms. Our experiments showed that the proposed method performs better than other oversampling methods on several evaluation metrics, i.e., accuracy, precision score, F1-score, and ROC.

## 360. An Improved Tabular Data Generator with VAE-GMM Integration

- Authors: Patricia A. Apellániz; Juan Parras; Santiago Zazo
- Year: 2024
- DOI: 10.23919/eusipco63174.2024.10715230
- Venue: 
- Countries: ES
- Source: openalex
- URL: https://doi.org/10.23919/eusipco63174.2024.10715230

The rising use of machine learning in various fields requires robust methods to create synthetic tabular data that preserve key characteristics while mitigating data scarcity chal-lenges. State-of-the-art approaches, such as CTGAN and TVAE, face difficulties with the intricate structures inherent in tabular data, which often comprise continuous and discrete features with non-Gaussian distributions. To address these limitations, we pro-pose a novel approach based on Variational Autoencoders (VAEs) enhanced with a Bayesian Gaussian Mixture (BGM) model. Unlike other methods that alter the Gaussian prior of the VAE, our approach trains the VAE conventionally and then applies the BGM model to the learned latent space. This allows for a more accurate representation of the underlying data distribution during data generation. Moreover, our model offers enhanced flexibility by accommodating various differentiable distributions for individual features, enabling the handling of continuous and discrete data types. Thorough validation on three real-world datasets, including medically relevant ones, demonstrates significant outperformance compared to CTGAN and TVAE. Our model shows promise as a valuable tool for synthetic tabular data generation across diverse domains, particularly in healthcare.

## 361. Customer Personality Analysis for Churn Prediction Using Hybrid Ensemble Models and Class Balancing Techniques

- Authors: Noman Ahmad; Mazhar Javed Awan; Haitham Nobanee; Azlan Mohd Zain; Ansar Naseem; Amena Mahmoud
- Year: 2023
- DOI: 10.1109/access.2023.3334641
- Venue: IEEE Access
- Countries: AE; EG; GB; MY; PK
- Source: openalex
- URL: https://doi.org/10.1109/access.2023.3334641
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/6514899/10322869.pdf

Today’s businesses rely heavily on focused marketing to improve their chances of growing and keeping their consumer base. Internet behemoths like Google and Facebook have expanded their business models around targeted advertisements that support business growth. Customer personality identification helps for churn prediction for companies. This problem arises in several companies where customer leaves companies for many reasons. This gap leads to conduct study for customer personality analysis. The collected dataset was highly imbalanced in nature. Two class balancing approaches CTGAN (Conditional tabular Generative adversarial networks) and SMOTE (Synthetic minority oversampling technique) has been utilized to equalize the both classes. There are three ensemble approaches such as bagging, boosting and stacking have been utilized for modeling purpose bagging approach uses Random Forest (RF) boosting utilizes XGBoost (XGB), Light Gradient Boosting Machine (LGBM) and ADA Boost (ADA B). The proposed Hybrid Model HSLR comprises of RF, XGB, ADA Boost, LGBM approaches as base classifiers and LR as a Meta classifier. Three testing independent set, k-fold with 5 and 10 folds have been utilized. To evaluate the performance of classifiers evaluation metrics such as Accuracy score, Precision, Recall, F1 score, MCC and ROC score have been utilized. The SMOTE generated data has shown results as compare with CTGAN generated data. The SMOTE approach has shown the highest results of 94.06, 94.23, 94.28, 94.05, 88.13 and 0.984 as accuracy score, Precision, recall, F1, MCC and Roc score respectively.

## 362. Generative adversarial network approach for predicting tensile behavior and failure pattern of fiber-reinforced cementitious matrices

- Authors: Aman Kumar; Afshin Marani; Moncef L. Nehdi
- Year: 2025
- DOI: 10.1016/j.engstruct.2025.120276
- Venue: Engineering Structures
- Countries: CA
- Source: openalex
- URL: https://doi.org/10.1016/j.engstruct.2025.120276
- PDF: https://doi.org/10.1016/j.engstruct.2025.120276

Fiber-reinforced cementitious matrices (FRCM) are a sustainable solution for rehabilitating aging civil infrastructure. Yet, there is a lack of consistent models for predicting the tensile strength, ultimate strain, and failure pattern of FRCM coupons, posing hurdles against effective design and wider applications. The present study resolves this gap by coining a novel machine learning (ML) framework based on conditional tabular generative adversarial network (CTGAN) to estimate the tensile strength, ultimate strain, and failure patterns of FRCM coupons. Firstly, an extensive dataset of FRCM coupons considering tensile strength, ultimate strain, and failure patterns was collected from relevant publications. CTGAN was then employed to generate synthetic data, thus alleviating the problem of limited experimental data. A training subset encompassing 70 % of the collected data was used for synthetic data generation using CTGAN. The augmented dataset was used to develop ML models to prognosticate the tensile behavior of FRCM coupons. Results show that the synthetic dataset offers credibility enabling the development of ML models with higher prediction accuracy in estimating the tensile behavior of FRCM coupons compared to models trained with real datasets. Among the developed models trained with synthetic data, eXtreme gradient boosting showed the highest prediction accuracy, achieving testing R 2 and MAE values of 0.9690 and 84.50 MPa, respectively, for the tensile strength of FRCM coupons. SHAP feature importance analysis identified fiber density, width of FRCM coupons, thickness of fabric, and length of FRCM coupons as the most influential parameters affecting tensile strength and ultimate strain, conforming to domain knowledge in the open literature. • Novel conditional tabular generative adversarial network generated reliable synthetic data on FRCM tensile behavior. • Machine learning models trained on synthetic data yield superior accuracy to models trained on limited experimental data. • eXtreme gradient boosting was the most accurate in predicting tensile behavior and failure patterns. • Accurate estimation of FRCM’s coupon tensile behavior enables accurate FRCM design in structural rehabilitation.

## 363. Synthetic Data Augmentation for Imbalanced Tabular Protein Subcellular Localization: A Comparative Study of SMOTE, CTGAN, TVAE, and TabDDPM Methods

- Authors: Ali Fatih Gündüz; Canan Batur Şahin
- Year: 2026
- DOI: 10.3390/app16083694
- Venue: Applied Sciences
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3390/app16083694

<jats:p>Class imbalance is a persistent challenge in supervised machine learning, particularly in biological datasets where minority classes represent functionally critical categories. Synthetic data generation has emerged as a principal strategy for mitigating this problem, yet systematic comparisons of classical and modern deep generative approaches remain limited. This study presents a comprehensive benchmark evaluation of four synthetic data generation methods—SMOTE, CTGAN, TVAE, and TabDDPM—across two well-established biological datasets from the UCI Machine Learning Repository: the E. coli protein localization dataset (307 samples, 6 features, 4 classes) and the yeast protein localization dataset (1299 samples, 8 features, 4 classes). Synthetic data quality was rigorously assessed using a multi-dimensional evaluation framework encompassing distributional fidelity (Fréchet Distance, Wasserstein Distance), machine learning utility (Train-on-Synthetic-Test-on-Real and Train-on-Real-Test-on-Real protocols using XGBoost version 3.2.0, Logistic Regression, Support Vector Machines, and Random Forest), and distinguishability (Classifier Two-Sample Test). The datasets are rather imbalanced. During the experiments, the dataset size increased to three times its original size while preserving the imbalanced class-sample ratio. To evaluate the quality of synthetic data, the max(AUC,1−AUC) score is proposed. This score is inversely proportional to classification performance, indicating that synthetic data are not easily distinguishable from real data. Per-class analysis reveals that minority classes remain the primary challenge across all generative methods. SMOTE and TabDDPM obtained the highest predictive utility F1-scores across both datasets. TVAE offers the strongest distributional fidelity among deep generative models, producing synthetic samples that are most difficult to distinguish from real data (lowest C2ST scores). CTGAN exhibits significant performance degradation on both small- and medium-scale datasets, with F1 utility ratios below 0.50.</jats:p>

## 364. A comparative study on SMOTE, CTGAN, and hybrid SMOTE-CTGAN for medical data augmentation

- Authors: Ninda Khoirunnisa; Miftahurrahma Rosyda
- Year: 2025
- DOI: 10.31763/sitech.v6i1.2203
- Venue: Science in Information Technology Letters
- Countries: 
- Source: crossref
- URL: https://doi.org/10.31763/sitech.v6i1.2203
- PDF: https://pubs2.ascee.org/index.php/sitech/article/viewFile/2203/pdf

<jats:p>The imbalance of clinical datasets remains a challenge in medical data mining, often resulting in models biased toward majority outcomes and reduced sensitivity to rare but clinically critical cases. This study presents a comparative evaluation of three augmentation strategies—Synthetic Minority Oversampling Technique (SMOTE), Conditional Tabular GAN (CTGAN), and a hybrid SMOTE+CTGAN—on the Framingham Heart Study dataset for cardiovascular disease prediction. Augmented datasets were evaluated using Decision Tree, Random Forest, and XGBoost classifiers across multiple metrics, including accuracy, precision, recall, and F1-score. Results demonstrate that classifiers trained on imbalanced data achieved high accuracy but poor minority recall (0.40), confirming model’s bias toward majority class. SMOTE yielded the strongest improvements in minority recall (up to 0.88 with XGBoost) and balanced F1 across classes, though at the cost of reduced majority recall. CTGAN and SMOTE+CTGAN delivered more moderate improvements in minority recall (0.66–0.77) while preserving higher majority recall (0.86), providing a gentler trade-off. These findings indicate that while SMOTE remains a robust baseline for addressing imbalance, hybrid and GAN-based approaches offer practical alternatives for preserving majority performance. The results highlight that augmentation choice should be informed by clinical context.</jats:p>

## 365. CTGAN-Bandit: A Conditional Tabular GAN Model Leveraging Upper Confidence Bound Estimators for Hardware Design Verification

- Authors: Lorenzo Ferretti; Surya Teja Bandlamudi; Nihar Athreyas; Michael Yan; Vikram Narayan; Samir Mittal
- Year: 2025
- DOI: 10.1109/wmed65750.2025.11026967
- Venue: 2025 IEEE Workshop on Microelectronics and Electron Devices (WMED)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/wmed65750.2025.11026967

## 366. IMG-14. Post-Therapy Glioblastoma Multiforme (GBM) Progression Assessment using Conditional Tabular Generative Adversarial Network (CTGAN)-augmented Radiomics based Imaging Signature

- Authors: Dev Deveswar Rana; Shivani Prasad; Sanjay Saxena
- Year: 2025
- DOI: 10.1093/neuonc/noaf201.1093
- Venue: Neuro-Oncology
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1093/neuonc/noaf201.1093
- PDF: https://academic.oup.com/neuro-oncology/article-pdf/27/Supplement_5/v275/65257372/noaf201.1093.pdf

<jats:title>Abstract</jats:title>
                  <jats:sec>
                    <jats:title>BACKGROUND</jats:title>
                    <jats:p>Differentiating pseudo-progression (PsP) from true tumour progression (TP) in patients with GBM after standard chemoradiotherapy is a significant diagnostic challenge because of the substantial overlap in their radiological characteristics. Precise differentiation is very important for optimizing therapeutic prognosis and decisions. Advanced computational methodologies have demonstrated promising results in enhancing diagnostic precision. Furthermore, Generative Adversarial Networks have emerged as powerful tools for addressing class imbalance and improving model robustness by synthetically augmenting data in limited data scenarios such as GBM progression assessment.</jats:p>
                  </jats:sec>
                  <jats:sec>
                    <jats:title>METHODS</jats:title>
                    <jats:p>This study utilized multiparametric structural MRI sequences (T1, T2, FLAIR, and T1GD) from 58 GBM patients which comprises 41 cases of TP and 17 cases of PsP. Tumor regions were segmented using the nnU-Net framework and regions of interest were defined for radiomic feature extraction. Handcrafted features such as shape, texture, and intensity were extracted. To mitigate class imbalance a CTGAN was implemented. Feature selection was performed using a Variational Autoencoder followed by dimensionality reduction with Principal Component Analysis. A 5-fold cross-validation strategy was employed to train and evaluate multiple imaging signatures for distinguishing between PsP and TP.</jats:p>
                  </jats:sec>
                  <jats:sec>
                    <jats:title>RESULTS</jats:title>
                    <jats:p>The SVM based imaging signatures yielded promising results with an accuracy of 91.84% ± 0.0359 (95% CI – 0.841 to 0.989) and AUC of 0.9667 ± 0.378 (95% CI - 0.920 to 0.998). This demonstrates the model’s strong predictive performance and robustness given the limited dataset of 58 patients. The low standard error further indicates consistent performance across folds which affirms the reliability of the classification pipeline.</jats:p>
                  </jats:sec>
                  <jats:sec>
                    <jats:title>CONCLUSION</jats:title>
                    <jats:p>This study demonstrates the effectiveness of a hybrid radiomics and machine learning framework enhanced with CTGAN for distinguishing PsP from TP in GBM. The SVM model achieved high accuracy with consistent performance across folds. These results highlight the potential of AI-driven radiomic models as reliable tools for post-therapy GBM assessment.</jats:p>
                  </jats:sec>

## 367. Evaluating Fidelity in Synthetic Tabular Data Generation: A Comparative Study of CTGAN and TVAE for Human Activity Recognition Datasets

- Authors: Majid Liaquat; Chris Nugent; Ian Cleland; Naveed Khan
- Year: 2026
- DOI: 10.1007/978-3-032-16992-1_2
- Venue: Lecture Notes in Networks and Systems
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1007/978-3-032-16992-1_2

## 368. AE-CTGAN: Autoencoder–Conditional Tabular GAN for Multi-Omics Imbalanced Class Handling and Cancer Outcome Prediction

- Authors: Ibrahim Al-Hurani; Sara H. ElFar; Abedalrhman Alkhateeb; Salama Ikki
- Year: 2026
- DOI: 10.3390/a19020095
- Venue: Algorithms
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3390/a19020095

<jats:p>The rapid advancement of sequencing technologies has led to the generation of complex multi-omics data, which are often high-dimensional, noisy, and imbalanced, posing significant challenges for traditional machine learning methods. The novelty of this work resides in the architecture-level integration of autoencoders with Generative Adversarial Network (GAN) and Conditional Tabular Generative Adversarial Network (CTGAN) models, where the autoencoder is employed for latent feature extraction and noise reduction, while GAN-based models are used for realistic sample generation and class imbalance mitigation in multi-omics cancer datasets. This study proposes a novel framework that combines an autoencoder for dimensionality reduction and a CTGAN for generating synthetic samples to balance underrepresented classes. The process starts with selecting the most discriminative features, then extracting latent representations for each omic type, merging them, and generating new minority samples. Finally, all samples are used to train a neural network to predict specific cancer outcomes, defined here as clinically relevant biomarkers or patient characteristics. In this work, the considered outcome in the bladder cancer is Tumor Mutational Burden (TMB), while the breast cancer outcome is menopausal status, a key factor in treatment planning. Experimental results show that the proposed model achieves high precision, with an average precision of 0.9929 for TMB prediction in bladder cancer and 0.9748 for menopausal status in breast cancer, and reaches perfect precision (1.000) for the positive class in both cases. In addition, the proposed AE–CTGAN framework consistently outperformed an autoencoder combined with a standard GAN across all evaluation metrics, achieving average accuracies of 0.9929 and 0.9748, recall values of 0.9846 and 0.9777, and F1-scores of 0.9922 for bladder and breast cancer datasets, respectively. A comparative fidelity analysis in the latent space further demonstrated the superiority of CTGAN, reducing the average Euclidean distance between real and synthetic samples by approximately 72% for bladder cancer and by up to 84% for breast cancer compared to a standard GAN. These findings confirm that CTGAN generates high-fidelity synthetic samples that preserve the structural characteristics of real multi-omics data, leading to more reliable class balancing and improved predictive performance. Overall, the proposed framework provides an effective and robust solution for handling class imbalance in multi-omics cancer data and enhances the accuracy of clinically relevant outcome prediction.</jats:p>

## 369. KG-CTGAN: A Novel Approach Using Glowworm Swarm Optimized Clustering and CTGAN to Handle Imbalance Medical Data

- Authors: Kaikashan Siddavatam; Subhash Shinde
- Year: 2026
- DOI: 10.1007/978-3-032-15407-1_9
- Venue: Lecture Notes in Networks and Systems
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1007/978-3-032-15407-1_9

## 370. Ensemble Machine Learning for Enhanced Diabetes Detection Using CTGAN-Balanced Data

- Authors: Mohammad Reza Abbaszadeh Bavil Soflaei; Karim Samadzamini
- Year: 2025
- DOI: 10.22541/au.173638341.18317097/v1
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.22541/au.173638341.18317097/v1

<jats:p>Diabetes, a pervasive chronic disease, characterized by insufficient
insulin production or the body’s inefficiency in insulin utilization.
With rising global spread and severe consequences like blindness, kidney
failure, and stroke, timely detection is paramount. This paper
introduces an innovative framework for diabetes detection using machine
learning, concentrating on a benchmark dataset in the field, Pima
Indians Diabetes Database. The dataset inherent challenges like class
imbalance and missing values are dealt with utilizing Conditional
Tabular Generative Adversarial network (CTGAN), and pre-processing
methods. Furthermore, the study also employs an ensemble approach,
combining four base models—Random Forest (RF), Logistic Regression
(LR), Gaussian Naive Bayes (GNB), and K-Nearest-Neighbor (KNN)—trained
on a balanced dataset and amalgamated through stacking with an Extreme
Gradient Boosting (XGB) meta-classifier. The resulting ensemble model
demonstrates superior performance, achieving 96% accuracy on the test
set. In comparison, standalone models, exhibit lower accuracy at 85% on
an average. This work highlights the effectiveness of ensemble
techniques and data synthesis in improving diabetes prediction, and
emphasizes the significance of early detection in mitigating the global
impact of this life-threatening disease.</jats:p>

## 371. Physical-Data Coupling Driven Date Augmentation Framework Based on Bayesian-Physical Informed-Ctgan

- Authors: Shiqi Wang; Peng Xia; Fuyuan Gong; Yuxi Zhao; Peng Lin
- Year: 2024
- DOI: 10.2139/ssrn.4986504
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.2139/ssrn.4986504

## 372. Data Synthesis Technique for Categorical Pestes Des Petits Ruminants (PPR) Data Using CTGAN Model

- Authors: Devotha G. Nyambo; Nguse Ngulumbi; Neema Mduma; Ramadhani Sinde; Tumaini Lyimo
- Year: 2023
- DOI: 10.20944/preprints202305.0777.v1
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.20944/preprints202305.0777.v1

<jats:p>Data scarcity is a significant challenge in the field of Machine Learning (ML), as data collection can be expensive, time-consuming, and difficult, particularly in developing countries. This challenge is exaggerated on the need to use dataset for livestock disease predictions for early intervention and surveillance. To address this challenge, this paper presents a data synthesis method that has been used to accurately generate new data samples from few real-world data. With much data available to train the ML models, overfitting is eliminated. We present the use of Generative Adversarial Networks mainly the Conditional Tabular Generative Adversarial Network to synthesize categorical data for training machine learning models for prediction of the Pestes des Petits Ruminants (PPR) disease. The results showed that training score became 0.89 and the cross-validation score was 0.87 after synthesized data was used with Random Forest algorithm. The resulting dataset can be used to support the prediction and surveillance of the Pestes des Petits Ruminants (PPR) disease. The proposed method can also be applied to any domain with categorical data, and has the potential to improve the performance of machine learning models with increased data availability.</jats:p>

## 373. An Improved CTGAN for Data Processing Method of Imbalanced Disk Failure

- Authors: jingbo jia; Peng Wu; Hussain Dawood
- Year: 2023
- DOI: 10.2139/ssrn.4598620
- Venue: SSRN Electronic Journal
- Countries: 
- Source: crossref
- URL: https://doi.org/10.2139/ssrn.4598620

## 374. A Study on the Introduction of CTGAN Oversampling Algorithm to improve Imbalance Problem in Intrusion Detection Data

- Authors: Yoon-hee Choe; Kyoung-Whan Oh
- Year: 2020
- DOI: 10.7840/kics.2020.45.12.2114
- Venue: The Journal of Korean Institute of Communications and Information Sciences
- Countries: 
- Source: crossref
- URL: https://doi.org/10.7840/kics.2020.45.12.2114

## 375. Data synthesis and adversarial networks: A review and meta-analysis in cancer imaging

- Authors: Richard Osuala; Kaisar Kushibar; Lidia Garrucho; Akis Linardos; Zuzanna Szafranowska; Stefan Klein; Ben Glocker; Oliver Díaz; Karim Lekadir
- Year: 2022
- DOI: 10.1016/j.media.2022.102704
- Venue: Medical Image Analysis
- Countries: ES; GB; NL
- Source: openalex
- URL: https://doi.org/10.1016/j.media.2022.102704
- PDF: https://ars.els-cdn.com/content/image/1-s2.0-S1361841522003322-ga1_lrg.jpg

Despite technological and medical advances, the detection, interpretation, and treatment of cancer based on imaging data continue to pose significant challenges. These include inter-observer variability, class imbalance, dataset shifts, inter- and intra-tumour heterogeneity, malignancy determination, and treatment effect uncertainty. Given the recent advancements in image synthesis, Generative Adversarial Networks (GANs), and adversarial training, we assess the potential of these technologies to address a number of key challenges of cancer imaging. We categorise these challenges into (a) data scarcity and imbalance, (b) data access and privacy, (c) data annotation and segmentation, (d) cancer detection and diagnosis, and (e) tumour profiling, treatment planning and monitoring. Based on our analysis of 164 publications that apply adversarial training techniques in the context of cancer imaging, we highlight multiple underexplored solutions with research potential. We further contribute the Synthesis Study Trustworthiness Test (SynTRUST), a meta-analysis framework for assessing the validation rigour of medical image synthesis studies. SynTRUST is based on 26 concrete measures of thoroughness, reproducibility, usefulness, scalability, and tenability. Based on SynTRUST, we analyse 16 of the most promising cancer imaging challenge solutions and observe a high validation rigour in general, but also several desirable improvements. With this work, we strive to bridge the gap between the needs of the clinical cancer imaging community and the current and prospective research on data synthesis and adversarial networks in the artificial intelligence community.

## 376. Product Processing Quality Classification Model for Small-Sample and Imbalanced Data Environment

- Authors: Feixiang Liu; Yiru Dai
- Year: 2022
- DOI: 10.1155/2022/9024165
- Venue: Computational Intelligence and Neuroscience
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1155/2022/9024165
- PDF: https://downloads.hindawi.com/journals/cin/2022/9024165.pdf

With the rapid development of machine learning technology, how to use machine learning technology to empower the manufacturing industry has become a research hotspot. In order to solve the problem of product quality classification in a small sample data and imbalanced data environment, this paper proposes a data generation model called MSMOTE-GAN, which is based on Mahalanobis Synthetic Minority Oversampling Technology (MSMOTE) and Generative Adversarial Network (GAN). Among them, MSMOTE is proposed to solve the problem of the sample biased to the majority class expanded by methods such as GAN in a sample imbalanced environment. Based on the traditional SMOTE method, the sample distance measurement method is modified from Euclidean distance to Mahalanobis distance, taking into account the correlation between attributes and the influence of dimensions on the sample distance. In the data generation model, MSMOTE is used to balance the positive and negative samples in the data. GAN generates fake data with the same distribution as the original data based on a balanced data set and expands the sample size to solve the problems of overfitting and insufficient model expression ability that occur when the sample size is too small. The quality classification framework of water heater liner based on the data generation model and Random Forest is constructed, and the process of the quality classification of water heater liner under the environment of small sample data and imbalanced data is fully described. This paper compares the MSMOTE-GAN model, Bootstrap, and tableGAN on the water heater liner production line data set and the public data set. The experimental result shows that the expanded data set of the MSMOTE-GAN model can effectively improve the performance of the classification model.

## 377. Predicting the hardness of diamond-like carbon coatings using machine learning and generative adversarial networks

- Authors: Tahir Mahmood; Abdul Wasy Zia
- Year: 2025
- DOI: 10.1016/j.jmapro.2025.05.060
- Venue: Journal of Manufacturing Processes
- Countries: GB
- Source: openalex
- URL: https://doi.org/10.1016/j.jmapro.2025.05.060
- PDF: https://doi.org/10.1016/j.jmapro.2025.05.060

Producing diamond-like carbon (DLC) coatings with increased hardness remains an inspiration for achieving diamond-like properties. A multivariable parametric analysis may necessitate 50+ experiments to establish optimum plasma dynamics with a combination of electric, magnetic, kinetic, and thermal energies that build a DLC coating of a specific hardness. Overall, this places a strain on resources and the climate. This research aims to predict the hardness of DLC coatings as a function of bias voltage (0 to 140 V) and annealing temperature as a direct and two-stage heat treatment. In addition, this work investigates the critical features for estimating the hardness of DLC coatings. The conditional tabular generative adversarial networks (CTGANs) model is used to expand the small experimental data of DLC coatings, and a large dataset is obtained from the optimal CTGANs model. A range of 15 machine learning models are used to predict the hardness of DLC, and their efficacy is measured using the six well-known error-based performance measures. The data-driven modelling reflects that top-performing models, including SVR, XGBoost, LightGBM, CatBoost, ANNs, and FNNs, achieved exceptional predictive accuracy (∼99.9 %). Furthermore, the significance of each explanatory variable is indicated using the Shapley additive explanations (SHAP) model, which identified bias voltages of 40 V and 120 V and second-stage heat treatment as critical factors influencing hardness. Therefore, it is concluded that the implementation of the second stage potentially increasing the hardness and the bias levels of 40 and 120 V may decrease the hardness of the DLC coating. The approach demonstrates a novel and efficient data-driven strategy for optimizing DLC coating processes, offering significant potential to accelerate material design in applications where experimental trials are resource-intensive.

## 378. TableGAN-MCA: Evaluating Membership Collisions of GAN-Synthesized Tabular Data Releasing

- Authors: Aoting Hu; Renjie Xie; Zhigang Lü; Aiqun Hu; Minhui Xue
- Year: 2021
- DOI: 10.48550/arxiv.2107.13190
- Venue: arXiv (Cornell University)
- Countries: AU; CN
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2107.13190
- PDF: https://arxiv.org/pdf/2107.13190

Generative Adversarial Networks (GAN)-synthesized table publishing lets people privately learn insights without access to the private table. However, existing studies on Membership Inference (MI) Attacks show promising results on disclosing membership of training datasets of GAN-synthesized tables. Different from those works focusing on discovering membership of a given data point, in this paper, we propose a novel Membership Collision Attack against GANs (TableGAN-MCA), which allows an adversary given only synthetic entries randomly sampled from a black-box generator to recover partial GAN training data. Namely, a GAN-synthesized table immune to state-of-the-art MI attacks is vulnerable to the TableGAN-MCA. The success of TableGAN-MCA is boosted by an observation that GAN-synthesized tables potentially collide with the training data of the generator. Our experimental evaluations on TableGAN-MCA have five main findings. First, TableGAN-MCA has a satisfying training data recovery rate on three commonly used real-world datasets against four generative models. Second, factors, including the size of GAN training data, GAN training epochs and the number of synthetic samples available to the adversary, are positively correlated to the success of TableGAN-MCA. Third, highly frequent data points have high risks of being recovered by TableGAN-MCA. Fourth, some unique data are exposed to unexpected high recovery risks in TableGAN-MCA, which may attribute to GAN's generalization. Fifth, as expected, differential privacy, without the consideration of the correlations between features, does not show commendable mitigation effect against the TableGAN-MCA. Finally, we propose two mitigation methods and show promising privacy and utility trade-offs when protecting against TableGAN-MCA.

## 379. Applying Deep Generative Neural Networks to Data Augmentation for Consumer Survey Data with a Small Sample Size

- Authors: Shinya Watanuki; Katsue Edo; Toshihiko Miura
- Year: 2024
- DOI: 10.3390/app14199030
- Venue: Applied Sciences
- Countries: JP
- Source: openalex
- URL: https://doi.org/10.3390/app14199030
- PDF: https://www.mdpi.com/2076-3417/14/19/9030/pdf?version=1728208893

Questionnaire consumer survey research is primarily used for marketing research. To obtain credible results, collecting responses from numerous participants is necessary. However, two crucial challenges prevent marketers from conducting large-sample size surveys. The first is cost, as organizations with limited marketing budgets struggle to gather sufficient data. The second involves rare population groups, where it is difficult to obtain representative samples. Furthermore, the increasing awareness of privacy and security concerns has made it challenging to ask sensitive and personal questions, further complicating respondent recruitment. To address these challenges, we augmented small-sized datawith synthesized data generated using deep generative neural networks (DGNNs). The synthesized data from three types of DGNNs (CTGAN, TVAE, and CopulaGAN) were based on seed data. For validation, 11 datasets were prepared: real data (original and seed), synthesized data (CTGAN, TVAE, and CopulaGAN), and augmented data (original + CTGAN, original + TVAE, original + CopulaGAN, seed + CTGAN, seed + TVAE, and seed + CopulaGAN). The large-sample-sized data, termed “original data”, served as the benchmark, whereas the small-sample-sized data acted as the foundation for synthesizing additional data. These datasets were evaluated using machine learning algorithms, particularly focusing on classification tasks. Conclusively, augmenting and synthesizing consumer survey data have shown potential in enhancing predictive performance, irrespective of the dataset’s size. Nonetheless, the challenge remains to minimize discrepancies between the original data and other datasets concerning the values and orders of feature importance. Although the efficacy of all three approaches should be improved in future work, CopulaGAN more accurately grasps the dependencies between the variables in table data compared with the other two DGNNs. The results provide cues for augmenting data with dependencies between variables in various fields.

## 380. Principles of Synthesizing Medical Datasets

- Authors: Michal Kolárik; Lucia Gojdičová; Ján Paralič
- Year: 2022
- DOI: 10.2478/aei-2022-0019
- Venue: Acta Electrotechnica et Informatica
- Countries: SK
- Source: openalex
- URL: https://doi.org/10.2478/aei-2022-0019
- PDF: https://sciendo.com/pdf/10.2478/aei-2022-0019

Abstract Data in many application domains provide a valuable source for analysis and data-driven decision support. On the other hand, legislative restrictions are provided, especially on personal data and patients’ data in the medical domain. In order to maximize the use of data for decision purposes and comply with legislation, sensitive data needs to be properly anonymized or synthetized. This article contributes to the area of medical records synthesis. We first introduce this topic and present it in a broader context, as well as in terms of methods used and metrics for their evaluation. Based on the related work analysis, we selected CTGAN neural network model for data synthesis and experimentally validated it on three different medical datasets. The results were evaluated both quantitatively by means of selected metrics as well as qualitatively by means of proper visualization techniques. The results showed that in most cases, the synthesized dataset is a very good approximation of the original one, with similar prediction performance.

## 381. Enhancing Network Intrusion Detection Performance using Generative Adversarial Networks

- Authors: Xinxing Zhao; Kar Wai Fok; Vrizlynn L. L. Thing
- Year: 2024
- DOI: 10.48550/arxiv.2404.07464
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2404.07464
- PDF: https://arxiv.org/pdf/2404.07464

Network intrusion detection systems (NIDS) play a pivotal role in safeguarding critical digital infrastructures against cyber threats. Machine learning-based detection models applied in NIDS are prevalent today. However, the effectiveness of these machine learning-based models is often limited by the evolving and sophisticated nature of intrusion techniques as well as the lack of diverse and updated training samples. In this research, a novel approach for enhancing the performance of an NIDS through the integration of Generative Adversarial Networks (GANs) is proposed. By harnessing the power of GANs in generating synthetic network traffic data that closely mimics real-world network behavior, we address a key challenge associated with NIDS training datasets, which is the data scarcity. Three distinct GAN models (Vanilla GAN, Wasserstein GAN and Conditional Tabular GAN) are implemented in this work to generate authentic network traffic patterns specifically tailored to represent the anomalous activity. We demonstrate how this synthetic data resampling technique can significantly improve the performance of the NIDS model for detecting such activity. By conducting comprehensive experiments using the CIC-IDS2017 benchmark dataset, augmented with GAN-generated data, we offer empirical evidence that shows the effectiveness of our proposed approach. Our findings show that the integration of GANs into NIDS can lead to enhancements in intrusion detection performance for attacks with limited training data, making it a promising avenue for bolstering the cybersecurity posture of organizations in an increasingly interconnected and vulnerable digital landscape.

## 382. Synthetic Financial Data: A Case Study Regarding Polish Limited Liability Companies Data

- Authors: Aleksandra Szymura
- Year: 2024
- DOI: 10.15611/eada.2024.2.01
- Venue: Econometrics
- Countries: PL
- Source: openalex
- URL: https://doi.org/10.15611/eada.2024.2.01
- PDF: https://dbc.wroc.pl/Content/127165/Szymura_Synthetic_Financial_Data_A_Case_Study.pdf

Aim: The aim of this article was to present and evaluate the concept of synthetic data. They are completely new, artificially generated data, but keep the statistical properties of real data. Due to the statistical similarity with real data, they can be used instead of them. This action allows data to be shared externally while guaranteeing their privacy. Methodology: New datasets were generated based on financial information about Polish limited liability companies, which come from the Orbis database and refer to 2020. To create synthetic data, it was decided to use generative models: CTGAN (based on GAN architecture) and TVAE (based on autoencoders). Lastly, the synthetic data were compared with the real ones in terms of statistical properties (e.g. shape of distributions, correlations etc.) and their applicability in data analysis (the PCA method). Results: The Overall Quality Score was higher for the data generated by TVAE, but after examining the results in more detail, it was seen that the data generated by CTGAN had a better quality in terms of keeping the statistical properties of the real data. Comparing the results of the PCA method, TVAE was better than CTGAN. In addition, the TVAE method was less time-consuming than CTGAN. Implications and recommendations: Before publishing the synthetic data externally, it is recommended that the data are generated using several algorithms, evaluating their final results and finally selecting the best option. This action enables the resulting dataset to be of the highest quality. In further research, it is proposed that other algorithms are tested (e.g. CopulaGAN or TableGAN), in an attempt to deal with some of the realistic data problems that were missed in this analysis, such as missing values (the work was carried out with a complete dataset). Data generated in this study may be used to build financial indicators, which in turn could be used to construct company assessment models. Originality/value: Synthetic data help to deal with some of the data limitations, such as data privacy or scarcity. Due to their statistical similarity with real data, it is possible to use them in advanced machine learning methods instead of real datasets. Analysis on high quality synthetic data allows conclusions similar to analysis on real data to be achieved, while retaining privacy and without publishing sensitive data to third parties.

## 383. A Comparative Study to Predict Bearing Degradation Using Discrete Wavelet Transform (DWT), Tabular Generative Adversarial Networks (TGAN) and Machine Learning Models

- Authors: Keval Bhavsar; Vinay Vakharia; Rakesh Chaudhari; Jay Vora; Danil Yurievich Pimenov; Khaled Giasin
- Year: 2022
- DOI: 10.3390/machines10030176
- Venue: Machines
- Countries: GB; IN; RU
- Source: openalex
- URL: https://doi.org/10.3390/machines10030176
- PDF: https://www.mdpi.com/2075-1702/10/3/176/pdf?version=1646103458

Prognostics and health management (PHM) is a framework to identify damage prior to its occurrence which leads to the reduction of both maintenance costs and safety hazards. Based on the data collected in condition monitoring, the degradation of the part is predicted. Studies show that most failures are caused by faults in rolling element bearing, which highlights that a bearing is one of the most important mechanical components of any machine. Thus, it becomes important to monitor bearing degradation to make sure that it is utilized properly. Generally, machine learning (ML) or deep learning (DL) techniques are utilized to predict bearing degradation using a data-driven approach, where signals are captured from the machine. There should be a large amount of data to apply either ML or DL techniques, but it is difficult to collect that amount of data directly from any machine. In this study, health assessment is carried out using the correlation coefficient to divide the bearing life into two degradation stages. The raw signal is processed using discrete wavelet transform (DWT), where mutual information (MI) is used to rank and select the base wavelet, after which tabular generative adversarial networks (TGAN) are used to generate the artificial coefficients. Statistical features are calculated from the real data (DWT coefficients) and the artificial data (generated from TGAN). The constructed feature vector is then used as an input to train machine learning models, namely ensemble bagged tree (EBT) and Gaussian process regression with the squared exponential kernel function (SEGPR), to estimate bearing degradation conditions. Both the machine learning models were validated on the publicly available experimental data of FEMTO bearing. Obtained results showed that the developed EBT and SEGPR models accurately predicted the bearing degradation conditions with the average lowest RMSE value of 0.0045 and MAE value of 0.0037.

## 384. Modeling Tabular data using Conditional GAN

- Authors: Lei Xu; Maria Skoularidou; Alfredo Cuesta‐Infante; Kalyan Veeramachaneni
- Year: 2019
- DOI: 10.48550/arxiv.1907.00503
- Venue: arXiv (Cornell University)
- Countries: ES; GB; US
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1907.00503
- PDF: https://arxiv.org/pdf/1907.00503

Modeling the probability distribution of rows in tabular data and generating realistic synthetic data is a non-trivial task. Tabular data usually contains a mix of discrete and continuous columns. Continuous columns may have multiple modes whereas discrete columns are sometimes imbalanced making the modeling difficult. Existing statistical and deep neural network models fail to properly model this type of data. We design TGAN, which uses a conditional generative adversarial network to address these challenges. To aid in a fair and thorough comparison, we design a benchmark with 7 simulated and 8 real datasets and several Bayesian network baselines. TGAN outperforms Bayesian methods on most of the real datasets whereas other deep learning methods could not.

## 385. Fs-Tgan: An Enhanced Approach for Internet of Things (Iot) Intrusion Detection System Based on Feature Selection and Tabular Generative Adversarial Network

- Authors: Mohammed Chemmakha; Abdellah Chehri; Omar Habibi; Mohamed Lazaar; Rachid Saadane
- Year: 2023
- DOI: 10.2139/ssrn.4673886
- Venue: SSRN Electronic Journal
- Countries: CA; MA
- Source: openalex
- URL: https://doi.org/10.2139/ssrn.4673886
- PDF: http://dx.doi.org/10.2139/ssrn.4673886

## 386. Fed-TGAN: Federated Learning Framework for Synthesizing Tabular Data

- Authors: Zilong Zhao; Robert Birke; Aditya Kunar; Lydia Y. Chen
- Year: 2021
- DOI: 10.48550/arxiv.2108.07927
- Venue: arXiv (Cornell University)
- Countries: CH; NL
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2108.07927
- PDF: https://arxiv.org/pdf/2108.07927

Generative Adversarial Networks (GANs) are typically trained to synthesize data, from images and more recently tabular data, under the assumption of directly accessible training data. Recently, federated learning (FL) is an emerging paradigm that features decentralized learning on client's local data with a privacy-preserving capability. And, while learning GANs to synthesize images on FL systems has just been demonstrated, it is unknown if GANs for tabular data can be learned from decentralized data sources. Moreover, it remains unclear which distributed architecture suits them best. Different from image GANs, state-of-the-art tabular GANs require prior knowledge on the data distribution of each (discrete and continuous) column to agree on a common encoding -- risking privacy guarantees. In this paper, we propose Fed-TGAN, the first Federated learning framework for Tabular GANs. To effectively learn a complex tabular GAN on non-identical participants, Fed-TGAN designs two novel features: (i) a privacy-preserving multi-source feature encoding for model initialization; and (ii) table similarity aware weighting strategies to aggregate local models for countering data skew. We extensively evaluate the proposed Fed-TGAN against variants of decentralized learning architectures on four widely used datasets. Results show that Fed-TGAN accelerates training time per epoch up to 200% compared to the alternative architectures, for both IID and Non-IID data. Overall, Fed-TGAN not only stabilizes the training loss, but also achieves better similarity between generated and original data. Our code is released at https://github.com/zhao-zilong/Fed-TGAN.

## 387. Effect of Data Augmentation Using Deep Learning on Predictive Models for Geopolymer Compressive Strength

- Authors: Ho Anh Thu Nguyen; Duy Hoang Pham; Yonghan Ahn
- Year: 2024
- DOI: 10.3390/app14093601
- Venue: Applied Sciences
- Countries: KR
- Source: openalex
- URL: https://doi.org/10.3390/app14093601
- PDF: https://www.mdpi.com/2076-3417/14/9/3601/pdf?version=1713966236

In recent years, machine learning models have become a potential approach in accurately predicting the concrete compressive strength, which is essential for the real-world application of geopolymer concrete. However, the precursor system of geopolymer concrete is known to be more heterogeneous compared to Ordinary Portland Cement (OPC) concrete, adversely affecting the data generated and the performance of the models. To its advantage, data enrichment through deep learning can effectively enhance the performance of prediction models. Therefore, this study investigates the capability of tabular generative adversarial networks (TGANs) to generate data on mixtures and compressive strength of geopolymer concrete. It assesses the impact of using synthetic data with various models, including tree-based, support vector machines, and neural networks. For this purpose, 930 instances with 11 variables were collected from the open literature. In particular, 10 variables including content of fly ash, slag, sodium silicate, sodium hydroxide, superplasticizer, fine aggregate, coarse aggregate, added water, curing temperature, and specimen age are considered as inputs, while compressive strength is the output of the models. A TGAN was employed to generate an additional 1000 data points based on the original dataset for training new predictive models. These models were evaluated on real data test sets and compared with models trained on the original data. The results indicate that the developed models significantly improve performance, particularly neural networks, followed by tree-based models and support vector machines. Moreover, data characteristics greatly influence model performance, both before and after data augmentation.

## 388. Generation of synthetic full-scale burst test data for corroded pipelines using the tabular generative adversarial network

- Authors: Z. T. He; Wenxing Zhou
- Year: 2022
- DOI: 10.1016/j.engappai.2022.105308
- Venue: Engineering Applications of Artificial Intelligence
- Countries: CA
- Source: openalex
- URL: https://doi.org/10.1016/j.engappai.2022.105308

## 389. Explainable Data-Driven Ensemble Learning Models for the Mechanical Properties Prediction of Concrete Confined by Aramid Fiber-Reinforced Polymer Wraps Using Generative Adversarial Networks

- Authors: Celal Çakıroğlu
- Year: 2023
- DOI: 10.3390/app132111991
- Venue: Applied Sciences
- Countries: TR
- Source: openalex
- URL: https://doi.org/10.3390/app132111991
- PDF: https://www.mdpi.com/2076-3417/13/21/11991/pdf?version=1698940925

The current study offers a data-driven methodology to predict the ultimate strain and compressive strength of concrete reinforced by aramid FRP wraps. An experimental database was collected from the literature, on which seven different machine learning (ML) models were trained. The diameter and length of the cylindrical specimens, the compressive strength of unconfined concrete, the thickness, elasticity modulus and ultimate tensile strength of the FRP wrap were used as the input features of the machine learning models, to predict the ultimate strength and strain of the specimens. The experimental dataset was further enhanced with synthetic data using the tabular generative adversarial network (TGAN) approach. The machine learning models’ performances were compared to the predictions of the existing strain capacity and compressive strength prediction equations for aramid FRP-confined concrete. The accuracy of the predictive models was measured using state-of-the-art statistical metrics such as the coefficient of determination, mean absolute error and root mean squared error. On average, the machine learning models were found to perform better than the available equations in the literature. In particular, the extra trees regressor, XGBoost and K-nearest neighbors algorithms performed significantly better than the remaining algorithms, with R2 scores greater than 0.98. Furthermore, the SHapley Additive exPlanations (SHAP) method and individual conditional expectation (ICE) plots were used to visualize the effects of various input parameters on the predicted ultimate strain and strength values. The unconfined compressive strength of concrete and the ultimate tensile strength of the FRP wrap were found to have the greatest impact on the machine learning model outputs.

## 390. A Generative Adversarial Network Approach to Predict Nanoparticle Size in Microfluidics

- Authors: Sara Mihandoost; Sima Rezvantalab; Roger M. Pallares; Volkmar Schulz; Fabian Kießling
- Year: 2024
- DOI: 10.1021/acsbiomaterials.4c01423
- Venue: ACS Biomaterials Science & Engineering
- Countries: DE; IR
- Source: openalex
- URL: https://doi.org/10.1021/acsbiomaterials.4c01423

To achieve precise control over the properties and performance of nanoparticles (NPs) in a microfluidic setting, a profound understanding of the influential parameters governing the NP size is crucial. This study specifically delves into poly(lactic-co-glycolic acid) (PLGA)-based NPs synthesized through microfluidics that have been extensively explored as drug delivery systems (DDS). A comprehensive database, containing more than 11 hundred data points, is curated through an extensive literature review, identifying potential effective features. Initially, we employed a tabular generative adversarial network (TGAN) to enhance data sets, increasing the reliability of the obtained results and elevating prediction accuracy. Subsequently, NP size prediction was performed using different machine learning (ML) techniques including decision tree (DT), random forest (RF), deep neural networks (DNN), linear regression (LR), support vector regression (SVR), and gradient boosting (GB). Among these ensembles, DT emerges as the most accurate algorithm, yielding an average prediction error of 8%. Further simulations underscore the pivotal role of the synthesis method, poly(vinyl alcohol) (PVA) concentration, and lactide-to-glycolide (LA/GA) ratio of PLGA copolymers as the primary determinants influencing NP size.

## 391. Development of machine learning-based burst capacity models for pipelines containing dent-gouges with synthetic full-scale burst test data generated using tabular generative adversarial network

- Authors: Ze He; Wenxing Zhou
- Year: 2024
- DOI: 10.1016/j.engappai.2024.108090
- Venue: Engineering Applications of Artificial Intelligence
- Countries: CA
- Source: openalex
- URL: https://doi.org/10.1016/j.engappai.2024.108090
- PDF: https://doi.org/10.1016/j.engappai.2024.108090

This study develops accurate burst capacity models for steel oil and gas pipelines containing dent-gouge damages through the innovative use of a deep learning algorithm, the tabular generative adversarial network (TGAN), and three machine learning (ML) algorithms, the random forest, extra tree and Gaussian process regression. TGAN is employed to expand a limited number (88) of full-scale burst tests of dent-gouged pipe specimens available in the literature by generating synthetic test data. A dataset consisting of 62 real and 438 synthetic test data is then employed to train the three ML models to predict the dent-gouge burst capacity. Based on a validation dataset of 26 real test data, the accuracy of the ML models is shown to be markedly higher than that of a well-known semi-empirical engineering model: coefficients of variation of the test-to-predicted ratios for the ML models are below 15% compared with about 45% for the engineering model. Uncertainty quantification of predictions by the ML models is also carried out. The present study demonstrates the promising potential and effectiveness of combining deep learning algorithms and ML models to improve the integrity assessment practice for oil and gas pipelines.

## 392. Row Conditional-TGAN for Generating Synthetic Relational Databases

- Authors: Mohamed Gueye; Yazid Attabi; Maxime Dumas
- Year: 2023
- DOI: 10.1109/icassp49357.2023.10096001
- Venue: 
- Countries: 
- Source: openalex
- URL: https://doi.org/10.1109/icassp49357.2023.10096001

Besides reproducing tabular data properties of standalone tables, synthetic relational databases also require modeling the relationships between related tables. In this paper, we propose the Row Conditional–Tabular Generative Adversarial Network (RC-TGAN), a novel generative adversarial network (GAN) model that extends the tabular GAN to support modeling and synthesizing relational databases. The RC-TGAN models relationship information between tables by incorporating conditional data of parent rows into the design of the child table’s GAN. We further extend the RC-TGAN to model the influence that grandparent table rows may have on their grandchild rows, in order to prevent the loss of this connection when the rows of the parent table fail to transfer this relationship information. The experimental results, using eight real relational databases, show significant improvements in the quality of the synthesized relational databases when compared to the benchmark system, demonstrating the effectiveness of the RC-TGAN in preserving relationships between tables of the original database.

## 393. Prediction and reliability analysis of ultimate axial strength for outer circular CFRP-strengthened CFST columns with CTGAN and hybrid MFO-ET model

- Authors: Viet‐Linh Tran; Jaehong Lee; Jin-Kook Kim
- Year: 2024
- DOI: 10.1016/j.eswa.2024.125704
- Venue: Expert Systems with Applications
- Countries: KR; VN
- Source: openalex
- URL: https://doi.org/10.1016/j.eswa.2024.125704

## 394. Predicting Ultra-High-Performance Concrete Compressive Strength Using Tabular Generative Adversarial Networks

- Authors: Afshin Marani; Armin Jamali; Moncef L. Nehdi
- Year: 2020
- DOI: 10.3390/ma13214757
- Venue: Materials
- Countries: CA; IR
- Source: openalex
- URL: https://doi.org/10.3390/ma13214757
- PDF: https://www.mdpi.com/1996-1944/13/21/4757/pdf?version=1603536486

There have been abundant experimental studies exploring ultra-high-performance concrete (UHPC) in recent years. However, the relationships between the engineering properties of UHPC and its mixture composition are highly nonlinear and difficult to delineate using traditional statistical methods. There is a need for robust and advanced methods that can streamline the diverse pertinent experimental data available to create predictive tools with superior accuracy and provide insight into its nonlinear materials science aspects. Machine learning is a powerful tool that can unravel underlying patterns in complex data. Accordingly, this study endeavors to employ state-of-the-art machine learning techniques to predict the compressive strength of UHPC using a comprehensive experimental database retrieved from the open literature consisting of 810 test observations and 15 input features. A novel approach based on tabular generative adversarial networks was used to generate 6513 plausible synthetic data for training robust machine learning models, including random forest, extra trees, and gradient boosting regression. While the models were trained using the synthetic data, their ability to generalize their predictions was tested on the 810 experimental data thus far unknown and never presented to the models. The results indicate that the developed models achieved outstanding predictive performance. Parametric studies using the models were able to provide insight into the strength development mechanisms of UHPC and the significance of the various influential parameters.

## 395. Causal-TGAN: Causally-Aware Synthetic Tabular Data Generative Adversarial Network

- Authors: Bingyang Wen; Yupeng Cao; Fan Yang; K. P. Subbalakshmi; R. Chandramouli
- Year: 2021
- DOI: 
- Venue: 
- Countries: 
- Source: openalex
- URL: https://openalex.org/W3214016257

## 396. Optimizing Stone Mastic Asphalt mix design with TGAN-enhanced surrogate models

- Authors: Mahdi Zakerzadeh; Mohsen Mousavi; Babak Shahbodagh; James Jeremy Kien Chung Ng; Nasser Khalili
- Year: 2024
- DOI: 10.1016/j.conbuildmat.2024.138863
- Venue: Construction and Building Materials
- Countries: AU
- Source: openalex
- URL: https://doi.org/10.1016/j.conbuildmat.2024.138863
- PDF: https://doi.org/10.1016/j.conbuildmat.2024.138863

The design procedure for asphalt mixes is still largely empirical, often requiring lengthy and resource-intensive trials in the laboratory. To streamline and accelerate the mix design process, this study investigates the use of a surrogate-assisted model to predict the volumetric characteristics of asphalt mixtures and automate the design process. Optimizing mixture design is essential for ensuring that the asphalt mixtures meet the required volumetric properties, involving complex decisions on the proportions of aggregates and binder content to satisfy multiple objectives. The mix design of Stone Mastic Asphalt (SMA) is often challenged by the intricate balance required to satisfy these multiple objectives simultaneously. Traditional optimization techniques struggle to cope with these challenges, especially under conditions of incomplete or scarce data, which is common in practice. In this paper, tabular generative adversarial networks (TGAN) have been specifically developed to address such problems. The paper further demonstrates the application of the developed framework in optimizing SMA mixture design, which proves to be a challenging problem in the realm of pavement engineering. Models trained on aggregated data – including those augmented with TGAN-generated samples – showed approximately a 50% improvement in R 2 values for maximum density and a 30%–40% improvement for bulk density at 120 and 350 cycles, respectively, compared to the non-TGAN models. Moreover, the results of experimental volumetric tests confirm that the TGAN-based models perform superior to the non-TGAN models. As such, the absolute error percentages of the candidate solutions obtained from the model trained on the TGAN-generated data were consistently below 10%, whereas the non-TGAN models exhibited higher variations, with errors exceeding 15%. The results of this study were further verified through experimental validation, as well as by analyzing parameters extracted from the Rosin-Rammler distribution function and the Bailey method. The qualitative and quantitative results demonstrate the effectiveness of the proposed framework in solving the optimization problem for Stone Mastic Asphalt mixture design. • A timesaving asphalt mix design using a Surrogate-Assisted model is proposed. • A Black Box Optimization (BBO) approach is proposed for optimizing SMA mix design. • It is demonstrated that the proposed TGAN can generate high-quality synthetic data. • It is shown that feature importance analyses reveal key design variables for SMA.

## 397. Enhancing Synthetic Data Generation for Class Imbalance and Privacy Preservation

- Authors: Weijie Niu; Alberto Huertas; Jingjing Li; Burkhard Stiller
- Year: 2024
- DOI: 10.1109/bigdata62323.2024.10825316
- Venue: 
- Countries: CH
- Source: openalex
- URL: https://doi.org/10.1109/bigdata62323.2024.10825316

Synthetic data generation has emerged as a powerful solution to meet the demand for high-quality, diverse, and privacy-preserving data in many domains. Still, there is an open challenge when dealing with class imbalance and privacy preservation in synthetic tabular data generation. Thus, this study introduces two algorithms: balanced Tabular Generative Adversarial Network (b-TGAN) and balanced Tabular Principle Component Analysis (b-TPCA). While b-TGAN proactively tackles class imbalance by incorporating a re-balancing mechanism and leveraging an Autoencoder, b-TPCA offers a privacy-preserving solution by generating synthetic data using statistical properties. Through experiments on five datasets, this study demonstrates the effectiveness of b-TGAN in generating balanced data, particularly in improving the performance on minority classes. b-TPCA also shows promising results, achieving comparable ML utility to the baseline method while enhancing privacy preservation.

## 398. Identification of Generative Adversarial Network Models Suitable for Software Defect Prediction

- Authors: Jiwon Choi; Jaewook Lee; Duksan Ryu; Suntae Kim
- Year: 2022
- DOI: 10.5626/jok.2022.49.1.52
- Venue: Journal of KIISE
- Countries: 
- Source: openalex
- URL: https://doi.org/10.5626/jok.2022.49.1.52

소프트웨어 결함 예측은 결함이 야기될 모듈을 식별해 한정된 품질 보증 자원을 효과적으로 배분하는데 도움을 준다. 소프트웨어 결함 데이터는 비결함 인스턴스의 수가 결함 인스턴스의 수보다 많은 클래스 불균형 문제를 겪는다. 대부분의 기계 학습에서 특정 클래스의 인스턴스 비율이 한쪽으로 치우치게 되면 결함 예측 성능에 부정적인 영향을 끼친다. 따라서 본 연구에서는 생성적 적대 신경망 모델(Generative Adversarial Network, GAN)을 사용해 클래스 불균형 문제를 해결하고, 결함 예측 성능 향상을 목표로 한다. 이를 위해, 본 연구에서는 여러 종류의 GAN 모델 중 소프트웨어 결함 예측에 적합한 모델은 무엇인지 비교하고, 관련 연구에서 적용하지 않았던 GAN 모델들의 적용성 여부를 확인한다. 본 연구에서는 이미지 생성에 최적화되어 있는 Vanilla-GAN(GAN)과 Conditional GAN(cGAN), Wasserstein GAN(WGAN) 모델을 소프트웨어 결함 예측 데이터에 적합하게 개조한 후, 개조한 GAN과 cGAN, WGAN, Tabular GAN(TGAN), Modeling Tabular data using Conditional GAN(CTGAN)의 성능을 비교 실험한다. 실험 결과, CTGAN 모델이 소프트웨어 결함 예측 데이터에 적합함을 보인다. 또한 CTGAN의 하이퍼파라미터 중 결함 발견율(Recall)을 높이고, 결함 오보율(Probability of False Alarm, PF)를 낮추는 하이퍼파라미터 값은 무엇인지 민감도 분석을 수행한다. 실험 결과, 데이터셋에 따라 하이퍼파라미터를 조정해야 함을 보였다. 우리의 제안한 기법이 소프트웨어 결함 예측의 성능을 향상시켜 한정된 자원을 효과적으로 할당하는데 도움이 될 것이라고 기대한다.

## 399. Generative Adversarial Neural Network and Genetic Algorithm To Predict Oil and Gas Pipeline Defect Length

- Authors: Huda Aldosari; Sanguthevar Rajasekaran; Reda A. Ammar
- Year: 2021
- DOI: 10.29007/w663
- Venue: EPiC series in computing
- Countries: US
- Source: openalex
- URL: https://doi.org/10.29007/w663

Estimation of expected failure in an oil and gas pipeline system is challenging due to large uncertainties in the parameters associated with burst failure predictive models. The development of machine learning (ML) algorithms for reliability and risk assessment applications has attracted considerable attention from the scientific and research community in recent years. Working on the automation, efficiency, and optimization of underground oil and gas pipeline networks demands open access to extensive databases, which may not be possible. Oil and gas databases are confidential assets of specific countries, and no one can access these databases easily. As a result, training ML models is a big challenge, since it needs large data. To address this data shortage, in this paper, we have generated synthetic training datasets using a tabular generative adversarial neural network (TGAN). The generated synthetic data and real data (when available) were combined to train an artificial neural network (ANN). To further enhance the performance of the proposed system, the application of a genetic algorithm (GA) has been introduced to optimize the weights and biases of the ANN automatically. The results show superior performance results when compared with the previously reported algorithms in the literature. The proposed methodology succeeds to predict Oil and Gas pipeline defects with robust results and low error rates.

## 400. A generative adversarial network enhanced ensemble learning-based prediction model for moment improvement effect of UHPC strengthened damaged RC beams

- Authors: Woubishet Zewdu Taffese; Nima Khodadadi; Yanping Zhu; Seyedali Mirjalili; Antonio Nanni
- Year: 2025
- DOI: 10.1016/j.cscm.2025.e05323
- Venue: Case Studies in Construction Materials
- Countries: AU; CZ; HU; US
- Source: openalex
- URL: https://doi.org/10.1016/j.cscm.2025.e05323
- PDF: https://doi.org/10.1016/j.cscm.2025.e05323

Reinforced Concrete (RC) structures are often compromised by cracks and corrosion, necessitating effective retrofitting strategies to restore their structural integrity. Ultra-High-Performance Concrete (UHPC) has emerged as a promising material for strengthening damaged RC beams, significantly enhancing their load-bearing capacity and durability. However, accurately predicting the flexural performance of UHPC-strengthened RC beams remains a challenge due to complex material interactions and limited datasets. This addresses this gap by developing a data-driven framework that combines generative data augmentation and explainable machine learning to predict the ultimate moment resistance ( M u ) of strengthened beams. A curated dataset of 160 experimental cases was expanded using a Tabular Generative Adversarial Network (TGAN), and six ensemble learning models were trained and evaluated. Among them, Categorical Boosting (CatBoost) demonstrated superior performance with an R² of 0.90 on the test set. SHapley Additive exPlanations (SHAP) were employed to explain model predictions, revealing that the UHPC reinforcement ratio, longitudinal reinforcement ratio of beam, beam width, and concrete compressive strength are the most influential factors. The proposed approach not only improves prediction accuracy and model robustness but also provides interpretable insights to support rational design decisions in structural retrofitting. • First use of GANs to predict moment improvement in UHPC-strengthened damaged RC beams. • CatBoost achieved high accuracy on both the training set ( R 2 =0.99) and test set ( R 2 =0.90). • The Shapely-based model explanations reveal features importance and sensitivity for engineering design.

## 401. Synthesis of Tabular Financial Data using Generative Adversarial Networks

- Authors: Anton Karlsson; Torbjörn Sjöberg
- Year: 2020
- DOI: 
- Venue: KTH Publication Database DiVA (KTH Royal Institute of Technology)
- Countries: 
- Source: openalex
- URL: https://openalex.org/W3094090798
- PDF: http://urn.kb.se/resolve?urn=urn:nbn:se:kth:diva-273633

Digitalization has led to tons of available customer data and possibilities for data-driven innovation. However, the data needs to be handled carefully to protect the privacy of the customers. Generative Adversarial Networks (GANs) are a promising recent development in generative modeling. They can be used to create synthetic data which facilitate analysis while ensuring that customer privacy is maintained. Prior research on GANs has shown impressive results on image data. In this thesis, we investigate the viability of using GANs within the financial industry. We investigate two state-of-the-art GAN models for synthesizing tabular data, TGAN and CTGAN, along with a simpler GAN model that we call WGAN. A comprehensive evaluation framework is developed to facilitate comparison of the synthetic datasets. The results indicate that GANs are able to generate quality synthetic datasets that preserve the statistical properties of the underlying data and enable a viable and reproducible subsequent analysis. It was however found that all of the investigated models had problems with reproducing numerical data.

## 402. Predictive models for the axial capacity of NSM- and hybrid FRP-strengthened RC columns using ensemble learning optimized by metaheuristic algorithms

- Authors: Solmaz Afzali; Seyed Ali Eftekhar Afzali; Mohsen Ali Shayanfar; Mohammad Ghanooni-Bagha; Mostafa Afzali
- Year: 2025
- DOI: 10.1016/j.cscm.2025.e05167
- Venue: Case Studies in Construction Materials
- Countries: IR
- Source: openalex
- URL: https://doi.org/10.1016/j.cscm.2025.e05167
- PDF: https://doi.org/10.1016/j.cscm.2025.e05167

The strengthening of reinforced concrete (RC) columns with fiber-reinforced polymers (FRP) has gained attention, particularly with near surface mounted (NSM) FRP bars and FRP jacketing. However, uncertainties in design codes, such as the effectiveness of fibers under compression and the complexity of bonding behavior, necessitate machine learning-based predictive models. This study develops a machine learning framework to predict the axial capacity of RC columns strengthened using NSM and hybrid techniques. A dataset comprising 112 experimental samples, and 112 synthetic samples generated using tabular generative adversarial networks (TGAN) was utilized. The hyperparameters of gradient boosting regressor (GBR) and random forest regressor (RFR) models were optimized via Bayesian optimization and metaheuristic algorithms, including arithmetic optimization algorithm (AOA), artificial hummingbird blgorithm (AHA), and slime mould algorithm (SMA). Comparing models trained exclusively on empirical data with those trained on the combined real–synthetic dataset demonstrated that TGAN-based augmentation significantly improves performance and reduces model variability. The proposed model outperforms existing code‐based approaches on all metrics, providing more accurate and reliable axial‐capacity predictions for NSM- and hybrid FRP-strengthened RC columns. SHapley Additive exPlanations (SHAP) analysis revealed that jacketing and NSM parameters positively affect capacity, while load eccentricity reduces it. Concrete compressive strength negatively affected strengthening efficiency, particularly beyond 38 MPa. Among optimization methods, AHA-GBR showed the best performance, followed by AOA-GBR and SMA-GBR. While Bayesian optimization was faster, it exhibited higher performance variance. The best-selected model outperformed traditional Bayesian methods, reducing RMSE on the test dataset by over 20%.

## 403. A Tabular Conditional Generative Adversarial Imputation Network for Vertical Federated Learning

- Authors: Liu Xin; Chen Hongyu; Hangxuan He; Feng Chen; Ying Qian
- Year: 2024
- DOI: 10.2139/ssrn.4775836
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.2139/ssrn.4775836

## 404. Time-series Anonymization of Tabular Health Data using Generative Adversarial Network

- Authors: Atiye Sadat Hashemi; Kobra Etminani; Amira Soliman; Omar Hamed; Jens Lundström
- Year: 2023
- DOI: 10.1109/ijcnn54540.2023.10191367
- Venue: 2023 International Joint Conference on Neural Networks (IJCNN)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/ijcnn54540.2023.10191367

## 405. Application of Generative Adversarial Network Tabular Data Synthesis for Federal Learning-based Thermal Process Performance Prediction

- Authors: Lewei Xu; Yong Liu
- Year: 2022
- DOI: 10.1109/iccc56324.2022.10065986
- Venue: 2022 IEEE 8th International Conference on Computer and Communications (ICCC)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/iccc56324.2022.10065986

## 406. Synthetic Model Generation from Metamodel Using Conditional Tabular Generative Adversarial Network

- Authors: El Abbassia Deba; Abdelouadoud Sadeuk Ben Abbas; Karima Berramla
- Year: 2024
- DOI: 10.1109/edis63605.2024.10783213
- Venue: 2024 4th International Conference on Embedded &amp;amp; Distributed Systems (EDiS)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/edis63605.2024.10783213

## 407. Enhanced Intrusion Detection Using Conditional-Tabular-Generative-Adversarial-Network-Augmented Data and a Convolutional Neural Network: A Robust Approach to Addressing Imbalanced Cybersecurity Datasets

- Authors: Shridhar Allagi; Toralkar Pawan; Wai Yie Leong
- Year: 2025
- DOI: 10.3390/math13121923
- Venue: Mathematics
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3390/math13121923

<jats:p>Intrusion prevention and classification are common in the research field of cyber security. Models built from training data may fail to prevent or classify intrusions accurately if the dataset is imbalanced. Most researchers employ SMOTE to balance the dataset. SMOTE in turn fails to address the constraints associated with the dataset, such as diverse data types, preserving the data distribution, capturing non-linear relationships, and preserving oversampling noise. The novelty of this work is in addressing the issues associated with data distribution and SMOTE by employing Conditional Tabular Generative Adversarial Networks (CTGANs) on NSL_KDD and UNSW_NB15 datasets. The balanced input corpus is fed into the CNN model to predict the intrusion. The CNN model involves two convolution layers, max-pooling, ReLU as the activation layer, and a dense layer. The proposed work employs measures such as accuracy, recall, precision, specificity and F1-score for measuring the model performance. The study shows that CTGAN improves the intrusion detection rate. This research highlights the high-quality synthetic samples generated by CTGAN that significantly enhance CNN-based intrusion detection performance on imbalance datasets. This demonstrates the potential for deploying GAN-based oversampling techniques in real-world cybersecurity systems to improve detection accuracy and reduce false negatives.</jats:p>

## 408. Power Transformer DGA Data Augmentation Using Conditional Tabular Generative Adversarial Network

- Authors: Nkiru L. Agu; Syed M. Haider; Gobind G. Pillai; Imran Bashir; Gill Lacey
- Year: 2024
- DOI: 10.1109/upec61344.2024.10892386
- Venue: 2024 59th International Universities Power Engineering Conference (UPEC)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/upec61344.2024.10892386

## 409. SID-TGAN: A Transformer-Based Generative Adversarial Network for Sonar Image Despeckling

- Authors: Xin Zhou; Kun Tian; Zihan Zhou; Bo Ning; Yanhao Wang
- Year: 2023
- DOI: 10.3390/rs15205072
- Venue: Remote Sensing
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3390/rs15205072

<jats:p>Sonar images are inherently affected by speckle noise, which degrades image quality and hinders image exploitation. Despeckling is an important pre-processing task that aims to remove such noise so as to improve the accuracy of analysis tasks on sonar images. In this paper, we propose a novel transformer-based generative adversarial network named SID-TGAN for sonar image despeckling. In the SID-TGAN framework, transformer and convolutional blocks are used to extract global and local features, which are further integrated into the generator and discriminator networks for feature fusion and enhancement. By leveraging adversarial training, SID-TGAN learns more comprehensive representations of sonar images and shows outstanding performance in speckle denoising. Meanwhile, SID-TGAN introduces a new adversarial loss function that combines image content, local texture style, and global similarity to reduce image distortion and information loss during training. Finally, we compare SID-TGAN with state-of-the-art despeckling methods on one image dataset with synthetic optical noise and four real sonar image datasets. The results show that it achieves significantly better despeckling performance than existing methods on all five datasets.</jats:p>

## 410. A Novel Hybrid Architecture of Conditional Tabular Generative Adversarial Network and 1D Convolution Neural Network for Enhanced Attack Detection in IoT Systems

- Authors: Mohammed Chemmakha; Omar Habibi; Mohamed Lazaar
- Year: 2023
- DOI: 10.1109/icvee59738.2023.10348290
- Venue: 2023 Sixth International Conference on Vocational Education and Electrical Engineering (ICVEE)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/icvee59738.2023.10348290

## 411. A GENERATIVE ADVERSARIAL NETWORK APPROACH TO SYNTHETIC TABULAR DATA GENERATION: ARCHITECTURES, MATHEMATICAL FOUNDATIONS, AND EVALUATION PRACTICES

- Authors: Mukund Kumar Singh; Prof. Dr. Mrs. Shivani A. Budhkar
- Year: 2026
- DOI: 10.36713/epra27893
- Venue: EPRA International Journal of Research &amp; Development (IJRD)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.36713/epra27893

<jats:p>Defence organisations collect operational, medical, cyber, logistics, and maintenance records that are valuable for model development but difficult to share because they may contain sensitive or mission-revealing information. Synthetic tabular data offers a practical way to support experimentation, benchmarking, and training while reducing direct exposure of original records. This paper presents an original review of Generative Adversarial Network (GAN)-based approaches for tabular data synthesis, with emphasis on the requirements of defenceoriented workflows. It explains the adversarial objective, the Wasserstein formulation with gradient penalty, and preprocessing methods that allow neural generators to handle numerical and categorical fields. The paper also discusses evaluation through fidelity, downstream utility, robustness, fairness, and privacy testing. Rather than treating synthetic data as automatically safe, the analysis argues for a documented validation pipeline that measures both model performance and disclosure risk before synthetic records are released or used in operational decision support.
Keywords: Generative Adversarial Networks, Synthetic Data, Tabular Data, Defence Analytics, Privacy, WGAN-GP</jats:p>

## 412. Generative Adversarial Network-based Image and Tabular Data Generation with Differential Privacy

- Authors: Jiming Yang; Xu Wang; Yi Jin; Yidong Li; Hui Yu
- Year: 2025
- DOI: 10.1109/icme59968.2025.11209493
- Venue: 2025 IEEE International Conference on Multimedia and Expo (ICME)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/icme59968.2025.11209493

## 413. PIM-TGAN: A Processing-in-Memory Accelerator for Ternary Generative Adversarial Networks

- Authors: Adnan Siraj Rakin; Shaahin Angizi; Zhezhi He; Deliang Fan
- Year: 2018
- DOI: 10.1109/iccd.2018.00048
- Venue: 2018 IEEE 36th International Conference on Computer Design (ICCD)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/iccd.2018.00048

## 414. SR - TGAN: Smoke Removal with Temporal Generative Adversarial Models in Robot-assisted Surgery

- Authors: Mengya Xu; Omer Raza; An Wang; Hongliang Ren
- Year: 2024
- DOI: 10.1109/bhi62660.2024.10913669
- Venue: 2024 IEEE EMBS International Conference on Biomedical and Health Informatics (BHI)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/bhi62660.2024.10913669

## 415. Toward a New Approach Based on Conditional Tabular Generative Adversarial Network for Ransomware Attack Detection in IoT Systems

- Authors: Zhor Ismaili; Omar Habibi; Mohammed Chemmakha; Mohamed Lazaar
- Year: 2025
- DOI: 10.1109/sita67914.2025.11273687
- Venue: 2025 International Conference on Intelligent Systems: Theories and Applications (SITA)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/sita67914.2025.11273687

## 416. Gaussian Mixture Conditional Tabular Generative Adversarial Network for Data Imbalance Problem

- Authors: Yongwei Ke; Jiali Cheng; Zhiqiang Cai
- Year: 2023
- DOI: 10.1109/srse59585.2023.10336134
- Venue: 2023 5th International Conference on System Reliability and Safety Engineering (SRSE)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/srse59585.2023.10336134

## 417. Optimization of Warpage Parameter Design and Feedback Suggestions in Semiconductor Packaging Products with Genetic Algorithms Artificial Neural Networks and Conditional Tabular Generative Adversarial Network

- Authors: Hung-Kai Wang; Yan-Cheng Lin; Tang-Yuan Chen; Chen-Chao Wang; Chin-Pin Hung
- Year: 2025
- DOI: 10.2139/ssrn.5222008
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.2139/ssrn.5222008

## 418. A data augmentation method for multiaxial fatigue life prediction based on physics-informed tabular generative adversarial network

- Authors: Gaoyuan He; Yongxiang Zhao; Chuliang Yan
- Year: 2024
- DOI: 10.1088/1742-6596/2816/1/012048
- Venue: Journal of Physics: Conference Series
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1088/1742-6596/2816/1/012048
- PDF: https://iopscience.iop.org/article/10.1088/1742-6596/2816/1/012048/pdf

<jats:title>Abstract</jats:title>
               <jats:p>Currently, in the multiaxial fatigue life prediction problem, machine learning (ML) algorithms are still limited by small samples. For ML tasks requiring large amounts of data, this paper proposes a Conditional Tabular Generative Adversarial Network (CTGAN) model using a physical equation as a generation constraint. The proposed method can make synthetic samples satisfy specific physical knowledge. The method is evaluated using two datasets of different materials. ML-based algorithms verify the feasibility of using synthetic datasets for life prediction. Verification analysis shows that the proposed method successfully synthesizes high-quality multiaxial fatigue datasets and effectively improves the prediction accuracy of ML algorithms.</jats:p>

## 419. HS-CGK: A Hybrid Sampling Method for Imbalance Data Based on Conditional Tabular Generative Adversarial Network and K-Nearest Neighbor Algorithm

- Authors: Xiaoyan Zhao; Shaopeng Guan; Yuewei Xue; Hao Pan
- Year: 2024
- DOI: 10.31577/cai_2024_1_213
- Venue: Computing and Informatics
- Countries: 
- Source: crossref
- URL: https://doi.org/10.31577/cai_2024_1_213

## 420. Optimized customer churn prediction using tabular generative adversarial network (GAN)-based hybrid sampling method and cost-sensitive learning

- Authors: I Nyoman Mahayasa Adiputra; Paweena Wanchai; Pei-Chun Lin
- Year: 2025
- DOI: 10.7717/peerj-cs.2949
- Venue: PeerJ Computer Science
- Countries: 
- Source: crossref
- URL: https://doi.org/10.7717/peerj-cs.2949
- PDF: https://peerj.com/articles/cs-2949.pdf

<jats:sec>
<jats:title>Background</jats:title>
<jats:p>Imbalanced and overlapped data in customer churn prediction significantly impact classification results. Various sampling and hybrid sampling methods have demonstrated effectiveness in addressing these issues. However, these methods have not performed well with classical machine learning algorithms.</jats:p>
</jats:sec>
<jats:sec>
<jats:title>Methods</jats:title>
<jats:p>To optimize the performance of classical machine learning on customer churn prediction tasks, this study introduces an extension framework called CostLearnGAN, a tabular generative adversarial network (GAN)-hybrid sampling method, and cost-sensitive Learning. Utilizing a cost-sensitive learning perspective, this research aims to enhance the performance of several classical machine learning algorithms in customer churn prediction tasks. Based on the experimental results classical machine learning algorithms exhibit shorter execution times, making them suitable for predicting churn in large customer bases.</jats:p>
</jats:sec>
<jats:sec>
<jats:title>Results</jats:title>
<jats:p>This study conducted an experiment with six comparative sampling methods, six datasets, and three machine learning algorithms. The results show that CostLearnGAN achieved a satisfying result across all evaluation metrics with a 1.44 average mean rank score. Additionally, this study provided a robustness measurement for algorithms, demonstrating that CostLearnGAN outperforms other sampling methods in improving the performance of classical machine learning models with a 5.68 robustness value on average.</jats:p>
</jats:sec>

## 421. Toward a New Approach for Internet of Things (IoT) Intrusion Detection Based on Feature Selection and Tabular Generative Adversarial Network

- Authors: Mohammed Chemmakha; Omar Habibi; Mohamed Lazaar
- Year: 2025
- DOI: 10.1177/17248035251361258
- Venue: Intelligenza Artificiale
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1177/17248035251361258
- PDF: https://journals.sagepub.com/doi/pdf/10.1177/17248035251361258

<jats:p>The improvement of IoT security solutions is nowadays more current and urgent because of the large masses of vulnerabilities, cyber attacks, data theft, and other threats related to the use of IoT devices. Most IoT datasets are imbalanced, as benign traffic dominates while malicious traffic is scarce. Additionally, IoT traffic is sensitive and rarely available for public research. Generating realistic synthetic data is essential for overcoming these limitations. Our study focuses on Deep Learning models for network intrusion detection by implementing Tabular Generative Adversarial Networks (TGAN) to address class imbalance. GANs help by increasing the proportion of rare malware samples, improving model training and detection accuracy. In this paper, we rely on the UNSW-NB15 and NSL-KDD datasets to address the issue of imbalanced classes. We propose a new approach that we called FS-TGAN, which is based on feature selection methods and TGAN model for samples generating. The time is a crucial parameter for security tools such as IDS and antivirus, where a lot of data must be analyzed to look for malware, anomalies, or anything suspicious that might be trying to penetrate the system. For this purpose, we reduced the number of features to eliminate redundant features or those that are highly correlated. The results show that TGAN performs well. We achieved 99.03% of accuracy with the UNSW-NB15 dataset, demonstrating a significantly reduced error rate by learning to provide new unseen data that share the training set’s statistics, with a detection time of 0.230 ms per traffic set.</jats:p>

## 422. An early malware threat detection model using Conditional Tabular Generative Adversarial Network

- Authors: V Amrith; Darshan S; Suriya K S; Sulakshan Vajipayajula; Kartik Srinivasan; Senthil Kumar Thangavel; T. Gireesh Kumar
- Year: 2023
- DOI: 10.1109/icccnt56998.2023.10307903
- Venue: 2023 14th International Conference on Computing Communication and Networking Technologies (ICCCNT)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/icccnt56998.2023.10307903

## 423. Generating Multi-label Discrete Patient Records using Generative Adversarial Networks

- Authors: Edward Choi; Siddharth Biswal; Bradley Malin; Jon Duke; Walter F. Stewart; Jimeng Sun
- Year: 2017
- DOI: 10.48550/arxiv.1703.06490
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1703.06490
- PDF: https://arxiv.org/pdf/1703.06490

Access to electronic health record (EHR) data has motivated computational advances in medical research. However, various concerns, particularly over privacy, can limit access to and collaborative use of EHR data. Sharing synthetic EHR data could mitigate risk. In this paper, we propose a new approach, medical Generative Adversarial Network (medGAN), to generate realistic synthetic patient records. Based on input real patient records, medGAN can generate high-dimensional discrete variables (e.g., binary and count features) via a combination of an autoencoder and generative adversarial networks. We also propose minibatch averaging to efficiently avoid mode collapse, and increase the learning efficiency with batch normalization and shortcut connections. To demonstrate feasibility, we showed that medGAN generates synthetic patient records that achieve comparable performance to real data on many experiments including distribution statistics, predictive modeling tasks and a medical expert review. We also empirically observe a limited privacy risk in both identity and attribute disclosure using medGAN.

## 424. Generating Multi-label Discrete Patient Records using Generative Adversarial Networks

- Authors: Edward Choi; Siddharth Biswal; Bradley Malin; Jon Duke; Walter F. Stewart; Jimeng Sun
- Year: 2017
- DOI: 
- Venue: Machine Learning for Healthcare Conference
- Countries: 
- Source: openalex
- URL: https://openalex.org/W2963671176

Access to electronic health record (EHR) data has motivated computational advances in medical research. However, various concerns, particularly over privacy, can limit access to and collaborative use of EHR data. Sharing synthetic EHR data could mitigate risk. In this paper, we propose a new approach, medical Generative Adversarial Network (medGAN), to generate realistic synthetic patient records. Based on input real patient records, medGAN can generate high-dimensional discrete variables (e.g., binary and count features) via a combination of an autoencoder and generative adversarial networks. We also propose minibatch averaging to efficiently avoid mode collapse, and increase the learning efficiency with batch normalization and shortcut connections. To demonstrate feasibility, we showed that medGAN generates synthetic patient records that achieve comparable performance to real data on many experiments including distribution statistics, predictive modeling tasks and a medical expert review. We also empirically observe a limited privacy risk in both identity and attribute disclosure using medGAN.

## 425. Extending a Generative Adversarial Network to Produce Medical Records with Demographic Characteristics and Health System Use

- Authors: Piper Jackson; Marco Lussetti
- Year: 2019
- DOI: 10.1109/iemcon.2019.8936168
- Venue: 
- Countries: CA
- Source: openalex
- URL: https://doi.org/10.1109/iemcon.2019.8936168

Generative adversarial networks use machine learning to generate synthetic data that is similar to real data. This has been widely applied to image data, and is now being applied to electronic medical records. Synthetically generated medical records are promising for many applications where privacy and security issues make using real medical records too risky. This includes software and systems development, training, and health research. Developing upon previous work, we have extended the MEDGAN system to generate records with eight additional variables, including demographic and health system use factors. The records generated are similar in distribution to the underlying dataset for all of these added variables. Finally, we discuss our future plans, with an emphasis on privacy-protecting approaches.

## 426. Ensuring electronic medical record simulation through better training, modeling, and evaluation

- Authors: Ziqi Zhang; Chao Yan; Diego A Mesa; Jimeng Sun; Bradley Malin
- Year: 2019
- DOI: 10.1093/jamia/ocz161
- Venue: Journal of the American Medical Informatics Association
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1093/jamia/ocz161
- PDF: https://academic.oup.com/jamia/article-pdf/27/1/99/34152076/ocz161.pdf

OBJECTIVE: Electronic medical records (EMRs) can support medical research and discovery, but privacy risks limit the sharing of such data on a wide scale. Various approaches have been developed to mitigate risk, including record simulation via generative adversarial networks (GANs). While showing promise in certain application domains, GANs lack a principled approach for EMR data that induces subpar simulation. In this article, we improve EMR simulation through a novel pipeline that (1) enhances the learning model, (2) incorporates evaluation criteria for data utility that informs learning, and (3) refines the training process. MATERIALS AND METHODS: We propose a new electronic health record generator using a GAN with a Wasserstein divergence and layer normalization techniques. We designed 2 utility measures to characterize similarity in the structural properties of real and simulated EMRs in the original and latent space, respectively. We applied a filtering strategy to enhance GAN training for low-prevalence clinical concepts. We evaluated the new and existing GANs with utility and privacy measures (membership and disclosure attacks) using billing codes from over 1 million EMRs at Vanderbilt University Medical Center. RESULTS: The proposed model outperformed the state-of-the-art approaches with significant improvement in retaining the nature of real records, including prediction performance and structural properties, without sacrificing privacy. Additionally, the filtering strategy achieved higher utility when the EMR training dataset was small. CONCLUSIONS: These findings illustrate that EMR simulation through GANs can be substantially improved through more appropriate training, modeling, and evaluation criteria.

## 427. Mortality prediction among ICU inpatients based on MIMIC-III database results from the conditional medical generative adversarial network

- Authors: Wei Yang; Hong Zou; Meng Wang; Qin Zhang; Shadan Li; Hongyin Liang
- Year: 2023
- DOI: 10.1016/j.heliyon.2023.e13200
- Venue: Heliyon
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1016/j.heliyon.2023.e13200
- PDF: http://www.cell.com/article/S2405844023004073/pdf

Background and aims: Improved mortality prediction among intensive care unit (ICU) inpatients is a valuable and challenging task. Limited clinical data, especially with appropriate labels, are an important element restricting accurate predictions. Generative adversarial networks (GANs) are excellent generative models and have shown great potential for data simulation. However, there have been no relevant studies using GANs to predict mortality among ICU inpatients. In this study, we aim to evaluate the predictive performance of a variant of GAN called conditional medical GAN (c-med GAN) compared with some baseline models, including simplified acute physiology score II (SAPS II), support vector machine (SVM), and multilayer perceptron (MLP). Methods: Data from a publicly available intensive care database, the Medical Information Mart for Intensive Care III (MIMIC-III) database (v1.4), were included in this study. The area under the precision-recall curve (PR-AUC), area under the receiver operating characteristic curve (ROC-AUC), and F1 score were used to evaluate the predictive performance. In addition, the size of the dataset was artificially reduced, and the performance of the c-med GAN was compared in different size datasets. Results: The results showed that c-med GAN achieves the best PR-AUC, ROC-AUC, and F1 score compared with SAPS II, SVM, and MLP when training in the full MIMIC-III dataset. When the size of the dataset was reduced, the prediction performances of both MLP and c-med GAN were affected. However, the c-med GAN still outperformed MLP on smaller datasets and had less degradation. Conclusion: The prediction of in-hospital mortality based on the c-med GAN for ICU patients showed better performance than the baseline models. Despite some inadequacies, this model may have a promising future in clinical applications which will be explored by further research.

## 428. Generating synthetic clinical data that capture class imbalanced distributions with generative adversarial networks: Example using antiretroviral therapy for HIV

- Authors: Nicholas I-Hsien Kuo; Féderico García; Anders Sönnerborg; Michael Böhm; Rolf Kaiser; Maurizio Zazzi; Mark N. Polizzotto; Louisa Jorm; Sebastiano Barbieri
- Year: 2023
- DOI: 10.1016/j.jbi.2023.104436
- Venue: Journal of Biomedical Informatics
- Countries: AU; DE; ES; IT; SE
- Source: openalex
- URL: https://doi.org/10.1016/j.jbi.2023.104436
- PDF: https://doi.org/10.1016/j.jbi.2023.104436

OBJECTIVE: Clinical data's confidential nature often limits the development of machine learning models in healthcare. Generative adversarial networks (GANs) can synthesise realistic datasets, but suffer from mode collapse, resulting in low diversity and bias towards majority demographics and common clinical practices. This work proposes an extension to the classic GAN framework that includes a variational autoencoder (VAE) and an external memory mechanism to overcome these limitations and generate synthetic data accurately describing imbalanced class distributions commonly found in clinical variables. METHODS: The proposed method generated a synthetic dataset related to antiretroviral therapy for human immunodeficiency virus (ART for HIV). We evaluated it based on five metrics: (1) accurately representing imbalanced class distribution; (2) the realism of the individual variables; (3) the realism among variables; (4) patient disclosure risk; and (5) the utility of the generated dataset for developing downstream machine learning models. RESULTS: The proposed method overcomes the issue of mode collapse and generates a synthetic dataset that accurately describes imbalanced class distributions commonly found in clinical variables. The generated data has a patient disclosure risk of 0.095%, lower than the 9% threshold stated by Health Canada and the European Medicines Agency, making it suitable for distribution to the research community with high security. The generated data also has high utility, indicating the potential of the proposed method to enable the development of downstream machine learning algorithms for healthcare applications using synthetic data. CONCLUSION: Our proposed extension to the classic GAN framework, which includes a VAE and an external memory mechanism, represents a promising approach towards generating synthetic data that accurately describe imbalanced class distributions commonly found in clinical variables. This method overcomes the limitations of GANs and creates more realistic datasets with higher patient cohort diversity, facilitating the development of downstream machine learning algorithms for healthcare applications.

## 429. Generating Synthetic Mixed-type Longitudinal Electronic Health Records for Artificial Intelligent Applications

- Authors: Jin Li; Benjamin J. Cairns; Jingsong Li; Tingting Zhu
- Year: 2021
- DOI: 10.48550/arxiv.2112.12047
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2112.12047
- PDF: https://arxiv.org/pdf/2112.12047

The recent availability of electronic health records (EHRs) have provided enormous opportunities to develop artificial intelligence (AI) algorithms. However, patient privacy has become a major concern that limits data sharing across hospital settings and subsequently hinders the advances in AI. Synthetic data, which benefits from the development and proliferation of generative models, has served as a promising substitute for real patient EHR data. However, the current generative models are limited as they only generate single type of clinical data for a synthetic patient, i.e., either continuous-valued or discrete-valued. To mimic the nature of clinical decision-making which encompasses various data types/sources, in this study, we propose a generative adversarial network (GAN) entitled EHR-M-GAN which simultaneously synthesizes mixed-type timeseries EHR data. EHR-M-GAN is capable of capturing the multidimensional, heterogeneous, and correlated temporal dynamics in patient trajectories. We have validated EHR-M-GAN on three publicly-available intensive care unit databases with records from a total of 141,488 unique patients, and performed privacy risk evaluation of the proposed model. EHR-M-GAN has demonstrated its superiority over state-of-the-art benchmarks for synthesizing clinical timeseries with high fidelity, while addressing the limitations regarding data types and dimensionality in the current generative models. Notably, prediction models for outcomes of intensive care performed significantly better when training data was augmented with the addition of EHR-M-GAN-generated timeseries. EHR-M-GAN may have use in developing AI algorithms in resource-limited settings, lowering the barrier for data acquisition while preserving patient privacy.

## 430. Electronic Health Records and Patient Safety

- Authors: D. Gans; J. White; R. Nath; J. Pohl; C. Tanner
- Year: 2015
- DOI: 10.4338/aci-2014-11-ra-0099
- Venue: Applied Clinical Informatics
- Countries: 
- Source: crossref
- URL: https://doi.org/10.4338/aci-2014-11-ra-0099

<jats:title>Summary</jats:title><jats:p>Background: The role of electronic health records (EHR) in enhancing patient safety, while substantiated in many studies, is still debated.</jats:p><jats:p>Objective: This paper examines early EHR adopters in primary care to understand the extent to which EHR implementation is associated with the workflows, policies and practices that promote patient safety, as compared to practices with paper records. Early adoption is defined as those who were using EHR prior to implementation of the Meaningful Use program.</jats:p><jats:p>Methods: We utilized the Physician Practice Patient Safety Assessment (PPPSA) to compare primary care practices with fully implemented EHR to those utilizing paper records. The PPPSA measures the extent of adoption of patient safety practices in the domains: medication management, handoffs and transition, personnel qualifications and competencies, practice management and culture, and patient communication.</jats:p><jats:p>Results: Data from 209 primary care practices responding between 2006–2010 were included in the analysis: 117 practices used paper medical records and 92 used an EHR. Results showed that, within all domains, EHR settings showed significantly higher rates of having workflows, policies and practices that promote patient safety than paper record settings. While these results were expected in the area of medication management, EHR use was also associated with adoption of patient safety practices in areas in which the researchers had no a priori expectations of association.</jats:p><jats:p>Conclusions: Sociotechnical models of EHR use point to complex interactions between technology and other aspects of the environment related to human resources, workflow, policy, culture, among others. This study identifies that among primary care practices in the national PPPSA database, having an EHR was strongly empirically associated with the workflow, policy, communication and cultural practices recommended for safe patient care in ambulatory settings.</jats:p><jats:p>Citation: Tanner C, Gans D, White J, Nath R, Pohl J. Electronic health records and patient safety – co-occurrence of early EHR implementation with patient safety practices in primary care settings. Appl Clin Inf 2015; 6: 136–147</jats:p><jats:p>http://dx.doi.org/10.4338/ACI-2014-11-RA-0099</jats:p>

## 431. EHR-Safe: Generating High-Fidelity and Privacy-Preserving Synthetic Electronic Health Records

- Authors: Jinsung Yoon; Michel Mizrahi; Nahid Ghalaty; Thomas Jarvinen; Ashwin Ravi; Peter Brune; Fanyu Kong; Dave Anderson; George Lee; Arie Meir; Farhana Bandukwala; Elli Kanal; Sercan Arik; Tomas Pfister
- Year: 2022
- DOI: 10.21203/rs.3.rs-2347130/v1
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.21203/rs.3.rs-2347130/v1

<title>Abstract</title>
        <p>Privacy concerns often arise as the key bottleneck for the sharing of data between consumers and data holders, particularly for sensitive data such as Electronic Health Records (EHR). This impedes the application of data analytics and ML-based innovations with tremendous potential. One promising approach to avoid such privacy concerns is to instead use synthetic data. We propose a novel generative modeling framework, EHR-Safe, for generating highly realistic and privacy-preserving synthetic EHR data. EHR-Safe is based on a two-stage model that consists of sequential encoder-decoder networks and generative adversarial networks. Our innovations focus on the key challenging aspects of real-world EHR data: the data are heterogeneous, consisting of numerical and categorical features with distinct characteristics; they contain time-varying features with highly-varying sequence lengths; and the features are often highly sparse. Under numerous evaluations, we demonstrate that the fidelity of EHR-Safe is very high, i.e. it has almost-identical properties with real data while yielding almost-ideal performance in practical privacy metrics.</p>

## 432. A Self-Attention Synthesizing Model with Privacy-Preserving(ACCT-GAN) for Medical Tabular Data

- Authors: Huamei Qi; Wenqin Zou; Sen Fu; Lei Deng
- Year: 2024
- DOI: 10.1109/bibm62325.2024.10822191
- Venue: 
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/bibm62325.2024.10822191

Accurate clinical cancer prediction is important for clinical diagnosis. Most of the cancer patient data have high privacy and using clinical patient data directly may create concerns such as privacy leakage, which can be solved by replacing real data with synthetic data for clinical trial modelling. Synthetic data can also fill in the missing, unbalanced clinical datasets. Data augmentation can achieve data synthesis. However, traditional data augmentation models are mostly based on convolutional neural network architectures, which can only capture local dependencies and do not well describe the feature-related information of patients over long survival times. In this paper, we propose a self-attention medical tabular data augmentation model with privacy protection, ACCT-GAN, based on the generative adversarial network model, which uses the AC block generated by combining the ACmix model to reconstruct the discriminator model in the CTAB-GAN+ network, which can effectively solve the limitations of the original convolutional neural network, model the global relationship, and make the generated data retain the feature correlation between the original data better correlations between the original data. Meanwhile, taking into account the privacy of medical data, the DP-SGD algorithm of CTAB-GAN+ is optimised to reduce the privacy risk of synthetic data. The results show that ACCT-GAN synthesizes privacy-preserving data with at least 26.21% higher utility across the dateset of nasopharyngeal cancer patients provided by Xiangya Medical College and learning tasks under different privacy budgets, demonstrating the usability, high quality, and better privacy preservation of the generated data, validating the effectiveness of this paper’s method, and confirming the potential of this paper’s method for cancer datasets.

## 433. Mimicking clinical trials with synthetic acute myeloid leukemia patients using generative artificial intelligence

- Authors: Jan‐Niklas Eckardt; Waldemar Hahn; Christoph Röllig; Sebastian Stasik; Uwe Platzbecker; Carsten Müller‐Tidow; Hubert Serve; Claudia D. Baldus; Christoph Schliemann; Kerstin Schäfer‐Eckart; Maher Hanoun; Martin Kaufmann; Andreas Burchert; Christian Thiede; Johannes Schetelig; Martin Sedlmayr; Martin Bornhäuser; Markus Wolfien; Jan Moritz Middeke
- Year: 2024
- DOI: 10.1038/s41746-024-01076-x
- Venue: npj Digital Medicine
- Countries: DE
- Source: openalex
- URL: https://doi.org/10.1038/s41746-024-01076-x
- PDF: https://www.nature.com/articles/s41746-024-01076-x.pdf

Clinical research relies on high-quality patient data, however, obtaining big data sets is costly and access to existing data is often hindered by privacy and regulatory concerns. Synthetic data generation holds the promise of effectively bypassing these boundaries allowing for simplified data accessibility and the prospect of synthetic control cohorts. We employed two different methodologies of generative artificial intelligence - CTAB-GAN+ and normalizing flows (NFlow) - to synthesize patient data derived from 1606 patients with acute myeloid leukemia, a heterogeneous hematological malignancy, that were treated within four multicenter clinical trials. Both generative models accurately captured distributions of demographic, laboratory, molecular and cytogenetic variables, as well as patient outcomes yielding high performance scores regarding fidelity and usability of both synthetic cohorts (n = 1606 each). Survival analysis demonstrated close resemblance of survival curves between original and synthetic cohorts. Inter-variable relationships were preserved in univariable outcome analysis enabling explorative analysis in our synthetic data. Additionally, training sample privacy is safeguarded mitigating possible patient re-identification, which we quantified using Hamming distances. We provide not only a proof-of-concept for synthetic data generation in multimodal clinical data for rare diseases, but also full public access to synthetic data sets to foster further research.

## 434. Federated learning for generating synthetic data: a scoping review

- Authors: Claire Little; Mark Elliot; Richard Allmendinger
- Year: 2023
- DOI: 10.23889/ijpds.v8i1.2158
- Venue: International Journal for Population Data Science
- Countries: GB
- Source: openalex
- URL: https://doi.org/10.23889/ijpds.v8i1.2158
- PDF: https://ijpds.org/article/download/2158/4965

Introduction: Federated Learning (FL) is a decentralised approach to training statistical models, where training is performed across multiple clients, producing one global model. Since the training data remains with each local client and is not shared or exchanged with other clients the use of FL may reduce privacy and security risks (compared to methods where multiple data sources are pooled) and can also address data access and heterogeneity problems. Synthetic data is artificially generated data that has the same structure and statistical properties as the original but that does not contain any of the original data records, therefore minimising disclosure risk. Using FL to produce synthetic data (which we refer to as "federated synthesis") has the potential to combine data from multiple clients without compromising privacy, allowing access to data that may otherwise be inaccessible in its raw format. Objectives: The objective was to review current research and practices for using FL to generate synthetic data and determine the extent to which research has been undertaken, the methods and evaluation practices used, and any research gaps. Methods: A scoping review was conducted to systematically map and describe the published literature on the use of FL to generate synthetic data. Relevant studies were identified through online databases and the findings are described, grouped, and summarised. Information extracted included article characteristics, documenting the type of data that is synthesised, the model architecture and the methods (if any) used to evaluate utility and privacy risk. Results: A total of 69 articles were included in the scoping review; all were published between 2018 and 2023 with two thirds (46) in 2022. 30% (21) were focussed on synthetic data generation as the main model output (with 6 of these generating tabular data), whereas 59% (41) focussed on data augmentation. Of the 21 performing federated synthesis, all used deep learning methods (predominantly Generative Adversarial Networks) to generate the synthetic data. Conclusions: Federated synthesis is in its early days but shows promise as a method that can construct a global synthetic dataset without sharing any of the local client data. As a field in its infancy there are areas to explore in terms of the privacy risk associated with the various methods proposed, and more generally in how we measure those risks.

## 435. Systematic Review of Generative Modelling Tools and Utility Metrics for Fully Synthetic Tabular Data

- Authors: Anton D. Lautrup; Tobias Hyrup; Arthur Zimek; Peter Schneider–Kamp
- Year: 2024
- DOI: 10.1145/3704437
- Venue: ACM Computing Surveys
- Countries: DK
- Source: openalex
- URL: https://doi.org/10.1145/3704437
- PDF: https://dl.acm.org/doi/pdf/10.1145/3704437

Sharing data with third parties is essential for advancing science, but it is becoming more and more difficult with the rise of data protection regulations, ethical restrictions, and growing fear of misuse. Fully synthetic data, which transcends anonymisation, may be the key to unlocking valuable untapped insights stored away in secured data vaults. This review examines current synthetic data generation methods and their utility measurement. We found that more traditional generative models such as Classification and Regression Tree models alongside Bayesian Networks remain highly relevant and are still capable of surpassing deep learning alternatives like Generative Adversarial Networks. However, our findings also display the same lack of agreement on metrics for evaluation, uncovered in earlier reviews, posing a persistent obstacle to advancing the field. We propose a tool for evaluating the utility of synthetic data and illustrate how it can be applied to three synthetic data generation models. By streamlining evaluation and promoting agreement on metrics, researchers can explore novel methods and generate compelling results that will convince data curators and lawmakers to embrace synthetic data. Our review emphasises the potential of synthetic data and highlights the need for greater collaboration and standardisation to unlock its full potential.

## 436. Permutation-Invariant Tabular Data Synthesis

- Authors: Yujin Zhu; Zilong Zhao; Robert Birke; Lydia Y. Chen
- Year: 2022
- DOI: 10.48550/arxiv.2211.09286
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2211.09286
- PDF: https://arxiv.org/pdf/2211.09286

Tabular data synthesis is an emerging approach to circumvent strict regulations on data privacy while discovering knowledge through big data. Although state-of-the-art AI-based tabular data synthesizers, e.g., table-GAN, CTGAN, TVAE, and CTAB-GAN, are effective at generating synthetic tabular data, their training is sensitive to column permutations of input data. In this paper, we first conduct an extensive empirical study to disclose such a property of permutation invariance and an in-depth analysis of the existing synthesizers. We show that changing the input column order worsens the statistical difference between real and synthetic data by up to 38.67% due to the encoding of tabular data and the network architectures. To fully unleash the potential of big synthetic tabular data, we propose two solutions: (i) AE-GAN, a synthesizer that uses an autoencoder network to represent the tabular data and GAN networks to synthesize the latent representation, and (ii) a feature sorting algorithm to find the suitable column order of input data for CNN-based synthesizers. We evaluate the proposed solutions on five datasets in terms of the sensitivity to the column permutation, the quality of synthetic data, and the utility in downstream analyses. Our results show that we enhance the property of permutation-invariance when training synthesizers and further improve the quality and utility of synthetic data, up to 22%, compared to the existing synthesizers.

## 437. Mimicking Clinical Trials with Synthetic Acute Myeloid Leukemia Patients Using Generative Artificial Intelligence

- Authors: Jan‐Niklas Eckardt; Waldemar Hahn; Christoph Röllig; Sebastian Stasik; Uwe Platzbecker; Carsten Müller‐Tidow; Hubert Serve; Claudia D. Baldus; Christoph Schliemann; Kerstin Schäfer-Eckart; Maher Hanoun; Martin Kaufmann; Andreas Burchert; Christian Thiede; Johannes Schetelig; Martin Sedlmayr; Martin Bornhäuser; Markus Wolfien; Jan Moritz Middeke
- Year: 2023
- DOI: 10.1101/2023.11.08.23298247
- Venue: medRxiv
- Countries: DE; NL
- Source: openalex
- URL: https://doi.org/10.1101/2023.11.08.23298247
- PDF: https://www.medrxiv.org/content/medrxiv/early/2023/11/08/2023.11.08.23298247.full.pdf

Abstract Clinical research relies on high-quality patient data, however, obtaining big data sets is costly and access to existing data is often hindered by privacy and regulatory concerns. Synthetic data generation holds the promise of effectively bypassing these boundaries allowing for simplified data accessibility and the prospect of synthetic control cohorts. We employed two different methodologies of generative artificial intelligence – CTAB-GAN+ and normalizing flows (NFlow) – to synthesize patient data derived from 1606 patients with acute myeloid leukemia, a heterogeneous hematological malignancy, that were treated within four multicenter clinical trials. Both generative models accurately captured distributions of demographic, laboratory, molecular and cytogenetic variables, as well as patient outcomes yielding high performance scores regarding fidelity and usability of both synthetic cohorts (n=1606 each). Survival analysis demonstrated close resemblance of survival curves between original and synthetic cohorts. Inter-variable relationships were preserved in univariable outcome analysis enabling explorative analysis in our synthetic data. Additionally, training sample privacy is safeguarded mitigating possible patient re-identification, which we quantified using Hamming distances. We provide not only a proof-of-concept for synthetic data generation in multimodal clinical data for rare diseases, but also full public access to synthetic data sets to foster further research. Graphical Abstract

## 438. An enhancement of machine learning model performance in disease prediction with synthetic data generation

- Authors: M. K. Jayanthi Kannan; Duraiswamy Umamaheswari; B. Manimekala; I. Priya Stella Mary; P. Margaret Savitha; Juliet Rozario
- Year: 2025
- DOI: 10.1038/s41598-025-15019-3
- Venue: Scientific Reports
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.1038/s41598-025-15019-3
- PDF: https://www.nature.com/articles/s41598-025-15019-3.pdf

The challenges of handling imbalanced datasets in machine learning significantly affect the model performance and predictive accuracy. Classifiers tend to favor the majority class, leading to biased training and poor generalization of minority classes. Initially, the model incorrectly treats the target variable as an independent feature during data generation, resulting in suboptimal outcomes. To address this limitation, the model was adjusted to more effectively manage target variable generation and mitigate the issue. This study employed advanced techniques for synthetic data generation, such as synthetic minority oversampling (SMOTE) and Adaptive Synthetic Sampling (ADASYN), to enhance the representation of minority classes by generating synthetic samples. In addition, data augmentation strategies using Deep Conditional Tabular Generative Adversarial Networks (Deep-CTGANs) integrated with ResNet have been utilized to improve model robustness and overall generalizability. For classification, TabNet, a model tailored specifically for tabular data, proved highly effective with its sequential attention mechanism that dynamically processes features, making it well suited for handling complex and imbalanced datasets. Model performance was evaluated using a novel approach of training synthetic data and testing on real data (TSTR). The framework was validated on the COVID-19, Kidney, and Dengue datasets, achieving impressive testing accuracies of 99.2%, 99.4%, and 99.5%, respectively. Furthermore, similarity scores of 84.25%, 87.35%, and 86.73% between the real and synthetic data for the COVID-19, Kidney, and Dengue datasets, respectively, confirmed the reliability of the synthetic data. TabNet consistently showed substantial improvements in F1-scores compared to other models, such as Random Forest, XGBoost, and KNN, emphasizing the importance of selecting the right synthetic data augmentation techniques and classifiers. Additionally, SHapley Additive exPlanations (SHAP)-based explainable AI tools were used to interpret model performance, providing insights into feature importance and its impact on predictions. These findings confirm that the proposed approach enhances the accuracy, robustness, and interpretability, offering a valuable solution for addressing data imbalance in classification tasks.

## 439. Synthetic Tabular Data Generation for Imbalanced Classification: The Surprising Effectiveness of an Overlap Class

- Authors: A. D'Souza; M Swetha; Sunita Sarawagi
- Year: 2025
- DOI: 10.1609/aaai.v39i15.33771
- Venue: Proceedings of the AAAI Conference on Artificial Intelligence
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.1609/aaai.v39i15.33771
- PDF: https://ojs.aaai.org/index.php/AAAI/article/download/33771/35926

Handling imbalance in class distribution when building a classifier over tabular data has been a problem of long-standing interest. One popular approach is augmenting the training dataset with synthetically generated data. While classical augmentation techniques were limited to linear interpolation of existing minority class examples, recently higher capacity deep generative models are providing greater promise. However, handling of imbalance in class distribution when building a deep generative model is also a challenging problem, that has not been studied as extensively as imbalanced classifier model training. We show that state-of-the-art deep generative models yield significantly lower-quality minority examples than majority examples. We propose a novel technique of converting the binary class labels to ternary class labels by introducing a class for the region where minority and majority distributions overlap. We show that just this pre-processing of the training set, significantly improves the quality of data generated spanning several state-of-the-art diffusion and GAN-based models. While training the classifier using synthetic data, we remove the overlap class from the training data and justify the reasons behind the enhanced accuracy. We perform extensive experiments on four real-life datasets, five different classifiers, and five generative models, demonstrating that our method enhances not only the synthesizer performance of state-of-the-art models but also the classifier performance

## 440. A Novel Digital Twin Strategy to Examine the Implications of Randomized Clinical Trials for Real-World Populations

- Authors: Phyllis Thangaraj; Sumukh Vasisht Shankar; Sicong Huang; Girish N. Nadkarni; Bobak J. Mortazavi; Evangelos K. Oikonomou; Rohan Khera
- Year: 2024
- DOI: 10.1101/2024.03.25.24304868
- Venue: medRxiv
- Countries: US
- Source: openalex
- URL: https://doi.org/10.1101/2024.03.25.24304868
- PDF: https://www.medrxiv.org/content/medrxiv/early/2024/03/26/2024.03.25.24304868.full.pdf

Randomized clinical trials (RCTs) are essential to guide medical practice; however, their generalizability to a given population is often uncertain. We developed a statistically informed Generative Adversarial Network (GAN) model, RCT-Twin-GAN, that leverages relationships between covariates and outcomes and generates a digital twin of an RCT (RCT-Twin) conditioned on covariate distributions from a second patient population. We used RCT-Twin-GAN to reproduce treatment effect outcomes of the Systolic Blood Pressure Intervention Trial (SPRINT) and the Action to Control Cardiovascular Risk in Diabetes (ACCORD) Blood Pressure Trial, which tested the same intervention but found different treatment effects. To demonstrate treatment effect estimates of each RCT conditioned on the other RCT's patient population, we evaluated the cardiovascular event-free survival of SPRINT digital twins conditioned on the ACCORD cohort and vice versa (ACCORD twins conditioned on SPRINT). The conditioned digital twins were balanced across intervention and control arms (mean absolute standardized mean difference (MASMD) of covariates between treatment arms 0.019 (SD 0.018), and the conditioned covariates of the SPRINT-Twin on ACCORD were more similar to ACCORD than SPRINT (MASMD 0.0082 SD 0.016 vs. 0.46 SD 0.20). Notably, across iterations, SPRINT conditioned ACCORD-Twin datasets reproduced the overall non-significant effect size seen in ACCORD (5-year cardiovascular outcome hazard ratio (95% confidence interval) of 0.88 (0.73-1.06) in ACCORD vs. median 0.87 (0.68-1.13) in the SPRINT conditioned ACCORD-Twin), while the ACCORD conditioned SPRINT-Twins reproduced the significant effect size seen in SPRINT (0.75 (0.64-0.89) vs. median 0.79 (0.72-0.86)) in the ACCORD conditioned SPRINT-Twin). Finally, we demonstrate the translation of this approach to real-world populations by conditioning the trials on an electronic health record population. Therefore, RCT-Twin-GAN simulates the direct translation of RCT-derived treatment effects across various patient populations.

## 441. HT-Fed-GAN: Federated Generative Model for Decentralized Tabular Data Synthesis

- Authors: Shaoming Duan; Chuanyi Liu; Peiyi Han; Xiaopeng Jin; Xinyi Zhang; Tianyu He; Hezhong Pan; Xiayu Xiang
- Year: 2022
- DOI: 10.3390/e25010088
- Venue: Entropy
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3390/e25010088

<jats:p>In this paper, we study the problem of privacy-preserving data synthesis (PPDS) for tabular data in a distributed multi-party environment. In a decentralized setting, for PPDS, federated generative models with differential privacy are used by the existing methods. Unfortunately, the existing models apply only to images or text data and not to tabular data. Unlike images, tabular data usually consist of mixed data types (discrete and continuous attributes) and real-world datasets with highly imbalanced data distributions. Existing methods hardly model such scenarios due to the multimodal distributions in the decentralized continuous columns and highly imbalanced categorical attributes of the clients. To solve these problems, we propose a federated generative model for decentralized tabular data synthesis (HT-Fed-GAN). There are three important parts of HT-Fed-GAN: the federated variational Bayesian Gaussian mixture model (Fed-VB-GMM), which is designed to solve the problem of multimodal distributions; federated conditional one-hot encoding with conditional sampling for global categorical attribute representation and rebalancing; and a privacy consumption-based federated conditional GAN for privacy-preserving decentralized data modeling. The experimental results on five real-world datasets show that HT-Fed-GAN obtains the best trade-off between the data utility and privacy level. For the data utility, the tables generated by HT-Fed-GAN are the most statistically similar to the original tables and the evaluation scores show that HT-Fed-GAN outperforms the state-of-the-art model in terms of machine learning tasks.</jats:p>

## 442. A Cross-Attention Optimized CTAB-GAN+ Algorithm for Student Data Generation

- Authors: Yong-Mei Zhang; Zhi-Zheng Yang; Zhi-Rong Du
- Year: 2025
- DOI: 10.1109/ccet66260.2025.11199693
- Venue: 2025 IEEE 8th International Conference on Computer and Communication Engineering Technology (CCET)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/ccet66260.2025.11199693

## 443. C3-TGAN- Controllable Tabular Data Synthesis with Explicit Correlations and Property Constraints

- Authors: Peiyi Han; Wen Xu; Wanyu Lin; Jiahao Cao; Chuanyi Liu; Shaoming Duan; Haifeng Zhu
- Year: 2023
- DOI: 10.36227/techrxiv.24249643
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.36227/techrxiv.24249643

<jats:p>&lt;p&gt;GAN-based tabular synthesis methods have made important progress in generating sophisticated synthetic data for privacypreserving data publishing. However, existing methods do not consider explicit attribute correlations and property constraints on tabular data synthesis, which may lead to inaccurate data analysis results. In this paper, we propose a Controllable tabular data synthesis framework with explicit Correlations and property Constraints, namely C3-TGAN. It leverages Bayesian networks to learn explicit correlations among attributes and model them as control vectors. Such control vectors can guide C3-TGAN to generate synthetic data with complicated property constraints. By conducting comprehensive experiments on 14 publicly available benchmark datasets, we showcase C3-TGAN’s remarkable performance advantage over state-of-the-art methods for synthesizing tabular data.&lt;/p&gt;</jats:p>

## 444. Generating high-fidelity privacy-conscious synthetic patient data for causal effect estimation with multiple treatments

- Authors: Jingpu Shi; Dong Wang; Gino Tesei; Beau Norgeot
- Year: 2022
- DOI: 10.3389/frai.2022.918813
- Venue: Frontiers in Artificial Intelligence
- Countries: US
- Source: openalex
- URL: https://doi.org/10.3389/frai.2022.918813
- PDF: https://www.frontiersin.org/articles/10.3389/frai.2022.918813/pdf

In the past decade, there has been exponentially growing interest in the use of observational data collected as a part of routine healthcare practice to determine the effect of a treatment with causal inference models. Validation of these models, however, has been a challenge because the ground truth is unknown: only one treatment-outcome pair for each person can be observed. There have been multiple efforts to fill this void using synthetic data where the ground truth can be generated. However, to date, these datasets have been severely limited in their utility either by being modeled after small non-representative patient populations, being dissimilar to real target populations, or only providing known effects for two cohorts (treated vs. control). In this work, we produced a large-scale and realistic synthetic dataset that provides ground truth effects for over 10 hypertension treatments on blood pressure outcomes. The synthetic dataset was created by modeling a nationwide cohort of more than 580, 000 hypertension patient data including each person's multi-year history of diagnoses, medications, and laboratory values. We designed a data generation process by combining an adapted ADS-GAN model for fictitious patient information generation and a neural network for treatment outcome generation. Wasserstein distance of 0.35 demonstrates that our synthetic data follows a nearly identical joint distribution to the patient cohort used to generate the data. Patient privacy was a primary concern for this study; the ϵ-identifiability metric, which estimates the probability of actual patients being identified, is 0.008%, ensuring that our synthetic data cannot be used to identify any actual patients. To demonstrate its usage, we tested the bias in causal effect estimation of four well-established models using this dataset. The approach we used can be readily extended to other types of diseases in the clinical domain, and to datasets in other domains as well.

## 445. Revolutionizing personalized medicine with generative AI: a systematic review

- Authors: Isaias Ghebrehiwet; Nazar Zaki; Rafat Damseh; Mohd Saberi Mohamad
- Year: 2024
- DOI: 10.1007/s10462-024-10768-5
- Venue: Artificial Intelligence Review
- Countries: AE
- Source: openalex
- URL: https://doi.org/10.1007/s10462-024-10768-5
- PDF: https://link.springer.com/content/pdf/10.1007/s10462-024-10768-5.pdf

Abstract Background Precision medicine, targeting treatments to individual genetic and clinical profiles, faces challenges in data collection, costs, and privacy. Generative AI offers a promising solution by creating realistic, privacy-preserving patient data, potentially revolutionizing patient-centric healthcare. Objective This review examines the role of deep generative models (DGMs) in clinical informatics, medical imaging, bioinformatics, and early diagnostics, showcasing their impact on precision medicine. Methods Adhering to PRISMA guidelines, the review analyzes studies from databases such as Scopus and PubMed, focusing on AI's impact in precision medicine and DGMs' applications in synthetic data generation. Results DGMs, particularly Generative Adversarial Networks (GANs), have improved synthetic data generation, enhancing accuracy and privacy. However, limitations exist, especially in the accuracy of foundation models like Large Language Models (LLMs) in digital diagnostics. Conclusion Overcoming data scarcity and ensuring realistic, privacy-safe synthetic data generation are crucial for advancing personalized medicine. Further development of LLMs is essential for improving diagnostic precision. The application of generative AI in personalized medicine is emerging, highlighting the need for more interdisciplinary research to advance this field.

## 446. Synthetic Data Generation Using Generative AI: Revolutionizing Data-Driven Innovation

- Authors: Anil Kumar Shukla
- Year: 2025
- DOI: 10.36227/techrxiv.174970408.89727969/v1
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.36227/techrxiv.174970408.89727969/v1

<jats:p>Synthetic data arise to solve problems of data scarcity, privacy regulation, and bias in machine learning. However, trade-offs between fidelity, privacy, computational costs, and scalability of generative models have not yet been explored. The work presents an extensive benchmarking and critical evaluation of major generative frameworks for synthetic data generation-GANs, VAEs, diffusion models, and recent hybrid architectures. Through standardized metrics across image and tabular datasets, we show that such hybrid architectures, namely Diffusion-GANs, can drastically improve fidelity (32% reduction in Fréchet Inception Distance) while reducing computation cost by 40% compared to regular GANs. Our technical evaluation is followed by a systematic study of the real-world applications in healthcare, finance, and autonomous systems, covering the ethical, environmental, and governance issues regarding synthetic data. Our findings provide a balanced roadmap that intertwines technical advancement with responsible deployment strategies, making synthetic data generation a foundation for scalable and privacypreserving AI innovations.</jats:p>

## 447. GDTS: GAN-Based Distributed Tabular Synthesizer

- Authors: Zilong Zhao; Robert Birke; Lydia Y. Chen
- Year: 2023
- DOI: 10.1109/cloud60044.2023.00078
- Venue: 2023 IEEE 16th International Conference on Cloud Computing (CLOUD)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/cloud60044.2023.00078

## 448. Augmenting Nonlinear Shear Creep Evaluation of Adhesive Joints with Conditional Tabular Gan

- Authors: Songbo Wang; Yanchen Fu; Tim Stratford; Jun Su; Yang Li; Biao Li
- Year: 2024
- DOI: 10.2139/ssrn.4987241
- Venue: 
- Countries: 
- Source: crossref
- URL: https://doi.org/10.2139/ssrn.4987241

## 449. OCT-GAN: Neural ODE-based Conditional Tabular GANs

- Authors: Jayoung Kim; Jinsung Jeon; Jaehoon Lee; Jihyeon Hyeong; Noseong Park
- Year: 2021
- DOI: 10.1145/3442381.3449999
- Venue: Proceedings of the Web Conference 2021
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1145/3442381.3449999

## 450. Leveraging Distributional Symmetry in Credit Card Fraud Detection via Conditional Tabular GAN Augmentation and LightGBM

- Authors: Cichen Wang; Can Xie; Jialiang Li
- Year: 2026
- DOI: 10.3390/sym18020224
- Venue: Symmetry
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3390/sym18020224

<jats:p>Credit card fraud detection remains a major challenge due to extreme class imbalance and evolving attack patterns. This paper proposes a practical hybrid pipeline that combines conditional tabular generative adversarial networks (CTGANs) for targeted minority-class synthesis with Light Gradient Boosting Machine (LightGBM) for classification. Inspired by symmetry principles in machine learning, we leverage the adversarial equilibrium of CTGAN to generate realistic fraudulent transactions that maintain distributional symmetry with real fraud patterns, thereby preserving the structural and statistical balance of the original dataset. Synthetic fraud samples are merged with real data to form augmented training sets that restore the symmetry of class representation. We evaluate Simple Recurrent Neural Network (RNN), Long Short-Term Memory (LSTM), Gated Recurrent Unit (GRU) classifiers, and a LightGBM model on a public dataset using stratified 5-fold validation and an independent hold-out test set. Models are compared using sensitivity, precision, F-measure(F1), and area under the precision–recall curve (PR-AUC), which reflects symmetry between detection and false-alarm trade-offs. Results show that CTGAN-based augmentation yields large and consistent gains across architectures. The best-performing configuration, CTGAN + LightGBM, attains sensitivity = 0.986, precision = 0.982, F1 = 0.984, and PR-AUC = 0.918 on the test data, substantially outperforming non-augmented baselines and recent methods. These findings indicate that conditional synthetic augmentation materially improves the detection of rare fraud modes while preserving low false-alarm rates, demonstrating the value of symmetry-aware data synthesis in classification under imbalance. We discuss generation-quality checks, risk of distributional shift, and deployment considerations. Future work will explore alternative generative models with explicit symmetry constraints and time-aware production evaluation.</jats:p>

## 451. A Conditional Tabular GAN-Enhanced Intrusion Detection System for Rare Attacks in IoT Networks

- Authors: Safaa Menssouri; El Mehdi Amhoud
- Year: 2025
- DOI: 10.1109/iccworkshops67674.2025.11162182
- Venue: 2025 IEEE International Conference on Communications Workshops (ICC Workshops)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/iccworkshops67674.2025.11162182

## 452. Temporal Transformer with Conditional Tabular GAN for Credit Card Fraud Detection: A Sequential Deep Learning Approach

- Authors: Jiaying Chen; Yiwen Liang; Jingyi Liu; Mengjie Zhou
- Year: 2026
- DOI: 10.3390/math14071183
- Venue: Mathematics
- Countries: 
- Source: crossref
- URL: https://doi.org/10.3390/math14071183

<jats:p>Credit card fraud detection remains a critical challenge in financial security, characterized by severe class imbalance and the need to capture complex temporal patterns in transaction sequences. Traditional machine learning approaches treat transactions as independent events, failing to model the sequential nature of user behavior and suffering from inadequate handling of minority class samples. In this paper, we propose an integrated framework that combines generative modeling and time-aware sequential learning for credit card fraud detection. Our approach addresses two fundamental limitations: (1) we model transaction histories as temporal sequences using a Transformer-based architecture that captures both long-term dependencies and abrupt behavioral changes through multi-head self-attention mechanisms, and (2) we employ CTGAN to generate high-quality synthetic fraudulent samples, providing more effective oversampling than conventional techniques like SMOTE. The Time-Aware Transformer incorporates temporal encoding and position-aware attention to preserve transaction order and time intervals, while CTGAN learns the complex conditional distributions of fraudulent transactions to produce realistic synthetic samples. We evaluate our framework on the IEEE-CIS Fraud Detection dataset, demonstrating significant improvements over representative classical and sequential deep-learning baselines. Experimental results show that our method achieves superior performance with an AUC-ROC of 0.982, precision of 0.891, recall of 0.876, and F1-score of 0.883, outperforming the representative baselines considered in this study, including traditional machine learning models, standalone deep learning architectures, and supervised sequential neural models. Ablation studies confirm the individual contributions of both the sequential modeling component and the generative oversampling strategy. Our work demonstrates that combining temporal sequence modeling with generative synthesis provides a robust solution for imbalanced fraud detection, with potential applications extending to other domains requiring sequential pattern recognition under extreme class imbalance.</jats:p>

## 453. Enhancing Tabular GAN Fairness: The Impact of Intersectional Feature Selection

- Authors: Tahereh Dehdarirad; Ericka Johnson; Gabriel Eilertsen; Saghi Hajisharif
- Year: 2024
- DOI: 10.1109/icmla61862.2024.00176
- Venue: 2024 International Conference on Machine Learning and Applications (ICMLA)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/icmla61862.2024.00176

## 454. WRGAN: Improvement of RelGAN with Wasserstein Loss for Text Generation

- Authors: Ziyun Jiao; Fuji Ren
- Year: 2021
- DOI: 10.3390/electronics10030275
- Venue: Electronics
- Countries: JP
- Source: openalex
- URL: https://doi.org/10.3390/electronics10030275
- PDF: https://www.mdpi.com/2079-9292/10/3/275/pdf?version=1611554191

Generative adversarial networks (GANs) were first proposed in 2014, and have been widely used in computer vision, such as for image generation and other tasks. However, the GANs used for text generation have made slow progress. One of the reasons is that the discriminator’s guidance for the generator is too weak, which means that the generator can only get a “true or false” probability in return. Compared with the current loss function, the Wasserstein distance can provide more information to the generator, but RelGAN does not work well with Wasserstein distance in experiments. In this paper, we propose an improved neural network based on RelGAN and Wasserstein loss named WRGAN. Differently from RelGAN, we modified the discriminator network structure with 1D convolution of multiple different kernel sizes. Correspondingly, we also changed the loss function of the network with a gradient penalty Wasserstein loss. Our experiments on multiple public datasets show that WRGAN outperforms most of the existing state-of-the-art methods, and the Bilingual Evaluation Understudy(BLEU) scores are improved with our novel method.

## 455. Collaborative Training of Gans in Continuous and Discrete Spaces for Text Generation

- Authors: Yanghoon Kim; Seungpil Won; Seunghyun Yoon; Kyomin Jung
- Year: 2020
- DOI: 10.1109/access.2020.3045166
- Venue: IEEE Access
- Countries: KR; US
- Source: openalex
- URL: https://doi.org/10.1109/access.2020.3045166
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/6514899/09296209.pdf

Applying generative adversarial networks (GANs) to text-related tasks is challenging due to the discrete nature of language. One line of research resolves this issue by employing reinforcement learning (RL) and optimizing the next-word sampling policy directly in a discrete action space. Such methods compute the rewards from complete sentences and avoid error accumulation due to exposure bias. Other approaches employ approximation techniques that map the text to continuous representation in order to circumvent the non-differentiable discrete process. Particularly, autoencoder-based methods effectively produce robust representations that can model complex discrete structures. In this article, we propose a novel text GAN architecture that promotes the collaborative training of the continuous-space and discrete-space methods. Our method employs an autoencoder to learn an implicit data manifold, providing a learning objective for adversarial training in a continuous space. Furthermore, the complete textual output is directly evaluated and updated via RL in a discrete space. The collaborative interplay between the two adversarial trainings effectively regularize the text representations in different spaces. The experimental results on three standard benchmark datasets show that our model substantially outperforms state-of-the-art text GANs with respect to quality, diversity, and global consistency.

## 456. Generating culturally-contextual chinese cyberbullying datasets: A GAN approach for social psychology research

- Authors: Xiangqin Dai; Mohd Najwadi Yusoff; Bingli Zhu; Xiao Zhang; Wujin Jiang; Lei Wang
- Year: 2025
- DOI: 10.59429/esp.v10i7.3834
- Venue: Environment and Social Psychology
- Countries: 
- Source: openalex
- URL: https://doi.org/10.59429/esp.v10i7.3834
- PDF: https://doi.org/10.59429/esp.v10i7.3834

Cyberbullying has become a growing concern with serious psychological and social consequences, including anxiety, depression, and disrupted online communities. Grounded in social psychology theories such as social learning and online disinhibition, cyberbullying is shaped by factors like anonymity and peer influence. However, the lack of Chinese-language cyberbullying datasets limits research and intervention efforts. To address this, we used four GAN models SeqGAN, RankGAN, MaliGAN, and LeakGAN to generate realistic Chinese cyberbullying text. LeakGAN outperformed the others, achieving a BLEU2 score of 0.948, self-BLEU2 of 0.963, NLL of 0.48, and the highest EmbSim values. Beyond technical performance, we emphasized psychological validity, cultural relevance, and ethical considerations in the data generation process. The findings have important implications for automated detection, intervention design, and social psychology research. Framed within ecological systems theory, this work also considers how online environments shape behavior. The synthetic dataset supports applications in schools, workplaces, and cross-cultural studies, though limitations remain in capturing the full complexity of real human behavior. Overall, LeakGAN’s success offers a strong foundation for future research on cyberbullying in digital contexts.

## 457. Abusive and Hate Speech Tweets Detection with Text Generation

- Authors: Abhishek Nalamothu
- Year: 2019
- DOI: 
- Venue: Journal of Bioresource Management
- Countries: 
- Source: openalex
- URL: https://openalex.org/W2982439895
- PDF: https://corescholar.libraries.wright.edu/etd_all/2094

According to a Pew Research study, 41% of Americans have personally experienced online harassment and two-thirds of Americans have witnessed harassment in 2017. Hence, online harassment detection is vital for securing and sustaining the popularity and viability of online social networks. Machine learning techniques play a crucial role in automatic harassment detection. One of the challenges of using supervised approaches is training data imbalance. Existing text generation techniques can help augment the training data, but they are still inadequate and ineffective. This research explores the role of domain-specific knowledge to complement the limited training data available for training a text generator. We conduct domain-specific text generation by combining inverse reinforcement learning (IRL) with domain-specific knowledge. Our approach includes two adversarial nets, a text generator and a Reward Approximator (RA). The objective of the text generator is to generate domain-specific text that is hard to discriminate from the real-world domain-specific text. The objective of the reward approximator is to discriminate the generated domain-specific text from the real-world text. During adversarial training, the generator and the RA play a mini-max game and try to arrive at a win-win state. Ultimately, augmenting diversified and semantically meaningful, generated domain-specific data to the existing dataset improves detection of domain-specific text. In addition to developing the Generative Adversarial Network-based framework, we also present a novel evaluation that uses variants of the BLEU metric to measure the diversity of generated text; uses perplexity and cosine similarity to measure the quality of the generated text. Experimental results show that the proposed framework outperforms a previous baseline (IRL without domain knowledge) on harassment (i.e., Abusive and Hate speech) tweet generation. Additionally, the generated tweets effectively augment the training data for online abusive and hate speech detection (tweet classification) resulting in a 9% accuracy improvement in classification using the augmented training set compared to the existing training set.

## 458. Unveiling Deception: A GAN-Based Unsupervised Learning Approach for Real-Time Generation and Detection of Text-Based Fake News

- Authors: Vivek Joshi
- Year: 2024
- DOI: 10.52783/jes.6586
- Venue: Journal of Electrical Systems
- Countries: 
- Source: openalex
- URL: https://doi.org/10.52783/jes.6586
- PDF: https://journal.esrgroups.org/jes/article/download/6586/4570

Generative artificial intelligence technology advancements have made it easy to generate fake news. Online community platforms like social media have made propagation of such fake news faster and more convenient. We have witnessed the social impact of such fake news in the past few years. In the literature, a Generative Adversarial Network (GAN) is used to detect text-based fake news based on structured data with the supervised learning approaches. However, we have observed that most large-scale online data are unstructured and can not be used with the supervised learning approaches. In this paper, we have used an auto-encoder to select the features from the unstructured data and feed them to GAN.

## 459. Research on Text Summary Generation Based on Bidirectional Encoder Representation from Transformers

- Authors: Kai Wen; Zhou Lingyu
- Year: 2020
- DOI: 10.1109/itca52113.2020.00074
- Venue: 
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/itca52113.2020.00074

For Chinese automatic summarization, most of the generation methods are extractive, and the generative summary is not smooth, incoherent, and covers incomplete information. Compared with the traditional sequence-to-sequence model, Generative Adversarial Network (GAN) uses a reinforcement learning strategy The use of discriminator to guide generation has achieved good results in text generation. This paper proposes a pre-training method based on Bidirectional Encoder Representation from Transformers (BERT) and combined with LeakGAN model to generate abstracts. Firstly, using the bidirectional encoding characteristics of the BERT model, it can retain the original information well, and has a better effect when extracting features of words in the context to generate high-quality word vectors; secondly, for the current supervised generative model Both have the training problem of maximum likelihood estimation. This article uses the LeakGAN model that can decompose the task into different levels of sub-strategies, and uses hierarchical reinforcement learning to solve the characteristics of sparse rewards and generate a more accurate summary.

## 460. LeakGAN-Based Causality Extraction in the Financial Field

- Authors: Zhengyan Sun; Xiaoqing Li; Guangli Zhu
- Year: 2023
- DOI: 10.1007/978-3-031-28893-7_30
- Venue: Lecture notes on data engineering and communications technologies
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1007/978-3-031-28893-7_30

## 461. TransLeakGAN: A Transformer-Based Framework for Enhanced Long Text Generation

- Authors: Harsha Vasireddy; B. Shanmuga Priya; B. Sivaselvan
- Year: 2025
- DOI: 10.1007/978-3-031-96473-2_20
- Venue: Communications in computer and information science
- Countries: IN
- Source: openalex
- URL: https://doi.org/10.1007/978-3-031-96473-2_20

## 462. Abstractive Document Summarisation using Generative Adversarial Networks

- Authors: Karl Svensson
- Year: 2018
- DOI: 
- Venue: Chalmers Publication Library (Chalmers University of Technology)
- Countries: 
- Source: openalex
- URL: https://openalex.org/W2886039284
- PDF: http://studentarbeten.chalmers.se/publication/255471-abstractive-document-summarisation-using-generative-adversarial-networks

The use of automatically generated summaries for long texts is commonly used in digital services. In this thesis, one method for such document summarisation is created by combining existing techniques for abstractive document summarization with LeakGAN – a successful approach at text generation using generative adversarial networks (GAN). The resulting model is tested on two diﬀerent datasets originating from conventional newspapers and the world’s largest online community: Reddit. The datasets are examined and several important diﬀerences are highlighted. The evaluations show that the summaries generated by the model do not correlate with the corresponding documents. Possible reasons are discussed and several suggestions for future research are presented.

## 463. Claim Verification using a Multi-GAN based Model

- Authors: Amartya Hatua; Arjun Mukherjee; Rakesh Verma
- Year: 2021
- DOI: 10.26615/978-954-452-072-4_056
- Venue: 
- Countries: US
- Source: openalex
- URL: https://doi.org/10.26615/978-954-452-072-4_056
- PDF: https://doi.org/10.26615/978-954-452-072-4_056

This article describes research on claim verification carried out using a multiple GAN-based model. The proposed model consists of three pairs of generators and discriminators. The generator and discriminator pairs are responsible for generating synthetic data for supported and refuted claims and claim labels. A theoretical discussion about the proposed model is provided to validate the equilibrium state of the model. The proposed model is applied to the FEVER dataset, and a pre-trained language model is used for the input text data. The synthetically generated data helps to gain information that improves classification performance over state of the art baselines. The respective F1 scores after applying the proposed method on FEVER 1.0 and FEVER 2.0 datasets are 0.650.018 and 0.650.051.

## 464. Generative Adversarial Networks for Creating Synthetic Free-Text Medical Data: A Proposal for Collaborative Research and Re-use of Machine Learning Models.

- Authors: Suranga N. Kasthurirathne; Gregory Dexter; Shaun J. Grannis
- Year: 2021
- DOI: 
- Venue: PubMed
- Countries: US
- Source: openalex
- URL: https://openalex.org/W3188341194
- PDF: http://hdl.handle.net/1805/26152

Restrictions in sharing Patient Health Identifiers (PHI) limit cross-organizational re-use of free-text medical data. We leverage Generative Adversarial Networks (GAN) to produce synthetic unstructured free-text medical data with low re-identification risk, and assess the suitability of these datasets to replicate machine learning models. We trained GAN models using unstructured free-text laboratory messages pertaining to salmonella, and identified the most accurate models for creating synthetic datasets that reflect the informational characteristics of the original dataset. Natural Language Generation metrics comparing the real and synthetic datasets demonstrated high similarity. Decision models generated using these datasets reported high performance metrics. There was no statistically significant difference in performance measures reported by models trained using real and synthetic datasets. Our results inform the use of GAN models to generate synthetic unstructured free-text data with limited re-identification risk, and use of this data to enable collaborative research and re-use of machine learning models.

## 465. Adversarial Sub-sequence for Text Generation

- Authors: Xingyuan Chen; Yanzhe Li; Peng Jin; Jiuhua Zhang; Xinyu Dai; Jiajun Chen; Gang Song
- Year: 2019
- DOI: 10.48550/arxiv.1905.12835
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1905.12835
- PDF: https://arxiv.org/pdf/1905.12835

Generative adversarial nets (GAN) has been successfully introduced for generating text to alleviate the exposure bias. However, discriminators in these models only evaluate the entire sequence, which causes feedback sparsity and mode collapse. To tackle these problems, we propose a novel mechanism. It first segments the entire sequence into several sub-sequences. Then these sub-sequences, together with the entire sequence, are evaluated individually by the discriminator. At last these feedback signals are all used to guide the learning of GAN. This mechanism learns the generation of both the entire sequence and the sub-sequences simultaneously. Learning to generate sub-sequences is easy and is helpful in generating an entire sequence. It is easy to improve the existing GAN-based models with this mechanism. We rebuild three previous well-designed models with our mechanism, and the experimental results on benchmark data show these models are improved significantly, the best one outperforms the state-of-the-art model.\footnote[1]{All code and data are available at https://github.com/liyzcj/seggan.git

## 466. LAG-Sizer: A Novel Gate Sizer Based on Leak Generative Adversarial Network with Feature Fusion

- Authors: Z. Zhang; Wenjie Ding; Guoqing He; Peng Cao
- Year: 2024
- DOI: 10.1145/3676536.3676799
- Venue: 
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1145/3676536.3676799
- PDF: https://dl.acm.org/doi/pdf/10.1145/3676536.3676799

Gate sizing is an NP-hard problem to achieve Performance, Power and Area (PPA) optimization. Recently proposed learning-based approaches struggle to overcome the runtime issue of traditional heuristics, but lack the consideration of the intrinsic features for candidate gates in library and could not address the inequality issue of candidate sizes for different gates properly, suffering from insufficient design space exploration and inaccurate sizing assignment. In this work, based on a variant of generative adversarial network, Leak Adversarial Generation (LAG), a novel LAG-Sizer is proposed to model gate sizing as sequence generation problem, which breaks the traditional adversarial network by leaking the discriminator feature information into the generator to guide sizing generation. Feature fusion technique is introduced to comprehensively consider circuit feature and cell library feature while a unified classification is proposed to perfectly solve the inequality issue for sizing. The proposed sizer was validated with IWLS2005 and Opencores benchmark circuits under 22nm process. Experimental results demonstrate that an average of 4.6% Total Negative Slack (TNS) improvement and 15.6% number of violating endpoints (NVE) reduction are achieved by this work with similar area and power consumption compared to commercial tools as well as significant runtime speedup of 47.8×.

## 467. Research on LeakGAN-Based Text Augmentation Technology for Transformer State Assessment

- Authors: Yang Song; Kai Chen; Xiaodong Liu; Hao Qin; Yang Lu; Hui Zhong
- Year: 2025
- DOI: 10.1109/icpet66029.2025.11160421
- Venue: 2025 7th International Conference on Power and Energy Technology (ICPET)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/icpet66029.2025.11160421

## 468. Automated Generation of Chinese Text-Image Summaries Using Deep Learning Techniques

- Authors: Meiling Xu; Hayati Abd Rahman; Feng Li
- Year: 2023
- DOI: 10.18280/ts.400644
- Venue: Traitement du signal
- Countries: CN; MY
- Source: openalex
- URL: https://doi.org/10.18280/ts.400644
- PDF: https://iieta.org/download/file/fid/117969

In the era of the internet, an abundance of Chinese text-image content is continuously produced, necessitating effective automated technologies for processing and summarizing these materials.Automated generation of Chinese text-image summaries facilitates rapid comprehension of key information, thereby enhancing the efficiency of information consumption.Due to the unique characteristics of the Chinese language, traditional automatic summarization techniques are inadequately transferable, prompting the development of text-image summary generation technologies tailored to Chinese features.Research indicates that while existing natural language processing and deep learning techniques have made strides in text summarization, deficiencies remain in the deep semantic mining and integration of text-image content.This study primarily focuses on two aspects: Firstly, a generative approach based on an enhanced MaliGAN model, employing deep learning models to improve text generation quality.Secondly, a retrieval-based approach, utilizing cross-modal similarity retrieval to extract text information most relevant to the image content, guiding summary generation.Additionally, this study innovatively proposes a model architecture comprising segmentation, cross-modal retrieval, and adaptive fusion strategy modules, significantly augmenting the accuracy and reliability of text-image summary generation.

## 469. AN UNSUPERVISED LEARNING APPROACH FOR REAL-TIME GENERATION AND DETECTION OF TEXT-BASED FAKE NEWS DETECTION

- Authors: Sarang Joshi
- Year: 2025
- DOI: 10.12732/ijam.v38i2s.79
- Venue: International Journal of Apllied Mathematics
- Countries: 
- Source: openalex
- URL: https://doi.org/10.12732/ijam.v38i2s.79
- PDF: https://ijamjournal.org/ijam/publication/index.php/ijam/article/download/79/77

The rapid spread of fake news has become a critical issue in the digital era, posing challenges to information authenticity and decision-making. This research presents a novel method for fake news detection leveraging a Generative Adversarial Network (GAN) combined with the BLEU (Bilingual Evaluation Understudy) score for evaluating textual quality. The proposed model uses a GAN framework to generate synthetic news data and trains a classifier to distinguish between genuine and fabricated articles. The BLEU score, commonly used in machine translation, is adapted to assess the accuracy of generated text against real-world news. Experimental results show the effectiveness of this approach, with detection performance categorized based on BLEU score ranges: Excellent (0.7+), Good (0.5-0.7), Average (0.3-0.5), and Poor (&lt;0.3). With a BLEU score of 0.66, the model demonstrates strong performance in distinguishing fake from real news, with potential applications in automated content moderation and misinformation detection.

## 470. Generation of Synthetic Electronic Medical Record Text

- Authors: Jiaqi Guan; Runzhe Li; Sheng Yu; Xuegong Zhang
- Year: 2018
- DOI: 10.48550/arxiv.1812.02793
- Venue: arXiv (Cornell University)
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1812.02793
- PDF: https://arxiv.org/pdf/1812.02793

Machine learning (ML) and Natural Language Processing (NLP) have achieved remarkable success in many fields and have brought new opportunities and high expectation in the analyses of medical data. The most common type of medical data is the massive free-text electronic medical records (EMR). It is widely regarded that mining such massive data can bring up important information for improving medical practices as well as for possible new discoveries on complex diseases. However, the free EMR texts are lacking consistent standards, rich of private information, and limited in availability. Also, as they are accumulated from everyday practices, it is often hard to have a balanced number of samples for the types of diseases under study. These problems hinder the development of ML and NLP methods for EMR data analysis. To tackle these problems, we developed a model to generate synthetic text of EMRs called Medical Text Generative Adversarial Network or mtGAN. It is based on the GAN framework and is trained by the REINFORCE algorithm. It takes disease features as inputs and generates synthetic texts as EMRs for the corresponding diseases. We evaluate the model from micro-level, macro-level and application-level on a Chinese EMR text dataset. The results show that the method has a good capacity to fit real data and can generate realistic and diverse EMR samples. This provides a novel way to avoid potential leakage of patient privacy while still supply sufficient well-controlled cohort data for developing downstream ML and NLP methods. It can also be used as a data augmentation method to assist studies based on real EMR data.

## 471. Unlocking the Power of GANs in Non-Autoregressive Text Generation

- Authors: Da Ren; Cai, Yi; Li, Qing
- Year: 2023
- DOI: 10.48550/arxiv.2305.03977
- Venue: arXiv (Cornell University)
- Countries: 
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.2305.03977
- PDF: https://arxiv.org/pdf/2305.03977

Generative Adversarial Networks (GANs) have been studied in text generation to tackle the exposure bias problem. Despite their remarkable development, they adopt autoregressive structures so suffering from high latency in both training and inference stages. Although GANs have potential to support efficient generation by adopting non-autoregressive (NAR) structures, their explorations in NAR models are extremely limited. In this work, we conduct pioneering study of building language GANs based on NAR structures. We identify two issues that constrain the performance of GAN-based NAR models. Firstly, existing methods of incorporating latent variables provide highly similar representations which cannot describe the diversity of different words in sentences. We tackle this problem by proposing Position-Aware Self-Modulation, providing more diverse and effective representations. Secondly, the attention mechanism in Transformer cannot accurately build word dependencies in the unstable training of GANs, and we adopt Dependency Feed Forward Network to enhance the model capacity in dependency modeling. Armed with these two facilities, we propose a GAN-based NAR model, Adversarial Non-autoregressive Transformer (ANT). The experimental results demonstrate that ANT can achieve comparable performance with mainstream models in a single forward pass and has great potential in various applications like latent interpolation and semi-supervised learning.

## 472. Learning from Few Samples: A Novel Approach for High-Quality Malcode Generation

- Authors: Haijian Ma; Daizong Liu; Xiaowen Cai; Pan Zhou; Yulai Xie
- Year: 2025
- DOI: 10.18653/v1/2025.emnlp-main.70
- Venue: 
- Countries: 
- Source: openalex
- URL: https://doi.org/10.18653/v1/2025.emnlp-main.70
- PDF: https://aclanthology.org/2025.emnlp-main.70.pdf

Intrusion Detection Systems (IDS) play a crucial role in network security defense.However, a significant challenge for IDS in training detection models is the shortage of adequately labeled malicious samples.To address these issues, this paper introduces a novel semi-supervised framework GANGRL-LLM, which integrates Generative Adversarial Networks (GANs) with Large Language Models (LLMs) to enhance malicious code generation and SQL Injection (SQLi) detection capabilities in few-sample learning scenarios.Specifically, our framework adopts a collaborative training paradigm where: (1) the GAN-based discriminator improves malicious pattern recognition through adversarial learning with generated samples and limited real samples; and (2) the LLM-based generator refines the quality of malicious code synthesis using reward signals from the discriminator.The experimental results demonstrate that even with a limited number of labeled samples, our training framework is highly effective in enhancing both malicious code generation and detection capabilities.This dual enhancement capability offers a promising solution for developing adaptive defense systems capable of countering evolving cyber threats.

## 473. Spontaneous regression of maligan breast neoplasia in a female patient with high level of immunoglobulin ig e

- Authors: Jackson Roberto de Moura
- Year: 2020
- DOI: 10.29289/259453942020v30s1063
- Venue: Mastology
- Countries: 
- Source: crossref
- URL: https://doi.org/10.29289/259453942020v30s1063

<jats:p>M.C.V., aged 54, born in Presidente Bernardes, Minas Gerais, was admitted on 09/10/2018 with a palpable alteration in the right breast, having a 15mm heterogeneous lobed nodule at the junction of the upper quadrant of the right breast (BI-RADS 5) with mammography having focal asymmetry in the same position (BI-RADS 0), being submitted to core-biopsy by ultrasound with resulting Infiltrating Ductal Carcinoma – Grade 3. Immunohistochemical pattern reveals positivity of the estrogen and progesterone hormone receptors, C-ERB B2 with a score of +2 and Ki67‒positive by 20%. Negative Fish test. She refused treatment, returning to the service on 14/08/2019 with normal physical examination, an 8 mm ultrasound lesion at the junction of the upper quadrants of the right breast (BI-RADS 6) and regression in mammography of focal asymmetry. Staging study performed with chest X-rays, total abdomen ultrasound and normal bone scintigraphy. Laboratory study was normal, except for the high level of total IgE in 4,290. She underwent segmental and sentinel lymph node resection in the right breast on 17/08/2019 at Hospital São Vicente de Paula, Ubá, Minas Gerais, with histological result, infiltrating lobular carcinoma, 9 mm in size, free margins and study of the negative sentinel lymph node. Radiotherapy and use of Tamoxifen 20mg for 5 years were indicated. It was possible to conclude that there is something different, possibly associated with the high level of IgE, which we continue to study to further understand.</jats:p>

## 474. MaskGAN: Better Text Generation via Filling in the ____

- Authors: William Fedus; Ian Goodfellow; Andrew M. Dai
- Year: 2018
- DOI: 
- Venue: arXiv (Cornell University)
- Countries: US
- Source: openalex
- URL: https://openalex.org/W2963574252
- PDF: https://arxiv.org/pdf/1801.07736.pdf

## 475. A systematic review of deep learning chemical language models in recent era

- Authors: Hector Flores-Hernandez; Emmanuel Martínez-Ledesma
- Year: 2024
- DOI: 10.1186/s13321-024-00916-y
- Venue: Journal of Cheminformatics
- Countries: MX
- Source: openalex
- URL: https://doi.org/10.1186/s13321-024-00916-y
- PDF: https://jcheminf.biomedcentral.com/counter/pdf/10.1186/s13321-024-00916-y

Discovering new chemical compounds with specific properties can provide advantages for fields that rely on materials for their development, although this task comes at a high cost in terms of complexity and resources. Since the beginning of the data age, deep learning techniques have revolutionized the process of designing molecules by analyzing and learning from representations of molecular data, greatly reducing the resources and time involved. Various deep learning approaches have been developed to date, using a variety of architectures and strategies, in order to explore the extensive and discontinuous chemical space, providing benefits for generating compounds with specific properties. In this study, we present a systematic review that offers a statistical description and comparison of the strategies utilized to generate molecules through deep learning techniques, utilizing the metrics proposed in Molecular Sets (MOSES) or Guacamol. The study included 48 articles retrieved from a query-based search of Scopus and Web of Science and 25 articles retrieved from citation search, yielding a total of 72 retrieved articles, of which 62 correspond to chemical language models approaches to molecule generation and other 10 retrieved articles correspond to molecular graph representations. Transformers, recurrent neural networks (RNNs), generative adversarial networks (GANs), Structured Space State Sequence (S4) models, and variational autoencoders (VAEs) are considered the main deep learning architectures used for molecule generation in the set of retrieved articles. In addition, transfer learning, reinforcement learning, and conditional learning are the most employed techniques for biased model generation and exploration of specific chemical space regions. Finally, this analysis focuses on the central themes of molecular representation, databases, training dataset size, validity-novelty trade-off, and performance of unbiased and biased chemical language models. These themes were selected to conduct a statistical analysis utilizing graphical representation and statistical tests. The resulting analysis reveals the main challenges, advantages, and opportunities in the field of chemical language models over the past four years.

## 476. RelGAN: Multi-Domain Image-to-Image Translation via Relative Attributes

- Authors: Po-Wei Wu; Yujing Lin; Che-Han Chang; Edward Yi Chang; Shih-Wei Liao
- Year: 2019
- DOI: 10.48550/arxiv.1908.07269
- Venue: arXiv (Cornell University)
- Countries: TW; US
- Source: openalex
- URL: https://doi.org/10.48550/arxiv.1908.07269
- PDF: https://arxiv.org/pdf/1908.07269

Multi-domain image-to-image translation has gained increasing attention recently. Previous methods take an image and some target attributes as inputs and generate an output image with the desired attributes. However, such methods have two limitations. First, these methods assume binary-valued attributes and thus cannot yield satisfactory results for fine-grained control. Second, these methods require specifying the entire set of target attributes, even if most of the attributes would not be changed. To address these limitations, we propose RelGAN, a new method for multi-domain image-to-image translation. The key idea is to use relative attributes, which describes the desired change on selected attributes. Our method is capable of modifying images by changing particular attributes of interest in a continuous manner while preserving the other attributes. Experimental results demonstrate both the quantitative and qualitative effectiveness of our method on the tasks of facial attribute transfer and interpolation.

## 477. Data-to-text generation using conditional generative adversarial with enhanced transformer

- Authors: Elham Seifossadat; Hossein Sameti
- Year: 2023
- DOI: 10.1017/s1351324923000487
- Venue: Natural Language Engineering
- Countries: IR
- Source: openalex
- URL: https://doi.org/10.1017/s1351324923000487
- PDF: https://www.cambridge.org/core/services/aop-cambridge-core/content/view/5E5A7C1272C234F77ECB4A354E6FB253/S1351324923000487a.pdf/div-class-title-data-to-text-generation-using-conditional-generative-adversarial-with-enhanced-transformer-div.pdf

Abstract In this paper, we propose an enhanced version of the vanilla transformer for data-to-text generation and then use it as the generator of a conditional generative adversarial model to improve the semantic quality and diversity of output sentences. Specifically, by adding a diagonal mask matrix to the attention scores of the encoder and using the history of the attention weights in the decoder, this enhanced version of the vanilla transformer prevents semantic defects in the output text. Also, using this enhanced transformer along with a triplet network, respectively, as the generator and discriminator of conditional generative adversarial network, diversity and semantic quality of sentences are guaranteed. To prove the effectiveness of the proposed model, called conditional generative adversarial with enhanced transformer (CGA-ET), we performed experiments on three different datasets and observed that our proposed model is able to achieve better results than the baselines models in terms of BLEU, METEOR, NIST, ROUGE-L, CIDEr, BERTScore, and SER automatic evaluation metrics as well as human evaluation.

## 478. Password Guessing Based on GAN with Gumbel-Softmax

- Authors: Tao Zhou; Hao‐Tian Wu; Hui Lu; Peiming Xu; Yiu‐ming Cheung
- Year: 2022
- DOI: 10.1155/2022/5670629
- Venue: Security and Communication Networks
- Countries: CN; HK
- Source: openalex
- URL: https://doi.org/10.1155/2022/5670629
- PDF: https://downloads.hindawi.com/journals/scn/2022/5670629.pdf

Password guessing is an important issue in user security and privacy protection. Using generative adversarial network (GAN) to guess passwords is a new strategy emerging in recent years, which exploits the discriminator’s evaluation of passwords to guide the update of the generator so that password guessing sets can be produced. However, the sampling process of discrete data from a categorical distribution is not differentiable so that backpropagation does not work well. In this paper, we propose a novel password guessing model named G-Pass, which consists of two main components. The first is a new network structure, which modifies the generator from the convolutional neural network (CNN) to long short-term memory- (LSTM-) based network and employs multiple convolutional layers in the discriminator to provide more informative signals for generator updating. The second is Gumbel-Softmax with temperature control for training GAN on passwords. Experimental results show the proposed G-Pass outperforms PassGAN in password quality and cracking rate. Moreover, by dynamically adjusting one parameter during the training process, a trade-off between sample diversity and quality can be achieved with our proposed model.

## 479. Optimizing distributions over molecular space. An Objective-Reinforced Generative Adversarial Network for Inverse-design Chemistry (ORGANIC)

- Authors: Benjamín Sánchez-Lengeling; Carlos Outeiral; Gabriel L. Guimaraes; Alán Aspuru‐Guzik
- Year: 2017
- DOI: 10.26434/chemrxiv.5309668.v3
- Venue: ChemRxiv
- Countries: US
- Source: openalex
- URL: https://doi.org/10.26434/chemrxiv.5309668.v3
- PDF: https://doi.org/10.26434/chemrxiv.5309668.v3

Molecular discovery seeks to generate chemical species tailored to very specific needs. In this paper, we present ORGANIC, a framework based on Objective-Reinforced Generative Adversarial Networks (ORGAN), capable of producing a distribution over molecular space that matches with a certain set of desirable metrics. This methodology combines two successful techniques from the machine learning community: a Generative Adversarial Network (GAN), to create non-repetitive sensible molecular species, and Reinforcement Learning (RL), to bias this generative distribution towards certain attributes. We explore several applications, from optimization of random physicochemical properties to candidates for drug discovery and organic photovoltaic material design.

## 480. Optimizing distributions over molecular space. An Objective-Reinforced Generative Adversarial Network for Inverse-design Chemistry (ORGANIC)

- Authors: Benjamín Sánchez-Lengeling; Carlos Outeiral; Gabriel L. Guimaraes; Alán Aspuru‐Guzik
- Year: 2017
- DOI: 10.26434/chemrxiv.5309668.v2
- Venue: ChemRxiv
- Countries: US
- Source: openalex
- URL: https://doi.org/10.26434/chemrxiv.5309668.v2
- PDF: https://doi.org/10.26434/chemrxiv.5309668.v2

Molecular discovery seeks to generate chemical species tailored to very specific needs. In this paper, we present ORGANIC, a framework based on Objective-Reinforced Generative Adversarial Networks (ORGAN), capable of producing a distribution over molecular space that matches with a certain set of desirable metrics. This methodology combines two successful techniques from the machine learning community: a Generative Adversarial Network (GAN), to create non-repetitive sensible molecular species, and Reinforcement Learning (RL), to bias this generative distribution towards certain attributes. We explore several applications, from optimization of random physicochemical properties to candidates for drug discovery and organic photovoltaic material design.

## 481. Optimizing distributions over molecular space. An Objective-Reinforced Generative Adversarial Network for Inverse-design Chemistry (ORGANIC)

- Authors: Benjamín Sánchez-Lengeling; Carlos Outeiral; Gabriel L. Guimaraes; Alán Aspuru‐Guzik
- Year: 2017
- DOI: 10.26434/chemrxiv.5309668
- Venue: ChemRxiv
- Countries: US
- Source: openalex
- URL: https://doi.org/10.26434/chemrxiv.5309668
- PDF: https://chemrxiv.org/articles/ORGANIC_1_pdf/5309668/files/9117841.pdf

Molecular discovery seeks to generate chemical species tailored to very specific needs. In this paper, we present ORGANIC, a framework based on Objective-Reinforced Generative Adversarial Networks (ORGAN), capable of producing a distribution over molecular space that matches with a certain set of desirable metrics. This methodology combines two successful techniques from the machine learning community: a Generative Adversarial Network (GAN), to create non-repetitive sensible molecular species, and Reinforcement Learning (RL), to bias this generative distribution towards certain attributes. We explore several applications, from optimization of random physicochemical properties to candidates for drug discovery and organic photovoltaic material design.

## 482. Benchmarking Study of Deep Generative Models for Inverse Polymer Design

- Authors: Tianle Yue; Lei Tao; Vikas Varshney; Ying Li
- Year: 2024
- DOI: 10.26434/chemrxiv-2024-gzq4r
- Venue: ChemRxiv
- Countries: US
- Source: openalex
- URL: https://doi.org/10.26434/chemrxiv-2024-gzq4r
- PDF: https://chemrxiv.org/engage/api-gateway/chemrxiv/assets/orp/resource/item/65f4c34066c138172914029c/original/benchmarking-study-of-deep-generative-models-for-inverse-polymer-design.pdf

Molecular generative models based on deep learning have increasingly gained attention for their ability in de novo polymer design. However, there remains a knowledge gap in the thorough evaluation of these models. This benchmark study explores de novo polymer design using six popular deep generative models: Variational Autoencoder (VAE), Adversarial Autoencoder (AAE), Objective-Reinforced Generative Adversarial Networks (ORGAN), Character-level Recurrent Neural Network (CharRNN), REINVENT, and GraphINVENT. Various metrics highlighted the excellent performance of CharRNN, REINVENT, and GraphINVENT, particularly when applied to the real polymer dataset, while VAE and AAE show more advantages in generating hypothetical polymers. The CharRNN, REINVENT, and GraphINVENT models were further trained on real polymers utilizing reinforcement learning methods, targeting the generation of hypothetical polymers with high glass transition temperatures. The findings of this study provide critical insights into the capabilities and limitations of each generative model, offering valuable guidance for future endeavors in polymer design and discovery.

## 483. ORGANIC (1).pdf

- Authors: Benjamín Sánchez-Lengeling; Carlos Outeiral; Gabriel L. Guimaraes; Alán Aspuru‐Guzik
- Year: 2017
- DOI: 10.26434/chemrxiv.5309668.v1
- Venue: ChemRxiv
- Countries: US
- Source: openalex
- URL: https://doi.org/10.26434/chemrxiv.5309668.v1
- PDF: https://chemrxiv.org/articles/ORGANIC_1_pdf/5309668/files/9100894.pdf

Molecular discovery seeks to generate chemical species tailored to very specific needs. In this paper, we present ORGANIC, a framework based on Objective-Reinforced Generative Adversarial Networks (ORGAN), capable of producing a distribution over molecular space that matches with a certain set of desirable metrics. This methodology combines two successful techniques from the machine learning community: a Generative Adversarial Network (GAN), to create non-repetitive sensible molecular species, and Reinforcement Learning (RL), to bias this generative distribution towards certain attributes. We explore several applications, from optimization of random physicochemical properties to candidates for drug discovery and organic photovoltaic material design.

## 484. Transformer-based Objective-reinforced Generative Adversarial Network to Generate Desired Molecules

- Authors: Chen Li; Chikashige Yamanaka; Kazuma Kaitoh; Yoshihiro Yamanishi
- Year: 2022
- DOI: 10.24963/ijcai.2022/539
- Venue: Proceedings of the Thirty-First International Joint Conference on Artificial Intelligence
- Countries: 
- Source: crossref
- URL: https://doi.org/10.24963/ijcai.2022/539

<jats:p>Deep generative models of sequence-structure data have attracted widespread attention in drug discovery. However, such models cannot fully extract the semantic features of molecules from sequential representations. Moreover, mode collapse reduces the diversity of the generated molecules. This paper proposes a transformer-based objective-reinforced generative adversarial network (TransORGAN) to generate molecules. TransORGAN leverages a transformer architecture as a generator and uses a stochastic policy gradient for reinforcement learning to generate plausible molecules with rich semantic features. The discriminator grants rewards that guide the policy update of the generator, while an objective-reinforced penalty encourages the generation of diverse molecules. Experiments were performed using the ZINC chemical dataset, and the results demonstrated the usefulness of TransORGAN in terms of uniqueness, novelty, and diversity of the generated molecules.</jats:p>

## 485. ECG Generation With Sequence Generative Adversarial Nets Optimized by Policy Gradient

- Authors: Fei Ye; Fei Zhu; Yuchen Fu; Bairong Shen
- Year: 2019
- DOI: 10.1109/access.2019.2950383
- Venue: IEEE Access
- Countries: CN
- Source: openalex
- URL: https://doi.org/10.1109/access.2019.2950383
- PDF: https://ieeexplore.ieee.org/ielx7/6287639/8600701/08887504.pdf

Electrocardiogram (ECG) is a method used by physicians to detect cardiac disease. Requirements for batch processing and accurate recognition of clinical data have led to the applications of deep-learning methods for feature extraction, classification, and denoising of ECGs; however, deep learning requires large amounts of data and multi-feature integration of datasets, with most available methods used for ECGs incapable of extracting global features or resulting in unstable, low quality training. To address these deficiencies, we proposed a novel generative adversarial architecture called RPSeqGAN using a training process reliant upon a sequence generative adversarial network (SeqGAN) algorithm that adopts the policy gradient (PG) in reinforcement learning. Based on clinical records collected from the MIT-BIH arrhythmia database, we compared our proposed model with three deep generative models to evaluate its stability by observing the variance of their loss curves. Additionally, we generated ECGs with five periods and evaluated them according to six metrics suitable for time series. The results indicate that the proposed model showed the highest stability and data quality.

## 486. Linguistic Descriptions of Human Motion with Generative Adversarial Seq2Seq Learning

- Authors: Yusuke Goutsu; Tetsunari Inamura
- Year: 2021
- DOI: 10.1109/icra48506.2021.9561519
- Venue: 
- Countries: JP
- Source: openalex
- URL: https://doi.org/10.1109/icra48506.2021.9561519

In this paper, we propose a generative model that learns a sequence-to-sequence (Seq2Seq) translation between human whole-body motions and linguistic descriptions by natural language. Our model merges the Seq2Seq model with the training strategy of sequence generative adversarial nets (SeqGAN), which extends a GAN framework to solve the problem that the gradient cannot pass back to the generator network. This model considers a generator, trained using a policy gradient method, as a stochastic parameterized policy. In the policy gradient, we employ a Monte Carlo (MC) search to receive the final reinforcement learning (RL) reward from the discriminator. The proposed generative network is trained on the KIT Motion-Language Dataset, which is one of the few large-scale datasets available and includes 3,911 human motions and 6,278 natural language descriptions. During the experiments, we evaluated the effectiveness of our model by comparing its various configurations and parameter settings. Finally, our model achieves a remarkably high performance, outperforming an existing state-of-the-art method under the same dataset split for fair comparison. In addition, the qualitative results of the motion-to-language translation demonstrate that our model can generate semantically and grammatically correct sentences with detailed linguistic descriptions from human motions.

## 487. Categorical EHR Imputation with Generative Adversarial Nets

- Authors: Yinchong Yang; Zhiliang Wu; Volker Tresp; Peter A. Fasching
- Year: 2019
- DOI: 10.1109/ichi.2019.8904717
- Venue: 2019 IEEE International Conference on Healthcare Informatics (ICHI)
- Countries: 
- Source: crossref
- URL: https://doi.org/10.1109/ichi.2019.8904717

