import numpy as np
SNR_up = int(input("Enter the SNR upper limit in dB: "))
SNR_down = int(input("Enter the SNR lower limit in dB: "))
Sample = 5
assert SNR_up > SNR_down, "SNR upper limit must be greater than SNR lower limit"
SNR_test_range = np.linspace(SNR_down, SNR_up, Sample*(SNR_up-SNR_down) + 1, endpoint=True)
print(SNR_test_range, len(SNR_test_range), sep='\n')