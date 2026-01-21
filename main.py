from pytubefix import YouTube
import os
from pathlib import Path


def _ensure_directories() -> None:
    """Create output directories if they do not exist."""
    Path("audio").mkdir(parents=True, exist_ok=True)
    Path("video").mkdir(parents=True, exist_ok=True)


def get_video_and_audio(url: str):
    """
    Download audio (best available) and video (best progressive mp4) for the given YouTube URL.
    Returns tuple of (audio_path, video_path).
    """
    if not url:
        raise ValueError("URL이 비어 있습니다.")

    _ensure_directories()
    yt = YouTube(url)

    audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    if audio_stream is None:
        raise ValueError("오디오 스트림을 찾지 못했습니다.")
    audio_file_path = audio_stream.download(output_path="audio")

    video_stream = (
        yt.streams.filter(progressive=True, file_extension="mp4")
        .order_by("resolution")
        .desc()
        .first()
    )
    if video_stream is None:
        raise ValueError("비디오 스트림을 찾지 못했습니다.")
    video_file_path = video_stream.download(output_path="video")

    return audio_file_path, video_file_path


if __name__ == "__main__":
    url = input("YouTube 동영상 URL을 입력하세요: ")
    audio_file_path, video_file_path = get_video_and_audio(url)
    print(f"오디오 파일 경로: {audio_file_path}")
    print(f"비디오 파일 경로: {video_file_path}")

