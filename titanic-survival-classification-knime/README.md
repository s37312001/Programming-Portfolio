# Titanic Survival Classification with KNIME

A supervised machine learning classification project developed in **KNIME Analytics Platform** to predict Titanic passenger survival and compare the generalization performance of **Naïve Bayes** and **Decision Tree** models.

This project was completed as individual coursework during my **MSc Data Science at the University of Sheffield**. The focus was not only on model accuracy, but also on the complete machine learning lifecycle: **data preparation, feature engineering, feature selection, class balancing, cross-validation, model configuration, model comparison, holdout testing, and ROC-based evaluation**.

---

## Machine Learning Problem

The task is formulated as a **supervised binary classification problem**.

- **Input:** passenger demographic, family, ticket, and socioeconomic attributes
- **Target:** `Survived`
- **Target classes:** survived / did not survive
- **Dataset size:** 1,204 records after joining the personal and ticket datasets
- **Candidate algorithms:** Naïve Bayes and Decision Tree
- **Primary model-selection metric:** classification accuracy
- **Final evaluation:** unseen holdout test set and ROC curve

The central question was:

> Which combination of algorithm, feature representation, feature subset, and model configuration gives the strongest predictive performance while maintaining reasonable generalization to unseen data?

---

## End-to-End ML Pipeline

The KNIME workflow implements the following modelling pipeline:

```text
Data Ingestion
    ↓
Dataset Join
    ↓
Data Cleaning
    ↓
Train/Test Partition (80/20)
    ↓
Feature Engineering & Missing-Value Handling
    ↓
Feature Screening / Selection
    ↓
Cross-Validation
    ↓
Model Training
    ├── Naïve Bayes
    └── Decision Tree
    ↓
Model Configuration Comparison
    ↓
Best Model Selection
    ↓
Prediction on Unseen Test Data
    ↓
Accuracy / ROC Evaluation
```

This structure separates **model development** from **final holdout evaluation**, reducing the risk of selecting a model based on information from the test set.

---

## 1. Data Preparation

The original analysis combined two Titanic data sources:

- personal data
- ticket data

The tables were joined into a single modelling dataset containing **1,204 passenger records**.

### Removing non-predictive identifiers

Attributes such as passenger IDs, names, and ticket identifiers were removed because they primarily identify individual observations rather than represent reusable predictive patterns.

`Cabin` was also excluded because of substantial missingness.

This step reduces unnecessary dimensionality and avoids allowing identifier-like variables to influence the classifier without meaningful generalizable information.

### Missing-value handling

Missing values were handled before model training.

Examples include:

- missing `Embarked` / `Fare` observations handled during preprocessing
- missing `Age` values replaced with the mean in the Naïve Bayes branch

For `Age`, mean imputation preserved the approximate central tendency of the available observations while allowing the records to remain usable by the classifier.

---

## 2. Holdout Strategy and Data Leakage Control

The workflow uses an **80/20 train-test partition**.

The training portion is used for:

- feature preparation
- feature comparison
- cross-validation
- model configuration
- model selection

The test portion is retained as **unseen data** for the final prediction stage.

This distinction is important because evaluating many candidate configurations directly against the test set would introduce **test-set leakage** into the model-selection process. The holdout set should represent data that did not influence the choice of the final model.

---

## 3. Feature Engineering

The two algorithms have different requirements and inductive biases, so preprocessing was adapted to each model rather than forcing both models through an identical transformation pipeline.

### Naïve Bayes preprocessing

Selected variables were transformed into categorical representations using **KNIME Rule Engine** nodes.

For example, `Age` was converted from a continuous variable into discrete categories.

This is a form of **discretization (binning)**:

> continuous values → categorical intervals

Discretization can simplify the representation of continuous variables for a categorical probabilistic model, although the chosen bin boundaries can also affect the information retained by the model.

Other attributes such as `Sex`, `Embarked`, `Salary`, and `Fare` were also transformed into representations suitable for the Naïve Bayes workflow.

