import math
import random
import sys
import pygame
import pymunk
import pymunk.pygame_util

pygame.init()
WIDTH, HEIGHT = 1080, 720
color = (0, 0, 0)
ground_color = (51, 0, 0)
bird_color = (51, 51, 255, 255)
pig_color = (254, 204, 153, 255)
wood_color = (150, 90, 40, 255)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("blud birds")
clock = pygame.time.Clock()
BLOCK_SIZE = 60
GRID_SIZE = BLOCK_SIZE
GRID_COLOR = (50, 50, 50)
BLOCK_MASS = 0.18
BLOCK_ELASTICITY = 0.5
BLOCK_FRICTION = 0.5
# New padding to make sure the spawns down collide with each other
SPAWN_PADDING = 16
MIN_CENTER_DISTANCE = BLOCK_SIZE + SPAWN_PADDING

space = pymunk.Space()
space.damping = 0.82
space.gravity = (0,700)
# Collision prevention
space.collision_slop = 0.05
space.collision_bias = 0.4
PIG_CATEGORY = 2
PIG_WOOD_CATEGORY = 4
PIG_COLLISION_TYPE = 10
PIG_DEATH_IMPULSE = 70
# Explosion parameters
EXPLOSION_RADIUS = 500
EXPLOSION_DURATION = 300


def is_valid_position(pos):
  return not (math.isnan(pos[0]) or math.isnan(pos[1]))


def snap_to_grid(pos):
  # Keep each block centered inside a single grid cell.
  return (
      (round(pos[0] / GRID_SIZE) * GRID_SIZE) + (GRID_SIZE / 2),
      (round(pos[1] / GRID_SIZE) * GRID_SIZE) + (GRID_SIZE / 2),
  )


def cell_to_position(cell_x, cell_y):
  return (
      (cell_x * GRID_SIZE) + (GRID_SIZE / 2),
      (cell_y * GRID_SIZE) + (GRID_SIZE / 2),
  )


def birdspolosion(position):
  explosions.append((position, pygame.time.get_ticks()))
  # Takes the shapes and bodies and applies an impuslse reaction to the bodies within the explosion radius.
  for body, shapes in environment_objects:
    if body.body_type != pymunk.Body.DYNAMIC:
      continue
    # Calculate the distance from the explosion centre from body position.
    offset = body.position - position
    distance = offset.length
    # If the distance is greater than the explosion radius, this will not act.
    if distance >= EXPLOSION_RADIUS:
      continue
    # Calculate the direction and strengh of the impulse applied.
    direction = offset.normalized() if distance > 0 else pymunk.Vec2d(0, -1)
    # Strength of the applied impulse
    strength = 25 * (1 - distance / EXPLOSION_RADIUS)
    body.apply_impulse_at_world_point(direction * strength, body.position)
    blocks_hit_by_bird.add(body)  



# Pair of colliding shapes and all data related to their collision.
def on_bird_block_collision(arbiter, collision_space, data):
  global explosion_triggered, pending_explosion
  if not is_launched or explosion_triggered or ball_body is None:
    return True

  collision_shapes = set(arbiter.shapes)
  hit_blocks = [
      body
      for body, shapes in environment_objects
      if len(shapes) > 1 and any(shape in collision_shapes for shape in shapes)
  ]
  if not hit_blocks:
    return True

# If the collision involves the bird, trigger the explosion.
  if ball_shape in collision_shapes:
    blocks_hit_by_bird.update(hit_blocks)
    explosion_triggered = True
    pending_explosion = tuple(ball_body.position)
  return True


