"""Small, standard-library-only network helpers for LAN-Drop."""

import socket


def get_local_ip():
    """Return the local IPv4 address used for outbound network traffic.

    The UDP socket is used only to ask the operating system which local
    interface it would route through; no application data is sent. If no
    suitable route is available, return loopback as a safe fallback.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        if ip and not ip.startswith("127."):
            return ip
    except OSError:
        pass
    finally:
        sock.close()

    # Fallback for environments where the route probe above is unavailable.
    try:
        hostname = socket.gethostname()
        for result in socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_DGRAM):
            candidate = result[4][0]
            if candidate and not candidate.startswith("127."):
                return candidate
    except OSError:
        pass

    return "127.0.0.1"
