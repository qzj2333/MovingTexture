# model.py
# draw appropriate 3D shape using pyglet
import random
import os.path
import numpy as np
from random import uniform, randint
from pyglet.gl     import *
from pyglet.window import *

# color
#glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, yellow)
#glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, yellow)
#glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, greens)
#glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, high_shine)

# ---------- variables that can be changed ----------
shape         = "spline_16" # 3D model name (all model appear in data file)
percentLimit  = 1.       # percent of dir lines that show on every frame
clusterDepth  = 1           # (need >0) for cluster stroke: number of triangles from center of every cluster
#moveSpeedDen = 200         # effect only when fixLength == False: increase will shorter the distance between control points
#lengthDen    = 35          # effect only when fixLength == True:  increase will shorter the distance between control points
useLength     = "triangle"  # triangle / xyzRange use to compute moveSpeed and length that effect length of stroke
location      = "global"    # translation model read file: pres/oblique/global/local
fixLength     = True        # T: dir line has same length; F: dir line depends on curvature read from data file 
isCluster     = False       # T: cluster BOTH strokes and pd lines based on clusterDepth; F: not cluster BOTH strokes and pd lines
save          = False       # switch for save frames
loadPre       = True        # T: load pre-generate information from data/prepare/temp or formal/"shape".txt; F: generate info before draw
loadMat       = False       # load translation model (must save translation model first)
# ----- pt related -----
ptLength      = 10          # number steps of a pt will go
loadPoints    = False       # T: load points from data/points/temp or formal/"shape".txt; F: random generate percentLimit amount of points and automatically save them to "shape"Points.txt
randomColorP  = False       # random color switch for points
drawDots      = False       # T: draw a dot on every picked points; F: no dots drawing
# ----- stroke related -----
minNumCP      = 2           # min number of control points/steps in a stroke
maxNumCP      = 50          # max number of control points/steps in a stroke
minDistDen    = 10           # effect the distance between 1st and last of cps at each stroke, increase will shorter the distance/increase number of total strokes 
randomColorS  = False       # random color switch for stroke

# ---------- global variables that do not change ----------
tx = 0.
ty = 0.
xAngle = 0.
yAngle = 0.
zAngle = 0.
zoom   = 1.
# window frame size
winW = 800
winH = 800
win = pyglet.window.Window(winW, winH)
fileName = "data/" + shape + ".smfd"
pointsList = []
allPoints = {}
trianglesList = []
triList = {}
strokesList = []
originalStrokes = []
originalPoints = []
drawingList = []
count = 0
minDist = 1.
length       = 1.       # length of each curvature
moveSpeed    = 1.       # make it relate to triangle size
minX = float('inf')
minY = float('inf')
minZ = float('inf')
maxX = -float('inf')
maxY = -float('inf')
maxZ = -float('inf')
drawShape    = "tri"    # surface shape: tri / line / None
isMove       = False    # pause first frame after draw it
# ----- for points -----
launchP      = 0
drawPoint    = False
# ----- for strokes -----
launchS      = 0        # launch new strokes/points
drawStroke   = False

# ---------- win events -----------
# data members:
# create ctypes arrays of floats:
def vec(*args):
    return (GLfloat * len(args))(*args)

light_diffuse  = vec(0.8, 0.8, 0.8, 1.0)
light_ambient  = vec(1.0, 1.0, 1.0, 1.0)
light_specular = vec(1.0, 1.0, 1.0, 1.0)
light_position = vec(1.0, 2.0, 3.0, 1.0)
#different intensity ambient lighting
no_light    = vec(0.0, 0.0, 0.0, 1.0)   # black light
low_light   = vec(0.3, 0.3, 0.3, 1.0)   # dark gray light
med_light   = vec(0.7, 0.7, 0.7, 1.0)   # light gray light
white_light = vec(1.0, 1.0, 1.0, 1.0)   # white light
# light positions (non-directional) in homogeneous coordinates
# could have a light position with variables for x, y, z to vary the position
light_position1 = vec(1.0, 1.0, 1.0, 0.0)   # on the right
light_position2 = vec(-1.0, 1.0, 1.0, 0.0)  # on the left
light_position3 = vec(-0.2, 0.2, 0.98, 0.0)
# different levels of shininess
no_shine   = vec(0.0)
low_shine  = vec(10.0)
med_shine  = vec(68.0)
high_shine = vec(120.0)
# different levels of red, green, and blue
reds   = vec(0.1, 0, 0, 0.2, 0, 0,0.4, 0, 0, 0.6, 0, 0, 0.8, 0, 0,1.0, 0, 0)
blues  = vec(0, 0, 0.1, 0, 0, 0.2, 0, 0, 0.4, 0, 0, 0.6, 0, 0, 0.8, 0, 0, 1.0)
greens = vec(0, 0.1, 0, 0, 0.2, 0, 0, 0.4, 0, 0, 0.6, 0, 0, 0.8, 0, 0, 1.0, 0.0)
#single intense colored lights
yellow = vec(1.0, 1.0, 0.0)
purple = vec(1.0, 0.0, 1.0)
blueGreen = vec(0.0, 1.0, 1.0)

# initially, transform matrix is 4x4 identity matrix in 1D array
transformMat = vec(0.0, 0.0, 0, 0.0, 0.0, 0., 0.0, 0.0, 0, 0.0, 0., 0.0, 0.0, 0., -1., 1.0)
# get the current transformation in OpenGL into an array
# print it (or save to file) and use it as transformMat later
saveTransformMat = (GLfloat*16)()

# set up viewing point, light effect, etc for every frame
# called only once (before frame pop up)
def setup():
    glShadeModel(GL_SMOOTH)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)   # GL_FILL / GL_LINE
    glEnable(GL_NORMALIZE)
    glEnable(GL_DEPTH_TEST)
    #glEnable(GL_CULL_FACE)
    #glCullFace(GL_BACK)
    #glFrontFace(GL_CW)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glPointSize(4)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  light_diffuse)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT,  light_ambient)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glEnable(GL_LIGHT0)
    #glLightModeli(GL_LIGHT_MODEL_COLOR_CONTROL, GL_SEPARATE_SPECULAR_COLOR)
    glLightModelf(GL_LIGHT_MODEL_TWO_SIDE, 1)
    glEnable(GL_LIGHTING)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glEnable(GL_DEPTH_TEST) # 3D drawing work when sth. in front of sth. else
    glViewport(0, 0, winW, winH)

