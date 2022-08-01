#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------
from mapBot import core

searchKey = 'teen iop los angeles'
mapTileIdentifierName = 'Key Transitions Teen Treatment Program'
trafficCount = 500
parallelWorkerCount = 5

core(searchKey, mapTileIdentifierName, trafficCount, parallelWorkerCount)


