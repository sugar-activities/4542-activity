#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMediaWidgets.py por:
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

import gtk, pygtk, os, gobject, cairo, platform, time, mimetypes

import JAMediaGlobals as G
from JAMediaMixer import JAMediaMixer

class JAMediaButton(gtk.EventBox):
	__gsignals__ = {"clicked":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
	"clickederecho":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}
	def __init__(self):
		gtk.EventBox.__init__(self)
		self.set_visible_window(True)
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
		self.set_border_width(1)

		# http://developer.gnome.org/pygtk/stable/gdk-constants.html#gdk-event-mask-constants
		self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK |
			gtk.gdk.ENTER_NOTIFY_MASK | gtk.gdk.LEAVE_NOTIFY_MASK)

		self.connect("button_press_event", self.button_press)
		self.connect("button_release_event", self.button_release)
		self.connect("enter-notify-event", self.enter_notify_event)
		self.connect("leave-notify-event", self.leave_notify_event)

	        self.imagen= gtk.Image()
        	self.add(self.imagen)

		self.show_all()

	# --------------------------- EVENTOS --------------------------
	def button_release(self, widget, event):
		self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)
	def leave_notify_event(self, widget, event):
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
	def enter_notify_event(self, widget, event):
		self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)
	def button_press(self, widget, event):
		if event.button == 1:
			self.modify_bg(gtk.STATE_NORMAL, G.NARANJA)
			self.emit("clicked", event)
		if event.button == 3:
			#self.modify_bg(gtk.STATE_NORMAL, G.NARANJA)
			self.emit("clickederecho", event)
	# --------------------------- EVENTOS --------------------------

	# --------------------------- SETEOS ---------------------------
	def set_tooltip(self, texto):
		tooltips = gtk.Tooltips()
		tooltips.set_tip(self, texto, tip_private=None)

	def set_imagen(self, archivo):
        	self.imagen.set_from_file(archivo)
	
	def set_tamanio(self, w, h):
		self.set_size_request(w,h)
	# --------------------------- SETEOS ---------------------------

class Superficie_de_Reproduccion(gtk.DrawingArea):
	__gsignals__ = {"ocultar_controles":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))}
	def __init__(self):
		gtk.DrawingArea.__init__(self)
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
		self.set_size_request(G.WIDTH, G.HEIGHT)
		self.show_all()
		self.add_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK)

		self.imagen= None
		
		self.connect("motion-notify-event", self.mousemotion)
		self.connect("expose_event", self.repaintimagen)

	def set_imagen(self, archivo= None):
		if archivo:
			self.imagen= gtk.gdk.pixbuf_new_from_file(archivo)
			self.repaintimagen()
		else:
			self.imagen= None

	def repaintimagen(self, widget= None, event= None):
		if self.imagen:
			x,y,w,h= self.get_allocation()
			context=  self.window.cairo_create()
			ww, hh= self.imagen.get_width(), self.imagen.get_height()		
			ct= gtk.gdk.CairoContext(context)

			while ww < w or hh < h:
				ww += 1
				hh = int (ww/4*3)

			while ww > w or hh > h:
				ww -= 1
				hh = int (ww/4*3)

			scaledPixbuf= self.imagen.scale_simple(ww, hh, gtk.gdk.INTERP_BILINEAR)
			ct.set_source_pixbuf(scaledPixbuf, w/2-ww/2, h/2-hh/2)
			context.paint()
			context.stroke()
		return True

	def expose(self, widget= None, event= None):
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)

	def mousemotion(self, widget, event):
		x, y, state= event.window.get_pointer()
		xx,yy,ww,hh= self.get_allocation()
		if x in range(xx, ww) and y in range(yy, hh/2):
			self.emit("ocultar_controles", False)
			return
		else:
			self.emit("ocultar_controles", True)
			return

class Barra_de_Progreso(gtk.EventBox):
	__gsignals__ = {"change-value":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT, ))}
	def __init__(self):
		gtk.EventBox.__init__(self)
		self.scale= ProgressBar(gtk.Adjustment(0.0, 0.0, 101.0, 0.1, 1.0, 1.0))

		self.scale.connect("button-press-event", self.buttonpressevent)
		self.scale.connect("change-value", self.changevalueprogressbar)
		self.scale.connect("button-release-event", self.buttonreleaseevent)

		self.valor= 0
		self.presion= False

		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)

		self.add(self.scale)
		self.show_all()

	def buttonpressevent(self, widget, event):
		self.presion= True

	def buttonreleaseevent(self, widget, event):
		self.presion= False

	def set_progress(self, valor= 0):
		if not self.presion: self.scale.set_value(valor)

	def changevalueprogressbar(self, widget= None, flags= None, valor= None):
		if valor < 0 or valor > self.scale.ajuste.upper-2: return
		valor= int(valor)
		if valor != self.valor:
			self.valor= valor
		if not self.presion:
			self.scale.set_value(valor)
			self.emit("change-value", self.valor)

class ProgressBar(gtk.HScale):
	def __init__(self, ajuste):
		gtk.HScale.__init__(self, ajuste)
		self.ajuste= ajuste
		self.set_digits(0)
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
		self.set_draw_value(False)

		self.x, self.y, self.w, self.h= (0,0,200,40)
		self.borde, self.ancho= (15, 10)

		self.pixbuf= gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "progress.png"), 25, 25)

		self.connect("expose_event", self.expose)
		self.connect("size-allocate", self.size_allocate)

	def expose( self, widget, event ):
		x, y, w, h= (self.x, self.y, self.w, self.h)
		ancho, borde= (self.ancho, self.borde)

		gc= gtk.gdk.Drawable.new_gc(self.window)
		# http://developer.gnome.org/pygtk/stable/class-gdkgc.html
		# http://developer.gnome.org/pygtk/stable/class-gdkdrawable.html#method-gdkdrawable--draw-rectangle
		# draw_rectangle(gc, filled, x, y, width, height)

		gc.set_rgb_fg_color(G.BLANCO)
		self.window.draw_rectangle( gc, True, x, y, w, h )

		gc.set_rgb_fg_color(G.AMARILLO)
		ww= w- borde*2
		xx= x+ w/2 - ww/2
		hh= ancho
		yy= y+ h/2 - ancho/2
		self.window.draw_rectangle( gc, True, xx, yy, ww, hh )

		anchoimagen, altoimagen= (self.pixbuf.get_width(), self.pixbuf.get_height())
		ximagen= int((xx- anchoimagen/2) + self.get_value() * (ww / (self.ajuste.upper - self.ajuste.lower)))
		yimagen= yy + hh/2 - altoimagen/2

		gc.set_rgb_fg_color(G.NARANJA)
		self.window.draw_rectangle( gc, True, xx, yy, ximagen, hh)

		gc.set_rgb_fg_color(G.NEGRO)
		self.window.draw_rectangle( gc, False, xx, yy, ww, hh )

		self.window.draw_pixbuf( gc, self.pixbuf, 0, 0, ximagen, yimagen, anchoimagen, altoimagen, gtk.gdk.RGB_DITHER_NORMAL, 0, 0 )

		return True

	def size_allocate( self, widget, allocation ):
		self.x, self.y, self.w, self.h= allocation
		return False

