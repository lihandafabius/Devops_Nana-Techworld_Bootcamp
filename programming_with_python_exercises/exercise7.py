class Student:
    def __init__(self, first_name, last_name, age, lectures):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.lectures = lectures

    def print_full_name(self):
        full_name = self.first_name + " " + self.last_name
        print(full_name)

    def list_lectures(self):
        for lecture in self.lectures:
            print(lecture)

    def add_new_lectures(self, lecture):
        if lecture not in self.lectures:
            self.lectures.append(lecture)
        print(self.lectures)

    def remove_lecture(self, lecture):
        if lecture in self.lectures:
            self.lectures.remove(lecture)
            print(self.lectures)
        else:
            print(f"{lecture} is not in lectures learned")

student1 = Student("Fabius", "Lihanda", 20, ["Python", "linux", "docker", "kubernetes"])
student1.print_full_name()
student1.list_lectures()
student1.add_new_lectures("jenkins")
student1.remove_lecture("jenkins")

class Professor:
    def __init__(self, first_name, last_name, age, subjects):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.subjects = subjects

    def print_full_name(self):
        full_name = self.first_name + " " + self.last_name
        print(full_name)

    def list_subjects(self):
        for subject in self.subjects:
            print(subject)

    def add_new_subjects(self, subject):
        if subject not in self.subjects:
            self.subjects.append(subject)
        print(self.subjects)

    def remove_subjects(self, subject):
        if subject in self.subjects:
            self.subjects.remove(subject)
            print(self.subjects)
        else:
            print(f"{subject} is not in subjects taught")

professor1= Professor("Bonniventure", "Ishiuya", 60, ["Python", "Cloud Computing", "C++", "Linux"])
professor1.print_full_name()
professor1.list_subjects()
professor1.add_new_subjects("Databases")
professor1.remove_subjects("c")

class Lecture:

    def __init__(self, name, max_students, duration, no_of_professors):
        self.name = name
        self.max_students = max_students
        self.duration = duration
        self.no_of_professors = no_of_professors

    def