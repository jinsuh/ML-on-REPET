import librosa, numpy as np, scipy as sp, os, nussl, mir_eval, sqlite3, matplotlib.pyplot as plt, sys

def wavwrite(filepath, data, sr, norm=True, dtype='int16',):
    '''
    Write wave file using scipy.io.wavefile.write, converting from a float (-1.0 : 1.0) numpy array to an integer array
    
    Parameters
    ----------
    filepath : str
        The path of the output .wav file
    data : np.array
        The float-type audio array
    sr : int
        The sampling rate
    norm : bool
        If True, normalize the audio to -1.0 to 1.0 before converting integer
    dtype : str
        The output type. Typically leave this at the default of 'int16'.
    '''
    if norm:
        data /= np.max(np.abs(data))
    data = data * np.iinfo(dtype).max
    data = data.astype(dtype)
    sp.io.wavfile.write(filepath, sr, data)

def save_foreground(input_path, output_path, length, sample_rate):
    '''
    Shorten wave files to a specified length

    Parameters
    ----------
    input_path : str
        the path of the input file
    length : int
        length in seconds of the output file
    output_path : str
        the path of the output file
    '''
    print 'loading fg file...'
    fg, sample_rate = librosa.load(input_path, sr=sample_rate)
    print 'shortening fg file....'
    fg = fg[:length * sample_rate]
    print 'writing fg...' 
    wavwrite(output_path, fg, sample_rate)

def save_background(input_path, output_path, sample_rate, length=0, number_of_repeating_segments=0):
    '''
    Stitch together wave files to a specified length

    Parameters
    ----------
    input_path : str
        the path of the input file
    length : int
        length in seconds of the output file
    output_path : str
        the path of the output file
    '''
    print 'loading bg file...'
    bg, sample_rate = librosa.load(input_path, sr=sample_rate)
    print 'stitching bg file...'
    if length > 0:
        bg_length = bg.shape[0] / sample_rate
        number_of_segments = int(np.ceil(length / bg_length))
    elif number_of_repeating_segments > 0:
        number_of_segments = number_of_repeating_segments
    else:
        print 'a length or number of repeating segments must be specified'
        return
    
    result = bg
    for i in range(0, number_of_segments):
        result = np.concatenate((bg, result))

    print 'writing bg...' 
    wavwrite(output_path, result, sample_rate)

def pre_process_background(start, end):
    '''
    Process background files

    Parameters
    ----------
    start : int
        start index for numbered sound files
    end : int
        one more than the end index for numbered sound files
    '''
    for i in range(start, end):
        length = 30
        number_of_repeating_segments = 10
        save_background('../bg/bg-%02d.wav' % i, '../bg/beat-spectrum-processed/bg-%02d.wav' % i, 44100, number_of_repeating_segments=10)

def generate_repeating_files_and_compare(input_path, output_path, length):
    '''
    Generate repeating files and compare the simple method and complex method for period computation

    Parameters
    ----------
    input_path : str
        directory of source files
    output_path : str
        directory of the output repeating files
    length : float
        total time in seconds for repeating pattern
    '''
    files = os.listdir(input_path)

    for f in files:
        if os.path.isfile(os.path.join(input_path, f)):
            file_name = os.path.splitext(f)
            if file_name[1] == '.wav':
                try:
                    seed = nussl.AudioSignal(os.path.join(input_path, f))
                    print('Read {}!'.format(f))
                except:
                    print('Couldn\'t read {}'.format(f))
                    continue
                  
                original_seed = nussl.AudioSignal(audio_data_array=seed.audio_data)

                for i in range(1, 11):  
                    seed = nussl.AudioSignal(audio_data_array=original_seed.audio_data[0][:len(original_seed.audio_data[0])/i])
                    full_file_name = '%s%02d.wav' % (file_name[0], i)
                    compare_and_create_files(seed, full_file_name, length, output_path)


                for j in range(2, 11):  
                    seed = nussl.AudioSignal(audio_data_array=original_seed.audio_data[0][len(original_seed.audio_data[0]) - len(original_seed.audio_data[0])/j:])
                    full_file_name = '%s%02d.wav' % (file_name[0], j + i - 1)
                    compare_and_create_files(seed, full_file_name, length, output_path)
                    

def compare_and_create_files(seed, file_name, length, output_path):
    period_actual = float(len(seed.audio_data[0])) / float(seed.sample_rate)
    seed = create_looped_file(seed, length, file_name, output_path)
    period_simple, period_complex = compare_simple_complex_actual(seed)

    insert_result(period_actual, period_simple, period_complex, seed.sample_rate, length)

def create_looped_file(audio_signal, max_file_length, file_name, output_path):
    max_samples = int(max_file_length * audio_signal.sample_rate)

    while len(audio_signal) < max_samples:
        audio_signal.concat(audio_signal)

    audio_signal.truncate_samples(max_samples)

    new_path = os.path.join(output_path, os.path.splitext(file_name)[0] + '_repeating' + os.path.splitext(file_name)[1])
    audio_signal.write_audio_to_file(new_path, sample_rate=44100, verbose=True)
    return audio_signal

