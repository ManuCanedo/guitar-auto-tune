# -*- coding: utf-8 -*-

import hps
from collections import deque

# Sliding window size: number of samples to be storaged temporally
WINDOW_LENGTH = 3


class Chunk:
    "Object representing a chunk of recorded data"

    def __init__(self, data = None, prevsList = WINDOW_LENGTH*[None]):
        "Creates a chunk object with the specified atributes"
        self.data = data
        self.prevs = deque(prevsList, WINDOW_LENGTH)

    def isValid(self, pitch):
        "Returns True if the given pitch is valid based on recent history"
        if pitch is None: return False

        # If the two previous samples were valid and similar between them
        if None not in list(self.prevs)[-2:]:
            if abs(self.prevs[-2] - self.prevs[-1]) < 3:
                # And the current is very different, we discard it
                if abs(pitch - self.prevs[-1]) > 10: return False

        # Otherwise we accept it
        return True

    def getPitch(self):
        """ Returns the next pitch using HPS algorithm and post-processing
        If the data is not good enough, returns None
        """
        pitch = hps.obtainPitch(self.data)

        self.prevs.append(pitch if self.isValid(pitch) else None)

        return self.prevs[-1]