class Barra_de_Reproduccion(gtk.HBox):
	__gsignals__ = {"activar":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))}
	def __init__(self):
		gtk.HBox.__init__(self, False, 0)

		# ****** BOTON_ATRAS
		self.botonatras= JAMediaButton()
		self.botonatras.set_tooltip("Pista Anterior")
		self.botonatras.set_imagen(os.path.join(G.ICONOS, "atras.png"))
		self.botonatras.set_tamanio( G.BUTTONS, G.BUTTONS )
        	self.botonatras.connect("clicked", self.clickenatras)

		# ****** BOTON PLAY
		self.botonplay= JAMediaButton()
		self.botonplay.set_tooltip("Reproducir o Pausar")
		self.botonplay.set_imagen(os.path.join(G.ICONOS, "play.png"))
		self.botonplay.set_tamanio( G.BUTTONS, G.BUTTONS )
        	self.botonplay.connect("clicked", self.clickenplay_pausa)

		# ****** BOTON SIGUIENTE
		self.botonsiguiente= JAMediaButton()
		self.botonsiguiente.set_tooltip("Pista Siguiente")
		self.botonsiguiente.set_imagen(os.path.join(G.ICONOS, "siguiente.png"))
		self.botonsiguiente.set_tamanio( G.BUTTONS, G.BUTTONS )
        	self.botonsiguiente.connect("clicked", self.clickensiguiente)

		# ****** BOTON STOP
		self.botonstop= JAMediaButton()
		self.botonstop.set_tooltip("Detener Reproducción")
		self.botonstop.set_imagen(os.path.join(G.ICONOS, "stop.png"))
		self.botonstop.set_tamanio( G.BUTTONS, G.BUTTONS )
        	self.botonstop.connect("clicked", self.clickenstop)

		self.pack_start(self.botonatras, True, True, 0)
		self.pack_start(self.botonplay, True, True, 0)
		self.pack_start(self.botonsiguiente, True, True, 0)
		self.pack_start(self.botonstop, True, True, 0)

        	self.show_all()

	def set_paused(self):
		self.botonplay.set_imagen(os.path.join(G.ICONOS, "play.png"))
	def set_playing(self):
		self.botonplay.set_imagen(os.path.join(G.ICONOS, "pausa.png"))

    	def clickenstop(self, widget= None, event= None):
		self.emit("activar", "stop")
	def clickenplay_pausa(self, widget= None, event= None):
		self.emit("activar", "pausa")
    	def clickenatras(self, widget= None, event= None):
		self.emit("activar", "atras")
    	def clickensiguiente(self, widget= None, event= None):
		self.emit("activar", "siguiente")

class ButtonJAMediaMixer(JAMediaButton):
	def __init__(self):
		JAMediaButton.__init__(self)
		self.set_tooltip("JAMediaMixer")
		self.set_imagen(os.path.join(G.ICONOS, "volumen.png"))
		self.set_tamanio(G.BUTTONS, G.BUTTONS)

	        self.jamediamixer= JAMediaMixer()
		self.jamediamixer.reset_sound()
		self.jamediamixer.hide()

		self.connect("clicked", self.get_jamediamixer)
		self.show_all()

	def get_jamediamixer(self, widget= None, event= None):
		self.jamediamixer.present()

class JAMediaDialog(gtk.Window):
	__gsignals__ = {"ok":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, )),
	"cancel":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}
	def __init__(self, etiqueta, ventanajamedia):
		super(JAMediaDialog, self).__init__(gtk.WINDOW_POPUP)
		self.set_transient_for(ventanajamedia)
		self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.set_resizable(False)
        	self.set_border_width(20)
		self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)

		vcaja= gtk.VBox()
		label= gtk.Label(etiqueta)
		vcaja.pack_start(label, True, True, 3)

		hbox= gtk.HBox()
		botonOK= gtk.Button("Si")
		botonNO= gtk.Button("No")
		botonOK.connect("clicked", self.ok_callback)
		botonNO.connect("clicked", self.cerrar)
		hbox.pack_start(botonOK, True, True, 3)
		hbox.pack_start(botonNO, True, True, 3)

		vcaja.pack_start(hbox, True, True, 3)

		self.add(vcaja)
		self.show_all()

	def ok_callback(self, widget= None, event= None):
		self.emit("ok", None)
		self.destroy()

	def cerrar(self, widget= None, event= None):
		self.emit("cancel", None)
		self.destroy()

class JAMediaLabel(gtk.EventBox):
	def __init__(self):
		gtk.EventBox.__init__(self)
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
		self.etiqueta= gtk.Label("  Reproduciendo: ")
		self.add(self.etiqueta)
		self.show_all()

	def set_text(self, texto):
		self.etiqueta.set_text("Reproduciendo: %s  " % (texto))

