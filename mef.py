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
    MODEL0 = 0
    MODEL1 = 1
    MODEL2 = 2
    MODEL3 = 3


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
class MeshHeader:
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
        return MeshHeader(buffer.read_float(), DateTime.from_buffer(buffer), ModelType(buffer.read_uint32()),
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
class RenderStat:
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
            return RenderStat(44, buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
                              buffer.read_uint32(),
                              0, 0,
                              buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
                              buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32()
                              )
        elif size == 40:
            return RenderStat(40, 0, buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
                              buffer.read_uint32(),
                              buffer.read_uint32(), buffer.read_uint32(),
                              buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
                              0, 0
                              )
        elif size == 36:
            return RenderStat(36, buffer.read_uint32(), 0, buffer.read_uint32(), buffer.read_uint32(), 0, 0,
                              buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32(),
                              buffer.read_uint32(), 0, 0)


@dataclass(slots=True)
class FaceGroup:
    color: tuple[int, int, int, int]
    scaled_vertex_sum: Vector3
    index_offset: int
    face_count: int
    vertex_offset: int
    vertex_count: int
    indices: tuple[int, int]

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return FaceGroup(buffer.read_fmt("4B"), Vector3.from_buffer(buffer), buffer.read_uint16(), buffer.read_uint16(),
                         buffer.read_uint16(), buffer.read_uint16(), buffer.read_fmt("2h"))


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
class Mesh:
    render_info: RenderStat
    faces: np.ndarray = field(repr=False)
    vertices: np.ndarray = field(repr=False)
    primitives: list[FaceGroup] = field(default_factory=list)


@dataclass(slots=True)
class CollisionMeshHeader:
    face_count: int
    vertex_count: int
    material_count: int
    sphere_count: int
    field_10: int
    field_14: int
    field_18: int
    field_1C: int
    field_20: int
    field_24: int
    field_28: int
    field_2C: int
    field_30: int
    field_34: int
    field_38: int
    field_3C: int

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return CollisionMeshHeader(*buffer.read_fmt("16I"))


@dataclass(slots=True)
class CollisionSphere:
    sphere: Sphere
    unk: tuple[int, int, int, int]

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return CollisionSphere(Sphere.from_buffer(buffer), buffer.read_fmt("4H"))


CollisionSphereDtype = np.dtype([
    ("pos", np.float32, (3,)),
    ("radius", np.float32, (1,)),
    ("unk", np.uint16, (4,)),
])

CollisionVertexDtype = np.dtype([
    ("pos", np.float32, (3,)),
    ("uv", np.float32, (2,))
])
CollisionFaceDtype = np.dtype([
    ("face", np.uint16, (3,)),
    ("unk", np.uint16, (3,))
])


class MefModel:
    def __init__(self, buffer: Buffer):
        loop_file = LoopFile(buffer, flip_ident=True)

        self.mesh_info: MeshHeader | None = None
        self.collision_mesh_info: CollisionMeshHeader | None = None
        self.mesh: Mesh | None = None
        self.bones: list[Bone] = []
        self.attachments: list[Attachment] = []

        while loop_file:
            chunk = loop_file.next_chunk()
            if chunk.ident == "MESH":
                self.mesh_info = MeshHeader.from_buffer(chunk.buffer)
            elif chunk.ident == "HIER":
                child_counts = [chunk.buffer.read_uint8() for _ in range(self.mesh_info.bone_count)]
                buffer.align(4)
                bone_positions = [Vector3.from_buffer(chunk.buffer) for _ in range(self.mesh_info.bone_count)]
                name_chunk = loop_file.expect_chunk("BNAM")
                bone_names = [name_chunk.buffer.read_ascii_string(16) for _ in range(self.mesh_info.bone_count)]
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
                for _ in range(self.mesh_info.attachment_count):
                    self.attachments.append(Attachment.from_buffer(chunk.buffer))
            elif chunk.ident == "RD3D":
                render_stat = RenderStat.from_buffer(chunk.buffer)
                face_chunk = loop_file.expect_chunk("FACE")
                faces = np.frombuffer(face_chunk.buffer.data, np.uint16)
                del face_chunk

                rend_chunk = loop_file.expect_chunk("REND")
                render_info = [FaceGroup.from_buffer(rend_chunk.buffer) for _ in range(render_stat.face_group_count)]
                del rend_chunk

                vert_chunk = loop_file.expect_chunk("VRTX")
                if self.mesh_info.model_type == ModelType.MODEL0:
                    dtype = np.dtype([
                        ("pos", np.float32, (3,)),
                        ("normal", np.float32, (3,)),
                        ("uv0", np.float32, (2,))
                    ])
                elif self.mesh_info.model_type == ModelType.MODEL1:
                    dtype = np.dtype([
                        ("pos", np.float32, (3,)),
                        ("unk", np.float32, (6,)),
                        ("indices_and_weights", np.ushort, (2,))
                    ])
                elif self.mesh_info.model_type == ModelType.MODEL3:
                    dtype = np.dtype([
                        ("pos", np.float32, (3,)),
                        ("uv0", np.float32, (2,)),
                        ("uv1", np.float32, (2,))
                    ])
                else:
                    raise Exception("Unknown model type")

                vertices = np.frombuffer(vert_chunk.buffer.data, dtype)
                del vert_chunk
                # if render_stat.type == 44:
                #     lightmap_chunk = loop_file.expect_chunk("LTMP")
                mesh = Mesh(render_stat, faces, vertices, render_info)
                self.mesh = mesh
            elif chunk.ident == "CMSH":
                self.collision_mesh_info = CollisionMeshHeader.from_buffer(chunk.buffer)
                collision_vertices_chunk = loop_file.expect_chunk("CVTX")
                collision_faces_chunk = loop_file.expect_chunk("CFCE")
                collision_materials_chunk = loop_file.expect_chunk("CMAT")
                collision_spheres_chunk = loop_file.expect_chunk("CSPH")

                collision_vertices = np.frombuffer(collision_vertices_chunk.buffer.data, CollisionVertexDtype)
                collision_faces = np.frombuffer(collision_faces_chunk.buffer.data, CollisionFaceDtype)
                collision_spheres = np.frombuffer(collision_spheres_chunk.buffer.data, CollisionSphereDtype)
                del collision_vertices_chunk, collision_faces_chunk, collision_spheres_chunk

                print(1)
            else:
                if chunk.header.data_size > 0:
                    print(f"Unhandled chunk {chunk}")
        print(self.mesh_info)
        print(self.mesh)
        print(self.attachments)
        print("***************")
