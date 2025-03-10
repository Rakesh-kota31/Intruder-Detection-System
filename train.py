
import tkinter as tk
from tkinter import Message ,Text
import cv2,os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import tkinter.ttk as ttk
import tkinter.font as font
import urllib.request
import numpy as np
import requests
def nothing(x):
    pass
 
#change the IP address below according to the
#IP shown in the Serial monitor of Arduino code
url='http://192.168.29.48/cam-lo.jpg'
url1='http://192.168.29.48/'
window = tk.Tk()
window.title("Intruder Detection System")

window.geometry('1280x720')
window.configure(background='white')
#window.attributes('-fullscreen', True)
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)



message = tk.Label(window, text="INTRUDER DETECTION SYSTEM" ,bg="blue"  ,fg="white"  ,width=50  ,height=1,font=('times', 20, 'italic bold underline')) 

message.place(x=50, y=20)

lbl = tk.Label(window, text="Enter ID",width=16  ,height=2  ,fg="black"  ,bg="white" ,font=('times', 15, ' bold ') ) 
lbl.place(x=100, y=100)

txt = tk.Entry(window,width=16  ,bg="white" ,fg="black",font=('times', 15, ' bold '))
txt.place(x=400, y=115)

lbl2 = tk.Label(window, text="Enter Name",width=16  ,fg="black"  ,bg="white"    ,height=2 ,font=('times', 15, ' bold ')) 
lbl2.place(x=100, y=200)

txt2 = tk.Entry(window,width=16  ,bg="white"  ,fg="black",font=('times', 15, ' bold ')  )
txt2.place(x=400, y=215)

lbl3 = tk.Label(window, text="Notification : ",width=20  ,fg="orange"  ,bg="white"  ,height=2 ,font=('times', 15, ' bold underline ')) 
lbl3.place(x=100, y=300)

message = tk.Label(window, text="...................." ,bg="white"  ,fg="black"  ,width=30  ,height=2, activebackground = "yellow" ,font=('times', 15, ' bold ')) 
message.place(x=400, y=300)

message2 = tk.Label(window, text="....................." ,fg="black"   ,bg="white",activeforeground = "green",width=30  ,height=2  ,font=('times', 15, ' bold ')) 
message2.place(x=400, y=550)
 
def clear():
    txt.delete(0, 'end')    
    res = ""
    message.configure(text= res)

def clear2():
    txt2.delete(0, 'end')    
    res = ""
    message.configure(text= res)    
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False
 
def TakeImages():        
    Id=(txt.get())
    name=(txt2.get())
    if(is_number(Id) and name.isalpha()):
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector=cv2.CascadeClassifier(harcascadePath)
        sampleNum=0
        while(True):
            img_resp=urllib.request.urlopen(url)
            imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
            img=cv2.imdecode(imgnp,-1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)        
                #incrementing sample number 
                sampleNum=sampleNum+1
                #saving the captured face in the dataset folder TrainingImage
                cv2.imwrite("TrainingImage\ "+name +"."+Id +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
                #display the frame
                cv2.imshow('frame',img)
            #wait for 100 miliseconds 
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # break if the sample number is morethan 100
            elif sampleNum>60:
                break
        cv2.destroyAllWindows() 
        res = "Images Saved for ID : " + Id +" Name : "+ name
        row = [Id , name]
        with open('Authorized_Person_Details\Authorized_Person_Details.csv','a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        message.configure(text= res)
    else:
        if(is_number(Id)):
            res = "Enter Alphabetical Name"
            message.configure(text= res)
        if(name.isalpha()):
            res = "Enter Numeric Id"
            message.configure(text= res)
    
def TrainImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()#recognizer = cv2.face.LBPHFaceRecognizer_create()#$cv2.createLBPHFaceRecognizer()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector =cv2.CascadeClassifier(harcascadePath)
    faces,Id = getImagesAndLabels("TrainingImage")
    recognizer.train(faces, np.array(Id))
    recognizer.save("Trainner.yml")
    res = "Image Trained"#+",".join(str(f) for f in Id)
    message.configure(text= res)

def getImagesAndLabels(path):
    #get the path of all the files in the folder
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)] 
    #print(imagePaths)
    
    #create empth face list
    faces=[]
    #create empty ID list
    Ids=[]
    #now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        #loading the image and converting it to gray scale
        pilImage=Image.open(imagePath).convert('L')
        #Now we are converting the PIL image into numpy array
        imageNp=np.array(pilImage,'uint8')
        #getting the Id from the image
        Id=int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        Ids.append(Id)        
    return faces,Ids

def TrackImages():
    recognizer = cv2.face.LBPHFaceRecognizer_create()#cv2.createLBPHFaceRecognizer()
    recognizer.read("Trainner.yml")
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath);    
    df=pd.read_csv("Authorized_Person_Details\Authorized_Person_Details.csv")
    font = cv2.FONT_HERSHEY_SIMPLEX        
    col_names =  ['Id','Name','Date','Time']
    while True:
        img_resp=urllib.request.urlopen(url)
        imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
        im=cv2.imdecode(imgnp,-1)
        #cv2.imshow("live transmission", frame)
        gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        faces=faceCascade.detectMultiScale(gray, 1.2,5)    
        for(x,y,w,h) in faces:
            cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
            Id, conf = recognizer.predict(gray[y:y+h,x:x+w])                                   
            if(conf < 90):
                aa=df.loc[df['Id'] == Id]['Name'].values
                tt=str(Id)+"-"+aa
            else:
                Id='Unknown'                
                tt=str(Id)  
            if(conf > 95):
                noOfFile=len(os.listdir("ImagesUnknown"))+1
                cv2.imwrite("ImagesUnknown\Image"+str(noOfFile) + ".jpg", im[y:y+h,x:x+w])            
            cv2.putText(im,str(tt),(x,y+h), font, 1,(255,255,255),2)          
        cv2.imshow('im',im) 
        if (cv2.waitKey(1)==ord('q')):
            break
    cv2.destroyAllWindows()

  
clearButton = tk.Button(window, text="Clear", command=clear  ,fg="black"  ,bg="gray"  ,width=10  ,height=1 ,activebackground = "Red" ,font=('times', 15, ' bold '))
clearButton.place(x=650, y=100)
clearButton2 = tk.Button(window, text="Clear", command=clear2  ,fg="black"  ,bg="gray"  ,width=10  ,height=1, activebackground = "Red" ,font=('times', 15, ' bold '))
clearButton2.place(x=650, y=200)    
takeImg = tk.Button(window, text="Take Images", command=TakeImages  ,fg="black"  ,bg="gray"  ,width=10  ,height=2, activebackground = "Red" ,font=('times', 15, ' bold '))
takeImg.place(x=100, y=400)
trainImg = tk.Button(window, text="Train Images", command=TrainImages  ,fg="black"  ,bg="gray"  ,width=10  ,height=2, activebackground = "Red" ,font=('times', 15, ' bold '))
trainImg.place(x=300, y=400)
trackImg = tk.Button(window, text="Track Images", command=TrackImages  ,fg="black"  ,bg="gray"  ,width=10  ,height=2, activebackground = "Red" ,font=('times', 15, ' bold '))
trackImg.place(x=500, y=400)
quitWindow = tk.Button(window, text="Quit", command=window.destroy  ,fg="black"  ,bg="gray"  ,width=10  ,height=2, activebackground = "Red" ,font=('times', 15, ' bold '))
quitWindow.place(x=700, y=400)

window.mainloop()
