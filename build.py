"""
Pool-noodle kick target for a standard interior door.

Generates printable STLs (in ./stl) and an assembly preview (assembly.glb).
All dimensions in mm. Edit the PARAMETERS block, then run:

    pip install manifold3d trimesh numpy
    python build.py
"""
import os
import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold, JoinType, set_circular_segments

set_circular_segments(96)

# ----------------------------------------------------------------- PARAMETERS
DOOR_T = 34.9          # door thickness (1-3/8" standard interior; 44.5 for 1-3/4")
DOOR_FIT = 1.0         # clearance added to door thickness inside the hanger
NOODLE_D = 64.0        # pool-noodle outer diameter (measure yours! 2.5" = 63.5)
NOODLE_CORE = True     # True if the noodle has a hollow core -> center spigot
CORE_SPIGOT_D = 18.0   # spigot diameter (noodle cores are ~20-25 mm)

# hanger (over-door / under-door clip)
H_WIDTH = 30.0         # print height of the hanger
H_STRAP = 2.4          # bridge thickness over the door edge (must fit the gap)
H_BACK_T = 2.6         # back leg (stop side) - stays thin, it sits behind the stop
H_BACK_LEN = 45.0
H_FRONT_T = 6.0        # front leg (target side)
H_FRONT_LEN = 85.0
H_EYE_R = 12.5         # outer radius of the hook eye
H_EYE_HOLE = 7.0       # hole radius for the bungee hook
H_EYE_T = 10.0         # eye loop thickness: must be well under the hook's throat (~23 mm)

# mount (noodle socket + cord cleats)
M_W, M_H, M_T = 184.0, 140.0, 6.0   # backplate
SOCK_DEPTH = 90.0                   # socket height above the plate face
SOCK_WALL = 3.5
CLEAT_X = 72.0                      # cleat column offset from center
PEG_R, PEG_H, PEG_PITCH = 8.0, 13.0, 34.0
CAP_R = 11.5
PIN_R, PIN_Z = 4.0, 78.0            # cross pin through socket + noodle

OUT = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------------- helpers
def rect(x0, y0, x1, y1):
    return CrossSection.square([x1 - x0, y1 - y0]).translate([x0, y0])


def circle(r, x=0, y=0):
    return CrossSection.circle(r).translate([x, y])


def paint(tm: trimesh.Trimesh, rgba):
    mat = trimesh.visual.material.PBRMaterial(baseColorFactor=rgba, metallicFactor=0.0,
                                              roughnessFactor=0.7)
    tm.visual = trimesh.visual.TextureVisuals(material=mat)


def to_trimesh(m: Manifold) -> trimesh.Trimesh:
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3],
                           np.asarray(mesh.tri_verts), process=True)


# -------------------------------------------------------------------- HANGER
def hanger() -> Manifold:
    """C-clip profile in XY (x: through door thickness, y: vertical, 0 = door edge),
    extruded H_WIDTH along Z.  Printed lying on this profile -> layer lines follow
    the C, so the bend never splits on a layer line."""
    gap = DOOR_T + DOOR_FIT
    xf = gap                     # inner face of front leg
    xo = gap + H_FRONT_T         # outer face of front leg
    bridge = rect(-H_BACK_T, 0, xo, H_STRAP)
    back = rect(-H_BACK_T, -H_BACK_LEN, 0, H_STRAP)
    front = rect(xf, -H_FRONT_LEN, xo, H_STRAP)
    ey = -H_FRONT_LEN + H_EYE_R
    ex = xo + H_EYE_R - 5
    eye = CrossSection.batch_hull([rect(xf, -H_FRONT_LEN, xo, -H_FRONT_LEN + 34),
                                   circle(H_EYE_R, ex, ey)])
    # small grip nub at the tip of the back leg
    nub = circle(1.2, 0, -H_BACK_LEN + 4)
    prof = CrossSection.batch_boolean([bridge, back, front, eye, nub], manifold3d_op("Add"))
    prof = prof.offset(1.2, JoinType.Round).offset(-1.2, JoinType.Round)   # fillet inside corners
    prof = prof.offset(-0.8, JoinType.Round).offset(0.8, JoinType.Round)   # soften outside edges
    prof = prof - circle(H_EYE_HOLE, ex, ey)
    body = prof.extrude(H_WIDTH)
    # neck the eye down to a thin loop (sitting on the bed) so a J-hook can wrap it;
    # the front leg itself stays full width
    clear = Manifold.cube([3 * H_EYE_R, H_FRONT_LEN, H_WIDTH]).translate(
        [xo + 0.3, -H_FRONT_LEN - 10, H_EYE_T])
    return body - clear


def manifold3d_op(name):
    import manifold3d
    return getattr(manifold3d.OpType, name)


