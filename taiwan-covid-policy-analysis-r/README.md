# Taiwan COVID-19 Policy Analysis in R

An end-to-end **statistical data analysis project in R** examining Taiwan's COVID-19 case trends, government policy responses, vaccination progress, confirmed cases, deaths, and case-fatality ratio.

This project was completed as individual coursework for the **MSc Data Science** programme at the **University of Sheffield**.

The project demonstrates a complete analytical workflow:

**Data Ingestion → Data Preprocessing → Data Integration → Feature Engineering → Statistical Testing → Missing-Value Handling → Derived Metrics → Data Visualization → Interpretation**

---

## Project Overview

The analysis was divided into two stages.

### 2021 — Government Policy & COVID-19 Case Analysis

Three government policy indicators were analysed alongside daily new COVID-19 cases:

- Face-covering requirements
- Public-event cancellation
- Stay-at-home requirements

Daily case counts were transformed into categorical severity levels, and **Pearson's Chi-square tests of independence** were used to evaluate the relationship between case severity and each policy variable.

### 2022 — Vaccination, Cases & Deaths

A second dataset was prepared to analyse:

- People vaccinated
- Total confirmed cases
- Total deaths
- Cumulative case-fatality ratio

Missing cumulative observations were processed using **Last Observation Carried Forward (LOCF)**, followed by time-based visualization in `ggplot2`.

---

## Analytical Workflow

```text
Multiple COVID-19 datasets
          ↓
      Read CSV files
          ↓
 Parse and standardize dates
          ↓
 Filter Taiwan / target year
          ↓
 Select analytical variables
          ↓
 Harmonize join keys
          ↓
 Join multiple datasets by date
          ↓
 Feature engineering
 new_cases → severity levels
          ↓
 Chi-square hypothesis testing
          ↓
 2021 policy / case visualization
          ↓
 Prepare 2022 cumulative dataset
          ↓
 Missing-value handling with LOCF
          ↓
 Vaccination / cases / deaths visualization
          ↓
 Calculate case-fatality ratio
          ↓
 Interpret analytical results
```

---

# Data Sources

The project uses public COVID-19 and policy-response datasets from **Our World in Data (OWID)** and the Oxford COVID-19 Government Response Tracker.

## Main COVID-19 Dataset

Variables used across the two analytical stages include:

- `location`
- `date`
- `new_cases`
- `people_vaccinated`
- `total_cases`
- `total_deaths`

## Government Policy Datasets

Three policy datasets were used:

1. **Face Coverings**
2. **Cancellation of Public Events and Gatherings**
3. **Stay-at-Home Requirements**

The policy variables use ordinal levels to represent different degrees of restriction.

---

# 1. Data Preprocessing

## Date Processing

The source datasets contained date fields that needed to be converted before filtering and joining.

Dates were parsed with `lubridate::ymd()`:

```r
covid_data <- covid_data %>%
  mutate(date = ymd(date)) %>%
  mutate(
    year = year(date),
    month = month(date),
    day = day(date)
  )
```

The extracted calendar fields were then used to select the required analysis period.

## Filtering

For the 2021 policy analysis, the main dataset was filtered to:

```text
location = Taiwan
year = 2021
```

The main analytical columns were reduced to:

```text
location
date
new_cases
```

Equivalent country and year filtering was applied to each government policy dataset.

## Column Selection

Only fields required for the analysis were retained.

This reduced unnecessary attributes before dataset integration and produced a more focused analytical structure.

---

# 2. Schema Harmonization & Data Integration

The COVID-19 dataset used:

```text
date
```

while the policy datasets used:

```text
Day
```

The main date column was renamed so the four datasets could share a common join key.

The policy datasets were then integrated using sequential `left_join()` operations:

```r
covid_data <- covid_data %>%
  left_join(facial_coverings, by = "Day") %>%
  left_join(cancel_public_events, by = "Day") %>%
  left_join(stay_home_requirements, by = "Day")
```

The integrated daily dataset contained:

- daily new cases
- face-covering policy level
- public-event cancellation level
- stay-at-home requirement level

This step demonstrates **multi-source relational data integration using a shared temporal key**.

---

# 3. Feature Engineering

The original `new_cases` variable contains daily case counts.

To perform categorical association testing with the ordinal policy variables, the case counts were transformed into five severity levels:

```r
level_new_cases <- cut(
  covid_data$new_cases,
  breaks = 5,
  labels = 0:4
)
```

The resulting feature was appended to the integrated dataset:

```r
covid_data <- cbind(
  covid_data,
  level_new_cases
)
```

This transformation is an example of **discretization / binning**, where a numerical variable is converted into categorical intervals for subsequent statistical analysis.

---

# 4. Statistical Analysis — Chi-Square Test of Independence

