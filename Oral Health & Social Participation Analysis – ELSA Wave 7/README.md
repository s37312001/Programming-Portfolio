# Oral Health & Social Participation Analysis

An individual statistical analysis project completed during my MSc in Data Science at the University of Sheffield.

## Project Overview

This project examines the association between self-rated dental health and social participation among older adults in the UK using data from the **English Longitudinal Study of Ageing (ELSA) Wave 7**.

The analysis covered **9,666 participants** and explored demographic, oral-health, and social-participation variables using descriptive and inferential statistical methods.

## Research Objectives

The project focused on three objectives:

1. Assess the relationship between dental health conditions and removable dentures.
2. Examine whether dental health conditions are associated with demographic factors.
3. Explore the relationship between dental health conditions and social participation.

## Dataset

**Source:** English Longitudinal Study of Ageing (ELSA), Wave 7  
**Participants:** 9,666

The selected variables included:

### Demographic
- Age range
- Gender

### Oral Health
- Denture use
- Eating-out frequency

### Social Participation
- Connection with society / current events
- Internet use
- Living with a partner

### Outcome Variable
- Self-rated dental health condition

For logistic regression, the dental-health outcome was additionally recoded into a binary variable.

> The raw ELSA dataset is not included in this repository.

## Statistical Methods

The analysis included:

- Descriptive statistics
- Frequency analysis
- Cross-tabulation
- Chi-square Linear-by-Linear Association
- Spearman Rank Correlation
- Binary Logistic Regression
- Missing-value assessment
- Variable recoding

The original analysis was conducted using **SPSS**.

## Analysis

### 1. Denture Use and Dental Health

**Research question:**  
Is denture use associated with self-rated dental health?

**Method:** Chi-square Linear-by-Linear Association

**Result:**  
A statistically significant association was identified between denture use and self-rated dental health (**p < 0.001**).

Participants who reported poorer dental health were more likely to report denture use, while those reporting excellent dental health were more likely not to use dentures.

---

### 2. Eating-Out Frequency and Dental Health

**Research question:**  
Is eating-out frequency correlated with self-rated dental health?

**Method:** Spearman Rank Correlation

**Result:**

- Spearman's rho = **0.110**
- p < **0.001**

The result indicates a statistically significant but weak positive association between eating-out frequency and self-rated dental health.

---

### 3. Age and Dental Health

**Research question:**  
Is age associated with self-rated dental health, and does the relationship differ by gender?

**Method:** Spearman Rank Correlation, analysed separately by gender

**Results:**

| Group | Spearman's rho | p-value |
|---|---:|---:|
| Male | -0.039 | 0.011 |
| Female | -0.084 | < 0.001 |

Both groups showed statistically significant but weak negative correlations, suggesting that older participants tended to report slightly poorer dental health.

---

### 4. Social Participation and Dental Health

**Research question:**  
Are social-participation factors associated with self-rated dental health?

**Variables examined:**

- Frequency of Internet/email use
- Connection with society/current events
- Living with a partner

**Method:** Binary Logistic Regression

**Key results:**

- Overall Internet-use variable: **p < 0.001**
- Daily/almost-daily Internet use: **OR = 1.339, p < 0.001**
- Living with a partner: **OR = 1.251, p < 0.001**
- Following current events: **p = 0.072**
- Nagelkerke R² = **0.010**

The model identified some statistically significant relationships, but its explanatory power was low.

## Key Findings

- Denture use was significantly associated with self-rated dental health.
- Eating-out frequency had a statistically significant but weak positive correlation with dental health.
- Age had a statistically significant but weak negative correlation with dental health for both males and females.
- Daily Internet use and living with a partner were significantly associated with the binary dental-health outcome.
- Statistical significance did not necessarily imply a strong relationship; several observed associations were small.

## Limitations

Several limitations should be considered when interpreting the results:

- Dementia-related variables contained substantial missing data and were therefore not suitable for direct analysis.
- Some social-participation variables also contained missing responses.
- Self-rated dental health is subjective and does not necessarily represent objective clinical dental conditions.
- The logistic regression model explained only a small proportion of variation in the outcome.
- Social participation is a broad concept, and more narrowly defined variables could improve future analysis.

## Future Work

Possible extensions include:

- Incorporating additional objective dental-health indicators, such as number of natural teeth or oral pain.
- Narrowing social-participation measures to specific areas such as family support, social activities, or digital participation.
- Reproducing the original SPSS analysis in **Python** using pandas, SciPy, and statsmodels.
- Adding reproducible visualisations and analysis notebooks.

## Skills Demonstrated

- Statistical Analysis
- Hypothesis Testing
- Chi-square Testing
- Spearman Correlation
- Logistic Regression
- Categorical Data Analysis
- Data Cleaning & Recoding
- Missing-Value Analysis
- Research Design
- Statistical Interpretation
- SPSS

## Repository Structure

```text
oral-health-social-participation-analysis/
│
├── README.md
├── Data_Analysis_Report.pdf
```

## Full Report

The complete academic report, including literature review, methodology, statistical outputs, discussion, references, and appendix, is available in:

`Data_Analysis_Report.pdf`

## Academic Context

This was an individual coursework project completed in **2022** as part of the **MSc Data Science** programme at the **University of Sheffield**.
