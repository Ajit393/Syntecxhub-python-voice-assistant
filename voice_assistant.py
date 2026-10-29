
import speech_recognition as sr
import pyttsx3
from datetime import datetime
import webbrowser
import pyjokes
import wikipedia
import subprocess
import ast
import operator
from urllib.parse import quote_plus

# Initialize voice assistant
r = sr.Recognizer()
engine = pyttsx3.init()

first_time = True

# Supported websites
websites = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "wikipedia": "https://www.wikipedia.org",
    "stackoverflow": "https://stackoverflow.com",
    "stack overflow": "https://stackoverflow.com",
}

# Safe arithmetic operations
operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def speak(message):
    """Print and speak a response."""
    print(message)
    engine.say(str(message))
    engine.runAndWait()


def calculate(expression):
    """Calculate basic arithmetic without using eval()."""
    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in operators:
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Exponent too large")

            return operators[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in operators:
            return operators[type(node.op)](evaluate(node.operand))

        raise ValueError("Unsupported expression")

    tree = ast.parse(expression, mode="eval")
    return evaluate(tree.body)


def handle_command(command):
    """Process a recognized voice command."""
    command = command.lower().strip()

    # Greeting
    if "hello" in command or "hey assistant" in command:
        return "Hello! What can I help you with today?"

    # Take a note
    elif command == "note" or command.startswith("note "):
        note_text = command.split("note", 1)[1].strip()

        if not note_text:
            return "Please tell me what you want me to note."

        try:
            with open("filename.txt", "a", encoding="utf-8") as file:
                file.write(note_text + "\n")

            return "Note saved successfully."

        except OSError:
            return "Sorry, I could not save your note."

    # Date
    elif "date" in command or "today" in command:
        today = datetime.now().strftime("%d %B %Y")
        return f"Today's date is {today}"

    # Time
    elif "time" in command:
        now = datetime.now().strftime("%I:%M %p")
        return f"The time is {now}"

    # Calculator
    elif (
        "what is" in command
        or "calculate" in command
        or "how much is" in command
    ):
        expression = command

        for phrase in ("what is", "calculate", "how much is"):
            expression = expression.replace(phrase, "", 1)

        replacements = {
            "multiplied by": "*",
            "divided by": "/",
            "plus": "+",
            "minus": "-",
            "times": "*",
            " x ": " * ",
        }

        for word, symbol in replacements.items():
            expression = expression.replace(word, symbol)

        try:
            answer = calculate(expression.strip())
            return f"The answer is {answer}"

        except (ValueError, SyntaxError, TypeError, ZeroDivisionError, OverflowError):
            return "Sorry, I couldn't calculate that."

    # Open websites or search Google
    elif command.startswith("open "):
        target = command.split("open ", 1)[1].strip()

        if not target:
            return "Please tell me what to open."

        if target in websites:
            webbrowser.open_new_tab(websites[target])
            return f"Opening {target}"

        # Open desktop applications on Windows
        elif target in ("notepad", "calculator"):
            app = "notepad.exe" if target == "notepad" else "calc.exe"

            try:
                subprocess.Popen([app])
                return f"Opening {target}"

            except OSError:
                return f"Sorry, I couldn't open {target}."

        # Search for anything not in the website list
        else:
            search_url = (
                "https://www.google.com/search?q=" + quote_plus(target)
            )
            webbrowser.open_new_tab(search_url)
            return f"Searching Google for {target}"

    # Tell a joke
    elif "joke" in command:
        try:
            return pyjokes.get_joke()
        except Exception:
            return "Sorry, I couldn't get a joke right now."

    # Wikipedia search
    elif "wikipedia" in command:
        search_term = command.replace("wikipedia", "", 1).strip()

        if not search_term:
            return "Please tell me what you want to search on Wikipedia."

        try:
            return wikipedia.summary(search_term, sentences=2)

        except Exception:
            return "Sorry, I couldn't find anything on Wikipedia."

    # Help
    elif "help" in command or "what can you do" in command:
        return (
            "You can ask me to open Google, YouTube, GitHub, "
            "or Gmail; open Notepad or Calculator; tell the time or date; "
            "take a note; calculate sums; tell a joke; or search Wikipedia."
        )

    # Exit
    elif any(word in command for word in ("exit", "goodbye", "quit", "stop")):
        return "Goodbye!"

    # Unknown command
    return "Sorry, I don't understand that command. Say help for options."


# Main listening loop
while True:
    try:
        with sr.Microphone() as source:
            if first_time:
                speak("Personal voice assistant is ready. Please say something.")
                first_time = False

            r.adjust_for_ambient_noise(source, duration=0.5)
            print("\nListening...")

            audio = r.listen(source, timeout=8, phrase_time_limit=10)

        print("Audio captured, processing...")

        command_text = r.recognize_google(audio)
        print("You said:", command_text)

        result = handle_command(command_text)
        speak(result)

        if result == "Goodbye!":
            break

        if "hello" not in command_text.lower():
            speak("Anything else?")

    except sr.WaitTimeoutError:
        print("No speech detected. Please try again.")

    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")

    except sr.RequestError as error:
        print(f"Speech recognition service error: {error}")
        speak("Speech recognition is temporarily unavailable.")

    except (OSError, AttributeError) as error:
        print(f"Microphone error: {error}")
        speak("I could not access the microphone. Please check your settings.")
        break
