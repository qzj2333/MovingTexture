# draw3DShape.py
# read file to draw 3D shape (with/without 1st/2nd direction field on)

import numpy as np
import matplotlib.pyplot as plt
from utils import *
from random import uniform
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# data members
shape    = "spline_64_5"
fileName = "data/" + shape + ".smfd"
allPoints     = {}
allPtsList    = []
pointsList    = {}      # x, y, z --> point
trianglesList = []
percentLimit = 0.3
moveSpeed    = 0.1
length = 0.05
nStep = 20
nCluster = 0

points    = False
surface   = True
dir1      = True
dir2      = False
fixLength = True
moveDir   = True  # True: dir1 / False: dir2 
save      = True
plot      = "move"   # rest / move

def drawTriangle(ax):
        global trianglesList
        for t in trianglesList:
                p0 = t.t0
                p1 = t.t1
                p2 = t.t2
                px = [p0.px, p1.px, p2.px]
                py = [p0.py, p1.py, p2.py]
                pz = [p0.pz, p1.pz, p2.pz]
                trianglePts = [zip(px, py, pz)]
                triangle = Poly3DCollection(trianglePts, alpha=0.1)
                triangle.set_color("grey")
                triangle.set_edgecolor('grey')
                ax.add_collection3d(triangle)

def drawPts(ax, ptList, isDraw):
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
        
        for p in ptList.values():
                X1, Y1, Z1 = npAppend(p.px, p.py, p.pz, X1, Y1, Z1)
                X2, Y2, Z2 = npAppend(p.d1x, p.d1y, p.d1z, X2, Y2, Z2)
                X3, Y3, Z3 = npAppend(p.d2x, p.d2y, p.d2z, X3, Y3, Z3)

        X1 = X1[1:]
        Y1 = Y1[1:]
        Z1 = Z1[1:]
        X2 = X2[1:]
        Y2 = Y2[1:]
        Z2 = Z2[1:]
        X3 = X3[1:]
        Y3 = Y3[1:]
        Z3 = Z3[1:]
        xNew1 = X1 + X2
        yNew1 = Y1 + Y2
        zNew1 = Z1 + Z2
        xNew2 = X1 + X3
        yNew2 = Y1 + Y3
        zNew2 = Z1 + Z3
        
        if isDraw == True:
                if points:
                        ax.scatter(X1, Y1, Z1, c = "grey")
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

def drawDirLine(ax, x1, x2, y1, y2, z1, z2, col):
        ax.plot([x1, x2], [y1, y2], [z1, z2], color = col)
        #ax.scatter(x2, y2, z2, c = col, marker='1')

def updatePts(ptList, xNew, yNew, zNew):
        newPtList = {}
        for x, y, z in zip(xNew, yNew, zNew):
                newPt = Point(x, y, z)
                newPtList[x, y, z] = newPt
        return newPtList

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
        global pointsList
        fig=plt.figure() 
        ax=Axes3D(fig)
        pointsList = clusterPts(pointsList, allPoints, nCluster)
        drawPts(ax, pointsList, True)
        ax.set_xlabel('x axis', color='black')  
        ax.set_ylabel('y axis', color='black')  
        ax.set_zlabel('z axis', color='black')
        ax.view_init(elev=0, azim=70)
        #plt.title("This is main title")
        setLim(ax)
        if save:
                plt.savefig(shape+'1.png')
        plt.show()
        return plt

def movingDir():
        global nStep, pointsList, oldPointsList
        for i in range(0, nStep):
                print i
                fig=plt.figure(i)
                ax=Axes3D(fig)
                pointsList = clusterPts(pointsList, allPoints, nCluster)
                pointsList = drawPts(ax, pointsList, True)
                pointsList = findAllEndPt(pointsList, allPoints)
                ptList     = generateNewPts(percentLimit, allPoints)
                pointsList = appendList(pointsList, ptList)
                ax.set_xlabel('x axis', color='black')  
                ax.set_ylabel('y axis', color='black')  
                ax.set_zlabel('z axis', color='black')
                ax.view_init(elev=0, azim=70)
                setLim(ax)  
                if save:
                        plt.savefig(shape+str(i).zfill(3)+'.png')
                #plt.show()
                plt.close()
        return plt

# ----- Test -----
nCluster = generatePts(length, percentLimit, fixLength, fileName, allPoints, allPtsList, pointsList, trianglesList, moveSpeed)
if plot == "rest":
        plt = restPlot()
elif plot == "move":
        plt = movingDir()
#plt.show()