# set up viewing point, called every frame
def resize(minX, maxX, minY, maxY, minZ, maxZ):
    #Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)    # camera perspective
    glLoadIdentity() # reset camera
    #gluPerspective(60.0, 1.*winW/winH, 0.1, 50.)
    #gluPerspective(45.0, 1.*winW/winH, 0.1, 1000.)
    glOrtho(-maxX-1, maxX+1, -maxY-1, maxY+1, -100, 100)   #minZ-1, maxZ+1)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity() # reset camera
    

# key press events:
# S: print & save to file: "shape".txt
# X/A: rotate drawing on x-direction
# Y/B: rotate drawing on y-direction
# Z/C: rotate drawing on z-direction
# up/down/left/right: translate drawing
# Shift + > / <: zoom in/out the drawing
# P: one step forward stroke and/or point drawing
# R: rest the frame (all moving pause)
# .: continue move forward for stroke drawing
# M: continue move forward for point drawing
# D: display/hide stroke drawing
# E: display/hide point drawing
# F: switch surface drawing as: triangle surface --> line surface --> no surface
@win.event
def on_key_press(symbol, modifiers):
    global drawPoint, drawShape, drawStroke, zoom, xAngle, yAngle, zAngle, tx, ty, isMove, count, sprite, drawPrev
    if symbol == key.S: 
        glGetFloatv(GL_MODELVIEW_MATRIX, saveTransformMat)
        print list(saveTransformMat)
        f = file(shape+".txt", "w")
        for num in list(saveTransformMat):
            print >> f, "%f" %(num)
        f.close()
    elif symbol == key.GREATER:
        zoom += 0.1
    elif symbol == key.LESS:
        zoom -= 0.1
    elif symbol == key.X:
        xAngle += 15.
    elif symbol == key.Y:
        yAngle += 15.
    elif symbol == key.Z:
        zAngle += 15.
    elif symbol == key.A:
        xAngle -= 15.
    elif symbol == key.B:
        yAngle -= 15.
    elif symbol == key.C:
        zAngle -= 15.
    elif symbol == key.RIGHT:
        tx += 0.5
    elif symbol == key.LEFT:
        tx -= 0.5
    elif symbol == key.UP:
        ty += 0.5
    elif symbol == key.DOWN:
        ty -= 0.5
    elif symbol == key.P: 
        isMove = True
    elif symbol == key.R:
        clearClockEvent()
    elif symbol == key.PERIOD:
        clearClockEvent()
        pyglet.clock.schedule(autoDrawForward)
    elif symbol == key.M:
        clearClockEvent()
        pyglet.clock.schedule(autoDrawPt)
    elif symbol == key.D:   
        drawStroke = not drawStroke
    elif symbol == key.E:   
        drawPoint = not drawPoint
    elif symbol == key.F:
        if drawShape == "tri":
            drawShape = "line"
        elif drawShape == "line":
            drawShape = None
        else:   # drawShape == None
            drawShape = "tri"


# ---------- prepare function ----------
def savePrepare(trianglesList, pointsList, strokesList):
    f = file("data/prepare/temp/"+shape+".txt", "w")   # 0 based
    print >> f, "precentLimit %d" %percentLimit
    print >> f, "cluster %s %d" %(isCluster, clusterDepth)
    print >> f, "fixLength %s" %fixLength
    print >> f, "pcp %d scp %d" %(ptLength, maxNumCP)
    print >> f, "randomColor S %s P %s" %(randomColorP, randomColorS)
    print >> f, "%f %f %f %f %f %f" %(minX, maxX, minY, maxY, minZ, maxZ)

    #print >> f, "trianglesList"
    for t in trianglesList:
        nx, ny, nz = t.norm
        print >> f, "t %f %f %f" %(nx, ny, nz)    # normal
        for p in t.vertices:
            x, y, z = p.initial
            print >> f, "%f %f %f" %(x, y, z) # position for each vertex

    #print >> f, "pointsList"
    for p in pointsList:
        print >> f, "p %d" %len(p.cps)  # p length of cps
        r, g, b = p.color
        print >> f, "%f %f %f" %(r, g, b) # color
        for cp in p.cps:
            x, y, z = cp
            print >> f, "%f %f %f" %(x, y, z)   # cp location
            
    #print >> f, "strokesList"
    for s in strokesList:
        print >> f, "s %d" %len(s.cps)  # s length of cps
        r, g, b = s.color
        print >> f, "%f %f %f" %(r, g, b) # color
        for cp in s.cps:
            x, y, z = cp
            print >> f, "%f %f %f" %(x, y, z)   # cp location
    f.close()

def loadPrepare():
    if os.path.exists("data/prepare/formal/"+shape+".txt"):
        f = file("data/prepare/formal/"+shape+".txt", "r")
    else:
        f = file("data/prepare/temp/"+shape+".txt", "r")
    # throw first five lines
    for i in range(0, 5):
        f.readline()
    trianglesList = []
    pointsList = []
    strokesList = []

    line = f.readline()
    minX, maxX, minY, maxY, minZ, maxZ = line.split()
    minX, maxX, minY = str2float(minX, maxX, minY)
    maxY, minZ, maxZ = str2float(maxY, minZ, maxZ)
    
    line = f.readline()
    while line.strip() != '':   # not reach the end of line
        if line.startswith("t"):
            t, nx, ny, nz = line.split()
            nx, ny, nz = str2float(nx, ny, nz)
            tri = SimpleTriangle(nx, ny, nz)
            for i in range(0, 3):
                line = f.readline()
                x, y, z = line.split()
                x, y, z = str2float(x, y, z)
                tri.addLoc(x, y, z)
            trianglesList.append(tri)
                
        elif line.startswith("p"):
            p, n = line.split()
            n = int(n)
            r, g, b = f.readline().split()
            r, g, b = str2float(r, g, b)
            currP = SimplePS(r, g, b)
            for i in range(0, n):
                x, y, z = f.readline().split()
                x, y, z = str2float(x, y, z)
                currP.addCP(x, y, z)
            pointsList.append(currP)
            
        elif line.startswith("s"):
            s, n = line.split()
            n = int(n)
            r, g, b = f.readline().split()
            r, g, b = str2float(r, g, b)
            currS = SimplePS(r, g, b)
            for i in range(0, n):
                x, y, z = f.readline().split()
                x, y, z = str2float(x, y, z)
                currS.addCP(x, y, z)
            strokesList.append(currS)
        else:
            break
        line = f.readline()
    return trianglesList, pointsList, strokesList, minX, maxX, minY, maxY, minZ, maxZ
            
