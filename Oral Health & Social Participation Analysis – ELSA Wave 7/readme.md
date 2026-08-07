# Oral Health & Social Participation Analysis

A statistical analysis project examining the association between oral health
and social participation among older adults in the United Kingdom.

This project was completed as an individual MSc Data Science assignment
at the University of Sheffield.

## Project Overview

The project investigates whether self-rated dental health is associated with
oral-health characteristics, demographic factors, and social participation
among older adults.

The analysis uses data from the English Longitudinal Study of Ageing (ELSA)
Wave 7, which contains health, social, wellbeing, and economic information
about adults aged 50 and over in England.

The Wave 7 dataset included 9,666 participants.

## Research Objectives

The analysis focuses on three main objectives:

1. Assess the relationship between dental health conditions and removable dentures.
2. Examine whether dental health conditions are associated with demographic factors.
3. Explore the relationship between dental health conditions and social participation.

## Variables

Eight variables were selected for the analysis.

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

### Outcome
- Self-rated dental health condition

For logistic regression, the self-rated dental health variable was additionally
recoded into a binary outcome.

## Statistical Methods

The analysis was conducted using:

- Descriptive statistics
- Cross-tabulation
- Chi-square Linear-by-Linear Association
- Spearman Rank Correlation
- Binary Logistic Regression

## Research Questions

### Test 1
Is denture use associated with self-rated dental health?

**Method:** Chi-square Linear-by-Linear Association

### Test 2
Is eating-out frequency correlated with self-rated dental health?

**Method:** Spearman Rank Correlation

### Test 3
Is age associated with self-rated dental health, and does the relationship
differ by gender?

**Method:** Spearman Rank Correlation

### Test 4
Are social participation factors associated with self-rated dental health?

Variables examined:
- Internet use
- Connection with society
- Living with a partner

**Method:** Binary Logistic Regression

## Key Findings

- Denture use showed a statistically significant association with
  self-rated dental health (p < 0.001).

- Eating-out frequency had a statistically significant but weak positive
  correlation with dental health (Spearman's rho = 0.110, p < 0.001).

- Age showed a weak negative correlation with dental health for both males
  and females.

- The logistic regression indicated that social participation variables
  were statistically associated with dental health overall, although the
  explanatory power of the model was low.

- Daily Internet use and living with a partner showed significant positive
  relationships with the binary dental-health outcome.

## Limitations

Several limitations should be considered:

- Dementia-related variables contained substantial missing data and therefore
  could not be directly incorporated into the main analysis.
- Some social-participation variables also contained missing responses.
- The logistic regression model explained only a small proportion of the
  variation in self-rated dental health.
- Self-rated dental health does not necessarily represent objective clinical
  oral-health conditions.

Future analysis could incorporate additional objective dental-health variables
and use more narrowly defined measures of social participation.

## Report

The complete academic report, including methodology, statistical tables,
discussion, references, and appendices, is available here:

[View Full Report](report/Data_Analysis_Report.pdf)

## Tools & Skills

- Statistical Analysis
- Hypothesis Testing
- Chi-square Test
- Spearman Correlation
- Logistic Regression
- Data Cleaning & Recoding
- Categorical Data Analysis
- Research Design
- Data Interpretation

## Data Source

English Longitudinal Study of Ageing (ELSA), Wave 7.

The raw ELSA dataset is not included in this repository.

## Author

MSc Data Science  
University of Sheffield
