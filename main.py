from rps.rps import select_winner
from rps.showcam import capture_screen


def playing_game():
    while True:
        player_guess = input("Please Enter your choice.. Options: Rock, Paper, Scissor ")
        select_winner(player_guess)
        prompt = input("Do you want to play again? (Y/N) ")
        prompt = prompt.lower()
        if prompt == 'n' or prompt == 'no':
            print("Thank you for playing...")
            break
        elif prompt == 'y' or prompt == 'yes':
            print()
        else:
            print("Not a valid input, Please select an appropriate option...")
            prompt = input("Do you want to play again? Yes or No (Y/N) ")
            prompt = prompt.lower()
            if prompt == 'n' or prompt == 'no':
                print("Thank you for playing...")
                break
            elif prompt == 'y' or prompt == 'yes':
                print()
            else:
                print("I don't want to play with you... just leave, Bye!")
                break


# if __name__ == "__main__":
#     playing_game()
#
#


if __name__ == '__main__':
    capture_screen()