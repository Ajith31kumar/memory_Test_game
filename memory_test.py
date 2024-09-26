

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
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Memory Test")
small_font = pygame.font.SysFont("Arial", 24)

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_GREY = (200, 200, 200)

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

# Function to display messages in the center of the screen
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

# Function to run the memory test game
def memory_test(user_data):
    level = 1  # Start at level 1
    score = 0  # Track the score
    running = True  # Game loop flag

    while running:  # Infinite loop until the player fails
        sequence_length = 3 + (level - 1)  # Start with 3 numbers, increase by 1 per level
        correct_attempts = 0  # Track correct attempts per level
        total_attempts = 0  # Track total attempts per level
        remaining_chances = 3  # Player starts with 3 chances per level

        # The player gets 3 tests per level
        while total_attempts < 3:  # Each level has exactly 3 attempts
            sequence = generate_sequence(sequence_length)  # Generate the sequence for the current level
            show_sequence(sequence)  # Display the sequence to the player

            # Get player input (via voice or typing)
            player_input = get_player_input(sequence_length)

            # Check how many correct guesses the player made
            correct_guesses = sum(1 for i, j in zip(player_input, sequence) if i == str(j))

            # Display the sequence and the player's input
            screen.fill(WHITE)
            display_sequence_text = small_font.render(f"Display numbers: {''.join(map(str, sequence))}", True, BLACK)
            screen.blit(display_sequence_text, (screen_width // 2 - display_sequence_text.get_width() // 2, screen_height // 2 - display_sequence_text.get_height() // 2))

            player_input_text = small_font.render(f"You said: {player_input}", True, BLACK)
            screen.blit(player_input_text, (screen_width // 2 - player_input_text.get_width() // 2, screen_height - 100))

            # Determine if the player's input was correct
            if correct_guesses == sequence_length:
                correct_attempts += 1  # Increase correct attempts
                score += 1  # Increase score for correct guesses
                result_text = "Correct!"
                result_color = GREEN
            else:
                result_text = "Wrong!"
                result_color = RED
                remaining_chances -= 1  # Decrease remaining chances if incorrect

            # Display the result of the attempt
            result_display = font.render(result_text, True, result_color)
            screen.blit(result_display, (screen_width // 2 - result_display.get_width() // 2, screen_height // 2 + 50))

            # Display how many chances are left
            remaining_chances_text = small_font.render(f"Chances Left: {remaining_chances}", True, RED)
            screen.blit(remaining_chances_text, (screen_width // 2 - remaining_chances_text.get_width() // 2, screen_height // 2 + 100))

            pygame.display.flip()
            time.sleep(2)  # Wait before the next attempt

            total_attempts += 1  # Track how many attempts the player has used

            # If the player gets 2 correct attempts out of 3, move to the next level
            if total_attempts == 3 and correct_attempts >= 2:
                level += 1  # Increase the level
                
                # Display level completion and points
                screen.fill(WHITE)
                level_completed_text = font.render(f"Level {level - 1} Completed!", True, BLUE)
                points_text = small_font.render(f"Points: {score}", True, BLACK)
                screen.blit(level_completed_text, (screen_width // 2 - level_completed_text.get_width() // 2, screen_height // 3))
                screen.blit(points_text, (screen_width // 2 - points_text.get_width() // 2, screen_height // 2))
                pygame.display.flip()
                time.sleep(3)  # Display the message for 3 seconds
                
                print(f"Level {level} reached! Sequence length increased to {sequence_length + 1}.")
                break  # Move to the next level

        # If the player fails to get 2 correct attempts after 3 tries, end the game
        if correct_attempts < 2 and total_attempts == 3:
            running = False  # End the game loop

    # Create a PDF report of the game
    create_pdf(user_data, score)

    # Display Game Over screen and final score
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
    # No login, directly start the memory test game
    user_data = {"name": "Test User", "age": "25", "sex": "male", "email": "test@example.com", "phone": "1234567890"}  # Dummy user data
    if start_screen():
        memory_test(user_data)

pygame.quit()



