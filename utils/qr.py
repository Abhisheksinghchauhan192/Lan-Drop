"""Optional terminal QR-code display for LAN-Drop.

QR support is deliberately optional: LAN-Drop continues to work when neither
an optional Python QR package nor the `qrencode` command is installed.
"""

import subprocess


def show_qr(url):
    """Display a terminal QR code if optional QR support is available."""
    # Prefer the optional Python package. It does not require Pillow when only
    # printing an ASCII QR code to the terminal.
    try:
        import qrcode

        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
        return True
    except ImportError:
        pass
    except Exception as error:
        # If the Python QR package exists but fails, try the optional CLI below.
        print(f"QR display via Python package failed: {error}")

    # Preserve support for users who already have qrencode installed.
    try:
        subprocess.run(
            ["qrencode", "-t", "ansiutf8", url],
            check=True,
        )
        return True
    except FileNotFoundError:
        pass
    except (subprocess.CalledProcessError, OSError) as error:
        print(f"Could not display a QR code: {error}")

    print("QR code unavailable; LAN-Drop is still running normally.")
    print("To enable terminal QR codes, optionally install the Python package:")
    print("    python -m pip install qrcode")
    print("Or install the 'qrencode' command for your operating system.")
    print(f"Use this URL instead: {url}")
    return False
