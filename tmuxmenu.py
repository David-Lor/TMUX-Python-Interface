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
		"Matar un tmux en ejecución", #2
		"Enviar comandos a tmux en ejecución", #3
		"Salir" #4
	]
	opciones_letras = ['a', 'c', 'k', 'e', 'q']
	
	while True:
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
		
		if seleccion == 0: #Elegir tmux
			submenu_opentmux()
		elif seleccion == 1: #Nuevo tmux
			submenu_newtmux()
		elif seleccion == 2: #Matar tmux
			submenu_killtmux()
		elif seleccion == 3: #Enviar comando a tmux
			submenu_sendtmux()
		elif seleccion == 4: #Salir
			exit()


def submenu_newtmux():
	"""Creación de nuevo tmux con nombre personalizado"""
	clr()
	tm = input("Introduce nombre para el nuevo tmux: ")
	subprocess.call(["tmux","new","-s",tm])

def submenu_opentmux():
	tm = choosetmux()
	if tm == False:
		return
	subprocess.call( ["tmux", "attach", "-t", tm] )

def submenu_killtmux():
	tm = choosetmux()
	if tm == False:
		return
	subprocess.call( ["tmux", "kill-pane", "-t", tm] )

def submenu_sendtmux():
	tm = choosetmux()
	if tm == False:
		return
	clr()
	order = input("Introduce orden que enviar al tmux '%s': " % tm)
	subprocess.call( ["tmux", "send", "-t", tm, order, "ENTER"] )

tmux_seleccionado = 0
def choosetmux():
	"""Selección de uno de los tmux disponibles en el sistema
	Devuelve el nombre del tmux seleccionado, o False si no se seleccionó ninguno o no hay tmuxes disponibles"""
	global tmux_seleccionado
	try:
		clr()
		o = subprocess.check_output(["tmux", "ls"]).splitlines()
	
	except: #Sin tmuxes
		clr()
		print("¡No hay tmuxes disponibles!")
		sleep(1.5)
		return False
		
	else: #Con tmuxes
		o = [ s.split(b': ')[0].decode("utf-8") for s in o ]
		textuales = [ str(x) for x in range( len(o) ) ]
		o.append("Volver")
		textuales.append("q")

		while True:
			render(
				titulo = "** Hay {} Tmuxes abiertos**".format(len(o)-1),
				opciones = o,
				textuales = textuales,
				seleccion = tmux_seleccionado,
				textual_izq = True
			)
			
			seleccionado = False
			while seleccionado == False:
				seleccionado = seleccionar(
					opciones = o,
					textuales = textuales,
					seleccion = tmux_seleccionado
				)
			
			if isinstance(seleccionado, list): #Cambio de opción o selección con textual
				tmux_seleccionado = seleccionado[1]
				if seleccionado[0] == True: #Seleccionada opción con textual
					break
			elif seleccionado == True:
				break
		if tmux_seleccionado == (len(o) - 1):
			tmux_seleccionado = 0
			return False
		else:
			return o[tmux_seleccionado]



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