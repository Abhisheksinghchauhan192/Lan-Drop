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
    - Windows
    - macOS
"""

"""
Download Handler

Provides:

- Directory browsing
- File downloads
- Folder navigation
- File size display
- Download logging
"""

from http.server import (
    BaseHTTPRequestHandler
)
from pathlib import Path
import config
from utils.templates import (
    load_template
)
import mimetypes
from urllib.parse import (
    unquote,
    quote
)

from html import escape

from utils.file_utils import (
    format_size,
    get_icon
)
from handlers import get_client_name


class DownloadHandler(BaseHTTPRequestHandler):
    """Serve directory listings and files from the configured shared folder."""

    def log_message(self, format, *args):
        """Suppress the base handler's default access log."""
        return

    def do_GET(self):
        """Route a GET request to a directory listing or file response."""

        request_path = unquote(self.path.split("?", 1)[0])

        target = (config.SHARED_DIR / request_path.lstrip("/")).resolve()

        try:
            target.relative_to(config.SHARED_DIR)
        except ValueError:
            self.send_error(403, "Forbidden")
            return

        if not target.exists():
            self.send_error(404, "Not Found")
            return

        if target.is_dir():
            self.show_directory(target)
            return

        self.send_file(target)

    def show_directory(self, directory):
        """Render and send an HTML listing for a shared directory."""

        relative = directory.relative_to(config.SHARED_DIR)

        items = []

        if directory != config.SHARED_DIR:

            parent = "/" + quote(relative.parent.as_posix(), safe="/") if relative.parent != Path(".") else "/"

            parent_html = (
                f'<p><a href="{parent}">⬅ Parent Directory</a></p>'
            )

        else:
            parent_html = ""

        entries = sorted(
            directory.iterdir(),
            key=lambda p: (not p.is_dir(), p.name.lower())
        )

        for entry in entries:

            icon = get_icon(entry)
            rel_path = "/" + quote(
                entry.relative_to(config.SHARED_DIR).as_posix(),
                safe="/"
            )

            name = escape(entry.name)

            if entry.is_dir():

                items.append(
                    f'<li>📁 <a href="{rel_path}">{name}/</a></li>'
                )

            else:

                size = format_size(entry.stat().st_size)
                items.append(
                    f'<li>{icon} <a href="{rel_path}">{name}</a>'
                    f'<span class="size">{size}</span> </li>'
                )

        file_list = "\n".join(items)

        html = load_template("download.html")

        html = html.replace(
            "{{CURRENT_PATH}}",
            escape(relative.as_posix())
        )

        html = html.replace(
            "{{PARENT_LINK}}",
            parent_html
        )

        html = html.replace(
            "{{FILE_LIST}}",
            file_list
        )

        encoded = html.encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(encoded))
        )

        self.end_headers()

        self.wfile.write(encoded)

    def send_file(self, file_path):
        """Stream a validated file to the requesting client."""

        mime_type, _ = mimetypes.guess_type(file_path)
        client = get_client_name(self.client_address, self.headers)
            
        if mime_type is None:
            mime_type = "application/octet-stream"
        print(f"[DOWNLOADED] {file_path.name} | by:- {client}")
        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.send_header(
            "Content-Disposition",
            f'attachment; filename="{file_path.name}"'
        )
        self.send_header(
            "Content-Length",
            str(file_path.stat().st_size)
        )
        self.end_headers()

        with open(file_path, "rb") as f:
            while chunk := f.read(1024 * 1024):
                self.wfile.write(chunk)
