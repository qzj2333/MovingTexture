# pygletUtils.py

import numpy as np
from pyglet.gl     import *
from pyglet.window import *

# ---------- global variables ----------
tx = 0.
ty = 0.
xAngle = 0.
yAngle = 0.
zAngle = 0.
zoom   = 1.
winW = 800
winH = 800
win = pyglet.window.Window(winW, winH)

shape    = "spline_0"
fileName = "data/" + shape + ".smfd"
count = 0
percentLimit = 0.3
moveSpeed    = 0.15     # make it relate to triangle size
length       = 0.7     # fixed length of each curvature
nStep        = 50       # numer of steps/iterations/images generate to make gif
drawShape    = "tri"
location     = "pres/oblique"
fixLength    = True
save         = True
loadMat      = True
isMove       = True    # pause first frame after draw it
drawSur      = True
drawDire     = True
drawPrev     = False

# ---------- win events -----------
# data members:
# create ctypes arrays of floats:
def vec(*args):
    return (GLfloat * len(args))(*args)

light_diffuse  = vec(0.1, 0.5, 0.8, 1.0)
light_ambient  = vec(0.7, 0.7, 0.7, 1.0)
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

# initially, transform matrix is 4x4 identity matrix in 1D array
transformMat = vec(0.0, 0.0, 0, 0.0, 0.0, 0., 0.0, 0.0, 0, 0.0, 0., 0.0, 0.0, 0., -1., 1.0)
# get the current transformation in OpenGL into an array
# print it (or save to file) and use it as transformMat later
saveTransformMat = (GLfloat*16)()

def setup():
    glShadeModel(GL_SMOOTH)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)   # GL_FILL / GL_LINE
    glEnable(GL_NORMALIZE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CW)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glPointSize(4)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  light_diffuse)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT,  light_ambient)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glEnable(GL_LIGHT0)
    glLightModeli(GL_LIGHT_MODEL_COLOR_CONTROL, GL_SEPARATE_SPECULAR_COLOR)
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST) # 3D drawing work when sth. in front of sth. else
    glViewport(0, 0, winW, winH)

def resize():
    #global minX, maxX, minY, maxY, minZ, maxZ
    #Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)    # camera perspective
    glLoadIdentity() # reset camera
    gluPerspective(60.0, 1.*winW/winH, 0.1, 50.)
    #glOrtho(-maxX-1, maxX+1, -maxY-1, maxY+1, -100, 100)   #minZ-1, maxZ+1)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity() # reset camera

def drawTriSurface(trianglesList):
    global drawShape
    
    if drawShape == "tri":
        gDraw = GL_TRIANGLES
    else:  #if draw == "line":
        gDraw = GL_LINES
    
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, greens)
    for t in trianglesList.values():
        glBegin(gDraw)
        p1Loc = t.vertices[0].initial
        p2Loc = t.vertices[1].initial
        p3Loc = t.vertices[2].initial
        v1 = p1Loc - p2Loc
        v2 = p2Loc - p3Loc
        norm = normalize(np.cross(v2, v1))
        x, y, z = norm
        glNormal3f(x, y, z)

        x1, y1, z1 = p1Loc
        x2, y2, z2 = p2Loc
        x3, y3, z3 = p3Loc
        
        glVertex3f(x1, y1, z1)
        glVertex3f(x2, y2, z2)
        glVertex3f(x3, y3, z3)

        glEnd()

# ---------- prepare function ----------
def generatePts(length, percentLimit, fixLength, fileName, moveSpeed=1):
    f = file(fileName)

    allPoints     = {}
    allPtsList    = []
    trianglesList = {}
    triList       = {} 

    '''
    minCur1 = float('inf')
    minCur2 = float('inf')
    maxCur1 = 0
    maxCur2 = 0
    minX = float('inf')
    minY = float('inf')
    minZ = float('inf')
    maxX = -float('inf')
    maxY = -float('inf')
    maxZ = -float('inf')
    '''
    for line in f.readlines():
        if line.startswith("v"):
            # v
            v, x, y, z = line.split()
            x, y, z = str2float(x, y, z)
            '''
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
            '''
                
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
                    cur1 = np.abs(cur1)
                    cur2 = np.abs(cur2)
            '''
            if minCur1 > cur1:
                minCur1 = cur1
            if maxCur1 < cur1:
                maxCur1 = cur1
            if minCur2 > cur2:
                minCur2 = cur2
            if maxCur2 < cur2:
                maxCur2 = cur2
            '''
            currP = Point(x, y, z, cur1, cur1*direX, cur1*direY, cur1*direZ, cur2, cur2*dirX, cur2*dirY, cur2*dirZ)
            allPoints[x, y, z] = currP
            allPtsList.append(currP)
            
        else:   # line.startwith("t")
            t, p1Pos, p2Pos, p3Pos = line.split()
            p1Pos, p2Pos, p3Pos = str2int(p1Pos, p2Pos, p3Pos)

            p1 = allPtsList[p1Pos-1]
            p2 = allPtsList[p2Pos-1]
            p3 = allPtsList[p3Pos-1]

            
            tri = Triangle(p1, p2, p3)
            x, y, z = tri.centroid
            trianglesList[x, y, z] = tri

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
    return trianglesList, allPoints, triList

