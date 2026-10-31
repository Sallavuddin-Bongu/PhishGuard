
from pathlib import Path
from urllib.parse import urlparse

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
)

# File paths
DATASET_PATH = Path(
    "datasets/phiusiil/PhiUSIIL_Phishing_URL_Dataset.csv"
)

MODEL_PATH = Path(
    "app/ml/phishguard_url_model_domain_split.joblib"
)

# Load dataset
df = pd.read_csv(DATASET_PATH, usecols=["URL", "label"])

# Clean data
df = df.dropna()
df["URL"] = df["URL"].astype(str).str.strip()
df["label"] = df["label"].astype(int)

df = df[df["URL"] != ""]

# Extract hostname for domain grouping
def extract_domain(url):
    try:
        host = urlparse(url).hostname
        if not host:
            return ""
        return host.lower().removeprefix("www.")
    except Exception:
        return ""

df["domain"] = df["URL"].apply(extract_domain)

df = df[df["domain"] != ""]
df = df.drop_duplicates(subset=["URL"]).reset_index(drop=True)

# Original PhiUSIIL labels:
# 0 = Phishing
# 1 = Legitimate
#
# Our model labels:
# 0 = Legitimate
# 1 = Phishing

X = df["URL"]
y = (df["label"] == 0).astype(int)
groups = df["domain"]

# Split by domain, not by individual URL
splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(X, y, groups=groups)
)

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]

y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

train_domains = set(groups.iloc[train_idx])
test_domains = set(groups.iloc[test_idx])

# Verify no domain overlap
assert len(train_domains & test_domains) == 0

if y_train.nunique() < 2 or y_test.nunique() < 2:
    raise ValueError(
        "Both classes must exist in training and testing data."
    )

# Build model
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
            random_state=42
        )
    )
])

# Train
print("\nTraining PhishGuard domain-separated model...")

model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)

print("\n========== DATASET DETAILS ==========")
print("Total URLs:", len(df))
print("Unique domains:", df["domain"].nunique())
print("Training URLs:", len(X_train))
print("Testing URLs:", len(X_test))
print("Training domains:", len(train_domains))
print("Testing domains:", len(test_domains))
print("Domain overlap:", len(train_domains & test_domains))

print("\n========== MODEL PERFORMANCE ==========")
print("Accuracy:", round(accuracy_score(y_test, predictions), 4))
print(
    "Balanced accuracy:",
    round(balanced_accuracy_score(y_test, predictions), 4)
)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        target_names=["Legitimate", "Phishing"],
        zero_division=0
    )
)

# Save model separately
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(model, MODEL_PATH)

print("\nModel saved successfully:")
print(MODEL_PATH)
