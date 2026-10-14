# Door Noodle Kick Target

A 3D-printed mount that holds a pool noodle straight out from a closed interior door, at any height, as a kicking target. It needs no tools, no screws and no holes in the door.

You print six parts and add two bungee cords. Hangers clip over the top and under the bottom of the door, the cords run down the door face, and the noodle mount grips the cords wherever you set it.

## How it works

| Part | Qty | What it does |
|---|---|---|
| **Hanger** | 4 | A thin C-clip that hooks over the top edge of the door. The same part, flipped, hooks under the bottom edge. Each has a thin 10 mm loop at one edge for a bungee hook. The loop stands off the door so the hook never touches the paint. |
| **Bungee cords** | 2 runs | Each run goes from a top hanger straight down the door face to the bottom hanger below it. The two runs are 144 mm apart. If one cord isn't long enough, hook two together; the joint can sit anywhere. |
| **Noodle mount** | 1 | A backplate with a 9 cm deep socket for the noodle, ribs that grip the foam, and a peg that fits into the noodle's hollow core. Each side has three capped pegs. The cord weaves through them left, right, left, and friction holds the mount at that height. |
| **Cross pin** | 1 | Pushes through holes in the socket and through the foam, so the noodle can't pull out. |

> **Mount the target on the side the door swings toward.** Kicks then push the door into its stop instead of pulling it open. The thin back leg of each hanger sits on the stop side, where the gap around the door is tightest.

## Measure first

Four measurements decide the fit. The first three are settings at the top of `build.py`; change them if yours differ.

| Measurement | Default | Setting | Notes |
|---|---|---|---|
| Door thickness | 34.9 mm | `DOOR_T` | 1-3/8" is standard for interior doors. Solid doors are often 1-3/4" (44.5 mm). |
| Noodle diameter | 64 mm | `NOODLE_D` | Most noodles are 2.5" (63.5 mm). Jumbo ones are 3 to 4". |
| Gap above the door | at least 2.5 mm | `H_STRAP` | The strip that crosses the top of the door is 2.4 mm thick. |
| Gap under the door | at least 6 mm | | Usually 10 to 19 mm. The bottom hangers sit in this gap. |

## Parts to print

| File | Qty | Size (mm) | Print orientation | Notes |
|---|---|---|---|---|
| `stl/hanger_x4.stl` | 4 | 65 × 87 × 30 | Lying on the C shape, as exported | The layers follow the curve of the C, so the bend can't split along a layer. The hook loop sits on the bed. |
| `stl/noodle_mount.stl` | 1 | 184 × 140 × 96 | Backplate on the bed, socket up | The pin hole has a pointed top and the peg caps have angled undersides, so no supports are needed. |
| `stl/cross_pin.stl` | 1 | 95 × 18 × 12 | On its flat side | The pointed tip pierces the foam. |

All six parts fit on one 256 × 256 mm bed, and none need supports.

### Print settings

- **Material:** PETG is best. It bends instead of snapping, which matters for the hangers. PLA is fine for the mount.
- **Hangers:** 100% infill and 0.2 mm layers. They carry all the cord tension.
- **Mount:** 4 walls, 25 to 30% gyroid infill, and 5 top and bottom layers.
- **Pin:** 100% infill.

### You also need

- A pool noodle. Cut it to about 0.8 to 1 m long, because a full-length noodle droops.
- Bungee cords: enough to reach from the top of the door to the bottom on each side, about 2 m per side. Two 1 m cords hooked together per side is typical.
- Optional: felt pads or painter's tape on the back of the mount and inside the hangers, to protect the door's finish.

## Install

1. **Put on the top hangers.** Open the door and hook two hangers over the top edge, about 144 mm apart, centered where you want the noodle. The thick leg with the loop goes on the target side and the thin leg goes on the stop side.
2. **Put on the bottom hangers.** Turn the other two upside down and slide them under the bottom edge, directly below the top ones. The loops go on the target side again.
3. **Run the cords.** Hold a hook with its curve flat against the door and slip the tip sideways through a top loop, from the open side. Run the cord down the door face and hook it to the bottom loop, joining cords if needed. Stretch it firmly, to about 15 to 25% longer than its relaxed length. Repeat on the other side.
4. **Weave the mount onto the cords.** Hold the mount at the height you want. On each side, press the cord between the pegs so it passes **left of the top peg, right of the middle peg, and left of the bottom peg**. The cord tucks under the peg caps. For more grip, wrap it once all the way around the middle peg.
5. **Put in the noodle.** Twist the noodle into the socket until it reaches the bottom, over the center peg. Push the cross pin through the side holes and through the foam.
6. **Close the door and test it.** Close and latch the door. Start with light kicks and check that the hangers stay in place and the mount stays at its height.

## Changing the height

Lift the cords off the pegs on both sides, slide the mount up or down, and weave the cords back on. It takes under 30 seconds and needs no tools. The usable range is about 20 cm to 1.85 m off the floor.

If the mount slides down when kicked hard, wrap the cord once around the middle peg on both sides, or tighten the cords. Tighter cords grip harder.

## Troubleshooting

- **The door won't latch:** the stop molding (the strip the door closes against) is pinching the thin back leg of the hanger. Set `H_BACK_T` to 2.0, reprint the hangers, or move them along the door to where the gap is looser.
- **The bungee hook won't go into the loop:** the loop is 10 mm thick (`H_EYE_T`) with a 14 mm hole, sized for a hook with a 23 mm opening. Lower `H_EYE_T` if your hooks have a smaller opening.
- **Hollow-core doors:** these work fine. The load goes into the edges of the door, not its thin face.
- **Solid noodle with no hole in the middle:** set `NOODLE_CORE = False`. The socket ribs and the cross pin will hold it.
- **Safety:** kick the noodle, not the mount. The deep socket keeps feet away from the hard plastic.

## Making your own version

All the parts are generated by [`build.py`](build.py). Edit the settings block at the top, then run:

```bash
pip install manifold3d trimesh numpy
python build.py
```

This rewrites the STL files in `stl/`. It also rewrites the 3D preview models (`assembly.glb` and `print_layout.glb`), plus the `.glb.js` copies the guide page loads.

## Files

| Path | What it is |
|---|---|
| `build.py` | Generates all the parts from the settings |
| `stl/` | Files ready to print |
| `kick_target_guide.html` | Build guide with a 3D model you can rotate. Open it through a local web server, for example `python -m http.server`. |
| `assembly.glb`, `print_layout.glb` | 3D previews of the installed system and the print bed |
| `*.glb.js` | Copies of the previews that the guide page loads |

## Status

This design has not been fully tested. The first hanger has been printed and the hook loop was redesigned after testing it with a real bungee hook. How well the cord holds the mount under hard kicks is still an estimate.