# MENU PRINCIPAL
class Menu():
	# El menú principal con las opciones generales
	def __init__(self, fixed):
		self.fixed= fixed

		# BOTONES
		self.filmar= JAMediaButton()
		self.fotografiar= JAMediaButton()
		self.microfono= JAMediaButton()
		self.reproducir= JAMediaButton()
		self.verimagenes= JAMediaButton()
		self.salir= JAMediaButton()
		self.ceibaljam= JAMediaButton()
		self.licencia= JAMediaButton()
		self.uruguay= JAMediaButton()
		self.label= JAMediaLabel()

		self.filmar.set_imagen(os.path.join(G.ICONOS, "camara.png"))
		self.filmar.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.filmar.set_tooltip("Grabar Audio y Video")
		self.fotografiar.set_imagen(os.path.join(G.ICONOS, "foto.png"))
		self.fotografiar.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.fotografiar.set_tooltip("Tomar Fotografías")
		self.microfono.set_imagen(os.path.join(G.ICONOS, "microfono.png"))
		self.microfono.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.microfono.set_tooltip("Grabar sólo Audio")
		self.reproducir.set_imagen(os.path.join(G.ICONOS, "iconplay.png"))
		self.reproducir.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.reproducir.set_tooltip("Reproducir Grabaciones")
		self.verimagenes.set_imagen(os.path.join(G.ICONOS, "monitor.png"))
		self.verimagenes.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.verimagenes.set_tooltip("Ver Fotografías")
		self.salir.set_imagen(os.path.join(G.ICONOS, "salir.png"))
		self.salir.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.salir.set_tooltip("Salir del Programa")

		self.ceibaljam.set_imagen(os.path.join(G.ICONOS, "ceibaljam.png"))
		self.ceibaljam.set_tamanio(162, 60)
		self.licencia.set_imagen(os.path.join(G.ICONOS, "licencia.png"))
		self.licencia.set_tamanio(170, 60)
		self.uruguay.set_imagen(os.path.join(G.ICONOS, "uruguay.png"))
		self.uruguay.set_tamanio(72, 60)
		self.label.etiqueta.set_text("https://sites.google.com/site/sugaractivities/jam/jamediavideoestudio")

		self.controles= [self.filmar, self.fotografiar, self.reproducir, self.verimagenes, self.salir,
			self.ceibaljam, self.licencia, self.uruguay, self.label, self.microfono]

		self.poslabel= (0,0)
		self.possalir= (0,0)

		self.agregarse()
		self.fixed.show_all()

	def agregarse(self):
		for control in self.controles:
			self.fixed.put(control, 0, 0)

	def reubicarcontroles(self, pantalla):
		x,y,w,h= pantalla.get_allocation()
		x, y= (w - G.BUTTONS - 10, 10)
		if self.possalir != (x,y):
			self.fixed.move(self.salir, x, y)
			self.possalir = (x, y)

			x, y= (10, 10)
			self.fixed.move(self.filmar, x, y)

			x+= 1+G.BUTTONS
			self.fixed.move(self.fotografiar, x, y)

			x+= 1+G.BUTTONS
			self.fixed.move(self.microfono, x, y)

			x+= 1+G.BUTTONS
			self.fixed.move(self.reproducir, x, y)

			x+= 1+G.BUTTONS
			self.fixed.move(self.verimagenes, x, y)

		x,y,w,h= pantalla.get_allocation()
		xxx,yyy,www,hhh= self.label.get_allocation()
		posx, posy= (x+w/2-www/2, y+h-10-hhh)
		if self.poslabel != (posx, posy):
			self.fixed.move(self.label, posx, posy)
			self.poslabel = (posx, posy)
			xx,yy,ww,hh= self.uruguay.get_allocation()
			self.fixed.move(self.uruguay, x+w/2-ww/2, y+h-hh-20-hhh)
			xx,yy,ww,hh= self.ceibaljam.get_allocation()
			self.fixed.move(self.ceibaljam, x+10, y+h-hh-20-hhh)
			xx,yy,ww,hh= self.licencia.get_allocation()
			self.fixed.move(self.licencia, x+w-ww-10, y+h-hh-20-hhh)
			
	def hide(self):
		for control in self.controles:
			control.hide()

	def show(self):
		for control in self.controles:
			control.show_all()

# MENU Filmar
class MenuFilmar():
	# El menú para grabar videos.
	def __init__(self, fixed):
		self.fixed= fixed

		# BOTONES
		self.filmar= JAMediaButton()
		self.botonjamediamixer= ButtonJAMediaMixer()
		self.salir= JAMediaButton()
		self.configurar= JAMediaButton()

		self.filmar.set_imagen(os.path.join(G.ICONOS, "camara.png"))
		self.filmar.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.filmar.set_tooltip("Comenzar a Grabar")
		self.salir.set_imagen(os.path.join(G.ICONOS, "salir.png"))
		self.salir.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.salir.set_tooltip("Volver al Menú")
		self.label= JAMediaLabel()
		self.videos= -1
		self.setinfo()
		self.configurar.set_imagen(os.path.join(G.ICONOS, "configurar.png"))
		self.configurar.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.configurar.set_tooltip("Configurar Filmación")

		self.controles= [self.filmar, self.botonjamediamixer, self.salir, self.label, self.configurar]

		self.possalir= (0,0)
		self.poslabel= (0,0)

		self.agregarse()
		self.fixed.show_all()

		self.color= G.NARANJA
		self.actualizador= None

	def set_stop(self):
		if self.actualizador:
			gobject.source_remove(self.actualizador)
			self.actualizador= None

	def set_grabando(self):
		self.set_stop()
		self.actualizador= gobject.timeout_add(500, self.timeralert)

    	def timeralert(self):
		if self.color == G.NARANJA:
			self.color= G.AMARILLO
		else:
			self.color= G.NARANJA
		self.filmar.modify_bg(gtk.STATE_NORMAL, self.color)
		return True

	def agregarse(self):
		for control in self.controles:
			self.fixed.put(control, 0, 0)

	def reubicarcontroles(self, pantalla):
		x,y,w,h= pantalla.get_allocation()
		xx, yy, ww, hh=  self.label.get_allocation()
		cambios= False

		posx, posy= (x+10, y+ h- 10- hh)
		if self.poslabel != (posx, posy):
			self.fixed.move(self.label, posx, posy)
			self.poslabel= (posx, posy)
			cambios= True

		xx, yy, ww, hh=  self.salir.get_allocation()
		posx, posy= (w - ww - 10, 10)
		if self.possalir != (posx, posy):
			self.fixed.move(self.salir, posx, posy)
			self.possalir = (posx, posy)
			cambios= True

		if cambios:
			xx, yy, ww, hh= self.configurar.get_allocation()
			posx, posy= (w/2- ww/2, 10)
			self.fixed.move(self.configurar, posx, posy)
			xx, yy, ww, hh= self.filmar.get_allocation()
			pos = posx - ww - 1
			self.fixed.move(self.filmar, pos, posy)
			xx, yy, ww, hh= self.botonjamediamixer.get_allocation()
			pos= posx + ww + 1
			self.fixed.move(self.botonjamediamixer, pos, posy)

	def hide(self):
		for control in self.controles:
			control.hide()

	def show(self):
		for control in self.controles:
			control.show_all()

	def setinfo(self):
		archivos= len(os.listdir(G.DIRECTORIOVIDEOS))
		self.videos += 1
		self.label.etiqueta.set_text("  Videos en esta Seción: %s  Archivos Totales Almacenados: %s  " % (self.videos, archivos))

	def setactualinfo(self):
		archivos= len(os.listdir(G.DIRECTORIOVIDEOS))
		self.label.etiqueta.set_text("  Videos en esta Seción: %s  Archivos Totales Almacenados: %s  " % (self.videos, archivos))

