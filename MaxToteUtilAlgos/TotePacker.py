
from typing import List
from MaxToteUtilAlgos.entities.box_class import Box
from MaxToteUtilAlgos.entities.sku_class import Sku
from MaxToteUtilAlgos.packmeV2 import PackMe
from MaxToteUtilAlgos.entities.stack_calss import Stack

from math import floor



class TotePacker(object):

    def __init__(self, sku_list: List[Sku], tote: Box, stack: bool = True):
        self.sku_list = sku_list
        self.tote = tote
        self.stack = stack
        self.WLH = range(3)

    def pack(self) -> PackMe:
        """ main function essentially of the tote packer. will return a packme
        instance from which we can call .getBox() to get the tote, .getUnfit()
        to get what skus didnt fit and getFinalEPs() to get the EPs of the
        resulting box
        """

        if self.stack:
            sku_dict = dict()
            for sku in self.sku_list: # group the same skus into {sku_id : [skus]}
                sku_id = sku.getName()
                if (sku_id in sku_dict): sku_dict[sku_id].append(sku)
                else: sku_dict[sku_id] = [sku]

            # stacks = [stack for sku_id, skus in sku_dict.items() # flattening the stack list
            #                 for stack in self.createSkuStacks(skus)]
            stacks = []
            for sku_id, skus in sku_dict.items():
                stacks += self.createSkuStacks(skus)
            packer = PackMe()
            packer.setBox(self.tote)
            for stack in stacks:
                packer.addSku(stack)
            packer.pack(self.tote.getEPs()) # passing in EPs of the tote ([] if empty)
        else:
            packer = PackMe()
            packer.setBox(self.tote)
            for sku in self.sku_list:
                packer.addSku(sku)
            packer.pack(self.tote.getEPs())  # passing in EPs of the tote ([] if empty)
        return packer


    def createSkuStacks(self, skus: List[Sku]) -> List[Stack]:
        """given a list of identical skus, will create the stacks and their 
         rotations to pack essentially the "item generator" that generates 
         stacks that will be packed into the tote with the skus as the input
         this function will recursively call itself until there are no more skus
         left to stack... SKUs must be of the same kind
        """
        if not skus: return []
        w,l,h = self.WLH
        tote_max_h = self.tote.getH()
        sku_cnt = len(skus)
        sku_dims = sorted(skus[0].getDims())
        # stack counts for each H diff [w -> h, l -> h, h -> h]
        tote_max_w = self.tote.max_weight//skus[0].weight
        stack_maximums = [min((tote_max_h/sku_dims[i]),tote_max_w) for i in self.WLH]
        remaining = [tote_max_h-min(floor(stack_maximums[i]),sku_cnt)*sku_dims[i] for i in self.WLH]
        # print(stack_maximums)

        best_sku_h_index = remaining.index(min(remaining))
        stack_item_count = min(floor(stack_maximums[best_sku_h_index]),sku_cnt)
        all_skus_in_single_stack = floor(stack_maximums[best_sku_h_index])>=sku_cnt

        # num_accomodations = sum(1 if sku_cnt >1 and stack_max>=sku_cnt else 0 for stack_max in stack_maximums)
        #
        # # figure out the rotation that leads to max stack height & can still stack the total sku cnt
        # if (num_accomodations == 3): # all sku rotations can be accomodated
        #     best_sku_h_index = stack_maximums.index(min(stack_maximums))
        #     all_skus_in_single_stack = True
        # # find largest stack (but not > sku_cnt) we can make that can accomodate the skus
        # elif (num_accomodations == 2 or num_accomodations == 1):
        #     best_sku_h_index = stack_maximums.index(min(filter(lambda x: x>=sku_cnt, stack_maximums)))
        #     all_skus_in_single_stack = True
        # else: # num_accomodations == 0
        #     best_sku_h_index = stack_maximums.index(max(stack_maximums))
        #     all_skus_in_single_stack = False

        chosen_rotation = self.findOptimalRotation(skus[0], sku_dims[best_sku_h_index])

        if all_skus_in_single_stack:
            return [Stack(skus, chosen_rotation)]


        return ([Stack(skus[:stack_item_count], chosen_rotation)]
                + self.createSkuStacks(skus[stack_item_count:]))


    def findOptimalRotation(self, sku: Sku, optimal_height: float) -> int:
        """ will rotate a given sku until the the height dimension (2nd index 
        aka last index) matches that of the optimal height
        returns -1 if none of the rotations match the optimal_height parameter
        """
        for rot in range(6):
            sku.modDimsFromRot(rot)
            if (sku.getDims()[-1] == optimal_height):
                return rot
        return -1 # should not get here



        







