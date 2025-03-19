import random
from itertools import combinations
from dataclasses import dataclass
from .utils import test_uniqueness, detect_encoding
import csv
import time
from copy import deepcopy
import sys
from itertools import chain

@dataclass
class GroupCandidates:
    """
    Represents a group of candidates.
    """
    members: list[int]  #: A list of integers representing the members of the group.
    collisions: int  #: The number of collisions or conflicts within the group.


@dataclass
class CsvMeta:
    """
    Meta data about the CSV file opend by the user.
    """
    dialect: csv.Dialect #: The dialect of the CSV file. Includes the delimiter and other information.
    header: bool #: If the CSV file has a header.
    headers: list[str] #: A list of the headers in the CSV file. Or [Column n] if no header is present.
    path: str #: The path to the CSV file.
    encoding: str #: The encoding of the CSV file.



class GroupCalculator:
    """
    Class that is to be used to create groups given a number of members and groups.
    If the number of members is less than the number of groups, an exception is raised.
    Multiple iterations can be created by calling the :meth:`create_groups` method multiple times. Each iteration attempts to avoid reoccurring pairs of members.
    If the number of students cannot be divided evenly by the number of groups, 
    the remaining members are added to the groups one of the smalest groups with the least amount of conflicts.
    This class is meant to be used as a singleton.
    """

    instance = None

    def __new__(cls, *args, **kwargs):
        """
        Singleton implementation for the :class:`GroupCalculator` class.
        Returns the existing instance if it exists, else creates a new instance.

        :return: The :class:`GroupCalculator` object.
        """
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance._singolton_init(*args, **kwargs)
        return cls.instance

    def _singolton_init(self, n_members: int|None = 0, n_groups: int | None = None, allow_setting_invalid_inputs: bool = True):
        """
        Initializes the :class:`GroupCalculator` object. Optionally sets the number of members and groups.

        :param n_members: The number of members in the group.
        :type n_members: int
        :param n_groups: The number of groups to divide the members into.
        :type n_groups: int
        :param allow_setting_invalid_inputs: If True, the number of members and groups can be set to 0, non Int or None.
        :type allow_setting_invalid_inputs: bool

        :raises ValueError: The number of members or groups is invalid or set to an uncompatible value.

        :return: None
        """
        self.__allow_setting_invalid_inputs = allow_setting_invalid_inputs
        if n_members != None and n_groups != None and n_members <= n_groups:
            raise ValueError("The number of members must be greater than the number of groups")
        self.__n_members: int|None = n_members
        self.__n_groups: int|None = n_groups

        self.__group_size: int|None = None
        self.__try_calc_group_size()

        self.__whitlist: dict[int, set[int]] | None = None
        self.__csv_meta = CsvMeta(None, False, [], None, None)

        self.groups: dict[int, dict[str, list[str]]] = {}
        self.alias = {}
        self.__pair_repetition_brakepoinnt = sys.maxsize

    @staticmethod
    def get_group_letter(group: int) -> str:
        """
        Returns the string representation of a group number.
        For example: 0 returns 'A', 1 returns 'B', and 26 returns 'AA'.

        :param group: The group number.
        :type group: int

        :return: The string representation of the group number.
        :rtype: str
        """
        res = "" 
        if group > 25:
            res += GroupCalculator.get_group_letter(group // 26)
        return f"{res}{chr(65 + group)}"

    def __replace_with_alias(self, iteration):
        """
        Replaces the members in the group with their aliases.

        :param iteration: The iteration to replace the members in.
        :type iteration: dict[str, list[str]]

        :return: The iteration with the members replaced by their aliases.
        :rtype: dict[str, list[str]]        
        """
        for _, members in iteration.items():
            for member in members:
                member = self.alias.get(member, member)
        return iteration
    
    def __try_calc_group_size(self):
        """
        Attempts to calculate the group size based on the number of members and groups
        if the number of members and groups are set. Else does nothing.

        :return: None
        """
        if self.__n_members is not None and self.__n_groups is not None and self.__n_groups > 0:
            self.__group_size = self.__n_members // self.__n_groups

    @property
    def pair_repetition_brakepoinnt(self):
        """
        ‎ 

        :return: The iteration number where the first pair repetition was detected.
        :rtype: int
        """
        return self.__pair_repetition_brakepoinnt

    @property
    def n_members(self):
        """
        ‎ 

        :return: Returns the number of members in the group.
        :rtype: int
        """
        return self.__n_members

    @n_members.setter
    def n_members(self, value: int):
        """
        Sets the number of members in the group. If the value is less than or equal to 0, a ValueError is raised unless allow invalid inputs where allowed during creation.

        :param value: The number of members in the group.
        :type value: int

        :raises ValueError: The number of members is less than or equal to 0.

        :return: None        
        """
        if not self.__allow_setting_invalid_inputs and value is not None and value <= 0:
            raise ValueError("The number of students must be greater than 0")
        self.reset_groups()
        self.__n_members = value
        self.__try_calc_group_size()

    @property
    def n_groups(self):
        """
        ‎

        :return: The number of groups to divide the members into.
        :rtype: int
        """
        return self.__n_groups
    
    @n_groups.setter
    def n_groups(self, value: int):
        """
        Sets the number of groups to divide the members into. If the value is less than or equal to 0, a ValueError is raised unless allow invalid inputs where allowed during creation.

        :param value: The number of groups to divide the members into.
        :type value: int

        :raises ValueError: The number of groups is less than or equal to 0.

        :return: None
        """
        if not self.__allow_setting_invalid_inputs and value is not None and value <= 0:
            raise ValueError("The number of groups must be greater than 0")
        self.reset_groups()
        self.__n_groups = value
        self.__try_calc_group_size()

    def get_iteration(self):
        """
        Returns the current iteration number. -1 if no iterations have been created.

        :return: The current iteration number.
        :rtype: int
        """
        return max(self.groups.keys(), default=-1) 

    def create_groups(self):
        """
        Creates groups based on the number of members and groups set during object creation.
        If the number of members or groups is not set, a ValueError is raised.

        :raises ValueError: The number of students and groups must be set before creating groups.

        :return: All groups from all iterations.
        :rtype: dict[int, dict[str, list[str]]]
        """
        print("clear")
        print("Creating groups...")

        if self.__n_members is None or self.__n_groups is None or self.__n_groups == 0 or self.__n_members == 0:
            raise ValueError("The number of students and groups must be set before creating groups")
        if self.__n_groups >= self.__n_members:
            raise ValueError("The number of students must be greater than the number of groups")
        
        students_list: list[int] = list(range(self.__n_members))
        this_iteration = self.get_iteration()+1

        if self.__whitlist is None:
            random.shuffle(students_list)
            self.__whitlist = {student: list(filter(lambda x: x != student, students_list)) for student in students_list}
        else:
            for student in self.__whitlist:
                self.__whitlist[student]

        # Assemble the groups
        g_rest = self.__n_members % self.__n_groups
        group_layout: dict[str, list[int]] = {key: [-1 for _ in range(self.__group_size)] for key in map(GroupCalculator.get_group_letter, range(self.__n_groups))}
        for i in range(0, g_rest):
            group_layout[GroupCalculator.get_group_letter(i)].append(-1)

        virtual_members = {key: [] for key in group_layout} # Alternaativly pass blocked groups around (might be faster)
        # Note the CR will never match none whitlist pairs
        def change_request(whitelist_requirement: int, _future_layout: dict[str, list[int]]) : # [bool, list[str] | dict[str, list[int]]]]
            # Finde optimal destaination, the handover if required
            group_ranking = []
            for group in filter(lambda x: not all(y == -2 for y in _future_layout[x]) and # The group compleatly blocked \
                    list(filter(lambda z: whitelist_requirement not in self.__whitlist.get(z, students_list), virtual_members.get(x, []))) == [],  # The group is blocked by a member that is to be added to the group \
                _future_layout):
                # Lowest is best
                group_ranking.append([group, sum(map(lambda x: x!=-1 and (x not in self.__whitlist[whitelist_requirement]), _future_layout[group]))])
            best_match = sorted(group_ranking, key=lambda x: x[1])

            for destination in map(lambda x: x[0], best_match):
                future_layout = deepcopy(_future_layout)
                blocking_members = list(filter(lambda x: whitelist_requirement not in self.__whitlist.get(x, students_list), future_layout[destination]))
                
                if -1 not in future_layout[destination] and blocking_members == []:
                    # Happens when destination is full and no collision is present
                    continue
                    blocking_members.append(list(filter(lambda x: x != -2, future_layout[destination]))[0])

                for blocker in blocking_members:
                    if blocker not in future_layout[destination]:
                        #print(f"Blocker {blocker} not anymore in group {destination}, skipping")
                        continue
                    change_at_index = future_layout[destination].index(blocker)
                    future_layout[destination][change_at_index] = -2 # Mark as blocked/imovable

                    virtual_members[destination].append(blocker)
                    response = change_request(whitelist_requirement=blocker, _future_layout=future_layout)
                    virtual_members[destination].remove(blocker)

                    if response is not None:
                        future_layout = response
                    else:
                        #print(f"Could not find a solution for blocker {blocker} while trying to fit {whitelist_requirement} in {destination}")
                        # no need to reset future_layout[destination][change_at_index] = blocker for we deepcopied
                        break
                    future_layout[destination][change_at_index] = -1
                else:
                    future_layout[destination][future_layout[destination].index(-1)] = whitelist_requirement
                    #print(f"Added {whitelist_requirement} to {destination}")
                    return future_layout
                continue
            return None
        # Add the members to the groups
        added_members = []
        i = 0 # I __should__ never become maxsize for it will be caught by backtrack_memory dubbeling
        max_iterations = sys.maxsize-1 if self.__pair_repetition_brakepoinnt == sys.maxsize else len(students_list)
        mutable_students_list = deepcopy(students_list)
        backtrack_memory = {1: [], 0: []}
        while mutable_students_list != [] and i < max_iterations:
            student = mutable_students_list.pop()
            
            while True:
                res = change_request(whitelist_requirement=student, _future_layout=group_layout)
                if res is not None:
                    group_layout = res
                    added_members.append(student)
                    break
                
                member = added_members.pop(0)
                for group in group_layout:
                    if member in group_layout[group]:
                        group_layout[group][group_layout[group].index(member)] = -1
                        break
                mutable_students_list.insert(0, member)
                print(f"\nBacktracking {member}")
                    
                    
            if len(backtrack_memory[0]) == len(backtrack_memory[1]) == self.n_members:
                if backtrack_memory[0] == backtrack_memory[1]:
                    print("\nNo solution found")
                    break
                backtrack_memory[0] = []
                backtrack_memory[1] = []
            elif len(backtrack_memory[0]) < self.n_members:
                backtrack_memory[0].append(student)
            else:
                backtrack_memory[1].append(student)
            i += 1
            print(f"\nAdded {student} to group")


            
        # Add left over members to groups
        for student in mutable_students_list:
            # group[1] is the group members, group[0] is name of the group
            prefered_group_key = []
            for name in group_layout:
                group_layout[name] = list(filter(lambda x: x != -1, group_layout[name]))

                colisions = sum(map(lambda x: x not in self.__whitlist[student], group_layout[name]))
                to_long_punishment = 10 if len(group_layout[name]) >= self.__group_size else 0
                prefered_group_key.append((name, colisions, to_long_punishment))
            prefered_group_key = sorted(prefered_group_key, key=lambda x: x[1] + x[2])[0]
            if prefered_group_key[1] > 0 and self.__pair_repetition_brakepoinnt > this_iteration:
                self.__pair_repetition_brakepoinnt = this_iteration
            prefered_group = group_layout[prefered_group_key[0]]
            prefered_group.append(student)

        # Update the whitelist
        for group in group_layout:
            for member in group_layout[group]:
                self.__whitlist[member] = list(filter(lambda x: x not in group_layout[group], self.__whitlist[member]))
             
        # The whitlist was updated during the group creation
        self.groups[this_iteration] = group_layout
        print("\nDone")
        return self.groups
    
    def get_current_group(self, iteration: int = None, replace_alias: bool = True):
        """
        Gets the current group for the given iteration. If no iteration is given, the latest iteration is returned.
        If the iteration does not exist, an empty dictionary is returned.

        :param iteration: The iteration to get the group from. If None, the latest iteration is returned.
        :type iteration: int
        :param replace_alias: If True, the members are replaced with their aliases using :meth:`__replace_with_alias`.
        :type replace_alias: bool

        :return: The current group for the given iteration.
        :rtype: dict[str, list[str]]
        """
        if self.groups == {}:
            return {}
        try:       
            group = self.groups[max(self.groups.keys()) if iteration is None else iteration]
            return self.__replace_with_alias(group) if replace_alias else group
        except KeyError:
            return {}
    
    def get_all_groups(self, replace_alias: bool = True):
        """
        Gets all groups for all iterations.

        :param replace_alias: If True, the members are replaced with their aliases using :meth:`__replace_with_alias`.
        :type replace_alias: bool

        :return: All groups for all iterations.
        :rtype: dict[int, dict[str, list[str]]]
        """
        ret_groups = self.groups.copy()
        if replace_alias:
            for iteration in ret_groups:
                ret_groups[iteration] = self.__replace_with_alias(iteration)
        return ret_groups

    def export_group_as_csv(self, iteration: int, path: str):
        """
        Exports the group for the given iteration to a CSV file.

        :param iteration: The iteration to export the group from.
        :type iteration: int
        :param path: The path to the CSV file to export the group to.
        :type path: str

        :return: None
        """

        groups = self.get_current_group(iteration, replace_alias=False)
        rows = []
        for group, members in groups.items():
            for member in members:
                rows.append([group, member, self.alias.get(member, "")])
        with open(path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Group", "Member", "Alias"])
            writer.writerows(rows)

    def reset_groups(self):
        """
        Resets the groups and internal state of the GroupCalculator object.
        Alias and user input is not reset.

        :return: None
        """
        self.groups = {}
        self.__whitlist = None
        self.__pair_repetition_brakepoinnt = sys.maxsize

    def visualize_groups(self):
        """
        Prints the groups in a human-readable format to the CLI.

        :return: None
        """
        for iteration, groups in self.groups.items():
            print(f"Iteration {iteration}")
            for group, members in groups.items():
                print(f"Group {group}: {list(map(lambda x: self.alias.get(x, x), members))}")
            print("\n")

    def read_csv_columns(self, path: str):
        """
        Reads the headers of a CSV file and returns them as a list.
        if the CSV file dose not have a header, the columns are named "Column n" where n is the column number.
        Also stores meta data about the CSV file in object memory.

        :param path: The header of the CSV file to read.
        :type path: list[str]
        """
        headers = []
        self.reset_groups()
        encoding = detect_encoding(path)
        with open(path, 'r', encoding=encoding) as csvfile:
            first_bytes = csvfile.read(1024)
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(first_bytes)
            header = sniffer.has_header(first_bytes.replace(dialect.delimiter, ","))
            csvfile.seek(0)
            next_row = next(csv.reader(csvfile, dialect=dialect))
            if header:
                headers = next_row
            else:
                headers = [f"Column {i}" for i in range(0, len(next_row))]
            self.__csv_meta = CsvMeta(dialect, header, headers, path, encoding)
        return list(headers)

    def select_from_csv_file(self, header_name: list[str]):
        """
        Sets the members of the group based on the max number of entrys in selected columns of the CSV file.
        Also sets the alias of the members based on the selected columns value.

        :param header_name: The name of the headers to select the members from.
        :type header_name: list[str]

        :raises ValueError: The given header name is not in the CSV file or no CSV file selected was selected.

        :return: None
        """
        header_name = list(filter(lambda x: x != "", header_name))
        if self.__csv_meta.path is None:
            raise ValueError("No CSV file selected.")   
        if any(map(lambda x: x not in self.__csv_meta.headers, header_name)):
            raise ValueError("The header name is not in the CSV file.")

        with open(self.__csv_meta.path, 'tr', encoding=self.__csv_meta.encoding, errors="replace") as csvfile:
            reader = csv.reader(csvfile, dialect=self.__csv_meta.dialect)
            if self.__csv_meta.header:
                next(reader)
            header_index = list(map(lambda x: self.__csv_meta.headers.index(x), header_name))

            row = []
            row_assambler = lambda row: [row[i] if len(row) > i else "" for i in header_index]
            if "Member" in self.__csv_meta.headers:
                # It most likly is a file that was exported from this program
                member_index = self.__csv_meta.headers.index("Member")
                member, row = zip(*[(row[member_index], row_assambler(row)) for row in reader])
                row = list(map(lambda x: x[1], sorted(zip(member, row), key=lambda x: x[0])))
            else:
                row = [row_assambler(row) for row in reader]
        row = list(map(lambda x: list(filter(lambda y: y != "", x)), row))
        self.alias = {i: ", ".join(row[i]) for i in range(0, len(row))}
        self.__n_members = len(row) # Else it would trigger an reset
        return 

    def can_repeat(self):
        """
        Tests how many iterations it takes to get a pair repetition in the groups.
        
        :return: The number of iterations it takes to get a pair repetition in the groups.
        :rtype: int
        """

        [mem_groups, mem_whitlist] = [self.groups, self.__whitlist]
        self.reset_groups()
        while test_uniqueness(self.create_groups())[1] <= 1:
            pass
        counter = max(self.groups.keys()) # Not +1 because the last iteration is the first invalid one
        self.groups = mem_groups
        self.__whitlist = mem_whitlist
        return counter

if __name__ == "__main__":
    calc = GroupCalculator(24,6)
    for i in range(0, 6):
        calc.create_groups()
    calc.visualize_groups()
    result = test_uniqueness(calc.get_all_groups(replace_alias=False))
    print(f"Min: {result[0]}, Max: {result[1]}, Avg: {result[2]}")


