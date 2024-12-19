import itertools
import heapq
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

    # Min-heap to keep track of the top 10 matches
    top_matches = []
    best_match_count = 0

    print("=" * 80)
    print(f"\nUsing {NUM_PROCESSES} processes")
    print(f"Batch size {format_number(BATCH_SIZE)}")

    with ProcessPoolExecutor(max_workers=NUM_PROCESSES) as executor:
        for i, batch in enumerate(batched_permutations(horiz_candidates, BATCH_SIZE)):
            futures = [
                executor.submit(process_combination, horiz_perm, vert_candidates)
                for horiz_perm in batch
            ]

            for future in futures:
                match_count, success_rate, horiz_perm, vert_perm = future.result()

                # Store the result as a tuple (match_count, success_rate, horiz_perm, vert_perm)
                result = (match_count, success_rate, horiz_perm, vert_perm)

                if match_count > best_match_count:
                    if len(top_matches) < 10:
                        heapq.heappush(top_matches, result)
                    else:
                        heapq.heappushpop(top_matches, result)

            print(f"Processed batch {i + 1}")

    print(f"\nTotal count_matches calls: {format_number((i + 1) * BATCH_SIZE)}")
    print("Analyze results...")
    print("-" * 80)

    # Sort the top matches in descending order
    top_matches.sort(reverse=True, key=lambda x: x[0])

    # Display the top 10 results with their matrices
    for rank, (match_count, success_rate, horiz_perm, vert_perm) in enumerate(
        top_matches, start=1
    ):
        print(f"Rank {rank}:")
        print(f"  Match Count: {match_count}")
        print(f"  Success Rate: {success_rate:.4f}")
        print(f"  Horizontal Permutation: {horiz_perm}")
        print(f"  Vertical Permutation: {vert_perm}")

        # Create and print the matrix for this match
        best_matrix = Matrix(list(horiz_perm), list(vert_perm))
        best_matrix.print()

        print("=" * 80)

    print(f"Total Time: {time.time() - start_time}")


if __name__ == "__main__":
    brute_force(
        list(H_QA.values()),
        list(V_QA.values()),
    )
