from PIL import Image, ImageStat
from send2trash import send2trash
import math
import os

def getTargetPictureSize():
    return 240

def remove_small_images_and_give_list_of_proper_sized_images(subdirName, baseDir, remove_small_files_from_source,
                                                             minimum_size_short_side_image,
                                                             maximum_size_short_side_image):
    data_set_dir = os.path.join(baseDir, subdirName)
    file_names = [f for f in os.listdir(data_set_dir) if os.path.isfile(os.path.join(data_set_dir, f))]
    verwijderd_vanwege_extentie = 0
    verwijderd_vanwege_te_klein = 0
    kleiner_gemaakt = 0
    for file_name in file_names:
        dummy, file_extension = os.path.splitext(file_name)
        full_file_name = os.path.join(data_set_dir, file_name)
        if file_extension != '.jpg' and file_extension != '.jpeg':
            send2trash(full_file_name)
            file_names.remove(file_name)
        else:
            im = Image.open(full_file_name)
            size = im.size
            if min(size) < minimum_size_short_side_image:
                if remove_small_files_from_source:
                    send2trash(full_file_name)
                file_names.remove(file_name)
            elif min(size) > maximum_size_short_side_image:
                size = math.ceil(maximum_size_short_side_image * max(size) / min(size))
                im.thumbnail((size, size), Image.ANTIALIAS)
                im = im.convert('RGB')
                send2trash(full_file_name)
                im.save(full_file_name)
    return file_names, verwijderd_vanwege_extentie, verwijderd_vanwege_te_klein, kleiner_gemaakt

def resizeImage(im, sx, sy, vergrotingsfactor):
    sx = int(sx * vergrotingsfactor)
    sy = int(sy * vergrotingsfactor)
    return im.resize(size=(sx, sy), resample= Image.BICUBIC), sx, sy

def convertImageToSquareIm(im, targetSizeIm):
    im = im.convert("RGB")
    sx_oorspronkelijk, sy_oorspronkelijk = im.size
    meanColor = tuple([math.floor(n) for n in ImageStat.Stat(im)._getmean()])
    antwoord = Image.new(mode="RGB", size=(targetSizeIm, targetSizeIm), color=meanColor)
    # Als plaatje volledig binnen nieuwe image valt vergroten we het totdat de langste
    # as gelijk is aan targetSizeIm
    if max(sx_oorspronkelijk, sy_oorspronkelijk) > 4 * min(sx_oorspronkelijk, sy_oorspronkelijk): # Dit gaat toch niks worden
        return sx_oorspronkelijk, sy_oorspronkelijk, None
    if min(sx_oorspronkelijk, sy_oorspronkelijk) * 2 < targetSizeIm:
        return sx_oorspronkelijk, sy_oorspronkelijk, None
    if max(sx_oorspronkelijk, sy_oorspronkelijk) < targetSizeIm:
        im, sx, sy = resizeImage(im, sx_oorspronkelijk, sy_oorspronkelijk, targetSizeIm / max(sx_oorspronkelijk, sy_oorspronkelijk))
        antwoord.paste(im, ((targetSizeIm - sx) // 2, (targetSizeIm - sy) // 2))
        return sx_oorspronkelijk, sy_oorspronkelijk, antwoord
    # ultra breed plaatje
    if sx_oorspronkelijk > sy_oorspronkelijk * 2:
        im, sx, sy = resizeImage(im, sx_oorspronkelijk, sy_oorspronkelijk, targetSizeIm / (sy_oorspronkelijk * 2))
        im_crop1 = im.crop((0, 0, targetSizeIm, sy))
        im_crop2 = im.crop((sx - targetSizeIm, 0, sx, sy))
        antwoord.paste(im_crop1, (0, 0))
        antwoord.paste(im_crop2, (0, targetSizeIm // 2))
        return sx_oorspronkelijk, sy_oorspronkelijk, antwoord
    if sx_oorspronkelijk * 2 < sy_oorspronkelijk:
        im, sx, sy = resizeImage(im, sx_oorspronkelijk, sy_oorspronkelijk, targetSizeIm / (sx_oorspronkelijk * 2))
        im_crop1 = im.crop((0, 0, sx, targetSizeIm))
        im_crop2 = im.crop((0, sy - targetSizeIm, sx, sy))
        antwoord.paste(im_crop1, (0, 0))
        antwoord.paste(im_crop2, (targetSizeIm // 2, 0))
        return sx_oorspronkelijk, sy_oorspronkelijk, antwoord
    if sx_oorspronkelijk >= sy_oorspronkelijk: # (en sx <= 2* sy)
        im, sx, sy = resizeImage(im, sx_oorspronkelijk, sy_oorspronkelijk, targetSizeIm / sx_oorspronkelijk)
        antwoord.paste(im, (0, (targetSizeIm - sy) // 2))
        return sx_oorspronkelijk, sy_oorspronkelijk, antwoord
    # Nu moet wel gelden sx <= sy en 2 * sx >= sy
    im, sx, sy = resizeImage(im, sx_oorspronkelijk, sy_oorspronkelijk, targetSizeIm / sy_oorspronkelijk)
    antwoord.paste(im, ((targetSizeIm - sx) // 2, 0))
    return sx_oorspronkelijk, sy_oorspronkelijk, antwoord

def convertImageToSquareIm_from_file(imagePath, targetSizeIm):
    # returns a square part of the image sized to target size
    im = Image.open(imagePath)
    return convertImageToSquareIm(im=im, targetSizeIm=targetSizeIm)

def get_square_images_from_image(im, targetSizeIm, minimaalVerschilInVerhoudingImages):
    # returns a square part of the image sized to target size
    im = im.convert("RGB")
    sx, sy = im.size
    antwoord = []
    # kijken of het plaatje wel groot genoeg is
    if min(sx, sy) < targetSizeIm:
        return antwoord
    # links of boven bij breed of hoog plaatje
    if sx >= (sy * minimaalVerschilInVerhoudingImages):
        antwoord.append(im.crop((0, 0, sy, sy)))
    elif (sx * minimaalVerschilInVerhoudingImages)<= sy:
        antwoord.append(im.crop((0, 0, sx, sx)))
    # en altijd het centrum omdat daar meestal de meeste inforamtie is
    if sx > sy:
        left = (sx - sy) / 2
        antwoord.append(im.crop((left, 0, left + sy, sy)))
    else:
        top = (sy - sx) / 2
        antwoord.append(im.crop((0, top, sx, top + sx)))
    # en rechts of onder bij breed of hoog plaatje
    if sx >= (sy * minimaalVerschilInVerhoudingImages):
        left = sx - sy
        antwoord.append(im.crop((left, 0, left + sy, sy)))
    elif (sx * minimaalVerschilInVerhoudingImages)<= sy:
        top = sy - sx
        antwoord.append(im.crop((0, top, sx, top + sx)))
    return antwoord

def get_square_images_from_file(imagePath, targetSizeIm, minimaalVerschilInVerhoudingImages):
    # returns a square part of the image sized to target size
    im = Image.open(imagePath)
    return get_square_images_from_image(im=im, targetSizeIm=targetSizeIm, minimaalVerschilInVerhoudingImages=minimaalVerschilInVerhoudingImages)
