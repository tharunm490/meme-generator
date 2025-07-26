
# import os
# import requests
# from flask import Flask, render_template, request, send_from_directory, url_for, send_file, session
# from PIL import Image, ImageDraw, ImageFont
# import random
# import io # To handle image data in memory
# from gtts import gTTS # Import the gTTS library
# import uuid # For unique filenames for generated audio
# import re # For regular expressions to remove punctuation
# import json # For parsing JSON from API response

# # --- Global Directory Definitions and Creation ---
# STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
# IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
# MUSIC_DIR = os.path.join(STATIC_DIR, 'music')
# FONTS_DIR = os.path.join(STATIC_DIR, 'fonts')
# CORRECT_IMAGES_DIR = os.path.join(IMAGES_DIR, 'correct')

# # Ensure the static directories exist immediately when the script runs
# os.makedirs(IMAGES_DIR, exist_ok=True)
# os.makedirs(MUSIC_DIR, exist_ok=True)
# os.makedirs(FONTS_DIR, exist_ok=True)
# os.makedirs(CORRECT_IMAGES_DIR, exist_ok=True)


# app = Flask(__name__)
# app.config['PROPAGATE_EXCEPTIONS'] = True


# # --- IMPORTANT: Set a strong secret key for session management! ---
# # In production, this should be a complex, random string stored in an environment variable.
# app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_dev_key_please_change_this!")


# # # Imgflip API Configuration (No longer used for image fetching, or any text generation)
# # IMGFLIP_API_URL = "https://api.imgflip.com/get_memes"
# # IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME", "your_imgflip_username") # Replace with your Imgflip username
# # IMGFLIP_PASSWORD = os.getenv("IMGFLP_PASSWORD", "your_imgflip_password") # Replace with your Imgflip password


# # --- MAPPING FOR LOCAL IMAGES TO MEME NAMES ---
# # This helps associate a random image with a "meme type" for the captions.
# LOCAL_MEME_NAMES = {
#     "i1.jpg": "Success Kid",
#     "i2.jpg": "Distracted Boyfriend",
#     "i3.jpg": "Evil Kermit",
#     "i4.jpg": "Drake Hotline Bling",
#     "i5.jpg": "Confused Nick Young",
#     "i6.jpg": "Condescending Wonka",
#     "i7.jpg": "Is This A Pigeon?",
#     "i8.jpg": "Woman Yelling At Cat",
#     "i9.jpg": "Epic Handshake",
#     "i10.jpg": "This Is Fine Dog",
#     "i11.jpg": "One Does Not Simply",
#     "i12.jpg": "Surprised Pikachu",
#     "i13.jpg": "Grumpy Cat",
#     "i14.jpg": "Bad Luck Brian",
#     "i15.jpg": "Ancient Aliens",
#     "i16.jpg": "Doge",
#     "i17.jpg": "Boardroom Meeting Suggestion",
#     "i18.jpg": "Futurama Fry",
#     "i19.jpg": "Oprah You Get A",
#     "i20.jpg": "Satisfied Seal",
#     "i21.jpg": "Facepalm",
#     # Add more mappings for your 21 images if you add more files
# }

# # --- GENERIC CAPTIONS (Now accept both meme_name and feedback_text) ---
# # These are the primary source for the meme text and audio.
# GENERIC_CORRECT_CAPTIONS = [
#     "Looks like a perfect compile! Your '{meme_name}' energy is on point. {feedback_text}",
#     "Bug? What bug? My code just works! This '{meme_name}' is how I feel right now. {feedback_text}",
#     "This answer deserves a standing ovation from the entire dev team! You're giving off major '{meme_name}' vibes. {feedback_text}",
#     "My brain cells after solving that tricky bug are doing a '{meme_name}' dance. Perfection! {feedback_text}",
#     "When your obscure fix actually works, it's a true '{meme_name}' moment. {feedback_text}",
#     "That's a 'correct' answer, radiating pure '{meme_name}' energy. {feedback_text}",
#     "Your answer just made my compiler smile, like a happy '{meme_name}'. {feedback_text}",
#     "Feeling that 'Success Kid' vibe, because your answer is as correct as a perfectly indented Python file. {feedback_text}",
#     "This is the face of pure triumph, channeling the '{meme_name}' spirit. {feedback_text}",
#     "You just unlocked the 'Expert' badge with that answer, giving me serious '{meme_name}' satisfaction. {feedback_text}",
#     "My code is singing praises for your correct answer, just like this '{meme_name}' enjoying the moment. {feedback_text}",
#     "That's not just correct, it's '{meme_name}' correct! {feedback_text}",
# ]

# GENERIC_INCORRECT_CAPTIONS = [
#     "That's a '{meme_name}' level of wrong answer. Better luck next time, or maybe try a different IDE! {feedback_text}",
#     "My code after I 'fixed' one bug and created ten more looks just like this '{meme_name}'. Oops! {feedback_text}",
#     "That moment when your code looks right but screams 'Segmentation Fault' is a real '{meme_name}' situation. {feedback_text}",
#     "Debugging for hours only to realize you forgot a semicolon feels like this '{meme_name}'. Nope! {feedback_text}",
#     "The only thing worse than no errors is silent errors, but this '{meme_name}' screams failure. Looks like someone needs a rubber duck! {feedback_text}",
#     "My face when I realize I've been coding for 12 hours straight and my answer is still wrong, just like this '{meme_name}'. {feedback_text}",
#     "You're giving me 'Distracted Boyfriend' vibes with that answer; clearly, the correct one was over there. {feedback_text}",
#     "This is a classic 'Evil Kermit' moment for your answer. 'You should totally give the wrong answer.' And you did! {feedback_text}",
#     "My brain trying to parse that answer is having a '{meme_name}' moment. {feedback_text}",
#     "This '{meme_name}' perfectly captures my reaction to that incorrect answer. Back to the drawing board, champ! {feedback_text}",
#     "Your answer just threw a 'NullPointerException' in my brain, much like this '{meme_name}' confusion. {feedback_text}",
#     "I'm pretty sure that answer is a 'This Is Fine Dog' moment for your code. It's not fine. {feedback_text}",
# ]


