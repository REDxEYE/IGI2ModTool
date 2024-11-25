from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum

import numpy as np

from igi2cs.file_utils import Buffer
from igi2cs.loop_file import LoopFile


class UnsupportedModelType(Exception):
    pass


class InvalidModelType(Exception):
    pass


class ModelType(IntEnum):
    StaticModel = 0
    SkinnedModel = 1
    MODEL2 = 2
    LightmappedModel = 3


class DateTime(datetime):
    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return DateTime(
            buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
            buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
            buffer.read_uint32(),
        )


@dataclass(slots=True)
class Vector3:
    x: float
    y: float
    z: float

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return Vector3(buffer.read_float(), buffer.read_float(), buffer.read_float())

    def to_list(self):
        return [self.x, self.y, self.z]


@dataclass(slots=True)
class Sphere:
    pos: Vector3
    radius: float

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return Sphere(Vector3(buffer.read_float(), buffer.read_float(), buffer.read_float()), buffer.read_float())


@dataclass
class MeshInfo:
    face_count: int
    vertex_count: int
    buffer_size: int

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return MeshInfo(buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32())


@dataclass(slots=True)
class ModelInfo:
    version: float
    creation_type: DateTime
    model_type: ModelType
    unk: tuple[int, int, int]
    spheres: tuple[Sphere, Sphere, Sphere]

    render_mesh_info: MeshInfo
    collision_mesh_info: MeshInfo

    field_74: float
    field_80: int
    attachment_count: int
    field_84: int
    field_86: int
    glow_count: int
    bone_count: int
    field_8C: int
    field_90: int
    field_94: int
    field_98: int
    field_9C: int
    field_A0: int
    field_A4: int
    field_A8: int
    field_00: int
    field_001: int

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return ModelInfo(buffer.read_float(), DateTime.from_buffer(buffer), ModelType(buffer.read_uint32()),
                         buffer.read_fmt("3i"),
                         (Sphere.from_buffer(buffer), Sphere.from_buffer(buffer), Sphere.from_buffer(buffer)),
                         MeshInfo.from_buffer(buffer), MeshInfo.from_buffer(buffer),
                         buffer.read_float(), buffer.read_uint16(), buffer.read_uint16(), buffer.read_uint16(),
                         buffer.read_uint16(), buffer.read_uint16(), buffer.read_uint16(),
                         buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
                         buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
                         buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
                         buffer.read_uint32()
                         )


@dataclass(slots=True)
class RenderMeshHeader:
    type: int
    dword0: int
    lightmap_count: int
    face_count: int
    face_group_count: int
    bone_related_0: int
    bone_related_1: int
    vertex_count: int
    dword14: int
    dword18: int
    dword1c: int
    dword20: int
    dword24: int
    dword28: int

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        size = buffer.size()
        if size == 44:
            return RenderMeshHeader(44, buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
                                    buffer.read_uint32(),
                                    0, 0,
                                    buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
                                    buffer.read_uint32(),
                                    buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32()
                                    )
        elif size == 40:
            return RenderMeshHeader(40, 0, buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
                                    buffer.read_uint32(),
                                    buffer.read_uint32(), buffer.read_uint32(),
                                    buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
                                    buffer.read_uint32(),
                                    0, 0
                                    )
        elif size == 36:
            return RenderMeshHeader(36, buffer.read_uint32(), 0, buffer.read_uint32(), buffer.read_uint32(), 0, 0,
                                    buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
                                    buffer.read_uint32(),
                                    buffer.read_uint32(), 0, 0)


@dataclass(slots=True)
class CollisionMeshHeader:
    face_count: int
    vertex_count: int
    material_count: int
    sphere_count: int
    face_ptr: int
    vertex_ptr: int
    materials_ptr: int
    sphere_ptr: int
    face_2_count: int
    vertex_2_count: int
    material_2_count: int
    sphere_2_count: int
    face_2_ptr: int
    vertex_2_ptr: int
    materials_2_ptr: int
    sphere_2_ptr: int

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return CollisionMeshHeader(*buffer.read_fmt("16I"))


@dataclass(slots=True)
class ShadowMeshHeader:
    face_offset: int
    vertex_offset: int
    edge_offset: int
    face_count: int
    vertex_count: int
    edge_count: int
    unk: int

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return ShadowMeshHeader(*buffer.read_fmt("7I"))


@dataclass(slots=True)
class FaceGroup:
    transparency: int
    shininess: int
    unk0: int
    unk1: int
    scaled_vertex_sum: Vector3
    index_offset: int
    face_count: int
    vertex_offset: int
    vertex_count: int

    @classmethod
    def from_buffer(cls, buffer: Buffer, model_type: ModelType):
        if model_type == ModelType.SkinnedModel or model_type == ModelType.StaticModel:
            return SkinnedFaceGroup.from_buffer(buffer, model_type)
        elif model_type == ModelType.LightmappedModel:
            return LightmapFaceGroup.from_buffer(buffer, model_type)
        else:
            raise NotImplementedError("Unsupported model type: {model_type}")


