import numpy as np
import matplotlib.pyplot as plt 
import pickle

# QAM-256 Constellation Map (Gray Coding)
QAM256 = {}
RQAM256 = {}
NQAM256 = {}

I_values = [i for i in range(-15, 16, 2)]
Q_values = I_values[::-1]  # Reverse for symmetry

# Function to generate Gray code from a given integer n
def gray_code(n):
    return n ^ (n >> 1)

# Generate Gray-coded QAM-256 symbols
for i in range(16):  # I component (In-Phase)
    for j in range(16):  # Q component (Quadrature)
        gray_i = gray_code(i)
        gray_j = gray_code(j)

        symbol = f'{gray_i:04b}' + f'{gray_j:04b}'  # 8-bit Gray code symbol
        QAM256[symbol] = {'I': I_values[i], 'Q': Q_values[j]}

        RQAM256[(I_values[i], Q_values[j])] = symbol

        NQAM256[symbol] = {'I': I_values[i]/(2/3*(256-1))**0.5, 'Q': Q_values[j]/(2/3*(256-1))**0.5}

with open('NQAM256.pkl', 'wb') as f:
    pickle.dump(NQAM256, f)

with open('RQAM256.pkl', 'wb') as f:
    pickle.dump(RQAM256, f)

with open('QAM256.pkl', 'wb') as f:
    pickle.dump(QAM256, f)

with open('NQAM256.pkl', 'rb') as f:
    QAM256_r = pickle.load(f)

for i in QAM256_r.items():
    print(i)

# Prepare data for plotting
I_points = [entry['I'] for entry in QAM256_r.values()]
Q_points = [entry['Q'] for entry in QAM256_r.values()]

# Plotting the QAM-256 Constellation with Annotations
plt.figure(figsize=(12, 12))
plt.scatter(I_points, Q_points, marker='o', color='blue')

# Adding annotations for each point
for symbol, coords in QAM256_r.items():
    plt.annotate(symbol, (coords['I'], coords['Q']), textcoords="offset points",
                 xytext=(0, 5), ha='center', fontsize=8)

# Adding labels, title, and grid
plt.title('QAM-256 Constellation Diagram (Gray Coding)')
plt.xlabel('In-Phase (I)')
plt.ylabel('Quadrature (Q)')
plt.grid(True)

# Display the plot
plt.show()