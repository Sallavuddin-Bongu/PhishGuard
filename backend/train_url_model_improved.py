from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import ipaddress
import json

import joblib
import pandas as pd
import tldextract

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GroupShuffleSplit
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    brier_score_loss,
    log_loss
)


# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

DATASET_PATH = Path(
    "datasets/phiusiil/PhiUSIIL_Phishing_URL_Dataset.csv"
)

SUPPLEMENTAL_PATH = Path(
    "datasets/verified_legitimate_urls.csv"
)

CALIBRATED_MODEL_PATH = Path(
    "app/ml/phishguard_url_model_calibrated.joblib"
)

CALIBRATED_REPORT_PATH = Path(
    "app/ml/phishguard_url_model_calibrated_report.json"
)


# --------------------------------------------------
# 2. DOMAIN EXTRACTOR
# --------------------------------------------------

extract_domain = tldextract.TLDExtract(
    suffix_list_urls=()
)


# --------------------------------------------------
# 3. URL NORMALIZATION
# --------------------------------------------------

def normalize_url(url):
    """
    Normalize URL formatting consistently.

    - Lowercase scheme and hostname.
    - Remove www prefix.
    - Remove default ports.
    - Remove root trailing slash.
    - Remove URL fragment.
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
# 4. EXTRACT REGISTRABLE DOMAIN
# --------------------------------------------------

def get_domain(url):

    try:
        candidate = normalize_url(url)

        parsed = urlsplit(candidate)

        hostname = (
            parsed.hostname or ""
        ).lower().rstrip(".")

        if not hostname:
            return None

        try:
            ipaddress.ip_address(hostname)
            return hostname

        except ValueError:
            pass

        result = extract_domain(hostname)

        registered = (
            result.top_domain_under_public_suffix
        )

        return registered or hostname

    except Exception:
        return None


# --------------------------------------------------
# 5. LOAD ORIGINAL PHIUSIIL DATASET
# --------------------------------------------------

print("\nLoading PhiUSIIL dataset...")

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )

df = pd.read_csv(
    DATASET_PATH,
    usecols=["URL", "label"]
)

df = df.dropna(
    subset=["URL", "label"]
).copy()

df["URL"] = df["URL"].astype(str)

df["label"] = pd.to_numeric(
    df["label"],
    errors="coerce"
)

df = df.dropna(
    subset=["label"]
).copy()

df["label"] = df["label"].astype(int)

df = df[
    (df["URL"].str.strip() != "")
    & (df["label"].isin([0, 1]))
].copy()


# Original PhiUSIIL labels:
# 0 = Phishing
# 1 = Legitimate

# Our ML labels:
# 0 = Legitimate
# 1 = Phishing

df["target"] = (
    df["label"] == 0
).astype(int)

df = df[["URL", "target"]]

print("Original dataset rows:", len(df))


# --------------------------------------------------
# 6. LOAD VERIFIED LEGITIMATE URLS
# --------------------------------------------------

if SUPPLEMENTAL_PATH.exists():

    extra = pd.read_csv(
        SUPPLEMENTAL_PATH
    )

    if not {"URL", "label"}.issubset(
        extra.columns
    ):
        raise ValueError(
            "Supplemental CSV must contain URL and label columns."
        )

    extra = extra.dropna(
        subset=["URL", "label"]
    ).copy()

    extra["URL"] = extra["URL"].astype(str)

    extra["label"] = pd.to_numeric(
        extra["label"],
        errors="coerce"
    )

    extra = extra.dropna(
        subset=["label"]
    ).copy()

    extra["label"] = extra["label"].astype(int)

    if not extra["label"].isin([1]).all():

        raise ValueError(
            "The supplemental file is for verified legitimate URLs only. "
            "Every label must be 1."
        )

    extra = extra[
        extra["URL"].str.strip() != ""
    ].copy()

    # Original label 1 = Legitimate.
    # Our ML target 0 = Legitimate.

    extra["target"] = 0

    extra = extra[
        ["URL", "target"]
    ]

    print(
        "Supplemental legitimate rows:",
        len(extra)
    )

    df = pd.concat(
        [df, extra],
        ignore_index=True
    )

else:

    print(
        "WARNING: No supplemental legitimate URL dataset found."
    )


# --------------------------------------------------
# 7. NORMALIZE ALL URLS
# --------------------------------------------------

print("\nNormalizing URLs...")

df["URL"] = df["URL"].apply(
    normalize_url
)

df = df[
    df["URL"] != ""
].copy()

print(
    "Rows after URL normalization:",
    len(df)
)


# --------------------------------------------------
# 8. REMOVE CONFLICTING URL LABELS
# --------------------------------------------------

label_counts = df.groupby(
    "URL"
)["target"].nunique()

conflicting_urls = label_counts[
    label_counts > 1
].index

print(
    "Conflicting exact URLs removed:",
    len(conflicting_urls)
)

df = df[
    ~df["URL"].isin(conflicting_urls)
].copy()

df = df.drop_duplicates(
    subset=["URL", "target"]
).reset_index(drop=True)


# --------------------------------------------------
# 9. EXTRACT DOMAINS
# --------------------------------------------------

df["domain"] = df["URL"].apply(
    get_domain
)

df = df.dropna(
    subset=["domain"]
).copy()

df = df[
    df["domain"] != ""
].reset_index(drop=True)

if df["target"].nunique() != 2:

    raise ValueError(
        "Training data must contain both legitimate and phishing URLs."
    )

print("\nFinal dataset rows:", len(df))

print("\nML class counts:")

print(
    df["target"]
    .value_counts()
    .rename(
        index={
            0: "Legitimate",
            1: "Phishing"
        }
    )
)

print(
    "\nUnique registered domains:",
    df["domain"].nunique()
)


# --------------------------------------------------
# 10. DOMAIN-BASED TRAIN / TEST SPLIT
# --------------------------------------------------

X = df["URL"]

y = df["target"]

groups = df["domain"]


outer_splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_idx, test_idx = next(
    outer_splitter.split(
        X,
        y,
        groups=groups
    )
)

X_train_full = X.iloc[train_idx]

X_test = X.iloc[test_idx]

y_train_full = y.iloc[train_idx]

y_test = y.iloc[test_idx]

groups_train = groups.iloc[train_idx]

train_domains = set(groups_train)

test_domains = set(
    groups.iloc[test_idx]
)

if train_domains.intersection(test_domains):

    raise RuntimeError(
        "Domain leakage between training and testing."
    )

if y_test.nunique() != 2:

    raise ValueError(
        "Test set must contain both classes."
    )


# --------------------------------------------------
# 11. CALIBRATION SPLIT
# --------------------------------------------------

calibration_splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=43
)

fit_idx, calibration_idx = next(
    calibration_splitter.split(
        X_train_full,
        y_train_full,
        groups=groups_train
    )
)

X_fit = X_train_full.iloc[fit_idx]

X_cal = X_train_full.iloc[calibration_idx]

y_fit = y_train_full.iloc[fit_idx]

y_cal = y_train_full.iloc[calibration_idx]

fit_domains = set(
    groups_train.iloc[fit_idx]
)

calibration_domains = set(
    groups_train.iloc[calibration_idx]
)

if fit_domains.intersection(calibration_domains):

    raise RuntimeError(
        "Domain leakage in calibration split."
    )

if y_fit.nunique() != 2 or y_cal.nunique() != 2:

    raise ValueError(
        "Fit and calibration sets must contain both classes."
    )

print("\nModel fitting URLs:", len(X_fit))

print("Calibration URLs:", len(X_cal))

print("Testing URLs:", len(X_test))

print(
    "Fit/calibration overlap:",
    len(fit_domains.intersection(calibration_domains))
)

print(
    "Train/test overlap:",
    len(train_domains.intersection(test_domains))
)


# --------------------------------------------------
# 12. BUILD TF-IDF + LINEAR SVC MODEL
# --------------------------------------------------

model = Pipeline([

    (
        "tfidf",

        TfidfVectorizer(
            analyzer="char",
            ngram_range=(3, 5),
            max_features=300000,
            min_df=2,
            sublinear_tf=True
        )
    ),

    (
        "classifier",

        LinearSVC(
            class_weight="balanced",
            random_state=42,
            max_iter=5000
        )
    )

])


# --------------------------------------------------
# 13. TRAIN MODEL
# --------------------------------------------------

print("\nTraining PhishGuard model...")

model.fit(
    X_fit,
    y_fit
)

print("\nModel training completed.")


# --------------------------------------------------
# 14. CALIBRATE PROBABILITIES
# --------------------------------------------------

print("\nCalibrating phishing probabilities...")

calibration_scores = model.decision_function(
    X_cal
).reshape(-1, 1)

calibrator = LogisticRegression(
    max_iter=1000,
    random_state=42
)

calibrator.fit(
    calibration_scores,
    y_cal
)

print("Calibration completed.")


# --------------------------------------------------
# 15. EVALUATE MODEL
# --------------------------------------------------

predictions = model.predict(
    X_test
)

test_scores = model.decision_function(
    X_test
).reshape(-1, 1)

phishing_class_index = list(
    calibrator.classes_
).index(1)

phishing_probabilities = calibrator.predict_proba(
    test_scores
)[:, phishing_class_index]

cm = confusion_matrix(
    y_test,
    predictions,
    labels=[0, 1]
)

tn, fp, fn, tp = cm.ravel()

false_positive_rate = (
    fp / (fp + tn)
    if (fp + tn) > 0
    else 0
)

false_negative_rate = (
    fn / (fn + tp)
    if (fn + tp) > 0
    else 0
)

metrics = {

    "accuracy": float(
        accuracy_score(y_test, predictions)
    ),

    "balanced_accuracy": float(
        balanced_accuracy_score(
            y_test,
            predictions
        )
    ),

    "precision": float(
        precision_score(
            y_test,
            predictions,
            zero_division=0
        )
    ),

    "recall": float(
        recall_score(
            y_test,
            predictions,
            zero_division=0
        )
    ),

    "f1_score": float(
        f1_score(
            y_test,
            predictions,
            zero_division=0
        )
    ),

    "false_positive_rate": float(
        false_positive_rate
    ),

    "false_negative_rate": float(
        false_negative_rate
    ),

    "brier_score": float(
        brier_score_loss(
            y_test,
            phishing_probabilities
        )
    ),

    "log_loss": float(
        log_loss(
            y_test,
            phishing_probabilities,
            labels=[0, 1]
        )
    )
}


# --------------------------------------------------
# 16. DISPLAY RESULTS
# --------------------------------------------------

print("\n========== CONFUSION MATRIX ==========")

print(cm)

print("\n========== CLASSIFICATION REPORT ==========")

print(
    classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=[
            "Legitimate",
            "Phishing"
        ],
        zero_division=0
    )
)

print("\n========== MODEL METRICS ==========")

for name, value in metrics.items():

    print(
        f"{name}: {value:.6f}"
    )


# --------------------------------------------------
# 17. SAVE CALIBRATED MODEL
# --------------------------------------------------

CALIBRATED_MODEL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

model_bundle = {

    "model": model,

    "calibrator": calibrator,

    "label_mapping": {
        0: "Legitimate",
        1: "Phishing"
    }
}

joblib.dump(
    model_bundle,
    CALIBRATED_MODEL_PATH
)

print(
    "\nCalibrated model saved:",
    CALIBRATED_MODEL_PATH
)


# --------------------------------------------------
# 18. SAVE EVALUATION REPORT
# --------------------------------------------------

report = {

    "dataset": str(DATASET_PATH),

    "supplemental_dataset": str(
        SUPPLEMENTAL_PATH
    ),

    "model": (
        "TF-IDF character ngrams + "
        "LinearSVC + LogisticRegression calibration"
    ),

    "label_mapping": {
        "0": "Legitimate",
        "1": "Phishing"
    },

    "model_fit_rows": int(len(X_fit)),

    "calibration_rows": int(len(X_cal)),

    "testing_rows": int(len(X_test)),

    "model_fit_domains": int(len(fit_domains)),

    "calibration_domains": int(len(calibration_domains)),

    "testing_domains": int(len(test_domains)),

    "fit_calibration_domain_overlap": int(
        len(
            fit_domains.intersection(
                calibration_domains
            )
        )
    ),

    "training_testing_domain_overlap": int(
        len(
            train_domains.intersection(
                test_domains
            )
        )
    ),

    "conflicting_urls_removed": int(
        len(conflicting_urls)
    ),

    "confusion_matrix": cm.tolist(),

    "metrics": metrics,

    "random_state": 42
}

CALIBRATED_REPORT_PATH.write_text(
    json.dumps(
        report,
        indent=4
    ),
    encoding="utf-8"
)

print(
    "\nCalibration report saved:",
    CALIBRATED_REPORT_PATH
)

print("\nPhishGuard model training completed.")