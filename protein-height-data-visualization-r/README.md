# Protein Consumption & Human Height — Data Visualization in R

An exploratory data visualization project developed in **R** to examine cross-country patterns in **adult height, protein supply, meat consumption, BMI, and overweight prevalence**.

This project was completed as individual coursework for the **MSc Data Science** programme at the **University of Sheffield**. The analysis combines multiple public datasets and uses a sequence of visualizations to move from a global overview to more focused comparisons.

> **Scope:** This is an exploratory visualization project. The charts identify patterns and associations in aggregated country-level data; they do **not** establish that protein or meat consumption causes differences in human height.

---

## Research Question

**Is protein consumption associated with differences in human height across countries?**

The project explores this question through five visualization stages:

1. Global distribution of average adult height
2. Long-term height trends in high-HDI countries
3. Animal vs. plant protein supply
4. Meat consumption vs. average male height
5. BMI and overweight prevalence in high-meat-consumption countries

The analysis primarily uses **2014** for cross-sectional comparisons because it was the latest common/reference year used in the original coursework datasets.

---

## Analytical Story

The visualization design follows a **zoom-out → zoom-in** analytical narrative:

```text
Global height patterns
        ↓
Historical height trends
        ↓
Protein-source composition
        ↓
Meat consumption vs. height
        ↓
BMI / overweight context
```

Rather than relying on a single chart, the project uses multiple visual encodings to examine the topic from geographical, temporal, compositional, relational, and health perspectives.

---

## Data Sources

The original project used public secondary datasets from:

- **Our World in Data / NCD Risk Factor Collaboration (NCD-RisC)** — adult height and BMI
- **Food and Agriculture Organization of the United Nations (FAOSTAT)** — food supply, protein supply, and meat consumption
- **United Nations Development Programme (UNDP)** — Human Development Index reference countries

The repository focuses on the analysis and visualization code. The original academic report contains the complete dataset and literature references.

---

## Data Preparation

The project required several data-wrangling operations before visualization.

### Filtering

Cross-sectional datasets were filtered to a common reference year:

```r
Year == 2014
```

Rows without valid country codes were removed where appropriate.

### Ranking and Top-N Selection

For focused comparisons, countries were sorted by protein or meat consumption and the **top 10 countries** were selected.

This reduced visual clutter and made country-level comparisons more interpretable.

### Dataset Integration

Multiple datasets were combined using country names as the joining key.

For example:

```r
left_join(meat_consumption, men_height, by = c("Entity" = "Entity"))
```

This created combined analytical tables containing measures from different sources, such as:

- average male height
- meat consumption
- average male BMI
- percentage of overweight adults

### Reshaping

The animal/plant protein table was **transposed** before producing the stacked bar chart.

> The original coursework described this operation as a “matrix inverse”; technically, R's `t()` function performs a **matrix transpose**, not a matrix inverse.

---

# Visualizations

## 1. Global Adult Height — Choropleth Maps

Two world maps show average height for:

- women aged 18
- men aged 18

### Visualization technique

The country-level height data are joined to world-map polygon data and visualized with `ggplot2`.

```r
geom_polygon(aes(fill = Mean_female_height))
scale_fill_viridis_c()
theme_void()
```

### Why a choropleth?

A choropleth is appropriate when:

- the analytical unit is geographical
- values vary continuously across countries
- the objective is to identify broad spatial patterns

The **Viridis continuous colour scale** was selected because it provides perceptually ordered colour differences and is more accessible for many forms of colour-vision deficiency.

### Observation

The maps suggest that average adult height was generally higher in parts of **Europe, North America, and Australia** than in many other regions.

Missing country values remain unfilled, which is an important limitation when interpreting global coverage.

---

## 2. Historical Height Trends — Multi-Series Line Charts

The second visualization examines height trends by year of birth for five high-HDI countries:

- Germany
- Iceland
- Norway
- Sweden
- Switzerland

Separate charts are created for males and females.

