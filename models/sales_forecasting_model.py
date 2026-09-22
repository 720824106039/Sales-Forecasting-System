"""
Sales Forecasting Model using Scikit-Learn Linear Regression.
Features:
- Time-based features (year, month, day, day of week, weekend, day of year)
- Autoregressive lag features (lag 1, lag 7, lag 14, 7-day rolling mean)
- Chronological train/test split for realistic time-series evaluation
- Evaluation metrics: MAE, RMSE, R-squared
- Recursive multi-step forecasting for 7, 14, and 30-day horizons
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from preprocessing.data_preprocessing import (
    aggregate_daily_sales,
    create_time_and_lag_features
)

class SalesForecastingModel:
    def __init__(self):
        self.model = LinearRegression()
        self.feature_cols = []
        self.metrics = {}
        self.is_trained = False
        self.feature_importance = {}

    def train_and_evaluate(self, daily_df):
        """
        Trains the Linear Regression model on chronological time-series data
        and evaluates performance using MAE, RMSE, and R2.
        
        Args:
            daily_df (pd.DataFrame): Daily aggregated sales dataframe with 'Date' and 'Sales'.
            
        Returns:
            dict: Evaluation metrics and training summary.
        """
        features_df, feature_cols = create_time_and_lag_features(daily_df)
        self.feature_cols = feature_cols

        if len(features_df) < 10:
            raise ValueError(
                f"Insufficient historical data points ({len(features_df)} valid feature rows). "
                "At least 25 daily records are required to build lag features and train."
            )

        # Chronological train/test split (80% train, 20% test)
        # In time series, we never shuffle data to prevent lookahead data leakage
        split_idx = int(len(features_df) * 0.8)
        # Ensure test set has at least 5 points if possible
        if len(features_df) - split_idx < 5:
            split_idx = max(5, len(features_df) - 5)

        train_df = features_df.iloc[:split_idx]
        test_df = features_df.iloc[split_idx:]

        X_train = train_df[feature_cols]
        y_train = train_df["Sales"]
        X_test = test_df[feature_cols]
        y_test = test_df["Sales"]

        # Train model on training split for evaluation
        eval_model = LinearRegression()
        eval_model.fit(X_train, y_train)

        # Evaluate on test set
        y_pred = eval_model.predict(X_test)
        
        # Calculate performance metrics
        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2 = float(r2_score(y_test, y_pred))

        # Retrain model on full feature set to produce the most accurate future forecasts
        self.model.fit(features_df[feature_cols], features_df["Sales"])
        self.is_trained = True

        # Extract feature importance (coefficients)
        self.feature_importance = {
            col: round(float(coef), 4)
            for col, coef in zip(feature_cols, self.model.coef_)
        }

        self.metrics = {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "r2": round(r2, 4),
            "train_samples": len(train_df),
            "test_samples": len(test_df),
            "total_samples": len(features_df)
        }

        return self.metrics

    def predict_future(self, daily_df, forecast_days=7):
        """
        Recursively forecasts sales for the next N days.
        Dynamically updates lag features and rolling averages as each day is predicted.
        
        Args:
            daily_df (pd.DataFrame): Daily historical sales.
            forecast_days (int): Forecast horizon (7, 14, or 30).
            
        Returns:
            list of dict: Forecast records with date, day_of_week, and predicted_sales.
        """
        if not self.is_trained:
            raise RuntimeError("Model has not been trained yet. Call train_and_evaluate first.")

        forecast_days = int(forecast_days)
        if forecast_days not in [7, 14, 30]:
            forecast_days = 7

        # Working history of sales: dictionary of date -> sales
        # Sorted by date
        sorted_daily = daily_df.sort_values(by="Date").copy()
        history_dates = list(sorted_daily["Date"])
        history_sales = list(sorted_daily["Sales"])

        # Create quick lookup
        sales_history = {d: s for d, s in zip(history_dates, history_sales)}
        last_date = history_dates[-1]

        forecast_results = []
        simulated_sales = list(history_sales)

        for step in range(1, forecast_days + 1):
            next_date = last_date + timedelta(days=step)
            next_date_str = next_date.strftime("%Y-%m-%d")

            # 1. Compute time-based features
            year = next_date.year
            month = next_date.month
            day = next_date.day
            day_of_week = next_date.weekday()
            is_weekend = 1 if day_of_week in [5, 6] else 0
            day_of_year = next_date.timetuple().tm_yday

            # 2. Compute lag features using simulated sales history
            lag_1 = simulated_sales[-1]
            lag_7 = simulated_sales[-7] if len(simulated_sales) >= 7 else simulated_sales[0]
            lag_14 = simulated_sales[-14] if len(simulated_sales) >= 14 else simulated_sales[0]
            
            # 7-day rolling mean
            window_7 = simulated_sales[-7:]
            rolling_mean_7 = float(np.mean(window_7)) if len(window_7) > 0 else lag_1

            feature_dict = {
                "year": year,
                "month": month,
                "day": day,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "day_of_year": day_of_year,
                "lag_1": lag_1,
                "lag_7": lag_7,
                "lag_14": lag_14,
                "rolling_mean_7": rolling_mean_7
            }

            # Align with model feature order
            x_step = pd.DataFrame([feature_dict])[self.feature_cols]

            # Predict sales
            pred = float(self.model.predict(x_step)[0])
            pred_sale = max(0.0, round(pred, 2))  # Sales cannot be negative

            # Add to simulation history for future lags
            simulated_sales.append(pred_sale)

            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            forecast_results.append({
                "date": next_date_str,
                "day_name": day_names[day_of_week],
                "predicted_sales": pred_sale
            })

        return forecast_results


def run_sales_forecast(df, forecast_days=7):
    """
    Convenience wrapper to run complete forecasting pipeline from raw sales dataframe.
    
    Returns:
        dict: Complete forecast output containing historical data, forecasts, metrics, and summary.
    """
    daily_df = aggregate_daily_sales(df)
    forecaster = SalesForecastingModel()
    metrics = forecaster.train_and_evaluate(daily_df)
    future_forecast = forecaster.predict_future(daily_df, forecast_days)

    total_forecasted_sales = round(sum(item["predicted_sales"] for item in future_forecast), 2)
    avg_forecasted_sales = round(total_forecasted_sales / len(future_forecast), 2)

    # Prepare historical data for visualization (last 60 days to keep chart clear)
    historical_chart_data = []
    display_daily = daily_df.tail(60)
    for _, row in display_daily.iterrows():
        historical_chart_data.append({
            "date": row["Date_str"],
            "sales": round(float(row["Sales"]), 2)
        })

    return {
        "metrics": metrics,
        "forecast_days": forecast_days,
        "forecast_results": future_forecast,
        "total_forecasted_sales": total_forecasted_sales,
        "avg_forecasted_sales": avg_forecasted_sales,
        "historical_chart_data": historical_chart_data,
        "feature_importance": forecaster.feature_importance,
        "summary": "Based on historical sales patterns, the system forecasts the expected sales for the selected future period."
    }