# MENU Fotografiar
class MenuFotografiar():
	# El menú para tomar fotografías.
	def __init__(self, fixed):
		self.fixed= fixed

		# BOTONES
		self.fotografiar= JAMediaButton()
		self.salir= JAMediaButton()
		self.configurar= JAMediaButton()

		self.fotografiar.set_imagen(os.path.join(G.ICONOS, "foto.png"))
		self.fotografiar.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.fotografiar.set_tooltip("Tomar Fotografías")
		self.salir.set_imagen(os.path.join(G.ICONOS, "salir.png"))
		self.salir.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.salir.set_tooltip("Volver al Menú")

		self.configurar.set_imagen(os.path.join(G.ICONOS, "configurar.png"))
		self.configurar.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.configurar.set_tooltip("Configurar Disparador")

		self.label= JAMediaLabel()
		self.fotos= -1
		self.setinfo()

		self.controles= [self.fotografiar, self.salir, self.label, self.configurar]

		self.posfotografiar= (0,0)
		self.possalir= (0,0)
		self.poslabel= (0,0)
		self.posconfigurar= (0,0)

		self.agregarse()
		self.fixed.show_all()

		self.color= G.NARANJA
		self.actualizador= None

	def set_stop(self):
		if self.actualizador:
			gobject.source_remove(self.actualizador)
			self.actualizador= None

	def set_grabando(self):
		self.set_stop()
		self.actualizador= gobject.timeout_add(500, self.timeralert)

    	def timeralert(self):
		if self.color == G.NARANJA:
			self.color= G.AMARILLO
		else:
			self.color= G.NARANJA
		self.fotografiar.modify_bg(gtk.STATE_NORMAL, self.color)
		return True

	def agregarse(self):
		for control in self.controles:
			self.fixed.put(control, 0, 0)

	def reubicarcontroles(self, pantalla):
		x,y,w,h= pantalla.get_allocation()
		posx, posy= (w/2- G.BUTTONS/2, 10)
		if self.posfotografiar != (posx, posy):
			self.fixed.move(self.fotografiar, posx, posy)
			self.posfotografiar = (posx, posy)

		posx += (G.BUTTONS + 1)
		if self.posconfigurar != (posx, posy):
			self.fixed.move(self.configurar, posx, posy)
			self.posconfigurar = (posx, posy)

		posx= (w - G.BUTTONS - 10)
		if self.possalir != (posx, posy):
			self.fixed.move(self.salir, posx, posy)
			self.possalir = (posx, posy)

		xx, yy, ww, hh=  self.label.get_allocation()
		posx, posy= (10, h - 10 - hh)
		if self.poslabel != (posx, posy):
			self.fixed.move(self.label, posx, posy)
			self.poslabel = (posx, posy)

	def setinfo(self):
		archivos= len(os.listdir(G.DIRECTORIOFOTOS))
		self.fotos += 1
		self.label.etiqueta.set_text("  Fotografías en esta Seción: %s  Archivos Totales Almacenados: %s  " % (self.fotos, archivos))

	def setactualinfo(self):
		archivos= len(os.listdir(G.DIRECTORIOFOTOS))
		self.label.etiqueta.set_text("  Fotografías en esta Seción: %s  Archivos Totales Almacenados: %s  " % (self.fotos, archivos))

	def hide(self):
		for control in self.controles:
			control.hide()

	def show(self):
		for control in self.controles:
			control.show_all()

# MENU Reproducción
class MenuReproduccion():
	# El menú para reproducir grabaciones
	def __init__(self, fixed):
		self.fixed= fixed

		# BOTONES
		self.progressbar= Barra_de_Progreso()
		self.controlesrepro= Barra_de_Reproduccion()
		self.botonjamediamixer= ButtonJAMediaMixer()
		self.lista= JAMediaButton()
		self.salir= JAMediaButton()

		self.label= JAMediaLabel()

		self.salir.set_imagen(os.path.join(G.ICONOS, "salir.png"))
		self.salir.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.salir.set_tooltip("Volver al Menú")
		self.lista.set_imagen(os.path.join(G.ICONOS, "lista.png"))
		self.lista.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.lista.set_tooltip("Ver Lista de Archivos")

		self.controles= [self.progressbar, self.controlesrepro, self.botonjamediamixer, self.lista, self.salir, self.label]

		self.posprogressbar= (0,0)
		self.poscontrolesrepro= (0,0)
		self.possalir= (0,0)
		self.posbotonjamediamixer= (0,0)
		self.poslabel= (0,0)
		self.poslista= (0,0)

		self.agregarse()
		self.fixed.show_all()

	def agregarse(self):
		for control in self.controles:
			self.fixed.put(control, 0, 0)

	def reubicarcontroles(self, pantalla):
		x,y,w,h= pantalla.get_allocation()

		xlabel, ylabel, wlabel, hlabel= self.label.get_allocation()
		xlabel, ylabel= (10, y+h-hlabel-10)
		if self.poslabel != (xlabel, ylabel):
			self.fixed.move(self.label, xlabel, ylabel)
			self.poslabel= (xlabel, ylabel)

		ancho= w - (G.BUTTONS + 30)
		self.progressbar.set_size_request(ancho, 30)
		x, y= (10, 10)
		if self.posprogressbar != (x,y):
			self.fixed.move(self.progressbar, x, y)
			self.posprogressbar = (x, y)
		x, y= (w - G.BUTTONS - 10, 10)
		if self.possalir != (x,y):
			self.fixed.move(self.salir, x, y)
			self.possalir = (x, y)
		x,y,w,h= self.progressbar.get_allocation()
		y = h+20
		if self.poscontrolesrepro != (x,y):
			self.fixed.move(self.controlesrepro, x, y)
			self.poscontrolesrepro = (x, y)
	
		x= x+w - G.BUTTONS
		if self.posbotonjamediamixer != (x,y):
			self.fixed.move(self.botonjamediamixer, x, y)
			self.posbotonjamediamixer = (x, y)

		x-= G.BUTTONS + 1
		if self.poslista != (x,y):
			self.fixed.move(self.lista, x, y)
			self.poslista = (x, y)

	def hide(self):
		for control in self.controles:
			control.hide()

	def show(self):
		for control in self.controles:
			control.show_all()

# MENU para ver imagenes
class MenuVerImagenes():
	# El menú para reproducir grabaciones
	def __init__(self, fixed):
		self.fixed= fixed

		# BOTONES
		self.controlesrepro= Barra_de_Reproduccion()
		self.lista= JAMediaButton()
		self.salir= JAMediaButton()
		self.configurar= JAMediaButton()

		self.salir.set_imagen(os.path.join(G.ICONOS, "salir.png"))
		self.salir.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.salir.set_tooltip("Volver al Menú")
		self.lista.set_imagen(os.path.join(G.ICONOS, "lista.png"))
		self.lista.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.lista.set_tooltip("Ver Lista de Archivos")
		self.configurar.set_imagen(os.path.join(G.ICONOS, "configurar.png"))
		self.configurar.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.configurar.set_tooltip("Configurar Presentación")

		self.controles= [self.controlesrepro, self.lista, self.salir, self.configurar]

		self.poscontrolesrepro= (0,0)
		self.possalir= (0,0)
		self.poslista= (0,0)
		self.posconfigurar= (0,0)

		self.agregarse()
		self.fixed.show_all()

	def agregarse(self):
		for control in self.controles:
			self.fixed.put(control, 0, 0)

	def reubicarcontroles(self, pantalla):
		x,y,w,h= pantalla.get_allocation()

		posx, posy= (10, 10)
		if self.poscontrolesrepro != (posx, posy):
			self.fixed.move(self.controlesrepro, posx, posy)
			self.poscontrolesrepro = (posx, posy)

		xx,yy,ww,hh= self.salir.get_allocation()
		posx= w- (ww+ 10)
		if self.possalir != (posx, posy):
			self.fixed.move(self.salir, posx, posy)
			self.possalir = (posx, posy)

		xx,yy,ww,hh= self.lista.get_allocation()
		posx -= ww+ 10
		if self.poslista != (posx, posy):
			self.fixed.move(self.lista, posx, posy)
			self.poslista = (posx, posy)

		xx,yy,ww,hh= self.configurar.get_allocation()
		posx = w/2 - ww/2
		if self.posconfigurar != (posx, posy):
			self.fixed.move(self.configurar, posx, posy)
			self.posconfigurar = (posx, posy)

	def hide(self):
		for control in self.controles:
			control.hide()

	def show(self):
		for control in self.controles:
			control.show_all()