### Decision Tree preprocessing

Decision Trees do not require feature scaling because split decisions depend on ordering or categorical partitions rather than Euclidean distance or gradient magnitude.

As a result, the Decision Tree branch required less feature transformation than the Naïve Bayes branch.

This illustrates an important machine learning principle:

> **Preprocessing should reflect the assumptions and requirements of the selected algorithm.**

---

## 4. Feature Selection

Feature selection was explicitly evaluated in the Naïve Bayes experiments.

A series of **Crosstab** analyses was used to examine the relationship between individual candidate predictors and the `Survived` target.

Based on these associations, different feature subsets were tested rather than assuming that adding every available predictor would improve the model.

Three Naïve Bayes configurations were evaluated:

1. selected features: `Sex`, `Salary`, `Fare`
2. all candidate features except `Age`
3. all available modelling features

The strongest Naïve Bayes configuration used only:

- `Sex`
- `Salary`
- `Fare`

This result demonstrates that **more features do not automatically produce a better classifier**. Additional variables can introduce weak, redundant, or noisy information that does not improve out-of-sample prediction.

---

## 5. Naïve Bayes Model

Naïve Bayes is a **probabilistic classifier** based on Bayes' theorem.

Conceptually, the classifier estimates the posterior probability of each target class:

```text
P(Class | Features) ∝ P(Class) × P(Features | Class)
```

The "naïve" assumption treats predictors as **conditionally independent given the target class**.

Although this assumption is often simplified compared with real-world relationships between variables, Naïve Bayes can still perform effectively on relatively small classification datasets because it estimates comparatively few parameters and is computationally efficient.

### Why Naïve Bayes was appropriate here

- binary classification target
- relatively small dataset
- categorical feature representations
- fast model training
- interpretable comparison between feature subsets

### Naïve Bayes tuning strategy

The main tuning dimension in this project was **feature-subset selection** rather than optimization of a large hyperparameter space.

Three candidate feature sets were evaluated under cross-validation to determine whether reducing the input dimensionality improved predictive accuracy.

This is a form of **model selection through feature-space tuning**.

---

## 6. Decision Tree Model

A Decision Tree is a **non-parametric supervised learning algorithm** that recursively partitions the feature space into increasingly homogeneous groups.

At each split, the model chooses a feature and decision rule that separates observations according to the target.

Conceptually:

```text
Root Node
   ↓
Feature Split
   ├── Branch A
   │      ↓
   │   Further Split
   │
   └── Branch B
          ↓
       Leaf / Prediction
```

Decision Trees are attractive because they:

- handle nonlinear decision boundaries
- naturally represent interactions between variables
- require little feature scaling
- provide an interpretable rule-based structure

However, an unrestricted tree can continue splitting until it learns patterns that are specific to the training sample, creating **high variance and overfitting**.

---

## 7. Decision Tree Regularization and Pruning

Two Decision Tree configurations were compared:

- **MDL pruning enabled**
- **pruning disabled**

The workflow also used a **minimum number of records per node = 6** as a stopping condition.

### Why pruning matters

Tree growth involves a trade-off between:

- **model complexity**
- **training fit**
- **generalization**

A very deep tree can have low training error but poor performance on new observations.

**Pruning** removes branches whose additional complexity does not provide enough predictive value.

The MDL configuration applies the principle of **Minimum Description Length**: prefer a model that explains the data well without unnecessary structural complexity.

In this experiment, the pruned Decision Tree achieved substantially better validation accuracy than the unpruned tree, supporting the use of regularization to control overfitting.

---

## 8. Class Balancing

The Decision Tree workflow uses **Equal Size Sampling** to create a more balanced representation of the two `Survived` classes during model development.

Class imbalance can cause a classifier to favour the majority class because predicting the dominant class can produce deceptively high overall accuracy.

Balancing the classes helps the learner receive a more comparable representation of both outcomes and makes model evaluation less dominated by the majority class.