def compare_simple_complex_actual(audio_signal):
    repet = nussl.Repet(audio_signal)

    beat_spectrum = repet.get_beat_spectrum()

    repet.update_periods()
    period_simple = repet.find_repeating_period_simple(beat_spectrum, repet.min_period, repet.max_period)
    period_complex = float(repet.find_repeating_period_complex(beat_spectrum))

    # repeating_period based on the stft so is a multiple of hop, so have to convert it
    period_simple_seconds = repet.stft_params.hop_length * period_simple / audio_signal.sample_rate
    period_complex_seconds = repet.stft_params.hop_length * period_complex / audio_signal.sample_rate

    return period_simple_seconds, period_complex_seconds

    # print 'actual = ', period_actual, 'samples', float(period_actual) / audio_signal.sample_rate, 'seconds'
    # print 'simple = ', period_simple,'hops,', period_simple * repet.stft_params.hop_length, 'samples',  period_simple_seconds, 'seconds'
    # print 'complex = ', period_complex,'hops,', period_complex * repet.stft_params.hop_length, 'samples', period_complex_seconds, 'seconds'

def insert_result(period_actual, period_simple, period_complex, sample_rate, length):
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    cursor.execute('insert into results (actual_period, simple_period, complex_period, sample_rate, length) values (?, ?, ?, ?, ?)', (period_actual, period_simple, period_complex, sample_rate, length))
    conn.commit()
    conn.close()

def percent_error(experimental, actual):
    return (actual - experimental) / actual * 100
    # return 1 - np.abs(experimental / actual - np.round(experimental / actual))

def analyze_results():
    simple = []
    complex = []
    actual = []

    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    cursor.execute('select actual_period, simple_period, complex_period, sample_rate from results')
    
    for row in cursor:
        # simple_period_seconds = row[1] / row[3]
        # actual_period_seconds = row[0] / row[3]
        # complex_period_seconds = row[2] / row[3]

        simple_error = percent_error(row[1], row[0])
        # if simple_error < 200:
        if np.abs(simple_error) < 500:
            simple.append(simple_error)
        complex_error = percent_error(row[2], row[0]) 
        # if complex_error < 200:
        if np.abs(complex_error) < 500:
            complex.append(complex_error)   

        actual.append(0)   

    conn.close()

    complex_good = []
    complex_bad = []
    simple_good = []
    simple_bad = []

    for i in range(5, 101, 5):
        threshold = float(i) / 10
        good, bad = classify_percent_error(simple, threshold)
        simple_good.append(good)
        simple_bad.append(bad)

        good, bad = classify_percent_error(complex, threshold)
        complex_good.append(good)
        complex_bad.append(bad)

    print simple_good
    print complex_good

    t = [float(x) / 10 for x in range(5, 101, 5)]
    plt.title('Integer Multiple Percent Error')
    plt.xlabel('Threshold')
    plt.ylabel('Number of Files within Threshold')
    plt.plot(t, simple_good, 'r.', t, complex_good, 'b.')
    plt.show()

    # plot_data(actual, simple, complex)
    plot_hist(actual, 'Actual', 1000)
    plot_hist(simple, 'Simple', 1000)
    plot_hist(complex, 'Complex', 1000)
    plot_box_plot(simple, complex)

    print 'Simple'
    print np.mean(simple)
    print np.median(simple)
    print np.std(simple)

    print 'Complex'
    print np.mean(complex)
    print np.median(complex)
    print np.std(complex)

def classify_percent_error(data, threshold):
    good = []
    bad = []
    max_value = int(np.ceil(np.max(data)))

    for x in data:
        if classify(x, max_value, threshold):
            good.append(x)
        else:
            bad.append(x)

    return len(good), len(bad)

def classify(value, max_value, threshold):
    '''
    returns true if good and returns bad if not
    '''
    for i in range(0, max_value):
        step = i * 100

        if np.abs(value - step) <= threshold:
            return True

    return False

def plot_data(actual, simple, complex):
    plt.figure()
    t = np.arange(0, len(actual))
    plt.title('Files and Percent Error')
    plt.xlabel('File')
    plt.ylabel('Percent Error')
    plt.plot(t, actual, 'r.', t, simple, 'b.', t, complex, 'y.')
    plt.show()

def plot_box_plot(simple, complex):
    plt.figure()
    plt.ylabel('Percent Error')
    plt.boxplot([simple, complex], ['simple', 'complex'])
    plt.show()

def plot_hist(data, title, bins):
    plt.figure()
    axes = plt.gca()
    # axes.set_xlim([-100,100])
    plt.hist(data, bins=bins)
    plt.title(title)
    plt.xlabel('Percent Error')
    plt.ylabel('Number of Files')
    plt.show()
