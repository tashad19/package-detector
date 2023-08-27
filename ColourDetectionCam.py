# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import imutils
import cv2
import requests
from pyzbar.pyzbar import decode


# some variables for colour detection
max_value = 255
max_value_H = 360 // 2
# starting HSV values (tested)
low_H = 7
low_S = 98
low_V = 110
high_H = 20
high_S = 229
high_V = 188
window_detection_name = 'Object Detection'
low_H_name = 'Low H'
low_S_name = 'Low S'
low_V_name = 'Low V'
high_H_name = 'High H'
high_S_name = 'High S'
high_V_name = 'High V'
origX = 997/2     # dont change 
origY = 561/2

# HSV colour trackbars
def on_low_H_thresh_trackbar(val):
    global low_H
    global high_H
    low_H = val
    low_H = min(high_H - 1, low_H)
    cv2.setTrackbarPos(low_H_name, window_detection_name, low_H)

def on_high_H_thresh_trackbar(val):
    global low_H
    global high_H
    high_H = val
    high_H = max(high_H, low_H + 1)
    cv2.setTrackbarPos(high_H_name, window_detection_name, high_H)

def on_low_S_thresh_trackbar(val):
    global low_S
    global high_S
    low_S = val
    low_S = min(high_S - 1, low_S)
    cv2.setTrackbarPos(low_S_name, window_detection_name, low_S)

def on_high_S_thresh_trackbar(val):
    global low_S
    global high_S
    high_S = val
    high_S = max(high_S, low_S + 1)
    cv2.setTrackbarPos(high_S_name, window_detection_name, high_S)

def on_low_V_thresh_trackbar(val):
    global low_V
    global high_V
    low_V = val
    low_V = min(high_V - 1, low_V)
    cv2.setTrackbarPos(low_V_name, window_detection_name, low_V)

def on_high_V_thresh_trackbar(val):
    global low_V
    global high_V
    high_V = val
    high_V = max(high_V, low_V + 1)
    cv2.setTrackbarPos(high_V_name, window_detection_name, high_V)

cv2.namedWindow(window_detection_name)
cv2.createTrackbar(low_H_name, window_detection_name, low_H, max_value_H, on_low_H_thresh_trackbar)
cv2.createTrackbar(high_H_name, window_detection_name, high_H, max_value_H, on_high_H_thresh_trackbar)
cv2.createTrackbar(low_S_name, window_detection_name, low_S, max_value, on_low_S_thresh_trackbar)
cv2.createTrackbar(high_S_name, window_detection_name, high_S, max_value, on_high_S_thresh_trackbar)
cv2.createTrackbar(low_V_name, window_detection_name, low_V, max_value, on_low_V_thresh_trackbar)
cv2.createTrackbar(high_V_name, window_detection_name, high_V, max_value, on_high_V_thresh_trackbar)


# url to get feed from smartphone camera
# get this url by downloading 'IP Camera' app on your phone and select 'start server'
url = "http://172.20.16.121:8080/shot.jpg"

# Load Cap object (of the pc's webcam)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# for finding midpoint of bounding boxes
def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# get the left-most contour as the marker out of all given contours in the reference image
def find_marker(cnts):
	# sort the contours from left-to-right
    cnts, _ = contours.sort_contours(cnts)
    my_cnts = []

    for c in cnts:
        if cv2.contourArea(c) < 5000:
            continue
        else:
            my_cnts.append(c)
            break

    # left-most contour
    if my_cnts:
        left = my_cnts[0]
        marker = cv2.minAreaRect(left)
        return marker
    else:
        return None

def distance_to_camera(knowWidth, focalLength, perWidth):
	return (knowWidth * focalLength) / perWidth       # perWidth = perceived width

# this function uses colour detection
def find_cnts(image):

    image_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(image_HSV, (low_H, low_S, low_V), (high_H, high_S, high_V))

    # construct a closing kernel and apply it to the thresholded image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (45, 15))
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # perform a series of erosions and dilations
    closed = cv2.erode(closed, None, iterations = 1)
    closed = cv2.dilate(closed, None, iterations = 1)

    # Find contours
    cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return cnts, closed


# initialize the known distance from the camera to the object, which
# in this case is 80 cm
KNOWN_DISTANCE = 80.0
# initialize the known object width, which in this case, the
# box is 20 cm wide
KNOWN_WIDTH = 20.0
# load the first image that contains an object that is KNOWN TO BE some fixed distance
# from our camera, then find the paper marker in the image, and initialize
# the focal length
image = cv2.imread("cam2.jpg")

cnts, _ = find_cnts(image)

# left-most contour is the marker
marker = find_marker(cnts)
# find the focal length
if marker:
    print(marker[1][0])
    PIXEL_WIDTH = marker[1][0]
    
