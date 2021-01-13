import regex
import os
import itertools
import time
from tensorflow.keras import models
from generiekeFuncties.fileHandlingFunctions import readDictFile, writeDict, lees_file_regels_naar_ontdubbelde_lijst
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, classificeer_vollig_image, download_image_naar_memory, sla_image_op, bigHashPicture, classificeer_vollig_image_from_file
from datetime import datetime, timedelta
from generiekeFuncties.neural_netwerk_maatwerk import recall_m, precision_m, f2_m
from numpy.random import exponential
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from generiekeFuncties.RawTherapeeDefaults import RawTherapeeDefaults
import random
import sys

grenswaarde = 0.5  # Waarde waarboven we uitgaan van een p plaatje
targetImageSize = get_target_picture_size()
percentageRandomFromChosen = 0
percentageAdditionalExtraRandom = 10
minimaalVerschilInVerhoudingImages = 1.1

urlStart = 'https://yandex.com/images/search?text='
urlEnd = '&isize=gt&iw=1920&ih=1080'

rawEditorDefaults = RawTherapeeDefaults()



screenSizes = [360, 375, 414, 667, 720, 760, 768, 812, 896, 900, 1080, 1366, 1440, 1536, 1920, 1200, 1600, 2560]
const_base_dir = '/mnt/GroteSchijf/machineLearningPictures/take1'
const_verwijzing_boekhouding_dir = os.path.join(const_base_dir, 'VerwijzingenBoekhouding')
const_model_dir = os.path.join(const_base_dir, 'BesteModellen/inceptionResnetV2_299/m_')
constBenaderde_hash_administratie_pad = os.path.join(const_verwijzing_boekhouding_dir, 'benaderde_hash.txt')
constBenaderde_url_administratie_pad = os.path.join(const_verwijzing_boekhouding_dir, 'benaderde_url.txt')
constBenaderde_query_administratie_pad = os.path.join(const_verwijzing_boekhouding_dir, 'benaderde_woorden.txt')

geladenUrlWords = [woorden.replace(' ', '%20') for woorden in lees_file_regels_naar_ontdubbelde_lijst(
    os.path.join(const_verwijzing_boekhouding_dir, 'woordenGeladen.txt'))]
bijvoegelijkeUrlWords = [woorden.replace(' ', '%20') for woorden in lees_file_regels_naar_ontdubbelde_lijst(
    os.path.join(const_verwijzing_boekhouding_dir, 'woordenBijvoegelijk.txt'))]
urlGeladenWoordenPermutations = []
for i in range(1, len(geladenUrlWords) + 1):
    urlGeladenWoordenPermutations.extend(
        ["%20".join(map(str, comb)) for comb in itertools.combinations(geladenUrlWords, i)])
urlBijvoegelijkeWoordenPermutations = []
for i in range(1, len(geladenUrlWords) + 1):
    urlBijvoegelijkeWoordenPermutations.extend(
        ["%20".join(map(str, comb)) for comb in itertools.combinations(bijvoegelijkeUrlWords, i)])
urlWoordenPermutaties = [a + '%20' + b for a in urlBijvoegelijkeWoordenPermutations for b in
                         urlGeladenWoordenPermutations]
random.shuffle(urlWoordenPermutaties)
print(str(len(urlWoordenPermutaties)) + ' permutaties')

constNieuwePlaatjesLocatie = os.path.join(const_base_dir, 'RawInput')

hash_administratie = readDictFile(constBenaderde_hash_administratie_pad)
url_administratie = readDictFile(constBenaderde_url_administratie_pad)
benaderde_woorden_administratie = readDictFile(constBenaderde_query_administratie_pad)

constClassifier = models.load_model(const_model_dir, custom_objects={'recall_m': recall_m, 'precision_m': precision_m, "f2_m": f2_m})
# Testen of hij goed geinitialiseerd is
print(str(classificeer_vollig_image_from_file(os.path.join(const_base_dir, 'maan.jpg'), constClassifier, targetImageSize)))


constBasisWachttijd = 900

options = Options()
regexPlaatje = '(https[^&]+jpg)&'  # '{"url":"([^"]+jpg)"' #{"url":"https://wallpapercave.com/wp/wp6828079.jpg"

vorigeClick = datetime.now() - timedelta(seconds=constBasisWachttijd)

ua = UserAgent()
ua.update()



def haal_query_resultaat_op(query_url, tijd_vorige_query):
    user_agent = UserAgent().random
    print(user_agent)
    #options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options,
                              executable_path="/usr/lib/chromium-browser/chromedriver")
