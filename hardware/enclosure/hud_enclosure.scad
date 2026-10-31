// HUD glasses display-unit enclosure v3 (parametric, OpenSCAD).
// v3: no mirror. OLED lies flat, screen down, straight above the lens (bench: OLED -> lens 22 mm is sharp).
// v2 features kept: a pocket per component, lid clicks shut, clip-on mount (dovetail slot + swappable clip).
// Units: mm. Design axes (left-hand build, mirrored for side = "right"):
//   x = front (0) -> rear (L), y = body side wall (0) -> lid (W), z = tube floor (0) -> top (H).
//   Head drops below z = 0 to z = -drop. Body side wall faces the temple arm.
// Light path: OLED (screen down) -> lens -> acrylic 45 deg -> eye.
// Render one part:  openscad -D 'part="body"' -o stl/body.stl hud_enclosure.scad
// Parts: body | lid | lens_plate | clip | plate (all 4 on one bed) | test_fit | assembly, section (previews only)

/* [View] */
part = "assembly";  // [assembly, section, plate, body, lid, lens_plate, clip, test_fit]
side = "right";     // [right, left] eye the display sits in front of

/* [Housing, internal] */
L      = 95;   // total internal length
H      = 30;   // tube internal height
W      = 29;   // internal width
drop   = 43;   // head goes this far below the tube floor (fits the acrylic at 25 mm)
wall   = 2.4;
side_t = 4;    // body side wall, thicker to hold the dovetail slot

/* [Fits] */
clr     = 0.3;   // slide-in slots: acrylic, lens plate, OLED, pockets
fit_clr = 0.15;  // lid lip to wall
g       = 1.0;   // groove depth into each side wall

/* [Optics] -- distances from the Step 12 bench test */
d_oled_lens = 22;    // OLED screen -> lens centre (bench: sharp at 22)
d_lens_acr  = 25;    // lens centre -> acrylic centre (chosen 25; does not change focus)
focus_step  = 3;     // OLED slot pitch
focus_n     = 1;     // slots each side of nominal -> u = 19 / 22 / 25
acr_L    = 30;  acr_t    = 1;   // clear acrylic beam combiner (45 deg)
lens_d   = 25;  lens_t   = 5;   // lens diameter, centre thickness  MEASURE
lens_seat = 1.5;                // counterbore depth in lens plate
lens_lip  = 1.0;                // ledge the lens rests on
plate_t   = 3;
lens_z    = -6;                 // lens plate top, below the tube floor so the OLED + pins fit under the top

/* [OLED module, lies flat, screen down, pins at the rear edge] */
oled_w = 27.3;  oled_h = 27.8;  // PCB across (y) x along (x)        MEASURE
oled_pcb_t   = 1.2;
oled_glass_t = 1.5;             // glass under the PCB                 MEASURE
oled_glass_x = [4.0, 23.3];     // glass span along x from the PCB front edge  MEASURE
oled_pin_h   = 3.5;             // room above the PCB for header pins bent flat
rail_w       = 2.5;             // OLED rails: reach in from each side wall

/* [Electronics] */
lipo  = [30, 20, 6];   // 600 mAh 602030: L, W, T          MEASURE
tp    = [28, 17.5];    // TP4056 Type-C board L, W         MEASURE
tp_h  = 5.5;           // TP4056 height incl. parts        MEASURE
esp   = [22.5, 18];    // ESP32-C3 SuperMini L, W          MEASURE
pcb_t = 1.6;
usbc_shell_h = 3.2;    // USB-C receptacle height above PCB
usbc        = [9.2, 3.6];  // ESP32 port cut-out (W, H)
usbc_recess = [13, 7];     // outside pocket so the plug overmold reaches the port
usbc_web    = 0.8;         // wall left at the port
chg_d   = 3.5;             // charge-lead exit (B+/B- pigtail to bench supply)
shelf_t = 1.6;
shelf_w = 22;              // trays leave a wire gap on the lid side
rim_t   = 1.2;             // pocket rim thickness
rim_h   = 1.0;             // board pocket rim height above tray
lipo_rim_h = 4;
s1 = lipo[2] + 1.5;                // TP4056 tray, above the LiPo
s2 = s1 + shelf_t + tp_h + 3.0;    // ESP32 tray (room to slide the TP4056 in)
sw_body = [8.6, 3.6, 3.6];  // slide switch body L, W, H     MEASURE
sw_slot = [7, 3.5];         // lever slot in top wall
sw_x    = 60;
finger_t = 1.5;             // lid finger that holds a board down on its USB-C shell

