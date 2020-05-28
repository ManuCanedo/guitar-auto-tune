#!/usr/bin/python
# -*- coding: utf-8 -*-

import Queue, time
from threading import Thread

from sound import *
from motor import *

# Shared synchronized queue between input and output threads
QUEUE = None

# Stop condition so that other thread can stop the tuner properly
STOP = False


def processOutput(freqExp = None):
	""" Output processing thread
	Repeatedly wait for recorded data, check if the SNR is good enough and if
	so, move motor appropriately (otherwise stop motor) based on the pitch
	"""
        myChunk = chunk.Chunk()

	while True:
                # Check if the STOP variable has been changed
                if STOP: break
                # Get data from the shared queue and compute pitch
		myChunk.data = QUEUE.get()
                start, pitch = time.time(), myChunk.getPitch()
                QUEUE.task_done()

                # If the chunk was valid, move the motor according to the obtained pitch
                if pitch is not None:
                        print "%f in %f ms" % (pitch, 1000*(time.time()-start))
                        # Stop condition: the current string is tuned
                        if output.isStringTuned(myChunk.prevs, freqExp):
                                print "String is tuned!"
                                motorMove.turnOnLed()
                                break
                        else:
                                motorMove.turnOffLed()
                                output.executeOrder(pitch, freqExp)
                else:
                        motorMove.stop()


def processInput():
	""" Input processing thread
	Repeatedly check if the button is pressed and then record a chunk of data
	"""
	while True:
                data = record.rec()
                if QUEUE is None: break
                QUEUE.put(data)


def createQueue():
        "Initialises the shared queue between threads"
        global QUEUE
        QUEUE = Queue.Queue()


def destroyQueue():
        "Destroy the shared queue between threads"
        global QUEUE
        QUEUE = None


def stopTuner():
        "Modifies stopping variable in order for the tuner to stop"
        global STOP
        STOP = True


def unStopTuner():
        "Modifies stopping variable in order for the tuner not to stop"
        global STOP
        STOP = False


def main(freqExp = None):
	""" Main function of GuitarAutoTune
	Creates and starts input and output threads and goes placidly to sleep
	"""
        # Create shared synchronized queue
        createQueue()
        # Set STOP condition to False
        unStopTuner()

        # Create and start threads
	inputThread = Thread(target=processInput)
	outputThread = Thread(target=processOutput, args=(freqExp,))
	inputThread.start()
	outputThread.start()

        # Wait until the string is tuned and destroy queue
        outputThread.join()
        destroyQueue()

        # Wait for input thread to gracefully stop and close stream
        inputThread.join()
        record.closeStream()


if __name__ == '__main__':
        while True: main()
