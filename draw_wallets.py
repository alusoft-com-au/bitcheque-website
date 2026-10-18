#!/usr/bin/env python3
"""Draw three simple generic cold wallets in banknote "dot-and-lash" engraving: parallel lines that follow
each surface, swelling in shadow and breaking into dashes and dots in the light; cross-hatch on the dark
screens, concentric rings on the buttons, fading horizontal dashes behind. Pure numpy, no model.
Output: assets/engr/what.webp (black ink on transparency)."""
import os, subprocess
import numpy as np

S = 1                                   # design units: the drawing is laid out on a 1300 x 1000 grid
K, SS = 0.5, 3                          # rendered at half that size (its display size), 3x supersampled
W, H = int(1300 * K * SS), int(1000 * K * SS)
y, x = (np.mgrid[0:H, 0:W].astype(np.float32) / (K * SS))
ink = np.zeros((H, W), np.float32)
claimed = np.zeros((H, W), bool)        # pixels already owned by a nearer object

def frac(a): return a - np.floor(a)
def local(cx, cy, ang):
    c, s = np.cos(ang), np.sin(ang)
    dx, dy = x - cx, y - cy
    return dx * c + dy * s, -dx * s + dy * c
def rrect(u, v, hw, hh, r):              # signed distance to a rounded rectangle
    qx, qy = np.abs(u) - (hw - r), np.abs(v) - (hh - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r

def lines(d, phase, along, period, dash=8.0):
    """dot-and-lash: d = darkness 0..1, phase across lines (in periods), along = coordinate along the line"""
    w = 0.07 + 0.50 * d                                 # line width as a fraction of the period
    centre = np.abs(frac(phase) - .5) * 2               # 0 on the line centre
    on = centre < w
    duty = np.clip(d * 2.4, 0, 1)                       # in the light, lines break into dashes then dots
    dots = frac(along / dash + np.floor(phase) * .37) < np.maximum(duty, .22)
    return on & (dots | (d > .42))

def put(mask, m):
    global ink, claimed
    sel = mask & ~claimed
    ink[sel] = np.maximum(ink[sel], m[sel])
    claimed |= mask

def wallet(cx, cy, ang, hw, hh, kind, cracked=False, usb=False):
    u, v = local(cx, cy, ang)
    body = rrect(u, v, hw, hh, 34 * S)
    inside = body < 0
    P = 9.0
    # body tone: lit from top-left, darker toward bottom-right, bevel band near the edge
    t = .28 + .30 * ((u / hw) * .5 + (v / hh) * .5 + 1) / 2
    bevel = (body > -14 * S) & inside
    t = np.where(bevel, np.clip(t + .28 * np.sign(u + v), 0, 1), t)
    m = lines(t, (u * .45 + v * .89) / P, u * .89 - v * .45, P)
    parts = np.zeros_like(inside)
    if kind == "screen":                                 # USB stick / phone style: screen + two buttons
        su, sv = u, v + hh * .30
        scr = rrect(su, sv, hw * .66, hh * .32, 10 * S)
        sc = scr < 0
        st = .95 - .5 * np.exp(-((su * .7 + sv * .7 - hw * .1) / (hw * .16)) ** 2)  # dark glass, one glossy streak
        a = lines(st, (u * .45 + v * .89) / (P * .8), u, P * .8)
        b = lines(np.clip((st - .55) * 2.2, 0, 1), (u * .89 - v * .45) / (P * .8), v, P * .8) & (st > .55)
        m = np.where(sc, a | b, m); parts |= sc
        for bx in (-hw * .32, hw * .32):
            r = np.hypot(u - bx, v - hh * .45)
            bt = np.clip(.25 + .6 * (r / (hw * .17)) ** 2, 0, 1)
            ring = lines(bt, r / (P * .55), np.arctan2(v - hh * .45, u - bx) * r, P * .55)
            bm = r < hw * .17
            m = np.where(bm, ring, m); parts |= bm
    elif kind == "dial":                                 # square device with one round dial
        r = np.hypot(u, v + hh * .05)
        dm = r < hw * .52
        dt = np.clip(.2 + .7 * np.abs(np.sin(np.arctan2(v, u) * 1.0 + .8)) * (r / (hw * .52)), 0, 1)
        m = np.where(dm, lines(dt, r / (P * .6), np.arctan2(v, u) * r, P * .6), m); parts |= dm
    elif kind == "card":                                 # card wallet with a small contact pad
        pad = rrect(u + hw * .45, v + hh * .05, hw * .17, hh * .22, 6 * S) < 0
        pt = .65
        m = np.where(pad, lines(pt, (u * .89 - v * .45) / (P * .6), v, P * .6), m); parts |= pad
    elif kind == "swivel":                               # slim stick under a metal swivel guard, round window, one button
        win = np.hypot(u, v + hh * .3) < hw * .5
        wt = np.clip(.9 - .45 * np.exp(-((u + v * .4) / (hw * .22)) ** 2), 0, 1)
        m = np.where(win, lines(wt, (u * .7 + v * .7) / (P * .7), u, P * .7) | lines(np.clip((wt - .6) * 2, 0, 1), (u * .7 - v * .7) / (P * .7), v, P * .7), m); parts |= win
        r = np.hypot(u, v + hh * .02); bm = r < hw * .22
        m = np.where(bm, lines(np.clip(.25 + .6 * (r / (hw * .22)) ** 2, 0, 1), r / (P * .55), np.arctan2(v + hh * .02, u) * r, P * .55), m); parts |= bm
    elif kind == "touch":                                # tall slab, edge-to-edge glass with a reflection
        scr = rrect(u, v, hw - 22 * S, hh - 22 * S, 14 * S) < 0
        st = np.clip(.82 - .55 * np.exp(-((u * .55 + v * .45 + hw * .1) / (hw * .22)) ** 2), 0, 1)
        m = np.where(scr, lines(st, (u * .45 + v * .89) / (P * .8), u, P * .8) | (lines(np.clip((st - .62) * 2.3, 0, 1), (u * .89 - v * .45) / (P * .8), v, P * .8) & (st > .62)), m); parts |= scr
    elif kind == "plate":                                # steel seed plate with punched dot rows
        dots = np.zeros_like(inside)
        for j in range(6):
            for i in range(8):
                dots |= np.hypot(u - (-hw * .7 + i * hw * .2), v - (-hh * .6 + j * hh * .24)) < 5 * S
        m = np.where(dots, True, lines(t * .7, (u * .98 + v * .2) / (P * .55), u, P * .55)); parts |= dots
    # outlines: thin, slightly heavier on the shadow side
    edge = np.abs(body) < 3.0
    sub = np.zeros_like(edge)
    if kind == "screen":
        sub = np.abs(rrect(u, v + hh * .30, hw * .66, hh * .32, 10 * S)) < 2.2
    if kind == "touch":
        sub = np.abs(rrect(u, v, hw - 22 * S, hh - 22 * S, 14 * S)) < 2.2
    m = m | edge | sub
    if cracked:                                          # a few straight crack lines across the face
        for (a0, b0, a1, b1) in ((-.2, -.9, .25, .1), (.25, .1, -.1, .9), (.25, .1, .9, .35)):
            pu0, pv0, pu1, pv1 = a0 * hw, b0 * hh, a1 * hw, b1 * hh
            du, dv = pu1 - pu0, pv1 - pv0; L = np.hypot(du, dv)
            tt = np.clip(((u - pu0) * du + (v - pv0) * dv) / L ** 2, 0, 1)
            dist = np.hypot(u - (pu0 + tt * du), v - (pv0 + tt * dv))
            m = (m & (dist > 6.5)) | (dist < 2.2)
    if usb:                                              # metal USB plug sticking out of the top
        pb = rrect(u, v + hh + 34 * S, hw * .42, 36 * S, 5 * S)
        pin = (np.abs(u) < hw * .26) & (v < -hh - 18 * S) & (v > -hh - 50 * S) & ((np.abs(u + hw * .12) < 6 * S) | (np.abs(u - hw * .12) < 6 * S))
        m = np.where(pb < 0, lines(np.clip(.3 + .3 * (u / hw), 0, 1), v / (P * .45), u, P * .45) | pin, m) | (np.abs(pb) < 1.6 * S)
        inside = inside | (pb < 0)
    put(inside | edge, m.astype(np.float32))
    return body

def shadow(cx, cy, ang, hw, hh):
    u, v = local(cx + 26 * S, cy + 34 * S, ang)
    d = rrect(u, v, hw, hh, 40 * S)
    t = np.clip(.62 - d / (60 * S), 0, .62)
    m = lines(t, y / 7.5, x, 7.5) & (t > .04)
    return m, t > .04

# front to back so nearer objects claim their pixels first
objs = [
  (dict(cx=650 * S, cy=520 * S, ang=.04, hw=118 * S, hh=225 * S, kind="screen", usb=True)),
  (dict(cx=330 * S, cy=545 * S, ang=-.14, hw=74 * S, hh=235 * S, kind="swivel")),
  (dict(cx=975 * S, cy=545 * S, ang=.14, hw=125 * S, hh=210 * S, kind="touch")),
]
shadows = [shadow(o["cx"], o["cy"], o["ang"], o["hw"], o["hh"]) for o in objs]
# the strike: one bold bar across all three devices (the 'no device' mark used elsewhere on the site)
bu, bv = local(640 * S, 560 * S, -.46)
bar = rrect(bu, bv, 520 * S, 15 * S, 15 * S)
put(bar < 14 * S, (bar < 0).astype(np.float32))
for o in objs: wallet(**o)
# shadows and background: horizontal dot-and-lash, fading out
bg = np.exp(-(((x - 650 * S) / (560 * S)) ** 2 + ((y - 520 * S) / (340 * S)) ** 2))
bgd = .30 * bg
for m, region in shadows:
    put(region, m.astype(np.float32))
bgm = lines(bgd, y / 8.5, x, 12) & (frac(x / 12 + np.floor(y / 8.5) * .37) < np.clip(bg * 1.1, 0, .9)) & (bg > .06)
put(np.ones_like(claimed), bgm.astype(np.float32))

# downsample (anti-alias) and write black ink on transparency
a = ink.reshape(H // SS, SS, W // SS, SS).mean(axis=(1, 3))
a = (np.clip(a * 1.15, 0, 1) * 255).astype(np.uint8)
rgba = np.zeros((H // SS, W // SS, 4), np.uint8); rgba[..., 3] = a
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "engr", "what.webp")
subprocess.run(["magick", "-size", f"{W // SS}x{H // SS}", "-depth", "8", "rgba:-", "-trim", "+repage", "-bordercolor", "none", "-border", "3%", "-quality", "92", out],
               input=rgba.tobytes(), check=True)
print("wrote", out)
