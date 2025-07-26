import os
import requests
from flask import Flask, render_template, request, send_from_directory, url_for, send_file, session
from PIL import Image, ImageDraw, ImageFont
import random
import io # To handle image data in memory
from gtts import gTTS # Import the gTTS library
import uuid # For unique filenames for generated audio
import re # For regular expressions to remove punctuation

app = Flask(__name__)

# --- IMPORTANT: Set a strong secret key for session management! ---
# In production, this should be a complex, random string stored in an environment variable.
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_dev_key_please_change_this!")


# Imgflip API Configuration
IMGFLIP_API_URL = "https://api.imgflip.com/get_memes"
# You MUST replace these with your actual Imgflip username and password
# It's highly recommended to use environment variables for these as well in a real deployment!
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME", "your_imgflip_username") # Replace with your Imgflip username
IMGFLIP_PASSWORD = os.getenv("IMGFLP_PASSWORD", "your_imgflip_password") # Replace with your Imgflip password


# --- CURATED LISTS OF IMGFLIP MEME IDs FOR CORRECT/INCORRECT ANSWERS ---
# These are fallback IDs if the dynamic fetch from Imgflip fails or is empty.
# They should ideally be valid Imgflip IDs that you've verified.
# These IDs are chosen because they are popular and versatile for coding-related captions.
CORRECT_MEME_IDS = [
    "101288",    # Success Kid
    "181913649", # Drake Hotline Bling
    "135256802", # Epic Handshake
    "89652",     # Satisfied Seal
    "71838",     # Good Guy Greg
    "3218037",   # Oprah You Get A
    "101511",    # One Does Not Simply
    "124055",    # Is This A Pigeon?
    "14230520",  # Success Kid (again)
    "11016393",  # Woman Yelling At Cat (can be positive for "finally fixed it")
    "101716",    # Anakin Padme (for "I like this code")
    "101662",    # Facepalm (can be positive, e.g., "I fixed it, facepalm")
    "101440",    # 10 Guy (for "mind blown" success)
    "40878337",  # This Is Fine (ironic success)
    "119139145", # One Does Not Simply (another version)
    "101366",    # Bad Luck Brian (ironic success)
    "101488",    # Overly Attached Girlfriend (for code attachment)
    "101450",    # Scumbag Steve (ironic, for good practices)
    "101490",    # Grumpy Cat (ironic, for coding joy)
    "101483",    # Ancient Aliens (for complex solutions)
    "186194504", # Think About It
    "1509839",   # X, X Everywhere (for green checkmarks)
    "101353",    # Futurama Fry (for "not sure if...")
    # Adding more versatile popular memes that can be adapted for coding success
    "129242436", # Is This A Pigeon? (can be used for "is this working?")
    "101884",    # Disappointed Black Guy (ironic success)
    "100955",    # Confused Nick Young (for understanding complex code)
    "101910",    # Evil Kermit (for good dev decisions)
    "102156234", # Running Away Balloon (for finishing a project)
    "80707670",  # Doge (for "wow, such code")
    "196652222", # Boardroom Meeting Suggestion (for good tech suggestions)
    "100000",    # Surprised Pikachu (for unexpected success)
]

INCORRECT_MEME_IDS = [
    "112126428", # Distracted Boyfriend
    "100955",    # Confused Nick Young
    "101910",    # Evil Kermit
    "101470",    # Condescending Wonka
    "102156234", # Running Away Balloon
    "80707670",  # Doge
    "101884",    # Disappointed Black Guy
    "101716",    # Anakin Padme (for "I don't like it")
    "129242436", # Is This A Pigeon (for confusion)
    "131087935", # Spiderman Pointing (for blaming others)
    "188390779", # Woman Yelling At Cat (for frustration)
    "196652222", # Boardroom Meeting Suggestion (for bad suggestions)
    "100000",    # Surprised Pikachu (for unexpected errors)
    "101662",    # Facepalm
    "101440",    # 10 Guy (for utter confusion)
    "40878337",  # This Is Fine (for when it's NOT fine)
    "119139145", # One Does Not Simply (for getting it wrong)
    "101366",    # Bad Luck Brian
    "101488",    # Overly Attached Girlfriend (for code breaking up with you)
    "101450",    # Scumbag Steve (for bad dev practices)
    "101490",    # Grumpy Cat (for coding misery)
    "101483",    # Ancient Aliens (for inexplicable errors)
    "186194504", # Think About It (for failing to think)
    "1509839",   # X, X Everywhere (for red X's)
    "101353",    # Futurama Fry (for uncertainty)
    # Adding more versatile popular memes that can be adapted for coding failure
    "101288",    # Success Kid (ironic failure)
    "181913649", # Drake Hotline Bling (for bad coding practices)
    "135256802", # Epic Handshake (for code breaking ties)
    "89652",     # Satisfied Seal (ironic failure)
    "71838",     # Good Guy Greg (ironic, for bad guy dev)
    "3218037",   # Oprah You Get A (for getting errors)
]


# --- MEME CAPTIONS MAPPED TO SPECIFIC IMGFLIP MEME IDs (Coding/Debugging Themed) ---
MEME_CAPTIONS_BY_ID = {
    "101288": { # Success Kid
        "correct": "When your code compiles on the first try. Success Kid! You're a legend!",
        "incorrect": "When you debug for hours and it was just a typo. My disappointment is immeasurable, and my day is ruined."
    },
    "181913649": { # Drake Hotline Bling
        "correct": "Using Python's append() (Yes!) vs. Trying to use push() (No! Seriously, stop.)",
        "incorrect": "Trying to use push() in Python (Nah!) vs. Sticking to append() (Yeah! Learn the language, human!)"
    },
    "135256802": { # Epic Handshake
        "correct": "Me and the debugger, finally on the same page. A true love story.",
        "incorrect": "Me trying to handshake with my broken code. It's not reciprocating."
    },
    "89652": { # Satisfied Seal
        "correct": "When your legacy code still runs perfectly. Pure, unadulterated bliss.",
        "incorrect": "When you accidentally delete the entire repo. My soul just left my body."
    },
    "71838": { # Good Guy Greg
        "correct": "Good Guy Greg: Comments his code. The hero we didn't deserve.",
        "incorrect": "Bad Luck Brian: Deploys on Friday. May the odds be ever against you."
    },
    "3218037": { # Oprah You Get A
        "correct": "You get a variable! And you get a variable! Everyone gets a variable! Except for you, you get an error.",
        "incorrect": "You get an error! And you get an error! Everyone gets an error! Because you didn't listen."
    },
    "101511": { # One Does Not Simply
        "correct": "One does not simply write bug-free code... unless you're a coding deity! Which you clearly are.",
        "incorrect": "One does not simply understand this error message. It's a riddle wrapped in a mystery."
    },
    "124055": { # Is This A Pigeon?
        "correct": "Is this... a working solution? Yes! Yes, it is! Miracles do happen.",
        "incorrect": "Is this... a syntax error or a feature? My brain hurts just looking at it."
    },
    "11016393": { # Woman Yelling At Cat
        "correct": "My code finally running vs. The 100 errors I fixed. I'm not crying, you're crying.",
        "incorrect": "My code after I 'fixed' it vs. The new errors it created. This is fine. Everything is fine."
    },
    "101716": { # Anakin Padme
        "correct": "I like writing clean code. I love it. It's beautiful.",
        "incorrect": "I hate bugs. They're coarse and rough and they get everywhere. And they crash my app."
    },
    "101662": { # Facepalm
        "correct": "When you overthink a simple problem but still get it right. My genius is almost frightening.",
        "incorrect": "When you spend hours debugging and it was a missing semicolon. I need a new keyboard. Or a new life."
    },
    "101440": { # 10 Guy
        "correct": "My brain after successfully deploying a complex system. I'm a god.",
        "incorrect": "My brain trying to understand recursion at 3 AM. Send help. And coffee."
    },
    "40878337": { # This Is Fine
        "correct": "When your code has one warning but you deploy it anyway. This is fine. Probably.",
        "incorrect": "When your entire system is on fire but you're still coding. This is fine. Just a little bit of fire."
    },
    "119139145": { # One Does Not Simply (another version)
        "correct": "One does not simply pass all unit tests without trying. Unless you're a wizard.",
        "incorrect": "One does not simply ignore compiler warnings. They come back to haunt you."
    },
    "101366": { # Bad Luck Brian
        "correct": "Writes 1000 lines of code. It works on the first try. Bad Luck Brian? More like Good Luck Brian!",
        "incorrect": "Writes 5 lines of code. Gets 100 errors. Classic Brian."
    },
    "101488": { # Overly Attached Girlfriend
        "correct": "I saw you trying to close the IDE. Are you done coding already? But we just started!",
        "incorrect": "I saw you looking at other languages. Am I not good enough? I thought we had something special."
    },
    "101450": { # Scumbag Steve
        "correct": "Scumbag Steve: Uses dark mode. Saves your eyes. What a hero.",
        "incorrect": "Scumbag Steve: Deploys broken code. Blames the network. Typical."
    },
    "101490": { # Grumpy Cat
        "correct": "I hate everything. Except when my code compiles. That's a rare moment of joy.",
        "incorrect": "I had fun once. It was awful. (Like this error). Just pure misery."
    },
    "101884": { # Disappointed Black Guy
        "correct": "When your junior dev actually fixes a critical bug. I'm not mad, I'm just... surprised.",
        "incorrect": "When your code fails the simplest test case. My disappointment is palpable."
    },
    "100955": { # Confused Nick Young
        "correct": "When the error message makes no sense at all. Is this even English?",
        "incorrect": "When your code works but you don't know why. I'm scared, but also impressed."
    },
    "101910": { # Evil Kermit
        "correct": "Me: I should write unit tests. Also me: Just push it to production. YOLO!",
        "incorrect": "Me: I should fix this bug properly. Also me: Just add a band-aid solution. It'll be fine. Probably."
    },
    "101470": { # Condescending Wonka
        "correct": "Oh, you debugged your code in 5 minutes? Tell me more about your magic. I'm all ears.",
        "incorrect": "So, you think 'git push --force' is a good idea? Fascinating. Tell me more about your life choices."
    },
    "102156234": { # Running Away Balloon
        "correct": "Me running away from my responsibilities after successfully deploying code. Catch me if you can!",
        "incorrect": "My motivation running away after seeing the error log. I'm out. Peace."
    },
    "80707670": { # Doge
        "correct": "Wow. Such code. Very compile. Much success. So good.",
        "incorrect": "So error. Much fail. Very confuse. Wow."
    },
    "196652222": { # Boardroom Meeting Suggestion
        "correct": "My suggestion: Let's use Python for everything. Everyone else: *throws out*. Their loss.",
        "incorrect": "My suggestion: Let's refactor the entire codebase. Everyone else: *throws out*. Guess we're stuck with spaghetti."
    },
    "100000": { # Surprised Pikachu
        "correct": "My reaction when my old code still works after an update. Impossible!",
        "incorrect": "My reaction when the 'simple fix' introduces 20 new bugs. Shocked, but not surprised."
    },
    "186194504": { # Think About It
        "correct": "When you solve a complex algorithm in your head before coding. Think about it.",
        "incorrect": "When the error message says 'unexpected token' but you've checked everything. Think about it."
    },
    "1509839": { # X, X Everywhere
        "correct": "Green checkmarks, green checkmarks everywhere! My code is beautiful.",
        "incorrect": "Syntax errors, syntax errors everywhere! I'm losing my mind."
    },
    "101353": { # Futurama Fry
        "correct": "Not sure if my code is brilliant or just lucky. Why not both?",
        "incorrect": "Not sure if I fixed the bug or just introduced a new one. Guess I'll find out."
    }
}

# Generic fallback captions if a specific meme ID is not in MEME_CAPTIONS_BY_ID
GENERIC_CORRECT_CAPTIONS = [
    "Your code is cleaner than my search history! And that's saying something.",
    "Bug? What bug? My code just works! It'    s a miracle!",
    "This answer deserves a standing ovation from the entire dev team! Take a bow!",
    "Green checkmark achieved! Time for a coffee break! Or a vacation.",
    "My brain cells after solving that tricky bug: *chef's kiss*. Perfection!",
    "Code compiled, tests passed, coffee brewed. Life is good! For now...",
    "That feeling when your obscure fix actually works. I am a god among mortals.",
    "Another day, another perfectly executed function. You're a legend! Seriously.",
    "The compiler just whispered 'Thank you' to your code. You're welcome, compiler.",
    "You just made a programmer somewhere happy. Well done! Keep up the good work!",
]

GENERIC_INCORRECT_CAPTIONS = [
    "When you try to run JavaScript in Python. Classic mistake! Did you even try?",
    "My code after I 'fixed' one bug and created ten more. It's an art form, really.",
    "That moment when your code looks right but screams 'Segmentation Fault'. My eyes deceive me!",
    "Debugging for hours only to realize you forgot a semicolon. Again. It's a rite of passage.",
    "My face when the 'fix' breaks everything else. Back to the drawing board! Send snacks.",
    "Error 404: Brain not found. Please try again. Or get some sleep.",
    "Did you even read the documentation? Just kidding... mostly. (But seriously, read it.)",
    "My code is like a box of chocolates. You never know what error you're gonna get. And it's always the bad kind.",
    "The only thing worse than no errors is silent errors. And this isn't silent! It's screaming!",
    "Looks like someone needs a rubber duck. Or a whole pond of them! Maybe a therapist.",
]


# Ensure the static directories exist
STATIC_DIR = os.path.join(app.root_path, 'static')
IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
MUSIC_DIR = os.path.join(STATIC_DIR, 'music') # Can remain empty
FONTS_DIR = os.path.join(STATIC_DIR, 'fonts') # Define fonts directory
CORRECT_IMAGES_DIR = os.path.join(IMAGES_DIR, 'correct') # New: Path to correct images folder

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(CORRECT_IMAGES_DIR, exist_ok=True) # Ensure correct images directory exists

# Temporary storage for generated audio streams (in a real app, use a proper cache/database)
generated_audio_streams = {}

# Global cache for Imgflip memes, populated once
all_imgflip_memes_cache = []