/* [Lid click] */
lip_t = 1.2;  lip_h = 2;    // lid locating lip
bump  = 0.4;  dimple = 0.6; // lip bumps snap into wall dimples

/* [Clip-on mount] */
slot_mouth = 6;  slot_in = 9;  slot_d = 2.5;   // female dovetail in body side wall
slot_x0 = 45;                                  // closed front end; open at the rear
rail_z  = H / 2;
dt_clr  = 0.15;              // dovetail clearance per side (friction fit)
clip_len = 25;
clip_t   = 2.5;              // clip back plate
// Glasses, measured 2026-10-31 (Step 12 sheet, Lenskart frame). New glasses: change these 5, reprint clip only.
temple_w  = 7;               // temple arm width (side to side)
temple_h  = 7;               // temple arm height (top to bottom)
temple_dv = 10;              // pupil -> arm centre, up (+) / down (-)
temple_dh = 37;              // pupil -> arm centre, sideways
frame_rim = 13;              // frame top edge above the pupil
jaw_t    = 1.6;              // jaw wall
jaw_lip  = 0.45;             // lips under the temple (snap)
jaw_grip = 0.3;              // jaw narrower than temple by this much
clip_x   = 60;               // clip position in the assembly preview

/* [Zip ties, v1 backup] */
tie_grooves_on = false;
tie_x = [48, 84];
tie_w = 5;  tie_d = 1;

$fn = 64;
e = 0.01;

// ---- derived ----
head_L  = oled_h + clr + 2;               // optics head length
ox      = (oled_glass_x[0] + oled_glass_x[1]) / 2;  // optical axis x = OLED glass centre
lens_cz = lens_z - lens_seat + lens_t / 2;  // lens centre
az      = lens_cz - d_lens_acr;           // acrylic centre z
function oled_glass_z(i) = lens_cz + d_oled_lens + i * focus_step;   // screen surface for slot i
function oled_pcb_z(i)   = oled_glass_z(i) + oled_glass_t;           // PCB underside for slot i
rail_z0 = oled_pcb_z(-focus_n) - clr / 2 - (focus_step - oled_pcb_t - clr);  // bottom of OLED rails
lipo_x0 = L - lipo[0];
board_y0 = rim_t + clr;                   // boards sit against the body-side rim
tp_y    = board_y0 + tp[1] / 2;
esp_y   = board_y0 + esp[1] / 2;
tp_top  = s1 + shelf_t + pcb_t;
esp_top = s2 + shelf_t + pcb_t;
esp_usb_z = esp_top + usbc[1] / 2;
chg_y = (shelf_w + W - lip_h) / 2;        // in the lid-side wire gap
chg_z = lipo_rim_h;
half_a  = acr_L / 2 * cos(45);
cut_max = W + 2 * (g - clr);              // widest acrylic that still fits
jaw_vc   = az + temple_dv;                 // temple centre z (pupil sits level with the acrylic centre)
jaw_drop = rail_z - jaw_vc;                // rail centre -> temple centre, down
jaw_out  = temple_dh - W / 2 - side_t - clip_t - temple_w / 2;  // gap from clip plate to temple arm
jaw_uc   = clip_t + jaw_out + temple_w / 2;  // temple centre, outward from body side face
jaw_strain = 1.5 * jaw_t * jaw_lip / pow(temple_h, 2);  // cantilever snap strain

