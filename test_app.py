"""
Automated Test Suite for Sales Forecasting System.
Tests data preprocessing, machine learning model, database operations,
and Flask HTTP routes.
"""

import os
import io
import unittest
import pandas as pd
import numpy as np

import database
from preprocessing.data_preprocessing import (
    validate_and_clean_dataframe,
    aggregate_daily_sales,
    create_time_and_lag_features
)
from models.sales_forecasting_model import (
    SalesForecastingModel,
    run_sales_forecast
)
from app import app


class TestSalesForecastingSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Ensure sample data and database are initialized."""
        database.load_sample_dataset_if_empty()

    def setUp(self):
        """Create a test client for Flask routes."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    # -------------------------------------------------------------
    # 1. PREPROCESSING TESTS
    # -------------------------------------------------------------
    def test_valid_csv_preprocessing(self):
        dates = [f"2025-01-{i:02d}" for i in range(1, 21)]
        df_raw = pd.DataFrame({
            "Date": dates,
            "Sales": [100.0 + i * 5 for i in range(20)],
            "Product": [f"Item {i % 4}" for i in range(20)],
            "Category": ["Cat 1" if i % 2 == 0 else "Cat 2" for i in range(20)],
            "Quantity": [(i % 3) + 1 for i in range(20)],
            "Unit_Price": [50.0 for _ in range(20)]
        })
        clean_df, err = validate_and_clean_dataframe(df_raw)
        self.assertIsNone(err)
        self.assertIsNotNone(clean_df)
        self.assertEqual(len(clean_df), 20)
        self.assertIn("Date", clean_df.columns)
        self.assertIn("Sales", clean_df.columns)

    def test_missing_required_columns_validation(self):
        # Missing Date column
        df_invalid = pd.DataFrame({
            "Product": ["Mouse", "Keyboard"],
            "Sales": [25.0, 50.0]
        })
        clean_df, err = validate_and_clean_dataframe(df_invalid)
        self.assertIsNone(clean_df)
        self.assertIn("Invalid dataset", err)
        self.assertIn("Date and Sales", err)

        # Missing Sales column
        df_no_sales = pd.DataFrame({
            "Date": ["2025-01-01", "2025-01-02"],
            "Product": ["Mouse", "Keyboard"]
        })
        clean_df, err = validate_and_clean_dataframe(df_no_sales)
        self.assertIsNone(clean_df)
        self.assertIn("Invalid dataset", err)

    def test_daily_aggregation_and_continuous_dates(self):
        df_sparse = pd.DataFrame({
            "Date": ["2025-01-01", "2025-01-03"],
            "Sales": [100.0, 300.0],
            "Quantity": [1, 3]
        })
        daily = aggregate_daily_sales(df_sparse)
        # Should fill Jan 2nd with 0 sales
        self.assertEqual(len(daily), 3)
        jan2_row = daily[daily["Date_str"] == "2025-01-02"]
        self.assertEqual(float(jan2_row["Sales"].iloc[0]), 0.0)

    def test_feature_engineering_lags_and_time(self):
        df = database.get_sales_dataframe()
        daily = aggregate_daily_sales(df)
        features_df, feature_cols = create_time_and_lag_features(daily)

        expected_features = [
            "year", "month", "day", "day_of_week", "is_weekend", "day_of_year",
            "lag_1", "lag_7", "lag_14", "rolling_mean_7"
        ]
        for f in expected_features:
            self.assertIn(f, feature_cols)
            self.assertIn(f, features_df.columns)
        self.assertFalse(features_df[feature_cols].isnull().any().any())

    # -------------------------------------------------------------
    # 2. MODEL FORECASTING TESTS
    # -------------------------------------------------------------
    def test_forecasting_pipeline_7_14_30_days(self):
        df = database.get_sales_dataframe()
        for days in [7, 14, 30]:
            res = run_sales_forecast(df, forecast_days=days)
            self.assertEqual(res["forecast_days"], days)
            self.assertEqual(len(res["forecast_results"]), days)
            self.assertIn("mae", res["metrics"])
            self.assertIn("rmse", res["metrics"])
            self.assertIn("r2", res["metrics"])
            self.assertGreater(res["total_forecasted_sales"], 0)
            self.assertGreater(res["avg_forecasted_sales"], 0)
            # Ensure predictions are positive
            for item in res["forecast_results"]:
                self.assertGreaterEqual(item["predicted_sales"], 0.0)
                self.assertIn("date", item)
                self.assertIn("day_name", item)

    # -------------------------------------------------------------
    # 3. DATABASE OPERATIONS TESTS
    # -------------------------------------------------------------
    def test_database_kpi_summary(self):
        kpi = database.get_kpi_summary()
        self.assertGreater(kpi["record_count"], 0)
        self.assertGreater(kpi["total_sales"], 0)
        self.assertNotEqual(kpi["best_product"], "N/A")
        self.assertNotEqual(kpi["best_category"], "N/A")

    def test_database_recent_sales(self):
        recent = database.get_recent_sales(limit=5)
        self.assertEqual(len(recent), 5)
        self.assertIn("date", recent[0])
        self.assertIn("sales", recent[0])

    # -------------------------------------------------------------
    # 4. FLASK ROUTES AND API TESTS
    # -------------------------------------------------------------
    def test_index_redirects_to_dashboard(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard", response.headers["Location"])

    def test_dashboard_route(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sales Forecasting System", response.data)
        self.assertIn(b"Executive Sales Dashboard", response.data)

    def test_sales_data_route(self):
        response = self.client.get("/sales-data")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sales Data Management", response.data)

    def test_analytics_route(self):
        response = self.client.get("/analytics")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sales Analytics", response.data)

    def test_forecast_route(self):
        response = self.client.get("/forecast")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Predictive Sales Forecasting", response.data)

    def test_about_route(self):
        response = self.client.get("/about")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"B.Tech IT Mini Project", response.data)
        self.assertIn(b"What is Sales Forecasting?", response.data)

    def test_download_sample_route(self):
        response = self.client.get("/download-sample")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response.headers["Content-Type"])

    def test_api_forecast_endpoints(self):
        for days in [7, 14, 30]:
            response = self.client.get(f"/api/forecast?days={days}")
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data["forecast_days"], days)
            self.assertEqual(len(data["forecast_results"]), days)
            self.assertIn("metrics", data)
            self.assertIn("mae", data["metrics"])

    def test_csv_upload_validation_error(self):
        # Upload empty / malformed CSV
        invalid_csv_data = io.BytesIO(b"Col1,Col2\nVal1,Val2\n")
        response = self.client.post(
            "/upload",
            data={"csv_file": (invalid_csv_data, "bad.csv")},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid dataset", response.data)

    def test_load_sample_route(self):
        response = self.client.get("/load-sample", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Database successfully restored", response.data)


if __name__ == "__main__":
    unittest.main()
