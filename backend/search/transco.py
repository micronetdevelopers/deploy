# =========================================================================================
# STAND_CHECKING_GUI.py
# =========================================================================================
# The script to perform the quality checking os the TRANSCO database as per the prescribed
# standards. It check the domain tables, its description and the coded values and descr.
# It check the FD, FC, its fields, data structure. It also checks all the addational data
# tables, its fields and data structure. The writes report in the text file in geodatabase
# directory as 'STANDARD_QC_REPORT.TXT'
# =========================================================================================
# Authors: Mr. Ashish Kumar Sharma & Dr. Subrata N. Das
# Main program initiated  : 29/3/22, 09/5/2022,
# =========================================================================================
# Palash D Patil i used the osgeo, GDAL, OGR instend of arcpy in this script to perform -
# the quality checking
# =========================================================================================
# To install GDAL in VENV python download wheel file using this link -
# https://github.com/cgohlke/geospatial-wheels/releases
# first check version of python and download as per the python version
# activate and VENV and install like pip install <wheel>
# =========================================================================================


from __future__ import print_function
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
import xml.etree.ElementTree as ET
import json
from osgeo import ogr
from osgeo import gdal
import datetime
import shutil
import sys
import os
import osgeo
print("OSGEO VERSION -", osgeo.__version__)
# =========================================================================================


