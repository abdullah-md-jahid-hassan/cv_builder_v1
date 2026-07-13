#!/usr/bin/env python3
"""CV Builder.

Renders a CV template folder (cv.html + user_data.json) into a PDF or a
self-contained HTML file.

Usage:
    python3 main.py <cv_folder> <target_file_path> <-p|-h>

    <cv_folder>         Folder containing cv.html, data_stricture.json and
                        user_data.json (e.g. ./modern_navy_cv)
    <target_file_path>  Output path. Extension is added automatically if
                        missing. If it is an existing directory the file is
                        written inside it, named after the cv folder.
    -p                  Output PDF
    -h                  Output HTML

Example:
    python3 main.py ./modern_navy_cv ./result -p
"""

import base64
import json
import mimetypes
import re
import sys
from pathlib import Path

USAGE = "Usage: python3 main.py <cv_folder> <target_file_path> <-p|-h>\nExample: python3 main.py ./modern_navy_cv ./result -p"


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def parse_args(argv):
    if len(argv) != 4:
        print(USAGE, file=sys.stderr)
        sys.exit(1)

    cv_folder = Path(argv[1]).resolve()
    target = Path(argv[2])
    fmt_flag = argv[3].lower()

    if fmt_flag not in ("-p", "-h"):
        fail(f"unknown format flag '{argv[3]}'. Use -p for PDF or -h for HTML.")

    return cv_folder, target, ("pdf" if fmt_flag == "-p" else "html")


def load_data(cv_folder: Path) -> dict:
    user_data = cv_folder / "user_data.json"
    dummy_data = cv_folder / "data_stricture.json"

    if user_data.is_file():
        source = user_data
    elif dummy_data.is_file():
        print(f"Warning: {user_data.name} not found in {cv_folder.name}/, "
              f"falling back to dummy data from {dummy_data.name}.")
        source = dummy_data
    else:
        fail(f"neither user_data.json nor data_stricture.json found in {cv_folder}")

    try:
        with open(source, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        fail(f"{source.name} is not valid JSON: {exc}")


def render_html(cv_folder: Path, data: dict) -> str:
    try:
        from jinja2 import Environment, FileSystemLoader, ChainableUndefined
    except ImportError:
        fail("jinja2 is not installed. Run: pip install -r requirements.txt")

    env = Environment(
        loader=FileSystemLoader(str(cv_folder)),
        undefined=ChainableUndefined,
        autoescape=True,
    )
    template = env.get_template("cv.html")
    return template.render(**data)


def resolve_target(target: Path, cv_folder: Path, fmt: str) -> Path:
    ext = f".{fmt}"
    if target.is_dir():
        out = target / (cv_folder.name + ext)
    elif target.suffix.lower() == ext:
        out = target
    else:
        out = target.with_name(target.name + ext)
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def embed_local_images(html: str, base_dir: Path) -> str:
    """Inline local image files as data URIs so the HTML is self-contained."""

    def replace(match):
        src = match.group(2)
        if src.startswith(("data:", "http://", "https://", "//")):
            return match.group(0)
        img_path = (base_dir / src).resolve()
        if not img_path.is_file():
            print(f"Warning: image '{src}' not found, leaving reference as-is.")
            return match.group(0)
        mime = mimetypes.guess_type(str(img_path))[0] or "application/octet-stream"
        encoded = base64.b64encode(img_path.read_bytes()).decode("ascii")
        return f'{match.group(1)}data:{mime};base64,{encoded}{match.group(3)}'

    return re.sub(r'(src=")([^"]+)(")', replace, html)


def write_pdf(html: str, base_dir: Path, out_path: Path) -> None:
    try:
        from weasyprint import HTML
    except ImportError:
        fail("weasyprint is not installed. Run: pip install -r requirements.txt")

    HTML(string=html, base_url=str(base_dir)).write_pdf(str(out_path))


def main():
    cv_folder, target, fmt = parse_args(sys.argv)

    if not cv_folder.is_dir():
        fail(f"cv folder not found: {cv_folder}")
    if not (cv_folder / "cv.html").is_file():
        fail(f"cv.html not found in {cv_folder}")

    data = load_data(cv_folder)
    html = render_html(cv_folder, data)
    out_path = resolve_target(target, cv_folder, fmt)

    if fmt == "html":
        out_path.write_text(embed_local_images(html, cv_folder), encoding="utf-8")
    else:
        write_pdf(html, cv_folder, out_path)

    print(f"Done: {out_path}")


if __name__ == "__main__":
    main()
