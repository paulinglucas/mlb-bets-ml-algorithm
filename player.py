class Batter:
    def __init__(self, team, GP=0, AB=0, R=0, H=0, RBI=0, BB=0, K=0, AVG=0.0, OBP=0.0, SLG=0.0, OPS=0.0):
        self.team = team
        self.AB = AB
        self.R = R
        self.H = H
        self.RBI = RBI
        self. BB = BB
        self. K = K
        self.AVG = AVG
        self.OBP = OBP
        self. SLG = SLG
        self.OPS = OPS

    def getTeam():
        return self.team

    def setTeam(newTeam):
        self.team = newTeam

    def getGP():
        return self.GP

    def playedGame():
        self.GP += 1

    def getAB():
        return self.AB

    def addAB(newAB):
        self.AB += newAB

    def getR():
        return self.R

    def addR(newR):
        self.R += newR

    def getH():
        return self.H

    def addH(newH):
        self.H += newH

    def getRBI():
        return self.RBI

    def addRBI(newRBI):
        self.RBI += newRBI

    def getBB():
        return self.BB

    def addBB(newBB):
        self.BB += newBB

    def getK():
        return self.K

    def addK(newK):
        self.K += newK

    def getAVG():
        return self.AVG

    def updateAVG():
        self.AVG = float(self.H / self.AB)

    def getOBP():
        return self.OBP

    def updateOBP():
        self.OBP = float((self.H + self.BB) / self.AB)

    def getSLG():
        return self.SLG

    def updateSLG():
        self.SLG = self.OPS - self.OBP

    def getOPS():
        return self.OPS

    def setOPS(newOPS):
        self.OPS = newOPS

class Pitcher:
    def __init__(self, team, starter, GP=0, IP=0, H=0, R=0, ER=0, BB=0, K=0, HR=0, ERA=0.0, WHIP=0.0):
        self.team = team
        self.starter = starter
        self.GP = GP
        self.IP = IP
        self.H = H
        self.R = R
        self.ER = ER
        self.BB = BB
        self.K = K
        self.HR = HR
        self.ERA = ERA
        self.WHIP = WHIP

    def getTeam():
        return self.team

    def setTeam(newTeam):
        self.team = newTeam

    def isStarter():
        return self.starter

    def getGP():
        return self.GP

    def playedGame():
        self.GP += 1

    def getIP():
        return self.IP

    def addIP(newIP):
        self.IP += newIP

    def getH():
        return self.H

    def addH(newH):
        self.H += newH

    def getR():
        return self.R

    def addR(newR):
        self.R += newR

    def getER():
        return self.ER

    def addER(newER):
        self.ER += newER

    def getBB():
        return self.BB

    def addBB(newBB):
        self.BB += newBB

    def getK():
        return self.K

    def addK(newK):
        self.K += newK

    def getHR():
        return self.HR

    def addHR(newHR):
        self.HR += newHR

    def getERA():
        return self.ERA

    def updateERA():
        self.ERA = float(self.ER / self.IP * 9)

    def getWHIP():
        return self.WHIP

    def updateWHIP():
        self.WHIP = float((self.H + self.BB) / self.IP)
