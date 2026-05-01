import os
import joblib
import warnings
import pandas as pd
import numpy as np
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

try:
    from import_data import df
except ImportError as e:
    print(f"Error importing data: {e}")
    exit(1)

# Create models directory
if not os.path.exists('models'):
    os.makedirs('models')

print("\n--- Data Quality Check ---")
print(f"Total rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}\n")

# Analyze weather features distribution
print("Weather Features Statistics:")
print(df[['rainfall', 'avg_temperature']].describe())
print(f"\nRainfall range: {df['rainfall'].min():.2f} to {df['rainfall'].max():.2f}")
print(f"Temperature range: {df['avg_temperature'].min():.2f} to {df['avg_temperature'].max():.2f}")
print(f"Yield range: {df['yield'].min():.2f} to {df['yield'].max():.2f}")

print(f"{'Crop Name':<15} | {'Samples':<8} | {'Linear R2':<12} | {'Ridge R2':<12} | {'MSE':<12} | {'MAE':<10}")
print("-" * 85)

# Loop through each crop to train and test
for crop in df['crop_name'].unique():
    crop_data = df[df['crop_name'] == crop]
    
    if len(crop_data) < 10:
        print(f"{crop:<15} | {len(crop_data):<8} | Insufficient data (need ≥10)")
        continue

    X = crop_data[['rainfall', 'avg_temperature']].reset_index(drop=True)
    y = crop_data['yield'].reset_index(drop=True)
    
    # Check for missing values
    if X.isnull().any().any() or y.isnull().any():
        print(f"{crop:<15} | {len(crop_data):<8} | Contains NaN values, skipping")
        continue
    
    # Remove outliers using IQR method
    Q1 = y.quantile(0.25)
    Q3 = y.quantile(0.75)
    IQR = Q3 - Q1
    y_filtered = y[(y >= Q1 - 1.5*IQR) & (y <= Q3 + 1.5*IQR)]
    X_filtered = X.loc[y_filtered.index]
    
    if len(X_filtered) < 5:
        print(f"{crop:<15} | {len(crop_data):<8} | Too few samples after outlier removal")
        continue
    
    X_train, X_test, y_train, y_test = train_test_split(X_filtered, y_filtered, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # LINEAR MODEL
    linear_model = LinearRegression()
    linear_model.fit(X_train_scaled, y_train)
    y_pred_linear = linear_model.predict(X_test_scaled)
    linear_r2 = r2_score(y_test, y_pred_linear)
    linear_mse = mean_squared_error(y_test, y_pred_linear)
    
    # RIDGE MODEL (regularization)
    ridge_model = Ridge(alpha=10.0)
    ridge_model.fit(X_train_scaled, y_train)
    y_pred_ridge = ridge_model.predict(X_test_scaled)
    ridge_r2 = r2_score(y_test, y_pred_ridge)
    ridge_mse = mean_squared_error(y_test, y_pred_ridge)
    mae = mean_absolute_error(y_test, y_pred_ridge)
    
    # Choose better model
    best_model = ridge_model if ridge_r2 > linear_r2 else linear_model
    
    print(f"{crop:<15} | {len(crop_data):<8} | {linear_r2:<12.4f} | {ridge_r2:<12.4f} | {ridge_mse:<12.2f} | {mae:<10.2f}")
    
    # Save the better model with scaler
    filename = f"models/model_{crop.replace(' ', '_').lower()}.pkl"
    scaler_file = f"models/scaler_{crop.replace(' ', '_').lower()}.pkl"
    joblib.dump(best_model, filename)
    joblib.dump(scaler, scaler_file)

    print(f"\n  Coefficients for {crop}:")
    print(f"    Rainfall: {best_model.coef_[0]:.6f}")
    print(f"    Temperature: {best_model.coef_[1]:.6f}")
    print(f"    Intercept: {best_model.intercept_:.2f}")

print("\n All models trained, tested, and saved!")
print("\nModel coefficients show:")
print(" Positive coefficient = more rainfall/heat increases yield")
print(" Negative coefficient = less rainfall/heat increases yield")