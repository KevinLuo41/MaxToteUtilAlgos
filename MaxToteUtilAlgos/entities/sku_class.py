'''
@author: Rei Siew Hew Sam (rus003o)

this file holds the code for an sku class
aka, and item that will be packed

'''
class Sku(object):
    # listing a few constants
    W_AXIS = 0
    L_AXIS = 1
    H_AXIS = 2
    WLH,LWH,LHW,HLW,HWL,WHL = range(6)
    def __init__(self, width, length, height, weight, name='', chem=False, sort=True, stack_on_top=False):
        self.name = name
        if sort:
            self.width, self.length, self.height = sorted([width, length, height], reverse=True)
            self.orig_w, self.orig_l, self.orig_h = sorted([width, length, height], reverse=True)
        else:
            self.width, self.length, self.height = width, length, height
            self.orig_w, self.orig_l, self.orig_h = width, length, height


        self.weight = weight
        self.volume = length*height*width
        self.pos = [0,0,0]
        self.cur_rot = 0  #default to W,L,H
        self.chemical = chem
        self.index = 0
        self.stack_on_top = stack_on_top
        # consts


    def setIndex(self, idx):
        self.index = idx
    
    def getIndex(self) -> int:
        return self.index

    # unused here, but good for enumerating the different rotation types
    def rotationType(self):
        ROT_TYPES = {
                      0 : 'W,L,H',
                      1 : 'L,W,H',
                      2 : 'L,H,W',
                      3 : 'H,L,W',
                      4 : 'H,W,L',
                      5 : 'W,H,L'
                     }
        return ROT_TYPES[self.cur_rot]


    def getName(self):
        return self.name
    def getVol(self):
        return self.volume
    def getWeight(self):
        return self.weight
    def getChemical(self):
        return self.chemical
    def setChemical(self, val: bool):
        self.chemical = val

    def getDims(self): # maybe rename this
        dim = []
        cr = self.cur_rot
        w,l,h = self.orig_w, self.orig_l, self.orig_h
        if   (cr == self.WLH):
            dim = [w,l,h]
            self.width, self.length, self.height = w,l,h
        elif (cr == self.LWH):
            dim = [l,w,h]
            self.width, self.length, self.height = l,w,h
        elif (cr == self.LHW):
            dim = [l,h,w]
            self.width, self.length, self.height = l,h,w
        elif (cr == self.HLW):
            dim = [h,l,w]
            self.width, self.length, self.height = h,l,w
        elif (cr == self.HWL):
            dim = [h,w,l]
            self.width, self.length, self.height = h,w,l
        elif (cr == self.WHL):
            dim = [w,h,l]
            self.width, self.length, self.height = w,h,l
        else: dim = [-1,-1,-1] # should never be here
        return dim

    def getPos(self):
        return self.pos

    def modDimsFromRot(self,cr):
        self.modRot(cr)
        w,l,h = self.orig_w, self.orig_l, self.orig_h
        if   (cr == self.WLH):
            self.width, self.length, self.height = w,l,h
        elif (cr == self.LWH):
            self.width, self.length, self.height = l,w,h
        elif (cr == self.LHW):
            self.width, self.length, self.height = l,h,w
        elif (cr == self.HLW):
            self.width, self.length, self.height = h,l,w
        elif (cr == self.HWL):
            self.width, self.length, self.height = h,w,l
        elif (cr == self.WHL):
            self.width, self.length, self.height = w,h,l
        return [self.width, self.length, self.height]

    def modPos(self,pos):
        x,y,z = range(3)
        self.pos[x] = pos[x]
        self.pos[y] = pos[y]
        self.pos[z] = pos[z]

    def modRot(self,rot):
        self.cur_rot = rot

    def getW(self):
        return self.width

    def getL(self):
        return self.length

    def getH(self):
        return self.height

    def getRotation(self):
        return self.cur_rot

    # def getWeight(self):
    #     return self.weight

    # for internal class use only
    '''
    checks if the the cur_sku and another sku intersecs on a axis
    '''
    def _rectIntersect(self, sku2, axis):
        self_dims = self.getDims()
        sku2_dims = sku2.getDims()

        xmin1 = self.pos[axis]
        xmax1 = self.pos[axis] + self_dims[axis]
        xmin2 = sku2.pos[axis]
        xmax2 = sku2.pos[axis] + sku2_dims[axis]
        res1 = xmax1 > xmin2
        res2 = xmax2 > xmin1
        return res1 and res2

    '''
    check all the three different axis' to see if they dont insterect on all
    '''
    def intersect(self,sku2):
        res1 = self._rectIntersect(sku2,self.W_AXIS)
        res2 = self._rectIntersect(sku2,self.L_AXIS)
        res3 = self._rectIntersect(sku2,self.H_AXIS)
        return (res1 and res2 and res3)


    def __str__(self):
        return f'{self.name} ==> {(self.width,self.length,self.height)} @ {self.pos} weight: {self.weight}'



