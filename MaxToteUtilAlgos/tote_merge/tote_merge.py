'''
@author: Kaiwen Luo (k0l06rk)
this file holds the code for the tote merge class.
Two algos are provide: In-Order; Max-Util
'''

from typing import List, Union
from copy import deepcopy

from MaxToteUtilAlgos.TotePacker import TotePacker
from MaxToteUtilAlgos.entities.box_class import Box

class ToteMerger:
    '''
    ToteMerge class
    Input:
        totes: list of totes that waiting to be merged
    '''
    def __init__(self, totes: List[Box]):
        self.totes = totes
        self.empty_tote = Box(totes[0].width, totes[0].length, totes[0].height, 'M0', totes[0].max_weight)
        self.count = 0
        # result merge is a dict that key is merged totes, values are its children tote.
        self.result_merge = {}
        self.unmerged = []

    # sort totes from min to max utilization
    def sort_totes(self):
        self.totes.sort(key=lambda x: x.util2d)

    # Max Util Merge: first tote is selected from the beginning, second tote is selected from the back.
    # Basic idea: maximize the merged tote utilization after merged
    def merge_max_util(self):
        remain_totes = dict.fromkeys(self.totes,0)
        while remain_totes:
            if len(remain_totes) % 10 == 0:
                print("# of remaining totes: ", len(remain_totes))

            remain_totes = dict(sorted(remain_totes.items(),key=lambda x:x[0].util2d))
            merged = list(remain_totes.keys())[0]
            temp_result = [merged]
            remain_totes.pop(merged, None)

            # if overweight, then skip this one
            if merged.total_weight>=merged.max_weight or merged.util2d>0.5:
                self.result_merge[merged] = temp_result
                continue
            idx = 0
            box =None
            for merging in list(remain_totes.keys())[::-1]:
                idx+=1
                box = self._try_merge(merged, merging)

                # if util>100%, all totes behind this one would be over uitl, so remove these totes from sequence.
                if box == -1:
                    remain_totes.pop(merging, None)

                # Successfully merged
                elif box:
                    all_children = self.result_merge.get(merged,[merged])+self.result_merge.get(merging,[merging])
                    self.result_merge.pop(merged,None)
                    self.result_merge.pop(merging,None)
                    self.result_merge[box]=all_children
                    remain_totes.pop(merging, None)
                    remain_totes.pop(merged, None)
                    remain_totes[box] = 1
                    break

            if box is None or box == -1:
                merged_children = self.result_merge.get(merged,[merged])
                self.result_merge[merged] = merged_children

        return list(self.result_merge.keys())

    # In order merge: merge the first several totes until over util limit in each iteration.
    def merge_in_order(self):
        self.sort_totes()
        remain_totes = dict.fromkeys(self.totes,0)

        while remain_totes:
            if len(remain_totes) % 50 == 0:
                print("# of remaining totes: ", len(remain_totes))
            merged = list(remain_totes.keys())[0]
            temp_result = [merged]
            remain_totes.pop(merged, None)

            if merged.total_weight>=merged.max_weight:
                self.result_merge[merged] = temp_result
                continue

            idx = 0
            for merging in list(remain_totes.keys())[idx:]:
                idx+=1
                box = self._try_merge(merged, merging)
                if box == -1:
                    self.result_merge[merged] = temp_result
                    break
                elif box:
                    temp_result.append(merging)
                    remain_totes.pop(merging, None)
                    merged = box
                    idx-=1

    '''
    this function is trying to merged two totes.
    There are three outcomes:
        overweight: return None,
        fail to merge but not over 100% util limit: return None
        over 100% util limit: return -1
        successfully merged: return merged tote
    '''
    def _try_merge(self, merged: Box, merging: Box) -> Union[int, None, Box]:
        if merging.util2d + merged.util2d > 1:
            return -1
        if merging.total_weight + merged.total_weight > merged.max_weight:
            return None
        if len(merged.getContents())>len(merging.getContents()):
            merging,merged = merged,merging

        merging,starter = self.indexing(merging,0)
        merged,starter = self.indexing(merged,starter)
        skus = merged.getContents()
        packer = TotePacker(skus, deepcopy(merging),False)
        p = packer.pack()
        packed_skus = set()
        for item in p.getBox().getContents():
            packed_skus.add(item.getIndex())
        skus = [sku for sku in skus if sku.getIndex() not in packed_skus]
        if skus:
            return None
        else:
            # merged.draw3d()
            # merging.draw3d()
            # p.getBox().draw3d()
            return p.getBox()

    def indexing(self, tote:Box, start:int = 0):
        for item in tote.getContents():
            item.setIndex(start)
            start+=1
        return tote,start