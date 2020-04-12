import sys
import math
import io
import operator
import numpy as np
import urllib.request
from PIL import Image


import math


EarthRadius = 6378137
MinLat = -85.05112878
MaxLat = 85.05112878
MinLong = -180
MaxLong = 180


def clip(n, minval, maxval):
	return min(max(n, minval), maxval)



def mapSize(level):
	return 256 << level



def groundResolution(latitude, level):
	latitude = clip(latitude, MinLat, MaxLat)
	return math.cos(latitude*math.pi / 180) * 2 * math.pi * EarthRadius / mapSize(level)



def mapScale(latitude, level, dpi):
	return groundResolution(latitude, level) * dpi/0.0254



def latLongToPixelXY(latitude, longitude, level):
	latitude = clip(latitude, MinLat, MaxLat)
	longitude = clip(longitude, MinLong, MaxLong)

	x1 = (longitude + 180) / 360
	sinlat = math.sin(latitude * math.pi / 180)
	x2 = 0.5 - math.log((1 + sinlat) / (1 - sinlat)) / (4 * math.pi)

	size_level = mapSize(level)
	pixelX = int(clip(x1 * size_level + 0.5, 0, size_level - 1))
	pixelY = int(clip(x2 * size_level + 0.5, 0, size_level - 1))

	return pixelX, pixelY



def pixelXYToTileXY(pixelX, pixelY):
	x1 = int(pixelX / 256)
	x2 = int(pixelY / 256)
	return x1, x2



def tileXYToQuadKey(tileX, tileY, level):
	key = ""
	for k in range(level, 0, -1):
		digit = '0'
		j = 1 << (k-1)
		if ((tileX & j) != 0):
			digit = chr(ord(digit) + 1)
		if ((tileY & j) != 0):
			digit = chr(ord(digit) + 1)
			digit = chr(ord(digit) + 1)
		key += digit

	return key



def latLongToTileXY(latitude, longitude, level):
	x1, x2 = latLongToPixelXY(latitude, longitude, level)
	y1, y2 = pixelXYToTileXY(x1, x2)

	return y1, y2

TILE_SIZE = 256 			# number of pixels per tile per edge

def getURL(quadkey):
	# To get license_key, see https://msdn.microsoft.com/en-us/library/ff428642.aspx
	license_key = "Akk7WP-w0TJrlJV0Kl5JO9gutSR1_ox5BEqIgs3iDdFdp4KZB7UlJp5FcEo2BTMW"
	return "http://h0.ortho.tiles.virtualearth.net/tiles/h%s.jpeg?g=131&key=%s" % (quadkey, license_key)


def getImageFromQuadkey(quadkey):
	with urllib.request.urlopen(getURL(quadkey)) as response:
		read_img = Image.open(io.BytesIO(response.read()))
	return read_img


def getLowestLevel(lat1, lon1, lat2, lon2):
	for k in range(23, 0, -1):
		x1, y1 = latLongToTileXY(lat1, lon1, k)
		x2, y2 = latLongToTileXY(lat2, lon2, k)
		if x1 > x2:
			x1, x2 = x2, x1
		if y1 > y2:
			y1, y2 = y2, y1

		# The lowest acceptable level is the level where the bounding box is within only one same tile.
		if (x2 - x1 <= 1) and (y2 - y1 <= 1):
			print("The lowest acceptable level is: ")
			print(k)
			return k
	print("Error: Improper bounding box.")



def nullImage(img):
	point = (img == Image.open('null.jpeg'))
	return point



def findBestLevel(lat1, lon1, lat2, lon2, minlevel):
	# set UPPER_SIZE as the size limit of the desired image, in case it is too large to open efficiently.
	UPPER_SIZE = 1 << 12 		# 4096 pixels

	m = 23

	# select the level, iterated from the finest one to the lowest acceptable one
	while m >= minlevel:
		print ("Check quality in level: ")
		print (m)
		point = True
		x1, y1 = latLongToTileXY(lat1, lon1, m)
		x2, y2 = latLongToTileXY(lat2, lon2, m)
		if x1 > x2:
			x1, x2 = x2, x1
		if y1 > y2:
			y1, y2 = y2, y1

		# filter out the "overfine" levels in case of too big images
		if (x2 - x1) * TILE_SIZE > UPPER_SIZE:
			m = m - 1
			continue

		# filter out the level as long as where exists even one null image
		for j in range(x1, x2+1):
			for k in range(y1, y2+1):
				curr_key = tileXYToQuadKey(j, k, m)
				curr_img = getImageFromQuadkey(curr_key)
				if nullImage(curr_img):
					point = False
					print("can't find tile:")
					print("(%d, %d)" % (j,k))
					print("at the level:")
					print(m)
					break
			if point == False:
				break

		if point == True:
			break
		m = m - 1

	if point == True:
		print("Finally at level: %d" % m)
		return m, x1, y1, x2, y2
	else:
		print("Error: No acceptable level. Please re-select the bounding box.")





def main():
	## user input parameters
	lat1 = float(sys.argv[1])
	lon1 = float(sys.argv[2])
	lat2 = float(sys.argv[3])
	lon2 = float(sys.argv[4])

	## determine the lowest acceptable level
	minlevel = getLowestLevel(lat1, lon1, lat2, lon2)

	## determine the final best level
	l, tx1, ty1, tx2, ty2 = findBestLevel(lat1, lon1, lat2, lon2, minlevel)

	## generte image
	width = (tx2 - tx1 + 1) * TILE_SIZE
	height = (ty2 - ty1 + 1) * TILE_SIZE
	image = Image.new('RGB', (width, height))

	for x in range(tx1, tx2+1):
		for y in range(ty1, ty2+1):
			curr_quadkey = tileXYToQuadKey(x, y, l) 		# query and paste every tile image orderly
			curr_image = getImageFromQuadkey(curr_quadkey)
			start_x = (x - tx1) * TILE_SIZE
			start_y = (y - ty1) * TILE_SIZE
			end_x = start_x + TILE_SIZE
			end_y = start_y + TILE_SIZE

			image.paste(curr_image, (int(start_x), int(start_y), int(end_x), int(end_y)))

	print("Image successfully generated.")


	## crop the image
	px1, py1 = latLongToPixelXY(lat1, lon1, l) 		# px1, py1 is the global pixel coordinates of the upper left point
	base_x = tx1 * TILE_SIZE 						# base_x, base_y is the global pixel coordinates of the upper left pixel in the upper left tile
	base_y = ty1 * TILE_SIZE
	d_x1 = px1 - base_x 							# d_x1, d_y1 is the displacement coodinates of the upper left point relative to the base pixel
	d_y1 = py1 - base_y

	px2, py2 = latLongToPixelXY(lat2, lon2, l)
	d_x2 = px2 - base_x
	d_y2 = py2 - base_y

	output = image.crop((d_x1, d_y1, d_x2, d_y2))
	print("Image successfully cropped.")
	output.save("result.jpg")




if __name__ == '__main__':
	main()
