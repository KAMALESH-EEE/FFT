import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit, SubCircuit
from PySpice.Unit import *

# Setup logging for PySpice to show any warnings or info
logger = Logging.setup_logging()

# Define a subcircuit class for a voltage divider
class VoltageDivider(SubCircuit):
    # Specify the external nodes (pins) of the subcircuit
    __nodes__ = ('input', 'output')

    # The __init__ method is where you define the components inside the subcircuit
    def __init__(self, name, R1_value, R2_value):
        # Call the parent constructor, providing the name and nodes
        SubCircuit.__init__(self, name, *self.__nodes__)

        # Add the components of the subcircuit using PySpice's syntax
        # The internal nodes are automatically handled by the library
        self.R(1, 'input', 'output', R1_value)
        self.R(2, 'output', self.gnd, R2_value)

# Define the main circuit where you will use your subcircuit
circuit = Circuit('Main Circuit')

# Instantiate the subcircuit multiple times with different parameters
# This is where reusability comes into play
circuit.subcircuit(VoltageDivider('divider_1', 1@u_kΩ, 1@u_kΩ))
circuit.subcircuit(VoltageDivider('divider_2', 10@u_kΩ, 1@u_kΩ))

# Use the subcircuit instances in the main circuit
# The 'X' prefix indicates that you are instantiating a subcircuit
# The first argument is the instance name, the next arguments are the nodes
# connected to its pins, and the last is the name of the subcircuit.
circuit.X('1', 'divider_1', 5@u_V, 'out1')  # Connects the first divider to a 5V source
circuit.X('2', 'divider_2', 5@u_V, 'out2')  # Connects the second divider to the same source

# Print the generated netlist to see the result
# The correct way to get the netlist is to print the circuit object directly.
# The 'clean_netlist' method that caused the error is not a valid attribute.
print(circuit)