This is particularly relevant when the objective is to distinguish both positive and negative outcomes rather than simply maximise majority-class predictions.

---

## 9. Cross-Validation

Model comparison was performed using KNIME's:

- `X-Partitioner`
- `X-Aggregator`

These nodes implement a **cross-validation loop**.

Cross-validation repeatedly separates the training data into internal training and validation folds:

```text
Training Data
     ↓
Multiple Train / Validation Splits
     ↓
Train Model on Fold Subsets
     ↓
Predict Validation Fold
     ↓
Aggregate Validation Performance
```

The purpose is to estimate how consistently a model performs on data that was not used to fit that particular fold.

This provides a stronger basis for model selection than evaluating a candidate model only on the same observations used for training.

Importantly, cross-validation was used for **model development**, while the separate 20% holdout set remained reserved for the final evaluation.

---

## 10. Model Selection and Tuning Strategy

Five configurations were compared.

The tuning process focused on two different sources of model complexity:

### Naïve Bayes
**Feature-space tuning**

- selected feature subset
- feature exclusion
- all-feature configuration

### Decision Tree
**Structural regularization**

- MDL pruning
- no pruning
- minimum-record stopping condition

This means the project did not treat "model tuning" as a single parameter change. Instead, the workflow examined how both **input representation** and **model complexity** affect generalization performance.

---

## Model Comparison

| Rank | Model / Configuration | Cross-Validation Accuracy |
|---:|---|---:|
| 1 | **Naïve Bayes — Sex, Salary, Fare** | **86.458%** |
| 2 | Decision Tree — MDL pruning | **85.417%** |
| 3 | Naïve Bayes — without Age | **85.208%** |
| 4 | Naïve Bayes — all features | **84.792%** |
| 5 | Decision Tree — without pruning | **82.222%** |

### Interpretation

Several modelling insights can be drawn from this comparison.

**1. Feature selection improved Naïve Bayes performance.**  
The three-feature model outperformed both larger Naïve Bayes feature sets. This suggests that additional predictors did not necessarily contribute useful conditional information for this classifier.

**2. Pruning improved Decision Tree generalization.**  
The MDL-pruned tree achieved **85.417%**, compared with **82.222%** without pruning. This is consistent with the role of pruning as a regularization mechanism.

**3. Algorithm choice alone was not sufficient.**  
Performance depended on the interaction between the algorithm, preprocessing strategy, feature subset, and regularization settings.

The best configuration was therefore selected based on its cross-validation performance rather than choosing an algorithm purely from theory.

---

## 11. Final Model and Holdout Prediction

The final selected model was:

> **Naïve Bayes using `Sex`, `Salary`, and `Fare`**

Performance:

| Evaluation Stage | Accuracy |
|---|---:|
| Cross-validation | **86.458%** |
| Unseen holdout test set | **82.988%** |

The reduction from cross-validation performance to holdout performance is expected when moving from model development to genuinely unseen observations.

More importantly, the test performance remained reasonably close to the validation result, providing evidence that the selected model retained predictive capability outside the data used for model selection.

This final stage represents the distinction between:

- **validation performance** — used to choose the model
- **test performance** — used to estimate final generalization

---

## 12. ROC-Based Evaluation

The final workflow also includes a **ROC Curve** node.

A Receiver Operating Characteristic (ROC) curve evaluates a binary classifier across different classification thresholds by comparing:

- **True Positive Rate (Sensitivity / Recall)**
- **False Positive Rate**

Unlike a single accuracy value, ROC analysis examines how the model behaves as the decision threshold changes.

This is useful because a binary classifier produces class probabilities or scores, while the final class assignment depends on the threshold used to convert that score into a prediction.

The original project used the ROC curve as a visual check that the selected classifier performed better than random discrimination.

> The report does not provide a numerical AUC value, so this repository does not claim one.

---

## 13. Generalization and Overfitting

A central theme of this project was controlling **overfitting**.

Three mechanisms were used:

### Cross-validation
Evaluates candidate models repeatedly on validation folds that are excluded from individual training folds.