# MENU Grabar Audio
class MenuGrabarAudio():
	# El menú para grabar videos.
	def __init__(self, fixed):
		self.fixed= fixed

		# BOTONES
		self.grabar= JAMediaButton()
		self.botonjamediamixer= ButtonJAMediaMixer()
		self.salir= JAMediaButton()
		self.configurar= JAMediaButton()

		self.grabar.set_imagen(os.path.join(G.ICONOS, "microfono.png"))
		self.grabar.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.grabar.set_tooltip("Comenzar a Grabar")
		self.salir.set_imagen(os.path.join(G.ICONOS, "salir.png"))
		self.salir.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.salir.set_tooltip("Volver al Menú")
		self.label= JAMediaLabel()
		self.videos= -1
		self.setinfo()
		self.configurar.set_imagen(os.path.join(G.ICONOS, "configurar.png"))
		self.configurar.set_tamanio(G.BUTTONS, G.BUTTONS)
		self.configurar.set_tooltip("Configurar Grabación")

		self.controles= [self.grabar, self.botonjamediamixer, self.salir, self.label, self.configurar]

		#self.posgrabar= (0,0)
		self.possalir= (0,0)
		#self.posbotonjamediamixer= (0,0)
		self.poslabel= (0,0)

		self.agregarse()
		self.fixed.show_all()

		self.color= G.NARANJA
		self.actualizador= None

	def set_stop(self):
		if self.actualizador:
			gobject.source_remove(self.actualizador)
			self.actualizador= None

	def set_grabando(self):
		self.set_stop()
		self.actualizador= gobject.timeout_add(500, self.timeralert)

    	def timeralert(self):
		if self.color == G.NARANJA:
			self.color= G.AMARILLO
		else:
			self.color= G.NARANJA
		self.grabar.modify_bg(gtk.STATE_NORMAL, self.color)
		return True

	def agregarse(self):
		for control in self.controles:
			self.fixed.put(control, 0, 0)

	def reubicarcontroles(self, pantalla):
		'''
		x,y,w,h= pantalla.get_allocation()

		x, y= (w/2- G.BUTTONS/2, 10)
		if self.posgrabar != (x,y):
			self.fixed.move(self.grabar, x, y)
			self.posgrabar = (x, y)

		x= x + G.BUTTONS + 1
		if self.posbotonjamediamixer != (x,y):
			self.fixed.move(self.botonjamediamixer, x, y)
			self.posbotonjamediamixer = (x, y)

		x, y= (w - G.BUTTONS - 10, 10)
		if self.possalir != (x,y):
			self.fixed.move(self.salir, x, y)
			self.possalir = (x, y)

		x,y,w,h= pantalla.get_allocation()
		xx, yy, ww, hh=  self.label.get_allocation()
		x, y= (x+10, y+h - 10 - hh)
		if self.poslabel != (x,y):
			self.fixed.move(self.label, x, y)
			self.poslabel = (x, y)'''

		x,y,w,h= pantalla.get_allocation()
		xx, yy, ww, hh=  self.label.get_allocation()
		cambios= False

		posx, posy= (x+10, y+ h- 10- hh)
		if self.poslabel != (posx, posy):
			self.fixed.move(self.label, posx, posy)
			self.poslabel= (posx, posy)
			cambios= True

		xx, yy, ww, hh=  self.salir.get_allocation()
		posx, posy= (w - ww - 10, 10)
		if self.possalir != (posx, posy):
			self.fixed.move(self.salir, posx, posy)
			self.possalir = (posx, posy)
			cambios= True

		if cambios:
			xx, yy, ww, hh= self.configurar.get_allocation()
			posx, posy= (w/2- ww/2, 10)
			self.fixed.move(self.configurar, posx, posy)
			xx, yy, ww, hh= self.grabar.get_allocation()
			pos = posx - ww - 1
			self.fixed.move(self.grabar, pos, posy)
			xx, yy, ww, hh= self.botonjamediamixer.get_allocation()
			pos= posx + ww + 1
			self.fixed.move(self.botonjamediamixer, pos, posy)


	def hide(self):
		for control in self.controles:
			control.hide()

	def show(self):
		for control in self.controles:
			control.show_all()

	def setinfo(self):
		archivos= len(os.listdir(G.DIRECTORIOAUDIO))
		self.videos += 1
		texto= "  Archivos de Audio en esta Seción: %s  Archivos Totales Almacenados: %s  " % (self.videos, archivos)
		self.label.etiqueta.set_text(texto)

	def setactualinfo(self):
		archivos= len(os.listdir(G.DIRECTORIOAUDIO))
		texto= "  Archivos de Audio en esta Seción: %s  Archivos Totales Almacenados: %s  " % (self.videos, archivos)
		self.label.etiqueta.set_text(texto)