echo(str("Optics: OLED slots at u = ", [for (i = [-focus_n:focus_n]) d_oled_lens + i * focus_step], " mm (bench value, not from f = 45)"));
echo(str("Cut acrylic ", acr_L, " x ", W, "..", cut_max, " mm. Eye level (acrylic centre) is ", -az, " mm below the tube floor"));
echo(str("Clip jaw snap strain ", round(jaw_strain * 1000) / 10, " % (PLA safe <= 2.5 %); jaw_drop ", jaw_drop, ", jaw_out ", jaw_out));
echo(str("Frame rim top sits ", -wall - (az + frame_rim), " mm below the tube floor"));

// ---- self-checks: fail the render if parts collide ----
assert(az - half_a - acr_t >= -drop, "acrylic hits head bottom");
assert(az + half_a + acr_t <= lens_z - plate_t, "acrylic hits lens plate");
assert(ox - lens_d / 2 - 0.2 >= 0 && ox + lens_d / 2 + 0.2 <= head_L - clr, "lens does not fit the lens plate");
assert(ox - half_a - acr_t > 0 && ox + half_a + acr_t < head_L, "acrylic longer than the head");
assert(oled_glass_z(-focus_n) - (lens_cz + lens_t / 2) > 5, "lowest OLED slot too close to the lens");
assert(oled_pcb_z(focus_n) + oled_pcb_t + oled_pin_h <= H, "no room above the OLED for its pins: lower lens_z");
assert(focus_step - oled_pcb_t - clr >= 1.0, "OLED rail tines too thin");
assert(W / 2 - (lens_d / 2 - lens_lip) >= rail_w, "OLED rails block the light cone");
assert(oled_glass_x[0] >= 2 && oled_h - oled_glass_x[1] >= 2, "no glass-free strip for the OLED rails");
assert(head_L + 10 < lipo_x0 - clr - rim_t, "no room for OLED wires before LiPo cradle");
assert(lipo[1] + clr + rim_t <= W - lip_h - 0.5, "LiPo cradle hits lid lip");
assert(s1 >= lipo[2] + 0.5, "TP4056 tray sits on LiPo");
assert(board_y0 + max(tp[1], esp[1]) <= shelf_w, "board wider than its tray");
assert(s2 - (s1 + shelf_t) >= tp_h + 2, "no room to slide TP4056 into its pocket");
assert(tp_top + usbc_shell_h + 0.2 + finger_t < s2, "TP4056 lid finger hits ESP32 tray");
assert(esp_top + usbc_shell_h + 0.2 + finger_t < H - fit_clr - lip_t, "ESP32 lid finger hits top lip");
assert(esp_usb_z + usbc_recess[1] / 2 <= H, "ESP32 USB-C pocket runs into top wall");
assert(chg_y - chg_d / 2 > lipo[1] + clr + rim_t && chg_y + chg_d / 2 < W - lip_h, "charge-lead hole not in the wire gap");
assert(chg_z + chg_d / 2 < s1, "charge-lead hole hits TP4056 tray");
assert(sw_x + sw_body[0] / 2 + rim_t < L - esp[0] - clr - rim_t - 1, "switch cradle hits ESP32 tray");
assert(slot_d <= side_t - 1, "dovetail slot too deep for side wall");
assert(rail_z - slot_in / 2 > 1 && rail_z + slot_in / 2 < H - 1, "dovetail slot outside tube height");
assert(slot_x0 > head_L, "dovetail slot must sit on the tube");
assert(jaw_drop > temple_h / 2 + jaw_t + slot_in / 2, "clip jaw overlaps the dovetail");
assert(temple_w - 2 * jaw_lip > 1, "jaw opening too narrow for the temple");
assert(jaw_strain <= 0.025, "clip jaw too stiff, PLA will crack: lower jaw_lip or jaw_t");
assert(jaw_out >= 2, "temple arm too close to the housing for the clip arm");
assert(az + frame_rim + 1 < -wall, "glasses frame rim hits the bottom of the tube");

