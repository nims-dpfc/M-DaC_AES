# -------------------------------------------------
# txttorawXML_for_AES.py
#
# Copyright (c) 2018, Data PlatForm Center, NIMS
#
# This software is released under the MIT License.
# -------------------------------------------------
# coding: utf-8
"""txttorawXML_for_AES.py

This module extracts primary parameter from
JEOL para file.

Copyright (c) 2018, Data PlatForm Center, NIMS
This software is released under the MIT License.

Example
-------

    Parameters
    ----------
    inputfile : JEOL para file
    templatefile : template file for JEOL para file
    outputfile : output file

    $ python txttorawXML_for_AES.py [inputfile] [templatefile] [outputfile]

"""
import argparse
import os.path
import csv
import pandas as pd
from dateutil.parser import parse
import xml.dom.minidom
import re
import xml.etree.ElementTree as ET
import codecs


count = 0
wvalue = []
item_key = []
item_value = []
column_num = 0
item_column = []
cnumber = None
dtype = None

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("file_path")
  parser.add_argument("template_file")
  parser.add_argument("out_file")
  parser.add_argument("--stdout", action="store_true")
  options = parser.parse_args()
  readfile = options.file_path
  templatefile = options.template_file
  outputfile = options.out_file
  print_option = options.stdout

  template = ET.parse(templatefile)
  columns = []  
  metas = template.findall('meta')
  for meta in metas:
    columns.append(meta.attrib["key"])

  dom = xml.dom.minidom.Document()
  metadata = dom.createElement('metadata')
  dom.appendChild(metadata)

  with open(readfile, "r", encoding="utf8") as f:
    for line in f:
        line = line.strip()
        if line == "":
            break
        else:
            if line.find("$AP_END_COMMENT") != -1:
                key = "AP_COMMENT"
                value = line[:-15]
            elif line.find("$AP_END_OPERATOR") != -1:
                key = "AP_OPERATOR"
                value = line[:-16]
            else:
                lines = line.split("  ")
                lines = [item.strip() for item in lines]
                key = lines[0]
                if key[0] == "$":
                    key = key[1:]
                if len(lines) == 1:
                    value = ""
                    if  key[0] == "#" or key == "AP_COMMENT" or key == "AP_OPERATOR":
                        key = None
                else:
                    value = lines[1]

                if key != None:
                    if key == "AP_DATATYPE":
                        if value == "3":
                            dtype = "wide"
                        elif value == "4":
                            dtype = "narrow"
                        else:
                            dtype = None
                    if key == "AP_SPC_ROI_NOFEXE":
                        if dtype == "narrow":
                           cnumber = value
                        else:
                           key = None
                    if key == "AP_SPOSN_EXEMOD":
                        count += 1
                    elif key == "AP_SPC_CEMSTAT":
                        key = None
                        wkey = "AP_SPC_CEMSTAT"
                        values = value.split(" ")
                        wcolumn_num = 0
                        wvalue.append(values[1])
                    elif key == "AP_SPC_ROI_EXEMOD":
                        if dtype == "narrow":
                           column_num = value[0]
                        else:
                           key = None
                    elif key == "AP_SPC_ROI_NAME":
                        if dtype == "narrow":
                           column_num = value[0]
                        else:
                          key = None
                    elif key == "AP_SPC_ROI_START":
                        if dtype == "narrow":
                           column_num = value[0]
                        else:
                           key = None
                    elif key == "AP_SPC_ROI_STOP":
                        if dtype == "narrow":
                           column_num = value[0]
                        else:
                           key = None
                    elif key == "AP_SPC_ROI_STEP":
                        if dtype == "narrow":
                           column_num = value[0]
                        else:
                           key = None
                    elif key == "AP_SPC_ROI_DWELL":
                        if dtype == "narrow":
                           column_num = value[0]
                        else:
                           key = None
                    elif key == "AP_SPC_ROI_SWEEPS":
                        if dtype == "narrow":
                           column_num = value[0]
                        else:
                           key = None
                    else:
                        if wvalue:
                            wvalues = " ".join(wvalue)
                            item_key.append(wkey)
                            item_value.append(wvalues)
                            item_column.append(wcolumn_num)
                            wkey = None
                            wvalue = []
        if key != None:
            item_key.append(key)
            item_value.append(value)
            item_column.append(column_num)
        column_num = 0

    subnode = dom.createElement('column_name')
    subnode.appendChild(dom.createTextNode('condition'))
    metadata.appendChild(subnode)
    subnode = dom.createElement('column_num')
    subnode.appendChild(dom.createTextNode(str(cnumber)))
    metadata.appendChild(subnode)

    for skey in columns:
        for i in range(len(item_key)):
            if skey == item_key[i]:
                subnode = dom.createElement('meta')
                subnode.appendChild(dom.createTextNode(item_value[i]))
                subnode_attr = dom.createAttribute('key')
                subnode_attr.value = item_key[i]
                subnode.setAttributeNode(subnode_attr)
                metadata.appendChild(subnode)
                subnode_attr = dom.createAttribute('type')
                subnode_attr.value = 'String'
                subnode.setAttributeNode(subnode_attr)
                metadata.appendChild(subnode)
                if item_column[i] == None or item_column[i] == " ":
                    column_num = 0
                else:
                    column_num = int(item_column[i])
                if column_num > 0:
                    subnode_attr = dom.createAttribute('column')
                    subnode_attr.value = str(column_num)
                    subnode.setAttributeNode(subnode_attr)
                    metadata.appendChild(subnode)

  if print_option:
    print(dom.toprettyxml())
  file = codecs.open(outputfile, 'wb', encoding='utf-8')

  dom.writexml(file, '', '\t', '\n', encoding='utf-8')

  file.close()
  dom.unlink()

