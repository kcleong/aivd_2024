import itertools
import multiprocessing as mp
from data.horizontal import H_QA
from data.vertical import V_QA
from matrix import Matrix

N = 21
SENTINEL = None  # Special value to signal workers to stop


def process_combination(horiz_perm, vert_candidates):
    best_match_count = 0
    best_success_rate = 0
    best_vert = None

    for vert_perm in itertools.product(*vert_candidates.values()):
        matrix = Matrix(list(horiz_perm), list(vert_perm))
        matches, success_rate = matrix.count_matches()

        if matches > best_match_count:
            # print("*", end="", flush=True)
            best_match_count = matches
            best_success_rate = success_rate
            best_vert = vert_perm

    # print(".", end="", flush=True)

    return best_match_count, best_success_rate, horiz_perm, best_vert


def producer(horiz_candidates, task_queue):
    horiz_permutations = itertools.product(*horiz_candidates.values())
    for horiz_perm in horiz_permutations:
        task_queue.put(horiz_perm)

    # Signal the workers to stop by putting sentinel values
    for _ in range(mp.cpu_count()):
        task_queue.put(SENTINEL)


def consumer(task_queue, vert_candidates, result_queue):
    while True:
        horiz_perm = task_queue.get()
        if horiz_perm is SENTINEL:
            break
        result = process_combination(horiz_perm, vert_candidates)
        result_queue.put(result)


def brute_force(horiz_candidates, vert_candidates):
    best_match_count = 0
    best_success_rate = 0
    best_horiz = None
    best_vert = None

    num_processes = mp.cpu_count()

    task_queue = mp.Queue(maxsize=1000)  # Limit the queue size to control memory usage
    result_queue = mp.Queue()

    # Start the producer process
    producer_process = mp.Process(target=producer, args=(horiz_candidates, task_queue))
    producer_process.start()

    # Start consumer processes
    consumers = [
        mp.Process(target=consumer, args=(task_queue, vert_candidates, result_queue))
        for _ in range(num_processes)
    ]

    print("-" * 80)
    print("Starting the consumers")
    print("-" * 80)
    for c in consumers:
        c.start()

    print("Collect results...")
    print("-" * 80)
    producer_process.join()  # Wait for the producer to finish

    for c in consumers:
        c.join()  # Wait for all consumers to finish

    print("Analyze results...")
    print("-" * 80)

    while not result_queue.empty():
        match_count, success_rate, horiz_perm, vert_perm = result_queue.get()
        if match_count > best_match_count:
            best_match_count = match_count
            best_success_rate = success_rate
            best_horiz = horiz_perm
            best_vert = vert_perm

    # Display the best results
    print("\nBest Match Count:", best_match_count)
    print("Best Success Rate:", best_success_rate)
    # print("Best Horizontal Values:", best_horiz)
    # print("Best Vertical Values:", best_vert)
    print("\n" + "-" * 80 + "\n")

    # Print the best matrix
    if best_horiz and best_vert:
        best_matrix = Matrix(list(best_horiz), list(best_vert))
        best_matrix.print()


if __name__ == "__main__":
    brute_force(H_QA, V_QA)
