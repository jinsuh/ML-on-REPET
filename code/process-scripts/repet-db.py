import librosa, numpy as np, scipy as sp, os, nussl, mir_eval, sqlite3, main as cl

def select_repet_row(window_size, window_type=None, period=None):
	conn = sqlite3.connect('repet.db')
	cursor = conn.cursor()
	values = []

	values.append(window_size)
	values.append(window_type)
	values.append(period)

	cursor.execute('select * from repet where window_size = ? and window_type = ? and period = ?', tuple(values))
	row = cursor.fetchone()
	conn.close()

	return row

def repet_db_parameters(window_size, window_type, period):
	select_repet_row(window_size, window_type, period)
	bg, fg = cl.run_repet(window_size, window_type, period)

	new_directory = './outputs'

	if not os.path.exists(new_directory):
		os.makedirs(new_directory)

	bg.write_audio_to_file(os.path.join(new_directory, 'repet_background.wav'))
	fg.write_audio_to_file(os.path.join(new_directory, 'repet_foreground.wav'))

if __name__ == '__main__':
	repet_db_parameters(2048, 'Hamming', 160)