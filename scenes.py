#!/usr/bin/env python3
"""Every site illustration as a coded banknote-engraving scene (see engrave_lib.py).
Usage: python3 scenes.py [name ...]   -> assets/engr/<name>.webp"""
import sys, math
import numpy as np
from engrave_lib import Plate

PI = math.pi

def printer(p, x0, y0, s=1.0, grid_sheet=False):
    """Simple desktop printer: body box, paper in the top slot, output tray, slot line."""
    w, h, d = 300 * s, 150 * s, 170 * s
    # paper coming out of the top (front-most part of the top area)
    sx0, sy0 = x0 + 55 * s + .62 * d * .55, y0 - .42 * d * .55
    sheet = p.poly([(sx0, sy0 + 6), (sx0 + 190 * s, sy0 + 6), (sx0 + 175 * s, sy0 - 130 * s), (sx0 - 10 * s, sy0 - 130 * s)])
    if grid_sheet:
        gl = np.zeros_like(p.claimed)
        for k in range(1, 6):
            gl |= p.segs([(sx0 + k * 32 * s - k * 2.6 * s, sy0), (sx0 - 10 * s + k * 31 * s, sy0 - 128 * s)]) < 1.6
        for k in range(1, 5):
            yy = sy0 - k * 26 * s
            gl |= p.segs([(sx0 - k * 2 * s, yy), (sx0 + 190 * s - k * 3 * s, yy)]) < 1.6
        p.shape(sheet, .08, 0, fill=gl, shadow=None)
    else:
        p.shape(sheet, p.grad((sx0, sy0), (sx0, sy0 - 130 * s), .25, .06), .0, shadow=None)
    # output tray in front
    tray = p.poly([(x0 + 45 * s, y0 + h - 40 * s), (x0 + w - 45 * s, y0 + h - 40 * s), (x0 + w - 20 * s, y0 + h + 28 * s), (x0 + 20 * s, y0 + h + 28 * s)])
    p.shape(tray, .2, 0.0, shadow=None)
    p.stroke([(x0 + 40 * s, y0 + 52 * s), (x0 + w - 40 * s, y0 + 52 * s)], 3)        # slot
    p.solid(p.circle(x0 + w - 40 * s, y0 + 26 * s, 8 * s))                          # button
    p.box(x0, y0, w, h, d, tones=(.2, .42, .74))

def cube(p, x, y, a, tones=(.2, .42, .72)):
    return p.box(x, y, a, a, a * .9, tones=tones)

def coin(p, cx, cy, r):
    p.shape(p.circle(cx, cy, r * .78), None, fill=p.rings(.3, cx - r * .15, cy - r * .2), outline=2.2, shadow=None)
    p.shape(p.circle(cx, cy, r), p.grad((cx - r, cy - r), (cx + r, cy + r), .25, .7), PI / 4, outline=2.8, shadow=(18, 22))

def scene_print2():
    p = Plate()
    printer(p, 690, 470, .95); printer(p, 230, 470, .95)
    return p

def scene_printer():
    p = Plate()
    printer(p, 420, 470, 1.15, grid_sheet=True)
    cable = [(420 + 345 * 1.15 * .0 + 300 * 1.15 + 110, 470 + 60), (1060, 520), (1110, 640), (1060, 760), (960, 800)]
    p.stroke([(ax, ay) for ax, ay in cable], 7)
    p.solid(p.rrect(955, 800, 26, 15, 4))
    return p

def scene_register():
    p = Plate()
    # envelope, tilted, coming down onto the stack
    ex, ey, ang = 650, 260, -.18
    flap = []
    u = lambda a, b: (ex + a * math.cos(ang) - b * math.sin(ang), ey + a * math.sin(ang) + b * math.cos(ang))
    p.stroke([u(-170, -105), u(0, 15), u(170, -105)], 3.2)
    p.stroke([u(-170, 105), u(-40, 5)], 2.4); p.stroke([u(170, 105), u(40, 5)], 2.4)
    p.shape(p.rrect(ex, ey, 170, 105, 6, ang), p.grad(u(-170, -105), u(170, 105), .12, .38), ang + .05)
    for k in range(3):                                   # motion lines above
        p.stroke([u(-120 + k * 120, -150), u(-120 + k * 120, -230)], 3)
    cube(p, 560, 640, 150); cube(p, 410, 640, 150); cube(p, 500, 490, 150)
    return p

def scene_receive():
    p = Plate()
    coin(p, 900, 690, 95); coin(p, 1010, 600, 95)
    cx, cy, ang = 600, 470, -.08
    boxes = np.zeros_like(p.claimed)
    for i in range(12):
        bx = -390 + i * 70 + 33
        boxes |= np.abs(p.rrect(cx + bx * math.cos(ang), cy + bx * math.sin(ang) - 10, 26, 30, 4, ang)) < 2.2
    card = p.rrect(cx, cy, 450, 200, 26, ang)
    tone = p.grad((cx - 450, cy - 200), (cx + 450, cy + 200), .14, .34)
    p.shape(card, tone, ang + .5, fill=boxes | p.hatch(tone * (boxes == 0), ang + .5))
    return p

