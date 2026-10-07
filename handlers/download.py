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
import config
from utils.templates import (
    load_template
)
import mimetypes
from urllib.parse import (
    unquote
)

from html import escape

from utils.file_utils import (
    format_size,
    get_icon
)


class DownloadHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return

    def do_GET(self):

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

        relative = directory.relative_to(config.SHARED_DIR)

        items = []

        if directory != config.SHARED_DIR:

            parent = "/" + str(relative.parent)

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
            rel_path = "/" + str(
                entry.relative_to(config.SHARED_DIR)
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
            escape(str(relative))
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

    def get_client_name(self):

        ip = self.client_address[0]

        user_agent = self.headers.get(
            "User-Agent",
            ""
        )

        if "Android" in user_agent:
            return f"Android ({ip})"

        if "iPhone" in user_agent:
            return f"iPhone ({ip})"

        if "Windows" in user_agent:
            return f"Windows PC ({ip})"

        if "Linux" in user_agent:
            return f"Linux PC ({ip})"

        return ip

    def send_file(self, file_path):

        mime_type, _ = mimetypes.guess_type(file_path)
        client = self.get_client_name()
            
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


