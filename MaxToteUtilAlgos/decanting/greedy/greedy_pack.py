'''
@author: Kaiwen Luo (k0l06rk)
this file holds the code for the greedy/ brute force pack class

'''

from typing import List, Tuple
import random
from copy import deepcopy
import multiprocessing as mp
from rectpack import newPacker, PackingMode, PackingBin

from MaxToteUtilAlgos.entities.stack_calss import Stack
from MaxToteUtilAlgos.entities.station_class import Station
from MaxToteUtilAlgos.entities.box_class import Box
from MaxToteUtilAlgos.entities.pack_class import Pack
from MaxToteUtilAlgos.TotePacker import TotePacker

'''
Greedy Pack class:
    input:
        packs: list of packs to be pack
        num_stations: hyperparameters, the number of open decanting stations
        target_util: utilization threshold, over which the totes will be closed and pushed to ASRS
        NUM_PROCS: number of cpu cores assigned to batch computing
        brute: if brute force algo runs instead of greedy
        rect: if using rectpack instead of packman 
        stack: if allow same sku stack together
'''
class GreedyPack:
    def __init__(self, packs: List[Pack], tote: Box, num_stations: int, target_util: float, rand_push:float = 0.0,
                 pack_more:float = 0.0,NUM_PROCS: int = None,
                 brute: bool = False, rect: bool = False, stack=True):
        self.packs = self.formatSkus(packs)
        self.tote = tote
        self.num_stations = num_stations
        self.target_util = target_util
        self.NUM_PROCS = NUM_PROCS
        self.stack = stack
        self.stack_idx = 0
        self.brute = brute
        self.rand_push = rand_push
        self.pack_more = pack_more
        self.rect = rect
        self.unpacked = 0
        self.push= 0
        self.more = 0
        self.stations = [Station(id=i, totes=[]) for i in range(self.num_stations)]

    def formatSkus(self, packs: List[Pack]):
        for i, pack in enumerate(packs):
            pack.setIndex(pack.getIndex() * (i + 1))
            for j, sku in enumerate(pack.getSkus()):
                sku.setIndex(pack.getIndex() + j + 1)
        return packs

    def getTotes(self) -> List[Box]:
        result_totes = []
        for station in self.stations:
            result_totes += station.getTotes()[:-1]
        return result_totes

    # try pack the next coming case to a give decanting station
    # ouputs: util3d, util2d, remain(Bool): if there are remaining skus after packing.
    def _try_pack(self, pack_station: Tuple[Pack, int]) -> List[float]:
        pack, s = pack_station
        skus = pack.getSkus()
        if not self.stations[s].getTotes():
            tote = deepcopy(self.tote)
            tote.setName(len(self.stations[s].getTotes()))
            if self.rect:
                tote = self.create_tote(s)
        else:
            tote = self.stations[s].getTotes()[-1]

        # try Tote Packer
        if not self.rect:
            packer = TotePacker(skus, tote, self.stack)
            p = packer.pack()
            if self.stack:
                packed_skus = {sku.getIndex() for stack in p.getBox().getContents() for sku in stack.getSkus()}
                skus = [sku for sku in skus if sku.getIndex() not in packed_skus]
                if skus:
                    packer2 = TotePacker(skus, p.getBox(), False)
                    p = packer2.pack()
                    for item in p.getBox().getContents():
                        if not isinstance(item, Stack):
                            packed_skus.add(item.getIndex())

                skus = [sku for sku in skus if sku.getIndex() not in packed_skus]
            return p.getBox().getUtilization() + [len(skus) > 0]
        # use rectpack
        else:
            tp = TotePacker([], self.tote)
            stacks = tp.createSkuStacks(skus)
            count = len(tote.rect.rect_list())
            for stack in stacks:
                if tote.total_weight + stack.getWeight() > tote.max_weight:
                    return [tote.util3d, tote.util2d, True]
                tote.rect.add_rect(stack.getW(), stack.getL())
                if len(tote.rect.rect_list()) > count:
                    count += 1
                    tote.util3d += stack.getVol() / tote.getVol()
                    tote.util2d += stack.width * stack.length / tote.getDim()
                else:
                    return [tote.util3d, tote.util2d, True]
            return [tote.util3d, tote.util2d, False]

    # Pack one case to station s; update the stations
    def pack_one(self, pack: Pack, s: int):
        skus = pack.getSkus()
        if not self.stations[s].getTotes():
            if not self.rect:
                tote = deepcopy(self.tote)
                tote.setName(len(self.stations[s].getTotes()))
            else:
                tote = self.create_tote(s)
        else:
            if random.random() < self.rand_push:
                tote = self.create_tote(s)
                self.push+=1
            else:
                tote = self.stations[s].getTotes()[-1]

        if not self.rect:
            while len(skus) > 0:
                packer = TotePacker(skus, tote, self.stack)
                p = packer.pack()
                if self.stack:
                    packed_skus = {sku.getIndex() for stack in p.getBox().getContents() for sku in stack.getSkus()}
                    skus = [sku for sku in skus if sku.getIndex() not in packed_skus]
                    if skus:
                        packer2 = TotePacker(skus, p.getBox(), False)
                        p = packer2.pack()
                        packed_skus = set()
                        for item in p.getBox().getContents():
                            if not isinstance(item, Stack):
                                packed_skus.add(item.getIndex())
                else:
                    packed_skus = {sku.getIndex() for sku in p.getBox().getContents()}
                skus = [sku for sku in skus if sku.getIndex() not in packed_skus]

                self.stations[s].updateTote(p.getBox())
                if skus:
                    tote = deepcopy(self.tote)
                    tote.setName(len(self.stations[s].getTotes()))
        else:
            tp = TotePacker([], self.tote)
            stacks = set(tp.createSkuStacks(skus))
            while stacks:
                count = len(tote.rect.rect_list())
                stack = stacks.pop()
                if tote.total_weight + stack.getWeight() > tote.max_weight:
                    stacks.add(stack)

                    tote = self.create_tote(s)

                tote.rect.add_rect(stack.getW(), stack.getL())
                if len(tote.rect.rect_list()) > count:
                    tote.util3d += stack.getVol() / tote.getVol()
                    tote.util2d += stack.width * stack.length / tote.getDim()
                    tote.total_weight += stack.getWeight()
                else:
                    stacks.add(stack)
                    tote = self.create_tote(s)
                self.stations[s].updateTote(tote)
            # return [tote.util3d, tote.util2d, False]

    def create_tote(self, s):
        tote = deepcopy(self.tote)
        tote.setName(len(self.stations[s].getTotes()))
        tote.rect = newPacker(mode=PackingMode.Online, bin_algo=PackingBin.BNF)
        tote.rect.add_bin(tote.getW(), tote.getL())
        return tote


    def pack_main(self, verbose=False):
        for i, p in enumerate(self.packs):
            if verbose and i % 250 == 0:
                print(f"==> complete {i}/{len(self.packs)}")

            if random.random()<self.pack_more:
                # self.more+=1
                for sku in p.getSkus():
                    self.more += sku.getVol()
                continue
            # test fit
            ww, ll, hh = sorted([p.getSkus()[0].getW(), p.getSkus()[0].getL(), p.getSkus()[0].getH()], reverse=True)
            if not (self.tote.getW() >= ww and self.tote.getL() >= ll and self.tote.getH() >= hh):
                self.unpacked += 1
                continue

            # if it's brute force, then random select one and pack
            if self.brute:
                s = random.randint(0, self.num_stations - 1)
                self.pack_one(p, s)

            else:
                try_p = [deepcopy(p) for _ in range(self.num_stations)]
                try_ps = list(zip(try_p, range(self.num_stations)))
                if self.NUM_PROCS:
                    p = mp.Pool(self.NUM_PROCS)
                    try_utils = p.map_async(self._try_pack, try_ps)
                    p.close()
                    p.join()
                else:
                    try_utils = list(map(self._try_pack, try_ps))

                utils_3d = [u[0] for u in try_utils]
                utils_2d = [u[1] for u in try_utils]
                remain = [u[2] for u in try_utils]

                # if a tote has already above the target utilization
                # or if the next coming pack cannot be fully packed into any totes
                # then select the tote with max util, pack and close it

                if max(utils_3d) >= self.target_util or not (False in remain):
                    s = utils_3d.index(max(utils_3d))
                    self.pack_one(p, s)
                    # ttt = self.stations[s].getTotes()[-2]
                    # ttt.draw2d()

                # otherwise, choose the tote with maximum available space
                else:
                    xx = zip(range(self.num_stations), utils_2d, remain)
                    yy = filter(lambda x: x[2] is False, xx)
                    zz = min(yy, key=lambda x: x[1])
                    s = zz[0]
                    self.pack_one(p, s)


