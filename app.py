#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------
import json
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

            options = {
                'proxy': {
                    "http": f"http://{VPN_User}:{VPN_Pass}@{VPN_IP_PORT}",
                    "https": f"https://{VPN_User}:{VPN_Pass}@{VPN_IP_PORT}",
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


def fetchMatchedEntries(driver, mapTileIdentifierName):
    driver.find_elements(by=By.TAG_NAME, value="a")
    entries = {}
    for a,x in enumerate(driver.find_elements(by=By.TAG_NAME, value="div")):
        for b, y in enumerate(x.find_elements(by=By.TAG_NAME, value="a")):
            try:
                if "https://www.google.com/maps/place/" in y.get_attribute("href"):
                    if x.get_attribute("role") == "article":
                        entry = {}
                        entry["href"] = y.get_attribute("href")
                        entry["label"] = y.get_attribute("aria-label")
                        entry["unit"] = y
                        entry["parent"] = x
                        entries[f"{a}_{b}"] = entry
            except:
                continue

    matched = {}
    for x in entries:
        try:
            if mapTileIdentifierName.lower() in entries[x]['label'].lower():
                matched[x] = entries[x]
        except:
            continue
    # print(matched.keys())
    return matched



def googleMapSearchModules(driver, searchKey, mapTileIdentifierName, pageMax=10):
    driver.maximize_window()
    time.sleep(randint(100, 5000) / 1000)
    driver.get(f"https://www.google.com/maps/search/{searchKey.replace(' ','+')}")
    time.sleep(randint(100, 5000) / 100)
    matched = fetchMatchedEntries(driver, mapTileIdentifierName)

    pageNum = 0
    while len(matched) == 0:
        if pageNum == pageMax:
            logger.debug(f"Result page {pageMax} reached. Halting run")
            # driver.quit()
            raise Exception("Keyword not found in Google Search data, increase pageMax or improve keyword precision")
        logger.debug(f"Starting search results page {pageNum}")

        [ActionChains(driver).send_keys(Keys.TAB).perform() for x in range(9)]

        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()

        pageNum += 1
        try: matched = {**matched, **fetchMatchedEntries(driver, mapTileIdentifierName)}
        except:
            time.sleep(5)
            matched = {**matched, **fetchMatchedEntries(driver, mapTileIdentifierName)}
    return matched


def secndryPageOps(driver, matched, mapTileIdentifierName, location="New York"):
    time.sleep(5)
    driver.execute_script("arguments[0].scrollIntoView();", matched[list(matched.keys())[0]]['parent'])
    matched[list(matched.keys())[0]]['unit'].click()
    time.sleep(randint(100, 5000) / 100)
    try:
        try: WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.TAG_NAME, "img")))
        except: pass

        try:
            logger.debug("Attempting site loading")
            # Website
            [x for x in matched[list(matched.keys())[0]]['parent'].find_elements(by=By.TAG_NAME, value="a") if
             x.get_attribute("data-value") == 'Website'][0].click()
        except:
            logger.debug(f"Attempting directions from {location}")
            # Directions from "New York"
            [x for x in matched[list(matched.keys())[0]]['parent'].find_elements(by=By.TAG_NAME, value="button") if x.get_attribute("data-value") == 'Directions'][0].click()
            ActionChains(driver).send_keys("New York")

        time.sleep(2)
    except Exception as e:
        logger.warning(f"Cant find Directions or Website entry {mapTileIdentifierName} : {e}")



def singleThread(searchKey, mapTileIdentifierName):
    logger.debug("Starting new browser proxy")
    driver = seleniumLiteTrigger()
    try:
        matched = googleMapSearchModules(driver, searchKey, mapTileIdentifierName, pageMax=10)
        if len(matched) > 0:
            time.sleep(randint(100, 5000) / 1000)
            secndryPageOps(driver, matched, mapTileIdentifierName)
            time.sleep(randint(100, 5000) / 1000)
    except Exception as e:
        logger.debug(e)
    driver.quit()


def core(searchKey, mapTileIdentifierName):
    parallelWorkerCount = 5
    confData = {
        "searchKey": searchKey,
        "mapTileIdentifierName": mapTileIdentifierName,
        "parallelWorkerCount": parallelWorkerCount
    }
    logger.debug(f"Started run with configs: {json.dumps(confData, indent=3)}")
    singleThread(searchKey, mapTileIdentifierName)
    #
    # with ThreadPoolExecutor(max_workers=parallelWorkerCount) as executor:
    #     for x in range(parallelWorkerCount):
    #         executor.submit(singleThread, searchKey, refUrl, secndaryAnchorText)
    #     executor.shutdown(wait=True)
    #
    # logger.debug(f"Completed run with configs: {json.dumps(confData, indent=3)}")
    #

if __name__ == '__main__':
    '''

    '''