def scene_sign():
    p = Plate()
    # pen: long body with a nib touching cell (row 2, col 3)
    tipx, tipy = 590, 560
    ang = -PI / 4.2
    c, n = math.cos(ang), math.sin(ang)
    nib = [(tipx, tipy), (tipx + 70 * c + 26 * n, tipy + 70 * n - 26 * c), (tipx + 110 * c, tipy + 110 * n), (tipx + 70 * c - 26 * n, tipy + 70 * n + 26 * c)]
    p.stroke([(tipx + 8 * c, tipy + 8 * n), (tipx + 70 * c, tipy + 70 * n)], 2.6, halo=1)
    p.shape(p.poly(nib), p.grad(nib[1], nib[3], .2, .7), ang + PI / 2, shadow=(20, 26))
    bx, by = tipx + 110 * c + 40 * c, tipy + 110 * n + 40 * n
    p.shape(p.rrect(tipx + 300 * c, tipy + 300 * n, 200, 34, 30, ang), p.grad((bx, by - 40), (bx, by + 40), .25, .8), ang, shadow=(24, 30))
    p.shape(p.rrect(tipx + 128 * c, tipy + 128 * n, 26, 30, 4, ang), .6, ang + PI / 2, shadow=None)
    # grid sheet
    gx, gy, cs = 250, 330, 85
    gl = np.zeros_like(p.claimed); dark = np.zeros_like(p.claimed)
    for i in range(7): gl |= np.abs(p.x - (gx + i * cs)) < 1.8
    for j in range(5): gl |= np.abs(p.y - (gy + j * cs)) < 1.8
    gl &= (p.x > gx - 2) & (p.x < gx + 6 * cs + 2) & (p.y > gy - 2) & (p.y < gy + 4 * cs + 2)
    for (i, j) in ((0, 1), (1, 3), (2, 2), (3, 0), (4, 2)):
        dark |= (p.x > gx + i * cs + 10) & (p.x < gx + (i + 1) * cs - 10) & (p.y > gy + j * cs + 10) & (p.y < gy + (j + 1) * cs - 10)
    sheet = p.rrect(gx + 3 * cs, gy + 2 * cs, 3 * cs + 50, 2 * cs + 50, 8)
    p.shape(sheet, .1, 0, fill=gl | (p.hatch(.62, PI / 4) & dark))
    return p

def scene_nodevice():
    p = Plate()
    c = (650, 500)
    p.stroke([(360, 210), (940, 790)], 34, halo=16)                  # the strike-through
    p.shape(p.rrect(*c, 150, 150, 14), p.grad((500, 350), (800, 650), .55, .8), PI / 4)
    p.shape(p.rrect(*c, 205, 205, 18), p.grad((445, 295), (855, 705), .18, .42), 0.0)
    for k in range(8):                                                 # pins
        o = -175 + k * 50
        for (px, py, hw, hh) in ((c[0] + o, c[1] - 240, 9, 34), (c[0] + o, c[1] + 240, 9, 34), (c[0] - 240, c[1] + o, 34, 9), (c[0] + 240, c[1] + o, 34, 9)):
            p.shape(p.rrect(px, py, hw, hh, 3), .35, 0.0 if hw > hh else PI / 2, shadow=None)
    return p

def shield_pts(cx, cy, w, h):
    """Heater shield: flat-ish top with a slight dip, straight upper sides, curving to a point at the bottom."""
    top = [(cx - w, cy - h * .82), (cx - w * .5, cy - h * .9), (cx, cy - h * .84), (cx + w * .5, cy - h * .9), (cx + w, cy - h * .82)]
    right = []
    for t in np.linspace(0, 1, 24):
        yy = cy - h * .82 + t * h * 1.82
        xx = cx + w * (1 - t ** 2.2) ** .85 if t < 1 else cx
        right.append((xx, yy))
    left = [(2 * cx - x, y) for (x, y) in reversed(right)]
    return top + right[1:] + left[1:-1]

def scene_quantum():
    p = Plate()
    cx, cy = 650, 520
    rings = np.zeros_like(p.claimed)
    for a in (0, PI / 3, -PI / 3):
        rings |= np.abs(p.ellipse(cx, cy - 10, 210, 72, a)) < 5
    p.solid(np.where(rings, -1.0, 1.0))
    p.shape(p.circle(cx, cy - 10, 44), None, fill=p.rings(.45, cx - 14, cy - 24), shadow=None)
    pts = shield_pts(cx, cy, 300, 380)
    p.shape(p.poly(pts), p.grad((cx - 300, cy - 380), (cx + 300, cy + 380), .2, .62), PI / 2.4)
    return p

