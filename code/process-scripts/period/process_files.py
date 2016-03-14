import library, sys

if __name__ == '__main__':
	if len(sys.argv) < 4:
		print 'python process_files.py [input_path] [output_path] [length]'
		exit()

	input_path = sys.argv[1]
	output_path = sys.argv[2]
	length = int(sys.argv[3])
	library.generate_repeating_files(input_path, output_path, length)