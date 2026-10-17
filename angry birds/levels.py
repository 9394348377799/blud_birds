import random

import pygame
import pymunk
import settings
from game_state import state


def cell_to_position(cell_x, cell_y):
	return (
		cell_x * settings.GRID_SIZE + settings.GRID_SIZE / 2,
		cell_y * settings.GRID_SIZE + settings.GRID_SIZE / 2,
	)




def _create_wood_shell(body):
	half_size = settings.BLOCK_SIZE / 2
	thickness = settings.BLOCK_SHELL_THICKNESS
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
	state.target_blocks.add(body)


def create_pig_wood_block(position):
	size = settings.BLOCK_SIZE
	mass = settings.BLOCK_MASS
	inertia = pymunk.moment_for_box(mass, (size, size))
	wood_body = pymunk.Body(
		mass=mass, moment=inertia, body_type=pymunk.Body.DYNAMIC
	)
	wood_body.position = position
	wood_shapes = _create_wood_shell(wood_body)

	pig_mass = settings.PIG_ATTACHED_MASS
	pig_inertia = pymunk.moment_for_circle(pig_mass, 0, 20)
	pig_body = pymunk.Body(
		mass=pig_mass, moment=pig_inertia, body_type=pymunk.Body.DYNAMIC
	)
	pig_body.position = (position[0], position[1] - settings.PIG_WOOD_OFFSET)
	pig_shape = pymunk.Circle(pig_body, 20)
	pig_shape.collision_type = settings.PIG_COLLISION_TYPE
	state.pig_expression_states[pig_shape] = (
		False, pygame.time.get_ticks() + random.randint(settings.PIG_LAUGH_MIN_MS, settings.PIG_LAUGH_MAX_MS)
	)
	pig_shape.elasticity = settings.PIG_ELASTICITY
	pig_shape.friction = settings.PIG_FRICTION
	pig_shape.color = settings.PIG_COLOR
	pig_shape.filter = pymunk.ShapeFilter(
		categories=settings.PIG_CATEGORY,
		mask=0xFFFFFFFF ^ settings.PIG_WOOD_CATEGORY,
	)

	slide = pymunk.SlideJoint(wood_body, pig_body, (0, 0), (0, 0), 0, settings.SLIDE_MAX_DISTANCE)
	slide.bias_coef = settings.SLIDE_BIAS
	slide.max_force = settings.SLIDE_MAX_FORCE
	spring = pymunk.DampedSpring(
		wood_body, pig_body, (0, 0), (0, 0), settings.SPRING_REST_LENGTH,
		stiffness=settings.SPRING_STIFFNESS, damping=settings.SPRING_DAMPING,
	)

	state.space.add(wood_body, *wood_shapes, pig_body, pig_shape, slide, spring)
	state.environment_objects.append((wood_body, wood_shapes))
	state.environment_objects.append((pig_body, [pig_shape]))
	state.target_blocks.add(wood_body)
	state.environment_constraints.extend((slide, spring))


def ground():
	body = pymunk.Body(body_type=pymunk.Body.STATIC)
	shape = pymunk.Segment(
		body, (0, settings.HEIGHT - settings.GROUND_HEIGHT), (settings.WIDTH, settings.HEIGHT - settings.GROUND_HEIGHT), 5
	)
	shape.elasticity = settings.BLOCK_ELASTICITY
	shape.friction = settings.BLOCK_FRICTION
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
	state.target_blocks.clear()
	state.pending_pig_deaths.clear()
	state.pig_expression_states.clear()
	state.shot_active = False
	state.settled_time = 0.0
	state.pig_body = None
	state.pig_shape = None


def generate_level(level_number=1):
    try:
        layout = settings.LEVEL_LAYOUTS[int(level_number)]
    except (KeyError, TypeError, ValueError) as error:
        print(f"[levels] unknown level {level_number!r}, using level 1 ({error})")
        layout = settings.LEVEL_LAYOUTS[1]

    destroy_environment()
    for cell_x, cell_y, block_type in layout:
        position = cell_to_position(cell_x, cell_y)
        if block_type == "wood":
            create_wood_block(position)
        else:
            create_pig_wood_block(position)


def reset_environment():
	generate_level()
