from keras import layers
from keras import models
from keras import optimizers
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator

import matplotlib.pyplot as plt
import os

epochs = 100
steps = 100
batchSize = 32
batchSizeTest = 100

model = models.Sequential()
model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 3)))
model.add(layers.BatchNormalization())
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.BatchNormalization())
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(128, (3, 3), activation='relu'))
#model.add(layers.Dropout(0.25)) #2
model.add(layers.BatchNormalization())
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(128, (3, 3), activation='relu'))
model.add(layers.Dropout(0.25)) #1
model.add(layers.BatchNormalization())
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Flatten())
model.add(layers.Dropout(0.5))
model.add(layers.Dense(512, activation='relu'))
model.add(layers.BatchNormalization(trainable=))
model.add(layers.Dense(1, activation='sigmoid'))
model.summary()

lr_schedule_exponential = optimizers.schedules.ExponentialDecay(
    initial_learning_rate=1.0,
    decay_steps=100000,
    decay_rate=0.96,
    staircase=True)

lr_schedule_polynomial = optimizers.schedules.PolynomialDecay(maxEpochs=epochs,
                                                              initAlpha=0.1,
                                                              power=2)

model.compile(loss='binary_crossentropy',
              optimizer=optimizers.adadelta(),
              metrics=['acc'])



# 0 basic                                             loss: 0.4510 - acc: 0.7955 - val_loss: 0.2912 - val_acc: 0.8273
# 1 + normalistation                                  loss: 0.4091 - acc: 0.8075 - val_loss: 0.3678 - val_acc: 0.8370
# 2 + dropout 1                                       loss: 0.4002 - acc: 0.8175 - val_loss: 0.3059 - val_acc: 0.8731
# 3 +- dropout 2 blijkbaar werkt die te verstorend    loss: 0.4049 - acc: 0.8150 - val_loss: 0.4560 - val_acc: 0.8138
# 4 + Adam() ipv #RMSprop(lr=1e-4)                    loss: 0.3182 - acc: 0.8615 - val_loss: 0.4637 - val_acc: 0.8454
# 5 - Alle augmentation (we hebben veel plaatjes)     loss: 0.1599 - acc: 0.9305 - val_loss: 0.3016 - val_acc: 0.8744
# 6 - Adam() ipv #RMSprop(lr=1e-4)                    loss: 0.2849 - acc: 0.8830 - val_loss: 0.3692 - val_acc: 0.8589
# 7 + Adadelta opv RMSprop                            loss: 0.1333 - acc: 0.9475 - val_loss: 0.1455 - val_acc: 0.9027
# 8 herhaal                                           loss: 0.1287 - acc: 0.9525 - val_loss: 0.2039 - val_acc: 0.9117
# 9 +-  lr=1.0, epsilon=1e-6                          loss: 0.1265 - acc: 0.9520 - val_loss: 0.7876 - val_acc: 0.8711
# 10 + lr = lr_schedule_polynomial power = 1          loss: 0.1311 - acc: 0.9520 - val_loss: 0.2652 - val_acc: 0.9143 raar dit zou niks uit moeten maken
# 11 + lr = lr_schedule_polynomial power = 2          loss: 0.1232 - acc: 0.9505 - val_loss: 0.1964 - val_acc: 0.9291 raar dit zou niks uit moeten maken
# 12 batchSize 100 -> 32                              loss: 0.1423 - acc: 0.9445 - val_loss: 0.5704 - val_acc: 0.7494 validatie erg eratic
# 13 adadelta() ipv parameters                        loss: 0.1425 - acc: 0.9435 - val_loss: 0.3155 - val_acc: 0.8930
# 11 + lr = lr_schedule_polynomial power = 3
# 11 porwer omhoog
# 10 + lr=lr_schedule ipv 1.0
# 10 + train batch_size=20->100
# 11 + trainable = False


base_dir = '/mnt/GroteSchijf/dogs_vs_cats/smallSelection'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')
train_cats_dir = os.path.join(train_dir, 'cats')
train_dogs_dir = os.path.join(train_dir, 'dogs')
validation_cats_dir = os.path.join(validation_dir, 'cats')
validation_dogs_dir = os.path.join(validation_dir, 'dogs')
test_cats_dir = os.path.join(test_dir, 'cats')
test_dogs_dir = os.path.join(test_dir, 'dogs')

train_datagen = ImageDataGenerator(rescale=1./255,
                                   #rotation_range=40,
                                   #width_shift_range=0.2,
                                   #height_shift_range=0.2,
                                   #shear_range=0.2,
                                   #zoom_range=0.2,
                                   #horizontal_flip=True
                                   )

# All test images will be rescaled by 1./255
# trainingsdata wordt augmented
#train_datagen = ImageDataGenerator(rescale=1./255)
test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    # This is the target directory
    train_dir,
    # All images will be resized to 150x150
    target_size=(150, 150),
    batch_size=batchSize,
    # Since we use binary_crossentropy loss, we need binary labels
    class_mode='binary')

validation_generator = test_datagen.flow_from_directory(
    validation_dir,
    target_size=(150, 150),
    batch_size=20,
    class_mode='binary')

for data_batch, labels_batch in train_generator:
    print('data batch shape:', data_batch.shape)
    print('labels batch shape:', labels_batch.shape)
    break

history = model.fit_generator(
    train_generator,
    steps_per_epoch=steps,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=50)
model.save('cats_and_dogs_small_2.h5')

acc = history.history['acc']
val_acc = history.history['val_acc']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(acc) + 1)
plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.legend()
plt.figure()
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()


if lr_schedule is not None:
	lr_schedule.plot(epochs)
plt.show()