import numpy as np
import time
from copy import copy, deepcopy
import sys
import math

# A függvény tetszőleges K páratlan méretre kell működjön.
k = 5
board = [[False if (i==0 or j==0 or i==k+1 or j==k+1) else True for i in range(k+2)] for j in range(k+2)] 
depth = 1
alfa = 2
step = 0.25
heuristic = True

#lerakom a playereket
board[1][int(k/2)+1] = 'P'
board[k][int(k/2)+1] = 'B'

#
# Azert foglalok le ilyen alakba neki helyet kxk helyett hogy legyen egy 'keret' korulotte, 
# igy minden olyan mezorol ami letesztelve lehet jatek kozben nyugodtan vehetem az osszes szomszedot korbe anelkul hogy kilepjek az indexekbol
#
# [[False, False, False,    False, False],
#  [False, True,  'P',      True,  False],
#  [False, True,  True,     True,  False],
#  [False, True,  'B',      True,  False],
#  [False, False, False,    False, False]]

# A függvény visszatérítési értéke legyen
# +1,ha a BOT játékos nyert,
# -1, ha az ellenfél nyert, 
# 0 különben.
#
def evaluate(state_of_game):
    global heuristic
    if heuristic:
        return heuristic_eval(state_of_game)
    return non_heuristic_eval(state_of_game)

def non_heuristic_eval(state_of_game):
    bot_x, bot_y = get_bot_coord(state_of_game)
    player_x, player_y = get_player_coord(state_of_game)
    if(len(get_valid_positions(state_of_game, bot_x, bot_y)) == 0):       #ha a bot nem tud mozogni sehova
        return -1
    if(len(get_valid_positions(state_of_game, player_x, player_y)) == 0): #ha a jatekos nem tud mozogni sehova
        return +1
    return 0                                                              #kulonben

def heuristic_eval(state_of_game):
    global alfa
    bot_x, bot_y = get_bot_coord(state_of_game)
    player_x, player_y = get_player_coord(state_of_game)
    MAX = len(get_valid_positions(state_of_game, bot_x, bot_y))
    MIN = len(get_valid_positions(state_of_game, player_x, player_y))
    return MAX - alfa * MIN

#megkeresi az adott betut a palyan
def getCoord(state_of_game, character):
    global k
    for i in range(1,k+1):
        for j in range(1,k+1):
            if(state_of_game[i][j] == character):
                return [i,j]
    print(character," not found in this state:\n",state_of_game)

#felsore absztrakciok
def get_bot_coord(state_of_game):
    return getCoord(state_of_game, 'B')

def get_player_coord(state_of_game):
    return getCoord(state_of_game, 'P')

#todo: nagy K eseten az ellenfel korulieket venni
#visszaadja az adott palyan az osszes lehetseges mozdulatot amit a player betuju cellarol vegre lehet halytani
def get_moves(state_of_game, player):
    moves = []
    x,y  = get_bot_coord(state_of_game) if player == 'B' else get_player_coord(state_of_game)
    opponent_x, opponent_y = get_player_coord(state_of_game) if player == 'B' else get_bot_coord(state_of_game) 
    for position in get_valid_positions(state_of_game,x,y):
        temp_state = deepcopy(state_of_game)
        temp_state[x][y] = True                         # 'felemeljuk' a babut => a regi helye ures lesz
        temp_state[position[0]][position[1]] = player   # letesszuk az uj poziciora
        for blocks in get_valid_positions(temp_state, opponent_x, opponent_y):
            temp_state_2 = deepcopy(temp_state)
            temp_state_2[blocks[0]][blocks[1]] = False
            moves.append(temp_state_2)
    return moves

#True ha a cella nincs lezarva/nem all rajta valaki
def is_valid(state_of_game, x,y):
    if (state_of_game[x][y] == False or state_of_game[x][y] == 'P' or state_of_game[x][y] == 'B'):  #or (bot_x == x and bot_y == y) or (player_x == x and player_y ==y)):
        return False
    return True

#Visszaadja az osszes szomszedos cellat amire lehet lepni
def get_valid_positions(state_of_game, i, j):
    positions = [[i-1,j-1], [i-1,j], [i-1,j+1], [i,j-1], [i,j+1], [i+1,j-1], [i+1,j], [i+1,j+1]]
    return [(x,y) for x,y in positions  if is_valid(state_of_game,x,y) ]


#osszes ures cellat visszaadja, akkor hasznaljuk majd mikor keresunk lezarando elemeket
def get_valid_blocks(state_of_game):
    global k
    cells = []
    for i in range(k+1):
        for j in range(k+1):
            if state_of_game[i][j] == True:
                cells.append([i,j])
    return cells

#Bot = MAX, Player = MIN
def minimax(state_of_game, depth, maximizing_player, a , b):
    max_eval = evaluate(state_of_game)
    if(depth == 0): 
         return max_eval

    depth -= 1
    if maximizing_player:
        max_eval = -float("inf") #lehetne akar 2 is, mivel azt az erteket ugyse eri el, vagy -2 a masik agon de altalanositva hagyom
        for move in get_moves(state_of_game, 'B'): #lekerem az osszes lehetseges mozdulatot
            eval = minimax(move, depth, False, a, b) #minden mozdulatot kiertekelek, -1/0/1
            max_eval = max(eval, max_eval) #a legjobbat mindig eltarolom
            a = max(max_eval, a)
            if a >= b:
                return max_eval
        return max_eval

    else:
        min_eval = float("inf")
        for move in get_moves(state_of_game, 'P'):
            eval = minimax(move, depth, True, a, b)
            min_eval = min(min_eval, eval)
            a = min(max_eval, a)
            if a >= b:
                return min_eval
        return min_eval