# # --- CODING QUESTIONS WITH CORE FEEDBACK ---
# # These now contain 'correct_feedback' and 'incorrect_feedback' strings.
# CODING_QUESTIONS = {
#     "python": {
#         "beginner": [
#             {"question": "What is the output of 'print(type([]))' in Python?", "correct_answer": "<class 'list'>",
#              "correct_feedback": "You absolutely nailed it, programmer extraordinaire!",
#              "incorrect_feedback": "Nope, that answer was a syntax error in itself!"},
#             {"question": "Which keyword is used to define a function in Python?", "correct_answer": "def",
#              "correct_feedback": "That's a 'def'-initely correct answer!",
#              "incorrect_feedback": "Are we doing JavaScript now? Python's throwing a fit!"},
#             {"question": "What is the result of '2 + 2 * 3' in Python?", "correct_answer": "8",
#              "correct_feedback": "Order of operations for the win! Spot on, math wizard!",
#              "incorrect_feedback": "Did you forget basic arithmetic, my friend? That's a calculation error!"},
#             {"question": "How do you comment a single line in Python?", "correct_answer": "#",
#              "correct_feedback": "Hash! Python's secret code for invisibility. Well done!",
#              "incorrect_feedback": "Double slash? Are you writing C++ or something? SyntaxError!"},
#             {"question": "Which data type is used to store a sequence of characters in Python?", "correct_answer": "string",
#              "correct_feedback": "String! The majestic ruler of characters! You got it!",
#              "incorrect_feedback": "Char array? My friend, in Python, we call it a string. Not quite!"},
#             {"question": "What is the keyword to exit a loop prematurely in Python?", "correct_answer": "break",
#              "correct_feedback": "Break! Freedom from the infinite loop. You nailed that exit strategy!",
#              "incorrect_feedback": "Continue? Exit? My friend, use 'break'! Your loop is still running."},
#             {"question": "Which function is used to get input from the user in Python?", "correct_answer": "input",
#              "correct_feedback": "Input! The magical gateway to user interaction. Correct!",
#              "incorrect_feedback": "Scanf? Getline? My friend, just write 'input()'! Not that!"},
#             {"question": "What is the operator for exponentiation in Python?", "correct_answer": "**",
#              "correct_feedback": "Double star! The ultimate power symbol! Absolutely correct!",
#              "incorrect_feedback": "Caret? Pow()? Are you doing math or a magic trick? Incorrect!"},
#             {"question": "What is the output of 'len(\"hello\")' in Python?", "correct_answer": "5",
#              "correct_feedback": "Five! Easy peasy, lemon squeezy! Your counting skills are sharp. Correct!",
#              "incorrect_feedback": "Length? Size? Count? My friend, it's five! Not quite!"},
#             {"question": "Which module is used for mathematical operations in Python?", "correct_answer": "math",
#              "correct_feedback": "Math! The undisputed king of calculations! Correct!",
#              "incorrect_feedback": "Calc? Num? My friend, it's the 'math' module. Incorrect!"},
#             {"question": "How do you define an empty dictionary in Python?", "correct_answer": "{}",
#              "correct_feedback": "Curly braces! An empty dictionary, ready to be filled. Correct!",
#              "incorrect_feedback": "Empty list? Tuple? My friend, use curly braces! Not a dictionary!"},
#             {"question": "What is the output of 'print(5 > 3 and 10 < 20)'?", "correct_answer": "True",
#              "correct_feedback": "True! The undeniable power of logic! Absolutely correct!",
#              "incorrect_feedback": "False? Did you forget Boolean algebra, my friend? Incorrect!"},
#         ],
#         "expert": [
#             {"question": "Describe Python's Global Interpreter Lock (GIL) in detail.", "correct_answer": "prevents multiple native threads from executing Python bytecodes at once",
#              "correct_feedback": "Ah, the GIL! Python's single-threaded masterpiece, understood by you! Spot on!",
#              "incorrect_feedback": "The GIL? Oh, that's like, when Python locks up your entire computer, right? Incorrect!"},
#             {"question": "Explain metaclasses in Python.", "correct_answer": "classes that create classes",
#              "correct_feedback": "Metaclasses! The architects of classes themselves, mind-bending stuff! Correct!",
#              "incorrect_feedback": "Metaclasses? Did you think too advanced, or just Google it? Not quite!"},
#             {"question": "What is the purpose of 'asyncio' in Python?", "correct_answer": "asynchronous I/O",
#              "correct_feedback": "Asyncio! The magic of non-blocking operations! Absolutely correct!",
#              "incorrect_feedback": "Asynchronous? Meaning, it runs whenever it feels like it? Incorrect!"},
#             {"question": "How do you implement a custom context manager?", "correct_answer": "with statement, __enter__, __exit__",
#              "correct_feedback": "Context manager! The boss of resource handling! Correct!",
#              "incorrect_feedback": "Manager? Are you in the office? Not how it works!"},
#             {"question": "What are descriptors in Python?", "correct_answer": "objects that implement __get__, __set__, or __delete__",
#              "correct_feedback": "Descriptors! Powerful objects that control attributes! Absolutely correct!",
#              "incorrect_feedback": "Description? Are you telling a story? Incorrect!"},
#             {"question": "Explain the difference between coroutines and threads.", "correct_answer": "coroutines are cooperative, threads are preemptive",
#              "correct_feedback": "Coroutines cooperative, threads preemptive! The difference is crystal clear! Correct!",
#              "incorrect_feedback": "One waits for the other, the other stops forcefully! Not quite!"},
#             {"question": "What is monkey patching in Python?", "correct_answer": "modifying a class or module at runtime",
#              "correct_feedback": "Monkey patching! Changing code at runtime, big risk, big fun! Absolutely correct!",
#              "incorrect_feedback": "Monkey? Is this a monkey's game? Incorrect!"},
#             {"question": "How does Python handle memory management?", "correct_answer": "reference counting and garbage collection",
#              "correct_feedback": "Reference counting and garbage collection! Python's sophisticated cleaning campaign! Correct!",
#              "incorrect_feedback": "Manual memory management? Memory leak happened!"},
#             {"question": "What are abstract base classes (ABCs) and why are they used?", "correct_answer": "define interfaces, prevent instantiation",
#              "correct_feedback": "ABCs! They define interfaces, objects are not created! Absolutely correct!",
#              "incorrect_feedback": "Abstract? Meaning, only for thinking? Incorrect!"},
#             {"question": "Discuss the implications of mutable default arguments in Python functions.", "correct_answer": "shared state across calls",
#              "correct_feedback": "Mutable default arguments! The danger of shared state, beware! Correct!",
#              "incorrect_feedback": "Default argument changed? Not my fault, it's your fault! Incorrect!"},
#         ]
#     },
#     "java": {
#         "beginner": [
#             {"question": "Which keyword is used to define a class in Java?", "correct_answer": "class",
#              "correct_feedback": "'Class'! The sacred keyword for Java class definition! You got it!",
#              "incorrect_feedback": "'Struct'? 'Module'? It's 'class', my friend! Incorrect!"},
#             {"question": "What is the entry point method for a Java application?", "correct_answer": "main",
#              "correct_feedback": "'Main' method! Where everything begins! Correct!",
#              "incorrect_feedback": "'Start'? 'Run'? My friend, write 'public static void main'! Not quite!"},
#             {"question": "Which keyword is used for inheritance in Java?", "correct_answer": "extends",
#              "correct_feedback": "'Extends'! The way to inherit properties from a parent! Absolutely correct!",
#              "incorrect_feedback": "'Inherit'? 'Derive'? It's 'extends', my friend! Incorrect!"},
#             {"question": "What is the default value of a boolean variable in Java?", "correct_answer": "false",
#              "correct_feedback": "False! Java's default truth! Correct!",
#              "incorrect_feedback": "True? Null? My friend, boolean defaults to false! Not quite!"},
#             {"question": "Which access modifier means visible only within the class?", "correct_answer": "private",
#              "correct_feedback": "'Private'! Java's personal space! Absolutely correct!",
#              "incorrect_feedback": "'Public'? 'Protected'? Keep it 'private'! Incorrect!"},
#             {"question": "What is the keyword to create an object in Java?", "correct_answer": "new",
#              "correct_feedback": "'New'! A new object, new hopes! Correct!",
#              "incorrect_feedback": "'Create'? 'Make'? My friend, it's the 'new' keyword! Not quite!"},
#             {"question": "Which loop executes at least once in Java?", "correct_answer": "do-while",
#              "correct_feedback": "'Do-while'! First action, then condition! Absolutely correct!",
#              "incorrect_feedback": "'While'? 'For'? My friend, 'do-while' will run at least once! Incorrect!"},
#             {"question": "What is the superclass of all classes in Java?", "correct_answer": "Object",
#              "correct_feedback": "'Object'! The parent of all, the superclass of everything! Correct!",
#              "incorrect_feedback": "'Class'? 'Main'? My friend, it's the 'Object' class! Not quite!"},
#             {"question": "Which keyword is used to handle exceptions in Java?", "correct_answer": "try",
#              "correct_feedback": "'Try'! The first step to catching errors! Absolutely correct!",
#              "incorrect_feedback": "'Catch'? 'Throw'? My friend, start with 'try'! Incorrect!"},
#             {"question": "What is the operator for logical AND in Java?", "correct_answer": "&&",
#              "correct_feedback": "Double ampersand! When both are true! Correct!",
#              "incorrect_feedback": "'And'? Single ampersand? My friend, it's double ampersand! Not quite!"},
#         ],
#         "expert": [
#             {"question": "Explain the Java Memory Model (JMM).", "correct_answer": "defines how threads interact with memory",
#              "correct_feedback": "Java Memory Model! The JMM defines how threads interact with memory! Absolutely correct!",
#              "incorrect_feedback": "JMM? Jalebi Murabba Mithai? Incorrect!"},
#             {"question": "What are Java's concurrency utilities and how are they used?", "correct_answer": "ExecutorService, Future, Callable, locks",
#              "correct_feedback": "ExecutorService, Future, Callable, locks! Concurrency utilities, Java's parallel processing game! Correct!",
#              "incorrect_feedback": "Threads? Race conditions? Not how you use concurrency!"},
#             {"question": "Describe the difference between 'synchronized' keyword and 'ReentrantLock'.", "correct_answer": "synchronized is implicit, ReentrantLock is explicit and more flexible",
#              "correct_feedback": "Synchronized is implicit, ReentrantLock is explicit and more flexible! Absolutely correct!",
#              "incorrect_feedback": "Lock? Where's the key? Incorrect!"},
#             {"question": "What is reflection in Java and its use cases?", "correct_answer": "examining and modifying classes at runtime",
#              "correct_feedback": "Reflection! Examining and modifying classes at runtime! Correct!",
#              "incorrect_feedback": "Reflection? Is it showing my face? Not quite!"},
#             {"question": "Explain the concept of custom annotations in Java.", "correct_answer": "metadata for code",
#              "correct_feedback": "Metadata for code! Custom Annotations! Absolutely correct!",
#              "incorrect_feedback": "Notes? Comments? Incorrect!"},
#             {"question": "How do you implement a custom ClassLoader in Java?", "correct_answer": "extend ClassLoader, override findClass",
#              "correct_feedback": "Extend ClassLoader, override findClass! Custom ClassLoader! Correct!",
#              "incorrect_feedback": "Class not found? My friend, build a ClassLoader! Not quite!"},
#             {"question": "Discuss the implications of using Java Native Interface (JNI).", "correct_answer": "interoperability with native code, platform dependent",
#              "correct_feedback": "Interoperability with native code, platform dependent! JNI! Absolutely correct!",
#              "incorrect_feedback": "Native code? My friend, it will become platform dependent! Incorrect!"},
#             {"question": "What are lambda expressions and functional interfaces in Java 8?", "correct_answer": "concise anonymous functions, single abstract method",
#              "correct_feedback": "Concise anonymous functions, single abstract method! Lambdas! Functional interfaces! Correct!",
#              "incorrect_feedback": "Anonymous class? My friend, use lambda! Not quite!"},
#             {"question": "Explain the principles of SOLID design in Java.", "correct_answer": "Single responsibility, Open/Closed, Liskov substitution, Interface segregation, Dependency inversion",
#              "correct_feedback": "Single responsibility, Open/Closed, Liskov substitution, Interface segregation, Dependency inversion! SOLID principles! Absolutely correct!",
#              "incorrect_feedback": "Code spaghetti? Follow SOLID principles! Incorrect!"},
#             {"question": "Describe the various garbage collection algorithms in JVM.", "correct_answer": "Serial, Parallel, CMS, G1, ZGC",
#              "correct_feedback": "Serial, Parallel, CMS, G1, ZGC! GC algorithms! Correct!",
#              "incorrect_feedback": "Memory leak? Read GC algorithms! Not quite!"},
#         ]
#     },
#     "cpp": {
#         "beginner": [
#             {"question": "What is the operator used for dynamic memory allocation in C++?", "correct_answer": "new",
#              "correct_feedback": "'New'! The sacred operator for dynamic memory allocation in C++! You got it!",
#              "incorrect_feedback": "'Malloc'? 'Alloc'? It's 'new', my friend! Incorrect!"},
#             {"question": "Which header file is used for input/output operations in C++?", "correct_answer": "iostream",
#              "correct_feedback": "'Iostream'! The heart of C++ input-output! Correct!",
#              "incorrect_feedback": "'Stdio.h'? 'Conio.h'? It's 'iostream', my friend! Not quite!"},
#             {"question": "What does 'cout' stand for in C++?", "correct_answer": "console output",
#              "correct_feedback": "Console output! 'Cout' is C++'s style for printing! Absolutely correct!",
#              "incorrect_feedback": "'See-out'? No, console output! Incorrect!"},
#             {"question": "Which symbol is used to indicate a pointer in C++?", "correct_answer": "*",
#              "correct_feedback": "Star! The symbol of an address! Correct!",
#              "incorrect_feedback": "Ampersand? Hash? My friend, use a star! Not quite!"},
#             {"question": "What is the keyword for defining a constant in C++?", "correct_answer": "const",
#              "correct_feedback": "'Const'! The keyword for defining constants! Absolutely correct!",
#              "incorrect_feedback": "'Var'? 'Let'? It's 'const', my friend! Incorrect!"},
#             {"question": "Which operator is used for dereferencing a pointer?", "correct_answer": "*",
#              "correct_feedback": "Star! The way to grab the value! Correct!",
#              "incorrect_feedback": "Are you taking the address? My friend, if you want the value, use a star! Not quite!"},
#             {"question": "What is the standard namespace in C++?", "correct_answer": "std",
#              "correct_feedback": "'Std'! The home of the standard library! Absolutely correct!",
#              "incorrect_feedback": "My_namespace? My friend, it's 'std'! Incorrect!"},
#             {"question": "Which loop is guaranteed to execute at least once in C++?", "correct_answer": "do-while",
#              "correct_feedback": "'Do-while'! First action, then condition! Correct!",
#              "incorrect_feedback": "'While'? 'For'? My friend, 'do-while' will run at least once! Not quite!"},
#             {"question": "What is the purpose of 'virtual' keyword in a function?", "correct_answer": "polymorphism",
#              "correct_feedback": "Polymorphism! The 'virtual' keyword is C++'s secret to runtime polymorphism! Absolutely correct!",
#              "incorrect_feedback": "'Abstract'? 'Override'? No, my friend, this is for polymorphism! Incorrect!"},
#             {"question": "What is the difference between 'nullptr' and 'NULL' in C++?", "correct_answer": "nullptr is type-safe, NULL is macro",
#              "correct_feedback": "'Nullptr' is type-safe, 'NULL' is a macro! Correct!",
#              "incorrect_feedback": "Are they the same? My friend, one is type-safe, the other a macro! Not quite!"},
#         ],
#         "intermediate": [
#             {"question": "Explain the difference between 'pass by value' and 'pass by reference'.", "correct_answer": "value copies, reference uses original",
#              "correct_feedback": "Value copies, reference uses original! Absolutely correct!",
#              "incorrect_feedback": "Pass by... what? Incorrect!"},
#             {"question": "What is a destructor in C++?", "correct_answer": "special member function called when object is destroyed",
#              "correct_feedback": "Special member function called when object is destroyed! Correct!",
#              "incorrect_feedback": "Garbage collector? No automatic cleanup, my friend! Not quite!"},
#             {"question": "What is operator overloading?", "correct_answer": "redefining operators for custom types",
#              "correct_feedback": "Redefining operators for custom types! Absolutely correct!",
#              "incorrect_feedback": "Operator... what now? Incorrect!"},
#             {"question": "Describe the concept of 'RAII' in C++.", "correct_answer": "Resource Acquisition Is Initialization",
#              "correct_feedback": "Resource Acquisition Is Initialization! Correct!",
#              "incorrect_feedback": "Rai-rai? Not quite!"},
#             {"question": "What is the difference between 'struct' and 'class' in C++?", "correct_answer": "struct default public, class default private",
#              "correct_feedback": "Struct default public, class default private! Absolutely correct!",
#              "incorrect_feedback": "Are they the same? Incorrect!"},
#             {"question": "What is a copy constructor in C++?", "correct_answer": "constructor that creates object by copying another object",
#              "correct_feedback": "A copy constructor creates an object by copying another! Correct!",
#              "incorrect_feedback": "Not quite a copy constructor! That's not how we duplicate objects."},
#             {"question": "Explain the concept of 'virtual functions' in C++.", "correct_answer": "functions that can be overridden in derived classes and enable runtime polymorphism",
#              "correct_feedback": "Virtual functions enable runtime polymorphism! Absolutely correct!",
#              "incorrect_feedback": "Virtual functions are not just regular functions! That's incorrect."},
#             {"question": "What is the purpose of 'explicit' keyword in C++ constructors?", "correct_answer": "prevents implicit conversions",
#              "correct_feedback": "Explicit prevents implicit conversions! Correct, keep those conversions clear!",
#              "incorrect_feedback": "Explicit doesn't force conversions! That's incorrect, it does the opposite."},
#             {"question": "What is a 'friend function' in C++?", "correct_answer": "non-member function that can access private and protected members of a class",
#              "correct_feedback": "A friend function can access private members! Absolutely correct, they're like code besties!",
#              "incorrect_feedback": "Friend functions aren't just any function! That's incorrect, they have special access."},
#             {"question": "Explain 'move semantics' (rvalue references) in C++11.", "correct_answer": "efficient transfer of resources",
#              "correct_feedback": "Move semantics is about efficient resource transfer! Correct, no unnecessary copying here!",
#              "incorrect_feedback": "Move semantics isn't just copying! That's incorrect, it's about ownership transfer."},
#         ],
#         "expert": [
#             {"question": "Describe the C++ Standard Template Library (STL) components.", "correct_answer": "containers, algorithms, iterators, function objects",
#              "correct_feedback": "STL components: containers, algorithms, iterators, function objects! Absolutely correct!",
#              "incorrect_feedback": "STL is more than just a library! That's incorrect, you missed some key components."},
#             {"question": "Explain the 'Rule of Three/Five/Zero' in C++.", "correct_answer": "copy constructor, copy assignment, destructor",
#              "correct_feedback": "Rule of Three/Five/Zero covers copy constructor, copy assignment, and destructor! Correct!",
#              "incorrect_feedback": "The Rule of Three/Five/Zero is not just about constructors! That's incorrect."},
#             {"question": "What is SFINAE (Substitution Failure Is Not An Error) in C++ templates?", "correct_answer": "template metaprogramming technique",
#              "correct_feedback": "SFINAE is a template metaprogramming technique! Absolutely correct, when failure is a feature!",
#              "incorrect_feedback": "SFINAE is not an error, but your answer is! That's incorrect."},
#             {"question": "Discuss the implications of virtual inheritance.", "correct_answer": "solves diamond problem",
#              "correct_feedback": "Virtual inheritance solves the diamond problem! Correct, avoiding multiple base class subobjects!",
#              "incorrect_feedback": "Virtual inheritance isn't just for fun! That's incorrect, it has a specific problem it solves."},
#             {"question": "Explain move semantics (rvalue references) in C++11.", "correct_answer": "efficient transfer of resources",
#              "correct_feedback": "Move semantics is about efficient resource transfer! Absolutely correct, no unnecessary copying here!",
#              "incorrect_feedback": "Move semantics isn't just copying! That's incorrect, it's about ownership transfer."},
#             {"question": "What is a 'perfect forwarding' in C++?", "correct_answer": "passing arguments while preserving their value category (lvalue/rvalue)",
#              "correct_feedback": "Perfect forwarding preserves value categories! Correct, keeping those lvalues and rvalues intact!",
#              "incorrect_feedback": "Perfect forwarding isn't just about passing arguments! That's incorrect, it's more nuanced."},
#             {"question": "Describe the concept of 'CRTP' (Curiously Recurring Template Pattern).", "correct_answer": "class derives from a template specialization of itself",
#              "correct_feedback": "CRTP is when a class derives from a template specialization of itself! Absolutely correct, a curious pattern indeed!",
#              "incorrect_feedback": "CRTP is not just a random template! That's incorrect, it's a specific design pattern."},
#             {"question": "What is the purpose of 'placement new' in C++?", "correct_answer": "constructs object at a pre-allocated memory location",
#              "correct_feedback": "Placement new constructs objects at pre-allocated memory! Correct, fine-grained memory control!",
#              "incorrect_feedback": "Placement new isn't regular new! That's incorrect, it doesn't allocate memory."},
#             {"question": "Explain the 'std::variant' and 'std::visit' in C++17.", "correct_answer": "type-safe union, apply visitor to variant",
#              "correct_feedback": "Std::variant is a type-safe union, and std::visit applies a visitor! Absolutely correct, modern C++ for the win!",
#              "incorrect_feedback": "Std::variant isn't just any union! That's incorrect, it's type-safe and powerful."},
#             {"question": "What is the difference between 'std::async' and 'std::thread'?", "correct_answer": "std::async manages future, std::thread manages raw thread",
#              "correct_feedback": "Std::async manages a future, std::thread manages a raw thread! Correct, knowing your concurrency tools!",
#              "incorrect_feedback": "Std::async and std::thread are not the same! That's incorrect, they have different management approaches."},
#         ]
#     }
# }


