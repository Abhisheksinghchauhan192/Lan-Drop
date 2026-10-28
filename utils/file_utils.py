"""Filesystem validation and presentation helpers for LAN-Drop."""

from pathlib import Path


def sanitize_filename(name):
    """Return only the final filename component from a user-supplied name."""
    return Path(str(name).replace("\\", "/")).name


def ensure_upload_path(upload_dir, relative_path):
    """Validate an upload path and create its parent directory."""

    from pathlib import PurePosixPath

    relative_path = PurePosixPath(str(relative_path).replace("\\", "/"))

    if (
        relative_path.is_absolute()
        or not relative_path.parts
        or any(part in ("", ".", "..") for part in relative_path.parts)
        or relative_path.parts[0].endswith(":")
    ):
        raise ValueError("Invalid upload path")

    upload_dir = Path(upload_dir).resolve()
    target = (upload_dir / Path(*relative_path.parts)).resolve()

    try:
        target.relative_to(upload_dir)
    except ValueError:
        raise ValueError("Upload path is outside the upload directory") from None

    target.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return target


def format_size(size):
    """Format a byte count using a human-readable binary unit."""

    units = ["B", "KB", "MB", "GB", "TB"]

    size = float(size)

    for unit in units:

        if size < 1024:
            return f"{size:.1f} {unit}"

        size /= 1024

    return f"{size:.1f} PB"


def get_unique_filename(filepath: Path) -> Path:
    """Return an unused path, adding a numbered suffix when necessary."""

    if not filepath.exists():
        return filepath

    stem = filepath.stem
    suffix = filepath.suffix

    counter = 1

    while True:

        candidate = filepath.with_name(
            f"{stem} ({counter}){suffix}"
        )

        if not candidate.exists():
            return candidate

        counter += 1


def get_icon(path):
    """Return a display emoji based on a path's type or extension."""

    if path.is_dir():
        return "📁"

    suffix = path.suffix.lower()

    icons = {
        ".pdf": "📕",
        ".txt": "📄",
        ".md": "📝",

        ".jpg": "🖼️",
        ".jpeg": "🖼️",
        ".png": "🖼️",
        ".webp": "🖼️",

        ".mp3": "🎵",
        ".m4a": "🎵",
        ".flac": "🎵",

        ".mp4": "🎬",
        ".mkv": "🎬",
        ".avi": "🎬",

        ".zip": "📦",
        ".tar": "📦",
        ".gz": "📦",
        ".7z": "📦",

        ".iso": "💿",

        ".py": "🐍",
        ".js": "📜",
        ".html": "🌐",
        ".css": "🎨",
        ".cpp": "⚙️",
        ".java": "☕",
    }

    return icons.get(suffix, "📄")