# Function to populate the Imgflip meme cache
def populate_imgflip_meme_cache():
    global all_imgflip_memes_cache
    if not all_imgflip_memes_cache: # Only fetch if cache is empty
        try:
            print("DEBUG: Attempting to fetch all memes from Imgflip API for caching...")
            response = requests.get(IMGFLIP_API_URL)
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            if data and data['success']:
                # Filter for memes with at least 2 boxes for versatility
                all_imgflip_memes_cache = [m for m in data['data']['memes'] if m.get('box_count', 0) >= 2]
                print(f"DEBUG: Successfully cached {len(all_imgflip_memes_cache)} memes from Imgflip.")
            else:
                print(f"DEBUG: Imgflip API reported an error during initial cache fetch: {data.get('error_message', 'Unknown error')}. Will rely on hardcoded IDs.")
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Network error during initial Imgflip cache fetch: {e}. Will rely on hardcoded IDs.")
        except Exception as e:
            print(f"DEBUG: An unexpected error occurred during initial Imgflip cache fetch: {e}. Will rely on hardcoded IDs.")

# Call this function once when the app starts
with app.app_context():
    populate_imgflip_meme_cache()


# --- CODING QUESTIONS WITH FULL CUSTOM AUDIO SCRIPTS (ENGLISH ONLY, MORE FUN) ---
# Each question now has its own complete correct_audio_script and incorrect_audio_script.
CODING_QUESTIONS = {
    "python": {
        "beginner": [
            {"question": "What is the output of 'print(type([]))' in Python?", "correct_answer": "<class 'list'>",
             "correct_audio_script": """
                Boom! Correct! You're a Python wizard in the making! It's a list, obviously. Keep that code clean and those deployments smooth!
             """,
             "incorrect_audio_script": """
                'Push'? Are we doing JavaScript now? Python's throwing a fit: 'Push' is not defined, only 'append' exists here! It's not a type error, it's a 'NameError' in your brain! Oof!
             """},
            {"question": "Which keyword is used to define a function in Python?", "correct_answer": "def",
             "correct_audio_script": """
                'Def'! The sacred word for Python function definition! That's its charm! Killer syntax, my friend! Now go forth and create complex, beautiful functions!
             """,
             "incorrect_audio_script": """
                'Function'? 'Method'? What are you even saying? Just say 'def'! How will this ever work? SyntaxError: invalid syntax, maybe you meant 'def'? Seriously, how did you mess up such a simple one?!
             """},
            {"question": "What is the result of '2 + 2 * 3' in Python?", "correct_answer": "8",
             "correct_audio_script": """
                Eight! Order of operations for the win! You're even strong in math, good job! Calculation successful! Now go solve some real-world problems, like how many coffee cups you need to finish this project.
             """,
             "incorrect_audio_script": """
                Ten? Did you forget basic arithmetic, my friend? MathError: Operator precedence mistake! Ugh, even this basic math is wrong! Were you sleeping during elementary school?
             """},
            {"question": "How do you comment a single line in Python?", "correct_answer": "#",
             "correct_audio_script": """
                Hash! Python's secret code for invisibility! Good job, now keep that code clean and readable! Comments are a programmer's best friend, after coffee.
             """,
             "incorrect_audio_script": """
                Double slash? Are you writing C++ or something? Use a hashtag, my dude! SyntaxError: invalid character in identifier! Oops, language mix-up! Time to pick a lane!
             """},
            {"question": "Which data type is used to store a sequence of characters in Python?", "correct_answer": "string",
             "correct_audio_script": """
                String! The majestic ruler of characters! Good, now you can start processing text, building chatbots, or writing the next great novel in code!
             """,
             "incorrect_audio_script": """
                Char array? My friend, in Python, we call it a string. Simple! TypeError: 'char' object is not iterable! Is this the Java influence creeping in?
             """},
            {"question": "What is the keyword to exit a loop prematurely in Python?", "correct_answer": "break",
             "correct_audio_script": """
                Break! Freedom from the infinite loop! Thank goodness, we dodged a bullet there! Loop exited successfully! Now go take a break yourself, you've earned it!
             """,
             "incorrect_audio_script": """
                Continue? Exit? My friend, use 'break'! It's the emergency exit! NameError: name 'exit' is not defined! Looks like your life needs a 'break' too!
             """},
            {"question": "Which function is used to get input from the user in Python?", "correct_answer": "input",
             "correct_audio_script": """
                Input! The magical gateway to user interaction! Good, now you can build interactive programs and finally get some data from those pesky users!
             """,
             "incorrect_audio_script": """
                Scanf? Getline? My friend, just write 'input()', talk directly! NameError: name 'scanf' is not defined! Are we back in C++ land?
             """},
            {"question": "What is the operator for exponentiation in Python?", "correct_answer": "**",
             "correct_audio_script": """
                Double star! The ultimate power symbol! Good, now you can play with massive numbers and calculate the true power of your coding skills!
             """,
             "incorrect_audio_script": """
                Caret? Pow()? Are you doing math or performing a magic trick? Use double star! TypeError: unsupported operand type(s) for ^: 'int' and 'int'! Failed in math too, huh?
             """},
            {"question": "What is the output of 'len(\"hello\")' in Python?", "correct_answer": "5",
             "correct_audio_script": """
                Five! Easy peasy, lemon squeezy! Counting length is like, coding 101! Length calculated! Now go count the lines of code you've written!
             """,
             "incorrect_audio_script": """
                Length? Size? Count? My friend, it's five! TypeError: object of type 'int' has no len()! Your counting skills are as rusty as my old floppy disk!
             """},
            {"question": "Which module is used for mathematical operations in Python?", "correct_answer": "math",
             "correct_audio_script": """
                Math! The undisputed king of calculations! Good, now you can tackle complex math problems, build scientific applications, or just calculate how many pizzas you can eat while coding!
             """,
             "incorrect_audio_script": """
                Calc? Num? My friend, it's the 'math' module. Simple! ModuleNotFoundError: No module named 'calc'! Did you forget the module name too, or just make one up?
             """},
            {"question": "How do you define an empty dictionary in Python?", "correct_answer": "{}",
             "correct_audio_script": """
                Curly braces! An empty dictionary, ready to be filled with glorious key-value pairs! Good, now go organize some data like a pro!
             """,
             "incorrect_audio_script": """
                Empty list? Tuple? My friend, use curly braces, it'll make a dictionary! SyntaxError: invalid syntax! Are you confused by brackets, or just trying to break my parser?
             """},
            {"question": "What is the output of 'print(5 > 3 and 10 < 20)'?", "correct_answer": "True",
             "correct_audio_script": """
                True! The undeniable power of logic! You're strong in Boolean algebra too, impressive! Logical operation successful! Now go solve some real-world logical puzzles, like why your code doesn't work on Tuesdays.
             """,
             "incorrect_audio_script": """
                False? Did you forget Boolean algebra, my friend? It's True! TypeError: 'bool' object is not callable! Looks like your logic gate crashed!
             """},
             {"question": "What is a virtual environment in Python?", "correct_answer": "isolated Python environment",
             "correct_audio_script": """
                Isolated environment! The end of dependency hell! Good practice, now your projects won't fight each other like siblings! Virtual environment created! Go build clean projects!
             """,
             "incorrect_audio_script": """
                Virtual reality? Gaming environment? My friend, this is for code isolation! NameError: name 'virtual_reality' is not defined! Is that the gaming addiction talking?
             """},
             {"question": "What is the purpose of 'self' in Python class methods?", "correct_answer": "refers to the instance of the class",
             "correct_audio_script": """
                Self! The object's personal reference! Good, now you're an expert in object-oriented programming! Instance referenced! Go create some self-aware code!
             """,
             "incorrect_audio_script": """
                Myself? Your self? My friend, this refers to the current instance! SyntaxError: invalid syntax! Did you have a moment of self-doubt there?
             """},
             {"question": "Which built-in function is used to convert a string to an integer in Python?", "correct_answer": "int()",
             "correct_audio_script": """
                Int! The magic spell to turn a string into a number! Good, now you're a master of data type conversion! Type conversion successful! Go convert some more, you wizard!
             """,
             "incorrect_audio_script": """
                To_int? Parse_int? My friend, it's the 'int()' function! NameError: name 'to_int' is not defined! Did you forget the function name, or just make up your own?
             """},
             {"question": "How do you remove an element from a list by its value in Python?", "correct_answer": "remove()",
             "correct_audio_script": """
                Remove! Delete an element by its value! Good, now you're an expert in list manipulation! Element removed! Go keep those lists squeaky clean!
             """,
             "incorrect_audio_script": """
                Delete? Pop? My friend, it's the 'remove()' method! AttributeError: 'list' object has no attribute 'delete'! Are you confused about how to delete things?
             """},
             {"question": "What is the purpose of 'pip' in Python?", "correct_answer": "package installer",
             "correct_audio_script": """
                Pip! The mighty package installer for Python! Good, now go install all the external libraries and build amazing apps! Pip, pip, hooray!
             """,
             "incorrect_audio_script": """
                Personal Internet Provider? My friend, this installs packages! CommandNotFoundError: pip! Were you checking your internet connection instead of coding?
             """},
             {"question": "What is a lambda function in Python?", "correct_answer": "anonymous function",
             "correct_audio_script": """
                Lambda! The anonymous, concise, and powerful function! Good, now write some elegant one-liners! Lambda created! Go embrace functional programming!
             """,
             "incorrect_audio_script": """
                Small function? Inline function? My friend, it's an anonymous function! SyntaxError: invalid lambda expression! Did you forget the function's name too?
             """},
             {"question": "What is the key difference between '==' and 'is' in Python?", "correct_answer": "equality vs identity",
             "correct_audio_script": """
                Equality versus identity! This distinction is super important in Python! Good, now you'll compare objects like a true connoisseur! Comparison logic clear!
             """,
             "incorrect_audio_script": """
                Are they the same? Oh man, one checks value, the other memory location! TypeError: invalid comparison! Did you get confused, or just guess?
             """},
             {"question": "What is a generator expression in Python?", "correct_answer": "lazy evaluation",
             "correct_audio_script": """
                Lazy evaluation! Generator expressions save memory like a boss! Good, now write efficient code that sips memory, not gulps it! Memory optimized!
             """,
             "incorrect_audio_script": """
                It's like list comprehension, but it eats memory? No, man, it saves memory! SyntaxError: invalid generator expression! Maybe a little more study is in order?
             """},
             {"question": "How do you handle multiple exceptions in a single 'except' block?", "correct_answer": "tuple of exception types",
             "correct_audio_script": """
                Tuple of exception types! Handle multiple errors in one elegant block! Good, now you'll do robust error handling like a pro! Error handling simplified!
             """,
             "incorrect_audio_script": """
                Multiple except blocks? No, man, use a tuple! TypeError: exceptions must derive from BaseException! You even got an error in error handling!
             """},
             {"question": "What is the purpose of the 'pass' statement in Python?", "correct_answer": "placeholder",
             "correct_audio_script": """
                Placeholder! When you've got nothing to do, just 'pass'! Good, now you won't get syntax errors for empty blocks! Code structure maintained!
             """,
             "incorrect_audio_script": """
                Skip? Ignore? My friend, this is just a placeholder! SyntaxError: expected an indented block! Empty code won't run, you know!
             """},
             {"question": "What is a 'docstring' in Python?", "correct_answer": "documentation string",
             "correct_audio_script": """
                Documentation string! A docstring is your code's self-explanation, a beautiful narrative! Good, now make your code self-documenting and tell its story!
                Code clarity improved! Now just write readable code!
             """,
             "incorrect_audio_script": """
                Comment? String literal? No, man, this is for documentation!
                SyntaxError: invalid string! Are you confused about what documentation is for?
             """},
             {"question": "How do you reverse a list in Python in-place?", "correct_answer": "list.reverse()",
             "correct_audio_script": """
                List dot reverse! Reverse the list right where it stands! Good, now you're an expert in list manipulation!
                List reversed! Now go turn your data upside down and inside out!
             """,
             "incorrect_audio_script": """
                Reversed() function? Slice[::-1]? No, man, it's the list dot reverse() method!
                AttributeError: 'list' object has no attribute 'reversed'! Are you confused about reversing things?
             """},
             {"question": "What is the purpose of 'enumerate()' function?", "correct_answer": "iterate with index",
             "correct_audio_script": """
                Iterate with index! The enumerate function is your best friend for iterating with an index! Good, now use that index in your loops!
                Indexed iteration simplified! Now go track every single item in your data!
             """,
             "incorrect_audio_script": """
                Count? Number? No, man, this iterates with an index!
                TypeError: 'int' object is not iterable! Did you get confused with counting?
             """},
             {"question": "How do you remove duplicate elements from a list while preserving order?", "correct_answer": "using OrderedDict or custom loop",
             "correct_audio_script": """
                Using OrderedDict or a custom loop! Remove duplicates and keep that order intact! Good, now create some perfectly clean lists!
                Duplicates removed! Now go handle unique data like a boss!
             """,
             "incorrect_audio_script": """
                Set conversion? No, man, the order won't be preserved!
                TypeError: unhashable type: 'list'! Are you confused about duplicates?
             """},
             {"question": "What is the purpose of 'collections.Counter'?", "correct_answer": "counts hashable objects",
             "correct_audio_script": """
                Counts hashable objects! Counter collection is Python's counting magic! Good, now count frequencies like a data scientist!
                Counting simplified! Now go analyze some data!
             """,
             "incorrect_audio_script": """
                List count? Dictionary count? No, man, this counts hashable objects!
                TypeError: unhashable type: 'list'! Are you confused about counting?
             """},
             {"question": "How do you implement a singleton pattern in Python?", "correct_answer": "using metaclass or decorator",
             "correct_audio_script": """
                Using metaclass or decorator! The Singleton pattern is Python's way of creating unique objects! Good, now create single instances!
                Object creation mastered! Now go handle global objects!
             """,
             "incorrect_audio_script": """
                Global variable? Class variable? No, man, this is a singleton pattern!
                TypeError: cannot instantiate multiple times! Are you confused about singletons?
             """},
             {"question": "What is the purpose of 'weakref' module in Python?", "correct_answer": "creates weak references to objects",
             "correct_audio_script": """
                Creates weak references to objects! The Weakref module is for memory management! Good, now you'll do memory efficient caching!
                Memory optimized! Now go handle large object graphs!
             """,
             "incorrect_audio_script": """
                Strong reference? Hard reference? No, man, this creates weak references!
                TypeError: cannot create weak reference to 'int' object! Are you confused about weak references?
             """},
             {"question": "Explain the 'LEGB' rule in Python for name resolution.", "correct_answer": "Local, Enclosing, Global, Built-in",
             "correct_audio_script": """
                Local, Enclosing, Global, Built-in! The LEGB rule is Python's name resolution mantra! Good, now you're an expert in variable scope!
                Scope understood! Now go avoid name conflicts!
             """,
             "incorrect_audio_script": """
                LEGB? Legs? No, man, this is the name resolution order!
                NameError: name 'legb' is not defined! Did you get confused about the path?
             """},
             {"question": "What is the purpose of 'collections.namedtuple'?", "correct_answer": "factory function for creating tuple subclasses with named fields",
             "correct_audio_script": """
                Factory function for creating tuple subclasses with named fields! Namedtuple makes data structures super readable! Good, now create readable data structures!
                Data structures improved! Now go write clean code!
             """,
             "incorrect_audio_script": """
                Named list? Named dictionary? No, man, this creates tuple subclasses!
                TypeError: 'str' object is not callable! Are you confused about namedtuples?
             """},
             {"question": "How do you implement a custom iterator in Python?", "correct_answer": "implement __iter__ and __next__ methods",
             "correct_audio_script": """
                Implement iter and next methods! A custom iterator is Python's data traversal superpower! Good, now traverse custom data structures!
                Data traversal mastered! Now go build efficient loops!
             """,
             "incorrect_audio_script": """
                Are you writing a loop? No, man, this is a custom iterator!
                TypeError: 'object' is not an iterator! Are you confused about iterators?
             """},
             {"question": "What is the difference between 'isinstance()' and 'issubclass()'?", "correct_answer": "isinstance checks object type, issubclass checks class inheritance",
             "correct_audio_script": """
                Isinstance checks object type, issubclass checks class inheritance! The sacred knowledge of type checking! Good, now check object types and class hierarchy correctly!
                Type checking mastered! Now go do robust type validation!
             """,
             "incorrect_audio_script": """
                Are they the same? No, man, one checks object type, the other class inheritance!
                TypeError: 'type' object is not callable! Are you confused about type checking?
             """},
             {"question": "Explain the concept of 'descriptors' in Python.", "correct_answer": "objects that implement __get__, __set__, or __delete__",
             "correct_audio_script": """
                Objects that implement get, set, or delete! Descriptors are Python's advanced attribute control! Good, now implement custom attribute behavior!
                Attribute control mastered! Now go build advanced classes!
             """,
             "incorrect_audio_script": """
                Description? Are you telling a story? No, man, this customizes attribute access!
                TypeError: 'object' is not a descriptor! Are you confused about descriptors?
             """},
             {"question": "What is the purpose of 'abc' module in Python?", "correct_answer": "provides infrastructure for defining abstract base classes",
             "correct_audio_script": """
                Provides infrastructure for defining abstract base classes! The ABC module is Python's abstract classes base! Good, now define abstract interfaces!
                Abstract interfaces understood! Now go build robust APIs!
             """,
             "incorrect_audio_script": """
                Abstract class? Interface? No, man, this provides infrastructure!
                TypeError: cannot instantiate abstract class! Are you confused about ABCs?
             """},
             {"question": "How do you implement a custom context manager using a decorator?", "correct_answer": "using @contextlib.contextmanager",
             "correct_audio_script": """
                Using contextlib dot contextmanager! Custom context manager with a decorator! Good, now do elegant resource management!
                Resource management simplified! Now go write clean code!
             """,
             "incorrect_audio_script": """
                Manual context manager? No, man, this can also be done with a decorator!
                TypeError: 'function' object is not a context manager! Are you confused about context managers?
             """},
             {"question": "What is the purpose of 'functools.partial'?", "correct_answer": "creates a new function with some arguments pre-filled",
             "correct_audio_script": """
                Creates a new function with some arguments pre-filled! Partial function application is Python's function customization! Good, now create flexible functions!
                Function customization mastered! Now go write reusable code!
             """,
             "incorrect_audio_script": """
                Function copy? Function clone? No, man, this pre-fills arguments!
                TypeError: 'function' object is not callable! Are you confused about partials?
             """},
        ],
        "expert": [
            {"question": "Describe Python's Global Interpreter Lock (GIL) in detail.", "correct_answer": "prevents multiple native threads from executing Python bytecodes at once",
             "correct_audio_script": """
                Ah, the GIL! Python's single-threaded masterpiece, misunderstood by many! Good, now use multiprocessing to truly unleash parallel power! GIL understood! Go conquer parallel processing!
             """,
             "incorrect_audio_script": """
                The GIL? Oh, that's like, when Python locks up your entire computer, right? No, my friend! This is a thread matter, not your PC freezing! SystemError: interpreter_lock_not_held! Your PC just crashed... metaphorically!
             """},
            {"question": "Explain metaclasses in Python.", "correct_answer": "classes that create classes",
             "correct_audio_script": """
                Metaclasses! The architects of classes themselves, mind-bending stuff! Good, now you're an expert in advanced object-oriented programming! Metaclass created! Go control classes at a whole new level!
             """,
             "incorrect_audio_script": """
                Metaclasses? Did you think too advanced, or just Google it? TypeError: metaclass conflict! Even Google got confused by that one!
             """},
            {"question": "What is the purpose of 'asyncio' in Python?", "correct_answer": "asynchronous I/O",
             "correct_audio_script": """
                Asyncio! The magic of non-blocking operations! Good, now I/O operations will be lightning fast! Asyncio activated! Go build high-performance, responsive apps!
             """,
             "incorrect_audio_script": """
                Asynchronous? Meaning, it runs whenever it feels like it? No, this is for efficiency, my friend! RuntimeError: Cannot run the event loop while another loop is running! Your timing is off!
             """},
            {"question": "How do you implement a custom context manager?", "correct_answer": "with statement, __enter__, __exit__",
             "correct_audio_script": """
                Context manager! The boss of resource handling! Good, now resources will be managed automatically, no more leaks! Context managed! Go do clean resource management!
             """,
             "incorrect_audio_script": """
                Manager? Are you in the office? Use __enter__ and __exit__ methods! AttributeError: __enter__! Did you forget your office work?
             """},
            {"question": "What are descriptors in Python?", "correct_answer": "objects that implement __get__, __set__, or __delete__",
             "correct_audio_script": """
                Descriptors! Powerful objects that control attributes! Good, now customize attribute access and become an attribute wizard! Descriptor applied! Go create some custom attributes!
             """,
             "incorrect_audio_script": """
                Description? Are you telling a story? Say get, set, delete methods! AttributeError: __get__! You have a hobby of storytelling, don't you?
             """},
            {"question": "Explain the difference between coroutines and threads.", "correct_answer": "coroutines are cooperative, threads are preemptive",
             "correct_audio_script": """
                Coroutines cooperative, threads preemptive! The difference is crystal clear! Good, now you're an expert in concurrency models! Concurrency understood! Go build concurrent apps!
             """,
             "incorrect_audio_script": """
                One waits for the other, the other stops forcefully! It's simple! RuntimeError: cannot switch to a different thread! Context switch happened... in your brain!
             """},
            {"question": "What is monkey patching in Python?", "correct_answer": "modifying a class or module at runtime",
             "correct_audio_script": """
                Monkey patching! Changing code at runtime, big risk, big fun! Good, but use with caution, you mischievous coder! Code modified! Go modify existing code!
             """,
             "incorrect_audio_script": """
                Monkey? Is this a monkey's game? It's called runtime modification! TypeError: can't set attributes of built-in type! You just made a monkey out of it!
             """},
            {"question": "How does Python handle memory management?", "correct_answer": "reference counting and garbage collection",
             "correct_audio_script": """
                Reference counting and garbage collection! Python's sophisticated cleaning campaign! Good, now there won't be memory leaks! Memory managed! Go write efficient code!
             """,
             "incorrect_audio_script": """
                Manual memory management? My friend, I'll do it myself, don't you worry! MemoryError: unable to allocate memory! Memory leak happened!
             """},
            {"question": "What are abstract base classes (ABCs) and why are they used?", "correct_answer": "define interfaces, prevent instantiation",
             "correct_audio_script": """
                ABCs! They define interfaces, objects are not created! Good, now define abstract interfaces and build robust APIs! Interface defined!
             """,
             "incorrect_audio_script": """
                Abstract? Meaning, only for thinking? They are interfaces, my friend! TypeError: Can't instantiate abstract class! It became abstract!
             """},
            {"question": "Discuss the implications of mutable default arguments in Python functions.", "correct_answer": "shared state across calls",
             "correct_audio_script": """
                Mutable default arguments! The danger of shared state, beware! Good, now there won't be side effects! Function arguments understood! Go create clean function signatures!
             """,
             "incorrect_audio_script": """
                Default argument changed? Not my fault, it's your fault! TypeError: unexpected keyword argument! Default arguments confusion!
             """},
             {"question": "Explain the concept of 'MRO' (Method Resolution Order) in Python.", "correct_answer": "order in which methods are searched in inheritance hierarchy",
             "correct_audio_script": """
                Method Resolution Order! MRO is Python's inheritance rulebook! Good, now there won't be mistakes in method lookup! Inheritance hierarchy understood! Go create complex class designs!
             """,
             "incorrect_audio_script": """
                MRO? Where is my path? No, my friend, this is the method lookup order! AttributeError: 'super' object has no attribute 'mro'! Did you get lost on the way?
             """},
             {"question": "What are weak references in Python and when are they useful?", "correct_answer": "references that don't prevent garbage collection",
             "correct_audio_script": """
                References that don't prevent garbage collection! Weak references are for memory efficient caching! Good, now you'll do memory efficient caching!
                Memory optimized! Now go handle large object graphs!
             """,
             "incorrect_audio_script": """
                Weak sauce? Weak link? No, my friend, this is a memory management concept! TypeError: cannot create weak reference to 'int' object! It's not weak!
             """},
             {"question": "Describe the 'with' statement and its underlying mechanism.", "correct_answer": "context manager protocol",
             "correct_audio_script": """
                Context manager protocol! The 'with' statement is Python's resource handling boss! Good, now resources will be managed automatically, no more leaks!
                Resource management simplified! Now go write clean code!
             """,
             "incorrect_audio_script": """
                Is it like an if statement? No, my friend, this is for resource management! SyntaxError: invalid 'with' statement! Are you confused about context?
             """},
             {"question": "What is the difference between 'threading' and 'multiprocessing' modules?", "correct_answer": "threading uses GIL, multiprocessing uses separate processes",
             "correct_audio_script": """
                Threading uses GIL, multiprocessing uses separate processes! The sacred knowledge of concurrency! Good, now you're an expert in parallel programming!
                Parallel processing understood! Now go build high-performance apps!
             """,
             "incorrect_audio_script": """
                Are they the same? No, my friend, one uses GIL, the other separate processes! RuntimeError: cannot start new thread! Concurrency confusion!
             """},
             {"question": "Explain how Python handles circular references in garbage collection.", "correct_answer": "cycle detector",
             "correct_audio_script": """
                Cycle detector! Python handles circular references like a detective! Good, now there won't be memory leaks!
                Memory managed! Now go build complex data structures!
             """,
             "incorrect_audio_script": """
                Infinite loop? No, my friend, this is a memory management concept! MemoryError: unable to allocate memory! Circular reference confusion!
             """},
             {"question": "What is the purpose of the 'slots' attribute in Python classes?", "correct_answer": "saves memory by preventing creation of __dict__",
             "correct_audio_script": """
                Saves memory by preventing creation of __dict__! The 'slots' attribute is for memory optimization! Good, now create memory efficient classes!
                Memory optimized! Now go handle large object instances!
             """,
             "incorrect_audio_script": """
                Slots machine? Casino? No, my friend, this is for memory optimization!
                AttributeError: '__slots__' must be a string or iterable! Slots confusion!
             """},
             {"question": "Describe Python's 'descriptor protocol' in detail.", "correct_answer": "mechanism for customizing attribute access",
             "correct_audio_script": """
                Mechanism for customizing attribute access! The Descriptor protocol is Python's advanced attribute control! Good, now implement custom attribute behavior!
                Attribute control mastered! Now go build advanced classes!
             """,
             "incorrect_audio_script": """
                Protocol? Rules? No, my friend, this customizes attribute access!
                TypeError: 'object' is not a descriptor! Protocol confusion!
             """},
             {"question": "What is the difference between 'abstractmethod' and 'abstractproperty' decorators?", "correct_answer": "abstractmethod for methods, abstractproperty for properties",
             "correct_audio_script": """
                Abstractmethod for methods, abstractproperty for properties! The ABCs knowledge! Good, now define abstract interfaces!
                Abstract interfaces understood! Now go build robust APIs!
             """,
             "incorrect_audio_script": """
                Are they the same? No, my friend, one is for methods, the other for properties!
                TypeError: 'function' object is not a property! Abstract confusion!
             """},
             {"question": "Explain the concept of 'co-routines' in Python.", "correct_answer": "generalized subroutines that can be paused and resumed",
             "correct_audio_script": """
                Generalized subroutines that can be paused and resumed! Co-routines are Python's asynchronous programming power! Good, now do non-blocking I/O operations!
                Asynchronous programming mastered! Now go build high-concurrency apps!
             """,
             "incorrect_audio_script": """
                Threads? Functions? No, my friend, these can be paused and resumed!
                CompilationError: invalid coroutine! Are you confused about coroutines?
             """},
             {"question": "What is the purpose of 'collections.namedtuple'?", "correct_answer": "factory function for creating tuple subclasses with named fields",
             "correct_audio_script": """
                Factory function for creating tuple subclasses with named fields! Namedtuple makes data structures super readable! Good, now create readable data structures!
                Data structures improved! Now go write clean code!
             """,
             "incorrect_audio_script": """
                Named list? Named dictionary? No, man, this creates tuple subclasses!
                TypeError: 'str' object is not callable! Are you confused about namedtuples?
             """},
             {"question": "How do you implement a custom iterator in Python?", "correct_answer": "implement __iter__ and __next__ methods",
             "correct_audio_script": """
                Implement iter and next methods! A custom iterator is Python's data traversal superpower! Good, now traverse custom data structures!
                Data traversal mastered! Now go build efficient loops!
             """,
             "incorrect_audio_script": """
                Are you writing a loop? No, man, this is a custom iterator!
                TypeError: 'object' is not an iterator! Are you confused about iterators?
             """},
             {"question": "What is the difference between 'isinstance()' and 'issubclass()'?", "correct_answer": "isinstance checks object type, issubclass checks class inheritance",
             "correct_audio_script": """
                Isinstance checks object type, issubclass checks class inheritance! The sacred knowledge of type checking! Good, now check object types and class hierarchy correctly!
                Type checking mastered! Now go do robust type validation!
             """,
             "incorrect_audio_script": """
                Are they the same? No, man, one checks object type, the other class inheritance!
                TypeError: 'type' object is not callable! Are you confused about type checking?
             """},
             {"question": "Explain the concept of 'descriptors' in Python.", "correct_answer": "objects that implement __get__, __set__, or __delete__",
             "correct_audio_script": """
                Objects that implement get, set, or delete! Descriptors are Python's advanced attribute control! Good, now implement custom attribute behavior!
                Attribute control mastered! Now go build advanced classes!
             """,
             "incorrect_audio_script": """
                Description? Are you telling a story? No, man, this customizes attribute access!
                TypeError: 'object' is not a descriptor! Are you confused about descriptors?
             """},
             {"question": "What is the purpose of 'abc' module in Python?", "correct_answer": "provides infrastructure for defining abstract base classes",
             "correct_audio_script": """
                Provides infrastructure for defining abstract base classes! The ABC module is Python's abstract classes base! Good, now define abstract interfaces!
                Abstract interfaces understood! Now go build robust APIs!
             """,
             "incorrect_audio_script": """
                Abstract class? Interface? No, man, this provides infrastructure!
                TypeError: cannot instantiate abstract class! Are you confused about ABCs?
             """},
             {"question": "How do you implement a custom context manager using a decorator?", "correct_answer": "using @contextlib.contextmanager",
             "correct_audio_script": """
                Using contextlib dot contextmanager! Custom context manager with a decorator! Good, now do elegant resource management!
                Resource management simplified! Now go write clean code!
             """,
             "incorrect_audio_script": """
                Manual context manager? No, man, this can also be done with a decorator!
                TypeError: 'function' object is not a context manager! Are you confused about context managers?
             """},
             {"question": "What is the purpose of 'functools.partial'?", "correct_answer": "creates a new function with some arguments pre-filled",
             "correct_audio_script": """
                Creates a new function with some arguments pre-filled! Partial function application is Python's function customization! Good, now create flexible functions!
                Function customization mastered! Now go write reusable code!
             """,
             "incorrect_audio_script": """
                Function copy? Function clone? No, man, this pre-fills arguments!
                TypeError: 'function' object is not callable! Are you confused about partials?
             """},
        ]
    },
    "java": {
        "beginner": [
            {"question": "Which keyword is used to define a class in Java?", "correct_answer": "class",
             "correct_audio_script": """
                'Class'! The sacred keyword for Java class definition! That's its identity! Good, now start your object-oriented journey! Your code is clean, go forth and build!
             """,
             "incorrect_audio_script": """
                'Struct'? 'Module'? It's 'class', my friend! Clear your basics! SyntaxError: invalid syntax! Are you confused about the basics?
             """},
            {"question": "What is the entry point method for a Java application?", "correct_answer": "main",
             "correct_audio_script": """
                'Main' method! Where everything begins! Good, now your Java apps will run! Application started! Go write some complex logic!
             """,
             "incorrect_audio_script": """
                'Start'? 'Run'? My friend, write 'public static void main'! NoSuchMethodError: main! Are you confused about the entry point?
             """},
            {"question": "Which keyword is used for inheritance in Java?", "correct_answer": "extends",
             "correct_audio_script": """
                'Extends'! The way to inherit properties from a parent! Good, now you're an expert in inheritance! Inheritance applied! Go build some class hierarchies!
             """,
             "incorrect_audio_script": """
                'Inherit'? 'Derive'? It's 'extends', simple! SyntaxError: invalid keyword! Are you confused about inheritance?
             """},
            {"question": "What is the default value of a boolean variable in Java?", "correct_answer": "false",
             "correct_audio_script": """
                False! Java's default truth! Good, now you're an expert in boolean logic! Boolean value set! Go write some conditional statements!
             """,
             "incorrect_audio_script": """
                True? Null? My friend, boolean defaults to false! TypeError: incompatible types! Are you confused about default values?
             """},
            {"question": "Which access modifier means visible only within the class?", "correct_answer": "private",
             "correct_audio_script": """
                'Private'! Java's personal space! Good, now you're an expert in data hiding! Access controlled! Go encapsulate some data!
             """,
             "incorrect_audio_script": """
                'Public'? 'Protected'? Keep it 'private', privacy is important! AccessControlException: access denied! Are you confused about privacy?
             """},
            {"question": "What is the keyword to create an object in Java?", "correct_answer": "new",
             "correct_audio_script": """
                'New'! A new object, new hopes! Good, now create objects and bring your classes to life! Object created! Go create some instances!
             """,
             "incorrect_audio_script": """
                'Create'? 'Make'? My friend, it's the 'new' keyword! SyntaxError: invalid keyword! Are you confused about object creation?
             """},
            {"question": "Which loop executes at least once in Java?", "correct_answer": "do-while",
             "correct_audio_script": """
                'Do-while'! First action, then condition! Good, now you're an expert in loops! Loop executed! Go do some repetitive tasks!
             """,
             "incorrect_audio_script": """
                'While'? 'For'? My friend, 'do-while' will run at least once! SyntaxError: invalid loop! Are you confused about loops?
             """},
            {"question": "What is the superclass of all classes in Java?", "correct_answer": "Object",
             "correct_audio_script": """
                'Object'! The parent of all, the superclass of everything! Good, now you're an expert in class hierarchy! Hierarchy understood! Go override some common methods!
             """,
             "incorrect_audio_script": """
                'Class'? 'Main'? My friend, it's the 'Object' class! ClassNotFoundException: Object! Are you confused about the superclass?
             """},
            {"question": "Which keyword is used to handle exceptions in Java?", "correct_answer": "try",
             "correct_audio_script": """
                'Try'! The first step to catching errors! Good, now you'll do robust error handling! Exception handled! Go show some clean error messages!
             """,
             "incorrect_audio_script": """
                'Catch'? 'Throw'? My friend, start with 'try'! SyntaxError: invalid keyword! Are you confused about exception handling?
             """},
            {"question": "What is the operator for logical AND in Java?", "correct_answer": "&&",
             "correct_audio_script": """
                Double ampersand! When both are true! Good, now you're an expert in logical operations! Logical operation successful! Go write some complex conditions!
             """,
             "incorrect_audio_script": """
                'And'? Single ampersand? My friend, it's double ampersand! SyntaxError: invalid operator! Are you confused about operators?
             """},
             {"question": "What is a constructor in Java?", "correct_answer": "special method for object initialization",
             "correct_audio_script": """
                Special method for object initialization! Constructor is Java's object creation mantra! Good, now initialize objects correctly! Go create custom constructors!
             """,
             "incorrect_audio_script": """
                Normal method? Function? No, my friend, this is for object initialization! SyntaxError: invalid method! Are you confused about constructors?
             """},
             {"question": "Which keyword is used to prevent a method from being overridden?", "correct_answer": "final",
             "correct_audio_script": """
                'Final'! Prevent a method from being overridden! Good, now control method overriding! Method protected! Go write secure code!
             """,
             "incorrect_audio_script": """
                'Static'? 'Private'? No, my friend, use 'final'! AccessControlException: method overridden! Are you confused about overriding?
             """},
             {"question": "What is the purpose of 'static' keyword in a method?", "correct_answer": "belongs to the class, not an object",
             "correct_audio_script": """
                Belongs to the class, not an object! A static method is a class property! Good, now create class-level methods! Go create utility functions!
             """,
             "incorrect_audio_script": """
                'Global'? 'Common'? No, my friend, this belongs to the class! SyntaxError: invalid keyword! Are you confused about static?
             """},
             {"question": "What is the difference between 'throw' and 'throws'?", "correct_answer": "throw for single exception, throws for declaring exceptions",
             "correct_audio_script": """
                'Throw' for single exception, 'throws' for declaring exceptions! The knowledge of exception handling! Good, now manage exceptions correctly! Exception declared! Go do robust error handling!
             """,
             "incorrect_audio_script": """
                Are they the same? No, my friend, one throws an exception, the other declares it! SyntaxError: invalid keyword! Are you confused about exceptions?
             """},
             {"question": "What is an abstract class in Java?", "correct_answer": "class that cannot be instantiated and may have abstract methods",
             "correct_audio_script": """
                Class that cannot be instantiated and may have abstract methods! An abstract class is a blueprint! Good, now define interfaces! Abstract class created! Go create concrete implementations!
             """,
             "incorrect_audio_script": """
                Normal class? Interface? No, my friend, this is an abstract class! InstantiationError: cannot instantiate abstract class! It became abstract!
             """},
             {"question": "What is the default access modifier for members of a Java class?", "correct_answer": "default (package-private)",
             "correct_audio_script": """
                Default (package-private)! Java's default access! Good, now you're an expert in access control! Access controlled! Go create clean APIs!
             """,
             "incorrect_audio_script": """
                'Public'? 'Private'? No, my friend, it's default (package-private)! AccessControlException: access denied! Are you confused about default access?
             """},
             {"question": "Explain the concept of 'autoboxing' and 'unboxing'.", "correct_answer": "automatic conversion between primitive types and their wrapper classes",
             "correct_audio_script": """
                Automatic conversion between primitive types and their wrapper classes! Autoboxing and unboxing, Java's magic! Good, now you're an expert in primitive and wrapper types! Type conversion simplified!
             """,
             "incorrect_audio_script": """
                Boxing? Unboxing? No, my friend, this is type conversion! TypeError: incompatible types! Are you confused about boxing?
             """},
             {"question": "What is the 'hashCode()' method used for?", "correct_answer": "returns an integer hash code for the object",
             "correct_audio_script": """
                Returns an integer hash code for the object! The hashCode method is for object identification! Good, now you're an expert in collections! Object identified! Go use hash maps!
             """,
             "incorrect_audio_script": """
                Returns object address? Returns object name? No, my friend, this is a hash code! NullPointerException: hashCode! Are you confused about hash codes?
             """},
             {"question": "What is the purpose of the 'transient' keyword in Java?", "correct_answer": "prevents serialization of a field",
             "correct_audio_script": """
                Prevents serialization of a field! The 'transient' keyword is for data security! Good, now protect sensitive data! Data protected! Go build secure applications!
             """,
             "incorrect_audio_script": """
                'Temporary'? 'Volatile'? No, my friend, this prevents serialization! SerializationException: invalid class! Are you confused about transient?
             """},
             {"question": "What is the difference between 'Vector' and 'ArrayList'?", "correct_answer": "Vector is synchronized, ArrayList is not",
             "correct_audio_script": """
                Vector is synchronized, ArrayList is not! The knowledge of concurrency! Good, now use thread-safe collections! Collections understood! Go build concurrent applications!
             """,
             "incorrect_audio_script": """
                Are they the same? No, my friend, one is synchronized, the other is not! ConcurrentModificationException: concurrent modification! Are you confused about concurrency?
             """},
             {"question": "Explain the concept of 'JVM' (Java Virtual Machine).", "correct_answer": "abstract machine that enables computer to run Java programs",
             "correct_audio_script": """
                Abstract machine that enables computer to run Java programs! JVM is Java's core! Good, now your Java applications will run!
                JVM understood! Now go build cross-platform apps!
             """,
             "incorrect_audio_script": """
                Virtual box? Operating system? No, my friend, this runs Java programs!
                NoClassDefFoundError: JVM! Are you confused about JVM?
             """},
             {"question": "What is 'JIT' (Just-In-Time) compilation in Java?", "correct_answer": "compiles bytecode to native machine code at runtime",
             "correct_audio_script": """
                Compiles bytecode to native machine code at runtime! JIT compilation is Java's performance booster! Good, now build fast applications!
                Performance optimized! Now go build high-performance systems!
             """,
             "incorrect_audio_script": """
                Ahead-of-time compilation? No, my friend, this compiles at runtime!
                CompilationError: invalid bytecode! Are you confused about JIT?
             """},
             {"question": "What is the purpose of 'enum' in Java?", "correct_answer": "defines a set of named constants",
             "correct_audio_script": """
                Defines a set of named constants! Enum is Java's king of constants! Good, now define readable constants!
                Constants defined! Now go write clean code!
             """,
             "incorrect_audio_script": """
                Class? Interface? No, my friend, this defines named constants!
                SyntaxError: invalid enum! Are you confused about enum?
             """},
             {"question": "Explain 'Serialization' and 'Deserialization' in Java.", "correct_answer": "converting object to byte stream and vice versa",
             "correct_audio_script": """
                Converting object to byte stream and vice versa! Serialization and deserialization, Java's object persistence magic! Good, now store objects!
                Object persistence mastered! Now go transfer data!
             """,
             "incorrect_audio_script": """
                Data transfer? File I/O? No, my friend, this converts objects to byte streams!
                SerializationException: invalid class! Are you confused about serialization?
             """},
             {"question": "What is the difference between 'throw' and 'rethrow' in exception handling?", "correct_answer": "throw creates new exception, rethrow propagates existing exception",
             "correct_audio_script": """
                'Throw' creates new exception, 'rethrow' propagates existing exception! The advanced knowledge of exception handling! Good, now propagate exceptions correctly!
                Exception propagated! Now go do robust error handling!
             """,
             "incorrect_audio_script": """
                Are they the same? No, my friend, one throws a new exception, the other an existing one!
                SyntaxError: invalid throw! Are you confused about rethrowing?
             """},
             {"question": "What is the purpose of 'super' keyword in Java?", "correct_answer": "refers to immediate parent class object",
             "correct_audio_script": """
                Refers to immediate parent class object! The 'super' keyword is Java's parent class reference! Good, now you're an expert in inheritance!
                Inheritance managed! Now go override methods!
             """,
             "incorrect_audio_script": """
                'This'? Current class? No, my friend, this refers to the parent class!
                SyntaxError: invalid super! Are you confused about super?
             """},
             {"question": "Explain the concept of 'Garbage Collection' in Java.", "correct_answer": "automatic memory management",
             "correct_audio_script": """
                Automatic memory management! Garbage Collection is Java's cleaning campaign! Good, now there won't be memory leaks!
                Memory managed! Now go write efficient code!
             """,
             "incorrect_audio_script": """
                Manual memory management? No, my friend, this is automatic!
                OutOfMemoryError: Java heap space! Are you confused about GC?
             """},
             {"question": "What is the purpose of 'final' keyword on a class?", "correct_answer": "prevents inheritance",
             "correct_audio_script": """
                Prevents inheritance! The 'final' keyword prevents a class from being extended! Good, now control class design!
                Class protected! Now go write secure code!
             """,
             "incorrect_audio_script": """
                Prevents instantiation? Prevents method overriding? No, my friend, this prevents inheritance!
                CompilationError: cannot inherit from final class! Are you confused about final?
             """},
             {"question": "What is the difference between 'interface' and 'abstract class'?", "correct_answer": "interface fully abstract, abstract class can have concrete methods",
             "correct_audio_script": """
                Interface fully abstract, abstract class can have concrete methods! Java's design knowledge! Good, now use interfaces and abstract classes!
                Design patterns understood! Now go build flexible architectures!
             """,
             "incorrect_audio_script": """
                Are they the same? No, my friend, one is fully abstract, the other is not!
                InstantiationError: cannot instantiate interface! Are you confused about interfaces?
             """},
             {"question": "Explain 'Polymorphism' in Java.", "correct_answer": "ability of an object to take on many forms",
             "correct_audio_script": """
                Ability of an object to take on many forms! Polymorphism is Java's object-oriented magic! Good, now write flexible code!
                Polymorphism mastered! Now go implement dynamic behavior!
             """,
             "incorrect_audio_script": """
                Many classes? Many objects? No, my friend, this is an object taking many forms!
                ClassCastException: cannot cast! Are you confused about polymorphism?
             """},
             {"question": "What is the purpose of 'package' keyword in Java?", "correct_answer": "organizes classes into namespaces",
             "correct_audio_script": """
                Organizes classes into namespaces! The 'package' keyword is Java's code organization! Good, now create clean code structure!
                Code organization mastered! Now go handle large projects!
             """,
             "incorrect_audio_script": """
                Folder? Directory? No, my friend, this organizes classes!
                ClassNotFoundException: class in wrong package! Are you confused about packages?
             """},
             {"question": "What is the purpose of 'import' keyword in Java?", "correct_answer": "brings classes from other packages into current scope",
             "correct_audio_script": """
                Brings classes from other packages into current scope! The 'import' keyword is Java's class access! Good, now use external classes!
                Class access mastered! Now go write reusable code!
             """,
             "incorrect_audio_script": """
                Copy paste? Include? No, my friend, this brings classes into the current scope!
                CompilationError: cannot find symbol! Are you confused about imports?
             """},
        ],
        "expert": [
            {"question": "Explain the Java Memory Model (JMM).", "correct_answer": "defines how threads interact with memory",
             "correct_audio_script": """
                Java Memory Model! The JMM defines how threads interact with memory! Good, now you're an expert in concurrency! Memory model understood! Go build thread-safe applications!
             """,
             "incorrect_audio_script": """
                JMM? Jalebi Murabba Mithai? No, my friend, this is a matter of threads and memory! OutOfMemoryError: Java heap space! Are you confused about the memory model?
             """},
            {"question": "What are Java's concurrency utilities and how are they used?", "correct_answer": "ExecutorService, Future, Callable, locks",
             "correct_audio_script": """
                ExecutorService, Future, Callable, locks! Concurrency utilities, Java's parallel processing game! Good, now build concurrent applications! Concurrency mastered! Go build high-performance systems!
             """,
             "incorrect_audio_script": """
                Threads? Race conditions? Use utilities, life will be easy! RejectedExecutionException: task rejected! Are you confused about concurrency?
             """},
            {"question": "Describe the difference between 'synchronized' keyword and 'ReentrantLock'.", "correct_answer": "synchronized is implicit, ReentrantLock is explicit and more flexible",
             "correct_audio_script": """
                Synchronized is implicit, ReentrantLock is explicit and more flexible! The knowledge of locking! Good, now you're an expert in thread synchronization! Synchronization mastered! Go write deadlock-free code!
             """,
             "incorrect_audio_script": """
                Lock? Where's the key? The code is locked, my friend, not the house door! IllegalMonitorStateException: current thread not owner! Are you confused about locking?
             """},
            {"question": "What is reflection in Java and its use cases?", "correct_answer": "examining and modifying classes at runtime",
             "correct_audio_script": """
                Reflection! Examining and modifying classes at runtime! Java's power to inspect itself! Good, now build dynamic applications! Reflection mastered! Go build frameworks!
             """,
             "incorrect_audio_script": """
                Reflection? Is it showing my face? We look at the code's face, my friend! InvocationTargetException: null! Are you confused about reflection?
             """},
            {"question": "Explain the concept of custom annotations in Java.", "correct_answer": "metadata for code",
             "correct_audio_script": """
                Metadata for code! Custom Annotations! Java's way of giving special tags to code! Good, now build custom frameworks! Annotations created! Go generate some code!
             """,
             "incorrect_audio_script": """
                Notes? Comments? It's metadata, my friend, it works at compile-time! AnnotationTypeMismatchException: invalid type! Are you confused about annotations?
             """},
            {"question": "How do you implement a custom ClassLoader in Java?", "correct_answer": "extend ClassLoader, override findClass",
             "correct_audio_script": """
                Extend ClassLoader, override findClass! Custom ClassLoader! Java's own style of class loading! Good, now do dynamic class loading! Class loading mastered! Go build plugin architectures!
             """,
             "incorrect_audio_script": """
                Class not found? My friend, build a ClassLoader, load it yourself! NoClassDefFoundError: custom class! Are you confused about class loading?
             """},
            {"question": "Discuss the implications of using Java Native Interface (JNI).", "correct_answer": "interoperability with native code, platform dependent",
             "correct_audio_script": """
                Interoperability with native code, platform dependent! JNI! The meeting of Java and C++, a bit risky, full power! Good, now use native libraries! Native integration mastered! Go build high-performance systems!
             """,
             "incorrect_audio_script": """
                Native code? My friend, it will become platform dependent! Think about it! UnsatisfiedLinkError: no native library! Are you confused about JNI?
             """},
            {"question": "What are lambda expressions and functional interfaces in Java 8?", "correct_answer": "concise anonymous functions, single abstract method",
             "correct_audio_script": """
                Concise anonymous functions, single abstract method! Lambdas! Functional interfaces! Java 8's marvel! Good, now do functional programming! Functional programming mastered! Go write concise code!
             """,
             "incorrect_audio_script": """
                Anonymous class? My friend, use lambda, be modern! LambdaConversionException: invalid lambda! Are you confused about lambda?
             """},
            {"question": "Explain the principles of SOLID design in Java.", "correct_answer": "Single responsibility, Open/Closed, Liskov substitution, Interface segregation, Dependency inversion",
             "correct_audio_script": """
                Single responsibility, Open/Closed, Liskov substitution, Interface segregation, Dependency inversion! SOLID principles! The formula to make code strong! Good, now write maintainable code! Design principles mastered! Go build scalable architectures!
             """,
             "incorrect_audio_script": """
                Code spaghetti? Follow SOLID principles, my friend! DesignPatternError: invalid pattern! Are you confused about SOLID?
             """},
            {"question": "Describe the various garbage collection algorithms in JVM.", "correct_answer": "Serial, Parallel, CMS, G1, ZGC",
             "correct_audio_script": """
                Serial, Parallel, CMS, G1, ZGC! GC algorithms! The secret to JVM's cleaning! Good, now you're an expert in memory optimization! Memory optimized! Go build high-performance applications!
             """,
             "incorrect_audio_script": """
                Memory leak? Read GC algorithms, my friend! OutOfMemoryError: GC overhead limit exceeded! Are you confused about GC?
             """},
             {"question": "What is the difference between 'Executor' and 'ExecutorService'?", "correct_answer": "Executor is interface, ExecutorService is interface with lifecycle methods",
             "correct_audio_script": """
                Executor is interface, ExecutorService is interface with lifecycle methods! The knowledge of concurrency! Good, now use thread pools! Concurrency mastered! Go handle asynchronous tasks!
             """,
             "incorrect_audio_script": """
                Are they the same? No, my friend, one is an interface, the other its extension! RejectedExecutionException: task rejected! Are you confused about executors?
             """},
             {"question": "Explain the concept of 'Type Erasure' in Java Generics.", "correct_answer": "generics information is removed at compile time",
             "correct_audio_script": """
                Generics information is removed at compile time! Type Erasure! Java Generics' secret! Good, now you're an expert in type safety! Generics understood! Go build generic algorithms!
             """,
             "incorrect_audio_script": """
                Type missing? Type error? No, my friend, this removes type information at compile time! ClassCastException: cannot cast! Are you confused about type erasure?
             """},
             {"question": "What is the purpose of 'volatile' keyword in Java?", "correct_answer": "ensures visibility of changes to variables across threads",
             "correct_audio_script": """
                Ensures visibility of changes to variables across threads! The 'volatile' keyword is for thread synchronization! Good, now you're an expert in concurrent programming! Synchronization mastered! Go protect shared variables!
             """,
             "incorrect_audio_script": """
                'Temporary'? 'Transient'? No, my friend, this ensures visibility! ConcurrentModificationException: volatile! Are you confused about volatile?
             """},
             {"question": "Describe the 'Fork/Join Framework' in Java.", "correct_answer": "framework for parallelizing recursive tasks",
             "correct_audio_script": """
                Framework for parallelizing recursive tasks! The Fork/Join Framework is Java's parallel processing power! Good, now parallelize complex algorithms! Parallel processing mastered! Go do high-performance computations!
             """,
             "incorrect_audio_script": """
                Fork and spoon? No, my friend, this is for parallel computing! RejectedExecutionException: task rejected! Are you confused about Fork/Join?
             """},
             {"question": "What are 'Stream API' and its benefits in Java 8?", "correct_answer": "functional-style operations on collections, declarative code",
             "correct_audio_script": """
                Functional-style operations on collections, declarative code! Stream API is Java 8's data processing magic! Good, now do concise data processing! Data processing mastered! Go do functional programming!
             """,
             "incorrect_audio_script": """
                Input stream? Output stream? No, my friend, this is for operations on collections! NoSuchElementException: no element! Are you confused about streams?
             """},
             {"question": "Explain the concept of 'NIO' (New I/O) in Java.", "correct_answer": "non-blocking I/O operations",
             "correct_audio_script": """
                Non-blocking I/O operations! NIO is Java's solution for high-performance I/O! Good, now build non-blocking applications!
                I/O mastered! Now go build scalable network applications!
             """,
             "incorrect_audio_script": """
                Old I/O? Blocking I/O? No, my friend, this is for non-blocking I/O!
                IOException: invalid channel! Are you confused about NIO?
             """},
             {"question": "What is the purpose of 'ThreadLocal' in Java?", "correct_answer": "provides thread-local variables",
             "correct_audio_script": """
                Provides thread-local variables! ThreadLocal is for thread safety! Good, now use thread-safe variables!
                Thread safety mastered! Now go build concurrent applications!
             """,
             "incorrect_audio_script": """
                Global variable? Static variable? No, my friend, these are thread-local variables!
                NullPointerException: thread local! Are you confused about ThreadLocal?
             """},
             {"question": "Describe the 'CompletableFuture' class in Java.", "correct_answer": "asynchronous computation and composition",
             "correct_audio_script": """
                Asynchronous computation and composition! CompletableFuture is Java's asynchronous programming power! Good, now handle non-blocking tasks!
                Asynchronous programming mastered! Now go build complex asynchronous workflows!
             """,
             "incorrect_audio_script": """
                'Future'? 'Callback'? No, my friend, this is for asynchronous computation!
                CompletionException: incomplete future! Are you confused about CompletableFuture?
             """},
             {"question": "What is 'Optional' class in Java 8 and its benefits?", "correct_answer": "container object which may or may not contain a non-null value",
             "correct_audio_script": """
                Container object which may or may not contain a non-null value! The Optional class saves you from NullPointerExceptions! Good, now avoid null checks!
                Null safety mastered! Now go write clean code!
             """,
             "incorrect_audio_script": """
                Null? Empty? No, my friend, this is a container object!
                NoSuchElementException: no value present! Are you confused about Optional?
             """},
             {"question": "Explain the concept of 'Dependency Injection' (DI) in Java.", "correct_answer": "design pattern for managing dependencies",
             "correct_audio_script": """
                Design pattern for managing dependencies! Dependency Injection is Java's modular design mantra! Good, now write loosely coupled code!
                Modular design mastered! Now go build testable applications!
             """,
             "incorrect_audio_script": """
                Manual dependency management? No, my friend, this is a design pattern!
                NoUniqueBeanDefinitionException: duplicate bean! Are you confused about Dependency Injection?
             """},
             {"question": "What is 'JMX' (Java Management Extensions)?", "correct_answer": "technology for monitoring and managing applications",
             "correct_audio_script": """
                Technology for monitoring and managing applications! JMX is Java's monitoring power! Good, now monitor applications!
                Monitoring mastered! Now go manage production applications!
             """,
             "incorrect_audio_script": """
                Java XML? Java Mail? No, my friend, this is for monitoring!
                MBeanRegistrationException: invalid MBean! Are you confused about JMX?
             """},
             {"question": "Describe 'Class Loaders' in Java in detail.", "correct_answer": "responsible for loading classes into JVM",
             "correct_audio_script": """
                Responsible for loading classes into JVM! Class Loaders are Java's class loading core! Good, now do dynamic class loading!
                Class loading mastered! Now go build plugin architectures!
             """,
             "incorrect_audio_script": """
                Class not found? No, my friend, this loads classes!
                ClassNotFoundException: custom class! Are you confused about Class Loaders?
             """},
             {"question": "What is 'AOT' (Ahead-Of-Time) compilation in Java?", "correct_answer": "compiles Java bytecode to native machine code before runtime",
             "correct_audio_script": """
                Compiles Java bytecode to native machine code before runtime! AOT compilation is Java's startup performance booster! Good, now build fast startup applications!
                Performance optimized! Now go build native images!
             """,
             "incorrect_audio_script": """
                JIT compilation? No, my friend, this compiles before runtime!
                CompilationError: invalid bytecode! Are you confused about AOT?
             """},
             {"question": "Explain 'Generics' and 'Wildcards' in Java.", "correct_answer": "type safety at compile time, flexible type arguments",
             "correct_audio_script": """
                Type safety at compile time, flexible type arguments! Generics and wildcards are Java's type safety magic! Good, now use type-safe collections!
                Type safety mastered! Now go build generic algorithms!
             """,
             "incorrect_audio_script": """
                Object casting? Raw types? No, my friend, this is for type safety!
                ClassCastException: cannot cast! Are you confused about Generics?
             """},
             {"question": "What is the purpose of 'ServiceLoader' in Java?", "correct_answer": "discovers and loads service providers",
             "correct_audio_script": """
                Discovers and loads service providers! ServiceLoader is Java's plugin architecture tool! Good, now build extensible applications!
                Plugin architecture mastered! Now go build modular applications!
             """,
             "incorrect_audio_script": """
                Class loader? Factory? No, my friend, this loads service providers!
                ServiceConfigurationError: service not found! Are you confused about ServiceLoader?
             """},
        ]
    },
    "cpp": {
        "beginner": [
            {"question": "What is the operator used for dynamic memory allocation in C++?", "correct_answer": "new",
             "correct_audio_script": """
                'New'! The sacred operator for dynamic memory allocation in C++! New memory, new adventures! Good, now you're an expert in memory management! Memory allocated!
             """,
             "incorrect_audio_script": """
                'Malloc'? 'Alloc'? It's 'new', my friend! This isn't C! NameError: name 'malloc' is not defined! Is that the C influence again?
             """},
            {"question": "Which header file is used for input/output operations in C++?", "correct_answer": "iostream",
             "correct_audio_script": """
                'Iostream'! The heart of C++ input-output! Good, now perform I/O operations! I/O ready! Go build some console applications!
             """,
             "incorrect_audio_script": """
                'Stdio.h'? 'Conio.h'? It's 'iostream', my friend! FileNotFoundError: 'iostream'! Are you confused about header files?
             """},
            {"question": "What does 'cout' stand for in C++?", "correct_answer": "console output",
             "correct_audio_script": """
                Console output! 'Cout' is C++'s style for printing to the console! Good, now display some output! Output displayed! Go debug some more!
             """,
             "incorrect_audio_script": """
                'See-out'? No, console output! It's an output stream! SyntaxError: invalid identifier! Are you confused about output?
             """},
            {"question": "Which symbol is used to indicate a pointer in C++?", "correct_answer": "*",
             "correct_audio_script": """
                Star! The symbol of an address! Good, now you're an expert in pointers! Pointer created! Go play with memory!
             """,
             "incorrect_audio_script": """
                Ampersand? Hash? My friend, use a star, a star! SyntaxError: invalid operator! Are you confused about pointers?
             """},
            {"question": "What is the keyword for defining a constant in C++?", "correct_answer": "const",
             "correct_audio_script": """
                'Const'! The keyword for defining constants in C++! What doesn't change, is constant! Good, now define constants! Constants defined! Go handle immutable data!
             """,
             "incorrect_audio_script": """
                'Var'? 'Let'? It's 'const', my friend! Fixed value! SyntaxError: invalid keyword! Are you confused about constants?
             """},
            {"question": "Which operator is used for dereferencing a pointer?", "correct_answer": "*",
             "correct_audio_script": """
                Star! The way to grab the value! Good, now you're an expert in dereferencing! Value accessed! Go do some pointer arithmetic!
             """,
             "incorrect_audio_script": """
                Are you taking the address? My friend, if you want the value, use a star! Segmentation fault: invalid memory access! Are you confused about dereferencing?
             """},
            {"question": "What is the standard namespace in C++?", "correct_answer": "std",
             "correct_audio_script": """
                'Std'! The home of the standard library! Good, now use the standard library! Namespace used! Go use common functions!
             """,
             "incorrect_audio_script": """
                My_namespace? My friend, it's 'std', standard! NameError: name 'my_namespace' is not defined! Are you confused about namespaces?
             """},
            {"question": "Which loop is guaranteed to execute at least once in C++?", "correct_answer": "do-while",
             "correct_audio_script": """
                'Do-while'! First action, then condition! Good, now you're an expert in loops! Loop executed! Go do some repetitive tasks!
             """,
             "incorrect_audio_script": """
                'While'? 'For'? My friend, 'do-while' will run at least once! SyntaxError: invalid loop! Are you confused about loops?
             """},
            {"question": "What is the purpose of 'virtual' keyword in a function?", "correct_answer": "polymorphism",
             "correct_audio_script": """
                Polymorphism! The 'virtual' keyword is C++'s secret to runtime polymorphism! Good, now you're an expert in dynamic dispatch! Polymorphism applied! Go build flexible designs!
             """,
             "incorrect_audio_script": """
                'Abstract'? 'Override'? No, my friend, this is for polymorphism! SyntaxError: invalid keyword! Are you confused about virtual?
             """},
            {"question": "What is the difference between 'nullptr' and 'NULL' in C++?", "correct_answer": "nullptr is type-safe, NULL is macro",
             "correct_audio_script": """
                'Nullptr' is type-safe, 'NULL' is a macro! The knowledge of null in C++! Good, now avoid null pointer errors! Null pointer handled! Go write robust code!
             """,
             "incorrect_audio_script": """
                Are they the same? No, my friend, one is type-safe, the other a macro! TypeError: incompatible types! Are you confused about null?
             """},
             {"question": "What is a reference in C++?", "correct_answer": "alias for an existing variable",
             "correct_audio_script": """
                Alias for an existing variable! A reference is C++'s shortcut! Good, now use aliases!
                Alias created! Now go refer to data!
             """,
             "incorrect_audio_script": """
                Pointer? Copy? No, my friend, this is an alias!
                SyntaxError: invalid reference! Are you confused about references?
             """},
             {"question": "What is the purpose of 'const' keyword in a function parameter?", "correct_answer": "prevents modification of the parameter",
             "correct_audio_script": """
                Prevents modification of the parameter! The 'const' keyword is for data integrity! Good, now protect parameters!
                Parameter protected! Now go write secure code!
             """,
             "incorrect_audio_script": """
                Read-only? Immutable? No, my friend, this prevents modification!
                TypeError: cannot modify const parameter! Are you confused about const?
             """},
             {"question": "What is the difference between 'delete' and 'delete[]'?", "correct_answer": "delete for single object, delete[] for array of objects",
             "correct_audio_script": """
                'Delete' for single object, 'delete[]' for array of objects! The knowledge of memory deallocation! Good, now avoid memory leaks!
                Memory deallocated! Now go do clean memory management!
             """,
             "incorrect_audio_script": """
                Are they the same? No, my friend, one is for a single object, the other for an array!
                MemoryError: invalid deallocation! Are you confused about deletion?
             """},
             {"question": "What is 'RAII' (Resource Acquisition Is Initialization) in C++?", "correct_answer": "resource management technique",
             "correct_audio_script": """
                Resource Acquisition Is Initialization! RAII is C++'s resource management superhero! Good, now resources will be managed automatically!
                Resource management mastered! Now go write exception-safe code!
             """,
             "incorrect_audio_script": """
                Random access is important? No, my friend, this is a resource management technique!
                SyntaxError: invalid RAII! Are you confused about RAII?
             """},
             {"question": "What is the purpose of 'inline' keyword in C++?", "correct_answer": "suggests compiler to expand function call at compile time",
             "correct_audio_script": """
                Suggests compiler to expand function call at compile time! The 'inline' keyword is for performance optimization! Good, now make functions fast!
                Performance optimized! Now go optimize small functions!
             """,
             "incorrect_audio_script": """
                Always expand? Force inline? No, my friend, this is just a suggestion!
                CompilationError: inline function not expanded! Are you confused about inline?
             """},
             {"question": "What is the purpose of 'volatile' keyword in C++?", "correct_answer": "prevents compiler optimizations on a variable",
             "correct_audio_script": """
                Prevents compiler optimizations on a variable! The 'volatile' keyword is C++'s optimization control! Good, now you're an expert in hardware interaction!
                Optimization controlled! Now go do embedded systems programming!
             """,
             "incorrect_audio_script": """
                'Temporary'? 'Transient'? No, my friend, this prevents compiler optimizations!
                CompilationError: invalid volatile! Are you confused about volatile?
             """},
             {"question": "What is the difference between 'const' and '#define'?", "correct_answer": "const is type-safe, #define is preprocessor macro",
             "correct_audio_script": """
                'Const' is type-safe, '#define' is a preprocessor macro! The knowledge of constants in C++! Good, now define type-safe constants!
                Constants defined! Now go write clean code!
             """,
             "incorrect_audio_script": """
                Are they the same? No, my friend, one is type-safe, the other a macro!
                SyntaxError: invalid define! Are you confused about define?
             """},
             {"question": "What is the purpose of 'using namespace std;'?", "correct_answer": "brings all names from std namespace into current scope",
             "correct_audio_script": """
                Brings all names from 'std' namespace into current scope! 'Using namespace std;' is C++'s shortcut! Good, now use standard library functions!
                Namespace simplified! Now go write concise code!
             """,
             "incorrect_audio_script": """
                Import everything? No, my friend, this brings the namespace into the current scope!
                CompilationError: ambiguous symbol! Are you confused about namespaces?
             """},
             {"question": "What is the difference between 'array' and 'vector' in C++?", "correct_answer": "array fixed size, vector dynamic size",
             "correct_audio_script": """
                Array fixed size, vector dynamic size! The knowledge of collections in C++! Good, now use dynamic arrays!
                Collections understood! Now go build flexible data structures!
             """,
             "incorrect_audio_script": """
                Are they the same? No, my friend, one is fixed size, the other dynamic!
                MemoryError: invalid size! Are you confused about arrays and vectors?
             """},
             {"question": "What is 'friend class' in C++?", "correct_answer": "class whose member functions can access private and protected members of another class",
             "correct_audio_script": """
                Class whose member functions can access private and protected members of another class! A friend class is C++'s access control loophole! Good, now access private data!
                Access granted! Now go handle special cases!
             """,
             "incorrect_audio_script": """
                Inheritance? Nested class? No, my friend, this is a friend class!
                AccessControlException: private member access! Are you confused about friend classes?
             """},
             {"question": "What is the purpose of 'static_cast' in C++?", "correct_answer": "converts between related types at compile time",
             "correct_audio_script": """
                Converts between related types at compile time! Static cast is C++'s type conversion! Good, now do type-safe conversions!
                Type conversion mastered! Now go write clean code!
             """,
             "incorrect_audio_script": """
                Dynamic cast? Reinterpret cast? No, my friend, this converts at compile-time!
                TypeError: invalid cast! Are you confused about static cast?
             """},
             {"question": "What is 'dynamic_cast' in C++?", "correct_answer": "converts between polymorphic types at runtime",
             "correct_audio_script": """
                Converts between polymorphic types at runtime! Dynamic cast is C++'s runtime type conversion! Good, now you're an expert in runtime polymorphism!
                Type conversion mastered! Now go build flexible designs!
             """,
             "incorrect_audio_script": """
                Static cast? Reinterpret cast? No, my friend, this converts at runtime!
                TypeError: invalid cast! Are you confused about dynamic cast?
             """},
             {"question": "What is 'reinterpret_cast' in C++?", "correct_answer": "converts between unrelated types, low-level bit manipulation",
             "correct_audio_script": """
                Converts between unrelated types, low-level bit manipulation! Reinterpret cast is C++'s low-level magic! Good, now do bit manipulation!
                Low-level programming mastered! Now go play with memory!
             """,
             "incorrect_audio_script": """
                Static cast? Dynamic cast? No, my friend, this converts unrelated types!
                TypeError: invalid cast! Are you confused about reinterpret cast?
             """},
             {"question": "What is 'const_cast' in C++?", "correct_answer": "removes constness from a variable",
             "correct_audio_script": """
                Removes constness from a variable! Const cast is C++'s const manipulation! Good, now modify const variables!
                Const manipulation mastered! Now go handle legacy code!
             """,
             "incorrect_audio_script": """
                Static cast? Dynamic cast? No, my friend, this removes constness!
                TypeError: cannot cast const! Are you confused about const cast?
             """},
        ],
        "intermediate": [
            {"question": "Explain the difference between 'pass by value' and 'pass by reference'.", "correct_answer": "value copies, reference uses original",
             "correct_audio_script": """
                Value copies, reference uses original! That's the core game of C++! Good, now you're an expert in function parameters! Parameters understood! Go make efficient function calls!
             """,
             "incorrect_audio_script": """
                Pass by... what? One creates a copy, the other uses the original! SyntaxError: invalid argument passing! Are you confused about passing?
             """},
            {"question": "What is a destructor in C++?", "correct_answer": "special member function called when object is destroyed",
             "correct_audio_script": """
                Special member function called when object is destroyed! A destructor is C++'s final farewell to an object! Good, now memory will be clean! Memory deallocated! Go do some resource cleanup!
             """,
             "incorrect_audio_script": """
                Garbage collector? No automatic cleanup, my friend! Write a destructor! MemoryError: memory leak! Are you confused about destructors?
             """},
            {"question": "What is operator overloading?", "correct_answer": "redefining operators for custom types",
             "correct_audio_script": """
                Redefining operators for custom types! Operator Overloading! The fun way to give operators a new form! Good, now define operators for custom types! Operator overloaded! Go use operators in custom classes!
             """,
             "incorrect_audio_script": """
                Operator... what now? Change plus to minus, if you feel like it! TypeError: unsupported operand type(s)! No magic happened for you!
             """},
            {"question": "Describe the concept of 'RAII' in C++.", "correct_answer": "Resource Acquisition Is Initialization",
             "correct_audio_script": """
                Resource Acquisition Is Initialization! RAII! The superhero of resource management! Good, now resources will be managed automatically! Resource management mastered! Go write exception-safe code!
             """,
             "incorrect_audio_script": """
                Rai-rai? Resource Acquisition Is Initialization! Understood? SyntaxError: invalid RAII! Are you confused about RAII?
             """},
            {"question": "What is the difference between 'struct' and 'class' in C++?", "correct_answer": "struct default public, class default private",
             "correct_audio_script": """
                Struct default public, class default private! The game of defaults! Good, now you're an expert in access specifiers! Access controlled! Go build clean class designs!
             """,
             "incorrect_audio_script": """
                Are they the same? There's a difference in default access specifier, my friend! SyntaxError: invalid access specifier! Are you confused about struct and class?
             """},
             {"question": "What is a copy constructor in C++?", "correct_answer": "constructor that creates object by copying another object",
             "correct_audio_script": """
                Constructor that creates object by copying another object! A copy constructor is C++'s object copying mantra! Good, now you're an expert in object copying!
                Object copied! Now go do a deep copy!
             """,
             "incorrect_audio_script": """
                Normal constructor? Assignment operator? No, my friend, this copies an object!
                CompilationError: no matching constructor! Are you confused about copy constructors?
             """},
             {"question": "Explain the concept of 'virtual functions' in C++.", "correct_answer": "functions that can be overridden in derived classes and enable runtime polymorphism",
             "correct_audio_script": """
                Functions that can be overridden in derived classes and enable runtime polymorphism! Virtual functions are C++'s polymorphism secret! Good, now you're an expert in dynamic dispatch!
                Polymorphism applied! Now go build flexible designs!
             """,
             "incorrect_audio_script": """
                Normal functions? Static functions? No, my friend, these are for runtime polymorphism!
                SyntaxError: invalid virtual function! Are you confused about virtual?
             """},
             {"question": "What is the purpose of 'explicit' keyword in C++ constructors?", "correct_answer": "prevents implicit conversions",
             "correct_audio_script": """
                Prevents implicit conversions! The 'explicit' keyword is C++'s type safety! Good, now avoid implicit conversions!
                Type safety improved! Now go write robust code!
             """,
             "incorrect_audio_script": """
                Always convert? Force convert? No, my friend, this prevents implicit conversions!
                CompilationError: cannot convert! Are you confused about explicit?
             """},
             {"question": "What is a 'friend function' in C++?", "correct_answer": "non-member function that can access private and protected members of a class",
             "correct_audio_script": """
                Non-member function that can access private and protected members of a class! A friend function is C++'s access control loophole! Good, now access private data!
                Access granted! Now go handle special cases!
             """,
             "incorrect_audio_script": """
                Member function? Global function? No, my friend, this is a non-member function!
                AccessControlException: private member access! Are you confused about friend?
             """},
             {"question": "Explain 'move semantics' (rvalue references) in C++11.", "correct_answer": "efficient transfer of resources",
             "correct_audio_script": """
                Efficient transfer of resources! Move semantics is C++11's performance booster! Good, now do efficient resource transfer!
                Performance optimized! Now go build high-performance applications!
             """,
             "incorrect_audio_script": """
                Copy everything? No, my friend, this moves resources, not copies them!
                CompilationError: invalid move! Are you confused about move?
             """},
             {"question": "What is 'pure virtual function' in C++?", "correct_answer": "virtual function with = 0, makes class abstract",
             "correct_audio_script": """
                Virtual function with equals zero, makes class abstract! A pure virtual function is C++'s abstract class mantra! Good, now define abstract interfaces!
                Abstract interfaces understood! Now go build concrete implementations!
             """,
             "incorrect_audio_script": """
                Normal virtual function? No, my friend, this makes the class abstract!
                CompilationError: cannot instantiate abstract class! Are you confused about pure virtual?
             """},
             {"question": "What is the purpose of 'const_cast' in C++?", "correct_answer": "removes constness from a variable",
             "correct_audio_script": """
                Removes constness from a variable! Const cast is C++'s const manipulation! Good, now modify const variables!
                Const manipulation mastered! Now go handle legacy code!
             """,
             "incorrect_audio_script": """
                Static cast? Dynamic cast? No, my friend, this removes constness!
                TypeError: cannot cast const! Are you confused about const cast?
             """},
             {"question": "Explain 'smart pointers' in C++.", "correct_answer": "objects that manage memory automatically",
             "correct_audio_script": """
                Objects that manage memory automatically! Smart pointers are C++'s memory management superhero! Good, now no more memory leaks!
                Memory management mastered! Now go write modern C++!
             """,
             "incorrect_audio_script": """
                Raw pointers? Manual memory management? No, my friend, these manage memory automatically!
                MemoryError: memory leak! Are you confused about smart pointers?
             """},
             {"question": "What is the difference between 'std::array' and C-style array?", "correct_answer": "std::array is fixed size, bounds checking, container features",
             "correct_audio_script": """
                Std array is fixed size, bounds checking, container features! C++'s modern array! Good, now use safe arrays!
                Array management improved! Now go use efficient data structures!
             """,
             "incorrect_audio_script": """
                Are they the same? No, my friend, one is safe, the other is not!
                Segmentation fault: invalid memory access! Are you confused about arrays and vectors?
             """},
             {"question": "What is 'template metaprogramming' in C++?", "correct_answer": "using templates to perform computations at compile time",
             "correct_audio_script": """
                Using templates to perform computations at compile time! Template metaprogramming is C++'s compile-time magic! Good, now do compile-time optimizations!
                Compile-time magic mastered! Now go build advanced templates!
             """,
             "incorrect_audio_script": """
                Runtime programming? Dynamic programming? No, my friend, this performs computations at compile time!
                CompilationError: template instantiation failed! Are you confused about templates?
             """},
             {"question": "What is the purpose of 'std::unique_ptr'?", "correct_answer": "exclusive ownership of a dynamically allocated object",
             "correct_audio_script": """
                Exclusive ownership of a dynamically allocated object! Unique pointer is C++'s single ownership! Good, now no more memory leaks!
                Memory management mastered! Now go do clean resource management!
             """,
             "incorrect_audio_script": """
                Shared pointer? Raw pointer? No, my friend, this is exclusive ownership!
                MemoryError: invalid unique pointer! Are you confused about unique pointers?
             """},
             {"question": "What is 'std::shared_ptr'?", "correct_answer": "shared ownership of a dynamically allocated object",
             "correct_audio_script": """
                Shared ownership of a dynamically allocated object! Shared pointer is C++'s multiple ownership! Good, now manage shared resources!
                Memory management mastered! Now go handle complex object graphs!
             """,
             "incorrect_audio_script": """
                Unique pointer? Raw pointer? No, my friend, this is shared ownership!
                MemoryError: invalid shared pointer! Are you confused about shared pointers?
             """},
             {"question": "What is 'std::weak_ptr'?", "correct_answer": "non-owning reference to an object managed by shared_ptr",
             "correct_audio_script": """
                Non-owning reference to an object managed by shared_ptr! Weak pointer is C++'s circular dependency solution! Good, now avoid circular dependencies!
                Memory management mastered! Now go handle complex object graphs!
             """,
             "incorrect_audio_script": """
                Unique pointer? Shared pointer? No, my friend, this is a non-owning reference!
                MemoryError: invalid weak pointer! Are you confused about weak pointers?
             """},
             {"question": "Explain 'polymorphic destruction' in C++.", "correct_answer": "ensuring correct destructor is called for derived classes through base class pointer",
             "correct_audio_script": """
                Ensuring correct destructor is called for derived classes through base class pointer! Polymorphic destruction is C++'s memory safety! Good, now avoid memory leaks!
                Memory safety mastered! Now go build clean inheritance hierarchies!
             """,
             "incorrect_audio_script": """
                Normal destruction? Static destruction? No, my friend, this calls the correct destructor!
                MemoryError: memory leak! Are you confused about polymorphic destruction?
             """},
             {"question": "What is 'std::function' in C++?", "correct_answer": "polymorphic function wrapper",
             "correct_audio_script": """
                Polymorphic function wrapper! Std function is C++'s flexible function objects! Good, now use function pointers!
                Function objects mastered! Now go build generic algorithms!
             """,
             "incorrect_audio_script": """
                Function pointer? Lambda? No, my friend, this is a polymorphic function wrapper!
                TypeError: invalid function! Are you confused about function?
             """},
             {"question": "What is 'std::bind' in C++?", "correct_answer": "adapts a function to different argument lists",
             "correct_audio_script": """
                Adapts a function to different argument lists! Std bind is C++'s function adaptation! Good, now build flexible function calls!
                Function adaptation mastered! Now go write reusable code!
             """,
             "incorrect_audio_script": """
                Function call? Function pointer? No, my friend, this adapts arguments!
                TypeError: invalid bind! Are you confused about bind?
             """},
             {"question": "What is 'std::move' in C++?", "correct_answer": "converts an lvalue to an rvalue reference",
             "correct_audio_script": """
                Converts an lvalue to an rvalue reference! Std move is C++'s move semantics tool! Good, now do efficient resource transfer!
                Move semantics mastered! Now go build high-performance applications!
             """,
             "incorrect_audio_script": """
                Copy? Assign? No, my friend, this converts an lvalue to an rvalue reference!
                TypeError: invalid move! Are you confused about move?
             """},
        ],
        "expert": [
            {"question": "Describe the C++ Standard Template Library (STL) components.", "correct_answer": "containers, algorithms, iterators, function objects",
             "correct_audio_script": """
                Containers, algorithms, iterators, function objects! The STL! C++'s ultimate arsenal, it has everything! Good, now use the standard library! STL mastered! Go use efficient data structures and algorithms!
             """,
             "incorrect_audio_script": """
                STL? Standard Toilet Library? No, my friend, these are templates! Containers, algorithms, iterators! SyntaxError: invalid template! Are you confused about STL?
             """},
            {"question": "Explain the 'Rule of Three/Five/Zero' in C++.", "correct_answer": "copy constructor, copy assignment, destructor",
             "correct_audio_script": """
                Copy constructor, copy assignment, destructor! The Rule of Three/Five/Zero! The sacred knowledge of object life cycle! Good, now no more memory leaks! Object life cycle managed! Go do clean resource management!
             """,
             "incorrect_audio_script": """
                Rule of what? Just code, bro! You'll get a memory leak, my friend! Follow the rules! MemoryError: memory leak! Are you confused about the rules?
             """},
            {"question": "What is SFINAE (Substitution Failure Is Not An Error) in C++ templates?", "correct_answer": "template metaprogramming technique",
             "correct_audio_script": """
                Substitution Failure Is Not An Error! SFINAE! When an error becomes a feature! Good, now use advanced templates! Template metaprogramming mastered! Go do compile-time magic!
             """,
             "incorrect_audio_script": """
                Sfi-what-now? This is advanced template magic, my friend! CompilationError: template substitution failed! Are you confused about SFINAE?
             """},
            {"question": "Discuss the implications of virtual inheritance.", "correct_answer": "solves diamond problem",
             "correct_audio_script": """
                Solves the diamond problem! Virtual Inheritance! The solution to the dreaded diamond problem! Good, now handle complex inheritance hierarchies! Inheritance managed! Go do multiple inheritance!
             """,
             "incorrect_audio_script": """
                Diamond problem? Your code just became a diamond! It's an inheritance issue, my friend! CompilationError: ambiguous base class! Are you confused about the diamond?
             """},
            {"question": "Explain move semantics (rvalue references) in C++11.", "correct_answer": "efficient transfer of resources",
             "correct_audio_script": """
                Efficient transfer of resources! Move semantics is C++11's performance booster! Good, now do efficient resource transfer! Performance optimized! Go build high-performance applications!
             """,
             "incorrect_audio_script": """
                Copy is best, right? No, my friend, this moves resources, not copies them! CompilationError: invalid move! Are you confused about move?
             """},
             {"question": "What is a 'perfect forwarding' in C++?", "correct_answer": "passing arguments while preserving their value category (lvalue/rvalue)",
             "correct_audio_script": """
                Passing arguments while preserving their value category! Perfect forwarding is C++'s template magic! Good, now build generic functions!
                Template metaprogramming mastered! Now go use universal references!
             """,
             "incorrect_audio_script": """
                Simple forwarding? No, my friend, this preserves value category!
                CompilationError: no matching function for call to 'forward'! Are you confused about forwarding?
             """},
             {"question": "Describe the concept of 'CRTP' (Curiously Recurring Template Pattern).", "correct_answer": "class derives from a template specialization of itself",
             "correct_audio_script": """
                Class derives from a template specialization of itself! CRTP is C++'s advanced template technique! Good, now implement static polymorphism!
                Template metaprogramming mastered! Now go do compile-time optimizations!
             """,
             "incorrect_audio_script": """
                Recursion? Infinite loop? No, my friend, this is a template pattern!
                CompilationError: recursive template instantiation! Are you confused about CRTP?
             """},
             {"question": "What is the purpose of 'placement new' in C++?", "correct_answer": "constructs object at a pre-allocated memory location",
             "correct_audio_script": """
                Constructs object at a pre-allocated memory location! Placement new is C++'s low-level memory control! Good, now build custom allocators!
                Memory management mastered! Now go do embedded systems programming!
             """,
             "incorrect_audio_script": """
                Normal new? Dynamic allocation? No, my friend, this constructs on pre-allocated memory!
                MemoryError: invalid placement! Are you confused about placement new?
             """},
             {"question": "Explain the 'std::variant' and 'std::visit' in C++17.", "correct_answer": "type-safe union, apply visitor to variant",
             "correct_audio_script": """
                Type-safe union, apply visitor to variant! Std variant and std visit are C++17's modern polymorphism! Good, now use type-safe unions!
                Modern C++ mastered! Now go build advanced data structures!
             """,
             "incorrect_audio_script": """
                Union? Switch case? No, my friend, this is a type-safe union!
                TypeError: invalid variant! Are you confused about variant?
             """},
             {"question": "What is the difference between 'std::async' and 'std::thread'?", "correct_answer": "std::async manages future, std::thread manages raw thread",
             "correct_audio_script": """
                Std async manages future, std thread manages raw thread! The knowledge of concurrency! Good, now handle asynchronous tasks!
                Concurrency mastered! Now go implement parallel algorithms!
             """,
             "incorrect_audio_script": """
                Are they the same? No, my friend, one manages a future, the other a raw thread!
                RuntimeError: cannot create thread! Are you confused about concurrency?
             """},
             {"question": "What is 'Pimpl Idiom' in C++?", "correct_answer": "pointer to implementation, hides implementation details",
             "correct_audio_script": """
                Pointer to implementation, hides implementation details! Pimpl Idiom is C++'s encapsulation secret! Good, now reduce compilation time!
                Encapsulation mastered! Now go build modular designs!
             """,
             "incorrect_audio_script": """
                Private implementation? Public implementation? No, my friend, this hides implementation details!
                CompilationError: undefined reference! Are you confused about Pimpl?
             """},
             {"question": "Describe 'Expression Templates' in C++.", "correct_answer": "compile-time technique to optimize numerical computations",
             "correct_audio_script": """
                Compile-time technique to optimize numerical computations! Expression Templates are C++'s performance booster! Good, now do high-performance numerical computations!
                Performance optimized! Now go do scientific computing!
             """,
             "incorrect_audio_script": """
                Runtime expressions? Dynamic expressions? No, my friend, this optimizes at compile-time!
                CompilationError: template instantiation failed! Are you confused about Expression Templates?
             """},
             {"question": "What is the purpose of 'std::enable_if' in C++ templates?", "correct_answer": "conditionally enables or disables template instantiations",
             "correct_audio_script": """
                Conditionally enables or disables template instantiations! Std enable if is C++'s template metaprogramming tool! Good, now build conditional templates!
                Template metaprogramming mastered! Now go build flexible templates!
             """,
             "incorrect_audio_script": """
                Always enable? Always disable? No, my friend, this conditionally enables!
                CompilationError: no matching function for call to 'enable_if'! Are you confused about enable_if?
             """},
             {"question": "Explain 'Coroutines' in C++20.", "correct_answer": "functions that can be suspended and resumed",
             "correct_audio_script": """
                Functions that can be suspended and resumed! Coroutines are C++20's asynchronous programming power! Good, now do non-blocking I/O operations!
                Asynchronous programming mastered! Now go build high-concurrency apps!
             """,
             "incorrect_audio_script": """
                Threads? Functions? No, my friend, these can be suspended and resumed!
                CompilationError: invalid coroutine! Are you confused about coroutines?
             """},
             {"question": "What is 'Concepts' in C++20?", "correct_answer": "mechanism to specify requirements on template parameters",
             "correct_audio_script": """
                Mechanism to specify requirements on template parameters! Concepts are C++20's template error handling solution! Good, now see readable template errors!
                Template error handling mastered! Now go build robust templates!
             """,
             "incorrect_audio_script": """
                Constraints? Rules? No, my friend, this specifies requirements on template parameters!
                CompilationError: constraint violation! Are you confused about Concepts?
             """},
             {"question": "What is 'std::jthread' in C++20?", "correct_answer": "thread that automatically joins on destruction",
             "correct_audio_script": """
                Thread that automatically joins on destruction! Std jthread is C++20's thread management solution! Good, now thread management will be simplified!
                Thread management mastered! Now go write clean concurrency code!
             """,
             "incorrect_audio_script": """
                Normal thread? Detached thread? No, my friend, this automatically joins!
                RuntimeError: cannot join thread! Are you confused about jthread?
             """},
             {"question": "Explain 'Modules' in C++20.", "correct_answer": "modern way to organize code, faster compilation, better encapsulation",
             "correct_audio_script": """
                Modern way to organize code, faster compilation, better encapsulation! Modules are C++20's code organization future! Good, now write modular code!
                Code organization mastered! Now go handle large projects!
             """,
             "incorrect_audio_script": """
                Header files? Preprocessor macros? No, my friend, this is a modern way!
                CompilationError: invalid module! Are you confused about Modules?
             """},
             {"question": "What is 'std::span' in C++20?", "correct_answer": "view over a contiguous sequence of objects",
             "correct_audio_script": """
                View over a contiguous sequence of objects! Std span is C++20's contiguous data view! Good, now use safe array views!
                Data view mastered! Now go do efficient data processing!
             """,
             "incorrect_audio_script": """
                Array? Vector? No, my friend, this is a view!
                TypeError: invalid span! Are you confused about span?
             """},
             {"question": "What is the purpose of 'std::format' in C++20?", "correct_answer": "type-safe and extensible text formatting",
             "correct_audio_script": """
                Type-safe and extensible text formatting! Std format is C++20's modern formatting! Good, now create clean output!
                Text formatting mastered! Now go generate readable output!
             """,
             "incorrect_audio_script": """
                Printf? Sprintf? No, my friend, this is type-safe formatting!
                TypeError: invalid format! Are you confused about format?
             """},
             {"question": "Explain 'Three-Way Comparison Operator' (spaceship operator) in C++20.", "correct_answer": "compares two values and returns ordering",
             "correct_audio_script": """
                Compares two values and returns ordering! The Three-Way Comparison Operator is C++20's comparison magic! Good, now compare custom types!
                Comparison mastered! Now go implement sorting algorithms!
             """,
             "incorrect_audio_script": """
                Less than? Greater than? No, my friend, this returns ordering!
                SyntaxError: invalid operator! Are you confused about the spaceship operator?
             """},
        ]
    }
}


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

