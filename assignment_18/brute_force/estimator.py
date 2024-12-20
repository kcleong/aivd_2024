from data.horizontal import H_QA
from data.vertical import V_QA


ITERATIONS_PER_SEC = 100_000


def format_number(number):
    return format(number, "_")


def count_possibilities(horiz_candidates, vert_candidates):
    # Calculate the product of possibilities for horizontal candidates
    horiz_counts = [len(options) for options in horiz_candidates.values()]
    total_horiz_possibilities = 1
    for count in horiz_counts:
        total_horiz_possibilities *= count

    # Calculate the product of possibilities for vertical candidates
    vert_counts = [len(options) for options in vert_candidates.values()]
    total_vert_possibilities = 1
    for count in vert_counts:
        total_vert_possibilities *= count

    # Total possibilities is the product of horizontal and vertical possibilities
    total_possibilities = total_horiz_possibilities * total_vert_possibilities

    # Print details
    print("Horizontal possibilities per category:")
    for category, count in zip(horiz_candidates.keys(), horiz_counts):
        print(f"  {category}: {count} options")

    print("\nVertical possibilities per category:")
    for category, count in zip(vert_candidates.keys(), vert_counts):
        print(f"  {category}: {count} options")

    print("\nTotal horizontal possibilities:", format_number(total_horiz_possibilities))
    print("Total vertical possibilities:", format_number(total_vert_possibilities))
    print("\nTotal combined possibilities:", format_number(total_possibilities))

    total_secs = total_possibilities / ITERATIONS_PER_SEC
    total_hours = total_secs / 3600
    total_days = total_hours / 24
    total_years = total_days / 365.242374

    print("\nTotal runtime in seconds: ", format_number(int(total_secs)))
    print("Total runtime in hours: ", format_number(int(total_hours)))
    print("Total runtime in days: ", format_number(int(total_days)))
    print("Total runtime in years: ", format_number(int(total_years)))
    return total_possibilities


if __name__ == "__main__":
    total = count_possibilities(H_QA, V_QA)