@api_view(['POST'])
def upload_gdb(request):
    try:
        if request.method == 'POST':
            GdbFolderPath = request.data.get('GdbFolderPath')
            print("GdbFolderPath -", GdbFolderPath)
            OutputFolderPath = request.data.get('OutputFolderPath')
            print("OutputFolderPath -", OutputFolderPath)

            # Enable exceptions
            ogr.UseExceptions()

            # Open the GDB
            gdb = ogr.Open(GdbFolderPath)
            print("gdb ", gdb)
            if gdb is None:
                return JsonResponse({'error': 'Failed to open GDB'})
            
            # Set the output directory
            output_dir = os.path.join(
                OutputFolderPath, "TRANSCO_STANDARD_QC_REPORT")
            os.makedirs(output_dir, exist_ok=True)

            # SETTING THE Dictionary of DOMAIN TABLES
            DOMNAMEdict = {
                "SSTYPEDO": "Substation Type",
                "EGENTYPEDO": "Electric Generation Type",
                "CONDUTYPEDO": "Conductor Type",
                "CONDUMATLDO": "Conductor Material Type",
                "STRANDNAMEDO": "Conductor Strand Name",
                "TLTYPEDO": "Transmission Line Type",
                "BUNDLETYPEDO": "Conductor Bundle Type",
                "EARTHWIRETYDO": "Earth Wire Type",
                "VOLTRATEDO": "Voltage Rating",
                "VOLTLEVELDO": "Voltage Level",
                "DISTRUSYSDO": "Distribution System",
                "STATUSDO": "Operational Status",
                "COMSOURDO": "Communication Source",
                "TODESIGNDO": "Tower Design Type",
                "TOTYPEDO": "Tower Type",
                "TOCONFIGDO": "Tower Configuration",
            }
            # "TSTOTYPEDO":"TRANSCO Tower Types"
            # #SETTING Dictionary for the SSTYPEDO domain table CODES & ATTRIBUTES
            SSTYPEDOdict = {
                "SUBS": "Substation",
                "GNSS": "Generation Substation",
                "CONS": "Consumer Substation",
                "DISS": "Distribution Substation",
                "COSS": "Collector Substation",
                "SWSS": "Switching Substation",
                "RLSS": "Railway Substation",
                "CVSS": "Converter Substation",
                "LISS": "Lift Irrigation Substation",
                "WWSS": "Water Works Substation",
                "GISS": "Gas Insulated Substation",
                "MOSS": "Mobile Substation",
                "OTSS": "Other Substation"
            }
            # #SETTING Dictionary for the EGENTYPEDO domain table CODES & ATTRIBUTES
            EGENTYPEDOdict = {
                "TPP": "Thermal Power Station",
                "NPP": "Nuclear Power Plant",
                "HPP": "Hydroelectric Power Plant",
                "CFP": "Coal-fired Power Plant (Thermal)",
                "DFP": "Diesel-fired Power Plant",
                "BPP": "Biomass Power Plant",
                "GTP": "Geothermal Power Plant",
                "GPP": "Gas Power Plant",
                "SPP": "Solar Power Plant",
                "STP": "Solar Thermal Power Plant",
                "WPP": "Wind Power Plant",
                "TPP": "Tidal Power Plant",
                "CCP": "Combined-cycle Power Plant",
                "CHP": "COGEN Power Plant (Combine Heat & Power)",
                "IPP": "Independent Power Plant",
                "CPP": "Captive Power Plant",
                "NAP": "Not Applicable",
                "OPP": "Other Power Plant",
            }
            # #SETTING Dictionary for the CONDUTYPEDO domain table CODES & ATTRIBUTES
            CONDUTYPEDOdict = {
                "01": "Solid Conductor",
                "02": "Hollow Conductor",
                "03": "Stranded Conductor",
                "04": "Composite Stranded Conductor (ACSR)",
                "05": "Bundled Conductors",
                "09": "Unknown",
            }
            # #SETTING Dictionary for the CONDUMATLDO domain table CODES & ATTRIBUTES
            CONDUMATLDOdict = {
                "AAC": "AAC(All Aluminium Conductor)",
                "ACAR": "ACAR(All Aluminium Conductor, Aluminium Reinforce)",
                "AAAC": "AAAC(All Aluminium Alloy Conductor)",
                "ACSR": "ACSR(Aluminium Conductor Steel Reinforced)",
                "HTLS": "HTLS(High Tension Low Sag)",
                "IACS": "IACS(International Annealed Copper Stand)",
            }
            # #SETTING Dictionary for the TLTYPEDO domain table CODES & ATTRIBUTES
            TLTYPEDOdict = {
                "ACOH": "AC:Overhead",
                "ACUG": "AC:Underground Cable",
                "DCOH": "DC:Overhead",
                "DCUG": "DC:Underground Cable",
                "ACUW": "AC:Underwater",
                "DCUW": "DC:Underwater",
                "OTRT": "Other Transmission Type",
            }
            # #SETTING Dictionary for the BUNDLETYPEDO domain table CODES & ATTRIBUTES
            BUNDLETYPEDOdict = {
                "01": "Single(1)",
                "02": "Twin(2)",
                "03": "Triple(3)",
                "04": "Quad(4)",
                "06": "Hextuple(6)",
                "08": "Octa(8)",
                "09": "Unknown",
            }
            # #SETTING Dictionary for the VOLTRATEDO domain table CODES & ATTRIBUTES
            VOLTRATEDOdict = {
                "Z": "1200kV",
                "L": "765kV",
                "K": "500kV",
                "J": "400kV",
                "H": "220kV",
                "G": "132kV",
                "F": "110kV",
                "E": "100kV",
                "D": "66kV",
                "U": "Unknown",
            }
            # #SETTING Dictionary for the VOLTLEVELDO domain table CODES & ATTRIBUTES
            VOLTLEVELDOdict = {
                "01": "400/220/132/33 kV",
                "02": "400/220/132 kV",
                "03": "400/220/ kV",
                "04": "400/13.8 kV",
                "05": "400/11 kV",
                "06": "220/6.6 kV",
                "07": "220/33 kV",
                "08": "220/132 kV",
                "09": "220/11 kV",
                "10": "132/33 kV",
                "11": "132/11 kV",
                "99": "Unknown",
            }
            # #SETTING Dictionary for the DISTRUSYSDO domain table CODES & ATTRIBUTES
            DISTRUSYSDOdict = {
                "01": "Radial Connected",
                "02": "Grid Connected",
                "03": "Ring Main Connected",
                "04": "Mesh Network",
                "09": "Unknown",
            }
            # #SETTING Dictionary for the STATUSDO domain table CODES & ATTRIBUTES
            STATUSDOdict = {
                "01": "Operational",
                "02": "Temporary Out-of-Order",
                "03": "Abandoned",
                "04": "Under Maintenance",
                "05": "Under Construction",
                "09": "Unknown",
            }
            # #SETTING Dictionary for the COMSOURDO domain table CODES & ATTRIBUTES
            COMSOURDOdict = {
                "01": "TRANSCO OFC(Optical Fiber Cable)",
                "02": "PLCC(Power Line Carrier Communication)",
                "03": "OFC+PLCC",
                "04": "Leased Line",
                "08": "Not Available",
                "09": "Unknown",
            }
            # #SETTING Dictionary for the TOTYPEDO domain table CODES & ATTRIBUTES
            TOTYPEDOdict = {
                "01": "Bi-Pole Tower",
                "02": "Suspension Tower",
                "03": "Tension Tower",
                "04": "Mono Pole Suspension",
                "05": "Mono Pole Tension",
                "06": "Transposition Tower",
                "07": "Dead-end Tower",
                "09": "Unknown",
            }
            # #SETTING Dictionary for the TOCONFIGDO domain table CODES & ATTRIBUTES
            TOCONFIGDOdict = {
                "01": "Horizontal",
                "02": "Vertical",
                "03": "Triangular",
                "09": "Unknown",
            }
            # #SETTING Dictionary for the TODESIGNDO domain table CODES & ATTRIBUTES
            TODESIGNDOdict = {
                "01": "Single Circuit",
                "02": "Double Circuit",
                "03": "Multi Circuit",
                "04": "XPLE Cable",
                "09": "Unknown",
            }
            # #SETTING Dictionary for the EGENTYPEDO domain table CODES & ATTRIBUTES
            TSTOTYPEDOdict = {
                "01": "Horizontal",
                "02": "Vertical",
                "03": "Triangular",
                "09": "Unknown",
            }
            # #SETTING Dictionary for the EGENTYPEDO domain table CODES & ATTRIBUTES
            STRANDNAMEDOdict = {
                "01": "Ant",
                "02": "Squirrel",
                "03": "Racoon",
                "04": "Coyote",
                "05": "Tiger",
                "06": "Fox",
                "07": "Weasel",
                "08": "Rabbit",
                "09": "Dog",
                "10": "Wolf",
                "11": "Panther",
                "12": "Zebra",
                "13": "Moose",
                "14": "Bear",
                "15": "Lynx",
                "16": "Drake",
                "17": "Deer",
                "18": "Panther and Lynx",
                "19": "Panther and Zebra",
                "20": "Panther and Moose",
                "21": "Panther and Wolf",
                "22": "Panther and Bear",
                "23": "Zebra and Moose",
                "24": "Zebra and Deer",
                "99": "Unknown",
            }
            # #SETTING Dictionary for the EGENTYPEDO domain table CODES & ATTRIBUTES
            EARTHWIRETYDOdict = {
                "01": "OPGW (Optical Ground Wire)",
                "02": "Earth Wire",
                "03": "Earth Wire & OPGW",
            }
            
            # **************************************************************************
            # Function Definition : WRITEFILELINE (text)
            # **************************************************************************

            def writefileline(text):
                # ---OPEN------
                file1 = open(txtFileName, "a")
                # ---APPEND----
                file1.write(text)
                # ---CLOSE-----
                file1.close()
            # ------------------------------------ END of FUNCTIONS-----------------------------------------------------
            # **************************************************************************
            # ********************** F U N C T I O N S *********************************
            # **************************************************************************
            # **************************************************************************
            # Function Definition : COMPARE_STRINGS(Original_string, compare_string)
            # **************************************************************************

            def compare_strings(org1, err5):
                vallen = 0
                if org1 != err5:
                    if len(org1) >= len(err5):
                        vallen = len(org1)
                    if len(org1) <= len(err5):
                        vallen = len(err5)
                thevar = ""
                for i in range(vallen):
                    if i + 1 <= len(org1):
                        e1 = org1[i]
                    else:
                        e1 = "~"
                    if i + 1 <= len(err5):
                        e2 = err5[i]
                    else:
                        e2 = "~"
                    if e1 != e2:
                        thevar = thevar + "[" + e1 + "[" + str(i + 1) + "],"
                writefileline(
                    "     Error at [word[location],]....= ["+thevar+"] \n")
                print("Error at [word[location],]....= [" + thevar + "]")
            # ------------------------------------ END of FUNCTIONS-----------------------------------------------------
            # **************************************************************************
            # Function Definition : CHECKFC (Feature datasets)
            # **************************************************************************


            def checkfc(fds):
                try:
                    TTASSETFDdict = {
                        "TT_SS_LOCA": "Substation Location",
                        "TT_SS_BOUND": "Substation Outer Boundary",
                        "TT_TLINES": "Transmission Line",
                        "TT_TLTOWERS": "Transmission Towers",
                    }

                    TSADMINFDdict = {
                        "TSADMINPO": "Administration Boundary",
                        "TS_STATE": "State Boundary",
                        "TS_DISTRICT": "District Boundary",
                        "TS_MANDAL": "Mandal Boundary",
                        "TTADMINPO": "TSTRANSCO Administration Jurisdiction",
                        "TT_ZONE": "Zone Jurisdiction",
                        "TT_CIRCLE": "Circle Jurisdiction",
                        "TT_DIVISION": "Division Jurisdiction",
                    }

                    TT_TLTOWERS_list = [["TOCODE", "String", "8", "", "True"],
                                        ["TO_LAT", "Single", "4", "", "True"],
                                        ["TO_LONG", "Single", "4", "", "True"],
                                        ["TL1CODE", "String", "19", "", "True"],
                                        ["TL2CODE", "String", "19", "", "True"],
                                        ["TL3CODE", "String", "19", "", "True"],
                                        ["TL4CODE", "String", "19", "", "True"],
                                        ["TL5CODE", "String", "19", "", "True"],
                                        ["TL6CODE", "String", "19", "", "True"],
                                        ["TL1NAME", "String", "80", "", "True"],
                                        ["TL2NAME", "String", "80", "", "True"],
                                        ["TL3NAME", "String", "80", "", "True"],
                                        ["TL4NAME", "String", "80", "", "True"],
                                        ["TL5NAME", "String", "80", "", "True"],
                                        ["TL6NAME", "String", "80", "", "True"],
                                        ["TO_REM", "String", "100", "", "True"]]

                    TT_TLINES_list = [["TLID", "String", "6", "", "True"],
                                    ["TL1CODE", "String", "19", "", "True"],
                                    ["TL2CODE", "String", "19", "", "True"],
                                    ["TL3CODE", "String", "19", "", "True"],
                                    ["TL4CODE", "String", "19", "", "True"],
                                    ["TL5CODE", "String", "19", "", "True"],
                                    ["TL6CODE", "String", "19", "", "True"],
                                    ["TL1NAME", "String", "80", "", "True"],
                                    ["TL2NAME", "String", "80", "", "True"],
                                    ["TL3NAME", "String", "80", "", "True"],
                                    ["TL4NAME", "String", "80", "", "True"],
                                    ["TL5NAME", "String", "80", "", "True"],
                                    ["TL6NAME", "String", "80", "", "True"],
                                    ["TLTYPE", "String", "4", "TLTYPEDO", "True"],
                                    ["TL_REM", "String", "100", "", "True"]]

                    TT_SS_LOCA_list = [["SSCODE", "String", "5", "", "False"],
                                    ["SS_NAME", "String", "50", "", "True"],
                                    ["SS_OWNER", "String", "50", "", "True"],
                                    ["SS_FULLNA", "String", "100", "", "True"],
                                    ["SS_STATUS", "String", "2", "STATUSDO", "True"],
                                    ["SS_TYPE", "String", "4", "SSTYPEDO", "True"],
                                    ["VOLT_LEVEL1", "String", "2",
                                        "VOLTLEVELDO", "True"],
                                    ["VOLT_LEVEL2", "String", "2",
                                        "VOLTLEVELDO", "True"],
                                    ["VOLT_LEVEL3", "String", "2",
                                        "VOLTLEVELDO", "True"],
                                    ["VOLT_LEVEL4", "String", "2",
                                        "VOLTLEVELDO", "True"],
                                    ["MIN_VOLTAGE", "SmallInteger", "2", "", "True"],
                                    ["MAX_VOLTAGE", "SmallInteger", "2", "", "True"],
                                    ["SS_LAT", "Single", "4", "", "True"],
                                    ["SS_LONG", "Single", "4", "", "True"],
                                    ["SS_REM", "String", "100", "", "True"]]

                    TT_SS_BOUND_list = [["SSCODE", "String", "5", "", "False"],
                                        ["SS_NAME", "String", "50", "", "True"],
                                        ["SS_OWNER", "String", "50", "", "True"],
                                        ["SS_FULLNA", "String", "100", "", "True"],
                                        ["SS_STATUS", "String", "2", "STATUSDO", "True"],
                                        ["SS_TYPE", "String", "4", "SSTYPEDO", "True"],
                                        ["SS_REM", "String", "100", "", "True"]]

                    TSADMINPO_list = [["TSADCODE", "String", "10", "", "True"],
                                    ["STNCODE", "String", "2", "", "True"],
                                    ["DTNCODE", "String", "2", "", "True"],
                                    ["MANCODE", "String", "4", "", "True"],
                                    ["GPCODE", "String", "6", "", "True"],
                                    ["VINCODE", "String", "6", "", "True"],
                                    ["VIL_NAME", "String", "40", "", "True"]]

                    TS_STATE_list = [["STNCODE", "String", "2", "", "False"],
                                    ["STNAME", "String", "50", "", "True"]]

                    TS_DISTRICT_list = [["DTNCODE", "String", "2", "", "True"],
                                        ["DTNAME", "String", "50", "", "True"]]

                    TS_MANDAL_list = [["MANCODE", "String", "4", "", "True"],
                                    ["MANNAME", "String", "50", "", "True"]]

                    TTADMINPO_list = [["TTADCODE", "String", "6", "", "True"],
                                    ["TTZONECO", "String", "2", "", "True"],
                                    ["TTCIRCO", "String", "4", "", "True"],
                                    ["TTDIVNCO", "String", "6", "", "True"]]

                    TT_ZONE_list = [["TTZONECO", "String", "2", "", "True"],
                                    ["TTZONENA", "String", "50", "", "True"]]

                    TT_CIRCLE_list = [["TTCIRCO", "String", "4", "", "True"],
                                    ["TTCIRNA", "String", "50", "", "True"]]

                    TT_DIVISION_list = [["TTDIVNCO", "String", "6", "", "True"],
                                        ["TTDIVNNA", "String", "50", "", "True"]]
                    fnmctr = "NOTOK"
                    ftyctr = "NOTOK"
                    flenctr = "NOTOK"
                    fdomctr = "NOTOK"
                    fnullctr = "NOTOK"
            
                    FCDICName_list = []
                    DICnm = eval(fds+"dict")
            
                    for x, y in DICnm.items():
                        fcnm = x
                        FCDICName_list.append(fcnm.strip())
                    print("FCDICName_list: ", FCDICName_list)
            
                    # Get the GDB_Items table
                    gdb_items = gdb.GetLayer('GDB_Items')
                    # Initialize an empty dictionary to store feature dataset names and their corresponding feature classes
                    feature_dataset_classes = {}
                    featureclasses = []
            
                    # Loop through the GDB_Items table
                    for item in gdb_items:
                        item_json = json.loads(item.ExportToJson())
                        definition = item_json['properties']['Definition']
                        if definition:
                            xml = ET.fromstring(definition)
                            print("xml ", xml)
                            if xml.tag == 'DEFeatureDataset':
                                feature_dataset_name = xml.find('Name').text
                                feature_dataset_classes[feature_dataset_name] = []
                            elif xml.tag == 'DEFeatureClassInfo':
                                feature_class_name = xml.find('Name').text
                                feature_dataset_classes[feature_dataset_name].append(
                                    feature_class_name)
            
                    # Print the feature dataset names and their corresponding feature classes
                    for feature_dataset_name, feature_classes in feature_dataset_classes.items():
                        print(f"Feature Dataset: {feature_dataset_name}")
                        for feature_class in feature_classes:
                            featureclasses.append(feature_class)
                            print(f"  - {feature_class}")
            
                    for fc in featureclasses:
                        fcna = '{0}'.format(fc)
                        print("fcna 🌮", fcna)
                        # fcna = feature.GetField("Name")
                        if fcna:
                            txt1 = "FEATURE DATASET  = " + str(fds)
                            txt2 = txt1.ljust(77, "-")
                            writefileline(txt2+"OK \n")
                            writefileline(
                                "  ================================================================================== \n")
                            print(txt2 + "OK")
                            print(
                                "  ==================================================================================")
                            fields = gdb.GetLayerByName(
                                fcna).GetLayerDefn().GetFieldCount()
            
                            thelist = eval(fcna + "_list")
                            for i in range(len(thelist)):
                                fnm0 = thelist[i][0]
                                fty0 = thelist[i][1]
                                flen0 = thelist[i][2]
                                fdom0 = thelist[i][3]
                                fnull0 = thelist[i][4]
            
                                for j in range(fields):
                                    field = gdb.GetLayerByName(
                                        fcna).GetLayerDefn().GetFieldDefn(j)
                                    pnm = ""
                                    pty = ""
                                    plen = ""
                                    pdom = ""
                                    pull = ""
                                    fnm1 = field.GetName()
                                    fty1 = field.GetTypeName()
                                    flen1 = field.GetWidth()
                                    fdom1 = field.GetDomainName()
                                    fnull1 = field.IsNullable()
            
                                    if (fnm0 == fnm1):
                                        fnmctr = "     " + fnm0 + "(Name)"
                                        txt2 = fnmctr.ljust(77, "-")
                                        writefileline(txt2+"OK \n")
                                        print(txt2 + "OK")
                                        testf = fnm0
            
                                        if (fty0 == fty1):
                                            ftyctr = "     " + fnm0 + "(Type)"
                                            txt2 = ftyctr.ljust(77, "-")
                                            writefileline(txt2+"OK \n")
                                            print(txt2 + "OK")
                                        else:
                                            ftyctr = "     " + fnm0 + "(Type)"
                                            txt2 = ftyctr.ljust(77, "-")
                                            writefileline(txt2+"NOTOK \n")
                                            print(txt2 + "NOTOK")
            
                                        if (flen0 == flen1):
                                            flenctr = "     " + fnm0 + "(Length)"
                                            txt2 = flenctr.ljust(77, "-")
                                            writefileline(txt2+"OK \n")
                                            print(txt2 + "OK")
                                        else:
                                            flenctr = "     " + fnm0 + "(Length)"
                                            txt2 = flenctr.ljust(77, "-")
                                            writefileline(txt2+"NOTOK \n")
                                            print(txt2 + "NOTOK")
            
                                        if (fdom0 == fdom1):
                                            fdomctr = "     " + fnm0 + "(Domain)"
                                            txt2 = fdomctr.ljust(77, "-")
                                            writefileline(txt2+"OK \n")
                                            print(txt2 + "OK")
                                        else:
                                            fdomctr = "     " + fnm0 + "(Domain)"
                                            txt2 = fdomctr.ljust(77, "-")
                                            writefileline(txt2+"NOTOK \n")
                                            print(txt2 + "NOTOK")
            
                                        if (fnull0 == fnull1):
                                            fnullctr = "     " + fnm0 + "(Nullable)"
                                            txt2 = fnullctr.ljust(77, "-")
                                            writefileline(txt2+"OK \n")
                                            print(txt2 + "OK")
                                        else:
                                            fnullctr = "     " + fnm0 + "(Nullable)"
                                            txt2 = fnullctr.ljust(77, "-")
                                            writefileline(txt2+"NOTOK \n")
                                            print(txt2 + "NOTOK")
            
                                    else:
                                        testf = fnm0
            
                                if fnmctr == "NOTOK":
                                    txt1 = "     " + fnm0 + "(Name)"
                                    txt2 = txt1.ljust(77, "-")
                                    writefileline(txt2+"DNE \n")
                                    print(txt2 + "DNE")
            
                                fnmctr = "NOTOK"
                                ftyctr = "NOTOK"
                                flenctr = "NOTOK"
                                fdomctr = "NOTOK"
                                fnullctr = "NOTOK"
                                testf = ""
                                writefileline(" \n")
                                writefileline(
                                    "  ---------------------------------------------------------------------------------- \n")
                                print(" ")
                                print(
                                    "  ----------------------------------------------------------------------------------")
                        else:
                            txt1 = "FEATURE DATASET  = " + str(fds)
                            txt2 = txt1.ljust(77, "-")
                            writefileline(txt2+"NOTOK \n")
                            writefileline(
                                "  ================================================================================== \n")
                            print(txt2 + "NOTOK")
                            print(
                                "  ==================================================================================")
            
                    writefileline(
                        "===================================================================================== \n")
                    writefileline("=== ENDING FEARURE DATASET - "+str(fds.ljust(20,
                                " "))+"==================================== \n")
                    writefileline(" \n")
                    print("=====================================================================================")
                    print("=== ENDING FEARURE DATASET - " + str(fds.ljust(20, " ")) +
                        "====================================")
                    print(" ")
                except Exception as e:
                    print(f"An error occurred: {e}")

            # ------------------------------------ END of FUNCTIONS-----------------------------------------------------
            # CHECKING THE EXISTANCE OF THE OUTPUT TEXT FILE "'STANDARD_QC_REPORT.DAT"==============================
            # Setting the file name ---------------------------------------------------------------------------------
            txtFileName = output_dir + "//STANDARD_QC_REPORT.DAT"

            # deleting file, if exist--------------------------------------------------------------------------------
            if os.path.exists(txtFileName):
                os.remove(txtFileName)

            # Setting present date and time -------------------------------------------------------------------------
            now = datetime.datetime.now()
            dt = now.strftime("%d %B(%A), %Y   %H:%M:%S %p")

            # Writing to file through the function "WRITEFILELINE" --------------------------------------------------
            writefileline(
                "************************************************************************************* \n")
            writefileline(
                "                  TUPLE SOLUTIONS & MICRONET SOLUTIONS ENTERPRISE \n")
            writefileline(
                "************************************************************************************* \n")
            writefileline("                    " + str(dt) + "\n")
            writefileline(
                "************************************************************************************* \n")
            writefileline("\n")
            # CHECKING THE LIST OF DOMAIN TABLE AND ITS DESCRIPTION
            writefileline(
                "************************************************************************************* \n")
            writefileline(
                "***** EVALUATING THE DOMAIN TABLES IN THE GEODATABASE: ****************************** \n")
            writefileline(
                "************************************************************************************* \n")
            print(
                "*************************************************************************************")
            print(
                "***** EVALUATING THE DOMAIN TABLES IN THE GEODATABASE: ******************************")
            print(
                "*************************************************************************************")

            # Get the number of layers in the geodatabase
            ctr = 0
            idx = 0
            DOM_Name_List = []
            DOM_Desc_List = []
            res = gdb.ExecuteSQL('select * from GDB_Items')
            for i in range(0, res.GetFeatureCount()):
                item = res.GetNextFeature().ExportToJson()
                item_json = json.loads(item)
                definition = item_json['properties']['Definition']
                if definition:
                    xml = ET.fromstring(definition)
                    if xml.tag == 'GPCodedValueDomain2':
                        domain_name = xml.find('DomainName').text
                        description = xml.find('Description').text
                        # Append domain name and description to lists
                        DOM_Name_List.append(domain_name.strip())
                        DOM_Desc_List.append(description.strip())
                        ctr += 1
            writefileline(
                "      Total Existing Domains tables = " + str(ctr) + "\n")
            print("      Total Existing Domains tables = " + str(ctr))
            writefileline(
                "------------------------------------------------------------------------------------- \n")
            print(
                "=====================================================================================")
            # Setting a variable ------------------------------
            fctr = "NF"

            # Reading Domains from Dictionary---------------------------------
            DOMDICValue_list = []
            DOMDICDesc_list = []
            domainhai = 0

            for x, y in DOMNAMEdict.items():
                # print(x, y)
                cv = x
                cvdesc = y
                DOMDICValue_list.append(cv.strip())
                DOMDICDesc_list.append(cvdesc.strip())

            for i in range(len(DOMDICValue_list)):
                # *********************************************************************
                writefileline("TABLE-" + str(i+1) + "\n")
                print(" ")
                element = DOMDICValue_list[i]
                elemdesc = DOMDICDesc_list[i]

                if (element in DOM_Name_List):
                    text1 = "DOMAIN NAME  = "+element
                    textjust1 = text1.ljust(77, "-")
                    writefileline(textjust1+"OK \n")
                    print(textjust1+"OK")
                    domainhai = 1
                else:
                    text1 = "DOMAIN NAME  = "+element
                    textjust1 = text1.ljust(77, "-")
                    writefileline(textjust1+"NOTOK \n")
                    print(textjust1+"NOTOK")
                    domainhai = 0

                if (elemdesc in DOM_Desc_List):
                    text1 = "DOMAIN DESCR = "+elemdesc
                    textjust1 = text1.ljust(77, "-")
                    writefileline(textjust1+"OK \n")
                    print(textjust1+"OK")
                else:
                    text1 = "DOMAIN DESCR = "+elemdesc
                    textjust1 = text1.ljust(77, "-")
                    writefileline(textjust1+"NOTOK \n")
                    print(textjust1+"NOTOK")

                writefileline("  PARAMETERS: \n")
                print("  PARAMETERS:")

                # *************************************************************************

                if domainhai == 1:

                    # Make Coded Values List from the Dictionary
                    dictname = eval(element+"dict")
                    # print "Dictionary", dictname

                    allok = 0
                    CV_list = []
                    CVD_list = []
                    # print element
                    res1 = gdb.ExecuteSQL('select * from GDB_Items')
                    for i in range(0, res1.GetFeatureCount()):
                        item = res1.GetNextFeature().ExportToJson()
                        item_json = json.loads(item)
                        definition = item_json['properties']['Definition']
                        if definition:
                            xml = ET.fromstring(definition)
                            if xml.tag == 'GPCodedValueDomain2':
                                dn = xml.find('DomainName').text

                                # Compare domain name with element
                                if dn.strip() == element:
                                    coded_values = xml.find('CodedValues')
                                    codev_list = []
                                    codevdesc_list = []

                                    for coded_value in coded_values:
                                        code = coded_value.find('Code').text
                                        desc = coded_value.find('Name').text
                                        codev_list.append(code.strip())
                                        codevdesc_list.append(desc.strip())

                                    print("Domain Name:", dn)
                                    print("Coded Values:", codev_list)
                                    print("Descriptions:", codevdesc_list)

                                # print "GDB Domains"
                                # print codev_list
                                # print codevdesc_list

                    for x, y in dictname.items():
                        # print(x, y)
                        cv = x
                        cvdesc = y
                        if (cv in codev_list):
                            idx = codev_list.index(cv)
                            # print "       Code = ",cv,".......","OK"
                            pass
                        else:
                            allok = allok + 1
                            temp = "["+cv+"]"
                            codejust = temp.ljust(59, "-")
                            codejust1 = codejust+"NOTOK"
                            writefileline("    CODE        = " +
                                        codejust1 + "\n")
                            print("    CODE        = "+codejust1)
                        if (cvdesc in codevdesc_list):
                            pass
                            # print "       Description = ",cvdesc,".......","OK"
                        else:
                            allok = allok + 1
                            cdescrjust = cvdesc.ljust(59, "-")
                            cdescrjust1 = cdescrjust+"NOTOK"
                            writefileline("    Descr(Std.) = " +
                                        cdescrjust1 + "\n")
                            writefileline("    Descr(Dom.) = " +
                                        codevdesc_list[idx] + "\n")
                            print("    Descr(Std.) = "+cdescrjust1)
                            print("    Descr(Dom.) = "+codevdesc_list[idx])
                            o1 = cvdesc
                            e5 = codevdesc_list[idx]
                            compare_strings(o1, e5)
                    if allok == 0:
                        paratext = "----------------------------------------------All Parameters"
                        paratext1 = paratext.ljust(77, "-")
                        writefileline(paratext1+"OK \n")
                        print(paratext1+"OK")
            writefileline(
                "------------------------------------------------------------------------------------- \n")
            writefileline(" \n")
            writefileline(
                "************************************************************************************* \n")
            writefileline(
                "**********   DOMAIN TABLES SUCESSFULLY CHECKED ! ************************************ \n")
            writefileline(
                "************************************************************************************* \n")
            writefileline(" \n")
            print(" ")
            print(
                "*************************************************************************************")
            print(
                "**********  DOMAIN TABLES SUCESSFULLY CHECKED ! *************************************")
            print(
                "*************************************************************************************")
            print(" ")

            # **************************************************************************************************
            # **************************************************************************************************
            # *************FOR FEATURE DATASETS AND FEATURE CLASSES AND ITS FIELD ******************************
            # **************************************************************************************************
            # **************************************************************************************************
            # Make a list of all Feature Classes
            writefileline(" \n")
            writefileline(
                "************************************************************************************* \n")
            writefileline(
                "***** EVALUATING THE FEATURE DATASET, FEATURE CLASSES & ITS FIELDS:  **************** \n")
            writefileline(
                "************************************************************************************* \n")

            print(
                "*************************************************************************************")
            print(
                "***** EVALUATING THE FEATURE DATASET, FEATURE CLASSES & ITS FIELDS:  ****************")
            print(
                "*************************************************************************************")

            # Feature Datasets Dictionary-----------------------------------------------------------------
            FDdict = {
                "TTASSETFD": "Assets Dataset",
                "TSADMINFD": "Administration Datasets",
            }
            # TTASSETFDdict = {
            #     "TT_SS_LOCA": "Substation Location",
            #     "TT_SS_BOUND": "Substation Outer Boundary",
            #     "TT_TLINES": "Transmission Line",
            #     "TT_TLTOWERS": "Transmission Towers",
            # }

            # TSADMINFDdict = {
            #     "TSADMINPO": "Administration Boundary",
            #     "TS_STATE": "State Boundary",
            #     "TS_DISTRICT": "District Boundary",
            #     "TS_MANDAL": "Mandal Boundary",
            #     "TTADMINPO": "TSTRANSCO Administration Jurisdiction",
            #     "TT_ZONE": "Zone Jurisdiction",
            #     "TT_CIRCLE": "Circle Jurisdiction",
            #     "TT_DIVISION": "Division Jurisdiction",
            # }

            # TT_TLTOWERS_list = [["TOCODE", "String", "8", "", "True"],
            #                     ["TO_LAT", "Single", "4", "", "True"],
            #                     ["TO_LONG", "Single", "4", "", "True"],
            #                     ["TL1CODE", "String", "19", "", "True"],
            #                     ["TL2CODE", "String", "19", "", "True"],
            #                     ["TL3CODE", "String", "19", "", "True"],
            #                     ["TL4CODE", "String", "19", "", "True"],
            #                     ["TL5CODE", "String", "19", "", "True"],
            #                     ["TL6CODE", "String", "19", "", "True"],
            #                     ["TL1NAME", "String", "80", "", "True"],
            #                     ["TL2NAME", "String", "80", "", "True"],
            #                     ["TL3NAME", "String", "80", "", "True"],
            #                     ["TL4NAME", "String", "80", "", "True"],
            #                     ["TL5NAME", "String", "80", "", "True"],
            #                     ["TL6NAME", "String", "80", "", "True"],
            #                     ["TO_REM", "String", "100", "", "True"]]

            # TT_TLINES_list = [["TLID", "String", "6", "", "True"],
            #                   ["TL1CODE", "String", "19", "", "True"],
            #                   ["TL2CODE", "String", "19", "", "True"],
            #                   ["TL3CODE", "String", "19", "", "True"],
            #                   ["TL4CODE", "String", "19", "", "True"],
            #                   ["TL5CODE", "String", "19", "", "True"],
            #                   ["TL6CODE", "String", "19", "", "True"],
            #                   ["TL1NAME", "String", "80", "", "True"],
            #                   ["TL2NAME", "String", "80", "", "True"],
            #                   ["TL3NAME", "String", "80", "", "True"],
            #                   ["TL4NAME", "String", "80", "", "True"],
            #                   ["TL5NAME", "String", "80", "", "True"],
            #                   ["TL6NAME", "String", "80", "", "True"],
            #                   ["TLTYPE", "String", "4", "TLTYPEDO", "True"],
            #                   ["TL_REM", "String", "100", "", "True"]]

            # TT_SS_LOCA_list = [["SSCODE", "String", "5", "", "False"],
            #                    ["SS_NAME", "String", "50", "", "True"],
            #                    ["SS_OWNER", "String", "50", "", "True"],
            #                    ["SS_FULLNA", "String", "100", "", "True"],
            #                    ["SS_STATUS", "String", "2", "STATUSDO", "True"],
            #                    ["SS_TYPE", "String", "4", "SSTYPEDO", "True"],
            #                    ["VOLT_LEVEL1", "String", "2",
            #                        "VOLTLEVELDO", "True"],
            #                    ["VOLT_LEVEL2", "String", "2",
            #                        "VOLTLEVELDO", "True"],
            #                    ["VOLT_LEVEL3", "String", "2",
            #                        "VOLTLEVELDO", "True"],
            #                    ["VOLT_LEVEL4", "String", "2",
            #                        "VOLTLEVELDO", "True"],
            #                    ["MIN_VOLTAGE", "SmallInteger", "2", "", "True"],
            #                    ["MAX_VOLTAGE", "SmallInteger", "2", "", "True"],
            #                    ["SS_LAT", "Single", "4", "", "True"],
            #                    ["SS_LONG", "Single", "4", "", "True"],
            #                    ["SS_REM", "String", "100", "", "True"]]

            # TT_SS_BOUND_list = [["SSCODE", "String", "5", "", "False"],
            #                     ["SS_NAME", "String", "50", "", "True"],
            #                     ["SS_OWNER", "String", "50", "", "True"],
            #                     ["SS_FULLNA", "String", "100", "", "True"],
            #                     ["SS_STATUS", "String", "2", "STATUSDO", "True"],
            #                     ["SS_TYPE", "String", "4", "SSTYPEDO", "True"],
            #                     ["SS_REM", "String", "100", "", "True"]]

            # TSADMINPO_list = [["TSADCODE", "String", "10", "", "True"],
            #                   ["STNCODE", "String", "2", "", "True"],
            #                   ["DTNCODE", "String", "2", "", "True"],
            #                   ["MANCODE", "String", "4", "", "True"],
            #                   ["GPCODE", "String", "6", "", "True"],
            #                   ["VINCODE", "String", "6", "", "True"],
            #                   ["VIL_NAME", "String", "40", "", "True"]]

            # TS_STATE_list = [["STNCODE", "String", "2", "", "False"],
            #                  ["STNAME", "String", "50", "", "True"]]

            # TS_DISTRICT_list = [["DTNCODE", "String", "2", "", "True"],
            #                     ["DTNAME", "String", "50", "", "True"]]

            # TS_MANDAL_list = [["MANCODE", "String", "4", "", "True"],
            #                   ["MANNAME", "String", "50", "", "True"]]

            # TTADMINPO_list = [["TTADCODE", "String", "6", "", "True"],
            #                   ["TTZONECO", "String", "2", "", "True"],
            #                   ["TTCIRCO", "String", "4", "", "True"],
            #                   ["TTDIVNCO", "String", "6", "", "True"]]

            # TT_ZONE_list = [["TTZONECO", "String", "2", "", "True"],
            #                 ["TTZONENA", "String", "50", "", "True"]]

            # TT_CIRCLE_list = [["TTCIRCO", "String", "4", "", "True"],
            #                   ["TTCIRNA", "String", "50", "", "True"]]

            # TT_DIVISION_list = [["TTDIVNCO", "String", "6", "", "True"],
            #                     ["TTDIVNNA", "String", "50", "", "True"]]

            # Setting the geoprocessing environment to the GDB path ------------------------------------
            fdatasets = []
            res2 = gdb.ExecuteSQL('select * from GDB_Items')
            for i in range(0, res2.GetFeatureCount()):
                item = res2.GetNextFeature().ExportToJson()
                item_json = json.loads(item)
                definition = item_json['properties']['Definition']
                if definition:
                    xml = ET.fromstring(definition)
                    # print("xml ",xml)
                    if xml.tag == 'DEFeatureDataset':
                        fdatasets_name = xml.find('Name').text
                        fdatasets.append(fdatasets_name)

            print("FEATURE DATASETS  = " + str(fdatasets))

            # Setting few variables -------------------------------------------------------------------
            fnmctr = "NOTOK"
            ftyctr = "NOTOK"
            flenctr = "NOTOK"
            fdomctr = "NOTOK"
            fnullctr = "NOTOK"
            testf = ""
            foundctr = 0

            # Checking the existance of the FC in the WORKSPACE-----------------------------------------
            FDDICName_list = []
            for x, y in FDdict.items():
                fdnm = x
                FDDICName_list.append(fdnm.strip())

            writefileline(" \n")
            writefileline("FEATURE DATASET QUALITY CHECKING: \n")
            writefileline(
                "===================================================================================== \n")
            print(" ")
            print("FEATURE DATASET QUALITY CHECKING:  ")
            print(
                "=====================================================================================")

            for i in range(len(FDDICName_list)):
                dstnm = FDDICName_list[i]

                for dataset in fdatasets:
                    ds = '{0}'.format(dataset)
                    if (ds in dstnm.strip()):
                        foundctr = 1

                # Print the result
                if foundctr == 1:
                    txt1 = "FEATURE DATASET  = "+str(dstnm)
                    txt2 = txt1.ljust(77, "-")
                    print(txt2+"OK")

                if foundctr == 0:
                    txt1 = "FEATURE DATASET  = "+str(dstnm)
                    txt2 = txt1.ljust(77, "-")
                    print(txt2+"NOTOK")

                foundctr = 0
            writefileline(
                "===================================================================================== \n")
            writefileline(" \n")
            print(
                "=====================================================================================")
            print(" ")

            writefileline(" \n")
            writefileline("FEATURE CLASS QUALITY CHECKING: \n")
            writefileline(
                "===================================================================================== \n")
            print(" ")
            print("FEATURE CLASS QUALITY CHECKING:  ")
            print(
                "=====================================================================================")

            for i in range(len(FDDICName_list)):
                dstnm = FDDICName_list[i]

                # Check if the feature dataset exists in the geodatabase
                for dataset in fdatasets:
                    ds = '{0}'.format(dataset)
                    if (ds in dstnm.strip()):
                        writefileline("FEATURE DTATSET : " + str(ds)+" \n")
                        writefileline(
                            "------------------------------------------------------------------------------------- \n")
                        print("FEATURE DATASET : " + str(ds))
                        print(
                            "-------------------------------------------------------------------------------------")
                        foundctr = 1

                # Call the checkfc function if the feature dataset exists
                if foundctr == 1:
                    print("dstnm 🎀", dstnm)
                    checkfc(dstnm)

                foundctr = 0

            writefileline(" \n")
            writefileline(
                "************************************************************************************* \n")
            writefileline(
                "****** FEATURE DATASETS, FEATURE CLASSES & ITS FIELDS SUCESSFULLY CHECKED ! ********* \n")
            writefileline(
                "************************************************************************************* \n")
            writefileline(" \n")
            print(" ")
            print(
                "*************************************************************************************")
            print(
                "****** FEATURE DATASETS, FEATURE CLASSES & ITS FIELDS SUCESSFULLY CHECKED ! *********")
            print(
                "*************************************************************************************")
            print(" ")

            # **************************************************************************************************
            # **************************************************************************************************
            # *************FOR ATTRIBUTE DATA TABLES (OBJECT TABLES) AND ITS FIELDS ****************************
            # **************************************************************************************************
            # **************************************************************************************************

            writefileline(" \n")
            writefileline(
                "************************************************************************************* \n")
            writefileline(
                "***** EVALUATING THE ATTRIBUTE DATA TABLES & ITS FIELDS:  *************************** \n")
            writefileline(
                "************************************************************************************* \n")
            print(" ")
            print(
                "*************************************************************************************")
            print(
                "***** EVALUATING THE ATTRIBUTE DATA TABLES & ITS FIELDS:  ***************************")
            print(
                "*************************************************************************************")

            # Tables Dictionary------------------------------------------------------------------------------------
            TABLESdict = {
                "TL_INFO": "Transmission Line Information",
                "STRAND_CODU_INFO": "Stranded conductor specification information",
                "SS_BASIC_INFO": "Substation Basic information",
                "SS_CONTACT_INFO": "Substation In-charge/Office Contact information",
                "SS_PTR_INFO": "Substation Power Transformation information",
                "SS_DTR_INFO": "Substation Distribution Transformation information",
                "SS_SR_INFO": "Shunt Reactor information",
                "SS_CAPBANK_INFO": "Substation Capacitor Bank information",
                "TT_TLTOWERS_INFO": "Tower other basic information",
            }

            # Setting some variables ----------------------------------------------------------------------------
            fnmctr = "NOTOK"
            ftyctr = "NOTOK"
            flenctr = "NOTOK"
            fdomctr = "NOTOK"
            fnullctr = "NOTOK"
            testf = ""

            TL_INFO_list = [["TLID", "String", "6", "", "False"],
                            ["TLCODE", "String", "19", "", "False"],
                            ["TL_NAME", "String", "50", "", "True"],
                            ["TL_LENGTH", "Single", "4", "", "True"],
                            ["TL_THRM_LO", "Single", "4", "", "True"],
                            ["TL_SIL", "SmallInteger", "2", "", "True"],
                            ["TL_CODU_TY", "String", "2", "CONDUTYPEDO", "True"],
                            ["TL_STRD_NA", "String", "2", "STRANDNAMEDO", "True"],
                            ["TL_STRD_MA", "String", "4", "CONDUMATLDO", "True"],
                            ["TL_CODU_BU", "String", "2", "BUNDLETYPEDO", "True"],
                            ["TL_TOT_TOW", "SmallInteger", "2", "", "True"],
                            ["TL_SRT_SS", "String", "6", "", "True"],
                            ["TL_END_SS", "String", "6", "", "True"],
                            ["TL_VTG_RT", "String", "1", "VOLTRATEDO", "True"],
                            ["TL_VTG_LEV", "String", "2", "VOLTLEVELDO", "True"],
                            ["TL_DOC", "Date", "", "", "True"],
                            ["TL_CKT_KM", "Single", "4", "", "True"],
                            ["TL_INTR_RP", "String", "50", "", "True"],
                            ["TL_AUTH_NA", "String", "50", "", "True"],
                            ["TL_AUTH_CO", "String", "10", "", "True"],
                            # EARTHWIRETYDO domain
                            ["TL_EART_TY", "String", "50", "", "True"],
                            ["TL_ALTR_NA", "String", "80", "", "True"],
                            ["TL_OWNER", "String", "30", "", "True"],
                            ["TL_REM", "String", "100", "", "True"]]

            STRAND_CODU_INFO_list = [["TL_STRD_NA", "String", "2", "STRANDNAMEDO", "True"],
                                    ["TL_CODU_NA", "String", "50", "", "True"],
                                    ["TL_VTG_USE", "SmallInteger", "2", "", "True"],
                                    ["TL_ASTRDNO", "SmallInteger", "2", "", "True"],
                                    ["TL_ASTRDDI", "Single", "4", "", "True"],
                                    ["TL_SSTRDNO", "SmallInteger", "2", "", "True"],
                                    ["TL_SSTRDDI", "Single", "4", "", "True"],
                                    ["TL_TOT_DI", "Single", "4", "", "True"],
                                    ["TL_UNIT_WT", "Single", "4", "", "True"],
                                    ["TL_AL_AR", "Single", "4", "", "True"],
                                    ["TL_SS_AR", "Single", "4", "", "True"],
                                    ["TL_TOT_AR", "Single", "4", "", "True"],
                                    ["TL_CCC", "Single", "4", "", "True"],
                                    ["TL_BK_LOAD", "Single", "4", "", "True"],
                                    ["TL_CODUREM", "Single", "4", "", "True"]]

            SS_BASIC_INFO_list = [["SSCODE", "String", "5", "", "False"],
                                ["SS_SAPCODE", "String", "50", "", "False"],
                                ["SS_NAME", "String", "50", "", "True"],
                                ["SS_MANNED", "SmallInteger", "2", "", "True"],
                                ["SS_STATUS", "String", "2", "STATUSDO", "True"],
                                ["SS_TYPE", "String", "4", "SSTYPEDO", "True"],
                                ["SS_DT_COMM", "Date", "2", "", "True"],
                                ["VLG_RATE", "String", "1",
                                    "VOLTRATEDO", "True"],
                                ["VLG_CLASS1", "String", "2",
                                    "VOLTLEVELDO", "True"],
                                ["VLG_CLASS2", "String", "2",
                                    "VOLTLEVELDO", "True"],
                                ["VLG_CLASS3", "String", "2",
                                    "VOLTLEVELDO", "True"],
                                ["VLG_LEVEL", "String", "2",
                                    "VOLTLEVELDO", "True"],
                                ["FLOC_CODE", "String", "50", "", "True"],
                                ["PLANT_CODE", "String", "50", "", "True"],
                                ["PRIM_MVA", "Single", "4", "", "True"],
                                ["SECO_MVA", "Single", "4", "", "True"],
                                ["TERT_MVA", "Single", "4", "", "True"],
                                ["TOTAL_MVA", "Single", "4", "", "True"],
                                ["T2T_TRANS", "SmallInteger", "2", "", "True"],
                                ["T2D_TRANS", "SmallInteger", "2", "", "True"],
                                ["SS_DISSYS", "String", "2",
                                    "DISTRUSYSDO", "True"],
                                ["SS_GCON", "SmallInteger", "2", "", "True"],
                                ["SS_GCON_NO", "SmallInteger", "2", "", "True"],
                                ["SS_GEN_TYP", "String", "3",
                                    "EGENTYPEDO", "True"],
                                ["SS_PTR_NO", "SmallInteger", "2", "", "True"],
                                ["SS_SCADA", "SmallInteger", "2", "", "True"],
                                ["SS_EHVCOSU", "SmallInteger", "2", "", "True"],
                                ["SS_RTSS", "SmallInteger", "2", "", "True"],
                                ["SS_ADMINCO", "String", "10", "", "True"],
                                ["SS_SLD", "String", "50", "", "True"],
                                ["SS_PHOTO", "String", "50", "", "True"],
                                ["SS_LAYOUT", "String", "50", "", "True"],
                                ["SS_DGSET", "SmallInteger", "2", "", "True"],
                                ["SS_FFUNIT", "SmallInteger", "2", "", "True"],
                                ["SS_FFWTCAP", "Single", "4", "", "True"],
                                ["SS_ERPCSOU", "String", "2",
                                    "COMSOURDO", "True"],
                                ["SS_WIDEBND", "String", "10", "", "True"]]

            SS_CONTACT_INFO_list = [["SSCODE", "String", "5", "", "False"],
                                    ["SS_SAPCODE", "String", "50", "", "False"],
                                    ["SS_NAME", "String", "50", "", "True"],
                                    ["SS_IC_NAME", "String", "50", "", "True"],
                                    ["SS_IC_MOB", "String", "10", "", "True"],
                                    ["SS_ALT_MOB", "String", "10", "", "True"],
                                    ["SS_IC_LANL", "String", "10", "", "True"],
                                    ["SS_ADDSS1", "String", "50", "", "True"],
                                    ["SS_ADDSS2", "String", "50", "", "True"],
                                    ["SS_TOWN", "String", "30", "", "True"],
                                    ["SS_PINCODE", "String", "6", "", "True"],
                                    ["SS_TALUK", "String", "50", "", "True"],
                                    ["SS_DIST", "String", "50", "", "True"],
                                    ["SS_STATE", "String", "30", "", "True"]]

            SS_PTR_INFO_list = [["SSCODE", "String", "5", "", "False"],
                                ["SS_SAPCODE", "String", "50", "", "False"],
                                ["PTRCODE", "String", "7", "", "True"],
                                ["PTR_NOS", "SmallInteger", "2", "", "True"],
                                ["PTR_CAP", "Single", "4", "", "True"],
                                ["PTR_V_RATE", "String", "30", "", "True"],
                                ["PTR_SNO", "String", "50", "", "True"],
                                ["PTR_MAKE", "String", "50", "", "True"],
                                ["PTR_VEC_GR", "String", "20", "", "True"],
                                ["PTR_YOC", "String", "4", "", "True"],
                                ["PTR_YOM", "String", "4", "", "True"],
                                ["PTR_PO", "String", "70", "", "True"],
                                ["PTR_TYPE", "String", "20", "", "True"]]

            SS_DTR_INFO_list = [["SSCODE", "String", "5", "", "False"],
                                ["SS_SAPCODE", "String", "50", "", "False"],
                                ["DTRCODE", "String", "6", "", "True"],
                                ["DTR_VEC_GR", "String", "20", "", "True"],
                                ["DTR_CAP", "Single", "4", "", "True"],
                                ["DTR_SRLNO", "String", "50", "", "True"],
                                ["DTR_MAKE", "String", "50", "", "True"],
                                ["DTR_YOC", "String", "4", "", "True"],
                                ["DTR_YOM", "String", "4", "", "True"],
                                ["DTR_PO", "String", "70", "", "True"]]

            SS_SR_INFO_list = [["SSCODE", "String", "5", "", "False"],
                            ["SS_SAPCODE", "String", "50", "", "False"],
                            ["SRCODE", "String", "6", "", "True"],
                            ["SR_VEC_GR", "String", "20", "", "True"],
                            ["SR_CAP", "Single", "4", "", "True"],
                            ["SR_SRLNO", "String", "50", "", "True"],
                            ["SR_MAKE", "String", "50", "", "True"],
                            ["SR_YOC", "String", "4", "", "True"],
                            ["SR_YOM", "String", "4", "", "True"],
                            ["SR_PO", "String", "70", "", "True"]]

            SS_CAPBANK_INFO_list = [["SSCODE", "String", "5", "", "False"],
                                    ["SS_SAPCODE", "String", "50", "", "False"],
                                    ["CBCODE", "String", "6", "", "True"],
                                    ["CB_CAP", "Single", "4", "", "True"],
                                    ["CB_SRLNO", "String", "50", "", "True"],
                                    ["CB_MAKE", "String", "50", "", "True"],
                                    ["CB_YOC", "String", "4", "", "True"],
                                    ["CB_YOM", "String", "4", "", "True"],
                                    ["CB_PO", "String", "70", "", "True"]]

            TT_TLTOWERS_INFO_list = [["TOCODE", "String", "8", "", "True"],
                                    ["TO_NUM", "String", "50", "", "True"],
                                    ["TO_DSGN", "String", "2",
                                        "TODESIGNDO", "True"],
                                    ["TO_STR_CKT", "SmallInteger", "2", "", "True"],
                                    ["TO_SPA_CKT", "SmallInteger", "2", "", "True"],
                                    ["TO_VTG_RT", "String", "20", "", "True"],
                                    ["TO_TYPE", "String", "50",
                                        "", "True"],  # TSTOTYPEDO
                                    ["TO_TYPE_DE", "String", "50", "", "True"],
                                    ["TO_EXTENS", "SmallInteger", "2", "", "True"],
                                    ["TO_MAKE", "String", "50", "", "True"],
                                    ["TO_FOUNDA", "String", "50", "", "True"],
                                    ["TO_SOIL", "String", "50", "", "True"],
                                    ["TO_CONFIG", "String", "30", "", "True"],
                                    ["TO_EARTHG", "String", "50", "", "True"],
                                    ["TO_HWSSNNO", "SmallInteger", "2", "", "True"],
                                    ["TO_HWDSNNO", "SmallInteger", "2", "", "True"],
                                    ["TO_HWSTNNO", "SmallInteger", "2", "", "True"],
                                    ["TO_HWDTNNO", "SmallInteger", "2", "", "True"],
                                    ["C1_RT_CODE", "String", "40", "", "True"],
                                    ["C1_RT_NAME", "String", "40", "", "True"],
                                    ["C2_RT_CODE", "String", "40", "", "True"],
                                    ["C2_RT_NAME", "String", "40", "", "True"],
                                    ["C3_RT_CODE", "String", "40", "", "True"],
                                    ["IN_DIC_70", "String", "50", "", "True"],
                                    ["IN_DIC_120", "String", "50", "", "True"],
                                    ["IN_DIC_160", "String", "50", "", "True"],
                                    ["IN_SRC_70", "String", "50", "", "True"],
                                    ["IN_SRC_120", "String", "50", "", "True"],
                                    ["IN_SRC_160", "String", "50", "", "True"],
                                    ["TO_DOC", "Date", "", "", "True"],
                                    ["TO_TELE_JB", "String", "40", "", "True"],
                                    ["TSADCODE", "String", "10", "", "True"],
                                    ["TTADCODE", "String", "10", "", "True"],
                                    ["TO_REM", "String", "100", "", "True"]]

            # GETTING THE TABLE IN THE GDB
            tables = gdb.GetLayerCount()
            gdbtablelist = []

            # Loop through each layer (table) in the geodatabase
            for i in range(tables):
                # Get the layer (table) at index i
                layer = gdb.GetLayerByIndex(i)
                # Get the name of the layer (table)
                table_name = layer.GetName()
                # Append the table name to the list
                gdbtablelist.append(table_name)
            print("gdbtablelist ", gdbtablelist)

            dicttablelist = []
            dicttabledescr = []

            for x, y in TABLESdict.items():
                ##print(x, y)
                cv = x
                cvdesc = y
                dicttablelist.append(cv.strip())
                dicttabledescr.append(cvdesc.strip())

            for i in range(len(dicttablelist)):
                tblnm = dicttablelist[i]
                tbdescr = dicttabledescr[i]

                if (tblnm in gdbtablelist):
                    writefileline(" \n")
                    writefileline(
                        "===================================================================================== \n")
                    print(" ")
                    print(
                        "=====================================================================================")
                    ftyctr = "ATTRIBUTE TABLE   = "+tblnm
                    txt2 = ftyctr.ljust(77, "-")
                    writefileline(txt2+"EXISTS \n")
                    print(txt2+"EXISTS")
                    ftyctr = "TABLE DESCRIPTION = "+tbdescr
                    txt2 = ftyctr.ljust(77, ".")
                    writefileline(txt2+" \n")
                    print(str(txt2))
                    writefileline(
                        "------------------------------------------------------------------------------------- \n")
                    print(
                        "-------------------------------------------------------------------------------------")
                    writefileline("  Field Checking : \n")
                    print("  Field Checking :")

                    fields = gdb.GetLayerByName(
                        tblnm).GetLayerDefn().GetFieldCount()
                    print("fields ", fields)
                    thelist = eval(tblnm+"_list")

                    # Checking the Fields ***
                    for i in range(len(thelist)):
                        fnm0 = thelist[i][0]
                        fty0 = thelist[i][1]
                        flen0 = thelist[i][2]
                        fdom0 = thelist[i][3]
                        fnull0 = thelist[i][4]

                        for j in range(fields):
                            field = gdb.GetLayerByName(
                                tblnm).GetLayerDefn().GetFieldDefn(j)
                            # print("field ",field)
                            pnm = ""
                            pty = ""
                            plen = ""
                            pdom = ""
                            pull = ""
                            fnm1 = '{0}'.format(field.GetName())
                            # print("fnm1",fnm1)
                            fty1 = '{0}'.format(field.GetTypeName())
                            # print("fty1",fty1)
                            flen1 = '{0}'.format(field.GetWidth())
                            # print("flen1 ",flen1)
                            fdom1 = '{0}'.format(field.GetDomainName())
                            # print("fdom1 ",fdom1)
                            fnull1 = '{0}'.format(field.IsNullable())
                            newstr = fnm1.strip()+","+fty1.strip()+","+flen1.strip() + \
                                ","+fdom1.strip()+","+fnull1.strip()

                            if (fnm0 == fnm1):
                                fnmctr = "    "+fnm0+"(Name)"
                                txt2 = fnmctr.ljust(77, "-")
                                writefileline(txt2+"OK \n")
                                print(txt2+"OK")
                                if (fty0 == fty1):
                                    ftyctr = "     "+fnm0+"(Type)"
                                    txt2 = ftyctr.ljust(77, "-")
                                    writefileline(txt2+"OK \n")
                                    print(txt2+"OK")
                                else:
                                    ftyctr = "     "+fnm0+"(Type)"
                                    txt2 = ftyctr.ljust(77, "-")
                                    writefileline(txt2+"NOTOK \n")
                                    print(txt2+"NOTOK")

                                if (flen0 == flen1):
                                    flenctr = "     "+fnm0+"(Length)"
                                    txt2 = flenctr.ljust(77, "-")
                                    writefileline(txt2+"OK \n")
                                    print(txt2+"OK")
                                else:
                                    flenctr = "     "+fnm0+"(Length)"
                                    txt2 = flenctr.ljust(77, "-")
                                    writefileline(txt2+"NOTOK \n")
                                    print(txt2+"NOTOK")

                                if (fdom0 == fdom1):
                                    fdomctr = "     "+fnm0+"(Domain)"
                                    txt2 = fdomctr.ljust(77, "-")
                                    writefileline(txt2+"OK \n")
                                    print(txt2+"OK")
                                else:
                                    fdomctr = "     "+fnm0+"(Domain)"
                                    txt2 = fdomctr.ljust(77, "-")
                                    writefileline(txt2+"NOTOK \n")
                                    print(txt2+"NOTOK")

                                if (fnull0 == fnull1):
                                    fnullctr = "     "+fnm0+"(Nullable)"
                                    txt2 = fnullctr.ljust(77, "-")
                                    writefileline(txt2+"OK \n")
                                    print(txt2+"OK")
                                else:
                                    fnullctr = "     "+fnm0+"(Nullable)"
                                    txt2 = fnullctr.ljust(77, "-")
                                    writefileline(txt2+"NOTOK \n")
                                    print(txt2+"NOTOK")
                                writefileline(" \n")
                                print(" ")

                        if fnmctr == "NOTOK":
                            txt1 = "    "+fnm0+"(Name)"
                            txt2 = txt1.ljust(77, "-")
                            writefileline(txt2+"DNE \n")
                            print(txt2+"DNE")
                            writefileline(" \n")
                            print(" ")
                            fnmctr = "NOTOK"
                            ftyctr = "NOTOK"
                            flenctr = "NOTOK"
                            fdomctr = "NOTOK"
                            fnullctr = "NOTOK"
                            testf = ""

                        fnmctr = "NOTOK"
                        ftyctr = "NOTOK"
                        flenctr = "NOTOK"
                        fdomctr = "NOTOK"
                        fnullctr = "NOTOK"

                else:
                    writefileline(" \n")
                    writefileline(
                        "===================================================================================== \n")
                    print(" ")
                    print(
                        "=====================================================================================")
                    ftyctr = "ATTRIBUTE TABLE   = "+tblnm
                    txt2 = ftyctr.ljust(57, "-")
                    writefileline(txt2+"DOES NOT EXIST-Not Checking! \n")
                    writefileline(
                        "------------------------------------------------------------------------------------- \n")
                    print(txt2+"DOES NOT EXIST-Not Checking!")
                    print(
                        "-------------------------------------------------------------------------------------")
                    fnmctr = "NOTOK"
                    ftyctr = "NOTOK"
                    flenctr = "NOTOK"
                    fdomctr = "NOTOK"
                    fnullctr = "NOTOK"

            writefileline(" \n")
            writefileline(
                "************************************************************************************* \n")
            writefileline(
                "************* ATTRIBURE TABLES SUCESSFULLY CHECKED ! ******************************** \n")
            writefileline(
                "************************************************************************************* \n")
            writefileline(" \n")

            print(" ")
            print(
                "*************************************************************************************")
            print(
                "************* ATTRIBURE TABLES SUCESSFULLY CHECKED ! ********************************")
            print(
                "*************************************************************************************")
            print(" ")

            # Setting present date and time -------------------------------------------------------------------------
            endT = datetime.datetime.now()
            elsp = endT - now
            #elaps1 = elsp.strftime("%S")
            # arcpy.AddMessage(str(elaps1))

            elapsec = elsp.total_seconds()
            txt = "{:.2f} seconds"
            txt1 = txt.format(elapsec)

            #arcpy.AddMessage("Total Time Difference : {.2f} Seconds".format(elapsec) )

            # Writing END LINES TO THE FILE --------------------------------------------------
            writefileline(
                "************************************************************************************* \n")
            writefileline(
                "                                   T H A N K S !!! \n")
            writefileline(
                "************************************************************************************* \n")
            writefileline("   " + str(dt) +
                        " (Elasped time: " + str(txt1) + ") \n")
            writefileline(
                "************************************************************************************* \n")
            writefileline(" \n")
            print(
                "*************************************************************************************")
            print("                                   T H A N K S !!! ")
            print(
                "*************************************************************************************")
            print("   " + str(dt) + " (Elasped time: " + str(txt1) + ")")
            print(
                "*************************************************************************************")
            print(" ")
            return Response({"message": "File uploaded successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return Response({"error": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