# read data from file and output:
# min/maxX/Y/Z: min/max of X&Y&Z among all points location
# allPoints: loc --> Point obj for all points from data
# triangleList: centroid --> Triangle obj for all triangles from data
# triList: For every point, Point obj --> list of Triangle objs that contian that point as one of its vertices
def generatePts(fileName, randomColorP):
    f = file(fileName)

    allPoints     = {}
    allPtsList    = []
    trianglesList = []
    triList       = {} 

    minX = float('inf')
    minY = float('inf')
    minZ = float('inf')
    maxX = -float('inf')
    maxY = -float('inf')
    maxZ = -float('inf')
    
    for line in f.readlines():
        if line.startswith("v"):
            # v
            v, x, y, z = line.split()
            x, y, z = str2float(x, y, z)
            
            if x < minX:
                minX = x
            if x > maxX:
                maxX = x
            if y < minY:
                minY = y
            if y > maxY:
                maxY = y
            if z < minZ:
                minZ = z
            if z > maxZ:
                maxZ = z
            
        elif line.startswith("D"):
            # D
            d, cur1, direX, direY, direZ = line.split()
            direX, direY, direZ = str2float(direX, direY, direZ)
            cur1 = float(cur1)
            
        elif line.startswith("d"):
            # d
            d, cur2, dirX, dirY, dirZ = line.split()
            dirX, dirY, dirZ = str2float(dirX, dirY, dirZ)
            cur2 = float(cur2)
            if randomColorP:
                colorNum = np.random.rand(1,3)[0]
                color = vec(colorNum[0], colorNum[1], colorNum[2])
                currP = Point(x, y, z, cur1, direX, direY, direZ, cur2, dirX, dirY, dirZ, c=color)
            else:
                currP = Point(x, y, z, cur1, direX, direY, direZ, cur2, dirX, dirY, dirZ)
            allPoints[x, y, z] = currP
            allPtsList.append(currP)
            
        else:   # line.startwith("t")
            t, p1Pos, p2Pos, p3Pos = line.split()
            p1Pos, p2Pos, p3Pos = str2int(p1Pos, p2Pos, p3Pos)

            p1 = allPtsList[p2Pos-1]
            p2 = allPtsList[p1Pos-1]
            p3 = allPtsList[p3Pos-1]

            tri = Triangle(p1, p2, p3)
            x, y, z = tri.centroid
            trianglesList.append(tri)

            # add to triList
            if p3 not in triList:
                triList[p3] = []
            triList[p3].append(tri)

            if p1 not in triList:
                triList[p1] = []
            triList[p1].append(tri)

            if p2 not in triList:
                triList[p2] = []
            triList[p2].append(tri)
    f.close()  
    return minX, maxX, minY, maxY, minZ, maxZ, trianglesList, triList, allPoints, allPtsList

# compute min and max side length among all triangles
def computeTriangleSideLength(trianglesList):
    minD = float("inf")
    maxD = 0
    for t in trianglesList:
        d1 = distancePt(t.vertices[0], t.vertices[1])
        d2 = distancePt(t.vertices[1], t.vertices[2])
        d3 = distancePt(t.vertices[0], t.vertices[2])
        dist = [d1, d2, d3]

        for d in dist:
            if d < minD:
                minD = d
            if d > maxD:
                maxD = d
    return minD, maxD

# compute length and moveSpeed based on range of X/Y/Z from data file
# (used for compute magnitude for direction lines) 
def computeLength(minX, maxX, minY, maxY, minZ, maxZ, trianglesList):
    # based on x/y/z range
    if useLength == "xyzRange":
        diff = min(maxX - minX, maxY - minY, maxZ - minZ)
        moveSpeed = diff / 200  # moveSpeedDen
        length = diff / 35      # lengthDen
    # based on triangle side length
    elif useLength == "triangle":
        minD, maxD = computeTriangleSideLength(trianglesList)
        diff = maxD - minD
        moveSpeed = diff / 15   # moveSpeedDen
        length = diff / 15      # lengthDen
    return moveSpeed, length

# get rid of short strokes
def computeMinDistance(strokesList):
    maxDist = 0
    for s in strokesList:
        x1, y1, z1 = s.cps[0]
        x2, y2, z2 = s.cps[-1]
        dist = distance(x1, x2, y1, y2, z1, z2)
        
        if dist > maxDist:
            maxDist = dist
    return maxDist / minDistDen
    
# compute magnitude for every pd line
def computePtLength(allPoints):
    for p in allPoints.values():
        p.computeLength()

# for every point, sign 1st pd as their pd line (the line that draws)
def computePD(allPoints):
    #reference = []
    for p in allPoints.values():
        '''
        if len(reference) == 0:
            reference = p.d1    # random choose

        pds = [p.d1, -p.d1, p.d2, -p.d2]
        minAngle = float("inf")
        ppd = None
        for pd in pds:
            crossProd = np.linalg.norm(np.cross(reference, pd))
            #print crossProd
            if crossProd < minAngle:
                minAngle = crossProd
                ppd = pd
        '''
        p.pd = p.d1 # ppd
        #reference = ppd

def resetPts(pointsList):
    if isinstance(pointsList, list):
        for p in pointsList:
            p.done = False
    else:
        for p in pointsList.values():
            p.done = False

# ----- for points -----
# generate pointsList from allPoints (percentLimit% of allPoints --> pointsList)
# and save all points' indices to file
# pointsList: points that will draw pd lines
def initializePtList(allPtsList, percentLimit):
    pointsList = []

    # auto. save in the file
    f = file("data/points/temp/"+shape+".txt", "w")   # 0 based
    for i, p in enumerate(allPtsList):
        percent = uniform(0, 1)
        if percent <= percentLimit:
            pointsList.append(p)
            print >> f, "%d" %i
    f.close()
    return pointsList

# generate pointsList based on indices from the loading file and allPtsList which contains all points
def loadPts(allPtsList):
    pointsList = []
    if os.path.exists("data/points/formal/"+shape+".txt"):
        f = file("data/points/formal/"+shape+".txt", "r")
    else:
        f = file("data/points/temp/"+shape+".txt", "r")
    for line in f.readlines():
        i = int(line)
        pointsList.append(allPtsList[i])
    f.close()
    return pointsList