# LA LISTA de JAMEDIA >>
class JAMediaList(gtk.EventBox):
	__gsignals__ = {"loadimagen":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, )),
	"play":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}
	def __init__(self, fixedbase):
		gtk.EventBox.__init__(self)
		self.fixedbase= fixedbase
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)

		#self.set_size_request(200, G.HEIGHT/2)
		self.set_border_width(5)
		self.set_visible_window(True)

		self.caja= gtk.VBox()
		self.caja.modify_bg(gtk.STATE_NORMAL, G.BLANCO)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
       		scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrolled_window.add_with_viewport(self.caja)

		self.add(scrolled_window)
		self.show_all()

		self.pos= (0,0)
		self.elementselected= None
		self.agregarse()

	def agregarse(self):
		self.fixedbase.put(self, 0, 0)
	
	def reubicarcontroles(self, drawingarea):
		x,y,w,h= drawingarea.get_allocation()
		posy= y+ G.BUTTONS*2
		ancho, alto= (w/4, h - posy - 25)
		self.set_size_request(ancho, alto)
		posx= x+w - ancho-10
		if self.pos != (posx, posy):
			self.pos= (posx, posy)
			self.fixedbase.move(self, self.pos[0], self.pos[1])

		elementos= self.caja.get_children()
		ancho= 0
		for child in elementos:
			x,y,w,h= child.get_allocation()
			if w > ancho: ancho= w
		for child in elementos:
			child.set_tamanio(ancho, -1)

	def set_list(self, listatuplas):
		''' texto a mostrar, direccion de archivo'''
		elementos= self.caja.get_children()
		for child in elementos:
			self.caja.remove(child)
			child.destroy()
		for elemento in listatuplas:
			elementoenlista= ElementoEnLista(elemento[0], elemento[1])
			elementoenlista.connect("clicked", self.click_elemento)
			elementoenlista.connect("clickederecho", self.click_derecho_elemento)
			self.caja.pack_start(elementoenlista, False, False, 1)
		elementos= self.caja.get_children()
		if elementos:
			self.elementselected= elementos[0]
			self.select_item()

	def siguiente(self):
		elementos= self.caja.get_children()
		if len(elementos) < 2: return

		if self.elementselected:
			index= elementos.index(self.elementselected)
			if index < len(elementos)-1:
				index += 1
			else:
				index= 0
			self.elementselected= elementos[index]
			self.select_item()
		else:
			self.elementselected= elementos[0]
			self.select_item()

	def anterior(self):
		elementos= self.caja.get_children()
		if len(elementos) < 2: return

		if self.elementselected:
			index= elementos.index(self.elementselected)
			if index > 0:
				index-= 1
			else:
				index= -1
			self.elementselected= elementos[index]
			self.select_item()
		else:
			self.elementselected= elementos[0]
			self.select_item()

	def select_item(self):
		for child in self.caja.get_children():
			child.colornormal= G.BLANCO
			child.colorselect= G.AMARILLO
			child.colorclicked= G.NARANJA
			child.eventbox.modify_bg(gtk.STATE_NORMAL, child.colornormal)
		self.elementselected.colornormal= G.AMARILLO
		self.elementselected.colorselect= G.NARANJA
		self.elementselected.eventbox.modify_bg(gtk.STATE_NORMAL, self.elementselected.colornormal)
		if "image" in self.elementselected.mimetype:
			self.emit("loadimagen", self.elementselected.archivo)
		elif "video" in self.elementselected.mimetype or "audio" in self.elementselected.mimetype:
			self.emit("play", self.elementselected.archivo)
		else:
			print "Nuevo mimetype encontrado", self.elementselected.mimetype

	def click_elemento(self, widget= None, senial= None):
		if self.elementselected != widget:
			self.elementselected= widget
			self.select_item()

	def click_derecho_elemento(self, widget= None, eventclick= None):
		boton= eventclick.button
		pos= (eventclick.x, eventclick.y)
		tiempo= eventclick.time
		self.get_menu(boton, pos, tiempo, widget)

   	def get_menu(self, boton, pos, tiempo, widget):
		menu = gtk.Menu()
		quitar = gtk.MenuItem("Quitar de la Lista")
		menu.append(quitar)
		quitar.connect_object("activate", self.quitardelalista, widget)

		borrar = gtk.MenuItem("Borrar el Archivo")
		menu.append(borrar)
		borrar.connect_object("activate", self.borrararchivo, widget)

		menu.show_all()
		gtk.Menu.popup(menu, None, None, None, boton, tiempo)

	def quitardelalista(self, widget):
		self.caja.remove(widget)
		widget.destroy()
		elementos= self.caja.get_children()
		if elementos:
			self.elementselected= elementos[0]
			self.select_item()

	def borrararchivo(self, widget):
		direccion= widget.archivo
		self.quitardelalista(widget)
		G.borrar_archivo(direccion)

class ElementoEnLista(gtk.Fixed):
	__gsignals__ = {"clicked":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
	"clickederecho":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}
	def __init__(self, texto, archivo):
		gtk.Fixed.__init__(self)
		self.archivo= archivo
		self.colornormal= G.BLANCO
		self.colorselect= G.AMARILLO
		self.colorclicked= G.NARANJA

		self.eventbox= gtk.EventBox()
		self.eventbox.modify_bg(gtk.STATE_NORMAL, self.colornormal)
		self.eventbox.set_border_width(0)
		self.eventbox.set_visible_window(True)
		self.eventbox.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK |
			gtk.gdk.ENTER_NOTIFY_MASK | gtk.gdk.LEAVE_NOTIFY_MASK)

		self.box= gtk.HBox()
		self.imagen= gtk.Image()

		# Para mimetypes es imposible saber si hay video o no dentro del archivo
		self.mimetype= str(mimetypes.guess_type(self.archivo, strict=True)[0])
		if "image" in self.mimetype:
			pixbuf= gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(self.archivo), 50, 50)
			self.imagen.set_from_pixbuf(pixbuf)
		else:
			tipo= G.get_tipo(self.archivo)
			if tipo == "video":
				duracion= G.get_duracion(self.archivo)
				newvideo= G.corta_archivo(self.archivo, int(duracion/2)) # mencoder lo sabe
				if newvideo:
					imagen= G.get_preview(newvideo)
					if os.path.exists(imagen):
						pixbuf= gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(imagen), 50, 50)
						self.imagen.set_from_pixbuf(pixbuf)
					self.mimetype= "video"
				else:
					self.mimetype= "audio"
			else:
				self.mimetype= "audio"

		self.label= gtk.Label(texto)
		
		self.box.pack_start(self.imagen, False, False, 2)
		self.box.pack_start(self.label, False, False, 2)
		self.eventbox.add(self.box)

		self.put(self.eventbox, 0, 0)
		self.show_all()

		self.eventbox.connect("button_press_event", self.button_press)
		self.eventbox.connect("button_release_event", self.button_release)
		self.eventbox.connect("enter-notify-event", self.enter_notify_event)
		self.eventbox.connect("leave-notify-event", self.leave_notify_event)

	def set_tamanio(self, ancho, alto):
		self.set_size_request(ancho, alto)
		self.box.set_size_request(ancho, alto)

	def button_release(self, widget, event):
		self.eventbox.modify_bg(gtk.STATE_NORMAL, self.colorselect)
	def leave_notify_event(self, widget, event):
		self.eventbox.modify_bg(gtk.STATE_NORMAL, self.colornormal)
	def enter_notify_event(self, widget, event):
		self.eventbox.modify_bg(gtk.STATE_NORMAL, self.colorselect)
	def button_press(self, widget, event):
		if event.button == 1:
			self.eventbox.modify_bg(gtk.STATE_NORMAL, self.colorclicked)
			self.emit("clicked", self)
		if event.button == 3:
			self.emit("clickederecho", event)
# << LA LISTA de JAMEDIA

