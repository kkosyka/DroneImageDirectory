# Kalynn Kosyka
# Feb 2018 - Present

#Python 2.7
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import csv
import psycopg2
from psycopg2.extras import Json
import json
import datetime

def getGPS(pathImg):
	exif_data = {}
	i = Image.open(pathImg)
	info = i._getexif()
	if info:
		for tag, value in info.items():
			decoded = TAGS.get(tag, tag)
			if decoded == "GPSInfo":
				gps_data = {}
				for t in value.keys():
					sub_decoded = GPSTAGS.get(t, t)
					gps_data[sub_decoded] = value[t]
				exif_data[decoded] = gps_data

			else:
				exif_data[decoded] = value

	return exif_data


def getCamera(pathImg):
	exif_data = {}
	i = Image.open(pathImg)
	info = i._getexif()
	for tag, value in info.items():
		decoded = TAGS.get(tag, tag)
		# decode = ExifTags.GPSTAGS.get(key,key)
		if decoded == "ShutterSpeedValue" or decoded == "DateTimeOriginal" or decoded == "ApertureValue" or decoded == "FocalLength" or decoded == "SubjectDistance" or decoded == "Make" or decoded == "Model":
			exif_data[decoded] = value
	return exif_data

def getOther(pathImg):
	exif_data = {}
	headers = ['LightSource', 'YResolution', 'ResolutionUnit', 'FlashPixVersion', 'Make', 'Flash', 'SceneCaptureType', 'GPSInfo', 'MeteringMode', 'XResolution', 'Contrast', 'Saturation', 'MakerNote', 'ExposureProgram', 'FocalLengthIn35mmFilm', 'ShutterSpeedValue', 'ColorSpace', 'ExifImageWidth', 'XPKeywords', 'ExposureBiasValue', 'DateTimeOriginal', 'SceneType', 'Software', 'SubjectDistanceRange', 'WhiteBalance', 'CompressedBitsPerPixel', 'DateTimeDigitized', 'FNumber', 'CustomRendered', 'ApertureValue', 'FocalLength', 'ExposureMode', 'ImageDescription', 'ComponentsConfiguration', 'SubjectDistance', 'ExifOffset', 'ExifImageHeight', 'ISOSpeedRatings', 'Model', 'DateTime', 'Orientation', 'ExposureTime', 'FileSource', 'MaxApertureValue', 'XPComment', 'ExifInteroperabilityOffset', 'Sharpness', 'ExposureIndex', 'GainControl', 'YCbCrPositioning', 'DigitalZoomRatio']
	#['LightSource', 'YResolution', 'ResolutionUnit', 'FlashPixVersion', 'Make', 'Flash', 'SceneCaptureType', 'GPSInfo', 'MeteringMode', 'XResolution', 'Contrast', 'Saturation', 'MakerNote', 'ExposureProgram', 'FocalLengthIn35mmFilm', 'ShutterSpeedValue', 'ColorSpace', 'ExifImageWidth', 'XPKeywords', 'ExposureBiasValue', 'DateTimeOriginal', 'SceneType', 'Software', 'SubjectDistanceRange', 'WhiteBalance', 'CompressedBitsPerPixel', 'DateTimeDigitized', 'FNumber', 'CustomRendered', 'ApertureValue', 'FocalLength', 'ExposureMode', 'ImageDescription', 'ComponentsConfiguration', 'SubjectDistance', 'ExifOffset', 'ExifImageHeight', 'ISOSpeedRatings', 'Model', 'DateTime', 'Orientation', 'ExposureTime', 'FileSource', 'MaxApertureValue', 'XPComment', 'ExifInteroperabilityOffset', 'Sharpness', 'ExposureIndex', 'GainControl', 'YCbCrPositioning', 'DigitalZoomRatio']
	
	i = Image.open(pathImg)
	info = i._getexif()
	for tag, value in info.items():
		decoded = TAGS.get(tag, tag)
		# decode = ExifTags.GPSTAGS.get(key,key)
		# if decoded == "ShutterSpeedValue" or decoded == "DateTimeOriginal" or decoded == "ApertureValue" or decoded == "FocalLength" or decoded == "SubjectDistance" or decoded == "Make" or decoded == "Model":
		if decoded in headers:
			exif_data[decoded] = value
	return exif_data


