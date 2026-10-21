Radio waveform simulation for normal text input
=================================================

Put Data.txt, QPSK.py and OFDM.py in the same folder.
Data.txt can contain ordinary text, including spaces, punctuation, and newlines.
The scripts preserve the original file bytes and write the recovered bytes to Out.txt.

Install permitted third-party libraries:
    python -m pip install numpy matplotlib

Run:
    python QPSK.py
    python OFDM.py

Outputs:
    Out.txt (recovered original text; overwritten by each run)
    QPSK_samples.txt / OFDM_samples.txt (sample index, I, Q, magnitude)
    QPSK_waveform.png / OFDM_waveform.png

Both scripts expose SNR_DB and MULTIPATH_DELAY settings near the top of the file
and simulate white Gaussian noise plus multipath. QPSK.py uses blocks of 64 QPSK
symbols with a 16-symbol cyclic prefix; OFDM.py uses its existing 64-sample FFT
and 16-sample cyclic prefix. The delay must not exceed the CP length for the
equalizer to remove inter-block interference. OFDM.py also compares the
multipath result with and without a cyclic prefix. Only Python standard library,
NumPy, and Matplotlib are used. Samples are complex baseband I/Q, not physical
RF voltages.
