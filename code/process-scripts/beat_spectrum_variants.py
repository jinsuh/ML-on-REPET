import nussl, os, sys

def main():
	path = sys.argv[1]
	files = os.listdir(path)

	for f in files:
		if os.path.isfile(os.path.join(path, f)):
			audio = nussl.AudioSignal(os.path.join(path, f))
			repet = nussl.Repet(audio)

			beat_spectrum = repet.get_beat_spectrum()

			repet.update_periods()
			period_simple = repet.find_repeating_period_simple(beat_spectrum, repet.min_period, repet.max_period)
			period_complex = float(repet.find_repeating_period_complex(beat_spectrum))

			# repeating_period based on the stft so is a multiple of hop, so have to convert it
			period_simple_seconds = repet.stft_params.hop_length * period_simple / audio.sample_rate
			period_complex_seconds = repet.stft_params.hop_length * period_complex / audio.sample_rate

			print 'simple = ', period_simple,'hops,', period_simple * repet.stft_params.hop_length, 'samples',  period_simple_seconds, 'seconds'
			print 'complex = ', period_complex,'hops,', period_complex * repet.stft_params.hop_length, 'samples', period_complex_seconds, 'seconds'
			
if __name__ == '__main__':
	main()