def scene_ledger(p=None, k=1.0):
    p = p or Plate()
    cx, cy = 650, 520
    L = [(cx - 470, cy - 250), (cx - 10, cy - 210), (cx - 10, cy + 260), (cx - 470, cy + 220)]
    R = [(cx + 10, cy - 210), (cx + 470, cy - 250), (cx + 470, cy + 220), (cx + 10, cy + 260)]
    rows = np.zeros_like(p.claimed); ticks = []
    for k in range(9):
        t = (k + 1) / 10
        yl, yr = cy - 230 + 470 * t, cy - 210 + 470 * t
        rows |= p.segs([(cx - 440, yl - 30 * (1 - t) * 0 - 24 + 40 * t * 0), (cx - 40, yr)]) < 1.6
        rows |= p.segs([(cx + 40, yr), (cx + 440, yl)]) < 1.6
        if k < 6: ticks.append((cx + 360, yr - 6 - (yr - yl) * .8))
    for (tx, ty) in ticks:
        p.stroke([(tx - 18, ty - 4), (tx - 4, ty + 10), (tx + 24, ty - 22)], 5)
    p.shape(p.poly(R), p.grad((cx, 0), (cx + 470, 0), .32, .1), PI / 2, fill=rows | p.hatch(p.grad((cx, 0), (cx + 470, 0), .32, .06), PI / 2), shadow=None)
    p.shape(p.poly(L), p.grad((cx - 470, 0), (cx, 0), .12, .4), PI / 2, fill=rows | p.hatch(p.grad((cx - 470, 0), (cx, 0), .06, .4), PI / 2), shadow=None)
    cover = p.poly([(cx - 500, cy - 230), (cx, cy - 190), (cx + 500, cy - 230), (cx + 500, cy + 250), (cx, cy + 290), (cx - 500, cy + 250)])
    p.shape(cover, .62, 0.0)
    return p

def scene_chain():
    p = Plate(W=1500, H=700)
    # magnifier over the middle block
    mx, my, r = 820, 300, 150
    p.shape(p.rrect(mx + 185, my + 185, 26, 105, 22, -PI / 4), p.grad((mx + 120, my + 120), (mx + 260, my + 260), .4, .85), -PI / 4)
    p.solid(np.abs(p.circle(mx, my, r)) - 12)
    p.blank(p.circle(mx, my, r - 12) + 0)
    for i in range(5):
        x = 120 + i * 255
        if i < 4:
            p.solid(np.abs(p.ellipse(x + 205, 375, 40, 22)) - 5)
        cube(p, x, 300, 150)
    return p

def doc_border(p, sdf_inner_offset, cx, cy, hw, hh, ang=0):
    return (np.abs(p.rrect(cx, cy, hw - 22, hh - 22, 6, ang)) < 1.8) | (np.abs(p.rrect(cx, cy, hw - 34, hh - 34, 4, ang)) < 1.2)

def scene_halves():
    p = Plate()
    zig = [(650 + (12 if k % 2 else -12), 250 + k * 50) for k in range(11)]
    leftpts = [(240, 250)] + zig + [(240, 750)]
    rightpts = [(x + 70, y + 20) for (x, y) in zig] + [(1130, 770), (1130, 270)]
    for pts, off in ((rightpts, 70), (leftpts, 0)):
        sd = p.poly(pts)
        tone = p.grad((240, 250), (1130, 770), .12, .34)
        border = (np.abs(p.rrect(685 + off / 2 * 0 + (off and 35), 510, 420, 225, 6)) < 1.8)
        p.shape(sd, tone, .35 + (off and .05), fill=(p.hatch(tone, .35) | border) & (sd < 0))
    return p

def scene_offline():
    p = Plate()
    # wifi above, struck through
    wx, wy = 650, 300
    p.stroke([(500, 120), (800, 420)], 20, halo=12)
    for k, r in enumerate((150, 105, 60)):
        p.stroke(p.arc_pts(wx, wy + 60, r, -PI * .78, -PI * .22), 18)
    p.solid(p.circle(wx, wy + 60, 16))
    # laptop: screen (dark) and base
    scr = p.rrect(650, 600, 250, 155, 14)
    inner = p.rrect(650, 600, 222, 128, 6)
    p.shape(inner, p.grad((428, 472), (872, 728), .78, .55), PI / 5)
    p.shape(scr, .3, 0.0)
    base = p.poly([(380, 760), (920, 760), (1000, 830), (300, 830)])
    keys = np.zeros_like(p.claimed)
    for j in range(3):
        keys |= p.segs([(370 + j * 10 - 40 * j * 0, 780 + j * 15), (930 - j * 10, 780 + j * 15)]) < 1.4
    p.shape(base, p.grad((300, 760), (1000, 830), .2, .55), 0.0, fill=keys | p.hatch(p.grad((300, 760), (1000, 830), .2, .55), 0.0))
    return p