### Decision Tree pruning
Reduces unnecessary tree complexity and controls variance.

### Independent holdout testing
Evaluates the selected model using data that did not participate in model selection.

Together, these steps form a basic but important model-development discipline:

```text
Fit → Validate → Tune / Compare → Select → Test
```

rather than:

```text
Fit → Test repeatedly → choose the best test result
```

The latter would contaminate the test set and lead to an overly optimistic estimate of generalization performance.

---

## 14. Bias–Variance Perspective

The comparison between Naïve Bayes and Decision Tree also reflects different **inductive biases**.

### Naïve Bayes
Uses a strong conditional-independence assumption.

- relatively simple model
- low computational cost
- lower tendency to fit highly complex interactions
- can introduce bias if predictors are strongly dependent

### Decision Tree
Can represent nonlinear rules and feature interactions.

- highly flexible
- easy to interpret
- low bias when grown deeply
- potentially high variance without stopping rules or pruning

The superior performance of the pruned tree relative to the unpruned tree illustrates the practical **bias–variance trade-off**: slightly restricting model flexibility can improve prediction on unseen data.

---

## 15. What This Project Demonstrates

This project demonstrates practical understanding of the following machine learning concepts:

| Concept | Application in This Project |
|---|---|
| **Supervised Learning** | Predicting the known binary target `Survived` |
| **Binary Classification** | Two target outcomes: survived / not survived |
| **Feature Engineering** | Transforming variables using Rule Engine nodes |
| **Discretization** | Converting continuous attributes such as Age into categories |
| **Missing-Value Imputation** | Replacing missing Age values with the mean |
| **Feature Selection** | Comparing predictor subsets for Naïve Bayes |
| **Class Balancing** | Equal Size Sampling for the Decision Tree workflow |
| **Cross-Validation** | X-Partitioner / X-Aggregator model validation |
| **Model Selection** | Comparing five candidate configurations |
| **Hyperparameter / Configuration Tuning** | MDL pruning and minimum-record stopping criteria |
| **Regularization** | Controlling Decision Tree complexity through pruning |
| **Overfitting Control** | Cross-validation, pruning, and holdout testing |
| **Holdout Evaluation** | Final prediction on the unseen 20% test data |
| **Generalization** | Comparing validation performance with unseen test performance |
| **ROC Analysis** | Evaluating discrimination across classification thresholds |
| **Bias–Variance Trade-off** | Comparing simpler probabilistic and flexible tree-based models |

---

## KNIME Components Used

The workflow includes nodes such as:

- File Reader
- Joiner
- Column Filter
- RowID
- Missing Value
- Rule Engine
- Crosstab
- Statistics
- Partitioning
- Equal Size Sampling
- X-Partitioner
- X-Aggregator
- Naïve Bayes Learner
- Naïve Bayes Predictor
- Decision Tree Learner
- Decision Tree Predictor
- Scorer
- ROC Curve

These components form an end-to-end visual machine learning workflow covering preprocessing, training, validation, prediction, and evaluation.

---

## Repository Structure

```text
titanic-survival-classification-knime/
│
├── README.md
│
├── workflow/
│   └── Titanic_Survival_Classification.html
│
└── report/
    └── titanic-survival-classification-knime.pdf
```

---

## Project Files

### KNIME Workflow

[View the exported KNIME workflow](workflow/itanic_Survival_Classification.svg)

The exported workflow shows the complete KNIME pipeline, including preprocessing branches, cross-validation loops, candidate models, scorers, and final holdout prediction.

### Full Report

[View the full data mining report](report/titanic-survival-classification-knime.pdf)

The report contains the original research background, data preparation, experimental setup, model comparisons, results, discussion, conclusion, and references.

---

## Academic Context

This project was completed in **2022** as individual coursework for the **MSc Data Science** programme at the **University of Sheffield**.

The repository preserves the original KNIME modelling approach while presenting the project from a modern machine learning workflow perspective.
