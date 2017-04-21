#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMediaGlobals.py por:
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

import gtk, pygtk, os, commands

DIRECTORIO_BASE= os.path.dirname(__file__)
ICONOS= os.path.join(DIRECTORIO_BASE, "Iconos/")

if not os.path.exists(os.path.join(os.environ["HOME"], "DatosJAMediaVideoEstudio")):
	os.mkdir(os.path.join(os.environ["HOME"], "DatosJAMediaVideoEstudio"))
	os.chmod(os.path.join(os.environ["HOME"], "DatosJAMediaVideoEstudio"), 0755)

DIRECTORIOVIDEOS= os.path.join(os.environ["HOME"], "DatosJAMediaVideoEstudio", "Videos")
DIRECTORIOFOTOS= os.path.join(os.environ["HOME"], "DatosJAMediaVideoEstudio", "Fotos")
DIRECTORIOAUDIO= os.path.join(os.environ["HOME"], "DatosJAMediaVideoEstudio", "Audio")

if not os.path.exists(DIRECTORIOVIDEOS):
	os.mkdir(DIRECTORIOVIDEOS)
	os.chmod(DIRECTORIOVIDEOS, 0755)

if not os.path.exists(DIRECTORIOFOTOS):
	os.mkdir(DIRECTORIOFOTOS)
	os.chmod(DIRECTORIOFOTOS, 0755)

if not os.path.exists(DIRECTORIOAUDIO):
	os.mkdir(DIRECTORIOAUDIO)
	os.chmod(DIRECTORIOAUDIO, 0755)

# Versiones viejas de gtk no funcionan si no se usa 0 a 65000. Ejem: 122*65000/255= 26000
GRIS= gtk.gdk.Color(60156, 60156, 60156, 1)#("#ececec")
AMARILLO= gtk.gdk.Color(65000,65000,40275,1)#("#ffff9e")
NARANJA= gtk.gdk.Color(65000,26000,0,1)#("#FF6600")
BLANCO= gtk.gdk.Color(65535, 65535, 65535,1)
NEGRO= gtk.gdk.Color(0, 0, 0, 1)

WIDTH= 640
HEIGHT= 480
BUTTONS= 60

def borrar_archivo(direccion):
	if os.path.exists(direccion):
		 commands.getoutput('rm %s' % (direccion))

def get_programa_esta(programa):
	# Devuelve true si programa se encuentra instaldo y false si no lo está.
	paths= os.environ['PATH'].split(":")
	esta= False
	for directorio in paths:
		if os.path.exists(directorio):
			datos= os.listdir(directorio)
			if programa in datos:
				esta= True
				break
		else:
			print "Directorio Inexistente en el path", directorio
	print programa, "Instalado en el sistema:", esta
	return esta

def get_duracion(archivo):
	# devulve la duración de reproducción de un archivo en segundos.
	try:
		datos= commands.getoutput('ffmpeg -i %s' % (archivo))
		for x in datos.split("\n"):
			duracion= 0
			if 'Duration' in x:
				duracion= x
				break
		duracion= duracion.split(",")[0].split(": ")[-1]
		h,m,s= duracion.split(":")
		segundos= (int(h*60)+int(m))*60+int(float(s))
		return int(segundos)
	except:
		return 0

def get_tipo(archivo):
	# Verifica si el archivo contiene video xor audio.
	datos= commands.getoutput('ffmpeg -i %s' % (archivo))
	for x in datos.split("\n"):
		tipo= None
		if 'Audio' in x:
			tipo= 'audio'
		elif 'Video' in x:
			tipo= 'video'
			break
	return tipo

def corta_archivo(origen, inicio):
	# genera un video de 2 segundos desde inicio.
	if inicio:
		destino= '/tmp/x.ogg'
		fin= 2
		datos= commands.getoutput('mencoder %s -ss %i -endpos %i -ovc copy -oac copy -o %s' % (origen, inicio, fin, destino))
		if "Audio only file format detected" in datos: return None
		return destino
	else:
		return 0

def get_preview(archivo):
	# Captura el 1º frame de un video y lo devuelve como una imagen
	try:
		imagen= "/tmp/imagen.png"
		comando= "gst-launch filesrc location=%s" % (archivo)
		comando += " ! decodebin ! ffmpegcolorspace ! pngenc snapshot=true ! multifilesink location=%s" % (imagen)
		commands.getoutput(comando)
		return imagen
	except:
		return False

