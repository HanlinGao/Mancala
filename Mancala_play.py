#!/usr/bin/env python3
from __future__ import print_function
import sys
import copy
import random
import time


# general setting
PITS1 = [4, 4, 4, 4, 4, 4, 0]   # the 6th pit for each is the store
PITS2 = [4, 4, 4, 4, 4, 4, 0]
STATE = [PITS1, PITS2]
new_turn_flag = 0       # the sign for whether create a new turn, 0-no, 1-yes

# the sign for current player, decide how to count the score for each node, like state[0][6] - state[1][6]
current_player = 'P1'

DEPTH = 0   # current search depth
DEPTH_THRESHOLD = 4     # set for max search depth
SAME_SCORE_HANDLE = 0   # set for equivalent moves handling. 1-the first max move, 0-randomly choose from all maximums


def eprint(*args, **kwargs):
    # print to standard error
    print(*args, file=sys.stderr, **kwargs)


def find_options(current_state, current_turn):
    # find the legal options for current_turn when chessboard is in current_state
    options = []
    if current_turn == 'P1':
        for i in range(6):
            if current_state[0][i] != 0:
                options.append(i+1)
    else:
        for i in range(6):
            if current_state[1][i] != 0:
                options.append(i+1)
    return options


def new_turn(state, p_move, current_turn):
    # Check whether get a new turn when current_turn choose p_move when chessboard is in state
    if current_turn == 'P1':
        seeds = state[0][p_move - 1]
    else:
        seeds = state[1][p_move - 1]

    if (seeds + p_move == 7) or (seeds + p_move == 20):
        return 1
    else:
        return 0


def each_turn(xstate, p_move, player):
    # change the chessboard from xstate to the result of player choose p_move
    state = copy.deepcopy(xstate)

    if player == 'P2':
        state.reverse()
    seeds = state[0][p_move - 1]
    state[0][p_move - 1] = 0
    # The case that seeds will not flow into opponent's pits
    if seeds + p_move < 7:
        for i in range(p_move, seeds + p_move):
            state[0][i] = state[0][i] + 1
        # Check whether the last seed flow into an empty pit of player's
        # and the pit directly across has seeds.
        # Once captured, put the last one and directly across in player's bank
        if (state[0][seeds + p_move - 1] == 1) and (seeds + p_move - 1 != 6) and (state[1][6 - seeds - p_move] != 0):
            state[0][6] = state[0][6] + state[0][seeds + p_move - 1] + state[1][6 - seeds - p_move]
            state[0][seeds + p_move - 1] = 0
            state[1][6 - seeds - p_move] = 0

    # Check whether the last seed flow into the bank
    # If does, Start a new turn for player
    elif seeds + p_move == 7:
        global new_turn_flag

        for i in range(p_move, seeds + p_move):
            state[0][i] = state[0][i] + 1
        if player == 'P2':
            state.reverse()

        new_turn_flag = 1
        return state
    # The case that the seeds flow into opponent's pits
    else:
        extras = seeds + p_move - 7
        for i in range(p_move, 7):
            state[0][i] = state[0][i] + 1
        # The seeds do not flow back
        if extras < 7:
            for i in range(0, extras):
                state[1][i] = state[1][i] + 1
        # The seeds flow back
        elif (extras >= 7) and (extras < 13):
            for i in range(0, 6):
                state[1][i] = state[1][i] + 1
            for i in range(0, extras - 6):
                state[0][i] = state[0][i] + 1
            # Check if captured
            if (state[0][extras - 7] == 1) and (extras != 13) and (state[1][12 - extras] != 0):
                state[0][6] = state[0][6] + state[0][extras - 7] + state[1][12 - extras]
                state[0][extras - 7] = 0
                state[1][12 - extras] = 0
        # Check if the last seed flow into the bank
        elif extras == 13:
            for i in range(0, 6):
                state[1][i] = state[1][i] + 1
            for i in range(0, extras - 6):
                state[0][i] = state[0][i] + 1
            if player == 'P2':
                state.reverse()
            new_turn_flag = 1
            return state
        # Check if the seeds flow into opponent's pits again
        else:
            for i in range(0, 6):
                state[1][i] = state[1][i] + 1
            for i in range(0, 7):
                state[0][i] = state[0][i] + 1
            for i in range(0, extras - 13):
                state[1][i] = state[1][i] + 1

    if player == 'P2':
        state.reverse()
    new_turn_flag = 0
    return state


