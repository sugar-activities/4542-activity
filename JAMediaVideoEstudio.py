#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMediaVideoEstudio.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   CeibalJAM! - Uruguay

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

# Necesita:
#	python 2.7.1 - gtk 2.0
#	gstreamer-plugins-base
#	gstreamer-plugins-good
#	gstreamer-plugins-ugly
#	gstreamer-plugins-bad
#	gstreamer-ffmpeg
# 	ffmpeg
#	mencoder

import gtk, pygtk, os, sys, gobject, time, datetime, commands, subprocess, gst, pygst
from sugar.activity import activity
from JAMediaWebCam import JAMediaWebCam
from JAMediaReproductor import JAMediaReproductor
from JAMediaWidgets import *
import JAMediaGlobals as G

gobject.threads_init()
gtk.gdk.threads_init()

G.get_programa_esta("ffmpeg")
G.get_programa_esta("mencoder")

class JAMediaVideoEstudio(activity.Activity):
	def __init__(self, handle):
		activity.Activity.__init__(self, handle, False)
		self.set_title("JAMedia Video Estudio")
		self.set_resizable(True)
		self.set_size_request(G.WIDTH, G.HEIGHT)
        	#self.set_border_width(2)
	        self.set_position(gtk.WIN_POS_CENTER)
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        	self.connect("delete_event", self.delete_event)

		self.fixebase= gtk.Fixed()
		self.widgetvideo= Superficie_de_Reproduccion()

		# Layout
		self.set_layout()
		self.show_all()
		self.realize()
		self.present()

		self.menubase= Menu(self.fixebase)
		self.menufilmar= MenuFilmar(self.fixebase)
		self.menugrabaraudio= MenuGrabarAudio(self.fixebase)
		self.menufotografiar= MenuFotografiar(self.fixebase)
		self.menureproduccion= MenuReproduccion(self.fixebase)
		self.menuverimagenes= MenuVerImagenes(self.fixebase)
		self.ventanaconfiguracionpresentacion= VentanaConfiguracionPresentacion(self)
		self.ventanaconfiguraciondisparador= VentanaConfiguracionDisparador(self)
		self.ventanaconfigurarfilmar= VentanaConfiguracionfilmar(self)
		self.ventanaconfigurargrabaraudio= VentanaConfiguraciongrabaraudio(self)
		self.menuactual= self.menubase

		self.menubase.show()
		self.menufilmar.hide()
		self.menugrabaraudio.hide()
		self.menufotografiar.hide()
		self.menureproduccion.hide()
		self.menuverimagenes.hide()
		self.ventanaconfiguracionpresentacion.hide()
		self.ventanaconfiguraciondisparador.hide()
		self.ventanaconfigurarfilmar.hide()
		self.ventanaconfigurargrabaraudio.hide()

		self.webcam= JAMediaWebCam(self.widgetvideo.window.xid)
		self.reproductor= JAMediaReproductor(self.widgetvideo.window.xid)

		self.jamedialist= JAMediaList(self.fixebase)
		self.jamedialist.hide()

		self.connect("check-resize", self.checksize)

		self.controlesview= True
		self.viewlist= False
		self.widgetvideo.connect("ocultar_controles", self.ver_controles)

		# En el menú base
		self.menubase.filmar.connect("clicked", self.runmenu, "filmar")
		self.menubase.fotografiar.connect("clicked", self.runmenu, "fotografiar")
		self.menubase.microfono.connect("clicked", self.runmenu, "grabaraudio")
		self.menubase.reproducir.connect("clicked", self.runmenu, "reproducir")
		self.menubase.verimagenes.connect("clicked", self.runmenu, "verimagenes")
		self.menubase.salir.connect("clicked", self.runmenu, "salir")

		# Filmando
		self.menufilmar.salir.connect("clicked", self.backmenu)
		self.menufilmar.filmar.connect("clicked", self.ejecutarfilmar)
		self.menufilmar.configurar.connect("clicked", self.verconfiguracion)
		self.ventanaconfigurarfilmar.connect("config", self.set_config_filmar)

		# Grabando audio
		self.menugrabaraudio.salir.connect("clicked", self.backmenu)
		self.menugrabaraudio.grabar.connect("clicked", self.ejecutargrabaraudio)
		self.menugrabaraudio.configurar.connect("clicked", self.verconfiguracion)
		self.ventanaconfigurargrabaraudio.connect("config", self.set_config_grabar_audio)

		# Fotografiando
		self.menufotografiar.salir.connect("clicked", self.backmenu)
		self.menufotografiar.fotografiar.connect("clicked", self.fotografiar)
		self.menufotografiar.configurar.connect("clicked", self.verconfiguracion)
		self.ventanaconfiguraciondisparador.connect("run", self.run_disparador)

		# Reproduciendo
		self.menureproduccion.lista.connect("clicked", self.verlista)
		self.menureproduccion.lista.connect("clickederecho", self.elegirlista)
		self.menureproduccion.salir.connect("clicked", self.backmenu)
		self.menureproduccion.controlesrepro.connect("activar", self.activar)
		self.menureproduccion.progressbar.connect("change-value", self.changevalueprogressbar)

		self.jamedialist.connect("play", self.play)
		self.reproductor.connect("endfile", self.endfile)
		self.reproductor.connect("estado", self.cambioestadoreproductor)
		self.reproductor.connect("newposicion", self.update_progress)

		# Viendo Imagenes
		self.menuverimagenes.salir.connect("clicked", self.backmenu)
		self.menuverimagenes.lista.connect("clicked", self.verlista)
		#self.menuverimagenes.lista.connect("clickederecho", self.elegirlista)
		self.jamedialist.connect("loadimagen", self.loadimagen)
		self.menuverimagenes.controlesrepro.connect("activar", self.imagenesactivar)
		self.menuverimagenes.configurar.connect("clicked", self.verconfiguracion)
		self.ventanaconfiguracionpresentacion.connect("run", self.run_presentacion)

		self.actualizador= None

		self.maximize()
		self.unmaximize()
		self.webcam.play()

	# SEÑALES >>
	def set_config_filmar(self, widget, device, resolucion, audiorate, audiochannels, audiodepth):
		w, h= resolucion.split("x")
		w, h= (int(w), int(h))
		self.webcam.set_config( device= device, resolucion= (w,h),
		audiorate= int(audiorate), audiochannels= int(audiochannels), audiodepth= int(audiodepth) )

	def set_config_grabar_audio(self, widget, audiorate, audiochannels, audiodepth):
		self.webcam.set_config_audio( audiorate= int(audiorate), audiochannels= int(audiochannels), audiodepth= int(audiodepth) )

	def elegirlista(self, widget= None, eventclick= None):
		boton= eventclick.button
		pos= (eventclick.x, eventclick.y)
		tiempo= eventclick.time
		self.get_menu(boton, pos, tiempo, widget)

   	def get_menu(self, boton, pos, tiempo, widget):
		menu = gtk.Menu()
		videos = gtk.MenuItem("Cargar Lista de Videos")
		menu.append(videos)
		videos.connect_object("activate", self.load_list, "Videos")

		audio = gtk.MenuItem("Cargar Lista de Archivos de Audio")
		menu.append(audio)
		audio.connect_object("activate", self.load_list, "Audio")

		otra = gtk.MenuItem("Cargar Archivos desde un Directorio Externo")
		menu.append(otra)
		otra.connect_object("activate", self.load_list, "Otra")

		menu.show_all()
		gtk.Menu.popup(menu, None, None, None, boton, tiempo)

	def load_list(self, tipo):
		if tipo== "Videos":		
			archivos= os.listdir(G.DIRECTORIOVIDEOS)
			lista= []
			for archivo in archivos:
				lista.append([archivo, os.path.join(G.DIRECTORIOVIDEOS, archivo)])
			self.jamedialist.set_list(lista)
			self.widgetvideo.expose()
		elif tipo== "Audio":
			archivos= os.listdir(G.DIRECTORIOAUDIO)
			lista= []
			for archivo in archivos:
				lista.append([archivo, os.path.join(G.DIRECTORIOAUDIO, archivo)])
			self.jamedialist.set_list(lista)
			self.widgetvideo.expose()
		elif tipo== "Audio":
			print "Cargar Otra Lista"
		else:
			pass

	def loadimagen(self, widget= None, archivo= None):
		self.widgetvideo.set_imagen(archivo= archivo)

	def fotografiar(self, widget= None, senial= None):
		if self.actualizador: gobject.source_remove(self.actualizador)
		self.actualizador= None
		self.menufotografiar.set_stop()
		self.webcam.get_fotografia()
		self.menufotografiar.setinfo()

	def verlista(self, widget= None, senial= None):
		if not self.viewlist:
			self.jamedialist.show_all()
			self.viewlist= True
		else:
			self.jamedialist.hide()
			self.viewlist= False

	def changevalueprogressbar(self, widget= None, valor= None):
		self.reproductor.set_position(valor)

	def update_progress(self, objetoemisor, valor):
		self.menureproduccion.progressbar.set_progress(float(valor))

	def cambioestadoreproductor(self, widget= None, senial= None):
		if "playing" in senial:
			self.menureproduccion.controlesrepro.set_playing()
		elif "paused" in senial or "None" in senial:
			self.menureproduccion.controlesrepro.set_paused()

	def endfile(self, widget= None, senial= None):
		self.menureproduccion.controlesrepro.set_paused()
		self.widgetvideo.expose()
		self.jamedialist.siguiente()

	def play(self, widget= None, url= None):
		self.widgetvideo.expose()
		self.reproductor.load(url)
		self.menureproduccion.label.set_text(url)

	def activar(self, widget= None, senial= None):
		if senial == "atras":
			self.widgetvideo.expose()
			self.jamedialist.anterior()
		elif senial == "siguiente":
			self.widgetvideo.expose()
			self.jamedialist.siguiente()
		elif senial == "stop":
			self.reproductor.stop()
			self.menureproduccion.controlesrepro.set_paused()
			self.widgetvideo.expose()
		elif senial == "pausa":
			if self.reproductor.estado== gst.STATE_PLAYING:
				self.reproductor.pause()
			else:
				self.reproductor.play()

	def verconfiguracion(self, widget= None, senial= None):
		if self.menuactual == self.menuverimagenes:
			self.ventanaconfiguracionpresentacion.show()
		elif self.menuactual == self.menufotografiar:
			self.ventanaconfiguraciondisparador.show()
		elif self.menuactual == self.menufilmar:
			if self.webcam.estado== None:
				self.ventanaconfigurarfilmar.show()
		elif self.menuactual == self.menugrabaraudio:
			if self.webcam.estado== None:
				self.ventanaconfigurargrabaraudio.show()

	def run_presentacion(self, widget= None, senial= None):
		if self.actualizador: gobject.source_remove(self.actualizador)
		self.actualizador= None
		self.actualizador= gobject.timeout_add(senial, self.handlepresentacion)
		self.menuverimagenes.controlesrepro.set_playing()

	def run_disparador(self, widget= None, senial= None):
		if self.actualizador: gobject.source_remove(self.actualizador)
		self.actualizador= None
		self.actualizador= gobject.timeout_add(senial, self.handledisparador)
		self.menufotografiar.set_grabando()

	def handlepresentacion(self):
		self.jamedialist.siguiente()
		return True

	def handledisparador(self):
		self.webcam.get_fotografia()
		self.menufotografiar.setinfo()
		return True

	def imagenesactivar(self, widget= None, senial= None):
		if senial == "atras":
			self.widgetvideo.expose()
			self.jamedialist.anterior()
		elif senial == "siguiente":
			self.widgetvideo.expose()
			self.jamedialist.siguiente()
		elif senial == "stop":
			if self.actualizador:
				gobject.source_remove(self.actualizador)
				self.actualizador= None
				self.menuverimagenes.controlesrepro.set_paused()
		elif senial == "pausa":
			if self.actualizador:
				gobject.source_remove(self.actualizador)
				self.actualizador= None
				self.menuverimagenes.controlesrepro.set_paused()
			else:
				intervalo= int(self.ventanaconfiguracionpresentacion.intervalo*1000)
				self.actualizador= gobject.timeout_add(intervalo, self.handlepresentacion)
				self.menuverimagenes.controlesrepro.set_playing()

	def ver_controles(self, widget= None, valor= None):
		if self.menuactual != self.menureproduccion and self.menuactual != self.menuverimagenes: return
		if valor and self.controlesview:
			self.menuactual.hide()
			self.controlesview= False
			self.jamedialist.hide()
			self.viewlist= False
		elif not valor and not self.controlesview:
			self.menuactual.show()
			self.controlesview= True

	def ejecutarfilmar(self, widget, event):
		if self.webcam.estado== None:
			self.webcam.grabar()
			self.menufilmar.set_grabando()
			self.menufilmar.setinfo()

		elif self.webcam.estado== "Grabando":
			self.webcam.stop()
			self.webcam.play()
			self.menufilmar.set_stop()

	def ejecutargrabaraudio(self, widget, event):
		if self.webcam.estado== None:
			self.webcam.grabarsoloaudio()
			self.menugrabaraudio.set_grabando()
			self.menugrabaraudio.setinfo()

		elif self.webcam.estado== "Grabando":
			self.webcam.stopaudio()
			self.webcam.play()
			self.menugrabaraudio.set_stop()

	def checksize(self, contenedor):
		width, height= contenedor.get_size()
		self.widgetvideo.set_size_request(width, height)
		
		self.menufotografiar.reubicarcontroles(self.widgetvideo)
		self.menufilmar.reubicarcontroles(self.widgetvideo)
		self.menugrabaraudio.reubicarcontroles(self.widgetvideo)
		self.menubase.reubicarcontroles(self.widgetvideo)
		self.menureproduccion.reubicarcontroles(self.widgetvideo)
		self.menuverimagenes.reubicarcontroles(self.widgetvideo)
		self.jamedialist.reubicarcontroles(self.widgetvideo)

	def runmenu(self, widget, senial, valor):
		self.menuactual.hide()
		if valor == "filmar":
			self.menuactual= self.menufilmar
			self.menuactual.filmar.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
			self.menufilmar.setactualinfo()
			self.menuactual.show()
		elif valor == "fotografiar":
			self.menuactual= self.menufotografiar
			self.menufotografiar.setactualinfo()
			self.menuactual.show()
		elif valor == "grabaraudio":
			self.menuactual= self.menugrabaraudio
			self.menuactual.grabar.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
			self.menugrabaraudio.setactualinfo()
			self.menuactual.show()
		elif valor == "reproducir":
			self.menuactual= self.menureproduccion
			self.menuactual.show()

			self.webcam.pipeline.set_state(gst.STATE_PAUSED)
			self.webcam.pipeline.set_state(gst.STATE_NULL)

			archivos= os.listdir(G.DIRECTORIOVIDEOS)
			lista= []
			for archivo in archivos:
				lista.append([archivo, os.path.join(G.DIRECTORIOVIDEOS, archivo)])
			self.jamedialist.set_list(lista)
			self.widgetvideo.expose()

		elif valor == "verimagenes":
			self.menuactual= self.menuverimagenes
			self.menuactual.show()

			self.webcam.pipeline.set_state(gst.STATE_PAUSED)
			self.webcam.pipeline.set_state(gst.STATE_NULL)

			archivos= os.listdir(G.DIRECTORIOFOTOS)
			lista= []
			for archivo in archivos:
				lista.append([archivo, os.path.join(G.DIRECTORIOFOTOS, archivo)])
			self.jamedialist.set_list(lista)
			self.widgetvideo.expose()

		elif valor == "salir":
			self.dialog_salir()

	def backmenu(self, widget= None, senial= None):
		if self.menuactual == self.menufilmar and self.webcam.estado== "Grabando":
			self.webcam.stop()
		if self.menuactual == self.menugrabaraudio and self.webcam.estado== "Grabando":
			self.webcam.stopaudio()

		self.menufilmar.set_stop()
		self.menugrabaraudio.set_stop()
		self.menufotografiar.set_stop()
		self.widgetvideo.set_imagen(archivo= False)
		self.reproductor.stop()
		self.menureproduccion.controlesrepro.set_paused()
		self.jamedialist.hide()
		self.viewlist= False
		if self.actualizador: gobject.source_remove(self.actualizador)
		self.actualizador= None
		self.menuverimagenes.controlesrepro.set_paused()
		self.ventanaconfiguracionpresentacion.hide()
		self.ventanaconfiguraciondisparador.hide()
		self.ventanaconfigurarfilmar.hide()
		self.ventanaconfigurargrabaraudio.hide()
		self.menuactual.hide()
		self.menuactual= self.menubase
		self.menuactual.show()
		self.webcam.play()
	# SEÑALES <<

	def dialog_salir(self, widget= None, valor= None):
		dialog= JAMediaDialog("¿ Salir de JAMedia Video Estudio?", self)
		dialog.connect("ok", self.salir)
		dialog.connect("cancel", self.canceldialog)
	def canceldialog(self, widget= None, event= None):
		self.menuactual.show()

	def set_layout(self):
		self.fixebase.put(self.widgetvideo, 0, 0)
		self.set_canvas(self.fixebase)

	def delete_event(self, widget, event, data=None):
		self.salir()
        	return False

	def salir(self, widget= None, event= None):
		sys.exit(0)

if __name__ == "__main__":
    	miventana = JAMediaVideoEstudio()
    	gtk.main()

