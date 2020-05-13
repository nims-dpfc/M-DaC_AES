#-------------------------------------------------
# jampcsv2graph.py
#
# Copyright (c) 2020, Data PlatForm Center, NIMS
#
# This software is released under the MIT License.
#-------------------------------------------------
# coding: utf-8
#__author__ = "nagao"

"""jampcsv2graph.py

This module creates a image data
by creating a csv file of the JAMP series
by JEOL.

Copyright (c) 2020, Data PlatForm Center, NIMS
This software is released under the MIT License.

Example
-------

    Parameters
    ----------
    inputfile : JEOL csv file
        Measurement data file measured by JAMP

    $ python jampcsv2graph.py [inputfile]

"""

__package__ = "M-DaC_AES/PHI_JEOL_AES_tools"
__version__ = "1.0.0"

import argparse
import pandas as pd
import os.path
import codecs
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import ScalarFormatter
import unicodedata

def plotlygraph(title, data, fig, xaxis, yaxis):
    x_axis = 'false'
    y_axis = 'false'
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

def is_japanese(string):
    for ch in string:
        name = unicodedata.name(ch)
        if "CJK UNIFIED" in name or "HIRAGANA" in name or "KATAKANA" in name:
            return(True)
    return(False)

def graphSetting(xaxis, yaxis, colname, title):
    fig = plt.figure()
    fig, ax = plt.subplots()
    plt.rcParams['font.size'] = 12
    formatter = ScalarFormatter(useMathText=True)
    ax.yaxis.set_major_formatter(formatter)
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.ticklabel_format(style="sci",  axis="y",scilimits=(0,0))
    plt.grid(True)
    plt.subplots_adjust(left=0.155, bottom=0.155, right=0.95, top=0.9, wspace=None, hspace=None)

    if is_japanese(title) == True:
        length = 17
        if len(title) > length:
            title = title[:length] + '...'
        plt.title(title, fontproperties=fp)
    else:
        length = 35
        if len(title) > length:
            title = title[:length] + '...'
        plt.title(title)

def makegraph(df, xaxis, yaxis, col, title):
    graphSetting(xaxis, yaxis, col, title)
    df = df.astype("float64")
    plt.plot(df[0].values, df[1].values, label=col, lw=1)
    plt.legend()
    writefile = name + '_' + col + '.png'
    plt.savefig(writefile)

if __name__ == "__main__":
    fp = FontProperties(fname=r'C:\WINDOWS\Fonts\meiryo.ttc', size=14)

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="input file")
    parser.add_argument("--encoding", default="utf_8")
    parser.add_argument("--jupytermode", help="for jupyter mode", action="store_true")
    options = parser.parse_args()
    readfile = options.file_path
    jupytermode = options.jupytermode
    encoding_option = options.encoding
    basename = os.path.basename(readfile)
    dirname = os.path.dirname(readfile)
    name, ext = os.path.splitext(basename)
    jupytermode = options.jupytermode

    if jupytermode == True:
        from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
        import plotly.graph_objs as go
        init_notebook_mode(connected=True)

    xaxis = "Kinetic energy" + " (eV)"
    yaxis = "Intensity" + " (counts/dwell time)"
    data_jupyter = []

    with codecs.open(readfile, 'r', encoding_option, 'ignore') as f:
        lines = f.read()

        blocks = lines.split("\r\n\r\n")
        for i, block in enumerate(blocks):
            data = [line.split(",") for line in block.splitlines()]
            if i == 0:
                data.pop(0)
            df = pd.DataFrame(data)
            colname = 'block' + str(i)
            title = name + '_' + colname
            makegraph(df, xaxis, yaxis, colname, title)

        fig = plt.figure()
        graphSetting(xaxis, yaxis, colname, name)
        for i, block in enumerate(blocks):
            data = [line.split(",") for line in block.splitlines()]
            if i == 0:
                data.pop(0)
            df = pd.DataFrame(data)
            df = df.astype("float64")
            colname = 'block' + str(i)
            plt.plot(df[0].values, df[1].values, label=colname, lw=1)
            if jupytermode == True:
                trace = dict(
                    name = colname,
                    x = df[0].values, y = df[1].values,
                    type = "lines",
                    mode = 'lines')
                data_jupyter.append(trace)

        plt.legend()
        writefile = name + '.png'
        plt.savefig(writefile)
    plt.close('all')
    if jupytermode == True:
        plotlygraph(name, data_jupyter, fig, xaxis, yaxis)
