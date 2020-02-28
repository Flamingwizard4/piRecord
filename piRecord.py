from __future__ import print_function
import platform, sys, os, shutil, datetime, subprocess, time, socket, random#, gspread
import numpy as np
from PIL import Image
import matplotlib.image

#validate time and recording log file

class TurtleTracker:
    def __init__(self):
        #Determine if PiCamera is attached
        self.piCamera = False
        if platform.node() == 'raspberrypi' or 'Pi' in platform.node():
            self.system = 'pi'
            from picamera import PiCamera
            self.camera = PiCamera()
            self.camera.resolution = (1296, 972)
            self.camera.framerate = 30
            self.piCamera = True
        print("Camera Working: ", self.piCamera)    
        projectID = str(random.randint(1, 9999999)) #projectID is 7 digit random number for now
        self.masterDirectory = '/home/pi/Trackers/'
        self.projectDirectory = self.masterDirectory + projectID + '/'
        self.loggerFile = self.projectDirectory + 'Logfile.txt'
        self.videoDirectory = self.projectDirectory + 'Videos/'
        
        self.masterStart = datetime.datetime.now()
        if not os.path.exists(self.projectDirectory):
            os.mkdir(self.projectDirectory)
        os.mkdir(self.videoDirectory)
        self.videoCounter = 1
        
        self.lf = open(self.loggerFile, 'a')

        self.captureVideo()
        
    def __del__(self): #when is this even called?
        #close out files and stop recording
        if self.piCamera:
            if self.camera.recording:
                self.camera.stop_recording()
                self._print('PiCamera Stopped: VideoFile=Videos/' + str(self.videoCounter).zfill(4) + '_vid.h264, Time=' + str(datetime.datetime.now()))
        self._closeFiles()
    
    def captureVideo(self, frame_delta = 5, background_delta = 60, max_frames = 20, stdev_threshold = 20):
        command = ''
        while True:            
            if self.piCamera:
                if self._video_recording() and not self.camera.recording: #what does this camera.recording do? check that the camera is working?
                    self.camera.capture(self.videoDirectory + str(self.videoCounter).zfill(4) + "_pic.jpg")
                    self.camera.start_recording(self.videoDirectory + str(self.videoCounter).zfill(4) + "_vid.h264", bitrate=7500000)
                    self._print('PiCamera Started: FrameRate=' + str(self.camera.framerate) + ', Resolution=' + str(self.camera.resolution) + ', VideoFile=Videos/' + str(self.videoCounter).zfill(4) + '_vid.h264, PicFile=Videos/' + str(self.videoCounter).zfill(4) + '_pic.jpg' + ', Time=' + str(datetime.datetime.now()))
                elif not self._video_recording() and self.camera.recording:
                    self.camera.stop_recording()
                    self._print('PiCamera Stopped: VideoFile=Videos/' + str(self.videoCounter).zfill(4) + "_vid.h264" + ', Time=' + str(datetime.datetime.now()))
                    #self._print(['rclone', 'copy', self.videoDirectory + str(self.videoCounter).zfill(4) + "_vid.h264"])
                    command = ['python3', 'Modules/processVideo.py', self.videoDirectory + str(self.videoCounter).zfill(4) + '_vid.h264']
                    command += [self.loggerFile, self.projectDirectory, self.cloudVideoDirectory]
                    self._print("Command: ", command)
                    self.processes.append(subprocess.Popen(command))
                    self.videoCounter += 1
                    _closeFiles()
                    break
 
    def _print(self, text): #logger print
        try:
            print(text, file = self.lf, flush=True)
        except:
            pass
        print(text, file = sys.stderr, flush=True)

    def _video_recording(self): #daylight check
        if datetime.datetime.now().hour >= 8 and datetime.datetime.now().hour <= 18:
            return True
        else:
            return False
        
    def _closeFiles(self):
       try:
            masterStop = datetime.datetime.now()
            timeElapsed = masterStop - self.masterStart
            self._print('MasterRecordStop: ' + str(masterStop))
            self._print("Total Time Elapsed: ", str(timeElapsed))
            self.lf.close()
       except AttributeError:
           pass
       try:
           if self.system == 'mac':
               self.caff.kill()
       except AttributeError:
           pass

tracker = TurtleTracker()