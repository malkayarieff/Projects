rd · MD
Amazon Sales Dashboard

A Streamlit dashboard that explores the Amazon Sales Dataset (Kaggle) — looking at product categories, prices, discounts, and ratings.

Setup
bash
# from the project root
uv add pandas streamlit plotly

Download amazon.csv from the Kaggle link above (requires a free Kaggle account) and place it at data/raw/amazon.csv. This file is intentionally excluded from git via .gitignore.

Run
bash
uv run streamlit run app.py

Then open the local URL Streamlit prints (usually http://localhost:8501).

Data Cleaning Decisions

The raw CSV has several fields that don't load as usable numbers by default:

discounted_price / actual_price — stored as text with a ₹ symbol and comma thousands separators (e.g. "₹1,099"). I stripped the ₹ and commas, then converted to float.
discount_percentage — stored as a string like "64%". I stripped the % sign and converted to float.
rating — mostly numeric strings, but at least one row contains a non-numeric placeholder ("|") that breaks a direct float() conversion. I used pd.to_numeric(..., errors="coerce") so bad values become NaN instead of crashing the app, then dropped rows with a missing rating.
rating_count — stored with comma separators (e.g. "24,269") and has some missing values. I stripped commas, converted to numeric, and dropped rows that were still missing after that.

After cleaning, rows still missing discounted_price, actual_price, rating, or rating_count are dropped, since those four fields are needed for the metrics and charts in the dashboard. This drops a small number of rows (dataset goes from 1,465 to 1,462 rows) — a negligible loss relative to having reliable numbers to analyze.

I also created a main_category column by taking the first segment of the |-separated category field (e.g. "Computers&Accessories|Accessories& Peripherals|..." → "Computers&Accessories"), since the full category path is too granular to chart cleanly.

Dashboard Contents
Dataset preview (first 10 rows after cleaning)
6 summary metrics: total products, average rating, average discount, average actual price, average discounted price, number of categories
4 charts with written takeaways:
Products per category
Average rating by category
Actual vs. discounted price for the most-discounted products
Rating vs. discounted price (do higher ratings mean higher prices?)