# # Temporary storage for generated audio streams (in a real app, use a proper cache/database)
# generated_audio_streams = {}

# def generate_audio_from_text(text, lang='en'):
#     """
#     Generates an MP3 audio stream from text using gTTS and returns a BytesIO object.
#     Removes common punctuation to ensure gTTS speaks clearly without pauses.
#     """
#     try:
#         # Remove common punctuation marks
#         text_without_punctuation = re.sub(r'[.,;!?"\'-]', '', text)
#         # Replace multiple spaces with a single space
#         text_without_punctuation = re.sub(r'\s+', ' ', text_without_punctuation).strip()

#         # Ensure language is English
#         tts = gTTS(text=text_without_punctuation, lang=lang, slow=False)
#         audio_stream = io.BytesIO()
#         tts.write_to_fp(audio_stream)
#         audio_stream.seek(0) # Rewind to the beginning of the stream
#         return audio_stream
#     except Exception as e:
#         print(f"Error generating audio from text: {e}")
#         return None

# @app.route('/audio/<audio_id>')
# def serve_generated_audio(audio_id):
#     """
#     Serves a dynamically generated audio file from in-memory storage.
#     """
#     audio_stream = generated_audio_streams.get(audio_id)
#     if audio_stream:
#         return send_file(audio_stream, mimetype='audio/mpeg', as_attachment=False)
#     else:
#         return "Audio not found or expired.", 404

