"""
Database module for Sales Forecasting System.
Uses SQLite to store sales transactions, forecast results, and provide fast querying.
"""

import sqlite3
import os
import pandas as pd

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")
SAMPLE_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_sales.csv")

def get_connection():
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables in the SQLite database if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Sales records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product TEXT,
            category TEXT,
            quantity INTEGER,
            unit_price REAL,
            sales REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Forecast logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecast_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            forecast_date TEXT NOT NULL,
            predicted_sales REAL NOT NULL,
            period_days INTEGER,
            mae REAL,
            rmse REAL,
            r2 REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()

def save_sales_dataframe(df, replace=False):
    """
    Saves a cleaned pandas DataFrame into the SQLite sales table.
    
    Args:
        df (pd.DataFrame): DataFrame with columns Date, Product, Category, Quantity, Unit_Price, Sales.
        replace (bool): If True, clears existing records first.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if replace:
        cursor.execute("DELETE FROM sales")

    records = []
    for _, row in df.iterrows():
        records.append((
            str(row["Date"]),
            str(row.get("Product", "General")),
            str(row.get("Category", "General")),
            int(row.get("Quantity", 1)),
            float(row.get("Unit_Price", row["Sales"])),
            float(row["Sales"])
        ))

    cursor.executemany("""
        INSERT INTO sales (date, product, category, quantity, unit_price, sales)
        VALUES (?, ?, ?, ?, ?, ?)
    """, records)

    conn.commit()
    conn.close()
    return len(records)

def get_sales_dataframe():
    """Loads all sales records from SQLite as a pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT date AS Date, product AS Product, category AS Category, quantity AS Quantity, unit_price AS Unit_Price, sales AS Sales FROM sales ORDER BY date ASC", conn)
    conn.close()
    return df

def get_recent_sales(limit=10):
    """Fetches the latest sales records for dashboard preview."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, product, category, quantity, unit_price, sales FROM sales ORDER BY date DESC, id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_sales_list(limit=500):
    """Fetches sales records for the data table view."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, product, category, quantity, unit_price, sales FROM sales ORDER BY date DESC, id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_kpi_summary():
    """Computes key summary statistics across historical sales records."""
    df = get_sales_dataframe()
    if df.empty:
        return {
            "total_sales": 0.0,
            "avg_sales": 0.0,
            "record_count": 0,
            "max_sales": 0.0,
            "min_sales": 0.0,
            "total_quantity": 0,
            "best_product": "N/A",
            "best_category": "N/A",
            "date_range": "No data"
        }

    total_sales = round(float(df["Sales"].sum()), 2)
    avg_sales = round(float(df["Sales"].mean()), 2)
    record_count = len(df)
    max_sales = round(float(df["Sales"].max()), 2)
    min_sales = round(float(df["Sales"].min()), 2)
    total_quantity = int(df["Quantity"].sum())

    # Top product by sales revenue
    product_sales = df.groupby("Product")["Sales"].sum()
    best_product = product_sales.idxmax() if not product_sales.empty else "N/A"

    # Top category by sales revenue
    cat_sales = df.groupby("Category")["Sales"].sum()
    best_category = cat_sales.idxmax() if not cat_sales.empty else "N/A"

    date_range = f"{df['Date'].min()} to {df['Date'].max()}"

    return {
        "total_sales": total_sales,
        "avg_sales": avg_sales,
        "record_count": record_count,
        "max_sales": max_sales,
        "min_sales": min_sales,
        "total_quantity": total_quantity,
        "best_product": best_product,
        "best_category": best_category,
        "date_range": date_range
    }

def get_analytics_data():
    """Aggregates sales for analytics charts: time, month, product, category."""
    df = get_sales_dataframe()
    if df.empty:
        return None

    df["Date_dt"] = pd.to_datetime(df["Date"])
    df["YearMonth"] = df["Date_dt"].dt.strftime("%Y-%m")

    # 1. Sales over time (daily)
    daily_sales = df.groupby("Date")["Sales"].sum().reset_index()
    daily_labels = daily_sales["Date"].tolist()
    daily_values = [round(float(v), 2) for v in daily_sales["Sales"]]

    # 2. Monthly sales
    monthly_sales = df.groupby("YearMonth")["Sales"].sum().reset_index()
    monthly_labels = monthly_sales["YearMonth"].tolist()
    monthly_values = [round(float(v), 2) for v in monthly_sales["Sales"]]

    # 3. Product-wise sales (Top 10)
    prod_sales = df.groupby("Product")["Sales"].sum().sort_values(ascending=False).head(10).reset_index()
    prod_labels = prod_sales["Product"].tolist()
    prod_values = [round(float(v), 2) for v in prod_sales["Sales"]]

    # 4. Category-wise sales
    cat_sales = df.groupby("Category")["Sales"].sum().sort_values(ascending=False).reset_index()
    cat_labels = cat_sales["Category"].tolist()
    cat_values = [round(float(v), 2) for v in cat_sales["Sales"]]

    return {
        "daily": {"labels": daily_labels, "values": daily_values},
        "monthly": {"labels": monthly_labels, "values": monthly_values},
        "products": {"labels": prod_labels, "values": prod_values},
        "categories": {"labels": cat_labels, "values": cat_values}
    }

def save_forecast_logs(forecast_data):
    """Saves predictions to forecast_results table."""
    conn = get_connection()
    cursor = conn.cursor()
    
    period = forecast_data.get("forecast_days", 7)
    mae = forecast_data["metrics"].get("mae", 0.0)
    rmse = forecast_data["metrics"].get("rmse", 0.0)
    r2 = forecast_data["metrics"].get("r2", 0.0)

    rows = []
    for item in forecast_data.get("forecast_results", []):
        rows.append((
            item["date"],
            item["predicted_sales"],
            period,
            mae,
            rmse,
            r2
        ))

    cursor.executemany("""
        INSERT INTO forecast_results (forecast_date, predicted_sales, period_days, mae, rmse, r2)
        VALUES (?, ?, ?, ?, ?, ?)
    """, rows)

    conn.commit()
    conn.close()

def load_sample_dataset_if_empty():
    """Auto-populates database from sample_sales.csv if sales table is empty."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0 and os.path.exists(SAMPLE_CSV):
        df = pd.read_csv(SAMPLE_CSV)
        save_sales_dataframe(df, replace=True)
        print(f"Database auto-seeded with {len(df)} sample sales records.")
