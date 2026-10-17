import math
import random

import pygame
import pymunk.pygame_util

import settings
from game_state import state


def draw_grid():
    for x in range(0, settings.WIDTH + settings.GRID_SIZE, settings.GRID_SIZE):
        pygame.draw.line(state.screen, settings.GRID_COLOR, (x, 0), (x, settings.HEIGHT), 1)
    for y in range(0, settings.HEIGHT + settings.GRID_SIZE, settings.GRID_SIZE):
        pygame.draw.line(state.screen, settings.GRID_COLOR, (0, y), (settings.WIDTH, y), 1)


def draw_trajectory_preview():
	if not state.ball_body or not state.is_dragging:
		return

	pull_x = settings.ANCHOR_POS[0] - state.ball_body.position.x
	pull_y = settings.ANCHOR_POS[1] - state.ball_body.position.y
	position_x, position_y = state.ball_body.position
	velocity_x = pull_x * settings.LAUNCH_MULTIPLIER
	velocity_y = pull_y * settings.LAUNCH_MULTIPLIER
	gravity_x, gravity_y = state.space.gravity
	simulation_dt = settings.SIMULATION_DT
	damping = state.space.damping

	for frame in range(settings.TRAJECTORY_FRAMES):
		velocity_x *= math.pow(damping, simulation_dt)
		velocity_y *= math.pow(damping, simulation_dt)
		velocity_x += gravity_x * simulation_dt
		velocity_y += gravity_y * simulation_dt
		position_x += velocity_x * simulation_dt
		position_y += velocity_y * simulation_dt
		if position_y >= settings.HEIGHT - settings.TRAJECTORY_FLOOR_MARGIN:
			break
		if frame % settings.TRAJECTORY_STEP:
			pygame.draw.circle(
				state.screen, (255, 255, 255),
				(int(position_x), int(position_y)), settings.TRAJECTORY_DOT_RADIUS,
			)


def draw_game():
	screen = state.screen
	screen.blit(state.background_image, (0, 0))
	font = pygame.font.Font(None, settings.FONT_SIZE_HUD)
	attempts_label = font.render(f"Birds: {state.attempts_left}", True, (255, 255, 255))
	screen.blit(attempts_label, (20, 20))
	# draw_grid()

	if state.is_dragging and state.ball_body:
		pygame.draw.line(
			screen,
			(100, 100, 100),
			settings.ANCHOR_POS,
			(int(state.ball_body.position.x), int(state.ball_body.position.y)),
			4,
		)
		draw_trajectory_preview()

	state.space.debug_draw(pymunk.pygame_util.DrawOptions(screen))
	now = pygame.time.get_ticks()

	if state.ball_body is not None:
		bird_image = state.bird_fly_image if state.is_launched else state.bird_idle_image
		bird_rect = bird_image.get_rect(
			center=(round(state.ball_body.position.x), round(state.ball_body.position.y))
		)
		screen.blit(bird_image, bird_rect)

	for body, shapes in state.environment_objects:
		for shape in shapes:
			if shape.collision_type != settings.PIG_COLLISION_TYPE:
				continue
			laughing, next_change = state.pig_expression_states[shape]
			if now >= next_change:
				laughing = not laughing
				next_change = now + random.randint(settings.PIG_LAUGH_MIN_MS, settings.PIG_LAUGH_MAX_MS)
				state.pig_expression_states[shape] = (laughing, next_change)
			if laughing:
				frame_index = (now // settings.PIG_LAUGH_FRAME_MS) % len(state.pig_laugh_frames)
				pig_image = state.pig_laugh_frames[frame_index]
				if state.pig_laugh_sound is not None:
					state.pig_laugh_sound.play()

			else:
				pig_image = state.pig_image
			pig_rect = pig_image.get_rect(
				center=(round(body.position.x), round(body.position.y))
			)
			screen.blit(pig_image, pig_rect)

	active_explosions = []
	for position, started_at in state.explosions:
		age = now - started_at
		if age >= settings.EXPLOSION_DURATION:
			continue
		progress = age / settings.EXPLOSION_DURATION
		radius = int(settings.EXPLOSION_START_RADIUS + settings.EXPLOSION_GROW_RADIUS * progress)
		alpha = int(settings.EXPLOSION_MAX_ALPHA * (1 - progress))
		blast_surface = pygame.Surface(
			(radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA
		)
		pygame.draw.circle(
			blast_surface,
			(255, 150, 35, alpha),
			(radius + 2, radius + 2),
			radius,
			width=settings.EXPLOSION_RING_WIDTH,
		)
		screen.blit(
			blast_surface,
			(int(position[0] - radius - 2), int(position[1] - radius - 2)),
		)
		active_explosions.append((position, started_at))
	state.explosions = active_explosions
