# Taiwan COVID-19 Policy Analysis in R
# Cleaned extraction of the original MSc Data Science coursework code.
#
# Expected input files:
#   owid-covid-data.csv
#   face-covering-policies-covid.csv
#   public-events-covid.csv
#   stay-at-home-covid.csv

Sys.setlocale("LC_ALL", "en_GB.UTF-8")

library(tidyverse)
library(dplyr)
library(lubridate)
library(ggplot2)
library(gridExtra)
library(zoo)

# ---------------------------------------------------------------------------
# 1. Read source datasets
# ---------------------------------------------------------------------------

covid_data <- read.csv("owid-covid-data.csv", header = TRUE)
facial_coverings <- read.csv("face-covering-policies-covid.csv", header = TRUE)
cancel_public_events <- read.csv("public-events-covid.csv", header = TRUE)
stay_home_requirements <- read.csv("stay-at-home-covid.csv", header = TRUE)

# ---------------------------------------------------------------------------
# 2. Prepare 2021 Taiwan COVID-19 data
# ---------------------------------------------------------------------------

covid_data <- covid_data %>%
  mutate(
    date = ymd(date),
    year = year(date),
    month = month(date),
    day = day(date)
  ) %>%
  filter(location == "Taiwan", year == 2021) %>%
  select(location, date, new_cases)

colnames(covid_data)[2] <- "Day"

facial_coverings <- facial_coverings %>%
  mutate(
    Day = ymd(Day),
    year = year(Day),
    month = month(Day),
    day = day(Day)
  ) %>%
  filter(Entity == "Taiwan", year == 2021)

facial_coverings <- facial_coverings[, -1:-2]

cancel_public_events <- cancel_public_events %>%
  mutate(
    Day = ymd(Day),
    year = year(Day),
    month = month(Day),
    day = day(Day)
  ) %>%
  filter(Entity == "Taiwan", year == 2021)

cancel_public_events <- cancel_public_events[, -1:-2]

stay_home_requirements <- stay_home_requirements %>%
  mutate(
    Day = ymd(Day),
    year = year(Day),
    month = month(Day),
    day = day(Day)
  ) %>%
  filter(Entity == "Taiwan", year == 2021)

stay_home_requirements <- stay_home_requirements[, -1:-2]

# ---------------------------------------------------------------------------
# 3. Join the four datasets by date
# ---------------------------------------------------------------------------

covid_data <- covid_data %>%
  left_join(facial_coverings, by = "Day") %>%
  left_join(cancel_public_events, by = "Day") %>%
  left_join(stay_home_requirements, by = "Day")

# Preserve the original coursework output structure by removing duplicated
# year/month/day fields introduced by the joins.
covid_data <- covid_data[, -c(
  5, 6, 7,
  9, 10, 11,
  13, 14, 15
)]

head(covid_data)
tail(covid_data)

# ---------------------------------------------------------------------------
# 4. Feature engineering: convert new_cases to severity categories
# ---------------------------------------------------------------------------

# cut(..., breaks = 5) creates five equal-width intervals.
level_new_cases <- cut(
  covid_data$new_cases,
  breaks = 5,
  labels = 0:4
)

covid_data <- cbind(covid_data, level_new_cases)

head(covid_data)
tail(covid_data)

# ---------------------------------------------------------------------------
# 5. Chi-square tests of independence
# ---------------------------------------------------------------------------

chi_face_covering <- chisq.test(
  covid_data$level_new_cases,
  covid_data$facial_coverings,
  correct = FALSE
)

chi_public_events <- chisq.test(
  covid_data$level_new_cases,
  covid_data$cancel_public_events,
  correct = FALSE
)

chi_stay_home <- chisq.test(
  covid_data$level_new_cases,
  covid_data$stay_home_requirements,
  correct = FALSE
)

chi_face_covering
# Original report:
# X-squared = 90.402, df = 8, p-value = 3.853e-16

chi_public_events
# Original report:
# X-squared = 119.69, df = 8, p-value < 2.2e-16

chi_stay_home
# Original report:
# X-squared = 119.33, df = 4, p-value < 2.2e-16

# ---------------------------------------------------------------------------
# 6. 2021 policy timeline visualizations
# ---------------------------------------------------------------------------

facial_plot <- ggplot(covid_data, aes(x = Day)) +
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
  ) +
  labs(
    x = NULL,
    y = NULL,
    title = "Levels of Facial Covering Policies in 2021"
  ) +
  scale_colour_manual(
    name = "Legend",
    values = c(
      "New Cases (hundred)" = "red",
      "Levels of Facial Covering Policies" = "blue"
    )
  )

