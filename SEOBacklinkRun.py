#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------
from SEOBacklinkBot import core

searchKey = 'teen depression rates urbanmatter'
refUrl = "https://urbanmatter.com/why-is-the-rate-of-teenage-depression-increasing-after-the-pandemic/"
secndaryAnchorText = 'teen depression treatment'
trafficCount = 500
parallelWorkerCount = 5

core(searchKey, refUrl, secndaryAnchorText, trafficCount, parallelWorkerCount)


