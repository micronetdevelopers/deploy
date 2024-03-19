from django.shortcuts import render,redirect, HttpResponse

# Create your views here.
def home(request):
    return render(request, 'archival/home.html')


import random
import zipfile
import xml.etree.ElementTree as ET
from django.shortcuts import render
from django.http import JsonResponse
from .models import MarsMainTableData, MarsBandInformation, MarsBoundsCoordinates
from .serializers import MarsMainTableDataSerializer, MarsBandInformationSerializer, MarsBoundsCoordinatesSerializer
# from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import status
from PIL import Image
from io import BytesIO
import base64
from django.shortcuts import get_object_or_404

def extract_xml_data(zip_ref, file_path):
    try:
        with zip_ref.open(file_path) as source:
            xml_data = source.read()
            xml_text = xml_data.decode('utf-8')
        return xml_text
    except Exception as e:
        # Handle the exception
        print(f"Error extracting XML data: {e}")
        return None

def parse_xml_data(xml_text, dim_file_name):
    try:
        root = ET.fromstring(xml_text)

        xmldata = root.tag
        xmlSplit = dim_file_name.split("_")
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

        dataNameElement  = root.find('./Dataset_Identification/DATASET_NAME')
        if dataNameElement is not None and dataNameElement.text is not None:
            dataName = dataNameElement.text
        else:
            dataName = None  # Set to None if the tag is not present or has no value

        compNameElement = root.find('./Product_Information/Producer_Information/PRODUCER_NAME')
        if compNameElement is not None and compNameElement.text is not None:
            compName = compNameElement.text
        else:
            compName = None  # Set to None if the tag is not present or has no value

        # satName = root.find('./Product_Information/Delivery_Identification/PRODUCT_CODE').text
        if xmlFirst == "DIM":
            if xmlSecond in ["PHR1A", "PHR1B"]:
                product_code_element = root.find('./Product_Information/Delivery_Identification/PRODUCT_CODE')
                satName = product_code_element.text if product_code_element is not None and product_code_element.text is not None else None
            elif xmlSecond in ["PNEO3", "PNEO4", "SPOT6", "SPOT7"]:
                product_info_element = root.find('./Product_Information/Delivery_Identification/PRODUCT_INFO')
                satName = product_info_element.text if product_info_element is not None and product_info_element.text is not None else None
                print(satName)

        clRefElement = root.find('./Product_Information/Delivery_Identification/Order_Identification/CUSTOMER_REFERENCE')
        if clRefElement is not None and clRefElement.text is not None:
            clRef = clRefElement.text
        else:
            clRef = None  # Set to None if the tag is not present or has no value

        source_ident = root.find('./Dataset_Sources/Source_Identification/Strip_Source')
        if source_ident is not None:
            mission_element = source_ident.find('MISSION')
            mission_index_element = source_ident.find('MISSION_INDEX')

            senName = f"{mission_element.text} {mission_index_element.text}" if mission_element is not None and mission_index_element is not None else 'NO_SATT_NA'
        else:
            senName = None


        imgDataProcessLevelElement = root.find(
            './Processing_Information/Product_Settings/PROCESSING_LEVEL')
        if imgDataProcessLevelElement is not None and imgDataProcessLevelElement.text is not None:
            imgDataProcessLevel = imgDataProcessLevelElement.text
        else:
            imgDataProcessLevel = None  # Set to None if the tag is not present or has no value

        imgDataProcessSpecElement = root.find(
            './Processing_Information/Product_Settings/SPECTRAL_PROCESSING')
        if imgDataProcessSpecElement is not None and imgDataProcessSpecElement.text is not None:
            imgDataProcessSpec = imgDataProcessSpecElement.text
        else:
            imgDataProcessSpec = None  # Set to None if the tag is not present or has no value

        imgDate_element = root.find('./Dataset_Sources/Source_Identification/Strip_Source/IMAGING_DATE')
        if imgDate_element is not None and imgDate_element.text is not None:
            splittext = imgDate_element.text.split("-")
            yr, mm, dd = splittext[0], splittext[1], splittext[2]
            imgDate = f"{dd}-{mm}-{yr}"
        else:
            imgDate = None  # Set to None if the tag is not present or has no value


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
            dArea = None  # Set to None if the tag is not present or has no attributes


        dQL_path_elem = root.find('./Dataset_Identification/DATASET_QL_PATH')
        if dQL_path_elem is not None and 'href' in dQL_path_elem.attrib:
            dQLname = dQL_path_elem.attrib['href']
        else:
            dQLname = None


        dFormatElement = root.find('./Raster_Data/Data_Access/DATA_FILE_FORMAT')
        if dFormatElement is not None and dFormatElement.text is not None:
            dFormat = dFormatElement.text
        else:
            dFormat = None  # Set to None if the tag is not present or has no value

        cloud_elem = root.find('./Dataset_Content/CLOUD_COVERAGE')
        if cloud_elem is not None:
            cloudUnit = cloud_elem.attrib.get('unit', '')
            dCloud = cloud_elem.text if cloud_elem.text is not None else ''
        else:
            cloudUnit = ''
            dCloud = None


        snow_elem = root.find('./Dataset_Content/SNOW_COVERAGE')
        if snow_elem is not None:
            snowUnit = snow_elem.attrib.get('unit', '')
            dSnow = snow_elem.text if snow_elem.text is not None else '0'
        else:
            snowUnit = None
            dSnow = None


        dAQrangeElement = root.find(
            './Radiometric_Data/Dynamic_Range/ACQUISITION_RANGE')
        if dAQrangeElement is not None and dAQrangeElement.text is not None:
            dAQrange = dAQrangeElement.text
        else:
            dAQrange = None  # Set to None if the tag is not present or has no value

        dPRrangeElement = root.find('./Radiometric_Data/Dynamic_Range/PRODUCT_RANGE')
        if dPRrangeElement is not None and dPRrangeElement.text is not None:
            dPRrange = dPRrangeElement.text
        else:
            dPRrange = None  # Set to None if the tag is not present or has no value

        if xmlSecond in ["PHR1B", "PHR1A", "SPOT6", "SPOT7"]:
            paths = ['./Coordinate_Reference_System/Geodetic_CRS/GEODETIC_CRS_CODE', './Coordinate_Reference_System/Projected_CRS/PROJECTED_CRS_CODE']
        elif xmlSecond in ["PNEO4", "PNEO3"]:
            paths = ['./Coordinate_Reference_System/Geodetic_CRS/GEODETIC_CRS_CODE', './Coordinate_Reference_System/Projected_CRS/PROJECTED_CRS_CODE']

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
                dRows = 0  # or any default value you prefer in case of a non-integer value
        else:
            dRows = None  # Set to 0 or any default value if the element is not present or has no text value

        # Handling NCOLS
        ncols_element = root.find('./Raster_Data/Raster_Dimensions/NCOLS')

        if ncols_element is not None and ncols_element.text is not None:
            try:
                dCols = int(ncols_element.text)
            except ValueError:
                dCols = 0  # or any default value you prefer in case of a non-integer value
        else:
            dCols = None  # Set to 0 or any default value if the element is not present or has no text value

        # Handling NBANDS
        nbands_element = root.find('./Raster_Data/Raster_Dimensions/NBANDS')

        if nbands_element is not None and nbands_element.text is not None:
            try:
                dBands = int(nbands_element.text)
            except ValueError:
                dBands = 0  # or any default value you prefer in case of a non-integer value
        else:
            dBands = None  # Set to 0 or any default value if the element is not present or has no text value


        # Handling DATA_FILE_TILES
        dtilesTF_element = root.find('./Raster_Data/Data_Access/DATA_FILE_TILES')
        dtilesTF = dtilesTF_element.text if dtilesTF_element is not None and dtilesTF_element.text is not None else ''

        # Handling NTILES
        if dtilesTF.lower() == "true":
            ntiles_element = root.find('./Raster_Data/Raster_Dimensions/Tile_Set/NTILES')
            
            if ntiles_element is not None and ntiles_element.text is not None:
                try:
                    dTiles = int(ntiles_element.text)
                except ValueError:
                    dTiles = 0  # or any default value you prefer in case of a non-integer value
            else:
                dTiles = 0  # Set to 0 or any default value if the element is not present or has no text value
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
            dType = None  # Set to None if the tag is not present or has no value

        # Handling NBITS
        nbits_element = root.find('./Raster_Data/Raster_Encoding/NBITS')

        if nbits_element is not None and nbits_element.text is not None:
            try:
                dBits = int(nbits_element.text)
            except ValueError:
                dBits = 0  # or any default value you prefer in case of a non-integer value
        else:
            dBits = 0  # Set to 0 or any default value if the element is not present or has no text value


        dSignElement = root.find('./Raster_Data/Raster_Encoding/SIGN')
        if dSignElement is not None and dSignElement.text is not None:
            dSign = dSignElement.text
        else:
            dSign = None  # Set to None if the tag is not present or has no value

        # Handling INCIDENCE_ANGLE
        incidence_angle_element = root.find('./Geometric_Data/Use_Area/Located_Geometric_Values/Acquisition_Angles/INCIDENCE_ANGLE')
        if incidence_angle_element is not None and incidence_angle_element.text is not None:
            try:
                dINangle = float(incidence_angle_element.text)
            except ValueError:
                dINangle = 0.0  # or any default value you prefer in case of a non-float value
        else:
            dINangle = None  # Set to 0.0 or any default value if the element is not present or has no text value

        # Handling GSD_ACROSS_TRACK
        gsd_across_track_element = root.find('./Geometric_Data/Use_Area/Located_Geometric_Values/Ground_Sample_Distance/GSD_ACROSS_TRACK')
        if gsd_across_track_element is not None and gsd_across_track_element.text is not None:
            try:
                dGSDaxt = float(gsd_across_track_element.text)
            except ValueError:
                dGSDaxt = 0.0  # or any default value you prefer in case of a non-float value
        else:
            dGSDaxt = None  # Set to 0.0 or any default value if the element is not present or has no text value

        # Handling GSD_ALONG_TRACK
        gsd_along_track_element = root.find('./Geometric_Data/Use_Area/Located_Geometric_Values/Ground_Sample_Distance/GSD_ALONG_TRACK')
        if gsd_along_track_element is not None and gsd_along_track_element.text is not None:
            try:
                dGSDalt = float(gsd_along_track_element.text)
            except ValueError:
                dGSDalt = 0.0  # or any default value you prefer in case of a non-float value
        else:
            dGSDalt = None  # Set to 0.0 or any default value if the element is not present or has no text value


        resampling_spacing_element = root.find('./Processing_Information/Product_Settings/Sampling_Settings/RESAMPLING_SPACING')

        if resampling_spacing_element is not None and resampling_spacing_element.text is not None:
            try:
                dPIXx = float(resampling_spacing_element.text)
                dPixelx = dPIXx
                dPixely = dPIXx
            except ValueError:
                dPixelx = ''  # or any default value you prefer in case of a non-float value
                dPixely = ''  # or any default value you prefer in case of a non-float value
        else:
            dPixelx = None  # Set to empty string or any default value if the element is not present or has no text value
            dPixely = None  # Set to empty string or any default value if the element is not present or has no text value


        print(xmldata)
        print(dataCODE)
        print(dataName)
        print(compName)
        print(satName)
        print(clRef)
        print(senName)
        print(imgDataProcessLevel)
        print(imgDataProcessSpec)
        print(imgDate)
        print(dArea)
        print(dQLname)
        print(dFormat)
        print(dCloud)
        print(dSnow)
        print(dAQrange)
        print(dPRrange)
        print(dPRJtable)
        print(dPRJname)
        print(dRows)
        print(dCols)
        print(dBands)
        print(dTiles)
        print(dType)
        print(dBits)
        print(dSign)
        print(dINangle)
        print(dGSDaxt)
        print(dGSDalt)
        print(dPixelx)
        print(dPixely)
        
        
        # This Section For Bands 
        bandList= [] ; specMinList = [] ; specMaxList = []       

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
                        bameasureUnit = '{}'.format(item.text)  # saving the unit for conversion from nanometers to micrometer

            bandidpaths = [
                './Radiometric_Data/Radiometric_Calibration/Instrument_Calibration/Band_Measurement_List/Band_Spectral_Range/BAND_ID',
                './Radiometric_Data/Radiometric_Calibration/Band_Spectral_Range/BAND_ID'
            ]

            for bandidpath in bandidpaths:
                elements = root.findall(bandidpath)
                if elements:
                    for item in elements:
                        bandList.append(item.text)

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
                        bameasureUnit = '{}'.format(item.text)  # saving the unit for conversion from nanometers to micrometer

            bandidpaths = [
                './Radiometric_Data/Radiometric_Calibration/Instrument_Calibration/Band_Measurement_List/Band_Spectral_Range/BAND_ID',
                './Radiometric_Data/Radiometric_Calibration/Band_Spectral_Range/BAND_ID'
            ]

            for bandidpath in bandidpaths:
                elements = root.findall(bandidpath)
                if elements:
                    for item in elements:
                        bandList.append(item.text)

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
            print("COULD NOT FIGURE OUT THE DATA .................................PLEASE CHECK!")   

        print (bandList)
        print (specMinList)
        print (specMaxList)
        print (len(bandList))
        print (len(specMinList))
        print (len(specMaxList))
        
        
        
        xcodlist = []; ycodlist = []
        for item in root.findall('./Dataset_Content/Dataset_Extent/Vertex'):
            for item in root.findall('./Dataset_Content/Dataset_Extent/Vertex/LON'):
                xcodlist.append(str(item.text))

            for item in root.findall('./Dataset_Content/Dataset_Extent/Vertex/LAT'):
                ycodlist.append(str(item.text))

            if item.tag != '' :  break
    
        for idx, xcod in enumerate(xcodlist):
            print(f"Index: {idx}, X Coordinate: {xcod}")

        for idx, ycod in enumerate(ycodlist):
            print(f"Index: {idx}, Y Coordinate: {ycod}") 


        print ("XXcood = "+str(xcodlist))
        print ("YYcood = "+str(ycodlist))
        print ("----------------------------------------------------------------------------------------")
        print (" ")
        
        
        # Return the extracted variables as a dictionary
        return {
            'xmldata': xmldata,
            'dataCODE': dataCODE,
            'dataName': dataName,
            'compName': compName,
            'satName': satName,
            'clRef': clRef,
            'senName': senName,
            'imgDataProcessLevel': imgDataProcessLevel,
            'imgDataProcessSpec': imgDataProcessSpec,
            'imgDate': imgDate,
            'dArea': dArea,
            'dQLname': dQLname,
            'dFormat': dFormat,
            'dCloud': dCloud,
            'dSnow': dSnow,
            'dAQrange': dAQrange,
            'dPRrange': dPRrange,
            'dPRJtable': dPRJtable,
            'dPRJname': dPRJname,
            'dRows': dRows,
            'dCols': dCols,
            'dBands': dBands,
            'dTiles': dTiles,
            'dType': dType,
            'dBits': dBits,
            'dSign': dSign,
            'dINangle': dINangle,
            'dGSDaxt': dGSDaxt,
            'dGSDalt': dGSDalt,
            'dPixelx': dPixelx,
            'dPixely': dPixely,
            # bands information
            'bandName': bandList,
            'bandSspec': specMinList,
            'bandEspec': specMaxList,
            # bounds information
            'coodXx':xcodlist,
            'coodYy':ycodlist,
        }
    except ET.ParseError as pe:
        print(f"Error parsing XML data: {pe}")
        return None


