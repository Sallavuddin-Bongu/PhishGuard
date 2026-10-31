import pandas as pd
from urllib.parse import urlsplit

# Load dataset
df = pd.read_csv(
    "datasets/phiusiil/PhiUSIIL_Phishing_URL_Dataset.csv",
    usecols=["URL", "label"]
)

websites = [
    "google.com",
    "youtube.com",
    "microsoft.com",
    "github.com",
    "amazon.com"
]

def get_hostname(url):
    try:
        url = str(url).strip()

        if "://" not in url:
            url = "https://" + url

        return (urlsplit(url).hostname or "").lower()

    except Exception:
        return ""

print("\nACTUAL DOMAIN LABEL ANALYSIS")
print("=" * 65)

df["hostname"] = df["URL"].apply(get_hostname)

for domain in websites:

    matches = df[
        (df["hostname"] == domain)
        | (df["hostname"].str.endswith("." + domain))
    ]

    print("\nWebsite:", domain)
    print("Total matching URLs:", len(matches))

    if len(matches) > 0:

        print("\nLabel distribution:")

        print(
            matches["label"]
            .value_counts()
            .rename(index={
                0: "Phishing",
                1: "Legitimate"
            })
        )

        print("\nSample URLs:")

        for _, row in matches.head(10).iterrows():

            label = (
                "Phishing"
                if row["label"] == 0
                else "Legitimate"
            )

            print(label, "|", row["URL"])

print("\nANALYSIS COMPLETED")