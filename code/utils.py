# utils.py
# functions used in both version of draw 3D shape

import numpy as np
from random   import uniform
from sklearn.cluster import AgglomerativeClustering

# ----- major function -----
def generatePts(length, percentLimit, fixLength, fileName, allPoints, allPtsList, pointsList, trianglesList, moveSpeed=1):
    f = file(fileName)
    for line in f.readlines():
        if line.startswith("v"):
            percent = uniform(0, 1)
            # v
            v, x, y, z = line.split()
            x, y, z = str2float(x, y, z)
                
        elif line.startswith("D"):
            # D
            d, cur1, direX, direY, direZ = line.split()
            direX, direY, direZ = str2float(direX, direY, direZ)
        elif line.startswith("d"):
            # d
            d, cur2, dirX, dirY, dirZ = line.split()
            dirX, dirY, dirZ = str2float(dirX, dirY, dirZ)
            
            if fixLength:
                    cur1 = length
                    cur2 = length
            else:
                    cur1 = float(cur1)*moveSpeed
                    cur2 = float(cur2)*moveSpeed

            currP = Point(x, y, z, cur1*direX, cur1*direY, cur1*direZ, cur2*dirX, cur2*dirY, cur2*dirZ)
            allPoints[x, y, z] = currP
            allPtsList.append(currP)
            
            if percent <= percentLimit:
                    pointsList[x, y, z] = currP
            
        else:   # line.startwith("t")
            t, p0Pos, p1Pos, p2Pos = line.split()
            p0Pos, p1Pos, p2Pos = str2int(p0Pos, p1Pos, p2Pos)
            p0 = allPtsList[p0Pos-1]
            p1 = allPtsList[p1Pos-1]
            p2 = allPtsList[p2Pos-1]
            trianglesList.append(Triangle(p0, p1, p2))
    f.close()
    return len(pointsList)

def generateNewPts(percentLimit, allPoints):
    ptList = {}
    for p in allPoints.values():
        percent = uniform(0, 1)
        if percent <= percentLimit:
            ptList[p.px, p.py, p.pz] = p
    return ptList

def findAllEndPt(pointsList, allPoints):
    newPointsList = {}
    for loc, p in pointsList.iteritems():
        end = findEndPt(p, allPoints)
        newPointsList[end.px, end.py, end.pz] = end
    pointsList = newPointsList
    return pointsList

def findEndPt(currPt, allPoints):
    minDist = float("inf")
    endPt = None
    for p in allPoints.values():
        dist = distance(currPt.px, p.px, currPt.py, p.py, currPt.pz, p.pz)
        if dist < minDist:
            minDist = dist
            endPt = p
    return endPt

def clusterPts(pointsList, allPoints, nCluster):
    clustersList = {}
    data = np.zeros((1, 3))
    for loc, p in pointsList.iteritems():
            x, y, z = loc
            data = np.append(data, [[x, y, z]], axis=0)
    data = data[1:]
    clustering = AgglomerativeClustering(n_clusters=nCluster, affinity='euclidean', linkage='ward')
    clusters = clustering.fit(data)
        
    for i, l in enumerate(clusters.labels_):
            clustersList[l]= data[i, :]
    pointsList = {}
    for loc in clustersList.values():
            x, y, z = loc
            pointsList[x, y, z] = allPoints[x, y, z]
    print len(clustersList), len(pointsList)
    return pointsList

# ----- helper function -----
def str2float(x, y, z):
        return float(x), float(y), float(z)

def str2int(x, y, z):
        return int(x), int(y), int(z)

def distancePt(p1, p2):
    return distance(p1.px, p2.px, p1.py, p2.py, p1.pz, p2.pz)

def distance(x1, x2, y1, y2, z1, z2):
        return np.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

def appendList(majorList, addList):
    for k ,v in addList.iteritems(): 
        majorList[k] = v
    return majorList

def npAppend(x, y, z, X, Y, Z):
    X = np.append(X, x)
    Y = np.append(Y, y)
    Z = np.append(Z, z)
    return X, Y, Z

# normalize 3D vector
def normalize(vec):
    x, y, z = vec
    mag = np.linalg.norm(vec)
    if mag == 0:
        x = 0
        y = 0
        z = 0
    else:
        x = x / mag
        y = y / mag
        z = z / mag
    result = makeVector(x, y, z)
    return result

def makeMatrix( *args ):
    dtype=np.float64
    if len(args) == 1:
        # from python list
        return np.array( args[0], dtype=dtype )
    elif len(args) == 2:
        # from (rows, cols)
        return np.zeros( (args[0], args[1]), dtype=dtype )
    elif len(args) == 3:
        # from (rows, cols, value)
        return args[2]*np.ones( (args[0], args[1]), dtype=dtype )

def makeVector( *args ):
    if len(args) != 1:
        # from given coordinates: makeVector(1, 2) or makeVector( 1, 2, 3 )
        return makeMatrix( args )
    else:
        # from list or vector: makeVector( [1, 2] ), makeVector( z )
        coords = [ c for c in args[0] ]
        return makeMatrix( coords )

# ----- class -----
class Point:
    def __init__(self, x, y, z, D1x=None, D1y=None, D1z=None, D2x=None, D2y=None, D2z=None):
        self.px   = x
        self.py   = y
        self.pz   = z
        self.d1x  = D1x
        self.d1y  = D1y
        self.d1z  = D1z
        self.d2x  = D2x
        self.d2y  = D2y
        self.d2z  = D2z
        self.cluster = None
        self.dist = float('inf')

    def signCluster(self, clustersList):
        for c in clustersList:
            cx, cy, cz = c.centroid
            d = distance(self.px, self.py, self.pz, cx, cy, cz)
            if d < self.dist:
                self.dist = d
                self.cluster = c

class Triangle:
    def __init__(self, p1, p2, p3):
        self.t0 = p1
        self.t1 = p2
        self.t2 = p3

class Cluster:
    def __init__(self, x, y, z):
        self.centroid = (x, y, z)
        self.majorP = None
    
    def findMajorPoint(self, pointsList):
        minDist = float('inf')
        cx, cy, cz = self.centroid
        for p in pointsList:
            d = distance(cx, cy, cz, p.px, p.py, p.pz)
            if d < minDist:
                minDist = d
                self.majorP = p
