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

space = pymunk.Space()
space.damping = 0.82
space.gravity = (0,700)
PIG_CATEGORY = 2
PIG_WOOD_CATEGORY = 4


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


def choose_spawn_cell(used_cells, min_distance=1.5):
  for _ in range(500):
    cell_x = random.randint(11, 15)
    cell_y = random.randint(4, 10)
    candidate = (cell_x, cell_y)

    if candidate in used_cells:
      continue

    ok = True
    for other in used_cells:
      dx = cell_x - other[0]
      dy = cell_y - other[1]
      if math.hypot(dx, dy) < min_distance:
        ok = False
        break

    if ok:
      used_cells.add(candidate)
      return candidate

  return None

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
environment_objects = []
environment_constraints = []


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

        cell = choose_spawn_cell(used_cells, min_distance=1.8)
        if cell is None:
          continue
        pos = cell_to_position(cell[0], cell[1])

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
   pig_body = None
   pig_shape = None


def create_bird():
  global ball_body, ball_shape, is_launched
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
  pig_shape.elasticity = 0.5
  pig_shape.friction = 0.5
  pig_shape.color = pig_color
  pig_shape.filter = pymunk.ShapeFilter(
      categories=PIG_CATEGORY, mask=0xFFFFFFFF ^ PIG_WOOD_CATEGORY
  )
  space.add(pig_body, pig_shape)
  environment_objects.append((pig_body, [pig_shape]))

def create_wood_block(pos):
    box_width = BLOCK_SIZE
    box_height = BLOCK_SIZE
    wall_thickness =  5
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
    wall_thickness = 5
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
    pig_shape.elasticity = 0.5
    pig_shape.friction = 0.5
    pig_shape.color = pig_color
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
  for frame in range(120):  
      # Apply damping 
      vx *= math.pow(damping, sim_dt)
      vy *= math.pow(damping, sim_dt)
      # Apply gravity
      vx += gx * sim_dt
      vy += gy * sim_dt
      # Advance position
      px += vx * sim_dt
      py += vy * sim_dt
      if py >= HEIGHT - 50:
          break
      if frame % 2 == 0:
          pygame.draw.circle(screen, (255, 255, 255), (int(px), int(py)), 3)

ground()
create_bird()
generate_level()
ball_shape.mass = 0.5


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
  
  # Validate ball pos
  if ball_body and not is_valid_position(ball_body.position):

    ball_body.position = ANCHOR_POS
    ball_body.velocity = (0, 0)

  pygame.display.flip()
  clock.tick(60)

pygame.quit()
sys.exit()