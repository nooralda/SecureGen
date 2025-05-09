def assign_severity(issue):
    message = issue.get("extra", {}).get("message", "").lower()
    check_id = issue.get("check_id", "").lower()

    critical = ["sql-injection", "rce", "remote-code", "path-traversal"]
    high = ["xss", "auth", "csrf", "command-injection"]
    medium = ["leak", "hardcoded", "info", "debug"]

    if any(term in message or term in check_id for term in critical):
        return "Critical"
    elif any(term in message or term in check_id for term in high):
        return "High"
    elif any(term in message or term in check_id for term in medium):
        return "Medium"
    else:
        return "Low"