@api_view(['POST','GET'])
def file_upload_view(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        # responseBack = uploaded_file
        selected_mission = request.POST.get('mission', '')
        selected_captureDataType = request.POST.get('captureDataType', '')
        print("selected_captureDataType ",selected_captureDataType)
        
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            file_names = zip_ref.namelist()
            desired_file = 'DIM_'
            desired_prefix = 'PREVIEW_'
            desired_extension = '.jpg'
            matching_files = [item for item in file_names if desired_file in item]

            matching_files_jpg = [item for item in file_names if desired_prefix in item and item.lower().endswith(desired_extension)]

            images_data = []
            for file_path_jpg in matching_files_jpg:
                with zip_ref.open(file_path_jpg) as file:
                    img_data = file.read()

                    # Convert the image data to base64
                    img_base64 = base64.b64encode(img_data).decode('utf-8')

                    images_data.append({
                        'file_path': file_path_jpg,
                        'image_data': img_base64,
                        # 'responseBack':uploaded_file,
                    })


            for file_path in matching_files:
                file_name = file_path.split('/')[-1]
                if file_name.startswith('DIM_'):
                    dim_file_name = file_name
                    xml_text = extract_xml_data(zip_ref, file_path)
                    parsed_variables = parse_xml_data(xml_text, dim_file_name)

                    root1 = ET.fromstring(xml_text)
                    xmlSplit1 = dim_file_name.split("_")
                    xmlFirst1 = xmlSplit1[0]
                    xmlSecond1 = xmlSplit1[1]

                    if xmlFirst1 == "DIM":
                        if xmlSecond1 in ["PHR1A", "PHR1B"]:
                            satName1 = root1.find(
                                './Product_Information/Delivery_Identification/PRODUCT_CODE').text
                        elif xmlSecond1 in ["PNEO3", "PNEO4", "SPOT6", "SPOT7"]:
                            satName1 = root1.find(
                                './Product_Information/Delivery_Identification/PRODUCT_INFO').text
                            if satName1 == selected_mission:
                                print(
                                    'ZIP file matches selected mission:', satName1)
                            else:
                                print(
                                    'ZIP file does not match selected mission:', satName1)

                    zipfile_size = uploaded_file.size
                    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
                    datasize = ""
                    for size in size_name:
                        if zipfile_size < 1024.0:
                            datasize = "%3.1f %s" % (zipfile_size, size)
                            break
                        zipfile_size /= 1024.0

                    if 'dim_file_name' in locals():
                        return Response({
                            'dim_file_name': dim_file_name,
                            'xml_text': xml_text,
                            'parsed_variables': parsed_variables,
                            'datasize': datasize,
                            "satName1": satName1,
                            'images_data': images_data
                            # 'file_path_jpg': file_path_jpg,
                            # 'image_data': img_data,
                        })
                    else:
                        return Response({'error': 'No DIM_ file found in the ZIP file.'}, status=status.HTTP_400_BAD_REQUEST)

            if 'dim_file_name' not in locals():
                return Response({'error': 'No DIM_ file found in the ZIP file.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'error': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST','GET'])
def formdatasave(request):
    if request.method == 'POST':
        try:
            # Extract data from the request
            data = {
                'DATACODE': request.data.get('dcode'),
                'DATANAME': request.data.get('dname'),
                'COMP_NA': request.data.get('cname'),
                'SATT_NA': request.data.get('sname'),
                'CL_REF': request.data.get('clRef'),
                'CL_ORDNA': request.data.get('cl_orderna'),
                'CL_PROJNA': request.data.get('cl_projna'),
                'CL_PURPOSE': request.data.get('cl_purpose'),
                'CL_ADDRESS1': request.data.get('cl_address1'),
                'CL_ADDRESS2': request.data.get('cl_address2'),
                'SEN_NAME': request.data.get('senName'),
                'IMG_DATYPE': request.data.get('imgDataType'),
                'IMG_DAPROC': request.data.get('imgDataProcSpec'),
                'IMG_DATE': request.data.get('imgDate'),
                'IMG_DT_RNG': request.data.get('img_dt_rng'),
                'DLOCA_CY': request.data.get('dloca_cy'),
                'DLOCA_ST': request.data.get('dloca_st'),
                'DLOCA_DT': request.data.get('dloca_dt'),
                'DLOCA_LOCA': request.data.get('dloca_loca'),
                'DAREA': request.data.get('dArea'),
                'DSIZE': request.data.get('dSize'),
                'DQLNAME': request.data.get('dQLname'),
                'DFORMAT': request.data.get('dFormat'),
                'DCLOUD': request.data.get('dCloud'),
                'DSNOW': request.data.get('dSnow'),
                'D_AQ_BITS': request.data.get('dAQBits'),
                'D_PR_BITS': request.data.get('dPRBits'),
                'DPRJ_TABLE': request.data.get('dPRJTable'),
                'DPRJ_NAME': request.data.get('dPRJName'),
                'D_NROWS': request.data.get('dRows'),
                'D_NCOLS': request.data.get('dCols'),
                'D_NBANDS': request.data.get('dBands'),
                'D_NTILES': request.data.get('dTiles'),
                'D_TYPE': request.data.get('dType'),
                'D_NBITS': request.data.get('dBits'),
                'D_SIGN': request.data.get('dSign'),
                'D_IN_ANGL': request.data.get('dINAngle'),
                'D_GSD_AXT': request.data.get('dGSDAxt'),
                'D_GSD_ALT': request.data.get('dGSDAlt'),
                'D_PIXELX': request.data.get('dPixelX'),
                'D_PIXELY': request.data.get('dPixelY'),
                'AL_DA_PATH': request.data.get('al_da_path'),
                'AL_SH_PATH': request.data.get('al_sh_path'),
                'AL_QL_PATH': request.data.get('al_ql_path'),
                'XML_FILE': request.data.get('xmlFile'),
            }
            print(data)

            # Saving main table data
            main_data_instance = MarsMainTableData(**data)
            main_data_instance.save()

            # Save band information
            bandcode = request.data.get('bandCode')
            bnd_names = request.data.get('bandName')
            bnd_s_specs = request.data.get('bandSSpec')
            bnd_e_specs = request.data.get('bandESpec')
            save_band_information(bandcode, bnd_names, bnd_s_specs, bnd_e_specs)

            # Save bounds coordinates
            boundcode = request.data.get('boundCode')
            cood_no = request.data.get('cood_no')
            cood_xx = request.data.get('coodXx')
            cood_yy = request.data.get('coodYy')
            save_bounds_coordinates(boundcode, cood_no, cood_xx, cood_yy)

            return Response({'message': 'Data saved successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f'Error saving data: {str(e)}')
            return Response({'message': f'Error saving data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)




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


        
from .serializers import MarsMainTableDataSerializer, MarsBandInformationSerializer, MarsBoundsCoordinatesSerializer

@api_view(['GET','POST'])
def show(request):
    marsmaintabledata = MarsMainTableData.objects.all()
    marsbandsinformation = MarsBandInformation.objects.all()
    marsboundsinfromation = MarsBoundsCoordinates.objects.all()
    # print(marsmaintabledata)
    # print(marsbandsinformation)
    # print(marsboundsinfromation)


    marsmaintabledata_serializer = MarsMainTableDataSerializer(marsmaintabledata, many=True)
    marsbandsinformation_serializer = MarsBandInformationSerializer(marsbandsinformation, many=True)
    marsboundsinfromation_serializer = MarsBoundsCoordinatesSerializer(marsboundsinfromation, many=True)

    data = {
        'marsmaintabledata': marsmaintabledata_serializer.data,
        'marsbandsinformation': marsbandsinformation_serializer.data,
        'marsboundsinfromation': marsboundsinfromation_serializer.data,
    }
    # print(data)

    return Response(data)
