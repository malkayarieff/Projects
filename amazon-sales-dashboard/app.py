import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------------------------------------
# Page setup
# ---------------------------------------------------------
st.set_page_config(page_title="Amazon Sales Dashboard", layout="wide")

st.title("Amazon Sales Data Dashboard")
st.write(
    "This dashboard explores a dataset of Amazon products (mostly electronics) "
    "to understand pricing, discounts, ratings, and categories. "
    "Use it to see which categories sell the most, which products offer the "
    "biggest discounts, and whether higher ratings relate to higher prices."
)

# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/raw/amazon.csv")

    # --- Clean discounted_price and actual_price ---
    # These are stored as text like "₹1,099". Strip the ₹ symbol and commas,
    # then convert to float. Rows that still fail to convert become NaN and
    # are dropped, since a product without a valid price can't be analyzed.
    for col in ["discounted_price", "actual_price"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Clean discount_percentage ---
    # Stored as text like "64%". Strip the % sign and convert to float.
    df["discount_percentage"] = (
        df["discount_percentage"].astype(str).str.replace("%", "", regex=False)
    )
    df["discount_percentage"] = pd.to_numeric(df["discount_percentage"], errors="coerce")

    # --- Clean rating ---
    # At least one row has a non-numeric placeholder (e.g. "|") instead of a
    # number. errors="coerce" turns any bad value into NaN instead of crashing,
    # and we drop those rows since a product with no real rating can't be
    # used in rating-based analysis.
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    # --- Clean rating_count ---
    # Stored as text with commas (e.g. "24,269") and has some missing values.
    df["rating_count"] = (
        df["rating_count"].astype(str).str.replace(",", "", regex=False)
    )
    df["rating_count"] = pd.to_numeric(df["rating_count"], errors="coerce")

    # --- Category ---
    # The category field is a "|"-separated path (e.g. "Computers&Accessories|
    # Accessories&Peripherals|..."). We use the first segment as the
    # top-level category, which is more readable for charts.
    df["main_category"] = df["category"].astype(str).str.split("|").str[0]

    # Drop rows missing the core numeric fields we depend on for analysis.
    before = len(df)
    df = df.dropna(subset=["discounted_price", "actual_price", "rating", "rating_count"])
    after = len(df)

    return df, before, after


df, rows_before, rows_after = load_data()

# ---------------------------------------------------------
# Dataset preview
# ---------------------------------------------------------
st.header("Dataset Preview")
st.write(
    f"Loaded **{rows_before}** rows from the raw file. After cleaning prices, "
    f"ratings, and review counts, **{rows_after}** rows remain with complete, "
    f"usable data ({rows_before - rows_after} rows were dropped for missing "
    "or invalid values)."
)
st.dataframe(df.head(10))

# ---------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------
st.header("Summary Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("Total Products", f"{len(df):,}")
col2.metric("Average Rating", f"{df['rating'].mean():.2f} / 5")
col3.metric("Average Discount", f"{df['discount_percentage'].mean():.0f}%")

col4, col5, col6 = st.columns(3)
col4.metric("Average Actual Price", f"₹{df['actual_price'].mean():,.0f}")
col5.metric("Average Discounted Price", f"₹{df['discounted_price'].mean():,.0f}")
col6.metric("Categories Represented", f"{df['main_category'].nunique()}")

# ---------------------------------------------------------
# Chart 1: Which categories have the most products?
# ---------------------------------------------------------
st.header("Chart 1: Products per Category")

category_counts = (
    df["main_category"].value_counts().head(10).reset_index()
)
category_counts.columns = ["Category", "Product Count"]

fig1 = px.bar(
    category_counts,
    x="Product Count",
    y="Category",
    orientation="h",
    title="Top 10 Categories by Number of Products",
)
fig1.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig1, use_container_width=True)

st.write(
    "The dataset is heavily concentrated in a small number of categories, "
    "with electronics-related categories dominating the product count. "
    "This tells us the dataset skews toward tech accessories rather than "
    "a broad mix of retail products."
)

# ---------------------------------------------------------
# Chart 2: Which categories have the highest average ratings?
# ---------------------------------------------------------
st.header("Chart 2: Average Rating by Category")

rating_by_category = (
    df.groupby("main_category")["rating"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
rating_by_category.columns = ["Category", "Average Rating"]

fig2 = px.bar(
    rating_by_category,
    x="Average Rating",
    y="Category",
    orientation="h",
    title="Top 10 Categories by Average Rating",
    range_x=[0, 5],
)
fig2.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig2, use_container_width=True)

st.write(
    "Average ratings across categories are fairly close together and mostly "
    "sit above 4.0, suggesting that products in this dataset are generally "
    "well-reviewed. Categories with only a few products can show unusually "
    "high or low averages, since one review has more impact on a small sample."
)

# ---------------------------------------------------------
# Chart 3: Actual price vs discounted price (biggest discounts)
# ---------------------------------------------------------
st.header("Chart 3: Actual Price vs. Discounted Price")

top_discounts = df.sort_values("discount_percentage", ascending=False).head(15)

fig3 = px.scatter(
    top_discounts,
    x="actual_price",
    y="discounted_price",
    size="discount_percentage",
    color="main_category",
    hover_name="product_name",
    title="Top 15 Products by Discount Percentage: Actual vs. Discounted Price",
    labels={"actual_price": "Actual Price (₹)", "discounted_price": "Discounted Price (₹)"},
)
st.plotly_chart(fig3, use_container_width=True)

st.write(
    "Among the most heavily discounted products, the gap between actual "
    "and discounted price is large, with some items discounted by well over "
    "50%. Higher original prices don't guarantee a bigger discount, so "
    "shoppers should compare discount percentage directly rather than "
    "assuming expensive items are marked down the most."
)

# ---------------------------------------------------------
# Chart 4: Are higher-rated products more expensive?
# ---------------------------------------------------------
st.header("Chart 4: Rating vs. Discounted Price")

fig4 = px.scatter(
    df,
    x="rating",
    y="discounted_price",
    color="main_category",
    hover_name="product_name",
    title="Product Rating vs. Discounted Price",
    labels={"rating": "Rating (out of 5)", "discounted_price": "Discounted Price (₹)"},
    opacity=0.6,
)
st.plotly_chart(fig4, use_container_width=True)

st.write(
    "There is no strong relationship between rating and price in this "
    "dataset — both cheap and expensive products can be rated highly. "
    "This suggests customers are rating based on product quality and value "
    "rather than simply rating expensive items higher."
)

st.caption("Data source: Amazon Sales Dataset (Kaggle) — amazon.csv")