#megkeressuk a legjobb mozdulatot, ha nincs mozdulat egyaltalan akkor None-t terit vissza
#ha a faster evaluationt hasznaljuk, akkor olyan esetekben ahol tul sok mozdulatot 
# kene kiertekelnunk elfogadunkegy semleges allapotot a legjobb allapot helyett(0 ertekut)
def best_move(state_of_game, depth, player, fast_eval = False, max_nr_of_moves = 20):
    best_move = None
    #lekerjuk az osszes lehetseges mozdulatot az adott jatekosnak (B/P)
    moves = get_moves(state_of_game, player)
    #Mindig a Bot a maximalo jatekos
    maximizing_player = (player == 'B')

    if maximizing_player:
        max_eval = -float("inf")
        for move in moves:
            eval = minimax(state_of_game, depth, True, -float("inf"), float("inf"))
            if eval > max_eval:
                max_eval = eval
                best_move = move


            # if fast_eval and len(moves) > max_nr_of_moves and eval == 0:
            #     break
            # if eval == 1:
                # break
        print("Best evaluation:", max_eval)
    else:
        min_eval = float("inf")
        for move in moves:
            eval = minimax(state_of_game, depth, False, -float("inf"), float("inf"))
            if eval < min_eval:
                min_eval = eval
                best_move = move
            

            # if fast_eval and len(moves) > max_nr_of_moves and eval == 0:
            #     break
            # if eval == -1:
                # break
    return best_move

def print_board(board):
    for i in range(1,k+1):
        print("")
        for j in range(1, k+1):
            if board[i][j] == True:
                print("[ ]",end = '')
            else:
                if board[i][j] == False:
                    print("[X]",end = '')
                else:
                    print("[", board[i][j],  "]",sep='',end = '')
    print("\n")

def bots_against_each_other():
    global board, depth
    while(True):
        board = best_move(board, math.floor(depth),  'B')
        #azert nem hivom meg az evaluate-et hogy megnezzem vege-e mert a best_move ugyis None-ot terit vissza ha nem tud mozogni
        if not board:
            print("P won")
            break
        print("B moved:")
        print_board(board)
        time.sleep(2)

        board = best_move(board, math.floor(depth), 'P')
        if not board:
            print("B won")
            break 
        print("P moved:")
        print_board(board)
        time.sleep(2)


#player gives a move by coordinate
def player_input(state_of_game):
    player_x, player_y = get_player_coord(state_of_game)
    input_x = int(input("X coordinate for the move: ")) + 1
    input_y = int(input("Y coordinate for the move: ")) + 1
    #player moves:
    while(not is_valid(state_of_game, input_x, input_y) or not (abs(input_x - player_x) <= 1) or not (abs(input_y - player_y) <= 1) 
        or (input_x > k ) and (input_y > k)):
        input_x = int(input("X coordinate for the move: ")) + 1
        input_y = int(input("Y coordinate for the move: ")) + 1
    state_of_game[player_x][player_y] = True
    state_of_game[input_x][input_y] = 'P'
    print_board(state_of_game)
    print("__________________________")

    input_x = int(input("X coordinate for the block: ")) + 1 
    input_y = int(input("Y coordinate for the block: ")) + 1
    #player moves:
    while(not is_valid(state_of_game, input_x, input_y)):
        input_x = int(input("X coordinate for the block: ")) + 1
        input_y = int(input("Y coordinate for the block: ")) + 1
    state_of_game[input_x][input_y] = False    
    print_board(state_of_game)

    print("__________________________")
    return state_of_game


#player starts off against bot, fast_eval set to false by default
def player_against_bot(fast_eval = False):
    global board, depth

    print_board(board)

    while(True):
        px,py = get_player_coord(board)
        if len(get_valid_positions(board, px, py)) == 0:
            print("B won")
            break
        board = player_input(board)
        print_board(board)

        depth = depth + step

        board = best_move(board, math.floor(depth), 'B', fast_eval)
        if not board:
            print("P won")
            break
        print("B moved:")
        print_board(board)

        depth = depth + step

#bot starts off against player, fast_eval set to false by default
def bot_against_player(fast_eval = False):
    global board, depth

    while(True):
        board = best_move(board, depth, 'B', fast_eval)
        if not board:
            print("P won")
            break
        print_board(board)
    
       
        px,py = get_player_coord(board)
        if len(get_valid_positions(board, px, py)) == 0:
            print("B won")
            break
        board = player_input(board)
        print_board(board)

modes = [1,2,3]
mode = 0
while(mode not in modes):
    print("__________________________")
    print("Choose mode")
    print("1. Bot vs Bot, 2 sec sleep between decisions")
    print("2. Player starts off against bot")
    print("3. Bot starts off against player")
    print("__________________________")
    mode = int(input())

print("Game starting...")
if mode == 1:
    bots_against_each_other()
if mode == 2:
    player_against_bot()
if mode == 3:
    bot_against_player()