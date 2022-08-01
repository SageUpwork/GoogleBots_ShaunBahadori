#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------
import json
import math
import os
import logging
import platform
import re
import time
from concurrent.futures import ThreadPoolExecutor
from random import randint

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
def loggerInit(logFileName):
    try:
        os.makedirs("logs")
    except:
        pass
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    file_handler = logging.FileHandler(f'logs/{logFileName}')
    # file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    # stream_handler.setLevel(logging.ERROR)
    logger.addHandler(stream_handler)
    return logger


logger = loggerInit(logFileName="backlink.googleBot.log")


def seleniumLiteTrigger():
    from seleniumwire import webdriver
    with open("vpn.config.json") as json_data_file:
        configs = json.load(json_data_file)

    atmpt = 0
    while atmpt < 10:
        try:
            VPN_User = configs['VPN_User']
            VPN_Pass = configs['VPN_Pass']
            VPN_IP_PORT = configs['VPN_IP_PORT'][randint(0, len(configs['VPN_IP_PORT']) - 1)]
            VPN_IP = VPN_IP_PORT.split(":")[0]
            VPN_Port = VPN_IP_PORT.split(":")[1]

            options = {
                'proxy': {
                    "http": f"http://{VPN_User}:{VPN_Pass}@{VPN_IP}:{VPN_Port}",
                    "https": f"https://{VPN_User}:{VPN_Pass}@{VPN_IP}:{VPN_Port}",
                    'no_proxy': 'localhost,127.0.0.1'
                }
            }
            if "Windows" in str(platform.system()):
                # WINDOWS
                geckoPath = r"driver\\geckodriver.exe"
                moz_profPath = r"C:\Users\SaGe\AppData\Roaming\Mozilla\Firefox\Profiles\jbz9m3sj.default"
                # driver = webdriver.Firefox(options=options, executable_path=geckoPath)
            elif "Linux" in str(platform.system()):
                # Linux
                geckoPath = r"driver/geckodriver"
                moz_profPath = r"/home/sage/.mozilla/firefox/249x8q9b.default-release"
            else:
                # Mac
                geckoPath = r"driver/geckodriver"
                moz_profPath = r"/Users/SaGe/Library/Application Support/Firefox/Profiles/24po1ob3.default-release"

            driver = webdriver.Firefox(executable_path=geckoPath, seleniumwire_options=options)
            time.sleep(randint(100, 5000) / 1000)
            try:
                driver.get("https://ifconfig.me/")
                time.sleep(randint(50,150)/100)
                driver.refresh()
                if '''<a href="http://ifconfig.me">What Is My IP Address? - ifconfig.me</a>''' in driver.page_source:
                    logger.debug(f"New Rotated IP: {driver.find_element(by=By.ID, value='ip_address').text}")
                    return driver

                # driver.get(f"https://www.google.com")
                # driver.get(f"https://www.google.com/search?q=facebook")
                # if len(driver.find_elements(by=By.TAG_NAME, value="a")) < 5: raise Exception("Compromised IP, Rotating")
                time.sleep(randint(50,150)/100)
                # TODO remove
                return driver
            except:
                driver.quit()
                raise Exception("BadSession")

        except Exception as e:
            atmpt += 1

            logger.debug("IP unavailable, rotating.")
            if atmpt == 10:
                raise e


def fetchMatchedEntries(driver, refWord, refDomain):
    entries = {a: {"href":x.get_attribute("href"),"unit":x} for a, x in enumerate(driver.find_elements(by=By.TAG_NAME, value="a"))}

    matched = {}
    for x in entries:
        try:
            if (refWord in entries[x]['href']) & (refDomain in entries[x]['href']):
                # print({x: entries[x]})
                matched[x] = entries[x]
        except:
            continue
    print(matched.keys())
    return matched



