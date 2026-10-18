"""Tiny banknote-engraving engine (numpy only). Scenes are laid out on a design grid (default 1300 x 1000)
and rendered at display size (K) with supersampling (SS). Shapes are drawn FRONT TO BACK: each claims its
pixels, so later (farther) shapes never paint over nearer ones.

Look: dot-and-lash. Parallel lines follow each surface, swell with darkness, and break into dashes and dots
in the light; concentric rings on round parts; cross-hatching in deep shadow; tapered dashed background."""
import os, subprocess
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "engr")

def frac(a): return a - np.floor(a)

class Plate:
    def __init__(s, W=1300, H=1000, K=0.5, SS=3, P=9.0):
        s.W, s.H, s.K, s.SS, s.P = W, H, K, SS, P
        h, w = int(H * K * SS), int(W * K * SS)
        s.y, s.x = np.mgrid[0:h, 0:w].astype(np.float32) / (K * SS)
        s.ink = np.zeros((h, w), np.float32)
        s.claimed = np.zeros((h, w), bool)
        s.shadows = []

    # ---------- signed distance helpers ----------
    def local(s, cx, cy, ang):
        c, n = np.cos(ang), np.sin(ang); dx, dy = s.x - cx, s.y - cy
        return dx * c + dy * n, -dx * n + dy * c
    def rrect(s, cx, cy, hw, hh, r=0, ang=0):
        u, v = s.local(cx, cy, ang)
        qx, qy = np.abs(u) - (hw - r), np.abs(v) - (hh - r)
        return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
    def circle(s, cx, cy, r): return np.hypot(s.x - cx, s.y - cy) - r
    def ellipse(s, cx, cy, a, b, ang=0):
        u, v = s.local(cx, cy, ang); k = np.hypot(u / a, v / b)
        return (k - 1) * min(a, b)
    def segs(s, pts, closed=False):
        P = list(pts) + ([pts[0]] if closed else [])
        d = np.full(s.x.shape, 1e9, np.float32)
        for (ax, ay), (bx, by) in zip(P[:-1], P[1:]):
            dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-6
            t = np.clip(((s.x - ax) * dx + (s.y - ay) * dy) / L2, 0, 1)
            d = np.minimum(d, np.hypot(s.x - (ax + t * dx), s.y - (ay + t * dy)))
        return d
    def poly(s, pts):
        d = s.segs(pts, closed=True); inside = np.zeros(s.x.shape, bool)
        n = len(pts)
        for i in range(n):
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
            cond = ((ay > s.y) != (by > s.y)) & (s.x < (bx - ax) * (s.y - ay) / ((by - ay) or 1e-6) + ax)
            inside ^= cond
        return np.where(inside, -d, d)
    def arc_pts(s, cx, cy, r, a0, a1, n=48):
        a = np.linspace(a0, a1, n); return list(zip(cx + r * np.cos(a), cy + r * np.sin(a)))

    # ---------- tone helpers ----------
    def grad(s, p0, p1, t0, t1):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L2 = dx * dx + dy * dy
        t = np.clip(((s.x - p0[0]) * dx + (s.y - p0[1]) * dy) / L2, 0, 1)
        return t0 + (t1 - t0) * t

    # ---------- line work ----------
    def _lines(s, d, phase, along, dash=8.0):
        d = np.clip(d, 0, 1)
        w = 0.07 + 0.50 * d
        on = np.abs(frac(phase) - .5) * 2 < w
        duty = np.clip(d * 2.4, 0, 1)
        dots = frac(along / dash + np.floor(phase) * .37) < np.maximum(duty, .22)
        return on & (dots | (d > .42))
    def hatch(s, tone, ang, P=None, cross=True):
        P = P or s.P; c, n = np.cos(ang), np.sin(ang)
        ph = (-s.x * n + s.y * c) / P; al = s.x * c + s.y * n
        m = s._lines(tone, ph, al)
        if cross:
            t2 = np.clip((np.asarray(tone) - .56) * 2.3, 0, 1)
            m = m | (s._lines(t2, (s.x * c + s.y * n) / P, -s.x * n + s.y * c) & (np.asarray(tone) > .56))
        return m
    def rings(s, tone, cx, cy, P=None):
        P = (P or s.P) * .62; r = np.hypot(s.x - cx, s.y - cy)
        return s._lines(tone, r / P, np.arctan2(s.y - cy, s.x - cx) * r)

    # ---------- drawing ----------
    def _put(s, region, m):
        sel = region & ~s.claimed
        s.ink[sel] = np.maximum(s.ink[sel], m[sel].astype(np.float32))
        s.claimed |= region
    def shape(s, sdf, tone, ang=0.0, outline=2.6, fill=None, shadow=(24, 30), cross=True, P=None):
        """Fill a shape with engraved lines (or a given fill mask) plus an outline; drawn front to back."""
        inside = sdf < 0
        m = fill if fill is not None else s.hatch(tone, ang, P, cross)
        edge = np.abs(sdf) < outline
        s._put(inside | edge, (m & inside) | edge)
        if shadow: s.shadows.append((sdf, shadow))
    def solid(s, sdf, halo=0.0):
        """A solid ink stroke or shape, optionally with a clear halo around it."""
        if halo: s._put(sdf < halo, sdf < 0)
        else: s._put(sdf < 0, sdf < 0)
    def stroke(s, pts, width, closed=False, halo=0.0):
        s.solid(s.segs(pts, closed) - width / 2, halo)
    def blank(s, sdf):                      # claim without ink (keeps an area clean)
        s._put(sdf < 0, np.zeros_like(s.claimed))
    def box(s, x0, y0, w, h, d, tones=(.22, .45, .72), dv=(.62, -.42), outline=2.6, front=None, top=None, side=None, shadow=(26, 32)):
        """Oblique box: front face (x0,y0)-(x0+w,y0+h), receding by depth d along dv. Optional per-face fills."""
        ox, oy = dv[0] * d, dv[1] * d
        F = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]
        T = [(x0, y0), (x0 + ox, y0 + oy), (x0 + w + ox, y0 + oy), (x0 + w, y0)]
        R = [(x0 + w, y0), (x0 + w + ox, y0 + oy), (x0 + w + ox, y0 + h + oy), (x0 + w, y0 + h)]
        fsd = s.poly(F); tsd = s.poly(T); rsd = s.poly(R)
        s.shape(fsd, s.grad((x0, y0), (x0 + w, y0 + h), tones[1] - .08, tones[1] + .1), 0.0, outline, front, None)
        s.shape(tsd, s.grad((x0, y0), (x0 + w + ox, y0 + oy), tones[0] - .05, tones[0] + .08), np.arctan2(oy, ox), outline, top, None)
        s.shape(rsd, s.grad((x0 + w, y0), (x0 + w + ox, y0 + h + oy), tones[2] - .08, tones[2] + .06), np.pi / 2, outline, side, None)
        if shadow:
            u = s.poly([F[3], F[2], (R[2][0], R[2][1]), (R[1][0], R[1][1]), T[1]])
            s.shadows.append((np.minimum(np.minimum(fsd, tsd), rsd), shadow))
        return F, T, R

    def finish(s, name, bg=(0.5, 0.5, 0.36, 0.33), bg_strength=.30):
        # engraved cast shadows, then the tapered dashed background
        for sdf, (dx, dy) in s.shadows:
            sh = np.roll(np.roll(sdf, int(dy * s.K * s.SS), 0), int(dx * s.K * s.SS), 1)
            t = np.clip(.6 - sh / 60, 0, .6)
            s._put(t > .05, s._lines(t, s.y / 7.5, s.x, 7.5))
        cx, cy, sx, sy = bg[0] * s.W, bg[1] * s.H, bg[2] * s.W, bg[3] * s.H
        g = np.exp(-(((s.x - cx) / sx) ** 2 + ((s.y - cy) / sy) ** 2))
        m = s._lines(bg_strength * g, s.y / 8.5, s.x, 12) & (frac(s.x / 12 + np.floor(s.y / 8.5) * .37) < np.clip(g * 1.1, 0, .9)) & (g > .06)
        if bg_strength: s._put(np.ones_like(s.claimed), m)
        SS = s.SS; h, w = s.ink.shape
        a = s.ink.reshape(h // SS, SS, w // SS, SS).mean(axis=(1, 3))
        a = (np.clip(a * 1.15, 0, 1) * 255).astype(np.uint8)
        rgba = np.zeros((h // SS, w // SS, 4), np.uint8); rgba[..., 3] = a
        os.makedirs(OUT, exist_ok=True)
        out = os.path.join(OUT, name + ".webp")
        subprocess.run(["magick", "-size", f"{w // SS}x{h // SS}", "-depth", "8", "rgba:-", "-trim", "+repage", "-bordercolor", "none", "-border", "3%", "-quality", "92", out],
                       input=rgba.tobytes(), check=True)
        return out
