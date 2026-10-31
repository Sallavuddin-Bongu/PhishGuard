
def explain_risk(features: dict, findings: list[str]) -> str:
    if not findings:
        return (
            "No strong suspicious URL patterns were detected. "
            "This does not establish that the website is legitimate. "
            "This scan checks URL characteristics but does not independently "
            "verify domain ownership, website content, or live threat "
            "intelligence. Verify the domain before sharing sensitive data."
        )

    details = " ".join(findings)

    return (
        f"The scan detected these warning signs: {details} "
        "These indicators can occur on phishing websites, but they do not "
        "prove malicious intent on their own. Attackers may use deceptive "
        "domains or links to steal login credentials, payment details, "
        "or verification codes. Verify the exact domain independently "
        "and do not enter sensitive information if you are unsure."
    )
