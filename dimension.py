import bpy
from mathutils import Vector
import time

# define nove presets de dimensão: (id, label, descrição)
PRESETS = [
    ("D1", "0.080, 0.074, 0.096", "Agua-Gelada - 10sac 16-20g "),
    ("D2", "0.080, 0.073, 0.081", "Cha-Misto-Quad - 10sac 15-16g"),
    ("D3", "0.133, 0.053, 0.060", "Matte - 25sac 30-40g"),
    ("D4", "0.077, 0.057, 0.062", "Cha - 10sac 10g"),
    ("D5", "0.067, 0.052, 0.064", "Boldo - 10sac 10g"),
    ("D6", "0.081, 0.069, 0.096", "Agua-Gelada - 10sac 23-25g"),
    ("D7", "0.102, 0.066, 0.077", "Matte-Natural - 15sac 24g"),
    ("D8", "0.120, 0.070, 0.190", "Terere"),
    ("D9", "0.096, 0.076, 0.163", "Granel"),
    ("D10", "0.096, 0.076, 0.163", "Chimarrao"),
]

# mapeia as chaves para vetores de dimensão alvo
DIM_VALUES = {
    "D1": Vector((0.08, 0.074, 0.096)),  # y e z trocados
    "D2": Vector((0.08, 0.073, 0.081)),
    "D3": Vector((0.133, 0.053, 0.06)),
    "D4": Vector((0.077, 0.057, 0.062)),
    "D5": Vector((0.067, 0.052, 0.064)),
    "D6": Vector((0.081, 0.069, 0.096)),
    "D7": Vector((0.102, 0.066, 0.077)),
    "D8": Vector((0.120, 0.070, 0.190)),
    "D9": Vector((0.096, 0.076, 0.163)),
    "D10": Vector((0.122, 0.063, 0.210)),
}

# operador para ajustar a malha às dimensões selecionadas
class OBJECT_OT_set_mesh_dimensions(bpy.types.Operator):
    bl_idname = "object.set_mesh_dimensions"
    bl_label = "Set Mesh Dimensions"
    bl_description = "Adjust mesh geometry to match preset dimensions, keeping object scale at 1,1,1"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # verifica se o objeto ativo é uma malha
        obj = context.active_object
        return obj is not None and obj.type == 'MESH'

    def execute(self, context):
        # aplica rotação para zerar transformações anteriores
        obj = context.active_object
        bpy.ops.object.auto_align_base()
        time.sleep(0.5)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        # garante que a escala do objeto esteja em 1,1,1
        obj.scale = (1.0, 1.0, 1.0)
        # obtém a malha do objeto
        mesh = obj.data
        # calcula as coordenadas mínima e máxima da bounding box local
        coords = [Vector(corner) for corner in obj.bound_box]
        minc = Vector((min(c.x for c in coords), min(c.y for c in coords), min(c.z for c in coords)))
        maxc = Vector((max(c.x for c in coords), max(c.y for c in coords), max(c.z for c in coords)))
        size = maxc - minc
        # recupera a dimensão alvo com base no preset selecionado
        key = context.scene.dimension_preset_xyz
        target = DIM_VALUES[key]
        # calcula os fatores de escala para cada eixo
        factors = Vector((
            target.x / size.x if size.x != 0 else 1.0,
            target.y / size.y if size.y != 0 else 1.0,
            target.z / size.z if size.z != 0 else 1.0,
        ))
        # aplica a escala nos vértices da malha
        for v in mesh.vertices:
            v.co.x *= factors.x
            v.co.y *= factors.y
            v.co.z *= factors.z
        return {'FINISHED'}

# painel na vista 3d para selecionar o preset e executar o operador
class VIEW3D_PT_dimension_presets(bpy.types.Panel):
    bl_label = "Mesh Dimension Presets"
    bl_idname = "VIEW3D_PT_dimension_presets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    def draw(self, context):
        layout = self.layout
        # propriedade para escolha do preset
        layout.prop(context.scene, "dimension_preset_xyz", text="Preset")
        # botão para aplicar o ajuste de dimensão
        layout.operator("object.set_mesh_dimensions", icon='ARROW_LEFTRIGHT')

# lista de classes para registrar/desregistrar
classes = [OBJECT_OT_set_mesh_dimensions, VIEW3D_PT_dimension_presets]

def register():
    # remove propriedade existente para evitar conflito
    if hasattr(bpy.types.Scene, 'dimension_preset_xyz'):
        delattr(bpy.types.Scene, 'dimension_preset_xyz')
    # registra as classes
    for c in classes:
        bpy.utils.register_class(c)
    # define a enum property no contexto da cena
    bpy.types.Scene.dimension_preset_xyz = bpy.props.EnumProperty(
        name="Dimension Preset",
        description="Choose a mesh dimension preset",
        items=PRESETS,
        default='D1',
    )

def unregister():
    # remove a propriedade antes de desregistrar classes
    if hasattr(bpy.types.Scene, 'dimension_preset_xyz'):
        delattr(bpy.types.Scene, 'dimension_preset_xyz')
    # desregistra as classes em ordem reversa
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

# executa o registro quando o script é rodado diretamente
if __name__ == "__main__":
    register()