The project uses **Pearson's Chi-square test of independence** to evaluate the relationship between COVID-19 case-severity levels and each government policy indicator.

## Hypotheses

### Null Hypothesis (H₀)

> Case-severity level and policy level are independent.

### Alternative Hypothesis (H₁)

> Case-severity level and policy level are associated.

Three tests were performed:

```r
chisq.test(
  covid_data$level_new_cases,
  covid_data$facial_coverings,
  correct = FALSE
)

chisq.test(
  covid_data$level_new_cases,
  covid_data$cancel_public_events,
  correct = FALSE
)

chisq.test(
  covid_data$level_new_cases,
  covid_data$stay_home_requirements,
  correct = FALSE
)
```

## Statistical Results

| Policy Variable | Chi-square | df | p-value |
|---|---:|---:|---:|
| Face Coverings | **90.402** | 8 | **3.853e-16** |
| Public-Event Cancellation | **119.69** | 8 | **< 2.2e-16** |
| Stay-at-Home Requirements | **119.33** | 4 | **< 2.2e-16** |

All three tests produced very small p-values.

Under the defined hypothesis-testing framework, the null hypothesis of independence was rejected for all three policy variables.

The results therefore showed statistically significant relationships between the categorical case-severity levels and the policy levels in the 2021 dataset.

---

# 5. 2021 Policy & Case Visualization

The statistical results were complemented with time-series visualizations.

Three line charts were created:

1. Daily new cases vs. face-covering policy
2. Daily new cases vs. public-event cancellation policy
3. Daily new cases vs. stay-at-home requirement

Example:

```r
facial_plot <- ggplot(
  covid_data,
  aes(x = Day)
) +
  geom_line(
    aes(
      y = new_cases / 100,
      col = "New Cases (hundred)"
    )
  ) +
  geom_line(
    aes(
      y = facial_coverings,
      col = "Levels of Facial Covering Policies"
    )
  )
```

Daily new cases were divided by 100 to make the case trend visually comparable with the smaller policy-level scale.

The three charts were combined using:

```r
grid.arrange(
  facial_plot,
  public_plot,
  home_plot,
  ncol = 1
)
```

This multi-panel view allows policy changes and case trends to be compared across the same period.

---

# 6. 2022 Dataset Preparation

A second subset of the OWID dataset was created for Taiwan in 2022.

```r
covid_data_2022 <- covid_data_2022 %>%
  filter(
    location == "Taiwan",
    year == 2022
  ) %>%
  select(
    location,
    date,
    people_vaccinated,
    total_cases,
    total_deaths
  )
```

Unlike `new_cases`, these variables are cumulative measures.

---

# 7. Missing-Value Handling

The 2022 cumulative dataset contained missing observations.

The project used the `zoo` package and `na.locf()`:

```r
covid_data_2022 <- na.locf(
  covid_data_2022,
  na.rm = FALSE
)
```

This method is known as **Last Observation Carried Forward (LOCF)**.

The latest available cumulative value is propagated forward when an intermediate observation is missing.

For example:

```text
18.7M → NA → NA → 18.9M
```

becomes:

```text
18.7M → 18.7M → 18.7M → 18.9M
```

The first 2022 vaccination value was supplemented with the known cumulative observation from 31 December 2021:

```r
covid_data_2022$people_vaccinated[1] <- 18712858
```

---

# 8. 2022 Cumulative Trend Visualization

Three `ggplot2` bar charts were produced for:

- people vaccinated
- total confirmed cases
- total deaths

Large values were converted into millions for readability.

Example:

```r
people_vaccinated_bar <- ggplot(
  covid_data_2022,
  aes(
    date,
    people_vaccinated / 1000000
  )
) +
  geom_bar(stat = "identity")
```

The plots were combined vertically:

```r
grid.arrange(
  people_vaccinated_bar,
  total_cases_bar,
  total_deaths_bar,
  ncol = 1
)
```

This made it possible to compare the progression of vaccination, cases, and deaths over the same 2022 period.

---

# 9. Derived Metric — Cumulative Case-Fatality Ratio

The project also created a derived metric using:

```r
total_deaths / total_cases
```

In the original coursework this was described as a mortality rate. In this repository it is labelled more precisely as the **cumulative case-fatality ratio (CFR)** because confirmed cases are used as the denominator.

```r
covid_data_2022 <- covid_data_2022 %>%
  mutate(
    case_fatality_ratio =
      total_deaths / total_cases
  )
```

The ratio was then visualized over time using a line chart.

---

# Key Results

## 2021

The Chi-square tests identified statistically significant relationships between case-severity levels and all three government policy variables.