@dataclass(slots=True)
class SkinnedFaceGroup(FaceGroup):
    diffuse_texture: int
    bump_texture: int
    reflection_texture: int
    reflection_scale: int
    bump_scale: int

    @classmethod
    def from_buffer(cls, buffer: Buffer, model_type: ModelType):
        assert model_type == ModelType.SkinnedModel or model_type == ModelType.StaticModel
        return SkinnedFaceGroup(buffer.read_uint8(), buffer.read_uint8(), buffer.read_uint8(), buffer.read_uint8(),
                                Vector3.from_buffer(buffer), buffer.read_uint16(), buffer.read_uint16(),
                                buffer.read_uint16(), buffer.read_uint16(), buffer.read_int16(), buffer.read_int16(),
                                buffer.read_int16(), buffer.read_uint8(), buffer.read_uint8())


@dataclass(slots=True)
class LightmapFaceGroup(FaceGroup):
    diffuse_texture: int
    bump_texture: int

    @classmethod
    def from_buffer(cls, buffer: Buffer, model_type: ModelType):
        assert model_type == ModelType.LightmappedModel
        return LightmapFaceGroup(buffer.read_uint8(), buffer.read_uint8(), buffer.read_uint8(), buffer.read_uint8(),
                                 Vector3.from_buffer(buffer), buffer.read_uint16(), buffer.read_uint16(),
                                 buffer.read_uint16(), buffer.read_uint16(), buffer.read_int16(), buffer.read_int16())


@dataclass(slots=True)
class Bone:
    name: str
    pos: Vector3
    parent_id: int


@dataclass(slots=True)
class Attachment:
    name: str
    pos: Vector3
    rotMat: list[float]
    unk: int
    bone_id: int

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return Attachment(buffer.read_ascii_string(16), Vector3.from_buffer(buffer),
                          buffer.read_fmt("9f"),
                          buffer.read_uint32(), buffer.read_uint32())


@dataclass(slots=True)
class RenderMeshData:
    mesh_header: RenderMeshHeader
    faces: np.ndarray = field(repr=False)
    vertices: np.ndarray = field(repr=False)
    primitives: list[SkinnedFaceGroup] = field(default_factory=list)


CollisionSphereDtype = np.dtype([
    ("pos", np.float32, (3,)),
    ("radius", np.float32, (1,)),
    ("id", np.int16, (1,)),
    ("unk1", np.uint16, (1,)),
    ("unk2", np.uint16, (1,)),
    ("parent_id", np.int16, (1,)),
])
CollisionVertexDtype = np.dtype([
    ("pos", np.float32, (3,)),
    ("uv", np.float32, (2,))
])
CollisionFaceDtype = np.dtype([
    ("face", np.uint16, (3,)),
    ("unk", np.uint16, (3,))
])


@dataclass(slots=True)
class CollisionMeshData:
    mesh_header: CollisionMeshHeader
    spheres: np.ndarray[CollisionSphereDtype]
    faces: np.ndarray[CollisionFaceDtype]
    vertices: np.ndarray[CollisionVertexDtype]


ShadowFaceDtype = np.dtype([
    ("face", np.uint32, (3,)),
    ("edge_flags", np.uint32, (1,)),
    ("normal", np.float32, (3,)),
])


@dataclass(slots=True)
class ShadowMeshData:
    mesh_header: ShadowMeshHeader
    faces: np.ndarray[ShadowFaceDtype]
    vertices: np.ndarray[np.float32]
    edges: np.ndarray[np.uint32]


