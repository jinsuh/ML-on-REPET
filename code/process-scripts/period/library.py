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

def generate_repeating_files(input_path, output_path, length):
    '''

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
                    create_looped_file(seed, length, full_file_name, output_path)

def create_looped_file(audio_signal, max_file_length, file_name, output_path):
    max_samples = int(max_file_length * audio_signal.sample_rate)

    while len(audio_signal) < max_samples:
        audio_signal.concat(audio_signal)

    audio_signal.truncate_samples(max_samples)

    new_path = os.path.join(output_path, os.path.splitext(file_name)[0] + '_repeating' + os.path.splitext(file_name)[1])
    audio_signal.write_audio_to_file(new_path, sample_rate=44100, verbose=True)