# cluster strokes by cluster neighbor triangles 
def clusterPts(pointsList, triList):
    colorUsed   = {}
    clusterList = {}
    resetPts(allPoints)
    for p in pointsList.values():
        if not p.done:
            if p in triList.keys():
                clusterList[p] = clusterPP(p, triList, pointsList, colorUsed)
                p.done = True
            else:
                p.done = True
    for c, v in clusterList.iteritems():
        print c, len(v)
    return clusterList

# help function of above: complete one cluster
def clusterPP(p, triList, pointsList, colorUsed):
    global clusterDepth
    colorNum = np.random.rand(1,3)[0]
    # if this color has been used, generate another random color
    while (colorNum[0], colorNum[1], colorNum[2]) in colorUsed.keys():
        colorNum = np.random.rand(1,3)[0]
    color = vec(colorNum[0], colorNum[1], colorNum[2])
    colorUsed[colorNum[0], colorNum[1], colorNum[2]] = color
    return clusterOneDepthP(p, triList, pointsList, color, clusterDepth)

# help function of above: complete one depth/edge/circle
def clusterOneDepthP(p, triList, pointsList, color, depth):
    clusterList = set()
    if depth > 0:
        triangles = triList[p]
        for t in triangles:
            p1, p2, p3 = t.vertices
            for p in t.vertices:
                if not p.done:
                    #p.color = color
                    clusterList.add(p)
                    clusterList.update(clusterOneDepth(p, triList, pointsList, color, depth-1))
                    p.done = True
    return clusterList

# generate and return percentLimit amount of new points from allPoints list
def generateNewPts(percentLimit, allPoints):
    ptList = {}
    for p in allPoints.values():
        percent = uniform(0, 1)
        if percent <= percentLimit:
            x, y, z = p.initial
            p.reset()
            ptList[x, y, z] = p
    return ptList

# help func for findAllEndPt func
# find and return the point that is closest to input currPt
def findEndPt(currP, allPoints, triList):
    mDist = float("inf")
    endPt = None
    x2, y2, z2 = currP.cps[-1] + currP.d1
    x3, y3, z3 = currP.cps[-1]
    movePt = np.array([x2, y2, z2])
    pt = allPoints[x3, y3, z3]
    for p in allPoints.values():
        x1, y1, z1 = p.initial
        dist = distance(x1, x2, y1, y2, z1, z2)
        if dist < mDist and (x1 != x3 or y1 != y3 or z1 != z3):
            mDist = dist
            endPt = p.initial
    neighborTriangles = triList[pt]
    isProject = False
    for t in neighborTriangles:
        adjustPt = t.projectPOntoTri(movePt)
        pd, w1, w2, w3 = t.computeTriPD(adjustPt)
        if w1 >= 0 and w2 >= 0 and w3 >= 0:
            currP.addCP(adjustPt)
            isProject = True
            break
    if isProject == False:
        i = randint(0, len(neighborTriangles)-1)
        adjustpt = neighborTriangles[i].projectPOntoTri(movePt)
        currP.addCP(adjustPt)
    return endPt

# generate at most "ptLength" long cp list for every point 
def generatePtCP(pointsList, allPoints, triList, ptLength):
    for i in range(0, ptLength):
        for p in pointsList:
            if not p.done:
                newP = findEndPt(p, allPoints, triList)
                # if newP exist (and is not same as any previous cp of current point)
                # then add it to cp list
                # otherwise current cp list is complete
                if len(newP) == 3:  # if newP != None
                    x1, y1, z1 = newP
                    # if current cp is already in the list
                    # (i.e. the segment goes back at some point)
                    # then end the cp list (not include last repeated cp)
                    for cp in p.cps:
                        x2, y2, z2 = cp
                        if x1 == x2 and y1 == y2 and z1 == z2:
                            p.done = True
                            break
                    if not p.done:  
                        p.addCP(newP)
                else:
                    p.done = True
        print i

# launch is called:
# launch every point in the origianl pointsList
# so that each pd line has a dot line looking
def addNewPts(pointsList, originalPoints):
    for p in originalPoints:
        newP = p.copy()
        pointsList.append(newP)
    return pointsList

# after every step drawing
# get rid of all points that reaches the end of its segment
def delFinishedPts(pointsList):
    newList = []
    for p in pointsList:
        if p.endIndex < len(p.cps)-1:  # not reaches the last point
            newList.append(p)
    return newList

# make sure no two points' either end share the same vertex 
def delOverlapPts(pointsList):
    ptsDict = {}
    for p1 in pointsList:
        # collect next frame segments
        x1, y1, z1 = p1.cps[p1.startIndex]
        x2, y2, z2 = p1.cps[p1.endIndex]
        segment = distance(x1, x2, y1, y2, z1, z2)
        if (x1, y1, z1) not in ptsDict and (x2, y2, z2) not in ptsDict:
            ptsDict[x1, y1, z1] = [p1, segment]
            ptsDict[x2, y2, z2] = [p1, segment]
    newList = set()
    for p, segLength in ptsDict.values():
        newList.add(p)
    return newList

# ----- for strokes -----
# initialize percentLimit amount of strokes from trianglesList
# (every stroke starts at centroid of every triangle)
def initializeStrokes(trianglesList, percentLimit):
    strokesList = []
    for t in trianglesList:
        percent = uniform(0, 1)
        if percent <= percentLimit:
            s = initializeStroke(t)
            strokesList.append(s)
    return strokesList

# helper function of above
# initialize of a stroke of input triangle t
# stroke's color is either random selected or purple based on data member
def initializeStroke(t):
    x, y, z = t.centroid
    if randomColorS:
        colorNum = np.random.rand(1,3)[0]
        color = vec(colorNum[0], colorNum[1], colorNum[2])
        s = Stroke(x, y, z, t, c=color)
    else:
        s = Stroke(x, y, z, t)
    t.stroke = s
    return s

