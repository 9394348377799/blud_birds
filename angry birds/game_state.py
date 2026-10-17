"""Shared mutable game state."""
import pymunk
import settings


class GameState:
	"""Container for all runtime state the game needs."""
	def __init__(self):
		"""Create the physics space and initialise every state attribute."""
		self.space = pymunk.Space()
		self.space.damping = 0.82
		self.space.gravity = (0, 700)
		self.space.collision_slop = 0.05
		self.space.collision_bias = 0.4

		self.screen = None
		self.background_image = None
		self.bird_idle_image = None
		self.bird_fly_image = None
		self.pig_image = None
		self.pig_laugh_frames = []
		self.bird_launch_sound = None
		self.pig_death_sound = None
		self.ui_manager = None
		self.start_button = None
		self.level_buttons = {}
		self.menu_button = None
		self.selected_level = None

		self.space.damping = settings.DAMPING
		self.space.gravity = settings.GRAVITY
		self.space.collision_slop = settings.COLLISION_SLOP
		self.space.collision_bias = settings.COLLISION_BIAS


		self.ball_body = None
		self.ball_shape = None
		self.pig_body = None
		self.pig_shape = None
		self.static_anchor = None

		self.is_dragging = False
		self.is_launched = False
		self.explosion_triggered = False
		self.pending_explosion = None
		self.explosions = []
		self.environment_objects = []
		self.environment_constraints = []
		self.blocks_hit_by_bird = set()
		self.pending_pig_deaths = set()
		self.pig_expression_states = {}
		self.target_blocks = set()
		self.game_state = "menu"
		self.attempts_left = 3
		self.shot_active = False
		self.settled_time = 0.0


state = GameState()