# --------------------------------------------------------------------- MOUNT
def gusset(angle_deg, r_in, r_out, h, t=5.0) -> Manifold:
    tri = CrossSection([[(r_in, 0), (r_out, 0), (r_in, h)]])
    g = tri.extrude(t).translate([0, 0, -t / 2]).rotate([90, 0, 0])
    return g.rotate([0, 0, angle_deg]).translate([0, 0, M_T])


def teardrop_bar_x(r, length) -> Manifold:
    """horizontal hole along X with a 45-degree roof so it prints without support"""
    td = CrossSection.batch_hull([circle(r), circle(0.01, 0, r * 1.414)])
    return td.extrude(length).translate([0, 0, -length / 2]).rotate([90, 0, 0]).rotate([0, 0, 90])


def mount() -> Manifold:
    plate = (rect(-M_W / 2, -M_H / 2, M_W / 2, M_H / 2)
             .offset(-12, JoinType.Round).offset(12, JoinType.Round)).extrude(M_T)

    sock_ir = NOODLE_D / 2 - 0.5
    sock_or = sock_ir + SOCK_WALL
    top = M_T + SOCK_DEPTH
    socket = Manifold.cylinder(SOCK_DEPTH, sock_or).translate([0, 0, M_T])
    bore = Manifold.cylinder(SOCK_DEPTH + 1, sock_ir).translate([0, 0, M_T])
    lead = Manifold.cylinder(6, sock_ir, sock_ir + 2.5).translate([0, 0, top - 5.99])

    parts = [plate, socket]
    for a in (45, 135, 225, 315):
        parts.append(gusset(a, sock_or - 1, 64, 48))
    for a in (90, 270):
        parts.append(gusset(a, sock_or - 1, M_H / 2 - 2, 48))
    body = Manifold.batch_boolean(parts, manifold3d_op("Add")) - bore - lead

    # crush ribs that bite into the foam
    ribs = []
    for i in range(10):
        a = np.radians(i * 36)
        ribs.append(Manifold.cylinder(SOCK_DEPTH - 8, 1.6)
                    .translate([sock_ir * np.cos(a), sock_ir * np.sin(a), M_T]))
    body = Manifold.batch_boolean([body] + ribs, manifold3d_op("Add"))

    if NOODLE_CORE:
        spig_h = 60.0
        r = CORE_SPIGOT_D / 2
        sp = (Manifold.cylinder(spig_h - 6, r).translate([0, 0, M_T])
              + Manifold.cylinder(6, r, r - 4).translate([0, 0, M_T + spig_h - 6]))
        body = body + sp

    # cross-pin hole (above the spigot)
    body = body - teardrop_bar_x(PIN_R + 0.35, M_W).translate([0, 0, M_T + PIN_Z])

    # cord cleats: 3 capped pegs per side, cord weaves L-R-L (S-path)
    for cx in (-CLEAT_X, CLEAT_X):
        for cy in (-PEG_PITCH, 0, PEG_PITCH):
            z0 = M_T
            peg = Manifold.cylinder(PEG_H, PEG_R).translate([cx, cy, z0 - 0.01])
            cone = Manifold.cylinder(CAP_R - PEG_R, PEG_R, CAP_R).translate([cx, cy, z0 + PEG_H])
            cap = Manifold.cylinder(2.5, CAP_R).translate([cx, cy, z0 + PEG_H + CAP_R - PEG_R])
            body = body + peg + cone + cap
    return body


# ----------------------------------------------------------------------- PIN
def pin() -> Manifold:
    L = 2 * (NOODLE_D / 2 + SOCK_WALL) + 12
    shaft = Manifold.cylinder(L, PIN_R).rotate([0, 90, 0])
    tip = Manifold.cylinder(8, PIN_R, 1.2).rotate([0, 90, 0]).translate([L, 0, 0])
    head = Manifold.cylinder(4, 9).rotate([0, 90, 0]).translate([-4, 0, 0])
    p = shaft + tip + head
    flat = PIN_R * 0.8            # print lying down on a flat
    keep = Manifold.cube([L + 40, 40, 40]).translate([-20, -20, -flat])
    return (p ^ keep).translate([0, 0, flat])


