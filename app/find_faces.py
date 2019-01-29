# -*-coding:utf-8-*-
import os, cv2, math, sys, time, dlib
import numpy as np
import face_recognition as fr
from PIL import Image

PREDICTOR_PATH = "app/static/shape_predictor_68_face_landmarks.dat"

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(PREDICTOR_PATH)


def find_locs(pic):
    img = cv2.imdecode(np.fromfile(pic, dtype=np.uint8), cv2.IMREAD_COLOR)
    img = cv2.resize(img, (img.shape[1], img.shape[0]))
    rects = detector(img, 1)
    with open(pic + '.txt', 'w') as f:
        for i in rects:
            f.write(str(i) + '\n')
            print(i)
