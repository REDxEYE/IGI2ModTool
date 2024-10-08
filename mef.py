from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum

import numpy as np

from igi2cs.file_utils import Buffer, MemoryBuffer
from igi2cs.res import ResChunk, ILFFHeader


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
class MeshChunkData:
    version: float
    creation_type: DateTime
    model_type: ModelType
    unk: tuple[int, int, int]
    spheres: tuple[Sphere, Sphere, Sphere]

    render_mesh_info: MeshInfo
    collision_mesh_info: MeshInfo

    field_74: float
    field_80: int
    field_82: int
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
        return MeshChunkData(buffer.read_float(), DateTime.from_buffer(buffer), ModelType(buffer.read_uint32()),
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
    lightmap_related: int
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
    field0: int
    scaled_vertex_sum: Vector3
    index_offset: int
    face_count: int
    vertex_offset: int
    vertex_count: int
    group_id: int

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return FaceGroup(buffer.read_uint32(), Vector3.from_buffer(buffer), buffer.read_uint16(), buffer.read_uint16(),
                         buffer.read_uint16(), buffer.read_uint16(), buffer.read_uint32())


@dataclass(slots=True)
class Bone:
    name: str
    pos: Vector3


@dataclass(slots=True)
class Mesh:
    render_info: RenderStat
    faces: np.ndarray
    vertices: np.ndarray
    primitives: list[FaceGroup] = field(default_factory=list)


class MefModel:
    def __init__(self, buffer: Buffer):
        root_header = ILFFHeader.from_buffer(buffer)
        if root_header.ident != "ILFF":
            raise Exception("Invalid ILFF header")
        container_type = buffer.read_ascii_string(4)
        if container_type != "OCEM":
            raise InvalidModelType("Invalid model type")

        model_info: MeshChunkData | None = None
        meshes: list[Mesh] = []

        chunks: list[tuple[ILFFHeader, Buffer]] = []
        while buffer:
            chunk = ILFFHeader.from_buffer(buffer)
            chunk_buffer = MemoryBuffer(buffer.read(chunk.data_size))
            chunks.append((chunk, chunk_buffer))
            buffer.align(chunk.alignment)
        # for chunk in chunks:
        #     print(chunk[0])
        while chunks:
            chunk, chunk_buffer = chunks.pop(0)
            if chunk.ident == "HSEM":
                model_info = MeshChunkData.from_buffer(chunk_buffer)
            elif chunk.ident == "REIH":
                parent_ids = []
                child_count = [chunk_buffer.read_uint8() for _ in range(model_info.bone_count)]
                positions = [Vector3.from_buffer(chunk_buffer) for _ in range(model_info.bone_count)]
                print(child_count)
            elif chunk.ident == "D3DR":
                render_stat = RenderStat.from_buffer(chunk_buffer)
                face_chunk, face_buffer = chunks.pop(0)
                if face_chunk.ident != "ECAF":
                    raise Exception("Expected 'ECAF' chunk")
                faces = np.frombuffer(chunk_buffer.data, np.uint16)

                rend_chunk, rend_buffer = chunks.pop(0)
                if rend_chunk.ident != "DNER":
                    raise Exception("Expected 'DNER' chunk")
                render_info = [FaceGroup.from_buffer(rend_buffer) for _ in range(render_stat.face_group_count)]

                vert_chunk, vert_buffer = chunks.pop(0)
                if vert_chunk.ident != "XTRV":
                    raise Exception("Expected 'XTRV' chunk")
                if model_info.model_type == ModelType.MODEL0:
                    dtype = np.dtype([
                        ("pos", np.float32, (3,)),
                        ("normal", np.float32, (3,)),
                        ("uv0", np.float32, (2,))
                    ])
                elif model_info.model_type == ModelType.MODEL1:
                    dtype = np.dtype([
                        ("pos", np.float32, (3,)),
                        ("unk", np.float32, (6,)),
                        ("indices_and_weights", np.ushort, (2,))
                    ])
                elif model_info.model_type == ModelType.MODEL3:
                    dtype = np.dtype([
                        ("pos", np.float32, (3,)),
                        ("uv0", np.float32, (2,)),
                        ("uv1", np.float32, (2,))
                    ])
                else:
                    raise Exception("Unknown model type")

                vertices = np.frombuffer(vert_buffer.data, dtype)
                if render_stat.type == 44:
                    face_chunk, face_buffer = chunks.pop(0)
                    if face_chunk.ident != "PMTL":
                        raise Exception("Expected 'PMTL' chunk")
                mesh = Mesh(render_stat, faces, vertices, render_info)
                meshes.append(mesh)
            else:
                pass
                print(f"Unhandled chunk {chunk}")
        print(model_info)
        print(meshes)
        print("***************")
