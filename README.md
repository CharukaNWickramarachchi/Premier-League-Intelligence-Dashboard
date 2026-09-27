# Premier League Intelligence Dashboard ⚽

An interactive Premier League analytics and prediction app built with **Streamlit**. Explore historical results, compare clubs, study league trends, train match prediction models, and simulate possible outcomes in one place.

**Created by Charuka Wickramarachchi and Lisandi Himara.**

## 🌐 Visit the live dashboard

**[Click here to open the Premier League Intelligence Dashboard](https://premier-league-intelligence-dashboard.streamlit.app/)**

You can use the app directly in your browser without installing anything.

## Project idea

Football results are often scattered across tables and match reports. This project turns match-level Premier League data into an accessible dashboard for answering questions such as:

- How has a team's form or strength changed over time?
- How do two clubs compare head to head?
- Which historical results were the biggest upsets?
- What do statistical models estimate for a future fixture?

The included dataset contains **9,880 matches**, **26 seasons (2000/01–2025/26)**, and **46 clubs**. It is a historical snapshot stored in `data/matches_clean.csv`; the app does **not** fetch live results or fixtures.

## Features

| Page | What you can do |
| --- | --- |
| **Home** | View match and goal KPIs, result shares, goal trends, and an all-time table preview. |
| **Match Explorer** | Filter and inspect individual matches and their pre-match Elo ratings. |
| **Team Analytics** | Explore club form, Elo history, attack and defense, home/away performance, and discipline. |
| **League Analytics** | Compare season standings, all-time records, and league-wide patterns. |
| **Head-to-Head** | Compare any two clubs using their historical meetings and result trends. |
| **Prediction Center** | Train and compare classifiers, estimate a selected fixture, and simulate match scores and season outcomes. |
| **AI Insights** | Discover data-driven findings such as upsets, home advantage, referee patterns, and feature importance. |
| **Statistics** | Explore PCA, clustering, outliers, correlations, regression, and statistical tests. |
| **Downloads** | Export filtered matches, tables, and available model results as CSV or Excel. |
| **Settings / About** | Manage session settings and read about the app's methods and limitations. |

## Prediction methods

The app creates **pre-match Elo ratings** and rolling **5- and 10-match form** features. In the Prediction Center, you can choose to predict:

- Home win, draw, or away win
- Both teams to score
- Over 2.5 goals

Available models include Logistic Regression, Random Forest, Gradient Boosting, K-Nearest Neighbors, Support Vector Machine, Decision Tree, Naive Bayes, and a multilayer perceptron. XGBoost and LightGBM are available when installed.

The app compares models using accuracy, precision, recall, F1, cross-validation scores, and diagnostic charts. It also provides Elo-based fixture probabilities, a Poisson-based Monte Carlo match simulation, and season outcome simulations.

**Predictions are estimates based on historical data, not guaranteed results.** The model evaluation uses a random train/test split and standard cross-validation; its scores should not be interpreted as a forward-in-time test of future-season performance.

## Run locally

You need Python and pip. From the repository root, create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies and start the app:

```bash
pip install -r requirements.txt
streamlit run Home.py
```

Streamlit will display a local URL in your terminal. The dataset is included in the repository, so no API key is required.

## Data and technology

The dataset contains match dates, teams, full-time and half-time scores, results, and available statistics such as shots, corners, fouls, cards, and referees.

The app uses **Streamlit, pandas, NumPy, scikit-learn, SciPy, statsmodels, Plotly, and openpyxl**.

```text
Home.py                 Streamlit entry point
pages/                  Dashboard pages
data/matches_clean.csv  Historical match dataset
utils/                  Data preparation, Elo, models, statistics, charts
components/             Shared filters and KPI cards
assets/                 Styling and visual assets
requirements.txt        Python dependencies
```

## Scope and limitations

- Results, standings, and predictions come from the bundled CSV; there is no live Premier League feed.
- The dataset is match-level, so the app does not include player or transfer analytics.
- The **AI Insights** page uses programmed analysis and model feature importance; it does not call a generative AI service.
- Stadium reference data is static.
- The Elo parameter sliders on the **Settings** page save values in the session but are not yet connected to the cached rating calculation.
- CSV and Excel exports are available; PDF export is not implemented.

## Authors

**Charuka Wickramarachchi** and **Lisandi Himara**

Built as a Data Science and Business Analytics project combining exploratory analysis, statistical methods, machine learning, and interactive visualization.

**[Explore the live app →](https://premier-league-intelligence-dashboard.streamlit.app/)**
