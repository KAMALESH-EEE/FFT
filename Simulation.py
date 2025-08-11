from PySpice.Spice.Netlist import Circuit, SubCircuitFactory

from PySpice.Unit import *
import numpy as np
from matplotlib import pyplot as plt


class VoltageDivider (SubCircuitFactory):
    __name__ = 'VoltageDivider'
    __node__ = ('IN1','IN2','OUT')

    def __init__(self,R1,R2):
        #super().__init__()

        self.R(1,'IN1','OUT',R1)
        self.R(2,'OUT','IN2',R2)



circuit = Circuit('System')
R1 = 10@u_Ohm
R2 = 10@u_Ohm

circuit.subcircuit(VoltageDivider (R1,R2))

circuit.X('D1','VoltageDivider','Vin',circuit.gnd,'Vout')
circuit.V(1,'Vin',circuit.gnd,10@u_V)

simulator = circuit.simulator()
analysis = simulator.operating_point()

print(analysis['Vout'][0])
