import tkinter as tk
from tkinter import ttk
import random
import pygame
from pathlib import Path
from PIL import Image, ImageTk
from tkinter import Toplevel
import threading
import sys




class App:
    BASE_DIR = Path(__file__).resolve().parent
    SOUND_FILE = BASE_DIR / 'fart.mp3'

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Fart Application")
        self.root.geometry("300x250")
        self.root.resizable(False, False)
        self.root.configure(bg="#E69797")

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.TOP, pady=10)


        self.main_canvas = tk.Canvas(self.root, background="#E69797")

        self.init_game_state()

        self.fart_sound = None
        try:
            pygame.mixer.init()
            self.fart_sound = pygame.mixer.Sound(str(self.SOUND_FILE))
        except Exception as e:
            print(f"Unable to initialize sound: {e}")

    def fart(self):
        if self.fart_sound:
            self.fart_sound.play()
        else:
            print("Fart sound not available")

    

    def init_game_state(self):
        self.fart_block = self.main_canvas.create_rectangle(100, 100, 200, 150, fill="#934361")
        self.main_canvas.pack(fill=tk.BOTH, expand=True)

        self.score = 0
        self.score_text = self.main_canvas.create_text(150, 50,
            text="Score: 0",
            font=("Arial", 16),
            fill="#000000")

        self.score_button = tk.Button(self.control_frame, 
        bg="#E69797", 
        highlightbackground="#E69797", 
        highlightthickness=0, 
        activebackground="#E69797", 
        relief=tk.FLAT, 
        bd=0, 
        text=f"Fart!", 
        command=self.increase_score)
        
        self.score_button.pack(
        pady=0, 
        side=tk.BOTTOM,)

        # try to load highscore from a file in the project directory
        PATH = self.BASE_DIR / 'highscore.txt'
        try:
            with open(PATH, 'r') as f:
                file = f.readlines()
                self.highscore = int(file[0].strip())
                self.highscore_holder = file[1].strip()
            self.fileload = True
        except Exception:
            self.highscore = 0
            self.highscore_holder = "None"
            self.fileload = False


    def increase_score(self):
        self.fart()
        self.score += 1
        print(f"new score= {self.score}")
        self.main_canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
        # change fart block color
        self.main_canvas.itemconfig(self.fart_block, fill=random.choice(["#934361", "#889343", "#439376", "#4E4393"]))
        # update the score button label
        try:
            self.score_button.config(text=f"Fart! ")
        except Exception:
            pass



if __name__ == "__main__":
    game = App()
    game.root.mainloop()