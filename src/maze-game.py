'''
Floating Maze
Version 20241110
Copyright: DOF Studio
'''

import pygame
import random
import numpy
from collections import deque
import json
import time
from tkinter import Tk, filedialog

# Initialize Pygame and Tkinter for file dialog
pygame.init()
Tk().withdraw()  # Hide the root window for Tkinter

# Constants and global settings
DEFAULT_TILE_SIZE = 16
DEFAULT_MAZE_WIDTH = 56   # Width and height should be odd numbers
DEFAULT_MAZE_HEIGHT = 42
DEFAULT_MOVE_RANGE = 20   # Number of steps for forward movement limit
DEFAULT_DIFFICULTY = 32  # Default difficulty level
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Extended Colors
LIGHT_GRAY = (211, 211, 211)
DARK_GRAY = (169, 169, 169)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
BEIGE = (245, 245, 220)
TURQUOISE = (64, 224, 208)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
MAROON = (128, 0, 0)
NAVY = (0, 0, 128)


# Global variables for customization and timing
custom_player_default = "./res/res.ch.png"
custom_background_default = "./res/res.bk.png"
custom_player_image = None
custom_background_image = None
TILE_SIZE = DEFAULT_TILE_SIZE
current_seed = None
start_time = None
difficulty_level = DEFAULT_DIFFICULTY

# Constants for water spread
WATER_SPREAD_DELAY = 5           # Delay for 5 seconds
WATER_SPREAD_RATE_NORMAL = 6     # Spread rate for non-downward paths (cells per second)
WATER_SPREAD_RATE_DOWNWARD = 10  # Spread rate for downward paths (cells per second)

# Initialize the water queue
water_queue = deque()

# Load Default resources
if custom_player_default != None:
    custom_player_image = pygame.image.load(custom_player_default)
    custom_player_image = pygame.transform.smoothscale(custom_player_image, (TILE_SIZE, TILE_SIZE))
if custom_background_default != None:
    custom_background_image = pygame.image.load(custom_background_default)
    custom_background_image = pygame.transform.smoothscale(custom_background_image, (960, 640))

# Global timeer class
class Timer:
    def __init__(self):
        self.last_time = time.time()
        self.delta_time = 0.0
        self.total_time = 0.0

    def update(self):
        current_time = time.time()
        self.delta_time = current_time - self.last_time
        self.total_time += self.delta_time
        self.last_time = current_time

    def get_delta_time(self):
        return self.delta_time

    def get_total_time(self):
        return self.total_time

# AI Assitant to find path
def find_path_within_range(maze, start, end, max_steps):
    queue = deque([(start, 0)])  # The queue holds tuples of (position, step_count)
    visited = set()
    visited.add(start)
    parent = {start: None}

    while queue:
        current, steps = queue.popleft()
        if current == end:
            break  # Path found

        x, y = current
        if steps < max_steps:  # Only continue if the step limit is not exceeded
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Right, Down, Left, Up
                nx, ny = x + dx, y + dy
                if (0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and
                    maze[ny][nx] in (' ', 'E') and (nx, ny) not in visited):
                    queue.append(((nx, ny), steps + 1))
                    visited.add((nx, ny))
                    parent[(nx, ny)] = current

    # Reconstruct the path from end to start
    path = []
    step = end
    while step:
        path.append(step)
        step = parent.get(step)
    path.reverse()

    return path if path and path[0] == start else []  # Return the path if valid, otherwise an empty list

