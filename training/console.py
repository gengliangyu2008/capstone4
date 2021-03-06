# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 18:13:21 2020

@author: User
"""
import os,re
import cv2
import sys
import logging as log
import datetime as dt

from time import sleep
from time import time

import numpy as np

from matplotlib import pyplot as plt
from tensorflow.keras.callbacks import ModelCheckpoint,CSVLogger,LearningRateScheduler
from tensorflow.keras.models import Model
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten,Dropout
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import AveragePooling2D,MaxPooling2D,UpSampling2D
from tensorflow.keras.layers import add,Lambda
from tensorflow.keras.regularizers import l2
from tensorflow.keras.utils import to_categorical,plot_model

from tensorflow.keras import optimizers
from tensorflow.keras import backend
from tensorflow.keras.preprocessing.image import ImageDataGenerator,img_to_array,load_img
import IPython
from scipy import ndimage
from scipy.ndimage.interpolation import shift
from numpy import savetxt,loadtxt

#savetxt('data.csv', data, delimiter=',')

#data = loadtxt('data.csv', delimiter=',')

import gc
from skimage.transform import resize

import pickle
from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix

from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier

import face_recognition

from mtcnn import MTCNN

debug=0
detector = MTCNN()

def grayplt(img,title=''):
    '''
    plt.axis('off')
    if np.size(img.shape) == 3:
        plt.imshow(img[:,:,0],cmap='gray',vmin=0,vmax=1)
    else:
        plt.imshow(img,cmap='gray',vmin=0,vmax=1)
    plt.title(title, fontproperties=prop)
    '''
    
    fig,ax = plt.subplots(1)
    ax.set_aspect('equal')
    


    # Show the image
    if np.size(img.shape) == 3:
        ax.imshow(img,vmin=0,vmax=1)
        #ax.imshow(img[:,:,0],cmap='hot',vmin=0,vmax=1)
    else:
        ax.imshow(img,cmap='hot',vmin=0,vmax=1)
   
    plt.show()

def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
 
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)    

import process_csv_dlib

def face_recog(imag,face_locations,face_encodings,que):
    face_recog1(imag,face_locations,face_encodings,que)
    if 1:
        if 1:
            print("Bbb")
            face_encodings=[]
            #que = queue.Queue()
            #proc=multiprocessing.Process( target=face_recog, args=(imag,face_locations,face_encodings) )
            proc=threading.Thread( target=face_recog1, args=(imag,face_locations,face_encodings,que) )
            
            try:
                timtemp3=time()
                proc.start()
                #print("ccc")
                sleep(0.001)
                #print("time",time()-timtemp3)
                proc.join(timeout=0)
                #print("ddd")
                #print(proc.isAlive())
                while proc.isAlive():
                    #print("aaa")
                    timtemp=time()
                    ret2, frame2 = video_capture.read()
                    cv2.imshow('Video', frame2)
                    #print(time()-timtemp)
                    #sleep(0.01)
                
                #sleep(0.01)
            except:
                #print("qqq")
                pass
            '''
            try:
                face_encodings=que.get()
            except:
                pass
            '''

def face_recog1(imag,face_locations,face_encodings,que):
    face_encodings=face_recognition.face_encodings(imag, num_jitters=1)
    #print(face_encodings)
    '''
    if face_encodings!=[]:
        with open('face_encode.csv', "w+") as ff:
            savetxt(ff, face_encodings, delimiter=',')
    else:
        inf=open('face_encode.csv', "w+")
        inf.write("9999")
        inf.close()
    '''
    que.put(face_encodings)    
    return face_encodings

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def grayplt(img,title=''):
    fig,ax = plt.subplots(1)
    ax.set_aspect('equal')

    if np.size(img.shape) == 3:
        #ax.imshow(img[:,:,0],cmap='hot',vmin=0,vmax=1)
        ax.imshow(img,vmin=0,vmax=1)
    else:
        ax.imshow(img,cmap='hot',vmin=0,vmax=1)
    plt.show()

def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values

	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")

	# apply gamma correction using the lookup table

	return cv2.LUT(image, table)    

def preprocess_image(img):
    imag=cv2.imread(img)
    res = cv2.resize(imag,(160, 160), interpolation = cv2.INTER_CUBIC)
    res=np.expand_dims(res,axis=0)
    return res



def findCosineDistance(source_representation, test_representation):

    a = np.matmul(np.transpose(source_representation), test_representation)

    b = np.sum(np.multiply(source_representation, source_representation))

    c = np.sum(np.multiply(test_representation, test_representation))

    return 1 - (a / (np.sqrt(b) * np.sqrt(c)))

 

def l2_normalize(x, axis=-1, epsilon=1e-10):
    output = x / np.sqrt(np.maximum(np.sum(np.square(x), axis=axis, keepdims=True), epsilon))
    return output

 

def findEuclideanDistance(source_representation, test_representation):

    euclidean_distance = source_representation - test_representation

    euclidean_distance = np.sum(np.multiply(euclidean_distance, euclidean_distance))

    euclidean_distance = np.sqrt(euclidean_distance)

    #euclidean_distance = l2_normalize(euclidean_distance )

    return euclidean_distance

def image_process(images,gamma,ratioo,flip,blur):    
    img_pointer=0
    path=".\\img\\"
    for img in images:
        
        imag=cv2.imread(path+img)
        imag = cv2.cvtColor(imag, cv2.COLOR_BGR2RGB)
        print("before")
        grayplt(imag/255)
        face_locations = face_recognition.face_locations(imag, number_of_times_to_upsample=2, model='hog') # For GPU, use model='cnn'
        face_encodings = face_recognition.face_encodings(imag, face_locations, num_jitters=2)
        print(face_locations)                
        print(face_encodings)   
        if face_encodings==[]: continue             
        
        if flip==1:
            imag=np.fliplr(imag)
            
        if blur==1:
            imag=cv2.GaussianBlur(imag,(5,5),0)
        elif blur==2:
            #imag=cv2.GaussianBlur(imag,(5,5),0)
            imag=cv2.GaussianBlur(imag,(3,3),0)
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            imag = cv2.filter2D(imag, -1, kernel)
        elif blur==3:
            #imag=cv2.GaussianBlur(imag,(5,5),0)
            #imag=cv2.GaussianBlur(imag,(3,3),0)
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            imag = cv2.filter2D(imag, -1, kernel)
        elif blur==4:
            imag=cv2.GaussianBlur(imag,(5,5),0)
            #imag=cv2.GaussianBlur(imag,(3,3),0)
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            imag = cv2.filter2D(imag, -1, kernel)

            
        imag=adjust_gamma(imag,gamma)
        print("after")
        grayplt(imag/255)
        #continue
        
        result = detector.detect_faces(imag)
        print("rawimage",result)
        if result==[]: continue
    
        keypoints = result[0]['keypoints']
        
        turned=0
        while keypoints['right_eye'][1]-keypoints['left_eye'][1]>8:
            imag2 = ndimage.rotate(imag, 2, mode='nearest')
            print("turned")
            turned=1
            result2 = detector.detect_faces(imag2)
            if result2==[]: break
            imag=imag2
            result=result2
            keypoints = result[0]['keypoints']
        while keypoints['left_eye'][1]-keypoints['right_eye'][1]>8:
            imag2 = ndimage.rotate(imag, -2, mode='nearest')
            print("turned")
            turned=1
            result2 = detector.detect_faces(imag2)
            if result2==[]: break
            imag=imag2
            result=result2
            keypoints = result[0]['keypoints']
        if turned==1:
            grayplt(imag/255)
    
        # Result is an array with all the bounding boxes detected. We know that for 'ivan.jpg' there is only one.
        bounding_box = result[0]['box']
        #print("bounding_box",bounding_box)
        if bounding_box[3]<45: continue
        if bounding_box[2]<45: continue
    
        keypoints = result[0]['keypoints']
        #print("keypoints",keypoints)   
        
        left_bound=int( bounding_box[0]) #+(keypoints['left_eye'][0]-bounding_box[0])/5 )
        right_bound=int( bounding_box[0]+bounding_box[2]) #-(bounding_box[0]+bounding_box[2]-keypoints['right_eye'][0])/5 )
        top_bound=int( bounding_box[1]) #+(min(keypoints['right_eye'][1],keypoints['left_eye'][1])-bounding_box[1])/5 )
        bottom_bound=int( bounding_box[1]+bounding_box[3]) #-(bounding_box[1]+bounding_box[3]-max(keypoints['mouth_right'][1],keypoints['mouth_left'][1]))/5 )
        
        '''
        left_length=keypoints['nose'][0]-bounding_box[0]
        right_length=bounding_box[2]-keypoints['nose'][0]
        top_length=keypoints['nose'][1]-bounding_box[1]
        bottom_length=bounding_box[3]-keypoints['nose'][1]
        imag=imag[ bounding_box[1]:bounding_box[1]+bounding_box[3] , bounding_box[0]:bounding_box[0]+bounding_box[2] ]
        '''
        left_length=keypoints['nose'][0]-left_bound
        right_length=right_bound-keypoints['nose'][0]
        top_length=keypoints['nose'][1]-top_bound
        bottom_length=bottom_bound-keypoints['nose'][1]        
        imag=imag[top_bound:bottom_bound, left_bound:right_bound]
        #print("32")
        #grayplt(imag/255)
        #print(imag.shape)
        
        #break
        '''
        if left_length>right_length:
            if left_length<80:
                delta=int( (left_length-right_length)/4 )
                res1=np.ones((imag.shape[0],delta,3))*140
                imag=np.concatenate((res1,imag,res1),axis=1)
            elif left_length>=80 :
                delta=int( (left_length-right_length)/2 )
                res1=np.ones((imag.shape[0],delta,3))*140
                imag=np.concatenate((imag,res1),axis=1)            
        if right_length>left_length:
            if right_length<80:
                delta=int( (right_length-left_length)/4 )
                res1=np.ones((imag.shape[0],delta,3))*140
                imag=np.concatenate((res1,imag,res1),axis=1)
            elif right_length>=80:
                delta=int( (right_length-left_length)/2 )
                res1=np.ones((imag.shape[0],delta,3))*140
                imag=np.concatenate((res1,imag),axis=1)
        if top_length>bottom_length:
            if top_length<80:
                delta=int( (top_length-bottom_length)/4 )
                res1=np.ones((delta,imag.shape[1],3))*140
                imag=np.concatenate((res1,imag,res1))
            elif top_length>=80:
                delta=int( (top_length-bottom_length)/2 )
                res1=np.ones((delta,imag.shape[1],3))*140
                imag=np.concatenate((imag,res1))
        if bottom_length>top_length:
            if bottom_length<80:
                delta=int( (bottom_length-top_length)/4 )
                res1=np.ones((delta,imag.shape[1],3))*140
                imag=np.concatenate((res1,imag,res1))
            if bottom_length>=80:
                delta=int( (bottom_length-top_length)/2 )
                res1=np.ones((delta,imag.shape[1],3))*140
                imag=np.concatenate((res1,imag))
        
        
        #grayplt(imag/255)
        print(imag.shape)
        #raise
        rati=max(left_length,right_length,top_length,bottom_length)
        rati=79.9/rati
        imag=cv2.resize(imag,(int(imag.shape[1]*rati),int(imag.shape[0]*rati)), interpolation = cv2.INTER_CUBIC)
        '''
        ratoo=[1.0,1.1,1.2,1.4,1.5,1.6,1.8,2.0]
        '''
        for ratioo in [1.1,1.2,1.4,1.5,1.6,1.8,2.0]:
            if ratioo>rati:
                ratoo.append(ratioo)
        print(rati,ratoo)
        '''
        #raise
        '''    
        if imag.shape[0]>=imag.shape[1]:
            ratio=160/imag.shape[0]
            imag = cv2.resize(imag,(int(imag.shape[1]*ratio),160), interpolation = cv2.INTER_CUBIC)
            if imag.shape[1]<160:
                delta=int( (160-imag.shape[1])/2 )
                res1=np.ones((imag.shape[0],delta,3))*140
                imag=np.concatenate((res1,imag,res1),axis=1)
            #grayplt(imag/255)
        elif imag.shape[0]<imag.shape[1]:
            ratio=160/imag.shape[1]
            imag = cv2.resize(imag,(160,int(imag.shape[0]*ratio)), interpolation = cv2.INTER_CUBIC)
            if imag.shape[1]<160:
                delta=int( (160-imag.shape[0])/2 )
                res1=np.ones((delta,imag.shape[1],3))*140
                imag=np.concatenate((res1,imag,res1),axis=0)
        '''
                
            #grayplt(imag/255)
        print("after bound")
        grayplt(imag/255)
        
        face_locations = face_recognition.face_locations(imag, number_of_times_to_upsample=2, model='hog') # For GPU, use model='cnn'
        face_encodings = face_recognition.face_encodings(imag, face_locations, num_jitters=2)
        print(face_locations)                
        print(face_encodings)        
        if face_encodings==[]: continue             

        #grayplt(imag/255)
        #print(imag.shape)
        #raise
        #continue
        #break
            
        img_pointer=eval(img.replace(".jpg","").replace("frame",""))
        for rotate in [0]:
            if rotate!=0:
                imag1 = ndimage.rotate(imag, rotate, mode='nearest')
            else:
                imag1=imag
                
            face_locations = face_recognition.face_locations(imag1, number_of_times_to_upsample=2, model='hog') # For GPU, use model='cnn'
            face_encodings = face_recognition.face_encodings(imag1, face_locations, num_jitters=2)
            #print(face_locations)                
            #print(face_encodings)        
            if face_encodings==[]: continue             
            
            for ratioo in ratoo:
                
            #for ratioo in [0.8]:
                print(ratioo)
                if ratioo==1:
                    imag2 = cv2.resize(imag1,(160, 160), interpolation = cv2.INTER_CUBIC)
                else:
                    imag2 = cv2.resize(imag1,(int(160*ratioo), int(160*ratioo)), interpolation = cv2.INTER_CUBIC)
                #print("before")    
                #grayplt(imag2/255)
                #print(imag2.shape)
                #raise
                result3a = detector.detect_faces(imag2)
                #print("just raw scaled",result3a)
                if result3a==[]: continue
                bounding_box = result3a[0]['box']
                #print("bounding_box2: ",bounding_box)
                if bounding_box[3]<45: continue
                if bounding_box[2]<45: continue
        
                keypoints3a = result3a[0]['keypoints']
                coor=keypoints3a["nose"]
                '''
                if ratioo>1:
                    #print(int(160*(ratioo-1)/2))
                    #imag2 = imag2[int(160*(ratioo-1)/2):160+int(160*(ratioo-1)/2), int(160*(ratioo-1)/2):160+int(160*(ratioo-1)/2)]
                    if coor[1]>=80 and coor[0]>=80:
                        #print("928",coor)
                        imag2=imag2[coor[1]-80:coor[1]+80,coor[0]-80:coor[0]+80]
                    elif coor[1]<80 and coor[0]>=80:
                        #print("923",coor)
                        diff1=80-coor[1]
                        res1=np.ones((diff1,imag2.shape[1],3))*140
                        #grayplt(imag2/255)
                        imag2=np.concatenate((res1,imag2))   
                        #grayplt(imag2/255)
                        imag2=imag2[0:160,coor[0]-80:coor[0]+80] 
                    elif coor[0]<80 and coor[1]>=80:
                        #print("926",coor)
                        diff1=80-coor[0]
                        res1=np.ones((imag2.shape[0],diff1,3))*140
                        imag2=np.concatenate((res1,imag2),axis=1)                        
                        imag2=imag2[coor[1]-80:coor[1]+80,0:160]
                    elif coor[0]<80 and coor[1]<80:
                        #print("927",coor)
                        diff1=80-coor[0]
                        res1=np.ones((imag2.shape[0],diff1,3))*140
                        imag2=np.concatenate((res1,imag2),axis=1)                        
                        diff1=80-coor[1]
                        res1=np.ones((diff1,imag2.shape[1],3))*140
                        imag2=np.concatenate((res1,imag2))    
                        imag2=imag2[0:160,0:160]
                    if imag2.shape[1]<160:
                        #print("i m here2")
                        diff1=160-imag2.shape[1]
                        res1=np.ones((imag2.shape[0],diff1,3))*140
                        imag2=np.concatenate((imag2,res1),axis=1)
                    if imag2.shape[0]<160:
                        diff1=160-imag2.shape[0]
                        res1=np.ones((diff1,imag2.shape[1],3))*140
                        imag2=np.concatenate((imag2,res1))
                        
                        
                else:
                    if coor[0]<80:
                        #print(":i m here")
                        diff1=80-coor[0]
                        res1=np.ones((imag2.shape[0],diff1,3))*140
                        imag2=np.concatenate((res1,imag2),axis=1)
                        #grayplt(imag2/255)
                        if imag2.shape[1]<160:
                            #print("i m here2")
                            diff1=160-imag2.shape[1]
                            res1=np.ones((imag2.shape[0],diff1,3))*140
                            imag2=np.concatenate((imag2,res1),axis=1)
                            #grayplt(imag2/255)
                        elif imag2.shape[1]>160:
                            imag2=imag2[:,0:160]
                            
                    elif coor[0]>=80:
                        #print(coor[0])
                        diff1=coor[0]-80
                        #grayplt(imag2/255)
                        imag2=imag2[:,diff1:160+diff1]
                        #grayplt(imag2/255)
                        if imag2.shape[1]<160:
                            print("i m here2")
                            diff1=160-imag2.shape[1]
                            res1=np.ones((imag2.shape[0],diff1,3))*140
                            imag2=np.concatenate((imag2,res1),axis=1)
                            #grayplt(imag2/255)
                        
                        #res1=np.zeros((imag2.shape[0],diff1,3))
                        #imag2=np.concatenate((res1,imag2,res1),axis=1)
                        
                    #print("intermidat")
                    #grayplt(imag2/255)
                        
                    if coor[1]<80:
                        diff1=80-coor[1]
                        res1=np.ones((diff1,imag2.shape[1],3))*140
                        imag2=np.concatenate((res1,imag2))
                        if imag2.shape[0]<160:
                            diff1=160-imag2.shape[0]
                            res1=np.ones((diff1,imag2.shape[1],3))*140
                            imag2=np.concatenate((imag2,res1))
                        elif imag2.shape[0]>160:
                            imag2=imag2[0:160,:]
                            
                    elif coor[1]>=80:
                        diff1=coor[1]-80
                        imag2=imag2[diff1:160+diff1,:]
                        if imag2.shape[0]<160:
                            diff1=160-imag2.shape[0]
                            res1=np.ones((diff1,imag2.shape[1],3))*140
                            imag2=np.concatenate((imag2,res1))
                        #res1=np.zeros((imag2.shape[0],diff1,3))
                        #imag2=np.concatenate((res1,imag2,res1),axis=1)
                    '''    
                    
                    
                #print("after")
                #grayplt(imag2/255)
                result3 = detector.detect_faces(imag2)
                #print("after scale",result3)
                if result3==[]: continue
        
                keypoints3 = result3[0]['keypoints']
    
                if keypoints3=={}:continue
                if 'left_eye' not in keypoints3: continue
                if 'right_eye' not in keypoints3: continue
                if 'mouth_left' not in keypoints3: continue
                if 'mouth_right' not in keypoints3: continue
                if 'nose' not in keypoints3: continue
                bounding_box = result3[0]['box']
                #print("bounding_box3: ",bounding_box)
                if bounding_box[3]<45: continue
                if bounding_box[2]<45: continue

                face_locations = face_recognition.face_locations(imag2, number_of_times_to_upsample=2, model='hog') # For GPU, use model='cnn'
                face_encodings = face_recognition.face_encodings(imag2, face_locations, num_jitters=2)
                #print(face_locations)                
                #print(face_encodings)        
                if face_encodings==[]: continue             
            
    
                #print(ratioo)
                #grayplt(imag2/255)
                #continue
                #if ratioo==1.6: 
                #    print(ratioo)
                #    grayplt(imag2/255)

                for sh in [0]:
                    if sh!=0:
                        res1 = np.roll(imag2, sh, axis=0)
                        '''
                        if sh<0:
                            res1[160+sh:160,0:160]=140
                        if sh>0:
                            res1[0:sh,0:160]=140
                        '''
                    else:
                        res1=imag2
                    
                    for sh2 in [0]:
                        
                        if sh2!=0:
                            res2 = np.roll(res1, sh2, axis=1)
                            '''
                            if sh2<0:
                                res2[0:160,160+sh2:160]=140
                            if sh2>0:
                                res2[0:160,0:sh2]=140
                            '''
                        else:
                            res2=res1
                        
                        result3 = detector.detect_faces(res2)
                        #print("before sample",result3)
                        if result3==[]: continue
                        #if result3=={}: continue
                
                        keypoints3 = result3[0]['keypoints']
            
                        if keypoints3=={}:continue
                        if 'left_eye' not in keypoints3: continue
                        if 'right_eye' not in keypoints3: continue
                        if 'mouth_left' not in keypoints3: continue
                        if 'mouth_right' not in keypoints3: continue
                        if 'nose' not in keypoints3: continue
                        bounding_box = result3[0]['box']
                        #print("bounding_box4: ",bounding_box)
                        if bounding_box[3]<45: continue
                        if bounding_box[2]<45: continue
                        if result3[0]['confidence']<0.95: continue
                        
                        
                        #grayplt(res2/255)
                        
                        #res22 = cv2.cvtColor(res2, cv2.COLOR_BGR2GRAY)
                        #res22=np.dot(res2[...,:3],[.3,.6,.1])
                        res22=(res2-res2%16)
                        #res22=res2
                        res22.astype('int')
                        #res22[(res22<=200)&(res22>=120)]=res22[(res22<=200)&(res22>=120)]-res22[(res22<=200)&(res22>=120)]%120
                        #res22[(res22<=198)&(res22>=90)]=res22[(res22<=198)&(res22>=90)]-res22[(res22<=198)&(res22>=90)]%90
                        #print(res22[20,87])
                        #print(res22[50,60])
                        
                        #print("res22")
                        grayplt(res22/255)
                        #import matplotlib
                        #matplotlib.image.imsave('res22.png',res22)
                        '''
                        res22=cv2.imread('res22.jpg')
                        res22 = cv2.cvtColor(res22, cv2.COLOR_BGR2RGB)
                        cv2.imwrite('res22.jpg',res22)
                        '''
                        #raise
                        res3=np.expand_dims(res22,axis=0)
                        #predicted=model.predict(res3)
                        #print(imag1)
                        face_locations = face_recognition.face_locations(res22, number_of_times_to_upsample=2, model='hog') # For GPU, use model='cnn'
                        face_encodings = face_recognition.face_encodings(res22, face_locations, num_jitters=2)
                        print(face_locations)                
                        print(face_encodings)
                        
                        predicted=face_encodings
                        if predicted==[]: continue
                        
                        print("sampled ",img_pointer,rotate,ratioo,sh,sh2)

                        #print(predicted)
                        
                        
                        with open('dlib_merged_representation.csv', "ab") as ff:
                            savetxt(ff, predicted, delimiter=',')
                        with open('dlib_merged_representation_result.csv', "ab") as ff:
                            savetxt(ff, [img_pointer], delimiter=',')
                        
                        del predicted
                        del res3
                        gc.collect()
                        
                #raise

                    
        #grayplt(imag/255)
        #raise
        

def image_process2(imag,gamma):  
    
    img_pointer=0
    if 1:
        if debug==1: grayplt(imag/255)
        imag=adjust_gamma(imag,gamma)
        if debug==1: grayplt(imag/255)
        result = detector.detect_faces(imag)
        if debug==1: print("rawimage",result)
        if result==[]: return False,imag
        keypoints = result[0]['keypoints']
        turned=0

        while keypoints['right_eye'][1]-keypoints['left_eye'][1]>8:
            imag2 = ndimage.rotate(imag, 2, mode='nearest')
            if debug==1: print("turned")
            turned=1
            result2 = detector.detect_faces(imag2)
            if result2==[]: break
            imag=imag2
            result=result2
            keypoints = result[0]['keypoints']

        while keypoints['left_eye'][1]-keypoints['right_eye'][1]>8:
            imag2 = ndimage.rotate(imag, -2, mode='nearest')
            if debug==1: print("turned")
            turned=1
            result2 = detector.detect_faces(imag2)
            if result2==[]: break
            imag=imag2
            result=result2
            keypoints = result[0]['keypoints']

        if turned==1:
            if debug==1: grayplt(imag/255)

        # Result is an array with all the bounding boxes detected. We know that for 'ivan.jpg' there is only one.

        bounding_box = result[0]['box']

        if debug==1: print("bounding_box",bounding_box)
        if bounding_box[3]<45: return False,imag
        if bounding_box[2]<45: return False, imag

        if debug==1: print("keypoints",keypoints)   

        if keypoints=={}:return False,imag

        if 'left_eye' not in keypoints: return False,imag
        if 'right_eye' not in keypoints: return False,imag
        if 'mouth_left' not in keypoints: return False,imag
        if 'mouth_right' not in keypoints: return False,imag
        if 'nose' not in keypoints: return False,imag

        if result[0]['confidence']<0.95: return False,imag

        left_bound=int( bounding_box[0]) #+(keypoints['left_eye'][0]-bounding_box[0])/3 )
        right_bound=int( bounding_box[0]+bounding_box[2]) #-(bounding_box[0]+bounding_box[2]-keypoints['right_eye'][0])/3 )
        top_bound=int( bounding_box[1]) #+(min(keypoints['right_eye'][1],keypoints['left_eye'][1])-bounding_box[1])/3 )
        bottom_bound=int( bounding_box[1]+bounding_box[3]) #-(bounding_box[1]+bounding_box[3]-max(keypoints['mouth_right'][1],keypoints['mouth_left'][1]))/3 )
        

        '''

        left_length=keypoints['nose'][0]-bounding_box[0]

        right_length=bounding_box[2]-keypoints['nose'][0]

        top_length=keypoints['nose'][1]-bounding_box[1]

        bottom_length=bounding_box[3]-keypoints['nose'][1]

        imag=imag[ bounding_box[1]:bounding_box[1]+bounding_box[3] , bounding_box[0]:bounding_box[0]+bounding_box[2] ]

        '''

        left_length=keypoints['nose'][0]-left_bound
        right_length=right_bound-keypoints['nose'][0]
        top_length=keypoints['nose'][1]-top_bound
        bottom_length=bottom_bound-keypoints['nose'][1]        
        imag=imag[top_bound:bottom_bound, left_bound:right_bound]

        if debug==1: grayplt(imag/255)

        imag=(imag-imag%16)
        #continue
    return True,imag

def execfile(pyfile):
    with open(pyfile) as f:
        code = compile(f.read(), pyfile, 'exec')
        exec(code)
    
    
def select_operation(cmd):
    if cmd==1: #application
        execfile("webcam_cv3_dlib2.py")
        #raise
    elif cmd==2: #full training
        execfile("facenet_predict6.py")
        execfile("knn_dlib.py")
        execfile("logistic_regression_dlib.py")
        execfile("mlp_dlib.py")
        execfile("svm_dlib.py")
        execfile("voting_dlib.py")
        #raise
    elif cmd==3: #capture image
        execfile("webcam_cv3_capture.py")
        #after review frame.jpg at working folder, go to step 4
    elif cmd==4: #save image which you captured in step 3
        lookup=open("lookup.csv","r")
        lines=lookup.readlines()
        buf=0
        last=""
        for line in lines:
            if line.find(",")==-1: continue
            buf=eval( re.split(",",line)[0] )+1
        print(buf)
        lookup.close()
        os.popen("copy frame.jpg img\\frame%i.jpg" % buf)
        lookup2=open("lookup.csv","a+")
        print("Press 1 for Francis")
        print("Press 2 for Yu Ka")
        print("Press 3 for Boonping")
        print("Press 0 for Others")
        Val=input()
        lookup2.write("%i,%s\n"%(buf,Val))
        lookup2.close()
        print("your picture is saved as frame%s.jpg in img/ folder" % (buf) )
    elif cmd==5: #partial training
        #key in your frame number generated in step 4
        execfile("facenet_predict6_partial.py")
        
        
        
        
        
if __name__=="__main__":
    while 1:
        print("Press 1 for Application")
        print("Press 2 for Training")
        print("Press 3 for Image Capturing")
        print("Press 4 for Saving Captured Image")
        print("Press 5 for Partial Training")
        inp=eval(input())
        
        select_operation(inp)