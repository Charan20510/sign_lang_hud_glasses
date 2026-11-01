"""Draw the 6 engineering sheets (SVG) for the README, in the hand-drawn style of the v1 sheets.

Every number comes from hardware/enclosure/hud_enclosure.scad (v3.1), its echo output, the STL files,
hardware/enclosure/README.md or firmware/glasses_display/glasses_display.ino. Run from anywhere:
    python3 docs/images/drawings/make_drawings.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent
W, H = 1600, 1130                      # A3 landscape ratio, like the v1 sheets
FONT = "Virgil, 'Comic Sans MS', 'Chalkboard SE', 'Comic Neue', cursive"
INK, BLUE, RED, GREEN, GREY = "#1e1e1e", "#1f4fa0", "#c0392b", "#2f8a3a", "#666"

# ---- design values (mm) -------------------------------------------------------------------------
L, TUBE_H, WIDTH, DROP, WALL, SIDE_T = 95, 30, 29, 43, 2.4, 4      # scad: L, H, W, drop, wall, side_t
HEAD_L = 27.8 + 0.3 + 2                                            # scad: oled_h + clr + 2
OX = (4.0 + 23.3) / 2                                              # optical axis x (OLED glass centre)
LENS_Z, LENS_D, LENS_T, PLATE_T = -6, 25, 5, 3
LENS_CZ = LENS_Z - 1.5 + LENS_T / 2                                # lens centre = -5
U, D_LENS_ACR, F_EST = 22, 25, 25                                  # u (bench), lens -> acrylic, f estimate
AZ = LENS_CZ - D_LENS_ACR                                          # acrylic centre / eye level = -30
ACR_L = 30
TEMPLE, DV, DH, RIM = 7, 10, 37, 13                                # glasses, measured
CLIP_T, JAW_DROP, JAW_OUT, STRAIN, RIM_GAP = 2.5, 35, 12.5, 2.2, 14.6
V_IMG = 1 / (1 / F_EST - 1 / U)                                    # -183.3
M_IMG = -V_IMG / U                                                 # 8.3


# ---- tiny SVG helpers -----------------------------------------------------------------------------
def head(title, sub, n):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'font-family="{FONT}">',
            '<defs><filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="4"/>'
            '<feDisplacementMap in="SourceGraphic" scale="2.2"/></filter>'
            f'<marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,1 L10,5 L0,9" fill="none" stroke="{INK}" stroke-width="1.6"/></marker>'
            f'<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,1 L10,5 L0,9" fill="none" stroke="{RED}" stroke-width="1.6"/></marker>'
            '<pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<line x1="0" y1="0" x2="0" y2="10" stroke="#8a7a2a" stroke-width="1.5"/></pattern></defs>',
            f'<rect width="{W}" height="{H}" fill="#faf8f2"/>',
            txt(W / 2, 48, title, 40, anchor="middle"),
            txt(W / 2, 86, f"Sheet {n} of 6  |  {sub}", 20, GREY, "middle"),
            txt(W - 30, H - 24, "Drawn by: Charan  |  ECE, IIIT Senapati, Manipur  |  Enclosure v3.1", 18, GREY, "end")]


def txt(x, y, s, size=18, color=INK, anchor="start", weight="normal"):
    s = s.replace("<", "&lt;")
    s = " " * (len(s) - len(s.lstrip(" "))) + s.lstrip(" ")     # keep the indent of note lines
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{s}</text>')


def lines(x, y, rows, size=19, color=INK, gap=30, anchor="start"):
    return [txt(x, y + i * gap, r, size, color, anchor) for i, r in enumerate(rows)]


def rect(x, y, w, h, fill="none", stroke=INK, sw=2.2, rx=0, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def line(x1, y1, x2, y2, stroke=INK, sw=2.2, dash="", marker=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linecap="round"{d}{m}/>')


def poly(pts, fill="none", stroke=INK, sw=2.4, close=True):
    tag = "polygon" if close else "polyline"
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<{tag} points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def dim(x1, y1, x2, y2, label, side=-1, size=17, color=INK):
    """Dimension line with arrows at both ends; label beside the middle."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    s = [f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1.4" '
         f'marker-start="url(#a)" marker-end="url(#a)"/>']
    if abs(y1 - y2) < 1:                                          # horizontal
        s.append(f'<rect x="{mx - len(label) * 5 - 6:.1f}" y="{my - 12:.1f}" width="{len(label) * 10 + 12}" height="22" fill="#faf8f2"/>')
        s.append(txt(mx, my + 6, label, size, color, "middle"))
    else:                                                         # vertical: label to the side
        s.append(txt(mx + side * 10, my + 6, label, size, color, "end" if side < 0 else "start"))
    return "\n".join(s)


