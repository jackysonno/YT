"""
Core download logic for YouTube Media Downloader.

Wraps yt-dlp to export YouTube videos as the highest quality MP3 (audio)
or as MP4 (video), with either the best available resolution or a
specific one (e.g. 1080p, 720p).
"""

import os
import yt_dlp


def _resolve_output_path(ydl, info: dict, fallback_ext: str) -> str:
    """Best-effort resolution of the final file path after download and
    post-processing (the final extension can differ from the source
    format's extension)."""
    downloads = info.get("requested_downloads")
    if downloads:
        path = downloads[0].get("filepath") or downloads[0].get("_filename")
        if path:
            return path
    base, _ = os.path.splitext(ydl.prepare_filename(info))
    return f"{base}.{fallback_ext}"


def download_audio(url: str, output_dir: str = "downloads") -> str:
    """Download the best available audio and export it as the highest
    quality MP3 possible."""
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",  # 0 = best VBR quality for mp3
            }
        ],
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return _resolve_output_path(ydl, info, "mp3")


def download_video(url: str, output_dir: str = "downloads", quality: str = "best") -> str:
    """Download a video as MP4.

    quality: "best" for the highest available resolution, or a target
    resolution such as "1080p", "720p", "480p", "360p".
    """
    os.makedirs(output_dir, exist_ok=True)

    if quality.lower() == "best":
        format_selector = "bestvideo+bestaudio/best"
    else:
        height = quality.lower().replace("p", "").strip()
        format_selector = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

    ydl_opts = {
        "format": format_selector,
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return _resolve_output_path(ydl, info, "mp4")


def list_available_qualities(url: str) -> list:
    """Return the distinct video resolutions available for a URL, sorted
    from highest to lowest, e.g. ['1080p', '720p', '480p']."""
    ydl_opts = {"quiet": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    heights = sorted(
        {f.get("height") for f in info.get("formats", []) if f.get("height")},
        reverse=True,
    )
    return [f"{h}p" for h in heights]
