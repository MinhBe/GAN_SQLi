
# RbSQLi-Dataset: Rule-based SQL Injection Dataset

## 📋 Overview

**RbSQLi-Dataset** is a comprehensive machine learning project focused on **SQL Injection (SQLi) detection and classification**. This repository contains algorithms and datasets for identifying multiple types of SQL injection attacks using various machine learning models.

The project implements both **binary classification** (malicious vs. non-malicious) and **multiclass classification** (identifying specific types of SQL injection attacks) using state-of-the-art machine learning techniques.

## 🎯 What is SQL Injection?

SQL Injection is a cyber attack where malicious SQL code is inserted into application queries, potentially allowing attackers to:
- Access unauthorized data
- Modify or delete database information  
- Execute administrative operations on the database
- In some cases, access the operating system

This project helps identify and classify these attacks automatically using machine learning.

## 🚀 Key Features

- **Multiple SQL Injection Types**: Detects 6 different types of SQL injection attacks
- **Dual Classification Modes**: Both binary and multiclass classification
- **Multiple ML Algorithms**: Implements 5 different machine learning models
- **Cross-Validation**: Robust model evaluation using cross-validation
- **Comprehensive Analysis**: Detailed exploratory data analysis (EDA)
- **Professional Implementation**: Ready-to-use Jupyter notebooks for research and production

## 📁 Repository Structure

```
RbSQLi-Dataset/
│
├── 📊 EDA/
│   └── Total_Appearance_of_SQL_Keywords.ipynb    # Exploratory Data Analysis
│
├── 🧠 Model Train/
│   ├── Stratified_Model_Train.ipynb              # Multiclass model training
│   └── model_comparison_nb_rf_knn_lr.ipynb       # Model performance comparison
│
└── ✅ cross_validation_binary_sql_injection/
    ├── cross_validation_nv_rf_svc_dataset_01.ipynb  # Binary classification CV
    ├── cross_validation_nv_rf_svc_dataset_02.ipynb  # Binary classification CV  
    └── cross_validation_nv_rf_svc_dataset_03.ipynb  # Binary classification CV
```

## 🔍 SQL Injection Types Detected

The system can identify **7 different types** of SQL injection attacks:

### 1. **Error-Based SQL Injection**
- Exploits database error messages to extract information
- Forces the database to output error messages containing sensitive data

### 2. **Time-Based SQL Injection**
- Uses database delay functions (like `SLEEP()`, `WAITFOR`) 
- Infers data based on response time delays

### 3. **Union-Based SQL Injection**
- Uses UNION SQL operator to combine results from multiple SELECT statements
- Extracts data from different database tables

### 4. **Boolean-Based SQL Injection**
- Uses TRUE/FALSE conditions to infer database information
- Analyzes application responses to determine data validity

### 5. **Stack Queries-Based SQL Injection**
- Executes multiple SQL statements in a single query
- Uses semicolons to separate multiple SQL commands

### 6. **Meta-Based SQL Injection**
- Exploits database metadata and system information
- Targets database schema and configuration data

### 7. **None_Type (Normal Queries)**
- Legitimate, non-malicious SQL queries
- Used as the "safe" class in classification

## 🤖 Machine Learning Models Implemented

The project implements and compares **5 different ML algorithms**:

| Model | Type | Best Accuracy | Key Features |
|-------|------|---------------|-------------|
| **SVM (Support Vector Classifier)** | Linear/Non-linear | 86.80% | Best overall performance, robust to overfitting |
| **Logistic Regression** | Linear | 85.00% | Fast training, interpretable results |
| **K-Nearest Neighbors (KNN)** | Instance-based | 84.43% | Simple, effective for similar patterns |
| **Naive Bayes** | Probabilistic | 79.33% | Fast, works well with text features |
| **Random Forest** | Ensemble | 77.37% | Good for feature importance analysis |

## 📂 Directory Breakdown

### 🔎 `/EDA` - Exploratory Data Analysis
**What it does:** Analyzes the dataset to understand SQL injection patterns and keyword frequencies.

**Key outputs:**
- SQL keyword frequency analysis
- Dataset distribution statistics
- Pattern recognition in malicious queries

### 🎓 `/Model Train` - Model Training & Comparison
**What it does:** Trains multiple machine learning models for SQL injection detection.

**Files:**
- **`Stratified_Model_Train.ipynb`**: Implements stratified sampling for balanced multiclass training (70%-10%-20% split)
- **`model_comparison_nb_rf_knn_lr.ipynb`**: Compares 5 different ML models with detailed performance metrics

**Key features:**
- Balanced dataset sampling
- TF-IDF vectorization with 50,000 features
- Comprehensive model evaluation

### ✅ `/cross_validation_binary_sql_injection` - Binary Classification
**What it does:** Performs cross-validation for binary classification (malicious vs. non-malicious).

**Files:**
- **Dataset 01**: Training on RbSQLi dataset, testing on external SQL injection dataset
- **Dataset 02**: Cross-dataset validation for generalization testing
- **Dataset 03**: Additional validation on different dataset splits

**Key features:**
- 5-fold cross-validation
- External dataset validation
- Balanced sampling (9,000 malicious + 9,000 normal for training)

## 🔧 Technical Implementation

