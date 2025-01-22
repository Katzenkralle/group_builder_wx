import random

class InvalideGroupSize(Exception):
    pass



class GroupCalculator:
    def __init__(self, n_students: int, n_groups: int):
        if n_students <= n_groups:
            raise InvalideGroupSize("The number of students must be greater than the number of groups")
        self.__n_students: int = n_students
        self.__n_groups: int = n_groups
        self.__group_size: int = n_students // n_groups
        
        self.groups: dict[int, dict[str, list[str]]] = {}

    def __compute_blocklist(self) -> dict[int, set[int]]: 
        blocklist = {student: set() for student in range(self.__n_students)}
        for iteration in self.groups.values():
            for group in iteration.values():
                for student in group:
                    if student == -1:
                        continue
                    blocklist[student] = set(list(blocklist[student]) + group)            
        return blocklist
    
    @staticmethod
    def get_group_letter(group: int) -> str:
        res = "" 
        if group > 25:
            res += GroupCalculator.get_group_letter(group // 26)
        return f"{res}{chr(65 + group)}"


    def compute_prefered_group_members(self, blocklist: dict[int, set[int]], students_list: list[int]) -> list[int]:
        groupleader = students_list[0]
        students_list.remove(groupleader)
        # Finds the best group members for the groupleader
        return [selected_student for selected_student in students_list
                if selected_student not in blocklist[groupleader] 
                and groupleader not in blocklist[selected_student]]
    

    # filter(GroupCalculator.compute_prefered_group_members(selected_student, blocklist, student_list), lambda x: x == student) = None

    def create_groups(self):
        student_list_generator = lambda: list(range(self.__n_students))

        iteration: int = 0 if self.groups == {} else sorted(self.groups.keys())[-1] + 1
        blocklist: dict[int, set[int]] = self.__compute_blocklist()
        students_list:  list[int] = student_list_generator()
        random.shuffle(students_list)

        self.groups[iteration] = {}

        for i in range(self.__n_groups):
            # Compute possible group members
            group_members = [students_list[0]] + self.compute_prefered_group_members( blocklist, students_list.copy())
            group_members = [ member for (i, member) in  enumerate(group_members) if i < self.__group_size]
            # Remove group members from student list
            students_list = [i for i in students_list if i not in group_members]
            # Select group members
            self.groups[iteration][GroupCalculator.get_group_letter(i)] = group_members

        # Fill up groups with remaining students, or dummy students
        for student in students_list:
            available_groups = [group for group in self.groups[iteration].values() if len(group) < self.__group_size]
            if available_groups == []:
                # If all groups have reached the median size, we still need to fill up the groups
                available_groups = [group for group in self.groups[iteration].values()]
            # We need the original student list to fill up
            optimal_members = self.compute_prefered_group_members(blocklist, student_list_generator())

            # Choose the group to add the student to
            # Negative modifier to discourage adding students to groups that are bigger than the median size
            available_groups.sort(key=lambda x: sum([1 for group in optimal_members if group in x ]
                                                    + [-1 if len(x) > self.__group_size else 0]))
            
            available_groups[0].append(student)

        for group in self.groups[iteration].values():
            while len(group) < self.__group_size:
                print(f"Group {iteration}{group} hat to be filled up with dummy")
                group.append(-1)

        return self.groups
    
    def can_repeat(self):
        # Calculate the number of unique group combinations
        return self.__group_size

if __name__ == "__main__":
    calc = GroupCalculator(10, 3)
    for i in range(0, 5):
        calc.create_groups()
    print(calc.create_groups())

