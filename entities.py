from typing import List, Optional, Dict, Type
import sdl2
import components
from collision import Circle
from helpers import Vec2f
import config


class Entity:
    def __init__(self) -> None:
        # Stores only properties relevant to every Entity in the game.
        self.position = Vec2f(0, 0)
        self.rotation = 0.0
        self.active = False
        self.components: List[components.Component] = []

        # Since bullet, enemy, and player are all of type Entity, inside
        # components we can't switch based on entity type. For instance, inside
        # the vulnerable_to_bullets component, it would be vulnerable to any
        # Entity, not just bullets. But assigning a tag to each Entity, we can
        # use it in checks to make vulnerable_to_bullets only apply to enemies.
        self.tag = ""

        # Entity can have zero or more collision points defined as circles with
        # which is can collide with other entities' collision points.
        self.collisions: List[Circle] = []

    def add_component(self, new: components.Component) -> None:
        """Adding a component gives the Entity the behavior of it. The new
        component must not share a type with any existing component in the
        Entity. As each component provides unique behavior, there's no reason
        why we'd need the same behavior twice."""
        for existing in self.components:
            if isinstance(existing, type(new)):
                raise Exception(type(new))
        self.components.append(new)

    def get_component(self, klass: Type[components.Component]) -> components.Component:
        for component in self.components:
            if isinstance(component, klass):
                return component
        raise Exception(klass)

    # Implementing update(), draw(), and collision() sort of make Entity itself
    # a Component. At least if we consider it Entity and Component an
    # implementation of Composite design pattern.
    def update(self) -> None:
        for component in self.components:
            component.update()

    def draw(self, renderer: sdl2.render.SDL_Renderer) -> None:
        for component in self.components:
            component.draw(renderer)

    def collision(self, other: "Entity") -> None:
        for component in self.components:
            component.collision(other)

# ------------------------------------------------------------------------------


# Ideally moves player x pixels every 1/60 second when left or right arrow key
# is pressed. As the game will runs at the highest possible speed allowed by
# hardware, actual speed is corrected by delta_time.
PLAYER_SPEED = 5.0
PLAYER_SIZE = 105

# Expressed in milliseconds allowing 1,000/Player_shot_cooldown bullets per
# second to be fired.
Player_shot_cooldown = 250


def create_player(renderer: sdl2.render.SDL_Renderer) -> Entity:
    """Creates a new player and attaches components to it."""
    player = Entity()
    player.position = Vec2f(
        config.SCREEN_WIDTH / 2,
        config.SCREEN_HEIGHT - PLAYER_SIZE / 2)
    player.active = True
    player.tag = "player"

    sprite_renderer = components.SpriteRenderer(
        renderer, player, "sprites/player.bmp")
    player.add_component(sprite_renderer)

    keyboard_mover = components.KeyboardMover(player, PLAYER_SPEED)
    player.add_component(keyboard_mover)

    keyboard_shooter = components.KeyboardShooter(player, Player_shot_cooldown)
    player.add_component(keyboard_shooter)
    return player

# ------------------------------------------------------------------------------


BULLET_SPEED = 10.0  # For visual effect, should be faster than player speed
BULLET_SIZE = 8


def create_bullet(renderer: sdl2.render.SDL_Renderer) -> Entity:
    bullet = Entity()
    bullet.position = Vec2f(0, 0)
    bullet.active = False
    bullet.tag = "bullet"

    sprite_renderer = components.SpriteRenderer(
        renderer, bullet, "sprites/bullet.bmp")
    bullet.add_component(sprite_renderer)

    bullet_mover = components.BulletMover(bullet, BULLET_SPEED)
    bullet.add_component(bullet_mover)

    collision = Circle(bullet.position, BULLET_SIZE)
    bullet.collisions.append(collision)
    return bullet


Bullet_pool: List[Entity] = []


def initialize_bullet_pool(renderer: sdl2.render.SDL_Renderer) -> None:
    for _ in range(30):
        bullet = create_bullet(renderer)
        Entities.append(bullet)
        Bullet_pool.append(bullet)


def bullet_from_pool() -> Optional[Entity]:
    """Searches the bullet pool for an unused bullet and returns it. Any Entity
    that needs to shoot a bullet will need to call this function to obtain one
    and do whatever operation it needs on the bullet returned. Without the pool
    we'd have to re-create a bullet every time its fired in the same way we
    create player and enemies. But there's a lot more bullets than player and
    enemy as the game is played."""
    for bullet in Bullet_pool:
        if not bullet.active:
            return bullet
    return None

# ------------------------------------------------------------------------------


ENEMY_SIZE = 105


def create_enemy(renderer: sdl2.render.SDL_Renderer, position: Vec2f) -> Entity:
    """Takes in position because unlike the player an enemy has no obvious default."""
    enemy = Entity()
    enemy.position = position
    enemy.rotation = 180
    enemy.active = True
    enemy.tag = "enemy"

    idle_sequence = components.Sequence(
        renderer, "sprites/enemy/idle", 5, True)
    destroy_sequence = components.Sequence(
        renderer, "sprites/enemy/destroy", 15, False)

    sequences: Dict[str, components.Sequence] = {
        "idle": idle_sequence,
        "destroy": destroy_sequence
    }

    animator = components.Animator(enemy, sequences, "idle")
    enemy.add_component(animator)

    vulnerable_to_bullets = components.VulnerableToBullets(enemy)
    enemy.add_component(vulnerable_to_bullets)

    # We want bullets to kill enemies so enemies must hold collision points so
    # we we can detect when a bullet hits an enemy.
    collision = Circle(enemy.position, 38)
    enemy.collisions.append(collision)

    return enemy

# ------------------------------------------------------------------------------


# From a threading perspective it's okay to make it a global variable. The game
# is inherently single threaded.
Entities: List[Entity] = []
