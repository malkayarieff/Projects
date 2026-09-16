# Amazon Sales Dashboard

![Dashboard summary metrics](screenshots/metrics.png)

A Streamlit dashboard exploring the [Amazon Sales Dataset (Kaggle)](https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset) — product categories, prices, discounts, and ratings.

## Setup

```bash
uv add pandas streamlit plotly
```

Download `amazon.csv` from the Kaggle link above (requires a free Kaggle account) and place it at `data/raw/amazon.csv`.

## Run

```bash
uv run streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## Data Cleaning Decisions

The raw CSV has several fields that don't load as usable numbers by default:

- **`discounted_price` / `actual_price`** — stored as text with a `₹` symbol and comma
