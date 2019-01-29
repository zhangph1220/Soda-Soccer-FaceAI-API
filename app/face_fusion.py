# -*-coding:utf-8-*-
import os, cv2, math, sys, time, dlib
import numpy as np
import face_recognition as fr
from PIL import Image
from app import saved_pics_path


PREDICTOR_PATH = "app/static/shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(PREDICTOR_PATH)



class TooManyFaces(Exception):
    pass

class NoFaces(Exception):
    pass

def getLandmarks(pic):
    img = cv2.imdecode(np.fromfile(pic, dtype=np.uint8), cv2.IMREAD_COLOR)
    img = cv2.resize(img, (img.shape[1], img.shape[0]))
    rects = detector(img, 1)
    
    if len(rects) == 0:
        raise NoFaces("no faces")

    target_rects = rects[0]
    if len(rects) > 1:
        pic_name = pic.split('/')[-1]
        if pic_name[:8] == 'template':
            with open(pic + '.txt', 'r') as f:
                target_rects = f.readline().strip()
            print(target_rects)
            for i in rects:
                if str(i) == target_rects:
                    target_rects = i
                    break

        else:
            raise TooManyFaces("too many faces")

    return np.matrix([[p.x, p.y] for p in predictor(img, target_rects).parts()]).tolist()

# Read points from pictures
def readPoints(pic1, pic2):
    # Create an array of array of points.
    pointsArray = []

    l1 = getLandmarks(pic1)
    l2 = getLandmarks(pic2)
    
    pointsArray.append(l1)
    pointsArray.append(l2)
   
    return pointsArray

# Read all jpg images in folder.
def readImages(pic1, pic2):
    #Create array of array of images.
    imagesArray = []
    
    # img1 = cv2.imread(pic1)
    # img2 = cv2.imread(pic2)
    img1 = cv2.imdecode(np.fromfile(pic1, dtype=np.uint8), cv2.IMREAD_COLOR)
    img2 = cv2.imdecode(np.fromfile(pic2, dtype=np.uint8), cv2.IMREAD_COLOR)
    
    # Convert to floating point
    img1 = np.float32(img1) / 255.0
    img2 = np.float32(img2) / 255.0
   
    # Add to array of images
    imagesArray.append(img1)
    imagesArray.append(img2)
   
            
    return imagesArray
                
# Compute similarity transform given two sets of two points.
# OpenCV requires 3 pairs of corresponding points.
# We are faking the third one.

def similarityTransform(inPoints, outPoints):
    s60 = math.sin(60*math.pi/180)
    c60 = math.cos(60*math.pi/180)  
  
    inPts = np.copy(inPoints).tolist()
    outPts = np.copy(outPoints).tolist()
    
    xin = c60*(inPts[0][0] - inPts[1][0]) - s60*(inPts[0][1] - inPts[1][1]) + inPts[1][0]
    yin = s60*(inPts[0][0] - inPts[1][0]) + c60*(inPts[0][1] - inPts[1][1]) + inPts[1][1]
    
    inPts.append([np.int(xin), np.int(yin)])
    
    xout = c60*(outPts[0][0] - outPts[1][0]) - s60*(outPts[0][1] - outPts[1][1]) + outPts[1][0]
    yout = s60*(outPts[0][0] - outPts[1][0]) + c60*(outPts[0][1] - outPts[1][1]) + outPts[1][1]
    
    outPts.append([np.int(xout), np.int(yout)])
    
    tform = cv2.estimateRigidTransform(np.array([inPts]), np.array([outPts]), False)
    
    return tform

# Check if a point is inside a rectangle
def rectContains(rect, point):
    if point[0] < rect[0] :
        return False
    elif point[1] < rect[1] :
        return False
    elif point[0] > rect[2] :
        return False
    elif point[1] > rect[3] :
        return False
    return True

# Calculate delanauy triangle
def calculateDelaunayTriangles(rect, points):
    # Create subdiv
    subdiv = cv2.Subdiv2D(rect)
   
    # Insert points into subdiv
    for p in points:
        subdiv.insert((p[0], p[1]))

    # List of triangles. Each triangle is a list of 3 points ( 6 numbers )
    triangleList = subdiv.getTriangleList()

    # Find the indices of triangles in the points array
    delaunayTri = []
    
    for t in triangleList:
        pt = []
        pt.append((t[0], t[1]))
        pt.append((t[2], t[3]))
        pt.append((t[4], t[5]))
        
        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])        
        
        if rectContains(rect, pt1) and rectContains(rect, pt2) and rectContains(rect, pt3):
            ind = []
            for j in range(0, 3):
                for k in range(0, len(points)):                    
                    if(abs(pt[j][0] - points[k][0]) < 1.0 and abs(pt[j][1] - points[k][1]) < 1.0):
                        ind.append(k)                            
            if len(ind) == 3:                                                
                delaunayTri.append((ind[0], ind[1], ind[2]))
        
    return delaunayTri


