import os
import requests
from flask import Flask, render_template, request, send_from_directory, url_for
from PIL import Image, ImageDraw, ImageFont
import random
import io
from gtts import gTTS
import uuid

# Get the absolute path to the project root (one level up from api/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__,
            static_folder=os.path.join(PROJECT_ROOT, 'static'),
            template_folder=os.path.join(PROJECT_ROOT, 'templates'))

# Ensure the static directories exist (relative to PROJECT_ROOT)
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')
IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
MUSIC_DIR = os.path.join(STATIC_DIR, 'music')
FONTS_DIR = os.path.join(STATIC_DIR, 'fonts')
CURATED_MEMES_DIR = os.path.join(IMAGES_DIR, 'curated_memes')

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(CURATED_MEMES_DIR, exist_ok=True) # Ensure curated memes directory exists

# Define coding questions and answers, now categorized by skill level
CODING_QUESTIONS = {
    "python": {
        "beginner": [
            {"question": "What is the output of 'print(type([]))' in Python?", "correct_answer": "<class 'list'>"},
            {"question": "Which keyword is used to define a function in Python?", "correct_answer": "def"},
            {"question": "What is the result of '2 + 2 * 3' in Python?", "correct_answer": "8"},
            {"question": "How do you comment a single line in Python?", "correct_answer": "#"},
            {"question": "Which data type is used to store a sequence of characters in Python?", "correct_answer": "string"},
            {"question": "What is the keyword to exit a loop prematurely in Python?", "correct_answer": "break"},
            {"question": "Which function is used to get input from the user in Python?", "correct_answer": "input"},
            {"question": "What is the operator for exponentiation in Python?", "correct_answer": "**"},
            {"question": "What is the output of 'len(\"hello\")' in Python?", "correct_answer": "5"},
            {"question": "Which module is used for mathematical operations in Python?", "correct_answer": "math"},
            {"question": "How do you import a module named 'random'?", "correct_answer": "import random"},
            {"question": "What is the data type of 'True' in Python?", "correct_answer": "boolean"},
            {"question": "Which loop is used to iterate over a sequence in Python?", "correct_answer": "for"},
            {"question": "What does 'pip' stand for in Python?", "correct_answer": "pip installs packages"},
            {"question": "How do you define an empty dictionary in Python?", "correct_answer": "{}"},
            {"question": "What is the purpose of 'else' in an 'if-else' statement?", "correct_answer": "alternative execution"},
            {"question": "What is the output of '10 // 3' in Python?", "correct_answer": "3"},
            {"question": "Which method is used to add an item to the end of a list?", "correct_answer": "append"},
            {"question": "What is the output of 'print(5 > 3 and 10 < 20)'?", "correct_answer": "True"},
            {"question": "How do you create a multiline string in Python?", "correct_answer": "triple quotes"},
        ],
        "intermediate": [
            {"question": "What is the output of: `x = [1, 2, 3]; y = x; y.append(4); print(x)`?", "correct_answer": "[1, 2, 3, 4]"},
            {"question": "How do you make a copy of a list without referencing the original?", "correct_answer": "list.copy() or list[:]"},
            {"question": "What is the output of: `print('Python' * 2)`?", "correct_answer": "PythonPython"},
            {"question": "Fill in the blank to print 'Hello, World!' using an f-string: `name = 'World'; print(f'Hello, {____}!')`", "correct_answer": "name"},
            {"question": "How do you remove duplicate elements from a list using a set?", "correct_answer": "list(set(my_list))"},
            {"question": "What is the output of: `def func(a, b=1): return a + b; print(func(5))`?", "correct_answer": "6"},
            {"question": "How do you swap two variables `a` and `b` in one line?", "correct_answer": "a, b = b, a"},
            {"question": "What is the output of: `print(bool(0))`?", "correct_answer": "False"},
            {"question": "How do you check if a key 'name' exists in a dictionary 'data'?", "correct_answer": "'name' in data"},
            {"question": "What is the output of: `list1 = [1, 2]; list2 = [3, 4]; list1.extend(list2); print(list1)`?", "correct_answer": "[1, 2, 3, 4]"},
            {"question": "How do you iterate over both index and value of a list in a loop?", "correct_answer": "enumerate()"},
            {"question": "What is the output of: `print('2' + '2')`?", "correct_answer": "22"},
            {"question": "How do you get the last element of a list 'my_list'?", "correct_answer": "my_list[-1]"},
            {"question": "What is the output of: `print(abs(-10))`?", "correct_answer": "10"},
            {"question": "How do you convert a string '123' to an integer?", "correct_answer": "int('123')"},
            {"question": "What is the output of: `x = 10; y = 20; print(x > y or y > x)`?", "correct_answer": "True"},
            {"question": "How do you create a list of numbers from 0 to 4 using `range()`?", "correct_answer": "list(range(5))"},
            {"question": "What is the output of: `print(len('coding'))`?", "correct_answer": "6"},
            {"question": "How do you define a constant variable (by convention) in Python?", "correct_answer": "UPPERCASE_SNAKE_CASE"},
            {"question": "What is the output of: `print(type((1,)))`?", "correct_answer": "<class 'tuple'>"},
        ],
        "expert": [
            {"question": "What is the output of: `(lambda x: x*2)(5)`?", "correct_answer": "10"},
            {"question": "How do you implement a simple context manager for a file?", "correct_answer": "with open(...) as f:"},
            {"question": "What is the output of: `class A: pass; class B(A): pass; print(isinstance(B(), A))`?", "correct_answer": "True"},
            {"question": "How do you create a generator expression for squares of numbers 0-2?", "correct_answer": "(x*x for x in range(3))"},
            {"question": "What is the output of: `def outer(): x = 10; def inner(): return x; return inner; print(outer()())`?", "correct_answer": "10"},
            {"question": "How do you make a class iterable in Python?", "correct_answer": "__iter__ and __next__"},
            {"question": "What is the output of: `import collections; d = collections.Counter('hello'); print(d['l'])`?", "correct_answer": "2"},
            {"question": "How do you use `map` to double all numbers in `[1,2,3]`?", "correct_answer": "list(map(lambda x: x*2, [1,2,3]))"},
            {"question": "What is the output of: `print(all([True, True, False]))`?", "correct_answer": "False"},
            {"question": "How do you create a simple decorator that prints 'Hello' before a function runs?", "correct_answer": "def decorator(func): def wrapper(*args, **kwargs): print('Hello'); return func(*args, **kwargs); return wrapper"},
            {"question": "What is the output of: `print(sum(range(4)))`?", "correct_answer": "6"},
            {"question": "How do you get the current working directory?", "correct_answer": "os.getcwd()"},
            {"question": "What is the output of: `data = {'a': 1, 'b': 2}; print(data.get('c', 0))`?", "correct_answer": "0"},
            {"question": "How do you flatten a list of lists `[[1,2],[3,4]]` into `[1,2,3,4]`?", "correct_answer": "[item for sublist in my_list for item in sublist]"},
            {"question": "What is the output of: `print(list(filter(lambda x: x % 2 == 0, [1,2,3,4])))`?", "correct_answer": "[2, 4]"},
            {"question": "How do you define a class method in Python?", "correct_answer": "@classmethod"},
            {"question": "What is the output of: `print(max(1, 5, 2))`?", "correct_answer": "5"},
            {"question": "How do you open a file for appending text?", "correct_answer": "open(filename, 'a')"},
            {"question": "What is the output of: `print(set([1, 1, 2, 3]))`?", "correct_answer": "{1, 2, 3}"},
            {"question": "How do you create an anonymous function for adding two numbers?", "correct_answer": "lambda x, y: x + y"},
        ]
    },
    "java": {
        "beginner": [
            {"question": "Which keyword is used to define a class in Java?", "correct_answer": "class"},
            {"question": "What is the entry point method for a Java application?", "correct_answer": "main"},
            {"question": "Which keyword is used for inheritance in Java?", "correct_answer": "extends"},
            {"question": "What is the default value of a boolean variable in Java?", "correct_answer": "false"},
            {"question": "Which access modifier means visible only within the class?", "correct_answer": "private"},
            {"question": "What is the keyword to create an object in Java?", "correct_answer": "new"},
            {"question": "Which loop executes at least once in Java?", "correct_answer": "do-while"},
            {"question": "What is the superclass of all classes in Java?", "correct_answer": "Object"},
            {"question": "Which keyword is used to handle exceptions in Java?", "correct_answer": "try"},
            {"question": "What is the operator for logical AND in Java?", "correct_answer": "&&"},
            {"question": "Which data type stores whole numbers in Java?", "correct_answer": "int"},
            {"question": "What is the purpose of 'static' keyword in a method?", "correct_answer": "belongs to class"},
            {"question": "Which method is used to print output to the console in Java?", "correct_answer": "System.out.println"},
            {"question": "What is the keyword to prevent a class from being subclassed?", "correct_answer": "final"},
            {"question": "What is the size of 'char' data type in Java?", "correct_answer": "2 bytes"},
            {"question": "Which collection stores unique elements in Java?", "correct_answer": "Set"},
            {"question": "What is a 'checked exception' in Java?", "correct_answer": "compile-time exception"},
            {"question": "Which keyword is used to refer to the current object?", "correct_answer": "this"},
            {"question": "What is the concept of wrapping data and methods into a single unit?", "correct_answer": "encapsulation"},
            {"question": "What is the default value of a reference type variable in Java?", "correct_answer": "null"},
        ],
        "intermediate": [
            {"question": "What is the output of: `String s = \"Java\"; System.out.println(s.length());`?", "correct_answer": "4"},
            {"question": "How do you create an empty ArrayList of Strings?", "correct_answer": "new ArrayList<String>()"},
            {"question": "What is the output of: `int x = 5; int y = x++; System.out.println(y);`?", "correct_answer": "5"},
            {"question": "Fill in the blank to print 'Hello': `public class MyClass { public static void main(String[] args) { System.out.println(\"Hello\"); } }`", "correct_answer": "main"},
            {"question": "How do you convert a String '123' to an int?", "correct_answer": "Integer.parseInt(\"123\")"},
            {"question": "What is the output of: `String s1 = \"abc\"; String s2 = \"abc\"; System.out.println(s1 == s2);`?", "correct_answer": "true"},
            {"question": "How do you iterate over an ArrayList named 'myList'?", "correct_answer": "for (String item : myList)"},
            {"question": "What is the output of: `System.out.println(Math.max(10, 20));`?", "correct_answer": "20"},
            {"question": "How do you declare a constant integer named `MAX_VALUE` with value 100?", "correct_answer": "final int MAX_VALUE = 100;"},
            {"question": "What is the output of: `int[] arr = {1, 2, 3}; System.out.println(arr[0]);`?", "correct_answer": "1"},
            {"question": "How do you throw a custom exception 'MyException'?", "correct_answer": "throw new MyException();"},
            {"question": "What is the output of: `String s = \"hello\"; System.out.println(s.toUpperCase());`?", "correct_answer": "HELLO"},
            {"question": "How do you add an element 'item' to a `HashSet` named `mySet`?", "correct_answer": "mySet.add(item);"},
            {"question": "What is the output of: `System.out.println(5 / 2);` (integer division)?", "correct_answer": "2"},
            {"question": "How do you define an abstract method?", "correct_answer": "abstract void myMethod();"},
            {"question": "What is the output of: `boolean b = (10 > 5) && (20 < 10); System.out.println(b);`?", "correct_answer": "false"},
            {"question": "How do you create a new thread using `Runnable`?", "correct_answer": "new Thread(new MyRunnable()).start();"},
            {"question": "What is the output of: `String s = null; System.out.println(s == null);`?", "correct_answer": "true"},
            {"question": "How do you implement multiple interfaces in a class?", "correct_answer": "implements Interface1, Interface2"},
            {"question": "What is the output of: `System.out.println(Integer.valueOf(\"5\"));`?", "correct_answer": "5"},
        ],
        "expert": [
            {"question": "What is the output of: `List<String> list = Arrays.asList(\"a\", \"b\"); list.forEach(System.out::print);`?", "correct_answer": "ab"},
            {"question": "How do you create a `Stream` from an `ArrayList` named `myList`?", "correct_answer": "myList.stream()"},
            {"question": "What is the output of: `Optional<String> opt = Optional.ofNullable(null); System.out.println(opt.isPresent());`?", "correct_answer": "false"},
            {"question": "How do you filter a stream of integers to keep only even numbers?", "correct_answer": ".filter(n -> n % 2 == 0)"},
            {"question": "What is the output of: `Map<String, Integer> map = new HashMap<>(); map.put(\"A\", 1); System.out.println(map.get(\"B\"));`?", "correct_answer": "null"},
            {"question": "How do you use `Collectors.toList()` in a stream pipeline?", "correct_answer": ".collect(Collectors.toList())"},
            {"question": "What is the output of: `CompletableFuture<String> cf = CompletableFuture.completedFuture(\"Done\"); System.out.println(cf.get());`?", "correct_answer": "Done"},
            {"question": "How do you define a functional interface with a single abstract method `void execute()`?", "correct_answer": "@FunctionalInterface interface MyInterface { void execute(); }"},
            {"question": "What is the output of: `System.out.println(new BigDecimal(\"1.0\").subtract(new BigDecimal(\"0.1\")));`?", "correct_answer": "0.9"},
            {"question": "How do you create an immutable list from an existing list `myList` (Java 9+)?", "correct_answer": "List.of(myList.toArray()) or myList.stream().collect(Collectors.toUnmodifiableList())"},
            {"question": "What is the output of: `System.out.println(\"hello\".chars().count());`?", "correct_answer": "5"},
            {"question": "How do you use `try-with-resources` for an `InputStream`?", "correct_answer": "try (InputStream is = ...) { ... }"},
            {"question": "What is the output of: `System.out.println(Duration.ofHours(1).toMinutes());`?", "correct_answer": "60"},
            {"question": "How do you sort an `ArrayList` of strings in reverse alphabetical order?", "correct_answer": "Collections.sort(list, Collections.reverseOrder());"},
            {"question": "What is the output of: `System.out.println(Pattern.matches(\"a.c\", \"abc\"));`?", "correct_answer": "true"},
            {"question": "How do you use `Thread.sleep()` to pause execution for 1 second?", "correct_answer": "Thread.sleep(1000);"},
            {"question": "What is the output of: `System.out.println(String.join(\"-\", \"A\", \"B\", \"C\"));`?", "correct_answer": "A-B-C"},
            {"question": "How do you get the current date using `java.time.LocalDate`?", "correct_answer": "LocalDate.now();"},
            {"question": "What is the output of: `System.out.println(IntStream.range(1, 3).sum());`?", "correct_answer": "3"},
            {"question": "How do you create a custom annotation `@MyAnnotation`?", "correct_answer": "@interface MyAnnotation { ... }"},
        ]
    },
    "cpp": {
        "beginner": [
            {"question": "What is the operator used for dynamic memory allocation in C++?", "correct_answer": "new"},
            {"question": "Which header file is used for input/output operations in C++?", "correct_answer": "iostream"},
            {"question": "What does 'cout' stand for in C++?", "correct_answer": "console output"},
            {"question": "Which symbol is used to indicate a pointer in C++?", "correct_answer": "*"},
            {"question": "What is the keyword for defining a constant in C++?", "correct_answer": "const"},
            {"question": "Which operator is used for dereferencing a pointer?", "correct_answer": "*"},
            {"question": "What is the standard namespace in C++?", "correct_answer": "std"},
            {"question": "Which loop is guaranteed to execute at least once in C++?", "correct_answer": "do-while"},
            {"question": "What is the purpose of 'virtual' keyword in a function?", "correct_answer": "polymorphism"},
            {"question": "Which operator is used for scope resolution in C++?", "correct_answer": "::"},
            {"question": "What is the data type for single characters in C++?", "correct_answer": "char"},
            {"question": "Which keyword is used to inherit a class in C++?", "correct_answer": "public"},
            {"question": "What is the size of an 'int' in C++ (typically)?", "correct_answer": "4 bytes"},
            {"question": "Which container stores elements in a sorted order by default?", "correct_answer": "map"},
            {"question": "What is the purpose of the 'delete' operator?", "correct_answer": "deallocate memory"},
            {"question": "Which type of inheritance allows a class to inherit from multiple base classes?", "correct_answer": "multiple"},
            {"question": "What is the operator for bitwise AND?", "correct_answer": "&"},
            {"question": "What is the concept of converting an object of one class type to another?", "correct_answer": "type casting"},
            {"question": "Which keyword is used to define a template in C++?", "correct_answer": "template"},
            {"question": "What is the purpose of the 'this' pointer in C++?", "correct_answer": "current object"},
        ],
        "intermediate": [
            {"question": "What is the output of: `int arr[] = {1, 2, 3}; std::cout << arr[1];`?", "correct_answer": "2"},
            {"question": "How do you include a header file named 'vector'?", "correct_answer": "#include <vector>"},
            {"question": "What is the output of: `int x = 5; int& y = x; y++; std::cout << x;`?", "correct_answer": "6"},
            {"question": "Fill in the blank to print 'Hello': `int main() { std::cout << \"Hello\"; return 0; }`", "correct_answer": "main"},
            {"question": "How do you create a new object of class `MyClass` using dynamic allocation?", "correct_answer": "new MyClass()"},
            {"question": "What is the output of: `std::string s = \"C++\"; std::cout << s.length();`?", "correct_answer": "3"},
            {"question": "How do you declare a constant integer named `PI` with value 3?", "correct_answer": "const int PI = 3;"},
            {"question": "What is the output of: `int a = 10, b = 20; std::cout << (a > b ? a : b);`?", "correct_answer": "20"},
            {"question": "How do you add an element `5` to a `std::vector<int>` named `vec`?", "correct_answer": "vec.push_back(5);"},
            {"question": "What is the output of: `int x = 10; std::cout << (x % 3);`?", "correct_answer": "1"},
            {"question": "How do you declare a pointer to an integer?", "correct_answer": "int* ptr;"},
            {"question": "What is the output of: `double val = 3.14; std::cout << (int)val;`?", "correct_answer": "3"},
            {"question": "How do you read a line of input from the user into a string `s`?", "correct_answer": "std::getline(std::cin, s);"},
            {"question": "What is the output of: `bool b = true && false; std::cout << b;`?", "correct_answer": "0"},
            {"question": "How do you define a function that takes no arguments and returns nothing?", "correct_answer": "void func()"},
            {"question": "What is the output of: `std::string s = \"Hello\"; s += \" World\"; std::cout << s;`?", "correct_answer": "Hello World"},
            {"question": "How do you get the size of an array `arr`?", "correct_answer": "sizeof(arr)/sizeof(arr[0])"},
            {"question": "What is the output of: `int x = 7; std::cout << (x | 2);`?", "correct_answer": "7"},
            {"question": "How do you create an object of a class `Car` on the stack?", "correct_answer": "Car myCar;"},
            {"question": "What is the output of: `std::cout << (10 / 3.0);`?", "correct_answer": "3.33333"}, # or similar float
        ],
        "expert": [
            {"question": "What is the output of: `std::vector<int> v = {1, 2, 3}; std::for_each(v.begin(), v.end(), [](int n){ std::cout << n; });`?", "correct_answer": "123"},
            {"question": "How do you declare a shared pointer to an integer initialized with 10?", "correct_answer": "std::make_shared<int>(10);"},
            {"question": "What is the output of: `template<typename T> T add(T a, T b) { return a + b; } std::cout << add(1, 2);`?", "correct_answer": "3"},
            {"question": "How do you use `std::bind` to create a function object that calls `std::plus<int>()` with the first argument fixed to 5?", "correct_answer": "std::bind(std::plus<int>(), 5, std::placeholders::_1);"},
            {"question": "What is the output of: `int x = 5; std::atomic<int> y(x); y++; std::cout << y;`?", "correct_answer": "6"},
            {"question": "How do you define a lambda that captures a variable `x` by value?", "correct_answer": "[x](){ ... };"},
            {"question": "What is the output of: `std::string s = \"test\"; std::cout << s.substr(1, 2);`?", "correct_answer": "es"},
            {"question": "How do you prevent a function from throwing exceptions?", "correct_answer": "noexcept"},
            {"question": "What is the output of: `std::vector<int> v = {1, 2, 3}; std::cout << *std::find(v.begin(), v.end(), 2);`?", "correct_answer": "2"},
            {"question": "How do you use `std::thread` to run a function `my_func` asynchronously?", "correct_answer": "std::thread t(my_func); t.join();"},
            {"question": "What is the output of: `std::cout << (std::numeric_limits<int>::max() + 1);`?", "correct_answer": "negative number (overflow)"}, # or specific negative number
            {"question": "How do you define a custom literal `_kg` for `double`?", "correct_answer": "double operator\"\"_kg(long double val) { return val; }"},
            {"question": "What is the output of: `std::map<int, std::string> m = {{1, \"one\"}}; std::cout << m[1];`?", "correct_answer": "one"},
            {"question": "How do you use `std::move` to move resources from `src` to `dest`?", "correct_answer": "dest = std::move(src);"},
            {"question": "What is the output of: `std::string s = \"hello\"; std::cout << s.at(0);`?", "correct_answer": "h"},
            {"question": "How do you make a class non-copyable (C++11 and later)?", "correct_answer": "MyClass(const MyClass&) = delete;"},
            {"question": "What is the output of: `std::vector<int> v = {1, 2, 3}; std::sort(v.begin(), v.end(), std::greater<int>()); std::cout << v[0];`?", "correct_answer": "3"},
            {"question": "How do you define a variadic template function?", "correct_answer": "template<typename... Args> void func(Args... args) { ... }"},
            {"question": "What is the output of: `enum class Color { Red, Green }; std::cout << (int)Color::Red;`?", "correct_answer": "0"},
            {"question": "How do you use `std::unique_ptr` to manage an object?", "correct_answer": "std::unique_ptr<MyClass> ptr(new MyClass());"},
        ]
    }
}

