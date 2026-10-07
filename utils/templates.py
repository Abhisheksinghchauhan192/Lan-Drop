from pathlib import Path

TEMPLATE_DIR = (
    Path(__file__).parent.parent
    / "templates"
)

def load_template(name):

    with open(
        TEMPLATE_DIR / name,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()
