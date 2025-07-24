import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import get_window

N = 82
X1 = list(np.array([i for i in range(40)])/42)
X2 = list(np.array([i for i in range(39,-1,-1)])/42)
Y1 = list(np.array([i for i in range(40)])*-1/42)
Y2 = list(np.array([i for i in range(39,-1,-1)])*-1/42)
preamble = [0,0]+ X1+X2 + Y1 + Y2 + [0,0]

print(len(preamble))

plt.plot(preamble)
plt.show()