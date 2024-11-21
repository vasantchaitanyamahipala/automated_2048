import pygame
import random
from collections import deque
import time
import heapq

pygame.init()

GRID_COLOR = (187, 173, 160)
EMPTY_CELL_COLOR = (205, 193, 180)
TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}

WINDOW_SIZE = (400, 500)
GRID_SIZE = 4
CELL_SIZE = 80
GRID_PADDING = 10

screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("2048 AI")
font = pygame.font.Font(None, 36)

class Game2048:
    def __init__(self):
        self.board = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4

    def move(self, direction):
        original_board = [row[:] for row in self.board]
        merged = [[False] * 4 for _ in range(4)]

        if direction == 'left':
            for i in range(4):
                for j in range(1, 4):
                    if self.board[i][j] != 0:
                        k = j
                        while k > 0 and self.board[i][k-1] == 0:
                            self.board[i][k-1] = self.board[i][k]
                            self.board[i][k] = 0
                            k -= 1
                        if k > 0 and self.board[i][k-1] == self.board[i][k] and not merged[i][k-1]:
                            self.board[i][k-1] *= 2
                            self.score += self.board[i][k-1]
                            self.board[i][k] = 0
                            merged[i][k-1] = True

        elif direction == 'right':
            for i in range(4):
                for j in range(2, -1, -1):
                    if self.board[i][j] != 0:
                        k = j
                        while k < 3 and self.board[i][k+1] == 0:
                            self.board[i][k+1] = self.board[i][k]
                            self.board[i][k] = 0
                            k += 1
                        if k < 3 and self.board[i][k+1] == self.board[i][k] and not merged[i][k+1]:
                            self.board[i][k+1] *= 2
                            self.score += self.board[i][k+1]
                            self.board[i][k] = 0
                            merged[i][k+1] = True

        elif direction == 'up':
            for j in range(4):
                for i in range(1, 4):
                    if self.board[i][j] != 0:
                        k = i
                        while k > 0 and self.board[k-1][j] == 0:
                            self.board[k-1][j] = self.board[k][j]
                            self.board[k][j] = 0
                            k -= 1
                        if k > 0 and self.board[k-1][j] == self.board[k][j] and not merged[k-1][j]:
                            self.board[k-1][j] *= 2
                            self.score += self.board[k-1][j]
                            self.board[k][j] = 0
                            merged[k-1][j] = True

        elif direction == 'down':
            for j in range(4):
                for i in range(2, -1, -1):
                    if self.board[i][j] != 0:
                        k = i
                        while k < 3 and self.board[k+1][j] == 0:
                            self.board[k+1][j] = self.board[k][j]
                            self.board[k][j] = 0
                            k += 1
                        if k < 3 and self.board[k+1][j] == self.board[k][j] and not merged[k+1][j]:
                            self.board[k+1][j] *= 2
                            self.score += self.board[k+1][j]
                            self.board[k][j] = 0
                            merged[k+1][j] = True

        if self.board != original_board:
            self.add_new_tile()

    def is_game_over(self):
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0:
                    return False
                if i < 3 and self.board[i][j] == self.board[i+1][j]:
                    return False
                if j < 3 and self.board[i][j] == self.board[i][j+1]:
                    return False
        return True
    
class AStarNode:
    def __init__(self, board, score, moves, heuristic_value):
        self.board = board
        self.score = score
        self.moves = moves
        self.heuristic_value = heuristic_value

    def __lt__(self, other):
        return (self.score + self.heuristic_value) > (other.score + other.heuristic_value)

def heuristic_empty_tiles(board):
    return sum(row.count(0) for row in board)

def astar_empty_tiles_ai(game, depth):
    return astar_ai(game, depth, heuristic_empty_tiles)

def heuristic_max_tile(board):
    return max(max(row) for row in board)

def astar_max_tile_ai(game, depth):
    return astar_ai(game, depth, heuristic_max_tile)

