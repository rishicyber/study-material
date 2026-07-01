"""
================================================================================
  COMPLETE OOP CONCEPTS — INTERVIEW PREPARATION (5 YEARS EXPERIENCE LEVEL)
================================================================================
  Topics Covered:
  1.  Classes & Objects
  2.  __init__, __str__, __repr__ (Dunder/Magic Methods)
  3.  Instance vs Class vs Static Variables
  4.  Instance vs Class vs Static Methods
  5.  Encapsulation (Public, Protected, Private)
  6.  Properties (@property, getter, setter, deleter)
  7.  Inheritance (Single, Multiple, Multilevel, Hierarchical, Hybrid)
  8.  Method Resolution Order (MRO) — Diamond Problem
  9.  Polymorphism (Method Overriding, Duck Typing)
  10. Operator Overloading (Magic Methods)
  11. Abstraction (abc module)
  12. Interfaces in Python
  13. Composition vs Inheritance
  14. Aggregation vs Composition
  15. Mixins
  16. Descriptors
  17. Metaclasses
  18. Design Patterns (Singleton, Factory, Observer, Decorator, Strategy)
  19. SOLID Principles
  20. Dataclasses
  21. Slots
  22. __new__ vs __init__
  23. Deep Copy vs Shallow Copy in Objects
  24. Object Introspection

  Each section includes:
  - Full working code
  - Detailed inline comments
  - Cross-questions you'll likely face at interview

================================================================================
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 1: CLASSES & OBJECTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is a class? What is an object?
      A class is a blueprint/template. An object is an instance of that blueprint.
      Example: class Car → object = Car("Toyota", "Red")

  Q2. How is memory allocated for objects in Python?
      Python uses a heap memory model. __new__ allocates memory, __init__ initializes.

  Q3. What is self in Python?
      'self' refers to the current instance of the class. It is NOT a keyword;
      it's just a strong convention. You could name it anything (e.g., 'this'),
      but 'self' is universally used.

  Q4. Can you have a class without __init__?
      Yes. Python provides a default __init__ inherited from 'object'.
"""

class Car:
    """
    A simple Car class demonstrating class definition, attributes, and methods.
    All Python classes implicitly inherit from 'object' (Python 3).
    """

    # ── Class Variable (shared across ALL instances) ──────────────────────────
    total_cars_created = 0  # Tracks how many Car objects exist

    def __init__(self, brand: str, color: str, speed: int = 0):
        """
        Constructor / Initializer.
        Called automatically when you do: car = Car("BMW", "Black")

        Parameters:
            brand (str)  : Car brand name
            color (str)  : Car color
            speed (int)  : Initial speed, default is 0
        """
        # ── Instance Variables (unique to each object) ──────────────────────
        self.brand = brand        # Public attribute
        self.color = color        # Public attribute
        self.speed = speed        # Public attribute

        # Increment class variable every time an object is created
        Car.total_cars_created += 1

    def accelerate(self, amount: int):
        """Increases the speed of the car."""
        self.speed += amount
        print(f"{self.brand} accelerated! New speed: {self.speed} km/h")

    def brake(self, amount: int):
        """Decreases the speed, minimum 0."""
        self.speed = max(0, self.speed - amount)
        print(f"{self.brand} braked! New speed: {self.speed} km/h")

    def __str__(self):
        """
        Called when you print(object) or str(object).
        Meant for END USERS — should be readable and friendly.
        """
        return f"Car({self.brand}, {self.color}, {self.speed} km/h)"

    def __repr__(self):
        """
        Called in Python shell or repr(object).
        Meant for DEVELOPERS — should be unambiguous and ideally eval()-able.
        """
        return f"Car(brand='{self.brand}', color='{self.color}', speed={self.speed})"


# ── Demo ──────────────────────────────────────────────────────────────────────
car1 = Car("BMW", "Black")
car2 = Car("Toyota", "White", speed=60)

car1.accelerate(80)
car2.brake(20)

print(car1)              # Uses __str__
print(repr(car2))        # Uses __repr__
print(f"Total cars created: {Car.total_cars_created}")  # Class variable


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 2: INSTANCE vs CLASS vs STATIC VARIABLES AND METHODS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. Difference between @classmethod and @staticmethod?
      - @classmethod receives 'cls' (the class itself) as first arg.
        It can access/modify class state.
      - @staticmethod receives NO implicit first arg.
        It's just a regular function scoped inside the class for organization.

  Q2. When would you use a @classmethod?
      Factory methods — alternative constructors. E.g., Employee.from_string("John-30-Engineer")

  Q3. When would you use a @staticmethod?
      Utility functions that logically belong to a class but don't need
      access to instance or class data. E.g., Math.add(2, 3)

  Q4. What happens if you modify a class variable through an instance?
      Python creates a new INSTANCE variable that shadows the class variable.
      The class variable remains unchanged. This is a common gotcha!
"""

class Employee:
    """
    Demonstrates Instance, Class, and Static variables and methods.
    """

    # Class variable — shared among all instances
    company_name = "TechCorp"
    employee_count = 0

    def __init__(self, name: str, age: int, role: str):
        # Instance variables — unique per object
        self.name = name
        self.age = age
        self.role = role
        Employee.employee_count += 1  # Always modify class var via class name

    # ── Instance Method ───────────────────────────────────────────────────────
    # Has access to 'self' → can read/write instance AND class variables
    def get_info(self) -> str:
        return f"{self.name} ({self.role}) at {Employee.company_name}"

    # ── Class Method ─────────────────────────────────────────────────────────
    # Decorator: @classmethod
    # First arg is 'cls' (the class, not the instance)
    # USE CASE: Alternative constructors (factory methods)
    @classmethod
    def from_string(cls, emp_string: str):
        """
        Alternative constructor.
        Accepts a string like "John-30-Engineer" and creates an Employee.
        """
        name, age, role = emp_string.split("-")
        return cls(name, int(age), role)  # cls() calls Employee()

    @classmethod
    def get_company_info(cls) -> str:
        """Access class variable through cls."""
        return f"Company: {cls.company_name}, Employees: {cls.employee_count}"

    # ── Static Method ─────────────────────────────────────────────────────────
    # Decorator: @staticmethod
    # No 'self' or 'cls' — it's a plain function inside the class
    # USE CASE: Utility/helper functions related to the class topic
    @staticmethod
    def is_valid_age(age: int) -> bool:
        """Validates if age is within a legal working range."""
        return 18 <= age <= 65

    @staticmethod
    def calculate_bonus(salary: float, percentage: float) -> float:
        """Calculate bonus — doesn't need instance or class data."""
        return salary * (percentage / 100)


# ── Demo ──────────────────────────────────────────────────────────────────────
emp1 = Employee("Alice", 28, "Developer")
emp2 = Employee.from_string("Bob-32-Manager")  # Using classmethod as factory

print(emp1.get_info())
print(emp2.get_info())
print(Employee.get_company_info())
print(f"Is 17 valid age? {Employee.is_valid_age(17)}")
print(f"Bonus: ₹{Employee.calculate_bonus(100000, 15)}")

# Gotcha Demo: Instance variable shadowing class variable
emp1.company_name = "StartupX"  # Creates NEW instance variable for emp1 only!
print(f"emp1 company: {emp1.company_name}")     # StartupX (instance variable)
print(f"emp2 company: {emp2.company_name}")     # TechCorp (class variable)
print(f"Class company: {Employee.company_name}") # TechCorp (unchanged!)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 3: ENCAPSULATION — PUBLIC, PROTECTED, PRIVATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. How does Python implement private access control?
      Python uses NAME MANGLING for double-underscore (__) attributes.
      __attribute becomes _ClassName__attribute internally.
      It's NOT truly private — it's "convention-based" privacy.

  Q2. What is name mangling?
      When you write self.__salary, Python internally stores it as
      self._BankAccount__salary. This prevents accidental access from outside
      but doesn't make it impossible.

  Q3. What's the difference between _ and __ prefix?
      _name  → Protected: "I'm internal, please don't use this outside"
               Convention only, no enforcement.
      __name → Private: Name mangling applied, harder (not impossible) to access outside.

  Q4. Why does Python not have strict access modifiers like Java/C++?
      Python philosophy: "We are all consenting adults here."
      Trust developers with conventions rather than enforcing rules.
