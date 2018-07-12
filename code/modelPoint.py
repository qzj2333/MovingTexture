# modelPoint.py

# color
#glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, yellow)
#glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, yellow)
#glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, greens)
#glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, high_shine)

from random          import uniform
from pygletUtils     import *
from sklearn.cluster import AgglomerativeClustering

# data members
trianglesList = {}
pointsList = {}
nCluster = 0

'''
minWidth = 1
maxWidth = 5
minX = float('inf')
minY = float('inf')
minZ = float('inf')
maxX = -float('inf')
maxY = -float('inf')
maxZ = -float('inf')
minCur1  = float('inf')
minCur2  = float('inf')
maxCur1  = 0
maxCur2  = 0
'''

# ---------- prepare function ----------
def initializePtList(allPoints, percentLimit):
    pointsList = {}
    for loc, p in allPoints.iteritems():
        percent = uniform(0, 1)
        if percent <= percentLimit:
            pointsList[loc] = p
    return pointsList

def generateNewPts(percentLimit, allPoints):
    ptList = {}
    for p in allPoints.values():
        percent = uniform(0, 1)
        if percent <= percentLimit:
            x, y, z = p.initial
            ptList[x, y, z] = p
    return ptList

def findAllEndPt(pointsList, allPoints):
    newPointsList = {}
    for loc, p in pointsList.iteritems():
        end = findEndPt(p, allPoints)
        x, y, z = end.initial
        newPointsList[x, y, z] = end  
    return newPointsList

def findEndPt(currPt, allPoints):
    minDist = float("inf")
    endPt = None
    for p in allPoints.values():
        x1, y1, z1 = p.initial
        x2, y2, z2 = currPt.end
        dist = distance(x1, x2, y1, y2, z1, z2) #currPt.distance(p.start)  #distance(currPt.px, p.px, currPt.py, p.py, currPt.pz, p.pz)
        if dist < minDist and p != currPt:
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
    return pointsList

# ---------- win events ----------
def adjustTrans():
    global tx, ty, zoom, shape
    if shape == "ell":
        glTranslatef(0, ty, tx)
    elif shape == "cyl":
        glTranslatef(ty, 0, tx)
    elif shape == "sad":
        glTranslatef(tx, ty, 0)
    elif shape == "spline_16":
        glTranslatef(0, tx, ty)
    elif shape == "spline_25":
        glTranslatef(tx, 0, ty)
    elif shape == "spline_64_1":
        glTranslatef(0, -tx, ty)
    elif shape == "spline_64_2":
        glTranslatef(ty, -tx, 0)
    elif shape == "spline_64_5":
        glTranslatef(ty, -tx, 0)
    elif shape == "spline_0":
        glTranslatef(-tx, ty, 0)
    elif shape == "ell4":
        glTranslatef(-tx, ty, 0)
    elif shape == "cyl4":
        glTranslatef(tx, ty, 0)
    elif shape == "sad4":
        glTranslatef(-tx, ty, 0)
    elif shape == "flat4":
        glTranslatef(-tx, ty, 0)

@win.event
def on_key_press(symbol, modifiers):
    global zoom, xAngle, yAngle, zAngle, tx, ty, isMove, count, sprite, drawPrev
    if symbol == key.S: # S --> print & save to file: "shape".txt
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
    elif symbol == key.P:   # get next frame
        isMove = True
    elif symbol == key.L:   # get previous frame
        if count > 0:   # if count = 0: draw first image
            count -= 1
            drawPrev = True

@win.event
def on_draw():
    global pointsList, allPoints, nStep, nCluster, percentLimit, minCur1, maxCur1, minWidth, maxWidth, location
    if isMove:
        for i in range(0, nStep):
            print i
            
            if i > 0:
                pointsList = clusterPts(pointsList, allPoints, nCluster)
                #if not fixLength:
                #    ptLength(minCur1, maxCur1, moveSpeed, pointsList)
                #ptThick(minCur1, maxCur1, minWidth, maxWidth, direction, pointsList)
            
            draw()
            
            pointsList = findAllEndPt(pointsList, allPoints)
            ptList     = generateNewPts(percentLimit, allPoints)
            pointsList = appendList(pointsList, ptList)
            
            pyglet.image.get_buffer_manager().get_color_buffer().save(shape+str(i).zfill(3)+'.png')
    else:
        draw()
        pyglet.image.get_buffer_manager().get_color_buffer().save(shape+'.png')
     
def draw():
    global pointsList, xAngle, yAngle, zAngle, transformMat, location, drawSur, drawDire
    resize()
    if loadMat:
        f = file("data/"+location+"/"+shape+".txt", "r")
        for i, line in enumerate(f.readlines()):
            transformMat[i] = float(line)
        glLoadMatrixf(transformMat)

    adjustTrans()
    # adjust viewing angles & zoom
    glRotatef(xAngle, 1, 0, 0)
    glRotatef(yAngle, 0, 1, 0)
    glRotatef(zAngle, 0, 0, 1)
    glScalef(zoom, zoom, zoom)

    if drawSur:
        drawTriSurface(trianglesList)

    if drawDire:
        drawDir(pointsList)

    '''
    for p in pointsList.values():
        if moveDir == "1":
            x, y, z = p.end1
            newPtList[x, y, z] = Point(x, y, z)
            newPtList[float(nextP.x), float(nextP.y), float(nextP.z)] = nextP
        elif moveDir == "2":
            x, y, z = p.end2
            newPtList[x, y, z] = Point(x, y, z)
            #newPtList[float(nextP.x), float(nextP.y), float(nextP.z)] = nextP
    if moveDir != None:
        pointsList = newPtList
    '''
    glFlush()

    if isMove:
        newPtList = {}
        for p in pointsList.values():
            x, y, z = p.ptMove()
            newPtList[x, y, z] = p
        pointsList = newPtList

def drawDir(pointsList):
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, yellow)
    #glLineWidth(5)
    for p in pointsList.values():
        p.drawSegment()

# ---------- help function ----------
def appendList(majorList, addList):
    for k ,v in addList.iteritems(): 
        majorList[k] = v
    return majorList

def npAppend(x, y, z, X, Y, Z):
    X = np.append(X, x)
    Y = np.append(Y, y)
    Z = np.append(Z, z)
    return X, Y, Z

# ---------- test ----------
trianglesList, allPoints, triList = generatePts(length, percentLimit, fixLength, fileName, moveSpeed)
pointsList = initializePtList(allPoints, percentLimit)
nCluster = len(pointsList)

#ptThick(minCur1, maxCur1, minWidth, maxWidth, direction, pointsList)

setup()
pyglet.app.run()

#for t in trianglesList.values():
#    print t.isOnSurface(t.centroid)
