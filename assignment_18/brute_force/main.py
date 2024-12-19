import itertools
import json
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

from data.horizontal import H_QA
from data.vertical import V_QA
from matrix import Matrix

N = 21
NUM_PROCESSES = 11  # Adjust based on your CPU cores
BATCH_SIZE = 100_000  # Number of permutations to process in each batch


def format_number(number):
    return format(number, "_")


def process_combination(horiz_perm, vert_candidates):
    results = []
    for vert_perm in itertools.product(*vert_candidates):
        matrix = Matrix(list(horiz_perm), list(vert_perm))
        match_count, success_rate = matrix.count_matches()

        results.append((match_count, success_rate, horiz_perm, vert_perm))

    return results


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

    # Min-heap to keep txack of the top 10 matches
    total_iterations = 0
    best_match_count = 0
    top_matches = []

    print("=" * 80)
    print(f"\nUsing {NUM_PROCESSES} processes")
    print(f"Batch size {format_number(BATCH_SIZE)}\n")

    with ProcessPoolExecutor(max_workers=NUM_PROCESSES) as executor:
        for i, batch in enumerate(batched_permutations(horiz_candidates, BATCH_SIZE)):
            batch_iterations = 0
            batch_start_time = time.time()

            futures = [
                executor.submit(process_combination, horiz_perm, vert_candidates)
                for horiz_perm in batch
            ]

            for future in futures:
                for match_count, success_rate, horiz_perm, vert_perm in future.result():
                    batch_iterations += 1

                    if match_count > best_match_count:
                        best_match_count = match_count

                        result = (match_count, success_rate, horiz_perm, vert_perm)

                        top_matches.insert(0, result)
                        top_matches = top_matches[:10]

            batch_end_time = time.time()
            batch_duration = int(batch_end_time - batch_start_time)
            iterations_per_second = int(
                len(batch) / batch_duration if batch_duration > 0 else 0
            )
            total_iterations += batch_iterations

            print(
                " / ".join(
                    [
                        f"Processed batch {i + 1}",
                        f"{batch_duration}s",
                        f"iterations p/s {format_number(iterations_per_second)}",
                        format_number(batch_iterations),
                    ]
                )
            )

    print(f"\nTotal count_matches calls: {format_number(total_iterations)}")
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

    # Save top matches to a timestamped JSON file
    timestamp = datetime.now().isoformat()
    filename = f"top_matches_{timestamp}.json"

    # Convert top_matches to a JSON-compatible format
    top_matches_serializable = [
        {
            "match_count": int(match_count),
            "success_rate": int(success_rate),
            "horizontal_permutation": horiz_perm,
            "vertical_permutation": vert_perm,
        }
        for match_count, success_rate, horiz_perm, vert_perm in top_matches
    ]

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(top_matches_serializable, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    brute_force(
        list(H_QA.values()),
        list(V_QA.values()),
    )
