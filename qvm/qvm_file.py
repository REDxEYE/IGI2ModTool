from dataclasses import dataclass

from igi2cs.file_utils import Buffer


@dataclass
class QVMScript:
    symbols: list[str]
    strings: list[str]
    code: bytes


def load_qvm(name: str, buffer: Buffer) -> QVMScript:
    (ident, *version, string_table_offset, strings_offset, string_count, strings_size,
     name_table_offset, names_offset, name_count, names_size,
     opcode_start, opcode_size, unk32, unk38, some_string_offset) = buffer.read_fmt("4s2I4I4I2I3I")

    assert unk32 == 0
    assert unk38 == 0

    if ident != b"LOOP":
        raise Exception(f"Invalid QVM header: {ident}, expected: LOOP")
    if tuple(version) != (8, 7):
        raise Exception(f"Invalid QVM version: {version}, expected: (8,7)")
    buffer.seek(strings_offset)
    strings = [s.decode("ascii") for s in buffer.read(strings_size).split(b"\x00")]
    buffer.seek(names_offset)
    names = [s.decode("ascii") for s in buffer.read(names_size).split(b"\x00")]
    buffer.seek(opcode_start)
    code_data = buffer.read(opcode_size)

    return QVMScript(strings, names, code_data)
