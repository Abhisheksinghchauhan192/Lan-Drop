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
    - Window*
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
import threading
import signal
import sys
import config
from pathlib import Path
from utils.qr import show_qr
from utils.network import get_local_ip

from utils.file_utils import (
    format_size,
)

from handlers.download import (
    DownloadHandler
)

from handlers.upload import (
    UploadHandler
)

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



TEMPLATE_DIR = Path(__file__).parent / "templates"
UPLOAD_DIR = Path.home() / "Desktop" / "LAN-Drop"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

config.SHARED_DIR = SHARED_DIR
config.UPLOAD_DIR = UPLOAD_DIR

download_server = None
upload_server = None

# html template files helper
def load_template(name):
    with open(TEMPLATE_DIR / name, "r", encoding="utf-8") as f:
        return f.read()


# Upload logger for terminal output
def log_upload(client_ip, filename, size):

    print(
        f"[UPLOAD] {filename} "
        f"({format_size(size)}) "
        f"from {client_ip}"
    )


class ThreadingHTTPServer(
    ThreadingMixIn,
    HTTPServer
):
    daemon_threads = True
    


def run_download_server():
    global download_server
    download_server = ThreadingHTTPServer(
        ("0.0.0.0", 3000),
        DownloadHandler
    )
    download_server.serve_forever()


def run_upload_server():
    global upload_server
    upload_server = ThreadingHTTPServer(
        ("0.0.0.0", 3001),
        UploadHandler
    )
    upload_server.serve_forever()


def shutdown_handler(sig, frame):
    print("\n\nStopping LAN-Drop...")

    if download_server:
        download_server.shutdown()
        download_server.server_close()

    if upload_server:
        upload_server.shutdown()
        upload_server.server_close()

    print("LAN-Drop stopped.")
    sys.exit(0)


# Launcher 
if __name__ == "__main__":

    signal.signal(signal.SIGINT, shutdown_handler)

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

    print(f"📂 Sharing:")
    print(f"   {SHARED_DIR}")

    print()
    print(f"📥 Download:")
    print(f"   {download_url}")
    print()
    print(f"📤 To Receive:")
    print(f"   {upload_url}")
    print()
    print(f"📁 Incoming Files:")
    print(f"   {UPLOAD_DIR}")

    print()
    print("📱 Recieving  QR:")
    print()

    show_qr(upload_url)


    print()
    print("Press Ctrl+C to stop.")
    print()
    print("=" * 50)

    signal.pause()
