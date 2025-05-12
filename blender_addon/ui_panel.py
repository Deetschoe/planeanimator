import bpy

class PLANEANIMATOR_PT_MainPanel(bpy.types.Panel):
    bl_label = "PlaneAnimator"
    bl_idname = "PLANEANIMATOR_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PlaneAnimator'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "pa_prompt")
        layout.prop(context.scene, "pa_style")
        layout.prop(context.scene, "pa_use_reference")
        layout.prop(context.scene, "pa_quality")
        layout.prop(context.scene, "pa_size")
        layout.prop(context.scene, "pa_transparent")
        layout.prop(context.scene, "pa_output_folder")
        layout.prop(context.scene, "pa_offset")
        layout.operator("planeanimator.generate_frame")

def register():
    bpy.utils.register_class(PLANEANIMATOR_PT_MainPanel)
    bpy.types.Scene.pa_prompt = bpy.props.StringProperty(name="Prompt", default="")
    bpy.types.Scene.pa_style = bpy.props.EnumProperty(
        name="Style",
        items=[("Anime", "Anime", ""), ("Realism", "Realism", ""), ("Cartoon", "Cartoon", "")]
    )
    bpy.types.Scene.pa_use_reference = bpy.props.BoolProperty(name="Use Camera Reference", default=True)
    bpy.types.Scene.pa_quality = bpy.props.EnumProperty(
        name="Quality",
        items=[("auto", "Auto", ""), ("low", "Low", ""), ("medium", "Medium", ""), ("high", "High", "")],
        default="medium"
    )
    bpy.types.Scene.pa_size = bpy.props.EnumProperty(
        name="Size",
        items=[("auto", "Auto", ""), ("1024x1024", "1024x1024", ""), ("1024x1536", "Portrait", ""), ("1536x1024", "Landscape", "")],
        default="1024x1024"
    )
    bpy.types.Scene.pa_transparent = bpy.props.BoolProperty(name="Transparent Background", default=True)
    bpy.types.Scene.pa_output_folder = bpy.props.StringProperty(name="Save Folder", subtype='DIR_PATH')
    bpy.types.Scene.pa_offset = bpy.props.FloatProperty(name="Z Offset", default=-3.0)

def unregister():
    bpy.utils.unregister_class(PLANEANIMATOR_PT_MainPanel)
    del bpy.types.Scene.pa_prompt
    del bpy.types.Scene.pa_style
    del bpy.types.Scene.pa_use_reference
    del bpy.types.Scene.pa_quality
    del bpy.types.Scene.pa_size
    del bpy.types.Scene.pa_transparent
    del bpy.types.Scene.pa_output_folder
    del bpy.types.Scene.pa_offset
