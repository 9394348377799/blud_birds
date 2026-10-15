import math
import random

import pygame
import pymunk

import settings
from game_state import state


def snap_to_grid(position):
	return (
		round(position[0] / settings.GRID_SIZE) * settings.GRID_SIZE + settings.GRID_SIZE / 2,
		round(position[1] / settings.GRID_SIZE) * settings.GRID_SIZE + settings.GRID_SIZE / 2,
	)


def cell_to_position(cell_x, cell_y):
	return (
		cell_x * settings.GRID_SIZE + settings.GRID_SIZE / 2,
		cell_y * settings.GRID_SIZE + settings.GRID_SIZE / 2,
	)


def choose_spawn_cell(used_cells):
	for _ in range(500):
		cell_x = random.randint(11, 15)
		roll = random.random()
		if roll < 0.7:
			cell_y = random.randint(8, 10)
		elif roll < 0.9:
			cell_y = random.randint(6, 7)
		else:
			cell_y = 5

		candidate = (cell_x, cell_y)
		if candidate in used_cells:
			continue

		if cell_y >= 6:
			support_cell = (cell_x, cell_y + 1)
			if support_cell not in used_cells and cell_y < 8:
				continue

		candidate_position = cell_to_position(cell_x, cell_y)
		if any(
			math.dist(candidate_position, cell_to_position(*other))
			< settings.MIN_CENTER_DISTANCE
			for other in used_cells
		):
			continue

		used_cells.add(candidate)
		return candidate
	return None


def _create_wood_shell(body):
	half_size = settings.BLOCK_SIZE / 2
	thickness = 3.5 / 2
	left, right = -half_size, half_size
	top, bottom = -half_size, half_size
	shapes = [
		pymunk.Segment(body, (left, bottom), (right, bottom), thickness),
		pymunk.Segment(body, (left, top), (right, top), thickness),
		pymunk.Segment(body, (left, top), (left, bottom), thickness),
		pymunk.Segment(body, (right, top), (right, bottom), thickness),
	]
	for shape in shapes:
		shape.elasticity = settings.BLOCK_ELASTICITY
		shape.friction = settings.BLOCK_FRICTION
		shape.color = settings.WOOD_COLOR
	return shapes


def create_wood_block(position):
	size = settings.BLOCK_SIZE
	mass = settings.BLOCK_MASS
	inertia = pymunk.moment_for_box(mass, (size, size))
	body = pymunk.Body(mass=mass, moment=inertia, body_type=pymunk.Body.DYNAMIC)
	body.moment = float("inf")
	body.position = position
	shapes = _create_wood_shell(body)
	state.space.add(body, *shapes)
	state.environment_objects.append((body, shapes))


def create_pig_wood_block(position):
	size = settings.BLOCK_SIZE
	mass = settings.BLOCK_MASS
	inertia = pymunk.moment_for_box(mass, (size, size))
	wood_body = pymunk.Body(
		mass=mass, moment=inertia, body_type=pymunk.Body.DYNAMIC
	)
	wood_body.position = position
	wood_shapes = _create_wood_shell(wood_body)

	pig_mass = 0.2
	pig_inertia = pymunk.moment_for_circle(pig_mass, 0, 20)
	pig_body = pymunk.Body(
		mass=pig_mass, moment=pig_inertia, body_type=pymunk.Body.DYNAMIC
	)
	pig_body.position = (position[0], position[1] - 10)
	pig_shape = pymunk.Circle(pig_body, 20)
	pig_shape.collision_type = settings.PIG_COLLISION_TYPE
	state.pig_expression_states[pig_shape] = (
		False, pygame.time.get_ticks() + random.randint(2000, 5000)
	)
	pig_shape.elasticity = 0.5
	pig_shape.friction = 0.5
	pig_shape.color = settings.PIG_COLOR
	pig_shape.filter = pymunk.ShapeFilter(
		categories=settings.PIG_CATEGORY,
		mask=0xFFFFFFFF ^ settings.PIG_WOOD_CATEGORY,
	)

	slide = pymunk.SlideJoint(wood_body, pig_body, (0, 0), (0, 0), 0, 100)
	slide.bias_coef = 0.08
	slide.max_force = 1800
	spring = pymunk.DampedSpring(
		wood_body, pig_body, (0, 0), (0, 0), rest_length=18,
		stiffness=22, damping=4,
	)

	state.space.add(wood_body, *wood_shapes, pig_body, pig_shape, slide, spring)
	state.environment_objects.append((wood_body, wood_shapes))
	state.environment_objects.append((pig_body, [pig_shape]))
	state.environment_constraints.extend((slide, spring))


def ground():
	body = pymunk.Body(body_type=pymunk.Body.STATIC)
	shape = pymunk.Segment(
		body, (0, settings.HEIGHT - 50), (settings.WIDTH, settings.HEIGHT - 50), 5
	)
	shape.elasticity = 0.5
	shape.friction = 1.0
	shape.color = (*settings.GROUND_COLOR, 255)
	state.space.add(body, shape)


def destroy_environment():
	for constraint in state.environment_constraints:
		state.space.remove(constraint)
	state.environment_constraints.clear()
	for body, shapes in state.environment_objects:
		state.space.remove(body, *shapes)
	state.environment_objects.clear()
	state.blocks_hit_by_bird.clear()
	state.pending_pig_deaths.clear()
	state.pig_expression_states.clear()
	state.pig_body = None
	state.pig_shape = None


def generate_level():
	destroy_environment()
	used_cells = set()
	for _ in range(random.randint(2, 10)):
		cell = choose_spawn_cell(used_cells)
		if cell is None:
			continue
		position = cell_to_position(*cell)
		position = (position[0], min(position[1], settings.HEIGHT - 120))
		if random.choice(("wood", "pig_wood")) == "wood":
			create_wood_block(position)
		else:
			create_pig_wood_block(position)


def reset_environment():
	generate_level()
