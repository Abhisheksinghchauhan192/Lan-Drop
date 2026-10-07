from http.server import (
    BaseHTTPRequestHandler
)

from pathlib import Path
from utils.templates import (
    load_template
)
from html import escape

from utils.file_utils import (
    get_unique_filename,
    ensure_upload_path,
    get_icon,
    format_size
)

import config

# Upload Handler
class UploadHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return
    def do_GET(self):
        if self.path == "/uploads":
            return self.show_uploads()
        html = load_template("upload.html")

        encoded = html.encode()

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

    def save_uploaded_file(
        self,
        relative_path,
        filedata
    ):
        target = self.get_upload_target(
            relative_path
        )

        with open(
            target,
            "wb"
        ) as f:

            f.write(filedata)

        print(
            f"[UPLOAD] "
            f"{target.relative_to(config.UPLOAD_DIR)}"
        )

        return str(
            target.relative_to(
                config.UPLOAD_DIR
            )
        )

    def parse_filename(
        self,
        header_bytes
    ):

        if b'filename="' not in header_bytes:
            return None

        try:

            filename = (
                header_bytes
                .split(b'filename="')[1]
                .split(b'"')[0]
                .decode(
                    "utf-8",
                    errors="ignore"
                )
            )

            return filename

        except Exception:

            return None
    
    
    def get_upload_target(
        self,
        relative_path
    ):

        relative_path = relative_path.replace(
            "\\",
            "/"
        )

        relative_path = str(
            Path(relative_path)
        )

        target = (
            config.UPLOAD_DIR /
            relative_path
        )

        target.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if target.exists():

            target = get_unique_filename(
                target
            )

        return target
    
    def send_success_page(
        self,
        saved_files
    ):

        files_html = "".join(
            f"<li>{escape(name)}</li>"
            for name in saved_files
        )

        response = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Upload Complete</title>
    </head>

    <body>

    <h2>Upload Successful</h2>

    <p>
    Saved {len(saved_files)} file(s)
    </p>

    <ul>
    {files_html}
    </ul>

    <br>

    <a href="/">
    Upload More Files
    </a>

    </body>
    </html>
    """

        encoded = response.encode(
            "utf-8"
        )

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

    def do_POST(self):

        content_type = self.headers.get(
            "Content-Type"
        )

        if not content_type:
            self.send_error(400)
            return

        if "boundary=" not in content_type:
            self.send_error(400)
            return

        boundary = (
            content_type
            .split("boundary=")[-1]
            .encode()
        )

        content_length = int(
            self.headers.get(
                "Content-Length",
                0
            )
        )

        data = self.rfile.read(
            content_length
        )

        parts = data.split(
            b"--" + boundary
        )

        saved_files = []

        for part in parts:

            if b'filename="' not in part:
                continue

            try:

                header, filedata = part.split(
                    b"\r\n\r\n",
                    1
                )

            except ValueError:
                continue

            filename = self.parse_filename(
                header
            )

            if not filename:
                continue

            filedata = filedata.rsplit(
                b"\r\n",
                1
            )[0]

            saved_path = self.save_uploaded_file(
                filename,
                filedata
            )

            saved_files.append(
                saved_path
            )

        if not saved_files:

            self.send_error(400)
            return

        self.send_success_page(
            saved_files
        )


    # showing LAN-Drop files
    def show_uploads(self):

        items = []

        entries = sorted(
            config.UPLOAD_DIR.iterdir(),
            key=lambda p: (not p.is_dir(), p.name.lower())
        )

        for entry in entries:

            icon = get_icon(entry)

            name = escape(entry.name)

            if entry.is_dir():

                items.append(
                    f'<li>{icon} {name}/</li>'
                )

            else:

                size = format_size(
                    entry.stat().st_size
                )

                items.append(
                    f'<li>{icon} {name}'
                    f' <span class="size">{size}</span>'
                    f'</li>'
                )

        html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>LAN-Drop Inbox</title>

    <style>

    body {{
        font-family: sans-serif;
        max-width: 900px;
        margin: auto;
        padding: 20px;
        background: #111;
        color: #eee;
    }}

    a {{
        color: #6cb6ff;
    }}

    ul {{
        list-style: none;
        padding: 0;
    }}

    li {{
        padding: 10px;
        border-bottom: 1px solid #333;
    }}

    .size {{
        float: right;
        color: #888;
    }}

    </style>
    </head>

    <body>

    <h1>📥 LAN-Drop Inbox</h1>

    <p>
    Uploaded files received on this device.
    </p>

    <ul>
    {''.join(items)}
    </ul>

    </body>
    </html>
    """

        encoded = html.encode()

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
