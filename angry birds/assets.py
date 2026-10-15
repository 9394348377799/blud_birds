import os

import pygame

import settings
from game_state import state


def load_assets():
    resource_dir = os.path.join(os.path.dirname(__file__), "resources")
    state.background_image = pygame.transform.scale(
        pygame.image.load(
            os.path.join(resource_dir, "2c24ba2e0e1a2455cccc366a96efcbf0.png")
        ).convert(),
        (settings.WIDTH, settings.HEIGHT),
    )
    state.bird_idle_image = pygame.transform.scale(
        pygame.image.load(os.path.join(resource_dir, "blud_idle.png")).convert_alpha(),
        (36, 36),
    )
    state.bird_fly_image = pygame.transform.scale(
        pygame.image.load(os.path.join(resource_dir, "blud_fly.png")).convert_alpha(),
        (36, 36),
    )
    state.pig_image = pygame.transform.scale(
        pygame.image.load(os.path.join(resource_dir, "BLURPIG.png")).convert_alpha(),
        (48, 48),
    )
    state.pig_laugh_frames = [
        pygame.transform.scale(
            pygame.image.load(
                os.path.join(resource_dir, f"laugher-frame-{frame}.png")
            ).convert_alpha(),
            (48, 48),
        )
        for frame in range(2)
    ]

    pygame.mixer.init()
    state.bird_launch_sound = pygame.mixer.Sound(
        os.path.join(resource_dir, "birdflynoise.mp3")
    )
    state.pig_death_sound = pygame.mixer.Sound(
        os.path.join(resource_dir, "barfer.mp3")
    )
