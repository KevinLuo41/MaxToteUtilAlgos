'''
@author: Rei Siew Hew Sam (rus003o)

this file holds the code for the packme class
aka, the thing that does the packing into the item
# algorithm one in the appendix is the EP update algo

items have dimensions W x L X H
X direction --> Width
Y direction --> Length
Z direction --> Height

Extreme Points are refered to as EPs or xps
an extreme points is characterized by a list with 6 items:
    [x,y,z,w,l,h] --> where x,y,z is the coordinate of the xp
                  --> w,l,h are the dimensions of the residual space associated
                      to the extreme point

the tryAndScorePlacement function holds the merit function... given an item,
it chooses the optimal positional and rotational placement

'''
import sys
import math
import copy
import random # for the coloring of the items within the boxes
from MaxToteUtilAlgos.entities.sku_class import Sku
from MaxToteUtilAlgos.entities.box_class import Box
import vpython as vp # only used for the visualization
import time
import copy

LARGEST_BOX = "W45-L6"
BEEG_VAL = 999999
X_COORD, Y_COORD, Z_COORD, W_DIM, L_DIM, H_DIM = range(6)
SCORE_TYPES = 6

class PackMe(object):
    SLEEP = 1

    def __init__(self,draw=False):
        self.box = None
        self.skus = []
        self.unFitSkus = []
        self.finalEPs = []
        self.draw = draw
###
# getter and setter methods for the packme object
###
    def setBox(self,b):
        self.box = b

    def addSku(self,sku):
        self.skus.append(sku)

    def getBox(self):
        return self.box

    def getUnFit(self):
        return self.unFitSkus

    def getSkus(self):
        return self.skus

    def getFinalEPs(self):
        return self.finalEPs

    def clear(self):
        self.box = None
        self.skus = []
        self.unFitSkus = []
        self.finalEPs = []
############################################

    '''
    find the box that fits the first item in the skus list... which is the
    largest item... because of the way we sort in the pack() method
    '''
    def findBoxFit(self,sku):
        res = None
        sku_vol = sku.getVol()
        sku_dims = sorted([sku.getW(),sku.getL(),sku.getH()])
        #print('largest sku dims ------------------------------>',sku_dims)
        iterations = len(self.getBoxes())
        for i in range(iterations):
            if (len(self.boxes[i].getContents()) > 0): continue
            b = self.boxes[i]
            box_dims = sorted([b.getW(),b.getL(),b.getH()])
            box_vol = b.getVol()

            if sku_vol > box_vol:
                continue

            bad_box = False
            for sku_dim, box_dim in zip(sku_dims,box_dims):
                if sku_dim > box_dim:
                    bad_box = True
                    break

            if bad_box == True:
                continue

            else:
#                b.clearBox()
                res = self.boxes[i]

        return res


    '''
    returns the next biggest box w.r.t a given box (box1) which is supplied
    in the parameters
    '''
    def getBiggerBoxThan(self,box1):
        res = None
        iterations = len(self.getBoxes())
        for i in range(iterations):
            box2 = self.boxes[i]
            if (box2.getVol() > box1.getVol()):
                res = box2

        return res


    '''
    takes the 0th index of skus and thne adds it to the unfit skus list
    an unfit sku is a sku that cannot be packed into the box cuz its too big
    or weighs too much
    '''
    def unFitSku(self):
        if (len(self.skus) == 0):
            return
        else:
            self.unFitSkus.append(self.skus[0])
            self.skus = self.skus[1:]