def choose_spawn_cell(used_cells):
  for _ in range(500):
    cell_x = random.randint(11, 15)

    # Roll for a radndomly generated structure.
    roll = random.random()
    if roll < 0.7:
      cell_y = random.randint(8, 10)
    elif roll < 0.9:
      cell_y = random.randint(6, 7)
    else:
      cell_y = random.randint(4, 5)

    candidate = (cell_x, cell_y)

    if candidate in used_cells:
      continue

    # Allow higher blocks only if they have support underneath or are grounded.
    if cell_y >= 6:
      support_cell = (cell_x, cell_y + 1)
      if support_cell not in used_cells and cell_y < 8:
        continue

    candidate_pos = cell_to_position(cell_x, cell_y)
    ok = True
    for other in used_cells:
      other_pos = cell_to_position(other[0], other[1])
      dist = math.hypot(candidate_pos[0] - other_pos[0], candidate_pos[1] - other_pos[1])
      if dist < MIN_CENTER_DISTANCE:
        ok = False
        break

    if ok:
      used_cells.add(candidate)
      return candidate

# "ok" is used as a boolean flag to indicate whether the candidate cell is valid.

#Anchor POS
ANCHOR_POS = (175, 450)
PIG_POS = (800, 570)  # Positioned inside the hollow box

static_anchor = pymunk.Body(body_type=pymunk.Body.STATIC)
static_anchor.position = ANCHOR_POS

ball_body = None
ball_shape = None
pig_body = None
pig_shape = None
is_dragging = False
is_launched = False
# Explosion state variables
explosion_triggered = False
pending_explosion = None
explosions = []
environment_objects = []
environment_constraints = []
blocks_hit_by_bird = set()
pending_pig_deaths = set()

def blocks_breaking():
  for body, shapes in list(environment_objects):
    if body.body_type != pymunk.Body.DYNAMIC:
      continue
    if len(shapes) == 4 and body in blocks_hit_by_bird:
      speed = body.velocity.length
      if speed > 200:
        for constraint in list(environment_constraints):
          if constraint.a is body or constraint.b is body:
            space.remove(constraint)
            environment_constraints.remove(constraint)
        space.remove(body, *shapes)
        environment_objects.remove((body, shapes))
        blocks_hit_by_bird.discard(body)


def on_pig_impact(arbiter, collision_space, data):
  pig_shapes = [
      shape for shape in arbiter.shapes
      if shape.collision_type == PIG_COLLISION_TYPE
  ]
  if arbiter.total_impulse.length >= PIG_DEATH_IMPULSE:
    pending_pig_deaths.update(pig_shapes)


def pigs_dying():
  for pig_shape in pending_pig_deaths:
    pig_body = pig_shape.body
    for constraint in list(environment_constraints):
      if constraint.a is pig_body or constraint.b is pig_body:
        space.remove(constraint)
        environment_constraints.remove(constraint)
    space.remove(pig_body, pig_shape)
    environment_objects[:] = [
        (body, shapes) for body, shapes in environment_objects
        if pig_shape not in shapes
    ]
  pending_pig_deaths.clear()


def reset_bird():
    destroy_bird()
    create_bird()

def reset_environment():
    destroy_environment()
    create_pig_wood_block()
    create_wood_block()
    create_piggy()

def generate_level():
    destroy_environment()

    block_count = random.randint(2, 10)
    used_cells = set()

    for _ in range(block_count):
        block_type = random.choice(["wood", "pig_wood"])

        cell = choose_spawn_cell(used_cells)
        if cell is None:
          continue
        pos = cell_to_position(cell[0], cell[1])

        # Force the block to start on the ground
        pos = (pos[0], min(pos[1], HEIGHT - 120))

        if block_type == "wood":
            create_wood_block(pos)
        elif block_type == "pig_wood":
            create_pig_wood_block(pos)

def destroy_environment():
   global pig_body, pig_shape
   for constraint in environment_constraints:
     space.remove(constraint)
   environment_constraints.clear()
   for body, shapes in environment_objects:
     space.remove(body, *shapes)
   environment_objects.clear()
   blocks_hit_by_bird.clear()
   pig_body = None
   pig_shape = None