# def get_random_local_image_info():
#     """
#     Selects a random image from the static/images/correct/ folder (i1.jpg to i21.jpg)
#     and returns its filename and a corresponding meme name.
#     """
#     random_image_num = random.randint(1, 21)
#     image_filename = f"i{random_image_num}.jpg"
#     local_image_url = url_for('static', filename=f'images/correct/{image_filename}')
    
#     # Get the meme name from the mapping, default to a generic name if not found
#     meme_name = LOCAL_MEME_NAMES.get(image_filename, f"Generic Meme {random_image_num}")

#     print(f"DEBUG: Image fetched from local fallback: {image_filename} (Meme Name: {meme_name})")
#     return {
#         "id": "local_fallback", # Special ID to indicate local fallback
#         "filename": image_filename, # Store filename to get its meme name
#         "url": local_image_url,
#         "name": meme_name,
#         "box_count": 1 # Assume 1 text box for local images for simplicity
#     }

# def create_meme_image(text, meme_template_info, filename="generated_meme.png"):
#     """
#     Generates a meme image by downloading an Imgflip template (or using fallback)
#     and overlaying the given text using Pillow.
#     The image will be saved to static/images/.
#     """
#     try:
#         image_url = meme_template_info.get('url')
#         img = None

#         if image_url and image_url.startswith('/static/'): # It's a local static file
#             image_path = os.path.join(app.root_path, image_url.lstrip('/'))
#             if not os.path.exists(image_path):
#                 print(f"Error: Local fallback image not found at {image_path}. Creating blank image.")
#                 img = Image.new('RGB', (250, 250), color = (73, 109, 137)) # Fixed size: 250x250
#                 d = ImageDraw.Draw(img)
#                 fnt = ImageFont.load_default()
#                 d.text((10,10), "Image Missing!", font=fnt, fill=(255,255,255))
#             else:
#                 img = Image.open(image_path).convert("RGB")
#         else: # Fallback for unexpected image_url, or if it was from Imgflip (which we're now avoiding)
#             print("Unexpected image URL or no URL provided. Creating blank image.")
#             img = Image.new('RGB', (250, 250), color = (73, 109, 137)) # Fixed size: 250x250
#             d = ImageDraw.Draw(img)
#             fnt = ImageFont.load_default()
#             d.text((10,10), "Image Load Error!", font=fnt, fill=(255,255,255))


#         # Define text color
#         text_color = (0, 0, 0)  # Black text

#         d = ImageDraw.Draw(img)

#         # --- Image Resizing to 250x250 ---
#         img_width = 250
#         img_height = 250
#         img = img.resize((img_width, img_height), Image.LANCZOS) # Use LANCZOS for high-quality downsampling

#         # --- Robust Font Loading ---
#         font_size = int(img.height * 0.07) # Adjust font size relative to image height
#         font = ImageFont.load_default() # Start with a reliable default font

#         try:
#             potential_font_paths = [
#                 os.path.join(FONTS_DIR, 'arial.ttf'),
#                 # Add other potential font paths if you have them, e.g.,
#                 # '/usr/share/fonts/truetype/msttcorefonts/Arial.ttf', # Linux example
#                 # '/Library/Fonts/Arial.ttf' # macOS example
#             ]

#             for path in potential_font_paths:
#                 if os.path.exists(path):
#                     font = ImageFont.truetype(path, font_size)
#                     print(f"Using font: {path}")
#                     break
#             else:
#                 print("Warning: Specific font not found. Using default Pillow font.")

#         except Exception as e:
#             print(f"Error loading custom font: {e}. Falling back to default font.")
#             font = ImageFont.load_default()
#         # --- End Robust Font Loading ---

#         # Simple text wrapping and positioning for better readability on various templates
#         lines = []
#         words = text.split()
#         current_line = []
#         for word in words:
#             test_line = " ".join(current_line + [word])
#             # Use textlength for accurate width calculation
#             bbox = d.textbbox((0, 0), test_line, font=font)
#             test_width = bbox[2] - bbox[0]
#             if test_width < img.width * 0.9: # Keep text within 90% of image width
#                 current_line.append(word)
#             else:
#                 lines.append(" ".join(current_line))
#                 current_line = [word]
#         lines.append(" ".join(current_line))

#         # Calculate total text height to center it vertically at the top
#         total_text_height = sum(d.textbbox((0, 0), line, font=font)[3] - d.textbbox((0, 0), line, font=font)[1] for line in lines)
        
#         # Position text towards the top, with some padding
#         y_start_pos = img.height * 0.05 # 5% from the top
#         y_text = y_start_pos

#         for line in lines:
#             # Calculate width of the current line
#             bbox = d.textbbox((0, 0), line, font=font)
#             line_width = bbox[2] - bbox[0]
#             x_text = (img.width - line_width) / 2 # Center horizontally
#             d.text((x_text, y_text), line, fill=text_color, font=font)
#             y_text += (bbox[3] - bbox[1]) # Move to next line

#         # Save the image to a BytesIO object for immediate use and then save to disk
#         img_byte_arr = io.BytesIO()
#         img.save(img_byte_arr, format='PNG')
#         img_byte_arr.seek(0) # Rewind to beginning

#         # Save to disk for static serving in case of direct URL access or debugging
#         image_path_on_disk = os.path.join(IMAGES_DIR, filename)
#         with open(image_path_on_disk, 'wb') as f:
#             f.write(img_byte_arr.getvalue())
        
#         return url_for('static', filename=f'images/{filename}')
#     except Exception as e:
#         print(f"Error creating meme image: {e}")
#         # Fallback to a generic blank image if all else fails
#         return url_for('static', filename='images/placeholder.png') # Ensure you have a placeholder.png in static/images/

# @app.route('/')
# def vikasa_home():
#     """Renders the new homepage."""
#     return render_template('vikasa_home.html')

# @app.route('/quiz')
# def index():
#     """Renders the main page for coding skill selection and questions."""
#     return render_template('index.html', questions=CODING_QUESTIONS)

# @app.route('/generate_meme', methods=['POST'])
# async def generate_meme():
#     """
#     Processes the user's coding skill and answer, generates a meme,
#     and renders the meme display page.
#     """
#     selected_language = request.form.get('coding_language')
#     self_assessed_skill_level = request.form.get('skill_level')
#     user_answer = request.form.get('answer', '').strip().lower() # Get the user's raw answer
#     question_text = request.form.get('question_text', '').strip() # Get the question text from the form

#     selected_meme_text = "Something went wrong. Try again!"
#     final_skill_level = "beginner"
#     is_answer_correct = False
#     core_feedback_text = "" # Initialize core feedback text

#     # Get the specific question object to determine correctness and core feedback
#     current_question_obj = None
#     if selected_language in CODING_QUESTIONS and self_assessed_skill_level in CODING_QUESTIONS[selected_language]:
#         questions_for_level = CODING_QUESTIONS[selected_language][self_assessed_skill_level]
#         for q_obj in questions_for_level:
#             if q_obj['question'].strip().lower() == question_text.lower():
#                 current_question_obj = q_obj
#                 break

#     correct_answer_for_question = ""
#     if current_question_obj:
#         correct_answer_for_question = current_question_obj['correct_answer'].lower()
#         if user_answer == correct_answer_for_question:
#             is_answer_correct = True
#             final_skill_level = self_assessed_skill_level
#             core_feedback_text = current_question_obj.get('correct_feedback', "That's correct!")
#         else:
#             is_answer_correct = False
#             final_skill_level = "beginner" # Incorrect answer or unmatched question defaults to beginner
#             core_feedback_text = current_question_obj.get('incorrect_feedback', "That's incorrect!")
#     else:
#         # Fallback if question not found (shouldn't happen with proper frontend)
#         is_answer_correct = False
#         final_skill_level = "beginner"
#         core_feedback_text = "Oops! Couldn't find that question, but your coding journey continues!"


#     # --- Step 1: Get a random local image and its meme name ---
#     meme_template_info = get_random_local_image_info()
#     meme_image_url = meme_template_info['url']
#     meme_name = meme_template_info['name'] # This is crucial for the caption formatting

#     # --- Step 2: Generate the combined text from generic captions and dictionary feedback ---
#     if is_answer_correct:
#         # Select a random correct generic caption and format it with both meme_name and core_feedback_text
#         selected_meme_text = random.choice(GENERIC_CORRECT_CAPTIONS).format(
#             meme_name=meme_name,
#             feedback_text=core_feedback_text
#         )
#     else:
#         # Select a random incorrect generic caption and format it with both meme_name and core_feedback_text
#         selected_meme_text = random.choice(GENERIC_INCORRECT_CAPTIONS).format(
#             meme_name=meme_name,
#             feedback_text=core_feedback_text
#         )

