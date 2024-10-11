from dataclasses import dataclass

from igi2cs.file_utils import Buffer, MemoryBuffer
from igi2cs.loop_header import FFLIHeader


@dataclass(slots=True)
class LoopChunk:
    """Represents a chunk in the ILFF file with its header and associated buffer."""
    header: FFLIHeader
    buffer: Buffer

    @property
    def ident(self):
        """Shortcut to header.ident."""
        return self.header.ident


class MultipleChunksFound(Exception):
    """Raised when multiple chunks with the same identifier are found."""
    pass


class InvalidLoopHeader(Exception):
    """Raised when the ILFF header is invalid or unrecognized."""
    pass


class UnexpectedChunk(Exception):
    """Raised when a chunk with an unexpected identifier is encountered."""
    pass


class LoopFile:
    """Parses an FFLI file, storing its header, container type, and chunks."""

    def __init__(self, buffer: Buffer, flip_ident: bool = False):
        """Initializes a LoopFile object, parsing the FFLI header and chunks.

        Args:
            buffer (Buffer): The buffer containing FFLI file data.
            flip_ident (bool): Boolean to toggle ident flip.

        Raises:
            InvalidLoopHeader: If the FFLI header identifier is invalid.
        """
        self.root_header = root_header = FFLIHeader.from_buffer(buffer, False)
        if root_header.ident != "ILFF":
            raise InvalidLoopHeader(f"Invalid ILFF header, got {root_header.ident}")

        self.container_type = buffer.read_ascii_string(4)

        self._all_chunks: list[LoopChunk] = []
        while buffer:
            chunk = FFLIHeader.from_buffer(buffer, flip_ident)
            chunk_buffer = MemoryBuffer(buffer.read(chunk.data_size))
            self._all_chunks.append(LoopChunk(chunk, chunk_buffer))
            buffer.align(chunk.alignment)
        self.chunk_stack = self._all_chunks.copy()

    def is_container_for(self, c_type: str) -> bool:
        """Checks if the container type matches `c_type`.

        Args:
            c_type (str): Container type to match.

        Returns:
            bool: True if it matches, False otherwise.
        """
        return self.container_type == c_type

    def next_chunk(self) -> LoopChunk:
        """Returns the next chunk from the chunk stack.

        Returns:
            LoopChunk: The next chunk.
        """
        return self.chunk_stack.pop(0)

    def expect_chunk(self, ident: str) -> LoopChunk:
        """Returns the top chunk if it matches the expected identifier.

        Args:
            ident (str): Identifier to match.

        Returns:
            LoopChunk: The top chunk if it matches.

        Raises:
            UnexpectedChunk: If the top chunk identifier does not match.
        """
        top = self.chunk_stack[0]
        if top.header.ident != ident:
            raise UnexpectedChunk(f"Expected {ident!r}, but got {top.header.ident!r}")
        self.chunk_stack.pop(0)
        return top

    def find_chunk(self, ident: str) -> LoopChunk | None:
        """Finds the first chunk with the specified identifier.

        Args:
            ident (str): Identifier to search for.

        Returns:
            LoopChunk | None: The found chunk or None if not found.

        Raises:
            MultipleChunksFound: If multiple chunks with the same identifier are found.
        """
        filtered = list(filter(lambda c: c.header.ident == ident, self.chunk_stack))
        if len(filtered) > 1:
            raise MultipleChunksFound(f"Multiple chunks found with {ident!r} ident")
        if filtered:
            return filtered[0]

    def __bool__(self) -> bool:
        """Returns True if there are chunks in the stack"""
        return len(self.chunk_stack) > 0
