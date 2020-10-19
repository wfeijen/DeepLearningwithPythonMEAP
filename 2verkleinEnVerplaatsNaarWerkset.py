# Maakt directories met positieve en negatieve samples.
# De samples worden gedupliceerd door twee keer te croppen zodat de crops samen het volledige rechthoek vullen
# Vierkante samples worden dus in effect gedupliceerd, maar dat komt niet vaak voor
# De reden hiervan is dat we vervorming willen voorkomen die bij een resize van rechthoek naar vierkant optreed.
# De verdubbeling is natuurlijk ook een soort poor mans augmentation
# Daarnaast vind er een herschaling van originelen plaats om het volume op schijf te beperken

import os
from generiekeFuncties.fileHandlingFunctions import give_list_of_images,  \
    maak_directory_helemaal_leeg, prioriteerGecontroleerd, maak_subdirectory_en_vul_met_random_squared_images
from generiekeFuncties.plaatjesFuncties import get_target_picture_size
from generiekeFuncties.utilities import geeftVoortgangsInformatie, initializeerVoortgangsInformatie

voortgangs_informatie = initializeerVoortgangsInformatie("start verklein en verplaats")

maximumAantalFilesPerKant = 30000
percentageTrain = 0.8
maximumAantalFilesPerKant = int(maximumAantalFilesPerKant / percentageTrain)
percentageTest = 0.1
percentageValidation = 0.1
maximaalVerschilInVerhoudingAantalImages = 2.0

# The path to the directory where the original
# data set was uncompressed
root = '/mnt/GroteSchijf/machineLearningPictures/take1'
full_data_set_dir = os.path.join(root, 'ontdubbeldEnVerkleind')
target_base_dir = '/mnt/GroteSchijf/machineLearningPictures/werkplaats'
targetSizeImage = get_target_picture_size()

nietFileNames = give_list_of_images(subdirName='niet', baseDir=full_data_set_dir)
welFileNames = give_list_of_images(subdirName='wel', baseDir=full_data_set_dir)

aantalSamplesWel = min(len(welFileNames), maximumAantalFilesPerKant)
aantalSamplesNiet = min(len(nietFileNames), maximumAantalFilesPerKant)

if aantalSamplesWel >= aantalSamplesNiet:
    aantalSamplesWel = int(min(aantalSamplesWel, int(aantalSamplesNiet * maximaalVerschilInVerhoudingAantalImages)))
else:
    aantalSamplesNiet = int(min(aantalSamplesNiet, int(aantalSamplesWel * maximaalVerschilInVerhoudingAantalImages)))

aantalSamplesTrainWel = int(percentageTrain * aantalSamplesWel)
aantalSamplesTestWel = int(percentageTest * aantalSamplesWel)

aantalSamplesTrainNiet = int(percentageTrain * aantalSamplesNiet)
aantalSamplesTestNiet = int(percentageTest * aantalSamplesNiet)
aantalSamplesValidation = min(aantalSamplesNiet - aantalSamplesTrainNiet - aantalSamplesTestNiet,
                              aantalSamplesWel - aantalSamplesTrainWel - aantalSamplesTestWel)

voortgangs_informatie = geeftVoortgangsInformatie("Start leegmaken dirs", voortgangs_informatie)

maak_directory_helemaal_leeg(target_base_dir)
train_dir = os.path.join(target_base_dir, 'train')
os.mkdir(train_dir)
test_dir = os.path.join(target_base_dir, 'test')
os.mkdir(test_dir)
validation_dir = os.path.join(target_base_dir, 'validation')
os.mkdir(validation_dir)

voortgangs_informatie = geeftVoortgangsInformatie("Start niet files", voortgangs_informatie)

nietFileNames = prioriteerGecontroleerd(nietFileNames, aantalSamplesNiet, "n")
nietFileNames = maak_subdirectory_en_vul_met_random_squared_images(subSubDirName='niet',
                                                                   sourceDir=full_data_set_dir,
                                                                   targetDir=train_dir,
                                                                   numberOfFiles=aantalSamplesTrainNiet,
                                                                   fileNames=nietFileNames,
                                                                   targetSizeImage=targetSizeImage)
nietFileNames = maak_subdirectory_en_vul_met_random_squared_images(subSubDirName='niet',
                                                                   sourceDir=full_data_set_dir,
                                                                   targetDir=test_dir,
                                                                   numberOfFiles=aantalSamplesTestNiet,
                                                                   fileNames=nietFileNames,
                                                                   targetSizeImage=targetSizeImage)
nietFileNames = maak_subdirectory_en_vul_met_random_squared_images(subSubDirName='niet',
                                                                   sourceDir=full_data_set_dir,
                                                                   targetDir=validation_dir,
                                                                   numberOfFiles=aantalSamplesValidation,
                                                                   fileNames=nietFileNames,
                                                                   targetSizeImage=targetSizeImage)

voortgangs_informatie = geeftVoortgangsInformatie("Start wel files", voortgangs_informatie)

welFileNames = prioriteerGecontroleerd(welFileNames, aantalSamplesWel, "w")
welFileNames = maak_subdirectory_en_vul_met_random_squared_images(subSubDirName='wel',
                                                                  sourceDir=full_data_set_dir,
                                                                  targetDir=train_dir,
                                                                  numberOfFiles=aantalSamplesTrainWel,
                                                                  fileNames=welFileNames,
                                                                  targetSizeImage=targetSizeImage)
welFileNames = maak_subdirectory_en_vul_met_random_squared_images(subSubDirName='wel',
                                                                  sourceDir=full_data_set_dir,
                                                                  targetDir=test_dir,
                                                                  numberOfFiles=aantalSamplesTestWel,
                                                                  fileNames=welFileNames,
                                                                  targetSizeImage=targetSizeImage)
welFileNames = maak_subdirectory_en_vul_met_random_squared_images(subSubDirName='wel',
                                                                  sourceDir=full_data_set_dir,
                                                                  targetDir=validation_dir,
                                                                  numberOfFiles=aantalSamplesValidation,
                                                                  fileNames=welFileNames,
                                                                  targetSizeImage=targetSizeImage)

voortgangs_informatie = geeftVoortgangsInformatie("Klaar", voortgangs_informatie)
