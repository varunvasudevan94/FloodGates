from itertools import product

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
import chess

LEGAL_COLS = "ABCDEFGH"
LEGAL_ROWS = "12345678"
LEGAL_COORDINATES = [x+y for (x, y) in product(LEGAL_COLS, LEGAL_ROWS)]
MAX = 8

def get_board_coordinates_consts_from_string(coordinate_str):
    coordinate_str = coordinate_str.upper()
    assert(coordinate_str in LEGAL_COORDINATES)
    return getattr(chess, coordinate_str)

def get_piece_at_coordinate(board, coordinate_str):
    coordinate_const = get_board_coordinates_consts_from_string(coordinate_str)
    return board.piece_at(coordinate_const)

def get_attacking_squares(board, coordinate_str):
    coordinate_const = get_board_coordinates_consts_from_string(coordinate_str)
    piece = get_piece_at_coordinate(board, coordinate_str)
    # Black -1, White 1, not assigning weights for pieces
    if piece:
        weight = -1 if piece.color else 1
    else:
        weight = 0
    squares = board.attacks(coordinate_const)
    return np.array([weight*int(x) for x in squares.tolist()])

def get_cumalative_floodgate(board):
    cum_arr = sum([get_attacking_squares(board, coord)for coord in LEGAL_COORDINATES])
    cum_2d_arr = np.reshape(cum_arr, (MAX, MAX))[::-1]
    
    flood_gates_df = pd.DataFrame(cum_2d_arr)
    flood_gates_df.columns = [x for x in LEGAL_COLS]
    flood_gates_df.index = flood_gates_df.index.map(lambda x: 8 - x)
    
    return flood_gates_df

def get_data_list_from_file(filename):
    import chess.pgn
    with open(filename) as pgn:
        data_list = list()
        game = chess.pgn.read_game(pgn)
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)
            flood_gate_df = get_cumalative_floodgate(board)
            # sb.heatmap(flood_gate_df)
            data_list.append(flood_gate_df)
        return data_list
    
def get_animation_from_file(file_name):
    import seaborn as sns
    import matplotlib.pyplot as plt
    from matplotlib import animation
    
    fig = plt.figure()
    
    data_list = get_data_list_from_file(file_name)

    def init():
          sns.heatmap(np.zeros((MAX, MAX)), square=True, cbar=False)

    def animate(i):
        df = data_list[i]
        df_norm_col=(df-df.mean())/df.std()
        sns.heatmap(df_norm_col, square=True, cbar=False, cmap=sns.color_palette("coolwarm", as_cmap=True))

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=20, repeat = False)
    
    return anim