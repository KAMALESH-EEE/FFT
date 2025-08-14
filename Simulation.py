import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit, SubCircuit
from PySpice.Unit import *
from matplotlib import pyplot as plt

logger = Logging.setup_logging()

libPath = 'C:\\Users\\KAMALESH\\OneDrive\\Documents\\LTspice\\LIBS\\'

lib = 'txb0108.inc'

circuit = Circuit('Buffer')

circuit.include(libPath+lib)


circuit.V('3V3','3V3',circuit.gnd,3.3@u_V)
circuit.V('5V','5V',circuit.gnd,5@u_V)

circuit.PulseVoltageSource('Input','OP_in',circuit.gnd,initial_value = 0@u_V, pulsed_value = 2@u_V, pulse_width = 4@u_ms, period = 8 @u_ms)

circuit.X('U1','TXB0108',)

simulator = circuit.simulator()
analysis = simulator.transient(step_time = 1@u_us, end_time = 500@u_ms)

plt.plot(analysis['out'])
plt.show()