###############################################################################
###############################################################################
#########################_____STUF FOR RESIDUAL SPACE____######################
###############################################################################

    '''
    used to project towards empty space for calcutating Residual Space
    returns true for a given axis if we can project outwards toward
    "empty" space. (the direction where we have not packed stuff yet)
    cpp    --> py
    length --> width      3
    depth  --> length     4
    height --> height     5
    '''
    def _canTakeProj_b(self, i, k, axis): # backwards
        Xy, Xz, Yz, Yx, Zx, Zy = range(6)
        x, y, z = range(3)
        res = False
        if (axis == Xy):
            return ((k.pos[y] + k.getL() <= i.pos[y])
                and (i.pos[x]            <= k.pos[x] + k.getW())
                and (k.pos[x] + k.getW() <  i.pos[x] + i.getW())
                and (i.pos[z]            <= k.pos[z])
                and (k.pos[z]            <  i.pos[z] + i.getH()))
        elif (axis == Xz):
            return ((k.pos[z] + k.getH() <= i.pos[z])
                and (i.pos[x]            <= k.pos[x] + k.getW())
                and (k.pos[x] + k.getW() <  i.pos[x] + i.getW())
                and (i.pos[y]            <= k.pos[y])
                and (k.pos[y]            <  i.pos[y] + i.getL()))
        elif (axis == Yz):
            return ((k.pos[z] + k.getH() <= i.pos[z])
                and (i.pos[y]            <= k.pos[y] + k.getL())
                and (k.pos[y] + k.getL() < i.pos[y] + i.getL())
                and (i.pos[x]            <= k.pos[x])
                and (k.pos[x]            <  i.pos[x] + i.getW()))
        elif (axis == Yx):
            return ((k.pos[x] + k.getW() <= i.pos[x])
                and (i.pos[y]            <= k.pos[y] + k.getL())
                and (k.pos[y] + k.getL() < i.pos[y] + i.getL())
                and (i.pos[z]            <= k.pos[z])
                and (k.pos[z]            <  i.pos[z] + i.getH()))
        elif (axis == Zx):
            return ((k.pos[x] + k.getW() <= i.pos[x])
                and (i.pos[z]            <= k.pos[z] + k.getH())
                and (k.pos[z] + k.getH() <  i.pos[z] + i.getH())
                and (i.pos[y]            <= k.pos[y])
                and (k.pos[y]            <  i.pos[y] + i.getL()))
        elif (axis == Zy):
            return ((k.pos[y] + k.getL() <= i.pos[y])
                and (i.pos[z]            <= k.pos[z] + k.getH())
                and (k.pos[z] + k.getH() <  i.pos[z] + i.getH())
                and (i.pos[x]            <= k.pos[x])
                and (k.pos[x]            <  i.pos[x] + i.getW()))

        return res

    '''
    update the minBound array which is used for calculating the residual
    space values for each of the EPs (how far out each XP can project outwards.
    which is the way we calculate the W,D,H of those EPs... RS = W*D*H of a
    given EP
    '''
    def _updateMinBound(self, it, minBound, neweps):
        x, y, z, w, l, h = range(6)
        Xy, Xz, Yz, Yx, Zx, Zy = range(6)
        virt_item = Sku(0, 0, 0, 0, 'virtual_item') # w, h, l, weight

        for i in range(6):
            virt_item.modPos([neweps[i][x],neweps[i][y],neweps[i][z]])

            if (self._canTakeProj_b(it, virt_item, Yx) and
                self._canTakeProj_b(it, virt_item, Zx)):
                minBound[i][x] = min(it.pos[x], minBound[i][x])

            if (self._canTakeProj_b(it, virt_item, Zy) and
                self._canTakeProj_b(it, virt_item, Xy)):
                minBound[i][y] = min(it.pos[y], minBound[i][y])

            if (self._canTakeProj_b(it, virt_item, Xz) and
                self._canTakeProj_b(it, virt_item, Yz)):
                minBound[i][z] = min(it.pos[z], minBound[i][z])
        #for zz in minBound:
        #    print("minbound",zz)
        return minBound


    '''
    update the Residual Space values of each of the extreme points
    '''
    def _updateRSs(self, packed, kt, minBound, neweps):
        x, y, z, w, l, h = range(6)
        for it in packed:
            minBound = self._updateMinBound(it, minBound, neweps)

        for i in range(6):
            neweps[i][w] = minBound[i][x] - neweps[i][x]
            neweps[i][l] = minBound[i][y] - neweps[i][y]
            neweps[i][h] = minBound[i][z] - neweps[i][z]

        return neweps

    '''
    minBound: track 6 projection xp residual space as
    from max x-right y-front z-top to min x-left y-behind z-bottom
    '''
    def _initMinBound(self,b):
        x, y, z = range(3)
        minBound = [[0]*3 for _ in range(6)]
        for i in range(6):
            minBound[i][x] = b.getW()
            minBound[i][y] = b.getL()
            minBound[i][z] = b.getH()
        return minBound

