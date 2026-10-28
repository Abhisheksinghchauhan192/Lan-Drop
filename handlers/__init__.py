"""Shared helpers for LAN-Drop HTTP request handlers."""


def get_client_name(client_address, headers):
    """Return a readable client label from its address and User-Agent."""
    ip = client_address[0]
    user_agent = headers.get("User-Agent", "")

    if "Android" in user_agent:
        return f"Android ({ip})"
    if "iPhone" in user_agent:
        return f"iPhone ({ip})"
    if "Windows" in user_agent:
        return f"Windows PC ({ip})"
    if "Linux" in user_agent:
        return f"Linux PC ({ip})"
    return ip