import itertools
from concurrent.futures import ProcessPoolExecutor
import time

from data.horizontal import H_QA
from data.vertical import V_QA
from matrix import Matrix

N = 21
NUM_PROCESSES = 10  # Adjust based on your CPU cores
BATCH_SIZE = 10_000  # Number of permutations to process in each batch


def format_number(number):
    return format(number, "_")


def process_combination(horiz_perm, vert_candidates):
    best_match_count = 0
    best_success_rate = 0
    best_vert = None

    for vert_perm in itertools.product(*vert_candidates):
        matrix = Matrix(list(horiz_perm), list(vert_perm))
        matches, success_rate = matrix.count_matches()

        if matches > best_match_count:
            best_match_count = matches
            best_success_rate = success_rate
            best_vert = vert_perm

    return best_match_count, best_success_rate, horiz_perm, best_vert


def batched_permutations(horiz_candidates, batch_size):
    """Generator that yields batches of permutations."""
    horiz_permutations = itertools.product(*horiz_candidates)
    batch = []

    for perm in horiz_permutations:
        batch.append(perm)
        if len(batch) >= batch_size:
            yield batch
            batch = []

    # Yield any remaining permutations
    if batch:
        yield batch


def brute_force(horiz_candidates, vert_candidates):
    start_time = time.time()

    best_match_count = 0
    best_success_rate = 0
    best_horiz = None
    best_vert = None

    print("=" * 80)
    print(f"\nUsing {NUM_PROCESSES} processes")

    with ProcessPoolExecutor(max_workers=NUM_PROCESSES) as executor:
        for i, batch in enumerate(batched_permutations(horiz_candidates, BATCH_SIZE)):
            futures = [
                executor.submit(process_combination, horiz_perm, vert_candidates)
                for horiz_perm in batch
            ]

            for future in futures:
                match_count, success_rate, horiz_perm, vert_perm = future.result()

                if match_count > best_match_count:
                    best_match_count = match_count
                    best_success_rate = success_rate
                    best_horiz = horiz_perm
                    best_vert = vert_perm

            print(f"Processed batch {i + 1}")

    print(f"\nTotal count_matches calls: {format_number((i + 1) * BATCH_SIZE)}")
    print("Analyze results...")
    print("-" * 80)

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
