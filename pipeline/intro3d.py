"""3D phone intro for 403 UNLOCKED (Blender, free). Usage:
  blender -b -P pipeline/intro3d.py -- <screen_image.jpg> <out_dir> [seconds]
Renders PNG frames 1080x1920 into out_dir: a glossy phone spins in under neon rim lights, then flies
toward the camera until its screen (the video's title card) fills the frame -> cut straight into the video.
"""
import bpy, sys, math, os

argv = sys.argv[sys.argv.index("--") + 1:]
screen_img, out_dir = argv[0], argv[1]
secs = float(argv[2]) if len(argv) > 2 else 2.6
FPS = 30; N = int(secs * FPS)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 20; sc.cycles.use_denoising = False; sc.render.resolution_percentage = 50
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
sc.render.image_settings.file_format = "PNG"; sc.render.filepath = os.path.join(out_dir, "f_")
sc.view_settings.view_transform = "Filmic" if "Filmic" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Standard"

# world: deep navy
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.015, 0.025, 0.07, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.0

PH_W, PH_H, PH_D = 0.75, 1.6, 0.08   # phone body (metres), aspect ~ 9:19.5
# body
bpy.ops.mesh.primitive_cube_add(size=1); body = bpy.context.object; body.name = "phone"
body.scale = (PH_W, PH_H, PH_D); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bev = body.modifiers.new("bev", "BEVEL"); bev.width = 0.035; bev.segments = 8
bpy.ops.object.shade_smooth()
mb = bpy.data.materials.new("body"); mb.use_nodes = True; p = mb.node_tree.nodes["Principled BSDF"]
p.inputs["Base Color"].default_value = (0.02, 0.02, 0.025, 1); p.inputs["Metallic"].default_value = 0.9; p.inputs["Roughness"].default_value = 0.22
body.data.materials.append(mb)

# screen: emissive image, 9:16
SW, SH = PH_W * 0.92, PH_W * 0.92 * 16 / 9
bpy.ops.mesh.primitive_plane_add(size=1); scr = bpy.context.object; scr.name = "screen"
scr.scale = (SW, SH, 1); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); scr.location = (0, 0, PH_D / 2 + 0.003)
ms = bpy.data.materials.new("screen"); ms.use_nodes = True; nt = ms.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(screen_img)
em = nt.nodes.new("ShaderNodeEmission"); em.inputs[1].default_value = 1.15
out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(tex.outputs[0], em.inputs[0]); nt.links.new(em.outputs[0], out.inputs[0])
scr.data.materials.append(ms)
scr.parent = body

def area(name, loc, rot, color, power, size):
    l = bpy.data.lights.new(name, "AREA"); l.color = color; l.energy = power; l.size = size
    o = bpy.data.objects.new(name, l); o.location = loc; o.rotation_euler = rot; sc.collection.objects.link(o)
area("rimG", (-2.2, 1.5, 1.2), (math.radians(60), math.radians(-50), 0), (0.1, 1.0, 0.45), 900, 1.2)   # neon green
area("rimC", (2.2, -1.0, 1.4), (math.radians(60), math.radians(50), 0), (0.1, 0.8, 1.0), 900, 1.2)    # cyan
area("key", (0, -3, 4), (math.radians(35), 0, 0), (1, 1, 1), 250, 3)

# camera
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 50
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0, 0, 6.2); cam.rotation_euler = (0, 0, 0)
# depth of field for a premium look
cam_d.dof.use_dof = True; cam_d.dof.focus_object = body; cam_d.dof.aperture_fstop = 2.8

# animation: spin in (frames 1..60%), settle, then fly so the screen fills the frame (last 30%)
def kf(obj, f, loc=None, rot=None):
    if loc is not None: obj.location = loc; obj.keyframe_insert("location", frame=f)
    if rot is not None: obj.rotation_euler = rot; obj.keyframe_insert("rotation_euler", frame=f)
f1, f2, f3 = 1, int(N * 0.62), N
kf(body, f1, (0, -0.6, -1.5), (math.radians(-25), math.radians(-200), math.radians(-12)))
kf(body, f2, (0, 0, 0), (math.radians(-8), math.radians(-8), math.radians(2)))
kf(body, f3, (0, 0, 0), (0, 0, 0))
# camera: distance where the 9:16 screen exactly fills the 9:16 frame (sensor 36mm, vertical fit)
fill_z = PH_D / 2 + SH * cam_d.lens / cam_d.sensor_width   # sensor_fit AUTO -> 36mm spans the long (vertical) side
kf(cam, f1, (0, 0, 6.2)); kf(cam, f2, (0, 0, 5.4)); kf(cam, f3, (0, 0, fill_z * 0.985))
for o in (body, cam):
    for fc in o.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation = "BEZIER"; k.easing = "EASE_IN_OUT"
bpy.ops.render.render(animation=True)
