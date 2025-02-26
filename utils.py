from collections import defaultdict
from itertools import combinations
from chardet.universaldetector import UniversalDetector

import threading
import ctypes

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
    detector = UniversalDetector()
    with open(file_path, 'rb') as file:
        for line in file:
            detector.feed(line)
            if detector.done: break
    detector.close()
    return detector.result.get('encoding', "utf-8")

class KillableThread(threading.Thread):
    def __init__(self, target=None, args=(), kwargs=None, daemon=True):
        super().__init__(target=target, args=args, kwargs=kwargs or {}, daemon=daemon)

    def kill(self):
        """Forcibly kills the thread using ctypes (use with caution)."""
        if not self.is_alive() or self.ident is None:
            return
        
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self.ident), ctypes.py_object(SystemExit)
        )
        
        if res == 1:
            print(f"\nSuccessfully killed thread {self.ident}.", end="")
        else:
            # Reset the exception if something went wrong
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.ident), 0)
            raise RuntimeError(f"\nFailed to kill thread {self.ident}", end="")
