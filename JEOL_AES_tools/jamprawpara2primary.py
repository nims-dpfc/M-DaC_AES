# -------------------------------------------------
# jamprawpara2primary.py
#
# Copyright (c) 2018, Data PlatForm Center, NIMS
#
# This software is released under the MIT License.
# -------------------------------------------------
# coding: utf-8
#__author__ = "nagao"

"""jamprawpara2primary.py

This module extracts primary parameter from
JEOL para file.

Copyright (c) 2018, Data PlatForm Center, NIMS
This software is released under the MIT License.

Example
-------

    Parameters
    ----------
    inputfile : JEOL JAMP AES raw parameter file (XML)
    templatefile : template file for JEOL JAMP AES primary parameter data
    outputfile : output file (primary parameter file (XML))

    $ python jamprawpara2primary.py [inputfile] [templatefile] [outputfile]

"""
import argparse
import os.path
import csv
import pandas as pd
from dateutil.parser import parse
import xml.dom.minidom
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import codecs

def registdf(key, channel, value, metadata, unitlist, template):
    column = key
    value_unit = ""
    tempflag = 1
    if column not in columns:
        tempflag = 0
    if tempflag == 1:
        if value is not None:
            arrayvalue = value.split()
            unitcolumn = template.find('meta[@key="{value}"][@unit]'.format(value=key))
            transition = 0
            datatype = rawdata.find('meta[@key="AP_DATATYPE"]').text
            analyser_mode = rawdata.find('meta[@key="AP_SPC_ANAMOD"]').text
            if unitcolumn is not None:
                value_unit = unitcolumn.get("unit")
                if key == "Probe_current":
                    value = arrayvalue[0] + 'x10^' + arrayvalue[1]
                elif key == "Analysis_chamber_pressure_when_measurement_finished":
                    value = arrayvalue[0] + 'x10^(-' + arrayvalue[1] + ')'
                elif key == "Probe_diameter":
                    value = arrayvalue[1]
                elif key == "Analyser_pass_energy":
                    if analyser_mode != "1":
                        value = ""
                elif key == "Abscissa_start" or key == "Abscissa_end" or key == "Abscissa_increment" or key == "Collection_time":
                    if datatype == "4":
                        value = arrayvalue[1]
            else:
                if key == "Year" or key == "Month" or key == "Day" or key == "Hours" or key == "Minutes" or key == "Seconds":
                    dt = datetime.strptime(value, '%Y%m%d%H%M%S')
                    if key == "Year":
                        value = dt.year
                    elif key == "Month":
                        value = "{0:02d}".format(dt.month)
                    elif key == "Day":
                        value = "{0:02d}".format(dt.day)
                    elif key == "Hours":
                        value = "{0:02d}".format(dt.hour)
                    elif key == "Minutes":
                        value = "{0:02d}".format(dt.minute)
                    else:
                        value = "{0:02d}".format(dt.second)
                elif key == "Analyser_mode":
                    if value == "1":
                        value = "CAE"
                    elif value == "2" or value == "3" or value == "4" or value == "5":
                        value = "CRR"
                    else:
                        value = "unknown"
                elif key == "Upper_left_x_coordinate" or key == "Upper_left_y_coordinate" or key == "Lower_right_x_coordinate" or key == "Lower_right_y_coordinate":
                    value = arrayvalue[1]
                elif key == "Species_label_Transitions":
                    if datatype == "4":
                        value = arrayvalue[1]
                elif key == "Number_of_scans":
                    if datatype == "4":
                        value = arrayvalue[1]
                elif key == "Probe_scan_mode":
                    if arrayvalue[1] == "1":
                        value = "Spot"
                    elif arrayvalue[1] == "2":
                        value = "Scan"
                    elif arrayvalue[1] == "3":
                        value = "limited scan"
                    else:
                        value = "unknown"
                elif key == "Data_type":
                    if value == "1":
                        value = "SEM image"
                    elif value == "3":
                        value = "Wide"
                    elif value == "4":
                        value = "Narrow"
                    elif value == "5":
                        value = "Depth"
                    elif value == "7":
                        value = "Line"
                    elif value == "8":
                        value = "Auger image"
                    else:
                        value = "unknown"
                elif key == "Neutralization_active_mode":
                    if value == "1":
                        value = "inactive"
                    elif value == "2":
                        value = "active"
                    else:
                        value = "unknown"

            subnode = dom.createElement('meta')
            subnode.appendChild(dom.createTextNode(str(value)))
            subnode_attr = dom.createAttribute('key')
            subnode_attr.value = column
            subnode.setAttributeNode(subnode_attr)
            metadata.appendChild(subnode)
            if len(value_unit) > 0:
                subnode_attr = dom.createAttribute('unit')
                subnode_attr.value = value_unit
                subnode.setAttributeNode(subnode_attr)
                metadata.appendChild(subnode)
                unitlist.append(key)

            subnode_attr = dom.createAttribute('type')
            typename = template.find('meta[@key="{value}"]'.format(value=key))
            if typename.get("type") is not None:
                subnode_attr.value = typename.get("type")
            else:
                subnode_attr.value = "String"
            subnode.setAttributeNode(subnode_attr)
            metadata.appendChild(subnode)

            if channel != 0:
                subnode_attr = dom.createAttribute('column')
                subnode_attr.value = channel
                subnode.setAttributeNode(subnode_attr)
                metadata.appendChild(subnode)

            if transition == 1:
                subnode = dom.createElement('meta')
                subnode.appendChild(dom.createTextNode(str(value2)))
                subnode_attr = dom.createAttribute('key')
                subnode_attr.value = "Transitions"
                subnode.setAttributeNode(subnode_attr)
                metadata.appendChild(subnode)

                subnode_attr = dom.createAttribute('type')
                typename = template.find('meta[@key="Transitions"]')
                if typename.get("type") is not None:
                    subnode_attr.value = typename.get("type")
                else:
                    subnode_attr.value = "String"
                subnode.setAttributeNode(subnode_attr)
                metadata.appendChild(subnode)

                if channel != 0:
                    subnode_attr = dom.createAttribute('column')
                    subnode_attr.value = channel
                    subnode.setAttributeNode(subnode_attr)
                    metadata.appendChild(subnode)

                transition = 0

        return metadata


