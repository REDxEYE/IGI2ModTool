from collections.abc import Iterable
from dataclasses import dataclass

from igi2cs.file_utils import Buffer, MemoryBuffer


@dataclass(slots=True)
class ILFFHeader:
    ident: str
    data_size: int
    alignment: int
    next_offset: int

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return ILFFHeader(buffer.read_ascii_string(4), buffer.read_uint32(), buffer.read_uint32(), buffer.read_uint32())


@dataclass(slots=True)
class ResHeader:
    header: ILFFHeader
    format: str

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        header = ILFFHeader.from_buffer(buffer)
        fmt = buffer.read_ascii_string(4)
        return ResHeader(header, fmt)


@dataclass(slots=True)
class ResChunk:
    header: ILFFHeader
    data: MemoryBuffer

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        header = ILFFHeader.from_buffer(buffer)
        data = MemoryBuffer(buffer.read(header.data_size))
        buffer.align(header.alignment)
        return ResChunk(header, data)


@dataclass(slots=True)
class ResEntry:
    name: str
    data: MemoryBuffer


class ResArchive:
    def __init__(self, buffer: Buffer):
        self.header = ResHeader.from_buffer(buffer)
        chunks = []
        while buffer:
            chunks.append(ResChunk.from_buffer(buffer))

        all_names = []
        self.files = []
        if chunks:
            if chunks[-1].header.ident == "PATH":
                name_chunk = chunks.pop(-2)
                paths = chunks.pop(-1)
                all_names.append(name_chunk.data.read_ascii_string())
                all_names.extend(paths.data.read_ascii_string().split(";"))
            while chunks:
                name_chunk = chunks.pop(0)
                assert name_chunk.header.ident == "NAME"
                data_chunk = chunks.pop(0)
                if data_chunk.header.ident == "BODY":
                    self.files.append(ResEntry(name_chunk.data.read_ascii_string(), data_chunk.data))
                elif data_chunk.header.ident == "CSTR":
                    self.files.append(ResEntry(name_chunk.data.read_ascii_string(), data_chunk.data))
                else:
                    assert False, f"Chunk of type {data_chunk.header.ident!r} not supported"
        if all_names:
            assert len(all_names) - 1 == len(self.files)

    def __repr__(self):
        return f"ResArchive({len(self.files)} files)"

    def __iter__(self)->Iterable[tuple[str,Buffer]]:
        for entry in self.files:
            name = entry.name
            if name.startswith("LOCAL:"):
                name = name[6:]
            yield name, entry.data