def heuristic_monotonicity(board):
    def calculate_monotonicity(sequence):
        increasing = decreasing = 0
        for i in range(len(sequence) - 1):
            if sequence[i] <= sequence[i+1]:
                increasing += sequence[i+1] - sequence[i]
            if sequence[i] >= sequence[i+1]:
                decreasing += sequence[i] - sequence[i+1]
        return max(increasing, decreasing)

    monotonicity = 0
    # Check rows
    for row in board:
        monotonicity += calculate_monotonicity(row)
    # Check columns
    for col in range(4):
        column = [board[row][col] for row in range(4)]
        monotonicity += calculate_monotonicity(column)
    
    return monotonicity


def astar_monotonicity_ai(game, depth):
    return astar_ai(game, depth, heuristic_monotonicity)

def heuristic_clustering(board):
    def manhattan_distance(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    clustering_score = 0
    for i in range(4):
        for j in range(4):
            if board[i][j] != 0:
                for k in range(4):
                    for l in range(4):
                        if board[k][l] != 0:
                            distance = manhattan_distance(i, j, k, l)
                            value_difference = abs(board[i][j] - board[k][l])
                            clustering_score -= value_difference / (distance + 1)

    return clustering_score

def astar_clustering_ai(game, depth):
    return astar_ai(game, depth, heuristic_clustering)

def heuristic_combination(board):
    return 0.6*heuristic_empty_tiles(board) + 0.6*heuristic_max_tile(board) + 0.2*heuristic_monotonicity(board) + 0.2*heuristic_clustering(board)+0.6*heuristic_adjacency(board)

def astar_combination_ai(game, depth):
    return astar_ai(game, depth, heuristic_combination)


def heuristic_adjacency(board):
    adjacency_score = 0
    for i in range(4):
        for j in range(4):
            if board[i][j] != 0:
                if i < 3 and board[i][j] == board[i+1][j]:  
                    adjacency_score += board[i][j]
                if j < 3 and board[i][j] == board[i][j+1]:  
                    adjacency_score += board[i][j]
    return adjacency_score

def astar_adjacency_ai(game, depth):
    return astar_ai(game, depth, heuristic_adjacency)


def astar_ai(game, depth, heuristic_func):
    start_node = AStarNode(game.board, game.score, [], heuristic_func(game.board))
    pq = [start_node]
    best_score = 0
    best_moves = []

    for _ in range(depth):
        if not pq:
            break

        current_node = heapq.heappop(pq)

        if current_node.score > best_score:
            best_score = current_node.score
            best_moves = current_node.moves

        for direction in ['up', 'down', 'left', 'right']:
            new_game = Game2048()
            new_game.board = [row[:] for row in current_node.board]
            new_game.score = current_node.score
            new_game.move(direction)

            if new_game.board != current_node.board:
                new_moves = current_node.moves + [direction]
                heuristic_value = heuristic_func(new_game.board)
                new_node = AStarNode(new_game.board, new_game.score, new_moves, heuristic_value)
                heapq.heappush(pq, new_node)

    return best_moves[0] if best_moves else random.choice(['up', 'down', 'left', 'right'])




def bfs_ai(game, depth):
    queue = deque([(game.board, [], game.score)])
    best_score = 0
    best_moves = []

    for _ in range(depth):
        level_size = len(queue)
        for _ in range(level_size):
            current_board, moves, current_score = queue.popleft()
            for direction in ['up', 'down', 'left', 'right']:
                new_game = Game2048()
                new_game.board = [row[:] for row in current_board]
                new_game.score = current_score
                new_game.move(direction)
                
                if new_game.board != current_board:
                    new_moves = moves + [direction]
                    
                    if new_game.score > best_score:
                        best_score = new_game.score
                        best_moves = new_moves
                    
                    queue.append((new_game.board, new_moves, new_game.score))

    return best_moves[0] if best_moves else random.choice(['up', 'down', 'left', 'right'])

def dfs_ai(game, depth):
    def dfs(board, moves, score, current_depth):
        if current_depth == depth:
            return score, moves

        best_score = score
        best_moves = moves

        for direction in ['up', 'down', 'left', 'right']:
            new_game = Game2048()
            new_game.board = [row[:] for row in board]
            new_game.score = score
            new_game.move(direction)

            if new_game.board != board:
                new_score, new_moves = dfs(new_game.board, moves + [direction], new_game.score, current_depth + 1)
                if new_score > best_score:
                    best_score = new_score
                    best_moves = new_moves

        return best_score, best_moves

    _, best_moves = dfs(game.board, [], game.score, 0)
    return best_moves[0] if best_moves else random.choice(['up', 'down', 'left', 'right'])

def draw_game(game):
    screen.fill(GRID_COLOR)
    for i in range(4):
        for j in range(4):
            value = game.board[i][j]
            color = TILE_COLORS.get(value, TILE_COLORS[2048])
            pygame.draw.rect(screen, color, (j * (CELL_SIZE + GRID_PADDING) + GRID_PADDING,
                                             i * (CELL_SIZE + GRID_PADDING) + GRID_PADDING + 100,
                                             CELL_SIZE, CELL_SIZE))
            if value != 0:
                text_surface = font.render(str(value), True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(j * (CELL_SIZE + GRID_PADDING) + GRID_PADDING + CELL_SIZE // 2,
                                                          i * (CELL_SIZE + GRID_PADDING) + GRID_PADDING + CELL_SIZE // 2 + 100))
                screen.blit(text_surface, text_rect)

    score_text = font.render(f"Score: {game.score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

def play_game(ai_function):
    game = Game2048()
    move_count = 0
    clock = pygame.time.Clock()

    while not game.is_game_over():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        move = ai_function(game, depth=4)
        game.move(move)
        move_count += 1
        print(f"Move {move_count}: {move}")
        print(f"Score: {game.score}")

        draw_game(game)
        clock.tick(2)  # Limit to 2 FPS for visibility

    print("Game Over!")
    print(f"Final Score: {game.score}")
    print(f"Max tile: {max(max(row) for row in game.board)}")
    print(f"Total moves: {move_count}")

    # Keep the window open after game over
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
def main():
    print("Choose AI algorithm:")
    print("1. BFS (Breadth-First Search)")
    print("2. DFS (Depth-First Search)")
    print("3. A* (Empty Tiles Heuristic)")
    print("4. A* (Max Tile Heuristic)")
    print("5. A* (Monotonicity Heuristic)")
    print("6. A* (Clustering Heuristic)")
    print("7. A* (Adjacency Heuristic)")
    print("8. A* (Combination Heuristic)")
    
    choice = input("Enter your choice (1, 2, 3, 4, 5, 6, 7 or 8): ")
    
    if choice == '1':
        print("Using BFS algorithm")
        play_game(bfs_ai)
    elif choice == '2':
        print("Using DFS algorithm")
        play_game(dfs_ai)
    elif choice == '3':
        print("Using A* algorithm with Empty Tiles heuristic")
        play_game(astar_empty_tiles_ai)
    elif choice == '4':
        print("Using A* algorithm with Max Tile heuristic")
        play_game(astar_max_tile_ai)
    elif choice == '5':
        print("Using A* algorithm with Monotonicity heuristic")
        play_game(astar_monotonicity_ai)
    elif choice == '6':
        print("Using A* algorithm with Clustering heuristic")
        play_game(astar_clustering_ai)
    elif choice == '7':
        print("Using A* algorithm with Adjacency heuristic")
        play_game(astar_adjacency_ai)
    elif choice == '8':
        print("Using A* algorithm with Combination heuristic")
        play_game(astar_combination_ai)
    else:
        print("Invalid choice. Defaulting to BFS.")
        play_game(bfs_ai)


if __name__ == "__main__":
    main()