class VentanaConfiguracionPresentacion(gtk.Window):
	__gsignals__ = {"run":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT, ))}
	def __init__(self, ventanajamedia):
		super(VentanaConfiguracionPresentacion, self).__init__(gtk.WINDOW_POPUP)
		self.set_transient_for(ventanajamedia)
		self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.set_resizable(False)
        	self.set_border_width(20)
		self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)
		self.intervalo= (0.5)

		vcaja= gtk.VBox()
		label= gtk.Label("Configurar Presentación")
		vcaja.pack_start(label, True, True, 3)

		hcaja= gtk.HBox()
		self.label= gtk.Label("Cambiar Imagen cada: %s Segundos" %(self.intervalo))
		hcaja.pack_start(self.label, True, True, 3)

		vcaja2= gtk.VBox()
		boton1= gtk.Button("+")
		boton2= gtk.Button("-")
		vcaja2.pack_start(boton1, True, True, 3)
		vcaja2.pack_start(boton2, True, True, 3)
		boton1.connect("clicked", self.mas_intervalo)
		boton2.connect("clicked", self.menos_intervalo)

		hcaja.pack_start(vcaja2, True, True, 3)
		vcaja.pack_start(hcaja, True, True, 3)

		hcaja= gtk.HBox()
		botonok= gtk.Button("Aceptar")
		botoncancel= gtk.Button("Cancelar")
		hcaja.pack_start(botonok, True, True, 3)
		hcaja.pack_start(botoncancel, True, True, 3)
		botonok.connect("clicked", self.run_presentacion)
		botoncancel.connect("clicked", self.cancel)

		vcaja.pack_start(hcaja, True, True, 3)

		self.add(vcaja)
		self.show_all()

	def mas_intervalo(self, widget= None):
		self.intervalo += 0.5
		self.label.set_text("Cambiar Imagen cada: %s Segundos" %(self.intervalo))

	def menos_intervalo(self, widget= None):
		if self.intervalo > 0.5:
			self.intervalo -= 0.5
			self.label.set_text("Cambiar Imagen cada: %s Segundos" %(self.intervalo))

	def run_presentacion(self, widget= None):
		self.emit("run", int(self.intervalo*1000))
		self.hide()

	def cancel(self, widget= None):
		self.hide()

class VentanaConfiguracionDisparador(gtk.Window):
	__gsignals__ = {"run":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT, ))}
	def __init__(self, ventanajamedia):
		super(VentanaConfiguracionDisparador, self).__init__(gtk.WINDOW_POPUP)
		self.set_transient_for(ventanajamedia)
		self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.set_resizable(False)
        	self.set_border_width(20)
		self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)
		self.intervalo= (1)

		vcaja= gtk.VBox()
		label= gtk.Label("Configurar Disparador")
		vcaja.pack_start(label, True, True, 3)

		hcaja= gtk.HBox()
		self.label= gtk.Label("Tomar Fotografía cada: %s Segundos" %(self.intervalo))
		hcaja.pack_start(self.label, True, True, 3)

		vcaja2= gtk.VBox()
		boton1= gtk.Button("+")
		boton2= gtk.Button("-")
		vcaja2.pack_start(boton1, True, True, 3)
		vcaja2.pack_start(boton2, True, True, 3)
		boton1.connect("clicked", self.mas_intervalo)
		boton2.connect("clicked", self.menos_intervalo)

		hcaja.pack_start(vcaja2, True, True, 3)
		vcaja.pack_start(hcaja, True, True, 3)

		hcaja= gtk.HBox()
		botonok= gtk.Button("Aceptar")
		botoncancel= gtk.Button("Cancelar")
		hcaja.pack_start(botonok, True, True, 3)
		hcaja.pack_start(botoncancel, True, True, 3)
		botonok.connect("clicked", self.run_disparador)
		botoncancel.connect("clicked", self.cancel)

		vcaja.pack_start(hcaja, True, True, 3)

		self.add(vcaja)
		self.show_all()

	def mas_intervalo(self, widget= None):
		self.intervalo += 0.5
		self.label.set_text("Tomar Fotografía cada: %s Segundos" %(self.intervalo))

	def menos_intervalo(self, widget= None):
		if self.intervalo > 1:
			self.intervalo -= 0.5
			self.label.set_text("Tomar Fotografía cada: %s Segundos" %(self.intervalo))

	def run_disparador(self, widget= None):
		self.emit("run", int(self.intervalo*1000))
		self.hide()

	def cancel(self, widget= None):
		self.hide()

