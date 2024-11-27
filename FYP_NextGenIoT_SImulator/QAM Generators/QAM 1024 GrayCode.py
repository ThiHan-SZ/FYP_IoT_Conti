import numpy as np
import matplotlib.pyplot as plt 
import pickle

# QAM-1024 Constellation Map (Gray Coding)
QAM1024 = {}
RQAM1024 = {}
NQAM1024 = {}

I_values = [i for i in range(-31, 32, 2)]
Q_values = I_values[::-1]  # Reverse for symmetry

# Function to generate Gray code from a given integer n
def gray_code(n):
    return n ^ (n >> 1)

# Generate Gray-coded QAM-1024 symbols
for i in range(32):  # I component (In-Phase)
    for j in range(32):  # Q component (Quadrature)
        gray_i = gray_code(i)
        gray_j = gray_code(j)

        symbol = f'{gray_i:05b}' + f'{gray_j:05b}'  # 8-bit Gray code symbol
        QAM1024[symbol] = {'I': I_values[i], 'Q': Q_values[j]}

        RQAM1024[(I_values[i], Q_values[j])] = symbol

        NQAM1024[symbol] = {'I': I_values[i]/(2/3*(1024-1))**0.5, 'Q': Q_values[j]/(2/3*(1024-1))**0.5}

with open('NQAM1024.pkl', 'wb') as f:
    pickle.dump(NQAM1024, f)
        
with open('RQAM1024.pkl', 'wb') as f:
    pickle.dump(RQAM1024, f)

with open('QAM1024.pkl', 'wb') as f:
    pickle.dump(QAM1024, f)

with open('NQAM1024.pkl', 'rb') as f:
    QAM1024_r = pickle.load(f)

for i in QAM1024_r.items():
    print(i)

# Prepare data for plotting
I_points = [entry['I'] for entry in QAM1024_r.values()]
Q_points = [entry['Q'] for entry in QAM1024_r.values()]

# Plotting the QAM-1024 Constellation with Annotations
plt.figure(figsize=(16, 16))
plt.scatter(I_points, Q_points, marker='o', color='blue')

# Adding annotations for each point
for symbol, coords in QAM1024_r.items():
    plt.annotate(symbol, (coords['I'], coords['Q']), textcoords="offset points",
                 xytext=(0, 5), ha='center', fontsize=4)

# Adding labels, title, and grid
plt.title('QAM-1024 Constellation Diagram (Gray Coding)')
plt.xlabel('In-Phase (I)')
plt.ylabel('Quadrature (Q)')
plt.grid(True)

# Display the plot
plt.show()