'''
@author: Rei Siew Hew Sam (rus003o)

this file holds the code for an stack class
aka,the stack can only include same skus.

'''
from .sku_class import Sku

from typing import List
""" ROT_TYPES = { 0 : 'W,L,H',
                1 : 'L,W,H',
                2 : 'L,H,W',
                3 : 'H,L,W',
                4 : 'H,W,L',
                5 : 'W,H,L'
            }
"""

class Stack(Sku):

    def __init__(self, skus: List[Sku], rotation: int, stack_on_top=False):
        """ the stack on top flag determines if THIS stack can be placed on
        another stack. NOT whether another stack can be placed on this stack...
        """
        for sku in skus:
            sku.modDimsFromRot(rotation)
        width, length, height = skus[0].getDims()
        single_weight = skus[0].getWeight()
        height *= len(skus)
        weight = single_weight*len(skus)
        super().__init__(width, length, height, weight,
                                    name=skus[0].getName(),
                                    chem=skus[0].getChemical, sort=False)
        self.skus = skus

        self.can_stack_on_top = stack_on_top
        # allowed_rotations will only have two elements
        self.allowed_rotations = {0, 1} # want to keep the last dim (the height) constant
        self.finalizeMove()
    
    def rotate(self, rot: int):
        if (rot not in self.allowed_rotations):
            return
        else:
            self.modDimsFromRot(rot)

    def getAllowedRotations(self):
        return self.allowed_rotations

    def getCanStackOnTop(self) -> bool:
        return self.can_stack_on_top

    def getSkus(self) -> List[Sku]:
        return self.skus

    # move all positions of the skus to the actual positions within the stack
    def finalizeMove(self):
        x,y,z = 0,1,2
        cur_pos = self.getPos()
        for i,sku in enumerate(self.skus):
            sku.modPos([cur_pos[x], cur_pos[y], cur_pos[z] + (i * sku.getH())])
            sku.modDimsFromRot(self.getRotation())
