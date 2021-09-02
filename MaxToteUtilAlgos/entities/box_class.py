'''
@author: Rei Siew Hew Sam (rus003o)

this file holds the code for an box
aka, the thing that holds the skus. Comment to test commit

'''
import vpython as vp
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
class Box(object):

    def __init__(self, width, length, height, name=0,max_weight=50, rect=None):
        self.contents = []
        self.width, self.length, self.height = width, length, height
        self.max_weight = max_weight
        self.name = name
        self.volume = width*height*length
        self.dim = width*length
        self.total_weight = 0
        self.chemical = False
        self.rect = rect
        self.EPs = []

        self.util3d = sum(s.getVol() for s in self.contents) / self.volume
        self.util2d = sum(s.width*s.length for s in self.contents if s.pos[-1] == 0 ) / (self.dim)

    '''
    getter and setter methods for the box class
    '''
    def getW(self) -> float:
        return self.width

    def getL(self) -> float:
        return self.length

    def getH(self) -> float:
        return self.height

    def getContents(self) -> list:
        return self.contents

    def getVol(self) -> float:
        return self.volume

    def getDim(self)->float:
        return self.dim

    def getName(self):
        return self.name

    def setName(self, id:int):
        self.name = id

    def clearBox(self):
        self.contents = []
    
    def getChemical(self) -> bool:
        return self.chemical

    def getUtilization(self) -> list:
        self.util3d = sum(s.getVol() for s in self.contents) / self.volume
        if self.rect:
            pass
        else:
            self.util2d = sum(s.width*s.length for s in self.contents if s.pos[-1] == 0 ) / self.dim
        return [self.util3d, self.util2d]

    def setChemical(self, val: bool):
        self.chemical =  val

    def getEPs(self):
        return self.EPs
    
    def setEPs(self, xps):
        self.EPs = xps
    ##############################################

    # return true if ok weight
    def overweightCheck(self,sku):
        if (self.total_weight + sku.getWeight() > self.max_weight):
            return False
        return True

    '''
    place the sku inside the box and see if it intersects with any other sku
    '''
    def putSku(self, sku, pos, rot=0, try_fit=False):
        x, y, z = range(3)
        fit = False
        if (rot > 6 or rot < 0 or None in pos): return fit
        sku.modPos(pos)
        sku.modRot(rot)
        dims = sku.getDims()
        #print(f"dims = {dims}, pos = {pos}, box = {self.width} {self.length} {self.height}")
        if ((self.width < pos[x]+dims[x]) or (self.length < pos[y]+dims[y])
            or (self.height < pos[z]+dims[z])):
            fit = False

        else: fit = True

        for i in range(len(self.contents)):
            item = self.contents[i]
            if (item.intersect(sku)):
                fit = False
                break

        if (fit == True and try_fit == False):
            self.total_weight += sku.weight
            self.contents.append(sku)
            self.getUtilization()

        return fit # or break

    def draw3d(self):
        if self.contents:
            if isinstance(self.contents[0],Box):
                skus = [sku for stack in self.contents for sku in stack.getSkus()]
            else:
                skus = self.contents
        else:
            return

        vp.canvas()
        vp.box(pos=vp.vector(self.width / 2, self.length / 2, self.height / 2), size=vp.vector(self.width, self.length, self.height),
               color=vp.color.white, opacity=0.5)
        draw_boxes = []
        for sku in skus:
            draw_boxes.append(vp.box(
                pos=vp.vector(sku.pos[0] + sku.width / 2, sku.pos[1] + sku.length / 2, sku.pos[2] + sku.height / 2),
                size=vp.vector(sku.width, sku.length, sku.height),
                color=vp.vector(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))))

    def draw2d(self):
        for index, abin in enumerate(self.rect):
            bw, bh = abin.width, abin.height
            # print('bin', bw, bh, "nr of rectangles in bin", len(abin))

            fig = plt.figure()
            ax = fig.add_subplot(111, aspect='equal')
            for rect in abin:
                x, y, w, h = rect.x, rect.y, rect.width, rect.height
                plt.axis([0, bw, 0, bh])
                # print('rectangle', w,h)
                patch = patches.Rectangle(
                    (x, y),  # (x,y)
                    w,  # width
                    h,  # height
                    facecolor="#00ffff",
                    edgecolor="black",
                    linewidth=3
                )
                ax.add_patch(patch)
                rx, ry = patch.get_xy()
                cx = rx + patch.get_width() / 2.0
                cy = ry + patch.get_height() / 2.0

                ax.annotate(f'w:{w}\nh:{h}', (cx, cy), color='b', weight='bold',
                            fontsize=4, ha='center', va='center')

            plt.show()

    def __str__(self):
        return f'{self.name} ==> {(self.width, self.length, self.height)}'


