#-------------------------------------------------
# phiaes_csv2graph.py
#
# Copyright (c) 2020, Data PlatForm Center, NIMS
#
# This software is released under the MIT License.
#-------------------------------------------------
# coding: utf-8
#__author__ = "nagao"

"""phiaes_csv2graph.py

This module creates a image data
by creating a csv file of the PHI-AES data.

Copyright (c) 2018, Data PlatForm Center, NIMS
This software is released under the MIT License.

Example
-------

    Parameters
    ----------
    inputfile : PHI AES csv data file

    $ python phiaes_csv2graph.py [inputfile]

"""

__author__ = "nagao"
__date__ = "$2017/03/21 11:16:02$"

import argparse
import os.path
import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import ScalarFormatter
import codecs
import unicodedata

def getKey(key, row):
    if row[0] == key:
        return row[1]
    else:
        return 0

def plotlygraph(xrevFlag, yrevFlag, title, data, fig):
    x_axis = 'false'
    y_axis = 'false'
    if xrevFlag:
        x_axis = 'reversed'
    if yrevFlag:
        y_axis = 'reversed'

    layout = dict(
        width=800,
        height=700,
        autosize=False,
        title=title,
        xaxis=dict(title=xaxis, autorange=x_axis),
        yaxis=dict(title=yaxis, autorange=y_axis),
        showlegend=True
    )

    fig = dict(data=data, layout=layout)
    iplot(fig, show_link=False, filename=title, validate=False, config={"displaylogo":False, "modeBarButtonsToRemove":["sendDataToCloud"]})

def is_japanese(titlestring):
    for ch in string:
        name = unicodedata.name(ch)
        if "CJK UNIFIED" in name or "HIRAGANA" in name or "KATAKANA" in name:
            return(True)
    return(False)

fp = FontProperties(fname=r'C:\WINDOWS\Fonts\meiryo.ttc', size=14)

parser = argparse.ArgumentParser()
parser.add_argument("file_path")
parser.add_argument("--encoding", default="utf_8")
parser.add_argument("--jupytermode", help="for jupyter mode", action="store_true")
parser.add_argument("--scale", nargs=2, type=float)
parser.add_argument("--unit", nargs=2)
parser.add_argument("--scalename", nargs=2)
parser.add_argument("--xrange", choices=['reverse'])
parser.add_argument("--yrange", choices=['reverse'])
options = parser.parse_args()
readfile = options.file_path
jupytermode = options.jupytermode
scale_option = options.scale
unit_option = options.unit
scalename_option = options.scalename
xrange_option = options.xrange
yrange_option = options.yrange
name, ext = os.path.splitext(readfile)
axis = []

if jupytermode == True:
    from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
    import plotly.graph_objs as go
    init_notebook_mode(connected=True)

with open(readfile, 'r') as f:
    reader = csv.reader(f)
    line = 1
    if xrange_option == 'reverse':
        xrevFlag = True
    else:
        xrevFlag = False
    if yrange_option == 'reverse':
        yrevFlag = True
    else:
        yrevFlag = False
    for row in reader:
        if len(row) != 0:
            line += 1
            key = getKey('#title', row)
            if (key != 0):
                title = key
            key = getKey('#dimension', row)
            if (key != 0):
                axis = row[:]
                axis.pop(0)
                dimension = len(axis)
            key = getKey('#dim_axis', row)
            if (key != 0):
                dim_option = row[:]
                dim_option.pop(0)
            if len(axis) > 0:
                key = getKey('#'+axis[0], row)
                if key != 0:
                    xaxis = row[1]
                    xunit = ''
                    if len(row) > 2:
                        xunit = "(" + row[2] + ")"
                    if isinstance(unit_option, list):
                        xunit = "(" + unit_option[0] + ")"
                    if isinstance(scalename_option, list):
                        xaxis = scalename_option[0]
                    xaxis = xaxis + xunit
                    if len(row) > 3:
                        if row[3] == 'reverse':
                            xrevFlag = True
                key = getKey('#'+axis[1], row)
                if key != 0:
                    yaxis = row[1]
                    yunit = ''
                    if len(row) > 2:
                        yunit = "(" + row[2] + ")"
                    if isinstance(unit_option, list):
                        yunit = "(" + unit_option[1] + ")"
                    if isinstance(scalename_option, list):
                        yaxis = scalename_option[1]
                    yaxis = yaxis + " " + yunit
                    if len(row) > 3:
                        if row[3] == 'reverse':
                            yrevFlag = True
            key = getKey('#legend', row)
            if (key != 0):
                row.pop(0)
                legends = row[:]
        else:
            break

