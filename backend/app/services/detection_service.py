from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import joblib

from app.services.feature_extractor import extract_url_features
from app.services.explanation_service import explain_risk
from app.services.threat_intelligence import check_url_with_google


# --------------------------------------------------
# 1. MODEL CONFIGURATION
# --------------------------------------------------

MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "ml"
    / "phishguard_url_model_calibrated.joblib"
)

_ml_bundle = None


def get_ml_model():
    """Load the calibrated model once and reuse it."""

    global _ml_bundle

    if _ml_bundle is None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Calibrated model not found: {MODEL_PATH}"
            )

        bundle = joblib.load(MODEL_PATH)

        if not isinstance(bundle, dict):
            raise ValueError("Invalid calibrated model file.")

        if "model" not in bundle or "calibrator" not in bundle:
            raise ValueError("Model or calibrator is missing.")

        _ml_bundle = bundle

    return _ml_bundle


# --------------------------------------------------
# 2. URL NORMALIZATION
# --------------------------------------------------

def normalize_url(url):
    """
    Keep training and prediction URL formats consistent.

    Removes:
    - www prefix
    - root trailing slash
    - default HTTP/HTTPS ports
    - URL fragment

    Preserves:
    - URL path
    - query parameters
    """

    try:

        url = str(url).strip()

        if not url:
            return ""

        if "://" not in url:
            url = "https://" + url

        parsed = urlsplit(url)

        scheme = parsed.scheme.lower()

        hostname = (
            parsed.hostname or ""
        ).lower().rstrip(".")

        if not hostname:
            return ""

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

        path = parsed.path

        if path == "/":
            path = ""

        return urlunsplit((
            scheme,
            netloc,
            path,
            parsed.query,
            ""
        ))

    except Exception:
        return ""


# --------------------------------------------------
# 3. URL ANALYSIS
# --------------------------------------------------

