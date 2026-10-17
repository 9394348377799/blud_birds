"""Physics rules: explosions, collisions, breaking blocks and shot settling."""
import math
import pygame
import pymunk
import settings
from characters import destroy_bird
from game_state import state


def is_valid_position(position):
	"""Return False when a position contains NaN."""
	return not (math.isnan(position[0]) or math.isnan(position[1]))


def trigger_explosion(position):
	"""Push nearby dynamic bodies away from the blast and queue the visual."""
	state.explosions.append((position, pygame.time.get_ticks()))
	for body, _shapes in state.environment_objects:
		if body.body_type != pymunk.Body.DYNAMIC:
			continue
		offset = body.position - position
		distance = offset.length
		if distance >= settings.EXPLOSION_RADIUS:
			continue
		direction = offset.normalized() if distance > 0 else pymunk.Vec2d(0, -1)
		strength = settings.EXPLOSION_STRENGTH * (1 - distance / settings.EXPLOSION_RADIUS)
		body.apply_impulse_at_world_point(direction * strength, body.position)
		state.blocks_hit_by_bird.add(body)


def on_bird_block_collision(arbiter, collision_space, data):
	"""Mark the first block the bird hits and arm the explosion."""
	if (
		not state.is_launched
		or state.explosion_triggered
		or state.ball_body is None
	):
		return True

	collision_shapes = set(arbiter.shapes)
	hit_blocks = [
		body
		for body, shapes in state.environment_objects
		if len(shapes) > 1 and any(shape in collision_shapes for shape in shapes)
	]
	if state.ball_shape in collision_shapes and hit_blocks:
		state.blocks_hit_by_bird.update(hit_blocks)
		state.explosion_triggered = True
		state.pending_explosion = tuple(state.ball_body.position)
	return True


def blocks_breaking():
	"""Remove wood blocks the bird hit that are moving faster than the break speed."""
	for body, shapes in list(state.environment_objects):
		if body.body_type != pymunk.Body.DYNAMIC:
			continue
		if len(shapes) == 4 and body in state.blocks_hit_by_bird:
			if body.velocity.length > 200:
				for constraint in list(state.environment_constraints):
					if constraint.a is body or constraint.b is body:
						state.space.remove(constraint)
						state.environment_constraints.remove(constraint)
				state.space.remove(body, *shapes)
				state.environment_objects.remove((body, shapes))
				state.blocks_hit_by_bird.discard(body)
				state.target_blocks.discard(body)


def scene_is_slow():
	"""Return True when every dynamic body has effectively stopped."""
	bodies = [body for body, _shapes in state.environment_objects]
	if state.ball_body is not None:
		bodies.append(state.ball_body)
	return all(
		body.body_type != pymunk.Body.DYNAMIC
		or (body.velocity.length < 10 and abs(body.angular_velocity) < 0.5)
		for body in bodies
	)


def finish_shot():
	"""End the shot, then decide win, loss, or load the next bird."""
	if not state.shot_active:
		return

	state.shot_active = False
	state.settled_time = 0.0
	destroy_bird()
	if not state.target_blocks:
		state.game_state = "won"
	elif state.attempts_left <= 0:
		state.game_state = "lost"
	else:
		from characters import create_bird

		create_bird()


def on_pig_impact(arbiter, collision_space, data):
	"""Queue pigs that took a hard enough impact for removal."""
	pig_shapes = [
		shape for shape in arbiter.shapes
		if shape.collision_type == settings.PIG_COLLISION_TYPE
	]
	if arbiter.total_impulse.length >= settings.PIG_DEATH_IMPULSE:
		state.pending_pig_deaths.update(pig_shapes)


def pigs_dying():
	"""Remove queued pigs, their constraints, and play the death sound."""
	for pig_shape in list(state.pending_pig_deaths):
		pig_body = pig_shape.body
		for constraint in list(state.environment_constraints):
			if constraint.a is pig_body or constraint.b is pig_body:
				state.space.remove(constraint)
				state.environment_constraints.remove(constraint)
			if state.pig_death_sound is not None:
				state.pig_death_sound.play()
		state.space.remove(pig_body, pig_shape)
		state.environment_objects[:] = [
			(body, shapes)
			for body, shapes in state.environment_objects
			if pig_shape not in shapes
		]
		state.pig_expression_states.pop(pig_shape, None)
	state.pending_pig_deaths.clear()


def setup_collision_handlers():
	"""Register the collision handlers on the physics space."""
	state.space.on_collision(
		None,
		None,
		begin=on_bird_block_collision,
		post_solve=on_pig_impact,
	)


def update(dt):
	"""Advance the simulation one frame and run the per-frame rules."""
	if state.is_dragging:
		mouse_x, mouse_y = pygame.mouse.get_pos()
		delta_x = mouse_x - settings.ANCHOR_POS[0]
		delta_y = mouse_y - settings.ANCHOR_POS[1]
		distance = math.hypot(delta_x, delta_y)
		max_pull = settings.MAX_PULL
		if distance > max_pull and distance > 0:
			delta_x = delta_x / distance * max_pull
			delta_y = delta_y / distance * max_pull
		new_position = (
			settings.ANCHOR_POS[0] + delta_x,
			settings.ANCHOR_POS[1] + delta_y,
		)
		if is_valid_position(new_position):
			state.ball_body.position = new_position
			state.ball_body.velocity = (0, 0)

	state.space.step(dt)
	blocks_breaking()
	pigs_dying()
	if state.pending_explosion is not None:
		trigger_explosion(state.pending_explosion)
		state.pending_explosion = None

	if state.ball_body and state.is_launched:
		position = state.ball_body.position
		if (
			position.y > settings.HEIGHT + settings.OFFSCREEN_MARGIN
			or position.x > settings.WIDTH + settings.OFFSCREEN_MARGIN
			or position.x < -settings.OFFSCREEN_MARGIN
		):
			destroy_bird()

	if state.ball_body and not is_valid_position(state.ball_body.position):
		state.ball_body.position = settings.ANCHOR_POS
		state.ball_body.velocity = (0, 0)

	if state.shot_active:
		if scene_is_slow():
			state.settled_time += dt
		else:
			state.settled_time = 0.0
		if state.settled_time >= settings.SETTLE_TIME:
			finish_shot()
