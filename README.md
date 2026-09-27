# Premier League Intelligence Dashboard ⚽

An interactive Premier League analytics and prediction app built with **Streamlit**. Explore historical results, compare clubs, study league trends, train match prediction models, and simulate possible outcomes in one place.

**Created by Charuka Wickramarachchi and Lisandi Himara.**

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
| **Prediction Center** | Train and compare classifiers; estimate a selected fixture; simulate match scores and season outcomes. |
| **AI Insights** | Surface data-driven findings such as upsets, home advantage, referee patterns, and feature importance. |
| **Statistics** | Explore PCA, clustering, outliers, correlations, regression, and statistical tests. |
| **Downloads** | Export filtered matches, tables, and available model results as CSV or Excel. |
| **Settings / About** | Manage session settings and read the app's methodology and limitations. |

### Prediction methods

The app creates **pre-match Elo ratings** and rolling **5- and 10-match form** features. In the Prediction Center, you can select a target: **home/draw/away result**, **both teams to score**, or **over 2.5 goals**. Available classifiers include Logistic Regression, Random Forest, Gradient Boosting, K-Nearest Neighbors, Support Vector Machine, Decision Tree, Naive Bayes, and a multilayer perceptron. XGBoost and LightGBM are detected when installed.

Models are compared with held-out accuracy, precision, recall, F1, cross-validation scores, and diagnostic charts. Fixture predictions also include Elo-based probabilities. A Poisson-based Monte Carlo model simulates match scores; a separate simulation estimates title, top-four, and relegation probabilities for a selected season scenario.

These outputs are **estimates from historical data**, not guaranteed results. The training code uses a stratified random train/test split and standard cross-validation, so its reported metrics should not be treated as a forward-in-time evaluation of future-season performance.

## Run locally

You need Python and pip. From the repository root:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Then install dependencies and launch the app:

```bash
pip install -r requirements.txt
streamlit run Home.py
```

Streamlit will display a local URL in the terminal. Use the sidebar to navigate between pages. The dataset is included in the repository, so no API key is required. If you only want the core app, XGBoost and LightGBM can be omitted; the code detects their availability at runtime.

## Data and implementation

The CSV contains match dates, teams, full-time and half-time scores, results, and available match statistics such as shots, corners, fouls, cards, and referees. `utils/data_loader.py` cleans and deduplicates records, creates derived outcomes, computes Elo ratings, and builds rolling team-form features. The app uses **pandas**, **NumPy**, **scikit-learn**, **SciPy**, **statsmodels**, and **Plotly**, with **openpyxl** for Excel exports.

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
- The dataset is match-level, so the app does not offer player or transfer analytics.
- The **AI Insights** page uses programmed analysis and a Random Forest feature-importance view; it does not call a generative AI service.
- Stadium reference data is static. The Elo parameter sliders on **Settings** save values in the session but are not yet connected to the cached rating calculation.
- CSV and Excel exports are available; PDF export is not implemented.

## Authors

**Charuka Wickramarachchi** and **Lisandi Himara**

Built as a data science and business analytics project combining exploratory analysis, statistical methods, machine learning, and interactive visualization.