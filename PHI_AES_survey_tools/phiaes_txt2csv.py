# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
# coding: utf-8
#
#__author__ = "nagao"
#__date__ = "$2017/03/09 17:18:43$"

from __future__ import print_function
from __future__ import unicode_literals
import argparse
import csv
import itertools
import io
import os.path

parser = argparse.ArgumentParser()
parser.add_argument("file_path")
parser.add_argument("--encoding", default="utf_8")
options = parser.parse_args()
readfile = options.file_path
encoding_option = options.encoding
#readfile = 'SNP159.113.txt'
name, ext = os.path.splitext(readfile)
flag = 0
count = 0
column = 0
area_comment = []
atomName_array = []
allData = []
header = []
maxlen = 0
arr = []
description = 'No title'
description_line = 0
templine = 0
acqdate = ''
filetype = ''
element = ['#legend']
collection_time = ['#acq_time']
xoption = 0

with open(readfile, 'r', encoding=encoding_option) as f:
    for line in f:
        line = line.strip()
        if flag == 0:
            if line.find('Area Comment,RegionNo,AtomicName,Area No,XLabel,YLabel,DataCount') > -1:
                templine  = 1
                flag = 1
                count = 1
                arr = []
                dimension = 2
                description_line = 1
            else:
                if line.find('AcqFileDate') > -1:
                    value = line.split(':')
                    date = value[-1].split()
                    mm = date[1].zfill(2)
                    dd = date[2].zfill(2)
                    acqdate = date[0] + mm + dd
                if line.find('SpectralRegDef:') > -1:
                    value = line.split(':')
                    spectral_reg = value[-1].split()
                    if spectral_reg[2] == 'Su1s':
                        spectral_reg[2] = 'Survey'
                    element.append(spectral_reg[2])
                    collection_time.append(float(spectral_reg[10]))
                if line.find('FileType') > -1:
                    value = line.split(':')
                    filetype = value[-1].strip()
                    print(filetype)
                if line.find('AcqFilename') > -1:
                    value = line.split(':')
                    temp = value[-1].split("\\")
                    description = temp[-1]
        else:
            if line == '' and description_line != 1:
                flag = 0
                allData.insert(column, arr)
                column += 1
                description_line = 0
                templine += 1
            else:
                templine += 1
                line = line.rstrip()
                temp = []
                if column == 0 and count == 1:
                    meta = ['#title', description]
                    header.append(meta)
                    meta = ['#dimension', 'x', 'y']
                    header.append(meta)
                elif count == 5 and column == 0:
                    itemList = line.split(',')
                    for i, j in enumerate(itemList):
                        temp.insert(i, j)
                    xlabel = itemList[0].split('(')
                    xlabelname = xlabel[0]
                    xlabelunit = xlabel[1].replace(')', '')
                    if len(itemList) > 1:
                        xoption = itemList[1]
                    xlabelList = itemList
                elif count == 6 and column == 0:
                    itemList = line.split(',')
                    for i, j in enumerate(itemList):
                        temp.insert(i, j)
                    ylabel = itemList[0].split('(')
                    ylabelname = ylabel[0]
                    ylabelunit = ylabel[1].replace(')', '')
                    if (ylabelunit == 'c/s'):
                        ylabelunit = 'cps'
                    if len(xlabelList) > 1:
                        if xoption == 0:
                            meta = ['#x', xlabelname, xlabelunit]
                        else:
                            meta = ['#x', xlabelname, xlabelunit, xoption]
                    else:
                        meta = ['#x', xlabelname, xlabelunit]
                    header.append(meta)
                    meta = ['#y', ylabelname, ylabelunit]
                    header.append(meta)
                    meta = element
                    header.append(meta)
                    meta = ['##acq_date', acqdate]
                    header.append(meta)
                    meta = ['##comment', filetype]
                    header.append(meta)
                elif 7 < count:
                    if ',' in line:
                        itemList = line.split(',')
                    else:
                        itemList = line.split('\t')
                    for i, j in enumerate(itemList):
                        temp.insert(i, j)
                    arr.insert(count-8, temp)
                    if maxlen < count-7:
                        maxlen = count-7
                count += 1
                description_line += 1

allData.insert(column, arr)
elements = element[:]
elements.pop(0)
atomName_array = []
for col in elements:
    atomName_array.append(col + '_x')
    atomName_array.append(col)

header.append('')
lst = [[[''] * 2 for i in range(maxlen)] for j in range(column+1)]
for i, j in enumerate(allData):
    lst[i][0:len(j)] = j
list2 = list(map(list, zip(*lst)))
for i, j in enumerate(list2):
    temp = list2[i]
    csvout = [x for l in temp for x in l]
writefile = name + '.csv'
with open(writefile, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(header)
    for i, j in enumerate(list2):
        temp = list2[i]
        csvout = [x for l in temp for x in l]
        writer.writerow(csvout)