public_plot <- ggplot(covid_data, aes(x = Day)) +
  geom_line(
    aes(
      y = new_cases / 100,
      col = "New Cases (hundred)"
    )
  ) +
  geom_line(
    aes(
      y = cancel_public_events,
      col = "Levels of Public Event Cancellation"
    )
  ) +
  labs(
    x = NULL,
    y = NULL,
    title = "Levels of Public Event Cancellation in 2021"
  ) +
  scale_colour_manual(
    name = "Legend",
    values = c(
      "New Cases (hundred)" = "red",
      "Levels of Public Event Cancellation" = "green"
    )
  )

home_plot <- ggplot(covid_data, aes(x = Day)) +
  geom_line(
    aes(
      y = new_cases / 100,
      col = "New Cases (hundred)"
    )
  ) +
  geom_line(
    aes(
      y = stay_home_requirements,
      col = "Levels of Stay at Home Requirement"
    )
  ) +
  labs(
    x = NULL,
    y = NULL,
    title = "Levels of Stay at Home Requirement in 2021"
  ) +
  scale_colour_manual(
    name = "Legend",
    values = c(
      "New Cases (hundred)" = "red",
      "Levels of Stay at Home Requirement" = "purple"
    )
  )

facial_plot
public_plot
home_plot

grid.arrange(
  facial_plot,
  public_plot,
  home_plot,
  ncol = 1
)

# ---------------------------------------------------------------------------
# 7. Prepare 2022 vaccination / cases / deaths data
# ---------------------------------------------------------------------------

covid_data_2022 <- read.csv("owid-covid-data.csv", header = TRUE)

covid_data_2022 <- covid_data_2022 %>%
  mutate(
    date = ymd(date),
    year = year(date),
    month = month(date),
    day = day(date)
  ) %>%
  filter(location == "Taiwan", year == 2022) %>%
  select(
    location,
    date,
    people_vaccinated,
    total_cases,
    total_deaths
  )

# ---------------------------------------------------------------------------
# 8. Missing-value handling
# ---------------------------------------------------------------------------

# Last Observation Carried Forward (LOCF)
covid_data_2022 <- na.locf(
  covid_data_2022,
  na.rm = FALSE
)

# Preserve the original report's manually supplied 2021-12-31 cumulative value.
covid_data_2022$people_vaccinated[1] <- 18712858

# ---------------------------------------------------------------------------
# 9. 2022 cumulative trend visualizations
# ---------------------------------------------------------------------------

people_vaccinated_bar <- ggplot(
  covid_data_2022,
  aes(
    x = date,
    y = people_vaccinated / 1000000
  )
) +
  geom_bar(stat = "identity", fill = "lightgreen") +
  labs(
    x = NULL,
    y = "People vaccinated (million)",
    title = "People Vaccinated in 2022 (Cumulative)"
  )

total_cases_bar <- ggplot(
  covid_data_2022,
  aes(
    x = date,
    y = total_cases / 1000000
  )
) +
  geom_bar(stat = "identity", fill = "lightblue") +
  labs(
    x = NULL,
    y = "Total cases (million)",
    title = "Total Cases in 2022 (Cumulative)"
  )

total_deaths_bar <- ggplot(
  covid_data_2022,
  aes(
    x = date,
    y = total_deaths / 1000000
  )
) +
  geom_bar(stat = "identity", fill = "purple") +
  labs(
    x = NULL,
    y = "Total deaths (million)",
    title = "Total Deaths in 2022 (Cumulative)"
  )

grid.arrange(
  people_vaccinated_bar,
  total_cases_bar,
  total_deaths_bar,
  ncol = 1
)

# ---------------------------------------------------------------------------
# 10. Cumulative case-fatality ratio
# ---------------------------------------------------------------------------

# The original report called total_deaths / total_cases a "mortality rate".
# The more precise term is cumulative case-fatality ratio (CFR).

covid_data_2022 <- covid_data_2022 %>%
  mutate(
    case_fatality_ratio = total_deaths / total_cases
  )

case_fatality_plot <- ggplot(
  covid_data_2022,
  aes(
    x = date,
    y = case_fatality_ratio
  )
) +
  geom_line(colour = "red") +
  labs(
    x = NULL,
    y = "Total Deaths / Total Cases",
    title = "Cumulative Case-Fatality Ratio"
  )

case_fatality_plot
