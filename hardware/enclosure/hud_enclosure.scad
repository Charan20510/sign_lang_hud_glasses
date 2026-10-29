// HUD glasses display-unit enclosure (parametric, OpenSCAD).
// Dimensions from files/hud_glasses_drawings.pdf and docs/handoff/00_project_overview.md §3.
// Units: mm. Axes: x = front (0) -> rear (L), y = body side wall (0) -> lid (W),
//                  z = tube floor (0) -> top (H). Head drops below z = 0 to z = -drop.
// Render one part:  openscad -D 'part="body"' -o stl/body.stl hud_enclosure.scad
// Parts: body | lid | lens_plate | test_fit | assembly (preview only)

part = "assembly";

/* [Housing, internal] */
L      = 95;   // total internal length
head_L = 25;   // optics head length
H      = 30;   // tube internal height
W      = 29;   // internal width
drop   = 30;   // head goes this far below the tube floor (total head 60)
wall   = 2.4;

/* [Fits] */
clr     = 0.3;   // slide-in slots: mirror, acrylic, lens plate, OLED
fit_clr = 0.15;  // lid lip to wall
g       = 1.0;   // groove depth into each side wall

/* [Optics] */
f_lens        = 45;
d_oled_mirror = 22;
d_mirror_lens = 18;
d_lens_acr    = 16;  // drawing says 15; +1 so the 30 mm acrylic clears the lens plate (focus unaffected)
mirror_L = 25;  mirror_t = 2;   // glass mirror (45 deg)
acr_L    = 30;  acr_t    = 1;   // clear acrylic beam combiner (45 deg)
lens_d   = 25;  lens_t   = 5;   // biconvex lens, centre thickness
lens_seat = 1.5;                // counterbore depth in lens plate
lens_lip  = 1.0;                // ledge the lens rests on
plate_t   = 3;

/* [OLED module] */
oled_w = 27.3;  oled_h = 27.8;
oled_pcb_t   = 1.2;
oled_glass_t = 1.5;  // PCB front face -> screen surface
focus_step   = 3;    // comb slot pitch
focus_n      = 1;    // slots each side of nominal -> +-focus_n*focus_step
comb_h       = 3;
comb_slot_d  = 2;

/* [Electronics] -- measure with calipers and update */
lipo  = [35, 26, 7];   // L, W, T
tp    = [28, 17.5];    // TP4056 Type-C board L, W
tp_h  = 5.5;           // TP4056 height incl. parts
esp   = [22.5, 18];    // ESP32-C3 SuperMini L, W
pcb_t = 1.6;
usbc        = [9.2, 3.6];  // port cut-out (W, H)
usbc_recess = [13, 7];     // outside pocket so the plug overmold reaches the port
usbc_web    = 0.8;         // wall left at the port
shelf_t = 1.6;
shelf_w = 22;              // shelves leave a wire gap on the lid side
s1 = lipo[2] + 1.5;                // TP4056 shelf, above the LiPo
s2 = s1 + shelf_t + tp_h + 1.5;    // ESP32 shelf
sw_slot = [7, 3.5];        // slide-switch lever slot in top wall
sw_x    = 60;

/* [Mounting] */
tie_x = [48, 84];          // zip-tie / velcro grooves around the tube
tie_w = 5;  tie_d = 1;
lip_t = 1.2;  lip_h = 2;   // lid locating lip

$fn = 64;
e = 0.01;

// ---- derived ----
ox      = head_L / 2;                     // optical axis x
lens_cz = -lens_seat + lens_t / 2;        // lens centre (lens plate top = z 0)
mz      = lens_cz + d_mirror_lens;        // mirror centre z
az      = lens_cz - d_lens_acr;           // acrylic centre z
pcb_x   = ox + d_oled_mirror + oled_glass_t + oled_pcb_t / 2;  // nominal OLED PCB centre
slot_w  = oled_pcb_t + clr;
comb_x0 = pcb_x - focus_n * focus_step - slot_w / 2 - 2;
comb_x1 = pcb_x + focus_n * focus_step + slot_w / 2 + 2;
lipo_x0 = L - lipo[0];
usb_y     = shelf_w / 2;
tp_usb_z  = s1 + shelf_t + pcb_t + usbc[1] / 2;
esp_usb_z = s2 + shelf_t + pcb_t + usbc[1] / 2;
half_m  = mirror_L / 2 * cos(45);
half_a  = acr_L / 2 * cos(45);
cut_max = W + 2 * (g - clr);              // widest mirror/acrylic that still fits

