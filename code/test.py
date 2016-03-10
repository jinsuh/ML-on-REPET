import os
import nussl
import mir_eval

def main():
    # input audio file
    input_name = os.path.join('police_noisy.wav')
    signal = nussl.AudioSignal(path_to_input_file=input_name)

    # make a directory to store output if needed
    if not os.path.exists('./Output/'):
        os.makedirs('./Output')

    # Set up window parameters
    win = nussl.WindowAttributes(signal.sample_rate)
    win.window_length = 2048
    win.window_type = nussl.WindowType.HAMMING

    # Set up Repet
    repet = nussl.Repet(signal, repet_type=nussl.RepetType.DEFAULT, window_attributes=win)
    # repet = nussl.Repet(signal, )
    repet.period = 22
    # and Run
    repet.run()

    # Get foreground and backgroun audio signals
    bkgd, fgnd = repet.make_audio_signals()

    # and write out to files
    bkgd.write_audio_to_file(os.path.join('.', 'Output', 'repet_background.wav'))
    fgnd.write_audio_to_file(os.path.join('.', 'Output', 'repet_foreground.wav'))

def bss_eval():
    input_name = os.path.join('police_noisy.wav')
    signal = nussl.AudioSignal(path_to_input_file=input_name)
    # print type(signal.audio_data)
    (sdr, sir, sar, perm) = mir_eval.separation.bss_eval_sources(signal.audio_data, signal.audio_data)
    print sdr

if __name__ == '__main__':
    bss_eval()