# Define funny meme texts based on skill level
MEME_TEXTS = {
    "beginner": [
        "Me debugging my code at 3 AM: 'It works on my machine!'",
        "When your code compiles on the first try... but you didn't even save it.",
        "My code doesn't work. I have no idea why. My code works. I have no idea why.",
        "Stack Overflow: My best friend and worst enemy.",
        "Trying to understand legacy code like: 'What even is this?'"
    ],
    "intermediate": [
        "When you finally understand recursion, but now you can't explain it.",
        "Optimizing code for performance vs. readability: The eternal struggle.",
        "Me refactoring someone else's code: 'This is fine.'",
        "When the senior dev says 'just use a lambda' and you nod knowingly.",
        "That moment when you realize your 'clever' solution is just a bug waiting to happen."
    ],
    "expert": [
        "Architecting distributed systems while simultaneously questioning all life choices.",
        "When your microservices communicate flawlessly... in your dreams.",
        "Explaining your complex algorithm to non-tech people: 'It's magic!'",
        "Me after deploying to production: 'Please don't break, please don't break.'",
        "When you find a bug in a library you've been using for years."
    ]
}

# Text phrases for Text-to-Speech, based on skill level and language
SKILL_LEVEL_AUDIO_TEXTS = {
    "beginner": {
        "en": [
            "Welcome to the coding journey, beginner! Keep learning!",
            "Don't worry, every expert was once a beginner. You'll get there!",
            "Debugging is just problem-solving. You got this, future coding star!",
            "Learning to code is like learning a new language. Keep practicing!",
            "One step at a time, and you'll master it. Happy coding!",
            "Syntax errors are just friendly reminders. Keep going!",
            "Your code might be messy, but it's *your* messy code!",
            "The first step is always the hardest. You've already taken it!",
            "Keep calm and code on, little coder!",
            "Don't be afraid to break things, that's how we learn!",
            "Every line of code is a step towards greatness. Keep coding!",
            "You're building the future, one semicolon at a time!",
            "Coding is fun, even when it's frustrating. Embrace the journey!",
            "Remember, Google is your best friend. Use it wisely!",
            "The only way to fail is to stop trying. Never give up!",
            "Your brain is compiling. Please wait.",
            "Just keep swimming, just keep coding!",
            "Code, debug, repeat. The cycle of life!",
            "You're learning, and that's what matters most!",
            "The code is strong with this one... almost!"
        ],
        "hi": [
            "कोडिंग की दुनिया में आपका स्वागत है, शुरुआती! सीखते रहें!",
            "चिंता मत करो, हर विशेषज्ञ कभी शुरुआती था। तुम भी पहुंचोगे!",
            "डीबगिंग सिर्फ समस्या-समाधान है। तुम कर सकते हो, भविष्य के कोडिंग स्टार!",
            "कोडिंग सीखना एक नई भाषा सीखने जैसा है। अभ्यास करते रहो!",
            "एक-एक कदम उठाओ, और तुम इसमें माहिर हो जाओगे। हैप्पी कोडिंग!",
            "सिंटैक्स एरर सिर्फ दोस्ताना अनुस्मारक हैं। चलते रहो!",
            "तुम्हारा कोड शायद गंदा हो, लेकिन यह तुम्हारा गंदा कोड है!",
            "पहला कदम हमेशा सबसे मुश्किल होता है। तुम पहले ही उठा चुके हो!",
            "शांत रहो और कोड करते रहो, छोटे कोडर!",
            "चीजों को तोड़ने से डरो मत, हम ऐसे ही सीखते हैं!",
            "कोड की हर लाइन महानता की ओर एक कदम है। कोड करते रहो!",
            "तुम भविष्य बना रहे हो, एक सेमीकोलन एक बार में!",
            "कोडिंग मजेदार है, भले ही यह frustrating हो। यात्रा का आनंद लो!",
            "याद रखना, गूगल तुम्हारा सबसे अच्छा दोस्त है। इसका बुद्धिमानी से उपयोग करो!",
            "असफल होने का एकमात्र तरीका कोशिश करना बंद करना है। कभी हार मत मानो!",
            "तुम्हारा दिमाग कंपाइल हो रहा है। कृपया प्रतीक्षा करें।",
            "बस तैरते रहो, बस कोड करते रहो!",
            "कोड करो, डीबग करो, दोहराओ। जीवन का चक्र!",
            "तुम सीख रहे हो, और यही सबसे महत्वपूर्ण है!",
            "यह कोड मजबूत है... लगभग!"
        ]
    },
    "intermediate": {
        "en": [
            "You're making great progress, intermediate coder! Keep pushing your limits!",
            "Refactoring code is an art. You're becoming a true artist!",
            "Understanding complex concepts? You're on your way to mastery!",
            "Keep optimizing, keep innovating. The coding world awaits your solutions!",
            "You're past the basics, now for the fun challenges!",
            "When the bug disappears after you show it to someone, that's magic!",
            "Your code is evolving, just like you!",
            "Finding elegant solutions? That's the intermediate way!",
            "You're not just coding, you're crafting!",
            "The more you learn, the more you realize you don't know... and that's good!",
            "Design patterns are your new best friends. Embrace them!",
            "You're bridging the gap between theory and practice. Awesome!",
            "When your code works on the first try, it's suspicious, right?",
            "You're starting to think like a machine. Beep boop!",
            "Complex problems? Challenge accepted!",
            "You're building, you're learning, you're conquering!",
            "That moment when you finally understand recursion. Mind blown!",
            "Your code is getting cleaner, faster, stronger!",
            "Keep exploring new frameworks and libraries. The world is your oyster!",
            "You're officially beyond 'Hello World'. Congratulations!"
        ],
        "hi": [
            "तुम अच्छी प्रगति कर रहे हो, इंटरमीडिएट कोडर! अपनी सीमाओं को आगे बढ़ाते रहो!",
            "कोड को रिफैक्टर करना एक कला है। तुम एक सच्चे कलाकार बन रहे हो!",
            "जटिल अवधारणाओं को समझना? तुम महारत की ओर बढ़ रहे हो!",
            "ऑप्टिमाइज़ करते रहो, नवाचार करते रहो। कोडिंग की दुनिया तुम्हारे समाधानों का इंतजार कर रही है!",
            "तुम बुनियादी बातों से आगे निकल चुके हो, अब मजेदार चुनौतियों का समय है!",
            "जब तुम किसी को बग दिखाते हो और वह गायब हो जाता है, तो यह जादू है!",
            "तुम्हारा कोड विकसित हो रहा है, ठीक तुम्हारी तरह!",
            "उत्कृष्ट समाधान ढूंढना? यही इंटरमीडिएट का तरीका है!",
            "तुम सिर्फ कोडिंग नहीं कर रहे हो, तुम कलाकारी कर रहे हो!",
            "जितना अधिक तुम सीखते हो, उतना ही अधिक तुम्हें एहसास होता है कि तुम नहीं जानते... और यह अच्छा है!",
            "डिज़ाइन पैटर्न तुम्हारे नए सबसे अच्छे दोस्त हैं। उन्हें अपनाओ!",
            "तुम सिद्धांत और व्यवहार के बीच की खाई को पाट रहे हो। कमाल है!",
            "जब तुम्हारा कोड पहली बार में ही काम करता है, तो यह संदिग्ध होता है, है ना?",
            "तुम मशीन की तरह सोचना शुरू कर रहे हो। बीप बूप!",
            "जटिल समस्याएं? चुनौती स्वीकार है!",
            "तुम बना रहे हो, तुम सीख रहे हो, तुम जीत रहे हो!",
            "वह क्षण जब तुम अंततः रिकर्सन को समझते हो। दिमाग हिल गया!",
            "तुम्हारा कोड साफ, तेज, मजबूत हो रहा है!",
            "नए फ्रेमवर्क और लाइब्रेरीज़ की खोज करते रहो। दुनिया तुम्हारी मुट्ठी में है!",
            "तुम आधिकारिक तौर पर 'हैलो वर्ल्ड' से आगे निकल चुके हो। बधाई हो!"
        ]
    },
    "expert": {
        "en": [
            "Greetings, coding expert! Your skills are truly impressive!",
            "You're a coding wizard! Keep architecting amazing solutions!",
            "Deploying to production? Piece of cake for an expert like you!",
            "The matrix is your playground. Keep bending those bits!",
            "Your code is poetry. Keep writing masterpieces!",
            "When your microservices communicate flawlessly... in your dreams!",
            "You're not just solving problems, you're preventing them!",
            "The compiler bows before your wisdom!",
            "You speak in algorithms and dreams in data structures!",
            "Another day, another complex system tamed. Well done, expert!",
            "You're the reason the internet works. Probably.",
            "When you optimize code, even the CPU gets excited!",
            "You've transcended mere coding; you're now a code whisperer!",
            "Your algorithms are so efficient, they predict the future!",
            "Bug? What bug? I only write features!",
            "You're not just writing code, you're composing symphonies of logic!",
            "The server just sent you a thank you note. You're that good!",
            "When you explain your code, even other experts take notes.",
            "You're the legend they tell stories about in hackathons.",
            "Congratulations, you've officially broken the matrix with your skills!"
        ],
        "hi": [
            "नमस्ते, कोडिंग विशेषज्ञ! तुम्हारे कौशल वाकई प्रभावशाली हैं!",
            "तुम एक कोडिंग जादूगर हो! अद्भुत समाधानों का निर्माण करते रहो!",
            "प्रोडक्शन में डिप्लॉय करना? तुम्हारे जैसे विशेषज्ञ के लिए तो यह बच्चों का खेल है!",
            "मैट्रिक्स तुम्हारा खेल का मैदान है। उन बिट्स को मोड़ते रहो!",
            "तुम्हारा कोड कविता है। उत्कृष्ट कृतियाँ लिखते रहो!",
            "जब तुम्हारी माइक्रोसर्विसेज त्रुटिहीन रूप से संवाद करती हैं... तुम्हारे सपनों में!",
            "तुम सिर्फ समस्याओं को हल नहीं कर रहे हो, तुम उन्हें रोक रहे हो!",
            "कंपाइलर तुम्हारी बुद्धिमत्ता के सामने झुकता है!",
            "तुम एल्गोरिदम में बात करते हो और डेटा संरचनाओं में सपने देखते हो!",
            "एक और दिन, एक और जटिल प्रणाली को वश में किया। शाबाश, विशेषज्ञ!",
            "तुम ही हो जिसकी वजह से इंटरनेट काम करता है। शायद।",
            "जब तुम कोड को ऑप्टिमाइज़ करते हो, तो सीपीयू भी उत्साहित हो जाता है!",
            "तुमने सिर्फ कोडिंग से ऊपर उठकर, अब तुम कोड फुसफुसाते हो!",
            "तुम्हारे एल्गोरिदम इतने कुशल हैं कि वे भविष्य की भविष्यवाणी करते हैं!",
            "बग? कौन सा बग? मैं तो सिर्फ फीचर्स लिखता हूँ!",
            "तुम सिर्फ कोड नहीं लिख रहे हो, तुम तर्क की सिम्फनी बना रहे हो!",
            "सर्वर ने तुम्हें अभी धन्यवाद नोट भेजा है। तुम इतने अच्छे हो!",
            "जब तुम अपने कोड को समझाते हो, तो दूसरे विशेषज्ञ भी नोट्स लेते हैं।",
            "तुम वह किंवदंती हो जिसके बारे में हैकाथॉन में कहानियाँ सुनाई जाती हैं।",
            "बधाई हो, तुमने अपने कौशल से आधिकारिक तौर पर मैट्रिक्स को तोड़ दिया है!"
        ]
    }
}