def get_random_imgflip_template_info(is_correct):
    """
    Selects a random meme template, prioritizing dynamically fetched Imgflip memes,
    then hardcoded Imgflip IDs, and finally local fallback images.
    Logs the source of the image.
    """
    selected_meme = None
    source_description = ""

    used_ids_key = 'used_correct_meme_ids' if is_correct else 'used_incorrect_meme_ids'
    session.setdefault(used_ids_key, [])

    # Strategy 1: Try to get from the dynamically cached Imgflip memes
    if all_imgflip_memes_cache:
        available_from_cache = [m for m in all_imgflip_memes_cache if m['id'] not in session[used_ids_key]]
        if available_from_cache:
            selected_meme = random.choice(available_from_cache)
            session[used_ids_key].append(selected_meme['id'])
            source_description = "Imgflip (dynamically cached)"
            print(f"DEBUG: Image fetched from {source_description} (ID: {selected_meme['id']}, Name: {selected_meme['name']})")
            return selected_meme
        else:
            # If all cached memes are used, reset and try again from cache
            session[used_ids_key] = []
            if all_imgflip_memes_cache: # Check again after reset
                selected_meme = random.choice(all_imgflip_memes_cache)
                session[used_ids_key].append(selected_meme['id'])
                source_description = "Imgflip (dynamically cached, reset session)"
                print(f"DEBUG: Image fetched from {source_description} (ID: {selected_meme['id']}, Name: {selected_meme['name']})")
                return selected_meme


    # Strategy 2: Fallback to hardcoded Imgflip IDs if dynamic cache fails or is exhausted
    hardcoded_ids_list = CORRECT_MEME_IDS if is_correct else INCORRECT_MEME_IDS
    available_from_hardcoded = [mid for mid in hardcoded_ids_list if mid not in session[used_ids_key]]

    if not available_from_hardcoded:
        session[used_ids_key] = [] # Reset hardcoded used IDs if all are exhausted
        available_from_hardcoded = hardcoded_ids_list[:] # Copy all hardcoded IDs

    if available_from_hardcoded:
        selected_template_id = random.choice(available_from_hardcoded)
        session[used_ids_key].append(selected_template_id)
        
        try:
            # Attempt to fetch details for the hardcoded ID from Imgflip
            response = requests.get(IMGFLIP_API_URL)
            response.raise_for_status()
            data = response.json()
            if data and data['success']:
                found_meme = next((m for m in data['data']['memes'] if m['id'] == selected_template_id), None)
                if found_meme:
                    selected_meme = found_meme
                    source_description = "Imgflip (via hardcoded ID)"
                    print(f"DEBUG: Image fetched from {source_description} (ID: {selected_meme['id']}, Name: {selected_meme['name']})")
                    return selected_meme
                else:
                    print(f"DEBUG: Hardcoded meme ID {selected_template_id} not found on Imgflip. Proceeding to local fallback.")
            else:
                print(f"DEBUG: Imgflip API reported error during hardcoded ID fetch: {data.get('error_message', 'Unknown error')}. Proceeding to local fallback.")
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Network error during hardcoded Imgflip ID fetch: {e}. Proceeding to local fallback.")
        except Exception as e:
            print(f"DEBUG: An unexpected error occurred during hardcoded Imgflip ID fetch: {e}. Proceeding to local fallback.")

    # Strategy 3: Final fallback to local images
    return get_random_local_correct_image_info()


