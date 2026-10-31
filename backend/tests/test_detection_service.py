from app.services.detection_service import analyze_url


def test_normal_example_has_no_url_warning_signals():
    result = analyze_url("https://example.com")
    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"
    assert result["explanation"]
    assert result["findings"] == []


def test_ip_address_url_reports_warning_signals():
    result = analyze_url("http://192.0.2.10/account/verify")
    assert result["risk_score"] > 0
    assert result["findings"]
    assert result["explanation"]


def test_suspicious_words_are_explained():
    result = analyze_url("https://google-login.example/verify")
    assert result["risk_score"] > 0
    assert result["findings"]
    assert result["explanation"]
    assert result["risk_level"] in {"Low", "Medium", "High"}


def test_https_documentation_url_has_no_url_warning_signals():
    result = analyze_url("https://docs.python.org/3/")
    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"


def test_score_and_risk_level_are_consistent():
    urls = [
        "https://example.com",
        "https://google-login.example/verify",
        "http://192.0.2.10/account/verify",
        "https://docs.python.org/3/",
    ]
    for url in urls:
        result = analyze_url(url)
        score = result["risk_score"]
        expected = "High" if score >= 60 else "Medium" if score >= 30 else "Low"
        assert result["risk_level"] == expected
        assert 0 <= score <= 100
