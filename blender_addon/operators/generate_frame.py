import bpy
import os
import requests
from mathutils import Vector
from datetime import datetime

class PLANEANIMATOR_OT_GenerateFrame(bpy.types.Operator):
    bl_idname = "planeanimator.generate_frame"
    bl_label = "Generate Image Frame"

    def execute(self, context):
        scene = context.scene
        folder = bpy.path.abspath(scene.pa_output_folder)
        os.makedirs(folder, exist_ok=True)

        prompt = scene.pa_prompt
        style = scene.pa_style
        quality = scene.pa_quality
        size = scene.pa_size
        use_ref = scene.pa_use_reference
        transparent = scene.pa_transparent
        offset = scene.pa_offset

        # Enhance style-specific phrasing
        style_map = {
            "Anime": "2D anime-style drawing",
            "Realism": "highly detailed realistic based on real life",
            "Cartoon": "cartoon 2d style"
        }
        style_text = style_map.get(style, style)

        # Add ref prompt if enabled
        ref_instruction = " Use the provided camera reference image as a guide." if use_ref else ""
        full_prompt = f"{style_text}, clean white transparent background.{ref_instruction} {prompt}"

        # Render unique ref image if needed
        ref_path = None
        if use_ref:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ref_path = os.path.join(folder, f"ref_{timestamp}.png")
            render = scene.render
            orig_path = render.filepath
            render.filepath = ref_path
            bpy.ops.render.opengl(write_still=True)
            render.filepath = orig_path

            if not os.path.exists(ref_path):
                self.report({'ERROR'}, "Failed to save reference image.")
                return {'CANCELLED'}

        try:
            # Build request
            data = {
                "prompt": full_prompt,
                "size": size,
                "quality": quality,
                "background": "transparent" if transparent else "opaque",
                "output_format": "png",
                "save_folder": folder
            }
            files = {"ref_image": open(ref_path, "rb")} if ref_path else {}

            res = requests.post("http://127.0.0.1:5001/generate", data=data, files=files).json()

            if res["status"] != "success":
                self.report({'ERROR'}, res["message"])
                return {'CANCELLED'}

            image_path = res["image_path"]
            image = bpy.data.images.load(image_path)

            bpy.ops.mesh.primitive_plane_add(size=2.0)
            plane = context.active_object
            cam = scene.camera
            if cam:
                plane.location = cam.location + cam.matrix_world.to_quaternion() @ Vector((0, 0, offset))
                plane.rotation_euler = cam.rotation_euler

            mat = bpy.data.materials.new(name="PA_Material")
            mat.use_nodes = True
            bsdf_nodes = mat.node_tree.nodes
            bsdf_links = mat.node_tree.links

            for node in bsdf_nodes:
                bsdf_nodes.remove(node)

            tex_image = bsdf_nodes.new("ShaderNodeTexImage")
            tex_image.image = image

            emission = bsdf_nodes.new("ShaderNodeEmission")
            transparent_bsdf = bsdf_nodes.new("ShaderNodeBsdfTransparent")
            math_node = bsdf_nodes.new("ShaderNodeMath")
            math_node.operation = 'GREATER_THAN'
            math_node.inputs[1].default_value = 0.1

            mix_shader = bsdf_nodes.new("ShaderNodeMixShader")
            output = bsdf_nodes.new("ShaderNodeOutputMaterial")

            bsdf_links.new(tex_image.outputs["Alpha"], math_node.inputs[0])
            bsdf_links.new(math_node.outputs[0], mix_shader.inputs[0])
            bsdf_links.new(tex_image.outputs["Color"], emission.inputs["Color"])
            bsdf_links.new(emission.outputs["Emission"], mix_shader.inputs[2])
            bsdf_links.new(transparent_bsdf.outputs["BSDF"], mix_shader.inputs[1])
            bsdf_links.new(mix_shader.outputs[0], output.inputs["Surface"])

            plane.data.materials.append(mat)

        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        return {'FINISHED'}

def register():
    bpy.utils.register_class(PLANEANIMATOR_OT_GenerateFrame)

def unregister():
    bpy.utils.unregister_class(PLANEANIMATOR_OT_GenerateFrame)