###############################################################################
#########################_____STUFF FOR EXTREME POINTS____#####################
    '''
    manually insert the extreme points and their residual space coords for the
    first item insertion
    '''
    def _initEPs(self,b,k):
        x,y,z,w,l,h = range(6)
        EPs = [[0]*6 for _ in range(3)]
        EPs[0][x], EPs[0][y], EPs[0][z] = k.getW(), 0, 0
        EPs[0][w], EPs[0][l], EPs[0][h] = b.getW() - k.getW(), b.getL(), b.getH()

        EPs[1][x], EPs[1][y], EPs[1][z] = 0, k.getL(), 0
        EPs[1][w], EPs[1][l], EPs[1][h] = b.getW(), b.getL() - k.getL(), b.getH()

        EPs[2][x], EPs[2][y], EPs[2][z] = 0, 0, k.getH()
        EPs[2][w], EPs[2][l], EPs[2][h] = b.getW(), b.getL(), b.getH() - k.getH()

        return EPs
    '''
    used to project coords from new item 'k' towards the items already packed
    in the box to find new extreme points
    cpp    --> py
    length --> width      3
    depth  --> length     4
    height --> height     5
    '''
    def _canTakeProj_f(self, k, i, axis): # forward
        Xy, Xz, Yz, Yx, Zx, Zy = range(6)
        x, y, z = range(3)
        res = False
        if (axis == Xy):
            return ((i.pos[y] + i.getL() <= k.pos[y])
                and (i.pos[x]            <= k.pos[x] + k.getW())
                and (k.pos[x] + k.getW() <  i.pos[x] + i.getW())
                and (i.pos[z]            <= k.pos[z])
                and (k.pos[z]            <  i.pos[z] + i.getH()))
        elif (axis == Xz):
            return ((i.pos[z] + i.getH() <= k.pos[z])
                and (i.pos[x]            <= k.pos[x] + k.getW())
                and (k.pos[x] + k.getW() <  i.pos[x] + i.getW())
                and (i.pos[y]            <= k.pos[y])
                and (k.pos[y]            <  i.pos[y] + i.getL()))
        elif (axis == Yz):
            return ((i.pos[z] + i.getH() <= k.pos[z])
                and (i.pos[y]            <= k.pos[y] + k.getL())
                and (k.pos[y] + k.getH() <  i.pos[y] + i.getL())
                and (i.pos[x]            <= k.pos[x])
                and (k.pos[x]            <  i.pos[x] + i.getW()))
        elif (axis == Yx):
            return ((i.pos[x] + i.getW() <= k.pos[x])
                and (i.pos[y]            <= k.pos[y] + k.getL())
                and (k.pos[y] + k.getL() <  i.pos[y] + i.getL())
                and (i.pos[z]            <= k.pos[z])
                and (k.pos[z]            <  i.pos[z] + i.getH()))
        elif (axis == Zx):
            return ((i.pos[x] + i.getW() <= k.pos[x])
                and (i.pos[z]            <= k.pos[z] + k.getH())
                and (k.pos[z] + k.getH() <  i.pos[z] + i.getH())
                and (i.pos[y]            <= k.pos[y])
                and (k.pos[y]            <  i.pos[y] + i.getL()))
        elif (axis == Zy):
            return ((i.pos[y] + i.getL() <= k.pos[y])
                and (i.pos[z]            <= k.pos[z] + k.getH())
                and (k.pos[z] + k.getH() <  i.pos[z] + i.getH())
                and (i.pos[x]            <= k.pos[x])
                and (k.pos[x]            <  i.pos[x] + i.getW()))


    '''
    with new item "k" placed into the box, remove the extreme points that are
    now covered by the item 'k'
    '''
    def _removeCoveredExtremePoints(self, k, EPs): # in the java version. its a method
        toDel = []
        x, y, z, w, l, h = range(6)

        # first find the extreme points to remove
        for xp in EPs:
            if (k.pos[x] <= xp[x] and xp[x] < k.pos[x] + k.getW() and
                k.pos[y] <= xp[y] and xp[y] < k.pos[y] + k.getL() and
                k.pos[z] <= xp[z] and xp[z] < k.pos[z] + k.getH()):
                toDel.append(xp)

        # remove the extreme points that are covered by item k
        for xp in toDel:
            if (xp in EPs):
                #print("removing RCEP", xp)
                EPs.remove(xp)

        #update the residual space of each of the extreme points w.r.t item k
        for xp in EPs:
            if (xp[x] <= k.pos[x] and xp[y] >= k.pos[y] and
                xp[y] <  k.pos[y] + k.getL() and
                xp[z] >= k.pos[z] and xp[z] <  k.pos[z] + k.getH()):
                xp[w] = min(xp[w], k.pos[x] - xp[x])


            if (xp[y] <= k.pos[y] and xp[z] >= k.pos[z] and
                xp[z] <  k.pos[z] + k.getH() and
                xp[x] >= k.pos[x] and xp[x] <  k.pos[x] + k.getW()):
                xp[l] = min(xp[l], k.pos[y] - xp[y])


            if (xp[z] <= k.pos[z] and xp[x] >= k.pos[x] and
                xp[x] <  k.pos[x] + k.getW() and xp[y] >= k.pos[y] and
                xp[y] <  k.pos[y] + k.getL()):
                xp[h] = min(xp[h], k.pos[z] - xp[z])

        return EPs


    '''
    this func removes:
        1) non-dominant extreme points
        2) zero residual space extreme points
    non-dominant extreme points are points that are wholy contained within
    another extreme point's rs --> not needed and will messup calculation
    '''
    def _purifyEPs(self,EPs):
        x, y, z, w, l, h = range(6)
        zeroRS_to_remove = [xp for xp in EPs if(xp[w]==0 or xp[l]==0 or xp[h]==0)]
        for xp in zeroRS_to_remove:
            #print("removing PUR1",xp)
            EPs.remove(xp)
        dominatedEPs_to_remove = []
        iters = len(EPs)
        for i in range(iters):
            for j in range(iters):
                if (i == j): continue
                elif ((EPs[i][x] <= EPs[j][x] and EPs[i][y] <= EPs[j][y] and
                      EPs[i][z] <= EPs[j][z] and EPs[i][w] >= EPs[j][w] and
                      EPs[i][l] >= EPs[j][l] and EPs[i][h] >= EPs[j][h])
                      or (EPs[i][x] == EPs[j][x] and EPs[i][y] == EPs[j][y]
                          and EPs[i][z] < EPs[j][z])):
                    dominatedEPs_to_remove.append(EPs[j])
        for xp in dominatedEPs_to_remove:
            if (xp in EPs):
                EPs.remove(xp)

        return EPs

    '''
    in paper, dims are ordered --> W x D x H
    here we they are ordered ----> W x L x H
    this func updates the EPs with a newly placed item "k"


    In java implementation --> splitting the updating of EP and maxbound to two
    functions
    '''
    def _updateEPs(self, b, packed, k, give_max_bnd=False):
        x, y, z, w, l, h = range(6)
        Xy, Xz, Yz, Yx, Zx, Zy = range(6)

        neweps = [[None]*6 for _ in range(6)]
        minBound = self._initMinBound(b)
        maxBound = [0]*6
        for i in packed:
            i_pos = i.getPos()
            k_pos = k.getPos()
            if (self._canTakeProj_f(k,i,Xy)and(i_pos[y] + i.getL() > maxBound[Xy])): ###  xY
                maxBound[Xy] = i_pos[y] + i.getL()
            neweps[Xy] = [k_pos[x]+k.getW(), maxBound[Xy], k_pos[z],0,0,0]

            if (self._canTakeProj_f(k,i,Xz)and(i_pos[z]+i.getH() > maxBound[Xz])):   #### xZ
                maxBound[Xz] = i_pos[z] + i.getH()
            neweps[Xz] = [k_pos[x]+k.getW(),k_pos[y],maxBound[Xz],0,0,0]

            if (self._canTakeProj_f(k,i,Yz)and(i_pos[z] + i.getH() > maxBound[Yz])): ### yZ
                maxBound[Yz] = i_pos[z] + i.getH()
            neweps[Yz] = [k_pos[x], k_pos[y]+k.getL(), maxBound[Yz],0,0,0]

            if (self._canTakeProj_f(k,i,Yx)and(i_pos[x] + i.getW() > maxBound[Yx])):  ### yX
                maxBound[Yx] = i_pos[x] + i.getW()
            neweps[Yx] = [maxBound[Yx], k_pos[y]+k.getL(), k_pos[z],0,0,0]

            if (self._canTakeProj_f(k,i,Zx)and(i_pos[x]+i.getW() > maxBound[Zx])):     ## zX
                maxBound[Zx] = i_pos[x] + i.getW()
            neweps[Zx] = [maxBound[Zx],k_pos[y],k_pos[z]+k.getH(),0,0,0]

            if (self._canTakeProj_f(k,i,Zy)and(i_pos[y]+i.getL() > maxBound[Zy])):    ## zY
                maxBound[Zy] = i_pos[y] + i.getL()
            neweps[Zy] = [k_pos[x], maxBound[Zy], k_pos[z]+k.getH(),0,0,0]

        neweps = self._updateRSs(packed, k, minBound, neweps)# update the rs for each xp

        if (give_max_bnd):
            return neweps, maxBound
        else:
            return neweps

    '''
    this function is called when:
    if fitted == True
    when we have found the optimal position, we add the newly created EPs to
    the original EP list and then remove the EPs that are now covered or
    non-dominant

    also called when finding entropy score for a given rot/pos for temp EPs
    '''
    def _mergeEPs(self, neweps, EPs):
        x, y, z = range(3)
        # merge new xps into the EP list
        for xp in neweps:
            if (xp not in EPs):
                EPs.append(xp)
        EPs = self._purifyEPs(EPs)      # remove RS == 0 and non-dominant xps
        # sorting by z first, then by y then x
        EPs.sort(key=lambda i: (i[z],i[y],i[x]))
        return EPs

