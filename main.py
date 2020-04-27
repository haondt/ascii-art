import numpy as np
import json
from skimage import io
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageEnhance
import argparse

# Terminology:
# The program converts an nxm image to various ascii art forms of size axb.
# The first step is to seperate the nxm pixels of the original image (hereby
# referred to as "subpixels") into axb groups. The groups are referred to as
# "pixels".

# convert the image to grayscale and seperate pixels into blocks matching desired scale
def seperate_image(path, desired_width, ratio=2):
	# ratio=  character height / width

	# load image into ndarray
	image = io.imread(path)


	# actual image height/width
	height_over_width = len(image)/len(image[0])

	# desired image height
	desired_height = desired_width * height_over_width

	# desired image height taking into account character ratio
	desired_height = int(round(desired_height / ratio))

	if type(image[0][0]) == np.ndarray:
		# formula for grayscale
		# gray = r*0.2125 + g*0.7154 + b*0.0721
		consts = np.array([0.2125, 0.7154, 0.0721])

		# grayscaleify each pixel
		image = np.tensordot(consts, image, (0,2))

	# group blocks of subpixels in pixel groups
	input_rows_per_output_row = len(image)/desired_height
	input_cols_per_output_col = len(image[0])/desired_width
	output_matrix = []
	for output_row in range(desired_height):
		out_row = []
		input_row_start = int(round(output_row*input_rows_per_output_row))
		input_row_end = int(round(input_row_start + input_rows_per_output_row))
		input_rows = image[input_row_start:input_row_end]
		for output_col in range(desired_width):
			input_col_start = int(round(output_col*input_cols_per_output_col))
			input_col_end = int(round(input_col_start + input_cols_per_output_col))
			output_cell = []
			for input_row in input_rows:
				output_cell.append(input_row[input_col_start:input_col_end])
			out_row.append(output_cell)
		output_matrix.append(out_row)

	return np.array(output_matrix)

# draw the image using the block (█) character and ansi escape codes
def blockify(image):
	# define some characters and escape codes
	char = '█'
	esc = u'\u001b['
	reset = esc + '0m'

	# define a function to scale the color value (0-255) to the available
	# grayscale terminal colors (232-255)
	color_scale = lambda x: int(round(((x/255)*23)+232))

	# define a function that converts the color value (0-255) to the
	# corresponding printable character
	get_char = lambda x: esc + '38;5;{}m'.format(color_scale(x)) + char

	# Go through each pixel of image
	outstr = ''
	for row in image:
		for col in row:
			# average subpixels
			color = np.sum(col)/np.array(col).size
			outstr += get_char(color)
		outstr += '\n'
	outstr += reset
	
	return outstr
	
# draw the image using ascii characters. Simply finds the ascii character with
# the closest average brightness
def asciiify(im):
	# Create dictionary mapping ascii characters to their average color
	fnt = ImageFont.truetype('Noto Mono for Powerline.ttf',15)
	charset = {}
	for i in range(32,127):
		img = Image.new('RGB', (10,17), color='white')
		d = ImageDraw.Draw(img)
		char = chr(i)
		d.text((0,0), char, font=fnt, fill='black')
		img = np.array(img)
		charset[int(round(np.sum(img)/img.size))] = char

	# define brightest, darkest and range of characters
	min_val = min(charset.keys())
	max_val = max(charset.keys())
	val_range = max_val-min_val

	# define function to scale pixel color (0-255) to available ascii
	# character brightnesses
	color_scale = lambda x: int(round((((255-x)/255)*val_range)+min_val))
	
	# define function to convert pixel color (0-255) to closest average
	# brightness ascii character
	get_char = lambda x: charset[min(charset.keys(), key=lambda y: abs(y-color_scale(x)))]

	# go through each pixel of image
	outstr = ''
	for row in im:
		for col in row:
			# average subpixels
			color = np.sum(col)/col.size
			outstr += get_char(color)
		outstr += '\n'
	return outstr

