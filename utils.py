from collections import defaultdict
from itertools import combinations
from bs4 import UnicodeDammit

def test_uniqueness(data):
    pair_counts = defaultdict(int)
    for seq in data.values():
        for group in seq.values():
            # Get all unique pairs in the group
            for pair in combinations(group, 2):
                # Sort the pair to ensure uniqueness (order doesn't matter)
                sorted_pair = tuple(sorted(pair))
                pair_counts[sorted_pair] += 1
    pair_distribution = dict(pair_counts)
    return [min(pair_distribution.values()), max(pair_distribution.values()), sum(pair_distribution.values()) / len(pair_distribution)]

def detect_encoding(file_path):
    finder = UnicodeDammit(open(file_path, 'rb').read())
    return finder.original_encoding