# Music files (ensure you place an MP3 file in static/music/)
BACKGROUND_MUSIC = "background_music.mp3" # User needs to provide this file

def create_meme_image(text, filename="generated_meme.png"):
    """
    Generates a simple meme image with the given text using Pillow.
    The image will be saved to static/images/.
    """
    try:
        # Define image dimensions and background color
        img_width = 800
        img_height = 400
        background_color = (255, 255, 255)  # White background
        text_color = (0, 0, 0)  # Black text

        # Create a blank image
        img = Image.new('RGB', (img_width, img_height), color=background_color)
        d = ImageDraw.Draw(img)

        # --- Robust Font Loading ---
        font_size = 40
        font = ImageFont.load_default() # Start with a reliable default font

        # Try to load a specific font if it exists
        try:
            # Common font names for cross-platform compatibility or provide a specific .ttf
            # You can download 'arial.ttf' and place it in static/fonts/
            # Or try other system fonts like 'Roboto', 'OpenSans', 'LiberationSans' etc.
            # For Windows, 'arial.ttf' is usually available.
            potential_font_paths = [
                os.path.join(FONTS_DIR, 'arial.ttf'),
                # Add other potential font paths if you have them, e.g.,
                # '/usr/share/fonts/truetype/msttcorefonts/Arial.ttf', # Linux example
                # '/Library/Fonts/Arial.ttf' # macOS example
            ]

            for path in potential_font_paths:
                if os.path.exists(path):
                    font = ImageFont.truetype(path, font_size)
                    print(f"Using font: {path}")
                    break # Found a font, stop searching
            else:
                print("Warning: Specific font not found. Using default Pillow font.")

        except Exception as e:
            print(f"Error loading custom font: {e}. Falling back to default font.")
            font = ImageFont.load_default() # Ensure fallback if truetype fails for any reason
        # --- End Robust Font Loading ---

        # Calculate text position to center it (basic centering for single line)
        # For multi-line text and better wrapping, you'd need more advanced logic
        bbox = d.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (img_width - text_width) / 2
        y = (img_height - text_height) / 2

        d.text((x, y), text, fill=text_color, font=font)

        # Save the image
        image_path = os.path.join(IMAGES_DIR, filename)
        img.save(image_path)
        return url_for('static', filename=f'images/{filename}')
    except Exception as e:
        print(f"Error creating meme image: {e}")
        # Return a placeholder image URL if image generation fails
        # Make sure you have a 'placeholder.png' in static/images/
        return url_for('static', filename='images/placeholder.png')

