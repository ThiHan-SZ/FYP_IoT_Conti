import pickle
import matplotlib.pyplot as plt
import numpy as np

with open(r'QAM_LUT_pkl\RQAM16.pkl', 'rb') as f:
    RQAM16 = pickle.load(f)

coords = [k[0]+1j*k[1] for k in RQAM16.keys()]
coords = np.array(coords)



n = np.linspace(1, 4, 8)
for n in np.linspace(1, 4, 8):
    a = coords ** n
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111)
    ax.plot(a.real, a.imag, 'o')
    for i, (xi, yi) in enumerate(zip(a.real, a.imag), start=1):
        ax.annotate(f'{i}', (xi, yi), textcoords="offset points", xytext=(0, 5), ha='center')


plt.show()