def terminal_turn(state):
    # check if state is a terminal_turn

    # Sum the seeds on the board for two players
    p1_seeds_sum = sum(state[0][:6])
    p2_seeds_sum = sum(state[1][:6])

    # not a terminal turn
    if (p1_seeds_sum != 0) and (p2_seeds_sum != 0):
        return False
    else:
        return True


def random_move(state, current_turn):
    # random choose a move for current_turn when chessboard is in state

    options = find_options(state, current_turn)
    return random.choice(options)


def min_value(state, alpha, beta, current_turn):
    # alpha-beta strategy. find the minimum score of current_turn's options when chessboard is in state and update alpha beta

    global DEPTH

    if terminal_turn(state) or DEPTH > DEPTH_THRESHOLD:
        if current_player == 'P1':
            return state[0][6] - state[1][6]
        else:
            return state[1][6] - state[0][6]

    # initial value to infinite negative
    v = 49
    options = find_options(state, current_turn)

    if current_turn == 'P1':
        temp_player = 'P2'
    else:
        temp_player = 'P1'

    # count the score of each option
    for each in options:
        DEPTH += 1
        temp_state = each_turn(state, each, current_turn)
        next_value = max_value(temp_state, alpha, beta, temp_player)
        v = min(v, next_value)
        DEPTH -= 1

        if v <= alpha:
            return v

        beta = min(beta, v)

    return v


def max_value(state, alpha, beta, current_turn):
    # alpha-beta strategy. find the maximum score of current_turn's options when chessboard is in state and update alpha beta
    global DEPTH
    if terminal_turn(state) or DEPTH > DEPTH_THRESHOLD:
        if current_player == 'P1':
            return state[0][6] - state[1][6]
        else:
            return state[1][6] - state[0][6]

    # initial value to infinite negative
    v = -49
    options = find_options(state, current_turn)

    if current_turn == 'P1':
        temp_player = 'P2'
    else:
        temp_player = 'P1'
    # count the score of each option
    for each in options:
        DEPTH += 1

        temp_state = each_turn(state, each, current_turn)
        next_value = min_value(temp_state, alpha, beta, temp_player)
        v = max(v, next_value)
        DEPTH -= 1

        if v >= beta:
            return v

        alpha = max(alpha, v)

    return v


def alpha_beta(state, current_turn):
    # alpha-beta strategy. find a best move for current_turn when chessboard is in state
    global DEPTH

    # find legal options
    options = find_options(state, current_turn)

    if current_turn == 'P1':
        temp_player = 'P2'
    else:
        temp_player = 'P1'

    # count the score of each option
    score_list = {}
    for each in options:
        temp_state = each_turn(state, each, current_turn)

        # if a terminal turn, return the score directly
        if terminal_turn(temp_state) or DEPTH > DEPTH_THRESHOLD:
            DEPTH += 1
            if current_player == 'P1':
                score_list[each] = temp_state[0][6] - temp_state[1][6]
            else:
                score_list[each] = temp_state[1][6] - temp_state[0][6]
            DEPTH -= 1

        # if a new turn, let score of the final state after the new turn replace the score of new_turn state
        elif new_turn(state, each, current_turn):
            new_state = each_turn(temp_state, alpha_beta(temp_state, current_turn), current_turn)
            DEPTH += 1
            score_list[each] = min_value(new_state, -49, 49, temp_player)
            DEPTH -= 1

        # if a normal turn, return the score of this node
        else:
            DEPTH += 1
            score_list[each] = min_value(temp_state, -49, 49, temp_player)
            DEPTH -= 1

    # return the max score option
    maximum = max(score_list.values())
    maximum_choice = max(score_list, key=score_list.get)
    if SAME_SCORE_HANDLE == 1:
        return maximum_choice
    else:
        choices = []
        for each in score_list:
            if score_list[each] == maximum:
                choices.append(each)
        return random.choice(choices)


