import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit, SubCircuit
from PySpice.Unit import *

logger = Logging.setup_logging()

class VoltageDivider(SubCircuit):
    __name__ = 'divider'
    __nodes__ = ('input', 'output', 'gnd')

    def __init__(self, R1_value, R2_value):
        SubCircuit.__init__(self,self.__name__,*self.__nodes__)
        self.R(1, 'input', 'output', R1_value)
        self.R(2, 'output', 'gnd', R2_value)

# Main circuit
circuit = Circuit('Main Circuit')

# Add subcircuits
circuit.subcircuit(VoltageDivider(1@u_kΩ, 1@u_kΩ))
circuit.subcircuit(VoltageDivider(10@u_kΩ, 1@u_kΩ))

# Voltage source
circuit.V(1, 'vin1', circuit.gnd, 5@u_V)
circuit.V(2, 'vin2', circuit.gnd, 5@u_V)

# Instantiate subcircuits
circuit.X('1', 'divider', 'vin1', 'out1', circuit.gnd)
circuit.X('2', 'divider', 'vin2', 'out2', circuit.gnd)

# Run transient analysis
simulator = circuit.simulator()
analysis = simulator.transient(step_time=1@u_ms, end_time=2@u_s)

print(float(analysis['out1'][-1]))
print(float(analysis['out2'][-1]))
