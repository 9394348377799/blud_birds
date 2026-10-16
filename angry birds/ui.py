import pygame
import pygame_gui

import settings
from characters import reset_bird
from game_state import state
from levels import generate_level


def initialize():
	state.ui_manager = pygame_gui.UIManager((settings.WIDTH, settings.HEIGHT))
	state.level_buttons = {
		level_number: pygame_gui.elements.UIButton(
			relative_rect=pygame.Rect(
				(settings.WIDTH // 2 - 75, settings.HEIGHT // 2 - 90 + (level_number - 1) * 70),
				(150, 50),
			),
			text=f"Level {level_number}",
			manager=state.ui_manager,
		)
		for level_number in range(1, 4)
	}
	state.menu_button = pygame_gui.elements.UIButton(
		relative_rect=pygame.Rect((settings.WIDTH - 120, 50), (110, 30)),
		text="Main Menu",
		manager=state.ui_manager,
	)
	state.start_button = pygame_gui.elements.UIButton(
		relative_rect=pygame.Rect(
			(settings.WIDTH // 2 - 75, settings.HEIGHT // 2 - 25), (150, 50)
		),
		text="Start Game",
		manager=state.ui_manager,
	)
	state.menu_button.hide()
	for button in state.level_buttons.values():
		button.hide()


def process_event(event):
	ui_consumed = state.ui_manager.process_events(event)
	if event.type == pygame_gui.UI_BUTTON_PRESSED:
		if event.ui_element == state.start_button:
			state.game_state = "level_select"
			state.start_button.hide()
			state.menu_button.show()
			for button in state.level_buttons.values():
				button.show()
		elif event.ui_element in state.level_buttons.values():
			level_number = next(
				number
				for number, button in state.level_buttons.items()
				if event.ui_element == button
			)
			state.selected_level = level_number
			generate_level(level_number)
			state.attempts_left = 3
			reset_bird()
			state.ball_shape.mass = 0.5
			state.game_state = "playing"
			for button in state.level_buttons.values():
				button.hide()
		elif event.ui_element == state.menu_button:
			state.game_state = "menu"
			state.start_button.show()
			state.menu_button.hide()
			for button in state.level_buttons.values():
				button.hide()
	return ui_consumed


def update_and_draw(time_delta):
	state.ui_manager.update(time_delta)
	state.ui_manager.draw_ui(state.screen)