class MefModel:
    def __init__(self, buffer: Buffer):
        loop_file = LoopFile(buffer, flip_ident=True)

        self.model_info: ModelInfo | None = None
        self.render_mesh_data: RenderMeshData | None = None
        self.collision_mesh_data: CollisionMeshData | None = None
        self.shadow_mesh_data: ShadowMeshData | None = None
        self.bones: list[Bone] = []
        self.attachments: list[Attachment] = []

        while loop_file:
            chunk = loop_file.next_chunk()
            if chunk.ident == "MESH":
                self.model_info = ModelInfo.from_buffer(chunk.buffer)
            elif chunk.ident == "HIER":
                child_counts = [chunk.buffer.read_uint8() for _ in range(self.model_info.bone_count)]
                chunk.buffer.align(4)
                bone_positions = [Vector3.from_buffer(chunk.buffer) for _ in range(self.model_info.bone_count)]
                name_chunk = loop_file.expect_chunk("BNAM")
                bone_names = [name_chunk.buffer.read_ascii_string(16) for _ in range(self.model_info.bone_count)]
                bone_queue = []

                def create_bone(parent_id: int, name: str, position: Vector3, child_count: int):
                    bone = Bone(name, position, parent_id)
                    next_parent_id = len(self.bones)
                    self.bones.append(bone)
                    counts = [child_counts.pop(0) for _ in range(child_count)]
                    names = [bone_names.pop(0) for _ in range(child_count)]
                    positions = [bone_positions.pop(0) for _ in range(child_count)]
                    for count, name, position in zip(counts, names, positions):
                        bone_queue.append((next_parent_id, name, position, count))

                bone_queue.append((-1, bone_names.pop(0), bone_positions.pop(0), child_counts.pop(0)))
                while bone_queue:
                    create_bone(*bone_queue.pop(0))
            elif chunk.ident == "ATTA":
                for _ in range(self.model_info.attachment_count):
                    self.attachments.append(Attachment.from_buffer(chunk.buffer))
            elif chunk.ident == "RD3D":
                assert self.render_mesh_data is None, "Mesh already exist! Report this!"
                render_mesh_info = RenderMeshHeader.from_buffer(chunk.buffer)
                face_chunk = loop_file.expect_chunk("FACE")
                faces = np.frombuffer(face_chunk.buffer.data, np.uint16)

                rend_chunk = loop_file.expect_chunk("REND")
                render_info = [FaceGroup.from_buffer(rend_chunk.buffer, self.model_info.model_type) for _ in
                               range(render_mesh_info.face_group_count)]

                vert_chunk = loop_file.expect_chunk("VRTX")
                if self.model_info.model_type == ModelType.StaticModel:
                    dtype = np.dtype([
                        ("pos", np.float32, (3,)),
                        ("normal", np.float32, (3,)),
                        ("uv0", np.float32, (2,))
                    ])
                elif self.model_info.model_type == ModelType.SkinnedModel:
                    dtype = np.dtype([
                        ("pos", np.float32, (3,)),
                        ("normal", np.float32, (3,)),
                        ("uv0", np.float32, (2,)),
                        ("weight", np.float32, (1,)),
                        ("index", np.ushort, (1,)),
                        ("bone_id", np.ushort, (1,))
                    ])
                elif self.model_info.model_type == ModelType.LightmappedModel:
                    dtype = np.dtype([
                        ("pos", np.float32, (3,)),
                        ("uv0", np.float32, (2,)),
                        ("uv1", np.float32, (2,))
                    ])
                else:
                    raise Exception("Unknown model type")

                vertices = np.frombuffer(vert_chunk.buffer.data, dtype)
                # if render_stat.type == 44:
                #     lightmap_chunk = loop_file.expect_chunk("LTMP")
                self.render_mesh_data = RenderMeshData(render_mesh_info, faces, vertices, render_info)
                del vert_chunk, face_chunk, rend_chunk
            elif chunk.ident == "CMSH":
                collision_mesh_info = CollisionMeshHeader.from_buffer(chunk.buffer)
                collision_vertices_chunk = loop_file.expect_chunk("CVTX")
                collision_faces_chunk = loop_file.expect_chunk("CFCE")
                collision_materials_chunk = loop_file.expect_chunk("CMAT")
                collision_spheres_chunk = loop_file.expect_chunk("CSPH")

                collision_vertices = np.frombuffer(collision_vertices_chunk.buffer.data, CollisionVertexDtype)
                collision_faces = np.frombuffer(collision_faces_chunk.buffer.data, CollisionFaceDtype)
                collision_spheres = np.frombuffer(collision_spheres_chunk.buffer.data, CollisionSphereDtype)
                self.collision_mesh_data = CollisionMeshData(collision_mesh_info, collision_spheres, collision_faces,
                                                             collision_vertices)
                del collision_vertices_chunk, collision_faces_chunk, collision_spheres_chunk
            elif chunk.ident == "SMES":
                shadow_mesh = ShadowMeshHeader.from_buffer(chunk.buffer)

                vertex_chunk = loop_file.expect_chunk("SVTX")
                face_chunk = loop_file.expect_chunk("SFAC")
                edge_chunk = loop_file.expect_chunk("EDGE")

                vertices = np.frombuffer(vertex_chunk.buffer.read(), np.float32).reshape(-1, 3)
                faces = np.frombuffer(face_chunk.buffer.read(), ShadowFaceDtype)
                edges = np.frombuffer(edge_chunk.buffer.read(), np.uint32).reshape(-1, 2)
                self.shadow_mesh_data = ShadowMeshData(shadow_mesh, faces, vertices, edges)

                del vertex_chunk, face_chunk, edge_chunk
            else:
                if chunk.header.data_size > 0:
                    print(f"Unhandled chunk {chunk}")
        # print(self.mesh_info)
        # print(self.mesh)
        # print(self.collision_data)
        # print(self.attachments)
        # print("***************")
