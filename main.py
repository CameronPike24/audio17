import threading
from kivy.app import App
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, LinePlot
import numpy as np
#from android_permissions import AndroidPermissions
from android.permissions import request_permissions,Permission,check_permission

from kivy.properties import ObjectProperty
from kivy.clock import Clock
from jnius import autoclass
from audiostream import get_input
import wave
#
import os


from tools import AudioPlayer
print("imported tools")

PATH = "rec_test.wav"
 
recordtime = 5
samples_per_second = 60

class Recorder(object):
    def __init__(self):
        # get the needed Java classes
        self.MediaRecorder = autoclass('android.media.MediaRecorder')
        self.AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        self.AudioFormat = autoclass('android.media.AudioFormat')
        self.AudioRecord = autoclass('android.media.AudioRecord')
    # define our system
        self.SampleRate = 44100
        self.ChannelConfig = self.AudioFormat.CHANNEL_IN_MONO
        self.AudioEncoding = self.AudioFormat.ENCODING_PCM_16BIT
        self.BufferSize = self.AudioRecord.getMinBufferSize(self.SampleRate, self.ChannelConfig, self.AudioEncoding)
        #self.outstream = self.FileOutputStream(PATH)
        self.sData = []
        self.mic = get_input(callback=self.mic_callback, source='mic', buffersize=self.BufferSize)
 
    def mic_callback(self, buf):
        self.sData.append(buf)
        print ('got : ' + str(len(buf)))
        print(self.sData)
 
 
    def start(self):
        self.mic.start()
        Clock.schedule_interval(self.readbuffer, 1/samples_per_second)
 
    def readbuffer(self, dt):
        self.mic.poll()
 
    def dummy(self, dt):
        print ("dummy")
 
    def stop(self):
        Clock.schedule_once(self.dummy, 0.5)
        Clock.unschedule(self.readbuffer)
        self.mic.stop()
        wf = wave.open(PATH, 'wb')
        wf.setnchannels(self.mic.channels)
        wf.setsampwidth(2)
        wf.setframerate(self.mic.rate)
        wf.writeframes(b''.join(self.sData))
        wf.close()
 
REC = Recorder()





class MainApp(App):

    def build(self):
        print("request_permissions")
        #request_permissions([Permission.INTERNET, Permission.RECORD_AUDIO])
        
        request_permissions([Permission.INTERNET, Permission.RECORD_AUDIO,Permission.READ_EXTERNAL_STORAGE,Permission.WRITE_EXTERNAL_STORAGE])
        self.app = MainGrid()       
        print("self.app = MainGrid()")

        return self.app
        
    #def on_start(self, *args):
        #self.dont_gc = AndroidPermissions(self.start_app)

    #def start_app(self):
        #self.dont_gc = None        
        
        
        
        

    def init_thread(self):
        print("def init_thread")
        '''
        self.playback_thread = threading.Thread(target=self.app.player.run)
        # daemon threads don't wait for main thread
        self.playback_thread.setDaemon(True)
        self.playback_thread.start()
        print("Playback Thread", self.playback_thread.native_id, "started")
        print("Main Thread", threading.main_thread().native_id)
        '''
        REC.start()
        #Clock.schedule_once(self.stop_record, recordtime)
        #Clock.schedule_interval(self.update_display, 1/30.)        
        
        
        

    def exit_thread(self):
        '''
        self.playback_thread.join()
        print("Playback Thread", self.playback_thread.native_id, "stopped")
        '''
        #Clock.unschedule(self.update_display)
        #self.p_bar.value = 0
        REC.stop()
        #self.b_record.disabled = False

class MainGrid(BoxLayout):
    

    zoom = NumericProperty(1)
    print("class MainGrid")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.samples = 1024
        self.zoom = 1
        print("self.graph = Graph")
        self.graph = Graph(y_ticks_major=0.5,
                           x_ticks_major=64,
                           border_color=[0, 1, 1, 1],
                           tick_color=[0, 1, 1, 0.7],
                           x_grid=True, y_grid=True,
                           xmin=0, xmax=self.samples,
                           ymin=-1.0, ymax=1.0,
                           draw_border=False,
                           x_grid_label=True, y_grid_label=False)
        # Mono, Sampling Rate, Chunksize
        print("self.player = AudioPlayer(1, 44100, self.samples)")
        #self.player = AudioPlayer(1, 44100, self.samples)
        self.player = AudioPlayer(1, 22050, self.samples)
        self.ids.modulation.add_widget(self.graph)
        self.plot_x = np.linspace(0, 1, self.samples)
        self.plot_y = np.zeros(self.samples)
        self.plot = LinePlot(color=[1, 1, 0, 1], line_width=1.5)
        self.old_freq = 0
        self.freq = 0
        # adds plot to the graph widget
        print("self.graph.add_plot(self.plot)")
        self.graph.add_plot(self.plot)
        self.update_plot(1)

    def update_plot(self, freq):
        print("def update_plot")
        self.plot_y = np.sin(2*np.pi*freq*self.plot_x)
        # draws plot
        self.plot.points = [(x, self.plot_y[x]) for x in range(self.samples)]

    def update_zoom(self, value):
        print("def update_zoom")
        if value == '+' and self.zoom < 8:
            self.zoom *= 2
            self.graph.x_ticks_major /= 2
        elif value == '-' and self.zoom > 1:
            self.zoom /= 2
            self.graph.x_ticks_major *= 2

    def play_result(self):
        print("def play_result")
        if self.ids.play.state == 'down':
            self.ids.play.text = '[b]STOP[/b]'            
            App.get_running_app().init_thread()
        else:
            self.ids.play.text = '[b]PLAY[/b]'
            self.player.stop()
            App.get_running_app().exit_thread()


MainApp().run()
