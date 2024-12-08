import random
from config import *

class Individual:
    def __init__(self):
        self.CInd = []

class OE:
    def __init__(self, fitness, population_size, generation_count, data):
        self.fitness = fitness
        self.population_size = population_size
        self.generation_count = generation_count
        self.data = data

    def schedule(self):
        individual = Individual()

        count = 0
        for bs in self.data["BaseStation"].all():
            if len(bs.edge_servers) == 1:
                count += 1

        individual.CInd = [0] * (self.data['User'].count() * count)

        task_size = count

        for task_idx in range(self.data['User'].count()):
            start_idx = task_idx * task_size

            assigned_resource = random.randint(0, task_size - 1)

            individual.CInd[start_idx:start_idx + task_size] = [0] * task_size
            individual.CInd[start_idx + assigned_resource] = 1
        return individual

    def run(self):
        population = [self.schedule() for _ in range(self.population_size)]

        evaluated_population = self.fitness(population, self.data)

        return evaluated_population
