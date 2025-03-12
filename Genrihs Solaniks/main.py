import pygame
import random
import math

# Inicializē Pygame
pygame.init()

# Ekrāna izmēri
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Number Division Game")

# Krāsas
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
GRAY = (150, 150, 150)

# Fonti
font = pygame.font.Font(None, 36)

# Ģenerē 5 skaitļus diapazonā no 30000 līdz 50000
numbers = [random.randint(30000, 50000) for _ in range(5)]
selected_number = None
points = 0
bank = 0

# Iespējamie dalītāji
divisors = [2, 3, 4, 5]
player_turn = True  # Контроль хода
ai_algorithm = "alpha-beta"  # Выбор алгоритма AI
first_player = None  # Кто ходит первым


def draw_text(text, x, y, color=BLACK):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


def draw_menu():
    screen.fill(WHITE)
    draw_text("Choose a starting number:", 50, 50)
    for i, num in enumerate(numbers):
        pygame.draw.rect(screen, BLUE, (50, 100 + i * 50, 200, 40))
        draw_text(str(num), 60, 110 + i * 50, WHITE)
    pygame.display.flip()


def alpha_beta(number, depth, alpha, beta, is_maximizing):
    if depth == 0 or all(number % d != 0 for d in divisors):
        return points + bank if points % 2 == 0 else points - bank

    if is_maximizing:
        best_score = -math.inf
        for divisor in divisors:
            if number % divisor == 0:
                new_number = number // divisor
                score = alpha_beta(new_number, depth - 1, alpha, beta, False)
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
        return best_score
    else:
        best_score = math.inf
        for divisor in divisors:
            if number % divisor == 0:
                new_number = number // divisor
                score = alpha_beta(new_number, depth - 1, alpha, beta, True)
                best_score = min(best_score, score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
        return best_score


def ai_move():
    global selected_number, points, bank
    best_score = -math.inf
    best_move = None
    for divisor in divisors:
        if selected_number % divisor == 0:
            new_number = selected_number // divisor
            score = alpha_beta(new_number, 3, -math.inf, math.inf, False)
            if score > best_score:
                best_score = score
                best_move = divisor

    if best_move:
        selected_number //= best_move
        if selected_number % 2 == 0:
            points -= 1
        else:
            points += 1
        if selected_number % 10 == 0 or selected_number % 10 == 5:
            bank += 1


def play_game():
    global selected_number, points, bank, player_turn
    running = True
    while running:
        screen.fill(WHITE)
        draw_text(f"Current number: {selected_number}", 50, 50)
        draw_text(f"Points: {points}", 50, 100)
        draw_text(f"Bank: {bank}", 50, 150)
        draw_text(f"Turn: {'Player' if player_turn else 'AI'}", 50, 200)

        for i, divisor in enumerate(divisors):
            color = BLUE if selected_number % divisor == 0 else GRAY
            pygame.draw.rect(screen, color, (50, 250 + i * 50, 200, 40))
            draw_text(f"Divide by {divisor}", 60, 260 + i * 50, WHITE)

        pygame.display.flip()

        if not player_turn:
            pygame.time.delay(500)  # Небольшая задержка перед ходом ИИ
            ai_move()
            player_turn = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                x, y = event.pos
                for i, divisor in enumerate(divisors):
                    if 50 <= x <= 250 and 250 + i * 50 <= y <= 290 + i * 50 and selected_number % divisor == 0:
                        selected_number //= divisor
                        if selected_number % 2 == 0:
                            points -= 1
                        else:
                            points += 1
                        if selected_number % 10 == 0 or selected_number % 10 == 5:
                            bank += 1
                        player_turn = False
                        pygame.time.delay(500)
                        ai_move()
                        player_turn = True

    pygame.quit()


def choose_first_player():
    global first_player, player_turn
    screen.fill(WHITE)
    draw_text("Who goes first?", 50, 50)
    pygame.draw.rect(screen, BLUE, (50, 100, 200, 40))
    draw_text("Player", 110, 110, WHITE)
    pygame.draw.rect(screen, BLUE, (50, 150, 200, 40))
    draw_text("AI", 110, 160, WHITE)
    pygame.display.flip()

    choosing = True
    while choosing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 50 <= x <= 250 and 100 <= y <= 140:
                    first_player = "Player"
                    player_turn = True
                    choosing = False
                elif 50 <= x <= 250 and 150 <= y <= 190:
                    first_player = "AI"
                    player_turn = False
                    choosing = False
                    pygame.time.delay(500)
                    ai_move()
                    player_turn = True


def main():
    global selected_number
    running = True
    while running:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for i in range(5):
                    if 50 <= x <= 250 and 100 + i * 50 <= y <= 140 + i * 50:
                        selected_number = numbers[i]
                        choose_first_player()
                        play_game()
                        running = False

    pygame.quit()


if __name__ == "__main__":
    main()
