"""Helpers for loading LAN-Drop's HTML templates."""

from pathlib import Path

TEMPLATE_DIR = (
    Path(__file__).parent.parent
    / "templates"
)

def load_template(name):
    """Read and return a UTF-8 template from the templates directory."""

    with open(
        TEMPLATE_DIR / name,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()
