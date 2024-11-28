from collections.abc import Iterable
from dataclasses import dataclass

from igi2cs.file_utils import Buffer
from igi2cs.loop_file import LoopFile


@dataclass(slots=True)
class ResEntry:
    name: str
    data: Buffer


class ResArchive:
    def __init__(self, buffer: Buffer):
        loop_file = LoopFile(buffer, flip_ident=False)
        if not loop_file.is_container_for("IRES"):
            raise Exception("Not a RES loop file")
        all_names = []
        self.files = []
        if loop_file:
            while loop_file:
                name_chunk = loop_file.expect_chunk("NAME")
                data_chunk = loop_file.next_chunk()
                if data_chunk.ident == "BODY":
                    self.files.append(
                        ResEntry(name_chunk.buffer.read_ascii_string(name_chunk.buffer.remaining()), data_chunk.buffer))
                elif data_chunk.ident == "CSTR":
                    self.files.append(
                        ResEntry(name_chunk.buffer.read_ascii_string(name_chunk.buffer.remaining()), data_chunk.buffer))
                elif data_chunk.ident == "PATH":
                    all_names.append(name_chunk.buffer.read_ascii_string(name_chunk.buffer.remaining()))
                    all_names.extend(data_chunk.buffer.read_ascii_string(data_chunk.buffer.remaining()).split(";"))
                else:
                    assert False, f"Chunk of type {data_chunk.header.ident!r} not supported"
        if all_names:
            assert len(all_names) - 1 == len(self.files)

    def __repr__(self):
        return f"ResArchive({len(self.files)} files)"

    def __iter__(self) -> Iterable[tuple[str, Buffer]]:
        for entry in self.files:
            name = entry.name
            if name.startswith("LOCAL:"):
                name = name[6:]
            yield name, entry.data
