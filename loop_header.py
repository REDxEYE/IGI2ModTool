from dataclasses import dataclass

from igi2cs.file_utils import Buffer


@dataclass(slots=True)
class FFLIHeader:
    ident: str
    data_size: int
    alignment: int
    next_offset: int

    @classmethod
    def from_buffer(cls, buffer: Buffer, flip_ident: bool = False):
        ident = buffer.read(4)
        if flip_ident:
            ident = ident[::-1]
        return FFLIHeader(ident.decode("ascii"), *buffer.read_fmt("3I"))