class VentanaConfiguracionfilmar(gtk.Window):
	__gsignals__ = {"config":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING,
	gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING))}
	def __init__(self, ventanajamedia):
		super(VentanaConfiguracionfilmar, self).__init__(gtk.WINDOW_POPUP)
		self.set_transient_for(ventanajamedia)
		self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.set_resizable(False)
        	self.set_border_width(20)
		self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)
		self.intervalo= (1)

		vcaja= gtk.VBox()
		label= gtk.Label("Configurar Video:")
		vcaja.pack_start(label, True, True, 3)

		hcaja= gtk.HBox()
		label= gtk.Label("Cámara: ")
		hcaja.pack_start(label, True, True, 3)
		self.combodevice= gtk.ComboBox()
		liststore= gtk.ListStore(gobject.TYPE_STRING)
		self.combodevice.set_model(liststore)
		text= gtk.CellRendererText()
		self.combodevice.pack_start(text, True)
		self.combodevice.add_attribute(text, 'text', 0)
		self.combodevice.append_text("/dev/video0")
		self.combodevice.append_text("/dev/video1")
		#self.combodevice.append_text("/dev/video2")
		#self.combodevice.append_text("/dev/video3")
		self.combodevice.set_active(0)
		hcaja.pack_start(self.combodevice, True, True, 3)

		vcaja.pack_start(hcaja, True, True, 3)

		hcaja= gtk.HBox()
		label= gtk.Label("Resolución: ")
		hcaja.pack_start(label, True, True, 3)
		self.comboresolucion= gtk.ComboBox()
		liststore= gtk.ListStore(gobject.TYPE_STRING)
		self.comboresolucion.set_model(liststore)
		text= gtk.CellRendererText()
		self.comboresolucion.pack_start(text, True)
		self.comboresolucion.add_attribute(text, 'text', 0)
		self.comboresolucion.append_text("160x120")
		self.comboresolucion.append_text("320x240")
		self.comboresolucion.append_text("640x480")
		self.comboresolucion.append_text("800x600")
		self.comboresolucion.set_active(1)
		hcaja.pack_start(self.comboresolucion, True, True, 3)

		vcaja.pack_start(hcaja, True, True, 3)

		label= gtk.Label("Configurar Audio:")
		vcaja.pack_start(label, True, True, 3)

		hcaja= gtk.HBox()
		label= gtk.Label("rate: ")
		hcaja.pack_start(label, True, True, 3)
		self.comboaudiorate= gtk.ComboBox()
		liststore= gtk.ListStore(gobject.TYPE_STRING)
		self.comboaudiorate.set_model(liststore)
		text= gtk.CellRendererText()
		self.comboaudiorate.pack_start(text, True)
		self.comboaudiorate.add_attribute(text, 'text', 0)
		self.comboaudiorate.append_text("8000")
		self.comboaudiorate.append_text("16000")
		self.comboaudiorate.append_text("32000")
		self.comboaudiorate.append_text("48000")
		self.comboaudiorate.set_active(1)
		hcaja.pack_start(self.comboaudiorate, True, True, 3)

		vcaja.pack_start(hcaja, True, True, 3)

		hcaja= gtk.HBox()
		label= gtk.Label("channels: ")
		hcaja.pack_start(label, True, True, 3)
		self.comboaudiochannels= gtk.ComboBox()
		liststore= gtk.ListStore(gobject.TYPE_STRING)
		self.comboaudiochannels.set_model(liststore)
		text= gtk.CellRendererText()
		self.comboaudiochannels.pack_start(text, True)
		self.comboaudiochannels.add_attribute(text, 'text', 0)
		self.comboaudiochannels.append_text("1")
		self.comboaudiochannels.append_text("2")
		self.comboaudiochannels.set_active(0)
		hcaja.pack_start(self.comboaudiochannels, True, True, 3)

		vcaja.pack_start(hcaja, True, True, 3)


		hcaja= gtk.HBox()
		label= gtk.Label("depth: ")
		hcaja.pack_start(label, True, True, 3)
		self.comboaudiodepth= gtk.ComboBox()
		liststore= gtk.ListStore(gobject.TYPE_STRING)
		self.comboaudiodepth.set_model(liststore)
		text= gtk.CellRendererText()
		self.comboaudiodepth.pack_start(text, True)
		self.comboaudiodepth.add_attribute(text, 'text', 0)
		self.comboaudiodepth.append_text("16")
		self.comboaudiodepth.append_text("32")
		self.comboaudiodepth.set_active(0)
		hcaja.pack_start(self.comboaudiodepth, True, True, 3)

		vcaja.pack_start(hcaja, True, True, 3)

		hcaja= gtk.HBox()
		botonok= gtk.Button("Aceptar")
		botoncancel= gtk.Button("Cancelar")
		hcaja.pack_start(botonok, True, True, 3)
		hcaja.pack_start(botoncancel, True, True, 3)
		botonok.connect("clicked", self.set_config)
		botoncancel.connect("clicked", self.cancel)

		vcaja.pack_start(hcaja, True, True, 3)

		self.add(vcaja)
		self.show_all()

		'''
		self.combodevice.connect("changed", self.change)

	def change(self, combo):
		self.emit("CHANGE_CONJUNTO", combo.get_active_text())'''

	def set_config(self, widget= None):
		device= self.combodevice.get_active_text()
		resolucion= self.comboresolucion.get_active_text()
		audiorate= self.comboaudiorate.get_active_text()
		audiochannels= self.comboaudiochannels.get_active_text()
		audiodepth= self.comboaudiodepth.get_active_text()
		self.emit("config", device, resolucion, audiorate, audiochannels, audiodepth)
		self.hide()

	def cancel(self, widget= None):
		self.hide()

class VentanaConfiguraciongrabaraudio(gtk.Window):
	__gsignals__ = {"config":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING))}
	def __init__(self, ventanajamedia):
		super(VentanaConfiguraciongrabaraudio, self).__init__(gtk.WINDOW_POPUP)
		self.set_transient_for(ventanajamedia)
		self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.set_resizable(False)
        	self.set_border_width(20)
		self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)
		self.intervalo= (1)

		vcaja= gtk.VBox()
		
		label= gtk.Label("Configurar Audio:")
		vcaja.pack_start(label, True, True, 3)

		hcaja= gtk.HBox()
		label= gtk.Label("rate: ")
		hcaja.pack_start(label, True, True, 3)
		self.comboaudiorate= gtk.ComboBox()
		liststore= gtk.ListStore(gobject.TYPE_STRING)
		self.comboaudiorate.set_model(liststore)
		text= gtk.CellRendererText()
		self.comboaudiorate.pack_start(text, True)
		self.comboaudiorate.add_attribute(text, 'text', 0)
		self.comboaudiorate.append_text("8000")
		self.comboaudiorate.append_text("16000")
		self.comboaudiorate.append_text("32000")
		self.comboaudiorate.append_text("48000")
		self.comboaudiorate.set_active(1)
		hcaja.pack_start(self.comboaudiorate, True, True, 3)

		vcaja.pack_start(hcaja, True, True, 3)

		hcaja= gtk.HBox()
		label= gtk.Label("channels: ")
		hcaja.pack_start(label, True, True, 3)
		self.comboaudiochannels= gtk.ComboBox()
		liststore= gtk.ListStore(gobject.TYPE_STRING)
		self.comboaudiochannels.set_model(liststore)
		text= gtk.CellRendererText()
		self.comboaudiochannels.pack_start(text, True)
		self.comboaudiochannels.add_attribute(text, 'text', 0)
		self.comboaudiochannels.append_text("1")
		self.comboaudiochannels.append_text("2")
		self.comboaudiochannels.set_active(0)
		hcaja.pack_start(self.comboaudiochannels, True, True, 3)

		vcaja.pack_start(hcaja, True, True, 3)


		hcaja= gtk.HBox()
		label= gtk.Label("depth: ")
		hcaja.pack_start(label, True, True, 3)
		self.comboaudiodepth= gtk.ComboBox()
		liststore= gtk.ListStore(gobject.TYPE_STRING)
		self.comboaudiodepth.set_model(liststore)
		text= gtk.CellRendererText()
		self.comboaudiodepth.pack_start(text, True)
		self.comboaudiodepth.add_attribute(text, 'text', 0)
		self.comboaudiodepth.append_text("16")
		self.comboaudiodepth.append_text("32")
		self.comboaudiodepth.set_active(0)
		hcaja.pack_start(self.comboaudiodepth, True, True, 3)

		vcaja.pack_start(hcaja, True, True, 3)

		hcaja= gtk.HBox()
		botonok= gtk.Button("Aceptar")
		botoncancel= gtk.Button("Cancelar")
		hcaja.pack_start(botonok, True, True, 3)
		hcaja.pack_start(botoncancel, True, True, 3)
		botonok.connect("clicked", self.set_config)
		botoncancel.connect("clicked", self.cancel)

		vcaja.pack_start(hcaja, True, True, 3)

		self.add(vcaja)
		self.show_all()

		'''
		self.combodevice.connect("changed", self.change)

	def change(self, combo):
		self.emit("CHANGE_CONJUNTO", combo.get_active_text())'''

	def set_config(self, widget= None):
		audiorate= self.comboaudiorate.get_active_text()
		audiochannels= self.comboaudiochannels.get_active_text()
		audiodepth= self.comboaudiodepth.get_active_text()
		self.emit("config", audiorate, audiochannels, audiodepth)
		self.hide()

	def cancel(self, widget= None):
		self.hide()

