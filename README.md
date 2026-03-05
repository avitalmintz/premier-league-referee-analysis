# Premier League Referee Tendency Analysis

An interactive data visualization app analyzing how Premier League referee tendencies — card rates, foul tolerance, home advantage bias — vary across officials and affect match outcomes.

## Overview

Using match data from 760 Premier League games across the 2023-24 and 2024-25 seasons, this project explores patterns in referee behavior through interactive Altair visualizations built with Streamlit.

## Visualizations

- **Slope charts**: How individual referees' card rates shift between seasons
- **Scatter plots**: Relationship between foul counts and cards issued per referee
- **Bar charts**: Home vs. away card distributions with interactive referee filtering

## Data

760 matches from [football-data.co.uk](https://www.football-data.co.uk/), covering:
- Match results, goals, shots
- Cards issued (yellow/red) by home/away
- Fouls committed
- Referee assignments

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tech Stack

Python, Streamlit, Altair, Pandas
