# from __future__ import print_function
# import osgeo
# print(osgeo.__version__)
# import os
# import sys
# import shutil
# import datetime
# from osgeo import gdal
# from osgeo import ogr
# import json
# import xml.etree.ElementTree as ET


from django.shortcuts import render,redirect, HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from archival.models import *
from archival.serializers import *
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.core.serializers import serialize
import json
from shapely.geometry import Polygon,Point,LineString
# from .serializers import MarsMainTableDataSerializer, MarsBandInformationSerializer, MarsBoundsCoordinatesSerializer




# Create your views here.
def home(request):
    return render(request, 'search/home.html')


@api_view(['POST','GET'])
def searchbyattributeapi(request):
    if request.method == 'POST':
        try:
            SUBJECT = request.data.get('subject')
            TOPIC = request.data.get('topic')
            CHAPTER = request.data.get('chapter')
            STARTDATE = request.data.get('startDate')
            ENDDATE = request.data.get('endDate')
            RESOLUTION = request.data.get('resolution')
            CLOUDCOVER = request.data.get('cloudCover')
            SNOWCOVER = request.data.get('snowCover')
            DATAPROCESSINGTYPE = request.data.get('dataProcessingType')
            DATAINCIDENCEANGLE = request.data.get('dataIncidenceAngle')
            AOIGEOMETRY = request.data.get('aoigeometry')
           
            print("SUBJECT====================================== ",SUBJECT)
            print("TOPIC========================================== ",TOPIC)
            print("CHAPTER====================================== ",CHAPTER)
            print("STARTDATE ================================= ",STARTDATE)
            print("ENDDATE====================================== ",ENDDATE)
            print("RESOLUTION================================ ",RESOLUTION)
            print("CLOUDCOVER================================ ",CLOUDCOVER)
            print("SNOWCOVER================================== ",SNOWCOVER)
            print("DATAPROCESSINGTYPE================ ",DATAPROCESSINGTYPE)
            print("DATAINCIDENCEANGLE================ ",DATAINCIDENCEANGLE)
            print("AOIGEOMETRY======================= ",AOIGEOMETRY)

            

            # Extract geometry type and coordinates from AOIGEOMETRY
            if isinstance(AOIGEOMETRY, dict):
                if AOIGEOMETRY.get('type') == 'Point':
                        coordinates = AOIGEOMETRY.get('coordinates')
                        if coordinates:
                            CorrectAOI = {'type': 'Point', 'coordinates': coordinates}
                        elif AOIGEOMETRY.get('type') == 'Point':
                            coordinates = AOIGEOMETRY.get('geometry', {}).get('coordinates')
                            if coordinates:
                                CorrectAOI = {'type': 'Point', 'coordinates': coordinates}
                            else:
                                CorrectAOI = None
                elif AOIGEOMETRY.get('type') == 'LineString':
                        coordinates = AOIGEOMETRY.get('coordinates')
                        if coordinates:
                            CorrectAOI = {'type': 'LineString', 'coordinates': coordinates}
                        elif AOIGEOMETRY.get('type') == 'LineString':
                            coordinates = AOIGEOMETRY.get('geometry', {}).get('coordinates')
                            if coordinates:
                                CorrectAOI = {'type': 'LineString', 'coordinates': coordinates}
                            else:
                                CorrectAOI = None
                elif AOIGEOMETRY.get('type') == 'Polygon':
                    coordinates = AOIGEOMETRY.get('coordinates')
                    if coordinates:
                        CorrectAOI = {'type': 'Polygon', 'coordinates': coordinates}
                    elif AOIGEOMETRY.get('type') == 'Polygon':
                        coordinates = AOIGEOMETRY.get('geometry', {}).get('coordinates')
                        if coordinates:
                            CorrectAOI = {'type': 'Polygon', 'coordinates': coordinates}
                        else:
                            CorrectAOI = None
            # elif isinstance(AOIGEOMETRY, list):
            #     if len(AOIGEOMETRY) > 1:
            #         CorrectAOI = {'type': 'Polygon', 'coordinates': AOIGEOMETRY}
            #     else:
            #         CorrectAOI = {'type': 'Point', 'coordinates': AOIGEOMETRY}
            # else:
            #     pass
            if CorrectAOI is None:
                return Response({"Message": "Error: Invalid AOIGEOMETRY type or missing coordinates"}, status=status.HTTP_400_BAD_REQUEST)

            print("CorrectAOI ",CorrectAOI)

            geometry_type = CorrectAOI.get('type')
            print("geometry_type ",geometry_type)

            if geometry_type == 'Point':
                coordinates = CorrectAOI.get('coordinates')
                if coordinates:
                    try:
                        point = Point(float(coordinates[0]), float(coordinates[1]))
                    except ValueError:
                        return Response({"Message": "Error: Invalid coordinates for Point geometry"}, status=status.HTTP_400_BAD_REQUEST)
                    bounding_box = point.buffer(0.09009)# for point i have add 10km distance
                    print("bounding_boxBuffer:- ",bounding_box)
                    filtered_coordinates = MarsBoundsCoordinates.objects.filter(
                        Q(COOD_XX__range=(bounding_box.bounds[0], bounding_box.bounds[2])) &
                        Q(COOD_YY__range=(bounding_box.bounds[1], bounding_box.bounds[3]))
                    )
                    print("filtered_coordinatesPoint 🧿 == ", filtered_coordinates)
                else:
                    return Response({"Message": "Error: Missing coordinates for Point geometry"}, status=status.HTTP_400_BAD_REQUEST)
            elif geometry_type == 'LineString':
                coordinates = CorrectAOI.get('coordinates')
                if coordinates:
                    try:
                        linestring = LineString([(float(coord[0]), float(coord[1])) for coord in coordinates])
                    except ValueError:
                        return Response({"Message": "Error: Invalid coordinates for LineString geometry"}, status=status.HTTP_400_BAD_REQUEST)
                    bounding_box = linestring.buffer(0.045)# for line i have add 5km distance
                    print("bounding_boxBuffer:- ",bounding_box)
                    filtered_coordinates = MarsBoundsCoordinates.objects.filter(
                        Q(COOD_XX__range=(bounding_box.bounds[0], bounding_box.bounds[2])) &
                        Q(COOD_YY__range=(bounding_box.bounds[1], bounding_box.bounds[3]))
                    )
                    print("filtered_coordinatesPoint 🧿 == ", filtered_coordinates)
                else:
                    return Response({"Message": "Error: Missing coordinates for LineString geometry"}, status=status.HTTP_400_BAD_REQUEST)

            elif geometry_type == 'Polygon':
                coordinates = CorrectAOI.get('coordinates')
                if coordinates:
                    try:
                        polygon = Polygon([(float(coord[0]), float(coord[1])) for coord in coordinates[0]])
                    except ValueError:
                        return Response({"Message": "Error: Invalid coordinates for Polygon geometry"}, status=status.HTTP_400_BAD_REQUEST)
                    bounding_box = polygon.buffer(0.045)# for polygon i have add 5km distance
                    print("bounding_boxBuffer:- ",bounding_box)
                    filtered_coordinates = MarsBoundsCoordinates.objects.filter(
                        Q(COOD_XX__range=(bounding_box.bounds[0], bounding_box.bounds[2])) &
                        Q(COOD_YY__range=(bounding_box.bounds[1], bounding_box.bounds[3]))
                    )
                    # filtered_coordinates = MarsBoundsCoordinates.objects.filter(
                    #     Q(COOD_XX__range=(polygon.bounds[0], polygon.bounds[2])) &
                    #     Q(COOD_YY__range=(polygon.bounds[1], polygon.bounds[3]))
                    # )
                    print("filtered_coordinates 🧿 == ",filtered_coordinates)
                else:
                    return Response({"Message": "Error: Missing coordinates for Polygon geometry"}, status=status.HTTP_400_BAD_REQUEST)            
            else:
                return Response({"Message": "Error: Invalid geometry type"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not filtered_coordinates:
                return Response({"Message": "Error: No data found for the Provided AOI"}, status=status.HTTP_404_NOT_FOUND)
            
            if CHAPTER is not None:
                # Extract location_code values from filtered coordinates
                # location_codes = filtered_coordinates.values_list('DATACODE', flat=True)
                # location_codes = [code.upper() for code in filtered_coordinates.values_list('DATACODE', flat=True)]
                location_codes = list(set([code.upper() for code in filtered_coordinates.values_list('DATACODE', flat=True)]))
                print("DATACODE :", location_codes)
                
                # First, filter based on DATACODE on MARSMAINTable to get all filter from MARSoordinates table
                filtered_datacode = MarsMainTableData.objects.filter(Q(DATACODE__in=location_codes))
                print("filtered_datacode :", filtered_datacode)
                
                
                # Then, filter the remaining entries based on the other conditions 
                Sensor_name_search = filtered_datacode.filter(
                    Q(COMP_NA__startswith=SUBJECT) and
                    Q(SEN_NAME__startswith=TOPIC) and
                    Q(SATT_NA__in=CHAPTER)
                )
                print("Filtered Sensor Names:", Sensor_name_search)
                # filter based on cloudCover
                if CLOUDCOVER is not None and CLOUDCOVER.strip():
                    print("Filtered by cloudCover =======", CLOUDCOVER)
                    cloudsearch = Sensor_name_search.filter(DCLOUD__startswith=CLOUDCOVER)
                    print("Filtered by cloudCover", cloudsearch)
                    band_information = MarsBandInformation.objects.filter(DATACODE__in=cloudsearch)
                    bounds_coordinates = MarsBoundsCoordinates.objects.filter(DATACODE__in=cloudsearch)
                else:
                    cloudsearch = None  
                print("Second ==================", cloudsearch)
                if SNOWCOVER is not None and SNOWCOVER.strip():
                    print("Filtered by SNOWCOVER ", SNOWCOVER)
                    snowsearch = Sensor_name_search.filter(DSNOW__startswith=SNOWCOVER)
                    band_information = MarsBandInformation.objects.filter(DATACODE__in=snowsearch)
                    bounds_coordinates = MarsBoundsCoordinates.objects.filter(DATACODE__in=snowsearch)
                    
                else:
                    snowsearch = None  
                print("THIRD ===================", snowsearch)
                if RESOLUTION is not None and RESOLUTION.strip():
                    print("Filtered by resolution ", RESOLUTION)
                    resolutionsearch = Sensor_name_search.filter(D_PIXELX__startswith=RESOLUTION)
                    band_information = MarsBandInformation.objects.filter(DATACODE__in=resolutionsearch)
                    bounds_coordinates = MarsBoundsCoordinates.objects.filter(DATACODE__in=resolutionsearch)
                else:
                    resolutionsearch = None  
                print("fourth ==================", resolutionsearch)
                if DATAPROCESSINGTYPE is not None and DATAPROCESSINGTYPE.strip():
                    print("Filtered by DATAPROCESSINGTYPE ", DATAPROCESSINGTYPE)
                    imgdatypesearch = Sensor_name_search.filter(IMG_DATYPE__startswith=DATAPROCESSINGTYPE)
                    band_information = MarsBandInformation.objects.filter(DATACODE__in=imgdatypesearch)
                    bounds_coordinates = MarsBoundsCoordinates.objects.filter(DATACODE__in=imgdatypesearch)
                else:
                    imgdatypesearch = None  
                print("five ====================", imgdatypesearch)
                if DATAINCIDENCEANGLE is not None and DATAINCIDENCEANGLE.strip():
                    print("Filtered by DATAINCIDENCEANGLE ", DATAINCIDENCEANGLE)
                    dinanglsearch = Sensor_name_search.filter(D_IN_ANGL__startswith=DATAINCIDENCEANGLE)
                    band_information = MarsBandInformation.objects.filter(DATACODE__in=dinanglsearch)
                    bounds_coordinates = MarsBoundsCoordinates.objects.filter(DATACODE__in=dinanglsearch)
                else:
                    dinanglsearch = None  
                print("sixth ===================", dinanglsearch)
            
            MainTable_combined_search = (imgdatypesearch or dinanglsearch or resolutionsearch or snowsearch or cloudsearch or Sensor_name_search).distinct()
            print("MainTable_combined_search 🎶🎉 ", MainTable_combined_search)
            # datacodes_list = [entry.DATACODE for entry in MainTable_combined_search]
            # print("datacodes_list ",datacodes_list)
            # for index, datacodenamee in enumerate(datacodes_list):
            #     print("datacodename:-",index,datacodenamee)

            # Extracting DATACODE from MainTable_combined_search
            datacodes_list = MainTable_combined_search.values_list('DATACODE', flat=True)
            print("datacodes_list ",datacodes_list)
            band_information = MarsBandInformation.objects.filter(DATACODE__in=datacodes_list)
            print("band_information 🎶🎉 ", band_information)
            # Filter MarsBoundsCoordinates using the same query
            bounds_coordinates = MarsBoundsCoordinates.objects.filter(DATACODE__in=datacodes_list)
            print("bounds_coordinates 🎶🎉 ", bounds_coordinates)
            maintabledat = MarsMainTableDataSerializer(MainTable_combined_search, many=True).data
            # print("maintabledat ",maintabledat)
            bandtabledata = MarsBandInformationSerializer(band_information, many=True).data
            # print("bandtabledata ",bandtabledata)
            boundstabledata = MarsBoundsCoordinatesSerializer(bounds_coordinates, many=True).data
            # print("boundstabledata ",boundstabledata)
            datacodes_set = set(datacodes_list)
            print("datacodes_set ",datacodes_set)

            # Initialize empty lists to store organized data
            maintabledat_serial = []
            bandtabledata_serial = []
            boundstabledata_serial = []

            # Iterate over data in maintabledat and match with datacodes_list
            # for entry in maintabledat:
            #     if entry['DATACODE'] in datacodes_set:
            #         maintabledat_serial.append(entry)

            # # Iterate over data in bandtabledata and match with datacodes_list
            # for entry in bandtabledata:
            #     if entry['DATACODE'] in datacodes_set:
            #         bandtabledata_serial.append(entry)

            # # Iterate over data in boundstabledata and match with datacodes_list
            # for entry in boundstabledata:
            #     if entry['DATACODE'] in datacodes_set:
            #         boundstabledata_serial.append(entry)

            # print("maintabledat_serial:", maintabledat_serial)
            # print("bandtabledata_serial:", bandtabledata_serial)
            # print("boundstabledata_serial:", boundstabledata_serial)
            # for item in maintabledat_serial:
            #     print("1:-",item["DATACODE"])
            
            # for index,item in enumerate(bandtabledata_serial):
            #     print("2:-",item["DATACODE"],index)

            # for index,item in enumerate(boundstabledata_serial):
            #     print("3:-",item["DATACODE"],index)
            for entry in maintabledat:
                if entry['DATACODE'] in datacodes_set:
                    maintabledat_serial.append(entry)
                    data_code = entry['DATACODE']
                    # Find corresponding entries in bandtabledata
                    for band_entry in bandtabledata:
                        if band_entry['DATACODE'] == data_code:
                            bandtabledata_serial.append(band_entry)
                    # Find corresponding entries in boundstabledata
                    for bound_entry in boundstabledata:
                        if bound_entry['DATACODE'] == data_code:
                            boundstabledata_serial.append(bound_entry)
            # print("maintabledat_serial:", maintabledat_serial)
            # print("bandtabledata_serial:", bandtabledata_serial)
            # print("boundstabledata_serial:", boundstabledata_serial)




            combined_data = {
                # 'marsmaintabledata': maintabledat,
                # 'marsbandsinformation': bandtabledata,
                # 'marsboundsinfromation': boundstabledata,
                'marsmaintabledata': maintabledat_serial,
                'marsbandsinformation': bandtabledata_serial,
                'marsboundsinfromation': boundstabledata_serial,
                # 'marsbandsinformation': ordered_band_data,
                # 'marsboundsinfromation': ordered_bounds_data,
            }

            return JsonResponse({'message': 'Data received successfully','Data':combined_data})
        except Exception as e:
            print(f'Error data: {str(e)}')
            return JsonResponse({'message': f'Error data: {str(e)}'}, status=500)
    return JsonResponse({'message': 'Invalid request method'}, status=400)