df = pd.read_csv(readfile, skiprows=line, header=None)
num_columns = len(df.columns)

if (len(legends) * len(axis) == num_columns):
    num = 0
    column = [];
    for col in legends:
        for i in range(len(axis)-1):
            column.append(col + '_' + str(i))
        column.append(col)
        num += len(axis)

df.columns=column
plt.rcParams['font.size'] = 12
fig, ax = plt.subplots()
formatter = ScalarFormatter(useMathText=True)
ax.yaxis.set_major_formatter(formatter)
if xrevFlag:
    plt.gca().invert_xaxis()
if yrevFlag:
    plt.gca().invert_yaxis()
plt.xlabel(xaxis)
plt.ylabel(yaxis)
plt.ticklabel_format(style="sci",  axis="y",scilimits=(0,0))
plt.grid(True)
plt.subplots_adjust(left=0.155, bottom=0.155, right=0.95, top=0.9, wspace=None, hspace=None)


num = 1
data =[]
for col in df.columns:
    if num % dimension != 0:
        if isinstance(scale_option, list):
            x=df[col] * scale_option[0]
        else:
            x=df[col]
    else:
        if isinstance(scale_option, list):
            y=df[col] * scale_option[1]
        else:
            y=df[col]
        plt.plot(x,y,lw=1)
        if jupytermode == True:
            trace = dict(
                name = col,
                x = x, y = y,
                type = "lines",
                mode = 'lines')
            data.append( trace )
    num += 1
length = 35
if len(title) > length:
    string = title[:length] + '...'
else:
    string = title

if is_japanese(string) == True:
    plt.title(string, fontproperties=fp)
else:
    plt.title(string)

plt.rcParams['font.family'] ='sans-serif'
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['xtick.major.width'] = 1.0
plt.rcParams['ytick.major.width'] = 1.0

plt.rcParams['axes.linewidth'] = 1.0

plt.legend()
writefile = name + '.png'
plt.savefig(writefile)
plt.close()

if len(legends) > 1:
    num = 1
    for col in df.columns:
        if num % dimension != 0:
            x=df[col]
        else:
            y=df[col]
            plt.rcParams['font.size'] = 12
            fig, ax = plt.subplots()
            formatter = ScalarFormatter(useMathText=True)
            ax.yaxis.set_major_formatter(formatter)
            if xrevFlag:
                plt.gca().invert_xaxis()
            if yrevFlag:
                plt.gca().invert_yaxis()
            plt.xlabel(xaxis)
            plt.ylabel(yaxis)
            plt.ticklabel_format(style="sci",  axis="y",scilimits=(0,0))
            plt.grid(True)
            plt.subplots_adjust(left=0.155, bottom=0.155, right=0.95, top=0.9, wspace=None, hspace=None)
            plt.plot(x,y,lw=1,label=col)
            if is_japanese(title) == True:
                plt.title(title + '_' + col, fontproperties=fp)
            else:
                plt.title(title + '_' + col)
            plt.rcParams['font.family'] ='sans-serif'
            plt.rcParams['xtick.direction'] = 'in'
            plt.rcParams['ytick.direction'] = 'in'
            plt.rcParams['xtick.major.width'] = 1.0
            plt.rcParams['ytick.major.width'] = 1.0
            plt.rcParams['axes.linewidth'] = 1.0
            plt.legend()
            writefile = name + '_' + col + '.png'
            plt.savefig(writefile)
            plt.close()
        num += 1

if jupytermode == True:
    plotlygraph(xrevFlag, yrevFlag, title, data, fig)
