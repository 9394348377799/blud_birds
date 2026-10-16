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
    pygame.display.set_caption("blud birds")
    clock = pygame.time.Clock()

    assets.load_assets()
    ui.initialize()

    levels.ground()
    characters.create_bird()
    state.ball_shape.mass = 0.5
    physics.setup_collision_handlers()

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        dt = 1.0 / 60.0

        for event in pygame.event.get():
            ui_consumed = ui.process_event(event)
            if event.type == pygame.QUIT:
                running = False
            elif state.game_state != "playing" or ui_consumed:
                continue
            elif event.type == pygame.KEYDOWN:
                if (
                    event.key == pygame.K_r
                    and not state.shot_active
                    and not state.is_launched
                    and state.attempts_left > 0
                ):
                    characters.reset_bird()
                    state.ball_shape.mass = 0.5
                elif event.key == pygame.K_e:
                    levels.generate_level(state.selected_level)
                    state.attempts_left = 3
                    characters.reset_bird()
                    state.ball_shape.mass = 0.5
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
                state.ball_body.mass = 0.5
                state.ball_body.moment = pymunk.moment_for_circle(0.5, 0, 15)
                state.ball_body.velocity = (pull_vector[0] * 8, pull_vector[1] * 8)
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
                message = "Level complete!" if state.game_state == "won" else "Out of birds"
                font = pygame.font.Font(None, 64)
                text = font.render(message, True, (255, 255, 255))
                state.screen.blit(text, text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2)))

        ui.update_and_draw(time_delta)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
