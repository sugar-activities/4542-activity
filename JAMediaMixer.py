#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMediaMixer.py por:
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

import gtk, pygtk, commands, os

import JAMediaGlobals as G

def get_mixer_controls():
	''' Devuelve la lista de controles con volumen, disponible.'''
	controles= commands.getoutput('amixer controls')
	controles= controles.split("\n")
	nombres= []
	for control in controles:
		if "Volume" in control:
			try:
				c= control.split("name")[-1].split("=")[-1].split("'")[-2]
				volumen= get_control_volumen(control= c)
				if volumen: nombres.append(c)
			except:
				pass
	return nombres

def get_control_volumen(control= "Master"):
	''' Devuelve el volumen actual de un canal determinado.'''
	ejecutar= 'amixer get %s | %s' % (control, 'egrep "%]"')	
	elem= commands.getoutput(ejecutar).split(" ")
	volumen= None
	for e in elem:
		if "%" in e: break
	if "%" in e:
		return float(e.split("%")[0].split("[")[1])
	else:
		return None

def set_control_volumen(control= "Master", valor= 1.0):
	''' Setea el volumen en un canal determinado.'''
	valor= int(valor)
	ejecutar= 'amixer set %s %s%s' % (control, str(valor), "%")
	commands.getoutput(ejecutar)

def get_amixer_info():
	print commands.getoutput('amixer info')
	print commands.getoutput('amixer help')

class JAMediaMixer(gtk.Window):
	def __init__(self):
		super(JAMediaMixer, self).__init__(gtk.WINDOW_POPUP)
		self.set_title("JAMVolumen")
		self.set_resizable(False)
        	self.set_border_width(3)
	        self.set_position(gtk.WIN_POS_CENTER)
		self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)

		self.mixer_controls= get_mixer_controls()
		self.widgets_controls= []

		vcaja= gtk.VBox()
		caja= gtk.HBox()
		for control in self.mixer_controls:
			wid= Control(control)
			caja.pack_start(wid, True, True, 3)
			self.widgets_controls.append(wid)

		boton= gtk.Button("Cerrar")
		boton.connect("clicked", self.salir)
		vcaja.pack_start(caja, True, True, 3)
		vcaja.pack_start(boton, True, True, 3)

		self.add(vcaja)
		self.show_all()

	def reset_sound(self, widget= None):
		'''Setea a 100 todos los canales de reproducción.'''
		for control in self.mixer_controls:
			if "Speaker" in control or "Master" in control or "PCM" in control:
				set_control_volumen(control= control, valor= 100.0)
		for wid in self.widgets_controls:
			wid.get_volumen()

	def salir(self, widget):
		self.hide()

class Control(gtk.Frame):
	''' Control de Volumen para un canal específico en amixer. '''
	def __init__(self, control):
		self.control= control # El control en amixer
		self.alias= self.control.split(" ")[0]

		gtk.Frame.__init__(self, self.alias)
		self.set_label_align(0.5, 0.0)

		self.scale= VolumenControl(gtk.Adjustment(0.0, 1.0, 101.0, 0.1, 1.0, 1.0))
		self.get_volumen()

		self.scale.connect('value-changed', self.set_volumen)

		self.add(self.scale)
		self.show_all()

	def get_volumen(self, widget= None):
		self.scale.set_value(get_control_volumen(control= self.control))

	def set_volumen(self, widget):
		valor= widget.get_value()
		set_control_volumen(control= self.control, valor= valor)

class VolumenControl(gtk.VScale):
	def __init__(self, ajuste):
		gtk.VScale.__init__(self, ajuste)
		self.ajuste= ajuste
		self.set_digits(0)
		self.set_size_request(40, 200)
		self.set_value_pos(gtk.POS_BOTTOM)
		self.set_inverted(True)
		self.set_draw_value(False)

		self.x, self.y, self.w, self.h= (0,0,40,200)
		self.borde, self.ancho= (10, 10)

		self.pixbuf= gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "progress.png"), 25, 25)

		self.connect("expose_event", self.expose)
		self.connect( "size-allocate", self.size_allocate )

	def expose( self, widget, event ):
		x, y, w, h= (self.x, self.y, self.w, self.h)
		ancho, borde= (self.ancho, self.borde)
		anchoimagen, altoimagen= (self.pixbuf.get_width(), self.pixbuf.get_height())
		yy= int((h - altoimagen) * (self.ajuste.upper - self.get_value())/(self.ajuste.upper - self.ajuste.lower))
		ximagen= x + w/2 - anchoimagen/2
		yimagen= y + yy

		gc= gtk.gdk.Drawable.new_gc(self.window)
		# http://developer.gnome.org/pygtk/stable/class-gdkgc.html
		# http://developer.gnome.org/pygtk/stable/class-gdkdrawable.html#method-gdkdrawable--draw-rectangle
		# draw_rectangle(gc, filled, x, y, width, height)

		gc.set_rgb_fg_color(G.AMARILLO)
		self.window.draw_rectangle( gc, True, x+ w/2 - ancho/2, y+ borde, ancho, h - borde*2 )
		gc.set_rgb_fg_color(G.NARANJA)
		altura= h - yimagen
		if altura > 0: self.window.draw_rectangle( gc, True, x+ w/2 - ancho/2, y+ yimagen- borde, ancho, altura)
		gc.set_rgb_fg_color(G.NEGRO)
		self.window.draw_rectangle( gc, False, x+ w/2 - ancho/2, y+ borde, ancho, h - borde*2 )

		self.window.draw_pixbuf( gc, self.pixbuf, 0, 0, ximagen, yimagen, anchoimagen, altoimagen, gtk.gdk.RGB_DITHER_NORMAL, 0, 0 )

		return True

	def size_allocate( self, widget, allocation ):
		self.x, self.y, self.w, self.h= allocation
		return False

if __name__=="__main__":
	JAMediaMixer()
	gtk.main()