### Data Processing Pipeline
1. **Data Loading**: Handles CSV datasets with SQL queries and labels
2. **Text Preprocessing**: Cleans and normalizes SQL query strings
3. **Feature Extraction**: Uses TF-IDF vectorization (1-2 n-grams, 50k features)
4. **Stratified Sampling**: Maintains class distribution across train/validation/test splits
5. **Model Training**: Implements multiple ML algorithms with hyperparameter tuning
6. **Evaluation**: Comprehensive metrics including accuracy, precision, recall, F1-score, AUC-ROC

### Dataset Specifications
- **Training Dataset**: 18,000 samples (balanced)
- **Validation Dataset**: ~10% of total data
- **Test Dataset**: ~20% of total data
- **Feature Engineering**: TF-IDF with 50,000 max features, 1-2 n-grams
- **Cross-Validation**: 5-fold stratified cross-validation

## 📊 Performance Results

### Multiclass Classification Results:
```
Model Performance Summary:
┌─────────────────────┬──────────────┬─────────────┬──────────────┐
│ Model               │ Accuracy     │ AUC-ROC     │ mAP Score    │
├─────────────────────┼──────────────┼─────────────┼──────────────┤
│ SVM                 │ 86.80%       │ 0.9843      │ 0.9113       │
│ Logistic Regression │ 85.00%       │ 0.9756      │ 0.8956       │
│ KNN                 │ 84.43%       │ 0.9689      │ 0.8789       │
│ Naive Bayes         │ 79.33%       │ 0.9234      │ 0.8234       │
│ Random Forest       │ 77.37%       │ 0.9123      │ 0.7998       │
└─────────────────────┴──────────────┴─────────────┴──────────────┘
```

### Binary Classification Results:
- **Training Dataset**: 18,000 samples (9k malicious + 9k normal)  
- **Test Dataset**: 2,000 samples (1k malicious + 1k normal)
- **Best Model**: Random Forest with optimized hyperparameters
- **Cross-Validation**: 5-fold CV for robust evaluation

## 🛠️ Getting Started

### Prerequisites
```python
# Required libraries
pandas
scikit-learn  
numpy
matplotlib
seaborn
jupyter
```

### Quick Start
1. **Clone the repository:**
   ```bash
   git clone https://github.com/RbSQLi-Dataset/RbSQLi-Dataset.git
   cd RbSQLi-Dataset
   ```

2. **Install dependencies:**
   ```bash
   pip install pandas scikit-learn numpy matplotlib seaborn jupyter
   ```

3. **Run the notebooks:**
   - Start with `/EDA/Total_Appearance_of_SQL_Keywords.ipynb` for data exploration
   - Use `/Model Train/Stratified_Model_Train.ipynb` for multiclass classification
   - Try `/cross_validation_binary_sql_injection/` for binary classification

### Dataset Setup
The notebooks are configured to work with:
- **Primary Dataset**: `sql_injectiondataset_final_updated.csv` (RbSQLi dataset)
- **External Dataset**: Various SQL injection datasets from Kaggle
- **Format**: CSV files with columns for SQL queries and labels

## 📈 Use Cases

### For Researchers
- **Academic Research**: Study SQL injection patterns and detection methods
- **Comparative Analysis**: Benchmark different ML models on SQL injection detection
- **Feature Engineering**: Analyze which SQL keywords are most indicative of attacks

### For Security Professionals
- **Web Application Security**: Integrate models into web application firewalls
- **Database Security**: Monitor database queries for suspicious patterns  
- **Incident Response**: Classify and prioritize SQL injection attempts

### For Developers
- **Code Security**: Validate SQL queries in applications
- **Security Testing**: Test applications against various SQL injection types
- **Educational**: Learn about SQL injection patterns and detection

## 🎓 Educational Value

This project is perfect for:
- **Students** learning about cybersecurity and machine learning
- **Researchers** studying SQL injection detection techniques  
- **Developers** wanting to understand SQL injection vulnerabilities
- **Security professionals** looking for automated detection methods

## 📄 Model Architecture Details

### Feature Engineering
- **TF-IDF Vectorization**: Converts SQL queries to numerical features
- **N-grams**: Uses 1-2 word combinations for better context understanding
- **Max Features**: 50,000 most important features selected
- **Normalization**: L2 normalization for consistent scaling

### Training Strategy  
- **Stratified Sampling**: Maintains original class distribution
- **Train/Validation/Test Split**: 70%/10%/20% ratio
- **Cross-Validation**: 5-fold stratified CV for model selection
- **Hyperparameter Tuning**: Grid search for optimal parameters

## 🔬 Research Applications

This dataset and methodology can be used for:
- **Cybersecurity Research**: Understanding SQL injection attack patterns
- **Machine Learning Studies**: Comparing text classification algorithms
- **Security Tool Development**: Building automated detection systems
- **Academic Projects**: Teaching cybersecurity and ML concepts

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional SQL injection types
- More sophisticated feature engineering
- Deep learning implementations  
- Real-time detection capabilities
- Web interface for easy usage

## 📞 Contact & Support

For questions, suggestions, or collaborations regarding this SQL injection detection project, please:
- Open an issue on GitHub
- Fork the repository for contributions
- Share your research findings using this dataset

---

**🛡️ Protecting databases through intelligent SQL injection detection using machine learning.**

*This project demonstrates the power of combining cybersecurity knowledge with machine learning techniques to create effective defense mechanisms against SQL injection attacks.*
