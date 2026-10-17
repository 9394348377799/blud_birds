import math

import pygame
import pymunk

import assets
import characters
import levels
import physics
import rendering
import settings
import ui
from game_state import state


def main():
    pygame.init()
    state.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption(settings.CAPTION)
    clock = pygame.time.Clock()

    assets.load_assets()
    ui.initialize()

    levels.ground()
    characters.create_bird()
    state.ball_shape.mass = settings.BIRD_MASS
    physics.setup_collision_handlers()

    running = True
    while running:
        time_delta = clock.tick(settings.FPS) 
        dt = settings.SIMULATION_DT

        for event in pygame.event.get():
            ui_consumed = ui.process_event(event)
            if event.type == pygame.QUIT:
                running = False
            elif state.game_state != "playing" or ui_consumed:
                continue
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    levels.generate_level(state.selected_level)
                    state.attempts_left = settings.ATTEMPTS
                    characters.reset_bird()
                    state.ball_shape.mass = settings.BIRD_MASS
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (
                    state.attempts_left > 0
                    and not state.is_launched
                    and state.ball_body
                ):
                    mouse_position = pygame.mouse.get_pos()
                    distance = math.hypot(
                        mouse_position[0] - state.ball_body.position.x,
                        mouse_position[1] - state.ball_body.position.y,
                    )
                    if distance < 30:
                        state.is_dragging = True
                        state.ball_body.body_type = pymunk.Body.KINEMATIC
            elif event.type == pygame.MOUSEBUTTONUP and state.is_dragging:
                pull_vector = (
                    settings.ANCHOR_POS[0] - state.ball_body.position.x,
                    settings.ANCHOR_POS[1] - state.ball_body.position.y,
                )
                state.ball_body.body_type = pymunk.Body.DYNAMIC
                state.ball_body.mass = settings.BIRD_MASS
                state.ball_body.moment = pymunk.moment_for_circle(
                    settings.BIRD_MASS, 
                    0, 
                    settings.BIRD_RADIUS)
                state.ball_body.velocity = tuple(coord * settings.LAUNCH_MULTIPLIER for coord in pull_vector)
                state.attempts_left -= 1
                state.is_launched = True
                state.bird_launch_sound.play()
                state.is_dragging = False
                state.settled_time = 0.0
                state.shot_active = True
        if state.game_state == "playing":
            physics.update(dt)
            rendering.draw_game()
        else:
            state.screen.blit(state.background_image, (0, 0))
            if state.game_state in ("won", "lost"):
                message = "Level completed!" if state.game_state == "won" else "Out of birds"
                font = pygame.font.Font(None, settings.FONT_SIZE_MESSAGE)
                text = font.render(message, True, (255, 255, 255))
                state.screen.blit(text, text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2)))

        ui.update_and_draw(time_delta)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
