#!/usr/bin/env python3
"""Bitcheque emblem: a pen nib drawn as a perfect square turned 45 degrees, with a breather hole flowing
into a tapered slit that runs out through the bottom point. One path, one colour: fill="currentColor".
Writes emblem.svg, emblem-black.svg, emblem-white.svg, app-icon.svg, logo.svg; prints the inline <svg>."""
import math
# a perfect square turned 45 degrees (all sides equal), corners softened; the nib cut runs into the bottom point
TOP, RIGHT, BOTTOM, LEFT = (32, 1.5), (62.5, 32), (32, 62.5), (1.5, 32)
RC = 3.2                        # corner softening (along each edge)
CX, CY, R = 32, 27.5, 6.6       # breather hole
W_TOP = W_BOT = 1.75            # slit half-width: a straight tube with parallel sides
def along(a, b, d):
    (ax, ay), (bx, by) = a, b; L = math.hypot(bx - ax, by - ay); return (ax + (bx - ax) * d / L, ay + (by - ay) * d / L)
def outline():
    yj = CY + math.sqrt(R * R - W_TOP * W_TOP)
    # where the slit sides meet the lower edges (lines x+y=94.5 on the right, y-x=30.5 on the left)
    pr = (CX + W_BOT, 94.5 - (CX + W_BOT)); pl = (CX - W_BOT, 30.5 + (CX - W_BOT))
    f = lambda p: f"{p[0]:.3f} {p[1]:.3f}"
    path = f"M{f(pr)} "
    for prev, v, nxt in ((BOTTOM, RIGHT, TOP), (RIGHT, TOP, LEFT), (TOP, LEFT, BOTTOM)):
        path += f"L{f(along(v, prev, RC))} Q{f(v)} {f(along(v, nxt, RC))} "
    path += f"L{f(pl)} L{f((CX - W_TOP, yj))} A{R} {R} 0 1 1 {f((CX + W_TOP, yj))} Z"
    return path
D = outline()
def svg(fill, attrs='role="img" aria-label="Bitcheque"'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" {attrs}><path fill="{fill}" fill-rule="evenodd" d="{D}"/></svg>'
w = lambda n, s: open(n, "w").write(s + "\n")
w("emblem.svg", svg("currentColor")); w("emblem-black.svg", svg("#02050A")); w("emblem-white.svg", svg("#FFFFFF"))
# app icon: the emblem itself is the tile (white square, black cut-out reads on any launcher)
w("app-icon.svg", f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Bitcheque"><rect width="64" height="64" rx="14" fill="#02050A"/>'
                  f'<g transform="translate(32 32) scale(.78) translate(-32 -32)"><path fill="#FFFFFF" fill-rule="evenodd" d="{D}"/></g></svg>')
w("logo.svg", f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 290 64" role="img" aria-label="Bitcheque"><path fill="currentColor" fill-rule="evenodd" d="{D}"/>'
              '<text x="76" y="45" font-family="system-ui, sans-serif" font-weight="700" font-size="38" letter-spacing="-1.2" fill="currentColor">Bitcheque</text></svg>')
print(f'<svg viewBox="0 0 64 64" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="{D}"/></svg>')
