# modelStroke.py
# draw appropriate 3D shape using pyglet

from random      import uniform
from pygletUtils import *

# color
#glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, yellow)
#glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, yellow)
#glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, greens)
#glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, high_shine)

# data members
maxNumCP  = 100      # max number of control points/steps in a stroke
maxNumTri = 50       # max number of triangles one stroke can pass
minDist   = moveSpeed / 10   # min distance any two strokes can have between
trianglesList = {}

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
    '''
    # step version
    global isMove, count, sprite, drawPrev

    if drawPrev:    # did not save backward image right now
        moveBackward(strokesList)
        drawPrev = False

    draw()

    while isMove: # initially isMove = false
        moveForward(strokesList)
        draw()
        # save current frame
        #pyglet.image.get_buffer_manager().get_color_buffer().save(shape+str(count).zfill(3)+'.png')

        count += 1
        isMove = False # pause current frame
    '''
    # auto version
    global nStep, shape
    for i in range(0, nStep):
        print i
        draw()
        moveForward(strokesList)
        pyglet.image.get_buffer_manager().get_color_buffer().save(shape+str(i).zfill(3)+'.png')

def draw():
    global xAngle, yAngle, zAngle, zoom, shape

    
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
        drawDir()
    glFlush()

def drawDir():
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, yellow)
    for s in strokesList:
        s.drawSegment()

def initializeStrokes(trianglesList, percentLimit):
    strokesList = []
    for c in trianglesList.keys():
        # apply percent limit
        percent = uniform(0, 1)
        if percent <= percentLimit:
            x, y, z = c
            s = Stroke(x, y, z, trianglesList[c])
            strokesList.append(s)
    return strokesList

def generateStroke(strokesList, triList, maxNumTri, maxNumCP, minDist, moveSpeed):
    nActive = 1
    while nActive != 0: # break when all strokes' cp are complete
        nActive = 0
        for s in strokesList:
            if not s.done:
                # stop if > maxNumTri or maxNumCPS
                if len(s.tris) > maxNumTri or len(s.cps) > maxNumCP:
                    s.done = True
                else:
                    x, y, z = s.cps[-1] # get last control points
                    curr = np.array([x, y, z])
                    tri = s.tris[-1]    # get last triangle #trianglesList[x, y, z]

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
                        tri = findNextTri(p1, p2, p3, tri, triList, curr)

                        if tri != None:
                            s.addTri(tri)
                            currPD, w1, w2, w3 = tri.computeTriPD(curr)
                            s.triChange = True
                        else:
                            s.done = True
                            continue
                    
                    curr += currPD * moveSpeed

                    # if curr point is too close to any of exist cps in curr triangle
                    if tri.isTooClose(curr, minDist):
                        s.done = True
                        if s.triChange == True:
                            s.deleteLastTri()
                            s.triChange = False
                    else:
                        # COPY curr and store into stroke
                        x, y, z = curr
                        s.addCP(np.array([x, y, z]))
                        tri.addCP(np.array([x, y, z]))
                        nActive += 1

def findNextTri(p1, p2, p3, currTri, triList, curr):
    tri = checkNeighborTri(p1, triList, curr)
    if tri == None:
        tri = checkNeighborTri(p2, triList, curr)
    if tri == None:
        tri = checkNeighborTri(p3, triList, curr)    
    return tri


def checkNeighborTri(p, triList, curr):
    neighborTriList = triList[p]
    
    for t in neighborTriList:
        currPD, w1, w2, w3 = t.computeTriPD(curr)
        if w1 >= 0 and w2 >= 0 and w3 >= 0:
            return t
    return None

def moveForward(strokesList):
    for s in strokesList:
        s.updateSegment()

def moveBackward(strokesList):
    for s in strokesList:
        s.stepBackSegment()
    
def computePD(pointsList):
    #reference = []
    for p in pointsList.values():
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
        p.pd = p.d1 #ppd
        #reference = ppd
       
# ---------- class ----------
class Stroke:
    def __init__(self, x, y, z, tri):
        self.initial   = np.array([x, y, z])
        self.done      = False
        self.triChange = False
        
        self.cps = []
        self.addCP(np.array([x, y, z]))

        self.tris = []
        self.addTri(tri)

    def addCP(self, p):
        self.cps.append(p)

    def addTri(self, tri):
        self.tris.append(tri)

    def deleteLastTri(self):
        del self.tris[-1]

    # do this after cps list is completed
    def initializeSegmentIndex(self):
        self.startIndex = 0
        self.endIndex   = min( len(self.cps)/3, 7 )

    def updateSegment(self):
        self.endIndex += 1
        
        if self.endIndex < len(self.cps):
            self.startIndex += 1
        else:
            self.initializeSegmentIndex()

    def stepBackSegment(self):
        self.startIndex -= 1
        if self.startIndex >= 0:
            self.endIndex -= 1
        else:
            self.initializeSegmentIndex()

    def drawSegment(self):
        i = self.startIndex
        f = self.endIndex

        while i < f: 
            iniP = self.cps[i]
            finP = self.cps[i+1]
            glBegin(GL_LINES)
            glVertex3f(iniP[0], iniP[1], iniP[2])
            glVertex3f(finP[0], finP[1], finP[2])
            glEnd()
            i += 1

# ---------- test ----------  
trianglesList, allPoints, triList = generatePts(length, percentLimit, fixLength, fileName, moveSpeed)
strokesList = initializeStrokes(trianglesList, percentLimit)
computePD(allPoints)    # continus PD

generateStroke(strokesList, triList, maxNumTri, maxNumCP, minDist, moveSpeed)
for s in strokesList:
    s.initializeSegmentIndex() 

#ptThick(minCur1, maxCur1, minWidth, maxWidth, direction, pointsList)

setup()
pyglet.app.run()

#for t in trianglesList.values():
#    print t.isOnSurface(t.centroid)