# generate control points list for every stroke
# moving speed is specified by input moveSpeed (global variable)
# moving direction is based on interpolate pd of three vertices of curr triangle that stroke is on
def generateStroke(strokesList, triList, maxNumCP, moveSpeed):
    nActive = 1
    while nActive != 0: # break when all strokes' cps are complete
        nActive = 0
        for s in strokesList:
            if not s.done:
                # stop if > maxNumCPS
                if len(s.cps) > maxNumCP:
                    s.done = True
                else:
                    x, y, z = s.cps[-1] # get last control points
                    curr = np.array([x, y, z])
                    tri = s.tris[-1]    # get last triangle #trianglesList[x, y, z]
                    # if curr is the centroid / start point: must on tri
                    # otherwise curr is project on tri in last iteration
                    currPD, w1, w2, w3 = tri.computeTriPD(curr)
                    if w1<0 or w2<0 or w3<0:
                        weights = [(0,w1), (1,w2), (2,w3)]
                        weights = sorted(weights, key= lambda w: w[1],reverse = True)  # sort on w1/w2/w3
                        p1Index  = weights[0][0]
                        p2Index  = weights[1][0]
                        p3Index  = weights[2][0]   
                        p1 = tri.vertices[p1Index]
                        p2 = tri.vertices[p2Index]
                        p3 = tri.vertices[p3Index]
                        tri = findNextTri(p1, p2, p3, tri, triList, curr, trianglesList)
                        if tri != None:
                            s.addTri(tri)
                            curr = tri.projectPOntoTri(curr)
                            currPD, w1, w2, w3 = tri.computeTriPD(curr)
                            s.triChange = True
                        else:
                            s.done = True
                            continue
                    curr += currPD
                    curr = tri.projectPOntoTri(curr)
                        
                    '''
                    # if curr point is too close to any of exist cps in curr triangle
                    if tri.isTooClose(curr, minDist):
                        s.done = True
                        if s.triChange == True:
                            s.deleteLastTri()
                            s.triChange = False
                    else:
                    '''
                    # COPY curr and store into stroke
                    x, y, z = curr
                    s.addCP(np.array([x, y, z]))
                    tri.addCP(np.array([x, y, z]))
                    nActive += 1

# find next triangles from neighbor triangles of given three vertices
def findNextTri(p1, p2, p3, currTri, triList, curr, trianglesList):
    tri = checkNeighborTri(p1, triList, curr)
    if tri == None:
        tri = checkNeighborTri(p2, triList, curr)
    if tri == None:
        tri = checkNeighborTri(p3, triList, curr)
    return tri
    
# check if location curr is on any neighbor triangles of input Point p 
def checkNeighborTri(p, triList, curr):
    neighborTriList = triList[p]
    for t in neighborTriList:
        temp = t.projectPOntoTri(curr)
        currPD, w1, w2, w3 = t.computeTriPD(temp)
        if w1 >= 0 and w2 >= 0 and w3 >= 0:
            return t
    return None

# after complete control points list of all strokes
# if list has max length (== maxNumCP + 1): random cut off some points
# if list is too short (< minNumCP): get rid of this stroke
def adjustStroke(strokesList):
    tempList = []
    for s in strokesList:
        if len(s.cps) >= 2:
            tempList.append(s)
    return tempList

# cluster strokes by cluster near triangles 
def clusterStrokes(pointsList, triList):
    resetPts(allPoints)
    colorUsed   = {}
    clusterList = {}
    # --------------
    # start by random pick one point from pointsList dictionary
    loc, p1 = random.choice(list(pointsList.items()))
    while p1 != None:
        if p1 in triList.keys():
            clusterList[p1] = clusterP(p1, triList, pointsList, colorUsed)
            p1.done = True
            x1, y1, z1 = p1.initial
            maxDist = 0
            p1 = None
            for p2 in pointsList.values():
                if not p2.done:
                    x2, y2, z2 = p2.initial
                    dist = distance(x1, x2, y1, y2, z1, z2)
                    if maxDist < dist:
                        maxDist = dist
                        p1 = p2
        else:
            p1.done = True
            while p1.done:
                loc, p1 = random.choice(list(pointsList.items()))
        
    # -------------
    #for p in pointsList.values():
    #    if not p.done:
    #        if p in triList.keys():
    #            clusterList[p] = clusterP(p, triList, pointsList, colorUsed)
    #            p.done = True
    #        else:
    #            p.done = True
    for c, v in clusterList.iteritems():
        print c, len(v)
    return clusterList

# help function of above: complete one cluster
def clusterP(p, triList, pointsList, colorUsed):
    global clusterDepth
    colorNum = np.random.rand(1,3)[0]
    # if this color has been used, generate another random color
    while (colorNum[0], colorNum[1], colorNum[2]) in colorUsed.keys():
        colorNum = np.random.rand(1,3)[0]
    color = vec(colorNum[0], colorNum[1], colorNum[2])
    colorUsed[colorNum[0], colorNum[1], colorNum[2]] = color
    return clusterOneDepth(p, triList, pointsList, color, clusterDepth)


# help function of above: complete one depth/edge/circle
def clusterOneDepth(p, triList, pointsList, color, depth):
    clusterList = set()
    returnP = None
    if depth > 0:
        triangles = triList[p]
        for t in triangles:
            t.color = color
            clusterList.add(t)
            p1, p2, p3 = t.vertices
            clusterList.update(clusterOneDepth(p1, triList, pointsList, color, depth-1))
            p1.done = True
            clusterList.update(clusterOneDepth(p2, triList, pointsList, color, depth-1))
            p2.done = True
            clusterList.update(clusterOneDepth(p3, triList, pointsList, color, depth-1))
            p3.done = True
    return clusterList

# for each cluster, pick the stroke that is closest to its centroid
# and generate the strokesList
def clusterPickStroke(clusterList, triList):
    strokesList = []
    for k, tris in clusterList.iteritems():    # center point --> all triangles around it
        mDist = float('inf')
        tri = None
        x1, y1, z1 = k.initial
        for t in tris:
            x2, y2, z2 = t.centroid
            dist = distance(x1, x2, y1, y2, z1, z2)
            if dist < mDist:
                mDist = dist
                tri = t
        '''    
        # pick the stroke that has longest segment (most number of cps) for each cluster
        for t in v: 
            if t.stroke != None and len(t.stroke.cps) > maxLen:
                maxLen = len(t.stroke.cps)
                s = t.stroke
        '''
        s = initializeStroke(tri)
        strokesList.append(s)

    '''
    # for testing color coded clusters
    for k, v in clusterList.iteritems():
        for t in v:
            s = initializeStroke(t)
            s.color = t.color
            strokesList.append(s)
    '''
    return strokesList

# for some triangles that does not belong to any clusters:
# random pick one of its neighbor triangle's color (if exists) and set as its own color
def adjustColor(trianglesList, triList):
    print len(trianglesList)
    for t in trianglesList:
        if t.color == None:
            colorList = []
            for v in t.vertices:
                neighborTriangles = triList[v]
                for nt in neighborTriangles:
                    if nt.color != None:
                        colorList.append(nt.color)
                i = randint(0, len(colorList)-1)
                t.color = colorList[i]

