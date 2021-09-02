'''
This serves as the main/experiment function of the greedy/brute force algorithm

'''
import random
import time
import multiprocessing as mp

import pandas as pd
from MaxToteUtilAlgos.entities.box_class import Box
from MaxToteUtilAlgos.entities.pack_class import Pack
from MaxToteUtilAlgos.runnableHelpers import readskulist
from MaxToteUtilAlgos.decanting.greedy.greedy_pack import GreedyPack

SKU_LIST_FILE = "../data/sku_list.csv"
TOTE_INFO = {"w": 23.6, "l": 15.9, "h": 12.2, "weight": 55}
# TOTE_INFO = { "w":25.6, "l":17.7, "h":12.8, "weight":99999999 }
NUM_PROCS = mp.cpu_count()
NUM_ITEMS = 2000
NUM_RUNS = 20
NUM_STATIONS = 15
METHODS = {"BRUTE": True, "GREEDY": False}
METHOD = "GREEDY"
RAND_PUSH = 0.0
PACK_MORE = 0.01

if __name__ == "__main__":

    print(f"Start {METHOD} Packing!")

    tote = Box(TOTE_INFO["w"], TOTE_INFO["l"], TOTE_INFO["h"], 0,
               TOTE_INFO["weight"])
    sku_list = readskulist(SKU_LIST_FILE)
    summary = {"run": [], "avg_util": [], "num_totes": [], "run_time": [], "unpacked": []}

    for i in range(NUM_RUNS):
        print("Start run ", i)
        tic = time.time()

        random.seed(i)
        raw_sku_list = random.sample(sku_list, NUM_ITEMS)

        packs = [Pack(sku) for sku in raw_sku_list]
        greedy_pack = GreedyPack(packs, tote, num_stations=NUM_STATIONS, NUM_PROCS=None,
                                 brute=METHODS[METHOD], rect=True, target_util=0.8, rand_push=RAND_PUSH, pack_more=PACK_MORE)
        greedy_pack.pack_main(verbose=True)

        utils = []
        result_totes = greedy_pack.getTotes()

        for t in result_totes[:-1]:
            utils.append(t.util3d)
        #     t.draw3d()

        avg_uitl = (sum(utils)+greedy_pack.more/tote.getVol()) / len(utils)
        summary["run"].append(i)
        summary["avg_util"].append(avg_uitl)
        summary["num_totes"].append(len(result_totes))
        summary["run_time"].append(time.time() - tic)
        summary["unpacked"].append(greedy_pack.unpacked)

        print("Run time: ", time.time() - tic)
        print("push", greedy_pack.push)
        print("more", greedy_pack.more)
        print("utils: ", avg_uitl)
        print("Complete run", i)

    result = pd.DataFrame.from_dict(summary)
    result.to_csv(f"./result/{METHOD}_summary_i{NUM_ITEMS}_s{NUM_STATIONS}_r{NUM_RUNS}_p{RAND_PUSH}_m{PACK_MORE}.csv", index=False)
