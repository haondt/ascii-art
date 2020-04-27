import numpy as np
from skimage import io
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageEnhance

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
	for row in image:
		for col in row:
			# average subpixels
			color = np.sum(col)/col.size
			print(get_char(color), end='')
		print('')
	print(reset)
	
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
	for row in im:
		for col in row:
			# average subpixels
			color = np.sum(col)/col.size
			print(get_char(color), end='')
		print('')

def advanced_asciiify(image):
	chars = [chr(i) for i in range(32,127)]
	return _advanced_asciiify(image, 'Noto Mono for Powerline.ttf', chars)

def braillify(image):
	chars = '⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰⠱⠲⠳⠴⠵⠶⠷⠸⠹⠺⠻⠼⠽⠾⠿⡀⡁⡂'
	chars += '⡃⡄⡅⡆⡇⡈⡉⡊⡋⡌⡍⡎⡏⡐⡑⡒⡓⡔⡕⡖⡗⡘⡙⡚⡛⡜⡝⡞⡟⡠⡡⡢⡣⡤⡥⡦⡧⡨⡩⡪⡫⡬⡭⡮⡯⡰⡱⡲⡳⡴⡵⡶⡷⡸⡹⡺⡻⡼⡽⡾⡿⢀⢁⢂⢃'
	chars += '⢄⢅⢆⢇⢈⢉⢊⢋⢌⢍⢎⢏⢐⢑⢒⢓⢔⢕⢖⢗⢘⢙⢚⢛⢜⢝⢞⢟⢠⢡⢢⢣⢤⢥⢦⢧⢨⢩⢪⢫⢬⢭⢮⢯⢰⢱⢲⢳⢴⢵⢶⢷⢸⢹⢺⢻⢼⢽⢾⢿⣀⣁⣂⣃⣄'
	chars += '⣅⣆⣇⣈⣉⣊⣋⣌⣍⣎⣏⣐⣑⣒⣓⣔⣕⣖⣗⣘⣙⣚⣛⣜⣝⣞⣟⣠⣡⣢⣣⣤⣥⣦⣧⣨⣩⣪⣫⣬⣭⣮⣯⣰⣱⣲⣳⣴⣵⣶⣷⣸⣹⣺⣻⣼⣽⣾⣿'
	chars += ' '

	return _advanced_asciiify(image, 'Symbola.ttf', chars)

def _advanced_asciiify(image, fontname, char_list):
	# Find the fontsize that will make the characters the same width as the
	# pixels
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

	total_pixels = len(image)*len(image[0])
	current_pixel = 0

	for row in image:
		for col in row:
			current_pixel += 1
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
			print(best_char[1], end='')
		print('')

def compare(img1, img2):
	diff = img1-img2
	squares = np.square(diff)
	s = np.sum(squares)
	mse = s / img1.size
	return -mse

def preprocess_image(path):
	# load image into ndarray
	image = Image.open(path)
	image = image.convert('L')
	image = image.point(lambda x: 0 if x<128 else 255, '1')
	image.save('tmp.jpg')


def preprocess_advanced_asciiify(path, desired_width):
	preprocess_image(path)
	path = 'tmp.jpg'
	image = seperate_image(path, desired_width)
	advanced_asciiify(image)

def preprocess_braillify(path, desired_width):
	preprocess_image(path)
	path = 'tmp.jpg'
	image = seperate_image(path, desired_width, 1.6)
	braillify(image)

def main():
	path = '/home/noah/Pictures/flower.jpg'
	desired_width = 130

	image = seperate_image(path, desired_width)

	blockify(image)
	asciiify(image)
	advanced_asciiify(image)

	braillify(image)
	preprocess_advanced_asciiify(path, desired_width)
	preprocess_braillify(path, desired_width)




if __name__ == '__main__':
	main()
