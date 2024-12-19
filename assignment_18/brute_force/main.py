import itertools
import multiprocessing as mp
import time

from data.horizontal import H_QA
from data.vertical import V_QA
from matrix import Matrix

N = 21
SENTINEL = None  # Special value to signal workers to stop
NUM_PROCESSES = mp.cpu_count()
QUEUE_SIZE = 2000
BATCH_SIZE = 10


def format_number(number):
    return format(number, "_")


def process_combination(horiz_perm, vert_candidates, count_counter, counter_lock):
    best_match_count = 0
    best_success_rate = 0
    best_vert = None

    for vert_perm in itertools.product(*vert_candidates):
        matrix = Matrix(list(horiz_perm), list(vert_perm))

        # Increment the counter
        with counter_lock:
            count_counter.value += 1

        if count_counter.value % 1_000_000 == 0:
            print(f"count_matches calls: {format_number(count_counter.value)}")

        matches, success_rate = matrix.count_matches()

        if matches > best_match_count:
            best_match_count = matches
            best_success_rate = success_rate
            best_vert = vert_perm
    return best_match_count, best_success_rate, horiz_perm, best_vert


def producer(horiz_candidates, task_queue):
    horiz_permutations = itertools.product(*horiz_candidates)

    for horiz_perm in horiz_permutations:
        try:
            task_queue.put(horiz_perm, timeout=5)
        except mp.queues.Full:
            print("Queue is full, skipping result.")

    # Signal the workers to stop by putting sentinel values
    for _ in range(NUM_PROCESSES * 2):
        task_queue.put(SENTINEL)


def consumer(task_queue, vert_candidates, result_queue, count_counter, counter_lock):
    while True:
        try:
            horiz_perm = task_queue.get(
                timeout=5
            )  # Add timeout to avoid indefinite blocking
        except mp.queues.Empty:
            print("Queue is empty, stopping consumer.")
            break

        if horiz_perm is SENTINEL:
            print("BREAK")
            break

        result = process_combination(
            horiz_perm, vert_candidates, count_counter, counter_lock
        )
        result_queue.put(result)

    print("**QUIT**")


def brute_force(horiz_candidates, vert_candidates):
    start_time = time.time()

    best_match_count = 0
    best_success_rate = 0
    best_horiz = None
    best_vert = None

    print("=" * 80)
    print(f"\nProcess count: {NUM_PROCESSES}")

    task_queue = mp.Queue(
        maxsize=QUEUE_SIZE
    )  # Limit the queue size to control memory usage
    result_queue = mp.Queue()

    # Shared counter and lock for counting calls
    count_counter = mp.Value("i", 0)  # Shared integer counter initialized to 0
    counter_lock = mp.Lock()  # Lock to synchronize access to the counter

    # Start the producer process
    producer_process = mp.Process(target=producer, args=(horiz_candidates, task_queue))
    producer_process.start()

    # Start consumer processes
    consumers = [
        mp.Process(
            target=consumer,
            args=(
                task_queue,
                vert_candidates,
                result_queue,
                count_counter,
                counter_lock,
            ),
        )
        for _ in range(NUM_PROCESSES)
    ]

    for c in consumers:
        c.start()

    print("-" * 80)
    print("Starting producer process...")
    print("-" * 80)
    producer_process.join()  # Wait for the producer to finish

    print("-" * 80)
    print("Starting consumer processes...")
    print("-" * 80)

    for c in consumers:
        print(f"Joining consumer {c.name}")
        c.join(timeout=0.1)
        if c.is_alive():
            c.terminate()

    print(f"Total count_matches calls: {format_number(count_counter.value)}\n")

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
    print("\n" + "-" * 80 + "\n")

    print(f"Total Time: {time.time() - start_time}")

    # Print the best matrix
    if best_horiz and best_vert:
        best_matrix = Matrix(list(best_horiz), list(best_vert))
        best_matrix.print()


if __name__ == "__main__":
    brute_force(
        list(H_QA.values()),
        list(V_QA.values()),
    )
