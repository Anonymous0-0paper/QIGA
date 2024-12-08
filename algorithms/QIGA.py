from config import *
import random
import numpy as np

class QIGA:
    def __init__(self, fitness, population_size, generation_count, data):
        self.fitness = fitness
        self.population_size = population_size
        self.generation_count = generation_count
        self.data = data
        self.distances = []

    def non_dominated_sorting(self, population):
        fronts = [[]]
        for i, individual in enumerate(population):
            individual.domination_count = 0
            individual.dominated_set = []
            
            for j, other_individual in enumerate(population):
                if i == j:
                    continue
                if self.dominates(individual.fitness, other_individual.fitness):
                    individual.dominated_set.append(other_individual)
                elif self.dominates(other_individual.fitness, individual.fitness):
                    individual.domination_count += 1
                    
            if individual.domination_count == 0:
                individual.rank = 0
                fronts[0].append(individual)
        
        current_front = 0
        while len(fronts[current_front]) > 0:
            next_front = []
            for individual in fronts[current_front]:
                for dominated_individual in individual.dominated_set:
                    dominated_individual.domination_count -= 1
                    if dominated_individual.domination_count == 0:
                        dominated_individual.rank = current_front + 1
                        next_front.append(dominated_individual)
            current_front += 1
            fronts.append(next_front)
        
        fronts.pop()
        return fronts

    def dominates(self, fitness1, fitness2):
        return all(f1 <= f2 for f1, f2 in zip(fitness1, fitness2)) and any(f1 < f2 for f1, f2 in zip(fitness1, fitness2))

    def calculate_crowding_distance(self, front):
        num_objectives = len(front[0].fitness)
        for individual in front:
            individual.crowding_distance = 0
        
        for i in range(num_objectives):
            front.sort(key=lambda ind: ind.fitness[i])
            min_fitness = front[0].fitness[i]
            max_fitness = front[-1].fitness[i]
            
            front[0].crowding_distance = float('inf')
            front[-1].crowding_distance = float('inf')
            
            for j in range(1, len(front) - 1):
                front[j].crowding_distance += (front[j + 1].fitness[i] - front[j - 1].fitness[i]) / (max_fitness - min_fitness + 1e-9)

    def _initialize_population(self):
        users = self.data['User'].all() 
        edge_servers = self.data['EdgeServer'].all()
        
        population = []
        individual = Individual()
        individual.QInd = []

        for _ in range(self.population_size):
            individual = Individual()
            individual.QInd = []
            for _ in range(len(users) * len(edge_servers)):
                theta_ij = random.uniform(0, np.pi)
                q_ij = np.array([[np.cos(theta_ij)], [np.sin(theta_ij)]])
                individual.QInd.append(q_ij)
            population.append(individual)

        return population

    def select_population(self, population, population_size):
        fronts = self.non_dominated_sorting(population)
        selected_population = []
        
        for front in fronts:
            self.calculate_crowding_distance(front)
            front.sort(key=lambda ind: (-ind.rank, -ind.crowding_distance))
            selected_population.extend(front)
            
            if len(selected_population) >= population_size:
                break
        
        return selected_population[:population_size]

    def _quantum_observation(self, population):
        for individual in population:
            classical_individual = []
            for i in range(0, len(individual.QInd), self.data['EdgeServer'].count()):
                task_qubits = individual.QInd[i:i + self.data['EdgeServer'].count()]
                probabilities = np.sin(np.array([q[1][0] for q in task_qubits])) ** 2 
                
                if np.random.rand() < 0.9:
                    selected_resource = np.argmax(probabilities)
                else:
                    selected_resource = np.random.choice(len(probabilities))
                
                classical_value = [1 if j == selected_resource else 0 for j in range(self.data['EdgeServer'].count())]
                classical_individual.extend(classical_value)

            individual.CInd = classical_individual

        return population

    def _quantum_cnot_gate(self, target, control):
        if control[1][0] > 0.5:
            target = np.array([[target[1][0]], [target[0][0]]])
        return target

    def _quantum_phase_gate(self, qubit, phase):
        phase_matrix = np.array([[np.exp(1j * phase), 0], [0, np.exp(-1j * phase)]])
        return np.dot(phase_matrix, qubit)

    def _quantum_mutation(self, individual, generation):
        mutation_rate = 0.2
        for i in range(len(individual.QInd)):
            if np.random.rand() < mutation_rate:
                control_qubit = individual.QInd[i]
                if i + 1 < len(individual.QInd):
                    target_qubit = individual.QInd[i + 1]
                    individual.QInd[i + 1] = self._quantum_cnot_gate(target_qubit, control_qubit)

                phase = (np.pi / 4) * (generation / self.generation_count)
                individual.QInd[i] = self._quantum_phase_gate(control_qubit, phase)
        return individual

    def _quantum_offspring_generation(self, population, generation):
        fronts = self.non_dominated_sorting(population)
        
        for front in fronts:
            self.calculate_crowding_distance(front)

        new_population = []
        for front in fronts:
            if len(new_population) + len(front) <= self.population_size:
                new_population.extend(front)
            else:
                sorted_front = sorted(front, key=lambda ind: ind.crowding_distance, reverse=True)
                new_population.extend(sorted_front[:self.population_size - len(new_population)])
                break
        
        offspring_population = []
        half_population_size = self.population_size // 2
        for i in range(half_population_size):
            parent1 = self._quantum_tournament_selection(new_population)
            parent2 = self._quantum_tournament_selection(new_population)
            
            offspring1, offspring2 = self._quantum_crossover(parent1, parent2)
            offspring_population.extend([
                self._quantum_mutation(offspring1, generation),
                self._quantum_mutation(offspring2, generation),
            ])
        
        return offspring_population
    
    def _quantum_tournament_selection(self, population, tournament_size=3):
        tournament = np.random.choice(population, tournament_size, replace=False)
        sorted_tournament = sorted(tournament, key=lambda ind: (ind.rank, -ind.crowding_distance))
        best_individual = sorted_tournament[0]
        return best_individual

    def _quantum_crossover(self, parent1, parent2, crossover_rate=0.8):
        offspring1 = Individual()
        offspring2 = Individual()

        if np.random.rand() < crossover_rate:
            theta_c = np.pi / 4
            R_theta_c = np.array([[np.cos(theta_c), -np.sin(theta_c)], [np.sin(theta_c), np.cos(theta_c)]])
            R_theta_nc = np.array([[np.cos(-theta_c), -np.sin(-theta_c)], [np.sin(-theta_c), np.cos(-theta_c)]])
            
            for i in range(len(parent1.QInd)):
                offspring1.QInd.append(np.dot(R_theta_c, parent1.QInd[i]))
                offspring2.QInd.append(np.dot(R_theta_nc, parent2.QInd[i]))
        else:
            offspring1.QInd = parent1.QInd
            offspring2.QInd = parent2.QInd

        return offspring1, offspring2

    def _quantum_elitism_selection(self, population, new_population, size):
        combined_population = population + new_population
        fronts = self.non_dominated_sorting(combined_population)

        selected_population = []
        for front in fronts:
            self.calculate_crowding_distance(front)
            front.sort(key=lambda ind: (ind.rank, -ind.crowding_distance))
            if len(selected_population) + len(front) <= size:
                selected_population.extend(front)
            else:
                selected_population.extend(front[:size - len(selected_population)])
                break
    
        def euclidean_distance(fitness):
            return np.sqrt(fitness[0]**2 + fitness[1]**2)

        if len(selected_population) < size:
            candidates = [ind for ind in combined_population if ind not in selected_population]
            distances = [(ind, euclidean_distance(ind.fitness)) for ind in candidates]
            distances.sort(key=lambda x: x[1])
            additional_candidates = [ind for ind, _ in distances[:size - len(selected_population)]]
            
            selected_population.extend(additional_candidates)
        return selected_population

    def run(self):
        population = self._initialize_population()
        population = self._quantum_observation(population)
        population = self.fitness(population, self.data)

        def euclidean_distance(fitness):
            return np.sqrt(fitness[0]**2 + fitness[1]**2)

        best_individual = min(population, key=lambda ind: euclidean_distance(ind.fitness))

        for i in range(self.generation_count):
            new_population = self._quantum_offspring_generation(population, i)
            new_population = self._quantum_observation(new_population)
            new_population = self.fitness(new_population, self.data)

            population = self._quantum_elitism_selection(population, new_population, self.population_size)
            best_individual = min(population, key=lambda ind: euclidean_distance(ind.fitness))
        
        return population
