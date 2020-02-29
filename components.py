import ctypes
import os
import math
from typing import Dict, List, cast
from abc import ABC, abstractclassmethod
import sdl2
from helpers import sdl, draw_texture, texture_from_bmp
import config
import entities


class Component(ABC):
    """Interface that each component must adhere to."""

    @abstractclassmethod
    def update(cls) -> None:
        """Called every frame to update component's game state."""
        raise NotImplementedError

    @abstractclassmethod
    def draw(cls, renderer: sdl2.render.SDL_Renderer) -> None:
        """Called every frame to draw component."""
        raise NotImplementedError

    @abstractclassmethod
    def collision(cls, other: "entities.Entity") -> None:
        """Called every frame for component to react to collision on container
        entity. other is the Entity with which we collided."""
        raise NotImplementedError


class SpriteRenderer(Component):
    """Rendering a sprite is a piece of functionality shared among components."""

    def __init__(self, renderer: sdl2.render.SDL_Renderer,
                 container: "entities.Entity", filename: str):
        # Container of this component
        self.container = container

        # Never explicitly deallocated, but reclaimed by the operating system
        # when the game exits.
        self.texture = texture_from_bmp(renderer, filename)

        # Dynamically determine width and height of sprite over using constants.
        w = ctypes.pointer(ctypes.c_int(0))
        h = ctypes.pointer(ctypes.c_int(0))
        sdl(sdl2.SDL_QueryTexture(self.texture, None, None, w, h))
        self.width = float(w.contents.value)
        self.height = float(h.contents.value)

    def draw(self, renderer: sdl2.render.SDL_Renderer) -> None:
        con = self.container
        draw_texture(renderer, self.texture, con.position, con.rotation)

    def update(self) -> None:
        pass

    def collision(self, other: "entities.Entity") -> None:
        pass


class Sequence():
    def __init__(self, renderer: sdl2.render.SDL_Renderer, filepath: str,
                 sample_rate: int, loop: bool):
        """ Creates a sequence from a list of files in filepath."""
        self.textures: List[sdl2.render.SDL_Texture] = []
        for filename in sorted(os.listdir(filepath)):
            self.textures.append(
                texture_from_bmp(renderer, os.path.join(filepath, filename)))

        # Number of times to update current_frame per second
        self.sample_rate = sample_rate
        self.loop = loop

        # Index into textures list
        self.current_frame = 0

    def current_texture(self) -> sdl2.render.SDL_Texture:
        return self.textures[self.current_frame]

    def next_frame(self) -> bool:
        if self.current_frame == len(self.textures) - 1:
            if self.loop:
                self.current_frame = 0
            else:
                return True
        else:
            self.current_frame += 1
        return False


class Animator(Component):
    def __init__(self, container: "entities.Entity", sequences:
                 Dict[str, Sequence], default_sequence: str):
        self.container = container
        self.sequences = sequences
        self.last_frame_change = sdl2.SDL_GetTicks()
        self.finished = False

        # Key used to index into self.sequences dictionary
        self.current_animation_playing = default_sequence

    def set_sequence(self, name: str) -> None:
        self.current_animation_playing = name
        self.last_frame_change = sdl2.SDL_GetTicks()

    def draw(self, renderer: sdl2.render.SDL_Renderer) -> None:
        texture = self.sequences[
            self.current_animation_playing].current_texture()
        con = self.container
        draw_texture(renderer, texture, con.position, con.rotation)

    def update(self) -> None:
        sequence = self.sequences[self.current_animation_playing]
        frame_interval = 1000.0 / sequence.sample_rate

        if (sdl2.SDL_GetTicks() - self.last_frame_change) >= frame_interval:
            self.finished = sequence.next_frame()
            self.last_frame_change = sdl2.SDL_GetTicks()

    def collision(self, other: "entities.Entity") -> None:
        pass


