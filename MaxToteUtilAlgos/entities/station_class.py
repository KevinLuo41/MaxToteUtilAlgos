'''
@author: Kaiwen Luo (k0l06rk)

this file holds the code for a decanting station class.
'''

from typing import List

from MaxToteUtilAlgos.entities.box_class import Box

class Station():
    def __init__(self,id:int, totes:List[Box]):
        self.id = id
        self.totes = totes

    def getId(self):
        return self.id

    def getTotes(self):
        return self.totes

    def updateTote(self, tote:Box):
        if self.totes and tote.getName() == self.totes[-1].getName():
            self.totes[-1] = tote
        else:
            self.totes.append(tote)