def scene_seal():
    p = Plate()
    cx, cy, R = 720, 560, 230
    p.stroke([(cx - 95, cy + 5), (cx - 25, cy + 75), (cx + 105, cy - 70)], 34)
    p.blank(p.circle(cx, cy, 150))
    p.solid(np.abs(p.circle(cx, cy, 165)) - 3)
    a = np.arctan2(p.y - cy, p.x - cx); rr = np.hypot(p.x - cx, p.y - cy)
    wavy = rr - (R + 14 * np.sin(a * 11))
    p.shape(wavy, p.grad((cx - R, cy - R), (cx + R, cy + R), .3, .78), PI / 3.5, shadow=(22, 28))
    doc = p.rrect(520, 430, 400, 260, 6, -.12)
    p.shape(doc, p.grad((120, 170), (920, 690), .08, .26), .45, fill=p.hatch(p.grad((120, 170), (920, 690), .08, .26), .45) | (np.abs(p.rrect(520, 430, 370, 230, 4, -.12)) < 1.6))
    return p

def scene_vault():
    p = Plate()
    cx, cy = 600, 520
    # door swung open to the right
    p.shape(p.ellipse(cx + 330, cy, 70, 230), None, fill=p.hatch(.5, PI / 2), shadow=(22, 28))
    p.shape(p.ellipse(cx + 300, cy, 60, 230), p.grad((cx + 240, 0), (cx + 360, 0), .2, .7), PI / 2)
    # booklets inside the opening
    for k in range(4):
        p.box(cx - 120, cy + 70 - k * 38, 220, 30, 70, tones=(.15, .3, .6), shadow=None)
    p.shape(p.circle(cx, cy, 200), .82, PI / 4, cross=True)
    p.solid(np.abs(p.circle(cx, cy, 214)) - 7)
    p.shape(p.rrect(cx, cy, 300, 300, 18), p.grad((cx - 300, cy - 300), (cx + 300, cy + 300), .25, .55), 0.0)
    return p

def scene_scissors():
    p = Plate()
    cx, cy = 640, 480
    for side in (1, -1):                                   # blades crossing at the pivot
        tip = (cx + 400, cy + side * 70)
        blade = p.poly([(cx - 30, cy - side * 22), (cx + 120, cy - side * 30), tip, (cx + 120, cy + side * 18), (cx - 10, cy + side * 30)])
        p.shape(blade, p.grad((cx, cy - side * 30), (cx, cy + side * 30), .5 if side > 0 else .7, .75 if side > 0 else .9), .08 * side)
    p.solid(p.circle(cx, cy, 13), halo=5)
    for side in (1, -1):                                   # handles
        hx, hy = cx - 210, cy - side * 120
        p.solid(np.abs(p.ellipse(hx, hy, 95, 62, side * .4)) - 14)
        p.stroke([(cx - 10, cy - side * 8), (hx + 80, hy + side * 20)], 22)
    # booklet being cut, with the cut line
    p.stroke([(cx + 60, cy), (cx + 420, cy)], 2, halo=0)
    book = p.rrect(cx + 280, cy + 20, 260, 170, 10, .04)
    p.shape(book, p.grad((cx + 20, cy - 150), (cx + 540, cy + 190), .2, .5), .5, shadow=(24, 30))
    return p

def scene_seed():
    p = Plate()
    pips = {1: [(0, 0)], 2: [(-.5, -.5), (.5, .5)], 3: [(-.5, -.5), (0, 0), (.5, .5)], 5: [(-.5, -.5), (.5, -.5), (0, 0), (-.5, .5), (.5, .5)], 6: [(-.5, -.5), (-.5, 0), (-.5, .5), (.5, -.5), (.5, 0), (.5, .5)]}
    for (x, y, n) in ((560, 560, 5), (330, 600, 3), (440, 330, 6)):
        a = 160
        for (u, v) in pips[n]:
            p.solid(p.circle(x + a / 2 + u * a * .55, y + a / 2 + v * a * .55, 14))
        p.box(x, y, a, a, a * .85, tones=(.12, .28, .6))
    card = p.rrect(900, 560, 230, 300, 12, .1)
    lines_ = np.zeros_like(p.claimed)
    for k in range(9):
        lines_ |= np.abs(p.rrect(900 - k * 0, 330 + k * 52, 170, 0.5, 0, .1) ) < 1.4
    p.shape(card, .1, .1 + PI / 2, fill=lines_ | p.hatch(.1, .1 + PI / 2))
    return p

