# draw3DShape.py
# read file to draw 3D shape (with/without 1st/2nd direction field on)

import numpy as np
import matplotlib.pyplot as plt
from random import uniform
from mpl_toolkits.mplot3d import Axes3D

# data members
shape = "ell"
fileName = shape + ".smfd"
allPoints = []
allDir1List = []
allDir2List = []
pointsList = []
newPointsList = []
dir1List = []
newDir1List = []
dir2List = []
newDir2List = []
index = 0
nSample = 100
percentLimit = 0.05
points = False
dir1 = True
dir2 = False
moveDir1 = True
moveDir2 = False

def generatePts():
        global allPoints, allDir1List, allDir2List, pointsList, dir1List, dir2List
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
                cur1 = float(cur1)
                allDir1List.append((cur1, direX, direY, direZ))

                # d
                d, cur2, dirX, dirY, dirZ = f.readline().split()
                dirX, dirY, dirZ = str2float(dirX, dirY, dirZ)
                cur2 = float(cur2)
                allDir2List.append((cur2, dirX, dirY, dirZ))
                
                if percent <= percentLimit:
                        pointsList.append((x, y, z))
                        dir1List.append((cur1, direX, direY, direZ))
                        dir2List.append((cur2, dirX, dirY, dirZ))
                
                line = f.readline()
        f.close()
        chooseSpecialLine()

def str2float(x, y, z):
        return float(x), float(y), float(z)

def drawPts(ax, ptList, d1List, d2List, c, m):
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
        
        if points:
                ax.plot3D(X1, Y1, Z1, "grey", alpha = 0.5)
        #ax.plot_surface(X1, Y1, Z1, color='b')
        
        if dir1:
                for i, z in enumerate(zip(X1, xNew1, Y1, yNew1, Z1, zNew1)):
                        x1, x2, y1, y2, z1, z2 = z
                        ax.plot([x1, x2], [y1, y2], [z1, z2], color = c)
                        ax.scatter(x2, y2, z2, c=c, marker=m)
                        if i == index:
                                print index, i
                                ax.plot([x1, x2], [y1, y2], [z1, z2], color = "blue")
                        #        ax.scatter(x2, y2, z2, c="blue", marker=m)
        if dir2:
                for x1, x2, y1, y2, z1, z2 in zip(X1, xNew2, Y1, yNew2, Z1, zNew2):
                        ax.plot([x1, x2], [y1, y2], [z1, z2], color = 'purple')
                        #ax.scatter(x2, y2, z2, c="blue", marker='^')
        #ax.contour3D(X, Y, Z, 50, cmap='binary')
        #plt.title("This is main title")

        if moveDir1:
                return updatePts(ptList, xNew1, yNew1, zNew1)
        elif moveDir2:
                return updatePts(ptList, xNew2, yNew2, zNew2)

def chooseSpecialLine():
        global pointsList, index
        for i, p in enumerate(pointsList):
                x, y, z = p
                if z > -0.1 and z < 0.1 and x > -1 and x < 0 and y > 1 and y < 2:
                        index = i
                        break
                
#def addSpecialLine(): 

def updatePts(ptList, xNew, yNew, zNew):
        #global pointsList
        ptList = []
        for x, y, z in zip(xNew, yNew, zNew):
                ptList.append((x, y, z))
        return ptList

def npAppend(x, y, z, X, Y, Z):
        X = np.append(X, x)
        Y = np.append(Y, y)
        Z = np.append(Z, z)
        return X, Y, Z

def findAllEndPt():
        global pointsList, dir1List, dir2List, allPoints, newPointsList, newDir1List, newDir2List
        newPointsList = []
        newDir1List = []
        newDir2List = []
        for p in pointsList:
                end, dir1, dir2 = findEndPt(p)
                newPointsList.append(end)
                newDir1List.append(dir1)
                newDir2List.append(dir2)

def findEndPt(currPt):
        global allPoints, allDir1List, allDir2List
        x1, y1, z1 = currPt
        minDist = float("inf")
        endPt = None
        for i, p in enumerate(allPoints):
                x2, y2, z2 = p
                dist = distance(x1, x2, y1, y2, z1, z2)

                if dist < minDist:
                        minDist = dist
                        endPt = p
                        dir1 = allDir1List[i]
                        dir2 = allDir2List[i]
        return endPt, dir1, dir2

def distance(x1, x2, y1, y2, z1, z2):
        return np.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

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

# ----- Test -----
generatePts()

for i in range(0, 5):
        fig=plt.figure(i) 
        ax=Axes3D(fig)
        pointsList = drawPts(ax, pointsList, dir1List, dir2List, "pink", "1")
        findAllEndPt()
        pointsList[:] = newPointsList[:]
        dir1List[:] = newDir1List[:]
        dir2List[:] = newDir2List[:]
        drawPts(ax, newPointsList, newDir1List, newDir2List, "red", "2")
        ax.set_xlabel('x axis', color='black')  
        ax.set_ylabel('y axis', color='black')  
        ax.set_zlabel('z axis', color='black')
        ax.view_init(elev=0, azim=70) 
        setLim(ax)
        plt.savefig(shape+str(i)+'.png')
plt.show()
