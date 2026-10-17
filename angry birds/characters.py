import random

import pygame
import pymunk
import settings
from game_state import state


def create_bird():
    """Creation and removal of the bird and pig physics bodies."""
    radius = settings.BIRD_RADIUS
    state.ball_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    state.ball_body.position = settings.ANCHOR_POS
    state.ball_shape = pymunk.Circle(state.ball_body, radius)
    state.ball_shape.elasticity = settings.BIRD_ELASTICITY
    state.ball_shape.friction = settings.BIRD_FRICTION
    state.ball_shape.color = settings.BIRD_COLOR
    state.space.add(state.ball_body, state.ball_shape)
    state.is_launched = False
    state.explosion_triggered = False


def destroy_bird():
    """Remove the bird from the physics space, if one exists."""
    if state.ball_body is not None and state.ball_shape is not None:
        state.space.remove(state.ball_body, state.ball_shape)
        state.ball_body = None
        state.ball_shape = None
        state.is_launched = False
        state.is_dragging = False


def reset_bird():
    """Destroy and recreate the bird at the anchor."""
    destroy_bird()
    create_bird()


def create_piggy(position):
    """Create a free-standing pig at the given position and track it as a target."""
    mass = settings.PIG_MASS
    radius = settings.PIG_RADIUS
    inertia = pymunk.moment_for_circle(mass, 0, radius)
    pig_body = pymunk.Body(mass=mass, moment=inertia, body_type=pymunk.Body.DYNAMIC)
    pig_body.position = position
    pig_shape = pymunk.Circle(pig_body, radius)
    pig_shape.collision_type = settings.PIG_COLLISION_TYPE
    state.pig_expression_states[pig_shape] = (
        False,
        pygame.time.get_ticks() + random.randint(2000, 5000),
    )
    pig_shape.elasticity = settings.PIG_ELASTICITY
    pig_shape.friction = settings.PIG_FRICTION
    pig_shape.color = settings.PIG_COLOR
    pig_shape.filter = pymunk.ShapeFilter(
        categories=settings.PIG_CATEGORY,
        mask=0xFFFFFFFF ^ settings.PIG_WOOD_CATEGORY,
    )
    state.space.add(pig_body, pig_shape)
    state.environment_objects.append((pig_body, [pig_shape]))
    state.pig_body = pig_body
    state.pig_shape = pig_shape