def scene_book():
    p = Plate()
    p.box(380, 560, 520, 70, 360, tones=(.12, .32, .62))
    p.box(400, 480, 500, 70, 340, tones=(.15, .36, .66))
    return p


# ---------- "Three things you don't have to trust": each vignette inside a round banknote medallion ----------
def medallion(p, cx=650, cy=500, r=470):
    """Double-ring medallion with a fine engraved field; drawn last so the subject sits in front."""
    p.solid(np.abs(p.circle(cx, cy, r)) - 4)
    p.solid(np.abs(p.circle(cx, cy, r - 18)) - 1.4)
    beads = np.zeros_like(p.claimed)
    for a in np.linspace(0, 2 * PI, 96, endpoint=False):
        beads |= p.circle(cx + (r - 9) * math.cos(a), cy + (r - 9) * math.sin(a), 3.2) < 0
    p.solid(np.where(beads, -1.0, 1.0))
    p.blank(np.abs(p.circle(cx, cy, r - 9)) - 8)
    field = p.circle(cx, cy, r - 19)
    p.shape(field, p.grad((cx - r, cy - r), (cx + r, cy + r), .10, .30), 0.0, outline=0.1, shadow=None, cross=False)

def scaled(fn, k):
    """Run a scene function on a plate whose design grid is enlarged by 1/k, so the subject shrinks by k."""
    p = Plate()
    W0, H0 = p.W, p.H
    p.x = (p.x - 650) / k + 650; p.y = (p.y - 500) / k + 500
    return p

def medallion_only(p, cx=650, cy=500, r=470):
    """Medallion, then nothing outside it: cast shadows stay inside the ring."""
    medallion(p, cx, cy, r)
    p.blank(-p.circle(cx, cy, r + 6))

def scene_m_nodevice():
    """No device: a pen copying a cell off a paper cheque; the wireless sign is struck out."""
    p = Plate()
    ux, uy = .707, -.707                                   # pen axis, nib to cap
    T = (604, 562)
    at = lambda d: (T[0] + ux * d, T[1] + uy * d)
    ang = -PI / 4
    nb = at(95)
    p.shape(p.poly([T, (nb[0] + .707 * 30, nb[1] + .707 * 30), (nb[0] - .707 * 30, nb[1] - .707 * 30)]), .55, ang + PI / 2, shadow=(20, 26))
    p.solid(p.segs([at(18), at(70)]) - 2.2)                # nib slit
    p.shape(p.rrect(*at(125), 32, 34, 8, ang), .75, ang + PI / 2, shadow=(20, 26))
    p.shape(p.rrect(*at(300), 145, 38, 34, ang), p.grad(at(160), (at(160)[0] + 60, at(160)[1] + 60), .2, .62), ang, shadow=(24, 30))
    p.stroke([at(380), (at(380)[0] + 30, at(380)[1] + 30), (at(250)[0] + 30, at(250)[1] + 30)], 9)   # clip
    # the cheque: a grid of cells, one picked out
    cx, cy, hw, hh, a = 650, 610, 300, 175, -.06
    grid = np.zeros_like(p.claimed)
    u, v = p.local(cx, cy, a)
    for k in range(1, 6):
        grid |= (np.abs(u - (-hw + k * 2 * hw / 6)) < 1.6) & (np.abs(v) < hh - 26)
    for k in range(1, 4):
        grid |= (np.abs(v - (-hh + k * 2 * hh / 4)) < 1.6) & (np.abs(u) < hw - 26)
    pick = (np.abs(u - (-hw + 2.5 * 2 * hw / 6)) < hw / 6 - 10) & (np.abs(v - (-hh + 1.5 * 2 * hh / 4)) < hh / 4 - 10)
    fill = grid | (pick & p.hatch(.7, PI / 4)) | (~pick & p.hatch(.08, a))
    p.shape(p.rrect(cx, cy, hw, hh, 10, a), .1, a, fill=fill | doc_border(p, 0, cx, cy, hw, hh, a), shadow=(24, 30))
    # wireless sign, struck out
    wx, wy = 420, 345
    p.stroke([(wx - 95, wy - 115), (wx + 95, wy + 45)], 20, halo=12)
    p.solid(p.circle(wx, wy, 17))
    for r in (55, 95, 135):
        p.stroke(p.arc_pts(wx, wy, r, -PI * .78, -PI * .22, 32), 17)
    medallion_only(p); return p

