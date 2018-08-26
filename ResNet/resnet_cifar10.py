
"""
Adapted from keras example cifar10_cnn.py
Train ResNet-18 on the CIFAR10 small images dataset.
GPU run command with Theano backend (with TensorFlow, the GPU is automatically used):
    THEANO_FLAGS=mode=FAST_RUN,device=gpu,floatX=float32 python cifar10.py
"""
from __future__ import print_function
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.utils import np_utils
from keras.callbacks import ReduceLROnPlateau, CSVLogger, EarlyStopping

import numpy as np
import resnet

import os
import keras
import matplotlib.pyplot as plt

class LossHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
    	self.i = 0
    	self.x = []
    	#self.acc = []
    	self.acc = []
    	self.logs = []

    def on_batch_end(self, batch, logs={}):
    	self.logs.append(logs)
    	self.x.append(self.i)
    	#self.acc.append(logs.get('acc'))
    	self.acc.append(logs.get('acc'))
    	self.i += 1

#lr_reducer = ReduceLROnPlateau(factor=np.sqrt(0.1), cooldown=0, patience=5, min_lr=0.5e-6)
#early_stopper = EarlyStopping(min_delta=0.001, patience=10)
#csv_logger = CSVLogger('resnet18_cifar10.csv')

#batch_size = 32
batch_size = 128
nb_classes = 10
#nb_epoch = 200
nb_epoch = 128 # 64K iterations
#data_augmentation = True
data_augmentation = False

save_dir = os.path.join(os.getcwd(), 'saved_models')
model_name = 'resnet_cifar10_trained_model.h5'

# input image dimensions
img_rows, img_cols = 32, 32
# The CIFAR10 images are RGB.
img_channels = 3

# The data, shuffled and split between train and test sets:
(X_train, y_train), (X_test, y_test) = cifar10.load_data()

# Convert class vectors to binary class matrices.
Y_train = np_utils.to_categorical(y_train, nb_classes)
#Y_test = np_utils.to_categorical(y_test, nb_classes)

X_train = X_train.astype('float32')
#X_test = X_test.astype('float32')

# subtract mean and normalize
mean_image = np.mean(X_train, axis=0)
X_train -= mean_image
#X_test -= mean_image
X_train /= 128.
#X_test /= 128.

opt = keras.optimizers.SGD(lr=0.1, decay=1e-4, momentum=0.9)	# SGD

model = resnet.ResnetBuilder.build_resnet_18((img_channels, img_rows, img_cols), nb_classes)
model.compile(loss='categorical_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

if not data_augmentation:
    print('Not using data augmentation.')
    history = LossHistory()
    model.fit(X_train, Y_train,
              batch_size=batch_size,
              epochs=nb_epoch,
              #validation_data=(X_test, Y_test),
              #shuffle=True,
              shuffle=False,
              #callbacks=[lr_reducer, early_stopper, csv_logger]
              callbacks=[history])
else:
    print('Using real-time data augmentation.')
    # This will do preprocessing and realtime data augmentation:
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False)  # randomly flip images

    # Compute quantities required for featurewise normalization
    # (std, mean, and principal components if ZCA whitening is applied).
    datagen.fit(X_train)

    history = LossHistory()
    # Fit the model on the batches generated by datagen.flow().
    model.fit_generator(datagen.flow(X_train, Y_train, batch_size=batch_size),
                        steps_per_epoch=X_train.shape[0] // batch_size,
                        validation_data=(X_test, Y_test),
                        epochs=nb_epoch, verbose=1, max_q_size=100,
                        #callbacks=[lr_reducer, early_stopper, csv_logger]
                        callbacks=[history])

# Save model and weights
if not os.path.isdir(save_dir):
    os.makedirs(save_dir)
model_path = os.path.join(save_dir, model_name)
model.save(model_path)
print('Saved trained model at %s ' % model_path)

#print(history.x)
#print(history.acc)
plt.xlabel('Iterations')
plt.ylabel('Accuracy')
plt.title("ResNet CIFAR-10 Without CLR")
plt.plot(history.x, history.acc)
plt.savefig('images_optimizers/resnet_cifar10.png')
plt.show()