import os
import joblib
import warnings
import pandas as pd
import numpy as np
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
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

print(f"{'Crop Name':<15} | {'Samples':<8} | {'RF R2':<12} | {'RF MSE':<12} | {'MAE':<10}")
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
    
    # Use Random Forest (better for non-linear relationships)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    rf_model = RandomForestRegressor(
        n_estimators=50,        # Reduce trees
        max_depth=5,            # Reduce depth
        min_samples_split=5,    # Increase split requirement
        min_samples_leaf=3,     # Increase leaf samples
        random_state=42
    )
    rf_model.fit(X_train_scaled, y_train)
    y_pred_rf = rf_model.predict(X_test_scaled)
    rf_r2 = r2_score(y_test, y_pred_rf)
    rf_mse = mean_squared_error(y_test, y_pred_rf)
    mae = mean_absolute_error(y_test, y_pred_rf)
    
    print(f"{crop:<15} | {len(crop_data):<8} | {rf_r2:<12.4f} | {rf_mse:<12.2f} | {mae:<10.2f}")
    
    # Save model AND scaler
    model_filename = f"models/model_{crop.replace(' ', '_').lower()}.pkl"
    scaler_filename = f"models/scaler_{crop.replace(' ', '_').lower()}.pkl"
    joblib.dump(rf_model, model_filename)
    joblib.dump(scaler, scaler_filename)

    # Feature importance
    print(f"\n  Feature Importance for {crop}:")
    print(f"    Rainfall: {rf_model.feature_importances_[0]:.4f}")
    print(f"    Temperature: {rf_model.feature_importances_[1]:.4f}")

print("\n All models trained, tested, and saved!")
print("\nRandom Forest captures non-linear relationships better than linear regression!")