def create_bird():
  global ball_body, ball_shape, is_launched, explosion_triggered
  mass = 0.5
  radius = 15
  inertia = pymunk.moment_for_circle(mass, 0, radius)
  ball_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
  ball_body.position = ANCHOR_POS
  ball_shape = pymunk.Circle(ball_body, radius)
  ball_shape.elasticity = 0.7
  ball_shape.friction = 0.5
  ball_shape.color = bird_color
  space.add(ball_body, ball_shape)
  is_launched = False
  # Explosion state variables
  explosion_triggered = False

def destroy_bird():
  global ball_body, ball_shape, is_launched, is_dragging
  if ball_body and ball_shape:
      space.remove(ball_body, ball_shape)
      ball_body = None
      ball_shape = None
      is_launched = False
      is_dragging = False

def create_piggy(pos):
  global pig_body, pig_shape
  mass = 0.5
  radius = 20
  intertia = pymunk.moment_for_circle(mass, 0, radius)
  pig_body = pymunk.Body(mass=mass, moment=intertia, body_type=pymunk.Body.DYNAMIC)
  pig_body.position = pos
  pig_shape = pymunk.Circle(pig_body, 20)
  pig_shape.collision_type = PIG_COLLISION_TYPE
  pig_shape.elasticity = 0.5
  pig_shape.friction = 0.5
  pig_shape.color = pig_color
  # Collision filtering to prevent pig from colliding with wood block
  pig_shape.filter = pymunk.ShapeFilter(
      categories=PIG_CATEGORY, mask=0xFFFFFFFF ^ PIG_WOOD_CATEGORY
  )
  space.add(pig_body, pig_shape)
  environment_objects.append((pig_body, [pig_shape]))

def create_wood_block(pos):
    box_width = BLOCK_SIZE
    box_height = BLOCK_SIZE
    wall_thickness = 3.5
    mass = BLOCK_MASS

    inertia = pymunk.moment_for_box(
        mass, (box_width, box_height)
    )

    wood_body = pymunk.Body(
        mass=mass,
        moment=inertia,
        body_type=pymunk.Body.DYNAMIC
    )

    wood_body.moment = float("inf")
    wood_body.position = pos

    left = -box_width / 2
    right = box_width / 2
    top = -box_height / 2
    bottom = box_height / 2

    # Bottom
    bottom_shape = pymunk.Segment(
        wood_body,
        (left, bottom),
        (right, bottom),
        wall_thickness / 2
    )

    # Top
    top_shape = pymunk.Segment(
        wood_body,
        (left, top),
        (right, top),
        wall_thickness / 2
    )

    # Left
    left_shape = pymunk.Segment(
        wood_body,
        (left, top),
        (left, bottom),
        wall_thickness / 2
    )

    # Right
    right_shape = pymunk.Segment(
        wood_body,
        (right, top),
        (right, bottom),
        wall_thickness / 2
    )

    # Set properties
    for shape in [
        bottom_shape,
        top_shape,
        left_shape,
        right_shape
    ]:
        shape.elasticity = BLOCK_ELASTICITY
        shape.friction = BLOCK_FRICTION
        shape.color = wood_color

    # Add only the four walls
    space.add(
        wood_body,
        bottom_shape,
        top_shape,
        left_shape,
        right_shape
    )

    environment_objects.append((
        wood_body,
        [
            bottom_shape,
            top_shape,
            left_shape,
            right_shape
        ]
    ))

