# draw3DShape.py
# read file to draw 3D shape (with/without 1st/2nd direction field on)

import numpy as np
import matplotlib.pyplot as plt
from random import uniform
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# data members
shape    = "ell"
fileName = "data/" + shape + ".smfd"
allPoints     = []
allDir1List   = []
allDir2List   = []
initialPts    = []
oldPointsList = []
pointsList    = []
initialDir1   = []
dir1List      = []
initialDir2   = []
dir2List      = []

percentLimit = 0.1
moveSpeed    = 0.1
minDist      = 0.05
length = 0.05
nStep = 20
index = 0
xMin  = -2
xMax  = -1
yMin  = 1
yMax  = 2
zMin  = -0.1
zMax  = 0.1

points    = False
surface   = True
dir1      = True
dir2      = False
fixLength = True
moveDir   = True  # True: dir1 / False: dir2 
save      = True
plot      = "move"   # rest / move

def generatePts():
        global length, percentLimit, fileName, allPoints, allDir1List, allDir2List, pointsList, dir1List, dir2List, initialPts, initialDir1, initialDir2
        f = file(fileName)
        line = f.readline()
        while not line.startswith("t"):
                percent = uniform(0, 1)
                # v
                v, x, y, z = line.split()
                x, y, z = str2float(x, y, z)
                allPoints.append((x,y,z))
                
                # D
                d, cur1, direX, direY, direZ = f.readline().split()
                direX, direY, direZ = str2float(direX, direY, direZ)
                # d
                d, cur2, dirX, dirY, dirZ = f.readline().split()
                dirX, dirY, dirZ = str2float(dirX, dirY, dirZ)
                
                if fixLength:
                        cur1 = length
                        cur2 = length
                else:
                        cur1 = float(cur1)*moveSpeed
                        cur2 = float(cur2)*moveSpeed
                
                allDir1List.append((cur1, direX, direY, direZ))
                allDir2List.append((cur2, dirX, dirY, dirZ))
                
                if percent <= percentLimit:
                        pointsList.append((x, y, z))
                        initialPts.append((x, y, z))
                        dir1List.append((cur1, direX, direY, direZ))
                        initialDir1.append((cur1, direX, direY, direZ))
                        dir2List.append((cur2, dirX, dirY, dirZ))
                        initialDir2.append((cur2, dirX, dirY, dirZ))
                
                line = f.readline()
        f.close()
        chooseSpecialLine()

def generateNewPts():
        global percentLimit, allPoints, allDir1List, allDir2List
        ptList = []
        d1List = []
        d2List = []
        for i, p in enumerate(allPoints):
                percent = uniform(0, 1)
                if percent <= percentLimit:
                        ptList.append(p)
                        d1List.append(allDir1List[i])
                        d2List.append(allDir2List[i])
        return ptList, d1List, d2List
        
def chooseSpecialLine():
        global pointsList, index
        for i, p in enumerate(pointsList):
                x, y, z = p
                if z > zMin and z < zMax and x > xMin and x < xMax and y > yMin and y < yMax:
                        index = i
                        break

def drawTriangle(ax):
        global fileName, allPoints
        f = file(fileName)
        for line in f.readlines():
                if line.startswith("t"):
                        t, p0Pos, p1Pos, p2Pos = line.split()
                        p0Pos, p1Pos, p2Pos = str2int(p0Pos, p1Pos, p2Pos)
                        p0x, p0y, p0z = allPoints[p0Pos-1]
                        p1x, p1y, p1z = allPoints[p1Pos-1]
                        p2x, p2y, p2z = allPoints[p2Pos-1]
                        px = [p0x, p1x, p2x]
                        py = [p0y, p1y, p2y]
                        pz = [p0z, p1z, p2z]
                        trianglePts = [zip(px, py, pz)]
                        triangle = Poly3DCollection(trianglePts, alpha=0.1)
                        triangle.set_color("grey")
                        triangle.set_edgecolor('grey')
                        ax.add_collection3d(triangle)
 
def str2float(x, y, z):
        return float(x), float(y), float(z)