def getMetadata(pathImg):
	# print pathImg
	#GPS related
	GPS = getGPS(pathImg)
	#other related
	camera = getCamera(pathImg)
	other = getOther(pathImg)

	return GPS, camera,other #, other

def _get_if_exist(data, key):
    if key in data:
        return data[key]
		
    return None
	
def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None
    gps_alt = None
    gps = None
    if "GPSInfo" in exif_data:		
        gps_info = exif_data["GPSInfo"]
        gps = gps_info
        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')
        gps_alt = _get_if_exist(gps_info, 'GPSAltitude')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":                     
	            lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon
    return lat, lon, gps


def main():
	computer = raw_input("MAC? (y/n): ")
	#go to folder of images
	#PC "\", MAC "/"

	if(computer =="Y" or computer =="y" or computer == "yes"):
		path = "/IMG"
	else:
		path = "\IMG"

	for subdir, dirs, files in os.walk(os.getcwd() + path):
		for currImg in files:
			if currImg.lower().endswith((".jpg")): #.endswith((".jpg", ".jpeg"))
				currPath = os.path.join(subdir, currImg)
				gps, camera,other = getMetadata(currPath) #gps, camera, other = getMetadata(currPath)
				header = []
				values = []
				header.extend(["FileName", "PATH", "X", "Y"])
				print "Location IMG: " + currPath
				print "GPS Specs: "
				lat, long, otherGPS = get_lat_lon(gps)
				print "XY-Coor: " + str(lat) + ", " + str(long) 
				values.extend([currImg, currPath, lat, long])

				if type(otherGPS) == type({}):
					for key, value in otherGPS.iteritems():
						header.append(key)
						values.append(value)

				for key, value in other.iteritems():
					header.append(key)
					if type(value) == {}:
						values.append(json.dumps(value))#json.dumps(value))
					else:
						values.append(str(value))

				#insert values into CSV w header: FileName, PATH, X, Y, GPSLongitude, GPSLatitudeRef, GPSAltitude, GPSLatitude, GPSVersionID, GPSLongitudeRef,GPSAltitudeRef, ApertureValue, FocalLength, Make, SubjectDistance, DateTimeOriginal, Model, ShutterSpeedValue
				with open(r'imagesCSV.csv', 'a') as f:
				    writer = csv.writer(f)
				    writer.writerow(values)

				now = datetime.datetime.now()
				date = now.strftime("%Y-%m-%d")

				conn = psycopg2.connect("dbname='DroneImageDirectory' host='localhost' user='postgres' password='smithgis'") #(database information - database, host, user, password)
				cur = conn.cursor()

				cur.execute("""INSERT INTO public."DroneImageDirectory"(DateAdded, FileName, PATH, X, Y, GPSLongitude, GPSLatitudeRef, GPSAltitude, GPSLatitude, GPSVersionID, 
				 	GPSLongitudeRef, GPSAltitudeRef, LightSource, YResolution, ResolutionUnit, FlashPixVersion, Make, Flash, SceneCaptureType, GPSInfo, MeteringMode, 
				 	XResolution, Contrast, Saturation, MakerNote, ExposureProgram, FocalLengthIn35mmFilm, ShutterSpeedValue, ColorSpace, ExifImageWidth, XPKeywords, 
				 	ExposureBiasValue, DateTimeOriginal, SceneType, Software, SubjectDistanceRange, WhiteBalance, CompressedBitsPerPixel, DateTimeDigitized, 
				 	FNumber, CustomRendered, ApertureValue, FocalLength, ExposureMode, ImageDescription, ComponentsConfiguration, SubjectDistance, ExifOffset,
				 	ExifImageHeight, ISOSpeedRatings, Model, DateTime, Orientation, ExposureTime, FileSource, MaxApertureValue, XPComment, 
				 	ExifInteroperabilityOffset, Sharpness, ExposureIndex, GainControl, YCbCrPositioning, DigitalZoomRatio) VALUES
				 	(%s, %s,%s,%s, %s, %s, %s,%s,%s,%s, %s, %s, %s,%s,%s,%s, %s, %s, %s,%s,%s,%s, %s, %s, %s,%s,%s,%s, %s, %s, %s,%s,%s,%s, %s, %s, %s,%s,%s,%s, %s,
				 	%s, %s,%s,%s,%s, %s, %s, %s,%s,%s,%s, %s, %s, %s,%s,%s,%s, %s, %s, %s,%s, %s)""",(date, values[0],values[1],values[2],values[3],values[4],values[5],
				 		values[6],values[7],values[8],values[9],values[10],values[11],values[12],values[13],values[14],values[15],values[16],values[17],
				 	 	values[18],values[19],values[20],values[21],values[22],values[23],values[24],values[25],values[26],values[27],values[28],values[29],
				 	 	values[30],values[31],values[32],values[33],values[34],values[35],values[36],values[37],values[38],values[39],values[40],values[41],
					 	values[42],values[43],values[44],values[45],values[46],values[47],values[48],values[49],values[50],values[51],values[52],values[53],
				 	 	values[54],values[55],values[56],values[57],values[58],values[59],values[60], values[61]))

				cur.execute("""UPDATE public."DroneImageDirectory" SET "coorgeom" = ST_GeomFromText('POINT('||y::text||' '||x::text||')', 4326)""")
				conn.commit()
				print
			else:
				print "Cannot extract EXIF data from: " + currImg
				print