# draw the image using ascii characters. See _advanced_asciiify.
def advanced_asciiify(image):
	chars = [chr(i) for i in range(32,127)]
	return _advanced_asciiify(image, 'Noto Mono for Powerline.ttf', chars)

# create a binary search tree of braille characters
def load_braille_dict():
	try:
		with open('bd.json', 'r') as f:
			return json.loads(f.read())
	except:
		chars = '⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰⠱⠲⠳⠴⠵⠶⠷⠸⠹⠺⠻⠼⠽⠾⠿⡀⡁⡂'
		chars += '⡃⡄⡅⡆⡇⡈⡉⡊⡋⡌⡍⡎⡏⡐⡑⡒⡓⡔⡕⡖⡗⡘⡙⡚⡛⡜⡝⡞⡟⡠⡡⡢⡣⡤⡥⡦⡧⡨⡩⡪⡫⡬⡭⡮⡯⡰⡱⡲⡳⡴⡵⡶⡷⡸⡹⡺⡻⡼⡽⡾⡿⢀⢁⢂⢃'
		chars += '⢄⢅⢆⢇⢈⢉⢊⢋⢌⢍⢎⢏⢐⢑⢒⢓⢔⢕⢖⢗⢘⢙⢚⢛⢜⢝⢞⢟⢠⢡⢢⢣⢤⢥⢦⢧⢨⢩⢪⢫⢬⢭⢮⢯⢰⢱⢲⢳⢴⢵⢶⢷⢸⢹⢺⢻⢼⢽⢾⢿⣀⣁⣂⣃⣄'
		chars += '⣅⣆⣇⣈⣉⣊⣋⣌⣍⣎⣏⣐⣑⣒⣓⣔⣕⣖⣗⣘⣙⣚⣛⣜⣝⣞⣟⣠⣡⣢⣣⣤⣥⣦⣧⣨⣩⣪⣫⣬⣭⣮⣯⣰⣱⣲⣳⣴⣵⣶⣷⣸⣹⣺⣻⣼⣽⣾⣿'
		chars += ' '


		braille_chars = '⠁⠈⠂⠐⠄⠠⡀⢀'

		braille_imgs = []
		fontname = 'Symbola.ttf'
		fnt = ImageFont.truetype(fontname, 14)
		for char in braille_chars:
			img = Image.new('RGB', (30,30), color='white')
			d = ImageDraw.Draw(img)
			d.text((0,0), char, font=fnt, fill='black')
			arr = np.average(np.array(img),2) # average the colors to make grayscale
			braille_imgs.append(arr)
		

		output = {}
		for char in chars:
			direction  = []
			img = Image.new('RGB', (30,30), color='white')
			d = ImageDraw.Draw(img)
			d.text((0,0), char, font=fnt, fill='black')
			arr = np.average(np.array(img),2) # average the colors to make grayscale
			for bi in braille_imgs:
				match = False
				for row_i in range(len(arr)):
					for col_i in range(len(arr[0])):
						if bi[row_i][col_i] < 100:
							if arr[row_i][col_i] < 100:
								match = True
								break
					if match:
						break
				if match:
					direction.append('1')
				else:
					direction.append('0')

			spot = output
			for i in direction[:-1]:
				if i not in spot:
					spot[i] = {}
				spot = spot[i]
			spot[direction[-1]] = char
		
		with open('bd.json', 'w') as f:
			f.write(json.dumps(output))
		return output




