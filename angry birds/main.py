import math
import sys
import pygame
import pymunk
import pymunk.pygame_util

pygame.init()
WIDTH, HEIGHT = 1080, 720
color = (0, 0, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pymunk Slingshot Demo")
clock = pygame.time.Clock()

space = pymunk.Space()
space.damping = 0.7
space.gravity = (0,900)
PIG_CATEGORY = 2
PIG_WOOD_CATEGORY = 4


def is_valid_position(pos):
  return not (math.isnan(pos[0]) or math.isnan(pos[1]))  

#Anchor POS
ANCHOR_POS = (175, 450)
PIG_POS = (800, 550)  # Positioned inside the hollow box

static_anchor = pymunk.Body(body_type=pymunk.Body.STATIC)
static_anchor.position = ANCHOR_POS

ball_body = None
ball_shape = None
pig_body = None
pig_shape = None
is_dragging = False
is_launched = False

def reset_game():
  global ball_body, ball_shape, pig_body, pig_shape, is_dragging, is_launched
  destroy_bird()
  if pig_body and pig_shape:
      space.remove(pig_body, pig_shape)
      pig_body = None
      pig_shape = None
  create_bird()
  create_piggy()
  is_dragging = False
  is_launched = False

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

def create_piggy():
  global pig_body, pig_shape
  mass = 0.75
  radius = 20
  intertia = pymunk.moment_for_circle(mass, 0, radius)
  pig_body = pymunk.Body(mass=mass, moment=intertia, body_type=pymunk.Body.DYNAMIC)
  pig_body.position = (PIG_POS[0], PIG_POS[1])
  pig_shape = pymunk.Circle(pig_body, 20)
  pig_shape.elasticity = 0.5
  pig_shape.friction = 0.5
  pig_shape.filter = pymunk.ShapeFilter(
      categories=PIG_CATEGORY, mask=0xFFFFFFFF ^ PIG_WOOD_CATEGORY
  )
  space.add(pig_body, pig_shape)

def create_wood_block():
  #box dim
  box_width = 60
  box_height = 60
  wall_thickness = 5
  mass = 0.26  # Mass for the hollow box
  

  inertia = pymunk.moment_for_box(mass, (box_width, box_height))
  
  wood_body = pymunk.Body(mass=mass, moment=inertia, body_type=pymunk.Body.DYNAMIC)
  wood_body.moment = float("inf")
  wood_body.position = (PIG_POS[0], PIG_POS[1] + 100)

  left = -box_width / 2
  right = box_width / 2
  top = -box_height / 2
  bottom = box_height / 2
  
  #wall segments
  # Bottom wall
  bottom_shape = pymunk.Segment(wood_body, (left, bottom), (right, bottom), wall_thickness / 2)
  bottom_shape.elasticity = 0.5
  bottom_shape.friction = 0.5
  space.add(wood_body, bottom_shape)
  
  # Top wall
  top_shape = pymunk.Segment(wood_body, (left, top), (right, top), wall_thickness / 2)
  top_shape.elasticity = 0.5
  top_shape.friction = 0.5
  space.add(top_shape)
  
  # Left wall
  left_shape = pymunk.Segment(wood_body, (left, top), (left, bottom), wall_thickness / 2)
  left_shape.elasticity = 0.5
  left_shape.friction = 0.5
  space.add(left_shape)
  
  # Right wall
  right_shape = pymunk.Segment(wood_body, (right, top), (right, bottom), wall_thickness / 2)
  right_shape.elasticity = 0.5
  right_shape.friction = 0.5
  space.add(right_shape)
  space.add(pymunk.Poly.create_box(wood_body, (box_width, box_height)))

def create_pig_wood_block():
  #box dim
  box_width = 60
  box_height = 60
  wall_thickness = 5
  mass = 0.26  # Mass for the hollow box
  

  inertia = pymunk.moment_for_box(mass, (box_width, box_height))
  
  wood_body = pymunk.Body(mass=mass, moment=inertia, body_type=pymunk.Body.DYNAMIC)
  wood_body.moment = float("inf")
  wood_body.position = (PIG_POS[0], PIG_POS[1])

  left = -box_width / 2
  right = box_width / 2
  top = -box_height / 2
  bottom = box_height / 2
  
  #wall segments
  # Bottom wall
  bottom_shape = pymunk.Segment(wood_body, (left, bottom), (right, bottom), wall_thickness / 2)
  bottom_shape.elasticity = 0.5
  bottom_shape.friction = 0.5
  space.add(wood_body, bottom_shape)
  
  # Top wall
  top_shape = pymunk.Segment(wood_body, (left, top), (right, top), wall_thickness / 2)
  top_shape.elasticity = 0.5
  top_shape.friction = 0.5
  space.add(top_shape)
  
  # Left wall
  left_shape = pymunk.Segment(wood_body, (left, top), (left, bottom), wall_thickness / 2)
  left_shape.elasticity = 0.5
  left_shape.friction = 0.5
  space.add(left_shape)
  
  # Right wall
  right_shape = pymunk.Segment(wood_body, (right, top), (right, bottom), wall_thickness / 2)
  right_shape.elasticity = 0.5
  right_shape.friction = 0.5
  space.add(right_shape)
  collision_shape = pymunk.Poly.create_box(wood_body, (box_width, box_height))
  collision_shape.filter = pymunk.ShapeFilter(
      categories=PIG_WOOD_CATEGORY, mask=0xFFFFFFFF ^ PIG_CATEGORY
  )
  space.add(collision_shape)
  

def ground():
  ground_body = pymunk.Body(body_type=pymunk.Body.STATIC)
  ground_shape = pymunk.Segment(ground_body, (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 5)
  ground_shape.elasticity = 0.5
  ground_shape.friction = 1.0
  space.add(ground_body, ground_shape)

ground()
create_bird()
create_pig_wood_block()
create_wood_block()
create_piggy()
ball_shape.mass = 0.5


# Main Game Loop
running = True
while running:
  dt = 1.0 / 60.0

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

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

  if is_dragging:
    pygame.draw.line(
        screen,
        (100, 100, 100),
        ANCHOR_POS,
        (int(ball_body.position.x), int(ball_body.position.y)),
        4,
    )

      
  # Render Pymunk objects via debug drawer
  draw_options = pymunk.pygame_util.DrawOptions(screen)
  space.debug_draw(draw_options)
  
  # Validate ball position if it exists
  if ball_body and not is_valid_position(ball_body.position):

    ball_body.position = ANCHOR_POS
    ball_body.velocity = (0, 0)

  pygame.display.flip()
  clock.tick(60)

pygame.quit()
sys.exit()