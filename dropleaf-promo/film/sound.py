# Custom score + foley for the Drop Leaf film.  python3 sound.py out/film_audio.wav [duration]
# Everything is synthesized here: no samples, no licensing.
import sys, numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

OUT = sys.argv[1]; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 40.5
SR = 48000; N = int((DUR + 1) * SR)
rng = np.random.default_rng(42)
T = lambda d: np.arange(int(d * SR)) / SR
def filt(x, kind, f, o=2): return sosfilt(butter(o, f, kind, fs=SR, output='sos'), x)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
noise = lambda d: rng.standard_normal(int(d * SR))

class Bus:
    def __init__(s): s.L = np.zeros(N); s.R = np.zeros(N)
    def add(s, x, t, g=1.0, pan=0.0):
        if x.ndim == 2: l, r = x[:, 0], x[:, 1]
        else: l = r = x
        i = int(t * SR); j = min(N, i + len(l))
        if i >= N or j <= max(i, 0): return
        a = max(0, -i); i = max(i, 0)
        s.L[i:j] += l[a:a + j - i] * g * min(1, 1 - pan); s.R[i:j] += r[a:a + j - i] * g * min(1, 1 + pan)
    def st(s): return np.stack([s.L, s.R], 1)

def ir(decay=2.2, pre=.012, bright=6000):
    t = T(decay * 1.6); env = np.exp(-t * 6.9 / decay)
    l = filt(rng.standard_normal(len(t)), 'low', bright) * env; r = filt(rng.standard_normal(len(t)), 'low', bright) * env
    pad = np.zeros(int(pre * SR)); l = np.concatenate([pad, l]); r = np.concatenate([pad, r])
    return l / np.sqrt((l ** 2).sum()), r / np.sqrt((r ** 2).sum())
def reverb(st, wet, decay=2.2, bright=6000):
    l, r = ir(decay, bright=bright)
    wl = fftconvolve(st[:, 0], l)[:len(st)]; wr = fftconvolve(st[:, 1], r)[:len(st)]
    return st * (1 - wet * .3) + np.stack([wl, wr], 1) * wet

# ---------------- score ----------------
music = Bus()
BEAT = .75                                         # 80 BPM
def saw_pad(m, d, att=1.6, rel=2.0, det=.12):
    t = T(d + rel); f = hz(m); env = np.minimum(1, t / att) * np.where(t > d, np.exp(-(t - d) * 3 / rel), 1)
    out = []
    for dt in (-det, det):
        ff = f * 2 ** (dt / 12); x = sum(np.sin(2 * np.pi * ff * k * t + k) / k for k in range(1, 10))
        out.append(x)
    x = np.stack(out, 1) * env[:, None]
    return x
CH = [  # D major colour: Dmaj9, Bm11, Gmaj7#11, Asus4 -> A
    (0.0, [50, 57, 61, 64, 66]), (4.0, [47, 54, 57, 61, 64]), (8.0, [43, 50, 54, 57, 61]), (12.0, [45, 52, 57, 59, 64]),
    (16.0, [50, 57, 61, 64, 69]), (20.0, [47, 54, 59, 62, 66]), (24.0, [43, 50, 55, 59, 66]), (28.0, [45, 52, 57, 61, 64]),
    (31.0, [47, 54, 57, 62, 66]), (35.2, [38, 50, 57, 61, 64, 69])]
for i, (t0, notes) in enumerate(CH):
    d = (CH[i + 1][0] - t0) if i + 1 < len(CH) else DUR - t0 - .4
    for k, m in enumerate(notes):
        x = saw_pad(m, d + .6, att=1.2 if i else 2.5)
        x = np.stack([filt(x[:, 0], 'low', 1400 + 300 * k), filt(x[:, 1], 'low', 1400 + 300 * k)], 1)
        music.add(x, t0, .045 if i < 9 else .06)
    music.add(np.sin(2 * np.pi * hz(notes[0] - 12) * T(d + 1)) * np.minimum(1, T(d + 1) / .8) * np.exp(-T(d + 1) * .25), t0, .10)

