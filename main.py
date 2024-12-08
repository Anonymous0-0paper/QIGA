from edge_sim_py import *

import os
from algorithms import QIGA, MOHEFT, RR, RA, OE, OC
from config import *
import pandas as pd

simulator = Simulator()

data = {
    'BaseStation': BaseStation,
    'EdgeServer': EdgeServer,
    'User': User,
    'NetworkSwitch': NetworkSwitch,
    'NetworkLink': NetworkLink
}

def individual_to_dict(ind):
    return {
        'fitness': ind.fitness,
        'energy': ind.energy,
        'latency': ind.latency,
        'qos': ind.qos,
        'resource_utilization': ind.resource_utilization,
        'missed_deadlines': ind.missed_deadlines,
        'completion_time': ind.max_resource_latency
    }

def save_population(es_count, user_count, algorithm_name, best_individuals):
    output_dir = f"scheme/outputs/ES_{es_count}/users_{user_count}/"
    os.makedirs(output_dir, exist_ok=True)

    df = pd.DataFrame([individual_to_dict(ind) for ind in best_individuals])
    df.to_csv(f"{output_dir}{algorithm_name}_best_population.csv", index=False)
    
edge_server_count = [30, 35, 40, 45, 50]
user_counts = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
for es_count in edge_server_count:
    for user_count in user_counts:
        input_file = f"scheme/input/ES-{es_count}_ED-{user_count}.json"
        simulator.initialize(input_file=input_file)

        print(f'Running simulations for {user_count} users with {es_count} edge servers...')

        print(f'Running QIGA')
        QIGA_alg = QIGA.QIGA(fitness, K_POP_SIZE, K_GEN_SIZE, data)
        QIGA_pop = QIGA_alg.run()
        save_population(es_count, user_count, "QIGA", QIGA_pop)

        print(f'Running MOHEFT')
        MOHEFT_alg = MOHEFT.MOHEFT(fitness, K_POP_SIZE, K_GEN_SIZE, data)
        MOHEFT_pop = MOHEFT_alg.run()
        save_population(es_count, user_count, "MOHEFT", MOHEFT_pop)

        print(f'Running RR')
        RR_alg = RR.RR(fitness, K_POP_SIZE, K_GEN_SIZE, data)
        RR_pop = RR_alg.run()
        save_population(es_count, user_count, "RR", RR_pop)

        print(f'Running RA')
        RA_alg = RA.RA(fitness, K_POP_SIZE, K_GEN_SIZE, data)
        RA_pop = RA_alg.run()
        save_population(es_count, user_count, "RA", RA_pop)

        print(f'Running OE')
        OE_alg = OE.OE(fitness, K_POP_SIZE, K_GEN_SIZE, data)
        OE_pop = OE_alg.run()
        save_population(es_count, user_count, "OE", OE_pop)

        print(f'Running OC')
        OC_alg = OC.OC(fitness, data)
        OC_pop = OC_alg.run()
        save_population(es_count, user_count, "OC", OC_pop)

print("All simulations completed.")
