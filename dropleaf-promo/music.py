# Original 112 BPM lo-fi bed + SFX from the edit's cue list.  python3 music.py out/reel_cues.json out/reel_audio.wav reel|story
import json, sys, numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

cfg = json.load(open(sys.argv[1])); OUT = sys.argv[2]; V = sys.argv[3]
SR = 48000; FPS = cfg['fps']; BEAT = 60 / 112
N = int(cfg['frames'] / FPS * SR) + SR // 2
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def add(buf, x, t, g=1.0):
    i = int(t * SR); j = min(N, i + len(x));
    if i < N: buf[i:j] += x[:j - i] * g
def addst(x, t, g=1.0, pan=0.0):
    add(L, x, t, g * (1 - max(0, pan))); add(R, x, t, g * (1 + min(0, pan)))
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
T = lambda n: np.arange(int(n * SR)) / SR

# arrangement (in beats): where the drums drop out, where the riser goes
if V == 'reel':
    total_beats = 49; breaks = [(12, 14), (38, 42)]; riser = (12, 14); outro = 42; first_drums = 4
else:
    total_beats = 29; breaks = [(22.5, 22.75)]; riser = (7, 8); outro = 22.5; first_drums = 3
in_break = lambda b: any(a <= b < c for a, c in breaks)

# chords: Am9  Fmaj7  Cmaj7  G6  (one bar each)
CH = [[57, 60, 64, 67, 71], [53, 57, 60, 64, 69], [48, 55, 59, 64, 67], [55, 59, 62, 64, 67]]
ROOT = [45, 41, 48, 43]
def epiano(m, dur):
    t = T(dur); f = hz(m); env = np.exp(-t * 2.2) * (1 - np.exp(-t * 300))
    x = (np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*2*f*t)*np.exp(-t*5) + .12*np.sin(2*np.pi*3.01*f*t)*np.exp(-t*8))
    return x * env * (1 + .08*np.sin(2*np.pi*4.5*t))
def kick():
    t = T(.35); f = 45 + 80*np.exp(-t*28); ph = 2*np.pi*np.cumsum(f)/SR
    return np.sin(ph) * np.exp(-t*9) + .3*rng.standard_normal(len(t))*np.exp(-t*120)
def snare():
    t = T(.25); n = bp(rng.standard_normal(len(t)), 900, 6000) * np.exp(-t*18)
    return n + .4*np.sin(2*np.pi*190*t)*np.exp(-t*25)
def hat(open_=False):
    t = T(.12 if not open_ else .3); return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t*(55 if not open_ else 14))
def bass(m, dur):
    t = T(dur); f = hz(m - 12); return (np.sin(2*np.pi*f*t) + .4*np.sin(4*np.pi*f*t) + .15*np.sin(6*np.pi*f*t)) * np.minimum(1, t*80) * np.exp(-t*1.1)

keys = np.zeros(N); drums = np.zeros(N); bas = np.zeros(N); duck = np.ones(N)
nb = int(total_beats)
for bar in range(0, nb // 4 + 1):
    b0 = bar * 4; c = bar % 4
    if b0 >= total_beats: break
    for hit, g in ((0, 1.0), (1.5, .55), (2.75, .4)):
        if b0 + hit < total_beats:
            for k, m in enumerate(CH[c]): add(keys, epiano(m, 2.4), (b0 + hit) * BEAT + k * .012, .34 * g)
    for hit, d in ((0, 1.4), (2.5, 1.2)):
        if b0 + hit < total_beats and b0 + hit >= first_drums - 0.01 and not in_break(b0 + hit): add(bas, bass(ROOT[c], d), (b0 + hit) * BEAT, .32)
for i in range(nb * 2):
    b = i / 2
    if b >= total_beats - .01: break
    swing = .03 if i % 2 else 0
    t = (b + swing) * BEAT
    if in_break(b): continue
    if b >= first_drums:
        if b % 4 in (0, 2.5) or (b % 4 == 0.5 and int(b) % 8 == 4):
            add(drums, kick(), t, .7); i0 = int(t*SR); dl = np.ones(int(.3*SR)); dl -= .45*np.exp(-np.arange(len(dl))/SR*10); duck[i0:i0+len(dl)] = np.minimum(duck[i0:i0+len(dl)], dl[:max(0, min(len(dl), N-i0))])
        if b % 4 in (1, 3): add(drums, snare(), t, .32)
    add(drums, hat(i % 8 == 7), t, .10 if i % 2 else .16)
# vinyl texture
crackle = np.zeros(N); idx = rng.integers(0, N, int(N / SR * 12)); crackle[idx] = rng.uniform(-.5, .5, len(idx))
crackle = hp(crackle, 1500) + .004 * lp(rng.standard_normal(N), 3000)
# riser into the 3D section
rs, re_ = riser[0] * BEAT, riser[1] * BEAT; rt = T(re_ - rs)
sweep = bp(rng.standard_normal(len(rt)), 300, 7000) * (rt / rt[-1]) ** 2 * .25
# intro filter: keys muffled until drums arrive
keys = np.where(np.arange(N) < int(first_drums * BEAT * SR), lp(keys, 1200), keys)
music = lp(keys, 5500) * duck + bas * duck + drums + crackle * .18
musL = music.copy(); musR = music.copy(); add(musL, sweep, rs); add(musR, sweep, rs)
# end: let the last chord ring, fade the tail
end_s = cfg['frames'] / FPS; fade = int(.8 * SR); e = int(end_s * SR)
for m in (musL, musR):
    m[e - fade:e] *= np.linspace(1, 0, fade); m[e:] = 0
L += musL; R += musR

# ---- SFX ----
def pop():
    t = T(.09); f = 380 + 900*np.exp(-t*60); return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*45)
def tick():
    t = T(.03); return (np.sin(2*np.pi*2400*t) + .5*rng.standard_normal(len(t))) * np.exp(-t*220)
def whoosh(d=.38, lo=400, hi=5000):
    t = T(d); n = rng.standard_normal(len(t)); env = np.sin(np.pi * t / d) ** 2
    out = np.zeros_like(n); seg = 1024
    for s in range(0, len(n), seg):
        cf = lo + (hi - lo) * (s / len(n)); out[s:s+seg] = bp(n[max(0, s-512):s+seg], cf*.6, min(cf*1.6, 20000))[-len(n[s:s+seg]):]
    return out * env
def clack():
    t = T(.18); x = sum(a*np.sin(2*np.pi*f*t)*np.exp(-t*k) for f, a, k in ((170, 1, 30), (430, .6, 45), (980, .35, 70)))
    return x + .5*bp(rng.standard_normal(len(t)), 1500, 6000)*np.exp(-t*160)
SFX = {'pop': (pop, .30), 'tick': (tick, .16), 'whoosh': (whoosh, .55), 'swoosh': (lambda: whoosh(.7, 250, 2500), .35), 'clack': (clack, .6)}
for c in cfg['cues']:
    fn, g = SFX[c['type']]; x = fn(); t = c['f'] / FPS
    addst(x, max(0, t), g, pan=(-.25 if c['type'] == 'whoosh' else 0))

st = np.stack([L, R], 1); st = st / (np.abs(st).max() + 1e-9) * .7
wavfile.write(OUT, SR, (st * 32767).astype(np.int16))
print('wrote', OUT, len(st) / SR, 's')
