from packmeV2 import PackMe
from box_class import Box
from sku_class import Sku
import random as r
from copy import copy, deepcopy

print("HI")
skus = []
items = [
    [11.5,1.2,1.2],
    [3.8,8.9,1.5],
    [15.9,8.7,3.6],
    [6.3,6.3,2.6]
]


for item in items:
    for _ in range(2):
        new_object = Sku(item[0],item[1],item[2],0,"new_object")
        skus.append(new_object)

r.seed(1)
# skus = []

# for i in range(1):
#     # s = Sku(r.randint(1, 20), r.randint(1, 15), r.randint(1, 10), 40, name = 'sku'+str(i))
#     s = Sku(12.68,9,10, 1, name='sku' + str(i))
#     for j in range(3):
#         ss = deepcopy(s)
#         ss.setIndex(str(i)+"id"+str(j))
#         skus.append(ss)

tote = Box(25.6, 17.7, 12.8, "id", 99999)

eps = []

for sku in skus:
    p = PackMe(draw=False)
    p.setBox(tote)
    p.addSku(sku)
    p.pack(eps)
    eps = deepcopy(p.finalEPs)
    print(eps)
    p.skus=[]
    tote = p.getBox()
# tote.putSku(skus[0],())
zz = p.getBox()
zz.draw3d()
for sku in zz.getContents():
    print(sku)
print("UNFIT SKUS",len(p.getUnFit()))

print("END")