def get_random_local_correct_image_info():
    """
    Selects a random image from the static/images/correct/ folder (i1.jpg to i21.jpg).
    Updated to support 21 images.
    """
    random_image_num = random.randint(1, 21) # Changed from 14 to 21
    image_filename = f"i{random_image_num}.jpg"
    local_image_url = url_for('static', filename=f'images/correct/{image_filename}')
    
    print(f"DEBUG: Image fetched from local fallback: {image_filename}")
    return {
        "id": "local_fallback", # Special ID to indicate local fallback
        "url": local_image_url,
        "name": f"Local Fallback Meme {image_filename}",
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
        elif image_url: # It's an external URL (from Imgflip)
            img_data = requests.get(image_url, stream=True)
            img_data.raise_for_status() # Raise an exception for HTTP errors
            img = Image.open(io.BytesIO(img_data.content)).convert("RGB")
        else:
            print("No image URL provided. Creating blank image.")
            img = Image.new('RGB', (250, 250), color = (73, 109, 137)) # Fixed size: 250x250
            d = ImageDraw.Draw(img)
            fnt = ImageFont.load_default()
            d.text((10,10), "Image Missing!", font=fnt, fill=(255,255,255))

        if img is None: # Should not happen if previous logic is sound, but as a safeguard
            print("Image could not be loaded or created. Using generic fallback.")
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
          # --- Image Resizing to 250x250 ---
        img = img.resize((img_width, img_height), Image.LANCZOS)
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
    selected_audio_script = "Error: Could not generate commentary." # Default fallback

    # Find the specific question object to get its audio scripts
    current_question_obj = None
    if selected_language in CODING_QUESTIONS and self_assessed_skill_level in CODING_QUESTIONS[selected_language]:
        questions_for_level = CODING_QUESTIONS[selected_language][self_assessed_skill_level]
        # Iterate through questions to find the matching one
        for q_obj in questions_for_level:
            # Normalize question text for comparison
            if q_obj['question'].strip().lower() == question_text.lower():
                current_question_obj = q_obj
                break

    # Determine correctness and select audio script
    if current_question_obj:
        correct_answer_for_question = current_question_obj['correct_answer'].lower()
        if user_answer == correct_answer_for_question:
            final_skill_level = self_assessed_skill_level
            is_answer_correct = True
            selected_audio_script = current_question_obj.get('correct_audio_script', "Boom! Correct! You got it right!")
        else:
            final_skill_level = "beginner" # Incorrect answer or unmatched question defaults to beginner
            is_answer_correct = False
            selected_audio_script = current_question_obj.get('incorrect_audio_script', "Oops! That's not quite right!")
    else:
        # Fallback if question not found (shouldn't happen with proper frontend)
        final_skill_level = "beginner"
        is_answer_correct = False
        selected_audio_script = "Error: Question not found, but your coding journey continues, friend!"

    # Get a random Imgflip template based on correctness, ensuring no repetition
    # This function now handles fallback to local images and logs the source
    meme_template_info = get_random_imgflip_template_info(is_answer_correct)
    
    # Select meme text based on meme ID and correctness, with generic fallbacks
    if meme_template_info['id'] in MEME_CAPTIONS_BY_ID:
        if is_answer_correct:
            selected_meme_text = MEME_CAPTIONS_BY_ID[meme_template_info['id']].get("correct", random.choice(GENERIC_CORRECT_CAPTIONS))
        else:
            selected_meme_text = MEME_CAPTIONS_BY_ID[meme_template_info['id']].get("incorrect", random.choice(GENERIC_INCORRECT_CAPTIONS))
    else:
        # If meme ID not in custom captions, use generic ones
        if is_answer_correct:
            selected_meme_text = random.choice(GENERIC_CORRECT_CAPTIONS)
        else:
            selected_meme_text = random.choice(GENERIC_INCORRECT_CAPTIONS)
            
    # Generate a unique filename for the meme image
    meme_filename = f"generated_meme_{uuid.uuid4()}.png"
    meme_image_url = create_meme_image(selected_meme_text, meme_template_info, meme_filename)

    # Generate audio using gTTS from the selected pre-defined script
    audio_stream = generate_audio_from_text(selected_audio_script, lang='en')
    generated_audio_id = str(uuid.uuid4())
    generated_audio_streams[generated_audio_id] = audio_stream
    generated_audio_url = url_for('serve_generated_audio', audio_id=generated_audio_id)

    return render_template('meme.html',
                           meme_text=selected_meme_text,
                           meme_image_url=meme_image_url,
                           background_music_url=generated_audio_url,
                           skill_level_display=final_skill_level.capitalize())

@app.route('/static/music/<path:filename>')
def serve_music(filename):
    """Serves music files from the static/music directory."""
    return send_from_directory(MUSIC_DIR, filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(STATIC_DIR, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    # Ensure static directories exist
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(MUSIC_DIR, exist_ok=True)
    os.makedirs(FONTS_DIR, exist_ok=True)
    os.makedirs(CORRECT_IMAGES_DIR, exist_ok=True) # Ensure correct images directory exists
    
    # To run locally:
    # 1. Ensure 'i1.jpg' through 'i21.jpg' are in your 'static/images/correct/' directory.
    # 2. You will need to replace "your_imgflip_username" and "your_imgflip_password"
    #    with actual Imgflip credentials for the meme generation to work.
    app.run(debug=True)