# launch is called:
# launch every stroke in the origianl strokesList
# so that each stroke has a dot line looking
def addNewStrokes(strokesList, originalStrokes):
    for s in originalStrokes:
        newS = s.copy()
        strokesList.append(newS)
    return strokesList

# after every step drawing
# get rid of all strokes that reaches the end of its segment
def delFinishedStrokes(strokesList):
    newList = []
    for s in strokesList:
        if s.endIndex < len(s.cps)-1:  # not reaches the last point
            newList.append(s)
    return newList

# ---------- drawing functions ----------
# clear all auto drawing
def clearClockEvent():
    pyglet.clock.unschedule(autoDrawForward)
    #pyglet.clock.unschedule(autoDrawBackward)
    pyglet.clock.unschedule(autoDrawPt)

# ----- for strokes move -----
# continue move forward for stroke drawing
def autoDrawForward(dt=None):
    moveForward()
    draw()
'''
# continue move backward for stroke drawing
def autoDrawBackward(dt=None):
    moveBackward(strokesList)
    draw()
'''
# move one step forward for stroke drawing
def moveForward():
    global launchS, originalStrokes, strokesList
    for s in strokesList:
        s.stepForwardSegment()
    launchS += 1
    if launchS == 3:
        launchS = 0
        strokesList = addNewStrokes(strokesList, originalStrokes)
    strokesList = delFinishedStrokes(strokesList)
'''
# move one step backward for stroke drawing
def moveBackward(strokesList):
    for s in strokesList:
        s.stepBackSegment()
'''
# ----- for points move -----
# continue move forward for points drawing
def autoDrawPt(dt=None):
    global pointsList, drawingList
    draw()
    pointsList, drawingList = ptForward(pointsList, allPoints, originalPoints)
      
# move one step forward for points drawing
def ptForward(pointsList, allPoints, originalPoints):
    global launchP
    for p in pointsList:
        p.drawSegment()
        p.stepForwardSegment()
    launchP += 1
    if launchP == 3:
        launchP = 0
        pointsList = addNewPts(pointsList, originalPoints)
    pointsList = delFinishedPts(pointsList)
    drawingList = delOverlapPts(pointsList)
    return pointsList, drawingList

# ----- for general drawing -----
@win.event
# based on different switches, continue or step draw stroke/point/surface and save current frame
def on_draw():
    global isMove, count, drawPrev, pointsList, allPoints, launch, triList, strokesList, originalStrokes, drawingList
    '''
    if drawStroke and drawPrev:    # did not save backward image right now
        moveBackward(strokesList)
        drawPrev = False'''
    if isMove:
        if drawStroke:
            moveForward()
        if drawPoint:
            pointsList, drawingList = ptForward(pointsList, allPoints, originalPoints)
        if save:
            # save current frame
            pyglet.image.get_buffer_manager().get_color_buffer().save(shape+str(count).zfill(3)+'.png')
            count += 1
        isMove = False
    draw()

# resize viewing point,
# load translation matrix if need.
# adjust x, y, z direction rotation and translation
# and draw surface, points and strokes direction lines as needed
def draw():
    global drawingList, xAngle, yAngle, zAngle, zoom, shape, minX, maxX, minY, maxY, minZ, maxZ, pointsList, allPoints
    resize(minX, maxX, minY, maxY, minZ, maxZ)
    if loadMat:
        f = file("data/"+location+"/"+shape+".txt", "r")
        for i, line in enumerate(f.readlines()):
            transformMat[i] = float(line)
        glLoadMatrixf(transformMat)
    
    # adjust translation, viewing angles & zoom
    glTranslatef(tx, ty, 0)
    glRotatef(xAngle, 1, 0, 0)
    glRotatef(yAngle, 0, 1, 0)
    glRotatef(zAngle, 0, 0, 1)
    glScalef(zoom, zoom, zoom)

    if drawDots:
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, purple)
        glBegin(GL_POINTS)
        for p in originalPoints:
            x, y, z = p.initial
            glVertex3f(x, y, z)
        glEnd()
    if drawShape != None:
        drawTriSurface(trianglesList)
    if drawStroke:
        drawDirStroke()
    if drawPoint:  # move points
        drawDirPt(drawingList)
    glFlush()

# draw triangle/line surface and light based on each triangle's normal
def drawTriSurface(trianglesList):
    global drawShape
    if drawShape == "tri":
        gDraw = GL_TRIANGLES
    elif drawShape == "line":
        gDraw = GL_LINES
    
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, greens)
    #glMaterialfv(GL_BACK,  GL_DIFFUSE, purple)
    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(3, 1)
    for t in trianglesList:
        glBegin(gDraw)
        x, y, z = -t.norm
        glNormal3f(x, y, z)
        if t.vertices != None:
            x1, y1, z1 = t.vertices[0].initial
            x2, y2, z2 = t.vertices[1].initial
            x3, y3, z3 = t.vertices[2].initial
            #print x1, x2, x3, y1, y2, y3, z1, z2, z3
            #break
        else:
            x1, y1, z1 = t.locations[0]
            x2, y2, z2 = t.locations[1]
            x3, y3, z3 = t.locations[2]
            #print x1, x2, x3, y1, y2, y3, z1, z2, z3
            #break
        
        glVertex3f(x1, y1, z1)
        glVertex3f(x2, y2, z2)
        glVertex3f(x3, y3, z3)
        glVertex3f(x1, y1, z1)

        glEnd()
    glDisable(GL_POLYGON_OFFSET_FILL)

# draw one frame stroke lines
def drawDirStroke():
    glLineWidth(2)
    for s in strokesList:
        s.drawSegment()

# draw one frame point pd lines
def drawDirPt(pointsList):
    glLineWidth(1)
    for p in pointsList:
        p.drawSegment()

# ----- helper function -----
def set2list(ptSet):
    ptDir = []
    for p in ptSet:
        x, y, z = p.initial
        ptDir.append(p)
    return ptDir

# input 3 strings and output their corresponding float numbers
def str2float(x, y, z):
        return float(x), float(y), float(z)

# input 3 strings and output their corresponding integer numbers
def str2int(x, y, z):
        return int(x), int(y), int(z)

# input 3 strings and output their corresponding float numbers
def distancePt(p1, p2):
    x1, y1, z1 = p1.initial
    x2, y2, z2 = p2.initial
    return distance(x1, x2, y1, y2, z1, z2)

# compute and return 3D distance between point (x1, y1, z1) and (x2, y2, z2)
def distance(x1, x2, y1, y2, z1, z2):
        return np.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