# ----- helper function -----
def str2float(x, y, z):
        return float(x), float(y), float(z)

def str2int(x, y, z):
        return int(x), int(y), int(z)

def distancePt(p1, p2):
    x1, y1, z1 = p1.start
    x2, y2, z2 = p2.start
    return distance(x1, x2, y1, y2, z1, z2)

def distance(x1, x2, y1, y2, z1, z2):
        return np.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

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

# ----------- class ----------
class Point:
    def __init__(self, x, y, z, cur1=None, d1x=None, d1y=None, d1z=None, cur2=None, d2x=None, d2y=None, d2z=None):
        self.d1     = np.array([d1x, d1y, d1z])
        self.d2     = np.array([d2x, d2y, d2z])
        self.c1     = cur1
        self.c2     = cur2
        #self.pd      = None
        #self.thick   = 1
        #self.cluster = None
        self.initial = np.array([x, y, z])
        self.reset()

    def drawSegment(self):
        glBegin(GL_LINES)
        ix, iy, iz = self.start
        fx, fy, fz = self.end
        if ix == fx and iy == fy and iz == fz:
            print "!"
        #print fx, fy, fz
        glVertex3f(ix, iy, iz)
        glVertex3f(fx, fy, fz)
        glEnd()

    def ptMove(self):
        x, y, z = self.end
        self.start = np.array([x, y, z])
        self.end = self.start + self.d1
        return x, y, z

    def reset(self):
        x, y, z = self.initial
        self.start   = np.array([x, y, z])
        self.end     = self.start+self.d1

class Triangle:
    def __init__(self, p1, p2, p3):
        self.vertices = (p1, p2, p3)
        self.cps = []
        self.computeCentroid()
        self.computePlaneEq()
        # print triangle side length
        #print distancePt(p1, p2), distancePt(p3, p2), distancePt(p1, p3), "!"

    '''
    # find other two points other than given point
    def find2p(self,  p):
        twoP = []
        for v in self.vertices:
            if p != v:
                twoP.append(v)
        return twoP
    '''

    def computeCentroid(self):
        x1, y1, z1 = self.vertices[0].start
        x2, y2, z2 = self.vertices[1].start
        x3, y3, z3 = self.vertices[2].start

        cx = (x1 + x2 + x3) / 3
        cy = (y1 + y2 + y3) / 3
        cz = (z1 + z2 + z3) / 3

        self.centroid = (cx, cy, cz)

    def computeTriPD(self, p):
        t1 = self.vertices[0]
        t2 = self.vertices[1]
        t3 = self.vertices[2]
        pd1 = t1.pd
        pd2 = t2.pd
        pd3 = t3.pd
        x1, y1, z1 = t1.start
        x2, y2, z2 = t2.start
        x3, y3, z3 = t3.start
        px, py, pz = p

        # calculate weight percent for pd0, 1, 2
        y23 = y2 - y3
        x32 = x3 - x2
        px3 = px - x3
        py3 = py - y3
        den = y23*(x1-x3) - x32*(y1-y3)
        if den == 0:
            w1 = 0
            w2 = 0
        else:
            w1 = (y23*px3 + x32*py3 ) / den
            w2 = ((y3-y1)*px3 + (x1-x3)*py3 ) / den
        w3 = 1-w1-w2
        return pd1 * w1 + pd2 * w2 + pd3 * w3, w1, w2, w3

    def addCP(self, p):
        self.cps.append(p)
        
    def computePlaneEq(self):
        p1 = self.vertices[0].start
        p2 = self.vertices[1].start
        p3 = self.vertices[2].start

        v1 = p3 - p1
        v2 = p2 - p1

        cp = np.cross(v1, v2)
        self.a, self.b, self.c = cp
        self.d = np.dot(cp, p3)

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