@app.route('/')
def index():
    """Renders the main page for coding skill selection and questions."""
    return render_template('index.html', questions=CODING_QUESTIONS)

@app.route('/generate_meme', methods=['POST'])
def generate_meme():
    """
    Processes the user's coding skill and answer, generates a meme,
    and renders the meme display page.
    """
    selected_language = request.form.get('coding_language')
    user_answer = request.form.get('answer', '').strip().lower() # Convert to lowercase for case-insensitive comparison

    meme_text = "Something went wrong. Try again!"
    skill_level = "beginner" # Default skill level

    if selected_language in CODING_QUESTIONS:
        question_info = CODING_QUESTIONS[selected_language]
        correct_answer_lower = question_info['correct_answer'].lower()

        if user_answer == correct_answer_lower:
            skill_level = random.choice(["intermediate", "expert"]) # Randomly assign higher skill
            meme_text = random.choice(MEME_TEXTS[skill_level])
        else:
            skill_level = "beginner"
            meme_text = random.choice(MEME_TEXTS[skill_level])
    else:
        meme_text = "Please select a valid coding language."

    # Generate the meme image
    meme_image_url = create_meme_image(meme_text)

    return render_template('meme.html',
                           meme_text=meme_text,
                           meme_image_url=meme_image_url,
                           background_music_url=url_for('static', filename=f'music/{BACKGROUND_MUSIC}'))

@app.route('/static/music/<path:filename>')
def serve_music(filename):
    """Serves music files from the static/music directory."""
    return send_from_directory(MUSIC_DIR, filename)

# Optional: Add a favicon route to prevent 404
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(STATIC_DIR, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    # For development, you can run with debug=True
    # For production, use a production-ready WSGI server like Gunicorn or uWSGI
    app.run(debug=True)
