class Circle():
    pi = 3.14
    def __init__(self,radius=1) -> None:
        self.radius = radius
    
    def area(self):
        result = self.radius**2 * self.pi
        return result
    
    def perimeter(self):
        return 2*self.radius*Circle.pi

mycircle = Circle(20)
print(mycircle.radius)
print(mycircle.area())

class Person():

    def __init__(self, first_name, last_name) -> None:
        self.first_name = first_name
        self.last_name = last_name
    
    def hello(self):
        print("Hello!")
    
    def report(self):
        print(f"I am {self.first_name} {self.last_name}")

x = Person("John", "Smith")
x.report()

class Agent(Person):
    def __init__(self, first_name, last_name, code_name) -> None:
        super().__init__(first_name, last_name)
        self.code_name = code_name

    def report(self):
        print(f"I am {self.code_name}")

    def reveal(self,passcode):
        if passcode == 123:
            print("I am secret agent!")
        else:
            self.report()

x = Agent("Hehe", "Somit", "Mr.X")
x.hello()
x.reveal(1234)

print("---------------------\n")

class Book():
    def __init__(self,title,author,pages) -> None:
        self.title=title
        self.author = author
        self.pages = pages
    
    def __str__(self):
        return f"{self.title} written by {self.author}"
    
    def __len__(self):
        return self.pages

mybook = Book("Python Rocks!", "Rose", 120)
print(mybook)
print(len(mybook))