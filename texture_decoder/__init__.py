import ctypes
import platform
from ctypes import cdll
from enum import IntEnum, auto
from pathlib import Path
from typing import Optional

_platform_info = platform.uname()
_lib_path: Optional[Path] = Path(__file__).parent
if _platform_info.system == "Windows":
    _lib_path /= "TextureDecoder.dll"

elif _platform_info.system == 'Linux':
    _lib_path /= "libTextureDecoder.so"

elif _platform_info.system == 'Darwin':
    _lib_path /= "libTextureDecoder.dylib"

else:
    raise NotImplementedError(f'System {_platform_info} not supported')

assert _lib_path.exists()

_lib = cdll.LoadLibrary(_lib_path.as_posix())


# noinspection PyPep8Naming
class _Texture(ctypes.Structure):
    pass


class PixelFormat(IntEnum):
    INVALID = 0
    RGBA32 = auto()
    RGB32 = auto()
    RG32 = auto()
    R32 = auto()
    RGBA16 = auto()
    RGB16 = auto()
    RG16 = auto()
    RG16_SIGNED = auto()
    R16 = auto()
    RGBA32F = auto()
    RGB32F = auto()
    RG32F = auto()
    R32F = auto()
    RGBA16F = auto()
    RGB16F = auto()
    RG16F = auto()
    R16F = auto()
    RGBA8888 = auto()
    BGRA8888 = auto()
    ABGR8888 = auto()
    ARGB8888 = auto()
    RGB888 = auto()
    BGR888 = auto()
    RG88 = auto()
    RA88 = auto()
    R8 = auto()
    RGB565 = auto()
    RGBA5551 = auto()
    RGBA1010102 = auto()
    RGBA4444 = auto()
    BC1 = auto()
    BC1a = auto()
    BC2 = auto()
    BC3 = auto()
    BC4 = auto()
    BC5 = auto()
    BC6 = auto()
    BC7 = auto()
    ETC1 = auto()
    RGBA1111 = auto()


# int64_t get_buffer_size_from_texture(const sTexture *texture);
_lib.get_buffer_size_from_texture.argtypes = [ctypes.POINTER(_Texture)]
_lib.get_buffer_size_from_texture.restype = ctypes.c_int64

# int64_t get_buffer_size_from_texture_format(uint32_t width, uint32_t height, ePixelFormat pixelFormat);
_lib.get_buffer_size_from_texture_format.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint16]
_lib.get_buffer_size_from_texture_format.restype = ctypes.c_int64

# sTexture *create_texture(const uint8_t *data, size_t dataSize, uint32_t width, uint32_t height, ePixelFormat pixelFormat);
_lib.create_texture.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_uint32,
                                ctypes.c_uint16]
_lib.create_texture.restype = ctypes.POINTER(_Texture)

# sTexture *create_empty_texture(uint32_t width, uint32_t height, ePixelFormat pixelFormat);
_lib.create_empty_texture.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint16]
_lib.create_empty_texture.restype = ctypes.POINTER(_Texture)

# bool convert_texture(const sTexture *from_texture, sTexture *to_texture);
_lib.convert_texture.argtypes = [ctypes.POINTER(_Texture), ctypes.POINTER(_Texture)]
_lib.convert_texture.restype = ctypes.c_bool

# sTexture *create_uninitialized_texture();
_lib.create_uninitialized_texture.argtypes = []
_lib.create_uninitialized_texture.restype = ctypes.POINTER(_Texture)

# DLL_EXPORT bool flip_texture(const sTexture *in_texture, sTexture *out_texture, bool flip_ud, bool flip_lr);
_lib.flip_texture.argtypes = [ctypes.POINTER(_Texture), ctypes.POINTER(_Texture), ctypes.c_bool, ctypes.c_bool]
_lib.flip_texture.restype = ctypes.c_bool

# bool get_texture_data(const sTexture *texture, char *buffer, uint32_t buffer_size);
_lib.get_texture_data.argtypes = [ctypes.POINTER(_Texture), ctypes.c_char_p, ctypes.c_uint32]
_lib.get_texture_data.restype = ctypes.c_bool

# uint32_t get_texture_width(const sTexture *texture);
_lib.get_texture_width.argtypes = [ctypes.POINTER(_Texture)]
_lib.get_texture_width.restype = ctypes.c_uint32

# uint32_t get_texture_height(const sTexture *texture);
_lib.get_texture_height.argtypes = [ctypes.POINTER(_Texture)]
_lib.get_texture_height.restype = ctypes.c_uint32

# ePixelFormat get_texture_pixel_format(const sTexture *texture);
_lib.get_texture_pixel_format.argtypes = [ctypes.POINTER(_Texture)]
_lib.get_texture_pixel_format.restype = ctypes.c_uint16

# void free_texture(sTexture *texture);
_lib.free_texture.argtypes = [ctypes.POINTER(_Texture)]
_lib.free_texture.restype = None

# sTexture *load_dds(char *filename);
_lib.load_dds.argtypes = [ctypes.c_char_p]
_lib.load_dds.restype = ctypes.POINTER(_Texture)

# sTexture *load_pvr(char *filename);
_lib.load_pvr.argtypes = [ctypes.c_char_p]
_lib.load_pvr.restype = ctypes.POINTER(_Texture)

# sTexture *load_png(const char *filename, int expected_channels);
_lib.load_png.argtypes = [ctypes.c_char_p, ctypes.c_int]
_lib.load_png.restype = ctypes.POINTER(_Texture)

# sTexture *load_tga(const char *filename, int expected_channels);
_lib.load_tga.argtypes = [ctypes.c_char_p, ctypes.c_int]
_lib.load_tga.restype = ctypes.POINTER(_Texture)

