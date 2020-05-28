# -*- coding: utf-8 -*-

from record import RATE, CHUNK

import numpy as np
from scipy.signal import decimate
from peakutils import peak

# Downsampling factor for decimating the chunk
DEC_FACTOR = 6

# Default oversampling of fft based on window length
FFT_SCALE = 4

# Number of harmonics to take count on while executing HPS algorithm
NUM_HARMONICS = 4

# Minimum frequency admitted
THRESHOLD_FREQ = 60

# Normalized threshold for a peak to exceed in order to be taken count on
THRES_AMPL = 0.15

# Minimum distance between two peaks in order to be taken separately
MIN_DIST = 10


def obtainFFT(chunk, size, fraction = 4):
    "Returns the FFT given an array of samples and the window size"
    
    # Getting FFT [a: array of samples, n: window size]
    fft = np.fft.fft(a = chunk, n = size)
    # Extracting just the first samples
    fft = fft[0 : len(fft) / fraction] 
    # Obtaining the value of each FFT sample
    fft = np.absolute(fft)
    
    return fft


def isValid(pitch):
    "Returns True if the given pitch is not bullshit"
    return pitch >= THRESHOLD_FREQ if pitch is not None else False


def HPS(fft, fft_size):
	"Returns the fundamental frecuency given the fft of the chunk"

	# Create array of arrays, each of them with the fft decimated in a factor
	downsamples = [fft] + [fft[0:-1:fac] for fac in range(2, NUM_HARMONICS + 2)]
	# Group amplitudes of same frequencies (index) and multiply them together
	product = [reduce(lambda x, y: x*y, freq) for freq in zip(*downsamples)]
	# Get the max indexes among the products
        indexes = peak.indexes(np.array(product), THRES_AMPL, MIN_DIST)

        # Discard chunks with noise and multiple frequency components
        if len(indexes) != 1: return None
        # If the max is not in the found peak it's not valid
        elif product.index(max(product)) != indexes[0]: return None

	# Multiply index by the fft precision (1/fft_size)...
	# ... and by the frequency used (fs / dec_factor)
	# The result is the equivalent frequency in Hz and must be returned
        return indexes[0] * RATE / float(DEC_FACTOR * fft_size)


def obtainPitch(chunk, fftScale = FFT_SCALE, fftFraction = 4):
	"Returns the fundamental frecuency given the chunk of samples"
	fft_size = int(len(chunk) * fftScale)

	# Re-sample with an equivalent frequency of RATE/DEC_FACTOR, after filtering
	decimated = decimate(chunk, DEC_FACTOR)

	fft = obtainFFT(decimated, fft_size, fftFraction)

        pitch = HPS(fft, fft_size)

	return pitch if isValid(pitch) else None
