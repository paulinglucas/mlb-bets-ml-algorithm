from enum import IntEnum
from math import floor

class BatterStat(IntEnum):
    AB = 2
    R = 3
    H = 4
    RBI = 5
    BB = 6
    K = 7
    AVG = 9
    OPS = 10

class PitcherStat(IntEnum):
    IP = 1
    H = 2
    R = 3
    ER = 4
    BB = 5
    K = 6
    HR = 7
    ERA = 8

class Batter:
    def __init__(self, name, team, GP=0, AB=0, R=0, H=0, RBI=0, BB=0, K=0, HR=0, AVG=0.0, OBP=0.0, SLG=0.0, OPS=0.0):
        self.name = name
        self.team = team
        self.GP = GP
        self.AB = AB
        self.R = R
        self.H = H
        self.RBI = RBI
        self. BB = BB
        self. K = K
        self.HR = HR
        self.AVG = AVG
        self.OBP = OBP
        self. SLG = SLG
        self.OPS = OPS
        self.gmpks = []
        self.dict = {}

    def __str__(self):
        return "Name: " + self.name + "; Team: " + self.team

    def getTeam(self):
        return self.team

    def setTeam(self, newTeam):
        self.team = newTeam

    def getGP(self):
        return self.GP

    def playedGame(self):
        self.GP += 1

    def getAB(self):
        return self.AB

    def addAB(self, newAB):
        self.AB += newAB

    def getR(self):
        return self.R

    def addR(self, newR):
        self.R += newR

    def getH(self):
        return self.H

    def addH(self, newH):
        self.H += newH

    def getRBI(self):
        return self.RBI

    def addRBI(self, newRBI):
        self.RBI += newRBI

    def getBB(self):
        return self.BB

    def addBB(self, newBB):
        self.BB += newBB

    def getK(self):
        return self.K

    def addK(self, newK):
        self.K += newK

    def getHR(self):
        return self.HR

    def addHR(self, newHR):
        self.HR += newHR

    def getAVG(self):
        return self.AVG

    def updateAVG(self):
        if self.AB == 0:
            return
        self.AVG = round(float(self.H / self.AB), 3)

    def getOBP(self):
        return self.OBP

    def updateOBP(self):
        if self.AB == 0:
            return
        self.OBP = round(float((self.H + self.BB) / (self.AB + self.BB)), 3)

    def getSLG(self):
        return self.SLG

    def updateSLG(self):
        self.SLG = round(self.OPS - self.OBP, 3)
        if self.AVG == 0.0:
            self.SLG = 0.0
        # take into account special instances where
        # players played games before March 28
        # Shouldn't affect the algorithm much...
        if self.SLG < 0:
            self.SLG = self.AVG

    def getOPS(self):
        return self.OPS

    def setOPS(self, newOPS):
        self.OPS = newOPS

    def getGmpks(self):
        return self.gmpks

    def getDict(self):
        return self.dict

    def getLastList(self):
        return self.dict[self.gmpks[-1]]

    def updateAfterGame(self, lst):
        self.playedGame()
        self.addAB(lst[BatterStat.AB])
        self.addR(lst[BatterStat.R])
        self.addH(lst[BatterStat.H])
        self.addRBI(lst[BatterStat.RBI])
        self.addBB(lst[BatterStat.BB])
        self.addK(lst[BatterStat.K])
        self.setOPS(lst[BatterStat.OPS])
        self.updateAVG()
        self.updateOBP()
        self.updateSLG()

    def updateList(self, gamepk):
        self.gmpks.append(gamepk)
        newlst = []
        newlst.append(self.getGP())
        newlst.append(self.getAB())
        newlst.append(self.getR())
        newlst.append(self.getH())
        newlst.append(self.getRBI())
        newlst.append(self.getBB())
        newlst.append(self.getK())
        newlst.append(self.getAVG())
        newlst.append(self.getOBP())
        newlst.append(self.getSLG())
        newlst.append(self.getOPS())
        self.dict[gamepk] = newlst

class Pitcher:
    def __init__(self, name, team, starter, GP=0, IP=0, H=0, R=0, ER=0, BB=0, K=0, HR=0, ERA=0.0, WHIP=0.0):
        self.name = name
        self.team = team
        self.starter = starter
        self.GP = GP
        self.IP = IP
        self.trueIP = 0
        self.H = H
        self.R = R
        self.ER = ER
        self.BB = BB
        self.K = K
        self.HR = HR
        self.ERA = ERA
        self.WHIP = WHIP
        self.dict = {}
        self.gmpks = []

    def __str__(self):
        return "Name: " + self.name + "; Team: " + self.team

    def getName(self):
        return self.name

    def getTeam(self):
        return self.team

    def setTeam(self, newTeam):
        self.team = newTeam

    def isStarter(self):
        return self.starter

    def getGP(self):
        return self.GP

    def setGP(self, newGP):
        self.GP = newGP

    def playedGame(self):
        self.GP += 1

    def getIP(self):
        return self.IP

    # stats return .1 and .2 for innings pitched, need to be converted to 1/3 and 2/3 of an inning
    def addIP(self, newIP):
        if (newIP % 1) > 0:
            if (newIP % 1) <= 0.12:
                self.trueIP += (1.0/3.0)
            elif (newIP % 1) <= 0.22:
                self.trueIP += (2.0/3.0)
        self.trueIP += floor(newIP)
        self.IP = round(self.trueIP, 1)

    def getH(self):
        return self.H

    def addH(self, newH):
        self.H += newH

    def getR(self):
        return self.R

    def addR(self, newR):
        self.R += newR

    def getER(self):
        return self.ER

    def addER(self, newER):
        self.ER += newER

    def getBB(self):
        return self.BB

    def addBB(self, newBB):
        self.BB += newBB

    def getK(self):
        return self.K

    def addK(self, newK):
        self.K += newK

    def getHR(self):
        return self.HR

    def addHR(self, newHR):
        self.HR += newHR

    def getERA(self):
        return self.ERA

    def updateERA(self):
        if self.IP == 0.0:
            return
        self.ERA = round(float(self.ER / self.IP * 9), 2)

    def getWHIP(self):
        return self.WHIP

    def updateWHIP(self):
        if self.IP == 0:
            return
        self.WHIP = round(float((self.H + self.BB) / self.IP), 2)

    def getGmpks(self):
        return self.gmpks

    def getDict(self):
        return self.dict

    def getLastList(self):
        return self.dict[self.gmpks[-1]]

    def updateAfterGame(self, lst):
        self.playedGame()
        self.addIP(lst[PitcherStat.IP])
        self.addH(lst[PitcherStat.H])
        self.addR(lst[PitcherStat.R])
        self.addER(lst[PitcherStat.ER])
        self.addBB(lst[PitcherStat.BB])
        self.addK(lst[PitcherStat.K])
        self.addHR(lst[PitcherStat.HR])
        self.updateERA()
        self.updateWHIP()

    def updateList(self, gamepk):
        self.gmpks.append(gamepk)
        newlst = []
        newlst.append(self.getGP())
        newlst.append(self.getIP())
        newlst.append(self.getH())
        newlst.append(self.getR())
        newlst.append(self.getER())
        newlst.append(self.getBB())
        newlst.append(self.getK())
        newlst.append(self.getHR())
        newlst.append(self.getERA())
        newlst.append(self.getWHIP())
        self.dict[gamepk] = newlst
