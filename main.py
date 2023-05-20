__author__ = 'Andre'
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock
from jnius import autoclass
from audiostream import get_input
import wave
from android.permissions import request_permissions,Permission,check_permission
#
import os
 
 
 
#if not os.path.isdir("/kivyrecords/"):
#    os.mkdir("/kivyrecords/")
 
PATH = "rec_test.wav"
 
recordtime = 5
samples_per_second = 60
 
 
class RootScreen(BoxLayout): #
    pass
 
 
class RecordForm(BoxLayout): #
    b_record = ObjectProperty()
    p_bar = ObjectProperty()
 
    def start_record(self):
        self.b_record.disabled = True
        self.p_bar.max = recordtime
        REC.start()
        Clock.schedule_once(self.stop_record, recordtime)
        Clock.schedule_interval(self.update_display, 1/30.)
 
    def stop_record(self, dt):
        Clock.unschedule(self.update_display)
        self.p_bar.value = 0
        REC.stop()
        self.b_record.disabled = False
 
    def update_display(self,dt):
        self.p_bar.value = self.p_bar.value + dt
 
 
class Recorder(object):
    def __init__(self):
        # get the needed Java classes
        self.MediaRecorder = autoclass('android.media.MediaRecorder')
        self.AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        self.AudioFormat = autoclass('android.media.AudioFormat')
        self.AudioRecord = autoclass('android.media.AudioRecord')
    # define our system
        self.SampleRate = 44100
        #self.SampleRate = 16000 ; // 44100 for music
        self.ChannelConfig = self.AudioFormat.CHANNEL_IN_MONO
        #self.ChannelConfig = self.AudioFormat.CHANNEL_CONFIGURATION_MONO;
        self.AudioEncoding = self.AudioFormat.ENCODING_PCM_16BIT
        self.BufferSize = self.AudioRecord.getMinBufferSize(self.SampleRate, self.ChannelConfig, self.AudioEncoding)
        #self.outstream = self.FileOutputStream(PATH)
        self.sData = []
        self.mic = get_input(callback=self.mic_callback, source='mic', buffersize=self.BufferSize)
 
    def mic_callback(self, buf):
        self.sData.append(buf)
        print ('got : ' + str(len(buf)))
 
 
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
 
class RecordApp(App):
 
    def build(self):
        request_permissions([Permission.INTERNET, Permission.RECORD_AUDIO, Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        
        self.title = 'Recording Application'
 
if __name__ == '__main__':
    RecordApp().run()
