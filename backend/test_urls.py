
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import joblib

# Load the calibrated model bundle
model_path = (
    Path(__file__).resolve().parent
    / "app"
    / "ml"
    / "phishguard_url_model_calibrated.joblib"
)

if not model_path.exists():
    raise FileNotFoundError(f"Model not found: {model_path}")

bundle = joblib.load(model_path)

model = bundle["model"]
calibrator = bundle["calibrator"]


def normalize_url(url):
    url = url.strip()

    if "://" not in url:
        url = "https://" + url

    parsed = urlsplit(url)

    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower().rstrip(".")

    if hostname.startswith("www."):
        hostname = hostname[4:]

    port = parsed.port

    if port and not (
        (scheme == "https" and port == 443)
        or (scheme == "http" and port == 80)
    ):
        netloc = f"{hostname}:{port}"
    else:
        netloc = hostname

    path = "" if parsed.path == "/" else parsed.path

    return urlunsplit((
        scheme,
        netloc,
        path,
        parsed.query,
        ""
    ))


test_urls = [
    "http://account.example.com/profile",
    "http://account-update.example.com/verify",
    "http://secure-login.example.com/home",
    "http://verify-account.example.com/login",
    "http://payment-check.example.com/confirm",
    "http://password-reset.example.com/signin",
    "http://bank-alert.example.com/secure",
    "http://paypal-security.example.com/account",
    "http://paypal-login-security.example.com/verify-account",
    "https://google.com",
    "https://github.com",
    "https://wikipedia.org",
]

print("\nPHISHGUARD CALIBRATED MODEL TEST")
print("-" * 65)

for url in test_urls:

    candidate = normalize_url(url)

    decision = model.decision_function([candidate])

    probabilities = calibrator.predict_proba(
        decision.reshape(-1, 1)
    )[0]

    phishing_index = list(calibrator.classes_).index(1)

    probability = float(probabilities[phishing_index])

    risk = round(probability * 100, 2)

    label = "PHISHING" if probability >= 0.50 else "LEGITIMATE"

    print(f"\nURL: {url}")
    print(f"Phishing Probability: {risk}%")
    print(f"Classification: {label}")

    if 10 <= risk <= 90:
        print("MATCH: Within the 10%-90% range")

    print("-" * 65)
