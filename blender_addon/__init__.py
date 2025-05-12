bl_info = {
    "name": "PlaneAnimator",
    "blender": (4, 3, 0),
    "category": "3D View",
}

from . import ui_panel
from .operators import generate_frame

def register():
    ui_panel.register()
    generate_frame.register()

def unregister():
    ui_panel.unregister()
    generate_frame.unregister()