u = d_oled_mirror + d_mirror_lens;
v = 1 / (1 / f_lens - 1 / u);
echo(str("Optics: u = ", u, " mm (< f = ", f_lens, "), virtual image ", round(-v), " mm away, x", round(-v / u), " magnified"));
echo(str("Cut mirror ", mirror_L, " x ", W, "..", cut_max, " mm; acrylic ", acr_L, " x ", W, "..", cut_max, " mm"));
echo(str("OLED focus slots at u = ", [for (i = [-focus_n:focus_n]) u + i * focus_step], " mm"));

// ---- self-checks: fail the render if parts collide ----
assert(mz + half_m + mirror_t <= H, "mirror hits top wall");
assert(ox - half_m >= 1, "mirror hits front wall");
assert(az - half_a - acr_t >= -drop, "acrylic hits head bottom");
assert(az + half_a + acr_t <= -plate_t, "acrylic hits lens plate");
assert(u < f_lens, "OLED must sit inside focal length for a virtual image");
assert(focus_step >= slot_w + 0.8, "OLED comb tines too thin");
assert(comb_x0 > head_L, "OLED comb runs into optics head");
assert(comb_x1 + 10 < lipo_x0, "no room for OLED header wires before LiPo");
assert(lipo[1] <= W - lip_h - 0.5, "LiPo too wide, hits lid lip");
assert(s1 >= lipo[2] + 0.5, "TP4056 shelf sits on LiPo");
assert(esp_usb_z - tp_usb_z >= usbc_recess[1] + 0.8, "USB-C pockets overlap");
assert(esp_usb_z + usbc_recess[1] / 2 <= H, "ESP32 USB-C pocket runs into top wall");
assert(abs(sw_x - tie_x[0]) > (sw_slot[0] + tie_w) / 2 && abs(sw_x - tie_x[1]) > (sw_slot[0] + tie_w) / 2, "switch slot hits tie groove");

module box(p0, p1) translate(p0) cube(p1 - p0);

// L-shaped side panel in the x-z plane
module side_profile()
    polygon([[-wall, -drop - wall], [head_L + wall, -drop - wall], [head_L + wall, -wall],
             [L + wall, -wall], [L + wall, H + wall], [-wall, H + wall]]);

module side_wall(y0) translate([0, y0 + wall, 0]) rotate([90, 0, 0]) linear_extrude(wall) side_profile();

// 45 deg slot for a flat optic, centred on the optical axis
module slab(cz, a, len, t, y0, y1)
    translate([ox, (y0 + y1) / 2, cz]) rotate([0, a, 0]) cube([len + 2 * clr, y1 - y0, t + clr], center = true);

// Grooves the mirror, acrylic and lens plate slide into (same on body and lid)
module optic_grooves(y0, y1) {
    slab(mz, -45, mirror_L, mirror_t, y0, y1);   // "/" folds OLED light down
    slab(az,  45, acr_L,    acr_t,    y0, y1);   // "\" folds it back to the eye
    box([0, y0, -plate_t - clr / 2], [head_L, y1, clr / 2]);
}

module tie_grooves() for (x = tie_x) difference() {
    box([x - tie_w / 2, -wall - e, -drop - wall - e], [x + tie_w / 2, W + wall + e, H + wall + e]);
    box([x - tie_w / 2 - e, -wall + tie_d, -wall + tie_d], [x + tie_w / 2 + e, W + wall - tie_d, H + wall - tie_d]);
}

module usb_cut(z) {
    translate([L - e, usb_y - usbc[0] / 2, z - usbc[1] / 2]) cube([wall + 2 * e, usbc[0], usbc[1]]);
    translate([L + usbc_web, usb_y - usbc_recess[0] / 2, z - usbc_recess[1] / 2]) cube([wall, usbc_recess[0], usbc_recess[1]]);
}

// Floor comb: OLED PCB drops into one slot; pick the slot that gives a sharp image
module oled_comb() difference() {
    box([comb_x0, 0, 0], [comb_x1, W - 0.2, comb_h]);
    for (i = [-focus_n:focus_n])
        box([pcb_x + i * focus_step - slot_w / 2, -e, comb_h - comb_slot_d], [pcb_x + i * focus_step + slot_w / 2, W, comb_h + e]);
}

