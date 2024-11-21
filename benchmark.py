import time
from sys import getsizeof
from collections import defaultdict
from src.game_2048 import bfs_ai, dfs_ai, astar_empty_tiles_ai, astar_max_tile_ai, astar_monotonicity_ai, astar_clustering_ai, astar_combination_ai,astar_adjacency_ai, Game2048

def benchmark_ai(algorithms, num_runs, depth=3):
    """
    Benchmark different AI algorithms for the 2048 game.

    :param algorithms: A dictionary of algorithm names and their corresponding functions.
    :param num_runs: Number of times to run each algorithm.
    :param depth: Depth parameter for AI algorithms.
    :return: None
    """
    results = defaultdict(lambda: {
        "total_score": 0,
        "total_moves": 0,
        "total_time": 0,
        "space_usage": [],
        "total_time_per_move": 0
    })

    for name, ai_func in algorithms.items():
        print(f"Running {name} for {num_runs} iterations...")
        for _ in range(num_runs):
            # Initialize game
            game = Game2048()
            
            # Track space and time usage
            start_time = time.time()
            total_memory = getsizeof(game)  # Track initial memory

            move_count = 0
            while not game.is_game_over():
                move_start_time = time.time()  # Time for each move
                move = ai_func(game, depth)
                total_memory += getsizeof(move)
                game.move(move)
                move_count += 1
                move_end_time = time.time()

                # Accumulate time per move
                results[name]["total_time_per_move"] += (move_end_time - move_start_time)

            end_time = time.time()
            elapsed_time = end_time - start_time

            # Update results
            results[name]["total_score"] += game.score
            results[name]["total_moves"] += move_count
            results[name]["total_time"] += elapsed_time
            results[name]["space_usage"].append(total_memory)

        print(f"Completed {name}.")

    # Compute and display averages
    print("\n--- Benchmark Results ---")
    for name, data in results.items():
        avg_score = data["total_score"] / num_runs
        avg_moves = data["total_moves"] / num_runs
        avg_time = data["total_time"] / num_runs
        avg_space = sum(data["space_usage"]) / len(data["space_usage"])
        avg_time_per_move = data["total_time_per_move"] / data["total_moves"]

        print(f"Algorithm: {name}")
        print(f"  Average Score: {avg_score}")
        print(f"  Average Moves: {avg_moves}")
        print(f"  Average Time (s): {avg_time:.2f}")
        print(f"  Average Time per Move (s): {avg_time_per_move:.4f}")
        print(f"  Average Space Used (bytes): {avg_space:.2f}\n")

if __name__ == "__main__":
    algorithms = {
        "BFS": bfs_ai,
        "DFS": dfs_ai,
        "A* (Empty Tiles)": astar_empty_tiles_ai,
        "A* (Max Tile)": astar_max_tile_ai,
        "A* (Monotonicity)": astar_monotonicity_ai,
        "A* (Clustering)": astar_clustering_ai,
        "A% (Adjacency)" : astar_adjacency_ai,
        "A* (Combined Heuristics)": astar_combination_ai
    }
    
    num_runs = int(input("Enter the number of iterations for benchmarking: "))
    benchmark_ai(algorithms, num_runs)