"""

class BankAccount:
    """
    Demonstrates Encapsulation:
    - Public attribute: account_holder
    - Protected attribute: _account_type (convention: don't access from outside)
    - Private attribute: __balance (name mangled, restricted access)
    """

    def __init__(self, holder: str, account_type: str, initial_balance: float):
        self.account_holder = holder           # Public — accessible anywhere
        self._account_type = account_type      # Protected — convention only
        self.__balance = initial_balance       # Private — name mangled to _BankAccount__balance
        self.__transaction_history = []        # Private list

    # ── Controlled access to private data via methods ─────────────────────────
    def deposit(self, amount: float):
        """Public method to deposit money — validates before modifying private state."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.__balance += amount
        self.__transaction_history.append(f"Deposited: +{amount}")
        print(f"Deposited ₹{amount}. New balance: ₹{self.__balance}")

    def withdraw(self, amount: float):
        """Public method to withdraw — prevents overdraft via encapsulation."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.__balance:
            raise ValueError("Insufficient balance.")
        self.__balance -= amount
        self.__transaction_history.append(f"Withdrawn: -{amount}")
        print(f"Withdrawn ₹{amount}. Remaining: ₹{self.__balance}")

    def get_balance(self) -> float:
        """Getter for private __balance — read-only access."""
        return self.__balance

    def get_statement(self):
        """Returns a copy of transaction history — protects internal list."""
        return list(self.__transaction_history)  # Return COPY, not reference


# ── Demo ──────────────────────────────────────────────────────────────────────
account = BankAccount("Alice", "Savings", 10000)
account.deposit(5000)
account.withdraw(3000)
print(f"Balance: ₹{account.get_balance()}")
print(f"Statement: {account.get_statement()}")

# Accessing protected (possible but discouraged by convention)
print(f"Account type: {account._account_type}")  # Works, but frowned upon

# Accessing private directly — this will FAIL:
# print(account.__balance)  # AttributeError!

# BUT name mangling allows access if you know the trick:
print(f"Via name mangling: ₹{account._BankAccount__balance}")  # Works! Not truly private


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 4: PROPERTIES — @property, getter, setter, deleter
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is the difference between a property and a regular method?
      A property is accessed like an attribute (no parentheses).
      It lets you add logic (validation, computation) while keeping
      the interface clean. obj.salary vs obj.get_salary()

  Q2. Why use @property instead of just making attribute public?
      Properties let you add validation/computation LATER without
      breaking the API. This follows the Open/Closed principle.

  Q3. What happens if you only define @property getter but no setter?
      The attribute becomes READ-ONLY. Attempting to set it raises AttributeError.

  Q4. What is a computed property?
      A property that calculates its value from other attributes dynamically.
      E.g., full_name = first_name + " " + last_name
"""

class Person:
    """
    Demonstrates Python @property decorator for getter, setter, and deleter.
    """

    def __init__(self, first_name: str, last_name: str, age: int):
        self.first_name = first_name    # Public
        self.last_name = last_name      # Public
        self._age = age                  # Protected (backing store for property)

    # ── Read-only computed property ───────────────────────────────────────────
    @property
    def full_name(self) -> str:
        """Computed property — dynamically combines first and last name."""
        return f"{self.first_name} {self.last_name}"

    # ── Property with getter ──────────────────────────────────────────────────
    @property
    def age(self) -> int:
        """Getter: access age like an attribute — person.age"""
        return self._age

    # ── Setter with validation ────────────────────────────────────────────────
    @age.setter
    def age(self, value: int):
        """
        Setter: person.age = 25
        Validates before allowing mutation.
        This is the KEY reason to use @property over public attributes!
        """
        if not isinstance(value, int):
            raise TypeError("Age must be an integer.")
        if value < 0 or value > 150:
            raise ValueError(f"Age {value} is out of valid range (0–150).")
        self._age = value

    # ── Deleter ──────────────────────────────────────────────────────────────
    @age.deleter
    def age(self):
        """Deleter: del person.age — optionally clean up."""
        print("Age attribute is being deleted!")
        del self._age

    def __str__(self):
        return f"Person({self.full_name}, age={self._age})"


# ── Demo ──────────────────────────────────────────────────────────────────────
p = Person("John", "Doe", 30)
print(p.full_name)   # Computed property — no ()
print(p.age)         # Getter

p.age = 31           # Setter with validation
print(p.age)

try:
    p.age = -5       # Triggers validation in setter
except ValueError as e:
    print(f"Error: {e}")

try:
    p.age = "thirty" # Type check fails
except TypeError as e:
    print(f"Error: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 5: INHERITANCE — SINGLE, MULTILEVEL, MULTIPLE, HIERARCHICAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is the difference between Inheritance and Composition?
      Inheritance = "IS-A" relationship. Dog IS-A Animal.
      Composition = "HAS-A" relationship. Car HAS-A Engine.
      Prefer composition over inheritance when possible (GoF principle).

  Q2. When do you use super()?
      To call a method from the parent class, especially __init__.
      super() is MRO-aware and handles multiple inheritance correctly.

  Q3. Can Python inherit from multiple classes?
      Yes. Python supports multiple inheritance.
      Python resolves method lookup using MRO (C3 Linearization algorithm).

  Q4. What is method overriding?
      When a child class provides its own implementation of a method
      already defined in the parent class. The child's version is called.

  Q5. What is the difference between overloading and overriding?
      Overloading: Same name, different parameters (Python doesn't natively
                   support it — use default args or *args).
      Overriding:  Child class redefines parent's method.
"""

# ── Single Inheritance ────────────────────────────────────────────────────────
class Animal:
    """Base class for all animals."""

    def __init__(self, name: str, sound: str):
        self.name = name
        self.sound = sound

    def speak(self):
        """Can be overridden by subclasses."""
        print(f"{self.name} says {self.sound}")

    def breathe(self):
        """All animals breathe — not typically overridden."""
        print(f"{self.name} is breathing...")

    def __str__(self):
        return f"Animal({self.name})"


class Dog(Animal):
    """
    Single Inheritance: Dog IS-A Animal.
    Dog inherits name, sound, speak(), breathe() from Animal.
    """

    def __init__(self, name: str, breed: str):
        # Call parent __init__ using super() to initialize name and sound
        super().__init__(name, sound="Woof")
        self.breed = breed   # Additional attribute specific to Dog

    def fetch(self, item: str):
        """Dog-specific method — Animal doesn't have this."""
        print(f"{self.name} fetched the {item}!")

    def speak(self):
        """
        Method Overriding: Dog provides its own speak().
        The parent Animal.speak() is overridden.
        """
        print(f"{self.name} ({self.breed}) barks: {self.sound} {self.sound}!")


# ── Multilevel Inheritance ────────────────────────────────────────────────────
class GuideDog(Dog):
    """
    Multilevel Inheritance: GuideDog → Dog → Animal
    GuideDog inherits from Dog which inherits from Animal.
    """

    def __init__(self, name: str, breed: str, owner: str):
        super().__init__(name, breed)  # Calls Dog.__init__
        self.owner = owner

    def guide(self):
        """Guide-dog-specific behavior."""
        print(f"{self.name} is guiding {self.owner} safely.")

    def speak(self):
        """
        Overrides Dog.speak(). Can also call parent's speak() with super().
        """
        super().speak()  # Calls Dog.speak()
        print(f"(quietly, since {self.name} is a trained guide dog)")


# ── Hierarchical Inheritance ──────────────────────────────────────────────────
class Cat(Animal):
    """Another subclass of Animal — Hierarchical inheritance."""

    def __init__(self, name: str, indoor: bool = True):
        super().__init__(name, sound="Meow")
        self.indoor = indoor

    def speak(self):
        print(f"{self.name} purrs: {self.sound}~")

    def purr(self):
        print(f"{self.name} is purring...🐱")


# ── Multiple Inheritance ──────────────────────────────────────────────────────
class SwimmingMixin:
    """Mixin class that adds swimming behavior."""
    def swim(self):
        print(f"{self.name} is swimming! 🏊")

class FlyingMixin:
    """Mixin class that adds flying behavior."""
    def fly(self):
        print(f"{self.name} is flying! 🦅")

class Duck(SwimmingMixin, FlyingMixin, Animal):
    """
    Multiple Inheritance: Duck IS-A Animal AND can Swim AND can Fly.
    Python uses MRO (C3 Linearization) to resolve method lookup order.
    """
    def __init__(self, name: str):
        super().__init__(name, sound="Quack")

    def speak(self):
        print(f"{self.name} quacks: {self.sound}!")


# ── Demo ──────────────────────────────────────────────────────────────────────
print("\n--- Single Inheritance ---")
dog = Dog("Rex", "Labrador")
dog.speak()       # Overridden
dog.breathe()     # Inherited from Animal
dog.fetch("ball") # Dog-specific

print("\n--- Multilevel Inheritance ---")
guide = GuideDog("Buddy", "Golden Retriever", "Mr. Smith")
guide.speak()   # GuideDog's speak → calls Dog's speak first
guide.guide()

print("\n--- Hierarchical Inheritance ---")
cat = Cat("Whiskers")
cat.speak()
cat.purr()

print("\n--- Multiple Inheritance ---")
duck = Duck("Donald")
duck.speak()
duck.swim()
duck.fly()

# Inspect Method Resolution Order
print(f"\nDuck MRO: {[cls.__name__ for cls in Duck.__mro__]}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 6: METHOD RESOLUTION ORDER (MRO) — DIAMOND PROBLEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is the Diamond Problem?
      When class D inherits from B and C, both of which inherit from A.
      Which version of A's method does D use?

           A
          / \
         B   C
          \ /
           D

  Q2. How does Python solve the Diamond Problem?
      Python uses C3 Linearization algorithm (also called C3 MRO).
      It creates a consistent linearization that respects the order
      in which classes are listed in the inheritance tuple.

  Q3. What does super() actually do in multiple inheritance?
      super() doesn't call the "parent" class — it calls the NEXT class
      in the MRO chain. This is why super() with multiple inheritance
      can be tricky but powerful.

  Q4. What is __mro__?
      A tuple that shows the Method Resolution Order for a class.
      Python walks this tuple left-to-right when resolving methods.
"""

class A:
    def greet(self):
        print("Hello from A")

class B(A):
    def greet(self):
        print("Hello from B")
        super().greet()  # Will call next in MRO, not necessarily A

class C(A):
    def greet(self):
        print("Hello from C")
        super().greet()  # Will call next in MRO

class D(B, C):
    """
    Diamond Problem Resolution:
    MRO of D: D → B → C → A → object
    When D.greet() calls super(), it follows this chain.
    """
    def greet(self):
        print("Hello from D")
        super().greet()  # Goes to B (next in MRO)


print("\n--- Diamond Problem / MRO Demo ---")
d = D()
d.greet()
# Output:
# Hello from D
# Hello from B
# Hello from C
# Hello from A

print(f"MRO of D: {[cls.__name__ for cls in D.__mro__]}")
# D → B → C → A → object


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 7: POLYMORPHISM — METHOD OVERRIDING & DUCK TYPING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is Polymorphism?
      "Many forms." The same interface (method name) behaves differently
      based on the object it's called on.

  Q2. What is Duck Typing?
      "If it walks like a duck and quacks like a duck, it's a duck."
      Python doesn't check TYPE — it checks if the object has the
      required METHOD. This enables polymorphism without inheritance.

  Q3. Difference between compile-time and runtime polymorphism?
      Compile-time (Static): Method Overloading — resolved at compile time.
                             Python doesn't have true overloading.
      Runtime (Dynamic):     Method Overriding — resolved at runtime based
                             on the actual object type.

  Q4. How does Python support method overloading?
      Python doesn't natively support it. Use:
      - Default arguments
      - *args / **kwargs
      - @singledispatch from functools
"""

# ── Runtime Polymorphism via Method Overriding ────────────────────────────────
class Shape:
    """Abstract-like base class for shapes."""

    def area(self) -> float:
        raise NotImplementedError("Subclasses must implement area()")

    def perimeter(self) -> float:
        raise NotImplementedError("Subclasses must implement perimeter()")

    def describe(self):
        """
        Polymorphic behavior: same method call, different outputs.
        The actual method invoked depends on the runtime type of 'self'.
        """
        print(f"Shape: {self.__class__.__name__}")
        print(f"  Area     : {self.area():.2f}")
        print(f"  Perimeter: {self.perimeter():.2f}")


import math

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Triangle(Shape):
    def __init__(self, a: float, b: float, c: float):
        self.a, self.b, self.c = a, b, c

    def area(self) -> float:
        s = (self.a + self.b + self.c) / 2  # Semi-perimeter
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    def perimeter(self) -> float:
        return self.a + self.b + self.c


# ── Polymorphic function — works with any Shape subclass ──────────────────────
def print_all_shapes(shapes: list):
    """
    Polymorphism in action:
    We don't care what TYPE each shape is — we just call the same methods.
    Python resolves which actual method to call at RUNTIME.
    """
    for shape in shapes:
        shape.describe()
        print()


shapes = [Circle(5), Rectangle(4, 6), Triangle(3, 4, 5)]
print("\n--- Polymorphism Demo ---")
print_all_shapes(shapes)


# ── Duck Typing ───────────────────────────────────────────────────────────────
class Robot:
    """Not an Animal — but has a speak() method."""
    name = "R2D2"
    def speak(self):
        print("Beep boop boop!")

class Parrot:
    """Not the same Animal class — but has a speak() method."""
    name = "Polly"
    def speak(self):
        print("Polly wants a cracker!")

def make_it_speak(thing):
    """
    Duck Typing: We don't check isinstance().
    We just call speak() and trust the object has it.
    Works for Dog, Robot, Parrot — any object with a speak() method!
    """
    thing.speak()

print("\n--- Duck Typing Demo ---")
make_it_speak(Dog("Rex", "Lab"))
make_it_speak(Robot())
make_it_speak(Parrot())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 8: OPERATOR OVERLOADING (MAGIC / DUNDER METHODS)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What are dunder methods / magic methods?
      Methods with double underscore prefix and suffix: __add__, __str__, etc.
      They allow objects to define behavior for built-in operations like +, -, *, ==, len().

  Q2. What is the difference between __eq__ and __hash__?
      __eq__: Defines == behavior.
      __hash__: Defines hash() behavior. If you override __eq__,
                Python sets __hash__ to None (making object unhashable)
                unless you also define __hash__.
      Rule: Objects that are equal must have the same hash.

  Q3. What does __len__ do?
      Called by len(obj). Should return an integer.

  Q4. When you do a + b, what Python method is called?
      a.__add__(b) is called first.
      If it returns NotImplemented, b.__radd__(a) is tried.

  Common Magic Methods:
  __init__, __str__, __repr__, __len__, __getitem__, __setitem__,
  __add__, __sub__, __mul__, __truediv__, __eq__, __lt__, __gt__,
  __contains__, __iter__, __next__, __call__, __enter__, __exit__
"""

class Vector:
    """
    2D Vector class demonstrating operator overloading.
    """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    # ── String representations ────────────────────────────────────────────────
    def __str__(self):
        return f"Vector({self.x}, {self.y})"

    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y})"

    # ── Arithmetic operators ──────────────────────────────────────────────────
    def __add__(self, other: "Vector") -> "Vector":
        """v1 + v2"""
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        """v1 - v2"""
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector":
        """v * scalar (e.g., v * 3)"""
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector":
        """scalar * v (e.g., 3 * v) — called when left operand doesn't support *"""
        return self.__mul__(scalar)

    def __neg__(self) -> "Vector":
        """-v (unary negation)"""
        return Vector(-self.x, -self.y)

    # ── Comparison operators ──────────────────────────────────────────────────
    def __eq__(self, other: "Vector") -> bool:
        """v1 == v2"""
        return self.x == other.x and self.y == other.y

    def __lt__(self, other: "Vector") -> bool:
        """v1 < v2 (compare magnitudes)"""
        return abs(self) < abs(other)

    def __abs__(self) -> float:
        """abs(v) — returns magnitude of vector"""
        return math.sqrt(self.x ** 2 + self.y ** 2)

    # ── Boolean ───────────────────────────────────────────────────────────────
    def __bool__(self) -> bool:
        """if v: → True if vector is non-zero"""
        return self.x != 0 or self.y != 0

    # ── Dot product as @  ─────────────────────────────────────────────────────
    def __matmul__(self, other: "Vector") -> float:
        """v1 @ v2 — dot product (Python 3.5+, @ operator)"""
        return self.x * other.x + self.y * other.y

    def __hash__(self):
        """
        Required if __eq__ is defined AND you want to use Vector in sets/dicts.
        Vectors that are equal must have same hash.
        """
        return hash((self.x, self.y))


# ── Demo ──────────────────────────────────────────────────────────────────────
print("\n--- Operator Overloading Demo ---")
v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(f"v1 = {v1}")
print(f"v2 = {v2}")
print(f"v1 + v2 = {v1 + v2}")
print(f"v1 - v2 = {v1 - v2}")
print(f"v1 * 3  = {v1 * 3}")
print(f"3 * v1  = {3 * v1}")    # Uses __rmul__
print(f"-v1     = {-v1}")
print(f"|v1|    = {abs(v1)}")   # Magnitude = 5.0 for (3,4)
print(f"v1 == v2: {v1 == v2}")
print(f"v1 < v2 (by magnitude): {v1 < v2}")
print(f"v1 @ v2 (dot product): {v1 @ v2}")  # 3*1 + 4*2 = 11
print(f"bool(v1): {bool(v1)}")
print(f"bool(Vector(0,0)): {bool(Vector(0, 0))}")


# ── Callable Objects with __call__ ────────────────────────────────────────────
class Multiplier:
    """
    __call__ makes an object callable like a function.
    USE CASE: Stateful functions, closures, function objects.
    """

    def __init__(self, factor: int):
        self.factor = factor

    def __call__(self, value: int) -> int:
        """obj(value) — called when object used like a function."""
        return value * self.factor


double = Multiplier(2)
triple = Multiplier(3)
print(f"\ndouble(5) = {double(5)}")   # __call__ invoked
print(f"triple(5) = {triple(5)}")


# ── Context Manager with __enter__ and __exit__ ───────────────────────────────
"""
CROSS-QUESTIONS:
  Q5. How do you make an object a context manager?
      Implement __enter__ and __exit__ methods.
      __enter__: called when entering 'with' block, returns resource.
      __exit__: called when leaving 'with' block (even on exception).
                Parameters: exc_type, exc_val, exc_tb
                Return True to suppress exceptions.
"""

class FileManager:
    """Custom context manager for file operations."""

    def __init__(self, filename: str, mode: str):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        """Called on 'with' block entry. Opens the file and returns it."""
        print(f"Opening {self.filename}...")
        self.file = open(self.filename, self.mode)
        return self.file  # This is bound to 'as' variable

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Called when 'with' block exits (normally or via exception).
        exc_type, exc_value, traceback: Exception info (None if no exception).
        Return True to SUPPRESS the exception. Return False/None to PROPAGATE it.
        """
        print(f"Closing {self.filename}...")
        if self.file:
            self.file.close()
        if exc_type:
            print(f"An exception occurred: {exc_type.__name__}: {exc_value}")
        return False  # Don't suppress exceptions


# Demo (creates a temp file)
import os
with FileManager("/tmp/test_oop.txt", "w") as f:
    f.write("OOP is powerful!\n")
os.remove("/tmp/test_oop.txt")  # Cleanup


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 9: ABSTRACTION — abc MODULE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is abstraction?
      Hiding implementation details and exposing only the essential interface.
      Users know WHAT an object does, not HOW it does it.

  Q2. How do you create an abstract class in Python?
      Import ABC from abc module. Inherit from ABC.
      Decorate methods with @abstractmethod.
      Python will PREVENT instantiation of the class directly.

  Q3. Can an abstract class have concrete methods?
      YES! Abstract classes can have:
      - Abstract methods (must be overridden)
      - Concrete methods (can be inherited as-is)
      - Class/static methods (can also be abstract)

  Q4. What is the difference between an abstract class and an interface?
      Abstract class: Can have state (attributes), concrete methods, constructors.
      Interface (Java): Only abstract methods, no state (Python doesn't have interfaces).
      In Python, we simulate interfaces with pure abstract classes (all @abstractmethod).

  Q5. Can you instantiate an abstract class?
      NO. Raises TypeError: "Can't instantiate abstract class X with abstract methods Y"
"""

from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    """
    Abstract Base Class for all payment gateways.
    Acts as an interface/contract that all subclasses MUST fulfill.
    """

    def __init__(self, merchant_id: str):
        self.merchant_id = merchant_id  # Concrete state in abstract class
        self._transaction_log = []

    @abstractmethod
    def process_payment(self, amount: float, card_number: str) -> bool:
        """
        MUST be implemented by every concrete subclass.
        Raises TypeError if subclass doesn't implement this.
        """
        pass

    @abstractmethod
    def refund(self, transaction_id: str) -> bool:
        """MUST be implemented by subclasses."""
        pass

    # ── Concrete method in abstract class ────────────────────────────────────
    def log_transaction(self, transaction_id: str, amount: float, status: str):
        """Concrete method — available to all subclasses."""
        entry = {"id": transaction_id, "amount": amount, "status": status}
        self._transaction_log.append(entry)
        print(f"Transaction logged: {entry}")

    def get_logs(self) -> list:
        return self._transaction_log

    @classmethod
    def get_gateway_name(cls) -> str:
        """Can also be overridden."""
        return cls.__name__


class StripeGateway(PaymentGateway):
    """Concrete implementation of PaymentGateway for Stripe."""

    def process_payment(self, amount: float, card_number: str) -> bool:
        print(f"[Stripe] Processing ₹{amount} for card ending {card_number[-4:]}")
        # Simulate Stripe API call...
        success = True  # Assume success
        txn_id = f"STRIPE_{id(self)}"
        self.log_transaction(txn_id, amount, "SUCCESS" if success else "FAILED")
        return success

    def refund(self, transaction_id: str) -> bool:
        print(f"[Stripe] Refunding transaction {transaction_id}")
        return True


class PayPalGateway(PaymentGateway):
    """Concrete implementation of PaymentGateway for PayPal."""

    def process_payment(self, amount: float, card_number: str) -> bool:
        print(f"[PayPal] Processing ₹{amount} via PayPal...")
        txn_id = f"PAYPAL_{id(self)}"
        self.log_transaction(txn_id, amount, "SUCCESS")
        return True

    def refund(self, transaction_id: str) -> bool:
        print(f"[PayPal] Refunding {transaction_id} via PayPal")
        return True


# ── Demo ──────────────────────────────────────────────────────────────────────
print("\n--- Abstraction Demo ---")

# Cannot instantiate abstract class:
try:
    gateway = PaymentGateway("MERCHANT_001")  # TypeError!
except TypeError as e:
    print(f"Error: {e}")

stripe = StripeGateway("MERCHANT_001")
paypal = PayPalGateway("MERCHANT_002")

stripe.process_payment(5000.0, "4111111111111234")
paypal.process_payment(2500.0, "5500000000000004")

# Polymorphic usage through abstract base class
gateways = [stripe, paypal]
for gw in gateways:
    print(f"{gw.get_gateway_name()} logs: {gw.get_logs()}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 10: COMPOSITION vs INHERITANCE & AGGREGATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. Composition vs Inheritance — when to prefer which?
      Inheritance: "IS-A" relationship. Dog IS-A Animal. ✓
      Composition: "HAS-A" relationship. Car HAS-A Engine. ✓
      Rule: Prefer Composition over Inheritance (GoF principle).
      Why? Inheritance creates tight coupling. Composition is more flexible.

  Q2. What is Aggregation vs Composition?
      Both are "HAS-A" relationships, but differ in LIFETIME:
      Aggregation: The contained object can exist INDEPENDENTLY.
                   E.g., University HAS departments, but departments
                   can exist without the university.
      Composition: The contained object CANNOT exist independently.
                   E.g., House HAS rooms, but rooms cannot exist
                   without the house (they're destroyed together).

  Q3. What is Favor Composition Over Inheritance (FCOI)?
      A design principle saying you should use composition to achieve
      code reuse rather than inheritance, because:
      - It avoids the fragile base class problem
      - More flexible (can change components at runtime)
      - Avoids deep inheritance hierarchies
"""

# ── Composition Example ───────────────────────────────────────────────────────
class Engine:
    """Engine is a component — part of a Car (Composition)."""

    def __init__(self, horsepower: int, fuel_type: str):
        self.horsepower = horsepower
        self.fuel_type = fuel_type
        self._running = False

    def start(self):
        self._running = True
        print(f"Engine ({self.fuel_type}, {self.horsepower}hp) started!")

    def stop(self):
        self._running = False
        print("Engine stopped.")

    @property
    def is_running(self):
        return self._running

    def __str__(self):
        return f"Engine({self.fuel_type}, {self.horsepower}hp)"


class GPS:
    """GPS is a component — part of a Car."""

    def __init__(self, brand: str):
        self.brand = brand

    def navigate(self, destination: str):
        print(f"[GPS:{self.brand}] Navigating to: {destination}")


class ElectricBattery:
    """Battery component."""

    def __init__(self, capacity_kwh: float):
        self.capacity_kwh = capacity_kwh
        self.charge_level = 100.0

    def discharge(self, amount: float):
        self.charge_level = max(0, self.charge_level - amount)
        print(f"Battery at {self.charge_level:.1f}%")


class ModernCar:
    """
    Composition: ModernCar HAS-A Engine, HAS-A GPS.
    The Engine and GPS are CREATED inside the car — they don't exist without it.
    This is stronger than Aggregation.
    """

    def __init__(self, brand: str, hp: int, fuel: str, gps_brand: str):
        self.brand = brand
        # Composition: Engine is created by the Car and lives with the Car
        self._engine = Engine(hp, fuel)
        self._gps = GPS(gps_brand)

    def start(self):
        print(f"{self.brand} starting...")
        self._engine.start()

    def navigate_to(self, destination: str):
        if self._engine.is_running:
            self._gps.navigate(destination)
        else:
            print("Start the car first!")

    def stop(self):
        self._engine.stop()


# ── Aggregation Example ───────────────────────────────────────────────────────
class Professor:
    """A Professor can exist independently of any department."""

    def __init__(self, name: str, subject: str):
        self.name = name
        self.subject = subject

    def teach(self):
        print(f"Prof. {self.name} is teaching {self.subject}")


class Department:
    """
    Aggregation: Department HAS Professors, but professors exist independently.
    If the department is closed, professors still exist.
    """

    def __init__(self, name: str):
        self.name = name
        self._professors: list[Professor] = []  # Aggregated objects

    def add_professor(self, prof: Professor):
        """Professor is passed in (not created here) — Aggregation."""
        self._professors.append(prof)

    def conduct_classes(self):
        for prof in self._professors:
            prof.teach()


# ── Demo ──────────────────────────────────────────────────────────────────────
print("\n--- Composition Demo ---")
car = ModernCar("Tesla Model S", 670, "Electric", "Garmin")
car.start()
car.navigate_to("Mumbai")
car.stop()

print("\n--- Aggregation Demo ---")
prof1 = Professor("Dr. Smith", "Python")  # Exists independently
prof2 = Professor("Dr. Jones", "OOP")

dept = Department("Computer Science")
dept.add_professor(prof1)  # Professors are aggregated
dept.add_professor(prof2)
dept.conduct_classes()

# Even if dept is deleted, professors still exist
del dept
prof1.teach()  # Still works!


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 11: MIXINS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is a Mixin?
      A class that provides methods to other classes via inheritance
      but is NOT meant to be instantiated on its own.
      It adds a specific "capability" or "behavior" to a class.

  Q2. Why use Mixins instead of regular inheritance?
      Mixins allow HORIZONTAL composition of behaviors.
      They avoid deep inheritance hierarchies.
      A class can mix in multiple behaviors independently.

  Q3. How do you name a Mixin class by convention?
      Convention: End the class name with "Mixin" (e.g., SerializableMixin, LoggingMixin).

  Q4. What's the difference between a Mixin and a regular base class?
      A Mixin:
      - Has no (or minimal) __init__
      - Has no state of its own (usually)
      - Provides reusable behavior meant to be "mixed in"
      - NOT designed to be instantiated alone
"""

import json
from datetime import datetime

class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamp tracking."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def touch(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now().isoformat()
        print(f"Updated at: {self.updated_at}")


class SerializableMixin:
    """Mixin that adds JSON serialization capability."""

    def to_json(self) -> str:
        """Serialize all public attributes to JSON."""
        data = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str: str):
        """Create instance from JSON string."""
        data = json.loads(json_str)
        # Assumes all keys in JSON are constructor parameters
        return cls(**data)


class ValidateMixin:
    """Mixin that adds a validation hook."""

    def validate(self) -> bool:
        """Override in subclass to add validation logic."""
        return True

    def save(self):
        if self.validate():
            print(f"{self.__class__.__name__} saved successfully.")
        else:
            raise ValueError(f"{self.__class__.__name__} validation failed.")


class User(TimestampMixin, SerializableMixin, ValidateMixin):
    """
    User class that MIXES IN:
    - Timestamp tracking
    - JSON serialization
    - Validation + save
    """

    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
        super().__init__()  # Calls TimestampMixin.__init__ via MRO

    def validate(self) -> bool:
        """Override ValidateMixin.validate() with User-specific rules."""
        return "@" in self.email and len(self.username) >= 3


# ── Demo ──────────────────────────────────────────────────────────────────────
print("\n--- Mixins Demo ---")
user = User("alice", "alice@example.com")
print(user.to_json())
user.save()

invalid_user = User("ab", "not-an-email")
try:
    invalid_user.save()  # Validation fails
except ValueError as e:
    print(f"Error: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 12: DESCRIPTORS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is a descriptor in Python?
      A descriptor is any object that defines __get__, __set__, or __delete__.
      They are the mechanism behind properties, class methods, static methods.

  Q2. What are the types of descriptors?
      Data descriptor:     Defines __get__ AND __set__ (or __delete__)
                           Takes priority over instance __dict__.
      Non-data descriptor: Only defines __get__.
                           Instance __dict__ takes priority.

  Q3. What is the difference between @property and a descriptor?
      @property is a convenience wrapper around the descriptor protocol.
      Descriptors are more powerful — they can be REUSED across multiple classes.

  Q4. When would you use a custom descriptor vs @property?
      Use @property for class-specific validation on one or two attributes.
      Use descriptors when you need the SAME validation logic in MULTIPLE classes.
      E.g., a "PositiveNumber" descriptor reused in Circle, Rectangle, Triangle.
"""

class PositiveNumber:
    """
    Reusable descriptor that enforces any numeric attribute to be positive.
    Can be used in multiple classes without repeating validation logic.
    """

    def __set_name__(self, owner, name):
        """
        Called automatically when descriptor is assigned to a class attribute.
        'owner' = the class, 'name' = the attribute name.
        We store the name so we know what to put in instance's __dict__.
        """
        self.name = name
        self.private_name = f"_{name}"  # Store value in _radius, _width, etc.

    def __get__(self, obj, objtype=None):
        """Called when attribute is READ: obj.radius"""
        if obj is None:
            return self  # Accessed from class, not instance
        return getattr(obj, self.private_name, 0)

    def __set__(self, obj, value):
        """Called when attribute is WRITTEN: obj.radius = 5"""
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be a number, got {type(value).__name__}")
        if value <= 0:
            raise ValueError(f"{self.name} must be positive, got {value}")
        setattr(obj, self.private_name, value)  # Store in _radius etc.

    def __delete__(self, obj):
        """Called when del obj.radius"""
        print(f"Deleting {self.name}")
        delattr(obj, self.private_name)


class Circle2:
    """Uses PositiveNumber descriptor for radius validation."""
    radius = PositiveNumber()  # Descriptor instance at CLASS level

    def __init__(self, radius: float):
        self.radius = radius  # Triggers PositiveNumber.__set__

    def area(self):
        return math.pi * self.radius ** 2


class Rectangle2:
    """Reuses the SAME PositiveNumber descriptor for both width and height."""
    width = PositiveNumber()
    height = PositiveNumber()

    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


# ── Demo ──────────────────────────────────────────────────────────────────────
print("\n--- Descriptors Demo ---")
c = Circle2(5)
print(f"Circle area: {c.area():.2f}")

try:
    c.radius = -3  # Triggers descriptor __set__ validation
except ValueError as e:
    print(f"Error: {e}")

r = Rectangle2(4, 6)
print(f"Rectangle area: {r.area()}")

try:
    r.width = "ten"  # Type check in descriptor
except TypeError as e:
    print(f"Error: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 13: METACLASSES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is a metaclass?
      A metaclass is the "class of a class."
      Just as objects are instances of classes, CLASSES are instances of metaclasses.
      In Python, the default metaclass is 'type'.
      type(int) → <class 'type'>
      type(str) → <class 'type'>

  Q2. When would you use a metaclass?
      - Enforcing class-level constraints (e.g., all methods must be documented)
      - Auto-registering subclasses (plugin systems)
      - ORMs like Django use metaclasses (Model metaclass registers fields)
      - Singleton pattern enforcement at the metaclass level

  Q3. How do you create a metaclass?
      Define a class that inherits from 'type'.
      Override __new__ and/or __init__.

  Q4. What's the difference between __new__ and __init__ in metaclasses?
      __new__: Creates the class object (like allocating memory for a class).
      __init__: Initializes the class object after it's been created.

  Q5. What does "type" do?
      type(name, bases, dict) creates a new class dynamically.
      It's the ultimate metaclass — mother of all classes in Python.
"""

class SingletonMeta(type):
    """
    Metaclass implementation of the Singleton pattern.
    Ensures only ONE instance of any class using this metaclass can exist.
    """
    _instances = {}  # Registry: class → its single instance

    def __call__(cls, *args, **kwargs):
        """
        Called whenever you do: MyClass(*args).
        We intercept this and return the existing instance if it exists.
        """
        if cls not in cls._instances:
            # First time: create the instance normally
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]  # Always return THE same instance


class DatabaseConnection(metaclass=SingletonMeta):
    """
    Uses SingletonMeta metaclass.
    No matter how many times you call DatabaseConnection(), you get the SAME object.
    """

    def __init__(self, host: str, port: int):
        # With Singleton, __init__ may be called on existing object
        # Use hasattr check to avoid re-initialization
        if not hasattr(self, "_initialized"):
            self.host = host
            self.port = port
            self._connected = False
            self._initialized = True
            print(f"DatabaseConnection created: {host}:{port}")

    def connect(self):
        self._connected = True
        print(f"Connected to {self.host}:{self.port}")

    def __repr__(self):
        return f"DatabaseConnection({self.host}:{self.port}, connected={self._connected})"


class EnforcingMeta(type):
    """
    Metaclass that enforces all methods have docstrings.
    Raises TypeError during class creation if any method is missing a docstring.
    """

    def __new__(mcs, name, bases, namespace):
        """
        Called when Python creates a new class that uses this metaclass.
        We inspect the methods and enforce docstring presence.
        """
        for attr_name, attr_value in namespace.items():
            if callable(attr_value) and not attr_name.startswith("__"):
                if not attr_value.__doc__:
                    raise TypeError(
                        f"Method '{attr_name}' in class '{name}' "
                        f"must have a docstring!"
                    )
        return super().__new__(mcs, name, bases, namespace)


# ── Demo ──────────────────────────────────────────────────────────────────────
print("\n--- Metaclass / Singleton Demo ---")

db1 = DatabaseConnection("localhost", 5432)
db2 = DatabaseConnection("remote-server", 3306)  # Same object! host won't change

print(f"db1 is db2: {db1 is db2}")  # True — same object!
print(f"db1: {db1}")

db1.connect()
print(f"db2 connected: {db2._connected}")  # True — same object!

print("\n--- EnforcingMeta Demo ---")
try:
    class BadService(metaclass=EnforcingMeta):
        def process(self):  # No docstring!
            pass
except TypeError as e:
    print(f"Error: {e}")

class GoodService(metaclass=EnforcingMeta):
    def process(self):
        """Processes the request."""
        return "processed"

print("GoodService created successfully!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 14: __new__ vs __init__ & OBJECT CREATION LIFECYCLE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is the difference between __new__ and __init__?
      __new__:  Creates (allocates memory for) the instance. Returns the new object.
                Called BEFORE __init__. Receives 'cls' (the class).
      __init__: Initializes the already-created instance. Returns None.
                Called AFTER __new__. Receives 'self' (the new object).

  Q2. When would you override __new__?
      - Implementing Singleton pattern
      - Controlling object creation (e.g., returning a cached instance)
      - Creating immutable types (int, str are immutable, so you need __new__)
      - Factory patterns

  Q3. What happens if __new__ returns something that's not an instance of cls?
      __init__ is NOT called. Python only calls __init__ if __new__ returns
      an instance of the class.

  Q4. How does Python create an object step by step?
      1. MyClass(*args) is called
      2. MyClass.__new__(MyClass, *args) creates the object
      3. If result is instance of MyClass → MyClass.__init__(result, *args) called
      4. Object is returned
"""

class ImmutablePoint:
    """
    Demonstrates __new__ override.
    We make this effectively immutable using __new__ and preventing __setattr__.
    """

    def __new__(cls, x: float, y: float):
        """
        __new__ is called first. We use object.__new__ to create the instance.
        We store data here because __init__ can't use normal setattr on frozen obj.
        """
        instance = super().__new__(cls)
        # Directly bypass __setattr__ to set attributes during creation
        object.__setattr__(instance, "x", x)
        object.__setattr__(instance, "y", y)
        return instance

    def __init__(self, x: float, y: float):
        """Called after __new__. In this case x, y already set — so do nothing."""
        pass  # Attributes already set in __new__

    def __setattr__(self, name, value):
        """Block any attribute modification after creation — immutable!"""
        raise AttributeError(f"ImmutablePoint is immutable. Cannot set '{name}'")

    def __repr__(self):
        return f"ImmutablePoint({self.x}, {self.y})"


# ── Demo ──────────────────────────────────────────────────────────────────────
print("\n--- __new__ vs __init__ Demo ---")
p = ImmutablePoint(3.0, 4.0)
print(p)

try:
    p.x = 10  # Blocked by __setattr__
except AttributeError as e:
    print(f"Error: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 15: DESIGN PATTERNS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What are Design Patterns?
      Reusable solutions to commonly occurring problems in software design.
      Categorized into: Creational, Structural, Behavioral.

  Q2. Name some Creational patterns.
      Singleton, Factory, Abstract Factory, Builder, Prototype.

  Q3. Name some Behavioral patterns.
      Observer, Strategy, Command, Iterator, Template Method, State.

  Q4. Name some Structural patterns.
      Decorator, Adapter, Facade, Proxy, Composite, Bridge.
"""

# ── PATTERN 1: SINGLETON ─────────────────────────────────────────────────────
# (Already shown via Metaclass — here's an alternative __new__-based approach)

class AppConfig:
    """
    Singleton via __new__.
    Only one AppConfig can exist — used for global application configuration.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
        return cls._instance

    def set(self, key: str, value):
        self._config[key] = value

    def get(self, key: str, default=None):
        return self._config.get(key, default)


# ── PATTERN 2: FACTORY METHOD ─────────────────────────────────────────────────
"""
CROSS-QUESTIONS (Factory):
  Q1. What is the Factory pattern?
      A creational pattern where a method/class creates objects without
      exposing instantiation logic to the client.
      Client asks WHAT to create; Factory decides HOW to create it.

  Q2. Factory Method vs Abstract Factory?
      Factory Method: One method that creates ONE product.
      Abstract Factory: A factory of factories — creates families of products.

  Q3. Why use Factory pattern?
      - Decouples object creation from usage
      - Easy to add new types without changing client code (Open/Closed)
      - Centralizes object creation logic
"""

class Notification(ABC):
    """Abstract product."""

    @abstractmethod
    def send(self, recipient: str, message: str):
        pass


class EmailNotification(Notification):
    def send(self, recipient: str, message: str):
        print(f"[Email] To: {recipient} → {message}")


class SMSNotification(Notification):
    def send(self, recipient: str, message: str):
        print(f"[SMS] To: {recipient} → {message}")


class PushNotification(Notification):
    def send(self, recipient: str, message: str):
        print(f"[Push] To: {recipient} → {message}")


class NotificationFactory:
    """
    Factory class: creates Notification objects based on type string.
    Client code doesn't need to know concrete class names.
    """

    _registry = {
        "email": EmailNotification,
        "sms":   SMSNotification,
        "push":  PushNotification,
    }

    @classmethod
    def create(cls, notification_type: str) -> Notification:
        """Factory method."""
        klass = cls._registry.get(notification_type.lower())
        if not klass:
            raise ValueError(f"Unknown notification type: {notification_type}")
        return klass()

    @classmethod
    def register(cls, name: str, klass):
        """Extensible: register new notification types at runtime."""
        cls._registry[name] = klass


# ── PATTERN 3: OBSERVER ───────────────────────────────────────────────────────
"""
CROSS-QUESTIONS (Observer):
  Q1. What is the Observer pattern?
      A behavioral pattern where an object (Subject/Observable) maintains a list
      of dependents (Observers) and notifies them automatically when its state changes.
      Real-world: Event systems, news feeds, stock market tickers.

  Q2. What is the difference between Observer and Pub/Sub?
      Observer: Observers know about the Subject (tight coupling).
      Pub/Sub: Intermediary message broker — Publisher and Subscriber don't know each other.

  Q3. What's the risk with Observer pattern?
      Memory leaks if observers aren't properly unregistered.
      Circular dependencies.
      Unpredictable notification order.
"""

class EventSystem:
    """
    Simple Observer / Event system.
    Subject maintains list of observers per event type.
    """

    def __init__(self):
        self._listeners: dict[str, list] = {}

    def subscribe(self, event_type: str, listener):
        """Register an observer (listener function) for an event."""
        self._listeners.setdefault(event_type, []).append(listener)

    def unsubscribe(self, event_type: str, listener):
        """Remove an observer."""
        if event_type in self._listeners:
            self._listeners[event_type].remove(listener)

    def emit(self, event_type: str, data=None):
        """Notify all observers for this event type."""
        for listener in self._listeners.get(event_type, []):
            listener(data)


class StockMarket:
    """Subject/Observable: Notifies observers when stock price changes."""

    def __init__(self):
        self._events = EventSystem()
        self._prices: dict[str, float] = {}

    def subscribe(self, event, listener):
        self._events.subscribe(event, listener)

    def update_price(self, ticker: str, new_price: float):
        old_price = self._prices.get(ticker)
        self._prices[ticker] = new_price
        # Notify all observers
        self._events.emit("price_change", {
            "ticker": ticker,
            "old_price": old_price,
            "new_price": new_price
        })


# Observer functions (can also be class methods)
def alert_investor(data):
    print(f"[Investor Alert] {data['ticker']}: ₹{data['old_price']} → ₹{data['new_price']}")

def log_to_database(data):
    print(f"[DB Log] Recording price change for {data['ticker']}")


# ── PATTERN 4: STRATEGY ───────────────────────────────────────────────────────
"""
CROSS-QUESTIONS (Strategy):
  Q1. What is the Strategy pattern?
      A behavioral pattern that defines a family of algorithms,
      encapsulates each one, and makes them interchangeable.
      The context class can switch strategies at runtime.

  Q2. Strategy vs State pattern?
      Strategy: Client CHOOSES which strategy to use. Algorithms are interchangeable.
      State: Object changes behavior based on its own internal STATE.
             Transitions are managed by the object itself.
"""

class SortStrategy(ABC):
    """Abstract Strategy."""

    @abstractmethod
    def sort(self, data: list) -> list:
        pass


class BubbleSortStrategy(SortStrategy):
    def sort(self, data: list) -> list:
        arr = data.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr


class QuickSortStrategy(SortStrategy):
    def sort(self, data: list) -> list:
        if len(data) <= 1:
            return data
        pivot = data[len(data) // 2]
        left   = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right  = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)


class PythonBuiltinSortStrategy(SortStrategy):
    def sort(self, data: list) -> list:
        return sorted(data)


class Sorter:
    """
    Context class that uses a SortStrategy.
    Strategy can be changed at runtime!
    """

    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy):
        """Change strategy at runtime — Strategy pattern's power."""
        self._strategy = strategy

    def sort(self, data: list) -> list:
        return self._strategy.sort(data)


# ── PATTERN 5: DECORATOR PATTERN (not the Python @decorator) ──────────────────
"""
CROSS-QUESTIONS (Decorator Pattern):
  Q1. What is the Decorator design pattern?
      A structural pattern that adds behavior to objects DYNAMICALLY
      without modifying their class. It wraps objects in decorator objects.

  Q2. Is Python's @decorator the same as the Decorator design pattern?
      Similar concept, but Python's @ syntax decorates FUNCTIONS/CLASSES directly.
      The GoF Decorator Pattern wraps OBJECTS at runtime.

  Q3. Decorator vs Inheritance?
      Inheritance: Static — decided at design time.
      Decorator:   Dynamic — behavior added at runtime, more flexible.
"""

class Coffee(ABC):
    """Abstract component for the Decorator pattern."""

    @abstractmethod
    def cost(self) -> float:
        pass

    @abstractmethod
    def description(self) -> str:
        pass


class SimpleCoffee(Coffee):
    """Concrete component."""

    def cost(self) -> float:
        return 50.0

    def description(self) -> str:
        return "Simple Coffee"


class CoffeeDecorator(Coffee):
    """Abstract Decorator — wraps a Coffee object."""

    def __init__(self, coffee: Coffee):
        self._coffee = coffee  # The wrapped component

    def cost(self) -> float:
        return self._coffee.cost()

    def description(self) -> str:
        return self._coffee.description()


class MilkDecorator(CoffeeDecorator):
    """Concrete Decorator — adds milk."""

    def cost(self) -> float:
        return self._coffee.cost() + 20.0

    def description(self) -> str:
        return self._coffee.description() + ", Milk"


class SugarDecorator(CoffeeDecorator):
    """Concrete Decorator — adds sugar."""

    def cost(self) -> float:
        return self._coffee.cost() + 10.0

    def description(self) -> str:
        return self._coffee.description() + ", Sugar"


class VanillaDecorator(CoffeeDecorator):
    """Concrete Decorator — adds vanilla."""

    def cost(self) -> float:
        return self._coffee.cost() + 30.0

    def description(self) -> str:
        return self._coffee.description() + ", Vanilla"


# ── Demo for all patterns ─────────────────────────────────────────────────────
print("\n--- Design Patterns Demo ---")

# Singleton
config1 = AppConfig()
config2 = AppConfig()
config1.set("debug", True)
print(f"Config is Singleton: {config1 is config2}")
print(f"config2 debug: {config2.get('debug')}")  # True — same object!

# Factory
print()
for ntype in ["email", "sms", "push"]:
    n = NotificationFactory.create(ntype)
    n.send("user@example.com", "Hello!")

# Observer
print()
market = StockMarket()
market.subscribe("price_change", alert_investor)
market.subscribe("price_change", log_to_database)
market.update_price("RELIANCE", 2500.0)
market.update_price("INFY", 1800.0)

# Strategy
print()
data = [64, 25, 12, 22, 11]
sorter = Sorter(BubbleSortStrategy())
print(f"Bubble Sort: {sorter.sort(data)}")
sorter.set_strategy(QuickSortStrategy())
print(f"Quick Sort: {sorter.sort(data)}")

# Decorator Pattern
print()
coffee = SimpleCoffee()
coffee = MilkDecorator(coffee)
coffee = SugarDecorator(coffee)
coffee = VanillaDecorator(coffee)
print(f"Order: {coffee.description()}")
print(f"Total: ₹{coffee.cost()}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 16: SOLID PRINCIPLES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What are the SOLID principles?
      S - Single Responsibility Principle (SRP)
      O - Open/Closed Principle (OCP)
      L - Liskov Substitution Principle (LSP)
      I - Interface Segregation Principle (ISP)
      D - Dependency Inversion Principle (DIP)

  Q2. Explain SRP with an example.
      A class should have ONLY ONE reason to change.
      Bad: A User class that handles user data AND sends emails AND logs.
      Good: Separate UserRepository, EmailService, Logger classes.

  Q3. What is LSP (Liskov Substitution Principle)?
      Objects of a subclass should be substitutable for objects of the base class
      without altering the correctness of the program.
      Violation: Square extending Rectangle. Setting width of a "Square" 
      also changes height — unexpected behavior for a Rectangle user.

  Q4. What is DIP (Dependency Inversion)?
      High-level modules should not depend on low-level modules.
      Both should depend on ABSTRACTIONS (interfaces/ABCs).
      This enables easy swapping of implementations (strategy, injection).
"""

# ── S: Single Responsibility ──────────────────────────────────────────────────
class UserRepository:
    """Handles ONLY data storage for users."""
    def __init__(self):
        self._users = {}

    def save(self, user_id: str, data: dict):
        self._users[user_id] = data
        print(f"User {user_id} saved to DB.")

    def find(self, user_id: str) -> dict:
        return self._users.get(user_id)


class EmailService:
    """Handles ONLY email communication."""
    def send_welcome_email(self, email: str):
        print(f"Welcome email sent to {email}")


class UserRegistrationService:
    """
    Orchestrates user registration.
    Delegates to UserRepository and EmailService — doesn't do their job.
    """

    def __init__(self, repo: UserRepository, email_svc: EmailService):
        self._repo = repo
        self._email = email_svc

    def register(self, user_id: str, email: str, name: str):
        data = {"email": email, "name": name}
        self._repo.save(user_id, data)
        self._email.send_welcome_email(email)
        print(f"Registration complete for {name}")


# ── O: Open/Closed Principle ──────────────────────────────────────────────────
# OPEN for extension, CLOSED for modification.
# Add new behaviors by EXTENDING (new classes), not MODIFYING existing code.

class DiscountStrategy(ABC):
    """Open for extension — add new discount types by subclassing."""

    @abstractmethod
    def apply(self, price: float) -> float:
        pass


class NoDiscount(DiscountStrategy):
    def apply(self, price: float) -> float:
        return price

class TenPercentDiscount(DiscountStrategy):
    def apply(self, price: float) -> float:
        return price * 0.9

class SeasonalDiscount(DiscountStrategy):
    def apply(self, price: float) -> float:
        return price * 0.75


class PriceCalculator:
    """
    Closed for modification — adding a new discount does NOT require
    changing PriceCalculator. Just pass a new DiscountStrategy.
    """

    def __init__(self, strategy: DiscountStrategy):
        self._strategy = strategy

    def calculate(self, base_price: float) -> float:
        return self._strategy.apply(base_price)


# ── L: Liskov Substitution ────────────────────────────────────────────────────
# Subclasses must behave correctly when used in place of the base class.

class Bird(ABC):
    @abstractmethod
    def make_sound(self):
        pass

class FlyingBird(Bird):
    """More specific base class for birds that can fly."""
    def fly(self):
        print(f"{self.__class__.__name__} is flying!")

class Sparrow(FlyingBird):
    def make_sound(self):
        print("Tweet tweet!")

class Penguin(Bird):
    """
    LSP: Penguin IS-A Bird but NOT a FlyingBird.
    If Penguin extended FlyingBird and fly() raised NotImplementedError,
    that would VIOLATE LSP because you can't substitute Penguin where
    FlyingBird is expected.
    Correct design: Penguin extends Bird only.
    """
    def make_sound(self):
        print("Squawk!")

    def swim(self):
        print("Penguin is swimming!")


# ── I: Interface Segregation ──────────────────────────────────────────────────
# Clients should not be forced to depend on interfaces they don't use.
# Split FAT interfaces into smaller, specific ones.

class Printable(ABC):
    @abstractmethod
    def print_doc(self): pass

class Scannable(ABC):
    @abstractmethod
    def scan(self): pass

class Faxable(ABC):
    @abstractmethod
    def fax(self, number: str): pass

class SimplePrinter(Printable):
    """Only implements what it needs — Printable."""
    def print_doc(self):
        print("Printing document...")

class AllInOnePrinter(Printable, Scannable, Faxable):
    """Implements all three segregated interfaces."""
    def print_doc(self):
        print("All-in-one printing...")
    def scan(self):
        print("All-in-one scanning...")
    def fax(self, number: str):
        print(f"All-in-one faxing to {number}...")


# ── D: Dependency Inversion Principle ────────────────────────────────────────
# High-level modules depend on ABSTRACTIONS, not concrete implementations.

class MessageSender(ABC):
    """Abstraction (interface)."""

    @abstractmethod
    def send(self, recipient: str, message: str):
        pass


class GmailSender(MessageSender):
    """Concrete low-level module."""
    def send(self, recipient: str, message: str):
        print(f"[Gmail] Sending to {recipient}: {message}")


class TwilioSender(MessageSender):
    """Another concrete low-level module."""
    def send(self, recipient: str, message: str):
        print(f"[Twilio SMS] Sending to {recipient}: {message}")


class OrderService:
    """
    High-level module.
    Depends on MessageSender ABSTRACTION, not Gmail or Twilio directly.
    You can swap the sender without changing OrderService (DIP).
    """

    def __init__(self, sender: MessageSender):
        self._sender = sender  # Dependency Injection

    def place_order(self, customer_email: str, item: str):
        print(f"Order placed: {item}")
        self._sender.send(customer_email, f"Your order for {item} is confirmed!")


# ── Demo ──────────────────────────────────────────────────────────────────────
print("\n--- SOLID Principles Demo ---")

# SRP
repo = UserRepository()
email_svc = EmailService()
reg_svc = UserRegistrationService(repo, email_svc)
reg_svc.register("U001", "john@example.com", "John Doe")

# OCP
calc = PriceCalculator(TenPercentDiscount())
print(f"\nFinal price (10% off ₹1000): ₹{calc.calculate(1000)}")
calc2 = PriceCalculator(SeasonalDiscount())
print(f"Final price (seasonal off ₹1000): ₹{calc2.calculate(1000)}")

# DIP
print()
order_svc = OrderService(GmailSender())
order_svc.place_order("alice@gmail.com", "MacBook Pro")

order_svc2 = OrderService(TwilioSender())
order_svc2.place_order("+91-9876543210", "iPhone 15")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 17: DATACLASSES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is a dataclass in Python?
      A decorator (@dataclass) that auto-generates boilerplate methods:
      __init__, __repr__, __eq__ (and optionally __lt__, __hash__).
      Introduced in Python 3.7 (PEP 557).

  Q2. What is the difference between a regular class and a dataclass?
      Regular class: You write all dunder methods manually.
      Dataclass: Auto-generates __init__, __repr__, __eq__ from field annotations.

  Q3. What does frozen=True do in a dataclass?
      Makes the dataclass immutable — raises FrozenInstanceError if you try to set attributes.
      Also auto-generates __hash__.

  Q4. When would you choose a dataclass vs NamedTuple?
      Dataclass: Mutable (default), supports inheritance, more OOP features.
      NamedTuple: Always immutable, tuple semantics, slightly faster for iteration.
"""

from dataclasses import dataclass, field, asdict, astuple
from typing import List

@dataclass
class Product:
    """
    Dataclass: auto-generates __init__, __repr__, __eq__.
    Field annotations define the attributes.
    """
    name: str
    price: float
    category: str
    tags: List[str] = field(default_factory=list)  # Mutable default needs field()
    in_stock: bool = True

    # You can still add custom methods!
    def apply_discount(self, percent: float) -> float:
        return self.price * (1 - percent / 100)

    def __post_init__(self):
        """
        Called automatically AFTER __init__.
        Use for validation or post-processing.
        """
        if self.price < 0:
            raise ValueError(f"Price cannot be negative: {self.price}")
        self.name = self.name.strip().title()  # Normalize name


@dataclass(frozen=True)  # Immutable dataclass
class Coordinate:
    """
    frozen=True: makes instance immutable + generates __hash__
    Can be used as dict keys or in sets.
    """
    latitude: float
    longitude: float

    def distance_to(self, other: "Coordinate") -> float:
        """Haversine-approximate distance (simplified)."""
        return math.sqrt(
            (self.latitude - other.latitude) ** 2 +
            (self.longitude - other.longitude) ** 2
        )


@dataclass(order=True)  # Auto-generates __lt__, __le__, __gt__, __ge__
class StudentGrade:
    """order=True: enables comparison based on field order."""
    sort_index: float = field(init=False, repr=False)  # Hidden sort key
    name: str
    grade: float

    def __post_init__(self):
        # Set sort key after init
        object.__setattr__(self, "sort_index", self.grade) if False else None
        self.sort_index = self.grade


# ── Demo ──────────────────────────────────────────────────────────────────────
print("\n--- Dataclasses Demo ---")
p1 = Product("  laptop  ", 75000.0, "Electronics", tags=["portable", "work"])
p2 = Product("Phone", 25000.0, "Electronics")

print(p1)                                   # __repr__ auto-generated
print(f"Discount: ₹{p1.apply_discount(10)}")
print(f"p1 == p2: {p1 == p2}")             # __eq__ auto-generated
print(f"As dict: {asdict(p1)}")            # Utility: convert to dict

coord1 = Coordinate(28.6139, 77.2090)   # Delhi
coord2 = Coordinate(19.0760, 72.8777)   # Mumbai
print(f"\nDistance: {coord1.distance_to(coord2):.2f} (approx degrees)")

try:
    coord1.latitude = 30.0  # FrozenInstanceError!
except Exception as e:
    print(f"Frozen: {e}")

grades = [StudentGrade("Alice", 92.5), StudentGrade("Bob", 88.0), StudentGrade("Charlie", 95.0)]
grades.sort()  # Works because order=True
for g in grades:
    print(f"  {g.name}: {g.grade}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 18: __SLOTS__ — MEMORY OPTIMIZATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is __slots__?
      By default, Python stores instance attributes in a dictionary (__dict__).
      __slots__ replaces __dict__ with a fixed array of attribute slots,
      saving memory and speeding up attribute access.

  Q2. When should you use __slots__?
      When creating MILLIONS of small objects (e.g., in game engines, network packets).
      Saves ~40-60% memory per instance.

  Q3. What are the limitations of __slots__?
      - Cannot add arbitrary new attributes to instances
      - Doesn't work well with multiple inheritance if both parents have __slots__
      - Cannot use __dict__ (unless you add '__dict__' to __slots__)
      - Cannot pickle by default (need __getstate__/__setstate__)

  Q4. How does __slots__ affect inheritance?
      If parent has __slots__ and child doesn't define __slots__,
      child gets __dict__ again — the memory saving is lost for the child.
"""

class PointWithSlots:
    """
    Uses __slots__ instead of __dict__ for memory efficiency.
    Each instance stores x and y directly, not in a dictionary.
    """
    __slots__ = ("x", "y")  # Only x and y allowed as attributes

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_from_origin(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


class PointWithoutSlots:
    """Regular class — uses __dict__ for attributes."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


# ── Demo ──────────────────────────────────────────────────────────────────────
import sys

print("\n--- __slots__ Demo ---")
ps = PointWithSlots(3.0, 4.0)
pr = PointWithoutSlots(3.0, 4.0)

print(f"With __slots__: {sys.getsizeof(ps)} bytes")
print(f"Without __slots__: {sys.getsizeof(pr)} bytes + dict: {sys.getsizeof(pr.__dict__)} bytes")

try:
    ps.z = 10  # Not in __slots__ — AttributeError!
except AttributeError as e:
    print(f"Slots restriction: {e}")

# Can add arbitrary attrs to regular class
pr.z = 10
print(f"Regular class allows z={pr.z}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 19: DEEP COPY vs SHALLOW COPY in Objects
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is shallow copy vs deep copy?
      Shallow copy: Creates a new object, but nested objects are still SHARED references.
      Deep copy:    Creates a new object AND recursively copies all nested objects.
                   Completely independent — no shared references.

  Q2. How do you perform shallow/deep copy?
      import copy
      copy.copy(obj)     → Shallow copy
      copy.deepcopy(obj) → Deep copy

  Q3. When is shallow copy enough?
      When the object has no nested mutable objects, or when sharing nested
      objects is intentional/acceptable.

  Q4. What magic methods control copying?
      __copy__:     Customize shallow copy behavior.
      __deepcopy__: Customize deep copy behavior.
"""

import copy

class Address:
    def __init__(self, city: str, country: str):
        self.city = city
        self.country = country

    def __repr__(self):
        return f"Address({self.city}, {self.country})"


class PersonWithAddress:
    def __init__(self, name: str, address: Address):
        self.name = name
        self.address = address  # Nested mutable object

    def __repr__(self):
        return f"PersonWithAddress({self.name}, {self.address})"


# ── Demo ──────────────────────────────────────────────────────────────────────
print("\n--- Shallow vs Deep Copy Demo ---")

original = PersonWithAddress("Alice", Address("Delhi", "India"))

# Shallow copy: person is new, but address is SAME object
shallow = copy.copy(original)

# Deep copy: everything is new — completely independent
deep = copy.deepcopy(original)

print(f"Original:  {original}")
print(f"Shallow:   {shallow}")
print(f"Deep:      {deep}")

# Modify the nested address through shallow copy
shallow.address.city = "Mumbai"
shallow.name = "Bob"  # This doesn't affect original (name is string — immutable)

print(f"\nAfter modifying shallow copy's address:")
print(f"Original address: {original.address}")  # Changed! Shared reference!
print(f"Shallow  address: {shallow.address}")

# Modify the nested address through deep copy
deep.address.city = "Chennai"
print(f"\nAfter modifying deep copy's address:")
print(f"Original address: {original.address}")  # Unchanged! Truly independent
print(f"Deep copy address: {deep.address}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 20: OBJECT INTROSPECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is introspection in Python?
      The ability to examine objects at runtime — check their type,
      attributes, methods, class hierarchy.

  Q2. What is the difference between type() and isinstance()?
      type(obj): Returns the exact class of obj. No inheritance.
      isinstance(obj, cls): Checks if obj is an instance of cls OR any SUBCLASS.
                            Preferred for type checking.

  Q3. What does hasattr() do?
      Checks if an object has a specific attribute.
      Equivalent to: try: getattr(obj, name) except AttributeError: False

  Q4. What is dir()?
      Returns a list of all attributes and methods of an object (including inherited).

  Q5. What is vars()?
      Returns the __dict__ of an object — only the instance attributes (not methods).
"""

print("\n--- Object Introspection Demo ---")

dog = Dog("Rex", "Labrador")

# type() — exact class
print(f"type(dog): {type(dog)}")

# isinstance() — with inheritance
print(f"isinstance(dog, Dog): {isinstance(dog, Dog)}")
print(f"isinstance(dog, Animal): {isinstance(dog, Animal)}")  # True — inheritance!
print(f"isinstance(dog, Cat): {isinstance(dog, Cat)}")        # False

# issubclass()
print(f"issubclass(Dog, Animal): {issubclass(Dog, Animal)}")
print(f"issubclass(Dog, Cat): {issubclass(Dog, Cat)}")

# hasattr / getattr / setattr / delattr
print(f"hasattr(dog, 'breed'): {hasattr(dog, 'breed')}")
print(f"hasattr(dog, 'fly'): {hasattr(dog, 'fly')}")
print(f"getattr(dog, 'breed'): {getattr(dog, 'breed')}")
getattr(dog, 'breed', 'Unknown')  # Default if missing

# vars() — instance dict
print(f"vars(dog): {vars(dog)}")

# dir() — all attributes including inherited and dunder
all_attrs = dir(dog)
user_attrs = [a for a in all_attrs if not a.startswith("_")]
print(f"User-facing methods/attrs: {user_attrs}")

# __class__, __bases__, __mro__
print(f"dog.__class__: {dog.__class__}")
print(f"Dog.__bases__: {Dog.__bases__}")
print(f"Dog.__mro__: {[c.__name__ for c in Dog.__mro__]}")

# callable()
print(f"callable(dog.speak): {callable(dog.speak)}")
print(f"callable(dog.breed): {callable(dog.breed)}")

# id() — memory address
print(f"id(dog): {id(dog)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 21: ITERATORS AND GENERATORS IN OOP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
CROSS-QUESTIONS:
  Q1. What is the iterator protocol?
      Two methods: __iter__ and __next__.
      __iter__: Returns the iterator object (usually self).
      __next__: Returns the next value. Raises StopIteration when exhausted.

  Q2. What is the difference between an iterable and an iterator?
      Iterable: Has __iter__ method. E.g., list, tuple, str.
                You can call iter() on it to get an iterator.
      Iterator: Has BOTH __iter__ AND __next__. Maintains current position.

  Q3. When would you create a custom iterator class?
      When you need lazy evaluation (compute values on-demand),
      infinite sequences, or complex traversal logic.

  Q4. What is a generator function? How is it different from an iterator class?
      Generator function uses 'yield'. Python auto-creates __iter__ and __next__.
      Much simpler syntax than writing an iterator class manually.
"""

class Fibonacci:
    """
    Custom iterator that generates Fibonacci numbers.
    Implements __iter__ and __next__ — the iterator protocol.
    """

    def __init__(self, max_count: int):
        self.max_count = max_count
        self.count = 0
        self.a, self.b = 0, 1

    def __iter__(self):
        """
        Returns the iterator object — usually 'self' for simple iterators.
        Called when you do: for x in fibonacci_obj
        """
        return self

    def __next__(self):
        """
        Returns next Fibonacci number.
        Raises StopIteration when exhausted.
        """
        if self.count >= self.max_count:
            raise StopIteration  # Signals end of iteration

        result = self.a
        self.a, self.b = self.b, self.a + self.b
        self.count += 1
        return result


class Range:
    """
    Custom Range iterator (like Python's built-in range()).
    Supports slicing and reversed iteration.
    """

    def __init__(self, start: int, stop: int, step: int = 1):
        self.start = start
        self.stop = stop
        self.step = step

    def __iter__(self):
        current = self.start
        while (self.step > 0 and current < self.stop) or \
              (self.step < 0 and current > self.stop):
            yield current          # Using yield makes this a generator-iterator
            current += self.step

    def __len__(self):
        return max(0, (self.stop - self.start + self.step - 1) // self.step)

    def __getitem__(self, index: int) -> int:
        """Support indexing: r[2]"""
        if index < 0:
            index += len(self)
        return self.start + index * self.step

    def __contains__(self, value: int) -> bool:
        """Support 'in' operator: 5 in r"""
        return self.start <= value < self.stop and (value - self.start) % self.step == 0


# ── Demo ──────────────────────────────────────────────────────────────────────
print("\n--- Custom Iterator Demo ---")
fib = Fibonacci(10)
print("First 10 Fibonacci:", list(fib))

# Exhausted — need new object
fib2 = Fibonacci(5)
for n in fib2:
    print(n, end=" ")
print()

r = Range(0, 20, 3)
print(f"Custom Range: {list(r)}")
print(f"r[2] = {r[2]}")
print(f"9 in r: {9 in r}")
print(f"10 in r: {10 in r}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 22: REAL-WORLD MINI PROJECT — E-COMMERCE SYSTEM
# (Combines: Inheritance, Composition, ABC, Properties, Polymorphism, Factory)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "=" * 70)
print("  REAL-WORLD MINI PROJECT: E-Commerce Order Processing System")
print("=" * 70)

from typing import Optional
from enum import Enum, auto

class OrderStatus(Enum):
    """Enum for order states — better than magic strings."""
    PENDING   = auto()
    CONFIRMED = auto()
    SHIPPED   = auto()
    DELIVERED = auto()
    CANCELLED = auto()


class Item:
    """Represents a product item in the cart."""

    def __init__(self, name: str, price: float, quantity: int = 1):
        self.name = name
        self._price = price
        self.quantity = quantity

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float):
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = value

    @property
    def subtotal(self) -> float:
        return self._price * self.quantity

    def __repr__(self):
        return f"Item({self.name}, ₹{self._price} x {self.quantity})"


class Cart:
    """Shopping cart — uses Composition (contains Items)."""

    def __init__(self):
        self._items: list[Item] = []

    def add_item(self, item: Item):
        self._items.append(item)
        print(f"Added: {item.name} (x{item.quantity})")

    def remove_item(self, name: str):
        self._items = [i for i in self._items if i.name != name]

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self._items)

    @property
    def item_count(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        lines = [f"  {item}" for item in self._items]
        return "\n".join(lines) + f"\n  Total: ₹{self.total}"


class BaseOrder(ABC):
    """Abstract base class for all order types."""

    _order_counter = 0

    def __init__(self, customer_name: str, cart: Cart):
        BaseOrder._order_counter += 1
        self.order_id = f"ORD-{BaseOrder._order_counter:04d}"
        self.customer_name = customer_name
        self._cart = cart
        self._status = OrderStatus.PENDING
        self._history: list[str] = [f"Order created: {self.order_id}"]

    @property
    def status(self) -> OrderStatus:
        return self._status

    @abstractmethod
    def get_delivery_days(self) -> int:
        """Different order types have different delivery times."""
        pass

    @abstractmethod
    def get_shipping_cost(self) -> float:
        """Different order types have different shipping costs."""
        pass

    @property
    def grand_total(self) -> float:
        return self._cart.total + self.get_shipping_cost()

    def confirm(self):
        self._status = OrderStatus.CONFIRMED
        self._history.append("Order confirmed")
        print(f"[{self.order_id}] Confirmed! Delivery in {self.get_delivery_days()} days.")

    def ship(self):
        if self._status != OrderStatus.CONFIRMED:
            raise RuntimeError("Order must be confirmed before shipping.")
        self._status = OrderStatus.SHIPPED
        self._history.append("Order shipped")
        print(f"[{self.order_id}] Shipped!")

    def cancel(self, reason: str = ""):
        self._status = OrderStatus.CANCELLED
        self._history.append(f"Cancelled: {reason}")
        print(f"[{self.order_id}] Cancelled. Reason: {reason}")

    def get_invoice(self) -> str:
        lines = [
            f"{'='*50}",
            f"INVOICE — {self.order_id}",
            f"Customer: {self.customer_name}",
            f"Status:   {self._status.name}",
            f"{'─'*50}",
            "Items:",
        ]
        for item in self._cart:
            lines.append(f"  {item.name:20s} ₹{item.price:8.2f} x{item.quantity}  = ₹{item.subtotal:.2f}")
        lines.extend([
            f"{'─'*50}",
            f"  Cart Total:    ₹{self._cart.total:.2f}",
            f"  Shipping:      ₹{self.get_shipping_cost():.2f}",
            f"  GRAND TOTAL:   ₹{self.grand_total:.2f}",
            f"{'='*50}",
        ])
        return "\n".join(lines)


class StandardOrder(BaseOrder):
    """Standard 5-7 day delivery."""

    def get_delivery_days(self) -> int:
        return 5

    def get_shipping_cost(self) -> float:
        return 0.0 if self._cart.total >= 500 else 49.0  # Free shipping above ₹500


class ExpressOrder(BaseOrder):
    """Express 1-2 day delivery with higher shipping cost."""

    def get_delivery_days(self) -> int:
        return 2

    def get_shipping_cost(self) -> float:
        return 149.0  # Flat express fee


class SameDayOrder(BaseOrder):
    """Same-day delivery — premium service."""

    def get_delivery_days(self) -> int:
        return 0  # Today!

    def get_shipping_cost(self) -> float:
        return 299.0


class OrderFactory:
    """Factory to create appropriate order type."""

    @staticmethod
    def create_order(
        order_type: str,
        customer: str,
        cart: Cart
    ) -> BaseOrder:
        types = {
            "standard":  StandardOrder,
            "express":   ExpressOrder,
            "sameday":   SameDayOrder,
        }
        klass = types.get(order_type.lower())
        if not klass:
            raise ValueError(f"Unknown order type: {order_type}")
        return klass(customer, cart)


# ── Run the mini e-commerce system ────────────────────────────────────────────
cart = Cart()
cart.add_item(Item("MacBook Pro 14\"", 199000.0, 1))
cart.add_item(Item("USB-C Hub", 3500.0, 2))
cart.add_item(Item("Screen Protector", 800.0, 1))

print(f"\nCart Summary:\n{cart}")

# Create orders using factory
std_order = OrderFactory.create_order("standard", "Rahul Sharma", cart)
exp_order = OrderFactory.create_order("express", "Priya Patel", cart)

std_order.confirm()
exp_order.confirm()
exp_order.ship()

print(f"\n{std_order.get_invoice()}")

# Polymorphism — iterate over different order types
all_orders = [std_order, exp_order]
print(f"\nAll Orders Summary:")
for order in all_orders:
    print(f"  {order.order_id} | {order.customer_name:15s} | "
          f"{order.status.name:10s} | {order.get_delivery_days()} days | "
          f"₹{order.grand_total:.2f}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FINAL SUMMARY — QUICK REFERENCE CHEAT SHEET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("""
╔══════════════════════════════════════════════════════════════════════╗
║         OOP CONCEPTS — QUICK REFERENCE CHEAT SHEET                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  Class          : Blueprint/template for objects                     ║
║  Object         : Instance of a class                                ║
║  __init__       : Initializer (not constructor — __new__ is)         ║
║  __str__        : Human-readable string (print/str)                  ║
║  __repr__       : Developer string (repr/shell)                      ║
║  @classmethod   : Takes 'cls', can access class state                ║
║  @staticmethod  : No cls/self, utility function in class             ║
║  Encapsulation  : Bundle data + control access                       ║
║  _protected     : Convention — don't use outside class               ║
║  __private      : Name mangled → _ClassName__attr                    ║
║  @property      : Controlled attribute access (getter/setter)        ║
║  Inheritance    : IS-A relationship, code reuse                      ║
║  super()        : Calls next in MRO, not just parent                 ║
║  MRO            : C3 Linearization — resolves diamond problem        ║
║  Polymorphism   : Same interface, different behavior                 ║
║  Duck Typing    : Check capability, not type                         ║
║  Abstraction    : abc.ABC + @abstractmethod                          ║
║  Composition    : HAS-A (lifetime bound)                             ║
║  Aggregation    : HAS-A (independent lifetime)                       ║
║  Mixin          : Reusable behavior, not standalone                  ║
║  Descriptor     : __get__/__set__/__delete__ — reusable validation   ║
║  Metaclass      : Class of classes — type is default metaclass       ║
║  __slots__      : Memory optimization, fixed attributes              ║
║  Dataclass      : Auto-generates boilerplate dunder methods          ║
║  Singleton      : Only one instance exists                           ║
║  Factory        : Centralized object creation                        ║
║  Observer       : Subscribe/notify pattern                           ║
║  Strategy       : Interchangeable algorithms                         ║
║  Decorator(GoF) : Wrap objects to add behavior dynamically           ║
║  SOLID          : SRP, OCP, LSP, ISP, DIP — design principles       ║
╚══════════════════════════════════════════════════════════════════════╝
""")

print("=" * 70)
print("  Good luck with your interview! 🚀 You've got this!")
print("=" * 70)