def leader(x1, y1, x2, y2, rows, color=BLUE, size=18, anchor="start"):
    """Callout: thin line from the part (x2, y2) to the text block at (x1, y1)."""
    w = max(len(r) for r in rows) * size * 0.52 + 12          # rough text width: start the line beside it
    sx = x1 + w if anchor == "start" and x2 > x1 + w else x1 - w if anchor == "end" and x2 < x1 - w else x1
    s = [line(sx, y1 - 6, x2, y2, color, 1.3)]
    tx = x1 + (6 if anchor == "start" else -6)
    s += lines(tx, y1, rows, size, color, 23, anchor)
    return "\n".join(s)


def panel(x, y, w, h, title, rows, size=19, gap=29):
    s = [rect(x, y, w, h, "#fffdf8", INK, 2.2, 10), txt(x + w / 2, y + 40, title, 26, INK, "middle")]
    s += lines(x + 28, y + 85, rows, size, INK, gap)
    return "\n".join(s)


def save(name, parts):
    (OUT / name).write_text("\n".join(parts + ["</svg>"]) + "\n")
    print("wrote", OUT / name)


# ---- sheet 1: side view to scale ------------------------------------------------------------------
def side_view():
    k, X0, Y0 = 7.0, 330, 520                      # px per mm; x=0 (front) and z=0 (tube floor)
    X = lambda x: X0 + x * k
    Y = lambda z: Y0 - z * k
    s = head("Sign-Language HUD Glasses  -  Display Unit (Side View, to scale)",
             "All dimensions in mm (internal)  |  no mirror: OLED -> lens -> 45 deg acrylic -> eye", 1)
    g = ['<g filter="url(#rough)">']
    # inside outline of the side wall: tube + optics head
    g.append(poly([(X(0), Y(TUBE_H)), (X(L), Y(TUBE_H)), (X(L), Y(0)), (X(HEAD_L), Y(0)),
                   (X(HEAD_L), Y(-DROP)), (X(0), Y(-DROP))], sw=3.2))
    # OLED rails (3 slots) + OLED (glass under the PCB, slot u = 22)
    for u in (19, 22, 25):
        z = LENS_CZ + u
        g.append(line(X(-1), Y(z), X(1.5), Y(z), GREY, 1.6))
        g.append(line(X(HEAD_L - 1.5), Y(z), X(HEAD_L + 1), Y(z), GREY, 1.6))
    zg = LENS_CZ + U
    g.append(rect(X(4), Y(zg + 1.5), (23.3 - 4) * k, 1.5 * k, "#9fb8e6"))
    g.append(rect(X(0), Y(zg + 2.7), 27.8 * k, 1.2 * k, "#d6e2f3"))
    # lens plate + lens
    g.append(rect(X(0), Y(LENS_Z), HEAD_L * k, PLATE_T * k, "#e8e2d4"))
    g.append(f'<ellipse cx="{X(OX):.1f}" cy="{Y(LENS_CZ):.1f}" rx="{LENS_D / 2 * k:.1f}" ry="{LENS_T / 2 * k:.1f}" '
             f'fill="#dbe9f7" stroke="{INK}" stroke-width="2.2"/>')
    # 45 deg acrylic "\" (folds the light towards the eye at the rear)
    h = ACR_L / 2 * 0.7071
    g.append(line(X(OX - h), Y(AZ + h), X(OX + h), Y(AZ - h), "#7b68ee", 6))
    # electronics: LiPo cradle, TP4056 tray, ESP32 tray, switch
    g.append(rect(X(L - 30), Y(6), 30 * k, 6 * k, "url(#hatch)"))
    g.append(rect(X(L - 28), Y(9.1 + 5.5), 28 * k, 5.5 * k, "#f3d9bf"))
    g.append(rect(X(L - 22.5), Y(19.2 + 3.2), 22.5 * k, 3.2 * k, "#d5e8d4"))
    g.append(rect(X(60 - 4.3), Y(TUBE_H), 8.6 * k, 3.6 * k, "#dddddd"))
    g.append(rect(X(L) - 4, Y(22.6 + 1.8), 8, 3.6 * k, "#888888"))          # ESP32 USB-C at rear
    g.append(f'<circle cx="{X(L):.1f}" cy="{Y(4):.1f}" r="{1.75 * k:.1f}" fill="#faf8f2" stroke="{INK}" stroke-width="2"/>')
    g.append('</g>')
    s += g
    # light path (red) and world view (green)
    for x in (OX - 5, OX + 5):
        zh = AZ - (x - OX)
        s.append(line(X(x), Y(zg), X(x), Y(zh), RED, 2.2, "7 5"))
        s.append(line(X(x), Y(zh), X(HEAD_L + 22), Y(AZ + (OX - x) * 0.25), RED, 2.2, "7 5", "ar"))
    s.append(line(40, Y(AZ), X(HEAD_L + 20), Y(AZ), GREEN, 2.2, "4 6"))
    ex, ey = X(HEAD_L + 27), Y(AZ)
    s.append(f'<ellipse cx="{ex}" cy="{ey}" rx="26" ry="17" fill="white" stroke="{INK}" stroke-width="2.4"/>'
             f'<circle cx="{ex - 9}" cy="{ey}" r="9" fill="{INK}"/>')
    s.append(txt(ex + 34, ey + 7, "EYE", 22))
    s += lines(40, Y(AZ) - 36, ["real world (signer)", "seen through acrylic"], 17, GREEN, 66)
    # dimensions
    s.append(dim(X(0), Y(TUBE_H) - 70, X(L), Y(TUBE_H) - 70, "95"))
    s.append(dim(X(0), Y(TUBE_H) - 35, X(HEAD_L), Y(TUBE_H) - 35, "30.1 head"))
    s.append(dim(X(HEAD_L), Y(TUBE_H) - 35, X(L), Y(TUBE_H) - 35, "64.9 electronics tube"))
    s.append(dim(X(L) + 30, Y(TUBE_H), X(L) + 30, Y(0), "30", 1))
    s.append(dim(X(L) + 30, Y(0), X(L) + 30, Y(AZ), "30", 1))
    s.append(txt(X(L) + 30, Y(AZ) + 28, "(to eye level)", 17, INK, "middle"))
    s.append(dim(X(0) - 60, Y(0), X(0) - 60, Y(-DROP), "43", -1))
    s.append(dim(X(HEAD_L) + 30, Y(zg), X(HEAD_L) + 30, Y(LENS_CZ), "u = 22", 1, color=RED))
    s.append(dim(X(HEAD_L) + 30, Y(LENS_CZ), X(HEAD_L) + 30, Y(AZ), "25", 1, color=RED))
    # callouts
    s.append(leader(40, Y(zg) - 10, X(1), Y(zg + 2), ["0.96\" OLED SSD1306,", "screen down, slots", "u = 19 / 22 / 25"]))
    s.append(leader(40, Y(LENS_CZ) - 10, X(OX - 11), Y(LENS_CZ), ["Lens dia 25", "(marked f45) on", "plate 6 below floor"]))
    s.append(leader(X(OX) + 40, Y(-DROP) + 50, X(OX + 6), Y(AZ - 7), ["Clear acrylic 30 x 30 x 1, 45 deg", "(beam combiner)"]))
    s.append(leader(X(L), Y(TUBE_H) - 130, X(L - 10), Y(21.5), ["ESP32-C3 SuperMini", "USB-C at rear"], anchor="end"))
    s.append(leader(X(52), Y(TUBE_H) - 110, X(58), Y(TUBE_H), ["Slide switch (top wall)"], anchor="end"))
    s.append(leader(X(45), Y(-8), X(L - 14), Y(12), ["TP4056 Type-C (protection)", "LiPo 600 mAh, 30 x 20 x 6", "charge leads exit dia 3.5"]))
    s.append(txt(X(L / 2), Y(-DROP) + 120, "SIDE VIEW (left = front, rear faces the ear; width into page = 29 internal)", 19, INK, "middle"))
    # panels
    s.append(panel(1090, 125, 480, 470, "Why these distances?", [
        "OLED -> lens centre  u = 22  (bench, sharp)",
        "lens focal length  f ~ 25  (estimate)",
        "u < f  ->  virtual, upright image",
        "",
        "1/v = 1/f - 1/u = 1/25 - 1/22 = -3/550",
        f"v ~ {V_IMG:.0f}  (virtual)",
        f"magnification m = |v/u| ~ {M_IMG:.1f}x",
        "",
        "=> text floats ~18 cm in front of the lens",
        "lens -> acrylic = 25 only sets eye level"], size=18))
    s.append(panel(1090, 615, 480, 440, "Build notes", [
        "1. Focus: move the OLED to slot 19 or 25",
        "   if the text is blurry.",
        "2. Print in matte black PLA: no painting.",
        "3. Acrylic must be 29 - 30.4 wide to fit.",
        "4. Text backwards / upside down:",
        "   MIRROR_X / FLIP_Y in firmware.",
        "5. Clip on the right arm, ~2 cm behind",
        "   the hinge; slide the unit from the rear.",
        "6. Print test_fit.stl first if unsure."], size=18, gap=33))
    save("side_view.svg", s)


