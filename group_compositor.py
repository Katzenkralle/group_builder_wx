import random
from itertools import combinations
from dataclasses import dataclass
from utils import test_uniqueness
import pandas as pd
import re

@dataclass
class GroupCanidates:
    members: list[int]
    colisions: int


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
        self.__csv_path: str | None = None

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
                random.shuffle(self.__whitlist[student])

        # Compute canidates for the group
        candidates: dict[int, list[GroupCanidates]] = {groupleader: [] for groupleader in students_list}
        for leader in candidates:
            group_combs = combinations(self.__whitlist[leader], self.__group_size - 1)
            for group in group_combs:
                # Maby add groupleader to group
                colisions = 0
                for member in group:
                    colisions += sum(map(lambda x: member not in self.__whitlist[x], filter(lambda x: x != member, group)))
                candidates[leader].append(GroupCanidates(group, colisions))
            candidates[leader] = sorted(candidates[leader], key=lambda x: x.colisions)
            
        
        # Sort > Most matches first, least colisions first
        candidates_iter = sorted(candidates.items(), key=lambda item: len(item[1]))

        # Try Grouplayout
        n_groups = 0
        group_layout: dict[str, list[int]] = {key: [] for key in map(GroupCalculator.get_group_letter, range(self.__n_groups))}
        for leader, candidates in candidates_iter:
            if leader not in students_list:
                continue
            for candidate in candidates:
                if False in map(lambda x: x in students_list, candidate.members) \
                    or leader not in students_list:
                    continue
                
                group_name = GroupCalculator.get_group_letter(n_groups)
                group_layout[group_name] = [leader] + list(candidate.members)

                for member in group_layout[group_name]:
                    self.__whitlist[member] = list(filter(lambda x: x not in group_layout[group_name], self.__whitlist[member]))
                    students_list.remove(member)
                
                n_groups += 1
                break

        # Add left over students to groups
        for student in students_list:
            # group[1] is the group members, group[0] is name of the group
            prefered_group_key = []
            for name, constelation in group_layout.items():
                colisions = sum(map(lambda x: x not in self.__whitlist[student], constelation))
                if len(constelation) >= self.__group_size:
                    colisions += 10
                prefered_group_key.append((name, colisions))

            prefered_group = group_layout[sorted(prefered_group_key, key=lambda x: x[1])[0][0]]
            prefered_group.append(student)
            for member in prefered_group:
                self.__whitlist[member] = list(filter(lambda x: x not in prefered_group, self.__whitlist[member]))


        # The whitlist was updated during the group creation
        self.groups[self.get_iteration()+1] = group_layout
    
        return self.groups
    
    def get_current_group(self, iteration: int = None, replace_alias: bool = True):
        if self.groups == {}:
            return {}
        group = self.groups[max(self.groups.keys()) if iteration is None else iteration]
        return self.__replace_with_alias(group) if replace_alias else group
    
    def get_all_groups(self):
        ret_groups = self.groups.copy()
        for iteration, groups in ret_groups:
            ret_groups[iteration] = self.__replace_with_alias(groups)
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
                print(f"Group {group}: {map(lambda x: self.alias.get(x, x), members)}")
            print("\n")

    def read_csv_columns(self, path: str):
        self.__csv_path = path
        df = pd.read_csv(path, nrows=0)
        return list(df.columns)

    def select_from_csv_file(self, header_name: str):
        if self.__csv_path is None:
            raise ValueError("No CSV file selected.")
        df = pd.read_csv(self.__csv_path)
        if header_name not in df.columns:
            raise ValueError(f"Header '{header_name}' not found in CSV file.")
        if "Member" not in df.columns:
            row = df[header_name].tolist()
        else:
            # It most likly is a file that was exported from this program
            [member, row] = [df["Member"].tolist(), df[header_name].tolist()]
            row = list(map(lambda x: x[1], sorted(zip(member, row), key=lambda x: x[0])))
        self.alias = {i: row[i] for i in range(0, len(row)) if pd.notnull(row[i])}
        self.n_students = len(row)
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
    calc = GroupCalculator(9, 3)
    for i in range(0, 3):
        calc.create_groups()
    calc.visualize_groups()
    print(calc.can_repeat())

