import pygame
import random
import time
import speech_recognition as sr
import os

# Initialize pygame
pygame.init()

# Set display dimensions
screen_width = 1200
screen_height = 900
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Memory Test")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)  # Soft background color
DARK_BLUE = (0, 0, 128)       # Text contrast color
DARK_GREY = (50, 50, 50)

# Define fonts
title_font = pygame.font.Font(None, 100)  # Large title font for the main title like "Memory Test"
regular_font = pygame.font.Font(None, 60)  # Regular font for important in-game messages like "Correct!" or "Wrong!"
small_font = pygame.font.Font(None, 40)    # Smaller font for instructions and descriptions
button_font = pygame.font.Font(None, 50)   # Font for button text like "Start"

# Initialize speech recognition
recognizer = sr.Recognizer()

# Function to generate a random sequence of numbers
def generate_sequence(length):
    return [random.randint(1, 9) for _ in range(length)]

# Function to show each number in the sequence one by one
def show_sequence(sequence):
    for number in sequence:
        screen.fill(LIGHT_BLUE)
        text = regular_font.render(str(number), True, DARK_BLUE)  # Displaying numbers using regular font
        screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
        pygame.display.flip()
        time.sleep(1)
        screen.fill(LIGHT_BLUE)
        pygame.display.flip()
        time.sleep(0.5)

# Function to display messages in the center of the screen
def display_message(message, color=BLACK):
    screen.fill(LIGHT_BLUE)
    text = regular_font.render(message, True, color)  # Displaying main messages like "Correct!" or "Wrong!" using regular font
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
    pygame.display.flip()

# Function to get player's voice input using speech recognition
def get_player_voice_input(length):
    input_str = ""
    recognizer.pause_threshold = 1.0
    recognizer.energy_threshold = 200
    max_attempts = 2
    attempts = 0

    while attempts < max_attempts:
        try:
            with sr.Microphone() as source:
                display_message("Calibrating microphone... Please wait.", DARK_BLUE)
                pygame.display.flip()
                recognizer.adjust_for_ambient_noise(source, duration=0.1)

                display_message("Speak the sequence clearly...", DARK_BLUE)
                pygame.display.flip()

                audio = recognizer.listen(source)
                spoken_text = recognizer.recognize_google(audio)
                print(f"You said: {spoken_text}")

                digits = [char for char in spoken_text if char.isdigit()]
                input_str = ''.join(digits[:length])

                if len(input_str) == length:
                    return input_str
                else:
                    display_message(f"Please speak exactly {length} numbers.", RED)
                    pygame.time.wait(2000)
                    attempts += 1

        except sr.UnknownValueError:
            display_message("Sorry, I couldn't understand. Try again.", RED)
            pygame.time.wait(2000)
            attempts += 1
        except sr.RequestError:
            display_message("Error with the speech recognition service.", RED)
            pygame.time.wait(2000)
            return None

    return None

# Function to handle manual typing input
def get_player_typing_input(length):
    input_str = ""
    typing_done = False

    while not typing_done:
        screen.fill(LIGHT_BLUE)
        display_message(f"Please type the {length} numbers:", DARK_BLUE)  # Displaying typing instructions using small font
        input_display = regular_font.render(input_str, True, BLACK)
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
    player_input = get_player_voice_input(length)
    
    if player_input is None:
        display_message("Switching to typing input...", DARK_BLUE)  # Displaying switch message using regular font
        pygame.time.wait(2000)
        player_input = get_player_typing_input(length)
    
    return player_input

# Function to run the memory test game
def memory_test(user_data):
    level = 1  # Start at level 1
    score = 0  # Track the score
    running = True  # Game loop flag

    while running:
        sequence_length = 3 + (level - 1)
        correct_attempts = 0  # Track correct attempts per level
        total_attempts = 0  # Track total attempts per level
        remaining_chances = 3  # Player starts with 3 chances per level

        while total_attempts < 3:
            sequence = generate_sequence(sequence_length)
            show_sequence(sequence)

            player_input = get_player_input(sequence_length)

            correct_guesses = sum(1 for i, j in zip(player_input, sequence) if i == str(j))

            screen.fill(LIGHT_BLUE)
            display_sequence_text = small_font.render(f"Display numbers: {''.join(map(str, sequence))}", True, DARK_BLUE)  # Sequence display using small font
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

            # Display the result of the attempt and chances left
            result_display = regular_font.render(result_text, True, result_color)  # Result display using regular font
            screen.blit(result_display, (screen_width // 2 - result_display.get_width() // 2, screen_height // 2 + 50))

            # Show chances left
            chances_left_text = small_font.render(f"Chances Left: {remaining_chances}", True, RED)  # Chances left using small font
            screen.blit(chances_left_text, (screen_width // 2 - chances_left_text.get_width() // 2, screen_height // 2 + 100))

            pygame.display.flip()
            time.sleep(2)

            total_attempts += 1

            if total_attempts == 3 and correct_attempts >= 2:
                level += 1
                screen.fill(LIGHT_BLUE)
                level_completed_text = regular_font.render(f"Level {level - 1} Completed!", True, DARK_BLUE)  # Display level completion using regular font
                points_text = small_font.render(f"Points: {score}", True, BLACK)  # Points display using small font
                screen.blit(level_completed_text, (screen_width // 2 - level_completed_text.get_width() // 2, screen_height // 3))
                screen.blit(points_text, (screen_width // 2 - points_text.get_width() // 2, screen_height // 2))
                pygame.display.flip()
                time.sleep(3)
                break

        if correct_attempts < 2 and total_attempts == 3:
            running = False

    # Display Game Over screen and final score
    screen.fill(LIGHT_BLUE)
    game_over_text = regular_font.render("Game Over", True, RED)  # Game over message using regular font
    score_text = small_font.render(f"Your score: {score}", True, BLACK)  # Final score display using small font
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
        screen.fill(LIGHT_BLUE)
        title_text = title_font.render("Memory Test", True, DARK_BLUE)  # Displaying the title using large title font
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))

        y_offset = 150
        for line in description:
            text_surface = small_font.render(line, True, DARK_BLUE)  # Displaying description using small font
            screen.blit(text_surface, (screen_width // 2 - text_surface.get_width() // 2, y_offset))
            y_offset += 40

        start_button = pygame.Rect(screen_width // 2 - 100, screen_height - 150, 200, 50)
        pygame.draw.rect(screen, GREEN, start_button)
        start_text = button_font.render("Start", True, BLACK)  # Start button using button font
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
