import math
import matplotlib.pyplot as plt 
import pickle

# QAM-16 Constellation Map (Gray Coding)
QAM16 = {}
RQAM16 = {}
NQAM16 = {}

I_values = [i for i in range(-3, 4, 2)]
Q_values = I_values[::-1]  # Reverse for symmetry

# Function to generate Gray code from a given integer n
def gray_code(n):
    return n ^ (n >> 1)

# Generate Gray-coded QAM-16 symbols
for i in range(4):  # I component (In-Phase)
    for j in range(4):  # Q component (Quadrature)
        gray_i = gray_code(i)
        gray_j = gray_code(j)

        symbol = f'{gray_i:02b}' + f'{gray_j:02b}'  # 8-bit Gray code symbol
        QAM16[symbol] = {'I': I_values[i], 'Q': Q_values[j]}

        RQAM16[(I_values[i], Q_values[j])] = symbol

        NQAM16[symbol] = {'I': I_values[i]/(2/3*(16-1))**0.5, 'Q': Q_values[j]/(2/3*(16-1))**0.5}

with open('NQAM16.pkl', 'wb') as f:
    pickle.dump(NQAM16, f)

with open('RQAM16.pkl', 'wb') as f:
    pickle.dump(RQAM16, f)

with open('QAM16.pkl', 'wb') as f:
    pickle.dump(QAM16, f)

with open('NQAM16.pkl', 'rb') as f:
    QAM16_r = pickle.load(f)

for i in QAM16_r.items():
    print(i)

# Prepare data for plotting
I_points = [entry['I'] for entry in QAM16_r.values()]
Q_points = [entry['Q'] for entry in QAM16_r.values()]

# Plotting the QAM-16 Constellation with Annotations
plt.figure(figsize=(12, 12))
plt.scatter(I_points, Q_points, marker='o', color='blue')

# Adding annotations for each point
for symbol, coords in QAM16_r.items():
    plt.annotate(symbol, (coords['I'], coords['Q']), textcoords="offset points",
                 xytext=(0, 5), ha='center', fontsize=8)

# Adding labels, title, and grid
plt.title('QAM-16 Constellation Diagram (Gray Coding)')
plt.xlabel('In-Phase (I)')
plt.ylabel('Quadrature (Q)')
plt.grid(True)

# Display the plot
plt.show()