def str2int(x, y, z):
        return int(x), int(y), int(z)

def drawPts(ax, ptList, d1List, d2List, isDraw):
        # initialization
        X1 = np.zeros(1)
        Y1 = np.zeros(1)
        Z1 = np.zeros(1)
        X2 = np.zeros(1)
        Y2 = np.zeros(1)
        Z2 = np.zeros(1)
        X3 = np.zeros(1)
        Y3 = np.zeros(1)
        Z3 = np.zeros(1)
        cur11 = np.zeros(1)
        cur22 = np.zeros(1)
        for point in ptList:
                x, y, z = point
                X1, Y1, Z1 = npAppend(x, y, z, X1, Y1, Z1)
        for dire in d1List:
                cur1, x, y, z = dire
                X2, Y2, Z2 = npAppend(x, y, z, X2, Y2, Z2)
                cur11 = np.append(cur11, cur1)
        for dire in d2List:
                cur2, x, y, z = dire
                X3, Y3, Z3 = npAppend(x, y, z, X3, Y3, Z3)
                cur22 = np.append(cur22, cur2)

        X1 = X1[1:]
        Y1 = Y1[1:]
        Z1 = Z1[1:]
        X2 = X2[1:]
        Y2 = Y2[1:]
        Z2 = Z2[1:]
        X3 = X3[1:]
        Y3 = Y3[1:]
        Z3 = Z3[1:]
        cur11 = cur11[1:]
        cur22 = cur22[1:]

        xNew1 = X1 + X2 * cur11
        yNew1 = Y1 + Y2 * cur11
        zNew1 = Z1 + Z2 * cur11
        xNew2 = X1 + X3 * cur22
        yNew2 = Y1 + Y3 * cur22
        zNew2 = Z1 + Z3 * cur22

        if isDraw == True:
                if points:
                        ax.scatter(X1, Y1, Z1, s = 1, c = "grey")
                if surface:
                        drawTriangle(ax)
                if dir1:
                        for i, z in enumerate(zip(X1, xNew1, Y1, yNew1, Z1, zNew1)):
                                drawDirLines(ax, i, z, "red")
                if dir2:
                        for i, z in enumerate(zip(X1, xNew2, Y1, yNew2, Z1, zNew2)):
                                drawDirLines(ax, i, z, "purple")

        if moveDir:     # move dir --> dir1
                return updatePts(ptList, xNew1, yNew1, zNew1)
        else:           # move dir --> dir2
                return updatePts(ptList, xNew2, yNew2, zNew2)

def drawDirLines(ax, i, z, col):
        x1, x2, y1, y2, z1, z2 = z
        drawDirLine(ax, x1, x2, y1, y2, z1, z2, col)
        #if i == index:
        #        drawDirLine(ax, x1, x2, y1, y2, z1, z2, "blue")

def drawDirLine(ax, x1, x2, y1, y2, z1, z2, col):
        ax.plot([x1, x2], [y1, y2], [z1, z2], color = col)
        #ax.scatter(x2, y2, z2, c = col, marker='1')

def updatePts(ptList, xNew, yNew, zNew):
        newPtList = []
        for x, y, z in zip(xNew, yNew, zNew):
                newPtList.append((x, y, z))
        return ptList, newPtList

def npAppend(x, y, z, X, Y, Z):
        X = np.append(X, x)
        Y = np.append(Y, y)
        Z = np.append(Z, z)
        return X, Y, Z

def findAllEndPt():
        global oldPointsList, pointsList, dir1List, dir2List, allPoints
        newPointsList = []
        newDir1List = []
        newDir2List = []
        for i, p in enumerate(pointsList):
                end, dir1, dir2 = findEndPt(p, oldPointsList[i])
                newPointsList.append(end)
                newDir1List.append(dir1)
                newDir2List.append(dir2)
        pointsList = newPointsList
        dir1List = newDir1List
        dir2List = newDir2List        