# ------------------------------------------------------------------ ASSEMBLY
def export_assembly(hg, mt, path, mount_z=1050.0):
    """Colored GLB of the installed system (Z up, mm) for the 3D viewer."""
    DOOR_W, DOOR_Z0, DOOR_Z1 = 762.0, 15.0, 15.0 + 2032.0
    cx = DOOR_W / 2
    gap = DOOR_T + DOOR_FIT

    def placed(mesh, R, t, color):
        T = np.eye(4); T[:3, :3] = R; T[:3, 3] = t
        m = mesh.copy(); m.apply_transform(T)
        paint(m, color)
        return m

    scene = trimesh.Scene()
    # hangers: local x -> world y (target face at y=0), local y -> world z, local z -> world x
    for top in (True, False):
        for s in (-1, 1):
            R = [[0, 0, 1], [1, 0, 0], [0, 1 if top else -1, 0]]
            t = [cx + s * CLEAT_X - H_EYE_T / 2, -gap, DOOR_Z1 if top else DOOR_Z0]
            if not top:   # mirrored copy needs its winding flipped
                m = placed(hg, R, t, [232, 128, 58, 255]); m.invert()
            else:
                m = placed(hg, R, t, [232, 128, 58, 255])
            scene.add_geometry(m, node_name=f"hanger_{'top' if top else 'bottom'}_{s:+d}")
    scene.add_geometry(placed(mt, [[-1, 0, 0], [0, 0, 1], [0, 1, 0]], [cx, 0, mount_z],
                              [58, 141, 232, 255]), node_name="noodle_mount")

    door = trimesh.creation.box(extents=[DOOR_W, DOOR_T, DOOR_Z1 - DOOR_Z0])
    door.apply_translation([cx, -DOOR_T / 2, (DOOR_Z0 + DOOR_Z1) / 2])
    paint(door, [222, 210, 190, 255])
    scene.add_geometry(door, node_name="door")

    noodle = trimesh.creation.cylinder(radius=NOODLE_D / 2, segment=[[cx, M_T + 2, mount_z],
                                                                      [cx, 1200, mount_z]])
    paint(noodle, [80, 200, 90, 255])
    scene.add_geometry(noodle, node_name="pool_noodle")

    eye_y = H_FRONT_T + H_EYE_R - 5
    eye_dz = H_FRONT_LEN - H_EYE_R
    peg_y = M_T + PEG_H / 2
    off = PEG_R + 4.5
    for s in (-1, 1):
        x = cx + s * CLEAT_X
        pts = [(x, eye_y, DOOR_Z1 - eye_dz), (x, 6, mount_z + M_H / 2 + 30),
               (x - off, peg_y, mount_z + PEG_PITCH), (x + off, peg_y, mount_z),
               (x - off, peg_y, mount_z - PEG_PITCH), (x, 6, mount_z - M_H / 2 - 30),
               (x, eye_y, DOOR_Z0 + eye_dz)]
        for i, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
            c = trimesh.creation.cylinder(radius=4.5, segment=[a, b], sections=12)
            paint(c, [30, 30, 30, 255])
            scene.add_geometry(c, node_name=f"bungee_{s:+d}_{i}")
    scene.export(path)


def export_print_layout(tms, path):
    """Parts in print orientation on a 256 x 256 mm bed (Z up, mm)."""
    scene = trimesh.Scene()
    bed = trimesh.creation.box(extents=[256, 256, 1])
    bed.apply_translation([0, 0, -0.5])
    paint(bed, [70, 74, 82, 255])
    scene.add_geometry(bed, node_name="bed")
    spots = {"noodle_mount": [(0, 58)],
             "hanger_x4": [(-94.5, -82), (-31.5, -82), (31.5, -82), (94.5, -82)],
             "cross_pin": [(0, -26)]}
    colors = {"noodle_mount": [58, 141, 232, 255], "hanger_x4": [232, 128, 58, 255],
              "cross_pin": [240, 200, 60, 255]}
    for name, xy in spots.items():
        for i, (x, y) in enumerate(xy):
            m = tms[name].copy()
            c = (m.bounds[0] + m.bounds[1]) / 2
            m.apply_translation([x - c[0], y - c[1], -m.bounds[0][2]])
            paint(m, colors[name])
            scene.add_geometry(m, node_name=f"{name}_{i}")
    scene.export(path)


# ---------------------------------------------------------------------- MAIN
if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "stl"), exist_ok=True)
    parts = {"hanger_x4": hanger(), "noodle_mount": mount(), "cross_pin": pin()}
    tms = {}
    for name, m in parts.items():
        tm = to_trimesh(m)
        assert tm.is_watertight, name
        tm.export(os.path.join(OUT, "stl", f"{name}.stl"))
        tms[name] = tm
        ext = tm.bounds[1] - tm.bounds[0]
        print(f"{name:14s} {ext[0]:6.1f} x {ext[1]:6.1f} x {ext[2]:6.1f} mm  "
              f"vol {tm.volume / 1000:6.1f} cm3")
    export_assembly(tms["hanger_x4"], tms["noodle_mount"],
                    os.path.join(OUT, "assembly.glb"))
    export_print_layout(tms, os.path.join(OUT, "print_layout.glb"))
    # base64 copies for the web viewer (kick_target_guide.html)
    import base64
    for n in ("assembly", "print_layout"):
        with open(os.path.join(OUT, f"{n}.glb"), "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        with open(os.path.join(OUT, f"{n}.glb.js"), "w") as f:
            f.write(f"window.MODELS=window.MODELS||{{}};window.MODELS['{n}']='{b64}';\n")
    print("done")
