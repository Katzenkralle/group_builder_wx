from collections import defaultdict
from itertools import combinations

from main import GroupCalculator

group_calculator = GroupCalculator(12, 4)
for i in range(0, 4):
    group_calculator.create_groups()

data = group_calculator.create_groups()
print(f"Iterations: {group_calculator.counter}")
print(data)
# Initialize a dictionary to count pair occurrences
pair_counts = defaultdict(int)

# Process each sequence and group
for seq in data.values():
    for group in seq.values():
        # Get all unique pairs in the group
        for pair in combinations(group, 2):
            # Sort the pair to ensure uniqueness (order doesn't matter)
            sorted_pair = tuple(sorted(pair))
            pair_counts[sorted_pair] += 1

# Analyze distribution
pair_distribution = dict(pair_counts)
min_occurrences = min(pair_distribution.values())
max_occurrences = max(pair_distribution.values())
average_occurrences = sum(pair_distribution.values()) / len(pair_distribution)

# Print the distribution nicely formatted
print("Pair Distribution:")
for pair, count in pair_distribution.items():
    print(f"Pair {pair}: {count} occurrences")

print("\nStatistics:")
print(f"Minimum occurrences: {min_occurrences}")
print(f"Maximum occurrences: {max_occurrences}")
print(f"Average occurrences: {average_occurrences:.2f}")
