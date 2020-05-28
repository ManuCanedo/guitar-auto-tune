import pyaudio, wave, sys, numpy

CHUNK = 7200
FORMAT = pyaudio.paInt16
NP_FORMAT = 'Int16'
CHANNELS = 1
RATE = 48000
DEVICE = 2

# Global variables for input stream
STREAM = None
PYAUDIO = pyaudio.PyAudio()


def openStream():
    "Opens stream input"
    # Initialising audio input stream
    global STREAM
 
    STREAM = PYAUDIO.open(format=FORMAT,
                          channels = CHANNELS,
                          rate = RATE,
                          input = True,
                          input_device_index = DEVICE,
                          frames_per_buffer = CHUNK)

def rec(chunkSize = CHUNK):
    "Records sound from input given a stream"
    if STREAM is None: openStream()

    # Gets data from buffer
    data = STREAM.read(chunkSize)
    # Decodes input to amplitude values
    decoded = numpy.fromstring(data, NP_FORMAT)
    return decoded

def closeStream():
    "Stops input stream"
    global STREAM

    try:
        STREAM.stop_stream()
        STREAM.close()
    except:
        print "Error closing stream"
    STREAM = None
