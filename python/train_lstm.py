import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
from tensorflow.keras import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib
import os

# ── Load Mumbai data ──────────────────────────────────────────
df = pd.read_csv("data/city_hour.csv")
df = df[df["City"] == "Mumbai"]
print("Mumbai shape:", df.shape)

# ── Keep needed columns ───────────────────────────────────────
df = df[["Datetime", "PM2.5", "PM10", "NO2", "AQI"]]
df = df.dropna(subset=["PM2.5", "AQI"])
df = df[df["PM2.5"] > 0]
df = df[df["AQI"] > 0]

df["PM10"] = df["PM10"].fillna(df["PM10"].median())
df["NO2"]  = df["NO2"].fillna(df["NO2"].median())

# ── Parse datetime ────────────────────────────────────────────
df["Datetime"] = pd.to_datetime(df["Datetime"])
df = df.sort_values("Datetime").reset_index(drop=True)

# ── Add seasonal features ─────────────────────────────────────
# These are what let LSTM understand WHY winter has higher AQI
df["hour"]        = df["Datetime"].dt.hour
df["month"]       = df["Datetime"].dt.month
df["day_of_week"] = df["Datetime"].dt.dayofweek

# Winter flag — Oct to Feb is high pollution season in Mumbai
df["is_winter"]   = df["month"].apply(
    lambda m: 1 if m in [10, 11, 12, 1, 2] else 0
)

# Rolling mean — captures recent trend
df["rolling_6h"]  = df["AQI"].rolling(window=6, min_periods=1).mean()

print("\nSeasonal AQI by month (shows winter pattern):")
print(df.groupby("month")["AQI"].mean().round(1))

# ── Features for LSTM ─────────────────────────────────────────
feature_cols = ["PM2.5", "PM10", "NO2", "hour",
                "month", "day_of_week", "is_winter", "rolling_6h"]
target_col   = "AQI"

# ── Scale data ────────────────────────────────────────────────
# LSTM needs values between 0 and 1
feature_scaler = MinMaxScaler()
target_scaler  = MinMaxScaler()

features_scaled = feature_scaler.fit_transform(df[feature_cols])
target_scaled   = target_scaler.fit_transform(df[[target_col]])

print("\nFeatures scaled. Shape:", features_scaled.shape)

# ── Create sequences ──────────────────────────────────────────
# LSTM looks at last 24 hours to predict next 24 hours
SEQ_LEN     = 24   # look back 24 hours
PRED_LEN    = 24   # predict next 24 hours

def create_sequences(features, target, seq_len, pred_len):
    X, y = [], []
    for i in range(len(features) - seq_len - pred_len):
        X.append(features[i : i + seq_len])
        y.append(target[i + seq_len : i + seq_len + pred_len])
    return np.array(X), np.array(y)

X, y = create_sequences(features_scaled, target_scaled,
                         SEQ_LEN, PRED_LEN)

print(f"Sequences created — X: {X.shape}, y: {y.shape}")

# ── Train/test split ──────────────────────────────────────────
split     = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

print(f"Train: {len(X_train)} sequences")
print(f"Test:  {len(X_test)} sequences")

# ── Build LSTM model ──────────────────────────────────────────
model = Sequential([
    LSTM(64, return_sequences=True,
         input_shape=(SEQ_LEN, len(feature_cols))),
    Dropout(0.2),
    LSTM(32, return_sequences=False),
    Dropout(0.2),
    Dense(PRED_LEN)   # output = 24 future AQI values
])

model.compile(optimizer='adam', loss='mse')
model.summary()

# ── Train ─────────────────────────────────────────────────────
print("\nTraining LSTM... (may take 3-5 mins)")
history = model.fit(
    X_train, y_train,
    epochs          = 20,
    batch_size      = 32,
    validation_split = 0.1,
    verbose         = 1
)

# ── Evaluate ──────────────────────────────────────────────────
y_pred_scaled = model.predict(X_test)

# Inverse transform to get real AQI values
y_pred_flat = y_pred_scaled.reshape(-1, 1)
y_test_flat = y_test.reshape(-1, 1)

y_pred_real = target_scaler.inverse_transform(y_pred_flat)
y_test_real = target_scaler.inverse_transform(y_test_flat)

mae = mean_absolute_error(y_test_real, y_pred_real)
print(f"\nLSTM MAE: {mae:.2f} AQI units")

# ── Save model and scalers ────────────────────────────────────
model.save("lstm_model.h5")
joblib.dump(feature_scaler, "lstm_feature_scaler.pkl")
joblib.dump(target_scaler,  "lstm_target_scaler.pkl")

print("\nlstm_model.h5 saved!")
print("lstm_feature_scaler.pkl saved!")
print("lstm_target_scaler.pkl saved!")

# ── Show seasonal insight ─────────────────────────────────────
print("\n── Seasonal AQI Pattern (what LSTM learned) ────")
monthly = df.groupby("month")["AQI"].mean().round(1)
seasons = {
    1: "Jan (Winter)", 2: "Feb (Winter)",
    3: "Mar (Spring)", 4: "Apr (Spring)",
    5: "May (Summer)", 6: "Jun (Monsoon)",
    7: "Jul (Monsoon)", 8: "Aug (Monsoon)",
    9: "Sep (Post-Monsoon)", 10: "Oct (Post-Monsoon)",
    11: "Nov (Winter)", 12: "Dec (Winter)"
}
for month, aqi in monthly.items():
    print(f"  {seasons[month]}: AQI {aqi}")