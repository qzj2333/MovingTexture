For model.py

- data members:
variables that can not be changed is listed in model.py. following are the variables that can be
changed:
-- shape: name of the 3D model that is going to use (all possible names appear in 
	  data file (use _____ in any of the ____.smfd file) )
-- percentLimit: increase --> more pd lines/strokes show up on every frame
-- fixLength:
   True  --> all pd lines/stroke segments have same length
             under this, if want stroke segment/pd lines longer, decrease denomitor of 
             length variable (on line 350+, inside method computeLength)
   False --> all pd lines/stroke segments' length related with the input curvature
             under this, if want stroke segment/pd lines longer, decrease denomitor of
	     moveSpeed variable (on line 350+, inside method computeLength)
-- useLength:
   "triangle" --> moveSpeed & length will related to the avg. side length of every triangle
   "xyzRange" --> moveSpeed & length will related to current shape's xyz range
-- isCluster & clusterDepth (only affect if isCluster == True):
   True  --> cluster BOTH strokes and pd lines
             choose the stroke/pd line that closest to each cluster's centroid
         clusterDepth: some int > 0 (min 1). increase will have less strokes/pd lines show on
                       the frame
   False --> clusterDepth will not affect the program
-- save: True --> every time press P to step one forward will also save current image
                  frame at the same location 
-- randomColorP/S: True  --> random color for every stroke / pd line
		   False --> yellow for all pd line, purple for all strokes
-- loadMat: see "About save/load transform matrix" below
-- loadPoints: see "About save/load points file" below
-- drawDots: True --> draw a dot on every point in pointsList (every picked point will draw pd line)
	              used to check the location of picked points (since when loadPoints == False,
	              points are randomly picked)
-- ptLength: the longest possible dots in every dot line for pd line drawing (the length of
             dot is depend on either "length" (if fixLength) or "moveSpeed" (if not fixLength))
             increase will longer dot lines
-- minNumCP & maxNumCP: 
min and max amount of dots in every dot line for stroke drawing (the length of dot is depend on 
either "length" (if fixLength) or "moveSpeed" (if not fixLength))
increase minNumCP will get rid of more shorter strokes but total number of strokes show on the 
frame will decrease
increase maxNumCP will longer the stroke dot lines
* minNumCP must >= 2 otherwise not able to draw a segment
-- minDistDen: get rid of strokes that two ends (of the whole dot line) are too close
               * increase will decrease the minDist (less strokes be deleted)

About save/load points file:
Save: 
1. set loadPoints == False
2. if want, set drawDots == True so that able to see all locations of all points that will be
   automatically generated (not necessary, saving progress still work if drawDots == False)
3. Program automatically random generate "percentLimit" amount of points and save it 
   into the file ____Points.txt where ___ is the 3D model name user choose. 
4. File will temp. save under same location as where model.py located
5. If user satisfied with points' choosing (as seen from the dots draw on the frame), move 
   ___Points.txt to data/points folder
Load: 
set loadPoint == True, program will load ____Points.txt from data/points
* if file that tring to load does not exist, program will throw some IO error exception
* if load points, then "percentLimit" and "ptLength" will not effect the program

About save/load transform matrix:
Save:
1. adjust the viewing on the frame use keyboard
2. press S to save current matrix (matrix variable will print out on python console window)
3. the saving transform matrix has form ___.txt where ___ is the 3D model user is using
   (the data member shape), and its saving location is the same location as model.py
4. Depend on current transform matrix is the global or local viewing of the 3D shape user
   choose, move the txt file to data/____(global or local)
Load:
set loadMat = True and location = "global" or "local"
* if file that tring to load does not exist, program will throw some IO error exception

About key-press:
S: print & save to file: "shape".txt
X/A: rotate drawing on x-direction
Y/B: rotate drawing on y-direction
Z/C: rotate drawing on z-direction
up/down/left/right: translate drawing
Shift + > / <: zoom in/out the drawing
P: one step forward stroke and/or point drawing
R: rest the frame (all moving pause)
.: continue move forward for stroke drawing
M: continue move forward for point drawing
D: display/hide stroke drawing
E: display/hide point drawing
F: switch surface drawing as: triangle surface --> line surface --> no surface

----------- other ----------
1. change pd to 2nd pd instead of 1st pd: go to method "computePD", set p.pd = p.d2
2. change stroke segment/pd lines' length, decrease denomitor of "length" (if fixLength) or
   denomitor of "moveSpeed" (if not fixLength) (both in method computeLength)