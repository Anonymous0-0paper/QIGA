from config import Individual
import random

class OC:
    def __init__(self, fitness, data):
        self.fitness = fitness
        self.data = data
        self.static_power_percentage = 0.000000001

    def calculate_delay(self, task):
        frequency = random.uniform(8 * 10**9, 11 * 10**9)
        bandwidth = random.uniform(4 * 10**3, 6 * 10**3)
        communication_delay = task['data_size'] / bandwidth
        static_network_latency = 3
        computation_delay = task['weight'] / frequency
        return communication_delay + computation_delay + static_network_latency, frequency
    
    def calculate_energy(self, task):
        energy_consumption = task['weight'] * self.static_power_percentage
        return energy_consumption
    
    def schedule(self):
        individual = Individual()
        tasks = [user.applications[0].services[0] for user in self.data["User"].all()]
        total_delay = 0
        total_energy = 0
        missed_deadlines = 0
        total_task_weight = 0
        active_time = 0
        max_delay = 0

        for task in tasks:
            task_vars = vars(task)
            delay, frequency = self.calculate_delay(task_vars)
            energy = self.calculate_energy(task_vars)
            total_delay += delay
            total_energy += energy
            total_task_weight += task_vars['weight']
            if delay > task_vars['deadline']:
                missed_deadlines += 1
            active_time += delay
            if delay > max_delay:
                max_delay = delay

        num_tasks = len(tasks)
        qos = (num_tasks - missed_deadlines) / num_tasks
        avg_latency = total_delay / num_tasks if num_tasks > 0 else 0
        individual.qos = qos
        individual.resource_utilization = 1
        individual.missed_deadlines = missed_deadlines
        individual.latency = avg_latency
        individual.energy = total_energy
        individual.max_resource_latency = max_delay

        return individual

    def run(self):
        return [self.schedule()]