main()


				#iterate through all folders of images w different files  - DONE
				#dont add to db if it is already there, check if such image exists 
				#add column where user cna put in curr date so we know when last this image was placed - in case image is moved - DONE

'''
		cur.execute("""SELECT EXISTS(SELECT 1 FROM public."DroneImageDirectory" WHERE 
			FileName=%s AND PATH=%s AND X=%s AND Y=%s AND  GPSLongitude=%s AND  GPSLatitudeRef=%s AND  GPSAltitude=%s AND  GPSLatitude=%s AND  GPSVersionID=%s AND 
			GPSLongitudeRef=%s AND  GPSAltitudeRef=%s AND  LightSource=%s AND  YResolution=%s AND  ResolutionUnit=%s AND  FlashPixVersion=%s AND  Make=%s AND 
			Flash=%s AND  SceneCaptureType=%s AND  GPSInfo=%s AND  MeteringMode=%s AND  XResolution=%s AND  Contrast=%s AND  Saturation=%s AND  MakerNote=%s AND 
			ExposureProgram=%s AND  FocalLengthIn35mmFilm=%s AND  ShutterSpeedValue=%s AND  ColorSpace=%s AND  ExifImageWidth=%s AND  XPKeywords=%s AND  
			ExposureBiasValue=%s AND  DateTimeOriginal=%s AND  SceneType=%s AND  Software=%s AND  SubjectDistanceRange=%s AND  WhiteBalance=%s AND  
			CompressedBitsPerPixel=%s AND  DateTimeDigitized=%s AND FNumber=%s AND CustomRendered=%s AND  ApertureValue=%s AND  FocalLength=%s AND  
			ExposureMode=%s AND  ImageDescription=%s AND ComponentsConfiguration=%s AND  SubjectDistance=%s AND ExifOffset=%s AND  ExifImageHeight=%s AND 
			ISOSpeedRatings=%s AND  Model=%s AND  DateTime=%s AND  Orientation=%s AND  ExposureTime=%s AND  FileSource=%s AND  MaxApertureValue=%s AND 
			XPComment=%s AND  ExifInteroperabilityOffset=%s AND  Sharpness=%s AND  ExposureIndex=%s AND  GainControl=%s AND  YCbCrPositioning=%s""",
			(values[0],values[1],values[2],values[3],values[4],values[5],values[6],values[7],values[8],values[9],values[10],values[11],
			values[12],values[13],values[14], values[15],values[16],values[17],values[18],values[19],values[20],values[21],values[22],values[23],values[24],
			values[25],values[26],values[27],values[28],values[29],values[30],values[31],values[32],values[33],values[34],values[35],values[36],values[37],
			values[38],values[39],values[40],values[41],values[42],values[43],values[44],values[45],values[46],values[47],values[48],values[49],values[50],
			values[51],values[52],values[53],values[54],values[55],values[56],values[57],values[58],values[59], values[60]))
		#AND xcoor=%s AND ycoor=%s AND username=%s AND created=%s AND hashtags=%s ) ,(text, coorX, coorY, screenName, createdAt, hashtagsHolder))
'''

