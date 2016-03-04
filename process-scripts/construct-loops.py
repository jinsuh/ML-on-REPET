import librosa, numpy as np, scipy as sp

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

sample_rate = 441000

for i in range(0, 4):
    print 'loading fg file...'
    fg, sample_rate = librosa.load('../fg/fg-0' + str(i) + '.wav', sr=sample_rate)
    print 'loading bg file...'
    bg, sample_rate = librosa.load('../bg/bg-0' + str(i) + '.wav', sr=sample_rate)

    fg = fg[:30 * 441000]

    fg_time = fg.shape[0] / sample_rate
    bg_time = bg.shape[0] / sample_rate

    new_bg = bg 

    while bg_time < fg_time:
        new_bg = np.concatenate((new_bg, bg))
        bg_time = new_bg.shape[0] / sample_rate
        print 'working...' 

    print 'writing fg' 
    wavwrite('../fg/processed/fg-0' + str(i) + '.wav', fg, sample_rate)
    print 'writing bg'
    wavwrite('../bg/processed/bg-0' + str(i) + '.wav', new_bg, sample_rate)
    
