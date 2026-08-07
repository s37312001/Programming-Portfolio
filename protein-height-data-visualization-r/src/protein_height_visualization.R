# Protein Consumption & Human Height
# Exploratory Data Visualization in R
#
# Original coursework project: MSc Data Science, University of Sheffield
#
# This script separates the R analysis from the written report and preserves
# the original visualization workflow with clearer structure and comments.
#
# Expected input CSV files:
#   women_height_revise.csv
#   men_height_revise.csv
#   men_height_HDI.csv
#   women_height_HDI.csv
#   daily-protein-supply-from-animal-and-plant-based-foods.csv
#   meat_consumption.csv
#   male_BMI.csv
#   percentage_overweight.csv

# ---------------------------------------------------------------------------
# 0. Packages
# ---------------------------------------------------------------------------

library(tidyverse)
library(ggplot2)
library(gridExtra)
library(treemapify)
library(dplyr)
library(maps)


# ---------------------------------------------------------------------------
# 1. Global adult height maps
# ---------------------------------------------------------------------------

# ---- 1.1 Women aged 18 -----------------------------------------------------

women_height <- read.csv(
  "women_height_revise.csv",
  header = TRUE
)

world_map <- map_data("world")

# Join country-level height values to world polygon data.
women_height_map <- left_join(
  world_map,
  women_height,
  by = c("region" = "Entity")
)

women_height_map_graph <- ggplot(
  women_height_map,
  aes(x = long, y = lat, group = group)
) +
  geom_polygon(
    aes(fill = Mean_female_height),
    colour = "white"
  ) +
  scale_fill_viridis_c() +
  theme_void() +
  labs(
    fill = "Mean Height (cm)",
    title = "Mean height of women aged 18 in 2014",
    caption = "NCD RisC, Human Height (2017)"
  )

women_height_map_graph


# ---- 1.2 Men aged 18 -------------------------------------------------------

men_height <- read.csv(
  "men_height_revise.csv",
  header = TRUE
)

men_height_map <- left_join(
  world_map,
  men_height,
  by = c("region" = "Entity")
)

men_height_map_graph <- ggplot(
  men_height_map,
  aes(x = long, y = lat, group = group)
) +
  geom_polygon(
    aes(fill = Mean_male_height),
    colour = "white"
  ) +
  scale_fill_viridis_c() +
  theme_void() +
  labs(
    fill = "Mean Height (cm)",
    title = "Mean height of men aged 18 in 2014",
    caption = "NCD RisC, Human Height (2017)"
  )

men_height_map_graph


# ---------------------------------------------------------------------------
# 2. Historical height trends in five high-HDI countries
# ---------------------------------------------------------------------------

# ---- 2.1 Male height -------------------------------------------------------

annual_change_men_height <- read.csv(
  "men_height_HDI.csv",
  header = TRUE
)

annual_change_men_height_graph <- ggplot(
  annual_change_men_height,
  aes(x = Year)
) +
  geom_line(aes(y = Norway, col = "Norway")) +
  geom_line(aes(y = Switzerland, col = "Switzerland")) +
  geom_line(aes(y = Iceland, col = "Iceland")) +
  geom_line(aes(y = Germany, col = "Germany")) +
  geom_line(aes(y = Sweden, col = "Sweden")) +
  labs(
    x = "Year",
    y = "Mean Height (cm)",
    title = paste(
      "Annual change in average height of 18-year-old males",
      "by year of birth in five high-HDI countries (1896–1996)"
    )
  ) +
  scale_y_continuous(limits = c(160, 190)) +
  scale_colour_manual(
    name = "Country",
    values = c(
      "Norway" = "#8338ec",
      "Switzerland" = "#219ebc",
      "Iceland" = "#023047",
      "Germany" = "#ffb703",
      "Sweden" = "#fb8500"
    )
  )


# ---- 2.2 Female height -----------------------------------------------------

annual_change_women_height <- read.csv(
  "women_height_HDI.csv",
  header = TRUE
)

annual_change_women_height_graph <- ggplot(
  annual_change_women_height,
  aes(x = Year)
) +
  geom_line(aes(y = Norway, col = "Norway")) +
  geom_line(aes(y = Switzerland, col = "Switzerland")) +
  geom_line(aes(y = Iceland, col = "Iceland")) +
  geom_line(aes(y = Germany, col = "Germany")) +
  geom_line(aes(y = Sweden, col = "Sweden")) +
  labs(
    x = "Year",
    y = "Mean Height (cm)",
    title = paste(
      "Annual change in average height of 18-year-old females",
      "by year of birth in five high-HDI countries (1896–1996)"
    ),
    caption = "NCD RisC (2017)"
  ) +
  scale_y_continuous(limits = c(150, 180)) +
  scale_colour_manual(
    name = "Country",
    values = c(
      "Norway" = "#8338ec",
      "Switzerland" = "#219ebc",
      "Iceland" = "#023047",
      "Germany" = "#ffb703",
      "Sweden" = "#fb8500"
    )
  )

# Display male and female trends together.
grid.arrange(
  annual_change_men_height_graph,
  annual_change_women_height_graph,
  ncol = 1
)