#        driver.set_window_size(random.choice(screenSizes), random.choice(screenSizes))
    #driver.minimize_window()
    nog_wachten = max(0.0, constBasisWachttijd - (datetime.now() - tijd_vorige_query).total_seconds()) + exponential(0.3) + exponential(0.2)
    print(query_url)
    print('start wachten: ' + str(datetime.now()) + ' nog wachten: ' + str(nog_wachten))
    time.sleep(nog_wachten)
    print('Klaar met wachten: ' + str(datetime.now()))
    driver.get(query_url)
    tijd_vorige_query = datetime.now()

    # driver.click()
    page_query_resultaat = driver.page_source
    gevonden_verwijzingen_naar_plaatjes = regex.findall(regexPlaatje, page_query_resultaat , regex.IGNORECASE)
    if len(gevonden_verwijzingen_naar_plaatjes) == 0:
        print('Niks gevonden. Blijkbaar zijn we ontdekt 1.')
        driver.maximize_window()
        input("Press Enter to continue...")
        page_query_resultaat = driver.page_source
        gevonden_verwijzingen_naar_plaatjes = regex.findall(regexPlaatje, page_query_resultaat , regex.IGNORECASE)
        if len(gevonden_verwijzingen_naar_plaatjes) == 0:
            print('Niks gevonden. Blijkbaar zijn we ontdekt 2.')
            sys.exit()
    SCROLL_PAUSE_TIME = 10

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        print('scroll')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    page_query_resultaat = driver.page_source
    gevonden_verwijzingen_naar_plaatjes = regex.findall(regexPlaatje, page_query_resultaat , regex.IGNORECASE)
    driver.quit()
# Voor debug doeleinden schrijven we de pagina weg
    f = open(os.path.join(const_base_dir, 'temp/pageSave' + str(datetime.now()) + '.html'), 'w')
    f.write(page_query_resultaat)
    f.close()
    return gevonden_verwijzingen_naar_plaatjes, tijd_vorige_query


for woorden_voor_query in urlWoordenPermutaties:
    if woorden_voor_query.replace('%20', ' ') in benaderde_woorden_administratie:
        print(woorden_voor_query.replace('%20', ' ') + ' is al eens bezocht.')
    else:
        zoek_url = urlStart + woorden_voor_query + urlEnd
        print('Zoekterm: ' + woorden_voor_query.replace('%20', ' '))
        gevonden_verwijzingen, vorigeClick = haal_query_resultaat_op(query_url=zoek_url, tijd_vorige_query=vorigeClick)
        for url_plaatje in gevonden_verwijzingen:
            url_plaatje = url_plaatje.replace('%3A', ':').replace('%2F', '/')
            if url_plaatje in url_administratie:
                print(url_plaatje + ' is al eens benaderd.')
            else:
                url_administratie[url_plaatje] = str(datetime.now())
                #print(url_plaatje)
                img = download_image_naar_memory(url_plaatje)
                if img is None:
                    print(url_plaatje + ' niet gelezen.')
                else:
                    hash_groot = bigHashPicture(img)
                    if hash_groot == '':
                        print(url_plaatje + ' wordt overgeslagen omdat de hash niet klopt')
                    elif hash_groot in hash_administratie:
                        print(url_plaatje + ' al eens gevonden.')
                    elif max(img.size) < 1000:
                        print(url_plaatje + ' is te klein. Afmetingen: ' + str(img.size))
                    else:
                        hash_administratie[hash_groot] = str(datetime.now())
                        resultaat = classificeer_vollig_image(img, url_plaatje, constClassifier, targetImageSize)
                        keuze = 'niet'
                        if resultaat >= grenswaarde:
                            keuze = 'wel'
                        print(url_plaatje + ' ' + keuze)
                        file_naam = os.path.join(constNieuwePlaatjesLocatie, keuze, hash_groot + ".jpg")
                        sla_image_op(img, file_naam)
                        if keuze == 'wel':
                            rawEditorDefaults.maak_specifiek(file_naam, img.size)
                        writeDict(hash_administratie, constBenaderde_hash_administratie_pad)
                writeDict(url_administratie, constBenaderde_url_administratie_pad)
        benaderde_woorden_administratie[woorden_voor_query.replace('%20', ' ')] = datetime.now()
        writeDict(benaderde_woorden_administratie, constBenaderde_query_administratie_pad)
        print('Afgerond ', woorden_voor_query.replace('%20', ' '))
        print("#######################################################################################################################################")