###############################################################################
###############################################################################

    '''
    returns a list of possible rotations given a sku and extreme points
    removes redundant checks impossible placements
    '''
    def _rotationChecks(self,sku,xp):
        original_rotation = sku.getRotation()
        x,y,z,w,l,h = range(6)
        all_dims = []
        ok_rots = []
        for rot in sku.getAllowedRotations(): # rotate based on what is allowed
            sku.modRot(rot)
            dims = sku.getDims() # when converting to java make sure to use the right method
            if (dims not in all_dims): # make sure each rotation is unique
                if (dims[x] <= xp[w] and dims[y] <= xp[l] and dims[z] <= xp[h]):
                    all_dims.append(dims)
                    ok_rots.append(rot)
        sku.modRot(original_rotation)
        return ok_rots


    '''
    entropy is great when the "goodness of fit" for each of the positions is
    uniform... low entropy is when the each of the RS's are the least uniform
    '''
    def _scoreEntropy(self, test_neweps, EPs):
        x,y,z,w,l,h = range(6)
        test_EPs = self._mergeEPs(test_neweps, EPs)
        rs = [i[w]*i[l]*i[h] for i in test_EPs]
        rs_sum = sum(rs)
        rs = [i/rs_sum for i in rs]

        # entropy calc
        cur_entropy = 0
        for elem in rs:
            cur_entropy += elem * math.log(elem)
        cur_entropy = -cur_entropy

        return cur_entropy

    def scoreType(self, cur_fill, best_fill, cur_lim, best_lim, sType):
        if sType == 0: # X --> Y --> Z
            return ((cur_fill < best_fill)
                    or (cur_fill == best_fill and cur_lim[X_COORD] < best_lim[X_COORD])
                    or (cur_fill == best_fill and cur_lim[X_COORD] == best_lim[X_COORD]
                                              and cur_lim[Y_COORD] < best_lim[Y_COORD])
                    or (cur_fill == best_fill and cur_lim[X_COORD] == best_lim[X_COORD]
                                              and cur_lim[Y_COORD] == best_lim[Y_COORD]
                                              and cur_lim[Z_COORD] < best_lim[Z_COORD]))
        elif sType == 1: # Y --> X --> Z
            return ((cur_fill < best_fill)
                    or (cur_fill == best_fill and cur_lim[Y_COORD] < best_lim[Y_COORD])
                    or (cur_fill == best_fill and cur_lim[Y_COORD] == best_lim[Y_COORD]
                                              and cur_lim[X_COORD] < best_lim[X_COORD])
                    or (cur_fill == best_fill and cur_lim[Y_COORD] == best_lim[Y_COORD]
                                              and cur_lim[X_COORD] == best_lim[X_COORD]
                                              and cur_lim[Z_COORD] < best_lim[Z_COORD]))
        elif sType == 2: # Y --> Z --> X
            return ((cur_fill < best_fill)
                    or (cur_fill == best_fill and cur_lim[Y_COORD] < best_lim[Y_COORD])
                    or (cur_fill == best_fill and cur_lim[Y_COORD] == best_lim[Y_COORD]
                                              and cur_lim[Z_COORD] < best_lim[Z_COORD])
                    or (cur_fill == best_fill and cur_lim[Y_COORD] == best_lim[Y_COORD]
                                              and cur_lim[Z_COORD] == best_lim[Z_COORD]
                                              and cur_lim[X_COORD] < best_lim[X_COORD]))
        elif sType == 3: # Z --> Y --> X
            return ((cur_fill < best_fill)
                    or (cur_fill == best_fill and cur_lim[Z_COORD] < best_lim[Z_COORD])
                    or (cur_fill == best_fill and cur_lim[Z_COORD] == best_lim[Z_COORD]
                                              and cur_lim[Y_COORD] < best_lim[Y_COORD])
                    or (cur_fill == best_fill and cur_lim[Z_COORD] == best_lim[Z_COORD]
                                              and cur_lim[Y_COORD] == best_lim[Y_COORD]
                                              and cur_lim[X_COORD] < best_lim[X_COORD]))
        elif sType == 4: # Z --> X --> Y
            return ((cur_fill < best_fill)
                    or (cur_fill == best_fill and cur_lim[Z_COORD] < best_lim[Z_COORD])
                    or (cur_fill == best_fill and cur_lim[Z_COORD] == best_lim[Z_COORD]
                                              and cur_lim[X_COORD] < best_lim[X_COORD])
                    or (cur_fill == best_fill and cur_lim[Z_COORD] == best_lim[Z_COORD]
                                              and cur_lim[X_COORD] == best_lim[X_COORD]
                                              and cur_lim[Y_COORD] < best_lim[Y_COORD]))
        elif sType == 5: # X --> Z --> Y
            return ((cur_fill < best_fill)
                    or (cur_fill == best_fill and cur_lim[X_COORD] < best_lim[X_COORD])
                    or (cur_fill == best_fill and cur_lim[X_COORD] == best_lim[X_COORD]
                                              and cur_lim[Z_COORD] < best_lim[Z_COORD])
                    or (cur_fill == best_fill and cur_lim[X_COORD] == best_lim[X_COORD]
                                              and cur_lim[Z_COORD] == best_lim[Z_COORD]
                                              and cur_lim[Y_COORD] < best_lim[Y_COORD]))
        else:
            cur_lim.sort()
            return ((cur_fill < best_fill) # smallest to largest projection priority
                    or (cur_fill == best_fill and cur_lim[X_COORD] < best_lim[X_COORD])
                    or (cur_fill == best_fill and cur_lim[X_COORD] == best_lim[X_COORD]
                                              and cur_lim[Y_COORD] < best_lim[Y_COORD])
                    or (cur_fill == best_fill and cur_lim[X_COORD] == best_lim[X_COORD]
                                              and cur_lim[Y_COORD] == best_lim[Y_COORD]
                                              and cur_lim[Z_COORD] < best_lim[Z_COORD]))
    '''
    test the placement of sku into the box at all the EPs with each of the 6
    possible rotations... then return the position and rotation with the best
    residual space score!
    '''
    def _tryAndScorePlacement(self, EPs, sku, b, sType):
        if (b.overweightCheck(sku) == False): return [None, None, None], 0
        itemVol = sku.getVol()
        best_rot = 0
        best_pos = [ None, None, None ]
        cur_lim = [ 0,0,0 ]
        best_lim = [ BEEG_VAL, BEEG_VAL, BEEG_VAL ]
        best_fill = 1
        cur_fill = 0
        for xp in EPs:
            # skip EPs that are not touching floor if sku is unstackable
            # print(sku.__class__)
            # print(Sku)
            if (isinstance(sku,Sku) or (not sku.getCanStackOnTop() and xp[Z_COORD] > 0)): continue
            cur_xp = xp
            cur_pos = [ cur_xp[X_COORD], cur_xp[Y_COORD], cur_xp[Z_COORD] ]
            cur_residual = cur_xp[W_DIM] * cur_xp[L_DIM] * cur_xp[H_DIM]
            ok_rots = self._rotationChecks(sku, xp)
            for cur_rot in ok_rots: 
                if (cur_rot < 0): continue 
                sku.modDimsFromRot(cur_rot)
                if (b.putSku(sku, cur_pos, cur_rot, True)): 
                    cur_fill = itemVol / cur_residual
                    cur_lim[X_COORD] = cur_xp[W_DIM] - sku.getW()
                    cur_lim[Y_COORD] = cur_xp[L_DIM] - sku.getL()
                    cur_lim[Z_COORD] = cur_xp[H_DIM] - sku.getH()
                    if (self.scoreType(cur_fill, best_fill, cur_lim, best_lim, sType)):
                        best_rot = cur_rot
                        best_fill = cur_fill
                        best_pos = xp[:3]
            sku.modDimsFromRot(0)
        sku.modDimsFromRot(best_rot)
        return best_pos, best_rot

    '''
    packs the largest item first then calls tryAndScorePlacement which finds the best
    sku @ the best extreme point to pack @...
    '''
    def _packToBox(self, b, skus,old_EPs, sType):
        draw_boxes = []
        draw_neweps = [None]*6
        x, y, z, w, l, h = range(6)
        alt_box = None
        unpacked = []
        # place the first box at point 0,0,0 with no rotation
        if(len(old_EPs) == 0): # initialize the EPs
            EPs = [[0,0,0,b.getW(),b.getL(),b.getH()]]
            best_pos, best_rot = self._tryAndScorePlacement(EPs,skus[0],b, sType)
            skus[0].modDimsFromRot(best_rot)
            #######################################################################
            if self.draw:
                sku = skus[0]
                draw_boxes.append(vp.box(pos=vp.vector(sku.pos[0]+sku.width/2,sku.pos[1]+sku.length/2,sku.pos[2]+sku.height/2),
                                         size=vp.vector(sku.width,sku.length,sku.height),
                                         color=vp.vector(random.uniform(0,1),random.uniform(0,1),random.uniform(0,1))))
            #######################################################################
            #print("first sku pos and rot",best_pos,best_rot)
            fit = b.putSku(skus[0],best_pos,best_rot)
            if (fit == False):
                return skus
            else:
                EPs = self._initEPs(b,skus[0]) # creates a single xp at 0,0,0 and wlh of the box itself
            skus = skus[1:] # first is packed so skip it
        else: # if itemsExist in tote already go straight to regular packing
            EPs = copy.deepcopy(old_EPs)
            if self.draw:
                for sku in b.getContents():
                    draw_boxes.append(vp.box(pos=vp.vector(sku.pos[0]+sku.width/2,sku.pos[1]+sku.length/2,sku.pos[2]+sku.height/2),
                                         size=vp.vector(sku.width,sku.length,sku.height),
                                         color=vp.vector(random.uniform(0,1),random.uniform(0,1),random.uniform(0,1))))
        max_iter = len(skus)
        self.finalEPs=EPs
