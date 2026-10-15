
#### function to display game borad
def print_board(board):
    print()
    for row in range(3):
        print(f" {board[row][0]} | {board[row][1]} | {board[row][2]} ")
        if row < 2:
            print("---+---+---")
    print()

###Return True if the mark completes a row, column, or diagonal.
def check_winner(board, mark):
   
    # Check rows
    for row in range(3):
        if all(board[row][col] == mark for col in range(3)):
            return True

    # Check columns
    for col in range(3):
        if all(board[row][col] == mark for row in range(3)):
            return True

    # Check diagonals
    if all(board[i][i] == mark for i in range(3)):
        return True

    if all(board[i][2 - i] == mark for i in range(3)):
        return True

    return False


def get_move(board, player_name, mark):
    
    while True:
        choice = input(
            f"{player_name} ({mark}), choose a cell (1-9): "
        ).strip()

        if choice == "":
            print("Input cannot be empty. Please try again.")
            continue

        if not choice.isdigit():
            print("Invalid input. Please enter a number from 1 to 9.")
            continue

        cell_number = int(choice)

        if cell_number < 1 or cell_number > 9:
            print("Out of range. Please choose a number from 1 to 9.")
            continue

        row = (cell_number - 1) // 3
        col = (cell_number - 1) % 3

        if board[row][col] in ("X", "O"):
            print("That cell is already occupied. Please choose another.")
            continue

        return row, col


def play_game():
    
    board = [[str(row * 3 + col + 1) for col in range(3)]
             for row in range(3)]
    players = [("Player 1", "X"), ("Player 2", "O")]
    turn = 0

    print("\nNew game! Choose a cell number from 1 to 9:")
    print_board(board)

    while True:
        player_name, mark = players[turn]
        row, col = get_move(board, player_name, mark)
        board[row][col] = mark

        # Show the board after every valid move.
        print_board(board)

        # Check for a win after the move.
        if check_winner(board, mark):
            print(f"Congratulations! {player_name} ({mark}) wins!")
            return

        # If no cells remain empty, the game is a draw.
        if all(cell in ("X", "O") for row in board for cell in row):
            print("It's a draw! Great game, both players.")
            return

        # Switch player only after a valid move.
        turn = 1 - turn


def main():
    
    print("Welcome to the Tic-Tac-Toe Game!")
    print("Player 1 uses X. Player 2 uses O.")

    while True:
        play_game()

        while True:
            again = input("Would you like to play again? (y/n): ").strip().lower()

            if again in ("y", "yes"):
                break
            elif again in ("n", "no"):
                print("Thanks for playing Tic-Tac-Toe.")
                return
            else:
                print("Please enter y (yes) or n (no).")


main()