# ---------------------------------------------------------------------------
# 3. Animal vs. plant protein supply
# ---------------------------------------------------------------------------

animal_plant_protein <- read.csv(
  "daily-protein-supply-from-animal-and-plant-based-foods.csv",
  header = TRUE
)

# Convert blank strings to missing values.
animal_plant_protein[animal_plant_protein == " "] <- NA

# Keep valid country records for the 2014 reference year.
animal_plant_protein <- animal_plant_protein[
  !is.na(animal_plant_protein$Code) &
    animal_plant_protein$Year == 2014,
]

# Rank countries by animal-protein supply and keep the top 10.
animal_plant_protein <- animal_plant_protein[
  order(
    animal_plant_protein$Animal_products,
    decreasing = TRUE
  ),
]

animal_plant_protein <- animal_plant_protein[1:10, ]

# Transpose the table for base R stacked-bar input.
# Note: t() is a matrix TRANSPOSE, not a matrix inverse.
animal_plant_protein <- t(animal_plant_protein)

# Use country names as column names.
colnames(animal_plant_protein) <- animal_plant_protein[1, ]

# Keep only the two protein-source rows.
animal_plant_protein <- animal_plant_protein[4:5, ]

barplot(
  animal_plant_protein,
  main = "Daily protein supply from animal and plant-based foods in 2014",
  sub = "Source: Food and Agriculture Organization of the United Nations (2022)",
  xlab = "Country",
  ylab = "Grams per day per capita",
  ylim = c(0, 200),
  col = c("Red", "Blue")
)

legend(
  "topright",
  c("Plant protein", "Animal protein"),
  fill = c("Blue", "Red")
)


# ---------------------------------------------------------------------------
# 4. Meat consumption vs. average male height
# ---------------------------------------------------------------------------

meat_consumption <- read.csv(
  "meat_consumption.csv",
  header = TRUE
)

# Combine meat-consumption values with male-height data by country.
male_height_protein <- left_join(
  meat_consumption,
  men_height,
  by = c("Entity" = "Entity")
)

# Keep only the fields used in the visualization.
male_height_protein <- male_height_protein %>%
  select(1, 3, 4, 7)

colnames(male_height_protein)[1] <- "Country"
colnames(male_height_protein)[2] <- "Year"

male_height_protein_graph <- ggplot(
  male_height_protein,
  aes(
    x = Mean_male_height,
    y = kg.pp,
    col = Country
  )
) +
  geom_point(size = 6) +
  scale_colour_brewer(palette = "Paired") +
  labs(
    x = "Average male height (cm)",
    y = "Meat consumption (kilograms per capita per year)",
    title = paste(
      "Average male height in the top 10 countries",
      "with the highest male meat consumption in 2014"
    ),
    caption = paste(
      "NCD RisC (2017)",
      "Food and Agriculture Organization of the United Nations (2022)",
      sep = "\n"
    )
  )

male_height_protein_graph


# ---------------------------------------------------------------------------
# 5. BMI and overweight prevalence in high-meat-consumption countries
# ---------------------------------------------------------------------------

male_BMI <- read.csv(
  "male_BMI.csv",
  header = TRUE
)

male_BMI[male_BMI == " "] <- NA

male_BMI <- male_BMI[
  !is.na(male_BMI$Code) &
    male_BMI$Year == 2014,
]

# Keep the countries selected in the original high-meat-consumption comparison.
male_BMI <- male_BMI[
  male_BMI$Entity %in% c(
    "Australia",
    "United States",
    "Argentina",
    "Samoa",
    "Brazil",
    "Israel",
    "Bahamas",
    "Spain",
    "Saint Lucia",
    "Saint Vincent and the Grenadines"
  ),
]

percentage_overweight <- read.csv(
  "percentage_overweight.csv",
  header = TRUE
)

percentage_overweight[percentage_overweight == " "] <- NA

percentage_overweight <- percentage_overweight[
  !is.na(percentage_overweight$Code) &
    percentage_overweight$Year == 2014,
]

percentage_overweight <- percentage_overweight %>%
  select(1, 4)

# Join BMI and overweight-prevalence data by country.
overweight_BMI <- left_join(
  male_BMI,
  percentage_overweight,
  by = c("Entity" = "Entity")
)

overweight_BMI <- overweight_BMI[
  !is.na(overweight_BMI$Percentage_of_overweight),
]

# Create explicit labels because similar treemap areas are difficult to compare.
overweight_BMI$label <- paste(
  overweight_BMI$Entity,
  overweight_BMI$Percentage_of_overweight,
  sep = "\n"
)

ggplot(
  overweight_BMI,
  aes(
    area = Percentage_of_overweight,
    fill = Mean_male_BMI,
    label = label
  )
) +
  geom_treemap() +
  geom_treemap_text(
    fontface = "italic",
    colour = "white",
    place = "centre"
  ) +
  labs(
    title = paste(
      "Average male BMI by overweight prevalence",
      "in high-meat-consumption countries in 2014"
    ),
    fill = "Average male BMI",
    caption = "Area labels show country name and percentage of overweight people"
  )
