#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------
import json
import os
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
from random import randint

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By


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
            VPN_IP = configs['VPN_IP'][randint(0, len(configs['VPN_IP']) - 1)]
            VPN_Port = configs['VPN_Port']

            options = {
                'proxy': {
                    "http": f"http://{VPN_User}:{VPN_Pass}@{VPN_IP}:{VPN_Port}",
                    "https": f"https://{VPN_User}:{VPN_Pass}@{VPN_IP}:{VPN_Port}",
                    'no_proxy': 'localhost,127.0.0.1'
                }
            }

            driver = webdriver.Firefox(executable_path="driver\\geckodriver.exe", seleniumwire_options=options)

            # TODO remove
            return driver

            # driver.get("https://ifconfig.me/")
            # time.sleep(randint(50,150)/100)
            # driver.refresh()
            # if '''<a href="http://ifconfig.me">What Is My IP Address? - ifconfig.me</a>''' in driver.page_source:
            #     logger.debug(f"New Rotated IP: {driver.find_element(by=By.ID, value='ip_address').text}")
            #     return driver

            # driver.get(f"https://www.google.com")
            # driver.get(f"https://www.google.com/search?q=facebook")
            # if len(driver.find_elements(by=By.TAG_NAME, value="a")) < 5: raise Exception("Compromised IP, Rotating")
            # time.sleep(randint(50,150)/100)
        except Exception as e:
            atmpt += 1
            driver.quit()
            logger.debug("IP unavailable, rotating.")
            if atmpt == 10:
                raise e


def fetchMatchedEntries(driver, refWord, refDomain):
    entries = {a: x.get_attribute("href") for a, x in enumerate(driver.find_elements(by=By.TAG_NAME, value="a"))}

    matched = {}
    for x in entries:
        try:
            if (refWord in entries[x]) & (refDomain in entries[x]):
                # print({x: entries[x]})
                matched[x] = entries[x]
        except:
            continue
    print(matched.keys())
    return matched


def googleSearchModules(driver, searchKey, refWord, refDomain, pageMax=10):
    driver.get(f"https://www.google.com/search?q={searchKey}")
    # time.sleep(randint(50, 1500) / 100)
    matched = fetchMatchedEntries(driver, refWord, refDomain)
    pageNum = 0
    while len(matched) == 0:
        if pageNum == pageMax:
            logger.debug(f"Result page {pageMax} reached. Halting run")
            driver.quit()
            raise Exception("Keyword not found in Google Search data, increase pageMax or improve keyword precision")
        logger.debug(f"Starting search results page {pageNum}")
        driver.find_element(by=By.ID, value="pnnext").click()
        pageNum += 1
        matched = {**matched, **fetchMatchedEntries(driver, refWord, refDomain)}
    return matched


def secndryPageOps(driver, matched, secndaryAnchorText, refUrl):
    # driver.find_elements(by=By.TAG_NAME, value="a")[list(matched.keys())[0]].click()
    from selenium.webdriver import ActionChains

    # driver.find_elements(by=By.TAG_NAME, value="a")[list(matched.keys())[0]].click()
    [ActionChains(driver).send_keys(Keys.TAB).perform() for x in range([list(matched.keys())[0]])]
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    # Anchor Text to click: teen depression treatment
    try:
        [x for x in driver.find_elements(by=By.TAG_NAME, value="a") if secndaryAnchorText in x.text][0].click()
    except:
        logger.warning(f"Cant find 2nd anchor text {secndaryAnchorText} in {refUrl}")


def tertryPageOps(driver, atmpt=0):
    # Click on any random url after
    tertryUrlList = driver.find_elements(by=By.TAG_NAME, value="a")
    while atmpt < 5:
        try:
            tertryUrlList[randint(0, len(tertryUrlList))].click()
            time.sleep(10)
            driver.quit()
        except:
            atmpt += 1
            time.sleep(2)
            if atmpt == 4:
                logger.debug("Cant find clickable tertiary urls")
                driver.quit()
            continue


def singleThread(searchKey, refUrl, secndaryAnchorText):
    logger.debug("Starting new browser proxy")
    driver = seleniumLiteTrigger()
    try:
        # Click on this URL: https://urbanmatter.com/why-is-the-rate-of-teenage-depression-increasing-after-the-pandemic/
        refWord = refUrl.strip("/").split("/")[-1]
        refDomain = re.findall(f'https?:\/\/([^\/]+)\/', refUrl)[0]

        matched = googleSearchModules(driver, searchKey, refWord, refDomain, pageMax=10)
        if len(matched) > 0:
            secndryPageOps(driver, matched, secndaryAnchorText, refUrl)
            tertryPageOps(driver)
    except Exception as e:
        logger.debug(e)
    driver.quit()


def core(searchKey, refUrl, secndaryAnchorText):
    parallelWorkerCount = 3
    confData = {
        "searchKey": searchKey,
        "refUrl": refUrl,
        "secndaryAnchorText": secndaryAnchorText,
        "parallelWorkerCount": parallelWorkerCount
    }
    logger.debug(f"Started run with configs: {json.dumps(confData, indent=3)}")
    singleThread(searchKey, refUrl, secndaryAnchorText)

    # with ThreadPoolExecutor(max_workers=parallelWorkerCount) as executor:
    #     for x in range(parallelWorkerCount):
    #         executor.submit(singleThread, searchKey, refUrl, secndaryAnchorText)
    #     executor.shutdown(wait=True)

    # logger.debug(f"Completed run with configs: {json.dumps(confData, indent=3)}")


if __name__ == '__main__':
    '''

    '''