# ---- sheet 2: optics ray diagram ------------------------------------------------------------------
def optics():
    s = head("Sign-Language HUD Glasses  -  Optics (thin-lens ray diagram)",
             "Light path unfolded: the 45 deg acrylic only turns it 90 deg towards the eye  |  mm", 2)
    k, LX, AY = 4.2, 1000, 600                     # px per mm, lens x, optical axis y
    X = lambda x: LX + x * k                       # x < 0: OLED side
    ho, hi = 10, 10 * M_IMG                        # object height (illustrative), image height
    xo, xi = -U, V_IMG
    g = ['<g filter="url(#rough)">', line(X(-200), AY, X(80), AY, GREY, 1.4, "10 6")]
    g.append(f'<ellipse cx="{X(0)}" cy="{AY}" rx="14" ry="{LENS_D / 2 * k * 2.2:.1f}" fill="#dbe9f7" stroke="{INK}" stroke-width="2.4"/>')
    g.append(line(X(xo), AY, X(xo), AY - ho * k, "#3e6bc4", 5))                       # OLED (object)
    g.append(line(X(xi), AY, X(xi), AY - hi * k, "#9fb8e6", 4, "8 6"))                 # virtual image
    for f in (-F_EST, F_EST):
        g.append(f'<circle cx="{X(f):.1f}" cy="{AY}" r="5" fill="{INK}"/>')
    g.append('</g>')
    s += g
    # ray 1: parallel to the axis -> through F on the eye side; ray 2: through the lens centre
    tip = (X(xo), AY - ho * k)
    s.append(line(*tip, X(0), AY - ho * k, RED, 2.4))
    slope = (ho * k) / (F_EST * k)
    s.append(line(X(0), AY - ho * k, X(70), AY - ho * k + slope * 70 * k, RED, 2.4, "", "ar"))
    s.append(line(X(0), AY - ho * k, X(xi), AY - hi * k, RED, 1.6, "6 6"))
    s.append(line(*tip, X(70), AY + ho * k * 70 / U, RED, 2.4, "", "ar"))       # straight through the centre
    s.append(line(*tip, X(xi), AY - hi * k, RED, 1.6, "6 6"))
    ex, ey = X(75), AY - 10
    s.append(f'<ellipse cx="{ex + 30}" cy="{ey}" rx="26" ry="17" fill="white" stroke="{INK}" stroke-width="2.4"/>'
             f'<circle cx="{ex + 21}" cy="{ey}" r="9" fill="{INK}"/>')
    s.append(txt(ex + 64, ey + 7, "EYE", 22))
    s.append(txt(X(xo) - 12, AY - ho * k / 2, "OLED", 19, "#3e6bc4", "end"))
    s.append(txt(X(xi) + 12, AY - hi * k + 10, f"virtual image ({M_IMG:.1f}x, upright)", 19, BLUE))
    s.append(txt(X(-F_EST), AY + 30, "F", 19, INK, "middle"))
    s.append(txt(X(F_EST), AY + 30, "F", 19, INK, "middle"))
    s.append(txt(X(0), AY + LENS_D / 2 * k * 2.2 + 30, "lens", 19, INK, "middle"))
    s.append(dim(X(xo), AY + 70, X(0), AY + 70, "u = 22"))
    s.append(dim(X(-F_EST), AY + 110, X(0), AY + 110, "f ~ 25"))
    s.append(dim(X(xi), AY + 150, X(0), AY + 150, f"|v| ~ {-V_IMG:.0f}"))
    s.append(txt(X(-100), AY + 215, "solid red = real rays, dashed = traced back to the virtual image the eye sees", 18, RED, "middle"))
    # old vs new table
    tx, ty = 70, 840
    rows = [("", "v1 concept", "v3.1 (built)"), ("mirror", "yes, 45 deg", "removed"),
            ("u", "40", "22 (bench)"), ("f", "45 (marking)", "~25 (estimate)"),
            ("v", "-360", f"~{V_IMG:.0f}"), ("m", "9x", f"~{M_IMG:.1f}x"), ("body", "foam board", "3D-printed PLA")]
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            s.append(txt(tx + 20 + c * 210, ty + 30 + r * 30, cell, 18, INK if r else BLUE, weight="bold" if r == 0 else "normal"))
    s.append(f'<g filter="url(#rough)">{rect(tx, ty, 640, 235, "none", INK, 2, 8)}</g>')
    s.append(panel(780, 840, 790, 235, "Thin-lens equation", [
        "1/u + 1/v = 1/f   (real-is-positive),   m = -v/u",
        "u < f  ->  v < 0: virtual, upright, magnified",
        "The bench focus (u = 22) shows the real f is ~25,",
        "not the marked 45: so the mirror path was dropped."], size=18, gap=30))
    save("optics_raydiagram.svg", s)


