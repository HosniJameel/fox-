"""Pipe render_frames.js output into a near-lossless intermediate (composite.mp4, no audio)."""
import io, struct, subprocess, sys, os
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
node = subprocess.Popen(["node", os.path.join(here, "render_frames.js")], stdout=subprocess.PIPE)
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", "30", "-i", "-",
                       "-c:v", "libx264", "-preset", "slow", "-crf", "8", "-pix_fmt", "yuv444p", os.path.join(here, "composite.tmp.mp4")], stdin=subprocess.PIPE)
def rd(k):
    b = b""
    while len(b) < k:
        c = node.stdout.read(k - len(b))
        if not c: return None
        b += c
    return b
n = 0
while True:
    h = rd(4)
    if h is None: break
    ff.stdin.write(Image.open(io.BytesIO(rd(struct.unpack(">I", h)[0]))).convert("RGB").tobytes()); n += 1
ff.stdin.close(); ff.wait(); node.wait()
print("frames", n)
