#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMediaWebCam.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   CeibalJAM! - Uruguay
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys, os, gtk, pygtk, gobject, gst, pygst, time, datetime, commands

import JAMediaGlobals as G

gobject.threads_init()
gtk.gdk.threads_init()

class JAMediaWebCam():
	def __init__(self, ventana_id):
		self.pipeline= None
		self.ventana_id= ventana_id
		self.estado= None

		# pads
		self.camara=  None
		self.multi= None
		self.hilovideoapantalla= None
		self.pantalla= None
		self.hiloencodearvideo= None
		self.theoraenc= None
		self.alsasrc= None
		self.capaaudio= None
            	self.filtroaudio= None
		self.hilofiltro= None
		self.audioconvert= None
		self.vorbisenc= None
		self.hilovideomuxor= None
		self.hiloaudiomuxor= None
		self.oggmux= None
		self.hiloarchivo= None
		self.archivo= None
		self.scale= None
		self.scalecapsfilter= None
		self.scalecaps= None
		self.colorspace= None

		# links
		self.camaramultihilo= None
		self.visorwebcam= None
		self.encodearvideo= None
		self.encodearaudio= None
		self.archivar= None

		# config
		self.device= "/dev/video0"
		self.resolucion= "video/x-raw-yuv,width=320,height=240"
		self.audio= "audio/x-raw-int,rate=16000,channels=1,depth=16"

		self.set_pipeline()

	def on_sync_message(self, bus, message):
        	if message.structure is None:
            		return
        	if message.structure.get_name() == 'prepare-xwindow-id':
            		gtk.gdk.threads_enter()
            		gtk.gdk.display_get_default().sync()
			message.src.set_xwindow_id(self.ventana_id)
            		message.src.set_property("force-aspect-ratio", True)
			#message.src.set_property("force-aspect-ratio", False)
			message.src.set_property("sync", False)
            		gtk.gdk.threads_leave()

    	def on_message(self, bus, message):
        	if message.type == gst.MESSAGE_ERROR:
            		err, debug = message.parse_error()
            		print "ERROR ON_MESSAGE: ", err, debug

	def play(self, widget= None, event= None):
		self.pipeline.set_state(gst.STATE_PLAYING)

	def stop(self, widget= None, event= None):
		self.pipeline.set_state(gst.STATE_PAUSED)
		self.pipeline.set_state(gst.STATE_NULL)
		try:
			gst.element_unlink_many(self.multi, self.hiloencodearvideo, self.scale, self.scalecapsfilter, self.colorspace,
			self.theoraenc, self.hilovideomuxor, self.oggmux)

			gst.element_unlink_many(self.alsasrc, self.audiorate, self.filtroaudio, self.hilofiltro, self.audioconvert,
			self.vorbisenc, self.hiloaudiomuxor, self.oggmux)

			gst.element_unlink_many(self.oggmux, self.hiloarchivo, self.archivo)

			self.pipeline.remove(self.hiloencodearvideo, self.scale, self.scalecapsfilter, self.colorspace, self.theoraenc,
			self.hilovideomuxor, self.oggmux, self.alsasrc, self.audiorate, self.filtroaudio, self.hilofiltro,
			self.audioconvert, self.vorbisenc, self.hiloaudiomuxor, self.hiloarchivo, self.archivo)
		except:
			pass
		self.estado= None
		self.set_pipeline()

	def stopaudio(self, widget= None, event= None):
		self.pipeline.set_state(gst.STATE_PAUSED)
		self.pipeline.set_state(gst.STATE_NULL)
		try:
			gst.element_unlink_many(self.alsasrc, self.audiorate, self.filtroaudio, self.hilofiltro,
			self.audioconvert, self.vorbisenc, self.hiloaudiomuxor, self.oggmux)

			gst.element_unlink_many(self.oggmux, self.hiloarchivo, self.archivo)

			self.pipeline.remove(self.oggmux, self.alsasrc, self.audiorate, self.filtroaudio, self.hilofiltro,
			self.audioconvert, self.vorbisenc, self.hiloaudiomuxor, self.hiloarchivo, self.archivo)
		except:
			pass
		self.estado= None
		self.set_pipeline()

	def get_fotografia(self):
		self.pipeline.set_state(gst.STATE_PAUSED)
		self.pipeline.set_state(gst.STATE_NULL)
		#self.stop()
		fecha= datetime.date.today()
		hora= time.strftime("%H-%M-%S")
		archivo= os.path.join(G.DIRECTORIOFOTOS,"%s-%s.png" % (fecha, hora))
		comando= 'gst-launch-0.10 v4l2src ! ffmpegcolorspace ! pngenc ! filesink location=%s' % (archivo)
		commands.getoutput(comando)
		self.set_pipeline()
		self.play()
		#return archivo

	def grabar(self, widget= None, event= None):
		self.pipeline.set_state(gst.STATE_PAUSED)
		self.pipeline.set_state(gst.STATE_NULL)
		#self.stop()
		fecha= datetime.date.today()
		hora= time.strftime("%H-%M-%S")
		archivo= os.path.join(G.DIRECTORIOVIDEOS,"%s-%s.ogg" % (fecha, hora))
		self.archivo.set_property("location", archivo)

		self.pipeline.add(self.hiloencodearvideo, self.scale, self.scalecapsfilter, self.colorspace, self.theoraenc,
			self.hilovideomuxor, self.oggmux, self.alsasrc, self.audiorate, self.filtroaudio, self.hilofiltro, self.audioconvert,
			self.vorbisenc, self.hiloaudiomuxor, self.hiloarchivo, self.archivo)

		self.encodearvideo= gst.element_link_many(self.multi, self.hiloencodearvideo,
			self.scale, self.scalecapsfilter, self.colorspace, self.theoraenc, self.hilovideomuxor, self.oggmux)

		self.encodearaudio= gst.element_link_many(self.alsasrc, self.audiorate, self.filtroaudio, self.hilofiltro,
			self.audioconvert, self.vorbisenc, self.hiloaudiomuxor, self.oggmux)

		self.archivar= gst.element_link_many(self.oggmux, self.hiloarchivo, self.archivo)

		self.estado= "Grabando"
		self.play()

	def grabarsoloaudio(self, widget= None, event= None):
		self.pipeline.set_state(gst.STATE_PAUSED)
		self.pipeline.set_state(gst.STATE_NULL)
		#self.stop()
		fecha= datetime.date.today()
		hora= time.strftime("%H-%M-%S")
		archivo= os.path.join(G.DIRECTORIOAUDIO,"%s-%s.ogg" % (fecha, hora))
		self.archivo.set_property("location", archivo)

		self.pipeline.add(self.oggmux, self.alsasrc, self.audiorate, self.filtroaudio, self.hilofiltro, self.audioconvert,
			self.vorbisenc, self.hiloaudiomuxor, self.hiloarchivo, self.archivo)

		self.encodearaudio= gst.element_link_many(self.alsasrc, self.audiorate, self.filtroaudio, self.hilofiltro,
			self.audioconvert, self.vorbisenc, self.hiloaudiomuxor, self.oggmux)

		self.archivar= gst.element_link_many(self.oggmux, self.hiloarchivo, self.archivo)

		self.estado= "Grabando"
		self.play()

	def set_pipeline(self):
		self.pipeline= gst.Pipeline("player")

		# Video
		self.camara=  gst.element_factory_make('v4l2src', "webcam")
		self.camara.set_property("device", self.device) # "/dev/video0"
		self.multi= gst.element_factory_make('tee', "multi")

		# Video 1
		self.hilovideoapantalla= gst.element_factory_make('queue', "hilovideoapantalla")
		self.pantalla= gst.element_factory_make('xvimagesink', "pantalla") # autovideosink o xvimagesink

		# Video 2
		self.hiloencodearvideo= gst.element_factory_make('queue', "hiloencodearvideo")

		self.scale = gst.element_factory_make("videoscale", "vbscale")
		self.scalecapsfilter = gst.element_factory_make("capsfilter", "scalecaps")
		self.scalecaps = gst.Caps(self.resolucion)
		# 'video/x-raw-yuv,width=320,height=240''video/x-raw-yuv,width=160,height=120'
		self.scalecapsfilter.set_property("caps", self.scalecaps)
		self.colorspace = gst.element_factory_make("ffmpegcolorspace", "vbcolorspace")

		self.theoraenc= gst.element_factory_make('theoraenc', 'theoraenc')
		#self.theoraenc.set_property("quality", 16) # 48 default

		# Audio
		self.alsasrc= gst.element_factory_make('alsasrc', "alsasrc") # alsasrc o pulsesrc
		self.alsasrc.set_property("device", "default")
		self.capaaudio = gst.Caps(self.audio)
		# "audio/x-raw-int,rate=16000,channels=1,depth=16" "audio/x-raw-int,rate=48000,channels=2,depth=16"
		self.audiorate = gst.element_factory_make("audiorate")

            	self.filtroaudio = gst.element_factory_make("capsfilter", "filtroaudio")
            	self.filtroaudio.set_property("caps", self.capaaudio)

		self.hilofiltro= gst.element_factory_make('queue', "hilofiltro")
		self.hilofiltro.set_property("leaky", True)

		self.audioconvert= gst.element_factory_make('audioconvert', "audioconvert")
		self.vorbisenc= gst.element_factory_make('vorbisenc', "vorbisenc")

		# Muxor - Unión audio y video
		self.hilovideomuxor= gst.element_factory_make('queue', "hilovideomuxor")
		self.hiloaudiomuxor= gst.element_factory_make('queue', "hiloaudiomuxor")
		self.oggmux= gst.element_factory_make('oggmux', "oggmux")

		# Archivo - Unión muxor archivo
		self.hiloarchivo= gst.element_factory_make('queue', "hiloarchivo")
		self.archivo= gst.element_factory_make('filesink', "archivo")

		self.pipeline.add(self.camara, self.multi, self.hilovideoapantalla, self.pantalla)

		self.camaramultihilo= gst.element_link_many(self.camara, self.multi)
		self.visorwebcam= gst.element_link_many(self.multi, self.hilovideoapantalla, self.pantalla)

        	self.bus= self.pipeline.get_bus()
        	self.bus.enable_sync_message_emission()
        	self.bus.add_signal_watch()
        	self.bus.connect("sync-message::element", self.on_sync_message)
        	self.bus.connect("message", self.on_message)

	def set_config( self, device, resolucion, audiorate, audiochannels, audiodepth):
		self.pipeline.set_state(gst.STATE_PAUSED)
		self.pipeline.set_state(gst.STATE_NULL)
		self.device= device
		w, h= resolucion
		self.resolucion= "video/x-raw-yuv,width=%i,height=%i" % (w,h)
		self.audio= "audio/x-raw-int,rate=%i,channels=%i,depth=%i" % (audiorate, audiochannels, audiodepth)
		self.set_pipeline()
		self.play()

	def set_config_audio( self, audiorate, audiochannels, audiodepth):
		self.pipeline.set_state(gst.STATE_PAUSED)
		self.pipeline.set_state(gst.STATE_NULL)
		self.audio= "audio/x-raw-int,rate=%i,channels=%i,depth=%i" % (audiorate, audiochannels, audiodepth)
		self.set_pipeline()
		self.play()