# ---- sheet 3: wiring ------------------------------------------------------------------------------
def wiring():
    s = head("Sign-Language HUD Glasses  -  Wiring", "Display unit  |  red = +, black = GND, yellow = SCL, green = SDA", 3)
    g = ['<g filter="url(#rough)">',
         rect(80, 290, 160, 150, "#f5e6a8"), rect(370, 240, 200, 240, "#f3d9bf"),
         rect(660, 262, 95, 36, "#dddddd"), rect(860, 200, 250, 310, "#d5e8d4"), rect(1310, 220, 190, 240, "#dbe6f5")]
    pin = lambda x, y, c: f'<circle cx="{x}" cy="{y}" r="5" fill="{c}" stroke="{INK}" stroke-width="1.2"/>'
    wires = [((240, 340), (370, 320), RED), ((240, 400), (370, 400), INK), ((570, 320), (660, 280), RED),
             ((755, 280), (860, 280), RED), ((570, 400), (860, 345), INK),
             ((1110, 260), (1310, 260), RED), ((1110, 315), (1310, 315), INK),
             ((1110, 370), (1310, 370), "#e0a020"), ((1110, 425), (1310, 425), GREEN)]
    for (x1, y1), (x2, y2), c in wires:
        xm = (x1 + x2) / 2
        g.append(poly([(x1, y1), (xm, y1), (xm, y2), (x2, y2)], stroke=c, sw=3.2, close=False))
        g += [pin(x1, y1, c), pin(x2, y2, c)]
    g.append('</g>')
    s += g
    s += [txt(160, 252, "LiPo 3.7 V 600 mAh", 21, INK, "middle"), txt(160, 277, "(602030)", 17, GREY, "middle"),
          txt(228, 346, "+ red", 17, RED, "end"), txt(228, 406, "- black", 17, INK, "end"),
          txt(470, 225, "TP4056 Type-C", 21, INK, "middle"), txt(470, 505, "USB-C taped \"NO USB\"", 17, RED, "middle"),
          txt(382, 326, "B+", 18), txt(382, 406, "B-", 18), txt(558, 326, "OUT+", 18, INK, "end"), txt(558, 406, "OUT-", 18, INK, "end"),
          txt(707, 250, "slide switch", 18, INK, "middle"),
          txt(985, 185, "ESP32-C3 SuperMini", 21, INK, "middle"),
          txt(872, 286, "5V", 18), txt(872, 351, "G", 18),
          txt(1098, 266, "3V3", 18, INK, "end"), txt(1098, 321, "G", 18, INK, "end"),
          txt(1098, 376, "GPIO9 (SCL)", 18, INK, "end"), txt(1098, 431, "GPIO8 (SDA)", 18, INK, "end"),
          txt(1405, 205, "0.96\" OLED (SSD1306)", 21, INK, "middle"),
          txt(1322, 266, "VDD", 18), txt(1322, 321, "GND", 18), txt(1322, 376, "SCK", 18), txt(1322, 431, "SDA", 18),
          txt(80, 575, "Power: LiPo -> TP4056 (charge + protection) -> switch -> ESP32-C3 5V pin (on-board 3.3 V regulator)  |  "
                       "OLED on I2C, address 0x3C", 19, BLUE)]
    s.append(panel(80, 630, 690, 420, "Safety (LiPo charging)", [
        "- Charge ONLY from a bench supply on B+ / B-:",
        "  4.20 V, 0.30 A limit, stop at <= 0.05 A.",
        "- Stock TP4056 charges at 1 A = 1.7C: too much",
        "  for 600 mAh, so its USB port is taped.",
        "- Never plug the ESP32 USB-C while the switch",
        "  is ON.",
        "- Solder battery leads one at a time; tape."], size=19, gap=36))
    s.append(panel(830, 630, 740, 420, "Measured (Rigol DM3058E)", [
        "ESP32-C3 5V pin, on USB ........ 5.162 V",
        "ESP32-C3 3V3 pin, on USB ....... 3.302 V",
        "LiPo #1 as received ............ 3.999 V",
        "5V pin on battery, under load .. 3.967 V",
        "",
        "On battery the 5V pin reads the cell voltage;",
        "3V3 stays regulated.",
        "I2C scan: OLED found at 0x3C (both OLEDs)."], size=19, gap=36))
    save("wiring_sheet.svg", s)