module box(p0, p1) translate(p0) cube(p1 - p0);

// Print parts mirrored for the right eye (mirror in x on the bed = same shape as mirror in y)
module hand_print() if (side == "right") mirror([1, 0, 0]) children(); else children();
// Preview mirrored for the right eye, keeping front at the front
module hand_view() if (side == "right") translate([0, W, 0]) mirror([0, 1, 0]) children(); else children();

// Text cut into a horizontal face; counter-mirrored so it still reads after hand_print()
module label(txt, p) translate(p) if (side == "right") mirror([1, 0, 0]) lbl(txt); else lbl(txt);
module lbl(txt) translate([0, 0, -0.4]) linear_extrude(0.4 + e)
    text(txt, size = 3, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");

// L-shaped side panel in the x-z plane
module side_profile()
    polygon([[-wall, -drop - wall], [head_L + wall, -drop - wall], [head_L + wall, -wall],
             [L + wall, -wall], [L + wall, H + wall], [-wall, H + wall]]);

module side_wall(y0, t) translate([0, y0 + t, 0]) rotate([90, 0, 0]) linear_extrude(t) side_profile();

// Grooves the acrylic and lens plate slide into (same on body and lid)
module optic_grooves(y0, y1) {
    translate([ox, (y0 + y1) / 2, az]) rotate([0, 45, 0])
        cube([acr_L + 2 * clr, y1 - y0, acr_t + clr], center = true);   // "\" folds light to the eye
    box([0, y0, lens_z - plate_t - clr / 2], [head_L, y1, lens_z + clr / 2]);
}

// OLED rails on one side wall (y0..y1): only on the glass-free strips at the front and rear of the PCB.
// Each rail has 2*focus_n+1 slots; the PCB edge slides into one of them.
module oled_rails(y0, y1) {
    strips = [[0, oled_glass_x[0] - 0.5], [oled_glass_x[1] + 0.5, oled_h + clr]];
    for (s = strips) difference() {
        box([s[0], y0, rail_z0], [s[1] + (s == strips[1] ? 1.5 : 0), y1, H + e]);   // rear strip ends in a stop
        for (i = [-focus_n:focus_n])
            box([s[0] - e, y0 - e, oled_pcb_z(i) - clr / 2], [min(s[1], oled_h + clr), y1 + e, oled_pcb_z(i) + oled_pcb_t + clr / 2]);
    }
}

module tie_grooves() if (tie_grooves_on) for (x = tie_x) difference() {
    box([x - tie_w / 2, -side_t - e, -drop - wall - e], [x + tie_w / 2, W + wall + e, H + wall + e]);
    box([x - tie_w / 2 - e, -side_t + tie_d, -wall + tie_d], [x + tie_w / 2 + e, W + wall - tie_d, H + wall - tie_d]);
}

module usb_cut(y, z) {
    translate([L - e, y - usbc[0] / 2, z - usbc[1] / 2]) cube([wall + 2 * e, usbc[0], usbc[1]]);
    translate([L + usbc_web, y - usbc_recess[0] / 2, z - usbc_recess[1] / 2]) cube([wall, usbc_recess[0], usbc_recess[1]]);
}

// Tray with a 3-side pocket: front stop + body-side rim; the rear wall is the 4th side
module tray(z, b) {
    x0 = L - b[0] - clr;
    box([x0 - rim_t - 1, 0, z], [L, shelf_w, z + shelf_t]);
    box([x0 - rim_t, 0, z + shelf_t - e], [x0, board_y0 + b[1] + clr, z + shelf_t + rim_h]);
    box([x0 - rim_t, 0, z + shelf_t - e], [L, rim_t, z + shelf_t + rim_h]);
}

// LiPo cradle on the floor: front + lid-side rims, notch for the leads
module lipo_cradle() difference() {
    union() {
        box([lipo_x0 - clr - rim_t, 0, -e], [lipo_x0 - clr, lipo[1] + clr + rim_t, lipo_rim_h]);
        box([lipo_x0 - clr - rim_t, lipo[1] + clr, -e], [L, lipo[1] + clr + rim_t, lipo_rim_h]);
    }
    box([lipo_x0 - clr - rim_t - e, lipo[1] / 2 - 3, 1], [lipo_x0 - clr + e, lipo[1] / 2 + 3, lipo_rim_h + e]);
}

// Press-fit frame for the slide switch, hanging from the top wall
module switch_cradle() difference() {
    box([sw_x - sw_body[0] / 2 - rim_t, W / 2 - sw_body[1] / 2 - rim_t, H - sw_body[2] + 0.6],
        [sw_x + sw_body[0] / 2 + rim_t, W / 2 + sw_body[1] / 2 + rim_t, H + e]);
    box([sw_x - sw_body[0] / 2 + 0.05, W / 2 - sw_body[1] / 2 + 0.05, H - sw_body[2]],
        [sw_x + sw_body[0] / 2 - 0.05, W / 2 + sw_body[1] / 2 - 0.05, H + 2 * e]);
}

// Female dovetail along x in the outer face of the body side wall, open at the rear
module dovetail_slot()
    translate([slot_x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(L + wall - slot_x0 + e)
        polygon([[-side_t - e, rail_z - slot_mouth / 2], [-side_t + slot_d, rail_z - slot_in / 2],
                 [-side_t + slot_d, rail_z + slot_in / 2], [-side_t - e, rail_z + slot_mouth / 2]]);

// Lid-click points: x positions on the top wall and on the floor (tube only)
click_top = [head_L + 15, L - 15];
click_bot = [(head_L + 2 + L - 2) / 2];

module body() difference() {
    union() {
        side_wall(-side_t, side_t);
        box([-wall, 0, H], [L + wall, W, H + wall]);                    // top
        box([L, 0, -wall], [L + wall, W, H + wall]);                    // rear
        box([head_L, 0, -wall], [L + wall, W, 0]);                      // tube floor
        box([head_L, 0, lens_z], [head_L + wall, W, 0]);                // head back, between lens plate and tube
        box([-wall, 0, lens_z - plate_t], [0, W, H + wall]);            // head front, above lens plate
        box([-wall, 0, -drop - wall], [head_L + wall, W, -drop]);       // head bottom bar
        oled_rails(0, rail_w);
        lipo_cradle();
        tray(s1, tp);
        tray(s2, esp);
        switch_cradle();
    }
    optic_grooves(-g, e);
    usb_cut(esp_y, esp_usb_z);
    translate([L - e, chg_y, chg_z]) rotate([0, 90, 0]) cylinder(d = chg_d, h = wall + 2 * e);
    box([sw_x - sw_slot[0] / 2, W / 2 - sw_slot[1] / 2, H - e], [sw_x + sw_slot[0] / 2, W / 2 + sw_slot[1] / 2, H + wall + e]);
    dovetail_slot();
    tie_grooves();
    for (x = click_top) translate([x, W - lip_h / 2, H - 1 + dimple]) sphere(r = 1);
    for (x = click_bot) translate([x, W - lip_h / 2, 1 - dimple]) sphere(r = 1);
    label("LiPo",   [lipo_x0 + lipo[0] / 2, lipo[1] / 2, 0]);
    label("TP4056", [L - tp[0] / 2, tp_y, s1 + shelf_t]);
    label("ESP32",  [L - esp[0] / 2, esp_y, s2 + shelf_t]);
}

module lid() difference() {
    union() {
        side_wall(W, wall);
        oled_rails(W - rail_w, W);
        // locating lip: thin bars that sit just inside the body's walls
        box([head_L + 1, W - lip_h, H - fit_clr - lip_t], [L - 2, W, H - fit_clr]);       // top (tube only)
        box([L - fit_clr - lip_t, W - lip_h, 2], [L - fit_clr, W, H - 2]);                // rear
        box([head_L + 2, W - lip_h, fit_clr], [L - 2, W, fit_clr + lip_t]);               // tube floor
        box([fit_clr, W - lip_h, lens_z + 1], [fit_clr + lip_t, W, rail_z0 - 1]);         // head front, below the rails
        box([2, W - lip_h, -drop + fit_clr], [head_L - 2, W, -drop + fit_clr + lip_t]);   // head bottom
        // bumps that click into the body dimples
        for (x = click_top) translate([x, W - lip_h / 2, H - fit_clr - 1 + bump]) sphere(r = 1);
        for (x = click_bot) translate([x, W - lip_h / 2, fit_clr + 1 - bump]) sphere(r = 1);
        // fingers press each board down on its USB-C shell when the lid is shut
        box([L - 7, tp_y - 3, tp_top + usbc_shell_h + 0.2], [L - 2, W, tp_top + usbc_shell_h + 0.2 + finger_t]);
        box([L - 7, esp_y - 3, esp_top + usbc_shell_h + 0.2], [L - 2, W, esp_top + usbc_shell_h + 0.2 + finger_t]);
    }
    optic_grooves(W - e, W + g);
    tie_grooves();
}

// Lens sits in the counterbore; plate slides into the side-wall grooves under the OLED
module lens_plate() {
    pw = W + 2 * (g - clr);
    difference() {
        cube([head_L - clr, pw, plate_t]);
        translate([ox, pw / 2, plate_t - lens_seat]) cylinder(d = lens_d + 0.4, h = lens_seat + e);
        translate([ox, pw / 2, -e]) cylinder(d = lens_d - 2 * lens_lip, h = plate_t + 2 * e);
    }
}

// Clip profile in (u, v): u = outward from the body side face, v = z.
// Male dovetail -> back plate -> arm -> C-jaw that snaps over the temple arm from below.
module clip_uv() {
    top = rail_z + slot_in / 2 + 2;
    jaw_top = jaw_vc + temple_h / 2;
    union() {
        polygon([[e, rail_z - slot_mouth / 2 + dt_clr], [-slot_d + 0.2, rail_z - slot_in / 2 + dt_clr],
                 [-slot_d + 0.2, rail_z + slot_in / 2 - dt_clr], [e, rail_z + slot_mouth / 2 - dt_clr]]);
        translate([0, jaw_top]) square([clip_t, top - jaw_top]);                         // back plate
        translate([0, jaw_top]) square([jaw_uc + temple_w / 2 + jaw_t, jaw_t]);         // arm
        difference() {
            translate([jaw_uc - temple_w / 2 - jaw_t, jaw_vc - temple_h / 2])
                square([temple_w + 2 * jaw_t, temple_h + jaw_t]);
            translate([jaw_uc - (temple_w - jaw_grip) / 2, jaw_vc - temple_h / 2 + jaw_lip])
                square([temple_w - jaw_grip, temple_h - jaw_lip + e]);                    // temple space
            translate([jaw_uc - temple_w / 2 + jaw_lip, jaw_vc - temple_h / 2 - e])
                square([temple_w - 2 * jaw_lip, jaw_lip + 2 * e]);                         // snap-in opening
        }
    }
}

// Clip in design coordinates (for the preview)
module clip_3d() translate([clip_x, 0, 0]) rotate([90, 0, 90]) linear_extrude(clip_len)
    translate([-side_t, 0]) mirror([1, 0]) clip_uv();

// Small prints to check fits before the full body
module test_fit() {
    // head strip of the body: OLED rails, acrylic and lens-plate grooves
    translate([0, 0, side_t]) rotate([90, 0, 0]) intersection() {
        body();
        box([-wall - e, -side_t - e, -drop - wall - e], [head_L + wall + e, 3, H + wall + e]);
    }
    // rear-wall patch: ESP32 USB-C cut-out + charge-lead hole, printed outside face down
    translate([40 - 2, 45, L + wall]) rotate([0, 90, 0]) intersection() {
        body();
        box([L - 3, e, 2], [L + wall + e, W, 28]);
    }
    translate([40, -35, 0]) lens_plate();
    // TP4056 pocket
    translate([95 - (L - tp[0] - 4), 0, -s1]) intersection() {
        body();
        box([L - tp[0] - 4, e, s1 - e], [L, W, s1 + shelf_t + rim_h + e]);
    }
    // 30 mm of dovetail slot + the clip
    translate([95 - (L - 30), -45, side_t]) rotate([90, 0, 0]) intersection() {
        body();
        box([L - 30, -side_t - e, rail_z - slot_in / 2 - 3], [L + wall + e, 0, rail_z + slot_in / 2 + 3]);
    }
    translate([150, 0, 0]) linear_extrude(clip_len) clip_uv();
}

// Everything inside the housing, in place (ghost parts for previews)
module internals() {
    color("silver") translate([clr / 2, -(g - clr), lens_z - plate_t]) lens_plate();
    color("lightblue", 0.6) translate([ox, W / 2, az]) rotate([0, 45, 0]) cube([acr_L, W, acr_t], center = true);
    color("white", 0.7) translate([ox, W / 2, lens_z - lens_seat]) cylinder(d = lens_d, h = lens_t);
    color("navy") translate([0, (W - oled_w) / 2, oled_pcb_z(0)]) cube([oled_h, oled_w, oled_pcb_t]);
    color("black") translate([oled_glass_x[0], (W - oled_w) / 2 + 0.3, oled_glass_z(0)])
        cube([oled_glass_x[1] - oled_glass_x[0], oled_w - 0.6, oled_glass_t]);
    color("gold", 0.8) translate([lipo_x0, 0, 0]) cube(lipo);
    color("green") translate([L - tp[0], board_y0, s1 + shelf_t]) cube([tp[0], tp[1], pcb_t]);
    color("purple") translate([L - esp[0], board_y0, s2 + shelf_t]) cube([esp[0], esp[1], pcb_t]);
}

module assembly() hand_view() {
    color("dimgray") body();
    color("gray", 0.4) translate([0, 25, 0]) lid();   // exploded
    internals();
    color("orange") clip_3d();
    color("saddlebrown", 0.6) translate([clip_x - 30, -side_t - jaw_uc - temple_w / 2, jaw_vc - temple_h / 2])
        cube([clip_len + 60, temple_w, temple_h]);   // temple arm (ghost)
}

// Body and parts cut in half along the length (no lid) to see inside
module section() hand_view() intersection() {
    union() { color("dimgray") body(); internals(); }
    box([-50, -50, -100], [200, W / 2, 100]);
}

// Print orientations (flat on the bed, no supports)
module body_print() translate([0, 0, side_t]) rotate([90, 0, 0]) body();      // side wall down
module lid_print()  translate([0, 0, W + wall]) rotate([-90, 0, 0]) lid();    // outside face down
module clip_print() linear_extrude(clip_len) clip_uv();                       // profile flat

// All four parts on one bed: one file, one print job
bed = [220, 220];
Hb  = H + drop + 2 * wall;                 // body/lid footprint across the bed
clip_v0 = jaw_vc - temple_h / 2 - e;       // lowest point of the clip profile
assert(10 + 2 * Hb <= bed[1] && L + 2 * wall + 50 <= bed[0], "parts do not fit on one bed");
module plate() {
    translate([wall + 5, H + wall + 5, 0]) body_print();
    translate([wall + 5, Hb + 10 + drop + wall, 0]) lid_print();
    translate([L + 2 * wall + 12, 5, 0]) lens_plate();
    translate([L + 2 * wall + 12 + slot_d, 45 - clip_v0, 0]) clip_print();
}

if (part == "body")            hand_print() body_print();
else if (part == "lid")        hand_print() lid_print();
else if (part == "lens_plate") lens_plate();
else if (part == "clip")       hand_print() clip_print();
else if (part == "plate")      hand_print() plate();
else if (part == "test_fit")   hand_print() test_fit();
else if (part == "section")    section();
else                           assembly();
