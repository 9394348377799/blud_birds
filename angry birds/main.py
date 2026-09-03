import math
import sys
import pygame
import pymunk
import pymunk.pygame_util

pygame.init()
WIDTH, HEIGHT = 1080, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pymunk Slingshot Demo")
clock = pygame.time.Clock()

space = pymunk.Space()
space.gravity = (0,450)


def is_valid_position(pos):
  return not (math.isnan(pos[0]) or math.isnan(pos[1]))  

#Anchor POS
ANCHOR_POS = (200, 400)

static_anchor = pymunk.Body(body_type=pymunk.Body.STATIC)
static_anchor.position = ANCHOR_POS

ball_body = None
ball_shape = None
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


create_bird()
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

        # 1. Switch to dynamic first
        ball_body.body_type = pymunk.Body.DYNAMIC 
        ball_body.mass = 0.5
        ball_body.inertia = pymunk.moment_for_circle(0.5, 0, 15)

        # 2. Set explicit launch velocity
        ball_body.velocity = (pull_vector[0] * 8, pull_vector[1] * 8)

        # 3. Update state flags last
        is_launched = True 
        is_dragging = False

  if is_dragging:
    mouse_pos = pygame.mouse.get_pos()
    dx = mouse_pos[0] - ANCHOR_POS[0]
    dy = mouse_pos[1] - ANCHOR_POS[1]
    dist = math.hypot(dx, dy)
    max_pull = 100
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


  screen.fill((240, 240, 240))

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
  # Validate ball position before drawing
  if ball_body and is_valid_position(ball_body.position):
    space.debug_draw(draw_options)
  elif ball_body and not is_valid_position(ball_body.position):
    # Reset position if it becomes invalid (NaN)
    ball_body.position = ANCHOR_POS
    ball_body.velocity = (0, 0)

  pygame.display.flip()
  clock.tick(60)

pygame.quit()
sys.exit()
