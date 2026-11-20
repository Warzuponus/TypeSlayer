# Cuts a loop found by tools/find_loop.py. Usage: python3 tools/cut_loop.py song.wav loop.wav <start s> <end s>
# Then: ffmpeg -i loop.wav -af volume=<gain to reach -16.4 LUFS>dB -ar 44100 -c:a libmp3lame -b:a 128k music/<name>.mp3
import sys, numpy as np, soundfile as sf
f, out, a, b = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
y, sr = sf.read(f, dtype='float32'); m = y.mean(1)
A, B = int(round(a * sr)), int(round(b * sr))
# 1. snap the end so the waveform just after it best matches the waveform just after the start (search +-20 ms)
win, srch = int(0.05 * sr), int(0.02 * sr)
ref = m[A:A + win]
best, bo = -9, 0
for o in range(-srch, srch + 1):
    seg = m[B + o:B + o + win]
    c = np.dot(ref, seg) / (np.linalg.norm(ref) * np.linalg.norm(seg) + 1e-9)
    if c > best: best, bo = c, o
B += bo
# 2. cut, then crossfade the last X samples: fade out the original tail while fading in the audio that leads into the start
X = int(0.03 * sr)
loop = y[A:B].copy()
t = np.linspace(0, 1, X, dtype='float32')[:, None]
fi, fo = np.sqrt(t), np.sqrt(1 - t)
loop[-X:] = loop[-X:] * fo + y[A - X:A] * fi
# seam check: jump size at the wrap compared with typical sample-to-sample change
jump = np.abs(loop[0] - loop[-1]).max(); typ = np.abs(np.diff(loop[:, 0])).mean()
sf.write(out, loop, sr, subtype='FLOAT')
print('corr %.3f shift %+.1f ms  len %.3f s  samples %d  seam jump %.4f (typ %.4f)' % (best, bo / sr * 1000, len(loop) / sr, len(loop), jump, typ))