# normalize and return input 3D vector
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
    result = np.array([x, y, z])
    return result

# add addList to the end of the majorList 
def appendList(majorList, addList):
    for k ,v in addList.iteritems(): 
        majorList[k] = v
    return majorList

# append X Y Z lists by adding x, y, z lists at the end
def npAppend(x, y, z, X, Y, Z):
    X = np.append(X, x)
    Y = np.append(Y, y)
    Z = np.append(Z, z)
    return X, Y, Z
       
# ---------- class ----------
class Point:
    def __init__(self, x, y, z, cur1=None, d1x=None, d1y=None, d1z=None, cur2=None, d2x=None, d2y=None, d2z=None, c=yellow):
        self.d1      = np.array([d1x, d1y, d1z])
        self.d2      = np.array([d2x, d2y, d2z])
        self.kMax    = cur1
        self.kMin    = cur2
        #self.thick   = 1
        self.color   = c
        self.initial = np.array([x, y, z])
        self.cps = []
        self.addCP(self.initial)
        self.done    = False    # is clustered or not
        self.initializeSegmentIndex()

    # copy and return current point
    def copy(self):
        x, y, z = self.initial
        d1x, d1y, d1z = self.d1
        d2x, d2y, d2z = self.d2 
        copyPt = Point(x, y, z, self.kMax, d1x, d1y, d1z, self.kMin, d2x, d2y, d2z, c = self.color)
        for cp in self.cps:
            copyPt.addCP(cp)
        return copyPt

    # add p into current point's cp list
    def addCP(self, p):
        self.cps.append(p)

    # compute the length/curvature of the pd line of current point
    def computeLength(self):
        global fixLength, length
        if fixLength:
            if self.kMax > 0:
                self.cur1 = length
            else:
                self.cur1 = -length
            if self.kMin > 0:
                self.cur2 = length
            else:
                self.cur2 = -length
        else:
            self.cur1 = np.abs(self.kMax * moveSpeed)
            self.cur2 = np.abs(self.kMin * moveSpeed)
        self.d1 = self.d1 * self.cur1
        self.d2 = self.d2 * self.cur2
        #self.reset()

    # draw pd line of current point
    def drawSegment(self):
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.color)
        glBegin(GL_LINES)
        ix, iy, iz = self.cps[self.startIndex]
        fx, fy, fz = self.cps[self.endIndex]
        glVertex3f(ix, iy, iz)
        glVertex3f(fx, fy, fz)
        glEnd()

    # move one step to the next segment 
    def stepForwardSegment(self):
        self.endIndex += 2
        if self.endIndex < len(self.cps):
            self.startIndex += 2
    
    # set segment back to its initial location
    def initializeSegmentIndex(self):
        self.startIndex = 0
        self.endIndex   = 1 #len(self.cps) / 4

class Triangle:
    def __init__(self, p1, p2, p3):
        self.vertices = (p1, p2, p3)
        self.cps = []
        self.color = None
        self.stroke = None
        self.computeCentroid()
        #self.computePlaneEq()
        self.calcNormal()

    # calculate normal of current triangle
    def calcNormal(self):
        p1Loc = self.vertices[0].initial
        p2Loc = self.vertices[1].initial
        p3Loc = self.vertices[2].initial
        v1 = p1Loc - p2Loc
        v2 = p2Loc - p3Loc
        self.norm = normalize(np.cross(v2, v1))

    # project given point p onto current triangle surface
    def projectPOntoTri(self, p):
        p1 = self.vertices[0].initial
        p2 = self.vertices[1].initial
        p3 = self.vertices[2].initial
        u = p2 - p1
        v = p3 - p1
        n = np.cross(u, v)
        w = p - p1
        den = np.dot(n, n)
        gamma = np.dot(np.cross(u, w), n) / den
        beta  = np.dot(np.cross(w, v), n) / den
        alpha = 1 - gamma - beta
        return alpha * p1 + beta * p2 + gamma * p3

    # return True if current triangle is a segment
    #        False otherwise
    def isDegenerate(self):
        t1 = self.vertices[0].initial
        t2 = self.vertices[1].initial
        t3 = self.vertices[2].initial
        v0 = np.subtract(t2, t1)
        v1 = np.subtract(t3, t1)
        d00 = np.dot(v0, v0)
        d11 = np.dot(v1, v1)
        d01 = np.dot(v0, v1)

        return d00 * d11 - d01 * d01 == 0    

    # compute the centroid of current triangle
    def computeCentroid(self):
        x1, y1, z1 = self.vertices[0].initial
        x2, y2, z2 = self.vertices[1].initial
        x3, y3, z3 = self.vertices[2].initial

        cx = (x1 + x2 + x3) / 3
        cy = (y1 + y2 + y3) / 3
        cz = (z1 + z2 + z3) / 3

        self.centroid = (cx, cy, cz)

    # compute input point p's pd by calculate weights of pds of three vertices of current triangle
    def computeTriPD(self, p):
        t1 = self.vertices[0]
        t2 = self.vertices[1]
        t3 = self.vertices[2]
        p1 = t1.initial
        p2 = t2.initial
        p3 = t3.initial
        # calculate weight percent for pd0, 1, 2
        v0 = np.subtract(p2, p1)
        v1 = np.subtract(p3, p1)
        v2 = np.subtract(p, p1)
        d00 = np.dot(v0, v0)
        d11 = np.dot(v1, v1)
        d01 = np.dot(v0, v1)
        d20 = np.dot(v2, v0)
        d21 = np.dot(v2, v1)
        den =  d00 * d11 - d01 * d01    
        w1 = (d11*d20-d01*d21)/den 
        w2 = (d00*d21-d01*d20)/den 
        w3 = 1-w1-w2

        pd1 = t1.pd
        pd2 = t2.pd
        pd3 = t3.pd
        return pd1 * w1 + pd2 * w2 + pd3 * w3, w1, w2, w3

    # add input point p into cps list
    def addCP(self, p):
        self.cps.append(p)
    '''
    # compute the plane equation of current triangle surface
    def computePlaneEq(self):
        p1 = self.vertices[0].initial
        p2 = self.vertices[1].initial
        p3 = self.vertices[2].initial

        v1 = p3 - p1
        v2 = p2 - p1

        cp = np.cross(v1, v2)
        self.a, self.b, self.c = cp
        self.d = np.dot(cp, p3)

    # check if input point p is on current triangle surface
    def isOnSurface(self, p):
        x, y, z = p
        diff = self.a * x + self.b * y + self.c * z - self.d
        return diff <= 1e-6

    def isTooClose(self, p, minDist):
        if len(self.cps) > 0:
            x1, y1, z1 = p
            for cp in self.cps:
                x2, y2, z2 = cp
                if distance(x1, x2, y1, y2, z1, z2) < minDist:
                    return True
        return False
    '''

