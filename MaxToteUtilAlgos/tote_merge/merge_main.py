'''
@author: Kaiwen Luo (k0l06rk)
this file holds the code for the main/experiments of tote merge.

'''

import random
import time

from MaxToteUtilAlgos.runnableHelpers import ReadSimulation
from MaxToteUtilAlgos.runnableHelpers import partition
from MaxToteUtilAlgos.runnableHelpers import Box
from MaxToteUtilAlgos.tote_merge.tote_merge import ToteMerger
import multiprocessing as mp
import pandas as pd

# TOTE INFO - 2 Types
TOTE_INFO = {"w": 23.6, "l": 15.9, "h": 12.2, "weight": 55}
# TOTE_INFO = { "w":25.6, "l":17.7, "h":12.8, "weight":55 }
tote = Box(TOTE_INFO["w"], TOTE_INFO["l"], TOTE_INFO["h"], 0, TOTE_INFO["weight"])

# Experiment Settings
## NUM_INPUTS: Total number of input totes
## INTERVALS: Increment of number of totes in experiments
NUM_INPUTS = 2000
INTERVALS = 200

# Mehtod Selection - 2 types of tote merge
method = "MAX_UTIL"
# method = "IN_ORDER"

# Multiprocessing or not
# NUM_PROCS = mp.cpu_count()
BATCH_SIZE = 500
NUM_PROCS = None

# Output Summary
summary = {"num_totes": [], "run_time": [], "num_save": [], "avg_util_before_3d": [],
           "avg_util_after_3d": [], "avg_util_before_2d": [], "avg_util_after_2d": []}

# Helper function to choose tote merge method.
def merge(totes,method):
    Merger = ToteMerger(totes)
    if method == "IN_ORDER":
        result_totes = Merger.merge_in_order()
    elif method == "MAX_UTIL":
        result_totes = Merger.merge_max_util()
    else:
        raise TypeError("Method can be only chosen from IN_ORDER or MAX_UTIL")

    return result_totes

if __name__ == "__main__":

    # Read input: if a .xlsx is given, it will be first convert to a .pkl file for further use
    # totes = ReadSimulation("./data/NJ51_Simulation_Data_Bin_Packing.xlsx",tote)
    totes = ReadSimulation("./data/raw_totes_NJ51.pkl")

    # Experiment start
    for i in range(1200, NUM_INPUTS + INTERVALS, INTERVALS):
        tic = time.time()

        # Random sample input totes
        random.seed(i)
        sub_totes = random.sample(totes, i)

        # Merging
        if not NUM_PROCS:
            result_totes = merge(sub_totes,method)
        else:
            totes_batch = partition(sub_totes,round(len(sub_totes)/BATCH_SIZE))
            pool = mp.Pool(NUM_PROCS)
            msgs = zip(totes_batch,len(totes_batch)*[method])
            result = pool.starmap_async(merge,msgs)
            result_totes = result.get()
            pool.close()
            pool.join()

            result_totes = [item for batch in result_totes for item in batch]

        # Result collection

        num_save = i - len(result_totes)

        util_before_2d = sum([x.util2d for x in sub_totes]) / i
        util_after_2d = sum([x.util2d for x in result_totes]) / len(result_totes)
        util_before_3d = sum([x.util3d for x in sub_totes]) / i
        util_after_3d = sum([x.util3d for x in result_totes]) / len(result_totes)
        run_time = time.time() - tic

        print("Run time: ", time.time() - tic)
        print("num_save: ", num_save)
        print("avg_util_before_3d: ", util_before_3d)

        print("avg_util_after_3d: ", util_after_3d)
        print("avg_util_before_2d: ", util_before_2d)
        print("avg_util_after_2d: ", util_after_2d)
        print("Complete run", i)

        summary["num_totes"].append(i)
        summary["run_time"].append(time.time() - tic)
        summary["num_save"].append(num_save)
        summary["avg_util_before_3d"].append(util_before_3d)
        summary["avg_util_after_3d"].append(util_after_3d)
        summary["avg_util_before_2d"].append(util_before_2d)
        summary["avg_util_after_2d"].append(util_after_2d)

    result = pd.DataFrame.from_dict(summary)
    if NUM_PROCS:
        result.to_csv(f"./result/{method}_summary_i{NUM_INPUTS}_t{INTERVALS}_b{BATCH_SIZE}.csv", index=False)
    else:
        result.to_csv(f"./result/{method}_summary_i{NUM_INPUTS}_t{INTERVALS}_b0.csv", index=False)
    print("complete")
