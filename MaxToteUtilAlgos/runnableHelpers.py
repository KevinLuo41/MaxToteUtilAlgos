import pickle
import pandas as pd
from copy import deepcopy

from MaxToteUtilAlgos.entities.box_class import Box
from MaxToteUtilAlgos.entities.sku_class import Sku
from MaxToteUtilAlgos.TotePacker import TotePacker

# Read simulation file to pkl file for further modeling.
def ReadSimulation(filename: str, tote: Box=None, num: int = None, cutoff: float = 0.35,verbose = True):
    if filename[-3:] == "pkl":
        with open(filename, 'rb') as f:
            t = pickle.load(f)
            return t
    elif filename[-4:] == "xlsx":
        df = pd.read_excel(filename)
    else:
        raise TypeError("Input file can be only .pxl or .xlsx")

    if num:
        df = df.sample(num)

    packs = []

    for idx, item in df.iterrows():
        packs.append(
            [Sku(item.ship_dim_x, item.ship_dim_y, item.ship_dim_z, item.weight, item.item_id, stack_on_top=False)
             for _ in range(int(item.vendor_pack_qty))])

    raw_totes = []
    t = deepcopy(tote)
    for ii, pack in enumerate(packs):
        if verbose and ii %500 ==0:
            print(f"===>{ii}/{len(packs)}")
        idx = 0
        for stack in t.getContents():
            for sku in stack.getSkus():
                sku.setIndex(idx)
                idx += 1
        for sku in pack:
            sku.setIndex(idx)
            idx += 1
        packer = TotePacker(pack, t, True)
        p = packer.pack()
        t = p.getBox()
        packed_skus = {sku.getIndex() for stack in t.getContents() for sku in stack.getSkus()}
        skus = [sku for sku in pack if sku.getIndex() not in packed_skus]

        if t.util2d >= cutoff or skus:
            raw_totes.append(p.getBox())
            t = deepcopy(tote)
            if skus:
                packs.append(skus)

    with open(f"./data/raw_totes_NJ51.pkl", 'wb') as f:
        pickle.dump(raw_totes, f)
    return raw_totes


def readskulist(filename:str) -> list:
    sku_list = pd.read_csv(filename)
    res = [[Sku(item["Each_dim_x"], item["Each_dim_y"], item["Each_dim_z"],
                 item["weight_per_unit"], name=int(item["upc"]), chem=False)
                 for _ in range(int(item["whpk_qty"]))]
           for index,item in sku_list.iterrows() for _ in range(int(item["case_qty"]))]
    return res

# partition a list to n near evenly parts for batch computing
def partition(lst, n):
    if n == 0 :
        return [lst]
    division = len(lst) / float(n)
    return [lst[int(round(division * i)): int(round(division * (i + 1)))] for i in range(n)]