def create_pig_wood_block(pos):
    box_width = BLOCK_SIZE
    box_height = BLOCK_SIZE
    wall_thickness = 3.5
    mass = BLOCK_MASS

    inertia = pymunk.moment_for_box(
        mass, (box_width, box_height)
    )

    wood_body = pymunk.Body(
        mass=mass,
        moment=inertia,
        body_type=pymunk.Body.DYNAMIC
    )
    wood_body.position = pos

    left = -box_width / 2
    right = box_width / 2
    top = -box_height / 2
    bottom = box_height / 2

    # Bottom
    bottom_shape = pymunk.Segment(
        wood_body,
        (left, bottom),
        (right, bottom),
        wall_thickness / 2
    )

    # Top
    top_shape = pymunk.Segment(
        wood_body,
        (left, top),
        (right, top),
        wall_thickness / 2
    )

    # Left
    left_shape = pymunk.Segment(
        wood_body,
        (left, top),
        (left, bottom),
        wall_thickness / 2
    )

    # Right
    right_shape = pymunk.Segment(
        wood_body,
        (right, top),
        (right, bottom),
        wall_thickness / 2
    )

    pig_mass = 0.2
    pig_inertia = pymunk.moment_for_circle(pig_mass, 0, 20)
    pig_body = pymunk.Body(mass=pig_mass, moment=pig_inertia, body_type=pymunk.Body.DYNAMIC)
    pig_body.position = (pos[0], pos[1] - 10)
    pig_shape = pymunk.Circle(pig_body, 20)
    pig_shape.collision_type = PIG_COLLISION_TYPE
    pig_shape.elasticity = 0.5
    pig_shape.friction = 0.5
    pig_shape.color = pig_color
    #Collision filtering to prevent pig from colliding with wood block
    pig_shape.filter = pymunk.ShapeFilter(
        categories=PIG_CATEGORY,
        mask=0xFFFFFFFF ^ PIG_WOOD_CATEGORY
    )

    for shape in [
        bottom_shape,
        top_shape,
        left_shape,
        right_shape,
    ]:
        shape.elasticity = BLOCK_ELASTICITY
        shape.friction = BLOCK_FRICTION
        shape.color = wood_color

    slide = pymunk.SlideJoint(
        wood_body,
        pig_body,
        (0, 0),
        (0, 0),
        0,
        100,
    )
    slide.bias_coef = 0.08
    slide.max_force = 1800

    spring = pymunk.DampedSpring(
        wood_body,
        pig_body,
        (0, 0),
        (0, 0),
        # Give the pig room to move
        rest_length=18,
        stiffness=22,
        damping=4,
    )

    space.add(
        wood_body,
        bottom_shape,
        top_shape,
        left_shape,
        right_shape,
        pig_body,
        pig_shape,
        slide,
        spring,
    )

    environment_objects.append((wood_body,[bottom_shape, top_shape, left_shape, right_shape]))
    environment_objects.append((pig_body,[pig_shape]))
    environment_constraints.append(slide)
    environment_constraints.append(spring)

def ground():
  ground_body = pymunk.Body(body_type=pymunk.Body.STATIC)
  ground_shape = pymunk.Segment(ground_body, (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 5)
  ground_shape.elasticity = 0.5
  ground_shape.friction = 1.0
  ground_shape.color = (*ground_color, 255)
  space.add(ground_body, ground_shape)


def draw_grid():
  for x in range(0, WIDTH + GRID_SIZE, GRID_SIZE):
    pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
  for y in range(0, HEIGHT + GRID_SIZE, GRID_SIZE):
    pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)


def draw_trajectory_preview():
  if not ball_body or not is_dragging:
    return

  pull_vector = (
      ANCHOR_POS[0] - ball_body.position.x,
      ANCHOR_POS[1] - ball_body.position.y,
  )

  px, py = ball_body.position.x, ball_body.position.y
  vx = pull_vector[0] * 8
  vy = pull_vector[1] * 8
  gx, gy = space.gravity
  sim_dt = 1.0 / 60.0  
  damping = space.damping
  for frame in range(250):  
      # Apply damping 
      vx *= math.pow(damping, sim_dt)
      vy *= math.pow(damping, sim_dt)
      # Apply gravity
      vx += gx * sim_dt
      vy += gy * sim_dt
      # Advance position
      px += vx * sim_dt
      py += vy * sim_dt
      if py >= HEIGHT - 120:
          break
      if frame % 4 == 0:
          pygame.draw.circle(screen, (255, 255, 255), (int(px), int(py)), 3)

