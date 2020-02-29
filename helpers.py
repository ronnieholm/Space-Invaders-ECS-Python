import ctypes
from typing import TypeVar
import sdl2


class Vec2f:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


TResult = TypeVar('TResult')


def sdl(result: TResult) -> TResult:
    """Checks return value of type c_int or POINTER"""
    if isinstance(result, int) and result < 0:
        raise Exception(f"SDL pooped itself: {sdl2.SDL_GetError().decode()}")
    if result == ctypes.pointer(ctypes.c_long(0)):
        raise Exception(f"SDL pooped itself: {sdl2.SDL_GetError().decode()}")
    return result


def texture_from_bmp(renderer: sdl2.render.SDL_Renderer, filename: str) -> sdl2.render.SDL_Texture:
    image = sdl(sdl2.SDL_LoadBMP(filename.encode()))
    texture = sdl(sdl2.SDL_CreateTextureFromSurface(renderer, image))
    sdl(sdl2.SDL_FreeSurface(image))
    return texture


def draw_texture(renderer: sdl2.render.SDL_Renderer, texture: sdl2.render.SDL_Texture,
                 position: Vec2f, rotation: float) -> None:
    w = ctypes.pointer(ctypes.c_int(0))
    h = ctypes.pointer(ctypes.c_int(0))
    sdl(sdl2.SDL_QueryTexture(texture, None, None, w, h))
    width = float(w.contents.value)
    height = float(h.contents.value)

    # Transforms coordinates to center of sprite rather than default upper left
    # corner. This makes centering the sprite on screen easier.
    x = position.x - width/2
    y = position.y - height/2

    sdl(sdl2.SDL_RenderCopyEx(
        renderer,
        texture,
        ctypes.byref(sdl2.SDL_Rect(
            0, 0,
            int(width), int(height))),
        ctypes.byref(
            sdl2.SDL_Rect(
                int(x), int(y),
                int(width), int(height))),
        rotation,
        ctypes.byref(sdl2.SDL_Point(
            int(width/2), int(height/2))),
        sdl2.SDL_FLIP_NONE))