def max_score(state, current_turn):
    # minimax strategy. find the maximum score of current_turn's options when chessboard is in state
    global DEPTH

    if terminal_turn(state) or DEPTH > DEPTH_THRESHOLD:
        if current_player == 'P1':
            return state[0][6] - state[1][6]
        else:
            return state[1][6] - state[0][6]

    v = -49
    options = find_options(state, current_turn)

    if current_turn == 'P1':
        temp_player = 'P2'
    else:
        temp_player = 'P1'
    # count the score of each option
    for each in options:
        DEPTH += 1

        temp_state = each_turn(state, each, current_turn)
        next_value = min_score(temp_state, temp_player)
        v = max(v, next_value)

        DEPTH -= 1

    return v


def min_score(state, current_turn):
    # minimax strategy. find the minimum score of current_turn's options when chessboard is in state
    global DEPTH

    if terminal_turn(state) or DEPTH > DEPTH_THRESHOLD:
        if current_player == 'P1':
            return state[0][6] - state[1][6]
        else:
            return state[1][6] - state[0][6]

    v = 49
    options = find_options(state, current_turn)

    if current_turn == 'P1':
        temp_player = 'P2'
    else:
        temp_player = 'P1'
    # count the score of each option
    for each in options:
        DEPTH += 1

        temp_state = each_turn(state, each, current_turn)
        next_value = max_score(temp_state, temp_player)
        v = min(v, next_value)

        DEPTH -= 1
    return v


def minimax_move(state, current_turn):
    # minimax strategy. find a best move for current_turn when chessboard is in state
    global DEPTH
    # find legal options
    options = find_options(state, current_turn)

    # count the score of each option
    score_list = {}

    if current_turn == 'P1':
        temp_player = 'P2'
    else:
        temp_player = 'P1'

    for each in options:    # use index to imply option
        temp_state = each_turn(state, each, current_turn)

        # if temp_state is a terminal turn, count the score for current_turn(max node)
        if terminal_turn(temp_state):
            DEPTH += 1
            if current_player == 'P1':
                score_list[each] = temp_state[0][6] - temp_state[1][6]
            else:
                score_list[each] = temp_state[1][6] - temp_state[0][6]
            DEPTH -= 1

        # if option leads to a new turn without game ending, find the final state and score it
        elif new_turn(state, each, current_turn):
            new_state = each_turn(temp_state, minimax_move(temp_state, current_turn), current_turn)

            DEPTH += 1
            score_list[each] = min_score(new_state, temp_player)
            DEPTH -= 1

        # finish in one turn(include capture), score the final state
        else:
            DEPTH += 1
            score_list[each] = min_score(temp_state, temp_player)
            DEPTH -= 1

    # return the max score option
    maximum = max(score_list.values())
    maximum_choice = max(score_list, key=score_list.get)
    if SAME_SCORE_HANDLE == 1:
        return maximum_choice
    else:
        choices = []
        for each in score_list:
            if score_list[each] == maximum:
                choices.append(each)
        return random.choice(choices)


def print_game_board(state):
    # print the game board to standard error
    state[1].reverse()
    eprint("      6    5    4     3    2    1")
    eprint("   --------------------------------")
    for i in range(0, 3):
        eprint(str(state[1][i]).rjust(2, '0'), "| ", end='')
    eprint(str(state[1][3]).rjust(2, '0'), '|| ', end='')
    for i in range(4, 7):
        eprint(str(state[1][i]).rjust(2, '0'), "| ", end='')
    eprint("P2", end='')
    eprint("\n--------------------------------------")
    eprint("P1", end='')
    for i in range(0, 3):
        eprint(" |", str(state[0][i]).rjust(2, '0'), end='')
    eprint(' ||', str(state[0][3]).rjust(2, '0'), end='')
    for i in range(4, 7):
        eprint(" |", str(state[0][i]).rjust(2, '0'), end='')
    eprint("\n   --------------------------------")
    eprint("      1    2    3     4    5    6\n")
    state[1].reverse()