def constrainPoint(p, w, h):
    p =  ( min( max( p[0], 0 ) , w - 1 ) , min( max( p[1], 0 ) , h - 1 ) )
    return p

# Apply affine transform calculated using srcTri and dstTri to src and
# output an image of size.
def applyAffineTransform(src, srcTri, dstTri, size):
    
    # Given a pair of triangles, find the affine transform.
    warpMat = cv2.getAffineTransform( np.float32(srcTri), np.float32(dstTri) )
    
    # Apply the Affine Transform just found to the src image
    dst = cv2.warpAffine( src, warpMat, (size[0], size[1]), None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101 )

    return dst


# Warps and alpha blends triangular regions from img1 and img2 to img
def warpTriangle(img1, img2, t1, t2):
    # Find bounding rectangle for each triangle
    r1 = cv2.boundingRect(np.float32([t1]))
    r2 = cv2.boundingRect(np.float32([t2]))

    # Offset points by left top corner of the respective rectangles
    t1Rect = [] 
    t2Rect = []
    t2RectInt = []

    for i in range(0, 3):
        t1Rect.append(((t1[i][0] - r1[0]),(t1[i][1] - r1[1])))
        t2Rect.append(((t2[i][0] - r2[0]),(t2[i][1] - r2[1])))
        t2RectInt.append(((t2[i][0] - r2[0]),(t2[i][1] - r2[1])))


    # Get mask by filling triangle
    mask = np.zeros((r2[3], r2[2], 3), dtype = np.float32)
    cv2.fillConvexPoly(mask, np.int32(t2RectInt), (1.0, 1.0, 1.0), 16, 0)

    # Apply warpImage to small rectangular patches
    img1Rect = img1[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
    
    size = (r2[2], r2[3])

    img2Rect = applyAffineTransform(img1Rect, t1Rect, t2Rect, size)
    
    img2Rect = img2Rect * mask

    # Copy triangular region of the rectangular patch to the output image
    img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] * ( (1.0, 1.0, 1.0) - mask )
     
    img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] + img2Rect