# ---- sheet 4: glasses mount (front view) ----------------------------------------------------------
def mount():
    s = head("Sign-Language HUD Glasses  -  Clip-on Mount (Front View)",
             "Looking at the right eye from the front  |  glasses measured 2026-10-31  |  mm", 4)
    k, X0, Y0 = 7.0, 560, 397                       # x = 0 at the body side face's inner wall, z = 0 at tube floor
    X = lambda y: X0 + y * k
    Y = lambda z: Y0 - z * k
    arm_c = -(SIDE_T + CLIP_T + JAW_OUT + TEMPLE / 2)   # temple arm centre (y), = W/2 - DH from the pupil
    zc = AZ + DV
    g = ['<g filter="url(#rough)">',
         # housing cross-section: temple-side wall (thick, dovetail), inside, lid wall
         rect(X(-SIDE_T), Y(TUBE_H + WALL), (SIDE_T + WIDTH + WALL) * k, (TUBE_H + WALL + DROP + WALL) * k, "#e9e6dd"),
         rect(X(0), Y(TUBE_H), WIDTH * k, (TUBE_H + DROP) * k, "#faf8f2"),
         line(X(0), Y(0), X(WIDTH), Y(0), GREY, 1.6, "8 6"),
         # dovetail slot in the side wall at rail_z = 15, and clip plate + rail
         poly([(X(-SIDE_T), Y(15 + 3)), (X(-SIDE_T + 2.5), Y(15 + 4.5)), (X(-SIDE_T + 2.5), Y(15 - 4.5)), (X(-SIDE_T), Y(15 - 3))], "#c9b98a"),
         rect(X(-SIDE_T - CLIP_T), Y(15 + 8), CLIP_T * k, (15 + 8 - zc + 2) * k, "#f0b860"),
         # jaw arm out to the temple, wrapping it
         rect(X(arm_c + TEMPLE / 2), Y(zc + 2), (-SIDE_T - CLIP_T - arm_c - TEMPLE / 2) * k, 4 * k, "#f0b860"),
         poly([(X(arm_c - TEMPLE / 2 - 1.6), Y(zc + TEMPLE / 2 + 1.6)), (X(arm_c + TEMPLE / 2 + 1.6), Y(zc + TEMPLE / 2 + 1.6)),
               (X(arm_c + TEMPLE / 2 + 1.6), Y(zc - TEMPLE / 2 - 0.4)), (X(arm_c + TEMPLE / 2 - 0.45), Y(zc - TEMPLE / 2 - 0.4)),
               (X(arm_c + TEMPLE / 2 - 0.45), Y(zc - TEMPLE / 2 + 0.6)), (X(arm_c - TEMPLE / 2 + 0.45), Y(zc - TEMPLE / 2 + 0.6)),
               (X(arm_c - TEMPLE / 2 + 0.45), Y(zc - TEMPLE / 2 - 0.4)), (X(arm_c - TEMPLE / 2 - 1.6), Y(zc - TEMPLE / 2 - 0.4))], "#f0b860"),
         rect(X(arm_c - TEMPLE / 2), Y(zc + TEMPLE / 2), TEMPLE * k, TEMPLE * k, "#9b6b3c"),
         # glasses frame rim (behind the head) and acrylic edge
         line(X(-12), Y(AZ + RIM), X(WIDTH + 25), Y(AZ + RIM), "#9b6b3c", 2.4, "10 6"),
         line(X(0), Y(AZ), X(WIDTH), Y(AZ), "#7b68ee", 5),
         '</g>']
    s += g
    px, py = X(WIDTH / 2), Y(AZ)
    s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="15" fill="white" stroke="{INK}" stroke-width="2.4"/>'
             f'<circle cx="{px:.1f}" cy="{py:.1f}" r="7" fill="{INK}"/>')
    s += lines(X(WIDTH) + 30, py + 30, ["pupil (level with", "the acrylic centre)"], 17, INK, 22)
    # dimensions
    s.append(line(X(arm_c), Y(AZ), px - 16, Y(AZ), GREY, 1.2, "3 5"))                 # pupil level guide
    s.append(dim(X(arm_c), Y(-DROP - WALL) + 45, px, Y(-DROP - WALL) + 45, "dh = 37"))
    s.append(dim(X(arm_c) - 45, Y(zc), X(arm_c) - 45, Y(AZ), "dv = 10", -1))
    s.append(dim(X(arm_c) - 160, Y(15), X(arm_c) - 160, Y(zc), f"jaw_drop = {JAW_DROP}", -1))
    s.append(line(X(arm_c) - 175, Y(15), X(-SIDE_T - CLIP_T), Y(15), GREY, 1.2, "3 5"))  # rail centre guide
    s.append(dim(X(WIDTH) + 55, Y(AZ + RIM), X(WIDTH) + 55, Y(AZ), "rim = 13", 1))
    s.append(dim(X(WIDTH) + 250, Y(-WALL), X(WIDTH) + 250, Y(AZ + RIM), f"{RIM_GAP} clear", 1))
    s.append(dim(X(arm_c + TEMPLE / 2), Y(zc) - 60, X(-SIDE_T - CLIP_T), Y(zc) - 60, f"{JAW_OUT}"))
    s.append(dim(X(0), Y(TUBE_H + WALL) - 30, X(WIDTH), Y(TUBE_H + WALL) - 30, "29 internal"))
    s.append(dim(X(arm_c - TEMPLE / 2), Y(zc - TEMPLE / 2) + 30, X(arm_c + TEMPLE / 2), Y(zc - TEMPLE / 2) + 30, "7"))
    # callouts
    s.append(leader(X(-SIDE_T - CLIP_T) - 30, Y(28), X(-SIDE_T + 1), Y(16), ["dovetail slot, 4 mm side wall", "(mouth 6, inside 9, depth 2.5)"], anchor="end"))
    s.append(leader(X(arm_c) - 30, Y(zc) + 120, X(arm_c), Y(zc - TEMPLE / 2), ["temple arm 7 x 7", "(snap jaw, 0.45 lips)"], anchor="end"))
    s.append(txt(X(WIDTH) + 30, Y(AZ + RIM) - 10, "glasses frame top rim", 18, BLUE))
    s.append(txt(X(WIDTH / 2), Y(TUBE_H / 2), "electronics tube", 18, GREY, "middle"))
    s.append(txt(X(WIDTH / 2), Y(-DROP + 4), "optics head", 18, GREY, "middle"))
    s.append(panel(1150, 125, 420, 470, "Clip numbers (scad)", [
        f"jaw_drop = {JAW_DROP}  (rail -> arm centre)",
        f"jaw_out  = {JAW_OUT}  (plate -> arm)",
        "check: 14.5 + 4 + 2.5 + 12.5 + 3.5",
        "       = 37 = dh",
        f"snap strain = {STRAIN} %",
        "  (PLA safe <= 2.5 %)",
        f"frame rim: {RIM_GAP} below the tube floor"], size=18, gap=33))
    s.append(panel(1150, 615, 420, 440, "Fit to new glasses", [
        "Measure ~2 cm behind the hinge:",
        "1. arm width x height (7 x 7)",
        "2. pupil -> arm centre, up (dv)",
        "3. pupil -> arm centre, side (dh)",
        "4. frame top rim above pupil (13)",
        "Change these 5 values in the scad,",
        "reprint clip.stl only."], size=18, gap=33))
    save("glasses_mount.svg", s)