def findEndPt(currPt, prevPt):
        global allPoints, allDir1List, allDir2List
        x1, y1, z1 = currPt
        minDist = float("inf")
        endPt = None
        for i, p in enumerate(allPoints):
                x2, y2, z2 = p
                if p != prevPt:
                        dist = distance(x1, x2, y1, y2, z1, z2)
                        if dist < minDist:
                                minDist = dist
                                endPt = p
                                dir1 = allDir1List[i]
                                dir2 = allDir2List[i]
        return endPt, dir1, dir2

def clearPts():
        global pointsList, oldPointsList, minDist, dir1List, dir2List
        tempPtList = []
        tempDir1 = []
        tempDir2 = []
        for i, p in enumerate(pointsList):
                if distancePt(p, oldPointsList[i]) >= minDist:
                        tempPtList.append(p)
                        tempDir1.append(dir1List[i])
                        tempDir2.append(dir2List[i])
        pointsList = tempPtList
        dir1List = tempDir1
        dir2List = tempDir2

def distancePt(p1, p2):
        x1, y1, z1 = p1
        x2, y2, z2 = p2
        return distance(x1, x2, y1, y2, z1, z2)

def distance(x1, x2, y1, y2, z1, z2):
        return np.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

def appendList(majorList, addList):
        for item in addList:
                majorList.append(item)
        return majorList

def setLim(ax):
        if shape == "ell":
                ax.set_xlim(-2.5, 2.5)
                ax.set_ylim(-2.5, 2.5)
                ax.set_zlim(-1.5, 1.5)
        elif shape == "cyl":
                ax.set_xlim(-2.5, 2)
                ax.set_ylim(-1, 2.5)
                ax.set_zlim(-0.5, 3.5)
        elif shape == "sad":
                ax.set_xlim(-6, 6)
                ax.set_ylim(-1, 6)
                ax.set_zlim(-4, 4)
        elif shape == "spline_16":
                ax.set_xlim(-1, 3)
                ax.set_ylim(0, 4)
                ax.set_zlim(0, 3)
        elif shape == "spline_25":
                ax.set_xlim(-1, 4)
                ax.set_ylim(0, 5)
                ax.set_zlim(0, 3)

        elif shape == "spline_64_1":
                ax.set_xlim(0, 3)
                ax.set_ylim(0, 5)
                ax.set_zlim(-1, 1)
        elif shape == "spline_64_2":
                ax.set_xlim(0, 6)
                ax.set_ylim(0, 8)
                ax.set_zlim(0.5, 1)
        elif shape == "spline_64_5":
                ax.set_xlim(0, 6)
                ax.set_ylim(0, 8)
                ax.set_zlim(0.5, 1.1)

def restPlot():
        global pointsList, dir1List, dir2List
        fig=plt.figure() 
        ax=Axes3D(fig)
        drawPts(ax, pointsList, dir1List, dir2List, True)
        ax.set_xlabel('x axis', color='black')  
        ax.set_ylabel('y axis', color='black')  
        ax.set_zlabel('z axis', color='black')
        ax.view_init(elev=0, azim=70)
        #plt.title("This is main title")
        setLim(ax)
        if save:
                plt.savefig(shape+'1.png')
        return plt

def movingDir():
        global nStep, pointsList, dir1List, dir2List, oldPointsList, initialPts, initialDir1, initialDir2
        for i in range(0, nStep):
                print i
                fig=plt.figure(i)
                ax=Axes3D(fig)
                oldPointsList, pointsList = drawPts(ax, pointsList, dir1List, dir2List, True)
                findAllEndPt()
                clearPts()
                ptList, d1List, d2List = generateNewPts()
                appendList(pointsList, ptList)
                appendList(dir1List, d1List)
                appendList(dir2List, d2List)

                ax.set_xlabel('x axis', color='black')  
                ax.set_ylabel('y axis', color='black')  
                ax.set_zlabel('z axis', color='black')
                ax.view_init(elev=0, azim=70)
                setLim(ax)  
                if save:
                        plt.savefig(shape+str(i).zfill(3)+'.png')
                plt.close()
        
        return plt

# ----- Test -----
generatePts()
if plot == "rest":
        plt = restPlot()
elif plot == "move":
        plt = movingDir()
#plt.show()