#FileName, PATH, X, Y, GPSLongitude, GPSLatitudeRef, GPSAltitude, GPSLatitude, GPSVersionID, GPSLongitudeRef, GPSAltitudeRef, LightSource, YResolution, ResolutionUnit, FlashPixVersion, Make, Flash, SceneCaptureType, GPSInfo, MeteringMode, XResolution, Contrast, Saturation, MakerNote, ExposureProgram, FocalLengthIn35mmFilm, ShutterSpeedValue, ColorSpace, ExifImageWidth, XPKeywords, ExposureBiasValue, DateTimeOriginal, SceneType, Software, SubjectDistanceRange, WhiteBalance, CompressedBitsPerPixel, DateTimeDigitized, FNumber, CustomRendered, ApertureValue, FocalLength, ExposureMode, ImageDescription, ComponentsConfiguration, SubjectDistance, ExifOffset, ExifImageHeight, ISOSpeedRatings, Model, DateTime, Orientation, ExposureTime, FileSource, MaxApertureValue, XPComment, ExifInteroperabilityOffset, Sharpness, ExposureIndex, GainControl, YCbCrPositioning, DigitalZoomRatio


		
# =======
# 		print	values[61]

# 		for x in range (0,62):
# 			print "values[" + str(x)+ "],"

#dasfas

# >>>>>>> Stashed changes
# 		# string = "FileName, PATH, X, Y, GPSLongitude, GPSLatitudeRef, GPSAltitude, GPSLatitude, GPSVersionID, GPSLongitudeRef, GPSAltitudeRef, 'LightSource', 'YResolution', 'ResolutionUnit', 'FlashPixVersion', 'Make', 'Flash', 'SceneCaptureType', 'GPSInfo', 'MeteringMode', 'XResolution', 'Contrast', 'Saturation', 'MakerNote', 'ExposureProgram', 'FocalLengthIn35mmFilm', 'ShutterSpeedValue', 'ColorSpace', 'ExifImageWidth', 'XPKeywords', 'ExposureBiasValue', 'DateTimeOriginal', 'SceneType', 'Software', 'SubjectDistanceRange', 'WhiteBalance', 'CompressedBitsPerPixel', 'DateTimeDigitized', 'FNumber', 'CustomRendered', 'ApertureValue', 'FocalLength', 'ExposureMode', 'ImageDescription', 'ComponentsConfiguration', 'SubjectDistance', 'ExifOffset', 'ExifImageHeight', 'ISOSpeedRatings', 'Model', 'DateTime', 'Orientation', 'ExposureTime', 'FileSource', 'MaxApertureValue', 'XPComment', 'ExifInteroperabilityOffset', 'Sharpness', 'ExposureIndex', 'GainControl', 'YCbCrPositioning, DigitalZoomRatio"
# 		# string = string.replace("\'", "")
# 		# print string





#DJI ['GPSLongitude', 'GPSLatitudeRef', 'GPSAltitude', 'GPSLatitude', 'GPSVersionID', 'GPSLongitudeRef', 'GPSAltitudeRef', 'ApertureValue', 'FocalLength', 'Make', 'SubjectDistance', 'DateTimeOriginal', 'Model', 'ShutterSpeedValue']
#p4p ['GPSLongitude', 'GPSLatitudeRef', 'GPSAltitude', 'GPSLatitude', 'GPSVersionID', 'GPSLongitudeRef', 'GPSAltitudeRef', 'ApertureValue', 'FocalLength', 'Make', 'SubjectDistance', 'DateTimeOriginal', 'Model', 'ShutterSpeedValue']
#iphone  ['ApertureValue', 'FocalLength', 'ShutterSpeedValue', 'DateTimeOriginal', 'Model', 'Make']
#nikon ['ApertureValue', 'FocalLength', 'ShutterSpeedValue', 'DateTimeOriginal', 'Model', 'Make']


