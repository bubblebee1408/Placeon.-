import cirq
import numpy as np
from typing import List, Dict

class QuantumBridge:
    """
    Bridge between classical interview states and Cirq quantum circuits.
    Maps skill scores to qubit rotations and measurements to classical scores.
    """
    
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.qubits = [cirq.LineQubit(i) for i in range(num_qubits)]
        self.simulator = cirq.Simulator()

    def classical_to_rotation(self, score: float) -> cirq.Gate:
        """Maps 0-1 score to Ry rotation angle theta = score * pi."""
        theta = float(score) * np.pi
        return cirq.ry(theta)

    def encode_belief(self, skill_vector: Dict[str, float], skill_map: List[str]) -> cirq.Circuit:
        """
        Creates a circuit that encodes the current skill belief into Qubits.
        """
        circuit = cirq.Circuit()
        for i, skill in enumerate(skill_map):
            if i >= self.num_qubits:
                break
            score = skill_vector.get(skill, 0.5)
            gate = self.classical_to_rotation(score)
            circuit.append(gate.on(self.qubits[i]))
        return circuit

    def measure_state(self, circuit: cirq.Circuit, repetitions: int = 100) -> List[float]:
        """
        Simulates the circuit and returns the '1' probability for each qubit.
        This effectively 'collapses' the quantum state back to classical scores.
        """
        # Add measurements to all qubits
        full_circuit = circuit.copy()
        full_circuit.append(cirq.measure(*self.qubits, key='result'))
        
        results = self.simulator.run(full_circuit, repetitions=repetitions)
        # Parse multi-qubit measurement results
        # measurements['result'] is a list of results, each result is a bitstring
        all_bits = results.measurements['result'] # [repetitions, num_qubits]
        
        probs = np.mean(all_bits, axis=0)
        return probs.tolist()

    def get_circuit_diagram(self, circuit: cirq.Circuit) -> str:
        return str(circuit)
