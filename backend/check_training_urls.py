import pandas as pd

dataset = pd.read_csv(
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

print("\nWEBSITE LABEL DISTRIBUTION")
print("=" * 60)

for website in websites:

    matches = dataset[
        dataset["URL"].str.contains(
            website,
            case=False,
            na=False,
            regex=False
        )
    ]

    print("\nWebsite:", website)
    print("Total rows:", len(matches))

    if len(matches) > 0:

        print(
            matches["label"]
            .value_counts()
            .rename(index={
                0: "Phishing",
                1: "Legitimate"
            })
        )

        print("\nSample URLs:")
        print(matches["URL"].head(5).to_string(index=False))

print("\nSupplemental dataset")
print("=" * 60)

extra = pd.read_csv(
    "datasets/verified_legitimate_urls.csv"
)

print(extra.to_string(index=False))