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
Upload Handler

Provides:

- Single file uploads
- Multiple file uploads
- Folder uploads
- Folder structure preservation
- Duplicate filename protection

Uses python-multipart for efficient
multipart form parsing.
"""

from http.server import (
    BaseHTTPRequestHandler
)

from multipart import (
    MultipartParser,
    parse_options_header
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
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Upload Complete</title>

<style>

body{{
    background:#111;
    color:#eee;
    font-family:system-ui,sans-serif;
    margin:0;
    padding:20px;
}}

.container{{
    max-width:700px;
    margin:auto;
}}

.card{{
    background:#1a1a1a;
    border:1px solid #2a2a2a;
    border-radius:16px;
    padding:24px;
}}

h1{{
    margin-top:0;
}}

.success{{
    color:#10b981;
    font-size:1.1rem;
    margin-bottom:20px;
}}

ul{{
    list-style:none;
    padding:0;
}}

li{{
    padding:10px;
    border-bottom:1px solid #2a2a2a;
}}

li:last-child{{
    border-bottom:none;
}}

.actions{{
    margin-top:24px;
}}

.button{{
    display:inline-block;
    background:#10b981;
    color:white;
    text-decoration:none;
    padding:10px 16px;
    border-radius:8px;
    margin-right:10px;
}}

.button.secondary{{
    background:#333;
}}

.footer{{
    margin-top:24px;
    color:#666;
    font-size:.85rem;
}}

</style>

</head>

<body>

<div class="container">

<div class="card">

<h1>✅ Upload Complete</h1>

<p class="success">
Successfully uploaded {len(saved_files)} file(s)
</p>

<ul>
{files_html}
</ul>

<div class="actions">

<a href="/" class="button">
📤 Upload More
</a>

<a href="/uploads" class="button secondary">
📥 Open Inbox
</a>

</div>

<div class="footer">
LAN-Drop v1.0
</div>

</div>
</div>

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


    # get the client Infromation
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


    # Uncomment below method for using Ram buffer and No Stremed Output 
    # This one will chock ram for large files.
    # if streamed one doesn't works for your system comment that one and use this one instead
    # but keep in mind the treadoff of this method.
    #It Reads entire request into memory.

    # def do_POST(self):

    #     content_type = self.headers.get(
    #         "Content-Type"
    #     )

    #     if not content_type:
    #         self.send_error(400)
    #         return

    #     if "boundary=" not in content_type:
    #         self.send_error(400)
    #         return

    #     boundary = (
    #         content_type
    #         .split("boundary=")[-1]
    #         .encode()
    #     )

    #     content_length = int(
    #         self.headers.get(
    #             "Content-Length",
    #             0
    #         )
    #     )

    #     data = self.rfile.read(
    #         content_length
    #     )

    #     parts = data.split(
    #         b"--" + boundary
    #     )

    #     saved_files = []

    #     for part in parts:

    #         if b'filename="' not in part:
    #             continue

    #         try:

    #             header, filedata = part.split(
    #                 b"\r\n\r\n",
    #                 1
    #             )

    #         except ValueError:
    #             continue

    #         filename = self.parse_filename(
    #             header
    #         )

    #         if not filename:
    #             continue

    #         filedata = filedata.rsplit(
    #             b"\r\n",
    #             1
    #         )[0]

    #         saved_path = self.save_uploaded_file(
    #             filename,
    #             filedata
    #         )

    #         saved_files.append(
    #             saved_path
    #         )

    #     if not saved_files:

    #         self.send_error(400)
    #         return

    #     self.send_success_page(
    #         saved_files
    #     )


    # This one is Streamed Upload using the python library multipart 
    # which need to be installed systemwide 
    
    def do_POST(self):

        content_type = self.headers.get(
            "Content-Type"
        )

        client = self.get_client_name()
        
        if not content_type:
            self.send_error(400)
            return

        if "multipart/form-data" not in content_type:
            self.send_error(400)
            return

        content_length = int(
            self.headers.get(
                "Content-Length",
                0
            )
        )

        _, options = parse_options_header(
            content_type
        )

        boundary = options.get(
            "boundary"
        )

        if not boundary:
            self.send_error(400)
            return

        parser = MultipartParser(
            self.rfile,
            boundary.encode(),
            content_length
        )

        saved_files = []

        for part in parser:

            if not part.filename:
                continue

            target = self.get_upload_target(
                part.filename
            )

            part.save_as(
                str(target)
            )

            relative = str(
                target.relative_to(
                    config.UPLOAD_DIR
                )
            )

            saved_files.append(
                relative
            )

            print(
                f"[Received] | {relative} | from :- {client}"
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
