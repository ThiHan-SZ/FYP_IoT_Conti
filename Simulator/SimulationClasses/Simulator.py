from SimulationClasses.Simulator import ModulationClass, DemodulationClass, SimpleGWNChannel_dB

def test_qam4096_alignment(self):
    # Transmit a known bit pattern through the modulator and demodulator at high SNR
    # Check if received bits match the transmitted bits exactly
    test_bits = "Known Test Pattern"  # Define a pattern
    t, modulated_signal = Mod.modulator.plot_full(test_bits)
    noisy_signal = SimpleGWNChannel_dB(1000).add_noise(modulated_signal)  # High SNR
    received_bits = Demod.demodulator.demapping(noisy_signal)
    assert test_bits == received_bits, "QAM4096 decoding misalignment at high SNR"