# Animation to make it smoother
def animate_movement(screen, clock, maze, player_pos, path):
    for step in path[1:]:  # Skip the starting position, as the player is already there
        player_pos[0], player_pos[1] = step
        draw_maze(screen, maze)

        # Draw the player at the current step position
        if custom_player_image:
            screen.blit(custom_player_image, (player_pos[0] * TILE_SIZE, player_pos[1] * TILE_SIZE))
        else:
            pygame.draw.rect(screen, BLUE, (player_pos[0] * TILE_SIZE, player_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Draw the end position in red to make it clear
        pygame.draw.rect(screen, RED, ((len(maze[0]) - 2) * TILE_SIZE, (len(maze) - 2) * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        pygame.display.flip()  # Update the screen to show the player's new position
        clock.tick(FPS)  # Control the speed of animation

# Function to show an input box with a submit button
def show_input_box(screen, prompt, x, y, width, height, digit_only=False):
    font = pygame.font.Font(None, 30)
    input_text = ""
    input_active = True
    submit_button_rect = pygame.Rect(x + width + 10, y, 80, height)

    while input_active:
        screen.fill(WHITE)
        pygame.draw.rect(screen, WHITE, (x, y, width, height))
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)

        # Draw the Submit button
        create_button(screen, "Submit", x + width + 10, y, 80, height, GRAY, (180, 180, 180))

        # Display the prompt and input text
        prompt_surface = font.render(prompt, True, BLACK)
        screen.blit(prompt_surface, (x, y - 30))
        text_surface = font.render(input_text, True, BLACK)
        screen.blit(text_surface, (x + 5, y + 5))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if digit_only and event.unicode.isdigit():
                        input_text += event.unicode
                    elif not digit_only:
                        input_text += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if submit_button_rect.collidepoint(mouse_x, mouse_y):
                    input_active = False  # Exit the loop when the submit button is clicked

        # Limit input length to prevent overflow
        input_text = input_text[:width // 10]

    return input_text.strip()

# Function to create a button
def create_button(screen, text, x, y, width, height, inactive_color, active_color, font_size=30):
    font = pygame.font.Font(None, font_size)
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
        if click[0] == 1:  # Button is clicked (left mouse button)
            return True  # Only return True when the button is clicked
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))

    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)
    return False  # Return False when not clicked

# Function to enter the setting screen
def show_settings_screen(screen):
    global TILE_SIZE, custom_player_image, custom_background_image, difficulty_level
    font = pygame.font.Font(None, 36)
    running = True

    while running:
        screen.fill(WHITE)
        if custom_background_image:
            screen.blit(custom_background_image, (0, 0))
        title = font.render("Settings", True, BLACK)
        screen.blit(title, (50, 20))

        # Button positions and dimensions
        resize_button_rect = pygame.Rect(50, 100, 300, 50)
        upload_player_button_rect = pygame.Rect(50, 170, 300, 50)
        upload_background_button_rect = pygame.Rect(50, 240, 300, 50)
        adjust_difficulty_button_rect = pygame.Rect(50, 310, 300, 50)
        back_button_rect = pygame.Rect(50, 380, 300, 50)

        # Draw the buttons
        create_button(screen, "Resize Tile Size", 50, 100, 300, 50, GRAY, (180, 180, 180))
        create_button(screen, "Upload Player Image", 50, 170, 300, 50, GRAY, (180, 180, 180))
        create_button(screen, "Upload Background Image", 50, 240, 300, 50, GRAY, (180, 180, 180))
        create_button(screen, "Adjust Difficulty", 50, 310, 300, 50, GRAY, (180, 180, 180))
        create_button(screen, "Back to Main Menu", 50, 380, 300, 50, GRAY, (180, 180, 180))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Check if Resize Tile Size button is clicked
                if resize_button_rect.collidepoint(mouse_x, mouse_y):
                    new_tile_size = show_input_box(screen, "Enter new tile size (digits only):", 50, 450, 300, 50, digit_only=True)
                    if new_tile_size.isdigit() and int(new_tile_size) > 0:
                        TILE_SIZE = int(new_tile_size)
                        show_notification(screen, f"Tile size set to {TILE_SIZE}", 1500)

                # Check if Upload Player Image button is clicked
                elif upload_player_button_rect.collidepoint(mouse_x, mouse_y):
                    image_path = filedialog.askopenfilename(title="Select Player Image")
                    if image_path:
                        custom_player_image = pygame.image.load(image_path)
                        custom_player_image = pygame.transform.smoothscale(custom_player_image, (TILE_SIZE, TILE_SIZE))
                        show_notification(screen, "Player image uploaded successfully!", 1500)

                # Check if Upload Background Image button is clicked
                elif upload_background_button_rect.collidepoint(mouse_x, mouse_y):
                    image_path = filedialog.askopenfilename(title="Select Background Image")
                    if image_path:
                        custom_background_image = pygame.image.load(image_path)
                        custom_background_image = pygame.transform.smoothscale(custom_background_image, (960, 640))
                        show_notification(screen, "Background image uploaded successfully!", 1500)

                # Check if Adjust Difficulty button is clicked
                elif adjust_difficulty_button_rect.collidepoint(mouse_x, mouse_y):
                    new_difficulty = show_input_box(screen, "Enter difficulty level (1-100):", 50, 450, 300, 50, digit_only=True)
                    if new_difficulty.isdigit() and 1 <= int(new_difficulty) <= 100:
                        difficulty_level = int(new_difficulty)
                        show_notification(screen, f"Difficulty set to {difficulty_level}", 1500)

                # Check if Back button is clicked
                elif back_button_rect.collidepoint(mouse_x, mouse_y):
                    running = False  # Exit the settings screen

        pygame.display.flip()

# Function to initialize water grid
def initialize_water_grid(width, height):
    """Initialize a grid to track water-occupied cells."""
    return [[False for _ in range(width)] for _ in range(height)]

# Function to initialize water in the starting position
def initialize_water(water_grid, water_queue, start_pos):
    """Initialize water at the starting position."""
    x, y = start_pos
    water_grid[y][x] = True
    water_queue.append((x, y, 'normal'))  # Start spreading normally

# Update water in the grid
def update_water(maze, water_grid, water_queue, delta_time, water_parameters):
    """
    Update water spread based on elapsed time.

    Args:
        maze: The maze grid.
        water_grid: Grid tracking water-occupied cells.
        water_queue: Queue managing water spread events.
        delta_time: Time elapsed since last update.
        water_parameters: Dictionary containing spread rates and other configurations.
    """
    # Accumulate elapsed time
    water_parameters['elapsed'] += delta_time
    
    # Get parameters
    rate_normal = water_parameters['normal']
    rate_downrard = water_parameters['downward']

    # Process water spread based on elapsed time and spread rates
    while water_queue:
        x, y, direction = water_queue[0]

        # Determine spread rate based on direction
        if direction == 'downward':
            spread_rate = rate_downrard
        else:
            spread_rate = rate_normal
            
        # Introduce some random term
        random_ela = numpy.random.rand() * 1 / spread_rate
        
        # If a bonus happens, remove the time increment
        if numpy.random.rand() * 0.25 > numpy.random.rand():
            water_parameters['elapsed'] -= numpy.random.rand() * 0.25 / spread_rate
            water_parameters['elapsed'] = max(water_parameters['elapsed'], 0)

        # Check if enough time has passed to spread to next cell
        if water_parameters['elapsed'] >= (1 / spread_rate + random_ela):
            water_queue.popleft()  # Remove the current event
            water_parameters['elapsed'] -= (1 / spread_rate + random_ela)   # Reset elapsed time

            # Determine possible directions to spread
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left, Right, Up, Down
            # Optionally shuffle directions for randomness
            random.shuffle(directions)

            for dx, dy in directions:
                nx, ny = x + dx, y + dy

                # Check bounds
                if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze):
                    # Check if the cell is a path and not already occupied by water
                    if maze[ny][nx] in (' ', 'E') and not water_grid[ny][nx]:
                        # Determine if the spread is downward
                        if dy == 1:
                            new_direction = 'downward'
                        else:
                            new_direction = 'normal'

                        # Occupy the cell with water
                        water_grid[ny][nx] = True

                        # Enqueue the new water spread event
                        water_queue.append((nx, ny, new_direction))
            # Continue processing without breaking to allow spreading in all directions
        else:
            break  # Not enough time has passed to spread further