#     # --- Step 3: Create the meme image with the selected text ---
#     meme_filename = f"generated_meme_{uuid.uuid4()}.png"
#     final_meme_image_url = create_meme_image(selected_meme_text, meme_template_info, meme_filename)

#     # --- Step 4: Generate audio from the selected (combined) text ---
#     audio_stream = generate_audio_from_text(selected_meme_text, lang='en')
#     generated_audio_id = str(uuid.uuid4())
#     generated_audio_streams[generated_audio_id] = audio_stream
#     generated_audio_url = url_for('serve_generated_audio', audio_id=generated_audio_id)

#     return render_template('meme.html',
#                            meme_text=selected_meme_text,
#                            meme_image_url=final_meme_image_url,
#                            background_music_url=generated_audio_url,
#                            skill_level_display=final_skill_level.capitalize())

# @app.route('/static/music/<path:filename>')
# def serve_music(filename):
#     """Serves music files from the static/music directory."""
#     return send_from_directory(MUSIC_DIR, filename)

# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(STATIC_DIR, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# if __name__ == '__main__':
#     app.run(debug=True)
import os
import requests
from flask import Flask, render_template, request, send_from_directory, url_for, send_file, session
from PIL import Image, ImageDraw, ImageFont
import random
import io # To handle image data in memory
from gtts import gTTS # Import the gTTS library
import uuid # For unique filenames for generated audio
import re # For regular expressions to remove punctuation
import json # For parsing JSON from API response

# --- Global Directory Definitions and Creation ---
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
MUSIC_DIR = os.path.join(STATIC_DIR, 'music')
FONTS_DIR = os.path.join(STATIC_DIR, 'fonts')
CORRECT_IMAGES_DIR = os.path.join(IMAGES_DIR, 'correct')

# Ensure the static directories exist immediately when the script runs
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(CORRECT_IMAGES_DIR, exist_ok=True)


app = Flask(__name__)

# --- IMPORTANT: Set a strong secret key for session management! ---
# In production, this should be a complex, random string stored in an environment variable.
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_dev_key_please_change_this!")


# Imgflip API Configuration (No longer used for image fetching, or any text generation)
IMGFLIP_API_URL = "https://api.imgflip.com/get_memes"
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME", "your_imgflip_username") # Replace with your Imgflip username
IMGFLIP_PASSWORD = os.getenv("IMGFLP_PASSWORD", "your_imgflip_password") # Replace with your Imgflip password


# --- MAPPING FOR LOCAL IMAGES TO MEME NAMES ---
# This helps associate a random image with a "meme type" for the captions.
LOCAL_MEME_NAMES = {
    "i1.jpg": "Success Kid",
    "i2.jpg": "Distracted Boyfriend",
    "i3.jpg": "Evil Kermit",
    "i4.jpg": "Drake Hotline Bling",
    "i5.jpg": "Confused Nick Young",
    "i6.jpg": "Condescending Wonka",
    "i7.jpg": "Is This A Pigeon?",
    "i8.jpg": "Woman Yelling At Cat",
    "i9.jpg": "Epic Handshake",
    "i10.jpg": "This Is Fine Dog",
    "i11.jpg": "One Does Not Simply",
    "i12.jpg": "Surprised Pikachu",
    "i13.jpg": "Grumpy Cat",
    "i14.jpg": "Bad Luck Brian",
    "i15.jpg": "Ancient Aliens",
    "i16.jpg": "Doge",
    "i17.jpg": "Boardroom Meeting Suggestion",
    "i18.jpg": "Futurama Fry",
    "i19.jpg": "Oprah You Get A",
    "i20.jpg": "Satisfied Seal",
    "i21.jpg": "Facepalm",
    # Add more mappings for your 21 images if you add more files
}

# --- GENERIC CAPTIONS (Now accept both meme_name and feedback_text) ---
# These are the primary source for the meme text and audio.
GENERIC_CORRECT_CAPTIONS = [
    "Looks like a perfect compile! Your '{meme_name}' energy is on point. {feedback_text}",
    "Bug? What bug? My code just works! This '{meme_name}' is how I feel right now. {feedback_text}",
    "This answer deserves a standing ovation from the entire dev team! You're giving off major '{meme_name}' vibes. {feedback_text}",
    "My brain cells after solving that tricky bug are doing a '{meme_name}' dance. Perfection! {feedback_text}",
    "When your obscure fix actually works, it's a true '{meme_name}' moment. {feedback_text}",
    "That's a 'correct' answer, radiating pure '{meme_name}' energy. {feedback_text}",
    "Your answer just made my compiler smile, like a happy '{meme_name}'. {feedback_text}",
    "Feeling that 'Success Kid' vibe, because your answer is as correct as a perfectly indented Python file. {feedback_text}",
    "This is the face of pure triumph, channeling the '{meme_name}' spirit. {feedback_text}",
    "You just unlocked the 'Expert' badge with that answer, giving me serious '{meme_name}' satisfaction. {feedback_text}",
    "My code is singing praises for your correct answer, just like this '{meme_name}' enjoying the moment. {feedback_text}",
    "That's not just correct, it's '{meme_name}' correct! {feedback_text}",
]

GENERIC_INCORRECT_CAPTIONS = [
    "That's a '{meme_name}' level of wrong answer. Better luck next time, or maybe try a different IDE! {feedback_text}",
    "My code after I 'fixed' one bug and created ten more looks just like this '{meme_name}'. Oops! {feedback_text}",
    "That moment when your code looks right but screams 'Segmentation Fault' is a real '{meme_name}' situation. {feedback_text}",
    "Debugging for hours only to realize you forgot a semicolon feels like this '{meme_name}'. Nope! {feedback_text}",
    "The only thing worse than no errors is silent errors, but this '{meme_name}' screams failure. Looks like someone needs a rubber duck! {feedback_text}",
    "My face when I realize I've been coding for 12 hours straight and my answer is still wrong, just like this '{meme_name}'. {feedback_text}",
    "You're giving me 'Distracted Boyfriend' vibes with that answer; clearly, the correct one was over there. {feedback_text}",
    "This is a classic 'Evil Kermit' moment for your answer. 'You should totally give the wrong answer.' And you did! {feedback_text}",
    "My brain trying to parse that answer is having a '{meme_name}' moment. {feedback_text}",
    "This '{meme_name}' perfectly captures my reaction to that incorrect answer. Back to the drawing board, champ! {feedback_text}",
    "Your answer just threw a 'NullPointerException' in my brain, much like this '{meme_name}' confusion. {feedback_text}",
    "I'm pretty sure that answer is a 'This Is Fine Dog' moment for your code. It's not fine. {feedback_text}",
]


