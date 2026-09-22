# Sales Forecasting System
### A Web-Based Predictive Analytics Platform using Machine Learning

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange.svg)](https://scikit-learn.org/)
[![Chart.js](https://img.shields.io/badge/Visualization-Chart.js%204.x-FF6384.svg)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/Academic-B.Tech%20IT%20Mini%20Project-success.svg)]()
[![Author](https://img.shields.io/badge/Developer-Hariharasuthan-blueviolet.svg)]()

> **Project Author:** Hariharasuthan  
> **Degree / Branch:** B.Tech Information Technology (IT)  
> **Project Type:** Mini Project (Machine Learning & Web Engineering)

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Objectives](#objectives)
4. [Key Features](#key-features)
5. [Technology Stack](#technology-stack)
6. [System Architecture](#system-architecture)
7. [Project Structure](#project-structure)
8. [Dataset Description](#dataset-description)
9. [Machine Learning Methodology](#machine-learning-methodology)
   - [Data Preprocessing & Cleaning](#data-preprocessing--cleaning)
   - [Feature Engineering (Time & Lag Features)](#feature-engineering-time--lag-features)
   - [Chronological Train/Test Splitting](#chronological-traintest-splitting)
   - [Autoregressive Multi-Step Forecasting](#autoregressive-multi-step-forecasting)
10. [Model Evaluation Metrics](#model-evaluation-metrics)
11. [Installation & Setup Guide](#installation--setup-guide)
12. [How to Run the Application](#how-to-run-the-application)
13. [Screenshots & UI Walkthrough](#screenshots--ui-walkthrough)
14. [Viva Preparation & Frequently Asked Questions](#viva-preparation--frequently-asked-questions)
15. [Future Enhancements](#future-enhancements)
16. [Conclusion](#conclusion)

---

## 1. Project Overview

The **Sales Forecasting System** is a complete, beginner-friendly web application designed for retail enterprises and store managers to analyze past sales patterns and predict future revenue. Developed as a **B.Tech IT Mini Project**, the system combines a responsive web frontend (Bootstrap 5 & Chart.js) with a Python Flask backend, SQLite database, and Scikit-Learn Machine Learning pipeline.

The model uses **Linear Regression** trained on engineered **time-based features** (day of week, month, day of year, weekend indicator) and **autoregressive lag features** (lag-1, lag-7, and 7-day rolling moving averages) to generate multi-step forecasts for **7, 14, and 30-day horizons**.

---

## 2. Problem Statement

Retail businesses face high financial risk from demand uncertainty:
- **Overstocking** leads to high warehousing holding costs, capital lockup, and product obsolescence.
- **Understocking (Stockouts)** leads to lost revenue and customer churn.
- Traditional spreadsheet or naive moving-average methods fail to capture weekly sales seasonality and trends.

There is a need for a lightweight, transparent, and easy-to-use software solution that automatically processes raw transaction data, extracts predictive signals, evaluates model accuracy, and visualizes future demand trajectories.

---

## 3. Objectives

- Develop a responsive web interface for uploading and browsing sales transaction datasets.
- Implement an automated preprocessing pipeline that cleans missing values, removes duplicates, validates schemas, and aggregates daily transactions.
- Extract temporal features and autoregressive lag indicators to give linear regression time-series predictive power.
- Train and evaluate a Scikit-Learn Linear Regression model using chronological train/test splits.
- Compute standard regression evaluation metrics: **MAE (Mean Absolute Error)**, **RMSE (Root Mean Squared Error)**, and **$R^2$ (Coefficient of Determination)**.
- Generate forecasts for 7, 14, and 30-day periods with interactive Chart.js visualizations.
- Provide clear viva-oriented explanations for academic evaluation.

---

## 4. Key Features

1. **Executive Dashboard (`/dashboard`)**:
   - Real-time KPI summaries: Total Revenue, Average Order Sales, Total Records, and Highest Single Sale.
   - Interactive 30-day recent sales trend line chart.
   - Best-selling product and top-performing category highlights.
   - 10 most recent transactions table.

2. **Sales Data Management (`/sales-data`)**:
   - Drag-and-drop CSV upload with validation.
   - Client-side live search and visible record counter.
   - One-click sample dataset reset button with 450+ realistic records.
   - Sample CSV template download for user data entry.

3. **Descriptive Sales Analytics (`/analytics`)**:
   - Daily Sales over Time (Line Chart).
   - Monthly Sales Performance (Bar Chart).
   - Category-wise Revenue Share (Doughnut Chart).
   - Top 10 Best-Selling Products (Horizontal Bar Chart).

4. **Predictive Sales Forecasting (`/forecast`)**:
   - Horizon selector: 7 Days, 14 Days, 30 Days.
   - Real-time model evaluation cards: MAE, RMSE, and $R^2$ Score with student viva tooltips.
   - Combined interactive chart: Solid blue historical sales + dotted green forecast trajectory.
   - Daily predictions table with day of the week and model estimate badge.
   - One-click CSV export of forecasted results.

5. **Academic Viva & About Guide (`/about`)**:
   - Detailed answers to examiner questions.
   - Machine learning methodology breakdown.
   - System architecture and tech stack overview.

---

## 5. Technology Stack

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | Python Flask | 3.1.x | Web server, URL routing, template rendering, and REST API |
| **Machine Learning** | Scikit-Learn | 1.9.x | Linear Regression, train/test splitting, and evaluation metrics |
| **Data Processing** | Pandas & NumPy | 2.x & 1.x | Data validation, missing value imputation, and lag generation |
| **Database** | SQLite 3 | Built-in | Persistent storage for transactions and forecast logs |
| **Frontend Framework** | HTML5, CSS3, Bootstrap | 5.3.x | Clean, responsive UI with mobile-friendly card layout |
| **Visualizations** | Chart.js | 4.4.x | Interactive client-side line, bar, horizontal bar, and doughnut charts |
| **Icons** | Bootstrap Icons | 1.11.x | Modern UI iconography |

---

## 6. System Architecture

```
+-------------------------------------------------------------------------+
|                              WEB BROWSER                                |
|  [Dashboard]   [Sales Data]   [Analytics]   [Forecast]   [About Page]   |
|         |               |           |           |                       |
|   Chart.js UI     Table Search   Chart.js   AJAX API Call & Export      |
+---------+---------------+-----------+-----------+-----------------------+
          |               |           |           |
          v               v           v           v
+-------------------------------------------------------------------------+
|                        FLASK BACKEND (app.py)                           |
|  - GET  /dashboard                                                      |
|  - POST /upload (CSV Validation & Storage)                              |
|  - GET  /analytics (Data Aggregation)                                   |
|  - GET  /api/forecast?days=7/14/30 (Model Execution)                    |
+---------------------+-------------------+-------------------------------+
                      |                   |
                      v                   v
+-----------------------------+   +---------------------------------------+
|     DATA PREPROCESSING      |   |        SQLITE DATABASE (db)           |
| (data_preprocessing.py)     |   |  - sales table                        |
|  - Schema Validation        |   |  - forecast_results table             |
|  - Missing Value Cleaning   |   +---------------------------------------+
|  - Daily Time Series Agg.   |                   |
|  - Time & Lag Features      |                   v
+--------------+--------------+   +---------------------------------------+
               |                  |         ML FORECASTING ENGINE         |
               +----------------->|      (sales_forecasting_model.py)     |
                                  |  - Chronological 80/20 Train/Test     |
                                  |  - Scikit-Learn Linear Regression     |
                                  |  - MAE, RMSE, R² Metric Evaluation    |
                                  |  - Recursive Multi-Step Forecasting   |
                                  +---------------------------------------+
```

---

## 7. Project Structure

```
sales-forecasting-system/
│
├── app.py                         # Main Flask application with routes and API endpoints
├── database.py                    # SQLite database schema, helpers, and sample auto-loader
├── requirements.txt               # Required Python packages
├── README.md                      # Comprehensive project documentation
├── test_app.py                    # Automated test suite (17 test cases)
├── generate_data.py               # Script generating realistic 450+ sample sales records
│
├── data/
│   └── sample_sales.csv           # Bundled realistic sales dataset
│
├── models/
│   ├── __init__.py
│   └── sales_forecasting_model.py # Linear Regression model with lag forecasting logic
│
├── preprocessing/
│   ├── __init__.py
│   └── data_preprocessing.py      # Validation, cleaning, daily aggregation & lag features
│
├── templates/
│   ├── base.html                  # Responsive Bootstrap 5 layout, navbar, and footer
│   ├── dashboard.html             # Overview KPI metrics, trend chart, and recent sales
│   ├── sales_data.html            # CSV upload, format guidelines, and searchable table
│   ├── analytics.html             # Chart.js analytics: time, monthly, product, category
│   ├── forecast.html              # 7/14/30-day forecasting with MAE, RMSE, R², charts
│   ├── about.html                 # Academic project details & viva preparation guide
│   └── 404.html                   # User-friendly error page
│
└── static/
    ├── css/
    │   └── style.css              # Custom styling (professional blue/white palette)
    └── js/
        └── script.js              # Chart.js rendering, AJAX forecast, search & export
```

---

## 8. Dataset Description

The system expects a CSV file containing at minimum:
- **`Date`** *(Required)*: The date of the sale in `YYYY-MM-DD` format.
- **`Sales`** *(Required)*: The numeric sales revenue for that entry.

Optional attributes that enrich descriptive analytics:
- **`Product`**: Product item name (e.g., Wireless Mouse, Air Fryer).
- **`Category`**: Product category (e.g., Electronics, Fashion, Home & Kitchen, Groceries).
- **`Quantity`**: Number of units sold.
- **`Unit_Price`**: Price per individual unit.

The bundled `data/sample_sales.csv` contains **455 realistic sales records** spanning January to July 2025 with weekend shopping spikes, seasonal variations, and a realistic upward growth trend.

---

## 9. Machine Learning Methodology

### Data Preprocessing & Cleaning
1. **Header Normalization**: Case-insensitive column renaming maps alternative names like `Amount`, `Revenue`, or `Item` to standard schema names.
2. **Missing Value Handling**: Invalid dates or negative sales are removed. Missing optional values are imputed with sensible defaults.
3. **Duplicate Removal**: Redundant identical rows are dropped.
4. **Daily Aggregation**: Raw order-level transactions are grouped by date to form a regular time series. Missing calendar dates are filled with zero sales to ensure lag calculations are unbroken.

### Feature Engineering (Time & Lag Features)
Linear regression cannot naturally model sequence orders without engineered features. We construct two groups of features:

1. **Time-Based Features**:
   - `year`, `month`, `day`: Calendar position.
   - `day_of_week` (0 = Monday, 6 = Sunday): Models intra-week seasonality.
   - `is_weekend` (1 if Saturday or Sunday, else 0): Captures weekend purchasing spikes.
   - `day_of_year`: Tracks long-term annual progression.

2. **Autoregressive Lag Features**:
   - `lag_1`: Sales revenue 1 day prior ($y_{t-1}$), capturing immediate momentum.
   - `lag_7`: Sales revenue 7 days prior ($y_{t-7}$), capturing weekly seasonality (e.g., this Monday vs. last Monday).
   - `lag_14`: Sales revenue 14 days prior ($y_{t-14}$).
   - `rolling_mean_7`: 7-day moving average of previous days ($\frac{1}{7}\sum_{i=1}^7 y_{t-i}$), smoothing random daily volatility.

### Chronological Train/Test Splitting
- Unlike standard classification tasks where data is randomly shuffled, **time series data must never be shuffled**. Shuffling causes *lookahead data leakage*, allowing the model to peek into future sales.
- We divide the dataset chronologically: the first **80%** serves as the training set, and the final **20%** serves as the unseen test set for unbiased evaluation.

### Autoregressive Multi-Step Forecasting
When forecasting into the future (e.g., day 1 to day 30):
- For day $t+1$: Features are calculated from known historical sales.
- For day $t+2$ through $t+30$: Lags for days after $t$ use the model's **own previous predictions**.
- Negative predictions are automatically bounded to zero, as sales cannot be negative.

---

## 10. Model Evaluation Metrics

The system evaluates the trained model on the chronological test split and displays three standard metrics:

### 1. MAE (Mean Absolute Error)
$$\text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|$$
- **Meaning**: Represents the average dollar amount by which predicted daily sales deviate from actual sales.
- **Viva Tip**: MAE treats all errors equally and gives a straightforward business interpretation in dollars ($).

### 2. RMSE (Root Mean Squared Error)
$$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2}$$
- **Meaning**: Penalizes larger errors more heavily due to the squaring operation before averaging.
- **Viva Tip**: If RMSE is substantially higher than MAE, it indicates the model made a few large outlier prediction mistakes.

### 3. $R^2$ Score (Coefficient of Determination)
$$R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$
- **Meaning**: Measures the proportion of variance in historical sales explained by the engineered time and lag features.
- **Viva Tip**: An $R^2$ close to 1 indicates high explanatory power, while an $R^2$ near 0 indicates performance comparable to predicting the simple historical mean.

---

## 11. Installation & Setup Guide

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed.
- Git (optional).
- VS Code (or any code editor).

### Step 1: Open Terminal in VS Code
Open the project directory in VS Code:
```bash
cd "C:\Users\Gowsi\.gemini\antigravity\scratch\sales-forecasting-system"
```

### Step 2: (Optional) Create a Virtual Environment
```bash
python -m venv venv

# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On Windows Command Prompt:
.\venv\Scripts\activate.bat
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 12. How to Run the Application

### Step 1: Run Unit Tests (Verification)
Verify that all 17 automated tests pass:
```bash
python -m unittest test_app.py
```
*Expected Output:*
```
Ran 17 tests in 0.497s
OK
```

### Step 2: Start the Flask Web Server
```bash
python app.py
```
*Expected Terminal Output:*
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 3: Open in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 13. Screenshots & UI Walkthrough

### 1. Dashboard View (`/dashboard`)
Displays four colored KPI cards (Total Revenue, Average Order, Total Records, Peak Sale), a 30-day recent sales trend chart, top-performing product/category badges, and recent transaction records.

### 2. Sales Data Management (`/sales-data`)
Provides a drag-and-drop CSV upload box, dataset validation guidelines, a live search bar, and one-click buttons to download the template or reset sample data.

### 3. Descriptive Analytics (`/analytics`)
Renders four Chart.js visualizations:
- Daily Sales Over Time (Line Chart)
- Monthly Sales Performance (Bar Chart)
- Product-Wise Sales (Horizontal Bar Chart)
- Category-Wise Sales (Doughnut Chart)

### 4. Predictive Forecasting (`/forecast`)
Features 7-day, 14-day, and 30-day horizon selector buttons, real-time MAE, RMSE, and $R^2$ score cards, a combined line chart displaying actual history vs. predicted future trajectory, an exportable predictions table, and an examiner viva card.

---

## 14. Viva Preparation & Frequently Asked Questions

#### Q1: Why did you choose Linear Regression instead of complex Deep Learning (LSTM / RNN)?
> **Answer**: For a B.Tech mini project and small-to-medium retail datasets (hundreds or thousands of records), Linear Regression with engineered lag features is lightweight, trains in milliseconds, is mathematically interpretable (coefficients can be analyzed), and avoids the severe overfitting that deep learning networks suffer from on smaller datasets.

#### Q2: What is the purpose of Lag Features in time series modeling?
> **Answer**: Standard linear models assume independent samples. By shifting past sales ($y_{t-1}, y_{t-7}$), we convert sequential historical dependency into tabular columns. `lag_1` captures short-term momentum, while `lag_7` captures weekly recurring cycles (e.g., weekend spikes).

#### Q3: Why did you use SQLite instead of MySQL or PostgreSQL?
> **Answer**: SQLite is serverless, zero-configuration, and self-contained within a single file (`database.db`). It eliminates the need to run an external database daemon, making the project portable, reproducible, and easy to run during an academic evaluation.

#### Q4: What happens if an uploaded CSV is missing required columns?
> **Answer**: The preprocessing engine in `preprocessing/data_preprocessing.py` validates the schema. If `Date` or `Sales` is missing, an informative user-friendly alert is displayed: *"Invalid dataset. Please upload a CSV containing Date and Sales columns."* without crashing the server.

#### Q5: How are predictions made 14 or 30 days into the future when lag values don't exist yet?
> **Answer**: We use an **autoregressive recursive multi-step forecasting loop**. Day 1 is predicted using actual past records. Day 1's prediction is then appended to the historical series, allowing Day 2 to use Day 1's prediction as its `lag_1` feature. This continues iteratively up to Day 30.

---

## 15. Future Enhancements

- **Ensemble Algorithms**: Implement Random Forest Regressor and XGBoost alongside Linear Regression to compare benchmark metrics.
- **External Influencing Factors**: Incorporate promotional discount flags, holiday indicators, and weather data into the feature matrix.
- **Multi-Product Forecasting**: Extend the model from store-wide daily sales to hierarchical per-SKU level forecasting.
- **PDF Report Generation**: Add a button to export forecast executive summaries and charts into a downloadable PDF report.

---

## 16. Conclusion

The **Sales Forecasting System** demonstrates how classical machine learning and sound feature engineering can be combined with modern web technologies to build an accessible, practical business intelligence tool. By implementing clean separation of concerns across preprocessing, model training, database access, and interactive UI, the project serves as a robust and easily explainable B.Tech IT mini project.
