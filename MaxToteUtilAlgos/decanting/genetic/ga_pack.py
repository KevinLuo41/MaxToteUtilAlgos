from MaxToteUtilAlgos.entities.box_class import Box
from MaxToteUtilAlgos.entities.pack_class import Pack
from MaxToteUtilAlgos.entities.chromosome import Chromosome
from MaxToteUtilAlgos.entities.stack_calss import Stack
from MaxToteUtilAlgos.TotePacker import TotePacker

import multiprocessing as mp
from math import ceil
from copy import deepcopy,copy
from typing import List,Union
import random
import time



###
# restrictions --> 
# (POP_SIZE - ELITE_CNT % 2) == 0     -->    normie count must be divisible by 2
#


### TODO: read this
# pack() is the entry/exit point... the main func of this class.
# it will return a list of filled Totes/boxes.... these totes are the totes that
# will be packed at each of the individual stations... 
# ie. 
# items in totes[0] --> divert to station 0
# items in totes[1] --> divert to station 1
# etc etc

class GeneticPack(object):

    def __init__(self,
                 packs: List[Pack],
                 tote: Box,
                 # init_para: float,
                 # packed_seq: dict,
                 tote_try:int = None,
                 stack:bool = False,
                 # rect:bool = False,
                 NUM_PROCS = None,
                 POP_SIZE: int = None,  # skus^station
                 GENERATIONS: int = 2,
                 MUTATION_RATE: float = 0.2,
                 ELITE_CNT: int = None,
                 PROB_GOOD_PARENT: float = 0.85,
                 PROB_INFERTILE_PARENTS: float = 0.1):

        self.NUM_PROCS = NUM_PROCS
        self.CHROM_SIZE = len(packs)
        self.POP_SIZE = min(100, POP_SIZE) if POP_SIZE else int(1.5*self.CHROM_SIZE)
        self.GENERATIONS = GENERATIONS
        self.MUTATION_RATE = MUTATION_RATE
        self.ELITE_CNT = ELITE_CNT if ELITE_CNT else self.POP_SIZE // 5
        self.PROB_GOOD_PARENT = PROB_GOOD_PARENT
        self.PROB_INFERTILE_PARENTS = PROB_INFERTILE_PARENTS

        self.og_packs = self.formatSkus(packs)
        self.tote = tote
        self.unpacked = 0
        # self.init_para = init_para
        self.min_num_tote = ceil(sum(sku.getVol() for pack in packs for sku in pack.getSkus())/ tote.getVol())

        if tote_try:
            self.tote_try = tote_try
        else:
            self.tote_try = self.min_num_tote

        self.packed_seq = {}
        self.stack = stack
        self.results = list()

    ############################ INIT FUNCS ####################################
    ###
    # helper function to the class constructor 
    # creates unique indexes for each sku
    ###
    def formatSkus(self, packs: List[Pack]):
        for i, pack in enumerate(packs):
            pack.setIndex(pack.getIndex()*(i+1))
            for j, sku in enumerate(pack.getSkus()):
                sku.setIndex(pack.getIndex()+j+1)
        return packs

    ###
    # formats the population from the self.og_skus... it will create POP_SIZE
    # copies of the sku list, each with different ordering
    ###
    def initPopulation(self) -> List[Chromosome]:
        num_packs = len(self.og_packs)
        sequence = [i % self.tote_try for i in range(num_packs)]
        population = [copy(sequence) for _ in range(self.POP_SIZE)]
        for i in range(1, self.POP_SIZE):  # index 0 stays in order (round robin)
            random.shuffle(population[i])

        # population = []
        #
        # num_tote_try = ceil(self.min_num_tote*self.init_para) - self.min_num_tote+1
        # for num in range(self.min_num_tote,ceil(self.min_num_tote*self.init_para)+1):
        #     sequence = [i % num for i in range(num_packs)]
        #     population += [copy(sequence) for _ in range(self.POP_SIZE // num_tote_try)]
        #
        # for i in range(1,len(population)):
        #     rand.shuffle(population[i])


        return [Chromosome(seq, [deepcopy(self.tote)])
                # TODO: might not need to deepcopy as the packer creates own copy
                for seq in population]

    ###
    # override func to set the tote
    ###
    def setTote(self, tote: Box):
        self.tote = tote

    ############################################################################

    # kind of like the starting point of the geneticPack class. 
    # will initialize the population and then run the breeding function 
    # over and over... kind of like evolving the population
    # GENERATIONS number of times. will return the best scoring chromie's totes
    # which contains the items 
    ###
    def pack(self):
        pop = self.initPopulation()
        best_chrom_list = []
        for i in range(self.GENERATIONS):
            print("Generation ", i)
            tic = time.time()
            pop = self.breed(pop)
            print("Run time: ", time.time()-tic,"\n")

        # best score (number of totes) is the lowest score
            best_chrom_list += [min(pop, key=lambda p: p.getScore())]
        best_chrom = min(pop, key=lambda p: p.getScore())
        return best_chrom, best_chrom_list

    ###
    # packs each chromie in its own process and then will score each one.
    # elites and normies are separated. elites continue on to next gen.
    # normies go thru selection and those selected go on to next gen.
    ###

    # - Kaiwen
    ### choose selection type from: tournament, etc.
    def breed(self, pop: List[Chromosome], selection: str = "tournament") -> List[Chromosome]:
        print("===> breeding")
        count = len(pop)
        # with mp.Pool(processes=NUM_PROCS) as pool: # each core pack a chromosome
        #     packs = pool.map(self.multiProcPack, pop) # each Chromosome is a packing sequence
        # print(count)
        print("=====> packing")
        if self.NUM_PROCS:
            p = mp.Pool(self.NUM_PROCS)
            packs = p.map(self.multiProcPack, pop)
            p.close()
            p.join()
        else:
            packs = []
            for i, p in enumerate(pop):
                # print(i," th chrom")
                packs.append(self.multiProcPack(p))
            # packs = list(map(self.multiProcPack, pop))



        scores = [self.score(pack) for pack in packs]
        results = [Chromosome(pop[i].getSequence(), packs[i], scores[i])
                   for i in range(count)]  # reconstruct the chromies from the packs

        results.sort(key=lambda res: res.getScore())  # best to worst: ascending # totes used

        if selection == "tournament":
            elites = results[:self.ELITE_CNT]
            # for i in elites:
            #     i.setElite(True)
            elite_children = self.selection(elites, duplicated=True)
            normie_children = self.selection(results[self.ELITE_CNT:], duplicated=True)
            for normie in normie_children:
                normie.setElite(False)
            return elite_children + normie_children
        else:
            raise TypeError("Selection type error")

    ###
    # helper function to self.breed -- this func is just the wrapper func around
    # Mr.Packman (python version). 
    ###
    def multiProcPack(self, pack_input: Chromosome) -> Union[List[Box], float]:
        # print("###packing####")
        sequence = pack_input.getSequence()
        if pack_input.isElite() or tuple(sequence) in self.packed_seq.keys():  # dont repack elites, since they are the same as before
            # self.packed_seq[tuple(sequence)]+=1
            return self.packed_seq[tuple(sequence)]

        #? not sure if deepcopu
        all_packs, tote = deepcopy(self.og_packs), self.tote

        station_cnt = max(sequence) + 1
        result_totes = []


        for station in range(station_cnt):  # pack station by station
            # print("station ", station)
            # packs = [all_packs[i] for i, s in enumerate(sequence) if s == station]
            skus = []
            for i, s in enumerate(sequence):
                if s == station:
                    ps = all_packs[i].getSkus()
                    ww,ll,hh = sorted([ps[0].getW(),ps[0].getL(),ps[0].getH()])
                    if not (tote.getW()>=ww and tote.getL()>=ll and tote.getH()>=hh):
                        self.unpacked+=1
                        continue
                    skus += all_packs[i].getSkus()

            while len(skus) > 0:  # keep packing until all skus packed into a tote

                # pack stack first
                packer = TotePacker(skus, tote, self.stack)
                # fill with single skus

                p = packer.pack()
                  # passing in an empty EP list

                if self.stack:
                    packed_skus = {sku.getIndex() for stack in p.getBox().getContents() for sku in stack.getSkus()}
                    skus = [sku for sku in skus if sku.getIndex() not in packed_skus]
                    if skus:
                        packer2 = TotePacker(skus, p.getBox(), False)
                        p = packer2.pack()
                        packed_skus = set()
                        for item in p.getBox().getContents():
                            if isinstance(item, Stack):
                                for sku in item.getSkus():
                                    packed_skus.add(sku)
                            else:
                                packed_skus.add(item)
                else:
                    packed_skus = {sku.getIndex() for sku in p.getBox().getContents()}
                skus = [sku for sku in skus if sku.getIndex() not in packed_skus]


                result_totes.append(p.getBox())


        self.packed_seq[tuple(sequence)]=result_totes
        return result_totes

    ###
    # should only be the number of totes as the number of items considered
    # is always the same
    # this can change tho if we introduce variable sequence sizes
    ### TODO: what other factors should be taken into consideration? how should they be weighted?
    ###
    def score(self, totes: List[Box]) -> float:

        avg_util = 0

        for t in totes:
            avg_util += sum(s.getVol() for s in t.getContents())/t.getVol() /len(totes)
        return 1-avg_util
        # return len(totes)

    # can implement something where we choose better parents instead of just 
    # random parents
    def selection(self, pool: List[Chromosome], duplicated: bool) -> List[Chromosome]:
        print("=======> selection")
        random.shuffle(pool)
        # go thru the population and add some good & some bad to mating pool

        # Some bugs here, just expand the expression
        # mating_pool = [ min(pool[i:i+2], key=lambda p: p.getScore())
        #                 if rand.random() <= PROB_GOOD_PARENT
        #                 else max(pool[i:i+2], key=lambda p: p.getScore())
        #                 for i in range (0, len(pool), 2) ]
        mating_pool = []
        non_mating = []
        for i in range(0, len(pool), 2):
            if random.random() <= self.PROB_GOOD_PARENT:
                mating_pool.append(min(pool[i:i + 2], key=lambda p: p.getScore()))
                non_mating.append(max(pool[i:i + 2], key=lambda p: p.getScore()))
            else:
                mating_pool.append(max(pool[i:i + 2], key=lambda p: p.getScore()))
                non_mating.append(min(pool[i:i + 2], key=lambda p: p.getScore()))

        # for those in the mating pool, breed or push thru to end

        if len(mating_pool) % 2:
            mating_size = len(mating_pool) - 1
            mating_left = [mating_pool[-1]]
        else:
            mating_size = len(mating_pool)
            mating_left = []
        print("=========> making children")
        selected = [(mating_pool[i], mating_pool[i + 1])
                    if random.random() <= self.PROB_INFERTILE_PARENTS  # go directly from pool to selected b/c infertile
                    else self.crossover(mating_pool[i], mating_pool[i + 1])
                    for i in range(0, mating_size, 2)]
        # flatten the 2d list to 1d
        return non_mating + [chromie for chromies in selected for chromie in chromies] + mating_left

    #################################################################################### TODO
    def crossover(self, p1: Chromosome, p2: Chromosome) -> List[Chromosome]:

        return [self.makeChild(p1, p2), self.makeChild(p1, p2)]

    # two parents make a child that is a mix of 'em both. can mutate
    # We cannot fully refer to Li's paper, the elements in the sequence are not unique.
    # Here we test the simplest crossover method: single-point crossover.
    def makeChild(self, p1: Chromosome, p2: Chromosome) -> Chromosome:
        num_skus = len(p1.getSequence())

        # inherit more sequence from the better chromosome
        cutpoints = random.randint(0, num_skus // 2)
        p1_skus, p2_skus = p1.getSequence(), p2.getSequence()
        if p1.getScore() < p2.getScore():
            child_seq = p1_skus[:cutpoints] + p2_skus[cutpoints:]
        else:
            child_seq = p2_skus[:cutpoints] + p1_skus[cutpoints:]

        # added = set(i for i,c in enumerate(child_skus) if c != None)
        # # insert genes from second parent
        # add_loc = cutpoints[1] # start adding after second cutpoint
        # for i in range(cutpoints[1], num_skus):
        #     ind = i % num_skus
        #     if p2_skus[ind] not in added:
        #         child_skus[add_loc] = deepcopy(p2_skus[ind])
        #         add_loc = (add_loc + 1) % num_skus # wrap around to begining
        if random.random() <= self.MUTATION_RATE:
            return self.mutate(child_seq)
        else:
            return Chromosome(child_seq, [deepcopy(self.tote)])

    # choose two sku in the order sequence and then swap em
    def mutate(self, seq: List[int],swap= True) -> Chromosome:
        # swap two elements
        if swap:
            i, j = random.sample(range(0, len(seq)), 2)  # swap_points
            seq[i], seq[j] = seq[j], seq[i]
        else:
            x = random.randint(0,len(seq)-1)
            p = random.randint(0,max(seq)-1)
            seq[x] = p

        return Chromosome(seq, [deepcopy(self.tote)])
