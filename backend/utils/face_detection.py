import json
from imutils import face_utils
import numpy as np
import argparse
import imutils
import dlib
import cv2
import time
import boto3
import os

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
bucket_name = 'utpr'
input_path = 'inputs/'
result_path = 'results/'

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,
                help="path to facial landmark predictor")
ap.add_argument("-i", "--image", required=True,
                help="path to input image")
args = vars(ap.parse_args())

shape_predictor = './shape_predictor_68_face_landmarks.dat'


def face_remap(shape):
    remapped_image = cv2.convexHull(shape)
    return remapped_image


def lambda_handler(event, context):
    image = './' + args["image"]
    image = cv2.imread(image)
    image = imutils.resize(image, width=500)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(shape_predictor)
    rects = detector(gray, 1)
    for (i, rect) in enumerate(rects):
        shape = predictor(gray, rect)
        # convert facial landmarks to numpy array
        shape = face_utils.shape_to_np(shape)

        # initialize new array layout as shape
        xmin, ymin = shape.min(axis=0)
        xmax, ymax = shape.max(axis=0)

        feature_mask = np.zeros((image.shape[0], image.shape[1]), np.uint8)
        remapped_shape = face_remap(shape)

        cv2.fillConvexPoly(feature_mask, remapped_shape, [255])
        out_face = cv2.bitwise_and(image, image, mask=feature_mask)

        (x, y, w, h) = cv2.boundingRect(remapped_shape)
        alpha = np.zeros((h, w), dtype=np.uint8)
        feature_mask = feature_mask[y:y + h, x:x + w]
        out_face = out_face[y:y + h, x:x + w]
        alpha[feature_mask == 255] = 255

        mv = []
        mv.append(out_face)
        mv.append(alpha)

        out_face = cv2.merge(mv)

        cv2.imwrite(args["image"], out_face)
        s3_client.upload_file(output, bucket_name, result_path + args["image"])

    print('suc')