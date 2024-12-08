from config import *
import numpy as np
import random

class MOHEFT:
    def __init__(self, fitness, population_size, generation_count, data):
        self.fitness = fitness
        self.population_size = population_size
        self.generation_count = generation_count
        self.data = data

    def initialize_population(self):
        population = []
        for _ in range(self.population_size):
            individual = Individual()
            individual.CInd = []
            for _ in range(self.data['User'].count() * self.data['EdgeServer'].count()):
                gene = random.randint(0, 1)
                individual.CInd.append(gene)
            population.append(individual)
        return population

    def apply_selection(self, population):
        dominated_counts = [0] * len(population)
        domination_sets = [[] for _ in range(len(population))]

        for i in range(len(population)):
            for j in range(len(population)):
                if i != j:
                    if self.dominates(population[i].fitness, population[j].fitness):
                        domination_sets[i].append(j)
                    elif self.dominates(population[j].fitness, population[i].fitness):
                        dominated_counts[i] += 1

        pareto_fronts = []
        current_front = []
        
        for i in range(len(population)):
            if dominated_counts[i] == 0:
                current_front.append(i)

        pareto_fronts.append(current_front)

        while current_front:
            next_front = []
            for index in current_front:
                for dominated_index in domination_sets[index]:
                    dominated_counts[dominated_index] -= 1
                    if dominated_counts[dominated_index] == 0:
                        next_front.append(dominated_index)
            current_front = next_front
            if current_front:
                pareto_fronts.append(current_front)

        selected_population = []
        for front in pareto_fronts:
            if len(selected_population) + len(front) > self.population_size:
                selected_population.extend(self.select_from_front(front, self.population_size - len(selected_population)))
                break
            selected_population.extend(front)

        return [population[i] for i in selected_population]

    def dominates(self, fitness1, fitness2):
        return all(f1 <= f2 for f1, f2 in zip(fitness1, fitness2)) and any(f1 < f2 for f1, f2 in zip(fitness1, fitness2))

    def select_from_front(self, front, remaining):
        return np.random.choice(front, remaining, replace=False).tolist()
    
    def run(self):
        population = self.initialize_population()
        self.fitness(population, self.data)  # Evaluate initial fitness

        for i in range(self.generation_count):
            population = self.fitness(population, self.data)
            population = self.apply_selection(population)

        return population
