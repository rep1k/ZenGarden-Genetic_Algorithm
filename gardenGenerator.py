class GardenGen:
    def __init__(self, rows, cols, rocks, rock_pos): # TODO: Fix pre rocks > rock pos a vice versa
        self.rows = rows    # Number of rows
        self.cols = cols    # Number of cols
        self.rocks = rocks  # Number of rocks in game
        self.rock_pos = rock_pos    # Positions of rocks
        self.max_free_spaces = self.rows * self.cols - self.rocks

    def create_garden(self) -> list[list]:
        garden = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for indx, pos in enumerate(self.rock_pos):
            if indx <= self.rocks:
                if 0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols:
                    garden[pos[0]-1][pos[1]-1] = -1
        return garden
