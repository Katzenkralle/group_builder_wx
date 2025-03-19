from collections import defaultdict
from itertools import combinations
from chardet.universaldetector import UniversalDetector

import threading
import ctypes

def test_uniqueness(data):
    """
    Test the of pairs in multiple iterations of provided groups.

    :param data: The data to test.
    :type data: dict[str, dict[str, list[str]]]

    :return: A list containing the minimum, maximum, and average number of pairs in the data. 
    :rtype: list[int, int, float]
    """
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
    """
    Detects the encoding of the file at the given path.
    Defaults to utf-8 if the encoding can not be detected.

    :param file_path: The path to the file.
    :type file_path: str

    :return: The encoding of the file.
    :rtype: str
    """
    detector = UniversalDetector()
    with open(file_path, 'rb') as file:
        for line in file:
            detector.feed(line)
            if detector.done: break
    detector.close()
    return detector.result.get('encoding', "utf-8")

class KillableThread(threading.Thread):
    """
    A thread class that supports killing the thread using ctypes.
    It is not recommended for it may cause invalid states but it is the only way to kill a thread
    that dose not listen to a flag.
    """
    def __init__(self, *args, **kwargs):
        """
        `See threading.Thread.__init__`
        """
        super().__init__(*args, **kwargs)

    def kill(self):
        """
        Forcibly kills the thread using ctypes (use with caution).
        
        :raises RuntimeError: If the thread could not be killed.

        :return: None
        """
        if not self.is_alive() or self.ident is None:
            return
        
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self.ident), ctypes.py_object(SystemExit)
        )
        
        if res == 1:
            print(f"\nSuccessfully killed thread {self.ident}.")
        else:
            # Reset the exception if something went wrong
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.ident), 0)
            raise RuntimeError(f"\nFailed to kill thread {self.ident}")