# {'YResolution': (72, 1), 
# 'ResolutionUnit': 2, 
# 'Make': u'Apple', 
# 'Flash': 16, 
# 'SceneCaptureType': 0, 
# 'DateTime': u'2017:06:25 09:19:46', 
# 'MeteringMode': 5, 
# 'XResolution': (72, 1), 
# 'LensSpecification': ((83, 20), (83, 20), (11, 5), (11, 5)),
# 'ExposureBiasValue': (0, 1), 
# 'MakerNote': 'Apple iOS\x00\x00\x01MM\x00\t\x00\x01\x00\t\x00\x00\x00\x01\x00\x00\x00\x05\x00\x03\x00\x07\x00\x00\x00h\x00\x00\x00\x80\x00\x04\x00\t\x00\x00\x00\x01\x00\x00\x00\x01\x00\x05\x00\t\x00\x00\x00\x01\x00\x00\x00\x93\x00\x06\x00\t\x00\x00\x00\x01\x00\x00\x00\x9a\x00\x07\x00\t\x00\x00\x00\x01\x00\x00\x00\x01\x00\x08\x00\n\x00\x00\x00\x03\x00\x00\x00\xe8\x00\x0e\x00\t\x00\x00\x00\x01\x00\x00\x00\x00\x00\x14\x00\t\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00bplist00\xd4\x01\x02\x03\x04\x05\x06\x07\x08UflagsUvalueUepochYtimescale\x10\x01\x13\x00\x02\xba\x82\x03L\x7f\xb8\x10\x00\x12;\x9a\xca\x00\x08\x11\x17\x1d#-/8:\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00?\x00\x00\x04\x13\x00\x00Q\xf2\xff\xff\xf7\x1b\x00\x00\x08\xe3\xff\xff\xf4\xd3\x00\x00\xe4\x95', 
# 'ExposureProgram': 2, 
# 'FocalLengthIn35mmFilm': 29, 
# 'SubjectLocation': (1631, 1223, 1795, 1077),
# 'ColorSpace': 1, 
# 'ExifImageWidth': 2448, 
# 'DateTimeDigitized': u'2017:06:25 09:19:46',
# 'ApertureValue': (7892, 3469), 
# 'SceneType': '\x01', 
# 'LensModel': u'iPhone 6 back camera 4.15mm f/2.2', 
# 'BrightnessValue': (18647, 1866), 
# 'WhiteBalance': 0,
# 'SensingMethod': 2,
# 'FNumber': (11, 5),
# 'DateTimeOriginal': u'2017:06:25 09:19:46', 
# 'FocalLength': (83, 20),
# 'SubsecTimeOriginal': u'050', 
# 'ExposureMode': 0, 
# 'ComponentsConfiguration': '\x01\x02\x03\x00', 
# 'ExifOffset': 188, 
#'ExifImageHeight': 3264,
# 'SubsecTimeDigitized': u'050', 
# 'ISOSpeedRatings': 32, 
# 'Model': u'iPhone 6', 
# 'Software': u'Photos 1.0.1', 
# 'ExposureTime': (1, 1721), 
# 'Orientation': 1, 
# 'FlashPixVersion': '0100', 
# 'LensMake': u'Apple', 
# 'ShutterSpeedValue': (3257, 303), 
# 'ExifVersion': '0221'}




