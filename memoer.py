import pygame
import random
import time
import speech_recognition as sr
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

# Initialize pygame
pygame.init()

# Set display dimensions
screen_width = 1200
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Memory Test")
small_font = pygame.font.SysFont("Arial", 24)

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Define fonts
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)
button_font = pygame.font.Font(None, 50)

# Initialize speech recognition
recognizer = sr.Recognizer()

# Function to create a PDF with user data and score
def create_pdf(user_data, score):
    pdf_filename = f"{user_data['name']}_{user_data['phone']}_memory_game_report.pdf"
    pdf_path = os.path.join(os.getcwd(), pdf_filename)
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Memory Game Report")

    c.setFont("Helvetica", 14)
    c.drawString(100, 700, f"Name: {user_data['name']}")
    c.drawString(100, 680, f"Age: {user_data['age']}")
    c.drawString(100, 660, f"Sex: {user_data['sex']}")
    c.drawString(100, 640, f"Email: {user_data['email']}")
    c.drawString(100, 620, f"Phone: {user_data['phone']}")

    # Draw game result
    c.drawString(100, 580, f"Levels Completed: {score // 3}")  
    c.drawString(100, 560, f"Points: {score}")

    c.showPage()
    c.save()
    print(f"PDF created: {pdf_path}")

# Function to generate a random sequence of numbers
def generate_sequence(length):
    return [random.randint(1, 9) for _ in range(length)]

# Function to show each number in the sequence one by one
def show_sequence(sequence):
    for number in sequence:
        screen.fill(WHITE)
        text = font.render(str(number), True, BLACK)
        screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
        pygame.display.flip()
        time.sleep(1)
        screen.fill(WHITE)
        pygame.display.flip()
        time.sleep(0.5)

# Function to display messages on the screen
def display_message(message):
    screen.fill(WHITE)
    text = font.render(message, True, BLACK)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
    pygame.display.flip()

# Function to get player's voice input using speech recognition
def get_player_voice_input(length):
    input_str = ""
    recognizer.pause_threshold = 1.0
    recognizer.energy_threshold = 200
    max_attempts = 2  # Set to 2 attempts
    attempts = 0

    while attempts < max_attempts:
        try:
            with sr.Microphone() as source:
                display_message("Calibrating microphone... Please wait.")
                pygame.display.flip()
                recognizer.adjust_for_ambient_noise(source, duration=0.1)

                display_message("Speak the sequence clearly...")
                pygame.display.flip()

                # Listening and recognizing speech
                audio = recognizer.listen(source)
                spoken_text = recognizer.recognize_google(audio)
                print(f"You said: {spoken_text}")

                # Extract digits from spoken text
                digits = [char for char in spoken_text if char.isdigit()]
                input_str = ''.join(digits[:length])

                if len(input_str) == length:
                    return input_str  # Return valid input
                else:
                    display_message(f"Please speak exactly {length} numbers.")
                    pygame.time.wait(2000)
                    attempts += 1  # Increment attempt count

        except sr.UnknownValueError:
            display_message("Sorry, I couldn't understand. Try again.")
            pygame.time.wait(2000)
            attempts += 1  # Increment attempt count
        except sr.RequestError:
            display_message("Error with the speech recognition service.")
            pygame.time.wait(2000)
            return None

    # If voice recognition fails after 2 attempts, return None to trigger typing input
    return None

