import random
from itertools import combinations
from dataclasses import dataclass

@dataclass
class GroupCanidates:
    members: list[int]
    colisions: int


class InvalideGroupSize(Exception):
    pass



class GroupCalculator:
    def __init__(self, n_students: int, n_groups: int):
        if n_students <= n_groups:
            raise InvalideGroupSize("The number of students must be greater than the number of groups")
        self.__n_students: int = n_students
        self.__n_groups: int = n_groups
        self.__group_size: int = n_students // n_groups
        
        self.__whitlist: dict[int, set[int]] | None = None
        self.counter: int = 0
        self.groups: dict[int, dict[str, list[str]]] = {}

    @staticmethod
    def get_group_letter(group: int) -> str:
        res = "" 
        if group > 25:
            res += GroupCalculator.get_group_letter(group // 26)
        return f"{res}{chr(65 + group)}"



    # filter(GroupCalculator.compute_prefered_group_members(selected_student, blocklist, student_list), lambda x: x == student) = None

    def create_groups(self):
        student_list_generator = lambda: list(range(self.__n_students))
        students_list: list[int] = student_list_generator()
        iteration: int = max(self.groups.keys(), default=-1) + 1

        #random.shuffle(students_list)

        if self.__whitlist is None:
            self.__whitlist = {student: list(filter(lambda x: x != student, students_list)) for student in students_list}


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
            print("Backup")
            # group[1] is the group members, group[0] is name of the group
            prefered_group_key = []
            for name, constelation in group_layout.items():
                colisions = sum(map(lambda x: x not in self.__whitlist[student], constelation))
                if len(constelation) > self.__group_size:
                    colisions += 10
                prefered_group_key.append((name, colisions))

            prefered_group = group_layout[sorted(prefered_group_key, key=lambda x: x[1])[0][0]]
            prefered_group.append(student)
            for member in prefered_group:
                self.__whitlist[member] = list(filter(lambda x: x not in prefered_group, self.__whitlist[member]))


        # The whitlist was updated during the group creation

        self.groups[iteration] = group_layout
    
        self.counter += 1
        return self.groups
    
    def can_repeat(self):
        # Calculate the number of unique group combinations
        return self.__group_size

if __name__ == "__main__":
    calc = GroupCalculator(10, 3)
    for i in range(0, 3):
        calc.create_groups()
    print(calc.create_groups())

