import bpy
from bpy.props import *

bl_info = {
    "name": "uv mat generator",
    "description": "Generate and apply a uv mat for your mesh",
    "author": "Bourez Timothee",
    "blender": (3, 20, 0),
    "category": "UV",
}

class MakeUVMat(bpy.types.Operator):
    bl_idname = "object.generate_uv_material"
    bl_label = "generate UV material"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    img_size : FloatProperty(
        name = 'Grid Resolution',
        description = 'Tiling of the grid',
        default = 1,
        min = 0.25,
        soft_min = 0.25,
    )


#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        
        #START of program
        #print are for debug formatting
        print(' ')
        print('###### NEW EXEC ######')


        #get active object
        so = bpy.context.active_object
        print('current object :',so)

        #this function create or replace given material with new one
        def MakeNewMat(oldMat):
            #remove old mat to ensure "clean" result
            if oldMat is not None:
                oldMat = bpy.data.materials.remove(oldMat)
            
            oldMat = bpy.data.materials.new(name='UVgrid')
            oldMat.use_nodes = True
            
            
            #this section generate image for the material
            #delete similarly named image for clean result
            uvImage = bpy.data.images.get('GeneratedGrid')
            if uvImage is not None:
                print('--> same grid found, deleting it for replacement')
                uvImage = bpy.data.images.remove(uvImage)
                
            #generate new uvGrid image
            print('--> generating grid')
            uvImage = bpy.data.images.new(name='GeneratedGrid', width=1024, height=1024)
            uvImage.source = 'GENERATED'
            uvImage.generated_type = 'UV_GRID'


            #this section make the node tree of the material
            #store node acess
            nodes = oldMat.node_tree.nodes
            links = oldMat.node_tree.links
            material_out = nodes.get('Material Output')
            principled_node = nodes.get('Principled BSDF')
            
            #creating, configuring and linking shader node together
            image_texture = nodes.new(type='ShaderNodeTexImage')
            image_texture.image = uvImage
            link_img_shader = links.new(image_texture.outputs[0],principled_node.inputs[0])
            
            uvMap = nodes.new(type='ShaderNodeUVMap')
            vecMath = nodes.new(type='ShaderNodeVectorMath')
            vecMath.operation = 'MULTIPLY'
            vecMath.inputs[1].default_value[0] = self.img_size
            vecMath.inputs[1].default_value[1] = self.img_size
            vecMath.inputs[1].default_value[2] = self.img_size
            
            link_math_img = links.new(vecMath.outputs[0],image_texture.inputs[0])
            link_map_math = links.new(uvMap.outputs[0],vecMath.inputs[0])

            return oldMat
        #end of NewMat function


        #the following section check for existing material, 
        #if a material exist with same name and is not used, 
        #assume it is not "clean" and replace it
        mat = bpy.data.materials.get('UVgrid')
        so.data.materials.clear()

        if mat is None:
            print('--> similar uv mat not found')
            print('creating a new one')
            
            mat = MakeNewMat(mat)
            so.data.materials.append(mat)
        else:
            if mat.users > 0:
                print('--> a similar mat exist and is used')
                print('using existing one')
                
                so.data.materials.append(mat)
            else:
                print('--> a similar material exist but is not used')
                print('creating a new one')
                
                mat = MakeNewMat(mat)
                so.data.materials.append(mat)


        #END of program
        print('###### END EXEC ######')
        print(' ')
        
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(MakeUVMat.bl_idname, text=MakeUVMat.bl_label)


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(MakeUVMat)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(MakeUVMat)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

#reactivate at the ende

if __name__ == "__main__":
    register()
    # test call
    bpy.ops.object.generate_uv_material()
