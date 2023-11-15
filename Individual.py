import numpy as np
import random as rd
import gardenGenerator


START_SIDE_COL = ['up', 'down']
START_SIDE_ROW = ['left', 'right']
START_PICK = ['row', 'col']
LEGAL_MOVES = ['left', 'right', 'up', 'down']


class Individual:

    def __init__(self, rows=10, cols=12, rocks=6, rock_pos=((3, 2), (5, 3), (4, 5), (2, 6), (7, 9), (7, 10))):
        self.garden = gardenGenerator.GardenGen(rows, cols, rocks, rock_pos).create_garden()
        self.garden_spaces = gardenGenerator.GardenGen(rows, cols, rocks, rock_pos).max_free_spaces
        self.start_config, self.start_pos, start_pick = self.generate_start_config()
        self.direction = self.pick_initial_direction(start_pick)
        self.max_genomes = (len(self.garden) - 1 + len(self.garden[0]) - 1) + rocks
        self.fitness = 0
        self.genes = []
        self.otocenie = self.generate_genome()
        self.rocks = rocks

    def generate_start_config(self):
        random_gen = np.random.default_rng()
        start_pick = rd.choice(START_PICK)

        starting_config = {'row': random_gen.integers(low=0, high=len(self.garden[0]) - 1),
                           'col': random_gen.integers(low=0, high=len(self.garden)),
                           'start_row': rd.choice(START_SIDE_ROW),
                           'start_col': rd.choice(START_SIDE_COL)}
        starting_position = [starting_config.get(start_pick),
                             starting_config.get(f"start_{start_pick}")]
        # Set initial direction based on starting side
        return starting_config, starting_position, start_pick

    def pick_initial_direction(self, start_pick):
        if start_pick == 'col':
            direction = 'down' if self.start_pos[1] == 'up' else 'up'
        else:
            direction = 'right' if self.start_pos[1] == 'left' else 'left'
        return direction

    def can_move(self, row, col):
        if self.is_inside_garden(row, col):
            return (len(self.garden) > row >= 0 == self.garden[row][col] and
                    0 <= col < len(self.garden[0]))

    def is_inside_garden(self, row, col):
        # Check if the position is within the boundaries of the garden
        return 0 <= row < len(self.garden) and 0 <= col < len(self.garden[0])

    def generate_genome(self):
        return [rd.randint(0, 1) for _ in range(10)]

    def move(self):

        count_paths = 0
        full_moves = 0
        path = []
        obstacle = 0

        temp_okometria = []
        path_num = 1
        num, side = self.start_pos
        move = 0
        # Set the initial position
        if side in ['up', 'down']:  # Starting on a column
            col = num
            row = 0 if side == 'up' else len(self.garden) - 1

        else:  # Starting on a row
            row = num
            col = 0 if side == 'left' else len(self.garden[0]) - 1

        prev_row = row
        prev_col = col

        while count_paths <= self.max_genomes:

            if self.can_move(row, col):

                self.garden[row][col] = path_num  # Mark the path
                path.append((row, col))
                temp_okometria.append(self.direction)
                move += 1
                prev_row = row
                prev_col = col

                next_row, next_col = self.calculate_next_position(row, col)
                row, col = next_row, next_col
                # print("[DEBUG] GARDEN ----------")
                # for gard in self.garden:
                #     print(gard)
                continue

            else:
                next_row, next_col = self.calculate_next_position(prev_row, prev_col)
                if self.is_inside_garden(next_row, next_col):

                    # print("[DEBUG] Found obstacle")
                    if self.edge_case(prev_row, prev_col, move, obstacle):
                        # print("[DEBUG] EDGE OF GARDEN")
                        row, col, path_num = self.find_new_start(path_num)

                        if row is None:  # If no new start found, break out of the loop
                            break
                        full_moves += move
                        move = 0  # Reset the move count for a new path
                        self.initialize_gene(path, temp_okometria)
                        self.otocenie = self.generate_genome()
                        path = []
                        temp_okometria = []
                        obstacle = 0
                        count_paths += 1
                        continue
                    if obstacle < 9:
                        obstacle += 1
                    else:
                        obstacle = 0
                    new_direction = self.choose_turn_direction(prev_row, prev_col, obstacle)

                    if new_direction:

                        self.direction = new_direction
                        # print("[DEBUG] New direction: ", self.direction)
                        next_row, next_col = self.calculate_next_position(prev_row, prev_col)
                        row, col = next_row, next_col
                        # print("[DEBUG] New selected row and column: ", row, col)
                        continue
                    else:

                        self.initialize_gene(path, temp_okometria)
                        obstacle = 0
                        path = []
                        temp_okometria = []
                        full_moves += move
                        if full_moves == self.garden_spaces:
                            # print("Zahrada pohrabana kompletne")
                            pass
                        break  # Monk came to place with no other options to turn
                else:
                    # print("[DEBUG] EDGE OF GARDEN")
                    row, col, path_num = self.find_new_start(path_num)
                    if row is None:  # If no new start found, break out of the loop
                        break

                    full_moves += move
                    self.initialize_gene(path, temp_okometria)
                    self.otocenie = self.generate_genome()
                    path = []
                    temp_okometria = []
                    move = 0  # Reset the move count for a new path
                    obstacle = 0
                    count_paths += 1
                    continue
        self.fitness = full_moves
        # print(temp_okometria)
        return full_moves

    def edge_case(self, row, col, move, obstacle):
        new_direction = self.choose_turn_direction(row, col, obstacle)
        if ((row == len(self.garden) - 1 or col == len(self.garden[0]) - 1 or row == 0 or col == 0)
                and move != 1 and not new_direction):
            return True
        else:
            return False

    def calculate_next_position(self, row, col, direction=None):
        if direction is None:
            direction = self.direction

        direction_delta = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
        delta_row, delta_col = direction_delta.get(direction, (0, 0))
        next_row = row + delta_row
        next_col = col + delta_col
        return next_row, next_col

    def choose_turn_direction(self, row, col, obstacle):
        # Function that chooses new direction if the monk encounters a rock
        # print("[DEBUG inside Turn func] Direction", self.direction)
        if self.direction in ['left', 'right']:
            # If moving left or right, choose up or down
            available_directions = [direc for direc in ['up', 'down'] if
                                    self.can_move(*self.calculate_next_position(row, col, direc))]
            # print("[DEBUG]From horizontal Available Directions", available_directions)
        else:
            # If moving up or down, choose left or right
            available_directions = [direc for direc in ['left', 'right'] if
                                    self.can_move(*self.calculate_next_position(row, col, direc))]

            # print("[DEBUG]From vertical Available Directions", available_directions)
        if len(available_directions) == 2:
            # print("[DEBUG] Obstacle num: ", obstacle)
            available_directions = available_directions[self.otocenie[obstacle]]
            return available_directions

        return rd.choice(available_directions) if available_directions else None

    def find_new_start(self, path_num):
        # List all unoccupied edge positions
        free_edges = []
        max_row = len(self.garden) - 1
        max_col = len(self.garden[0]) - 1

        # Check top and bottom rows for unoccupied cells
        for col in range(len(self.garden[0])):
            if self.garden[0][col] == 0:
                free_edges.append((0, col))
            if self.garden[max_row][col] == 0:
                free_edges.append((max_row, col))

        # Check leftmost and rightmost columns for unoccupied cells
        for row in range(1, len(self.garden) - 1):  # Avoid corners as they are already checked
            if self.garden[row][0] == 0:
                free_edges.append((row, 0))
            if self.garden[row][max_col] == 0:
                free_edges.append((row, max_col))

        if not free_edges:
            return None, None, path_num  # No free edge cell was found

        # Randomly select a starting position from the free edges
        row, col = rd.choice(free_edges)
        path_num += 1

        # Decide initial direction based on the edge position
        if row == 0:
            self.direction = 'down'
        elif row == max_row:
            self.direction = 'up'
        elif col == 0:
            self.direction = 'right'
        elif col == max_col:
            self.direction = 'left'

        return row, col, path_num

    def get_garden(self):
        return self.garden

    def initialize_gene(self, path, okometria):
        self.genes.append(self.otocenie)

    def print_genes(self):
        for gene in self.genes:
            print("Gene: ", gene)

    def get_fitness(self):
        return self.fitness

    def crossover(self, other):
        new_individual = Individual()

        random_choice = rd.random()
        if random_choice < 0.40:
            # jedna cast je z prveho jedinca, druha z druheho
            index = rd.randrange(len(self.genes))

            new_individual.genes = self.genes[:index] + other.genes[index:]
        elif random_choice < 0.80:
            # nahodne vyberame z prveho alebo druheho
            new_individual.genes = []
            for gen1, gen2 in zip(self.genes, other.genes):
                # print("{DEBUG} index of self.genes: ", i)
                # print("{DEBUG} other: ", len(other.genes))
                new_individual.genes.append(rd.choice([gen1, gen2]))
            new_individual.genes.append(max([gen1, gen2], key=lambda x: len(x))[len(new_individual.genes):])
        else:
            # bez krizenia
            new_individual.genes = rd.choice((self.genes, other.genes))

        # Mutacie
        for i in range(len(new_individual.genes)):
            # vygeneruje cely new_individual gen s pravdepodobnostou 6%
            random_choice = rd.random()
            if random_choice < 0.06:
                new_individual.genes[i] = new_individual.generate_genome()

        # prejdeme noveho jedinca a urcime fitness
        new_individual.move()

        return new_individual