ground()
create_bird()
generate_level()
ball_shape.mass = 0.5
# Set up collision handler for bird and block collisions
space.on_collision(
  None,
  None,
  begin=on_bird_block_collision,
  post_solve=on_pig_impact,
)


# Main Game Loop
running = True
while running:
  dt = 1.0 / 60.0

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_r:
        reset_bird()
        ball_shape.mass = 0.5
      elif event.key == pygame.K_e:
        generate_level()


    elif event.type == pygame.MOUSEBUTTONDOWN:
      if not is_launched and ball_body:
        mouse_pos = pygame.mouse.get_pos()
        dist = math.hypot(
            mouse_pos[0] - ball_body.position.x,
            mouse_pos[1] - ball_body.position.y,
        )
        if dist < 30:
          is_dragging = True
          ball_body.body_type = (  
              pymunk.Body.KINEMATIC
          )

    elif event.type == pygame.MOUSEBUTTONUP:
      if is_dragging:
        pull_vector = (
            ANCHOR_POS[0] - ball_body.position.x,
            ANCHOR_POS[1] - ball_body.position.y,
        )

        #Switch to dynamic first
        ball_body.body_type = pymunk.Body.DYNAMIC 
        ball_body.mass = 0.5
        ball_body.inertia = pymunk.moment_for_circle(0.5, 0, 15)

        #Set explicit launch velocity
        ball_body.velocity = (pull_vector[0] * 8, pull_vector[1] * 8)

        #Update state flags last
        is_launched = True 
        is_dragging = False

  if is_dragging:
    mouse_pos = pygame.mouse.get_pos()
    dx = mouse_pos[0] - ANCHOR_POS[0]
    dy = mouse_pos[1] - ANCHOR_POS[1]
    dist = math.hypot(dx, dy)
    max_pull = 125
    if dist > max_pull and dist > 0:
      dx = (dx / dist) * max_pull
      dy = (dy / dist) * max_pull
    new_pos = (ANCHOR_POS[0] + dx, ANCHOR_POS[1] + dy)
    if is_valid_position(new_pos):
      ball_body.position = new_pos
      ball_body.velocity = (0, 0)  

  space.step(dt)
  blocks_breaking()
  pigs_dying()
  # Handle pending explosion
  if pending_explosion is not None:
    birdspolosion(pending_explosion)
    pending_explosion = None

  if ball_body and is_launched:
    if ball_body.position.y > HEIGHT +100 or ball_body.position.x > WIDTH + 100 or ball_body.position.x < -100:
      destroy_bird()


  screen.fill(color)
  draw_grid()

  if is_dragging:
    pygame.draw.line(
        screen,
        (100, 100, 100),
        ANCHOR_POS,
        (int(ball_body.position.x), int(ball_body.position.y)),
        4,
    )
    draw_trajectory_preview()

  # Render Pymunk objects via debug drawer
  draw_options = pymunk.pygame_util.DrawOptions(screen)
  space.debug_draw(draw_options)

# Render explosions
  now = pygame.time.get_ticks()
  active_explosions = []
  for position, started_at in explosions:
    age = now - started_at
    if age >= EXPLOSION_DURATION:
      continue
    progress = age / EXPLOSION_DURATION
    radius = int(12 + 58 * progress)
    alpha = int(220 * (1 - progress))
    blast_surface = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(
        blast_surface,
        (255, 150, 35, alpha),
        (radius + 2, radius + 2),
        radius,
        width=4,
    )
    screen.blit(blast_surface, (int(position[0] - radius - 2), int(position[1] - radius - 2)))
    active_explosions.append((position, started_at))
  explosions = active_explosions
  
  # Validate ball pos
  if ball_body and not is_valid_position(ball_body.position):

    ball_body.position = ANCHOR_POS
    ball_body.velocity = (0, 0)

  pygame.display.flip()
  clock.tick(60)

pygame.quit()
sys.exit()