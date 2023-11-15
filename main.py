import Individual
import random as rd

NUMBER_OF_INDIVIDUALS = 100
NUMBER_OF_GENERATIONS = 1000
TOURNAMENT_VS_ROULETE_CHANCE = 0.5


def tournament(popul):
    # Tournament will choose the best individual based on fitness
    parents = rd.choices(popul, k=4)
    parents = sorted(parents, key=lambda chromosome: chromosome.fitness, reverse=True)
    return parents[0], parents[1]


def select_roulette(popul):
    inds = []
    # Fitness sum
    max_sum = sum([c.fitness for c in popul])
    pick = rd.uniform(0, max_sum)
    current = 0
    while len(inds) < 4:
        for chromosome in popul:
            current += chromosome.fitness
            # Choose individual based on fitness (Fitness proportionate selection)
            if current > pick:
                inds.append(chromosome)
    return inds[0], inds[1]


def select(pop):
    if rd.random() > TOURNAMENT_VS_ROULETE_CHANCE:
        # print("Tournament")
        return tournament(pop)
    else:
        # print("Roulette")
        return select_roulette(pop)


def main_loop(row_input=10, col_input=12, rocks_input=6,
              rock_pos_input=((3, 2), (5, 3), (4, 5), (2, 6), (7, 9), (7, 10))):
    global best
    # with open("datalog.txt", "w") as f:
    population = []
    # for i in range(20):
    #     f.write(f'Run {i}\n')
    for _ in range(NUMBER_OF_INDIVIDUALS):
        population.append(Individual.Individual(rows=row_input, cols=col_input,
                                                rocks=rocks_input, rock_pos=rock_pos_input))

    for x in population:
        x.move()
        # print(x.fitness)

    for xx in range(NUMBER_OF_GENERATIONS):
        # Best Individual
        best = max(population, key=lambda y: y.fitness)
        nextgen = [best]
        # Go across the population with crossover and mutation and creates a new one
        for _ in range(99):
            ind1, ind2 = select(population)
            nextgen.append(ind1.crossover(ind2))
        population = nextgen
        # f.write(f'Generation: {xx + 1}, Final: {population[0].garden_spaces}, Best: {best.fitness}\n')
        print(f'Generation: {xx + 1}, Final: {population[0].garden_spaces}, Best: {best.fitness}')
        if best.fitness == population[0].garden_spaces:
            # End if all squares were marked
            # f.write('\n\n')
            break
    else:
        # If not all squares are marked then print the best one
        print()
        print('Nepohrabanych: %d' % (population[0].garden_spaces - best.fitness))

    for row in best.garden:
        print(row)
# f.close()

if __name__ == "__main__":
    map_choose = int(input("Use default garden - 0 | Use new garden - 1 ->   "))
    if map_choose:
        rows = int(input("Input rows: "))
        cols = int(input("Input cols: "))
        rocks = int(input("Input number of rocks: "))
        rock_pos_in = input("Input rock position (in format: '(row,col), (row,col)' etc.):")

        rock_pos = tuple(eval(rock_pos_in))
        if len(rock_pos) == rocks:
            main_loop(rows, cols, rocks, rock_pos)
        else:
            print("Nezhoda v pocte kamenov a ich pozicii")
        # print(rock_pos)
    else:
        main_loop()