def generatePic(allPoints, images, w=400, h=400):

    # Eye corners
    eyecornerDst = [(np.int(0.3 * w), np.int(h / 3)), (np.int(0.7 * w), np.int(h / 3))]
    
    imagesNorm = []
    pointsNorm = []
    
    # Add boundary points for delaunay triangulation
    boundaryPts = np.array([(0, 0), (w/2, 0), (w-1, 0), (w-1, h/2), (w-1, h-1), (w/2, h-1), (0, h-1), (0, h/2)])
    
    # Initialize location of average points to 0s
    pointsAvg = np.array([(0,0)]* ( len(allPoints[0]) + len(boundaryPts) ), np.float32())
    
    n = len(allPoints[0])
    numImages = len(images)
    
    # Warp images and trasnform landmarks to output coordinate system, and find average of transformed landmarks.
    
    for i in range(0, numImages):
        points1 = allPoints[i]
        # Corners of the eye in input image
        eyecornerSrc  = [ allPoints[i][36], allPoints[i][45] ] 
        # Compute similarity transform
        tform = similarityTransform(eyecornerSrc, eyecornerDst)
        # Apply similarity transformation
        img = cv2.warpAffine(images[i], tform, (w,h))
        # Apply similarity transform on points
        points2 = np.reshape(np.array(points1), (68,1,2))        
        points = cv2.transform(points2, tform)
        points = np.float32(np.reshape(points, (68, 2)))
        # Append boundary points. Will be used in Delaunay Triangulation
        points = np.append(points, boundaryPts, axis=0)
        # Calculate location of average landmark points.
        pointsAvg = pointsAvg + points / numImages
        pointsNorm.append(points)
        imagesNorm.append(img)
    
    # Delaunay triangulation
    rect = (0, 0, w, h)
    dt = calculateDelaunayTriangles(rect, np.array(pointsAvg))

    # Output image
    output = np.zeros((h,w,3), np.float32())

    # Warp input images to average image landmarks
    for i in range(0, len(imagesNorm)) :
        img = np.zeros((h,w,3), np.float32())
        # Transform triangles one by one
        for j in range(0, len(dt)) :
            tin = [] 
            tout = []
            
            for k in range(0, 3) :                
                pIn = pointsNorm[i][dt[j][k]]
                pIn = constrainPoint(pIn, w, h)
                
                pOut = pointsAvg[dt[j][k]]
                pOut = constrainPoint(pOut, w, h)
                
                tin.append(pIn)
                tout.append(pOut)
                        
            warpTriangle(imagesNorm[i], img, tin, tout)

        # Add image intensities for averaging
        output = output + img

    # Divide by numImages to get average
    output = output / numImages

    for i in range(h//3, h//4*3):
        for j in range(w//3, w//4*3):
            if (output[i][j] == 0).all():
                output[i][j] = output[i][j-1]

    # Save result
    output_path = saved_pics_path + 'fusion_swap/fusion' + str(time.time()).replace('.', '') + '.jpg'
    cv2.imwrite(output_path , (output * 255).astype('uint8'))
    return output_path[5:]
   

def cutFace(allPoints, images, pic, w=400, h=400):
    # Eye corners
    eyecornerDst = [(np.int(0.3 * w), np.int(h / 3)), (np.int(0.7 * w), np.int(h / 3))]
    points1 = allPoints

    # Corners of the eye in input image
    eyecornerSrc  = [ allPoints[0][36], allPoints[0][45] ] 
    
    # Compute similarity transform
    tform = similarityTransform(eyecornerSrc, eyecornerDst)
    # Apply similarity transformation
    img = cv2.warpAffine(cv2.imdecode(np.fromfile(pic, dtype=np.uint8), cv2.IMREAD_COLOR), tform, (w,h))

    output_path = saved_pics_path + 'fusion_swap/cut' + str(time.time()).replace('.', '') + '.jpg'
    cv2.imwrite(output_path , img)
    return output_path[5:]


def mix_pics(pic1, pic2, w=400, h=400):
    # Read points for all images
    allPoints = readPoints(pic1, pic2)
    # Read all images
    images = readImages(pic1, pic2)

    paths_list = []

    # paths_list.append(cutFace([allPoints[0]], [images[0]], pic1))

    paths_list.append(generatePic([allPoints[0], allPoints[0], allPoints[0], allPoints[1]], 
                                  [images[0], images[0], images[0], images[1]], w, h))

    paths_list.append(generatePic([allPoints[0], allPoints[0],allPoints[1]], 
                                  [images[0], images[0], images[1]], w, h))

    paths_list.append(generatePic([allPoints[0], allPoints[0], allPoints[0], allPoints[1], allPoints[1]], 
                                  [images[0], images[0], images[0], images[1],images[1]], w, h))

    paths_list.append(generatePic([allPoints[0], allPoints[0], allPoints[1], allPoints[1], allPoints[1]], 
                                  [images[0],images[0], images[1], images[1], images[1]], w, h))

    paths_list.append(generatePic([allPoints[0], allPoints[1], allPoints[1]], 
                                  [images[0], images[1], images[1]], w, h))

    paths_list.append(generatePic([allPoints[0], allPoints[1], allPoints[1], allPoints[1]], 
                                  [images[0], images[1], images[1], images[1]], w, h))
    
    # paths_list.append(cutFace([allPoints[1]], [images[1]], pic2))

    return paths_list


def assemble_pics(pic1, pic2, w=200, h=400):
    pic_list = mix_pics(pic1, pic2, w, h)

    output_path = saved_pics_path + 'fusion_swap/assemble' + str(time.time()).replace('.', '') + '.jpg'
    target = Image.new('RGB', (w*6, h))

    for i in range(6):
        pic_list[i] = Image.open(r'/oss/' + pic_list[i])
        target.paste(pic_list[i], (i*w, 0, i*w+w, h))
    
    target.save(output_path)
    return output_path[4:]


def average_face(pic1, pic2):
    # Read points for all images
    allPoints = readPoints(pic1, pic2)
    # Read all images
    images = readImages(pic1, pic2)
    path = generatePic([allPoints[0], allPoints[1], allPoints[1], allPoints[1], allPoints[1]], 
                [images[0], images[1], images[1], images[1],images[1]], 600, 600)
    return path