################################################################################
        if self.draw:
            container = vp.box(pos=vp.vector(b.width/2,b.length/2,b.height/2),size=vp.vector(b.width,b.length,b.height),
                               color=vp.color.white,opacity=0.5)
            #time.sleep(3)
################################################################################
        for sku_ind,sku in enumerate(skus):
            #print('FITTING ---------->',sku)
            fitted = False

            XX = copy.deepcopy(EPs)
            best_pos, best_rot = self._tryAndScorePlacement(XX, sku, b, sType) # try all the EPs and return best one
            if (None not in best_pos):
                fitted = True
                # -----------UPDATE SKU----------------------------------------
                sku.modRot(best_rot)
                sku.modPos(best_pos)
                sku.modDimsFromRot(best_rot)

            ##---------------------UPDATING EPS---------------------------------

                EPs = self._removeCoveredExtremePoints(sku,EPs)#remove EPs that are within the new box Kt
                neweps = self._updateEPs(b, b.getContents(), sku)

                b.putSku(sku, best_pos, best_rot, try_fit=False)
                EPs = self._mergeEPs(neweps, EPs)
                self.finalEPs = copy.deepcopy(EPs)
            ##-----------------------------------------------------------------
                ##############################################################
                if self.draw:
                    #time.sleep(self.SLEEP)
                    draw_boxes.append(vp.box(pos=vp.vector(sku.pos[0]+sku.width/2,sku.pos[1]+sku.length/2,sku.pos[2]+sku.height/2),
                                         size=vp.vector(sku.width,sku.length,sku.height),
                                         color=vp.vector(random.uniform(0,1),random.uniform(0,1),random.uniform(0,1))))

                    img_eps = [None]*len(EPs)
                    for num,xp in enumerate(EPs):
                        img_eps[num] = vp.sphere(pos=vp.vector(xp[x],xp[y],xp[z]),
                                                 radius=.7,
                                                 color=vp.color.red,opacity=0.9)
                    #time.sleep(self.SLEEP)
                    for num,xp in enumerate(neweps):
                        draw_neweps[num] = vp.sphere(pos=vp.vector(xp[x],xp[y],xp[z]),
                                                 radius=.7,
                                                 color=vp.color.yellow,opacity=0.9)
                    #time.sleep(self.SLEEP)
                    img_fin = [None]*len(EPs)
                    for num,xp in enumerate(EPs):
                        img_fin[num] = vp.sphere(pos=vp.vector(xp[x],xp[y],xp[z]),
                                                 radius=.7,
                                                 color=vp.color.green,opacity=0.9)
                    img_new = []
                    img_eps = []
                    #time.sleep(self.SLEEP)
                ##############################################################
            if (not fitted):
                unpacked.append(sku)
                # once we hit a box that doesnt pack --> give up...unless...
                # dont give up if we are on the last boxsize... dont give up!
                #
                # this can be modified to never give up packing even if one item
                # does not fit... this will impact performace but might improve
                # packing on splits ... ie less than 2% of the orders
                #if (b.getName() != LARGEST_BOX):  #,36,21,18,50
                #    unpacked = skus[sku_ind:]
                #    return unpacked
        return unpacked

    '''
    main func in this class... sorts boxes and skus and then calls the
    packToBox func which does the actual packing w/ extreme point
    '''
    def pack(self,EPs):
        if (len(self.getSkus()) == 0):
            #print('empty sku list')
            return -1
        # order by Volume... then order by height
        #self.skus.sort(key=lambda x: (x.volume,x.height),reverse=True)
        if (self.getBox == None): return None

        item_copies = [copy.deepcopy(self.skus) for _ in range(SCORE_TYPES)]
        box_copies = [copy.deepcopy(self.getBox()) for _ in range(SCORE_TYPES)]
        ep_copies = [copy.deepcopy(EPs) for _ in range(SCORE_TYPES)]
        curUnfit = []
        minUnfit = len(self.getSkus())
        bestUnfit = None
        bestBoxIndex = 0
        for i in range(SCORE_TYPES):
            curUnfit = self._packToBox(box_copies[i], item_copies[i], ep_copies[i], i)
            ep_copies[i] = copy.deepcopy(self.finalEPs)
            if (len(curUnfit) < minUnfit):
                minUnfit = len(curUnfit)
                bestBoxIndex = i
                bestUnfit = curUnfit
        self.finalEPs = ep_copies[bestBoxIndex]        
        self.box = box_copies[bestBoxIndex]
        if (bestUnfit == None): self.unFitSkus = curUnfit
        else: self.unFitSkus = bestUnfit
        return None