def felt(m, d=2.2):                                # soft felt piano
    t = T(d); f = hz(m); env = (1 - np.exp(-t * 400)) * np.exp(-t * 2.6)
    x = (np.sin(2*np.pi*f*t) + .45*np.sin(2*np.pi*2*f*t)*np.exp(-t*4) + .18*np.sin(2*np.pi*3*f*t)*np.exp(-t*7) + .06*np.sin(2*np.pi*4.02*f*t)*np.exp(-t*9))
    return filt(x * env, 'low', 2600)
ARP = {0: [74, 78, 81, 76], 4: [71, 74, 78, 73], 8: [67, 71, 74, 78], 12: [69, 73, 76, 71], 16: [74, 78, 81, 85], 20: [71, 74, 78, 81], 24: [67, 71, 74, 78], 28: [69, 73, 76, 81]}
for t0, ns in ARP.items():
    if t0 < 4: continue
    for k in range(int(4 / BEAT)):
        tt = t0 + k * BEAT + (BEAT / 2 if k % 2 else 0) * 0
        if tt >= 31.0: break
        if t0 < 8 and k % 2: continue
        music.add(felt(ns[k % 4]), tt, .055 + (.02 if t0 >= 16 else 0), pan=(-.3 if k % 2 else .3))
# end motif: three notes over the title
for k, m in enumerate([81, 78, 74, 69]): music.add(felt(m, 3.2), 35.4 + k * .55, .07, pan=(-.2 + .13 * k))

def kick():
    t = T(.5); f = 42 + 70 * np.exp(-t * 30); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
def shaker():
    t = T(.09); return filt(rng.standard_normal(len(t)), 'high', 6500) * np.exp(-t * 60) * (1 - np.exp(-t * 900))
pulse_on = lambda t: 16.0 <= t < 30.6
k = 0
while k * BEAT < DUR:
    t = k * BEAT
    if pulse_on(t):
        if k % 2 == 0: music.add(kick(), t, .42)
        music.add(shaker(), t + BEAT / 2, .05, pan=.25); music.add(shaker(), t, .025, pan=-.25)
    k += 1
def swell(d, lo=300, hi=9000):
    t = T(d); x = noise(d); env = (t / d) ** 2.4
    out = np.zeros_like(x); blk = 2048
    for s in range(0, len(x), blk):
        c = lo * (hi / lo) ** (s / len(x)); out[s:s + blk] = filt(x[max(0, s - 2048):s + blk], 'band', [c * .7, min(c * 1.4, 23000)])[-len(x[s:s + blk]):]
    return out * env
for t_hit, d in ((8.0, 2.2), (20.0, 2.0), (35.2, 2.6)): music.add(swell(d), t_hit - d, .10)

# ---------------- foley / design ----------------
fx = Bus()
def whoosh(d=.9, lo=250, hi=4000, pan_from=-.6, pan_to=.6):
    t = T(d); x = noise(d); env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.6
    out = np.zeros_like(x); blk = 1024
    for s in range(0, len(x), blk):
        p = s / len(x); c = lo + (hi - lo) * np.sin(np.pi * p)
        out[s:s + blk] = filt(x[max(0, s - 1024):s + blk], 'band', [c * .6, min(c * 1.7, 23000)])[-len(x[s:s + blk]):]
    pan = np.linspace(pan_from, pan_to, len(x))
    return np.stack([out * env * np.clip(1 - pan, 0, 1), out * env * np.clip(1 + pan, 0, 1)], 1)
def knock(f0=150, bright=1.0, d=.35):        # wood on wood
    t = T(d); x = sum(a * np.sin(2*np.pi*f*t) * np.exp(-t*k) for f, a, k in ((f0, 1, 26), (f0*2.7, .55, 40), (f0*5.4, .3*bright, 70), (f0*8.9, .15*bright, 110)))
    return x + .35 * bright * filt(noise(d), 'band', [1200, 7000]) * np.exp(-t * 180)
def click(f=3200, d=.08):                     # steel hinge click
    t = T(d); return (np.sin(2*np.pi*f*t) + .6*np.sin(2*np.pi*f*1.53*t) + .4*filt(noise(d), 'high', 4000)) * np.exp(-t * 90)