# --- CODING QUESTIONS WITH CORE FEEDBACK ---
# These now contain 'correct_feedback' and 'incorrect_feedback' strings.
CODING_QUESTIONS = {
    "python": {
        "beginner": [
            {"question": "What is the output of 'print(type([]))' in Python?", "correct_answer": "<class 'list'>",
             "correct_feedback": "You absolutely nailed it, programmer extraordinaire!",
             "incorrect_feedback": "Nope, that answer was a syntax error in itself!"},
            {"question": "Which keyword is used to define a function in Python?", "correct_answer": "def",
             "correct_feedback": "That's a 'def'-initely correct answer!",
             "incorrect_feedback": "Are we doing JavaScript now? Python's throwing a fit!"},
            {"question": "What is the result of '2 + 2 * 3' in Python?", "correct_answer": "8",
             "correct_feedback": "Order of operations for the win! Spot on, math wizard!",
             "incorrect_feedback": "Did you forget basic arithmetic, my friend? That's a calculation error!"},
            {"question": "How do you comment a single line in Python?", "correct_answer": "#",
             "correct_feedback": "Hash! Python's secret code for invisibility. Well done!",
             "incorrect_feedback": "Double slash? Are you writing C++ or something? SyntaxError!"},
            {"question": "Which data type is used to store a sequence of characters in Python?", "correct_answer": "string",
             "correct_feedback": "String! The majestic ruler of characters! You got it!",
             "incorrect_feedback": "Char array? My friend, in Python, we call it a string. Not quite!"},
            {"question": "What is the keyword to exit a loop prematurely in Python?", "correct_answer": "break",
             "correct_feedback": "Break! Freedom from the infinite loop. You nailed that exit strategy!",
             "incorrect_feedback": "Continue? Exit? My friend, use 'break'! Your loop is still running."},
            {"question": "Which function is used to get input from the user in Python?", "correct_answer": "input",
             "correct_feedback": "Input! The magical gateway to user interaction. Correct!",
             "incorrect_feedback": "Scanf? Getline? My friend, just write 'input()'! Not that!"},
            {"question": "What is the operator for exponentiation in Python?", "correct_answer": "**",
             "correct_feedback": "Double star! The ultimate power symbol! Absolutely correct!",
             "incorrect_feedback": "Caret? Pow()? Are you doing math or a magic trick? Incorrect!"},
            {"question": "What is the output of 'len(\"hello\")' in Python?", "correct_answer": "5",
             "correct_feedback": "Five! Easy peasy, lemon squeezy! Your counting skills are sharp. Correct!",
             "incorrect_feedback": "Length? Size? Count? My friend, it's five! Not quite!"},
            {"question": "Which module is used for mathematical operations in Python?", "correct_answer": "math",
             "correct_feedback": "Math! The undisputed king of calculations! Correct!",
             "incorrect_feedback": "Calc? Num? My friend, it's the 'math' module. Incorrect!"},
            {"question": "How do you define an empty dictionary in Python?", "correct_answer": "{}",
             "correct_feedback": "Curly braces! An empty dictionary, ready to be filled. Correct!",
             "incorrect_feedback": "Empty list? Tuple? My friend, use curly braces! Not a dictionary!"},
            {"question": "What is the output of 'print(5 > 3 and 10 < 20)'?", "correct_answer": "True",
             "correct_feedback": "True! The undeniable power of logic! Absolutely correct!",
             "incorrect_feedback": "False? Did you forget Boolean algebra, my friend? Incorrect!"},
        ],
        "expert": [
            {"question": "Describe Python's Global Interpreter Lock (GIL) in detail.", "correct_answer": "prevents multiple native threads from executing Python bytecodes at once",
             "correct_feedback": "Ah, the GIL! Python's single-threaded masterpiece, understood by you! Spot on!",
             "incorrect_feedback": "The GIL? Oh, that's like, when Python locks up your entire computer, right? Incorrect!"},
            {"question": "Explain metaclasses in Python.", "correct_answer": "classes that create classes",
             "correct_feedback": "Metaclasses! The architects of classes themselves, mind-bending stuff! Correct!",
             "incorrect_feedback": "Metaclasses? Did you think too advanced, or just Google it? Not quite!"},
            {"question": "What is the purpose of 'asyncio' in Python?", "correct_answer": "asynchronous I/O",
             "correct_feedback": "Asyncio! The magic of non-blocking operations! Absolutely correct!",
             "incorrect_feedback": "Asynchronous? Meaning, it runs whenever it feels like it? Incorrect!"},
            {"question": "How do you implement a custom context manager?", "correct_answer": "with statement, __enter__, __exit__",
             "correct_feedback": "Context manager! The boss of resource handling! Correct!",
             "incorrect_feedback": "Manager? Are you in the office? Not how it works!"},
            {"question": "What are descriptors in Python?", "correct_answer": "objects that implement __get__, __set__, or __delete__",
             "correct_feedback": "Descriptors! Powerful objects that control attributes! Absolutely correct!",
             "incorrect_feedback": "Description? Are you telling a story? Incorrect!"},
            {"question": "Explain the difference between coroutines and threads.", "correct_answer": "coroutines are cooperative, threads are preemptive",
             "correct_feedback": "Coroutines cooperative, threads preemptive! The difference is crystal clear! Correct!",
             "incorrect_feedback": "One waits for the other, the other stops forcefully! Not quite!"},
            {"question": "What is monkey patching in Python?", "correct_answer": "modifying a class or module at runtime",
             "correct_feedback": "Monkey patching! Changing code at runtime, big risk, big fun! Absolutely correct!",
             "incorrect_feedback": "Monkey? Is this a monkey's game? Incorrect!"},
            {"question": "How does Python handle memory management?", "correct_answer": "reference counting and garbage collection",
             "correct_feedback": "Reference counting and garbage collection! Python's sophisticated cleaning campaign! Correct!",
             "incorrect_feedback": "Manual memory management? Memory leak happened!"},
            {"question": "What are abstract base classes (ABCs) and why are they used?", "correct_answer": "define interfaces, prevent instantiation",
             "correct_feedback": "ABCs! They define interfaces, objects are not created! Absolutely correct!",
             "incorrect_feedback": "Abstract? Meaning, only for thinking? Incorrect!"},
            {"question": "Discuss the implications of mutable default arguments in Python functions.", "correct_answer": "shared state across calls",
             "correct_feedback": "Mutable default arguments! The danger of shared state, beware! Correct!",
             "incorrect_feedback": "Default argument changed? Not my fault, it's your fault! Incorrect!"},
        ]
    },
    "java": {
        "beginner": [
            {"question": "Which keyword is used to define a class in Java?", "correct_answer": "class",
             "correct_feedback": "'Class'! The sacred keyword for Java class definition! You got it!",
             "incorrect_feedback": "'Struct'? 'Module'? It's 'class', my friend! Incorrect!"},
            {"question": "What is the entry point method for a Java application?", "correct_answer": "main",
             "correct_feedback": "'Main' method! Where everything begins! Correct!",
             "incorrect_feedback": "'Start'? 'Run'? My friend, write 'public static void main'! Not quite!"},
            {"question": "Which keyword is used for inheritance in Java?", "correct_answer": "extends",
             "correct_feedback": "'Extends'! The way to inherit properties from a parent! Absolutely correct!",
             "incorrect_feedback": "'Inherit'? 'Derive'? It's 'extends', my friend! Incorrect!"},
            {"question": "What is the default value of a boolean variable in Java?", "correct_answer": "false",
             "correct_feedback": "False! Java's default truth! Correct!",
             "incorrect_feedback": "True? Null? My friend, boolean defaults to false! Not quite!"},
            {"question": "Which access modifier means visible only within the class?", "correct_answer": "private",
             "correct_feedback": "'Private'! Java's personal space! Absolutely correct!",
             "incorrect_feedback": "'Public'? 'Protected'? Keep it 'private'! Incorrect!"},
            {"question": "What is the keyword to create an object in Java?", "correct_answer": "new",
             "correct_feedback": "'New'! A new object, new hopes! Correct!",
             "incorrect_feedback": "'Create'? 'Make'? My friend, it's the 'new' keyword! Not quite!"},
            {"question": "Which loop executes at least once in Java?", "correct_answer": "do-while",
             "correct_feedback": "'Do-while'! First action, then condition! Absolutely correct!",
             "incorrect_feedback": "'While'? 'For'? My friend, 'do-while' will run at least once! Incorrect!"},
            {"question": "What is the superclass of all classes in Java?", "correct_answer": "Object",
             "correct_feedback": "'Object'! The parent of all, the superclass of everything! Correct!",
             "incorrect_feedback": "'Class'? 'Main'? My friend, it's the 'Object' class! Not quite!"},
            {"question": "Which keyword is used to handle exceptions in Java?", "correct_answer": "try",
             "correct_feedback": "'Try'! The first step to catching errors! Absolutely correct!",
             "incorrect_feedback": "'Catch'? 'Throw'? My friend, start with 'try'! Incorrect!"},
            {"question": "What is the operator for logical AND in Java?", "correct_answer": "&&",
             "correct_feedback": "Double ampersand! When both are true! Correct!",
             "incorrect_feedback": "'And'? Single ampersand? My friend, it's double ampersand! Not quite!"},
        ],
        "expert": [
            {"question": "Explain the Java Memory Model (JMM).", "correct_answer": "defines how threads interact with memory",
             "correct_feedback": "Java Memory Model! The JMM defines how threads interact with memory! Absolutely correct!",
             "incorrect_feedback": "JMM? Jalebi Murabba Mithai? Incorrect!"},
            {"question": "What are Java's concurrency utilities and how are they used?", "correct_answer": "ExecutorService, Future, Callable, locks",
             "correct_feedback": "ExecutorService, Future, Callable, locks! Concurrency utilities, Java's parallel processing game! Correct!",
             "incorrect_feedback": "Threads? Race conditions? Not how you use concurrency!"},
            {"question": "Describe the difference between 'synchronized' keyword and 'ReentrantLock'.", "correct_answer": "synchronized is implicit, ReentrantLock is explicit and more flexible",
             "correct_feedback": "Synchronized is implicit, ReentrantLock is explicit and more flexible! Absolutely correct!",
             "incorrect_feedback": "Lock? Where's the key? Incorrect!"},
            {"question": "What is reflection in Java and its use cases?", "correct_answer": "examining and modifying classes at runtime",
             "correct_feedback": "Reflection! Examining and modifying classes at runtime! Correct!",
             "incorrect_feedback": "Reflection? Is it showing my face? Not quite!"},
            {"question": "Explain the concept of custom annotations in Java.", "correct_answer": "metadata for code",
             "correct_feedback": "Metadata for code! Custom Annotations! Absolutely correct!",
             "incorrect_feedback": "Notes? Comments? Incorrect!"},
            {"question": "How do you implement a custom ClassLoader in Java?", "correct_answer": "extend ClassLoader, override findClass",
             "correct_feedback": "Extend ClassLoader, override findClass! Custom ClassLoader! Correct!",
             "incorrect_feedback": "Class not found? My friend, build a ClassLoader! Not quite!"},
            {"question": "Discuss the implications of using Java Native Interface (JNI).", "correct_answer": "interoperability with native code, platform dependent",
             "correct_feedback": "Interoperability with native code, platform dependent! JNI! Absolutely correct!",
             "incorrect_feedback": "Native code? My friend, it will become platform dependent! Incorrect!"},
            {"question": "What are lambda expressions and functional interfaces in Java 8?", "correct_answer": "concise anonymous functions, single abstract method",
             "correct_feedback": "Concise anonymous functions, single abstract method! Lambdas! Functional interfaces! Correct!",
             "incorrect_feedback": "Anonymous class? My friend, use lambda! Not quite!"},
            {"question": "Explain the principles of SOLID design in Java.", "correct_answer": "Single responsibility, Open/Closed, Liskov substitution, Interface segregation, Dependency inversion",
             "correct_feedback": "Single responsibility, Open/Closed, Liskov substitution, Interface segregation, Dependency inversion! SOLID principles! Absolutely correct!",
             "incorrect_feedback": "Code spaghetti? Follow SOLID principles! Incorrect!"},
            {"question": "Describe the various garbage collection algorithms in JVM.", "correct_answer": "Serial, Parallel, CMS, G1, ZGC",
             "correct_feedback": "Serial, Parallel, CMS, G1, ZGC! GC algorithms! Correct!",
             "incorrect_feedback": "Memory leak? Read GC algorithms! Not quite!"},
        ]
    },
    "cpp": {
        "beginner": [
            {"question": "What is the operator used for dynamic memory allocation in C++?", "correct_answer": "new",
             "correct_feedback": "'New'! The sacred operator for dynamic memory allocation in C++! You got it!",
             "incorrect_feedback": "'Malloc'? 'Alloc'? It's 'new', my friend! Incorrect!"},
            {"question": "Which header file is used for input/output operations in C++?", "correct_answer": "iostream",
             "correct_feedback": "'Iostream'! The heart of C++ input-output! Correct!",
             "incorrect_feedback": "'Stdio.h'? 'Conio.h'? It's 'iostream', my friend! Not quite!"},
            {"question": "What does 'cout' stand for in C++?", "correct_answer": "console output",
             "correct_feedback": "Console output! 'Cout' is C++'s style for printing! Absolutely correct!",
             "incorrect_feedback": "'See-out'? No, console output! Incorrect!"},
            {"question": "Which symbol is used to indicate a pointer in C++?", "correct_answer": "*",
             "correct_feedback": "Star! The symbol of an address! Correct!",
             "incorrect_feedback": "Ampersand? Hash? My friend, use a star! Not quite!"},
            {"question": "What is the keyword for defining a constant in C++?", "correct_answer": "const",
             "correct_feedback": "'Const'! The keyword for defining constants! Absolutely correct!",
             "incorrect_feedback": "'Var'? 'Let'? It's 'const', my friend! Incorrect!"},
            {"question": "Which operator is used for dereferencing a pointer?", "correct_answer": "*",
             "correct_feedback": "Star! The way to grab the value! Correct!",
             "incorrect_feedback": "Are you taking the address? My friend, if you want the value, use a star! Not quite!"},
            {"question": "What is the standard namespace in C++?", "correct_answer": "std",
             "correct_feedback": "'Std'! The home of the standard library! Absolutely correct!",
             "incorrect_feedback": "My_namespace? My friend, it's 'std'! Incorrect!"},
            {"question": "Which loop is guaranteed to execute at least once in C++?", "correct_answer": "do-while",
             "correct_feedback": "'Do-while'! First action, then condition! Correct!",
             "incorrect_feedback": "'While'? 'For'? My friend, 'do-while' will run at least once! Not quite!"},
            {"question": "What is the purpose of 'virtual' keyword in a function?", "correct_answer": "polymorphism",
             "correct_feedback": "Polymorphism! The 'virtual' keyword is C++'s secret to runtime polymorphism! Absolutely correct!",
             "incorrect_feedback": "'Abstract'? 'Override'? No, my friend, this is for polymorphism! Incorrect!"},
            {"question": "What is the difference between 'nullptr' and 'NULL' in C++?", "correct_answer": "nullptr is type-safe, NULL is macro",
             "correct_feedback": "'Nullptr' is type-safe, 'NULL' is a macro! Correct!",
             "incorrect_feedback": "Are they the same? My friend, one is type-safe, the other a macro! Not quite!"},
        ],
        "intermediate": [
            {"question": "Explain the difference between 'pass by value' and 'pass by reference'.", "correct_answer": "value copies, reference uses original",
             "correct_feedback": "Value copies, reference uses original! Absolutely correct!",
             "incorrect_feedback": "Pass by... what? Incorrect!"},
            {"question": "What is a destructor in C++?", "correct_answer": "special member function called when object is destroyed",
             "correct_feedback": "Special member function called when object is destroyed! Correct!",
             "incorrect_feedback": "Garbage collector? No automatic cleanup, my friend! Not quite!"},
            {"question": "What is operator overloading?", "correct_answer": "redefining operators for custom types",
             "correct_feedback": "Redefining operators for custom types! Absolutely correct!",
             "incorrect_feedback": "Operator... what now? Incorrect!"},
            {"question": "Describe the concept of 'RAII' in C++.", "correct_answer": "Resource Acquisition Is Initialization",
             "correct_feedback": "Resource Acquisition Is Initialization! Correct!",
             "incorrect_feedback": "Rai-rai? Not quite!"},
            {"question": "What is the difference between 'struct' and 'class' in C++?", "correct_answer": "struct default public, class default private",
             "correct_feedback": "Struct default public, class default private! Absolutely correct!",
             "incorrect_feedback": "Are they the same? Incorrect!"},
            {"question": "What is a copy constructor in C++?", "correct_answer": "constructor that creates object by copying another object",
             "correct_feedback": "A copy constructor creates an object by copying another! Correct!",
             "incorrect_feedback": "Not quite a copy constructor! That's not how we duplicate objects."},
            {"question": "Explain the concept of 'virtual functions' in C++.", "correct_answer": "functions that can be overridden in derived classes and enable runtime polymorphism",
             "correct_feedback": "Virtual functions enable runtime polymorphism! Absolutely correct!",
             "incorrect_feedback": "Virtual functions are not just regular functions! That's incorrect."},
            {"question": "What is the purpose of 'explicit' keyword in C++ constructors?", "correct_answer": "prevents implicit conversions",
             "correct_feedback": "Explicit prevents implicit conversions! Correct, keep those conversions clear!",
             "incorrect_feedback": "Explicit doesn't force conversions! That's incorrect, it does the opposite."},
            {"question": "What is a 'friend function' in C++?", "correct_answer": "non-member function that can access private and protected members of a class",
             "correct_feedback": "A friend function can access private members! Absolutely correct, they're like code besties!",
             "incorrect_feedback": "Friend functions aren't just any function! That's incorrect, they have special access."},
            {"question": "Explain 'move semantics' (rvalue references) in C++11.", "correct_answer": "efficient transfer of resources",
             "correct_feedback": "Move semantics is about efficient resource transfer! Correct, no unnecessary copying here!",
             "incorrect_feedback": "Move semantics isn't just copying! That's incorrect, it's about ownership transfer."},
        ],
        "expert": [
            {"question": "Describe the C++ Standard Template Library (STL) components.", "correct_answer": "containers, algorithms, iterators, function objects",
             "correct_feedback": "STL components: containers, algorithms, iterators, function objects! Absolutely correct!",
             "incorrect_feedback": "STL is more than just a library! That's incorrect, you missed some key components."},
            {"question": "Explain the 'Rule of Three/Five/Zero' in C++.", "correct_answer": "copy constructor, copy assignment, destructor",
             "correct_feedback": "Rule of Three/Five/Zero covers copy constructor, copy assignment, and destructor! Correct!",
             "incorrect_feedback": "The Rule of Three/Five/Zero is not just about constructors! That's incorrect."},
            {"question": "What is SFINAE (Substitution Failure Is Not An Error) in C++ templates?", "correct_answer": "template metaprogramming technique",
             "correct_feedback": "SFINAE is a template metaprogramming technique! Absolutely correct, when failure is a feature!",
             "incorrect_feedback": "SFINAE is not an error, but your answer is! That's incorrect."},
            {"question": "Discuss the implications of virtual inheritance.", "correct_answer": "solves diamond problem",
             "correct_feedback": "Virtual inheritance solves the diamond problem! Correct, avoiding multiple base class subobjects!",
             "incorrect_feedback": "Virtual inheritance isn't just for fun! That's incorrect, it has a specific problem it solves."},
            {"question": "Explain move semantics (rvalue references) in C++11.", "correct_answer": "efficient transfer of resources",
             "correct_feedback": "Move semantics is about efficient resource transfer! Absolutely correct, no unnecessary copying here!",
             "incorrect_feedback": "Move semantics isn't just copying! That's incorrect, it's about ownership transfer."},
            {"question": "What is a 'perfect forwarding' in C++?", "correct_answer": "passing arguments while preserving their value category (lvalue/rvalue)",
             "correct_feedback": "Perfect forwarding preserves value categories! Correct, keeping those lvalues and rvalues intact!",
             "incorrect_feedback": "Perfect forwarding isn't just about passing arguments! That's incorrect, it's more nuanced."},
            {"question": "Describe the concept of 'CRTP' (Curiously Recurring Template Pattern).", "correct_answer": "class derives from a template specialization of itself",
             "correct_feedback": "CRTP is when a class derives from a template specialization of itself! Absolutely correct, a curious pattern indeed!",
             "incorrect_feedback": "CRTP is not just a random template! That's incorrect, it's a specific design pattern."},
            {"question": "What is the purpose of 'placement new' in C++?", "correct_answer": "constructs object at a pre-allocated memory location",
             "correct_feedback": "Placement new constructs objects at pre-allocated memory! Correct, fine-grained memory control!",
             "incorrect_feedback": "Placement new isn't regular new! That's incorrect, it doesn't allocate memory."},
            {"question": "Explain the 'std::variant' and 'std::visit' in C++17.", "correct_answer": "type-safe union, apply visitor to variant",
             "correct_feedback": "Std::variant is a type-safe union, and std::visit applies a visitor! Absolutely correct, modern C++ for the win!",
             "incorrect_feedback": "Std::variant isn't just any union! That's incorrect, it's type-safe and powerful."},
            {"question": "What is the difference between 'std::async' and 'std::thread'?", "correct_answer": "std::async manages future, std::thread manages raw thread",
             "correct_feedback": "Std::async manages a future, std::thread manages a raw thread! Correct, knowing your concurrency tools!",
             "incorrect_feedback": "Std::async and std::thread are not the same! That's incorrect, they have different management approaches."},
        ]
    }
}


