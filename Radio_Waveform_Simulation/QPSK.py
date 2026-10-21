"""
Single-carrier QPSK modulation/demodulation for arbitrary text input.
Allowed dependencies: Python standard library, NumPy, Matplotlib.

Input:  Data.txt (UTF-8 text)
Output: Out.txt (recovered UTF-8 text)
        QPSK_samples.txt (complex baseband I/Q DAC-like samples)
        QPSK_waveform.png (plots)

Run this script from the folder containing Data.txt.
The symbol-rate link uses cyclic-prefix blocks, a configurable multipath channel,
and AWGN. This is an educational baseband simulation, not a physical RF link.
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

INPUT_FILE = Path(__file__).resolve().parent / "Data.txt"
OUTPUT_FILE = Path(__file__).resolve().parent / "Out.txt"
SAMPLES_FILE = Path(__file__).resolve().parent / "QPSK_samples.txt"
PLOT_FILE = Path(__file__).resolve().parent / "QPSK_waveform.png"

FS = 1_000_000.0
BIT_RATE = 1_000_000.0
SPS = 3
ROLLOFF = 0.25
RRC_SPAN_SYMBOLS = 10
BLOCK_SYMBOLS = 64
CP_LEN = 16
SNR_DB = 24.0
MULTIPATH_DELAY = 3


def read_text_bytes(path):
    if not path.exists():
        raise FileNotFoundError(f"Cannot find {path}. Put Data.txt beside this script.")
    # Preserve the exact original bytes, including line endings and final newline.
    return path.read_bytes()


def bytes_to_bits(data):
    if not data:
        return np.array([], dtype=np.uint8)
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8))


def bits_to_bytes(bits, byte_count):
    needed = byte_count * 8
    if len(bits) < needed:
        raise ValueError("Not enough recovered bits to reconstruct the original file.")
    return np.packbits(bits[:needed]).tobytes()


def rrc_filter(beta, sps, span_symbols):
    n = np.arange(-span_symbols * sps // 2, span_symbols * sps // 2 + 1, dtype=float)
    t = n / sps
    h = np.zeros_like(t)
    for i, ti in enumerate(t):
        if abs(ti) < 1e-12:
            h[i] = 1.0 + beta * (4.0 / np.pi - 1.0)
        elif beta > 0 and abs(abs(4.0 * beta * ti) - 1.0) < 1e-10:
            h[i] = (beta / np.sqrt(2.0)) * (
                (1.0 + 2.0 / np.pi) * np.sin(np.pi / (4.0 * beta))
                + (1.0 - 2.0 / np.pi) * np.cos(np.pi / (4.0 * beta))
            )
        else:
            numerator = (np.sin(np.pi * ti * (1.0 - beta))
                         + 4.0 * beta * ti * np.cos(np.pi * ti * (1.0 + beta)))
            denominator = np.pi * ti * (1.0 - (4.0 * beta * ti) ** 2)
            h[i] = numerator / denominator
    h /= np.sqrt(np.sum(h * h))
    return h


def qpsk_map(bits):
    padded = np.pad(bits, (0, len(bits) % 2), constant_values=0) if len(bits) % 2 else bits
    pairs = padded.reshape(-1, 2)
    symbols = ((1.0 - 2.0 * pairs[:, 0]) + 1j * (1.0 - 2.0 * pairs[:, 1])) / np.sqrt(2.0)
    return symbols


def qpsk_demap(symbols):
    pairs = np.column_stack((symbols.real < 0, symbols.imag < 0)).astype(np.uint8)
    return pairs.reshape(-1)


def add_cp(symbol_blocks):
    return np.concatenate((symbol_blocks[:, -CP_LEN:], symbol_blocks), axis=1)


def make_channel(delay):
    if not 0 <= delay <= CP_LEN:
        raise ValueError(f"MULTIPATH_DELAY must be between 0 and CP_LEN ({CP_LEN}).")
    channel = np.zeros(delay + 1, dtype=complex)
    channel[0] = 1.0
    if delay:
        channel[delay] = 0.7 * np.exp(1j * 0.4)
    return channel / np.sqrt(np.sum(np.abs(channel) ** 2))


def add_awgn(signal, snr_db):
    signal_power = np.mean(np.abs(signal) ** 2)
    noise_power = signal_power / (10.0 ** (snr_db / 10.0))
    noise = np.sqrt(noise_power / 2.0) * (
        np.random.normal(size=signal.shape) + 1j * np.random.normal(size=signal.shape)
    )
    return signal + noise


def main():
    original_bytes = read_text_bytes(INPUT_FILE)
    bits = bytes_to_bits(original_bytes)
    if len(bits) == 0:
        OUTPUT_FILE.write_bytes(b"")
        print("Data.txt is empty; wrote empty Out.txt.")
        return

    symbols = qpsk_map(bits)
    frame_count = (len(symbols) + BLOCK_SYMBOLS - 1) // BLOCK_SYMBOLS
    padded_symbols = np.pad(
        symbols, (0, frame_count * BLOCK_SYMBOLS - len(symbols)), constant_values=0
    )
    symbol_blocks = padded_symbols.reshape(-1, BLOCK_SYMBOLS)
    tx_symbol_blocks = add_cp(symbol_blocks)

    channel = make_channel(MULTIPATH_DELAY)
    tx_symbol_stream = tx_symbol_blocks.reshape(-1)
    rx_symbol_stream = np.convolve(tx_symbol_stream, channel, mode="full")[
        :len(tx_symbol_stream)
    ]
    rx_symbol_stream = add_awgn(rx_symbol_stream, SNR_DB)
    rx_symbol_blocks = rx_symbol_stream.reshape(-1, BLOCK_SYMBOLS + CP_LEN)
    useful_blocks = rx_symbol_blocks[:, CP_LEN:]
    channel_freq = np.fft.fft(np.pad(channel, (0, BLOCK_SYMBOLS - len(channel))))
    rx_freq = np.fft.fft(useful_blocks, axis=1)
    equalized_blocks = np.fft.ifft(rx_freq / channel_freq[np.newaxis, :], axis=1)
    rx_symbols = equalized_blocks.reshape(-1)[:len(symbols)]

    h = rrc_filter(ROLLOFF, SPS, RRC_SPAN_SYMBOLS)
    tx_symbols = tx_symbol_stream
    upsampled = np.zeros(len(tx_symbols) * SPS, dtype=complex)
    upsampled[::SPS] = tx_symbols
    tx = np.convolve(upsampled, h, mode="full")

    recovered_bits = qpsk_demap(rx_symbols)[:len(bits)]
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
    print(f"QPSK symbols: {len(symbols)}")
    print(f"Block size / CP: {BLOCK_SYMBOLS} / {CP_LEN} symbols")
    print(f"SNR: {SNR_DB:.1f} dB; multipath delay: {MULTIPATH_DELAY} symbols")
    print(f"Sample rate: {FS/1e6:.3f} MS/s")
    print(f"Symbol rate: {BIT_RATE/2/1e3:.3f} ksymbols/s")
    print(f"Approx. RRC occupied bandwidth: {(1+ROLLOFF)*BIT_RATE/2/1e3:.1f} kHz")
    print(f"Bit errors (multipath + AWGN loopback): {errors}")
    print(f"Recovered text saved to: {OUTPUT_FILE.resolve()}")
    print(f"Baseband samples saved to: {SAMPLES_FILE.resolve()}")

    n_show = min(160, len(tx))
    fig, axes = plt.subplots(3, 1, figsize=(10, 8))
    axes[0].plot(indices[:n_show], tx.real[:n_show], label="I")
    axes[0].plot(indices[:n_show], tx.imag[:n_show], label="Q", alpha=0.8)
    axes[0].set_title("Single-carrier QPSK: complex baseband DAC-like samples")
    axes[0].set_xlabel("Sample index")
    axes[0].set_ylabel("Amplitude")
    axes[0].grid(True)
    axes[0].legend()

    axes[1].plot(rx_symbols.real, rx_symbols.imag, ".", markersize=4)
    axes[1].set_title(f"Equalized QPSK constellation ({SNR_DB:.1f} dB SNR)")
    axes[1].set_xlabel("In-phase")
    axes[1].set_ylabel("Quadrature")
    axes[1].axis("equal")
    axes[1].grid(True)

    show = min(80, len(bits))
    axes[2].step(np.arange(show), bits[:show], where="post", label="Input bits")
    axes[2].step(np.arange(show), recovered_bits[:show] + 0.04, where="post",
                 label="Recovered bits", alpha=0.8)
    axes[2].set_title(f"Input vs received bits (bit errors = {errors})")
    axes[2].set_xlabel("Bit index")
    axes[2].set_ylabel("Bit")
    axes[2].set_yticks([0, 1])
    axes[2].grid(True)
    axes[2].legend()

    fig.tight_layout()
    fig.savefig(PLOT_FILE, dpi=150)
    print(f"Plot saved to: {PLOT_FILE.resolve()}")
    plt.show()


if __name__ == "__main__":
    main()
