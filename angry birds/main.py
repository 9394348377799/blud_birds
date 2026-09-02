import math
import sys
import pygame
import pymunk
import pymunk.pygame_util

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pymunk Slingshot Demo")
clock = pygame.time.Clock()

space = pymunk.Space()
space.gravity = (0,0)  

#Anchor POS
ANCHOR_POS = (200, 400)

static_anchor = pymunk.Body(body_type=pymunk.Body.STATIC)
static_anchor.position = ANCHOR_POS


ball_body = None
ball_shape = None
is_dragging = False
is_launched = False


def create_ball():
  global ball_body, ball_shape, is_launched
  mass = 0.5
  radius = 15
  inertia = pymunk.moment_for_circle(mass, 0, radius)
  ball_body = pymunk.Body(mass, inertia)
  ball_body.position = ANCHOR_POS
  ball_shape = pymunk.Circle(ball_body, radius)
  ball_shape.elasticity = 0.7
  ball_shape.friction = 0.5
  space.add(ball_body, ball_shape)
  is_launched = False


# Spawn the first ball
create_ball()

# Main Game Loop
running = True
while running:
  ball_body.position = ANCHOR_POS if not is_launched else ball_body.position  
  dt = 1.0 / 60.0

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    elif event.type == pygame.using_mouse_down if hasattr(pygame, 'using_mouse_down') else event.type == pygame.MOUSEBUTTONDOWN:
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
        is_dragging = False
        is_launched = True
        ball_body.body_type = pymunk.Body.DYNAMIC 

        # Apply launch velocity based on pull-back distance (Slingshot effect)
        pull_vector = (
            ANCHOR_POS[0] - ball_body.position.x,
            ANCHOR_POS[1] - ball_body.position.y,
        )
        # Multiply by a scaling factor to increase launch speed
        ball_body.velocity = (pull_vector[0] * 8, pull_vector[1] * 8)

  if is_dragging:
    mouse_pos = pygame.mouse.get_pos()
    dx = mouse_pos[0] - ANCHOR_POS[0]
    dy = mouse_pos[1] - ANCHOR_POS[1]
    dist = math.hypot(dx, dy)
    max_pull = 100
    if dist > max_pull:
      dx = (dx / dist) * max_pull
      dy = (dy / dist) * max_pull
    ball_body.position = (ANCHOR_POS[0] + dx, ANCHOR_POS[1] + dy)
    ball_body.velocity = (0, 0)

  space.step(dt)


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
  space.debug_draw(draw_options)

  pygame.display.flip()
  clock.tick(60)

pygame.quit()
sys.exit()
