import sys

from .box_class import Box
from typing import List


class Chromosome(object):

    def __init__(self, sequence: List[int], totes: List[Box], score: float=sys.maxsize):
        self.sequence = sequence # [0,1,2,3,4,5,0,1,2,3,4,5] --> len(sequence) = len(skus)
        self.score = score
        self.totes = totes
        self.Elite = False

    def setElite(self, flag: bool):
        self.Elite = flag
    
    def isElite(self):
        return self.Elite

    def setSequence(self, sequence: List[int]):
        self.sequence = sequence

    def setScore(self, score: float):
        self.score = score

    def setTotes(self, totes: List[Box]):
        self.totes = totes

    def getSequence(self) -> List[int]:
        return self.sequence

    def getScore(self) -> float:
        return self.score

    def getTotes(self) -> List[Box]:
        return self.totes


