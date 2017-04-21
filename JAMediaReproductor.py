#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMediaReproductor.py por:
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

import sys, os, gtk, pygtk, gobject, gst, pygst, mimetypes

import JAMediaGlobals as G

gobject.threads_init()
gtk.gdk.threads_init()

class JAMediaReproductor(gtk.Object):
	__gsignals__ = {"endfile":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,)),
	"estado":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
	"newposicion":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT,))}
	def __init__(self, ventana_id):
		gtk.Object.__init__(self)
		self.ventana_id= ventana_id
		self.pipeline= None
		self.estado= None

		self.duracion= 0
		self.posicion= 0
		self.actualizador= None

		self.player= None
		self.bus= None

		self.set_pipeline()

	def set_pipeline(self):
		self.pipeline= gst.Pipeline("mypipeline")
		self.player= gst.element_factory_make("playbin2", "player")
		self.bus = self.player.get_bus()
		self.bus.add_signal_watch()
		self.bus.enable_sync_message_emission()
		self.bus.connect("message", self.on_message)
		self.bus.connect("sync-message::element", self.on_sync_message)

	def on_sync_message(self, bus, message):
		if "prepare-xwindow-id" in message.structure.get_name():
			imagesink = message.src
			#imagesink.set_property("force-aspect-ratio", False)
			imagesink.set_property("force-aspect-ratio", True)
			gtk.gdk.threads_enter()
			imagesink.set_xwindow_id(self.ventana_id)
			gtk.gdk.threads_leave()
		elif "playbin2-stream-changed" in message.structure.get_name():
			pass

    	def on_message(self, bus, message):
        	if message.type == gst.MESSAGE_ERROR:
            		err, debug = message.parse_error()
			print str(err) == "No se pudo abrir el recurso para su lectura." or str(err) == "No se pudo determinar el tipo de flujo."
			return self.stop()

		elif message.type == gst.MESSAGE_EOS: # fin de archivo
			self.emit("endfile", True) # También se puede: self.bus.connect("message::eos", self.on_finish)

		elif message.type == gst.MESSAGE_STATE_CHANGED:
			if message.structure["old-state"] == gst.STATE_PAUSED and message.structure["new-state"] == gst.STATE_PLAYING:
				if self.estado != message.structure["new-state"]:
					self.estado = message.structure["new-state"]
					self.emit("estado", "playing")
			elif message.structure["old-state"] == gst.STATE_READY and message.structure["new-state"] == gst.STATE_PAUSED:
				if self.estado != message.structure["new-state"]:
					self.estado = message.structure["new-state"]
					self.emit("estado", "paused")
			else:
				pass
		'''
		elif message.type == gst.MESSAGE_TAG:
			if message.structure.has_field("video-codec"):
				#print "Codec de Video en la Fuente"
		elif message.type == gst.MESSAGE_BUFFERING:
			pass
			# print message.structure["buffer-percent"]
		elif message.type == gst.MESSAGE_DURATION:
			# self.duracion= message.structure["duration"]
			# En la práctica, es recomendable y mas seguro obtener este dato en el handle.
			pass
		elif message.type == gst.MESSAGE_STREAM_STATUS:
			mensaje= message.structure.to_string().split(",")
			for m in mensaje:
				print "\t", m
		elif message.type == gst.MESSAGE_ELEMENT:
		elif message.type == gst.MESSAGE_NEW_CLOCK:
		elif message.type == gst.MESSAGE_QOS or message.type == gst.MESSAGE_ASYNC_DONE:
		else:
			try:
				print message.type, message.structure.get_name(), message.structure.to_string()
			except:
				print message'''

	def load(self, uri):
		self.stop()
		self.set_pipeline()
		direccion= uri
		mime= mimetypes.guess_type(direccion, strict=True)[0]
		#if "video" in mime or "audio" in mime: direccion= "file://%s" % (uri)
		direccion= "file://%s" % (uri)
		self.player.set_property("uri", direccion)
		#self.player.set_property("buffer-size", 1024)
		self.player.set_state(gst.STATE_PAUSED)
		self.play()

	def play(self):
		self.player.set_state(gst.STATE_PLAYING)
		self.estado= gst.STATE_PLAYING
		self.emit("estado", "playing")
		self.actualizador= gobject.timeout_add(30, self.handle)

	def stop(self):
		if self.actualizador: gobject.source_remove(self.actualizador)
		self.player.set_state(gst.STATE_NULL)
		self.estado= gst.STATE_NULL
		self.emit("estado", "None")

	def pause(self):
		self.player.set_state(gst.STATE_PAUSED)
		self.estado= gst.STATE_PAUSED
		self.emit("estado", "paused")

	def handle(self):
		try:
			nanosecs, format= self.player.query_duration(gst.FORMAT_TIME)
			nanosecs= float(nanosecs)
			self.duracion= nanosecs

			nanosecs, format= self.player.query_position(gst.FORMAT_TIME)
			nanosecs= float(nanosecs)
			pos= int(nanosecs * 100 / self.duracion)

			if pos < 0 or pos > self.duracion: return True
			if pos != self.posicion:
				self.posicion= pos
				self.emit("newposicion", self.posicion)
			# print "***", gst.video_convert_frame(self.player.get_property("frame"))
		except:
			# print "Error en el indice del Video:", self.get_posicion(), self.duracion
			pass
		return True

	def set_position(self, posicion):
		if self.duracion < posicion: return
		posicion= self.duracion * posicion / 100
		self.player.get_state()
		self.player.seek_simple(gst.Format(gst.FORMAT_TIME), gst.SEEK_FLAG_FLUSH, posicion)# * gst.MSECOND)
		self.player.get_state()

