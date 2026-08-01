import random

BEATS = {
    "rock": "scissor",
    "paper": "rock",
    "scissor": "paper"
}

def select_winner(guess):
    guess = guess.lower()
    if guess not in BEATS:
        return False

    computer_guess = random.choice(list(BEATS.keys()))

    if guess == computer_guess:
        return "tie"
    elif BEATS[guess] == computer_guess:
        return "win"
    else:
        return "lose"