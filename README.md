# QIGA: Quantum-Inspired Genetic Algorithm for Dynamic Scheduling in Mobile Edge Computing

## Abstract

This paper introduces a Quantum-Inspired Genetic Algorithm (QIGA) for efficient scheduling in a Mobile Edge Computing (MEC) environment. Inspired by the principles of quantum computing, QIGA enhances solution diversity and convergence in the MEC landscape characterized by heterogeneous resources and dynamic tasks. The QIGA framework tackles an optimization problem with multiple conflicting objectives, including makespan, energy consumption, and resource utilization. Extensive evaluations demonstrate that our proposed method outperforms three state-of-the-art scheduling approaches. On average, it reduces energy consumption by about 15.7%, makespan by up to 39%, resource utilization by 20.5%, and latency by 27.5%, with latency improvements reaching up to 69.9% in varied burst MEC scenarios.

This paper was accepted at the 2025 29th International Computer Conference, Computer Society of Iran (CSICC).

---

## Overview

**QIGA** is a novel approach that combines quantum computing principles with evolutionary algorithms to address dynamic scheduling challenges in Mobile Edge Computing. The algorithm generates a diverse set of candidate solutions by employing quantum-inspired operators, thereby improving convergence speed and solution quality in complex scheduling environments.

---

## Key Features

- **Quantum-Inspired Operators:** Utilizes quantum principles to enhance genetic diversity during the search process.
- **Multi-Objective Optimization:** Simultaneously minimizes makespan, energy consumption, and latency while maximizing resource utilization.
- **Dynamic Scheduling:** Adapts to fluctuating resource availability and task dynamics in MEC environments.
- **Extensive Evaluations:** Outperforms state-of-the-art scheduling methods in various burst MEC scenarios, demonstrating significant improvements across multiple performance metrics.


### Experimentation

- **Parameter Tuning:** Modify the parameters in the configuration file to experiment with different genetic operators and quantum-inspired settings.
- **Evaluation Metrics:** The system outputs logs and plots for makespan, energy consumption, resource utilization, and latency.
- **Visualization:** Use the provided Jupyter notebooks in the `notebooks/` folder for detailed performance analysis and visualization.

---

## Evaluation

Our experiments were conducted under varied burst MEC scenarios. The results demonstrated:
- **Energy Consumption:** Reduced by an average of 15.7% and up to 39%.
- **Makespan:** Decreased by up to 20.5%.
- **Resource Utilization:** Improved by 27.5%.
- **Latency:** Achieved reductions of up to 69.9%.

---

## Citation

If you find QIGA useful for your research, please cite our paper as follows:
```bibtex
@INPROCEEDINGS{10967435,
  author={Galavani, Sadra and Younesi, Abolfazl and Ansari, Mohsen},
  booktitle={2025 29th International Computer Conference, Computer Society of Iran (CSICC)}, 
  title={QIGA: Quantum-Inspired Genetic Algorithm for Dynamic Scheduling in Mobile Edge Computing}, 
  year={2025},
  volume={},
  number={},
  pages={1-5},
  keywords={Energy consumption;Quantum computing;Multi-access edge computing;Processor scheduling;Dynamic scheduling;Resource management;Optimization;Tuning;Genetic algorithms;Convergence;Quantum Computing;Scheduling;Mobile Edge Computing;Multi Objective Optimization},
  doi={10.1109/CSICC65765.2025.10967435}}

```

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements or bug fixes. For major changes, please open an issue first to discuss what you would like to change.

---
