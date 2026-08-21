import numpy as np

from skimage.transform import rescale, resize
from skimage.util import montage, crop, view_as_windows

from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, BatchNormalization, Activation, Dense, Dropout
from tensorflow.keras.layers import Conv2D, Conv2DTranspose
from tensorflow.keras.layers import MaxPooling2D, GlobalMaxPool2D
from tensorflow.keras.layers import concatenate, add

import tensorflow.keras.backend as K
from tensorflow.keras.losses import binary_crossentropy

import matplotlib.pyplot as plt

import cv2

class Unet(object):

    def __init__(self, model_path):

        # defining helper function - consider moving
        def dice_coef(y_true, y_pred, smooth=1):
            intersection = K.sum(y_true * y_pred, axis=[1, 2, 3])
            union = K.sum(y_true, axis=[1, 2, 3]) + K.sum(y_pred, axis=[1, 2, 3])
            return K.mean((2. * intersection + smooth) / (union + smooth), axis=0)

        def dice_p_bce(in_gt, in_pred):
            return 1e-3 * binary_crossentropy(in_gt, in_pred) - dice_coef(in_gt, in_pred)

        def true_positive_rate(y_true, y_pred):
            return K.sum(K.flatten(y_true) * K.flatten(K.round(y_pred))) / K.sum(y_true)

        def euc_dist_keras(y_true, y_pred):
            return K.sqrt(K.sum(K.square(y_true - y_pred), axis=-1, keepdims=True))
        
        # loading the model # ADD LOADING IN THRESHOLD AND STUFF
        self.model = load_model(model_path,
                                custom_objects={
                                    "dice_coef": dice_coef,
                                    "true_positive_rate": true_positive_rate,
                                    "euc_dist_keras": euc_dist_keras,
                                    "dice_p_bce": dice_p_bce
                                })
        
        # self.summary = self.model.summary()
    

    def predict(self, retina, mode="count", threshold=0.99, batch_size=32):          # CHAGE IT TO ACCEPT PLAIN IMAGES ALSO

        # run model prediction
        blocks = np.expand_dims(retina.blocks, axis=-1)
        preds = self.model.predict(blocks, batch_size=batch_size, verbose=1)

        # REMOVE ME LATER
        retina.preds = preds.squeeze()

        # removes hals of the overlap area on each side so the stiching is seamless
        cropped = crop(preds.squeeze(), (
            (0, 0),
            (retina.right_pad, retina.right_pad),
            (retina.right_pad, retina.right_pad),
        ))

        # stiches the patches together and crops the excess padding
        mon = montage(cropped, grid_shape=retina.new_shape)
        delta_shape = mon.shape - retina.shape

        probability_map = crop(mon, ((0, delta_shape[0]), (0, delta_shape[1])))

        probability_map = cv2.resize(probability_map, (retina.original_image.shape[1], (retina.original_image.shape[0])))

        prediction = probability_map > threshold

        # based on the prediction mode, saves the results differently in the retina object
        if mode == "count":
            retina.probability_map = probability_map
            retina.prediction = prediction
        elif mode == "seg":
            retina.segmentation_probability_map = prediction
            retina.segmentation = prediction

        # Old skimage resize. Uses a lot of ram
        # retina.probability_map = resize(retina.probability_map, retina.original_image.shape)

        # applies the threshold                                                                                                  # MAKE IT CHANGABLE
        # retina.prediction = retina.probability_map > threshold