class VulnerableToBullets(Component):
    def __init__(self, container: "entities.Entity") -> None:
        self.container = container
        self.animator: Animator = cast(
            Animator, container.get_component(Animator))

    def draw(self, renderer: sdl2.render.SDL_Renderer) -> None:
        pass

    def update(self) -> None:
        if self.animator.finished and self.animator.current_animation_playing == "destroy":
            self.container.active = False

    def collision(self, other: "entities.Entity") -> None:
        if other.tag == "bullet":
            self.animator.set_sequence("destroy")


class BulletMover(Component):
    def __init__(self, container: "entities.Entity", speed: float):
        self.container = container
        self.speed = speed

    def draw(self, renderer: sdl2.render.SDL_Renderer) -> None:
        pass

    def update(self) -> None:
        # Compute how much of bullet's speed should go in x and y directions.
        con = self.container
        pos = con.position
        pos.x += self.speed * math.cos(con.rotation) * config.delta_time
        pos.y += self.speed * math.sin(con.rotation) * config.delta_time

        if pos.x > config.SCREEN_WIDTH or pos.x < 0 or pos.y > config.SCREEN_HEIGHT or pos.y < 0:
            con.active = False

        # We know there's only ever one collision point for bullet.
        con.collisions[0].center = con.position

    def collision(self, other: "entities.Entity") -> None:
        """When bullet collides with enemy, make bullet invisible."""

        # Deactivation of bullet on collision with other entity strictly
        # speaking isn't related to the bullet movement component. Argument
        # could be made that this functionality ought to be places in a separate
        # component.
        self.container.active = False


class KeyboardMover(Component):
    def __init__(self, container: "entities.Entity", speed: float):
        # Component to be applied to any element to allow it to be moved around
        # based on keyboard input. Therefore we store a reference to parent
        # element that this component is a part of.
        self.container = container

        # KeyboardMover must know container element's speed to make different
        # KeyboardMovers for elements that move at different speeds.
        self.speed = speed

        # To detect when container element moves outside the screen we must know
        # the screen's height and width. It's stored inside the element's
        # SpriteRenderer which we must locate. This implies that when we attach
        # a KeyboardMover component to an element, it's assumed that a
        # SpriteRenderer component is also attached.
        self.sprite_renderer: SpriteRenderer = cast(
            SpriteRenderer, container.get_component(SpriteRenderer))

    def draw(self, renderer: sdl2.render.SDL_Renderer) -> None:
        pass

    def update(self) -> None:
        con = self.container
        keys = sdl(sdl2.SDL_GetKeyboardState(None))
        if keys[sdl2.SDL_SCANCODE_LEFT] == 1:
            if con.position.x - self.sprite_renderer.width/2 > 0:
                con.position.x -= self.speed * config.delta_time
        elif keys[sdl2.SDL_SCANCODE_RIGHT] == 1:
            if con.position.x + self.sprite_renderer.width/2 < config.SCREEN_WIDTH:
                con.position.x += self.speed * config.delta_time

    def collision(self, other: "entities.Entity") -> None:
        pass


class KeyboardShooter(Component):
    def __init__(self, container: "entities.Entity", cooldown: int) -> None:
        self.container: entities.Entity = container
        self.cooldown = cooldown
        self.last_shot = 0

    def draw(self, renderer: sdl2.render.SDL_Renderer) -> None:
        pass

    def update(self) -> None:
        pos = self.container.position
        keys = sdl(sdl2.SDL_GetKeyboardState(None))
        if keys[sdl2.SDL_SCANCODE_SPACE] == 1:
            if (sdl2.SDL_GetTicks() - self.last_shot) >= self.cooldown:
                # Player has two turrets
                self.shoot(pos.x + 25, pos.y - 20)
                self.shoot(pos.x - 25, pos.y - 20)
                self.last_shot = sdl2.SDL_GetTicks()

    def shoot(self, x: float, y: float) -> None:
        """Creates a bullet at (x,y) to allow bullet to originate from left and
        right gun turret instead of the player's center."""
        bullet = entities.bullet_from_pool()
        if bullet is not None:
            bullet.active = True
            bullet.position.x = x
            bullet.position.y = y
            bullet.rotation = 270 * (math.pi / 180)  # degrees to radians
            bullet.update()

    def collision(self, other: "entities.Entity") -> None:
        pass