def analyze_url(url: str) -> dict:

    raw_url = str(url).strip()

    if not raw_url or len(raw_url) > 2048:
        raise ValueError(
            "URL must contain between 1 and 2048 characters."
        )

    original_candidate = (
        raw_url
        if "://" in raw_url
        else "https://" + raw_url
    )

    # --------------------------------------------------
    # 4. URL VALIDATION
    # --------------------------------------------------

    try:

        original_parsed = urlsplit(original_candidate)

        hostname = (
            original_parsed.hostname or ""
        ).rstrip(".").lower()

        original_parsed.port

    except ValueError as exc:

        raise ValueError(
            "Enter a valid HTTP or HTTPS URL."
        ) from exc

    if (
        original_parsed.scheme.lower() not in {"http", "https"}
        or not hostname
        or any(char.isspace() for char in raw_url)
        or original_parsed.username is not None
        or original_parsed.password is not None
    ):

        raise ValueError(
            "Enter a valid HTTP or HTTPS URL "
            "without embedded credentials."
        )

    if "." not in hostname:

        raise ValueError(
            "Enter a valid hostname, such as example.com."
        )

    if (
        hostname == "localhost"
        or hostname.endswith(".localhost")
    ):

        raise ValueError(
            "Localhost URLs are not supported."
        )

    # --------------------------------------------------
    # 5. NORMALIZE BEFORE PREDICTION
    # --------------------------------------------------

    candidate = normalize_url(original_candidate)

    if not candidate:
        raise ValueError("Unable to normalize the URL.")

    # --------------------------------------------------
    # 6. FEATURE EXTRACTION
    # --------------------------------------------------

    features = extract_url_features(candidate)

    findings = []

    heuristic_score = 0

    def flag(condition, points, message):

        nonlocal heuristic_score

        if condition:
            heuristic_score += points
            findings.append(message)

    # --------------------------------------------------
    # 7. HEURISTIC SECURITY CHECKS
    # --------------------------------------------------

    flag(
        features["uses_ip_address"],
        30,
        "The hostname is an IP address instead of a conventional domain."
    )

    flag(
        features["has_at_symbol"],
        25,
        "The URL contains an @ symbol that may obscure its destination."
    )

    flag(
        features["has_punycode"],
        20,
        "The domain contains punycode."
    )

    flag(
        features["has_shortener_domain"],
        12,
        "The URL uses a shortening service."
    )

    flag(
        features["has_suspicious_port"],
        10,
        "The URL uses a nonstandard port."
    )

    flag(
        features["subdomain_count"] >= 4,
        12,
        "The hostname contains an unusually large number of subdomains."
    )

    flag(
        features["url_length"] >= 120,
        8,
        "The URL is unusually long."
    )

    flag(
        features["hyphen_count"] >= 3,
        6,
        "The hostname contains several hyphens."
    )

    flag(
        features["has_redirect_parameter"],
        8,
        "The URL contains a possible redirect parameter."
    )

    flag(
        bool(features["suspicious_words"]),
        6,
        "The URL contains suspicious wording."
    )

    flag(
        features["has_sensitive_path_words"],
        5,
        "The URL contains account or payment-related wording."
    )

    flag(
        not features["uses_https"],
        3,
        "The URL does not use HTTPS."
    )

    flag(
        features["has_encoded_characters"],
        3,
        "The URL contains percent-encoded characters."
    )

    suspicious_words = features.get(
        "suspicious_words", []
    )

    if (
        suspicious_words
        and features.get("has_sensitive_path_words")
        and features.get("hyphen_count", 0) >= 2
    ):

        heuristic_score += 20

        findings.append(
            "The URL combines suspicious wording, a sensitive path "
            "and multiple hostname hyphens."
        )

    heuristic_score = min(100, heuristic_score)

    # --------------------------------------------------
    # 8. CALIBRATED MACHINE LEARNING
    # --------------------------------------------------

    ml_prediction = None
    ml_label = "Unavailable"
    ml_decision_score = None
    ml_phishing_probability = None
    ml_error = None

    try:

        bundle = get_ml_model()

        model = bundle["model"]

        calibrator = bundle["calibrator"]

        # IMPORTANT:
        # Use the normalized URL for model prediction.

        decision = model.decision_function(
            [candidate]
        )

        ml_decision_score = float(decision[0])

        calibrated_input = decision.reshape(-1, 1)

        probabilities = calibrator.predict_proba(
            calibrated_input
        )[0]

        phishing_index = list(
            calibrator.classes_
        ).index(1)

        ml_phishing_probability = float(
            probabilities[phishing_index]
        )

        ml_prediction = int(
            ml_phishing_probability >= 0.50
        )

        ml_label = (
            "Phishing"
            if ml_prediction == 1
            else "Legitimate"
        )

        if ml_prediction == 1:

            findings.append(
                "The calibrated ML model classified this URL as phishing."
            )

        else:

            findings.append(
                "The calibrated ML model classified this URL as legitimate."
            )

    except Exception as exc:

        ml_error = type(exc).__name__

        findings.append(
            "The calibrated ML prediction is unavailable. "
            "The result will use heuristic checks and threat intelligence."
        )

    # --------------------------------------------------
    # 9. GOOGLE SAFE BROWSING
    # --------------------------------------------------

    try:

        threat_intelligence = check_url_with_google(
            candidate
        )

    except Exception:

        threat_intelligence = {
            "status": "unavailable",
            "matches": [],
            "threat_types": [],
            "message": "Google Safe Browsing check failed."
        }

    google_status = threat_intelligence.get(
        "status", "unavailable"
    )

    if google_status == "match":

        threat_types = threat_intelligence.get(
            "threat_types", []
        )

        findings.append(
            "Google Safe Browsing identified this URL "
            "as a known unsafe resource."
        )

        if threat_types:

            findings.append(
                "Google threat categories: "
                + ", ".join(threat_types)
                + "."
            )

    elif google_status == "no_match":

        findings.append(
            "Google Safe Browsing found no matching threat. "
            "This does not guarantee safety."
        )

    else:

        findings.append(
            "Google Safe Browsing was unavailable."
        )

    # --------------------------------------------------
    # 10. FINAL RISK SCORE
    # --------------------------------------------------

    if google_status == "match":

        score = 100

    elif ml_phishing_probability is not None:

        score = round(
            ml_phishing_probability * 100
        )

    else:

        score = heuristic_score

    score = min(
        100,
        max(0, int(score))
    )

    # --------------------------------------------------
    # 11. FINAL VERDICT
    # --------------------------------------------------

    if google_status == "match" or score >= 70:

        risk_level = "High"
        verdict = "Phishing"

    elif score >= 30:

        risk_level = "Medium"
        verdict = "Suspicious"

    else:

        risk_level = "Low"
        verdict = "Safe"

    # --------------------------------------------------
    # 12. EXPLANATION
    # --------------------------------------------------

    explanation = explain_risk(
        features,
        findings
    )

    if google_status == "match":

        explanation += (
            " Google Safe Browsing reported a threat match. "
            "Avoid opening this URL."
        )

    elif google_status == "no_match":

        explanation += (
            " Google Safe Browsing found no matching threat. "
            "This does not guarantee that the URL is safe."
        )

    else:

        explanation += (
            " Google Safe Browsing could not complete its check. "
            "The result uses local detection."
        )

    # --------------------------------------------------
    # 13. HARM EXPLANATION
    # --------------------------------------------------

    if google_status == "match":

        harm_explanation = (
            "Google Safe Browsing identified this URL as a known "
            "unsafe resource. Avoid opening it or sharing personal data."
        )

    elif verdict == "Phishing":

        harm_explanation = (
            "The calibrated ML model or security checks identified "
            "this URL as high risk. It may attempt to steal passwords, "
            "payment information or verification codes."
        )

    elif verdict == "Suspicious":

        harm_explanation = (
            "This URL contains suspicious characteristics. "
            "Verify the destination independently before opening it."
        )

    else:

        harm_explanation = (
            "No strong warning signs were detected by the available "
            "checks. This does not prove that the website is safe."
        )

    # --------------------------------------------------
    # 14. API RESPONSE
    # --------------------------------------------------

    return {

        "url": features["normalized_url"],

        "risk_score": score,
        "risk_level": risk_level,
        "verdict": verdict,

        "explanation": explanation,
        "harm_explanation": harm_explanation,

        "findings": findings,
        "features": features,

        "detection_method": (
            "calibrated_ml_heuristic_google_safe_browsing"
        ),

        "ml_prediction": ml_prediction,
        "ml_label": ml_label,

        "ml_phishing_probability": (
            round(ml_phishing_probability, 6)
            if ml_phishing_probability is not None
            else None
        ),

        "ml_decision_score": ml_decision_score,
        "ml_error": ml_error,

        "heuristic_score": heuristic_score,

        "score_type": (
            "calibrated_ml_probability_percentage"
            if ml_phishing_probability is not None
            else "heuristic_fallback_not_probability"
        ),

        "threat_intelligence": threat_intelligence
    }