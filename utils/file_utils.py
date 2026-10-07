from pathlib import Path


def sanitize_filename(name):
    return Path(name).name


def ensure_upload_path(upload_dir, relative_path):

    relative_path = relative_path.replace("\\", "/")

    target = upload_dir / relative_path

    target.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return target


def format_size(size):

    units = ["B", "KB", "MB", "GB", "TB"]

    size = float(size)

    for unit in units:

        if size < 1024:
            return f"{size:.1f} {unit}"

        size /= 1024

    return f"{size:.1f} PB"


def get_unique_filename(filepath: Path) -> Path:

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