def initialization():
    # initialize the chessboard
    temp_str = input('./play ')
    print_game_board(STATE)

    x = temp_str.split()
    if x[0] in ['random', 'minimax', 'alphabeta', 'human'] and x[1] in ['random', 'minimax', 'alphabeta', 'human']:
        return x[0], x[1]
    else:
        eprint('Please set in form of [option1, option2]\noptions:[random, minimax, alphabeta, human]')


def evaluate(move, current_state, current_turn):
    # check if the move for current_turn when chessboard is in current_state is legal
    if move not in [1, 2, 3, 4, 5, 6]:
        eprint("Illegal move! try again, please.\ncan only choose number from [1, 2, 3, 4, 5, 6]\n")
        return False

    if current_turn == 'P1':
        if current_state[0][move-1] == 0:
            eprint("Illegal move! try again, please.\n[cannot choose an empty pit to get stones]\n")
            return False
        else:
            return True
    elif current_turn == 'P2':

        if current_state[1][move-1] == 0:
            eprint("Illegal move! try again, please.\n[cannot choose an empty pit to get stones]\n")
            return False
        else:
            return True


def final_score(state):
    # count the final score for a terminal_turn
    p1_score = state[0][6]
    p2_score = state[1][6]
    if p1_score > p2_score:
        winner = 1
        print("Player 1 wins!")
    elif p1_score < p2_score:
        winner = 2
        print("Player 2 wins")
    else:
        winner = 0
        print("Draw game!")
    print("P1 score: ", p1_score, ", P2 score: ", p2_score)
    return winner, p1_score, p2_score


def main():
    (player1, player2) = initialization()
    current_state = STATE

    global current_player
    global DEPTH

    while True:
        DEPTH = 0
        if terminal_turn(current_state):
            final_score(current_state)
            break

        # check the strategy for P1
        if current_player == 'P1':
            if player1 == 'human':
                eprint(current_player, 'Please input your choice:')
                time.sleep(0.01)
                move = int(input())

            elif player1 == 'random':
                move = random_move(current_state, 'P1')

            elif player1 == 'minimax':
                move = minimax_move(current_state, 'P1')

            else:
                move = alpha_beta(current_state, 'P1')


            # if move is legal
            if evaluate(move, current_state, current_player):
                print(move)
                time.sleep(0.01)
                current_state = each_turn(current_state, move, current_player)
                print_game_board(current_state)
                time.sleep(0.01)

            else:
                continue

        # check the strategy for P2
        else:
            if player2 == 'human':
                eprint(current_player, 'Please input your choice:\n')
                time.sleep(0.01)
                move = int(input(' '))

            elif player2 == 'random':
                move = random_move(current_state, 'P2')


            elif player2 == 'minimax':
                move = minimax_move(current_state, 'P2')


            else:
                move = alpha_beta(current_state, 'P2')

            # if move is legal
            if evaluate(move, current_state, current_player):
                print(' ', move)
                time.sleep(0.01)
                current_state = each_turn(current_state, move, current_player)
                print_game_board(current_state)
                time.sleep(0.01)

            else:
                continue

        # no new turn, switch player
        if new_turn_flag == 0:
            if current_player == 'P1':
                current_player = 'P2'
            else:
                current_player = 'P1'


