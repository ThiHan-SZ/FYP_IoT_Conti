import numpy as np
import matplotlib.pyplot as plt 
import pickle

# QAM-64 Constellation Map (Gray Coding)
QAM64 = {}
RQAM64 = {}
NQAM64 = {}

I_values = [i for i in range(-7, 8, 2)]
Q_values = I_values[::-1]  # Reverse for symmetry

# Function to generate Gray code from a given integer n
def gray_code(n):
    return n ^ (n >> 1)

# Generate Gray-coded QAM-64 symbols
for i in range(8):  # I component (In-Phase)
    for j in range(8):  # Q component (Quadrature)
        gray_i = gray_code(i)
        gray_j = gray_code(j)

        symbol = f'{gray_i:03b}' + f'{gray_j:03b}'  # 8-bit Gray code symbol
        QAM64[symbol] = {'I': I_values[i], 'Q': Q_values[j]}

        RQAM64[(I_values[i], Q_values[j])] = symbol

        NQAM64[symbol] = {'I': I_values[i]/(2/3*(64-1))**0.5, 'Q': Q_values[j]/(2/3*(64-1))**0.5}

with open('NQAM64.pkl', 'wb') as f:
    pickle.dump(NQAM64, f)

with open('RQAM64.pkl', 'wb') as f:
    pickle.dump(RQAM64, f)

with open('QAM64.pkl', 'wb') as f:
    pickle.dump(QAM64, f)

with open('QAM64.pkl', 'rb') as f:
    QAM64_r = pickle.load(f)

for i in QAM64_r.items():
    print(i)

# Prepare data for plotting
I_points = [entry['I'] for entry in QAM64_r.values()]
Q_points = [entry['Q'] for entry in QAM64_r.values()]

# Plotting the QAM-64 Constellation with Annotations
plt.figure(figsize=(12, 12))
plt.scatter(I_points, Q_points, marker='o', color='blue')

# Adding annotations for each point
for symbol, coords in QAM64_r.items():
    plt.annotate(symbol, (coords['I'], coords['Q']), textcoords="offset points",
                 xytext=(0, 5), ha='center', fontsize=8)

# Adding labels, title, and grid
plt.title('QAM-64 Constellation Diagram (Gray Coding)')
plt.xlabel('In-Phase (I)')
plt.ylabel('Quadrature (Q)')
plt.grid(True)

# Display the plot
plt.show()