import numpy as np
import math
import matplotlib.pyplot as plt


# Gray code function to map a 3-bit binary index to Gray code
def gray_code_3bit(n):
    return n ^ (n >> 1)

QAM64 = {f'{gray_code_3bit(i):06b}': {'I': [0, 1], 'Q': [0, 1]} for i in range(64)}

# I/Q coordinate levels for 64-QAM
levels = [-7, -5, -3, -1, 1, 3, 5, 7]


# Generate the lookup table with Gray-coded I/Q values and polarities
for i in range(64):
    binary_str = f'{i:06b}'  # 6-bit binary representation

    # Split the 6-bit symbol into 3 bits for I and 3 bits for Q
    row_bits = int(binary_str[:3], 2)  # First 3 bits -> I
    col_bits = int(binary_str[3:], 2)  # Last 3 bits -> Q

    # Convert to Gray code for proper ordering
    row = gray_code_3bit(row_bits)
    col = gray_code_3bit(col_bits)

    # Assign levels based on the Gray code row and column
    I_level = levels[row]
    Q_level = levels[col]

    # Assign I/Q values with appropriate polarity
    QAM64[binary_str]['I'] = [I_level, 1 if I_level >= 0 else -1]
    QAM64[binary_str]['Q'] = [Q_level, 1 if Q_level >= 0 else -1]

Q = np.array([i[1]['Q'][0] for i in QAM64.items()])
I = np.array([i[1]['I'][0] for i in QAM64.items()])
fig = plt.figure()
ax = fig.add_subplot(111)
plt.scatter(I, Q)

for i, txt in enumerate(QAM64):
    ax.annotate(txt, (I[i], Q[i]))

plt.grid()
plt.show()