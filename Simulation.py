from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy as np
from matplotlib import pyplot as plt


circuit = Circuit('System')
circuit.V(1, 'Vin', circuit.gnd, 10@u_V)
circuit.R(1, 'Vin', 'M1', 5@u_Ohm)
circuit.R(2, 'M1', circuit.gnd, 5@u_Ohm)

simulator = circuit.simulator()
analysis = simulator.operating_point()

print(analysis['M1'][0])
