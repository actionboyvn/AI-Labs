import copy
import time

INF = 100000000

class ReversiGame():
    def __init__(self, initialState, initialTurn):
        self.state = initialState
        self.turn = initialTurn
        self.round_count = 0
        self.evaluation_function_calls = 0
        self.strategies = ["DiscCount", "Mobility", "Stability"]        

    def getNextTurn(self, currentTurn):
        if currentTurn == 1:
            return 2
        else:
            return 1
        
    def generateMoves(self, currentState, currentTurn):
        next_turn = self.getNextTurn(currentTurn)
        states = []
        for move in range(0, 64):
            if currentState[move] == 0:
                next_state = copy.deepcopy(currentState)
                next_state[move] = currentTurn
                flipped_horizontally = False
                flipped_vertically = False
                flipped_diagonally = False
                for i in range(0, 64):                                   
                    if next_state[i] == currentTurn and (abs(i // 8 - move // 8) > 1 or abs(i % 8 - move % 8) > 1):                        
                        begin = min(i, move)
                        end = max(i, move)                                                                  
                        if not flipped_horizontally and i // 8 == move // 8:                            
                            disks_check = True
                            for j in range(begin + 1, end):
                                if next_state[j] != next_turn:
                                    disks_check = False
                            if disks_check:             
                                for j in range(begin + 1, end):                   
                                    next_state[j] = currentTurn
                                flipped_horizontally = True

                        if not flipped_vertically and i % 8 == move % 8:
                            disks_check = True
                            for j in range(begin + 8, end, 8):
                                if next_state[j] != next_turn:
                                    disks_check = False
                            if disks_check:    
                                for j in range(begin + 8, end, 8):
                                    next_state[j] = currentTurn
                                flipped_vertically = True

                        if not flipped_diagonally and abs(i // 8 - move // 8) == abs(i % 8 - move % 8):
                            disks_check = True
                            if begin % 8 > end % 8:
                                step = 7
                            else:
                                step = 9
                            for j in range(begin + step, end, step):                          
                                if next_state[j] != next_turn:
                                    disks_check = False
                            if disks_check:
                                for j in range(begin + step, end, step):
                                    next_state[j] = currentTurn
                                flipped_diagonally = True  

                if flipped_horizontally or flipped_vertically or flipped_diagonally:
                    states.append(next_state)            
        return states
    
    def checkGameEnd(self, boardState):
        if len(self.generateMoves(boardState, 1)) == 0 and len(self.generateMoves(boardState, 2)) == 0:
            return True
        return False
    
    def getDiscCountDifference(self, boardState, rootTurn):
        count_1 = 0
        count_2 = 0
        for i in range(64):
            if boardState[i] == 1:
                count_1 += 1
            elif boardState[i] == 2:
                count_2 += 1
        if rootTurn == 1:
            return count_1 - count_2
        else:
            return count_2 - count_1
        
    def calcHeuristicForDiscCountStrategy(self, currentState, madeTurn):
        heuristic_value = self.getDiscCountDifference(currentState, madeTurn)
        return heuristic_value
    
    def calcHeuristicForMobilityStrategy(self, currentState, madeTurn):
        next_turn = self.getNextTurn(madeTurn)
        opponent_mobility = len(self.generateMoves(currentState, next_turn))
        return -opponent_mobility
    
    def calcHeuristicForStabilityStrategy(self, currentState, madeTurn):
        heuristic_value = 0
        for i in range(0, 64):            
            if currentState[i] == madeTurn:
                if i == 0 or i == 7 or i == 56 or i == 63: # discs at 4 corners
                    heuristic_value += 10
                elif i <= 7 or i in range(56, 64) or i in range(0, 56, 8) or i in range(7, 64, 8): # discs at 4 walls
                    heuristic_value += 5
        return heuristic_value
    
    def moveByStrategy(self, currentState, currentTurn, strategy):
        new_states = self.generateMoves(currentState, currentTurn)        
        if (len(new_states) > 0):
            heuristics = []
            for i in range(len(new_states)):
                if strategy == "DiscCount":
                    heuristics.append(self.calcHeuristicForDiscCountStrategy(new_states[i], currentTurn))                
                elif strategy == "Mobility":
                    heuristics.append(self.calcHeuristicForMobilityStrategy(new_states[i], currentTurn))
                elif strategy == "Stability":
                    heuristics.append(self.calcHeuristicForStabilityStrategy(new_states[i], currentTurn))
            pos = 0
            max_heuristic = heuristics[0]
            for i in range(1, len(heuristics)):
                if max_heuristic < heuristics[i]:
                    pos = i
                    max_heuristic = heuristics[i]
            return new_states[pos]
        return None
    
    def moveWithMinimax(self, currentState, currentTurn, rootTurn, depth):
        game_end = self.checkGameEnd(currentState)
        if game_end or depth == 0: 
            game_result = self.getDiscCountDifference(currentState, rootTurn)
            self.evaluation_function_calls += 1
            return game_result, currentState
        if currentTurn == rootTurn:
            max_possible_result = -INF
            new_state = None
            if len(self.generateMoves(currentState, currentTurn)) > 0:
                for s in self.strategies:
                    next_state = self.moveByStrategy(currentState, currentTurn, s)            
                    if next_state != None:
                        (result, state) = self.moveWithMinimax(next_state, self.getNextTurn(currentTurn), rootTurn, depth - 1)
                        if max_possible_result < result:
                            max_possible_result = result
                            new_state = next_state 
                return max_possible_result, new_state
            else:
                return self.moveWithMinimax(currentState, self.getNextTurn(currentTurn), rootTurn, depth - 1)
        else:
            min_possible_result = INF
            new_state = None
            if len(self.generateMoves(currentState, currentTurn)) > 0:
                for s in self.strategies:
                    next_state = self.moveByStrategy(currentState, currentTurn, s)
                    if next_state != None:
                        (result, state) = self.moveWithMinimax(next_state, self.getNextTurn(currentTurn), rootTurn, depth - 1)
                        if min_possible_result > result:
                            min_possible_result = result
                            new_state = next_state
                return min_possible_result, new_state
            else:
                return self.moveWithMinimax(currentState, self.getNextTurn(currentTurn), rootTurn, depth - 1)
            
    def moveWithMinimaxAlphaBeta(self, currentState, currentTurn, rootTurn, depth, alpha, beta):
        game_end = self.checkGameEnd(currentState)
        if game_end or depth == 0: 
            game_result = self.getDiscCountDifference(currentState, rootTurn)
            self.evaluation_function_calls += 1
            return game_result, currentState
        if currentTurn == rootTurn:
            new_state = None
            if len(self.generateMoves(currentState, currentTurn)) > 0:
                for s in self.strategies:
                    next_state = self.moveByStrategy(currentState, currentTurn, s)            
                    if next_state != None:
                        (result, state) = self.moveWithMinimaxAlphaBeta(next_state, self.getNextTurn(currentTurn), rootTurn, depth - 1, alpha, beta)
                        if alpha < result:
                            alpha = result
                            new_state = next_state 
                        if beta <= alpha:
                            break
                return alpha, new_state
            else:
                return self.moveWithMinimaxAlphaBeta(currentState, self.getNextTurn(currentTurn), rootTurn, depth - 1, alpha, beta)
        else:
            new_state = None
            if len(self.generateMoves(currentState, currentTurn)) > 0:
                for s in self.strategies:
                    next_state = self.moveByStrategy(currentState, currentTurn, s)
                    if next_state != None:
                        (result, state) = self.moveWithMinimaxAlphaBeta(next_state, self.getNextTurn(currentTurn), rootTurn, depth - 1, alpha, beta)
                        if beta > result:
                            beta = result
                            new_state = next_state
                        if beta <= alpha:
                            break
                return beta, new_state
            else:
                return self.moveWithMinimaxAlphaBeta(currentState, self.getNextTurn(currentTurn), rootTurn, depth - 1, alpha, beta)
            
    def printBoardState(self, boardState):
        board_state_string = '\n'
        for i in range(8):
            for j in range(8):
                board_state_string += str(boardState[i * 8 + j]) + ' '
            board_state_string += '\n'
        print(board_state_string)

    def play(self):
        while not self.checkGameEnd(self.state):    
            self.round_count += 1            
            if self.turn == 1:                
                next_state = self.moveByStrategy(self.state, self.turn, "Mobility")
                if next_state != None:
                    self.state = next_state                
                self.turn = 2
            else:
                next_state = self.moveByStrategy(self.state, self.turn, "DiscCount")  
                if next_state != None:
                    self.state = next_state
                self.turn = 1   

    def testRunningTimeOfMinimax(self, depth):
        total_time_player1 = 0
        total_time_player2 = 0
        while not self.checkGameEnd(self.state):    
            self.round_count += 1            
            if self.turn == 1:              
                begin_time = time.time()  
                (result, next_state) = self.moveWithMinimax(self.state, self.turn, 1, depth)         
                end_time = time.time()
                total_time_player1 += end_time - begin_time
                if next_state != None:
                    self.state = next_state                
                self.turn = 2
            else:
                begin_time = time.time()  
                next_state = self.moveByStrategy(self.state, self.turn, "DiscCount")
                end_time = time.time()
                total_time_player2 += end_time - begin_time
                if next_state != None:
                    self.state = next_state
                self.turn = 1   
        return total_time_player1, total_time_player2
    
    def testRunningTimeOfMinimaxWithAlphaBeta(self, depth):
        total_time_player1 = 0
        total_time_player2 = 0
        while not self.checkGameEnd(self.state):    
            self.round_count += 1            
            if self.turn == 1:              
                begin_time = time.time()  
                (result, next_state) = self.moveWithMinimaxAlphaBeta(self.state, self.turn, 1, depth, -INF, INF)         
                end_time = time.time()
                total_time_player1 += end_time - begin_time
                if next_state != None:
                    self.state = next_state                
                self.turn = 2
            else:
                begin_time = time.time()  
                next_state = self.moveByStrategy(self.state, self.turn, "DiscCount")
                end_time = time.time()
                total_time_player2 += end_time - begin_time
                if next_state != None:
                    self.state = next_state
                self.turn = 1   
        return total_time_player1, total_time_player2
    
    def getWinner(self):
        if self.checkGameEnd(self.state):
            score = self.getDiscCountDifference(self.state, 1)
            if score > 0:
                return '1'
            elif score < 0:
                return '2'
            else:
                return '0'
            
def main():
    board_state = []
    board_state_string = ''
    for i in range(8):
        line_read_string = input()
        board_state_string += ' ' + line_read_string
    board_state = list(map(int, board_state_string.split()))
    game = ReversiGame(board_state, 1)
    #game.play()
    (time1, time2) = game.testRunningTimeOfMinimaxWithAlphaBeta(5)
    game.printBoardState(game.state)
    print("Player 1's total time: %.4f s" % time1)
    print("Player 2's total time: %.4f s" % time2)
    print("Total number of rounds: " + str(game.round_count))
    winner = game.getWinner()
    if winner == 0:
        print("Draw")
    else:
        print("Player " + winner + " won")
    print("Evaluation function call count: ", game.evaluation_function_calls)
    print("Score: ", game.getDiscCountDifference(game.state, 1))

if __name__ == "__main__":
    main()
