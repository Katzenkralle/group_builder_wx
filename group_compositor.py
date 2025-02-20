import random
from itertools import combinations
from dataclasses import dataclass
from utils import test_uniqueness, detect_encoding
import csv
import time
from copy import deepcopy
import sys


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

class InvalideGroupSize(Exception):
    """
    Exception raised when the number of students is less than the number of groups.
    """
    pass



class GroupCalculator:
    def __init__(self, n_members: int|None = 0, n_groups: int | None = None, allow_setting_invalid_inputs: bool = False):
        self.__allow_setting_invalid_inputs = allow_setting_invalid_inputs
        if n_members != None and n_groups != None and n_members <= n_groups:
            raise InvalideGroupSize("The number of students must be greater than the number of groups")
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
        if self.__n_members is not None and self.__n_groups is not None and self.__n_groups > 0:
            self.__group_size = self.__n_members // self.__n_groups

    @property
    def pair_repetition_brakepoinnt(self):
        return self.__pair_repetition_brakepoinnt

    @property
    def n_members(self):
        return self.__n_members

    @n_members.setter
    def n_members(self, value: int):
        if not self.__allow_setting_invalid_inputs and value is not None and value <= 0:
            raise ValueError("The number of students must be greater than 0")
        self.reset_groups()
        self.__n_members = value
        self.__try_calc_group_size()

    @property
    def n_groups(self):
        return self.__n_groups
    
    @n_groups.setter
    def n_groups(self, value: int):
        if not self.__allow_setting_invalid_inputs and value is not None and value <= 0:
            raise ValueError("The number of groups must be greater than 0")
        self.reset_groups()
        self.__n_groups = value
        self.__try_calc_group_size()

    def get_iteration(self):
        return max(self.groups.keys(), default=-1) 

    def create_groups(self):
        start_time = time.time()
        if self.__n_members is None or self.__n_groups is None or self.__n_groups == 0 or self.__n_members == 0:
            raise ValueError("The number of students and groups must be set before creating groups")
        if self.__n_groups >= self.__n_members:
            raise InvalideGroupSize("The number of students must be greater than the number of groups")
        
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
        last_colision = []
        # Note the CR will never match none whitlist pairs
        def change_request(destination: str, whitelist_requirement: int, req_age: int, future_layout: dict[str, list[int]]) -> None | dict[str, list[int]]:
            #if len(blocking_members) == self.__group_size or (len(blocking_members) > 0 and req_age == MAX_AGE_CR):
            #    return None
          
            # Finde optimal destaination, the handover if required
            group_ranking = []
            for group in future_layout:
                # Lowest is best
                group_ranking.append([group, sum(map(lambda x: x!=-1 and (x not in self.__whitlist[whitelist_requirement]), future_layout[group]))])
            best_match = sorted(group_ranking, key=lambda x: x[1])[0]
            if best_match[0] != destination:
                #print(f"Handover from {destination} to {best_match}")
                for group in filter(lambda x: x != destination, best_match[0]):
                    response = change_request(group, whitelist_requirement, req_age+1, deepcopy(future_layout))
                    if response is not None:
                        return response
                    
                #return change_request(best_match, whitelist_requirement, req_age, future_layout)
               
            blocking_members = list(filter(lambda x: whitelist_requirement not in self.__whitlist.get(x, students_list), future_layout[destination]))

            if list(filter(lambda x: whitelist_requirement not in self.__whitlist.get(x, students_list), virtual_members.get(destination, []))) != []:
                # The group is blocked by a member that is to be added to the group
                return None
            
            if -1 not in future_layout[destination] and blocking_members == []:
                to_append = list(filter(lambda x: x != -2, future_layout[destination]))
                if len(to_append) == 0:
                    #print(f"To many blocking members while trying to fit {whitelist_requirement} in {destination}")
                    return None
                # Happens when destination is full and no collision is present
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
                    last_colision.insert(0, blocker)
                    return None
                future_layout[destination][change_at_index] = -1

                
            future_layout[destination][future_layout[destination].index(-1)] = whitelist_requirement
            #print(f"Added {whitelist_requirement} to {destination}")
            return future_layout
            
        # Add the members to the groups
        added_members = []
        i = 0
        max_iterations = len(students_list)**2 if self.__pair_repetition_brakepoinnt == sys.maxsize else len(students_list)
        mutable_students_list = deepcopy(students_list)
        while mutable_students_list != [] and i < max_iterations:
            student = mutable_students_list.pop()
            # 2: Try fitting with CR
            # 3: Fill up rest with prioritys
        
            res = change_request("A", whitelist_requirement=student, req_age=0, future_layout=deepcopy(group_layout))
            if res is not None:
                group_layout = res
                added_members.append(student)
                
            else:
                # backtracking
                last_added = []
                if  added_members != []:
                    last_added.append(added_members.pop(0))
                    for group in group_layout:
                        group_layout[group] = list(map(lambda x: -1 if x == last_added[0] else x, group_layout[group]))
                for group in group_layout:
                    if -1 not in group_layout[group]:
                        group_layout[group] = sorted(group_layout[group], key=lambda x: len(self.__whitlist[x]), reverse=True)
                        last_added.append(group_layout[group].pop(0))
                        added_members.pop(added_members.index(last_added[-1]))
                        group_layout[group].append(-1)
                        
                mutable_students_list = last_added + mutable_students_list + [student]
                last_colision = []
                i += 1

                    
            
            
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
                print({"Iteration": this_iteration, "Student": student, "Group": prefered_group_key[0], "Colisions": prefered_group_key[1], "To long punishment": prefered_group_key[2]})
            prefered_group = group_layout[prefered_group_key[0]]
            prefered_group.append(student)

        # Update the whitelist
        for group in group_layout:
            for member in group_layout[group]:
                self.__whitlist[member] = list(filter(lambda x: x not in group_layout[group], self.__whitlist[member]))
             
        # The whitlist was updated during the group creation
        self.groups[this_iteration] = group_layout
    
        return self.groups
    
    def get_current_group(self, iteration: int = None, replace_alias: bool = True):
        if self.groups == {}:
            return {}
        try:       
            group = self.groups[max(self.groups.keys()) if iteration is None else iteration]
            return self.__replace_with_alias(group) if replace_alias else group
        except KeyError:
            return {}
    
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
        with open(path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Group", "Member", "Alias"])
            writer.writerows(rows)

    def reset_groups(self):
        self.groups = {}
        self.__whitlist = None
        self.__pair_repetition_brakepoinnt = sys.maxsize

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
        # ToDO: remove byte order mark if at start of file
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