| Policy | Result |
|---|---|
| Face Coverings | χ² = **90.402**, p = **3.853e-16** |
| Public-Event Cancellation | χ² = **119.69**, p **< 2.2e-16** |
| Stay-at-Home Requirements | χ² = **119.33**, p **< 2.2e-16** |

The accompanying line charts visualized how policy levels changed during the 2021 case timeline.

## 2022

The second analysis visualized:

- vaccination growth
- cumulative confirmed cases
- cumulative deaths
- declining cumulative case-fatality ratio

This extended the original policy-focused analysis with additional epidemic and vaccination indicators.

---

# Data Science Skills Demonstrated

| Area | Implementation |
|---|---|
| **R Programming** | Complete analysis implemented in R |
| **Data Ingestion** | Reading multiple CSV datasets |
| **Data Cleaning** | Row filtering, column selection, redundant-column removal |
| **Date Processing** | `lubridate::ymd()`, year/month/day extraction |
| **Schema Harmonization** | Standardizing temporal join keys |
| **Data Integration** | Multiple `left_join()` operations |
| **Feature Engineering** | Creating `level_new_cases` |
| **Discretization / Binning** | Converting case counts into five severity levels |
| **Statistical Testing** | Pearson Chi-square tests |
| **Hypothesis Testing** | H₀/H₁ definition and p-value interpretation |
| **Missing-Value Handling** | LOCF using `zoo::na.locf()` |
| **Derived Metrics** | Cumulative case-fatality ratio |
| **Time-Based Analysis** | Daily and cumulative trend analysis |
| **Data Visualization** | `ggplot2` |
| **Multi-Panel Visualization** | `gridExtra::grid.arrange()` |
| **Result Interpretation** | Connecting statistical outputs with visual trends |

---

# R Packages

- **tidyverse**
- **dplyr**
- **lubridate**
- **ggplot2**
- **gridExtra**
- **zoo**

---

# Repository Structure

```text
taiwan-covid-policy-analysis-r/
│
├── README.md
├── src/
│   └── taiwan_covid_policy_analysis.R
└── report/
    └── taiwan-covid-policy-analysis-r.pdf
```

## R Analysis

[`src/taiwan_covid_policy_analysis.R`](src/taiwan_covid_policy_analysis.R)

Contains the complete R workflow for:

- data preprocessing
- date transformation
- multi-source joins
- feature engineering
- Chi-square testing
- missing-value handling
- derived metrics
- data visualization

## Full Report

[`report/taiwan-covid-policy-analysis-r.pdf`](report/taiwan-covid-policy-analysis-r.pdf)

Contains the original academic methodology, statistical output, visualizations, discussion, references, and R code appendix.

---

# Retrospective & Potential Improvements

This repository primarily documents the analysis that was originally completed. Looking back at the project, several methodological improvements could strengthen a future version.

### 1. Separate Association from Causal Interpretation

The Chi-square tests identify whether case-severity and policy categories are statistically associated.

A future analysis should distinguish this more explicitly from estimating whether a particular policy **caused** a subsequent change in cases.

### 2. Consider Reverse Causality

Government policy can respond to epidemic conditions:

```text
Increasing cases
      ↓
Stricter policy
```

This means a relationship between policy level and case severity can partly reflect the government's response to rising infections.

A future design should account for the direction of this relationship.

### 3. Account for Temporal Dependence

COVID-19 observations are ordered through time.

Cases observed on nearby dates are related, so a future model could explicitly account for **serial / temporal dependence** instead of treating each daily observation only as a categorical record.

### 4. Examine Lagged Policy Effects

A policy introduced today would not necessarily affect reported cases immediately.

A future analysis could compare:

```text
Policy at time t
      ↓
Cases at t + 7 days
Cases at t + 14 days
Cases at t + 21 days
```

to investigate potential **lagged effects**.

### 5. Preserve Continuous Case Information

The original analysis converted `new_cases` into five categorical severity levels to perform Chi-square tests.

A future extension could retain the original case-count variable and apply statistical models designed for count data or temporal outcomes.

Possible methods include:

- Poisson regression
- Negative Binomial regression
- Generalized Linear Models
- Interrupted time-series analysis

These would be **future extensions**, rather than methods used in the original project.

### 6. Add Additional Explanatory Variables

A future version could incorporate additional factors such as:

- vaccination rates
- testing volume
- mobility
- variants
- travel restrictions
- hospitalisation
- regional differences

This would allow the policy analysis to consider a broader set of epidemic conditions.

---

## Academic Context

This project was completed as individual coursework for the **MSc Data Science** programme at the **University of Sheffield**.

The repository presents the original work as an end-to-end **R statistical data analysis project**, focusing on the preprocessing, integration, feature engineering, statistical testing, missing-data handling, derived metrics, and visualization that were actually implemented.
