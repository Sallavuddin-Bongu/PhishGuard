
import ipaddress
import re
from urllib.parse import parse_qsl, urlsplit

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd",
    "cutt.ly", "rb.gy", "shorturl.at",
}

SUSPICIOUS_WORDS = {
    "login", "verify", "verification", "account",
    "secure", "update", "password", "signin",
    "banking", "wallet", "confirm", "suspended",
    "recover", "urgent", "payment",
}

REDIRECT_KEYS = {
    "redirect", "redirect_url", "return", "return_url",
    "next", "continue", "url", "target",
}


def extract_url_features(url: str) -> dict:
    candidate = url.strip()
    if "://" not in candidate:
        candidate = "https://" + candidate

    parsed = urlsplit(candidate)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    path_query = (parsed.path + "?" + parsed.query).lower()
    labels = hostname.split(".") if hostname else []

    try:
        ipaddress.ip_address(hostname)
        uses_ip = True
    except ValueError:
        uses_ip = False

    try:
        port = parsed.port
    except ValueError:
        port = None

    try:
        query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
    except ValueError:
        query_pairs = []

    suspicious_words = sorted(
        word for word in SUSPICIOUS_WORDS
        if re.search(
            r"(?<![a-z])" + re.escape(word) + r"(?![a-z])",
            candidate.lower(),
        )
    )

    return {
        "normalized_url": candidate,
        "scheme": parsed.scheme.lower(),
        "hostname": hostname,
        "url_length": len(candidate),
        "hostname_length": len(hostname),
        "dot_count": hostname.count("."),
        "hyphen_count": hostname.count("-"),
        "subdomain_count": max(0, len(labels) - 2),
        "uses_https": parsed.scheme.lower() == "https",
        "uses_ip_address": uses_ip,
        "has_at_symbol": "@" in candidate,
        "has_suspicious_port": port not in (None, 80, 443),
        "has_punycode": "xn--" in hostname,
        "has_encoded_characters": bool(
            re.search(r"%[0-9a-fA-F]{2}", candidate)
        ),
        "has_double_slash_in_path": "//" in parsed.path,
        "has_shortener_domain": hostname in SHORTENER_DOMAINS,
        "suspicious_words": suspicious_words,
        "has_sensitive_path_words": any(
            re.search(
                r"(?<![a-z])" + re.escape(word) + r"(?![a-z])",
                path_query,
            )
            for word in SUSPICIOUS_WORDS
        ),
        "has_redirect_parameter": any(
            key.lower() in REDIRECT_KEYS for key, _ in query_pairs
        ),
    }
