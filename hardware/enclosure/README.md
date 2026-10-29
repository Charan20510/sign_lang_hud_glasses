# HUD display-unit enclosure (3D print)

Parametric OpenSCAD model of the glasses display unit. It replaces the foam-board panels from
`files/hud_glasses_drawings.pdf` and uses the same internal sizes (95 × 29 × 30 mm tube, 25 mm optics head dropping to 60 mm).

![assembly](stl/assembly.png)

## Files
| File | What |
|---|---|
| `hud_enclosure.scad` | the model; all sizes are variables at the top |
| `build.sh` | exports every part to `stl/*.stl` + `stl/*.png` |
| `stl/body.stl` | side wall + top/rear/floor/front walls, OLED comb, board shelves |
| `stl/lid.stl` | other side wall with locating lip |
| `stl/lens_plate.stl` | holds the 25 mm lens under the mirror |
| `stl/test_fit.stl` | small fit-check prints (head strip, USB-C patch, lens plate) |

Rebuild after changing any value:
```bash
sh hardware/enclosure/build.sh
```
The render prints the optics check (`u = 40 mm, image ≈ 360 mm away, ×9`) and the mirror/acrylic cut sizes.
It stops with an error if parts collide (e.g. `acrylic hits lens plate`).

## 1. Measure first (calipers), then update the variables
| Part | Variable | Default |
|---|---|---|
| LiPo 500 mAh | `lipo` | 35 × 26 × 7 |
| TP4056 Type-C board | `tp`, `tp_h` | 28 × 17.5, 5.5 high |
| ESP32-C3 SuperMini | `esp` | 22.5 × 18 |
| OLED module | `oled_w`, `oled_h`, `oled_pcb_t` | 27.3 × 27.8, 1.2 |
| Mirror glass thickness | `mirror_t` | 2 |
| Lens centre thickness | `lens_t` | 5 |

## 2. Cut list
- Mirror: **25 × 30 mm** (fits 29–30.4 wide), thin glass.
- Acrylic: **30 × 30 mm**, 1 mm clear.
- The parts slide into 1 mm grooves in both side walls, so they must be a bit wider than the 29 mm inside.

## 3. Print settings (FDM, college lab)
- Matte **black** PLA or PETG, so the inside needs no paint.
- 0.4 mm nozzle, 0.2 mm layers, 3 walls, 20 % infill, **no supports**.
- Each STL is already placed in print orientation: body side-wall down, lid outside-face down, lens plate flat.
- Print `test_fit.stl` first (~30 min). If the mirror, acrylic, lens plate or USB-C plug fits too tight or too loose, change `clr` (default 0.3) and rebuild.

## 4. Assembly
1. Body on the table, open side up.
2. Drop the lens into the lens plate, then slide the plate into its groove under the mirror.
3. Put the mirror (`/` slot) and acrylic (`\` slot) into their 45° grooves.
4. Put the LiPo on the floor at the rear, the TP4056 on the lower shelf and the ESP32-C3 on the upper shelf. Push both USB-C ports into the rear-wall holes. Fix with double-sided foam tape.
5. Push the slide switch up into the top-wall slot and fix it with hot glue. Run the wires along the open gap on the lid side.
6. Put the OLED (screen facing the mirror) into the **middle** comb slot. Power it on and look through the acrylic. If the text is blurry, try the front or rear slot (u = 37 / 43 mm).
7. Press the lid on. The lip locates it.
8. Zip-tie or velcro the unit to the glasses arm using the two grooves around the tube. The ties also hold the lid shut.

## Notes
- Lens-to-acrylic distance is 16 mm, not the drawing's 15 mm, so the 30 mm acrylic clears the lens plate. Focus depends only on u (OLED → mirror → lens), so it is unchanged.
- The lower head is open front and back (see-through path). The bar at the bottom only makes it stiffer.
- The lens (Ø25) is as wide as the head, so its seat opens at the front and back of the plate. The front wall and the tube floor hold it in place.
