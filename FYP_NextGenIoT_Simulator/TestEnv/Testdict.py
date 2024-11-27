import pickle

with open(rf'QAM_LUT_pkl\RQAM4096.pkl', 'rb') as f:
    QAM_const = pickle.load(f)

print(QAM_const)