# ---- sheet 5: printed parts -----------------------------------------------------------------------
def parts():
    s = head("Sign-Language HUD Glasses  -  3D-Printed Parts", "Outer sizes from the STL files  |  print all 4 from print_all.stl (136.6 x 160.6)  |  mm", 5)
    k = 3.2
    g = ['<g filter="url(#rough)">']
    # body and lid: L-shaped side profile, outer 99.8 x 77.8, head 34.9 wide, tube 34.8 tall
    def lprofile(x0, y0, fill):
        return poly([(x0, y0), (x0 + 99.8 * k, y0), (x0 + 99.8 * k, y0 + 34.8 * k), (x0 + 34.9 * k, y0 + 34.8 * k),
                     (x0 + 34.9 * k, y0 + 77.8 * k), (x0, y0 + 77.8 * k)], fill)
    g += [lprofile(110, 190, "#cfcac0"), lprofile(110, 650, "#e4e0d6")]
    g += [rect(700, 190, 29.8 * k * 1.6, 30.4 * k * 1.6, "#cfcac0"),
          f'<circle cx="{700 + 29.8 * k * 0.8:.1f}" cy="{190 + 30.4 * k * 0.8:.1f}" r="{25 / 2 * k * 1.6:.1f}" fill="#faf8f2" stroke="{INK}" stroke-width="2"/>',
          rect(1060, 190, 25.9 * k * 1.6, 45 * k * 1.6, "#f0b860"),
          rect(700, 650, 30 * k * 1.6, 30 * k * 1.6, "#e6e1fb")]
    g.append('</g>')
    s += g
    s.append(dim(110, 165, 110 + 99.8 * k, 165, "99.8"))
    s.append(dim(85, 190, 85, 190 + 77.8 * k, "77.8", -1))
    s.append(dim(110, 190 + 77.8 * k + 25, 110 + 34.9 * k, 190 + 77.8 * k + 25, "34.9"))
    s.append(dim(110 + 99.8 * k + 25, 190, 110 + 99.8 * k + 25, 190 + 34.8 * k, "34.8", 1))
    s.append(txt(110 + 70 * k, 190 + 55 * k, "BODY x1", 24, BLUE, "middle"))
    s.append(txt(110 + 70 * k, 190 + 55 * k + 30, "33 thick | 50 g | 4.2 h", 18, BLUE, "middle"))
    s.append(txt(110 + 70 * k, 650 + 55 * k, "LID x1", 24, BLUE, "middle"))
    s += lines(110 + 70 * k, 650 + 55 * k + 30, ["same outline", "24.1 thick | 16 g | 1.3 h"], 18, BLUE, 24, "middle")
    s.append(dim(700, 165, 700 + 29.8 * k * 1.6, 165, "29.8"))
    s.append(dim(700 + 29.8 * k * 1.6 + 25, 190, 700 + 29.8 * k * 1.6 + 25, 190 + 30.4 * k * 1.6, "30.4", 1))
    s.append(txt(700 + 29.8 * k * 0.8, 190 + 30.4 * k * 1.6 + 40, "LENS PLATE x1", 22, BLUE, "middle"))
    s.append(txt(700 + 29.8 * k * 0.8, 190 + 30.4 * k * 1.6 + 66, "3 thick | dia 25 lens seat | 2 g", 17, BLUE, "middle"))
    s.append(dim(1060, 165, 1060 + 25.9 * k * 1.6, 165, "25.9"))
    s.append(dim(1060 + 25.9 * k * 1.6 + 25, 190, 1060 + 25.9 * k * 1.6 + 25, 190 + 45 * k * 1.6, "45", 1))
    s.append(txt(1060 + 25.9 * k * 0.8, 190 + 45 * k * 1.6 + 40, "CLIP x1", 22, BLUE, "middle"))
    s.append(txt(1060 + 25.9 * k * 0.8, 190 + 45 * k * 1.6 + 66, "25 thick | 5 g | 0.4 h", 17, BLUE, "middle"))
    s.append(dim(700, 625, 700 + 30 * k * 1.6, 625, "30"))
    s.append(dim(700 + 30 * k * 1.6 + 25, 650, 700 + 30 * k * 1.6 + 25, 650 + 30 * k * 1.6, "30", 1))
    s.append(txt(700 + 30 * k * 0.8, 650 + 30 * k * 1.6 + 40, "ACRYLIC x1 (cut, not printed)", 20, RED, "middle"))
    s.append(txt(700 + 30 * k * 0.8, 650 + 30 * k * 1.6 + 66, "1 mm clear, width 29 - 30.4", 17, RED, "middle"))
    s.append(txt(110, 1010, "Lens plate, clip and acrylic drawn 1.6x larger than the body and lid.", 17, GREY))
    s.append(panel(1060, 600, 510, 455, "Print settings", [
        "Matte black PLA (PETG ok)",
        "0.4 nozzle, 0.2 layers",
        "3 walls, 20 % infill",
        "Supports OFF, do not rotate",
        "Bed >= 140 x 165",
        "All 4 parts: ~73 g PLA,",
        "  ~6 h normal / ~2.5 h fast",
        "Optional test_fit.stl: 27 g"], size=19, gap=36))
    save("print_parts.svg", s)