def googleSearchModules(driver, searchKey, refWord, refDomain, pageMax=10):
    driver.maximize_window()
    time.sleep(randint(100, 5000) / 100)
    driver.get(f"https://www.google.com/search?q={searchKey}")
    time.sleep(randint(100, 5000) / 100)
    # time.sleep(randint(50, 1500) / 100)
    matched = fetchMatchedEntries(driver, refWord, refDomain)
    #
    # refWord, refDomain = ("psychcentral.com","teenage-depression-facts")
    #

    pageNum = 0
    while len(matched) == 0:
        if pageNum == pageMax:
            logger.debug(f"Result page {pageMax} reached. Halting run")
            # driver.quit()
            raise Exception("Keyword not found in Google Search data, increase pageMax or improve keyword precision")
        logger.debug(f"Starting search results page {pageNum}")
        driver.find_element(by=By.ID, value="pnnext").click()
        pageNum += 1
        matched = {**matched, **fetchMatchedEntries(driver, refWord, refDomain)}
    return matched


def secndryPageOps(driver, matched, secndaryAnchorText, refUrl):
    matched[list(matched.keys())[0]]['unit'].click()
    time.sleep(randint(100, 5000) / 100)
    time.sleep(5)
    try:
        try: WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.TAG_NAME, "img")))
        except: pass
        time.sleep(randint(100, 5000) / 1000)
        # driver.execute_script("document.body.style.zoom='50 %'")
        driver.execute_script("arguments[0].scrollIntoView();", [x for x in driver.find_elements(by=By.TAG_NAME, value="a") if secndaryAnchorText.lower() in x.text.lower()][0])
        time.sleep(2)
        ActionChains(driver).send_keys(Keys.PAGE_UP).perform()
        time.sleep(randint(100, 5000) / 1000)
        [x for x in driver.find_elements(by=By.TAG_NAME, value="a") if secndaryAnchorText in x.text][0].click()
        time.sleep(2)
    except Exception as e:
        logger.warning(f"Cant find 2nd anchor text {secndaryAnchorText} in {refUrl} : {e}")


def tertryPageOps(driver, atmpt=0):
    # Click on any random url after
    tertryUrlList = driver.find_elements(by=By.TAG_NAME, value="a")
    while atmpt < 5:
        try:
            try: WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.TAG_NAME, "img")))
            except: pass
            # driver.execute_script("document.body.style.zoom='50 %'")
            time.sleep(randint(100, 5000) / 1000)
            driver.execute_script("arguments[0].scrollIntoView();", tertryUrlList[randint(0, len(tertryUrlList))])
            time.sleep(2)
            tertryUrlList[randint(0, len(tertryUrlList))].click()
            time.sleep(2)
            return True
            # driver.quit()
        except:
            atmpt += 1
            time.sleep(2)
            if atmpt == 4:
                logger.debug("Cant find clickable tertiary urls")
                return False
                # driver.quit()
            continue


def singleThread(searchKey, refUrl, secndaryAnchorText):
    logger.debug("Starting new browser proxy")
    driver = seleniumLiteTrigger()
    try:
        refWord = refUrl.strip("/").split("/")[-1]
        refDomain = re.findall(f'https?:\/\/([^\/]+)\/', refUrl)[0]

        matched = googleSearchModules(driver, searchKey, refWord, refDomain, pageMax=10)
        if len(matched) > 0:
            secndryPageOps(driver, matched, secndaryAnchorText, refUrl)
            time.sleep(3)
            tertryPageOps(driver)
            time.sleep(randint(100, 5000) / 1000)
    except Exception as e:
        logger.debug(e)
    driver.quit()


def core(searchKey, refUrl, secndaryAnchorText, trafficCount, parallelWorkerCount):
    confData = {
        "searchKey": searchKey,
        "refUrl": refUrl,
        "secndaryAnchorText": secndaryAnchorText,
        "parallelWorkerCount": parallelWorkerCount
    }
    logger.debug(f"Started run with configs: {json.dumps(confData, indent=3)}")
    # singleThread(searchKey, refUrl, secndaryAnchorText)

    for a in range(math.ceil(trafficCount/parallelWorkerCount)):
        logger.debug(f"Completed {a*parallelWorkerCount} traffic generation")
        with ThreadPoolExecutor(max_workers=parallelWorkerCount) as executor:
            for x in range(parallelWorkerCount):
                executor.submit(singleThread, searchKey, refUrl, secndaryAnchorText)
            executor.shutdown(wait=True)

    logger.debug(f"Completed run with configs: {json.dumps(confData, indent=3)}")


if __name__ == '__main__':
    '''

    '''
