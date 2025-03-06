bl_info = {
    "name": "Reset 3D Cursor Rotation",
    "author": "Jatix",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D",
    "description": "Resets the 3D cursor's rotation with customizable shortcut",
    "category": "3D View",
}

import bpy
from mathutils import Euler

class ResetCursorRotation(bpy.types.Operator):
    """Reset 3D Cursor Rotation"""
    bl_idname = "view3d.reset_cursor_rotation"
    bl_label = "Reset 3D Cursor Rotation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.cursor.rotation_euler = Euler((0, 0, 0), 'XYZ')
        return {'FINISHED'}

class ResetCursorRotationPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    shortcut_key: bpy.props.StringProperty(
        name="Shortcut Key",
        default='D',
        description="Set the keyboard shortcut key"
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Set shortcut in the Keymap section below:")
        layout.label(text="After changing, save preferences and restart Blender")

addon_keymaps = []

def register():
    bpy.utils.register_class(ResetCursorRotation)
    bpy.utils.register_class(ResetCursorRotationPreferences)
    
    # Keymap registration
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        
        # Get shortcut key from preferences
        prefs = bpy.context.preferences.addons[__name__].preferences
        kmi = km.keymap_items.new(
            ResetCursorRotation.bl_idname,
            type=prefs.shortcut_key,
            value='PRESS'
        )
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    bpy.utils.unregister_class(ResetCursorRotation)
    bpy.utils.unregister_class(ResetCursorRotationPreferences)

if __name__ == "__main__":
    register()