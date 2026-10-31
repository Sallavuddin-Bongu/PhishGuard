
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from itertools import product

import joblib

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "app" / "ml"
    / "phishguard_url_model_calibrated.joblib"
)

bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
calibrator = bundle["calibrator"]

domains = [
    "account.test",
    "secure.test",
    "login.test",
    "update.test",
    "verify.test",
    "payment.test",
    "bank.test",
    "customer.test",
    "service.test",
    "portal.test",
    "account-check.test",
    "secure-account.test",
    "login-update.test",
    "payment-verify.test",
]

paths = [
    "/",
    "/home",
    "/profile",
    "/login",
    "/account",
    "/verify",
    "/payment",
    "/signin",
    "/update",
    "/account/verify",
]

schemes = ["http", "https"]

candidates = [
    f"{scheme}://{domain}{path}"
    for scheme, domain, path in product(schemes, domains, paths)
]

results = []

for url in candidates:
    try:
        decision = model.decision_function([url])
        probabilities = calibrator.predict_proba(
            decision.reshape(-1, 1)
        )[0]

        phishing_index = list(calibrator.classes_).index(1)
        probability = float(probabilities[phishing_index])

        results.append((probability * 100, float(decision[0]), url))

    except Exception as error:
        print("Error:", url, error)

middle = [r for r in results if 10 <= r[0] <= 90]

print("\nPHISHGUARD INTERMEDIATE PROBABILITY TEST")
print("=" * 65)

if middle:
    print("\nURLs naturally scoring between 10% and 90%:\n")

    for risk, margin, url in sorted(middle):
        print(f"URL: {url}")
        print(f"Risk: {risk:.2f}%")
        print(f"Decision score: {margin:.4f}")
        print("-" * 45)

else:
    print("\nNo URLs found between 10% and 90%.")

    print("\nClosest URLs to 50%:\n")

    for risk, margin, url in sorted(
        results, key=lambda x: abs(x[0] - 50)
    )[:10]:
        print(f"URL: {url}")
        print(f"Risk: {risk:.2f}%")
        print(f"Decision score: {margin:.4f}")
        print("-" * 45)
