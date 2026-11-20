# Finds a seamless loop in a Suno song: compares the music around every pair of beats a whole number of bars apart.
# Usage: python3 tools/find_loop.py song.wav <shortest loop s> <longest loop s>   (then tools/cut_loop.py cuts it)
import sys, numpy as np, librosa, soundfile as sf
f, lo, hi = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
y, sr = sf.read(f, dtype='float32'); mono = y.mean(1)
dur = len(mono) / sr
hop = 512
tempo, beats = librosa.beat.beat_track(y=mono, sr=sr, hop_length=hop, units='frames')
bt = librosa.frames_to_time(beats, sr=sr, hop_length=hop)
chroma = librosa.feature.chroma_cqt(y=mono, sr=sr, hop_length=hop)
mfcc = librosa.feature.mfcc(y=mono, sr=sr, hop_length=hop, n_mfcc=20)
mfcc = (mfcc - mfcc.mean(1, keepdims=True)) / (mfcc.std(1, keepdims=True) + 1e-6)
feat = np.vstack([chroma * 3, mfcc * 0.5])
rms = librosa.feature.rms(y=mono, hop_length=hop)[0]
W = 8  # beats compared on each side
def seg(b0, b1):
    return feat[:, beats[b0]:beats[b1]]
def sim(i, j):
    if i - W < 0 or j + W >= len(beats) or i + W >= len(beats): return -1
    s = 0
    for (a0, a1, c0, c1) in [(i, i + W, j, j + W), (i - W, i, j - W, j)]:
        A, B = seg(a0, a1), seg(c0, c1)
        n = min(A.shape[1], B.shape[1]); A, B = A[:, :n], B[:, :n]
        s += np.sum(A * B) / (np.linalg.norm(A) * np.linalg.norm(B) + 1e-9)
    return s / 2
loud = np.median(rms)
res = []
for i in range(W, len(beats)):
    if bt[i] < 1.0 or bt[i] > dur * 0.5: continue
    if rms[beats[i]] < 0.3 * loud: continue
    for k in range(4, 200, 4):   # whole bars of 4 beats
        j = i + k
        if j + W >= len(beats): break
        L = bt[j] - bt[i]
        if L < lo or L > hi: continue
        if bt[j] > dur - 4: continue
        res.append((sim(i, j), i, j, bt[i], bt[j], L))
res.sort(reverse=True)
print('tempo', tempo, 'dur', round(dur, 2), 'beats', len(beats))
for r in res[:8]: print('score %.4f  i=%d j=%d  start=%.3f end=%.3f len=%.3f' % r)