def scene_m_quantum():
    """Hashes only: a heavy padlock with a hash sign cut into it."""
    p = Plate()
    cx, cy = 650, 610
    k = 78                                                  # the # sign
    hs = np.full(p.x.shape, 1e9, np.float32)
    for d in (-1, 1):
        hs = np.minimum(hs, p.segs([(cx + d * 34 + 16, cy - k - 6), (cx + d * 34 - 16, cy + k + 6)]) - 13)
        hs = np.minimum(hs, p.segs([(cx - k, cy + d * 34), (cx + k, cy + d * 34)]) - 13)
    p.solid(hs); p.blank(hs - 10)
    body = p.rrect(cx, cy, 245, 185, 34)
    p.shape(body, p.grad((cx - 245, cy - 185), (cx + 245, cy + 185), .22, .62), PI / 2.6, shadow=(26, 32))
    p.solid(np.abs(p.rrect(cx, cy, 215, 155, 22)) - 2)      # inset line around the face
    sh = [(cx - 150, cy - 185), (cx - 150, cy - 300)] + p.arc_pts(cx, cy - 300, 150, PI, 2 * PI, 40) + [(cx + 150, cy - 300), (cx + 150, cy - 185)]
    shd = p.segs(sh) - 34
    p.shape(shd, p.grad((cx - 190, 0), (cx + 190, 0), .25, .7), 0.0, P=7, shadow=(22, 28))
    medallion_only(p); return p

def scene_m_ledger():
    """The chain remembers: a register of cheque numbers, the spent ones ticked and struck through."""
    p = Plate()
    cx, cy, hw, hh, a = 650, 500, 235, 315, -.05
    u, v = p.local(cx, cy, a)
    rows = 7; top = -hh + 60; step = (2 * hh - 100) / rows
    lines = np.zeros_like(p.claimed)
    c, n = math.cos(a), math.sin(a)
    to = lambda uu, vv: (cx + uu * c - vv * n, cy + uu * n + vv * c)
    for i in range(rows):
        y = top + step * (i + .5)
        bx = -hw + 70
        lines |= (np.abs(p.rrect(*to(bx, y), 22, 22, 3, a)) < 2.2)
        lines |= (np.abs(v - (y + 22)) < 1.4) & (u > -hw + 110) & (u < hw - 40)
        if i < 4:
            p.stroke([to(bx - 14, y), to(bx - 3, y + 12), to(bx + 20, y - 16)], 9, halo=4)
            p.stroke([to(-hw + 115, y), to(hw - 45, y)], 6, halo=3)
        else:
            lines |= (np.abs(v - y) < 1.2) & (u > -hw + 115) & (u < -hw + 115 + (hw * 1.2 - i * 25))
    p.shape(p.rrect(cx, cy, hw, hh, 8, a), .1, a, fill=lines | p.hatch(.07, a) | doc_border(p, 0, cx, cy, hw, hh, a), shadow=(24, 30))
    medallion_only(p); return p

def medallion_on(p, k):
    # medallion in true plate coordinates although the grid was scaled for the subject
    x, y = p.x, p.y
    p.x = (x - 650) * k + 650; p.y = (y - 500) * k + 500
    medallion(p)
    p.x, p.y = x, y

# ---------- explorer quick links ----------
def scene_mempool():
    """Hourglass: the transactions waiting for the next block."""
    p = Plate()
    cx, top, bot, hw = 650, 200, 800, 210
    for y in (top - 40, bot):                                                     # end plates
        p.shape(p.rrect(cx, y + 20, hw + 70, 20, 6), .5, 0.0, shadow=(20, 24))
    for x in (cx - hw - 40, cx + hw + 40):                                        # posts
        p.shape(p.rrect(x, 500, 13, 280, 6), p.grad((x - 13, 0), (x + 13, 0), .3, .75), PI / 2, shadow=(18, 22))
    neck = 500
    p.stroke([(cx, neck), (cx, 760)], 5)                                          # falling grain
    sand_low = p.poly([(cx - 190, 780), (cx + 190, 780), (cx + 60, 690), (cx, 670), (cx - 60, 690)])
    p.shape(sand_low, p.grad((cx, 670), (cx, 780), .45, .8), .35, shadow=None)
    sand_up = p.poly([(cx - 120, 410), (cx + 120, 410), (cx + 14, neck - 12), (cx - 14, neck - 12)])
    p.shape(sand_up, p.grad((cx, 410), (cx, neck), .45, .8), -.35, shadow=None)
    glass = [(cx - hw, top), (cx + hw, top), (cx + 22, neck), (cx + hw, bot), (cx - hw, bot), (cx - 22, neck)]
    p.shape(p.poly(glass), p.grad((cx - hw, top), (cx + hw, bot), .05, .16), PI / 3, outline=3.2, cross=False)
    return p

