import requests, pandas as pd
r = requests.get("https://archive-api.open-meteo.com/v1/archive", params={
    "latitude": -1.70, "longitude": 29.26,
    "start_date": "2014-01-01", "end_date": "2023-12-31",
    "daily": "precipitation_sum", "timezone": "Africa/Kigali"}).json()["daily"]
df = pd.DataFrame({"date": pd.to_datetime(r["time"]), "mm": r["precipitation_sum"]})
df["mm3"] = df["mm"].rolling(3).sum()
print("P95:", df["mm"].quantile(0.95), " P99:", df["mm"].quantile(0.99))
for d in ["2023-05-02", "2023-05-03", "2023-05-04"]:
    row = df[df["date"] == d].iloc[0]
    print(d, row["mm"], f'1-day percentile: {(df["mm"] <= row["mm"]).mean()*100:.1f}',
          f'3-day sum: {row["mm3"]:.1f}, percentile: {(df["mm3"].dropna() <= row["mm3"]).mean()*100:.1f}')