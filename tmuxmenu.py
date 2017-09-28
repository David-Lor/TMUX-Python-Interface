#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, os, atexit
from getch import getch
from time import sleep

ARROW_HEADER = "\x1b"
ARROW_LEFT = "[D"
ARROW_RIGHT = "[C"
ARROW_UP = "[A"
ARROW_DOWN = "[B"
TAB = "\t"
ENTER = "\n"
SPACE = " "
validos = [ARROW_DOWN, ARROW_HEADER, ARROW_LEFT, ARROW_RIGHT, ARROW_UP, TAB, ENTER, SPACE]

def clr():
	os.system("clear")

@atexit.register
def atexit_f():
	clr()

def mainmenu():
	titulo = "MENÚ TMUX"
	opciones = [
		"Abrir un tmux en ejecución", #0
		"Crear nuevo tmux", #1
		"Enviar comandos a tmux en ejecución", #2
		"Salir" #3
	]
	opciones_letras = ['a', 'c', 'e', 'q']
	seleccion = 0
	while True:
		seleccionado = False
		render(titulo, opciones, opciones_letras, seleccion)
		while seleccionado == False: #Reejecutar si se pulsa cualquier otra cosa
			seleccionado = seleccionar(opciones, opciones_letras, seleccion)
		if isinstance(seleccionado, list): #Cambio de opción o selección con textual
			seleccion = seleccionado[1]
			if seleccionado[0] == True: #Seleccionada opción con textual
				break
		elif seleccionado == True: #Enter sobre opción
			break
	
	if seleccion == 0:
		submenu_choosetmux()
	elif seleccion == 1:
		submenu_newtmux()
	elif seleccion == 2:
		print("\n\nEnviar TMUX")
		exit()
	elif seleccion == 3:
		exit()


def submenu_newtmux():
	"""Creación de nuevo tmux con nombre personalizado"""
	clr()
	tmuxname = input("Introduce nombre para el nuevo tmux: ")
	subprocess.call(["tmux","new","-s",tmuxname])
	mainmenu()


def submenu_choosetmux():
	"""Selección de uno de los tmux disponibles en el sistema para su apertura
	Devuelve:
	(to-do)"""
	try:
		clr()
		o = subprocess.check_output(["tmux", "ls"]).splitlines()
	
	except: #Sin tmuxes
		clr()
		print("¡No hay tmuxes disponibles!")
		sleep(1.5)
		
	else: #Con tmuxes
		o = [ s.split(b': ')[0].decode("utf-8") for s in o ]
		textuales = [ str(x) for x in range( len(o) ) ]
		o.append("Volver")
		textuales.append("q")
		seleccion = 0

		while True:
			render(
				titulo = "** Hay %s Tmuxes abiertos**" % len(o),
				opciones = o,
				textuales = textuales,
				seleccion = seleccion,
				textual_izq = True
			)
			
			seleccionado = False
			while seleccionado == False:
				seleccionado = seleccionar(
					opciones = o,
					textuales = textuales,
					seleccion = seleccion
				)
			
			if isinstance(seleccionado, list): #Cambio de opción o selección con textual
				seleccion = seleccionado[1]
				if seleccionado[0] == True: #Seleccionada opción con textual
					break
			elif seleccionado == True:
				break
		if not seleccion == (len(o) - 1):
			subprocess.call( [ "tmux", "attach", "-t", o[seleccion] ] )

	finally:
		mainmenu() #Volver al menú principal



def render(titulo, opciones, textuales, seleccion, textual_izq=False):
	"""Imprime la lista asignada y actualiza pantalla"""
	clr()
	print(titulo)
	for o in opciones:
		ast = "   "
		index = opciones.index(o)
		if seleccion == index:
			ast = ">> "
		if textual_izq:
			print( "{}[{}] {}".format(ast, textuales[index], o) )
		else:
			print( "{}{} [{}]".format(ast, o, textuales[index]) )


def seleccionar(opciones, textuales, seleccion):
	"""Procesa la acción realizada por el teclado.
	Acciones disponibles:
		* Flechas arriba/abajo
		* Pulsar teclas concretas ("textuales")
		* Tab
		* Enter/Space
	Devuelve:
		* True: Seleccionada opción (Enter)
		* False: cualquier otra cosa pulsada que no debe procesarse
		* [False, int]: Índice de selección al pulsar flechas
		* [True, int]: Opción seleccionada por atajo de teclas "textuales"
	"""
	vd = validos
	vd += textuales
	s1 = getch()
	if s1 not in vd:
		return False
	
	if s1 == ARROW_HEADER: #Teclas numéricas devuelven 3 valores Getch
		s2 = getch()
		s3 = getch()
		sa = s2 + s3

		if ( sa == ARROW_DOWN ) and ( seleccion < len(opciones)-1 ):
			return [False, seleccion + 1]
		elif ( sa == ARROW_UP ) and ( seleccion > 0 ):
			return [False, seleccion - 1]
	
	elif s1 == TAB:
		seleccion += 1
		if seleccion > len(opciones)-1:
			seleccion = 0
		return [False, seleccion]
	
	elif s1 == ENTER or s1 == SPACE:
		return True

	else: #Textuales
		return [True, textuales.index(s1)]

if __name__ == "__main__":
	mainmenu()