def regist(column, key, rawdata, metadata, channel, value, unitlist, template):
    if column in rawcolumns:
        registdf(key, channel, value, metadata, unitlist, template)
    return metadata


def conv(column, temp_name, rawdata, metadata, channel, unitlist, template):
    if channel == 0:
        metadata = regist(column, temp_name, rawdata, metadata, 0, rawdata.find('meta[@key="{value}"]'.format(value=column)).text, unitlist, template)
    else:
        for node in rawdata.findall('meta[@key="{value}"]'.format(value=column)):
            columnnum = node.attrib.get('column')
            metadata = regist(column, temp_name, rawdata, metadata, columnnum, node.text, unitlist, template)
    return(metadata)


if __name__ == "__main__":
  sorn = None
  column_num = None
  t_value = None
  w_list = []
  a_type = None
  ap_pe = 0
  a_mode = 0
  scount = 0
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
  channel = 0
  rawdata = ET.parse(readfile)
  rawcolumns=[]
  rawmetas = rawdata.findall('meta')
  for meta in rawmetas:
    rawcolumns.append(meta.attrib["key"])
  rawcolumns = list(set(rawcolumns))
  template = ET.parse(templatefile)
  columns=[]
  metas = template.findall('meta')
  for meta in metas:
    columns.append(meta.attrib["key"])
  dom = xml.dom.minidom.Document()
  metadata = dom.createElement('metadata')
  dom.appendChild(metadata)
  count = 0;

  metalist = {
            "Operator_identifier":"AP_OPERATOR",
            "Year":"AP_ACQDATE",
            "Month":"AP_ACQDATE",
            "Day":"AP_ACQDATE",
            "Hours":"AP_ACQDATE",
            "Minutes":"AP_ACQDATE",
            "Seconds":"AP_ACQDATE",
            "Probe_energy":"AP_PENERGY",
            "Probe_current":"AP_PCURRENT",
            "Analyser_mode":"AP_SPC_ANAMOD",
            "Analyser_pass_energy":"AP_SPC_ES",
            "Abscissa_start_w":"AP_SPC_WSTART",
            "Abscissa_end_w":"AP_SPC_WSTOP",
            "Abscissa_increment_w":"AP_SPC_WSTEP",
            "Collection_time_w":"AP_SPC_WDWELL",
            "Number_of_scans_w":"AP_SPC_WSWEEPS",
            "Species_label_Transitions":"AP_SPC_ROI_NAME",
            "Abscissa_start":"AP_SPC_ROI_START",
            "Abscissa_end":"AP_SPC_ROI_STOP",
            "Abscissa_increment":"AP_SPC_ROI_STEP",
            "Collection_time":"AP_SPC_ROI_DWELL",
            "Number_of_scans":"AP_SPC_ROI_SWEEPS",
            "Analysis_chamber_pressure_when_measurement_finished":"AP_CHAMBER_PRESS",
            "Probe_scan_mode":"AP_SPOSN_BSMOD",
            "Probe_diameter":"AP_SPOSN_PDIA",
            "Upper_left_x_coordinate":"AP_SPOSN_BEAM_P1X",
            "Upper_left_y_coordinate":"AP_SPOSN_BEAM_P1Y",
            "Lower_right_x_coordinate":"AP_SPOSN_BEAM_P2X",
            "Lower_right_y_coordinate":"AP_SPOSN_BEAM_P2Y",
            "Probe_polar_angle_to_sample_normal":"AP_STGTILT",
            "Comment":"AP_COMMENT",
            "Neutralization_active_mode":"AP_IGN_NEUT_MODE",
            "Data_type":"AP_DATATYPE",
            "Analysis_chamber_pressure_when_measurement_finished":"AP_CHAMBER_PRESS"
            }
  columns_unique = list(dict.fromkeys(columns))
  unitlist=[]
  maxcolumn = 0
  datatype = rawdata.find('meta[@key="AP_DATATYPE"]').text
  for k in columns_unique:
    if k in metalist:
        v = metalist[k]
        if datatype == "3":
            if k == "Abscissa_start":
                v = "AP_SPC_WSTART"
            elif k == "Abscissa_end":
                v = "AP_SPC_WSTOP"
            elif k == "Abscissa_increment":
                v = "AP_SPC_WSTEP"
            elif k == "Collection_time":
                v = "AP_SPC_WDWELL"
            elif k == "Number_of_scans":
                v = "AP_SPC_WSWEEPS"
        tempcolumn = len(rawdata.findall('meta[@key="{value}"]'.format(value=v)))-1
        if maxcolumn < tempcolumn + 1:
            maxcolumn = tempcolumn + 1
        metadata = conv(v, k, rawdata, metadata, len(rawdata.findall('meta[@key="{value}"]'.format(value=v)))-1, unitlist, template)

  subnode = dom.createElement('column_num')
  subnode.appendChild(dom.createTextNode(str(maxcolumn)))
  metadata.appendChild(subnode)
  column_name = template.find('column_name').text
  subnode = dom.createElement('column_name')
  subnode.appendChild(dom.createTextNode(column_name))
  metadata.appendChild(subnode)
  if print_option:
    print(dom.toprettyxml())
  file = codecs.open(outputfile, 'wb', encoding='utf-8')

  dom.writexml(file, '', '\t', '\n', encoding='utf-8')

  file.close()
  dom.unlink()
