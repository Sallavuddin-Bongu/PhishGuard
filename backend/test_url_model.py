
from pathlib import Path
import joblib

model_path = Path("app/ml/phishguard_url_model.joblib")

if not model_path.exists():
    raise FileNotFoundError(f"Model not found: {model_path}")

model = joblib.load(model_path)

test_urls = [
    "https://example.com/",
    "https://www.python.org/",
    "http://192.0.2.10/account/verify",
    "https://google-login.example/verify",
]

print("PhishGuard URL Model Test")
print("-" * 45)

for url in test_urls:
    prediction = int(model.predict([url])[0])
    label = "PHISHING" if prediction == 1 else "LEGITIMATE"

    print(f"URL: {url}")
    print(f"Prediction: {label}")
    print("-" * 45)