# Function to generate a maze using DFS
def generate_maze(width, height, seed=None, difficulty=DEFAULT_DIFFICULTY):
    if seed is not None:
        random.seed(seed)
    maze = [['#' for _ in range(width)] for _ in range(height)]
    start_x, start_y = 1, 1

    def carve_passages(x, y):
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width - 1 and 1 <= ny < height - 1 and maze[ny][nx] == '#':
                maze[ny][nx] = ' '
                maze[y + dy // 2][x + dx // 2] = ' '
                carve_passages(nx, ny)

    maze[start_y][start_x] = ' '
    carve_passages(start_x, start_y)
    maze[height - 2][width - 2] = 'E'  # Mark the exit

    # Find the solution path to protect it when adding dead ends
    solution_path = find_solution_path(maze, (start_x, start_y), (width - 2, height - 2))

    # Add dead ends based on difficulty without modifying the solution path
    add_dead_end_branches(maze, difficulty, solution_path)
    return maze

# Function to find the solution path using BFS
def find_solution_path(maze, start, end):
    width = len(maze[0])
    height = len(maze)
    queue = deque()
    queue.append((start, [start]))
    visited = set()
    visited.add(start)

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == end:
            return set(path)  # Return the solution path as a set for quick lookup

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < width and 0 <= ny < height and
                maze[ny][nx] in (' ', 'E') and (nx, ny) not in visited):
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))
    return set()  # Return empty set if no path is found

