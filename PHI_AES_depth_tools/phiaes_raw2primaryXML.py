# -------------------------------------------------
# phiaes_raw2primaryXML.py
#
# Copyright (c) 2018, Data PlatForm Center, NIMS
#
# This software is released under the MIT License.
# -------------------------------------------------
# coding: utf-8
"""rawtoprimaryXML_for_PHI_AES.py

This module extracts primary parameter from
PHI AES raw file.

Copyright (c) 2018, Data PlatForm Center, NIMS
This software is released under the MIT License.

Example
-------

    Parameters
    ----------
    inputfile : PHI AES raw file
    templatefile : template file for PHI AES primary Data
    outputfile : output file

    $ python txttorawXML_for_PHI_AES.py [inputfile] [templatefile] [outputfile]

"""
import argparse
import xml.dom.minidom
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import codecs
from dateutil.parser import parse


def checkDate(value):
    try:
        datetime.strptime(value, '%Y %m %d')
        return True
    except ValueError:
        return False

def registdf(key, channel, value, metadata, unitlist, template):
    column = key
    value_unit = ""
    tempflag = 1
    if column not in columns:
        tempflag = 0
    if tempflag == 1:
        if value is not None:
            unitcolumn = template.find('meta[@key="{value}"][@unit]'.format(value=key))
            transition = 0
            arrayvalue = value.split()
            if unitcolumn is not None:
                if len(arrayvalue) > 1:
                    value_unit = arrayvalue[1]
                else:
                    value_unit = unitcolumn.get("unit")
                value = arrayvalue[0]
                if key == "Source_analyser_angle_for_AES":
                    value_unit = "deg"
                elif key == "NeutralizerEnergy":
                    value_unit = "eV"
                elif key == "Sputtering_Raster_Area":
                    value_unit = arrayvalue[2]
                    value = arrayvalue[0] + 'x' + arrayvalue[1]
                elif key == "SemFieldOfView":
                    value_unit = "um"
                elif key == "Abscissa_increment":
                    value = arrayvalue[5]
                    value_unit = "eV"
                elif key == "Abscissa_start":
                    value = arrayvalue[6]
                    value_unit = "eV"
                elif key == "Abscissa_end":
                    value = arrayvalue[7]
                    value_unit = "eV"
                elif key == "Collection_time":
                    value = arrayvalue[10]
                    value_unit = "s"

            else:
                if key == "Year" or key == "Month" or key == "Day":
                    if checkDate(value):
                        dt = datetime.strptime(value, '%Y %m %d')
                        if key == "Year":
                            value = dt.year
                        elif key == "Month":
                            value = "{0:02d}".format(dt.month)
                        elif key == "Day":
                            value = "{0:02d}".format(dt.day)
                        else:
                            value = dt.strftime('%Y %m %d')
                    else:
                        return;
                elif key == "Element_and_transition":
                    value = arrayvalue[2]
                elif key == "Mode_of_signal_detection":
                    value = arrayvalue[12]
                elif key == "Peak_Sweep_Number":
                    value = arrayvalue[2]

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
    rawcolumns = []
    rawmetas = rawdata.findall('meta')
    for meta in rawmetas:
        rawcolumns.append(meta.attrib["key"])
    rawcolumns = list(set(rawcolumns))
    template = ET.parse(templatefile)
    columns = []
    metas = template.findall('meta')
    for meta in metas:
        columns.append(meta.attrib["key"])
    dom = xml.dom.minidom.Document()
    metadata = dom.createElement('metadata')
    dom.appendChild(metadata)
    count = 0

    metalist = {"Technique": "Technique",
                "Experiment_mode": "FileType",
                "Instrument_model_identifier": "InstrumentModel",
                "Year": "AcqFileDate",
                "Month": "AcqFileDate",
                "Day": "AcqFileDate",
                "File_name": "AcqFilename",
                "Institution_identifier": "Institution",
                "Experiment_Identifier": "ExperimentID",
                "Analyser_work_function":"AnalyserWorkFcn",
                "Source_analyser_angle_for_AES":"SourceAnalyserAngle",
                "Analyser_acceptance_solid_angle":"AnalyserSolidAngle",
                "Specimen_Stage_Rotation_Setting_During_Sputtering":"SampleRotation",
                "SemFieldOfView":"SemFieldOfView",
                "EBeamEnergy":"EBeamEnergy",
                "EBeamCurrent":"EBeamCurrent",
                "EBeamDiameter":"EBeamDiameter",
                "Sputtering_Raster_Area":"SputterRaster",
                "Analyser_mode":"AnalyserMode",
                "Measurement_Acquisition_Number":"SurvNumCycles",
                "NoDPDataCyc":"NoDPDataCyc",
                "NoPreSputterCyc":"NoPreSputterCyc",
                "SputterInterval":"SputterInterval",
                "SputterMode":"SputterMode",
                "NoSpectralReg":"NoSpectralReg",
                "Magnification":"Magnification",
                "NoSpatialArea":"NoSpatialArea",
                "NeutralizerCurrent":"NeutralizerCurrent",
                "NeutralizerEnergy":"NeutralizerEnergy",
                "AutoIonNeut":"AutoIonNeut",
                "Element_and_transition":"SpectralRegDef",
                "Abscissa_increment":"SpectralRegDef",
                "Abscissa_start":"SpectralRegDef",
                "Abscissa_end":"SpectralRegDef",
                "Collection_time":"SpectralRegDef",
                "Mode_of_signal_detection":"SpectralRegDef",
                "Peak_Sweep_Number":"SpectralRegDef2",
                "Comment":"FileDesc"}
    
    columns_unique = list(dict.fromkeys(columns))
    unitlist = []
    maxcolumn = 0
    for k in columns_unique:
        if k in metalist:
            v = metalist[k]
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
