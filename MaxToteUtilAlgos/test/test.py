from TotePacker import TotePacker
from packmeV2 import PackMe
from sku_class import Sku
from box_class import Box

print("testing --> tote packer create sku stacks")
tp = TotePacker([], Box(width=25, length=17, height=16,max_weight=20))
skus = [Sku(4, 5, 6, 10)] * 5
stacks = tp.createSkuStacks(skus)




# def test_createSkuStacks():
print("testing --> tote packer create sku stacks")

skus = [Sku(4,5,2,1) for _ in range(12)]
a = skus[0].getSkus()
for i,sku in enumerate(skus):
    sku.setIndex(i)
tp = TotePacker(skus, Box(width=4, length=7, height=12))
p = tp.pack()

packed_skus = {sku.getIndex() for stack in p.getBox().getContents() for sku in stack.getSkus()}
skus = [sku for sku in skus if sku.getIndex() not in packed_skus]
if skus:
    packer2 = TotePacker(skus, p.getBox(), False)
    p = packer2.pack()

b = p.getBox()
b.draw3d()
print("complete")
# for i in b:
#     i.draw3d()