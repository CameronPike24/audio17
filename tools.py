import numpy as np
from audiostream import get_output, AudioSample, get_input_sources, get_input
from kivy.clock import Clock
print("import libraries in tools.py")



class AudioPlayer:
    def __init__(self, channels, rate, chunk_size):
        super().__init__()
        print("class AudioPlayer:")
        self.rate = rate
        self.chunk_size = chunk_size
        # initialize the engine and get an output device; can be initialized only once
        print("self.stream = get_output")
        self.stream = get_output(
            channels=channels, rate=rate, buffersize=chunk_size, encoding=16)
        # create instance of AudioSample to handle the audio stream (output) e.g. play and stop
        
        #Find the sources for input
        self.mic_info =  get_input_sources()
        print("List of sources")
        print(*self.mic_info, sep = ", ")
        #default and mic
        
        
        self.sample = AudioSample()
        self.chunk = np.zeros(chunk_size)
        # indicator
        self.pos = 0
        self.playing = False
        self.freq = 20
        self.old_freq = self.freq
        
        
        self.samples_per_second = 60 # variables which stores the number of audio samples recorded per second
        self.audioData = [] # creates a list to store the audio bytes recorded
        #import sys
        #importlib.reload(sys.modules['audiostream']) # reloads the audiostream module - thought this might solve the problem; it doesn't!!
        #self.mic = get_input(callback=self.micCallback, rate=44100, source='default', buffersize=512, channels=1,encoding=16) # no frames received
        #self.mic = get_input(callback=self.micCallback, rate=8000, source='default', buffersize=2048) #Works but gets x\00x\00
        #self.mic = get_input(callback=self.micCallback, rate=44100, source='default', buffersize=2048) #Unable to use rate 44100, channels=1, encoder=16
        #self.mic = get_input(callback=self.micCallback, source='default', buffersize=2048) # Default is 44100 not working. try 8000, 11025, 16000, 22050, 44100, 48000
        #self.mic = get_input(callback=self.micCallback, rate=48000, source='default', buffersize=2048) # 48000 not working. try 8000, 11025, 16000, 22050, 44100, 48000
        #self.mic = get_input(callback=self.micCallback, rate=22050, source='default', buffersize=2048) # Works but gets x\00x\00
        #self.mic = get_input(callback=self.micCallback, rate=22050, source='default') # With no buffer does not work no frames
        #self.mic = get_input(callback=self.micCallback, rate=22050, source='default', buffersize=512) # does not work at all
        #self.mic = get_input(callback=self.micCallback, rate=22050, source='default', buffersize=1024) # does not work at all
        #self.mic = get_input(callback=self.micCallback, rate=22050, source='mic', buffersize=2048) # Works but gets x\00x\00
        self.mic = get_input(callback=self.micCallback, rate=22050, source='mic', buffersize=2048, channels=1) # 
        #self.mic = get_input(callback=self.micCallback, source='default')
        print("self.mic = get_input")
      
        
      
    def micCallback(self, buffer):
        print("def micCallback")
        # method which is called by the method 'get_input' to store recorded audio data (each buffer of audio samples)        
        self.audioData.append(buffer) # appends each buffer (chunk of audio data) to variable 'self.audioData'
        #print('size of frames: ' + str(len(self.audioData)))
        print('size of frames: ' + str(len(buffer)))
        print(self.audioData)
        #print ('got : ' + str(len(buf)))

    #def start(self):
        # method which begins the process of recording the audio data
        #self.mic.start() # starts the method 'self.mic' recording audio data
        #Clock.schedule_interval(self.readChunk, 1 / self.samples_per_second) # calls the method 'self.readChunk' to read and store each audio buffer (2048 samples) 60 times per second 


    def readChunk(self, sampleRate):
        print("def readChunk")
        # method which coordinates the reading and storing of the bytes from each buffer of audio data (which is a chunk of 2048 samples)
        self.mic.poll()  # calls 'get_input(callback=self.mic_....)' to read content. This byte content is then dispatched to the callback method 'self.micCallback'

    def stopmic(self):
        # method which terminates and saves the audio recording when the recording has been successful
        Clock.unschedule(self.readChunk) # un-schedules the Clock's rythmic execution of the 'self.readChunk' callback
        self.mic.stop() # stops recording audio
        return self.audioData    


        
        

    def set_freq(self, freq):
        print("def set_freq")
        self.old_freq = self.freq
        self.freq = freq
   
    def render_audio(self, pos, freq):
        print("def render_audio")
        start = pos
        end = pos + self.chunk_size
        x_audio = np.arange(start, end) / self.rate
        return np.sin(2*np.pi*freq*x_audio)

    def fade_out(self, signal, length):
        print("def fade_out")
        amp_decrease = np.linspace(1, 0, length)
        signal[-length:] *= amp_decrease
        return signal

    @staticmethod
    def get_bytes(chunk):
        print("def get_bytes")
        # chunk is scaled and converted from float32 to int16 bytes
        return (chunk * 32767).astype('int16').tobytes()
    
    def write_audio_data(self):
        print("def write_audio_data")
        self.chunk = self.get_bytes(self.chunk)
        # write bytes of chunk to internal ring buffer
        self.sample.write(self.chunk)

    def run(self):
        print("def run")
        self.stream.add_sample(self.sample)
        self.sample.play()
        self.playing = True
        self.pos = 0
        self.freq_change = False
        print("self.mic.start()")
        self.mic.start() # starts the method 'self.mic' recording audio data
        #Clock.schedule_interval(self.readChunk, 1 / self.samples_per_second) # calls the method 'self.readChunk' to read and store each audio buffer (2048 samples) 60 times per second   
        Clock.schedule_interval(self.readChunk, 0.001)      
        

        while self.playing:
            print("while self.playing:")
            self.chunk = self.render_audio(self.pos, self.old_freq)
            self.pos += self.chunk_size
            
            if self.freq != self.old_freq:
                self.chunk = self.fade_out(self.chunk, 256)
                self.pos = 0
                self.old_freq = self.freq
            print("self.write_audio_data()") 
            self.write_audio_data()

        # self.chunk = self.fade_out(
        #     self.render_audio(self.pos, self.old_freq), 256)
        # self.write_audio_data()
        # important for threading otherwise a new thread cannot be initialized
        print("self.sample.stop()")
        self.sample.stop()

    def stop(self):
        self.playing = False