### Why line charts?

A line chart is suitable because:

- `Year` is an ordered temporal variable
- the objective is to show **trend direction and rate of change**
- multiple countries can be compared over the same time scale

The project uses `grid.arrange()` to vertically combine the male and female charts.

### Axis design

The y-axis is restricted to make relatively small differences in height more visible.

This is useful for trend inspection, but truncated axes can visually amplify small changes. For that reason, the chart should be interpreted as a **trend-focused view**, not as a representation of absolute proportional differences.

### Observation

Height increased across the selected high-HDI countries over much of the historical period and then appeared to approach a plateau.

The original report discusses this pattern in the context of possible biological limits, but the visualization itself should be interpreted as descriptive evidence only.

---

## 3. Animal vs. Plant Protein Supply — Stacked Bar Chart

The third visualization compares the composition of daily protein supply for the ten selected countries with the highest animal-protein supply in 2014.

Each bar is divided into:

- animal protein
- plant protein

### Why a stacked bar chart?

The design supports two comparisons simultaneously:

1. total protein supply across countries
2. relative contribution of animal and plant sources within each country

The underlying table is transposed with `t()` so that the two protein-source variables can be represented as stacked components.

### Observation

Animal protein accounted for a substantial share of total protein supply in the selected countries, while plant protein remained a meaningful component.

This chart describes **protein-source composition** rather than individual dietary intake.

---

## 4. Meat Consumption vs. Average Male Height — Scatter Plot

A scatter plot compares:

- **x-axis:** average male height
- **y-axis:** meat consumption per capita

Each point represents one of the selected high-meat-consumption countries.

### Why a scatter plot?

Scatter plots are designed to investigate the relationship between **two continuous variables**.

They can reveal:

- direction of association
- clustering
- possible outliers
- nonlinear patterns
- heterogeneity between observations

### Observation

Within this small selected group of countries, the plot visually suggests a positive association between meat consumption and average male height.

However, this should **not** be interpreted as a causal relationship because:

- the sample is restricted to high-meat-consumption countries
- no regression or statistical significance test was performed
- country-level averages may be influenced by income, healthcare, genetics, childhood nutrition, inequality, and many other confounding factors
- aggregated country-level relationships do not necessarily represent individual-level relationships

This distinction between **visual association and causal inference** is central to responsible exploratory data analysis.

---

## 5. BMI & Overweight Prevalence — Treemap

The final visualization provides health context for countries with high meat consumption.

It combines:

- **area:** percentage of overweight people
- **fill:** average male BMI
- **label:** country and overweight percentage

### Why a treemap?

A treemap can encode multiple variables simultaneously using:

- area
- colour
- text labels

This allows overweight prevalence and mean BMI to be presented in one compact view.

### Design limitation

Several countries have relatively similar overweight percentages, making area comparison difficult.

The original project addressed this by adding explicit labels containing the country name and overweight percentage.

A grouped bar chart or a combined bar/line visualization could provide more precise comparison in a future revision.

---

# Accessibility & Visualization Design

Accessibility was treated as part of the visualization process rather than an afterthought.

Examples include:

### Colour-blind-friendly scales

The world maps use:

```r
scale_fill_viridis_c()
```

The scatter plot uses:

```r
scale_colour_brewer(palette = "Paired")
```

These choices aim to make categories and continuous values easier to distinguish for viewers with common colour-vision deficiencies.

### Reducing visual clutter

The analysis focuses on selected countries rather than plotting every country in comparison charts.

This improves readability but introduces a **selection trade-off**: the visualizations become clearer while representing a narrower subset of the global data.

### Explicit labels

The treemap includes text labels because area differences alone are difficult to estimate precisely.

### Visual hierarchy

Titles, axis labels, legends, captions, and source information are used to make each chart interpretable without relying entirely on surrounding prose.

---

# Key Findings

The visual analysis produced several exploratory observations:

- Average adult height varies substantially across countries and regions.
- Height in selected high-HDI countries increased historically before appearing to approach a plateau.
- Countries with high protein supply often receive a substantial portion from animal sources.
- Among the selected high-meat-consumption countries, meat consumption and male height show a visually positive association.
- Many of the selected high-meat-consumption countries also show relatively high overweight prevalence and male BMI.

These findings should be understood as **descriptive and exploratory**, not causal.

---

# Analytical Limitations

## Ecological analysis

The unit of analysis is primarily the **country**, not the individual.

A relationship observed between country averages does not imply that the same relationship exists at the individual level. Interpreting aggregated relationships as individual effects can lead to an **ecological fallacy**.

## Selection bias

Some visualizations deliberately focus on top-10 countries. This improves interpretability but means the displayed sample is **not representative of all countries**.

## Confounding

Human height is influenced by many factors beyond protein supply, including:

- genetics
- childhood nutrition
- healthcare
- socioeconomic conditions
- infectious disease burden
- food security
- living conditions

The project does not control for these variables.

## Correlation vs. causation

The scatter plot can reveal an association, but the project does not estimate a causal effect of meat or protein consumption on height.

A stronger causal or predictive study would require additional statistical modelling, carefully defined covariates, and a more appropriate research design.

## Missing data

Some countries are absent from the world maps because the source data could not be matched or were unavailable.

---

# Future Improvements

If extending this project today, useful improvements would include:

- Convert all data preparation into a fully reproducible R pipeline rather than relying on manually prepared CSV files.
- Reshape the line-chart data into tidy/long format and use a single `geom_line()` mapping by country.
- Use `ggplot2` consistently instead of mixing base R `barplot()` with `ggplot2`.
- Add correlation coefficients and confidence intervals where appropriate.
- Increase the scatter-plot sample beyond the top 10 countries.
- Add regression modelling while explicitly controlling for potential confounders.
- Replace the treemap with a more precise comparison chart if exact country-to-country comparison is the priority.
- Add interactive visualizations using tools such as `plotly` or `shiny`.
- Build a reproducible data-acquisition layer from the original public data sources.

---

# R Techniques Demonstrated

| Area | Techniques |
|---|---|
| Data manipulation | filtering, sorting, column selection, missing-value handling |
| Dataset integration | `left_join()` |
| Data reshaping | matrix transpose with `t()` |
| Geographic visualization | `map_data()`, `geom_polygon()` |
| Continuous colour encoding | `scale_fill_viridis_c()` |
| Time-series visualization | `geom_line()` |
| Multi-panel layout | `grid.arrange()` |
| Composition visualization | stacked bar chart |
| Relationship analysis | scatter plot |
| Categorical palettes | `scale_colour_brewer()` |
| Hierarchical/area visualization | `geom_treemap()` |
| Annotation | titles, captions, legends, text labels |
| Accessibility | colour-blind-aware palettes and explicit labels |

---

# Technology

- **R**
- **ggplot2**
- **dplyr**
- **tidyverse**
- **gridExtra**
- **treemapify**
- **maps / world map data**

---

# Repository Structure

```text
protein-height-data-visualization-r/
│
├── README.md
├── src/
│   └── protein_height_visualization.R
└── report/
    └── protein-height-data-visualization.pdf
```

---

# Project Files

## R Analysis

[`src/protein_height_visualization.R`](src/protein_height_visualization.R)

Contains the R code used for data preparation, dataset joins, filtering, and the five visualization stages.

## Full Report

[`report/protein-height-data-visualization.pdf`](report/protein-height-data-visualization.pdf)

Contains the original academic discussion, visualization rationale, accessibility considerations, limitations, references, and appendix.

---

## Academic Context

This project was completed as individual coursework for the **MSc Data Science** programme at the **University of Sheffield**.

The GitHub version reframes the original coursework as an **exploratory data visualization portfolio project**, while preserving the original analysis and clearly distinguishing descriptive association from causal inference.
