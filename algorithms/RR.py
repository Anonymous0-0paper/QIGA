from config import *

class RR:
    def __init__(self, fitness, population_size, generation_count, data):
        self.fitness = fitness
        self.population_size = population_size
        self.generation_count = generation_count
        self.data = data
        self.current_resource_idx = 0

    def schedule(self):
        individual = Individual()
        individual.CInd = [0] * (self.data['User'].count() * (self.data['EdgeServer'].count()))

        task_size = self.data['EdgeServer'].count()

        for task_idx in range(self.data['User'].count()):
            start_idx = task_idx * task_size

            assigned_resource = self.current_resource_idx % task_size

            individual.CInd[start_idx:start_idx + task_size] = [0] * task_size
            individual.CInd[start_idx + assigned_resource] = 1

            self.current_resource_idx += 1

        return individual

    def run(self):
        individual = self.schedule()


        population = [individual]
        evaluated_population = self.fitness(population, self.data)

        return evaluated_population