# bool write_png(const char *filename, const sTexture* texture);
_lib.write_png.argtypes = [ctypes.c_char_p, ctypes.POINTER(_Texture)]
_lib.write_png.restype = ctypes.c_bool

# bool write_tga(const char *filename, const sTexture* texture);
_lib.write_tga.argtypes = [ctypes.c_char_p, ctypes.POINTER(_Texture)]
_lib.write_tga.restype = ctypes.c_bool

# sTexture *load_hdr(const char *filename);
_lib.load_hdr.argtypes = [ctypes.c_char_p]
_lib.load_hdr.restype = ctypes.POINTER(_Texture)

# bool is_compressed_pixel_format(ePixelFormat pixelFormat);
_lib.is_compressed_pixel_format.argtypes = [ctypes.c_uint32]
_lib.is_compressed_pixel_format.restype = ctypes.c_bool

# ePixelFormat get_uncompressed_pixel_format_variant(ePixelFormat pixelFormat);
_lib.get_uncompressed_pixel_format_variant.argtypes = [ctypes.c_uint32]
_lib.get_uncompressed_pixel_format_variant.restype = ctypes.c_uint32

# DLL_EXPORT size_t zstd_decompress( void* dst, size_t dstCapacity, const void* src, size_t compressedSize);
_lib.zstd_decompress.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t]
_lib.zstd_decompress.restype = ctypes.c_size_t

# DLL_EXPORT size_t lz4_decompress( void* dst, size_t dstCapacity, const void* src, size_t compressedSize);
_lib.lz4_decompress.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t]
_lib.lz4_decompress.restype = ctypes.c_size_t


class Texture:
    def __init__(self, p):
        self.ptr = p

    def __del__(self):
        _lib.free_texture(self.ptr)

    @classmethod
    def from_dds(cls, path: Path) -> 'Texture':
        return cls(_lib.load_dds(str(path).encode("utf8")))

    @classmethod
    def from_png(cls, path: Path, expected_channels: int = 0) -> 'Texture':
        return cls(_lib.load_png(str(path).encode("utf8"), expected_channels))

    @classmethod
    def from_pvr(cls, path: Path) -> 'Texture':
        return cls(_lib.load_pvr(str(path).encode("utf8")))

    @classmethod
    def from_data(cls, data: bytes, width: int, height: int, pixel_format: PixelFormat) -> Optional['Texture']:
        texture = _lib.create_texture(data, len(data), width, height, pixel_format)
        if not texture:
            return None
        return cls(texture)

    @classmethod
    def new_empty(cls, width: int, height: int, pixel_format: PixelFormat) -> 'Texture':
        return cls(_lib.create_empty_texture(width, height, pixel_format))

    @classmethod
    def _new_uninitialized(cls) -> 'Texture':
        return cls(_lib.create_uninitialized_texture())

    @property
    def _is_null(self):
        return not bool(self.ptr)

    @property
    def width(self) -> int:
        if self._is_null:
            return 0
        return _lib.get_texture_width(self.ptr)

    @property
    def height(self) -> int:
        if self._is_null:
            return 0
        return _lib.get_texture_height(self.ptr)

    @property
    def pixel_format(self) -> PixelFormat:
        if self._is_null:
            return PixelFormat.INVALID
        return PixelFormat(_lib.get_texture_pixel_format(self.ptr))

    @property
    def data(self) -> Optional[bytes]:
        if self._is_null:
            return None
        buffer_size = _lib.get_buffer_size_from_texture(self.ptr)
        buffer = bytes(buffer_size)
        if _lib.get_texture_data(self.ptr, buffer, buffer_size):
            return buffer
        return None

    def convert_to(self, pixel_format: PixelFormat) -> Optional['Texture']:
        if self._is_null:
            return None
        new = self.new_empty(self.width, self.height, pixel_format)
        if _lib.convert_texture(self.ptr, new.ptr):
            return new
        return None

    def flipped(self, flip_ud: bool, flip_lr: bool) -> Optional['Texture']:
        if self._is_null:
            return None
        new = self._new_uninitialized()
        if _lib.flip_texture(self.ptr, new.ptr, flip_ud, flip_lr):
            return new
        return None

    def write_png(self, filepath: Path):
        if self._is_null:
            raise ValueError("Null texture")
        if not _lib.write_png(str(filepath).encode("utf8"), self.ptr):
            raise ValueError("Failed to save png")

    def write_tga(self, filepath: Path):
        if self._is_null:
            raise ValueError("Null texture")
        if not _lib.write_tga(str(filepath).encode("utf8"), self.ptr):
            raise ValueError("Failed to save tga")

    def __bool__(self):
        return bool(self.ptr)


def is_compressed_pixel_format(pixel_format: PixelFormat) -> bool:
    return _lib.is_compressed_pixel_format(pixel_format)


def get_uncompressed_pixel_format_variant(pixel_format: PixelFormat) -> PixelFormat:
    return PixelFormat(_lib.get_uncompressed_pixel_format_variant(pixel_format))


def get_buffer_size_from_texture_format(width: int, height: int, pixel_format: PixelFormat) -> int:
    return _lib.get_buffer_size_from_texture_format(width, height, pixel_format)


def lz4_decompress(data: bytes, decompressed_size: int):
    decompressed = bytes(decompressed_size)
    decompressed_size = _lib.lz4_decompress(decompressed, decompressed_size, data, len(data))
    return decompressed[:decompressed_size]


def zstd_decompress(data: bytes, decompressed_size: int):
    decompressed = bytes(decompressed_size)
    decompressed_size = _lib.zstd_decompress(decompressed, decompressed_size, data, len(data))
    return decompressed[:decompressed_size]
