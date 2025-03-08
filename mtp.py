from dataclasses import dataclass

from igi2cs.file_utils import Buffer


@dataclass(slots=True)
class MTPChunk:
    name: str
    size: int

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        buffer.set_big_endian()
        return MTPChunk(buffer.read_ascii_string(4), buffer.read_uint32())


@dataclass(slots=True)
class MTPInstance:
    model_id: int
    texture_info_ids: list[int]

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        model_id = buffer.read_uint32()
        count = buffer.read_uint32()
        texture_info_ids = [buffer.read_uint32() for _ in range(count)]
        return cls(model_id, texture_info_ids)


@dataclass(slots=True)
class MTPIndex:
    index: int
    flags: int

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return MTPIndex(buffer.read_uint32(), buffer.read_int32())


class MTPFile:
    def __init__(self, buffer: Buffer):
        self.animations: list[str] = []
        self.sounds: list[str] = []
        self.sound_volumes: list[str] = []
        self.models: list[str] = []
        self.vnam: list[tuple[int, str]] = []
        self.instances: list[MTPInstance] = []
        self.textures: list[str] = []
        self.texture_infos: list[MTPIndex] = []

        root_chunk = MTPChunk.from_buffer(buffer)
        if root_chunk.name != "FORM":
            raise Exception("Invalid MTP file")
        form_type = buffer.read_ascii_string(4)
        if form_type != "MTP ":
            raise Exception("Invalid MTP file")

        while buffer:
            buffer.set_big_endian()
            chunk = MTPChunk.from_buffer(buffer)
            buffer.set_little_endian()
            if chunk.size > 0:
                chunk_data = buffer.slice(size=chunk.size)
                buffer.skip(chunk.size)
                buffer.align(4)
                if chunk.name == "BANM":
                    count = chunk_data.read_uint32()
                    for _ in range(count):
                        self.animations.append(chunk_data.read_ascii_string())
                elif chunk.name == "SNDS":
                    count = chunk_data.read_uint32()
                    for _ in range(count):
                        self.sounds.append(chunk_data.read_ascii_string())
                elif chunk.name == "SVOL":
                    count = chunk_data.read_uint32()
                    for _ in range(count):
                        self.sound_volumes.append(chunk_data.read_ascii_string())
                elif chunk.name == "MODS":
                    count = chunk_data.read_uint32()
                    for _ in range(count):
                        self.models.append(chunk_data.read_ascii_string())
                elif chunk.name == "VNAM":
                    count = chunk_data.read_uint32()
                    ints = [chunk_data.read_uint32() for _ in range(count)]
                    strings = [chunk_data.read_ascii_string() for _ in range(count)]
                    self.vnam.extend(zip(ints, strings))
                elif chunk.name == "INST":
                    while chunk_data:
                        self.instances.append(MTPInstance.from_buffer(chunk_data))
                elif chunk.name == "TEXF":
                    count = chunk_data.read_uint32()
                    for _ in range(count):
                        self.textures.append(chunk_data.read_ascii_string())
                elif chunk.name == "PALF":
                    count = chunk_data.read_uint32()
                    assert count == 0
                elif chunk.name == "GTT ":
                    count = chunk_data.read_uint32()
                    for _ in range(count):
                        self.texture_infos.append(MTPIndex.from_buffer(chunk_data))
                else:
                    print(f"Unhandled MTP chunk {chunk}")

    def get_texture_names(self, model_name: str):
        model_index = self.models.index(model_name)
        instance = next(filter(lambda x: x.model_id == model_index, self.instances), None)
        if instance is None:
            return []
        texture_names = []
        for texture_info_id in instance.texture_info_ids:
            texture_info = self.texture_infos[texture_info_id]
            texture_names.append(self.textures[texture_info.index])
        return texture_names
