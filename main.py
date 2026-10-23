"""WaveSift: a local CLI tool for converting YouTube audio to MP3."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import yt_dlp
except ImportError:  # pragma: no cover - show the user installation instructions
    yt_dlp = None


YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be"}


def is_youtube_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and parsed.hostname in YOUTUBE_HOSTS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="WaveSift extracts audio from YouTube URLs and saves it as MP3."
    )
    parser.add_argument(
        "urls",
        nargs="*",
        help="YouTube URLs to process. If omitted, URLs are requested in the terminal.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("downloads"),
        help="Directory for MP3 files (default: ./downloads).",
    )
    parser.add_argument(
        "--quality",
        choices=tuple(str(value) for value in range(0, 11)),
        default="0",
        help="MP3 VBR quality: 0 is best, 10 is worst (default: 0).",
    )
    return parser.parse_args()


def read_urls() -> list[str]:
    print("Enter YouTube URLs, one per line. Leave a blank line when finished:")
    urls: list[str] = []
    while True:
        try:
            value = input().strip()
        except EOFError:
            break
        if not value:
            break
        urls.append(value)
    return urls


def download_audio(url: str, output_dir: Path, quality: str) -> None:
    options = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": str(output_dir / "%(title)s [%(id)s].%(ext)s"),
        "windowsfilenames": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }
        ],
    }
    with yt_dlp.YoutubeDL(options) as downloader:
        downloader.download([url])


def main() -> int:
    args = parse_args()
    urls = args.urls or read_urls()
    if not urls:
        print("Error: Provide at least one YouTube URL.", file=sys.stderr)
        return 2

    invalid_urls = [url for url in urls if not is_youtube_url(url)]
    if invalid_urls:
        for url in invalid_urls:
            print(f"Invalid YouTube URL: {url}", file=sys.stderr)
        return 2

    if yt_dlp is None:
        print("Error: yt-dlp is not installed. Run 'python -m pip install -r requirements.txt'.", file=sys.stderr)
        return 1

    missing_tools = [tool for tool in ("ffmpeg", "ffprobe") if shutil.which(tool) is None]
    if missing_tools:
        print(
            "Error: FFmpeg tools not found (" + ", ".join(missing_tools) + "). "
            "See README.md for installation instructions.",
            file=sys.stderr,
        )
        return 1

    try:
        args.output.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"Could not create output directory: {error}", file=sys.stderr)
        return 1

    failures = 0
    for index, url in enumerate(urls, start=1):
        print(f"\n[{index}/{len(urls)}] Processing: {url}")
        try:
            download_audio(url, args.output, args.quality)
        except yt_dlp.utils.DownloadError as error:
            failures += 1
            print(f"Download failed: {error}", file=sys.stderr)
        except Exception as error:  # Handle other runtime errors from yt-dlp or FFmpeg.
            failures += 1
            print(f"Processing failed: {error}", file=sys.stderr)

    completed = len(urls) - failures
    print(f"\nFinished: processed {completed}/{len(urls)} URL(s). Output directory: {args.output.resolve()}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
