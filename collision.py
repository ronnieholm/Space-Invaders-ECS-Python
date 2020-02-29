from math import sqrt
import helpers

class Circle:
    """A region within which a collision may happen. Circle is used
    because it does a good job wrapping most objects and because detecting
    collistions between two circles is cheap."""

    def __init__(self, center: helpers.Vec2f, radius: float) -> None:
        self.center = center
        self.radius = radius


def collide(c1: Circle, c2: Circle) -> bool:
    # Use absolute distance to make order of arguments irrelevant.
    distance = sqrt(abs(((c2.center.x - c1.center.x) ** 2) +
                        ((c2.center.y - c1.center.y) ** 2)))
    return distance <= c1.radius + c2.radius


def check_collisions() -> None:
    """Checks every entity for possible collections with every other entity."""
    def inner() -> None:
        from entities import Entities
        for i, e1 in enumerate(Entities[:-1]):
            # We only want to check each combination once. The order does
            # matter.
            for e2 in Entities[i + 1:]:
                for c1 in e1.collisions:
                    for c2 in e2.collisions:
                        # Check every possible collision between two elements,
                        # but only both elements are active, meaning they're
                        # visible.
                        if e1.active and e2.active and collide(c1, c2):
                            e1.collision(e2)
                            e2.collision(e1)

    inner()
