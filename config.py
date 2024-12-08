K_POP_SIZE = 32
K_GEN_SIZE = 60

class Individual:
    def __init__(self):
        self.QInd = []  # Quantum individual (Q-individual)
        self.CInd = []  # Classical individual (C-individual)
        self.fitness = [float('inf'), float('inf')]
        self.crowding_distance = float('inf')
        self.rank = float('inf')
        self.energy = float('inf')
        self.latency = float('inf')
        self.qos = 0
        self.resource_utilization = 0
        self.missed_deadlines = 0
        self.max_resource_latency = 0

def get_freq(model_name):
    if model_name == "E5430":
        av_frequency = 2.66 * 10e9
    elif model_name == "E5507":
        av_frequency = 2.26 * (10**9)
    elif model_name == "E5645":
        av_frequency = 2.40 * 10e9
    elif model_name == "NVIDIA Jetson Nano":
        av_frequency = 1.5 * 10e9
    elif model_name == "NVIDIA Jetson TX2":
        av_frequency = 2.0 * 10e9
    elif model_name == "Raspberry Pi 4":
        av_frequency = 1.8 * 10e9
    return av_frequency

import numpy as np
def decode(data, individual):
    resources_and_users = {es: [] for es in data['EdgeServer'].all()}
    num_resources = int(len(individual.CInd) / data['User'].count())

    for user in data['User'].all():
        start_index = (user.id - 1) * num_resources
        end_index = (user.id) * num_resources        

        assigned_resource_id = np.argmax(individual.CInd[start_index:end_index]) + 1
        edge_server = data['EdgeServer'].find_by_id(assigned_resource_id)
        
        if data['User'].find_by_id(user.id) not in resources_and_users[edge_server]:
            resources_and_users[edge_server].append(data['User'].find_by_id(user.id))
    
    return resources_and_users

def memory_is_overloaded(users, av_memory):
    mem_usage = 0
    for user in users:
        mem_usage += user.applications[0].services[0].memory_demand
    return mem_usage > av_memory

import math
def mobility_update(user, base_stations):
    user_position = user.coordinates_trace[1]
    
    min_distance = float('inf')
    nearest_base_station = None

    for base_station in base_stations:
        bs_position = (base_station.coordinates[0], base_station.coordinates[0])
        distance = math.sqrt((user_position[0] - bs_position[0]) ** 2 + (user_position[1] - bs_position[1]) ** 2)
        
        if distance < min_distance:
            min_distance = distance
            nearest_base_station = base_station
    
    user.base_station = nearest_base_station
    return nearest_base_station


from collections import deque
def get_path_delay(resource_bs_id, user_bs_id, task_data_size, data, user):
    
    nearest_base_station = mobility_update(user, data['BaseStation'].all())
    user_bs_id = nearest_base_station.id

    graph = {}
    for link in data['NetworkLink'].all():
        node1_id = link.nodes[0].base_station.id
        node2_id = link.nodes[1].base_station.id
        
        graph.setdefault(node1_id, []).append((node2_id, link.bandwidth))
        graph.setdefault(node2_id, []).append((node1_id, link.bandwidth))

    queue = deque([(resource_bs_id, 0)])
    visited = {resource_bs_id}

    while queue:
        current_node, cumulative_delay = queue.popleft()
        
        if current_node == user_bs_id:
            initial_delay = task_data_size / min(link.nodes[0].base_station.wireless_delay, link.nodes[1].base_station.wireless_delay) 
            total_delay = initial_delay + cumulative_delay
            return total_delay
        
        for neighbor, bandwidth in graph.get(current_node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                link_delay = task_data_size / bandwidth
                new_cumulative_delay = cumulative_delay + link_delay
                queue.append((neighbor, new_cumulative_delay))

    return None

def get_exe_delay(av_frequency, task_weight):
    return task_weight / av_frequency

def fitness(population, data):
    if type(population) is not list:
        population = [population]

    energy_values = []
    latency_values = []
    
    for individual in population:
        resources_and_users = decode(data, individual)
        individual.missed_deadlines = 0
        mem_flag = False
        total_resource_utilization = 0
        total_energy = 0
        total_latency = 0
        total_tasks = 0
        individual.max_resource_latency = 0

        for resource, users in resources_and_users.items():
            resource_bs_id = data['BaseStation'].find_by_id(resource.base_station.id).id
            av_frequency = get_freq(resource.model_name)
            av_memory = resource.memory

            if memory_is_overloaded(users, av_memory):
                mem_flag = True

            resource_total_energy = 0
            resource_total_latency = 0
            active_time = 0

            sorted_users = sorted(users, key=lambda user: user.applications[0].services[0].deadline)

            for user in sorted_users:
                user_bs_id = data['BaseStation'].find_by_id(user.base_station.id).id
                task = user.applications[0].services[0]

                path_delay = get_path_delay(resource_bs_id, user_bs_id, task.data_size, data, user)
                exe_delay = get_exe_delay(av_frequency, task.weight)
                delay = path_delay + exe_delay

                energy_consumption = task.weight * (resource.power_model_parameters['static_power_percentage'] / 1e9)
                resource_total_energy += energy_consumption
                resource_total_latency += delay
                active_time += exe_delay

                if delay > task.deadline:
                    individual.missed_deadlines += 1

            if sorted_users:
                resource_utilization = sum(user.applications[0].services[0].weight for user in users) / (av_frequency * active_time)
                total_resource_utilization += resource_utilization

            total_energy += resource_total_energy
            total_latency += resource_total_latency
            total_tasks += len(users)

            if active_time > individual.max_resource_latency:
                individual.max_resource_latency = active_time

        individual.qos = (data['User'].count() - individual.missed_deadlines) / data['User'].count()
        individual.energy = total_energy / data['EdgeServer'].count()
        individual.latency = total_latency / data['EdgeServer'].count()
        individual.resource_utilization = total_resource_utilization / data['EdgeServer'].count()

        energy_values.append(individual.energy)
        latency_values.append(individual.latency)

    # Normalization step
    min_energy = min(energy_values)
    max_energy = max(energy_values)
    min_latency = min(latency_values)
    max_latency = max(latency_values)

    for individual in population:
        if max_energy > min_energy:
            normalized_energy = (individual.energy - min_energy) / (max_energy - min_energy)
        else:
            normalized_energy = 0.5

        if max_latency > min_latency:
            normalized_latency = (individual.latency - min_latency) / (max_latency - min_latency)
        else:
            normalized_latency = 0.5

        penalty_weight = 1
        if mem_flag:
            mem_penalty = 100
        else:
            mem_penalty = 0
        total_penalty = individual.missed_deadlines * penalty_weight

        individual.fitness = [normalized_energy + total_penalty + mem_flag, normalized_latency + total_penalty + mem_flag]

    return population
