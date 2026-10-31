
import joblib
from pathlib import Path

model_path = Path("app/ml/phishguard_url_model.joblib")
model = joblib.load(model_path)

test_urls = [
    "https://www.google.com/",
    "https://www.microsoft.com/",
    "https://www.wikipedia.org/",
    "https://www.amazon.com/",
    "https://www.python.org/",
    "https://example.com/",
    "http://192.0.2.10/login",
    "https://secure-account-verify.example/login",
    "http://paypal.com.security-check.example/login",
    "https://account-update.example/verify",
]

print("PHISHGUARD - MODEL SANITY TEST")
print("=" * 55)

for url in test_urls:
    prediction = int(model.predict([url])[0])
    result = "PHISHING" if prediction == 1 else "LEGITIMATE"
    print(f"{result:10} | {url}")

print("=" * 55)
