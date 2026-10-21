"""
OFDM-QPSK modulation/demodulation for arbitrary text input.
Allowed dependencies: Python standard library, NumPy, Matplotlib.

Input:  Data.txt (UTF-8 text)
Output: Out.txt (recovered UTF-8 text)
        OFDM_samples.txt (complex baseband I/Q DAC-like samples)
        OFDM_waveform.png (plots and cyclic-prefix illustration)

Parameters:
    Fs = 1 MHz, NFFT = 64, 40 active subcarriers, CP = 16 samples.
    Subcarrier spacing = 15.625 kHz; active-carrier span ~625 kHz.
    Each OFDM symbol carries 80 raw bits in 80 us => 1 Mbps, before
    preamble/pilot/framing overhead.

The main loopback uses a configurable multipath channel, AWGN, and one-tap
frequency-domain equalization. A separate experiment compares CP present and
absent. This is an educational baseband simulation, not a 100 km RF link.
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "Data.txt"
OUTPUT_FILE = BASE_DIR / "Out.txt"
SAMPLES_FILE = BASE_DIR / "OFDM_samples.txt"
PLOT_FILE = BASE_DIR / "OFDM_waveform.png"

FS = 1_000_000.0
NFFT = 64*8
CP_LEN = 16 * 8
SNR_DB = 50.0
MULTIPATH_DELAY = 16
ACTIVE = np.r_[np.arange(1, 21), np.arange(NFFT - 20, NFFT)]
BITS_PER_SYMBOL = 2
BITS_PER_OFDM_SYMBOL = len(ACTIVE) * BITS_PER_SYMBOL
RAW_BIT_RATE = BITS_PER_OFDM_SYMBOL * FS / (NFFT + CP_LEN)


TX_SYMBOL = None



def read_bytes(path):
    if not path.exists():
        raise FileNotFoundError(f"Cannot find {path}. Put Data.txt beside this script.")
    return path.read_bytes()


def bytes_to_bits(data):
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8)) if data else np.array([], dtype=np.uint8)


def bits_to_bytes(bits, byte_count):
    needed = byte_count * 8
    if len(bits) < needed:
        raise ValueError("Not enough recovered bits to reconstruct the original file.")
    return np.packbits(bits[:needed]).tobytes()


def qpsk_map(bits):
    padded = np.pad(bits, (0, (-len(bits)) % 2), constant_values=0)
    pairs = padded.reshape(-1, 2)
    return ((1.0 - 2.0 * pairs[:, 0]) + 1j * (1.0 - 2.0 * pairs[:, 1])) / np.sqrt(2.0)


def qpsk_demap(symbols):
    pairs = np.column_stack((symbols.real < 0, symbols.imag < 0)).astype(np.uint8)
    return pairs.reshape(-1)


def make_ofdm_symbols(bits):
    # Pad only for the final OFDM frame; the original byte length controls output recovery.
    pad_bits = (-len(bits)) % BITS_PER_OFDM_SYMBOL
    padded = np.pad(bits, (0, pad_bits), constant_values=0)
    groups = padded.reshape(-1, BITS_PER_OFDM_SYMBOL)
    qpsk = qpsk_map(groups.reshape(-1)).reshape(-1, len(ACTIVE))
    freq = np.zeros((len(groups), NFFT), dtype=complex)
    freq[:, ACTIVE] = qpsk
    time = np.fft.ifft(freq, axis=1) * np.sqrt(NFFT)
    return time, freq


def add_cp(time_blocks):
    return np.concatenate((time_blocks[:, -CP_LEN:], time_blocks), axis=1)


def make_channel(delay):
    if not 0 <= delay <= CP_LEN:
        raise ValueError(f"MULTIPATH_DELAY must be between 0 and CP_LEN ({CP_LEN}).")
    channel = np.zeros(delay + 1, dtype=complex)
    channel[0] = 1.0
    if delay:
        channel[delay] = 0.90 * np.exp(1j * 0.7)
    return channel / np.sqrt(np.sum(np.abs(channel) ** 2))


def add_awgn(signal, snr_db):
    signal_power = np.mean(np.abs(signal) ** 2)
    noise_power = signal_power / (10.0 ** (snr_db / 10.0))
    noise = np.sqrt(noise_power / 2.0) * (
        np.random.normal(size=signal.shape) + 1j * np.random.normal(size=signal.shape)
    )
    return signal + noise


def demodulate(rx_blocks, bit_count, channel_freq):
    useful = rx_blocks[:, CP_LEN:CP_LEN + NFFT]
    freq = np.fft.fft(useful, axis=1) / np.sqrt(NFFT)
    equalized = freq / channel_freq[np.newaxis, :]
    detected_bits = qpsk_demap(equalized[:, ACTIVE].reshape(-1))
    return detected_bits[:bit_count]


def multipath_cp_demo(freq_blocks, channel):
    time_blocks = np.fft.ifft(freq_blocks, axis=1) * np.sqrt(NFFT)
    memory = len(channel) - 1
    h_freq = np.fft.fft(np.pad(channel, (0, NFFT - len(channel))))

    # With CP: channel memory is within the prefix length.
    cp_blocks = add_cp(time_blocks)
    cp_stream = cp_blocks.reshape(-1)
    rx_cp_stream = np.convolve(cp_stream, channel, mode="full")[:len(cp_stream)]
    rx_cp_blocks = rx_cp_stream.reshape(-1, NFFT + CP_LEN)
    useful_cp = rx_cp_blocks[:, CP_LEN:CP_LEN + NFFT]
    y_cp = np.fft.fft(useful_cp, axis=1) / np.sqrt(NFFT)
    y_cp_eq = y_cp / h_freq[np.newaxis, :]
    bits_cp = qpsk_demap(y_cp_eq[:, ACTIVE].reshape(-1))

    # Without CP: the previous OFDM block's tail overlaps the next block.
    no_cp_stream = time_blocks.reshape(-1)
    rx_no_cp_stream = np.convolve(no_cp_stream, channel, mode="full")[:len(no_cp_stream)]
    rx_no_cp_blocks = rx_no_cp_stream.reshape(-1, NFFT)
    y_no_cp = np.fft.fft(rx_no_cp_blocks, axis=1) / np.sqrt(NFFT)
    y_no_cp_eq = y_no_cp / h_freq[np.newaxis, :]
    bits_no_cp = qpsk_demap(y_no_cp_eq[:, ACTIVE].reshape(-1))

    reference = qpsk_demap(freq_blocks[:, ACTIVE].reshape(-1))
    n = min(len(reference), len(bits_cp), len(bits_no_cp))
    cp_errors = int(np.count_nonzero(reference[:n] != bits_cp[:n]))
    no_cp_errors = int(np.count_nonzero(reference[:n] != bits_no_cp[:n]))
    return memory, cp_errors, no_cp_errors, n


def main():
    original_bytes = read_bytes(INPUT_FILE)
    bits = bytes_to_bits(original_bytes)
    if len(bits) == 0:
        OUTPUT_FILE.write_bytes(b"")
        print("Data.txt is empty; wrote empty Out.txt.")
        return

    time_blocks, freq_blocks = make_ofdm_symbols(bits)
    
    tx_blocks = add_cp(time_blocks)
    tx = tx_blocks.reshape(-1)

    channel = make_channel(MULTIPATH_DELAY)
    channel_freq = np.fft.fft(np.pad(channel, (0, NFFT - len(channel))))
    tx_stream = tx_blocks.reshape(-1)
    TX_SYMBOL = tx_stream[:]
    rx_stream = np.convolve(tx_stream, channel, mode="full")[:len(tx_stream)]
    rx_stream = add_awgn(rx_stream, SNR_DB)
    rx_blocks = rx_stream.reshape(-1, NFFT + CP_LEN)
    recovered_bits = demodulate(rx_blocks, len(bits), channel_freq)
    recovered_symbols = (
        np.fft.fft(rx_blocks[:, CP_LEN:CP_LEN + NFFT], axis=1) / np.sqrt(NFFT)
    ) / channel_freq[np.newaxis, :]
    recovered_bytes = bits_to_bytes(recovered_bits, len(original_bytes))
    OUTPUT_FILE.write_bytes(recovered_bytes)

    indices = np.arange(len(tx))
    np.savetxt(SAMPLES_FILE,
               np.column_stack((indices, tx.real, tx.imag, np.abs(tx))),
               header="sample_index I_sample Q_sample magnitude",
               fmt=["%d", "%.10g", "%.10g", "%.10g"])

    errors = int(np.count_nonzero(bits != recovered_bits))
    print(f"Input bytes: {len(original_bytes)}")
    print(f"Input bits: {len(bits)}")
    print(f"FFT size: {NFFT}; active subcarriers: {len(ACTIVE)}; DC unused")
    print(f"Sample rate: {FS/1e6:.3f} MS/s")
    print(f"Subcarrier spacing: {FS/NFFT/1e3:.3f} kHz")
    print(f"Approx. active-carrier span: {len(ACTIVE)*FS/NFFT/1e3:.3f} kHz")
    print(f"CP: {CP_LEN} samples = {CP_LEN/FS*1e6:.1f} us")
    print(f"SNR: {SNR_DB:.1f} dB; multipath delay: {MULTIPATH_DELAY} samples")
    print(f"Raw PHY rate including CP time: {RAW_BIT_RATE/1e6:.3f} Mbps")
    print(f"Bit errors (multipath + AWGN loopback): {errors}")
    print(f"Recovered text saved to: {OUTPUT_FILE.resolve()}")
    print(f"Baseband samples saved to: {SAMPLES_FILE.resolve()}")

    memory, cp_errors, no_cp_errors, n = multipath_cp_demo(freq_blocks, channel)
    print("\nSeparate multipath CP demonstration (not used for Out.txt):")
    print(f"Channel memory: {memory} samples; CP length: {CP_LEN} samples")
    print(f"BER with CP + one-tap equalization: {cp_errors}/{n}")
    print(f"BER without CP + one-tap equalization: {no_cp_errors}/{n}")

    fig, axes = plt.subplots(4, 1, figsize=(11, 11))
    n_show = min(3 * (NFFT + CP_LEN), len(tx))
    axes[0].plot(indices[:n_show], tx.real[:n_show], label="I")
    axes[0].plot(indices[:n_show], tx.imag[:n_show], label="Q", alpha=0.8)
    axes[0].set_title("OFDM-QPSK complex baseband DAC-like samples (CP included)")
    axes[0].set_xlabel("Sample index")
    axes[0].set_ylabel("Amplitude")
    axes[0].grid(True)
    axes[0].legend()

    one = tx_blocks[0]
    axes[1].plot(np.arange(len(one)), one.real, marker=".", label="I samples")
    axes[1].axvspan(0, CP_LEN - 1, alpha=0.2, label="Cyclic prefix")
    axes[1].axvline(CP_LEN, linestyle="--", label="Useful FFT window starts")
    axes[1].set_title("CP = copied final samples of the useful OFDM symbol")
    axes[1].set_xlabel("Sample within OFDM symbol")
    axes[1].set_ylabel("I amplitude")
    axes[1].grid(True)
    axes[1].legend()

    axes[2].plot(recovered_symbols[:, ACTIVE].real,
                 recovered_symbols[:, ACTIVE].imag, ".", markersize=5)
    axes[2].set_title(f"Equalized received QPSK constellation ({SNR_DB:.1f} dB SNR)")
    axes[2].set_xlabel("In-phase")
    axes[2].set_ylabel("Quadrature")
    axes[2].axis("equal")
    axes[2].grid(True)

    axes[3].bar(["With CP", "Without CP"],
                [cp_errors / max(1, n), no_cp_errors / max(1, n)])
    axes[3].set_title("Multipath demo: BER after one-tap equalization")
    axes[3].set_ylabel("BER")
    axes[3].grid(True, axis="y")
    fig.tight_layout()
    fig.savefig(PLOT_FILE, dpi=150)
    print(f"Plot saved to: {PLOT_FILE.resolve()}")
    plt.show()

    TX_SYMBOL = TX_SYMBOL [CP_LEN:NFFT+CP_LEN]

    FREQ        =   np.fft.fftfreq(len(TX_SYMBOL),1/FS) / 1e6

    plt.plot(FREQ,abs(np.fft.fft(TX_SYMBOL)))
    plt.grid()
    plt.show()



if __name__ == "__main__":
    main()
