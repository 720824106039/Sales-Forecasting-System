"""
Sales Forecasting System
A web-based predictive analytics platform built with Flask, Scikit-Learn, and Chart.js.
Suitable for a B.Tech IT Mini Project.
"""

import os
import json
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file

import database
from preprocessing.data_preprocessing import validate_and_clean_dataframe
from models.sales_forecasting_model import run_sales_forecast

app = Flask(__name__)
app.secret_key = "sales-forecasting-secret-key-btech-mini-project"

# Ensure SQLite tables and sample data are ready at launch
database.load_sample_dataset_if_empty()


@app.route("/")
def index():
    """Redirect root path directly to dashboard."""
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    """
    Dashboard view: displays high-level KPIs, 30-day recent trend chart,
    and the 10 most recent transactions.
    """
    kpi = database.get_kpi_summary()
    recent_sales = database.get_recent_sales(limit=10)

    # Prepare 30-day trend chart for the dashboard
    df = database.get_sales_dataframe()
    trend_chart = {"labels": [], "values": []}

    if not df.empty:
        df["Date_dt"] = pd.to_datetime(df["Date"])
        daily_trend = df.groupby("Date")["Sales"].sum().reset_index().tail(30)
        trend_chart["labels"] = daily_trend["Date"].tolist()
        trend_chart["values"] = [round(float(v), 2) for v in daily_trend["Sales"]]

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        kpi=kpi,
        recent_sales=recent_sales,
        trend_chart_json=json.dumps(trend_chart)
    )


@app.route("/sales-data")
def sales_data():
    """
    Sales Data Management view: displays table of records, upload interface,
    and download/reset controls.
    """
    records = database.get_all_sales_list(limit=1000)
    kpi = database.get_kpi_summary()

    return render_template(
        "sales_data.html",
        active_page="sales_data",
        sales_records=records,
        total_records=kpi["record_count"]
    )


@app.route("/upload", methods=["POST"])
def upload_csv():
    """
    Handles CSV file upload, performs validation & cleaning,
    and updates the database.
    """
    if "csv_file" not in request.files:
        flash("No file part provided in the request.", "danger")
        return redirect(url_for("sales_data"))

    file = request.files["csv_file"]
    if file.filename == "":
        flash("No file selected. Please choose a valid CSV file.", "warning")
        return redirect(url_for("sales_data"))

    if not file.filename.lower().endswith(".csv"):
        flash("Invalid file type. Please upload a standard CSV (.csv) file.", "danger")
        return redirect(url_for("sales_data"))

    try:
        raw_df = pd.read_csv(file)
    except Exception as e:
        flash(f"Error reading CSV file: {str(e)}", "danger")
        return redirect(url_for("sales_data"))

    cleaned_df, error = validate_and_clean_dataframe(raw_df)
    if error:
        flash(error, "danger")
        return redirect(url_for("sales_data"))

    replace_existing = request.form.get("replace_existing") == "yes"
    records_saved = database.save_sales_dataframe(cleaned_df, replace=replace_existing)

    action_text = "replaced all existing records with" if replace_existing else "appended"
    flash(f"Success! Successfully {action_text} {records_saved} cleaned sales records.", "success")
    return redirect(url_for("sales_data"))


@app.route("/load-sample")
def load_sample():
    """Resets database with the bundled realistic sample dataset."""
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_sales.csv")
    if not os.path.exists(sample_path):
        flash("Sample dataset file not found on server.", "danger")
        return redirect(url_for("sales_data"))

    try:
        df = pd.read_csv(sample_path)
        cleaned_df, error = validate_and_clean_dataframe(df)
        if error:
            flash(f"Error validating sample data: {error}", "danger")
            return redirect(url_for("sales_data"))

        count = database.save_sales_dataframe(cleaned_df, replace=True)
        flash(f"Database successfully restored with {count} sample sales records.", "success")
    except Exception as e:
        flash(f"Failed to reset sample data: {str(e)}", "danger")

    return redirect(url_for("sales_data"))


@app.route("/download-sample")
def download_sample():
    """Allows user to download the sample CSV template."""
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_sales.csv")
    if os.path.exists(sample_path):
        return send_file(sample_path, as_attachment=True, download_name="sample_sales_template.csv", mimetype="text/csv")
    flash("Sample file not available for download.", "warning")
    return redirect(url_for("sales_data"))


@app.route("/analytics")
def analytics():
    """
    Analytics view: renders summary performance cards and
    Chart.js visualizations for time, products, and categories.
    """
    kpi = database.get_kpi_summary()
    analytics_data = database.get_analytics_data()

    if not analytics_data:
        flash("No sales data available to analyze. Please upload data or load the sample dataset.", "warning")
        return redirect(url_for("sales_data"))

    return render_template(
        "analytics.html",
        active_page="analytics",
        kpi=kpi,
        analytics_json=json.dumps(analytics_data)
    )


@app.route("/forecast")
def forecast():
    """
    Forecasting view: renders prediction controls, metrics cards,
    and future forecast charts.
    """
    kpi = database.get_kpi_summary()
    if kpi["record_count"] < 15:
        flash("Insufficient sales records to train the forecasting model. At least 15 daily records are needed.", "warning")
        return redirect(url_for("sales_data"))

    return render_template(
        "forecast.html",
        active_page="forecast",
        kpi=kpi
    )


@app.route("/api/forecast")
def api_forecast():
    """
    REST API endpoint: trains the Linear Regression model on current sales data
    and generates multi-step predictions for 7, 14, or 30 days.
    """
    days = request.args.get("days", default=7, type=int)
    if days not in [7, 14, 30]:
        days = 7

    df = database.get_sales_dataframe()
    if df.empty or len(df) < 15:
        return jsonify({"error": "Insufficient sales data in database to train model (minimum 15 records required)."}), 400

    try:
        forecast_output = run_sales_forecast(df, forecast_days=days)
        # Log results to SQLite database
        database.save_forecast_logs(forecast_output)
        return jsonify(forecast_output)
    except Exception as e:
        return jsonify({"error": f"Model training/prediction failed: {str(e)}"}), 500


@app.route("/about")
def about():
    """About view: detailed project documentation, architecture, and viva questions."""
    return render_template("about.html", active_page="about")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error occurred."}), 500


if __name__ == "__main__":
    # Host on 127.0.0.1:5000 with debug mode enabled for development
    app.run(host="127.0.0.1", port=5000, debug=True)
