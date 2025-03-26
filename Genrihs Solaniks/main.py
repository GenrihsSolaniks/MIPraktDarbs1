import pygame
import random
import math
from functools import partial

# =======================
# KOKA ĢENERĀCIJAS KLĀSSI
# =======================

class TreeNode:
    def __init__(self, value, parent=None):
        self.value = value
        self.parent = parent
        self.children = []
        self.bank = 0
        self.score = 0
        self.heuristic_value = None
        self.heuristic_sum = None

    def add_child(self, child):
        self.children.append(child)

class Tree:
    def __init__(self):
        self.root = None

    def generate_tree(self, num):
        self.root = self._create_node(num)
        self._generate_children(self.root)

    def _create_node(self, value, parent=None):
        node = TreeNode(value, parent)
        self._calculate(node)
        return node

    def _generate_children(self, node):
        # Ja vērtība jau ir 0, tālāk dalīt nav jēgas
        if node.value == 0:
            return
        for divisor in [2, 3, 4, 5]:
            if node.value % divisor == 0:
                child_value = node.value // divisor
                # Ja dalīšanas rezultāts ir 0 vai nav mainījies, izlaist
                if child_value <= 0 or child_value == node.value:
                    continue
                child = self._create_node(child_value, parent=node)
                node.add_child(child)
                self._generate_children(child)

    def _calculate(self, node):
        # Bankas aprēķins: ja skaitlis beidzas ar 0 vai 5, banka palielinās par 1
        if node.value % 10 == 0 or node.value % 10 == 5:
            node.bank = node.parent.bank + 1 if node.parent else 0
        else:
            node.bank = node.parent.bank if node.parent else 0
        # Rezultātu aprēķins: pāra skaitlim atņem 1, nepāra pievieno 1
        if node.value % 2 == 0:
            node.score = node.parent.score - 1 if node.parent else 0
        else:
            node.score = node.parent.score + 1 if node.parent else 0

    def calculate_heuristic_values(self, node, ai_goes_first, minimax_chosen, alpha=float('-inf'), beta=float('inf')):
        # Pamata gadījums: ja mezlim nav bērnu, tas ir lapas
        if not node.children:
            final_score = node.score + node.bank if node.score % 2 == 0 else node.score - node.bank
            if ai_goes_first:
                node.heuristic_value = -1 if final_score % 2 == 0 else 1
            else:
                node.heuristic_value = 1 if final_score % 2 == 0 else -1
            node.heuristic_sum = node.heuristic_value
            return (node.heuristic_value, node.heuristic_sum)
        
        # Zara bez alfa-beta nogriezuma (tīrs minimax)
        if minimax_chosen:
            if ai_goes_first:
                node.heuristic_value = float('-inf')
                node.heuristic_sum = 0
                for child in node.children:
                    child_value, child_sum = self.calculate_heuristic_values(child, not ai_goes_first, minimax_chosen, alpha, beta)
                    if child_value is None:
                        continue
                    node.heuristic_value = max(node.heuristic_value, child_value)
                    node.heuristic_sum += child_sum
            else:
                node.heuristic_value = float('inf')
                node.heuristic_sum = 0
                for child in node.children:
                    child_value, child_sum = self.calculate_heuristic_values(child, not ai_goes_first, minimax_chosen, alpha, beta)
                    if child_value is None:
                        continue
                    node.heuristic_value = min(node.heuristic_value, child_value)
                    node.heuristic_sum += child_sum
        # Zara ar alfa-beta nogriezumu
        else:
            if ai_goes_first:
                node.heuristic_value = float('-inf')
                node.heuristic_sum = 0
                for child in node.children:
                    child_value, child_sum = self.calculate_heuristic_values(child, not ai_goes_first, minimax_chosen, alpha, beta)
                    if child_value is None:
                        continue
                    node.heuristic_value = max(node.heuristic_value, child_value)
                    node.heuristic_sum += child_sum
                    alpha = max(alpha, node.heuristic_value)
                    if node.heuristic_value == 1 or beta <= alpha:
                        break
            else:
                node.heuristic_value = float('inf')
                node.heuristic_sum = 0
                for child in node.children:
                    child_value, child_sum = self.calculate_heuristic_values(child, not ai_goes_first, minimax_chosen, alpha, beta)
                    if child_value is None:
                        continue
                    node.heuristic_value = min(node.heuristic_value, child_value)
                    node.heuristic_sum += child_sum
                    beta = min(beta, node.heuristic_value)
                    if node.heuristic_value == -1 or beta <= alpha:
                        break

        node.heuristic_sum += node.heuristic_value
        return (node.heuristic_value, node.heuristic_sum)

# =======================
# SPĒLES LOĢIKAS FUNKCIJAS
# =======================

def generate_numbers():
    return random.sample(range(30000, 50001), 5)

