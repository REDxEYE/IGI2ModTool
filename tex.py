from dataclasses import dataclass
from enum import IntEnum

import numpy as np
from numpy.distutils.conv_template import header

from igi2cs.file_utils import Buffer
from igi2cs.texture_decoder import Texture, PixelFormat


class ConversionMode(IntEnum):
    Palette4 = 0x0
    Palette8 = 0x1
    ARGB1555 = 0x2
    ARGB8888 = 0x3
    ARGB4444 = 0x4
    RGB565 = 0x5
    Intensity8 = 0x6
    Bumpmap = 0x7


@dataclass(slots=True)
class TexHeader:
    ident: str
    version: int
    conversion_mode: ConversionMode
    has_mips: bool
    flags: int
    palette_offset: int
    scale_factor: int
    width: int
    height: int
    cropped_width: int
    cropped_height: int
    bytes_per_pixel: int

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        ident = buffer.read_ascii_string(4)
        version = buffer.read_uint32()
        mode = buffer.read_uint32()
        conv_mode = ConversionMode(mode & 0x3F)
        has_mips = (mode & 0x40) != 0
        flags = buffer.read_uint32()
        palette_offset = buffer.read_uint32()

        scale_factor = buffer.read_uint16()
        width = buffer.read_uint16()
        height = buffer.read_uint16()
        cropped_width = buffer.read_uint16()
        cropped_height = buffer.read_uint16()
        bytes_per_pixel = buffer.read_uint16()
        return cls(ident, version, conv_mode, has_mips, flags, palette_offset, scale_factor, width, height,
                   cropped_width,
                   cropped_height, bytes_per_pixel)


def argb1555_to_rgba5551(argb_pixels: np.ndarray) -> np.ndarray:
    blue = (argb_pixels >> 0) & 0x1F
    green = (argb_pixels >> 5) & 0x1F
    red = (argb_pixels >> 10) & 0x1F
    alpha = (argb_pixels >> 15) & 0x1

    rgba_pixels = (red << 0) | (green << 5) | (blue << 10) | (alpha << 15)

    return rgba_pixels

class UnsupportedImageMode(Exception):
    pass

class TexTexture:
    def __init__(self, buffer: Buffer):
        self.header = TexHeader.from_buffer(buffer)
        if self.header.conversion_mode == ConversionMode.Palette4:
            raise UnsupportedImageMode("Palette 4 is not supported")

        width = self.header.cropped_width
        height = self.header.cropped_height

        self.image_data = buffer.read(width * height * self.header.bytes_per_pixel)
        if self.header.has_mips and self.header.conversion_mode == ConversionMode.ARGB8888:
            mip_width = width >> 1
            mip_height = height >> 1
            while mip_width >= 1 and mip_height >= 1:
                buffer.skip(mip_width * mip_height * self.header.bytes_per_pixel)
                mip_width >>= 1
                mip_height >>= 1
        if self.header.palette_offset != 0:
            raise Exception("Palette offset is not supported")

        assert buffer.tell() == buffer.size()

    def convert_to_rgba(self) -> bytes:
        if self.header.conversion_mode == ConversionMode.ARGB8888:
            return Texture.from_data(self.image_data, self.header.cropped_width, self.header.cropped_height,
                                     PixelFormat.BGRA8888).data
        elif self.header.conversion_mode == ConversionMode.ARGB1555:
            image_data = self.image_data
            image_data = argb1555_to_rgba5551(np.frombuffer(image_data, np.uint16))
            return Texture.from_data(image_data.tobytes(), self.header.cropped_width, self.header.cropped_height,
                                     PixelFormat.RGBA5551).data

        else:
            raise Exception("Unsupported pixel format")