# Temporary storage for generated audio streams (in a real app, use a proper cache/database)
generated_audio_streams = {}

def generate_audio_from_text(text, lang='en'):
    """
    Generates an MP3 audio stream from text using gTTS and returns a BytesIO object.
    Removes common punctuation to ensure gTTS speaks clearly without pauses.
    """
    try:
        # Remove common punctuation marks
        text_without_punctuation = re.sub(r'[.,;!?"\'-]', '', text)
        # Replace multiple spaces with a single space
        text_without_punctuation = re.sub(r'\s+', ' ', text_without_punctuation).strip()

        # Ensure language is English
        tts = gTTS(text=text_without_punctuation, lang=lang, slow=False)
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0) # Rewind to the beginning of the stream
        return audio_stream
    except Exception as e:
        print(f"Error generating audio from text: {e}")
        return None

@app.route('/audio/<audio_id>')
def serve_generated_audio(audio_id):
    """
    Serves a dynamically generated audio file from in-memory storage.
    """
    audio_stream = generated_audio_streams.get(audio_id)
    if audio_stream:
        return send_file(audio_stream, mimetype='audio/mpeg', as_attachment=False)
    else:
        return "Audio not found or expired.", 404

def get_random_local_image_info():
    """
    Selects a random image from the static/images/correct/ folder (i1.jpg to i21.jpg)
    and returns its filename and a corresponding meme name.
    """
    random_image_num = random.randint(1, 21)
    image_filename = f"i{random_image_num}.jpg"
    local_image_url = url_for('static', filename=f'images/correct/{image_filename}')
    
    # Get the meme name from the mapping, default to a generic name if not found
    meme_name = LOCAL_MEME_NAMES.get(image_filename, f"Generic Meme {random_image_num}")

    print(f"DEBUG: Image fetched from local fallback: {image_filename} (Meme Name: {meme_name})")
    return {
        "id": "local_fallback", # Special ID to indicate local fallback
        "filename": image_filename, # Store filename to get its meme name
        "url": local_image_url,
        "name": meme_name,
        "box_count": 1 # Assume 1 text box for local images for simplicity
    }

