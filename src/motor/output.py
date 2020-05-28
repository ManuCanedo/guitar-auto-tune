#!/usr/bin/python
# -*- coding: utf-8 -*-

import motorMove

''' Tolerance line defining parameters: slope and offset
The tolerance is a linear function of the expected frequency, and its value is used as
an absolute value: string is tuned <-> |freqRec-freqExp| <= tolerance(freqExp)
'''
SLOPE = (1 - 0.5) / (300 - 100)
OFFSET =  0.5 - 100 * SLOPE

# List of tuned pitches, each one of them for a single string
PITCHES = [329.63, 246.94, 196.00, 146.83, 110.00, 82.41]

''' List of frequency ranges' limits
Limit between frequency f1 and f2 is computed as follows:
limit = (f1 + f2) / 2'''
LIMITS = [339.41, 288.28, 221.47, 171.42, 128.42, 96.21, 72.05]

# Maximum and minimum speeds that the motor supports
MAX_SPEED = 128
MIN_SPEED = 40


def getTunedPitch(freqRec):
	''' Returns the expected frequency (pitch) for this string.
	Please note that this function asumes that the string is not too much out of
	tune i.e. the recorded frequency is close to its string's target frequency.
	'''
	for index in range(len(LIMITS) - 2):
		if(freqRec >= LIMITS[index + 1]):
			# If the frequency is more than this limit,
			# the expected pitch is the one inmediately above
			return PITCHES[index]

	# If the recorded frequency is lower than every limit, it means that the
	# expected pitch should be the lowest (last in PITCHES list)
	return PITCHES[-1]


def getRange(freqExp, below = True):
	''' Returns the maximum distance a frequency can be from its target,
	which is the difference between the bottom (top if below=False) limit and
	the farget frequency itself.
	'''
        if freqExp not in PITCHES: return 10.0

	pitchIndex = PITCHES.index(freqExp)
	return freqExp - LIMITS[pitchIndex+1] if below else LIMITS[pitchIndex] - freqExp


def isStringTuned(pitches, freqExp = None):
        ''' Returns True if the guitar string is already tuned
        The tuning condition is that the last valid pitches detected
        have to be tuned at the same target frequency
        '''
        if None in pitches: return False

        if (max(pitches) - min(pitches)) <= 4: # 2*getTolerance(700)
                return all(isTuned(pitch, freqExp) for pitch in pitches)
        else:
                return False


def isTuned(freqRec, freqExp = None):
        'Returns True if the recorded frequency is tuned based on the tolerance'
        if freqExp is None: freqExp = getTunedPitch(freqRec)

        return abs(getDistance(freqRec, freqExp)) <= getTolerance(freqExp)


def getDistance(freqRec, freqExp):
        'Returns the distance (with sign) to the target frequency in Hz'
        return freqExp - freqRec


def getTolerance(freqExp):
        ''' Returns the absolute tolerance for the given frequency
        From the line with SLOPE slope and OFFSET value at x = 0,
        returns the value of such line at freqExp (value in x axis)
        '''
        return SLOPE * freqExp + OFFSET


def getSpeed(distance, freqExp):
        ''' Returns the speed given the expected frequency and the distance to it
        Spinning speed is proportional to the distance to the expected pitch'''
        rangeLength = getRange(freqExp, (distance > 0))
        return int(abs(distance) * MAX_SPEED / rangeLength) + MIN_SPEED


def executeOrder(freqRec, freqExp = None):
	''' Given the recorded frequency, spins the motor so that the pitch played
	moves towards the target (tuned) pitch.
	The string should be tensed/relaxed faster when it is quite out of tune, and
	slower when it's almost tuned.
	'''
        if freqExp is None: freqExp = getTunedPitch(freqRec)
        distance = getDistance(freqRec, freqExp)

        # If the string is not tuned and the frequency recorded is reasonable...
	if not isTuned(freqRec, freqExp) and (abs(distance) < freqExp/2):
                speed = getSpeed(distance, freqExp)

		if(distance > 0):
			# We tense the string if the frequency is below the target
			motorMove.tense(speed)
		else:
			# Otherwise we relax it
			motorMove.relax(speed)

	# If the pitch is already tuned, we stop the motor
	else:
		motorMove.stop()
