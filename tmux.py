#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

def chooseoption():
    print("Selecciona una opción y pulsa Enter:")
    print("[a] [1] - Abrir un tmux en ejecución")
    print("[c] [2] - Crear nuevo tmux")
    print("[e] [3] - Enviar comando a un tmux en ejecución")
    print("[q] [0] - Salir")
    validopt = ['a','c','e','q','0','1','2','3']
    opt = raw_input() #lee string + enter
    if validopt.__contains__(opt):
        return opt
    else:
        clearscreen()
        print("Orden no entendida")
        return 0

def list_tmux(): #función para listar los tmux en ejecución y seleccionar uno. Compatible con varias funciones. Devuelve un string con el nombre del tmux seleccionado.
    try:
        print("Listado de tmuxes abiertos: selecciona uno:")
        output = str( subprocess.check_output(["tmux","ls"]) )
        splitout = output.split("\n")
        n = len(splitout)
        linenames = list()
        for i in range(n-1):
            line = splitout[i]
            linename = splitout[i].split(": ")
            linenames.append(linename[0])
            print( "[" + str(i) + "] Nombre: " + linename[0] + " | " + linename[1] )
        op = raw_input()
        try:
            opindex = int(op)
            if (not opindex > n) and (not opindex < 0):
                return str(linenames[opindex]) #el P.P. se encarga de ejecutar la siguiente función
            else: #si se introduce un valor fuera de rango
                clearscreen()
                print("Opción no válida (fuera de rango)")
                st = list_tmux() #rellamada a la función y capturar el valor para return
                return st
        except: #si se introduce un valor inválido
            clearscreen()
            print("Opción no válida (valor inválido)")
            st = list_tmux() #rellamada a la función y capturar el valor para return
            return st
    except: #si no hay tmuxes abiertos, la ejecución anterior dará error, saltando a este punto.
        clearscreen()
        print("No hay tmuxes abiertos.")
        return 0 #devolver un 0, que indica que no hay tmuxes abiertos

def open_tmux(dest): #hay que pasarle un tmux (nombre del tmux en str), previamente escogido con la función list_tmux
    print ( "Seleccionado el tmux " + dest )
    subprocess.call(["tmux","attach","-t",dest])
    return

def execute_in_tmux(dest): #ejecuta un comando en un tmux en ejecución, previamente escogido co la función list_tmux
    print ( "Seleccionado el tmux " + dest )
    print("Escribe el comando que deseas ejecutar:")
    try:
        comm = str( raw_input() )
        subprocess.call(["tmux","send","-t",dest,comm,"ENTER"])
        print ("Lanzado con éxito el comando " + comm + " en el tmux " + dest )
        return
    except: #si hubo algún error al leer el comando
        clearscreen()
        print("Error al leer el comando introducido.")
        return

def create_tmux():
    print("Crear nuevo tmux: introduce un nombre para este tmux:")
    tmuxname = raw_input()
    print ( "Creado el nuevo tmux llamado: " + str(tmuxname) )
    subprocess.call(["tmux","new","-s",tmuxname])
    return

def clearscreen():
    subprocess.call("clear")
    return

while True:
    print("*-. HERRAMIENTA TMUX .-*")
    opt = chooseoption()
    error = False
    if not opt == 0: #si NO se return un 0 al elegir opción, se seleccionó una opción correcta
        if opt == "a" or opt == "1":
            tm = list_tmux()
            if not tm == 0: open_tmux(tm) #saltar al siguiente punto sólo si hay tmuxes disponibles.
            else: error = True #usar el bool error para evitar que se limpie la pantalla
        elif opt == "c" or opt == "2":
            create_tmux()
        elif opt == "e" or opt == "3":
            tm = list_tmux()
            if not tm == 0: execute_in_tmux(tm) #saltar al siguiente punto sólo si hay tmuxes disponibles.
            else: error = True #usar el bool error para evitar que se limpie la pantalla
        elif opt == "q" or opt == "0":
            print("Adiós!")
            break
        if not error: clearscreen() #limpiar la pantalla si todo fue bien. En caso de errores, la orden de limpiar pantalla se debe aplicar en las propias funciones! en caso de que las funciones devuelvan 0 (habiendo pasado sin problemas el paso de seleccionar opción) se debe usar el bool "error = True" para que no se limpie la pantalla en este punto (por ejemplo, si el error = no hay tmuxes disponibles)