# {'EXIF MakerNote': (0x927C) Undefined=[65, 112, 112, 108, 101, 32, 105, 79, 83, 0, 0, 1, 77, 77, 0, 9, 0, 1, 0, 9, ... ] @ 682, 
# 'MakerNote Tag 0x0008': (0x0008) Signed Ratio=[149159935/-187498496, -7019/83, 20/83] @ 232, 
# 'Image ExifOffset': (0x8769) Long=188 @ 114, 
# 'EXIF ComponentsConfiguration': (0x9101) Undefined=YCbCr @ 282, 
# 'MakerNote Tag 0x0001': (0x0001) Signed Long=5 @ 10, 
# 'MakerNote Tag 0x0003': (0x0003) Undefined=[6, 7, 8, 85, 102, 108, 97, 103, 115, 85, 118, 97, 108, 117, 101, 85, 101, 112, 111, 99, ... ] @ 128, 
# 'MakerNote Tag 0x0004': (0x0004) Signed Long=1 @ 34, 
# 'EXIF FlashPixVersion': (0xA000) Undefined=0100 @ 426, 
# 'MakerNote Tag 0x0006': (0x0006) Signed Long=154 @ 58, 
# 'MakerNote Tag 0x0007': (0x0007) Signed Long=1 @ 70, 
# 'Image DateTime': (0x0132) ASCII=2017:06:25 09:19:46 @ 168, 
# 'EXIF ShutterSpeedValue': (0x9201) Signed Ratio=3257/303 @ 634, 
# 'EXIF ColorSpace': (0xA001) Short=sRGB @ 438, 
# 'EXIF MeteringMode': (0x9207) Short=Pattern @ 342, 
# 'EXIF ExifVersion': (0x9000) Undefined=0221 @ 246, 
# 'Image Software': (0x0131) ASCII=Photos 1.0.1 @ 154, 
# 'EXIF Flash': (0x9209) Short=Flash did not fire, compulsory flash mode @ 354,
#  'EXIF FocalLengthIn35mmFilm': (0xA405) Short=29 @ 522, 
#  'Image Model': (0x0110) ASCII=iPhone 6 @ 128, 
#  'Image Orientation': (0x0112) Short=Horizontal (normal) @ 42, 
#  'EXIF DateTimeOriginal': (0x9003) ASCII=2017:06:25 09:19:46 @ 594, 
#  'EXIF ApertureValue': (0x9202) Ratio=7892/3469 @ 642, 
#  'EXIF FNumber': (0x829D) Ratio=11/5 @ 586, 
#  'EXIF ExifImageLength': (0xA003) Long=3264 @ 462, 
#  'EXIF SceneType': (0xA301) Undefined=Directly Photographed @ 486, 
#  'Image ResolutionUnit': (0x0128) Short=Pixels/Inch @ 78, 
#  'EXIF ExposureBiasValue': (0x9204) Signed Ratio=0 @ 658, 
#  'EXIF LensMake': (0xA433) ASCII=Apple @ 970, 
#  'EXIF ExposureProgram': (0x8822) Short=Program Normal @ 222, 
#  'EXIF ExposureMode': (0xA402) Short=Auto Exposure @ 498, 
#  'MakerNote Tag 0x0005': (0x0005) Signed Long=147 @ 46, 
#  'EXIF ExifImageWidth': (0xA002) Long=2448 @ 450, 
#  'MakerNote Tag 0x0014': (0x0014) Signed Long=1 @ 106, 
#  'EXIF SceneCaptureType': (0xA406) Short=Standard @ 534, 
#  'EXIF SubjectArea': (0x9214) Short=[1631, 1223, 1795, 1077] @ 674, 
#  'EXIF SubSecTimeOriginal': (0x9291) ASCII=050 @ 402, 
#  'EXIF BrightnessValue': (0x9203) Signed Ratio=18647/1866 @ 650, 
#  'EXIF LensModel': (0xA434) ASCII=iPhone 6 back camera 4.15mm f/2.2 @ 976, 
#  'EXIF DateTimeDigitized': (0x9004) ASCII=2017:06:25 09:19:46 @ 614, 
#  'EXIF FocalLength': (0x920A) Ratio=83/20 @ 666, 
#  'EXIF ExposureTime': (0x829A) Ratio=1/1721 @ 578, 
#  'Image XResolution': (0x011A) Ratio=72 @ 138, 
#  'Image Make': (0x010F) ASCII=Apple @ 122, 
#  'EXIF WhiteBalance': (0xA403) Short=Auto @ 510,
#   'MakerNote Tag 0x000E': (0x000E) Signed Long=0 @ 94,
#    'EXIF ISOSpeedRatings': (0x8827) Short=32 @ 234, 
#    'Image YResolution': (0x011B) Ratio=72 @ 146, 
#    'EXIF LensSpecification': (0xA432) Ratio=[83/20, 83/20, 11/5, 11/5] @ 938, 
#    'EXIF SensingMethod': (0xA217) Short=One-chip color area @ 474, 
#  'EXIF SubSecTimeDigitized': (0x9292) ASCII=050 @ 414}





#Test