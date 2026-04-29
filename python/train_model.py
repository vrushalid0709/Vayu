import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

# Load dataset 
df = pd.read_csv("data/city_hour.csv")

# Check what cities exist 
print("All cities:", df["City"].unique())
print("Total shape:", df.shape)

# Filter Mumbai 
df = df[df["City"] == "Mumbai"]
print("Mumbai shape:", df.shape)

# Keep only needed columns 
df = df[["Datetime", "PM2.5", "PM10", "NO2", "AQI"]]

# Clean 
df = df.dropna(subset=["PM2.5", "AQI"])
df = df[df["PM2.5"] > 0]
df = df[df["AQI"] > 0]

df["PM10"] = df["PM10"].fillna(df["PM10"].median())
df["NO2"]  = df["NO2"].fillna(df["NO2"].median())

# Extract hour 
df["hour"] = pd.to_datetime(df["Datetime"]).dt.hour

# Current AQI as feature 
df["AQI_now"] = df["AQI"]

# Shift to create future targets 
df["AQI_1h"] = df["AQI_now"].shift(-1)
df["AQI_2h"] = df["AQI_now"].shift(-2)
df["AQI_3h"] = df["AQI_now"].shift(-3)

# Drop rows with no future values
df = df.dropna()

print("Clean shape:", df.shape)
print("\nSample:")
print(df[["PM2.5", "PM10", "NO2", "hour",
          "AQI_now", "AQI_1h", "AQI_2h", "AQI_3h"]].head(5))

# Features 
X = df[["PM2.5", "PM10", "NO2", "hour", "AQI_now"]]

#  Train 3 models, one per future hour 
results = {}
models  = {}

for target, col in [("1h", "AQI_1h"), ("2h", "AQI_2h"), ("3h", "AQI_3h")]:

    y = df[col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\nTraining model +{target}...")
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1       
    )
    model.fit(X_train, y_train)

    mae = mean_absolute_error(y_test, model.predict(X_test))
    print(f"Done! MAE: {mae:.2f} AQI units")

    models[target]  = model
    results[target] = mae

#  Save all 3 models 
joblib.dump(models["1h"], "model_1h.pkl")
joblib.dump(models["2h"], "model_2h.pkl")
joblib.dump(models["3h"], "model_3h.pkl")

print("\n Summary ")
for k, v in results.items():
    status = "great" if v < 20 else "acceptable" if v < 35 else "needs work"
    print(f"  +{k}: MAE = {v:.2f}  ({status})")

print("\nmodel_1h.pkl, model_2h.pkl, model_3h.pkl saved!")
print("Training complete — ready for Flask!")