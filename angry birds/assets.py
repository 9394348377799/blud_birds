import os

import pygame
import settings
from game_state import state

RESOURCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")


def _load_image(filename, size, alpha=True):
    path = os.path.join(RESOURCE_DIR, filename)
    try:
        surface = pygame.image.load(path)
        surface = surface.convert_alpha() if alpha else surface.convert()
    except (pygame.error, FileNotFoundError, OSError):
        print(f"[assets] {filename} missing, using placeholder")
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((200, 60, 60, 255))
    return pygame.transform.scale(surface, size)


def _load_sound(filename, volume=1.0):
    path = os.path.join(RESOURCE_DIR, filename)
    try:
        sound = pygame.mixer.Sound(path)
    except (pygame.error, FileNotFoundError, OSError):
        print(f"[assets] sound {filename} missing")
        return None
    sound.set_volume(volume)
    return sound


def load_assets():
    state.background_image = _load_image(
        "2c24ba2e0e1a2455cccc366a96efcbf0.png",
        (settings.WIDTH, settings.HEIGHT),
        alpha=False,
    )
    state.bird_idle_image = _load_image(
        "blud_idle.png", (settings.BIRD_ICON_SIZE, settings.BIRD_ICON_SIZE)
    )
    state.bird_fly_image = _load_image(
        "blud_fly.png", (settings.BIRD_ICON_SIZE, settings.BIRD_ICON_SIZE)
    )
    state.pig_image = _load_image(
        "BLURPIG.png", (settings.PIG_ICON_SIZE, settings.PIG_ICON_SIZE)
    )
    state.pig_laugh_frames = [
        _load_image(
            f"laugher-frame-{frame}.png",
            (settings.PIG_ICON_SIZE, settings.PIG_ICON_SIZE),
        )
        for frame in range(settings.PIG_LAUGH_FRAME_COUNT)
    ]

    try:
        pygame.mixer.init()
        pygame.mixer.set_num_channels(32)
    except pygame.error as error:
        print(f"[assets] audio disabled ({error})")

    state.background_ost = _load_sound("theostaot.mp3", settings.BACKGROUND_OST_VOLUME)
    state.bird_launch_sound = _load_sound("birdflynoise.mp3", settings.BIRD_AHHHENA_VOLUME)
    state.pig_death_sound = _load_sound("barfer.mp3")
    state.pig_laugh_sound = _load_sound("lasghter(1).mp3", settings.PIG_LAUGH_VOLUME)