# ---- sheet 6: OLED screens ------------------------------------------------------------------------
def screens():
    s = head("Sign-Language HUD Glasses  -  What the OLED Shows", "128 x 64 px screen, drawn 2.5x  |  firmware/glasses_display", 6)
    k = 2.5
    def screen(x, y, caption, body, note):
        out = [f'<g filter="url(#rough)">{rect(x - 14, y - 14, 128 * k + 28, 64 * k + 28, "#2a2f3a", INK, 2.4, 10)}</g>',
               rect(x, y, 128 * k, 64 * k, "#05070c", "#05070c", 1), f'<svg x="{x}" y="{y}" width="{128 * k}" height="{64 * k}">',
               *body, '</svg>', txt(x + 64 * k, y - 30, caption, 21, INK, "middle")]
        out += lines(x + 64 * k, y + 64 * k + 48, note, 17, BLUE, 24, "middle")
        return out
    mono = lambda x, y, t, size, anchor="middle": (f'<text x="{x}" y="{y}" font-family="Menlo, Consolas, monospace" '
                                                   f'font-size="{size}" fill="#cfe8ff" text-anchor="{anchor}">{t}</text>')
    big, small = 16 * k * 1.25, 8 * k * 1.25           # text size 2 = 12 x 16 px, size 1 = 6 x 8 px
    x1, x2, x3, y1, y2 = 90, 625, 1160, 200, 640
    s += screen(x1, y1, "1. Boot", [mono(64 * k, 30 * k, "WIFI...", big), mono(64 * k, 47 * k, "&lt;hotspot name&gt;", small)],
                ["joining the 2.4 GHz hotspot"])
    s += screen(x2, y1, "2. Ready", [mono(64 * k, 30 * k, "READY", big), mono(64 * k, 47 * k, "192.168.43.57", small)],
                ["IP shown; also reachable as", "glasses.local, UDP port 4210"])
    s += screen(x3, y1, "3. A word (fits 128 px)", [mono(64 * k, 38 * k, "HELLO", big)],
                ["size 2, centred", "&lt;= 10 characters"])
    s += screen(x1, y2, "4. A sentence (wider than 128 px)", [mono(40 * k, 38 * k, "It is hot to", big, "start")],
                ["scrolls right -&gt; left at 60 px/s", "2 passes, new packet interrupts"])
    s.append(line(x1 + 110 * k, y2 + 54 * k, x1 + 30 * k, y2 + 54 * k, RED, 3, "", "ar"))
    s += screen(x2, y2, "5. After 2 passes", [], ["blank until the next packet"])
    s.append(panel(x3 - 14, y2 - 52, 128 * k + 28, 400, "Timing", [
        "one pass = (12 n + 128) / 60 s",
        "n = characters, at size 2",
        "",
        "\"I am going to school.\"",
        "n = 21: 2 passes = 12.67 s",
        "+ 2 s word gap = 14.67 s",
        "measured: 14.6 s"], size=18, gap=32))
    s.append(txt(W / 2, 1030, "Through the HUD optics the text can look mirrored: set MIRROR_X / FLIP_Y to 1 in the sketch.", 19, GREY, "middle"))
    save("oled_screens.svg", s)


if __name__ == "__main__":
    assert round(V_IMG) == -183 and round(M_IMG, 1) == 8.3 and AZ == -30   # matches the report and scad echo
    assert SIDE_T + CLIP_T + JAW_OUT + TEMPLE / 2 + WIDTH / 2 == DH          # clip geometry closes on dh
    for f in (side_view, optics, wiring, mount, parts, screens):
        f()
