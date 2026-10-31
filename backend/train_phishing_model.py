
from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier

DATASET = Path("datasets/phiusiil/PhiUSIIL_Phishing_URL_Dataset.csv")
MODEL_DIR = Path("app/ml")
MODEL_PATH = MODEL_DIR / "phishguard_model.joblib"

# Load dataset
df = pd.read_csv(DATASET)
print("Dataset shape:", df.shape)
print("Label counts:\n", df["label"].value_counts(dropna=False))

# Exclude URL, domain, title, filename and target from inputs.
# This avoids directly learning identifiers and text.
excluded = {"label", "URL", "Domain", "FILENAME", "Title"}
X = df.drop(columns=list(excluded), errors="ignore").copy()
y = df["label"]

if y.isna().any():
    raise ValueError("The label column contains missing values.")

if y.nunique() != 2:
    raise ValueError(f"Expected two label classes, found: {y.unique()}")

# Convert numeric-looking columns safely and preserve categorical columns.
for col in X.columns:
    if X[col].dtype == "object":
        converted = pd.to_numeric(X[col], errors="coerce")
        if converted.notna().sum() >= max(1, int(len(X) * 0.9)):
            X[col] = converted

numeric_cols = X.select_dtypes(include=["number", "bool"]).columns.tolist()
categorical_cols = [c for c in X.columns if c not in numeric_cols]

numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scale", StandardScaler()),
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=5)),
])

preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, numeric_cols),
    ("categorical", categorical_pipeline, categorical_cols),
])

model = RandomForestClassifier(
    n_estimators=250,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", model),
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining rows: {len(X_train):,}")
print(f"Test rows: {len(X_test):,}")
print("Training model...")

pipeline.fit(X_train, y_train)
pred = pipeline.predict(X_test)
probabilities = pipeline.predict_proba(X_test)

print("\nAccuracy:", round(accuracy_score(y_test, pred), 4))
print("\nClassification report:\n", classification_report(y_test, pred))
print("Confusion matrix:\n", confusion_matrix(y_test, pred))
print("ROC-AUC:", round(roc_auc_score(y_test, probabilities[:, 1]), 4))

MODEL_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump({
    "pipeline": pipeline,
    "feature_columns": X.columns.tolist(),
    "label_values": sorted(y.unique().tolist()),
    "dataset": DATASET.name,
}, MODEL_PATH)

print(f"\nSaved model to: {MODEL_PATH}")
print("IMPORTANT: label 0/1 meaning must be verified before deployment.")
