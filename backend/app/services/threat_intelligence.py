
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_URL = (
    "https://safebrowsing.googleapis.com/v5/urls:search"
)

TIMEOUT_SECONDS = 10


def check_url_with_google(url: str) -> dict:
    """Check a URL against Google Safe Browsing v5."""

    api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")

    if not api_key:
        return {
            "status": "unavailable",
            "matches": [],
            "threat_types": [],
            "message": "Google API key is not configured."
        }

    try:
        response = requests.get(
            GOOGLE_API_URL,
            params=[
                ("key", api_key),
                ("urls", url)
            ],
            timeout=TIMEOUT_SECONDS
        )

        response.raise_for_status()
        data = response.json()

        threats = data.get("threats", [])

        if threats:
            threat_types = sorted({
                threat_type
                for threat in threats
                for threat_type in threat.get("threatTypes", [])
            })

            return {
                "status": "match",
                "matches": threats,
                "threat_types": threat_types,
                "message": (
                    "Google Safe Browsing identified this URL "
                    "as a known threat."
                )
            }

        return {
            "status": "no_match",
            "matches": [],
            "threat_types": [],
            "message": (
                "Google Safe Browsing found no matching threat."
            )
        }

    except requests.exceptions.Timeout:
        message = "Google Safe Browsing request timed out."

    except requests.exceptions.HTTPError as exc:
        status_code = (
            exc.response.status_code
            if exc.response is not None
            else "unknown"
        )
        message = (
            f"Google Safe Browsing returned HTTP {status_code}."
        )

    except requests.exceptions.RequestException:
        message = "Could not connect to Google Safe Browsing."

    except (ValueError, TypeError):
        message = "Google Safe Browsing returned an invalid response."

    return {
        "status": "unavailable",
        "matches": [],
        "threat_types": [],
        "message": message
    }
