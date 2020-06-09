import cv2
import sys
import logging as log
import datetime as dt
from time import sleep
import random

cascPath = "Webcam-Face-Detect-master\haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
log.basicConfig(filename='webcam.log',level=log.INFO)
speed=5
screenVar=2
counter=0
video_capture = cv2.VideoCapture(0)
anterior = 0
cordY=0
obstacles=[]
foods=[]
score=0
class Point: 
    def __init__(self, x, y): 
        self.x = x 
        self.y = y 
class Obstacle:
    def __init__(self,x):
        self.y=0
        self.x=x
        self.newObstacleServed=False
        self.remainingOverlapsCount=3

class Food:
    def __init__(self,x):
        self.y=0
        self.x=x
        self.newObstacleServed=False
        self.remainingOverlapsCount=1

def checkOverlap(rect1Start, rect1End, rect2Start, rect2End): 
      
    # If one rectangle is on left side of other 
    if(rect1Start.x >= rect2End.x or rect2Start.x >= rect1End.x): 
        return False
  
    # If one rectangle is above other 
    if(rect1Start.y <= rect2End.y or rect2Start.y <= rect1End.y): 
        return False
  
    return True
gameOver=False
while gameOver==False:
    if counter==3 :
        counter=0
        speed=speed+1
        screenVar=screenVar+0.5
    if not video_capture.isOpened():
        print('Unable to load camera.')
        sleep(5)
        pass
    cordY=cordY+1
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    screenSizeX=frame.shape[1]
    screenSizeY=frame.shape[0]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    if(len(obstacles)==0):
        obstacle=Obstacle(random.randint(0,screenSizeX-1))
        obstacle.size=random.randint(20,50)
        obstacles.append(obstacle)
        counter=counter+1
    else:
        for obstacle in obstacles:
            obstacle.y=obstacle.y+speed
            cv2.rectangle(frame,(obstacle.x,obstacle.y), (obstacle.x+obstacle.size,obstacle.y+obstacle.size), (0,0,255), 20)   
            if obstacle.y>(screenSizeY/2) and obstacle.newObstacleServed==False:
                obstacle.newObstacleServed=True
                newObstacle=Obstacle(random.randint(0,screenSizeX-1))
                newObstacle.size=random.randint(20,50)
                obstacles.append(newObstacle)
                counter=counter+1
    if(len(foods)==0):
        food=Food(random.randint(0,screenSizeX-1))
        food.size=random.randint(20,50)
        foods.append(obstacle)
        
    else:
        for food in foods:
            food.y=food.y+speed
            cv2.rectangle(frame,(food.x,food.y), (food.x+food.size,food.y+food.size), (0,255,0), 20)   
            if food.y>(screenSizeY-1) :
                foods.remove(food)
                newFood=Food(random.randint(0,screenSizeX-1))
                newFood.size=random.randint(20,50)
                foods.append(newFood)
                
    
    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        font= cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (x,y)
        fontScale              = 1
        fontColor              = (0,0,255)
        lineType               = 2
        cv2.putText(frame,("Score :"+str(score)),(round(screenSizeX/4),25),font,fontScale,fontColor,lineType)
        #cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        #cv2.rectangle(frame,(200,cordY), (230,cordY+30), (255,0,0), 20)
        gameOver=False
        for obstacle in obstacles:
            if checkOverlap(Point(obstacle.x,obstacle.y+obstacle.size),Point(obstacle.x+obstacle.size,obstacle.y),Point(x,y+h),Point(x+w,y)):
                obstacle.remainingOverlapsCount=obstacle.remainingOverlapsCount-1
                if obstacle.remainingOverlapsCount==0:
                    cv2.putText(frame,'Game Over', 
                        bottomLeftCornerOfText, 
                        font, 
                        fontScale,
                        fontColor,
                        lineType)
                    gameOver=True
                    print("OVERLAP")
                    sleep(10)
        
        for food in foods:
            if checkOverlap(Point(food.x,food.y+food.size),Point(food.x+food.size,food.y),Point(x,y+h),Point(x+w,y)):
                food.remainingOverlapsCount=food.remainingOverlapsCount-1
                if food.remainingOverlapsCount==0:
                    score=score+1
                    foods.remove(food)
        

    if anterior != len(faces):
        anterior = len(faces)
        log.info("faces: "+str(len(faces))+" at "+str(dt.datetime.now()))


    # Display the resulting frame
    cv2.imshow('Video', frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Display the resulting frame
    cv2.imshow('Video', frame)

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()