# Function to handle manual typing input
def get_player_typing_input(length):
    input_str = ""
    typing_done = False

    while not typing_done:
        screen.fill(WHITE)
        display_message(f"Please type the {length} numbers:")
        input_display = font.render(input_str, True, BLACK)
        screen.blit(input_display, (screen_width // 2 - input_display.get_width() // 2, screen_height // 2))
        pygame.display.flip()

        # Handle keyboard input for manual typing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(input_str) == length:
                    typing_done = True
                elif event.key == pygame.K_BACKSPACE:
                    input_str = input_str[:-1]
                elif len(input_str) < length and event.unicode.isdigit():
                    input_str += event.unicode

    return input_str

# Function to switch between voice and typing input
def get_player_input(length):
    # Try voice input first
    player_input = get_player_voice_input(length)
    
    # If voice input fails after 2 attempts, switch to typing input
    if player_input is None:
        display_message("Switching to typing input...")
        pygame.time.wait(2000)
        player_input = get_player_typing_input(length)  # Switch to typing input
    
    return player_input

# Function to handle the user login
def user_login():
    user_data = {"name": "", "phone": "", "email": "", "sex": "", "age": ""}
    input_fields = ["name", "phone", "email", "sex", "age"]
    field_prompts = [
        "Enter your name: ",
        "Enter your phone number (10 digits): ",
        "Enter your email: ",
        "Enter your sex (male/female): ",
        "Enter your age: "
    ]
    input_text = ""
    current_field = 0
    running = True
    error_message = ""

    input_boxes = [pygame.Rect(50, 200, 500, 32) for _ in range(len(input_fields))]

    while running and current_field < len(input_fields):
        screen.fill(WHITE)

        # Render the current prompt and input text
        prompt = small_font.render(field_prompts[current_field], True, BLACK)
        input_display = small_font.render(input_text, True, BLACK)
        screen.blit(prompt, (50, 100))
        screen.blit(input_display, (input_boxes[current_field].x + 5, input_boxes[current_field].y + 5))

        # Only draw the current field's input box
        pygame.draw.rect(screen, BLUE, input_boxes[current_field], 2)

        # Show error message if any
        if error_message:
            error_display = small_font.render(error_message, True, RED)
            screen.blit(error_display, (50, 250))

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Validation for phone number
                    if current_field == 1:  # Phone validation
                        if len(input_text) == 10 and input_text.isdigit():
                            user_data[input_fields[current_field]] = input_text
                            input_text = ""
                            current_field += 1
                            error_message = ""
                        else:
                            error_message = "Invalid! Enter 10 digits."
                    # Validation for email address
                    elif current_field == 2:  # Email validation
                        if "@" in input_text:
                            user_data[input_fields[current_field]] = input_text
                            input_text = ""
                            current_field += 1
                            error_message = ""
                        else:
                            error_message = "Invalid email! Must include '@'."
                    elif input_text:
                        user_data[input_fields[current_field]] = input_text
                        input_text = ""
                        current_field += 1 
                        error_message = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if current_field == 1 and event.unicode.isdigit() and len(input_text) < 10:
                        input_text += event.unicode
                    elif current_field != 1:
                        input_text += event.unicode

    return user_data

# Function to run the memory test game
def memory_test(user_data):
    level = 1
    score = 0
    running = True

    while running:
        sequence_length = 3 + (level - 1)
        correct_attempts = 0
        total_attempts = 0
        remaining_chances = 3

        while total_attempts < 3:
            sequence = generate_sequence(sequence_length)
            show_sequence(sequence)

            # First try to get input via voice
            player_input = get_player_input(sequence_length)

            # Check the player's input
            correct_guesses = sum(1 for i, j in zip(player_input, sequence) if i == str(j))

            screen.fill(WHITE)
            display_sequence_text = small_font.render(f"Display numbers: {''.join(map(str, sequence))}", True, BLACK)
            screen.blit(display_sequence_text, (screen_width // 2 - display_sequence_text.get_width() // 2, screen_height // 2 - display_sequence_text.get_height() // 2))

            player_input_text = small_font.render(f"You said: {player_input}", True, BLACK)
            screen.blit(player_input_text, (screen_width // 2 - player_input_text.get_width() // 2, screen_height - 100))

            if correct_guesses == sequence_length:
                correct_attempts += 1
                score += 1
                result_text = "Correct!"
                result_color = GREEN
            else:
                result_text = "Wrong!"
                result_color = RED
                remaining_chances -= 1

            result_display = font.render(result_text, True, result_color)
            screen.blit(result_display, (screen_width // 2 - result_display.get_width() // 2, screen_height // 2 + 50))

            if result_text == "Wrong!":
                remaining_chances_text = small_font.render(f"Remaining Chances: {remaining_chances}", True, RED)
                screen.blit(remaining_chances_text, (screen_width // 2 - remaining_chances_text.get_width() // 2, screen_height // 2 + 100))
            
            pygame.display.flip()
            time.sleep(2)

            total_attempts += 1

            if correct_attempts >= 2:
                score += 1
                level += 1
                print(f"Level {level} reached! Sequence length increased to {sequence_length + 1}.")
                break

            if total_attempts == 3 and correct_attempts < 2:
                running = False

    create_pdf(user_data, score)

    screen.fill(WHITE)
    game_over_text = font.render("Game Over", True, RED)
    score_text = small_font.render(f"Your score: {score}", True, BLACK)
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 3))
    screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 2))
    pygame.display.flip()
    time.sleep(5)

# Start screen for the game
def start_screen():
    running = True
    description = [
        "Understand your capacity to store, retain, and recollect information.",
        "This test will assess your working memory and decision-making.",
        "Memory is the capacity to recall and use information to make decisions.",
        "Click Start to begin."
    ]

    while running:
        screen.fill(WHITE)
        title_text = font.render("Memory Test", True, BLACK)
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))

        y_offset = 150
        for line in description:
            text_surface = small_font.render(line, True, BLACK)
            screen.blit(text_surface, (screen_width // 2 - text_surface.get_width() // 2, y_offset))
            y_offset += 40

        start_button = pygame.Rect(screen_width // 2 - 100, screen_height - 150, 200, 50)
        pygame.draw.rect(screen, GREEN, start_button)
        start_text = button_font.render("Start", True, BLACK)
        screen.blit(start_text, (start_button.x + (start_button.width - start_text.get_width()) // 2, start_button.y + (start_button.height - start_text.get_height()) // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return True

# Main function to run the game
if __name__ == "__main__":
    if start_screen():
        user_data = user_login()
        memory_test(user_data)

pygame.quit()