def is_valid_division(num, divisor):
    return num is not None and num % divisor == 0

def calculate_points(num):
    points = 1 if num % 2 == 1 else -1
    bank = 1 if num % 10 in [0, 5] else 0
    return points, bank

# =======================
# ELEMENTU ZĪMĒŠANAS FUNKCIJAS
# =======================

def draw_text(text, x, y, size=32, color=(255,255,255)):
    font_obj = pygame.font.SysFont("Verdana", size, bold=False)
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x,y))
    screen.blit(text_surface, text_rect)

def draw_button(text, x, y, w, h, color, hover_color, disabled, action):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect_color = hover_color if x < mouse[0] < x+w and y < mouse[1] < y+h and not disabled else color
    pygame.draw.rect(screen, rect_color, (x, y, w, h))
    draw_text(text, x+w//2, y+h//2, 24, (0,0,0))
    if click[0] == 1 and action and x < mouse[0] < x+w and y < mouse[1] < y+h and not disabled:
        pygame.time.delay(200)
        action()

def draw_rules():
    pygame.draw.rect(screen, (50,50,50), (100,100,600,400))
    pygame.draw.rect(screen, (255,0,0), (650,110,40,40))
    draw_text("X", 670, 130, 30, (255,255,255))
    rules_text = [
        "Spēles noteikumi:",
        "",
        "Spēlētāji izdara gājienus pēc kārtas, dalot skaitli ar 2,3,4 vai 5.",
        "Dalīšana iespējama tikai, ja rezultāts ir vesels skaitlis.",
        "Nepāra rezultāts dod +1 punktu, pāra – -1 punktu.",
        "Ja rezultāts beidzas ar 0 vai 5, bankam pievienots 1 punkts.",
        "Spēle beidzas, ja skaitli vairs nevar dalīt.",
        "Gala rezultātā, ja punktu summa ir nepāra, uzvar spēlētājs,",
        "ja pāra – uzvar pretinieks."
    ]
    for i, line in enumerate(rules_text):
        draw_text(line, 400, 140+i*25, 16, (255,255,255))

def toggle_rules():
    global show_rules
    show_rules = not show_rules

# =======================
# PYGAME UN GLOBĀLO MAINĪGO INICIALIZĀCIJA
# =======================

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Number Division Game")
font = pygame.font.SysFont("Verdana", 32, bold=False)
small_font = pygame.font.SysFont("Verdana", 24, bold=False)
show_rules = False

# Spēles fāzes:
# "settings_algorithm" -> "settings_first" -> "choose_number" -> "game" -> "game_over"
game_phase = "settings_algorithm"
ai_goes_first = None      # True, ja AI spēlē pirmo
minimax_chosen = None     # True: minimax, False: alpha-beta
player_turn = None
selected_number = None
starting_number = None
available_numbers = []
points = 0
bank = 0
game_over = False
history = []
choosing = True

# =======================
# FĀŽU PĀREJAS FUNKCIJAS
# =======================

def select_algorithm(is_minimax):
    global minimax_chosen, game_phase
    minimax_chosen = is_minimax
    game_phase = "settings_first"

def select_first(is_ai):
    global ai_goes_first, game_phase
    ai_goes_first = is_ai
    game_phase = "choose_number"

def start_game_after_number():
    global game_phase, player_turn
    player_turn = not ai_goes_first
    game_phase = "game"

def reset_game():
    global selected_number, starting_number, available_numbers, points, bank, player_turn, game_over, history, choosing, game_phase, ai_goes_first, minimax_chosen
    available_numbers = generate_numbers()
    selected_number = None
    starting_number = None
    points = 0
    bank = 0
    game_over = False
    history = []
    choosing = True
    ai_goes_first = None
    minimax_chosen = None
    game_phase = "settings_algorithm"

def check_game_over():
    global game_over, winner, points, bank, game_phase
    if not (selected_number and any(is_valid_division(selected_number, d) for d in [2,3,4,5])):
        game_over = True
        final_score = points - bank if points % 2 == 1 else points + bank
        winner = "AI Wins!" if final_score % 2 == 0 else "Player Wins!"
        history.append(f"Final Score: {final_score}")
        game_phase = "game_over"

def choose_number(num):
    global selected_number, starting_number, choosing
    selected_number = num
    starting_number = num
    choosing = False
    start_game_after_number()

def divide_number(divisor):
    global selected_number, points, bank, player_turn
    if is_valid_division(selected_number, divisor) and player_turn:
        previous_number = selected_number
        selected_number //= divisor
        point_change, bank_change = calculate_points(selected_number)
        points += point_change
        bank += bank_change
        history.append(f"Player: {previous_number} / {divisor} = {selected_number} ({points} pts)")
        player_turn = False
        check_game_over()
        pygame.display.flip()

def ai_move():
    global selected_number, points, bank, player_turn
    tree = Tree()
    tree.generate_tree(selected_number)
    tree.calculate_heuristic_values(tree.root, ai_goes_first, minimax_chosen)
    best_move = None
    best_value = float('-inf')
    for child in tree.root.children:
        # Nosakām, kurš dalītājs tika izmantots:
        divisor = tree.root.value // child.value if child.value != 0 and (tree.root.value // child.value) in [2,3,4,5] else None
        if divisor is not None and child.heuristic_value is not None and child.heuristic_value > best_value:
            best_value = child.heuristic_value
            best_move = divisor
    if best_move:
        previous_number = selected_number
        selected_number //= best_move
        point_change, bank_change = calculate_points(selected_number)
        points += point_change
        bank += bank_change
        history.append(f"AI: {previous_number} / {best_move} = {selected_number} ({points} pts)")
    player_turn = True
    check_game_over()
    pygame.display.flip()

# =======================
# EKRĀNU ZĪMĒŠANAS FUNKCIJAS (SPĒLES FĀZES)
# =======================

def draw_settings_algorithm():
    pygame.draw.rect(screen, (50,50,50), (150,100,500,400))
    draw_text("Choose an algorithm:", WIDTH//2, 150, 28, (255,255,255))
    draw_button("Minimax", WIDTH//2 - 150, 220, 150, 50, 
                (100,200,100) if minimax_chosen == True else (200,200,200),
                (150,255,150), False, lambda: select_algorithm(True))
    draw_button("Alpha-Beta", WIDTH//2 + 30, 220, 150, 50, 
                (100,200,100) if minimax_chosen == False else (200,200,200),
                (150,255,150), False, lambda: select_algorithm(False))

def draw_settings_first():
    pygame.draw.rect(screen, (50,50,50), (150,100,500,400))
    draw_text("Choose who goes first:", WIDTH//2, 150, 28, (255,255,255))
    draw_button("Player", WIDTH//2 - 150, 220, 120, 50, 
                (100,200,100) if ai_goes_first == False else (200,200,200),
                (150,255,150), False, lambda: select_first(False))
    draw_button("AI", WIDTH//2 + 30, 220, 120, 50, 
                (100,200,100) if ai_goes_first == True else (200,200,200),
                (150,255,150), False, lambda: select_first(True))

def draw_choose_number():
    draw_text(f"Starting Number: {starting_number if starting_number else 'Not chosen'}", WIDTH//2, 20)
    draw_text(f"Points: {points} | Bank: {bank}", WIDTH//2, 60)
    if choosing:
        screen.fill((30,30,30))
        draw_text("Select the starting number:", WIDTH//2, 100, 36)
        for i, num in enumerate(available_numbers):
            draw_button(f"{num}", WIDTH//2 - 50, 150 + i*60, 100, 50,
                        (200,200,200), (255,255,255), False, partial(choose_number, num))

def draw_game():
    draw_text(f"Starting Number: {starting_number if starting_number else 'Not chosen'}", WIDTH//2, 20)
    draw_text(f"Current Number: {selected_number}", WIDTH//2, 50)
    draw_text(f"Points: {points} | Bank: {bank}", WIDTH//2, 90)
    for i, d in enumerate([2,3,4,5]):
        disabled = not (selected_number and is_valid_division(selected_number, d))
        draw_button(f"/{d}", WIDTH//2 - 130 + i*75, 140, 50, 50,
                    (100,100,100) if disabled else (100,200,100),
                    (150,255,150), disabled, partial(divide_number, d))
    for i, event in enumerate(history[-10:]):
        draw_text(event, 400, 280 + i*30, 24, (200,200,200))
    if game_phase == "game_over":
        draw_text(winner, WIDTH//2, 220, 40, (255,0,0))
        draw_button("Restart", WIDTH//2 - 50, HEIGHT - 100, 100, 50,
                    (200,200,200), (255,255,255), False, reset_game)

# =======================
# GALVENĀ SPĒLES CILPA
# =======================

reset_game()  # Pāreja uz algoritma izvēli

running = True
while running:
    screen.fill((30,30,30))
    draw_button("?", 750, 10, 40, 40, (200,200,200), (255,255,255), False, toggle_rules)
    
    if game_phase == "settings_algorithm":
        draw_settings_algorithm()
    elif game_phase == "settings_first":
        draw_settings_first()
    elif game_phase == "choose_number":
        if choosing:
            draw_choose_number()
        else:
            draw_game()
    elif game_phase in ["game", "game_over"]:
        draw_game()
    
    if show_rules:
        draw_rules()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and show_rules:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if 650 <= mouse_x <= 690 and 110 <= mouse_y <= 150:
                show_rules = False
    
    if game_phase in ["game", "game_over"] and not player_turn and selected_number and not game_over:
        ai_move()
    
    pygame.display.flip()

pygame.quit()
