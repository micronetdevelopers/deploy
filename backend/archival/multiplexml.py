# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 12:34:43 2024

@author: PRO-3
"""


from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
import xml.etree.ElementTree as ET
import random
import zipfile
import os
import glob
from django.shortcuts import render,redirect, HttpResponse
from .models import MarsMainTableData, MarsBandInformation, MarsBoundsCoordinates
from .serializers import MarsMainTableDataSerializer, MarsBandInformationSerializer, MarsBoundsCoordinatesSerializer


def home(request):
    return render(request, 'archival/home.html')

import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Disable CSRF protection for simplicity (You might want to remove this in production)
def generate_xml(request):
    if request.method == 'POST':
        input_folder_path = request.POST.get('Inputfolderpath', None)
        output_xml_file_path = request.POST.get('Outputxmlfilepath', None)
        
        if input_folder_path and output_xml_file_path:
            print("input_folder_path ",input_folder_path)
            print("output_xml_file_path ",output_xml_file_path)
            # Assuming output_xml_file_path contains the path of the output folder
            txtFileName = os.path.join(output_xml_file_path, "XML-EXTRACT-DATA.txt")  
            def writefileline(text, txtFileName):
                # Open file in append mode
                with open(txtFileName, "a") as file1:
                    # Write text to the file
                    file1.write(text + "\n")  # Add newline character to separate lines
            


            xml_folder = input_folder_path
            xml_files = glob.glob(os.path.join(xml_folder, "*.XML"))

            for index, xml_text in enumerate(xml_files):
                file_name = os.path.basename(xml_text)
                print("Processing file ", index + 1, ":", file_name)
                writefileline("Processing file {} : {}".format(index + 1, file_name), txtFileName)
                # writefileline("----------------------------------------------------------------------------------------", txtFileName)


                # xml_text = r"D:\MARS_XML_ExtractedFiles\DIM_PHR1A_MS_201903310528498_PRJ_4592482101-2.XML"
                # file_name = os.path.basename(xml_text)
                # print(file_name)
                
                
                root = ET.parse(xml_text)
                
                xmldata = root.getroot()
                xmlSplit = file_name.split("_")
                xmlFirst = "{0}".format(xmlSplit[0])
                xmlSecond = "{0}".format(xmlSplit[1])
                
                dataCODE = ''
                
                if xmlFirst == "DIM":
                    if xmlSecond in ["PHR1A", "PHR1B", "PNEO3", "PNEO4", "SPOT6", "SPOT7"]:
                        dataCODE = "AB" + str(random.randrange(100000, 999999))
                    elif xmlSecond == "PNEOXX":
                        dataCODE = "PL" + str(random.randrange(100000, 999999))
                    else:
                        dataCODE = "THE FILE NAME IS NOT IN PROPER FORMAT..... PLEASE CHECK !"
                
                dataNameElement = root.find('./Dataset_Identification/DATASET_NAME')
                if dataNameElement is not None and dataNameElement.text is not None:
                    dataName = dataNameElement.text
                else:
                    dataName = "notget"  # Set to None if the tag is not present or has no value
                
                compNameElement = root.find(
                    './Product_Information/Producer_Information/PRODUCER_NAME')
                if compNameElement is not None and compNameElement.text is not None:
                    compName = compNameElement.text
                else:
                    compName = "notget"  # Set to None if the tag is not present or has no value
                
                # satName = root.find('./Product_Information/Delivery_Identification/PRODUCT_CODE').text
                if xmlFirst == "DIM":
                    if xmlSecond in ["PHR1A", "PHR1B"]:
                        product_code_element = root.find(
                            './Product_Information/Delivery_Identification/PRODUCT_CODE')
                        satName = product_code_element.text if product_code_element is not None and product_code_element.text is not None else None
                    elif xmlSecond in ["PNEO3", "PNEO4", "SPOT6", "SPOT7"]:
                        product_info_element = root.find(
                            './Product_Information/Delivery_Identification/PRODUCT_INFO')
                        satName = product_info_element.text if product_info_element is not None and product_info_element.text is not None else None
                        print(satName)
                
                clRefElement = root.find(
                    './Product_Information/Delivery_Identification/Order_Identification/CUSTOMER_REFERENCE')
                if clRefElement is not None and clRefElement.text is not None:
                    clRef = clRefElement.text
                else:
                    clRef = "notget"  # Set to None if the tag is not present or has no value
                
                source_ident = root.find(
                    './Dataset_Sources/Source_Identification/Strip_Source')
                if source_ident is not None:
                    mission_element = source_ident.find('MISSION')
                    mission_index_element = source_ident.find('MISSION_INDEX')
                
                    senName = f"{mission_element.text} {mission_index_element.text}" if mission_element is not None and mission_index_element is not None else 'NO_SATT_NA'
                else:
                    senName = "notget"
                
                
                imgDataProcessLevelElement = root.find(
                    './Processing_Information/Product_Settings/PROCESSING_LEVEL')
                if imgDataProcessLevelElement is not None and imgDataProcessLevelElement.text is not None:
                    imgDataProcessLevel = imgDataProcessLevelElement.text
                else:
                    imgDataProcessLevel = "notget"  # Set to None if the tag is not present or has no value
                
                imgDataProcessSpecElement = root.find(
                    './Processing_Information/Product_Settings/SPECTRAL_PROCESSING')
                if imgDataProcessSpecElement is not None and imgDataProcessSpecElement.text is not None:
                    imgDataProcessSpec = imgDataProcessSpecElement.text
                else:
                    imgDataProcessSpec = "notget"  # Set to None if the tag is not present or has no value
                
                imgDate_element = root.find(
                    './Dataset_Sources/Source_Identification/Strip_Source/IMAGING_DATE')
                if imgDate_element is not None and imgDate_element.text is not None:
                    splittext = imgDate_element.text.split("-")
                    yr, mm, dd = splittext[0], splittext[1], splittext[2]
                    imgDate = f"{dd}-{mm}-{yr}"
                else:
                    imgDate = "notget"  # Set to None if the tag is not present or has no value
                
                
                dArea_elem = root.find('./Dataset_Content/SURFACE_AREA')
                if dArea_elem is not None and 'unit' in dArea_elem.attrib:
                    dattb = dArea_elem.attrib['unit']
                    if dattb == "square km":
                        bArea = dArea_elem.text
                        dArea = float(bArea)
                    elif dattb == "square m":
                        bArea = dArea_elem.text
                        dArea = float(bArea) / 10000
                    else:
                        dArea = ''
                else:
                    dArea = 0.0  # Set to None if the tag is not present or has no attributes
                
                
                dQL_path_elem = root.find('./Dataset_Identification/DATASET_QL_PATH')
                if dQL_path_elem is not None and 'href' in dQL_path_elem.attrib:
                    dQLname = dQL_path_elem.attrib['href']
                else:
                    dQLname = "notget"
                
                
                dFormatElement = root.find('./Raster_Data/Data_Access/DATA_FILE_FORMAT')
                if dFormatElement is not None and dFormatElement.text is not None:
                    dFormat = dFormatElement.text
                else:
                    dFormat = "notget"  # Set to None if the tag is not present or has no value
                
                cloud_elem = root.find('./Dataset_Content/CLOUD_COVERAGE')
                if cloud_elem is not None:
                    cloudUnit = cloud_elem.attrib.get('unit', '')
                    dCloud = cloud_elem.text if cloud_elem.text is not None else ''
                else:
                    cloudUnit = ''
                    dCloud = 0.0
                
                
                snow_elem = root.find('./Dataset_Content/SNOW_COVERAGE')
                if snow_elem is not None:
                    snowUnit = snow_elem.attrib.get('unit', '')
                    dSnow = snow_elem.text if snow_elem.text is not None else '0'
                else:
                    snowUnit = None
                    dSnow = 0.0
                
                
                dAQrangeElement = root.find(
                    './Radiometric_Data/Dynamic_Range/ACQUISITION_RANGE')
                if dAQrangeElement is not None and dAQrangeElement.text is not None:
                    dAQrange = dAQrangeElement.text
                else:
                    dAQrange = 1  # Set to None if the tag is not present or has no value
                
                dPRrangeElement = root.find('./Radiometric_Data/Dynamic_Range/PRODUCT_RANGE')
                if dPRrangeElement is not None and dPRrangeElement.text is not None:
                    dPRrange = dPRrangeElement.text
                else:
                    dPRrange = 1  # Set to None if the tag is not present or has no value
                
                if xmlSecond in ["PHR1B", "PHR1A", "SPOT6", "SPOT7"]:
                    paths = ['./Coordinate_Reference_System/Geodetic_CRS/GEODETIC_CRS_CODE',
                            './Coordinate_Reference_System/Projected_CRS/PROJECTED_CRS_CODE']
                elif xmlSecond in ["PNEO4", "PNEO3"]:
                    paths = ['./Coordinate_Reference_System/Geodetic_CRS/GEODETIC_CRS_CODE',
                            './Coordinate_Reference_System/Projected_CRS/PROJECTED_CRS_CODE']
                
                for path in paths:
                    for item in root.findall(path):
                        dPRJcode = item.text if item is not None and item.text is not None else ''
                        aaa = dPRJcode.split(":")
                        dPRJtable = aaa[4] if len(aaa) > 4 else None
                        dPRJname = aaa[6] if len(aaa) > 6 else None
                
                
                nrows_element = root.find('./Raster_Data/Raster_Dimensions/NROWS')
                
                if nrows_element is not None and nrows_element.text is not None:
                    try:
                        dRows = int(nrows_element.text)
                    except ValueError:
                        dRows = 1  # or any default value you prefer in case of a non-integer value
                else:
                    dRows = 1  # Set to 0 or any default value if the element is not present or has no text value
                
                # Handling NCOLS
                ncols_element = root.find('./Raster_Data/Raster_Dimensions/NCOLS')
                
                if ncols_element is not None and ncols_element.text is not None:
                    try:
                        dCols = int(ncols_element.text)
                    except ValueError:
                        dCols = 1  # or any default value you prefer in case of a non-integer value
                else:
                    dCols = 1  # Set to 0 or any default value if the element is not present or has no text value
                
                # Handling NBANDS
                nbands_element = root.find('./Raster_Data/Raster_Dimensions/NBANDS')
                
                if nbands_element is not None and nbands_element.text is not None:
                    try:
                        dBands = int(nbands_element.text)
                    except ValueError:
                        dBands = 1  # or any default value you prefer in case of a non-integer value
                else:
                    dBands = 1  # Set to 0 or any default value if the element is not present or has no text value
                
                
                # Handling DATA_FILE_TILES
                dtilesTF_element = root.find('./Raster_Data/Data_Access/DATA_FILE_TILES')
                dtilesTF = dtilesTF_element.text if dtilesTF_element is not None and dtilesTF_element.text is not None else ''
                
                # Handling NTILES
                if dtilesTF.lower() == "true":
                    ntiles_element = root.find(
                        './Raster_Data/Raster_Dimensions/Tile_Set/NTILES')
                
                    if ntiles_element is not None and ntiles_element.text is not None:
                        try:
                            dTiles = int(ntiles_element.text)
                        except ValueError:
                            dTiles = 1  # or any default value you prefer in case of a non-integer value
                    else:
                        dTiles = 1  # Set to 0 or any default value if the element is not present or has no text value
                else:
                    # Check if tile_R="1" and tile_C="1" exists
                    data_files = root.findall('./Raster_Data/Data_Access/Data_Files/Data_File')
                    if any(data_file.get('tile_R') == "1" and data_file.get('tile_C') == "1" for data_file in data_files):
                        dTiles = 1
                    else:
                        dTiles = 1  # Set to None or any default value if tile_R="1" and tile_C="1" does not exist
                
                
                dTypeElement = root.find('./Raster_Data/Raster_Encoding/DATA_TYPE')
                if dTypeElement is not None and dTypeElement.text is not None:
                    dType = dTypeElement.text
                else:
                    dType = "notget"  # Set to None if the tag is not present or has no value
                
                # Handling NBITS
                nbits_element = root.find('./Raster_Data/Raster_Encoding/NBITS')
                
                if nbits_element is not None and nbits_element.text is not None:
                    try:
                        dBits = int(nbits_element.text)
                    except ValueError:
                        dBits = 1  # or any default value you prefer in case of a non-integer value
                else:
                    dBits = 1  # Set to 0 or any default value if the element is not present or has no text value
                
                
                dSignElement = root.find('./Raster_Data/Raster_Encoding/SIGN')
                if dSignElement is not None and dSignElement.text is not None:
                    dSign = dSignElement.text
                else:
                    dSign = "notget"  # Set to None if the tag is not present or has no value
                
                # Handling INCIDENCE_ANGLE
                incidence_angle_element = root.find(
                    './Geometric_Data/Use_Area/Located_Geometric_Values/Acquisition_Angles/INCIDENCE_ANGLE')
                if incidence_angle_element is not None and incidence_angle_element.text is not None:
                    try:
                        dINangle = float(incidence_angle_element.text)
                    except ValueError:
                        dINangle = 0.0  # or any default value you prefer in case of a non-float value
                else:
                    dINangle = 0.0  # Set to 0.0 or any default value if the element is not present or has no text value
                
                # Handling GSD_ACROSS_TRACK
                gsd_across_track_element = root.find(
                    './Geometric_Data/Use_Area/Located_Geometric_Values/Ground_Sample_Distance/GSD_ACROSS_TRACK')
                if gsd_across_track_element is not None and gsd_across_track_element.text is not None:
                    try:
                        dGSDaxt = float(gsd_across_track_element.text)
                    except ValueError:
                        dGSDaxt = 0.0  # or any default value you prefer in case of a non-float value
                else:
                    dGSDaxt = 0.0  # Set to 0.0 or any default value if the element is not present or has no text value
                
                # Handling GSD_ALONG_TRACK
                gsd_along_track_element = root.find(
                    './Geometric_Data/Use_Area/Located_Geometric_Values/Ground_Sample_Distance/GSD_ALONG_TRACK')
                if gsd_along_track_element is not None and gsd_along_track_element.text is not None:
                    try:
                        dGSDalt = float(gsd_along_track_element.text)
                    except ValueError:
                        dGSDalt = 0.0  # or any default value you prefer in case of a non-float value
                else:
                    dGSDalt = 0.0  # Set to 0.0 or any default value if the element is not present or has no text value
                
                
                resampling_spacing_element = root.find(
                    './Processing_Information/Product_Settings/Sampling_Settings/RESAMPLING_SPACING')
                
                if resampling_spacing_element is not None and resampling_spacing_element.text is not None:
                    try:
                        dPIXx = float(resampling_spacing_element.text)
                        dPixelx = dPIXx
                        dPixely = dPIXx
                    except ValueError:
                        dPixelx = ''  # or any default value you prefer in case of a non-float value
                        dPixely = ''  # or any default value you prefer in case of a non-float value
                else:
                    dPixelx = 0.0  # Set to empty string or any default value if the element is not present or has no text value
                    dPixely = 0.0  # Set to empty string or any default value if the element is not present or has no text value
                
                print("----------------------------------------------------------------------------------------")
                print("xmlFile -", file_name)
                print("dataCODE -", dataCODE)
                print("dataName -", dataName)
                print("compName -", compName)
                print("satName -", satName)
                print("clRef -", clRef)
                print("senName -", senName)
                print("imgDataProcessLevel -", imgDataProcessLevel)
                print("imgDataProcessSpec -", imgDataProcessSpec)
                print("imgDate -", imgDate)
                print("dArea -", dArea)
                print("dQLname -", dQLname)
                print("dFormat -", dFormat)
                print("dCloud -", dCloud)
                print("dSnow -", dSnow)
                print("dAQrange -", dAQrange)
                print("dPRrange -", dPRrange)
                print("dPRJtable -", dPRJtable)
                print("dPRJname -", dPRJname)
                print("dRows -", dRows)
                print("dCols -", dCols)
                print("dBands -", dBands)
                print("dTiles -", dTiles)
                print("dType -", dType)
                print("dBits -", dBits)
                print("dSign -", dSign)
                print("dINangle -", dINangle)
                print("dGSDaxt -", dGSDaxt)
                print("dGSDalt -", dGSDalt)
                print("dPixelx -", dPixelx)
                print("dPixely -", dPixely)
                print("----------------------------------------------------------------------------------------")
                writefileline("----------------------------------------------------------------------------------------", txtFileName)
                writefileline("xmlFile - " + str(file_name), txtFileName)
                writefileline("dataCODE - " + str(dataCODE), txtFileName)
                writefileline("dataName - " + str(dataName), txtFileName)
                writefileline("compName - " + str(compName), txtFileName)
                writefileline("satName - " + str(satName), txtFileName)
                writefileline("clRef - " + str(clRef), txtFileName)
                writefileline("senName - " + str(senName), txtFileName)
                writefileline("imgDataProcessLevel - " + str(imgDataProcessLevel), txtFileName)
                writefileline("imgDataProcessSpec - " + str(imgDataProcessSpec), txtFileName)
                writefileline("imgDate - " + str(imgDate), txtFileName)
                writefileline("dArea - " + str(dArea), txtFileName)
                writefileline("dQLname - " + str(dQLname), txtFileName)
                writefileline("dFormat - " + str(dFormat), txtFileName)
                writefileline("dCloud - " + str(dCloud), txtFileName)
                writefileline("dSnow - " + str(dSnow), txtFileName)
                writefileline("dAQrange - " + str(dAQrange), txtFileName)
                writefileline("dPRrange - " + str(dPRrange), txtFileName)
                writefileline("dPRJtable - " + str(dPRJtable), txtFileName)
                writefileline("dPRJname - " + str(dPRJname), txtFileName)
                writefileline("dRows - " + str(dRows), txtFileName)
                writefileline("dCols - " + str(dCols), txtFileName)
                writefileline("dBands - " + str(dBands), txtFileName)
                writefileline("dTiles - " + str(dTiles), txtFileName)
                writefileline("dType - " + str(dType), txtFileName)
                writefileline("dBits - " + str(dBits), txtFileName)
                writefileline("dSign - " + str(dSign), txtFileName)
                writefileline("dINangle - " + str(dINangle), txtFileName)
                writefileline("dGSDaxt - " + str(dGSDaxt), txtFileName)
                writefileline("dGSDalt - " + str(dGSDalt), txtFileName)
                writefileline("dPixelx - " + str(dPixelx), txtFileName)
                writefileline("dPixely - " + str(dPixely), txtFileName)
                writefileline("----------------------------------------------------------------------------------------", txtFileName)
                
                # This Section For Bands
                bandList = []
                specMinList = []
                specMaxList = []
                
                if xmlSecond in ["PHR1B", "PHR1A", "SPOT6", "SPOT7"]:
                    unitpaths = [
                        './Radiometric_Data/Radiometric_Calibration/Instrument_Calibration/Band_Measurement_List/Band_Spectral_Range/MEASURE_UNIT',
                        './Radiometric_Data/Radiometric_Calibration/Band_Spectral_Range/MEASURE_UNIT'
                    ]
                
                    for unitpath in unitpaths:
                        elements = root.findall(unitpath)
                        if elements:
                            for item in elements:
                                print(item.tag + " MEASURE UNIT PHR " + item.text)
                                # saving the unit for conversion from nanometers to micrometer
                                bameasureUnit = '{}'.format(item.text)
                
                    bandidpaths = [
                        './Radiometric_Data/Radiometric_Calibration/Instrument_Calibration/Band_Measurement_List/Band_Spectral_Range/BAND_ID',
                        './Radiometric_Data/Radiometric_Calibration/Band_Spectral_Range/BAND_ID'
                    ]
                
                    for bandidpath in bandidpaths:
                        elements = root.findall(bandidpath)
                        if elements:
                            for item in elements:
                                bandList.append(item.text)
                        else:
                            bandList.append('not')
                
                    minpaths = [
                        './Radiometric_Data/Radiometric_Calibration/Instrument_Calibration/Band_Measurement_List/Band_Spectral_Range/MIN',
                        './Radiometric_Data/Radiometric_Calibration/Band_Spectral_Range/FWHM/MIN'
                    ]
                
                    for minpath in minpaths:
                        elements = root.findall(minpath)
                        if elements:
                            for item in elements:
                                print(item.tag + "Start" + item.text)
                                if bameasureUnit == 'nanometers' or bameasureUnit == 'nanometer':
                                    spec = float('{}'.format(item.text)) / 1000
                                    print(str(spec))
                                    specMinList.append(spec)
                                else:
                                    specMinList.append(item.text)
                        else:
                            specMinList.append('0.0')
                
                    maxpaths = [
                        './Radiometric_Data/Radiometric_Calibration/Instrument_Calibration/Band_Measurement_List/Band_Spectral_Range/MAX',
                        './Radiometric_Data/Radiometric_Calibration/Band_Spectral_Range/FWHM/MAX'
                    ]
                
                    for maxpath in maxpaths:
                        elements = root.findall(maxpath)
                        if elements:
                            for item in elements:
                                print(item.tag + " END " + item.text)
                                if bameasureUnit == 'nanometers' or bameasureUnit == 'nanometer':
                                    spec = float('{}'.format(item.text)) / 1000
                                    print(str(spec))
                                    specMaxList.append(spec)
                                else:
                                    specMaxList.append(item.text)
                            else:
                                specMaxList.append('0.0')
                elif xmlSecond == "PNEO3" or xmlSecond == "PNEO4":
                    unitpaths = [
                        './Radiometric_Data/Radiometric_Calibration/Instrument_Calibration/Band_Measurement_List/Band_Spectral_Range/MEASURE_UNIT',
                        './Radiometric_Data/Radiometric_Calibration/Band_Spectral_Range/MEASURE_UNIT'
                    ]
                
                    for unitpath in unitpaths:
                        elements = root.findall(unitpath)
                        if elements:
                            for item in elements:
                                print(item.tag + " MEASURE_UNIT_PNEO " + item.text)
                                # saving the unit for conversion from nanometers to micrometer
                                bameasureUnit = '{}'.format(item.text)
                
                    bandidpaths = [
                        './Radiometric_Data/Radiometric_Calibration/Instrument_Calibration/Band_Measurement_List/Band_Spectral_Range/BAND_ID',
                        './Radiometric_Data/Radiometric_Calibration/Band_Spectral_Range/BAND_ID'
                    ]
                
                    for bandidpath in bandidpaths:
                        elements = root.findall(bandidpath)
                        if elements:
                            for item in elements:
                                bandList.append(item.text)
                        else:
                            bandList.append('not')
                
                    minpaths = [
                        './Radiometric_Data/Radiometric_Calibration/Instrument_Calibration/Band_Measurement_List/Band_Spectral_Range/FWHM/MIN',
                        './Radiometric_Data/Radiometric_Calibration/Band_Spectral_Range/FWHM/MIN'
                    ]
                
                    for minpath in minpaths:
                        elements = root.findall(minpath)
                        if elements:
                            for item in elements:
                                print(item.tag + " Start " + item.text)
                                if bameasureUnit == 'nanometer' or bameasureUnit == 'nanometers':
                                    spec = float('{}'.format(item.text)) / 1000
                                    print(str(spec))
                                    specMinList.append(spec)
                                else:
                                    specMinList.append(item.text)
                        else:
                            specMinList.append('0.0')
                
                    maxpaths = [
                        './Radiometric_Data/Radiometric_Calibration/Instrument_Calibration/Band_Measurement_List/Band_Spectral_Range/FWHM/MAX',
                        './Radiometric_Data/Radiometric_Calibration/Band_Spectral_Range/FWHM/MAX'
                    ]
                
                    for maxpath in maxpaths:
                        elements = root.findall(maxpath)
                        if elements:
                            for item in elements:
                                print(item.tag + " end " + item.text)
                                if bameasureUnit == 'nanometer' or bameasureUnit == 'nanometers':
                                    spec = float('{}'.format(item.text)) / 1000
                                    print(str(spec))
                                    specMaxList.append(spec)
                                else:
                                    specMaxList.append(item.text)
                        else:
                            specMaxList.append('0.0')
                else:
                    print("COULD NOT FIGURE OUT THE DATA .................................PLEASE CHECK!")
                print("----------------------------------------------------------------------------------------")
                print("bandList -", bandList)
                print("specMinList -", specMinList)
                print("specMaxList -", specMaxList)
                print("bandList -", len(bandList))
                print("specMinList -", len(specMinList))
                print("specMaxList -", len(specMaxList))
                print("----------------------------------------------------------------------------------------")
                writefileline("bandList - " + str(bandList), txtFileName)
                writefileline("specMinList - " + str(specMinList), txtFileName)
                writefileline("specMaxList - " + str(specMaxList), txtFileName)
                writefileline("bandList - " + str(len(bandList)), txtFileName)
                writefileline("specMinList - " + str(len(specMinList)), txtFileName)
                writefileline("specMaxList - " + str(len(specMaxList)), txtFileName)

                writefileline("----------------------------------------------------------------------------------------", txtFileName)
                
                
                xcodlist = []
                ycodlist = []
                for item in root.findall('./Dataset_Content/Dataset_Extent/Vertex'):
                    for item in root.findall('./Dataset_Content/Dataset_Extent/Vertex/LON'):
                        xcodlist.append(str(item.text))
                
                    for item in root.findall('./Dataset_Content/Dataset_Extent/Vertex/LAT'):
                        ycodlist.append(str(item.text))
                
                    if item.tag != '':
                        break
                
                for idx, xcod in enumerate(xcodlist):
                    print(f"Index: {idx}, X Coordinate: {xcod}")
                
                for idx, ycod in enumerate(ycodlist):
                    print(f"Index: {idx}, Y Coordinate: {ycod}")
                
                print("----------------------------------------------------------------------------------------")
                print("XXcood = "+str(xcodlist))
                print("YYcood = "+str(ycodlist))
                print("----------------------------------------------------------------------------------------")
                print(" ")
                writefileline("XXcood = " + str(xcodlist), txtFileName)
                writefileline("YYcood = " + str(ycodlist), txtFileName)
                writefileline("----------------------------------------------------------------------------------------", txtFileName)
                writefileline("", txtFileName)  # Add an empty line between each record
                data = {
                    'DATACODE': dataCODE,
                    'DATANAME': dataName,
                    'COMP_NA': compName,
                    'SATT_NA': satName,
                    'CL_REF': clRef,
                    'CL_ORDNA': "userfill",
                    'CL_PROJNA': "userfill",
                    'CL_PURPOSE': "userfill",
                    'CL_ADDRESS1': "userfill",
                    'CL_ADDRESS2': "userfill",
                    'SEN_NAME': senName,
                    'IMG_DATYPE': imgDataProcessLevel,
                    'IMG_DAPROC': imgDataProcessSpec,
                    'IMG_DATE': imgDate,
                    'IMG_DT_RNG': "userfill",
                    'DLOCA_CY': "userfill",
                    'DLOCA_ST': "userfill",
                    'DLOCA_DT': "userfill",
                    'DLOCA_LOCA': "userfill",
                    'DAREA': dArea,
                    'DSIZE': "zipfile",
                    'DQLNAME': dQLname,
                    'DFORMAT': dFormat,
                    'DCLOUD': dCloud,
                    'DSNOW': dSnow,
                    'D_AQ_BITS': dAQrange,
                    'D_PR_BITS': dPRrange,
                    'DPRJ_TABLE': dPRJtable,
                    'DPRJ_NAME': dPRJname,
                    'D_NROWS': dRows,
                    'D_NCOLS': dCols,
                    'D_NBANDS': dBands,
                    'D_NTILES': dTiles,
                    'D_TYPE': dType,
                    'D_NBITS': dBits,
                    'D_SIGN': dSign,
                    'D_IN_ANGL': dINangle,
                    'D_GSD_AXT': dGSDaxt,
                    'D_GSD_ALT': dGSDalt,
                    'D_PIXELX': dPixelx,
                    'D_PIXELY': dPixely,
                    'AL_DA_PATH': "userfill",
                    'AL_SH_PATH': "userfill",
                    'AL_QL_PATH': "userfill",
                    'XML_FILE': file_name,
                }
                print(data)
                main_data_instance = MarsMainTableData(**data)
                main_data_instance.save()

                # Save band information
                bandcode = dataCODE
                bnd_names = bandList
                bnd_s_specs = specMinList
                bnd_e_specs = specMaxList
                save_band_information(bandcode, bnd_names, bnd_s_specs, bnd_e_specs)

                # Save bounds coordinates
                boundcode = dataCODE
                cood_no = "0,1,2,3"
                cood_xx = xcodlist
                cood_yy = ycodlist
                save_bounds_coordinates(boundcode, cood_no, cood_xx, cood_yy)
            return JsonResponse({'message': 'Both input values received successfully!'})
        else:
            return JsonResponse({'error': 'Both input values are required.'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    

def save_band_information(bandcode, bnd_names, bnd_s_specs, bnd_e_specs):
    if bnd_names is not None:
        bnd_names = ','.join(map(str, bnd_names))
        bnd_names = bnd_names.split(',')
    else:
        bnd_names = []

    if bnd_s_specs is not None:
        bnd_s_specs = ','.join(map(str, bnd_s_specs))
        bnd_s_specs = bnd_s_specs.split(',')
    else:
        bnd_s_specs = []

    if bnd_e_specs is not None:
        bnd_e_specs = ','.join(map(str, bnd_e_specs))
        bnd_e_specs = bnd_e_specs.split(',')
    else:
        bnd_e_specs = []

    for band_name, spec_min, spec_max in zip(bnd_names, bnd_s_specs, bnd_e_specs):
        band_info_instance = MarsBandInformation(
            DATACODE=MarsMainTableData.objects.get(DATACODE=bandcode),
            BAND_NAME=band_name,
            BAND_S_SPEC=float(spec_min),
            BAND_E_SPEC=float(spec_max)
        )
        band_info_instance.save()

def save_bounds_coordinates(boundcode, cood_no, cood_xx, cood_yy):
    import ast
    def convert_to_list(value):
        try:
            if value is not None and value != '':
                # If the value is already a list, return it
                if isinstance(value, list):
                    return value
                # If the value is a string, evaluate it using ast.literal_eval
                elif isinstance(value, str):
                    return ast.literal_eval(value)
            return []        
        except(ValueError, SyntaxError):
            return []   
    
    cood_no = convert_to_list(cood_no)
    cood_xx = convert_to_list(cood_xx)
    cood_yy = convert_to_list(cood_yy)        
    
    print("Length of cood_no:", len(cood_no))
    print("Length of cood_xx:", len(cood_xx))
    print("Length of cood_yy:", len(cood_yy))
    
    # # Check if lengths are the same
    if len(cood_no) == len(cood_xx) == len(cood_yy):
        for i in range(len(cood_no)):
            try:
                bounds_info_instance = MarsBoundsCoordinates(
                    DATACODE=MarsMainTableData.objects.get(DATACODE=boundcode),
                    COOD_NO=int(cood_no[i]),
                    COOD_XX=float(cood_xx[i]),
                    COOD_YY=float(cood_yy[i])
                )
                bounds_info_instance.save()
                print(bounds_info_instance)
            except (ValueError, TypeError) as e:
                print(f"Error creating MarsBoundsCoordinates instance: {e}")
    else:
        print("Error: The lengths of cood_no, cood_xx, and cood_yy are not the same.") 