else:
    # default marker width
    PIXEL_WIDTH = 200
    print("Marker not found. Assuming PIXEL_WIDTH default value.")

focalLength = (PIXEL_WIDTH * KNOWN_DISTANCE) / KNOWN_WIDTH

# draw a bounding box around the image and display it
# this is for the reference image
box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
box = np.int0(box)
cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
cv2.imshow("Reference Image", image)

    
# variable to pause the frame, initially set to false
pause = False

while True:

    # these 4 lines are to get feed from smartphone camera
    if not pause:
        img_resp = requests.get(url)
        img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
        img = cv2.imdecode(img_arr, -1)      # its dimensions are 1920 x 1080 by default
        frame = imutils.resize(img, width=1000, height=1800)
        paused_frame = frame.copy()

    # Process the paused frame (with bounding rectangles) if paused
    frame = paused_frame.copy() if pause else frame.copy()

    # to get feed from pc's webcam
    # _, refImage = cap.read()

    # 'pixels per metric' calibration variable for dimensions of box
    pixelsPerMetric = None

    if frame is None:
        break
    
    cnts, closed = find_cnts(frame)

    # loop over the contours individually
    for c in cnts:
        
        # if the contour is not sufficiently large, ignore it
        if cv2.contourArea(c) < 5000:
            continue
        
        # compute the rotated bounding box of the contour
        # orig = refImage.copy()
        box = cv2.minAreaRect(c)
        # distance to camera of each bbox
        z = distance_to_camera(KNOWN_WIDTH, focalLength, box[1][0])
        # cv2.putText(frame, "Distance: %.2f m" % (camDist/100), (frame.shape[1] - 500, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        
        # order the points in the contour such that they appear
        # in top-left, top-right, bottom-right, and bottom-left
        # order, then draw the outline of the rotated bounding
        # box
        box = perspective.order_points(box)
        cv2.drawContours(frame, [box.astype("int")], -1, (0, 255, 0), 2)
        
        # loop over the original points and draw them
        for (x, y) in box:
            cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)
            
        # unpack the ordered bounding box, then compute the midpoint
        # between the top-left and top-right coordinates, followed by
        # the midpoint between bottom-left and bottom-right coordinates
        (tl, tr, br, bl) = box
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)
        
        # compute the midpoint between the top-left and top-right points,
        # followed by the midpoint between the top-right and bottom-right
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)
        
        # draw the midpoints on the image
        cv2.circle(frame, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
        cv2.circle(frame, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
        cv2.circle(frame, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
        cv2.circle(frame, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

        # compute the center point of bbox
        (centX, centY) = midpoint([tltrX, tltrY], [blbrX, blbrY])
        # with respect to camera
        centXcam =  centX - origX
        centYcam =  -1*(centY - origY)
        

        # draw the center of bbox 
        cv2.circle(frame, (int(centX), int(centY)), 5, (255, 255, 0), -1)
        
        # draw lines between the midpoints
        cv2.line(frame, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)), (255, 0, 255), 2)
        cv2.line(frame, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)), (255, 0, 255), 2)
        
        # compute the Euclidean distance between the midpoints
        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
        
        # if the pixels per metric has not been initialized, then
        # compute it as the ratio of pixels to supplied metric
        # (in this case, inches)
        if pixelsPerMetric is None:
            pixelsPerMetric = dB / KNOWN_WIDTH
            
        # compute the size of the object
        dimA = dA / pixelsPerMetric
        dimB = dB / pixelsPerMetric

        # coordinates of center of bbox in cm
        x = centXcam / pixelsPerMetric
        y = centYcam / pixelsPerMetric

        # draw x, y coordinates of center
        cv2.putText(frame, "(x: {:.1f}cm, y: {:.1f}cm, z: {:.1f}cm)".format(x, y, z), (int(centX) - 15, int(centY) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 0, 0), 2)

        
        # draw the object sizes on the image
        cv2.putText(frame, "{:.1f}cm".format(dimA), (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(frame, "{:.1f}cm".format(dimB), (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)


    # barcode identification
    for barcode in decode(frame):

        myData = barcode.data.decode('utf-8')
        print(myData)

        # draw the bounding box for the polygon
        pts = np.array([barcode.polygon], np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.polylines(frame, [pts], True, (255,0,255), 5)

        # to get the rectangle points and display read text
        pts2 = barcode.rect
        cv2.putText(frame, myData, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)
        cv2.putText(frame, str(pts2.left) + "," + str(pts2.top), (pts2[0], pts2[1]-30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)

        
    # show the output frame
    cv2.imshow("Image with metrics", frame)
    cv2.imshow(window_detection_name, closed)

    key = cv2.waitKey(30)

    # pause or unpause if p is pressed
    if key == ord('p'):
        pause = not pause

    # Exit the loop when 'q' is pressed
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()