# draw the image using unicode braille symbols. See _advanced_asciiify.
def braillify(image):
	chars = '⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰⠱⠲⠳⠴⠵⠶⠷⠸⠹⠺⠻⠼⠽⠾⠿⡀⡁⡂'
	chars += '⡃⡄⡅⡆⡇⡈⡉⡊⡋⡌⡍⡎⡏⡐⡑⡒⡓⡔⡕⡖⡗⡘⡙⡚⡛⡜⡝⡞⡟⡠⡡⡢⡣⡤⡥⡦⡧⡨⡩⡪⡫⡬⡭⡮⡯⡰⡱⡲⡳⡴⡵⡶⡷⡸⡹⡺⡻⡼⡽⡾⡿⢀⢁⢂⢃'
	chars += '⢄⢅⢆⢇⢈⢉⢊⢋⢌⢍⢎⢏⢐⢑⢒⢓⢔⢕⢖⢗⢘⢙⢚⢛⢜⢝⢞⢟⢠⢡⢢⢣⢤⢥⢦⢧⢨⢩⢪⢫⢬⢭⢮⢯⢰⢱⢲⢳⢴⢵⢶⢷⢸⢹⢺⢻⢼⢽⢾⢿⣀⣁⣂⣃⣄'
	chars += '⣅⣆⣇⣈⣉⣊⣋⣌⣍⣎⣏⣐⣑⣒⣓⣔⣕⣖⣗⣘⣙⣚⣛⣜⣝⣞⣟⣠⣡⣢⣣⣤⣥⣦⣧⣨⣩⣪⣫⣬⣭⣮⣯⣰⣱⣲⣳⣴⣵⣶⣷⣸⣹⣺⣻⣼⣽⣾⣿'
	chars += ' '



	return _advanced_asciiify(image, 'Symbola.ttf', chars)

# braillify image using much faster algorithm. Compare pixel to 8 single-point
# braille characters and use a binary search tree to select character instead of
# testing all 256 characters.
def fast_braillify(image):
	# Find the fontsize that will make the characters the same width as the
	# pixels
	# If you can't see this symbol, your viewer does not support powerline
	# symbols. This is ok and will not alter the functionality of the program.
	testchar = ''
	test_fontname = 'Noto Mono for Powerline.ttf'
	char_width = len(image[0][0][0])
	char_height = len(image[0][0])
	fontsize = 0
	for i in range(1,72):
		img = Image.new('RGB', (char_width, char_height), color='white')
		d = ImageDraw.Draw(img)
		fnt = ImageFont.truetype(test_fontname, i)
		d.text((0,0), testchar, font=fnt, fill='black')
		arr = np.array(img)
		if sum(arr[0][-1]) < 200:
			fontsize = i
			break

	braille_dict = load_braille_dict()
	braille_chars = ' ⠁⠈⠂⠐⠄⠠⡀⢀'

	braille_imgs = []
	fontname = 'Symbola.ttf'
	fnt = ImageFont.truetype(fontname, fontsize)
	for char in braille_chars:
		img = Image.new('RGB', (char_width, char_height), color='white')
		d = ImageDraw.Draw(img)
		d.text((0,0), char, font=fnt, fill='black')
		arr = np.average(np.array(img),2) # average the colors to make grayscale
		braille_imgs.append(arr)

	outstr = ''
	for row in image:
		for col in row:
			direction = ''
			base_score = compare(braille_imgs[0],col)
			for img in braille_imgs[1:]:
				charscore = compare(img, col)
				if charscore < base_score:
					direction += '1'
				else:
					direction += '0'
			outstr += braille_dict \
				[direction[0]] \
				[direction[1]] \
				[direction[2]] \
				[direction[3]] \
				[direction[4]] \
				[direction[5]] \
				[direction[6]] \
				[direction[7]]
		outstr += '\n'
	return outstr

# draw the image using the given characters. Find the best character to
# represent a given pixel by comparing each pixel of the character with the
# subpixels of the image pixel
def _advanced_asciiify(image, fontname, char_list):
	# Find the fontsize that will make the characters the same width as the
	# pixels
	# If you can't see this symbol, your viewer does not support powerline
	# symbols. This is ok and will not alter the functionality of the program.
	testchar = ''
	test_fontname = 'Noto Mono for Powerline.ttf'
	char_width = len(image[0][0][0])
	char_height = len(image[0][0])
	fontsize = 0
	for i in range(1,72):
		img = Image.new('RGB', (char_width, char_height), color='white')
		d = ImageDraw.Draw(img)
		fnt = ImageFont.truetype(test_fontname, i)
		d.text((0,0), testchar, font=fnt, fill='black')
		arr = np.array(img)
		if sum(arr[0][-1]) < 200:
			fontsize = i
			break
	
	# generate a grayscale image for each ascii character
	fnt = ImageFont.truetype(fontname, fontsize)
	chars = []
	for char in char_list:
		img = Image.new('RGB', (char_width, char_height), color='white')
		d = ImageDraw.Draw(img)
		d.text((0,0), char, font=fnt, fill='black')
		arr = np.average(np.array(img),2) # average the colors to make grayscale
		chars.append((arr, char))


	# Find the best matching symbol for each pixel
	outstr = ''
	for row in image:
		for col in row:
			best_score = None
			best_char = None
			for char in chars:
				score = compare(char[0], col)
				if best_score == None:
					best_score = score
					best_char = char
				elif score < best_score:
					best_score = score
					best_char = char
			outstr += best_char[1]
		outstr += '\n'
	return outstr