def coin_stack(p, cx, base, r, n, tilt=.34):
    """A stack of n coins, top coin first (front to back)."""
    th = r * .2; ry = r * tilt
    ytop = base - n * th
    p.shape(p.ellipse(cx, ytop, r, ry), None, fill=p.rings(.22, cx, ytop) & (p.ellipse(cx, ytop, r * .8, ry * .8) < 0), outline=2.4, shadow=None)
    for k in range(n):
        y = ytop + k * th
        band = np.maximum(np.minimum(p.ellipse(cx, y + th, r, ry), p.rrect(cx, y + th / 2, r, th / 2)), -p.ellipse(cx, y, r, ry) if k == 0 else -1e9)
        p.shape(band, p.grad((cx - r, y), (cx + r, y), .3, .75), PI / 2, outline=2.2, shadow=None)
    p.shadows.append((np.minimum(p.ellipse(cx, base, r, ry), p.rrect(cx, base - n * th / 2, r, n * th / 2)), (22, 18)))

def scene_topaccounts():
    """Three coin stacks of different heights: who holds the most."""
    p = Plate(W=1400, H=1000)
    coin_stack(p, 1030, 820, 150, 5)
    coin_stack(p, 690, 790, 150, 14)
    coin_stack(p, 360, 760, 150, 9)
    return p

def scene_nodes():
    """Three servers joined by links: the nodes that keep the chain."""
    p = Plate(W=1400, H=1000)
    spots = [(250, 470), (560, 300), (880, 480)]
    def server(x, y):
        slots = np.zeros_like(p.claimed)
        for k in range(3):
            slots |= np.abs(p.rrect(x + 95, y + 50 + k * 70, 70, 9, 4)) < 2
            slots |= p.circle(x + 200, y + 50 + k * 70, 9) < 0
        p.box(x, y, 250, 230, 170, tones=(.16, .3, .66), front=slots | p.hatch(p.grad((x, y), (x + 250, y + 230), .2, .36) * 1, 0.0) & ~(p.rrect(x + 125, y + 120, 115, 100, 6) < 0))
    for x, y in [(250, 600), (880, 610), (560, 430)]:
        server(x, y)
    for (ax, ay), (bx, by) in [((375, 600), (640, 520)), ((1000, 610), (790, 520)), ((500, 720), (880, 730))]:
        p.stroke([(ax, ay), (bx, by)], 7)
    return p

# ---------- footer: banknote security print ----------
def _wave_ink(p, d, w):
    """Ink where a curve's (slope-corrected) distance d is under half the line width."""
    p.solid(np.abs(d) - w / 2)

def scene_rosette():
    """Guilloche rosette: interlaced wavy rings like the seal printed on a cheque."""
    p = Plate(W=1000, H=1000)
    cx, cy = 500, 500
    a = np.arctan2(p.y - cy, p.x - cx); rr = np.hypot(p.x - cx, p.y - cy)
    p.solid(np.abs(rr - 470) - 5); p.solid(np.abs(rr - 448) - 1.6)
    beads = np.zeros_like(p.claimed)
    for t in np.linspace(0, 2 * PI, 120, endpoint=False):
        beads |= p.circle(cx + 459 * math.cos(t), cy + 459 * math.sin(t), 3.4) < 0
    p.solid(np.where(beads, -1.0, 1.0))
    ink = np.zeros_like(p.claimed)
    for k in range(9):                                     # outer band: phase-shifted petals
        r = 330 + 80 * np.sin(12 * a + k * 2 * PI / 9) * np.cos(3 * a)
        ink |= np.abs(rr - r) < 1.5
    for k in range(8):                                    # inner band
        r = 170 + 55 * np.sin(9 * a + k * 2 * PI / 8)
        ink |= np.abs(rr - r) < 1.3
    for k in range(6):                                     # core
        r = 70 + 22 * np.sin(6 * a + k * 2 * PI / 6)
        ink |= np.abs(rr - r) < 1.1
    ink &= rr < 436
    p.solid(np.where(ink, -1.0, 1.0))
    return p

def scene_guilloche():
    """A long strip of interlaced sine waves: the security border along the bottom of a cheque."""
    p = Plate(W=3000, H=240)
    x, y = p.x, p.y
    ink = np.zeros_like(p.claimed)
    f = 3000 / (2 * PI * 10)                               # 10 full waves across the strip
    for k in range(7):                                     # a rope of phase-shifted waves
        ph = k * 2 * PI / 7
        for amp in (96,):
            c = 120 + amp * np.sin(x / f + ph)
            ink |= np.abs(y - c) < 2.2 * np.sqrt(1 + (amp / f * np.cos(x / f + ph)) ** 2)
    ink |= (np.abs(y - 6) < 3.2) | (np.abs(y - 234) < 3.2)
    p.solid(np.where(ink, -1.0, 1.0))
    return p

