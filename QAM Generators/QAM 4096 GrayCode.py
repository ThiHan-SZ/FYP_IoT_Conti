import numpy as np
import matplotlib.pyplot as plt 
import pickle

# QAM-4096 Constellation Map (Gray Coding)
QAM4096 = {}
RQAM4096 = {}

I_values = [i for i in range(-63, 64, 2)]
Q_values = I_values[::-1]  # Reverse for symmetry

# Function to generate Gray code from a given integer n
def gray_code(n):
    return n ^ (n >> 1)

# Generate Gray-coded QAM-4096 symbols
for i in range(64):  # I component (In-Phase)
    for j in range(64):  # Q component (Quadrature)
        gray_i = gray_code(i)
        gray_j = gray_code(j)

        symbol = f'{gray_i:06b}' + f'{gray_j:06b}'  # 8-bit Gray code symbol
        QAM4096[symbol] = {'I': I_values[i], 'Q': Q_values[j]}

        RQAM4096[(I_values[i], Q_values[j])] = symbol
        
with open('RQAM4096.pkl', 'wb') as f:
    pickle.dump(RQAM4096, f)

with open('QAM4096.pkl', 'wb') as f:
    pickle.dump(QAM4096, f)

with open('QAM4096.pkl', 'rb') as f:
    QAM4096_r = pickle.load(f)

for i in QAM4096_r.items():
    print(i)

# Prepare data for plotting
I_points = [entry['I'] for entry in QAM4096_r.values()]
Q_points = [entry['Q'] for entry in QAM4096_r.values()]

# Plotting the QAM-4096 Constellation with Annotations
plt.figure(figsize=(16, 16))
plt.scatter(I_points, Q_points, marker='o', color='blue')

# Adding annotations for each point
for symbol, coords in QAM4096_r.items():
    plt.annotate(symbol, (coords['I'], coords['Q']), textcoords="offset points",
                 xytext=(0, 5), ha='center', fontsize=4)

# Adding labels, title, and grid
plt.title('QAM-4096 Constellation Diagram (Gray Coding)')
plt.xlabel('In-Phase (I)')
plt.ylabel('Quadrature (Q)')
plt.grid(True)

# Display the plot
plt.show()