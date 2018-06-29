# model.py
# draw appropriate 3D shape using pyglet

import numpy as np
from utils         import *
from pyglet.gl     import *
from pyglet.window import *

# data members
shape    = "cyl"
fileName = "data/" + shape + ".smfd"
allPoints     = {}
allPtsList    = []
pointsList    = {}
trianglesList = []
winW = 800
winH = 600
win = pyglet.window.Window(winW, winH)
percentLimit = 0.3
moveSpeed    = 0.2
length = 0.1
nStep = 20
nCluster = 0
tx = 0.
ty = 0.
xAngle = 0.
yAngle = 0.
zAngle = 0.
zoom   = 1.
action = None
drawShape = "tri"
location = "local"

dir1      = True
dir2      = False
fixLength = True
moveDir   = None   # 1 / 2 / None 
save      = True
loadMat   = True
move      = True

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

def center():
    # normalize object to fit window
    # translate center to origin
    x = 0
    y = 0
    z = 0
    if shape == "ell":
        y = -0.5
        z = -3
    elif shape == "cyl":
        y = -1
        z = -2.5
    elif shape == "sad":
        y = -0.5
        z = -3
    elif shape == "spline_16":
        x = -0.5
        y = -0.5
        z = -3
    elif shape == "spline_25":
        x = -1
        y = -1
        z = -3
    elif shape == "spline_64_1":
        x = -0.5
        y = -0.7
        z = -2.5
    elif shape == "spline_64_2":
        x = -0.5
        y = -0.7
        z = -2.5
    elif shape == "spline_64_5":
        x = -0.5
        y = -0.7
        z = -2.5
    glTranslatef(x/2.0, y/2.0, z/2.0)
    
#@win.event
def on_resize():
    #Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)    # camera perspective
    glLoadIdentity() # reset camera
    gluPerspective(45.0, 1.*winW/winH, 1., 100.)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity() # reset camera

    return pyglet.event.EVENT_HANDLED
    
@win.event
def on_draw():
    global pointsList, allPoints, nStep, nCluster, percentLimit
    if move:
        for i in range(0, nStep):
            print i
            pointsList = clusterPts(pointsList, allPoints, nCluster)
            draw()
            pointsList = findAllEndPt(pointsList, allPoints)
            ptList     = generateNewPts(percentLimit, allPoints)
            pointsList = appendList(pointsList, ptList)
            pyglet.image.get_buffer_manager().get_color_buffer().save(shape+str(i).zfill(3)+'.png')
    else:
        #pointsList = clusterPts(pointsList, allPoints, nCluster)
        draw()
        
        
     
def draw():
    global pointsList, oldPointsList, fileName, drawShape, allPoints, xAngle, yAngle, zAngle, transformMat
    on_resize()
    center()
    if loadMat:
        f = file("data/"+location+"/"+shape+".txt", "r")
        for i, line in enumerate(f.readlines()):
            transformMat[i] = float(line)
        glLoadMatrixf(transformMat)

    glTranslatef(tx, ty, 0)
    glRotatef(xAngle, 0, 1, 0)
    glRotatef(yAngle, 1, 0, 0)
    glRotatef(zAngle, 0, 0, 1)
    #glScalef(zoom, zoom, zoom)

    if drawShape == "tri":
        gDraw = GL_TRIANGLES
    else:  #if draw == "line":
        gDraw = GL_LINES

    # color
    #glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, yellow)
    #glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, yellow)
    #glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, greens)
    #glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, high_shine)
    
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, greens)
    # triangle surface
    for t in trianglesList:
        glBegin(gDraw)
        p0 = t.t0
        p1 = t.t1
        p2 = t.t2
        p0Pos = np.array((p0.px, p0.py, p0.pz))
        p1Pos = np.array((p1.px, p1.py, p1.pz))
        p2Pos = np.array((p2.px, p2.py, p2.pz))
        v1 = p0Pos - p1Pos
        v2 = p1Pos - p2Pos
        norm = normalize(np.cross(v2, v1))
        x, y, z = norm
        glNormal3f(x, y, z)
        glVertex3f(p0.px,p0.py,p0.pz)
        glVertex3f(p1.px,p1.py,p1.pz)
        glVertex3f(p2.px,p2.py,p2.pz)

        glEnd()

    # assume: draw direction == moving direction
    newPtList = {}

    # principal direction lines
    if dir1:
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, yellow)
        for p in pointsList.values():
            glBegin(GL_LINES)
            glVertex3f(p.px,p.py,p.pz)
            pxNew = p.px+p.d1x
            pyNew = p.py+p.d1y
            pzNew = p.pz+p.d1z
            glVertex3f(pxNew, pyNew, pzNew)
            glEnd()
            
            if moveDir == "1":
                newPt = Point(pxNew, pyNew, pzNew)
                newPtList[pxNew, pyNew, pzNew] = newPt
               
    if dir2:
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, purple)
        for p in pointsList:
            glBegin(GL_LINES)
            glVertex3f(p.px,p.py,p.pz)
            pxNew = p.px+p.d2x
            pyNew = p.py+p.d2y
            pzNew = p.pz+p.d2z
            glVertex3f(pxNew, pyNew, pzNew)
            glEnd()

            if moveDir == "2":
                newPt = Point(pxNew, pyNew, pzNew)
                newPtList[pxNew, pyNew, pzNew] = newPt

    if moveDir != None:
        pointsList = newPtList
    glFlush()  

@win.event
def on_key_press(symbol, modifiers):
    if symbol == key.A: # A --> print & save to file: "shape".txt
        glGetFloatv(GL_MODELVIEW_MATRIX, saveTransformMat)
        print list(saveTransformMat)
        f = file(shape+".txt", "w")
        for num in list(saveTransformMat):
            print >> f, "%f" %(num)
        f.close()

@win.event
def on_mouse_press(x, y, button, modifiers):
    global action
    if (modifiers & key.MOD_SHIFT) and (modifiers & key.MOD_CTRL):
        action = "tran"
    elif (modifiers & key.MOD_NUMLOCK) and (modifiers & key.MOD_CAPSLOCK):
        action = "zoomOut"
    elif modifiers & key.MOD_SHIFT:
        action = "RotX"
    elif modifiers & key.MOD_CTRL:
        action = "RotY"
    elif modifiers & key.MOD_CAPSLOCK:
        action = "RotZ"
    elif modifiers & key.MOD_NUMLOCK:
        action = "zoomIn"
    else:
        action = None

@win.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global action, xAngle, yAngle, zAngle, tx, ty, zoom
    fx = dx / 20.
    fy = dy / 20.
    if action == "RotX":
        xAngle += np.sqrt(fx**2 + fy**2)
    elif action == "RotY":
        yAngle += np.sqrt(fx**2 + fy**2)
    elif action == "RotZ":
        zAngle += np.sqrt(fx**2 + fy**2)
    elif action == "tran":
        tx += fy / 15.
        ty += fx / 15.
    elif action == "zoomIn":
        zoom = np.sqrt(fx**2 + fy**2)
    elif action == "zoomOut":
        zoom = -np.sqrt(fx**2 + fy**2)
        
def main():
    global win, length, percentLimit, fixLength, fileName, allPoints, pointsList, trianglesList, moveSpeed, nCluster, clustersList
    nCluster = generatePts(length, percentLimit, fixLength, fileName, allPoints, allPtsList, pointsList, trianglesList, moveSpeed)
    setup()
    pyglet.app.run()

if __name__ == '__main__': 
    main()