# small icons for list rows (drawn bold so they still read at 40px)
def cheque_card(p, cx, cy, ang, hw=430, hh=220, tone=(.1, .3)):
    u = lambda a, b: (cx + a * math.cos(ang) - b * math.sin(ang), cy + a * math.sin(ang) + b * math.cos(ang))
    marks = np.zeros_like(p.claimed)
    for i in range(6):                                    # the row of boxes
        bx = -300 + i * 92
        marks |= np.abs(p.rrect(*u(bx, -40), 30, 36, 6, ang)) < 7
    marks |= p.segs([u(-330, 110), u(330, 110)]) < 6      # amount line
    card = p.rrect(cx, cy, hw, hh, 34, ang)
    t = p.grad(u(-hw, -hh), u(hw, hh), *tone)
    p.shape(card, t, ang + .6, fill=marks | p.hatch(t * (marks == 0), ang + .6, P=14), outline=9, shadow=None)
    p.stroke([u(hw - 34, -hh + 34), u(hw - 34, hh - 34)][:0] or [u(-hw + 40, -hh + 40), u(hw - 40, -hh + 40), u(hw - 40, hh - 40), u(-hw + 40, hh - 40)], 4, closed=True)

def scene_i_cheque():
    p = Plate()
    cheque_card(p, 650, 500, -.1)
    return p

def scene_i_book():
    p = Plate()
    for k, (dx, dy) in enumerate([(70, -90), (35, -45), (0, 0)]):
        cheque_card(p, 610 + dx, 560 + dy, -.1, tone=(.08 + .05 * (2 - k), .26 + .05 * (2 - k)))
    return p

def scene_i_pick():
    """Pickaxe: a slim crescent head with a collar around the handle, a long wooden handle with a wrapped grip."""
    p = Plate()
    ox, oy, ang = 690, 330, -.75                          # head centre; the whole tool is drawn upright, then tilted
    R = lambda x, y: (ox + x * math.cos(ang) - y * math.sin(ang), oy + x * math.sin(ang) + y * math.cos(ang))
    # collar first (earlier shapes sit on top), then the head, then the handle
    p.shape(p.poly([R(-46, -58), R(46, -58), R(40, 62), R(-40, 62)]), .62, ang, outline=9, shadow=None)
    top, bot = [], []
    for i in range(61):
        t = -1 + i / 30
        yc = 95 * t * t - 20                              # arch: centre high, tips curling down
        w = 40 * (1 - abs(t) ** 2.2) + 3                  # thick at the collar, sharp at the points
        top.append(R(t * 440, yc - w)); bot.append(R(t * 440, yc + w))
    p.shape(p.poly(top + bot[::-1]), p.grad(R(-440, 0), R(440, 0), .5, .18), ang + 1.2, outline=9, shadow=None)
    for k in range(3):                                    # leather wrap on the grip
        y = 520 + k * 46
        p.stroke([R(-34, y), R(34, y + 18)], 7)
    p.shape(p.poly([R(-26, 40), R(26, 40), R(34, 660), R(-34, 660)]), p.grad(R(0, 40), R(0, 660), .18, .4), ang + PI / 2 + .35, outline=9, shadow=None)
    return p

def scene_qrcode():
    """A QR code on a card: three finder squares and a module pattern (illustrative, not a real code)."""
    p = Plate()
    import random
    rnd = random.Random(7)
    n, ms, cx, cy = 21, 22, 650, 480
    x0, y0 = cx - n * ms / 2, cy - n * ms / 2
    dark = np.zeros_like(p.claimed)
    fin = lambda i, j: (i < 8 and j < 8) or (i >= n - 8 and j < 8) or (i < 8 and j >= n - 8)
    for j in range(n):
        for i in range(n):
            if fin(i, j):
                fi, fj = (i if i < 8 else i - (n - 7)), (j if j < 8 else j - (n - 7))
                on = 0 <= fi < 7 and 0 <= fj < 7 and (fi in (0, 6) or fj in (0, 6) or (2 <= fi <= 4 and 2 <= fj <= 4))
            else:
                on = rnd.random() < .48
            if on:
                dark |= (p.x >= x0 + i * ms + 1) & (p.x < x0 + (i + 1) * ms - 1) & (p.y >= y0 + j * ms + 1) & (p.y < y0 + (j + 1) * ms - 1)
    card = p.rrect(cx, cy, n * ms / 2 + 60, n * ms / 2 + 60, 28)
    p.shape(card, .08, .6, fill=dark | p.hatch(.1 * (dark == 0), .6), outline=6)
    return p

SCENES = {k[6:]: v for k, v in globals().items() if k.startswith("scene_")}

if __name__ == "__main__":
    names = sys.argv[1:] or list(SCENES)
    for n in names:
        p = SCENES[n]()
        print(p.finish(n, bg_strength=0 if n.startswith(('m_', 'i_')) or n in ('rosette', 'guilloche') else .30), flush=True)
