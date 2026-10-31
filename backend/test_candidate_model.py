
import joblib

MODEL_PATH = "app/ml/phishguard_url_model_candidate.joblib"

model = joblib.load(MODEL_PATH)

test_urls = [
    # Legitimate URLs
    "https://www.google.com/",
    "https://www.wikipedia.org/",
    "https://www.microsoft.com/",
    "https://www.amazon.com/",
    "https://www.python.org/",
    "https://www.github.com/",
    "https://www.apple.com/",
    "https://www.openai.com/",
    "https://www.youtube.com/",
    "https://www.linkedin.com/",

    # Suspicious URLs
    "http://paypal-login-security.example.com/verify-account",
    "http://secure-bank-login.example.com/verify",
    "http://google-account-security.example.com/login",
    "http://amazon-payment-verify.example.com/update",
    "http://microsoft-password-reset.example.com/login",
]

print("\n========== CANDIDATE MODEL VALIDATION ==========\n")

for url in test_urls:
    prediction = int(model.predict([url])[0])
    score = float(model.decision_function([url])[0])

    verdict = "PHISHING" if prediction == 1 else "LEGITIMATE"

    print("URL:", url)
    print("Prediction:", verdict)
    print("Decision score:", round(score, 4))
    print("-" * 70)
