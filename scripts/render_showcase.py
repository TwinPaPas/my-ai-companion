"""Render an explicitly edited 30-second replay of the captured real CLI replies.

Optional authoring dependencies: Pillow and imageio-ffmpeg. Not SAI runtime deps.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import textwrap

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", required=True, help="Path to a readable TrueType monospace font")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    capture = root / "docs/verification/showcase-0.1.1.json"
    record = json.loads(capture.read_text(encoding="utf-8"))
    if record["status"] != "PASS":
        raise ValueError("Refusing to render a failed or incomplete recording")
    replies = [s for s in record["steps"] if "reply" in s]
    if len(replies) != 4:
        raise ValueError("Expected conflict, recall, gift and apology replies")
    # Exact excerpts from this capture; refuse to reuse them for different replies.
    quotes = [
        "I told you my appearance is off-limits, so no, that wasn't funny",
        "You teased me about my looks after I told you that's off-limits",
        "They're lovely, thanks, but flowers don't cancel out you teasing my looks",
        "Thanks for actually owning the appearance thing, that means more than the flowers did",
    ]
    for entry, quote in zip(replies, quotes):
        if quote not in " ".join(entry["reply"].split()):
            raise ValueError("An editorial excerpt no longer matches its recorded source")
        entry["excerpt"] = quote + " ..."
    font = lambda n: ImageFont.truetype(args.font, n)
    small, body, heading, title = font(22), font(30), font(40), font(56)
    background, panel, white, muted = "#11141c", "#1b2030", "#eef0f5", "#a8b0c4"
    accent, warm = "#a7dfd3", "#ffb8c5"
    scenes = [
        (3, "SAI", "Your usual AI. A story that stays.", None,
         "Real Claude replies in standalone SAI chat.\nEnglish-first pilot · v0.1.1"),
        (6, "01 / A joke goes too far", "/sai act tease appearance", replies[0],
         "The same topic was teased twice. Ari's mood: angry."),
        (4, "02 / Close. Start again.", "Previous chat process: exited (code 0)\nNew CLI process: python -m sai status", None,
         "Ari · ON · Angry\nStill on their mind: appearance\nSame saved character and concern, read by a fresh process."),
        (6, "03 / The story is still there", "You still seem upset. What happened earlier?", replies[1],
         "Fresh process. Same stored relationship and recent conversation."),
        (5, "04 / Flowers are not a reset", "/sai act gift flowers", replies[2],
         "Mood: angry · The concern is still unresolved."),
        (6, "05 / A little closer", "/sai act apologize I'm sorry for teasing your appearance", replies[3],
         f"Irritation: {replies[2]['irritation']} → {replies[3]['irritation']} · Angry → sulking\nAn apology helps. It does not erase everything at once."),
    ]
    frames = []
    excerpts = []
    for duration, label, command, entry, note in scenes:
        canvas = Image.new("RGB", (1600, 900), background)
        draw = ImageDraw.Draw(canvas)
        draw.text((65, 42), "SAI   /   a little closer, one conversation at a time", font=small, fill=accent)
        draw.text((65, 100), label, font=title if entry is None else heading, fill=white)
        draw.rounded_rectangle((55, 195, 1545, 735), radius=22, fill=panel)
        for x, color in [(85, "#f5848a"), (112, "#e9c47d"), (139, "#88c5a4")]:
            draw.ellipse((x, 216, x + 12, 228), fill=color)
        y = 260
        for original in command.splitlines():
            for line in textwrap.wrap(original, width=75):
                draw.text((85, y), line, font=body, fill=accent)
                y += 42
        if entry:
            y += 24
            reply = entry["excerpt"]
            lines = textwrap.wrap(reply, width=75)
            if len(lines) > 6:
                lines = lines[:6]
                lines[-1] = lines[-1].rstrip() + " ..."
            displayed = "\n".join(lines)
            excerpts.append({"scene": label, "displayed_reply": displayed, "source_reply": entry["reply"]})
            draw.text((85, y), "Ari:", font=small, fill=warm)
            y += 36
            for line in lines:
                draw.text((85, y), line, font=body, fill=white)
                y += 42
            if y > 725:
                raise ValueError("Reply would overflow the terminal panel")
        else:
            y += 45
            for line in note.splitlines():
                draw.text((85, y), line, font=body, fill=white)
                y += 50
        if entry:
            for i, line in enumerate(note.splitlines()):
                draw.text((65, 760 + i * 30), line, font=small, fill=muted)
        draw.text((65, 850), "EDITED PLAYBACK · real reply excerpts · wait times compressed · full transcript linked", font=small, fill=muted)
        frames.append((duration, canvas))
    dist = root / "dist"
    dist.mkdir(exist_ok=True)
    video = dist / "sai-0.1.1-showcase.mp4"
    gif = dist / "sai-0.1.1-showcase.gif"
    poster = dist / "sai-0.1.1-showcase-poster.png"
    # Contact sheet is kept as a release artifact so the visual check is reproducible.
    sheet = Image.new("RGB", (1600, 1350), background)
    for i, (_, frame) in enumerate(frames):
        sheet.paste(frame.resize((800, 450)), ((i % 2) * 800, (i // 2) * 450))
    sheet.save(poster)
    flags = subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 0
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    command = [ffmpeg, "-y", "-v", "error", "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "1600x900", "-r", "10", "-i", "-", "-an", "-c:v", "libx264", "-threads", "2",
               "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=flags)
    for duration, frame in frames:
        pixels = frame.tobytes()
        for _ in range(duration * 10):
            process.stdin.write(pixels)
    process.stdin.close()
    error = process.stderr.read().decode("utf-8", errors="replace")
    if process.wait(timeout=60):
        raise RuntimeError(error)
    subprocess.run([ffmpeg, "-y", "-v", "error", "-threads", "2", "-i", str(video), "-filter_complex_threads", "1",
                    "-filter_complex", "fps=5,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=none",
                    "-loop", "0", str(gif)], capture_output=True, check=True, timeout=90, creationflags=flags)
    reader = imageio_ffmpeg.read_frames(str(video), pix_fmt="rgb24")
    metadata = next(reader)
    reader.close()
    if abs(metadata["duration"] - 30) > 0.1:
        raise ValueError("Expected a 30-second video")
    evidence = {"status": "PASS", "duration_seconds": metadata["duration"], "size": metadata["size"],
                "format": "Edited terminal-style playback, not a real-time screen capture", "capture": capture.name,
                "artifacts": [{"file": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
                              for p in (video, gif, poster)], "excerpts": excerpts}
    (root / "docs/verification/showcase-render-0.1.1.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: evidence[k] for k in ("status", "duration_seconds", "size", "artifacts")}))


if __name__ == "__main__":
    main()
