# To best share global variables across modules we put those inside a config
# module. This module is then inported into every module that need access to its
# variables There is only ever one instance of each module and so any changes
# made to the module object, such as updating delta_time, get reflected
# everywhere its references.

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

# As the game will run at the highest possible FPS allowed by hardware, actual
# speed is hardware dependent. How quickly entities move around is determined by
# how fast the game loop runs. So in order to do hardware independent physics
# calculations, such as moving entities around, we need a value that increases
# when the game is running slowly and decreases when game is running quickly.
# This delta_time is then applied to every calculation in the game that does
# something as a function of time. The net effect is that entities will move at
# the same rate regardless of hardware speed, even though the movement might
# sometimes be jittery. delta_time is updated each frame based on timing how
# long it took for the frame to render compared to TARGET_TICKS_PER_SECOND.
delta_time: float = 1

# To calculate delta_time we need a target ticks per second at which delta_time
# is 1. Here ticks refer to physics engine tick, but it could be anything such
# as CPU ticks. In this game we update game state and redraws the frame every
# second, making frames per second and ticks equal.
TARGET_TICKS_PER_SECOND = 60
