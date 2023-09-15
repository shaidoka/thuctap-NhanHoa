class Sample():

    def __init__(self,name):
        self.name = name

x = Sample(name="Jose")
print(x.name)

class Student():
    planet = "Earth" # Class Object Attribute
    def __init__(self,name,gpa):
        self.name = name # Attribute
        self.gpa = gpa

stu1 = Student("Rose", 4.0)
stu2 = Student("Mimi", 3.5)
print(stu1)
print(stu1.planet)

print("-----------")

class Agent():
    origin = "USA"
    def __init__(self,name,height,weight) -> None:
        self.name = name
        self.height = height
        self.weight = weight

x = Agent('Rose', 150, 50)
print(x.name)
x.weight = 60
print(x.weight)