# Compare two images of the same shape
def compare(img1, img2):
	diff = img1-img2
	squares = np.square(diff)
	s = np.sum(squares)
	mse = s / img1.size

	# multiplying the mean square error by -1 will invert the output
	return -mse

# use pillow to change the input image to black and white pixels only before
# processing
def preprocess_image(path):
	# load image into ndarray
	image = Image.open(path)
	image = image.convert('L')
	image = image.point(lambda x: 0 if x<128 else 255, '1')
	image.save('tmp.jpg')


# preprocess the image before calling advanced_asciiify
def preprocess_asciiify(path, desired_width):
	preprocess_image(path)
	path = 'tmp.jpg'
	image = seperate_image(path, desired_width)
	return advanced_asciiify(image)

# preprocess the image before calling braillify
def preprocess_braillify(path, desired_width):
	preprocess_image(path)
	path = 'tmp.jpg'
	image = seperate_image(path, desired_width)
	return fast_braillify(image)


def main():

	# Set up command line parser
	parser = argparse.ArgumentParser(description='Convert images to ascii art')
	parser.add_argument('-i',metavar='input.jpg', type=str, required=True,
		help='source image file')
	parser.add_argument('-o',nargs='?', metavar='output.txt', type=str,
		help='output txt file')
	parser.add_argument('-w', '--width',nargs='?', metavar='W', type=int, default=130,
		help='output image width')
	parser.add_argument('-k', '--blockify', action='store_true', default=False,
		help='generate the image using the block symbol and ansi escape codes')
	parser.add_argument('-a', '--asciiify', action='store_true', default=False,
		help='generate the image using ascii symbols')
	parser.add_argument('-A', '--advanced-asciiify', action='store_true',
		default=False, help='generate the image using ascii symbols, and a \
		refined method')
	parser.add_argument('-b', '--braillify', action='store_true',
		default=False, help='generate the image using unicode braille symbols')
	parser.add_argument('-p', '--preprocessed-asciiify', action='store_true',
		default=False, help='preprocess the image before asciiifying it with a \
		refined method')
	parser.add_argument('-P', '--preprocessed-braillify', action='store_true',
		default=False, help='preprocess the image before braillifying it with \
		a refined method')

	args = parser.parse_args()
	
	# pull info from parser
	path = args.i
	desired_width = args.width
	image = seperate_image(path, desired_width)

	# Append generations to output depending on args
	outstr = ''
	if args.blockify:
		outstr += '\n'
		outstr += blockify(image)

	if args.asciiify:
		outstr += '\n'
		outstr += asciiify(image)

	if args.advanced_asciiify:
		outstr += '\n'
		outstr += advanced_asciiify(image)
	
	if args.braillify:
		outstr += '\n'
		outstr += fast_braillify(image)

	if args.preprocessed_asciiify:
		outstr += '\n'
		outstr += preprocess_asciiify(path, desired_width)

	if args.preprocessed_braillify:
		outstr += '\n'
		outstr += preprocess_braillify(path, desired_width)

	# Save or display output
	if args.o is not None:
		with open(args.o, 'w+') as f:
			f.write(outstr)
	else:
		print(outstr)

if __name__ == '__main__':
	main()