class Stroke:
    def __init__(self, x, y, z, tri, c=purple):
        self.initial   = np.array([x, y, z])
        if not randomColorS or tri.color == None:
            self.color = c
        else:
            self.color = tri.color
        self.done      = False
        self.triChange = False
        
        self.cps = []
        self.addCP(np.array([x, y, z]))
        self.tris = []
        self.addTri(tri)
        self.initializeSegmentIndex()

    # copy and return current stroke
    def copy(self):
        x, y, z = self.initial
        copyStroke = Stroke(x, y, z, self.tris[0], self.color)
        for cp in self.cps:
            copyStroke.addCP(cp)
        for t in self.tris[1:]:
            copyStroke.addTri(t)
        copyStroke.initializeSegmentIndex()
        return copyStroke

    # add input point p into current stroke's cps list
    def addCP(self, p):
        self.cps.append(p)

    # add input triangle into current stroke's passed triangles list
    def addTri(self, tri):
        self.tris.append(tri)
        
    # delete the last triangle in the tris list
    def deleteLastTri(self):
        del self.tris[-1]

    # resize cps list:
    # if list has max length (== maxNumCP + 1): random cut off some points
    # (the new list must contains more than minNumCP points)
    def resizeCP(self):
        global maxNumCP
        if len(self.cps) == maxNumCP + 1:
            n = 0
            while n < minNumCP:
                percent = uniform(0, 1)
                n = int(round(len(self.cps) * percent))
            self.cps = self.cps[0:n]

    # return the middle point element in the cps list
    def middlePoint(self):
        middleIndex = len(self.cps) / 2
        return self.cps[middleIndex]

    # first time set current stroke's start, end and calculate diff
    def initializeSegmentIndex(self): 
        self.startIndex = 0
        self.endIndex   = 2

    # move current stroke one step forward
    def stepForwardSegment(self):
        self.endIndex += 1
        
        if self.endIndex < len(self.cps):
            self.startIndex += 1

    '''
    # move current stroke one step backward
    def stepBackSegment(self):
        self.startIndex -= 1
        
        if self.startIndex >= 0:
            self.endIndex -= 1
        else:
            self.endIndex = len(self.cps) - 1
            self.startIndex = self.endIndex - self.diff
    '''

    # draw current stroke's current segment
    def drawSegment(self):
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.color)
        
        i = self.startIndex
        f = self.endIndex-1
        while i < f: 
            iniP = self.cps[i]
            finP = self.cps[i+1]
            glBegin(GL_LINES)
            glVertex3f(iniP[0], iniP[1], iniP[2])
            glVertex3f(finP[0], finP[1], finP[2])
            glEnd()
            
            i += 1

# following 2 classes are used for pre-generate
class SimpleTriangle:
    def __init__(self, nx, ny, nz):
        self.norm = np.array((nx, ny, nz))
        self.locations = []
        self.vertices = None    # use to distingush Triangle & simpleTriangle at drawTriSurface

    def addLoc(self, x, y, z):
        loc = np.array((x, y, z))
        self.locations.append(loc)

class SimplePS: # point or stroke
    def __init__(self, r, g, b):
        self.cps = []
        self.color = vec(r, g, b)
        self.initializeSegmentIndex()

    def addCP(self, x, y, z):
        p = np.array((x, y, z))
        self.cps.append(p)

    def copy(self):
        r, g, b = self.color
        copyPS = SimplePS(r, g, b)
        for cp in self.cps:
            x, y, z = cp
            copyPS.addCP(x, y, z)
        return copyPS

    def drawSegment(self):
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.color)
        glBegin(GL_LINES)
        ix, iy, iz = self.cps[self.startIndex]
        fx, fy, fz = self.cps[self.endIndex]
        glVertex3f(ix, iy, iz)
        glVertex3f(fx, fy, fz)
        glEnd()

    def initializeSegmentIndex(self):
        self.startIndex = 0
        self.endIndex   = 1

    def stepForwardSegment(self):
        self.endIndex += 2
        if self.endIndex < len(self.cps):
            self.startIndex += 2

# ---------- test ----------
if loadPre: # load pre-generating file from previous
    trianglesList, pointsList, strokesList, minX, maxX, minY, maxY, minZ, maxZ = loadPrepare()
    print "load finish", len(trianglesList), len(pointsList), len(strokesList)
else:   # generate 
    minX, maxX, minY, maxY, minZ, maxZ, trianglesList, triList, allPoints, allPtsList = generatePts(fileName, randomColorP)
    print len(trianglesList)
    moveSpeed, length = computeLength(minX, maxX, minY, maxY, minZ, maxZ, trianglesList)
    computePtLength(allPoints)
    computePD(allPoints)    # continus PD
    print "Prepre compute done"
    # ----- points -----
    if loadPoints:
        pointsList = loadPts(allPtsList)
    else:
        pointsList = initializePtList(allPtsList, percentLimit)
    print len(pointsList)
    if isCluster:
        pointsList = clusterPts(allPoints, triList)
        pointsList = set2list(pointsList)
    resetPts(pointsList)
    print "cluster points done"
    generatePtCP(pointsList, allPoints, triList, ptLength)
    print "generate cp for points done"
    # ----- strokes -----
    if isCluster:
        clusterList = clusterStrokes(allPoints, triList)
        adjustColor(trianglesList, triList)
        strokesList = clusterPickStroke(clusterList, triList)
    else:   # not cluster
        strokesList = initializeStrokes(trianglesList, percentLimit)
    print "cluster strokes done"
    generateStroke(strokesList, triList, maxNumCP, moveSpeed)
    minDist = computeMinDistance(strokesList)
    strokesList = adjustStroke(strokesList)
    print "generate cp for strokes done"
    # saving pre-generate information
    savePrepare(trianglesList, pointsList, strokesList)
    print "saving done"
for p in pointsList:
    originalPoints.append(p.copy())
drawingList = pointsList
for s in strokesList:
    originalStrokes.append(s.copy())

setup()
dt = pyglet.clock.tick()    # setup clock
pyglet.app.run()
