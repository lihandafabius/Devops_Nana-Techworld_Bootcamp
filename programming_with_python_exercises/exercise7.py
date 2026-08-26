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
        self.list_of_professors_administering = no_of_professors

    def name_and_duration_of_lecture(self):
        print(f"name of lecture: {self.name}, duration: {self.duration}")

    def add_professors(self, professor):
        if professor not in self.list_of_professors_administering:
            self.list_of_professors_administering.append(professor)
        print(self.list_of_professors_administering)

linux_lecture = Lecture("Linux Lecture", 50, "120 hrs", ["Prof Ashiuya", "Professor Githuki", "Professor Omollo" ])
linux_lecture.name_and_duration_of_lecture()
linux_lecture.add_professors("Professor Tom")

class Person:

    def __init__(self, first_name, last_name, age):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age

    def print_name(self):
        print(self.first_name + " " + self.last_name)

# Class Inheritance

class Student(Person):

    def __init__(self, first_name, last_name, age, lectures):
        super().__init__(first_name, last_name, age)
        self.lectures = lectures

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
student1.print_name()
student1.list_lectures()
student1.add_new_lectures("jenkins")
student1.remove_lecture("jenkins")

class Professor(Person):
    def __init__(self, first_name, last_name, age, subjects):
        super().__init__(first_name, last_name, age)
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

professor1 = Professor("Bonniventure", "Ishiuya", 60, ["Python", "Cloud Computing", "C++", "Linux"])
professor1.print_name()
professor1.list_subjects()
professor1.add_new_subjects("Databases")
professor1.remove_subjects("c")