module body() difference() {
    union() {
        side_wall(-wall);
        box([-wall, 0, H], [L + wall, W, H + wall]);                  // top
        box([L, 0, -wall], [L + wall, W, H + wall]);                  // rear
        box([head_L, 0, -wall], [L + wall, W, 0]);                    // tube floor
        box([-wall, 0, -plate_t], [0, W, H + wall]);                  // head front, above lens
        box([-wall, 0, -drop - wall], [head_L + wall, W, -drop]);     // head bottom bar
        oled_comb();
        box([L - tp[0] - 2, 0, s1], [L, shelf_w, s1 + shelf_t]);      // TP4056 shelf
        box([L - esp[0] - 2, 0, s2], [L, shelf_w, s2 + shelf_t]);     // ESP32 shelf
    }
    optic_grooves(-g, e);
    usb_cut(tp_usb_z);
    usb_cut(esp_usb_z);
    box([sw_x - sw_slot[0] / 2, W / 2 - sw_slot[1] / 2, H - e], [sw_x + sw_slot[0] / 2, W / 2 + sw_slot[1] / 2, H + wall + e]);
    tie_grooves();
}

module lid() difference() {
    union() {
        side_wall(W);
        // locating lip: thin bars that sit just inside the body's walls
        box([2, W - lip_h, H - fit_clr - lip_t], [comb_x0 - 1, W, H - fit_clr]);         // top, front part
        box([comb_x1 + 1, W - lip_h, H - fit_clr - lip_t], [L - 2, W, H - fit_clr]);     // top, rear part
        box([L - fit_clr - lip_t, W - lip_h, 2], [L - fit_clr, W, H - 2]);               // rear
        box([comb_x1 + 2, W - lip_h, fit_clr], [L - 2, W, fit_clr + lip_t]);             // tube floor
        box([fit_clr, W - lip_h, 2], [fit_clr + lip_t, W, H - 2]);                       // head front
        box([2, W - lip_h, -drop + fit_clr], [head_L - 2, W, -drop + fit_clr + lip_t]);  // head bottom
    }
    optic_grooves(W - e, W + g);
    tie_grooves();
}

// Lens sits in the counterbore; plate slides into the side-wall grooves under the mirror
module lens_plate() {
    pw = W + 2 * (g - clr);
    difference() {
        cube([head_L - clr, pw, plate_t]);
        translate([ox - clr / 2, pw / 2, plate_t - lens_seat]) cylinder(d = lens_d + 0.4, h = lens_seat + e);
        translate([ox - clr / 2, pw / 2, -e]) cylinder(d = lens_d - 2 * lens_lip, h = plate_t + 2 * e);
    }
}

// Small prints to check fits before the full body (~30 min total)
module test_fit() {
    // head strip of the body: mirror, acrylic and lens-plate grooves
    translate([0, 0, wall]) rotate([90, 0, 0]) intersection() {
        body();
        box([-wall - e, -wall - e, -drop - wall - e], [head_L + wall + e, 3, H + wall + e]);
    }
    // rear-wall patch: both USB-C cut-outs, printed outside face down
    translate([40 - 8, 40, L + wall]) rotate([0, 90, 0]) intersection() {
        body();
        box([L - 3, -wall - e, 8], [L + wall + e, W, 28]);
    }
    translate([40, -30, 0]) lens_plate();
}

module assembly() {
    color("dimgray") body();
    color("gray", 0.4) translate([0, 25, 0]) lid();   // exploded
    color("silver") translate([clr / 2, -(g - clr), -plate_t]) lens_plate();
    color("lightblue", 0.6) {
        translate([ox, W / 2, mz]) rotate([0, -45, 0]) cube([mirror_L, W, mirror_t], center = true);
        translate([ox, W / 2, az]) rotate([0, 45, 0]) cube([acr_L, W, acr_t], center = true);
    }
    color("white", 0.7) translate([ox, W / 2, -lens_seat]) cylinder(d = lens_d, h = lens_t);
    color("navy") translate([pcb_x - oled_pcb_t / 2, (W - oled_w) / 2, comb_h - comb_slot_d]) cube([oled_pcb_t, oled_w, oled_h]);
    color("gold", 0.8) translate([lipo_x0, 0, 0]) cube(lipo);
    color("green") translate([L - tp[0], usb_y - tp[1] / 2, s1 + shelf_t]) cube([tp[0], tp[1], pcb_t]);
    color("purple") translate([L - esp[0], usb_y - esp[1] / 2, s2 + shelf_t]) cube([esp[0], esp[1], pcb_t]);
}

// Each printable part is placed flat on the bed in its print orientation
if (part == "body")            translate([0, 0, wall]) rotate([90, 0, 0]) body();       // side wall down
else if (part == "lid")        translate([0, 0, W + wall]) rotate([-90, 0, 0]) lid();   // outside face down
else if (part == "lens_plate") lens_plate();
else if (part == "test_fit")   test_fit();
else                           assembly();