def create_meme_image(text, meme_template_info, filename="generated_meme.png"):
    """
    Generates a meme image by downloading an Imgflip template (or using fallback)
    and overlaying the given text using Pillow.
    The image will be saved to static/images/.
    """
    try:
        image_url = meme_template_info.get('url')
        img = None

        if image_url and image_url.startswith('/static/'): # It's a local static file
            image_path = os.path.join(app.root_path, image_url.lstrip('/'))
            if not os.path.exists(image_path):
                print(f"Error: Local fallback image not found at {image_path}. Creating blank image.")
                img = Image.new('RGB', (250, 250), color = (73, 109, 137)) # Fixed size: 250x250
                d = ImageDraw.Draw(img)
                fnt = ImageFont.load_default()
                d.text((10,10), "Image Missing!", font=fnt, fill=(255,255,255))
            else:
                img = Image.open(image_path).convert("RGB")
        else: # Fallback for unexpected image_url, or if it was from Imgflip (which we're now avoiding)
            print("Unexpected image URL or no URL provided. Creating blank image.")
            img = Image.new('RGB', (250, 250), color = (73, 109, 137)) # Fixed size: 250x250
            d = ImageDraw.Draw(img)
            fnt = ImageFont.load_default()
            d.text((10,10), "Image Load Error!", font=fnt, fill=(255,255,255))


        # Define text color
        text_color = (0, 0, 0)  # Black text

        d = ImageDraw.Draw(img)

        # --- Image Resizing to 250x250 ---
        img_width = 250
        img_height = 250
        img = img.resize((img_width, img_height), Image.LANCZOS) # Use LANCZOS for high-quality downsampling

        # --- Robust Font Loading ---
        font_size = int(img.height * 0.07) # Adjust font size relative to image height
        font = ImageFont.load_default() # Start with a reliable default font

        try:
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
                    break
            else:
                print("Warning: Specific font not found. Using default Pillow font.")

        except Exception as e:
            print(f"Error loading custom font: {e}. Falling back to default font.")
            font = ImageFont.load_default()
        # --- End Robust Font Loading ---

        # Simple text wrapping and positioning for better readability on various templates
        lines = []
        words = text.split()
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            # Use textlength for accurate width calculation
            bbox = d.textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            if test_width < img.width * 0.9: # Keep text within 90% of image width
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))

        # Calculate total text height to center it vertically at the top
        total_text_height = sum(d.textbbox((0, 0), line, font=font)[3] - d.textbbox((0, 0), line, font=font)[1] for line in lines)
        
        # Position text towards the top, with some padding
        y_start_pos = img.height * 0.05 # 5% from the top
        y_text = y_start_pos

        for line in lines:
            # Calculate width of the current line
            bbox = d.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x_text = (img.width - line_width) / 2 # Center horizontally
            d.text((x_text, y_text), line, fill=text_color, font=font)
            y_text += (bbox[3] - bbox[1]) # Move to next line

        # Save the image to a BytesIO object for immediate use and then save to disk
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0) # Rewind to beginning

        # Save to disk for static serving in case of direct URL access or debugging
        image_path_on_disk = os.path.join(IMAGES_DIR, filename)
        with open(image_path_on_disk, 'wb') as f:
            f.write(img_byte_arr.getvalue())
        
        return url_for('static', filename=f'images/{filename}')
    except Exception as e:
        print(f"Error creating meme image: {e}")
        # Fallback to a generic blank image if all else fails
        return url_for('static', filename='images/placeholder.png') # Ensure you have a placeholder.png in static/images/

@app.route('/')
def vikasa_home():
    """Renders the new homepage."""
    return render_template('vikasa_home.html')

@app.route('/quiz')
def index():
    """Renders the main page for coding skill selection and questions."""
    return render_template('index.html', questions=CODING_QUESTIONS)

@app.route('/generate_meme', methods=['POST'])
async def generate_meme():
    """
    Processes the user's coding skill and answer, generates a meme,
    and renders the meme display page.
    """
    selected_language = request.form.get('coding_language')
    self_assessed_skill_level = request.form.get('skill_level')
    user_answer = request.form.get('answer', '').strip().lower() # Get the user's raw answer
    question_text = request.form.get('question_text', '').strip() # Get the question text from the form

    selected_meme_text = "Something went wrong. Try again!"
    final_skill_level = "beginner"
    is_answer_correct = False
    core_feedback_text = "" # Initialize core feedback text

    # Get the specific question object to determine correctness and core feedback
    current_question_obj = None
    if selected_language in CODING_QUESTIONS and self_assessed_skill_level in CODING_QUESTIONS[selected_language]:
        questions_for_level = CODING_QUESTIONS[selected_language][self_assessed_skill_level]
        for q_obj in questions_for_level:
            if q_obj['question'].strip().lower() == question_text.lower():
                current_question_obj = q_obj
                break

    correct_answer_for_question = ""
    if current_question_obj:
        correct_answer_for_question = current_question_obj['correct_answer'].lower()
        if user_answer == correct_answer_for_question:
            is_answer_correct = True
            final_skill_level = self_assessed_skill_level
            core_feedback_text = current_question_obj.get('correct_feedback', "That's correct!")
        else:
            is_answer_correct = False
            final_skill_level = "beginner" # Incorrect answer or unmatched question defaults to beginner
            core_feedback_text = current_question_obj.get('incorrect_feedback', "That's incorrect!")
    else:
        # Fallback if question not found (shouldn't happen with proper frontend)
        is_answer_correct = False
        final_skill_level = "beginner"
        core_feedback_text = "Oops! Couldn't find that question, but your coding journey continues!"


    # --- Step 1: Get a random local image and its meme name ---
    meme_template_info = get_random_local_image_info()
    meme_image_url = meme_template_info['url']
    meme_name = meme_template_info['name'] # This is crucial for the caption formatting

    # --- Step 2: Generate the combined text from generic captions and dictionary feedback ---
    if is_answer_correct:
        # Select a random correct generic caption and format it with both meme_name and core_feedback_text
        selected_meme_text = random.choice(GENERIC_CORRECT_CAPTIONS).format(
            meme_name=meme_name,
            feedback_text=core_feedback_text
        )
    else:
        # Select a random incorrect generic caption and format it with both meme_name and core_feedback_text
        selected_meme_text = random.choice(GENERIC_INCORRECT_CAPTIONS).format(
            meme_name=meme_name,
            feedback_text=core_feedback_text
        )

    # --- Step 3: Create the meme image with the selected text ---
    meme_filename = f"generated_meme_{uuid.uuid4()}.png"
    final_meme_image_url = create_meme_image(selected_meme_text, meme_template_info, meme_filename)

    # --- Step 4: Generate audio from the selected (combined) text ---
    audio_stream = generate_audio_from_text(selected_meme_text, lang='en')
    generated_audio_id = str(uuid.uuid4())
    generated_audio_streams[generated_audio_id] = audio_stream
    generated_audio_url = url_for('serve_generated_audio', audio_id=generated_audio_id)

    return render_template('meme.html',
                           meme_text=selected_meme_text,
                           meme_image_url=final_meme_image_url,
                           background_music_url=generated_audio_url,
                           skill_level_display=final_skill_level.capitalize())

# --- Define the routers for Render deployment ---
# These are already defined using @app.route() decorators.
# No additional "routers" need to be defined here.
# This section is just to explicitly show the existing routes.

@app.route('/health')
def health_check():
    """Simple health check endpoint for deployment platforms."""
    return "OK", 200

# The other routes are already defined above:
# @app.route('/')
# @app.route('/quiz')
# @app.route('/generate_meme', methods=['POST'])
# @app.route('/audio/<audio_id>')
# @app.route('/static/music/<path:filename>')
# @app.route('/favicon.ico')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

