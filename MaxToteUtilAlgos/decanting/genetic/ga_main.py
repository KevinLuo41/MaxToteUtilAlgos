'''
This serves as the main function of the GA algorithm

'''

from MaxToteUtilAlgos.decanting.genetic.ga_pack import GeneticPack
from MaxToteUtilAlgos.entities.box_class import Box
from MaxToteUtilAlgos.entities.pack_class import Pack
from MaxToteUtilAlgos.runnableHelpers import readskulist

from math import ceil
import multiprocessing as mp
import random
import time
import pandas as pd

SKU_LIST_FILE = "../data/sku_list.csv"

TOTE_INFO = {"w": 23.6, "l": 15.9, "h": 12.2, "weight": 55}
# TOTE_INFO = { "w":25.6, "l":17.7, "h":12.8, "weight":999999 }

NUM_PROCS = mp.cpu_count()
NUM_PACKS_PER_RUN = 20
NUM_TRY_PER_RUN = 100
NUM_ITEMS = 100
NUM_RUNS = 200

if __name__ == "__main__":

    tote = Box(TOTE_INFO["w"], TOTE_INFO["l"], TOTE_INFO["h"], "tote",
               TOTE_INFO["weight"])

    summary = {"run": [], "avg_util": [], "num_totes": [], "run_time": []}
    sku_list = readskulist(SKU_LIST_FILE)

    for i in range(NUM_RUNS):
        print("Start run ", i)
        tic = time.time()

        random.seed(i)
        raw_sku_list = random.sample(sku_list, NUM_ITEMS)
        num_run = ceil(len(raw_sku_list)//NUM_PACKS_PER_RUN)

        result_totes= []
        result_totes_list = []

        for j in range(num_run):
            # print("Run # ", i)
            packs = [Pack(item) for item in raw_sku_list[j*NUM_PACKS_PER_RUN:(j+1)*NUM_PACKS_PER_RUN]]

            ga_pack = GeneticPack(packs, tote, POP_SIZE=30, GENERATIONS=10,NUM_PROCS=None,stack=True)
            # pool = mp.Pool(processes=NUM_PROCS)
            # manager = mp.Manager()
            # ga_pack = GeneticPack(packs, tote, 2, NUM_PROCS=NUM_PROCS,packed_seq=manager.dict(),stack=False)

            best_chrom,best_chrom_list = ga_pack.pack()

            result_totes+=best_chrom.getTotes()

            result_totes_list = [chrom.getTotes() for chrom in best_chrom_list]
        utils = []

        for t in result_totes[:-1]:
            utils.append(t.util3d)
            # t.draw3d()

        avg_uitl = sum(utils) / len(utils)
        summary["run"].append(i)
        summary["avg_util"].append(avg_uitl)
        summary["num_totes"].append(len(result_totes))
        summary["run_time"].append(time.time() - tic)

        print("Run time: ", time.time() - tic)
        print("utils: ", avg_uitl)
        print("Complete run", i)

    result = pd.DataFrame.from_dict(summary)
    result.to_csv(f"./result/GENETIC_summary_i{NUM_ITEMS}_r{NUM_RUNS}.csv", index=False)
    print("Complete")

