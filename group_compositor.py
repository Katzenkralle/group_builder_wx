import random
from itertools import combinations
from dataclasses import dataclass
from utils import test_uniqueness, detect_encoding
import pandas as pd
import csv
import time
from copy import deepcopy

@dataclass
class GroupCanidates:
    members: list[int]
    colisions: int

@dataclass
class CsvMeta:
    dialect: csv.Dialect
    header: bool
    headers: list[str]
    path: str

class InvalideGroupSize(Exception):
    pass



class GroupCalculator:
    def __init__(self, n_students: int|None = 0, n_groups: int | None = None):
        if n_students != None and n_groups != None and n_students <= n_groups:
            raise InvalideGroupSize("The number of students must be greater than the number of groups")
        self.__n_students: int|None = n_students
        self.__n_groups: int|None = n_groups

        self.__group_size: int|None = None
        self.__try_calc_group_size()

        self.__whitlist: dict[int, set[int]] | None = None
        self.__csv_meta = CsvMeta(None, False, [], None)

        self.groups: dict[int, dict[str, list[str]]] = {}
        self.alias = {}

    @staticmethod
    def get_group_letter(group: int) -> str:
        res = "" 
        if group > 25:
            res += GroupCalculator.get_group_letter(group // 26)
        return f"{res}{chr(65 + group)}"

    def __replace_with_alias(self, iteration):
        for _, members in iteration.items():
            for member in members:
                member = self.alias.get(member, member)
        return iteration
    
    def __try_calc_group_size(self):
        if self.__n_students is not None and self.__n_groups is not None:
            self.__group_size = self.__n_students // self.__n_groups

    @property
    def n_students(self):
        return self.__n_students

    @n_students.setter
    def n_students(self, value: int):
        if value is not None and value < 0:
            raise ValueError("The number of students must be greater than 0")
        self.reset_groups()
        self.__n_students = value
        self.__try_calc_group_size()

    @property
    def n_groups(self):
        return self.__n_groups
    
    @n_groups.setter
    def n_groups(self, value: int):
        if value is not None and value < 0:
            raise ValueError("The number of groups must be greater than 0")
        self.reset_groups()
        self.__n_groups = value
        self.__try_calc_group_size()

    def get_iteration(self):
        return max(self.groups.keys(), default=-1) 

    def create_groups(self):
        start_time = time.time()
        if self.__n_students is None or self.__n_groups is None:
            raise ValueError("The number of students and groups must be set before creating groups")
        if self.__n_groups >= self.__n_students:
            raise InvalideGroupSize("The number of students must be greater than the number of groups")
        
        students_list: list[int] = list(range(self.__n_students))
        random.shuffle(students_list)

        if self.__whitlist is None:
            self.__whitlist = {student: list(filter(lambda x: x != student, students_list)) for student in students_list}
        else:
            for student in self.__whitlist:
                self.__whitlist[student]

        # Assemble the groups
        g_rest = self.__n_students % self.__n_groups
        group_layout: dict[str, list[int]] = {key: [-1 for _ in range(self.__group_size)] for key in map(GroupCalculator.get_group_letter, range(self.__n_groups))}
        for i in range(0, g_rest):
            group_layout[GroupCalculator.get_group_letter(i)].append(-1)

        MAX_AGE_CR = 20
        virtual_members = {key: [] for key in group_layout} # Alternaativly pass blocked groups around (might be faster)
        # Note the CR will never match none whitlist pairs
        def change_request(destination: str, whitelist_requirement: int, req_age: int, future_layout: dict[str, list[int]]) -> None | dict[str, list[int]]:
            blocking_members = list(filter(lambda x: whitelist_requirement not in self.__whitlist.get(x, students_list), future_layout[destination]))
            if len(blocking_members) == self.__group_size or (len(blocking_members) > 0 and req_age == MAX_AGE_CR):
                return None
          
            if list(filter(lambda x: whitelist_requirement not in self.__whitlist.get(x, students_list), virtual_members.get(destination, []))) != []:
                # The group is already demanded by a member that is jet to be added
                return None
            
            if -1 not in future_layout[destination] and blocking_members == []:
                to_append = list(filter(lambda x: x != -2, future_layout[destination]))
                if len(to_append) == 0:
                    #print(f"To many blocking members while trying to fit {whitelist_requirement} in {destination}")
                    return None
                blocking_members.append(to_append[0])

            for blocker in blocking_members:
                if blocker not in future_layout[destination]:
                    #print(f"Blocker {blocker} not anymore in group {destination}, skipping")
                    continue
                change_at_index = future_layout[destination].index(blocker)
                future_layout[destination][change_at_index] = -2 # Mark as blocked/imovable

                virtual_members[destination].append(blocker)
                cr_success = False
                for group in filter(lambda x: x != destination, future_layout):
                    response = change_request(group, whitelist_requirement=blocker, req_age=req_age+1, future_layout=deepcopy(future_layout))
                    if response is not None:
                        future_layout = response
                        cr_success = True
                        break
                virtual_members[destination].remove(blocker)
                if not cr_success:
                    #print(f"Could not find a solution for blocker {blocker} while trying to fit {whitelist_requirement} in {destination}")
                    return None
                future_layout[destination][change_at_index] = -1

                
            future_layout[destination][future_layout[destination].index(-1)] = whitelist_requirement
            #print(f"Added {whitelist_requirement} to {destination}")
            return future_layout
            
        # Add the members to the groups
        added_members = []
        for student in students_list:
            # 1: Try fitting directly
            # 2: Try fitting with CR
            # 3: Fill up rest with prioritys
            for group in group_layout:
                if -1 not in group_layout[group]:
                    continue
                if list(filter(lambda x: student not in self.__whitlist.get(x, students_list), group_layout[group])) == []:
                    group_layout[group][group_layout[group].index(-1)] = student
                    added_members.append(student)
                    break
            else:
                for group in group_layout:
                    res = change_request(group, whitelist_requirement=student, req_age=10, future_layout=deepcopy(group_layout))
                    if res is not None:
                        group_layout = res
                        added_members.append(student)
                        break
            
        # Add left over members to groups
        for student in filter(lambda x: x not in added_members, students_list):
            print(f"Adding leftover member {student}")
            # group[1] is the group members, group[0] is name of the group
            prefered_group_key = []
            for name in group_layout:
                group_layout[name] = list(filter(lambda x: x != -1, group_layout[name]))

                colisions = sum(map(lambda x: x not in self.__whitlist[student], group_layout[name]))
                if len(group_layout[name]) >= self.__group_size:
                    colisions += 10
                prefered_group_key.append((name, colisions))

            prefered_group = group_layout[sorted(prefered_group_key, key=lambda x: x[1])[0][0]]
            prefered_group.append(student)

        # Update the whitelist
        for group in group_layout:
            for member in group_layout[group]:
                self.__whitlist[member] = list(filter(lambda x: x not in group_layout[group], self.__whitlist[member]))

        # The whitlist was updated during the group creation
        self.groups[self.get_iteration()+1] = group_layout
    
        return self.groups
    
    def get_current_group(self, iteration: int = None, replace_alias: bool = True):
        if self.groups == {}:
            return {}
        group = self.groups[max(self.groups.keys()) if iteration is None else iteration]
        return self.__replace_with_alias(group) if replace_alias else group
    
    def get_all_groups(self, replace_alias: bool = True):
        ret_groups = self.groups.copy()
        if replace_alias:
            for iteration in ret_groups:
                ret_groups[iteration] = self.__replace_with_alias(iteration)
        return ret_groups

    def export_group_as_csv(self, iteration: int, path: str):
        groups = self.get_current_group(iteration, replace_alias=False)
        rows = []
        for group, members in groups.items():
            for member in members:
                rows.append([group, member, self.alias.get(member, "")])
        df = pd.DataFrame(rows, columns=["Group", "Member", "Alias"])
        df.to_csv(path, index=False)

    def reset_groups(self):
        self.groups = {}
        self.__whitlist = None

    def visualize_groups(self):
        for iteration, groups in self.groups.items():
            print(f"Iteration {iteration}")
            for group, members in groups.items():
                print(f"Group {group}: {list(map(lambda x: self.alias.get(x, x), members))}")
            print("\n")

    def read_csv_columns(self, path: str):
        #list(df.keys())
        headers = []
        self.reset_groups()
        with open(path, 'r') as csvfile:
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
            self.__csv_meta = CsvMeta(dialect, header, headers, path)
        return list(headers)

    def select_from_csv_file(self, header_name: list[str]):
        header_name = list(filter(lambda x: x != "", header_name))
        if self.__csv_meta.path is None:
            raise ValueError("No CSV file selected.")   
        if any(map(lambda x: x not in self.__csv_meta.headers, header_name)):
            raise ValueError("The header name is not in the CSV file.")

        with open(self.__csv_meta.path, 'r') as csvfile:
            reader = csv.reader(csvfile, dialect=self.__csv_meta.dialect)
            if self.__csv_meta.header:
                next(reader)
            header_index = list(map(lambda x: self.__csv_meta.headers.index(x), header_name))

            row = []
            if "Member" in self.__csv_meta.headers:
                # It most likly is a file that was exported from this program
                member_index = self.__csv_meta.headers.index("Member")
                member, row = zip(*[(row[member_index], [row[i] for i in header_index]) for row in reader])
                row = list(map(lambda x: x[1], sorted(zip(member, row), key=lambda x: x[0])))
            else:
                row = [[row[i] for i in header_index] for row in reader]
        row = list(map(lambda x: list(filter(lambda y: y != "", x)), row))
        self.alias = {i: ", ".join(row[i]) for i in range(0, len(row))}
        self.__n_students = len(row) # Else it would trigger an reset
        return 

    def can_repeat(self):
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


