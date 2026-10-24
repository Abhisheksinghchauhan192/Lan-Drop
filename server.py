#!/usr/bin/env python3

"""
LAN-Drop

Cross-platform LAN file sharing tool.

Author:
    Abhishek Singh Chauhan

Description:
    Provides local network file sharing
    through a lightweight web interface.

Supported Platforms:
    - Linux
    - Window
    - macOS
        
"""

#
#
#
#
#
#
"""
LAN-Drop Main Entry Point

Starts:

- Download server
- Upload server

Displays:

- Local URLs
- Network URLs
- QR Code

Handles graceful shutdown.
"""

from http.server import HTTPServer
from socketserver import ThreadingMixIn
import signal
import sys
import threading
from pathlib import Path

import config
from handlers.download import DownloadHandler
from handlers.upload import UploadHandler
from utils.network import get_local_ip
from utils.qr import show_qr
from utils.file_utils import format_size


if len(sys.argv) > 1:
    SHARED_DIR = Path(sys.argv[1]).expanduser().resolve()
else:
    SHARED_DIR = Path.cwd().resolve()

if not SHARED_DIR.exists():
    print(f"Error: {SHARED_DIR} does not exist")
    sys.exit(1)

if not SHARED_DIR.is_dir():
    print(f"Error: {SHARED_DIR} is not a directory")
    sys.exit(1)


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

# Keep incoming files on the user's Desktop when that directory exists.
# On systems without a Desktop directory (or with a nonstandard home setup),
# use a directory directly under the user's home instead.

DESKTOP_DIR = Path.home() / "Desktop"
if DESKTOP_DIR.is_dir():
    UPLOAD_DIR = DESKTOP_DIR / "LAN-Drop"
else:
    UPLOAD_DIR = Path.home() / "LAN-Drop"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

config.SHARED_DIR = SHARED_DIR
config.UPLOAD_DIR = UPLOAD_DIR


download_server = None
upload_server = None
stop_event = threading.Event()


def load_template(name):
    """Load an HTML template using a path relative to this file."""
    with open(TEMPLATE_DIR / name, "r", encoding="utf-8") as file:
        return file.read()


def log_upload(client_ip, filename, size):
    """Print a compact upload log entry."""
    print(f"[UPLOAD] {filename} ({format_size(size)}) from {client_ip}")


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def run_download_server():
    global download_server
    download_server = ThreadingHTTPServer(("0.0.0.0", 3000), DownloadHandler)
    download_server.serve_forever()


def run_upload_server():
    global upload_server
    upload_server = ThreadingHTTPServer(("0.0.0.0", 3001), UploadHandler)
    upload_server.serve_forever()


def shutdown_handler(_sig, _frame):
    """Ask the main thread to stop; cleanup happens outside the signal handler."""
    stop_event.set()


def stop_servers():
    """Stop and close any servers that were successfully started."""
    for server in (download_server, upload_server):
        if server is not None:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown_handler)

    t1 = threading.Thread(target=run_download_server, daemon=True)
    t2 = threading.Thread(target=run_upload_server, daemon=True)
    t1.start()
    t2.start()

    ip = get_local_ip()
    download_url = f"http://{ip}:3000"
    upload_url = f"http://{ip}:3001"

    print()
    print("=" * 50)
    print("               LAN-Drop")
    print("=" * 50)
    print()
    print("📂  Currentely Sharing:")
    print(f"   {SHARED_DIR}")
    print()
    print("📱 To Download Files Scan QR (optional):")
    print()
    show_qr(download_url)
    print()
    print("📥 Or Use Download LINK :")
    print(f"   {download_url}")
    print()
    print("📤 Send Files to This Machine Open Link :")
    print(f"   {upload_url}")
    print()
    print("📱 Receiving QR (optional):")
    print()
    show_qr(upload_url)
    print()
    print("📁 Incoming Files Will Be Saved At:")
    print(f"   {UPLOAD_DIR}")
    print()
    print("Press Ctrl+C to stop.")
    print()
    print("=" * 50)

    try:
        stop_event.wait()
    except KeyboardInterrupt:
        # Fallback in case the terminal delivers Ctrl+C as KeyboardInterrupt.
        pass
    finally:
        print("\n\nStopping LAN-Drop...")
        stop_servers()
        print("LAN-Drop stopped.")