def strategies_test(player1, player2, turn):
    # Initial for win-time counting
    p1_win = 0
    p2_win = 0
    draw_game = 0
    for i in range(0, turn):
        # In case of changing the global variable
        current_state = copy.deepcopy(STATE)

        global current_player
        global DEPTH

        while True:
            DEPTH = 0
            if terminal_turn(current_state):
                stat = final_score(current_state)
                if stat[0] == 1:
                    p1_win += 1
                elif stat[0] == 2:
                    p2_win += 1
                else:
                    draw_game += 1

                # Initial for next turn
                current_player = "P1"
                DEPTH = 0
                break

            if current_player == 'P1':
                if player1 == 'human':
                    print(current_player, 'Please input your choice:')
                    move = int(input())

                elif player1 == 'random':
                    move = random_move(current_state, 'P1')

                elif player1 == 'minimax':
                    move = minimax_move(current_state, 'P1')

                else:
                    move = alpha_beta(current_state, 'P1')

                # if move is legal
                if evaluate(move, current_state, current_player):
                    current_state = each_turn(current_state, move, current_player)
                    print_game_board(current_state)

                else:
                    continue

            else:
                if player2 == 'human':
                    eprint(current_player, 'Please input your choice:\n')
                    move = int(input(' '))

                elif player2 == 'random':
                    move = random_move(current_state, 'P2')

                elif player2 == 'minimax':
                    move = minimax_move(current_state, 'P2')

                else:
                    move = alpha_beta(current_state, 'P2')

                # if move is legal
                if evaluate(move, current_state, current_player):
                    current_state = each_turn(current_state, move, current_player)
                    print_game_board(current_state)

                else:
                    continue

            # no new turn, switch
            if new_turn_flag == 0:
                if current_player == 'P1':
                    current_player = 'P2'
                else:
                    current_player = 'P1'

    print("\nTEST OVER\n")
    print("Player 1 wins ", p1_win, " out of ", turn)
    print("Player 2 wins ", p2_win, " out of ", turn)
    print(draw_game, " draw game(s) out of ", turn)


# Count time spends on the algorithm
def time_test(player1, player2, turn):
    start = time.clock()
    for i in range(0, turn):
        current_state = copy.deepcopy(STATE)

        global current_player
        global DEPTH

        while True:
            DEPTH = 0
            if terminal_turn(current_state):
                final_score(current_state)
                current_player = "P1"
                DEPTH = 0
                break

            if current_player == 'P1':
                if player1 == 'human':
                    print(current_player, 'Please input your choice:')
                    move = int(input())

                elif player1 == 'random':
                    move = random_move(current_state, 'P1')

                elif player1 == 'minimax':
                    move = minimax_move(current_state, 'P1')

                else:
                    move = alpha_beta(current_state, 'P1')

                # if move is legal
                if evaluate(move, current_state, current_player):
                    current_state = each_turn(current_state, move, current_player)
                    print_game_board(current_state)

                else:
                    continue

            else:
                if player2 == 'human':
                    eprint(current_player, 'Please input your choice:\n')
                    move = int(input(' '))

                elif player2 == 'random':
                    move = random_move(current_state, 'P2')

                elif player2 == 'minimax':
                    move = minimax_move(current_state, 'P2')

                else:
                    move = alpha_beta(current_state, 'P2')

                # if move is legal
                if evaluate(move, current_state, current_player):
                    current_state = each_turn(current_state, move, current_player)
                    print_game_board(current_state)

                else:
                    continue

            # no new turn, switch
            if new_turn_flag == 0:
                if current_player == 'P1':
                    current_player = 'P2'
                else:
                    current_player = 'P1'

    end = time.clock()
    time_spend = end - start
    return time_spend


# Establish an approximate speedup for alpha-beta pruning over minimax.
def test_alpha_beta_effect(turn):
    m = time_test('random', 'minimax', turn)
    a = time_test('random', 'alpha_beta', turn)
    print("\nTEST OVER\n")
    print("Each algorithm try ", turn, " turn in total")
    print("Minimax spend ", m / turn, "seconds in average")
    print("Alpha beta pruning spend ", a / turn, "seconds in average")
    print("Alpha beta pruning is ", (m - a) / turn, " faster than minimax.")


