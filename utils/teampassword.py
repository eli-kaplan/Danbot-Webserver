import hashlib

def calculate_team_password(team_entry: object) -> str:
    """Calculates the team password for a given team database entry

    This is not super secure but obfuscates access to the team boards - it's just a portion of the SHA256 hash
    of the team's webhook URL (which is private/not retrievable except with admin permissions)

    Args:
        team_entry (object): Team db entry

    Returns:
        str: Team password
    """
    hash = hashlib.sha256()
    hash.update(team_entry.webhook_url.encode("utf-8"))
    digest = hash.hexdigest()
    return digest[:32]