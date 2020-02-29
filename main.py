import ctypes
import sdl2
from helpers import sdl, Vec2f
import entities
from collision import check_collisions
from config import TARGET_TICKS_PER_SECOND, SCREEN_WIDTH, SCREEN_HEIGHT
import config


def start() -> None:
    sdl(sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING))
    window = sdl(sdl2.SDL_CreateWindow(
        b"Overwritten by game loop",
        sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED,
        SCREEN_WIDTH, SCREEN_HEIGHT,
        sdl2.SDL_WINDOW_OPENGL))
    renderer = sdl(sdl2.SDL_CreateRenderer(
        window, -1, sdl2.SDL_RENDERER_ACCELERATED))

    entities.initialize_bullet_pool(renderer)
    entities.System.append(entities.create_player(renderer))

    for i in range(5):
        for j in range(3):
            x = (i / 5) * SCREEN_WIDTH + (entities.ENEMY_SIZE / 2)
            y = j * entities.ENEMY_SIZE + \
                (entities.ENEMY_SIZE / 2)
            entities.System.append(
                entities.create_enemy(renderer, Vec2f(x, y)))

    event = sdl2.SDL_Event()
    running = True
    while running:
        frame_start_time = sdl2.SDL_GetTicks()
        while sdl(sdl2.SDL_PollEvent(ctypes.byref(event))) != 0:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

        sdl(sdl2.SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255))
        sdl(sdl2.SDL_RenderClear(renderer))

        for element in entities.System:
            if element.active:
                element.draw(renderer)
                element.update()

        check_collisions()
        sdl(sdl2.SDL_RenderPresent(renderer))

        # Add artificial wait to simulate running game on slow computer
        # sdl2.SDL_Delay(100)

        # If we're running at half TARGET_TICKS_PER_SECOND, delta is 2. If we're
        # running at double TARGET_TICKS_PER_SECOND, delta becomes 0.5.
        frame_render_time = sdl2.SDL_GetTicks() - frame_start_time
        config.delta_time = (frame_render_time / 1000) * \
            TARGET_TICKS_PER_SECOND

        sdl2.SDL_SetWindowTitle(
            window, f"""Space invaders - Delta: {config.delta_time:.2f}, Render: {frame_render_time} ms""".encode())

    sdl(sdl2.SDL_DestroyRenderer(renderer))
    sdl(sdl2.SDL_DestroyWindow(window))


if __name__ == "__main__":
    start()
