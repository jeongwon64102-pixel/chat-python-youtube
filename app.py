from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from pathlib import Path
import os

from main import get_video_and_audio


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")


BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio"
VIDEO_DIR = BASE_DIR / "video"


TEMPLATE = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>YouTube Downloader</title>
  <style>
    :root {
      --sky: #e7f4ff;
      --sky-strong: #57a9ff;
      --text: #0f172a;
      --card: #ffffff;
      --border: #dbeafe;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: linear-gradient(180deg, var(--sky) 0%, #cfe8ff 100%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }
    .card {
      width: min(680px, 100%);
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow: 0 12px 50px rgba(87, 169, 255, 0.25);
      padding: 28px;
    }
    h1 {
      margin: 0 0 12px;
      font-size: 26px;
      color: #0b63c5;
      letter-spacing: -0.5px;
    }
    p.desc {
      margin: 0 0 20px;
      color: #475569;
    }
    form {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }
    input[type="url"] {
      flex: 1;
      min-width: 260px;
      padding: 12px 14px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: #f8fbff;
      font-size: 15px;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    input[type="url"]:focus {
      outline: none;
      border-color: var(--sky-strong);
      box-shadow: 0 0 0 3px rgba(87, 169, 255, 0.2);
    }
    button {
      padding: 12px 20px;
      border: none;
      border-radius: 10px;
      background: linear-gradient(135deg, #57a9ff, #6dd5ff);
      color: white;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 8px 20px rgba(87, 169, 255, 0.35);
      transition: transform 0.1s ease, box-shadow 0.1s ease;
    }
    button:hover { transform: translateY(-1px); }
    button:active { transform: translateY(1px); box-shadow: 0 4px 12px rgba(87, 169, 255, 0.3); }
    .alerts {
      margin-top: 16px;
      display: grid;
      gap: 10px;
    }
    .alert {
      padding: 12px 14px;
      border-radius: 10px;
      border: 1px solid #bfdbfe;
      background: #eff6ff;
      color: #0f172a;
    }
    .alert.error {
      border-color: #fecdd3;
      background: #fff1f2;
      color: #9f1239;
    }
    .downloads {
      margin-top: 18px;
      display: grid;
      gap: 10px;
    }
    .download-card {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 14px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: #f8fbff;
    }
    .download-card a {
      color: #0b63c5;
      font-weight: 600;
      text-decoration: none;
    }
    footer {
      margin-top: 18px;
      color: #475569;
      font-size: 13px;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>YouTube 오디오/비디오 다운로드</h1>
    <p class="desc">URL을 입력하면 최고 품질의 오디오와 비디오를 다운로드합니다.</p>
    <form method="post" action="{{ url_for('index') }}">
      <input type="url" name="url" placeholder="https://www.youtube.com/watch?v=..." value="{{ url or '' }}" required>
      <button type="submit">다운로드</button>
    </form>

    {% if messages %}
    <div class="alerts">
      {% for m in messages %}
      <div class="alert {{ m.category }}">{{ m.text }}</div>
      {% endfor %}
    </div>
    {% endif %}

    {% if audio_file or video_file %}
    <div class="downloads">
      {% if audio_file %}
      <div class="download-card">
        <span>오디오 파일</span>
        <a href="{{ url_for('download_file', kind='audio', filename=audio_file) }}">다운로드</a>
      </div>
      {% endif %}
      {% if video_file %}
      <div class="download-card">
        <span>비디오 파일</span>
        <a href="{{ url_for('download_file', kind='video', filename=video_file) }}">다운로드</a>
      </div>
      {% endif %}
    </div>
    {% endif %}

    <footer>pytubefix 기반 · 네트워크 환경에 따라 시간이 걸릴 수 있습니다.</footer>
  </div>
</body>
</html>
"""


def _filename_from_path(path: str) -> str:
    return secure_filename(Path(path).name)


@app.route("/", methods=["GET", "POST"])
def index():
    url = ""
    audio_file = None
    video_file = None
    messages = []

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        try:
            audio_path, video_path = get_video_and_audio(url)
            audio_file = _filename_from_path(audio_path)
            video_file = _filename_from_path(video_path)
            messages.append({"category": "", "text": "다운로드가 완료되었습니다."})
        except Exception as exc:  # noqa: BLE001
            messages.append({"category": "error", "text": f"오류: {exc}"})

    return render_template_string(
        TEMPLATE,
        url=url,
        audio_file=audio_file,
        video_file=video_file,
        messages=messages,
    )


@app.route("/download/<kind>/<filename>")
def download_file(kind: str, filename: str):
    if kind == "audio":
        return send_from_directory(AUDIO_DIR, filename, as_attachment=True)
    if kind == "video":
        return send_from_directory(VIDEO_DIR, filename, as_attachment=True)
    flash("잘못된 파일 유형입니다.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