def creak(d=1.6):                             # slow hinge/wood friction, very soft
    t = T(d); f = 180 + 60 * np.sin(2*np.pi*.7*t); ph = 2*np.pi*np.cumsum(f)/SR
    grit = filt(noise(d), 'band', [600, 2400]) * (.5 + .5*np.sin(2*np.pi*23*t) ** 2)
    env = np.sin(np.pi * t / d) ** .8
    return (np.sin(ph) * .25 * np.abs(np.sin(2*np.pi*11*t)) + grit * .6) * env
def tick():
    t = T(.12); return (np.sin(2*np.pi*2350*t) + .5*np.sin(2*np.pi*4700*t)) * np.exp(-t * 55) * (1 - np.exp(-t * 2000))
def thud(f=55, d=1.6):
    t = T(d); ff = f + 40 * np.exp(-t * 18); return np.sin(2*np.pi*np.cumsum(ff)/SR) * np.exp(-t * 2.4)
def shimmer(d=2.5):
    t = T(d); x = sum(np.sin(2*np.pi*hz(m)*t + m) for m in (86, 90, 93, 97)) / 4
    return x * np.minimum(1, t / .15) * np.exp(-t * 1.6) * (1 + .3*np.sin(2*np.pi*6*t))
room = filt(noise(DUR + 1), 'low', 400) * .004

# cuts / transitions
for t in (3.75, 7.7, 15.7, 19.7, 26.7, 30.7): fx.add(whoosh(1.0, 220, 3200, -.7, .7), t, .16)
# opening: slow air, macro glide
fx.add(whoosh(4.0, 120, 900, -.4, .4), 0.2, .08)
# deploy: lift (9.0-10.6), level stop, leaves 11.2-12.4, lock
fx.add(creak(1.6), 9.0, .10); fx.add(whoosh(1.5, 180, 1500, .3, -.2), 9.1, .10)
fx.add(knock(140, .6, .4), 10.58, .32); fx.add(click(2900), 10.6, .10)
fx.add(whoosh(.8, 300, 2500, -.6, -.2), 11.25, .09); fx.add(whoosh(.8, 320, 2600, .6, .2), 11.4, .09)
fx.add(knock(170, 1.0), 12.25, .42, pan=-.25); fx.add(click(3300), 12.26, .16, pan=-.25)
fx.add(knock(160, 1.0), 12.40, .48, pan=.25); fx.add(click(3500), 12.41, .2, pan=.25)
fx.add(thud(48, 1.8), 12.40, .55)
# laptop slides in and sets down
fx.add(whoosh(1.4, 400, 2200, .5, 0), 13.7, .07); fx.add(knock(95, .35, .3), 14.98, .3); fx.add(click(1800, .05), 15.0, .05)
# exploded view: apart, labels, together
fx.add(whoosh(1.3, 200, 5000, -.3, .3), 20.5, .14); fx.add(shimmer(2.4), 21.0, .045)
for t, p in ((21.6, -.3), (22.4, .3), (23.2, .35), (24.0, -.35)): fx.add(tick(), t, .07, pan=p)
fx.add(whoosh(1.1, 3000, 400, .3, -.3), 26.0, .12); fx.add(knock(165, .9), 27.05, .34); fx.add(click(3300), 27.06, .14)
# fold back flat
fx.add(whoosh(.9, 300, 2200, -.4, .4), 31.75, .08); fx.add(knock(180, .5, .3), 32.75, .18)
fx.add(creak(1.4), 33.0, .07); fx.add(whoosh(1.4, 1600, 250, .2, -.2), 33.0, .09); fx.add(knock(120, .7, .45), 34.38, .34)
# end title
fx.add(thud(42, 2.6), 35.2, .6); fx.add(shimmer(3.5), 35.25, .05)

m = music.st(); f = fx.st()
m = reverb(m, .45, 3.2, 5000)
f = reverb(f, .22, 1.4, 7000)
mix = m * .9 + f + np.stack([room, room], 1)
# fade out with the picture
e = int(DUR * SR); fo = int(1.4 * SR)
mix[e - fo:e] *= np.linspace(1, 0, fo)[:, None] ** 1.5; mix[e:] = 0
mix = mix[:e]
mix /= np.abs(mix).max() + 1e-9
wavfile.write(OUT, SR, (mix * .89 * 32767).astype(np.int16)); print('wrote', OUT, len(mix) / SR)
