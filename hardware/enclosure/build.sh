#!/bin/sh
# Export every printable part to stl/ plus PNG previews. Run from anywhere.
set -e
cd "$(dirname "$0")"
mkdir -p stl
for p in body lid lens_plate clip test_fit; do
  openscad --hardwarnings -D "part=\"$p\"" -o "stl/$p.stl" hud_enclosure.scad
  openscad -D "part=\"$p\"" --render --autocenter --viewall --imgsize=1000,700 -o "stl/$p.png" hud_enclosure.scad
done
openscad --hardwarnings -D 'part="plate"' -o stl/print_all.stl hud_enclosure.scad
openscad -D 'part="plate"' --render --autocenter --viewall --imgsize=1000,800 -o stl/print_all.png hud_enclosure.scad
openscad --autocenter --viewall --imgsize=1200,800 --camera=0,0,0,60,0,210,0 -o stl/assembly.png hud_enclosure.scad
openscad -D 'part="section"' --autocenter --viewall --imgsize=1200,800 --camera=0,0,0,90,0,0,0 -o stl/section.png hud_enclosure.scad
echo "Done: $(ls stl)"