# Function to add dead-end branches to the maze without affecting the solution path
def add_dead_end_branches(maze, difficulty, solution_path):
    """
    Adds dead-end branches to the maze to increase difficulty.
    The number and length of branches are determined by the difficulty level.
    """
    num_branches = min(difficulty, 100)  # Cap the number of branches to prevent over-fragmentation
    width = len(maze[0])
    height = len(maze)
    branch_length_range = max(1, min(difficulty // 10, 10))  # Adjust branch length based on difficulty

    potential_branch_points = [
        (x, y) for y in range(1, height - 1) for x in range(1, width - 1)
        if maze[y][x] == ' ' and (x, y) in solution_path
    ]

    random.shuffle(potential_branch_points)

    branches_added = 0

    for (x, y) in potential_branch_points:
        if branches_added >= num_branches:
            break

        # Possible directions to branch off (ensure they don't go back into the solution path)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (1 <= nx < width - 1 and 1 <= ny < height - 1 and maze[ny][nx] == '#'):
                # Carve a new branch
                maze[ny][nx] = ' '
                maze[y + dy // 2][x + dx // 2] = ' '

                # Determine the length of the branch
                branch_length = random.randint(1, branch_length_range)

                current_x, current_y = nx, ny
                branch_successful = True

                for _ in range(branch_length):
                    # Choose a new direction for the branch, avoiding reversing
                    possible_dirs = [d for d in directions if d != (-dx, -dy)]
                    if not possible_dirs:
                        break
                    branch_dir = random.choice(possible_dirs)
                    bdx, bdy = branch_dir
                    next_x, next_y = current_x + bdx, current_y + bdy

                    # Check if the next cell is available for carving
                    if (1 <= next_x < width - 1 and 1 <= next_y < height - 1 and
                        maze[next_y][next_x] == '#'):

                        # Ensure that carving here doesn't create a loop
                        if count_wall_neighbors(maze, next_x, next_y) >= 3:
                            maze[next_y][next_x] = ' '
                            maze[current_y + bdy // 2][current_x + bdx // 2] = ' '
                            current_x, current_y = next_x, next_y
                        else:
                            branch_successful = False
                            break
                    else:
                        branch_successful = False
                        break

                # Terminate the branch to make it a dead end
                # No action needed since the loop stops carving further

                branches_added += 1
                break  # Move to the next branch point after adding one branch

# Function to count wall neighbors
def count_wall_neighbors(maze, x, y):
    """Helper function to count how many neighboring cells are walls."""
    count = 0
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if maze[ny][nx] == '#':
            count += 1
    return count

# Adjust move range dynamically based on path type
def adjust_move_range(maze, player_pos):
    x, y = player_pos
    straight_paths = 0

    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == ' ':
            straight_paths += 1

    if straight_paths == 2:  # Path is a corner
        return int(DEFAULT_MOVE_RANGE * 0.5)
    elif straight_paths >= 3:  # Path is straight with more options
        return int(DEFAULT_MOVE_RANGE * 1.2)
    return DEFAULT_MOVE_RANGE

# Save game state to a JSON file, including the maze structure and other data
def save_game_state(player_pos, maze, seed, start_time, difficulty, water_grid, water_queue, water_parameters):
    current_time = time.time() - start_time
    game_state = {
        "player_pos": player_pos,
        "maze": maze,
        "seed": seed,
        "time_elapsed": current_time,
        "difficulty": difficulty,
        "water_grid": water_grid,
        "water_queue": list(water_queue),  # Convert deque to list for JSON serialization
        "water_parameters": water_parameters
    }
    # Open a file dialog to choose the save location
    save_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        title="Save Game State"
    )
    if save_path:
        with open(save_path, "w") as file:
            json.dump(game_state, file)
        show_notification(screen, "Game saved successfully!", 1500)

# Load game state from a custom location, ensuring the same maze structure is loaded
def load_game_state():
    # Open a file dialog to choose the file to load
    load_path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")],
        title="Load Game State"
    )
    if load_path:
        try:
            with open(load_path, "r") as file:
                game_state = json.load(file)
            return (
                game_state["player_pos"],
                game_state["maze"],
                game_state["seed"],
                game_state["time_elapsed"],
                game_state["difficulty"],
                game_state["water_grid"],
                deque(game_state["water_queue"]),
                game_state["water_parameters"]
            )
        except (FileNotFoundError, json.JSONDecodeError):
            show_notification(screen, "Failed to load the game. Invalid file or format.", 1500)
            return None
    else:
        show_notification(screen, "Loading canceled.", 1500)
        return None

# Show notification in game
def show_notification(screen, message, duration=1500):
    font = pygame.font.Font(None, 36)
    notification = font.render(message, True, ORANGE)
    screen.blit(notification, (10, 10))
    pygame.display.flip()
    pygame.time.wait(duration)

# Draw the maze game 
def draw_maze(screen, maze, water_grid=None, path=None):
    if custom_background_image:
        screen.blit(custom_background_image, (0, 0))
    else:
        screen.fill(WHITE)

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if water_grid and water_grid[y][x]:
                color = LIGHT_BLUE  # Water-occupied cell
            elif cell == '#':
                color = BLACK
            elif cell == 'E':
                color = RED
            else:
                color = WHITE
            
            # if not WHITE, display
            if color != WHITE:
                pygame.draw.rect(screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    if path:
        for x, y in path:
            pygame.draw.rect(screen, GREEN, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

# Check if the player encounters the water
def check_player_collision(player_pos, water_grid):
    """Check if the player has collided with water."""
    x, y = player_pos
    if water_grid[y][x]:
        return True
    return False

# Water speed schedule
def water_speed_schedule(water_parameters, round_num):
    # Calculate next water_speed
    if water_parameters is not None:
        water_parameters['normal'] = WATER_SPREAD_RATE_NORMAL * numpy.log(numpy.exp(1) + round_num)
        water_parameters['downward'] = WATER_SPREAD_RATE_DOWNWARD * numpy.log(numpy.exp(1) + round_num)
    return water_parameters
    
# Main function to play the game
def play_maze(maze_width, maze_height, move_range, seed=None):
    global TILE_SIZE, water_grid, start_time, difficulty_level
    start_time = time.time()
    round_count = 0
    
    while True:  # Loop to automatically transition to the next game after winning
        if seed is not None:
            seed += 11  # Increment the seed for a new maze generation
            
        # Accumulate the round 
        round_count += 1

        maze = generate_maze(maze_width, maze_height, seed, difficulty_level)
        screen_width = maze_width * TILE_SIZE
        screen_height = maze_height * TILE_SIZE + 60  # Additional space for buttons
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Maze Game with Enhanced Features")

        clock = pygame.time.Clock()
        player_pos = [1, 1]
        end_pos = (maze_width - 2, maze_height - 2)
        dragging = False  # Track whether the player is being dragged
        
        # Initialize water structures but do NOT initialize water deque
        water_time = 0
        water_grid = initialize_water_grid(maze_width, maze_height)
        water_queue = deque()
        water_parameters = {'elapsed': 0, 
                            'normal' : WATER_SPREAD_RATE_NORMAL,
                            'downward': WATER_SPREAD_RATE_DOWNWARD}
        water_parameters = water_speed_schedule(water_parameters, round_count)
        water_initial_place = (1, 1)
        
        # Initialize the global timer
        global_timer = Timer()
            
        running = True
        while running:
            # Update water spread
            global_timer.update()
            delta_time = global_timer.get_delta_time()
            water_time += delta_time
            # This is the delayed water appearance
            if water_time > WATER_SPREAD_DELAY:
                if len(water_queue) == 0:
                    initialize_water(water_grid, water_queue, water_initial_place)
                else:
                    update_water(maze, water_grid, water_queue, delta_time, water_parameters)

            move_range = adjust_move_range(maze, player_pos)
            screen.fill(WHITE)
            draw_maze(screen, maze, water_grid=water_grid, path = None) # do not provide navigation now

            # Draw the save, load, and settings buttons
            save_button_rect = pygame.Rect(10, screen_height - 50, 80, 40)
            load_button_rect = pygame.Rect(100, screen_height - 50, 80, 40)
            settings_button_rect = pygame.Rect(190, screen_height - 50, 120, 40)

            save_button = create_button(screen, "Save", 10, screen_height - 50, 80, 40, GRAY, (180, 180, 180))
            load_button = create_button(screen, "Load", 100, screen_height - 50, 80, 40, GRAY, (180, 180, 180))
            settings_button = create_button(screen, "Settings", 190, screen_height - 50, 120, 40, GRAY, (180, 180, 180))

            # Draw the player and the end position
            pygame.draw.rect(screen, RED, (end_pos[0] * TILE_SIZE, end_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            if custom_player_image:
                screen.blit(custom_player_image, (player_pos[0] * TILE_SIZE, player_pos[1] * TILE_SIZE))
            else:
                pygame.draw.rect(screen, BLUE, (player_pos[0] * TILE_SIZE, player_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                
            # Handling events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                   # Check if the save button is clicked
                    if save_button_rect.collidepoint(mouse_x, mouse_y):
                        save_game_state(player_pos, maze, seed, start_time, difficulty_level, water_grid, water_queue, water_parameters)
                
                    # Check if the load button is clicked
                    elif load_button_rect.collidepoint(mouse_x, mouse_y):
                        loaded_data = load_game_state()
                        if loaded_data:
                            player_pos, maze, current_seed, elapsed_time, loaded_difficulty, loaded_water_grid, loaded_water_queue, loaded_water_parameters = loaded_data
                            difficulty_level = loaded_difficulty
                            start_time = time.time() - elapsed_time  # Resume the saved time
                            # Reinitialize water structures based on loaded maze
                            water_grid = loaded_water_grid
                            water_queue = loaded_water_queue
                            water_parameters = loaded_water_parameters
                            break  # Reload the maze with loaded data

                    # Check if the settings button is clicked
                    elif settings_button_rect.collidepoint(mouse_x, mouse_y):
                        show_settings_screen(screen)  # Open the settings screen

                    else:
                        grid_x = mouse_x // TILE_SIZE
                        grid_y = mouse_y // TILE_SIZE

                        # Ensure grid_x and grid_y are within maze bounds
                        if 0 <= grid_x < maze_width and 0 <= grid_y < maze_height:
                            if [grid_x, grid_y] == player_pos:
                                dragging = True
                            elif maze[grid_y][grid_x] in (' ', 'E'):  # Click-to-move functionality
                                path = find_path_within_range(maze, tuple(player_pos), (grid_x, grid_y), move_range)
                                if path:
                                    animate_movement(screen, clock, maze, player_pos, path)
                                    if [grid_x, grid_y] == end_pos:
                                        show_notification(screen, "Congratulations! You reached the end!", 2000)
                                        running = False  # End current game to start a new game

                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging = False  # Stop dragging when the mouse button is released

            # Handling dragging
            if dragging:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // TILE_SIZE
                grid_y = mouse_y // TILE_SIZE

                # Ensure grid_x and grid_y are within maze bounds
                if 0 <= grid_x < maze_width and 0 <= grid_y < maze_height:
                    if maze[grid_y][grid_x] == '#':
                        dragging = False  # Stop dragging if the mouse moves over a wall
                    elif maze[grid_y][grid_x] in (' ', 'E'):
                        player_pos[0], player_pos[1] = grid_x, grid_y
                        if [grid_x, grid_y] == end_pos:
                            show_notification(screen, "Congratulations! You reached the end!", 2000)
                            running = False

            # Check if player reached the end
            if player_pos == list(end_pos):
                show_notification(screen, "Congratulations! You reached the end!", 2000)
                running = False
                
            # Inside the main game loop after updating player_pos
            if check_player_collision(player_pos, water_grid):
                show_notification(screen, "Game Over! You were flooded by water.", 2000)
                round_count = 0  # Reset Round Counter
                running = False  # End the current game


            pygame.display.flip()

# Welcome screen with buttons and input prompts
def show_welcome_screen(screen):
    font = pygame.font.Font(None, 48)
    screen.fill(WHITE)
    if custom_background_image:
        screen.blit(custom_background_image, (0, 0))
    title = font.render("Welcome to the Maze Game", True, BLACK)
    screen.blit(title, (50, 50))

    # Button rectangles for click detection
    start_button_rect = pygame.Rect(50, 150, 200, 50)
    settings_button_rect = pygame.Rect(50, 220, 200, 50)
    load_button_rect = pygame.Rect(50, 290, 200, 50)

    while True:
        screen.fill(WHITE)
        if custom_background_image:
            screen.blit(custom_background_image, (0, 0))
        screen.blit(title, (50, 50))

        # Draw the buttons
        create_button(screen, "Start Game", 50, 150, 200, 50, GREEN, (0, 200, 0))
        create_button(screen, "Settings", 50, 220, 200, 50, BLUE, (0, 0, 200))
        create_button(screen, "Load Game", 50, 290, 200, 50, RED, (200, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Check if the buttons are clicked
                if start_button_rect.collidepoint(mouse_x, mouse_y):
                    seed_input = show_input_box(screen, "Enter seed (digits only, or leave blank):", 50, 350, 300, 50, digit_only=True)
                    current_seed = int(seed_input) if seed_input else None
                    play_maze(DEFAULT_MAZE_WIDTH, DEFAULT_MAZE_HEIGHT, DEFAULT_MOVE_RANGE, current_seed)

                elif settings_button_rect.collidepoint(mouse_x, mouse_y):
                    show_settings_screen(screen)

                elif load_button_rect.collidepoint(mouse_x, mouse_y):
                    loaded_data = load_game_state()
                    if loaded_data:
                        player_pos, maze, current_seed, elapsed_time, loaded_difficulty = loaded_data
                        difficulty_level = loaded_difficulty
                        play_maze(len(maze[0]), len(maze), DEFAULT_MOVE_RANGE, current_seed)
                    else:
                        show_notification(screen, "No saved game found!", 1500)

        pygame.display.flip()

# Run the game
screen = pygame.display.set_mode((960, 640))  # Increased resolution for better GUI
pygame.display.set_caption("Maze Game")
show_welcome_screen(screen)
