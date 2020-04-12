# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 16:52:08 2018

@author: Naveenkumar Sivasubramanian
"""
import math
from collections import defaultdict


#Global variables used for the code (collection defaultdict is used to handle error in list)
pointDataList = defaultdict(list)
linkDataList = defaultdict(list)

#class used to find the latitude and longitude for fiven points
class Find_LatitudeAndLongitude():
    def __init__(self, shapeInfo):
        self.ID = shapeInfo
        shape_attributes = shapeInfo.split("/")
        self.longitude, self.latitude = map(float, (shape_attributes[0], shape_attributes[1]))

#class used to package the LinkData csv into a package object
class PackageLinkID():
    #The start and end data points are passed to the class which packages it into the class variables
    def __init__(self, ID, start, end):
        self.id = ID
        self.point_one, self.point_two = Find_LatitudeAndLongitude(start), Find_LatitudeAndLongitude(end)
        self.vector_longitude, self.vector_latitude = self.point_two.longitude - self.point_one.longitude, self.point_two.latitude - self.point_one.latitude
        self.length = math.sqrt(self.vector_longitude ** 2 + self.vector_latitude ** 2)
        if self.vector_latitude != 0:
            self.radian = math.atan(self.vector_longitude / self.vector_latitude)
        elif self.vector_longitude > 0:
            self.radian = math.pi / 2
        else:
            self.radian = math.pi * 3 / 2

    #Function used to calculate the distance between a packed linkData and a new probe-point
    def calculateDistance(self, point):
        target_longitude, target_latitude = point.longitude - self.point_one.longitude, point.latitude - self.point_one.latitude
        dist_point_refnode = (target_longitude ** 2) + (target_latitude ** 2)
        projection = (target_longitude * self.vector_longitude + target_latitude * self.vector_latitude) / self.length
        if projection < 0:
            return dist_point_refnode

        pro_squre = projection ** 2
        if pro_squre > self.length ** 2:
            return (point.longitude - self.point_two.longitude) ** 2 + (point.latitude - self.point_two.latitude) ** 2
        return (target_longitude**2 + target_latitude**2) - projection**2

   #Function used to calculate distance between two links (linkData is passed)
    def calculateDistanceFromLink(self, point):
        target_longitude, target_latitude = point.longitude - self.point_one.longitude, point.latitude - self.point_one.latitude
        return math.sqrt(target_longitude**2 + target_latitude**2)

#Class used to package the sample ID data set into an object
class PackageSampleID(object):
    def __init__(self, line):
        self.sampleID,      \
        self.dateTime,      \
        self.sourceCode,    \
        self.latitude,      \
        self.longitude,     \
        self.altitude,      \
        self.speed,         \
        self.heading = line.strip().split(',')

        self.direction = ""
        self.linkID = None
        self.distFromRef = None
        self.distFromLink = None
        self.slope = None

    # Function used to find the direction (F/T)
    def getDirection(self, A, B):
        self.direction = "F" if ((math.cos(A) * math.cos(B) + math.sin(A) * math.sin(B)) > 0) else "T"

    #Function used to convert the object to string and return the required format
    def toString(self):
        return '{}, {}, {}, {}, {}, {}, {}, {}, {}, {} ,{}, {}\n' \
            .format(self.sampleID,
                    self.dateTime,
                    self.sourceCode,
                    self.latitude,
                    self.longitude,
                    self.altitude,
                    self.speed,
                    self.heading,
                    self.linkID,
                    self.direction,
                    self.distFromRef,
                    self.distFromLink)

#Class used to package the sample ID data set into an object with scope object appended to the return list
class PackageProbeSlope(object):
	def __init__(self, line):
		 self.sampleID	, \
        self.dateTime	, \
        self.sourceCode	, \
        self.latitude	, \
        self.longitude	, \
        self.altitude	, \
        self.speed		, \
        self.heading	, \
        self.linkID		, \
        self.direction	, \
        self.distFromRef, \
        self.distFromLink = line.split(',')
		 self.elevation = None
		 self.slope = None

   #Function used to convert the object to string and return the required format with scope appended
	def toString(self):
		'''
        Function to convert data into comma seperated string
        '''
		return '{}, {}, {}, {}, {}, {}, {}, {}, {}, {} , {}, {}\n' \
			.format(self.sampleID,
					self.dateTime,
					self.sourceCode,
					self.latitude,
					self.longitude,
					self.altitude,
					self.speed,
					self.heading,
					self.linkID,
					self.direction,
					self.distFromRef,
					#self.distFromLink,
                 self.slope)

#Class used to package the linkData used to calculate the slope and evaluate it
class PackageLink(object):
	def __init__(self, line):
		self.linkID		  ,\
		self.refNodeID		  ,\
		self.nrefNodeID		  ,\
		self.length			  ,\
		self.functionalClass  ,\
		self.directionOfTravel,\
		self.speedCategory	  ,\
		self.fromRefSpeedLimit,\
		self.toRefSpeedLimit  ,\
		self.fromRefNumLanes  ,\
		self.toRefNumLanes	  ,\
		self.multiDigitized	  ,\
		self.urban			  ,\
		self.timeZone		  ,\
		self.shapeInfo		  ,\
		self.curvatureInfo	  ,\
		self.slopeInfo		  = line.strip().split(',')

		self.ReferenceNodeLat,self.ReferenceNodeLong,_  = self.shapeInfo.split('|')[0].split('/')
		self.ReferenceNode = map(float, (self.ReferenceNodeLat,self.ReferenceNodeLong))
		self.ProbePoints   = []

#Function used to read the linkData from the csv and create linkDataList/pointDataList
def readLinkData():
    print("Processing LinkData....")
    for line in open("Partition6467LinkData.csv").readlines():
        columns = line.strip().split(",")
        shapeInfo = columns[14].split("|")
        #Iterate through the link data to form the package by passing into the class
        for iterator in range(len(shapeInfo)-1):
            tempShape = PackageLinkID(columns[0], shapeInfo[iterator], shapeInfo[iterator+1])
            linkDataList[columns[0]].append(tempShape)
            pointDataList[shapeInfo[iterator]].append(tempShape)
            pointDataList[shapeInfo[iterator + 1]].append(tempShape)

    print("linkDataList and pointDataList created....");

#Function used to match the linkDataList with the probe data, find the shortest distance and create the Partition6467MatchedPoints.csv
def matchData():
    matchedPoints = open("Partition6467MatchedPoints.csv", "w+")
    previousID = None
    matchPackageDataArray = []
    print("Processing Partition6467MatchedPoints CSV....");
    recordCount=0;
    #Loop to check every data in the linkDataList with the probe data from the csv in order to find [sampleID, dateTime, sourceCode, latitude, longitude, altitude, speed, heading, linkPVID, direction, distFromRef, distFromLink]
    for line in open("Partition6467ProbePoints.csv").readlines():
        if recordCount < 1048576:
            recordCount=recordCount+1;
            probePoints = PackageSampleID(line)
            latitude_longitude = Find_LatitudeAndLongitude(probePoints.latitude + "/" + probePoints.longitude)
            #Check if the previous value is repeated
            if probePoints.sampleID != previousID:
                previousID = probePoints.sampleID
                #Looping through every element in the linkDataList
                for key in linkDataList.keys():
                    for link in linkDataList[key]:
                        distance = link.calculateDistance(latitude_longitude)
                        #If the probe point is empty or less than the distance find the direction b/w the point and the linkdata
                        if not probePoints.distFromRef or distance < probePoints.distFromRef:
                            probePoints.distFromRef, probePoints.linkID = distance, link.id
                            probePoints.distFromLink = linkDataList[probePoints.linkID][0].calculateDistanceFromLink(latitude_longitude)
                            probePoints.getDirection(float(probePoints.heading), link.radian)
                            matchPackageDataArray = [link.point_one, link.point_two]

            else:
                #Looping through the array of match data when the repeation occurs
                for candidate_point in matchPackageDataArray:
                    for link in pointDataList[candidate_point.ID]:
                        distance = link.calculateDistance(latitude_longitude)
                        if not probePoints.distFromRef or distance < probePoints.distFromRef:
                            probePoints.distFromRef, probePoints.linkID = distance, link.id
                            probePoints.distFromLink = linkDataList[probePoints.linkID][0].calculateDistanceFromLink(latitude_longitude)
                            probePoints.getDirection(float(probePoints.heading), link.radian)
        else:
            break;
        #Finding the distance from the reference
        probePoints.distFromRef = math.sqrt(probePoints.distFromRef) * (math.pi / 180 * 6371000)
        #Finding the distance from the link
        probePoints.distFromLink = probePoints.distFromLink * (math.pi / 180 * 6371000)
        matchedPoints.write(probePoints.toString())

    matchedPoints.close()
    print("Done loading the Partition6467MatchedPoints CSV....");

#Function used to distance between two data points (latitude and longitude) with respect to earth avg rad
def distance(longitude_point_one, latitude_point_one, longitude_point_two, latitude_point_two):
    longitude_point_one, latitude_point_one, longitude_point_two, latitude_point_two = list(map(math.radians, [longitude_point_one, latitude_point_one, longitude_point_two, latitude_point_two]))
    distance_longitude, distance_latitude = longitude_point_two - longitude_point_one , latitude_point_two - latitude_point_one
    #Calculating the distance
    raw_distance = math.sin(distance_latitude/2)**2 + math.cos(latitude_point_one) * math.cos(latitude_point_two) * math.sin(distance_longitude/2)**2
    #Converting in Km with respect with earth radius
    distance_kilometers = 6371 * 2 * math.asin(math.sqrt(raw_distance))
    return distance_kilometers

#Function used to find the slope of the road link
def calculateSlopeData():
    slopeArray = []
    recordCount=0;
    slope_csv = open("slope_data.csv", 'w')
    #test2 = open("test2.txt", 'w')
    previousProbe = None
    print("Calculating slope data....")
    #creating the linkArray with linkdata csv (converted in respective package)
    for line in open("Partition6467LinkData.csv").readlines():
        slopeArray.append(PackageLink(line))
    print("Comparing the match data....")

    #Looping through matched point csv to find the slope and create slope csv
    with open("Partition6467MatchedPoints.csv") as each_data:
        for line in each_data:
            if recordCount < 1200000:
                recordCount=recordCount+1;
                current_probe = PackageProbeSlope(line)
                #checking previous value for repetation
                if not previousProbe or current_probe.linkID != previousProbe.linkID:
                    current_probe.slope = ''
                else:
                    try:
                        start, end = list(map(float, [current_probe.longitude, current_probe.latitude])), list(map(float, [previousProbe.longitude, previousProbe.latitude]))
                        hypotenuse_angle = distance(start[0], start[1], end[0], end[1]) / 1000
                        opposite_angle = float(current_probe.altitude) - float(previousProbe.altitude)
                        current_probe.slope = (2 * math.pi * math.atan(opposite_angle / hypotenuse_angle)) / 360
                    except ZeroDivisionError:
                        current_probe.slope = 0.0
                    #Looping through each linkArray
                    for link in slopeArray:
                        if current_probe.linkID.strip() == link.linkID.strip() and link.slopeInfo != '':
                           link.ProbePoints.append(current_probe)
                           break
                #Writing to the slope csv
                slope_csv.write(current_probe.toString())
                previousProbe = current_probe
            else:
                break;
        #closing the slope csv and returning the array
        slope_csv.close()
    print("Done calculating slope data....")
    return slopeArray

#Function used to evaluate the derived road slope with the surveyed road slope in the link data file
def slope_evaluation(scope_data):
    print("Processing evaluation....")
    evaluationCsv = open("evaluation.csv", 'w')
    #Creating the header for the csv file
    #evaluationCsv.write('ID,  Given Slope, Calculated Slope' + "\n")
    #looping through each element in the scope array
    for node in scope_data:
        # checking for matched point in the node
        if len(node.ProbePoints) > 0:
            summation = 0.0
            #Splitting the slopeInfo to form an array of slopes
            slopeGroupArray = node.slopeInfo.strip().split('|')
            #Looping through each element and finding the sum in the slope group
            for eachSlope in slopeGroupArray:
                summation += float(eachSlope.strip().split('/')[1])
            #calculating the average
            slope = summation / len(slopeGroupArray)
            calculatedSum, probCount = 0.0, 0
            # Calculating the mean of calculated slope info for the link
            for eachProbe in node.ProbePoints:
                #If direction is towards turn the slope value to negative
                if eachProbe.direction == "T":
                    eachProbe.slope = -eachProbe.slope
                #Incrementing the count
                if eachProbe.slope != '' and eachProbe.slope != 0:
                    calculatedSum += eachProbe.slope
                    probCount += 1

            evaluatedSlope = calculatedSum / probCount if probCount != 0 else 0
            evaluationCsv.write('{}, {}, {}\n'
                                  .format(node.linkID,
                                          slope,
                                          evaluatedSlope))
    print("Done evaluating slope....")
    evaluationCsv.close()

#Function which maeks the start of the script
if __name__ == '__main__':
    #Function called to create linkdata array
    readLinkData()
    #Function called to create the Partition6467MatchedPoints csv
    matchData()
    #Function used to calculate the slope
    slope_data = calculateSlopeData()
    #Function called to do the evaluation process
    slope_evaluation(slope_data)
