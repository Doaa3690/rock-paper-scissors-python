# Import necessary libraries
import tkinter as tk
from tkinter import PhotoImage
import random
from playsound import playsound
import pygame
import threading

# Game constants
MAX_ROUNDS = 3
WIN_COLOR = "green"
LOSE_COLOR = "red"
DRAW_COLOR = "#444"

# Simple AI class to predict player's move
class RPSAI:
    def __init__(self):
        self.history = []

    def predict(self):
        if not self.history:
            return random.choice(["rock", "paper", "scissors"])
        last = self.history[-1]
        return {"rock": "paper", "paper": "scissors", "scissors": "rock"}[last]

    def update(self, move):
        self.history.append(move)

# Main game class
class RPSGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Rock Paper Scissors")
        self.root.geometry("500x600")

        # Set background image
        self.bg_image = PhotoImage(file="backg.png")
        self.bg_canvas = tk.Canvas(self.root, width=500, height=600, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.bg_canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        # Initialize AI and game variables
        self.ai = RPSAI()
        self.reset_game_vars()

        # Create the central frame for UI elements
        self.center_frame = tk.Frame(self.bg_canvas, highlightthickness=0, bd=0)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Game title label
        tk.Label(self.center_frame, text="ROCK PAPER SCISSORS", font=("Arial", 18, "bold")).pack(pady=20)

        # Load button images
        self.rock_img = PhotoImage(file="rock.png")
        self.paper_img = PhotoImage(file="paper.png")
        self.scissors_img = PhotoImage(file="scissors.png")

        # Frame to hold the three choice buttons
        self.btn_container = tk.Frame(self.center_frame, width=300, height=100)
        self.btn_container.pack(pady=10)

        # Animation variables
        self.choice_buttons = []
        self.button_frames = []
        self.anim_offsets = [0, 0, 0]
        self.anim_directions = [1, 1, 1]

        # Create the buttons with images
        images = [self.rock_img, self.paper_img, self.scissors_img]
        moves = ["rock", "paper", "scissors"]
        for i in range(3):
            frame = tk.Frame(self.btn_container, width=100, height=100)
            frame.place(x=i * 100, y=0)
            btn = tk.Button(frame, image=images[i], command=lambda m=moves[i]: self.play(m), bd=0)
            btn.place(x=0, y=0)
            self.choice_buttons.append(btn)
            self.button_frames.append(frame)

        # Start button animation
        self.animate_buttons()

        # Label for displaying round result
        self.result_label = tk.Label(self.center_frame, text="", font=("Arial", 16), fg=DRAW_COLOR)
        self.result_label.pack(pady=30)

        # Label for showing tries left
        self.try_label = tk.Label(self.center_frame, text=f"Tries left: {MAX_ROUNDS}", font=("Arial", 14), fg="#333")
        self.try_label.pack()

        # Countdown label before final result
        self.countdown_label = tk.Label(self.center_frame, text="", font=("Arial", 28, "bold"))
        self.countdown_label.pack()

        # Restart button (hidden at start)
        self.restart_button = tk.Button(self.center_frame, text="Restart Game", font=("Arial", 14),
                                        command=self.restart_game, bg="#d1e7dd", fg="#000")
        self.restart_button.pack(pady=20)
        self.restart_button.pack_forget()

        # Play background music using threading
        threading.Thread(target=self.play_background_music, daemon=True).start()

    # Function to play background music in a loop
    def play_background_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load("background.mp3") # Load music file
        pygame.mixer.music.set_volume(0.3)      # Set low volume
        pygame.mixer.music.play(-1)   # Loop forever

    # Animate the three buttons (slightly up and down)
    def animate_buttons(self):
        for i, btn in enumerate(self.choice_buttons):
            if self.anim_offsets[i] >= 5:
                self.anim_directions[i] = -1    # Change direction downwards (float movement)
            elif self.anim_offsets[i] <= 0:           
                self.anim_directions[i] = 1      # Change direction upwards
            self.anim_offsets[i] += self.anim_directions[i]
            btn.place_configure(y=self.anim_offsets[i])
        self.root.after(100, self.animate_buttons)

    # Reset game state variables
    def reset_game_vars(self):
        self.player_wins = 0
        self.ai_wins = 0
        self.rounds_left = MAX_ROUNDS
        self.ai.history = []    # Clear AI memory

    # Enable or disable buttons
    def set_buttons_state(self, state):
        for btn in self.choice_buttons:
            btn.config(state=state)

    # Decide round winner based on player vs AI choice
    def determine_winner(self, player, ai_choice):
        if player == ai_choice:
            return "draw"
        wins = {
            "rock": "scissors",
            "paper": "rock",
            "scissors": "paper"
        }
        return "player" if wins[player] == ai_choice else "ai"

    # Main game logic when a player selects a move
    def play(self, player):
        if self.rounds_left == 0:
            return  # Game is already over

        ai_choice = self.ai.predict()  # Get AI move
        self.ai.update(player)      # Update AI history

        # Play sound on click
        threading.Thread(target=lambda: playsound("click.mp3"), daemon=True).start()

        winner = self.determine_winner(player, ai_choice)
        color = DRAW_COLOR

        # Update the result label depending on outcome
        if winner == "draw":
            result = f"Draw!\n You both chose {player}"
        elif winner == "player":
            result = f"You win this round!\n {player.capitalize()} beats {ai_choice}"
            color = WIN_COLOR
            self.player_wins += 1
        else:
            result = f"You lose this round!\n {ai_choice.capitalize()} beats {player}"
            color = LOSE_COLOR
            self.ai_wins += 1

        self.rounds_left -= 1
        self.try_label.config(text=f"Tries left: {self.rounds_left}")
        self.result_label.config(text=result, fg=color)

        # If game over, start final countdown
        if self.player_wins == 2 or self.ai_wins == 2 or self.rounds_left == 0:
            self.set_buttons_state("disabled")
            self.start_final_countdown()
        else:
            self.set_buttons_state("normal")

    # Countdown before final result
    def start_final_countdown(self):
        self.countdown_label.config(text="3")
        self.root.after(700, lambda: self.countdown_label.config(text="2"))
        self.root.after(1400, lambda: self.countdown_label.config(text="1"))
        self.root.after(2100, self.show_final_result)

    # Display the final result after countdown
    def show_final_result(self):
        self.countdown_label.config(text="")

        if self.player_wins > self.ai_wins:
            result = "YOU WIN!"
            color = WIN_COLOR
        elif self.ai_wins > self.player_wins:
            result = "YOU LOST!"
            color = LOSE_COLOR
        else:
            result = "DRAW!"
            color = DRAW_COLOR

        self.result_label.config(text=result, fg=color)
        self.restart_button.pack()   # Show restart button

    # Restart the game to initial state
    def restart_game(self):
        self.reset_game_vars()
        self.result_label.config(text="", fg=DRAW_COLOR)
        self.try_label.config(text=f"Tries left: {MAX_ROUNDS}")
        self.countdown_label.config(text="")
        self.set_buttons_state("normal")
        self.restart_button.pack_forget()

# start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = RPSGame(root)
    root.mainloop()
