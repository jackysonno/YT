"""
Command-line interface for YouTube Media Downloader.

Examples:
    python cli.py "https://youtube.com/watch?v=XXXX" --type audio
    python cli.py "https://youtube.com/watch?v=XXXX" --type video --quality 1080p
    python cli.py "https://youtube.com/watch?v=XXXX" --type video --quality best
    python cli.py "https://youtube.com/watch?v=XXXX" --list-qualities
"""

import argparse
import sys

from downloader import download_audio, download_video, list_available_qualities


def main():
    parser = argparse.ArgumentParser(
        description="Convert a YouTube link into an MP3 (audio) or MP4 (video) file."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--type",
        choices=["audio", "video"],
        help="Output type: audio (mp3) or video (mp4). Required unless --list-qualities is used.",
    )
    parser.add_argument(
        "--quality",
        default="best",
        help="Video quality: best, 1080p, 720p, 480p, etc. "
        "(ignored for audio, which always exports at the highest quality)",
    )
    parser.add_argument(
        "--output",
        default="downloads",
        help="Output directory (default: downloads/)",
    )
    parser.add_argument(
        "--list-qualities",
        action="store_true",
        help="List the available video resolutions for this URL and exit",
    )

    args = parser.parse_args()

    if args.list_qualities:
        qualities = list_available_qualities(args.url)
        print("Available qualities:", ", ".join(qualities) if qualities else "N/A")
        return

    if not args.type:
        parser.error("--type is required (audio or video) unless using --list-qualities")

    try:
        if args.type == "audio":
            path = download_audio(args.url, args.output)
        else:
            path = download_video(args.url, args.output, args.quality)
        print(f"Done! File saved to: {path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