def random_experiment(times):
    # take two random players and return the detailed statement after experiments
    # parameter times as the times that the experiment will take place
    p1_win = 0
    p2_win = 0 # record number of wins from both player
    draw = 0
    detail = []
    # iterator for experiments
    for i in range(1, times + 1):
        dic = ['Round', 'Winner', 'Deviation']
        row = []
        row.append(i)
        state = copy.deepcopy(STATE)
        # simulation of a game
        while not terminal_turn(state):
            state = each_turn(state, random_move(state, 'P1'), 'P1')
            if not terminal_turn(state):
                state = each_turn(state, random_move(state, 'P2'), 'P2')
        # calculate the wins, deviation of scores from both players, draws, win rate
        if state[0][6] - state[1][6] > 0:
            p1_win += 1
            row.append("P1")
        elif state[0][6] - state[1][6] < 0:
            p2_win += 1
            row.append("P2")
        else:
            draw += 1
            row.append("Draw")
        row.append(state[0][6] - state[1][6])
        dictionary = dict(zip(dic, row))
        detail.append(dictionary)
    print("In total {0} rounds of games, player 1 wins {1} time\
, player 2 wins {2}, {3} draws. The first player`s win rate is {4}.".format(times, p1_win, p2_win, draw,
                                                                            p1_win / times))
    # calculate and display the max deviation, min deviation, average deviation
    max_deviation = 0
    min_deviation = 48
    sum = 0
    for i in range(0, len(detail)):
        sum += detail[i]['Deviation']
        if detail[i]['Deviation'] > max_deviation:
            max_deviation = detail[i]['Deviation']
        if detail[i]['Deviation'] < min_deviation:
            min_deviation = detail[i]['Deviation']
    print("The Max deviation is ", max_deviation)
    print("The Min deviation is ", min_deviation)
    print("The average deviation is ", sum/len(detail))
    print("Round detail is following.")
    for i in range(0, len(detail)):
        print(detail[i])


def minimax_experiment(times):
    # take two minimax players and return the detailed statement after experiments
    # parameter times as the times that the experiment will take place
    p1_win = 0
    p2_win = 0 # record number of wins from both player
    draw = 0
    detail = []
    # iterator for experiments
    for i in range(1, times + 1):
        DEPTH = 0
        dic = ['Round', 'Winner', 'Deviation']
        row = []
        row.append(i)
        state = copy.deepcopy(STATE)
        # simulation of a game
        while not terminal_turn(state):
            state = each_turn(state, minimax_move(state, 'P1'), 'P1')
            if not terminal_turn(state):
                state = each_turn(state, minimax_move(state, 'P2'), 'P2')
        # calculate the wins, deviation of scores from both players, draws, win rate
        if state[0][6] - state[1][6] > 0:
            p1_win += 1
            row.append("P1")
        elif state[0][6] - state[1][6] < 0:
            p2_win += 1
            row.append("P2")
        else:
            draw += 1
            row.append("Draw")
        row.append(state[0][6] - state[1][6])
        dictionary = dict(zip(dic, row))
        detail.append(dictionary)
    print("In total {0} rounds of games, player 1 wins {1} time\
, player 2 wins {2}, {3} draws. The first player`s win rate is {4}.".format(times, p1_win, p2_win, draw, p1_win / times))

    # calculate and display the max deviation, min deviation, average deviation
    max_deviation = 0
    min_deviation = 48
    sum = 0
    for i in range(0, len(detail)):
        sum += detail[i]['Deviation']
        if detail[i]['Deviation'] > max_deviation:
            max_deviation = detail[i]['Deviation']
        if detail[i]['Deviation'] < min_deviation:
            min_deviation = detail[i]['Deviation']
    print("The Max deviation is ", max_deviation)
    print("The Min deviation is ", min_deviation)
    print("The average deviation is ", sum / len(detail))
    print("Round detail is following.")
    for i in range(0, len(detail)):
        print(detail[i])
# strategies_test('random', 'minimax', 500)
main()