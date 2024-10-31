import random
from typing import Optional

import bpy
import numpy as np


def is_blender_4():
    return bpy.app.version >= (4, 0, 0)


def is_blender_4_1():
    return bpy.app.version >= (4, 1, 0)


def add_material(material, model_ob):
    md = model_ob.data
    for i, ob_material in enumerate(md.materials):
        if ob_material.name == material.name:
            return i
    else:
        md.materials.append(material)
        return len(md.materials) - 1


def get_or_create_material(name: str):
    mat = bpy.data.materials.get(name, None)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = [random.uniform(.4, 1) for _ in range(3)] + [1.0]
    return mat


def add_uv_layer(name: str, uv_data: np.ndarray, mesh_data: bpy.types.Mesh,
                 vertex_indices: Optional[np.ndarray] = None,
                 flip_uv: bool = True):
    uv_layer = mesh_data.uv_layers.new(name=name)
    uv_data = uv_data.copy()
    if flip_uv:
        uv_data[:, 1] = 1 - uv_data[:, 1]
    if vertex_indices is None:
        vertex_indices = np.zeros((len(mesh_data.loops, )), dtype=np.uint32)
        mesh_data.loops.foreach_get('vertex_index', vertex_indices)

    uv_layer.data.foreach_set('uv', uv_data[vertex_indices].ravel())


def add_vertex_color_layer(name: str, v_color_data: np.ndarray, mesh_data: bpy.types.Mesh,
                           vertex_indices: Optional[np.ndarray] = None):
    v_color_data = v_color_data.copy()
    if vertex_indices is None:
        vertex_indices = np.zeros((len(mesh_data.loops, )), dtype=np.uint32)
        mesh_data.loops.foreach_get('vertex_index', vertex_indices)

    vertex_colors = mesh_data.vertex_colors.get(name, False) or mesh_data.vertex_colors.new(name=name)
    vertex_colors.data.foreach_set('color', v_color_data[vertex_indices].flatten())


def add_custom_normals(normals: np.ndarray, mesh_data: bpy.types.Mesh):
    mesh_data.polygons.foreach_set("use_smooth", np.ones(len(mesh_data.polygons), np.uint32))
    if not is_blender_4_1():
        mesh_data.use_auto_smooth = True
    mesh_data.normals_split_custom_set_from_vertices(normals)


def add_weights(bone_indices: np.ndarray, bone_weights: np.ndarray, bone_names: list[str], mesh_obj: bpy.types.Object):
    weight_groups = {name: mesh_obj.vertex_groups.new(name=name) for name in bone_names}
    for n, (index_group, weight_group), in enumerate(zip(bone_indices, bone_weights)):
        for index, weight in zip(index_group, weight_group):
            if weight > 0:
                weight_groups[bone_names[index]].add([n], weight, 'REPLACE')
