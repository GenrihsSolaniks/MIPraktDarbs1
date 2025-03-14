#DIZAINS IR OK
#RESTARTS NESTRĀDĀ KĀ VAJAG (SĀKUMA SKAITLIS IR None)
#SĀKUMA SKAITLI VAJAG PĀRBĪDĪT PIE VĒSTURES
#NAV HEIRISTISKĀ FUNKCIJA
#NAV IZVĒLES KURŠ SĀK SPĒLI (DATORAM ARĪ VAJADZĒTU IZVĒLĒTIES SĀKUMA SKAITLI?)
#IESPĒJAMS 0 VĒRTĪBA NAV DEFINĒTA KĀ PĀRA SKAITLIS (JĀPĀRBAUDA)

import pygame
import random
import math
from functools import partial

def generate_numbers():
    return random.sample(range(30000, 50001), 5)

def is_valid_division(num, divisor):
    return num is not None and num % divisor == 0

def calculate_points(num):
    points = 1 if num % 2 == 1 else -1
    bank = 1 if num % 10 in [0, 5] else 0
    return points, bank

def minimax(num, depth, is_maximizing, alpha, beta):
    if depth == 0 or not any(is_valid_division(num, d) for d in [2, 3, 4, 5]):
        return calculate_points(num)[0]
    
    if is_maximizing:
        max_eval = -math.inf
        for d in [2, 3, 4, 5]:
            if is_valid_division(num, d):
                eval = minimax(num // d, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = math.inf
        for d in [2, 3, 4, 5]:
            if is_valid_division(num, d):
                eval = minimax(num // d, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Number Division Game")
font = pygame.font.SysFont("Verdana", 32, bold=False)
small_font = pygame.font.SysFont("Verdana", 24, bold=False)

def draw_text(text, x, y, size=32, color=(255, 255, 255)):
    font = pygame.font.SysFont("Verdana", size, bold=False)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_button(text, x, y, w, h, color, hover_color, disabled, action):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect_color = hover_color if x < mouse[0] < x + w and y < mouse[1] < y + h and not disabled else color
    pygame.draw.rect(screen, rect_color, (x, y, w, h))
    draw_text(text, x + w // 2, y + h // 2, 24, (0, 0, 0))
    if click[0] == 1 and action and x < mouse[0] < x + w and y < mouse[1] < y + h and not disabled:
        pygame.time.delay(200)
        action()

def reset_game():
    global selected_number, available_numbers, points, bank, player_turn, game_over, history, winner, choosing
    available_numbers = generate_numbers()
    selected_number = None
    points = 0
    bank = 0
    player_turn = True
    game_over = False
    history = []
    winner = None
    choosing = True

def check_game_over():
    global game_over, winner, points, bank
    if not any(is_valid_division(selected_number, d) for d in [2, 3, 4, 5]):
        game_over = True
        final_score = points - bank if points % 2 == 1 else points + bank
        winner = "AI Wins!" if final_score % 2 == 0 else "Player Wins!"
        history.append(f"Final Score: {final_score}")

def choose_number(num):
    global selected_number, choosing
    selected_number = num
    choosing = False

def divide_number(divisor):
    global selected_number, points, bank, player_turn
    if is_valid_division(selected_number, divisor) and player_turn:
        selected_number //= divisor
        point_change, bank_change = calculate_points(selected_number)
        points += point_change
        bank += bank_change
        history.append(f"Player: {selected_number} ({points} pts)")
        player_turn = False
        check_game_over()

def ai_move():
    global selected_number, points, bank, player_turn
    best_move = None
    best_value = -math.inf
    for d in [2, 3, 4, 5]:
        if is_valid_division(selected_number, d):
            eval = minimax(selected_number // d, 3, False, -math.inf, math.inf)
            if eval > best_value:
                best_value = eval
                best_move = d
    if best_move:
        selected_number //= best_move
        point_change, bank_change = calculate_points(selected_number)
        points += point_change
        bank += bank_change
        history.append(f"AI: {selected_number} ({points} pts)")
    player_turn = True
    check_game_over()

reset_game()
while choosing:
    screen.fill((30, 30, 30))
    draw_text("Choose a starting number:", WIDTH // 2, 100, 36)
    for i, num in enumerate(available_numbers):
        draw_button(f"{num}", WIDTH // 2 - 50, 150 + i * 60, 100, 50, (200, 200, 200), (255, 255, 255), False, partial(choose_number, num))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    pygame.display.flip()

running = True
while running:
    screen.fill((30, 30, 30))
    draw_text(f"Starting Number: {available_numbers[0]}", WIDTH // 2, 20)
    draw_text(f"Current Number: {selected_number}", WIDTH // 2, 50)
    draw_text(f"Points: {points} | Bank: {bank}", WIDTH // 2, 90)
    for i, d in enumerate([2, 3, 4, 5]):
        disabled = not is_valid_division(selected_number, d)
        draw_button(f"/{d}", WIDTH // 2 - 75 + i * 75, 140, 50, 50, (100, 100, 100) if disabled else (100, 200, 100), (150, 255, 150), disabled, partial(divide_number, d))
    if game_over:
        draw_text(winner, WIDTH // 2, HEIGHT // 2, 40, (255, 0, 0))
        draw_button("Restart", WIDTH // 2 - 50, HEIGHT - 100, 100, 50, (200, 200, 200), (255, 255, 255), False, reset_game)
    for i, event in enumerate(history[-10:]):
        draw_text(event, 150, 150 + i * 30, 24, (200, 200, 200))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if not player_turn and selected_number and not game_over:
        ai_move()
    pygame.display.flip()
pygame.quit()