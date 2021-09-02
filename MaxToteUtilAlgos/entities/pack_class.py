'''
@author: Kaiwen Luo (k0l06rk)

this file holds the code for an pack class
aka, pack that will be diverted to each decanting station
'''

class Pack(object):

    def __init__(self, sku:list = None):
        self.index = 10000
        self.skus = sku


    def getSkus(self):
        return self.skus

    def getIndex(self):
        return self.index

    def setIndex(self, index: int):
        self.index = index
