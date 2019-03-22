#!/usr/bin/env python

from bullet import Bullet
from datetime import datetime
from collections import OrderedDict
from typing import Dict, Optional
from subprocess import check_output, call, CalledProcessError, DEVNULL


###
# HELPERS, SUBPROCESS CALLS
###

def clear():
    call("clear")


def get_running_tmuxes() -> Dict[str, datetime]:
    tmuxes = dict()
    try:
        output: str = check_output(
            ["tmux", "list-sessions", "-F", "#{session_name}__separator__#{session_created}"],
            stderr=DEVNULL
        ).decode()
    except CalledProcessError:
        pass
    else:
        for line in output.splitlines():
            if line:
                name, epoch = line.split("__separator__")
                tmuxes[name] = datetime.fromtimestamp(int(epoch))
    return tmuxes


def attach_tmux(tmux: str):
    call(["tmux", "attach", "-t", tmux])


def kill_tmux(tmux: str):
    call(["tmux", "kill-session", "-t", tmux])


def run_command_in_tmux(tmux: str, command: str):
    call(["tmux", "send", "-t", tmux, command, "ENTER"])

###
# OPTIONS (SUBMENUS)
###


def choose_tmux(tmuxes: Dict[str, datetime]) -> Optional[str]:
    options = OrderedDict(
        (name, "{} ({})".format(name, dt.strftime("%d/%m %H:%M:%S")))
        for name, dt
        in sorted(list(tmuxes.items()), key=lambda kv: kv[1], reverse=True)
    )
    options[None] = "Volver"
    cli = Bullet(
        prompt="\nSelecciona un tmux:",
        choices=list(options.values())
    )
    selected = cli.launch()
    return next(key for key in options.keys() if options[key] == selected)


def option_open_running_tmux():
    selection = choose_tmux(get_running_tmuxes())
    if selection:
        attach_tmux(selection)
    clear()


def option_create_new_tmux():
    try:
        name = input("Nombre para el nuevo tmux (vacío para valor por defecto): ")
    except (KeyboardInterrupt, InterruptedError):
        pass
    else:
        if name:
            call(["tmux", "new", "-s", name])
        else:
            call(["tmux", "new"])
    clear()


def option_run_command_in_tmux():
    selection = choose_tmux(get_running_tmuxes())
    if selection:
        clear()
        command = input("Introduce el comando a ejecutar (vacío para cancelar): ")
        if command:
            run_command_in_tmux(selection, command)
    clear()


def option_kill_tmux():
    selection = choose_tmux(get_running_tmuxes())
    if selection:
        kill_tmux(selection)
    clear()


def option_exit():
    exit(0)


###
# MAIN MENU
###

def main():
    running_tmuxes = len(get_running_tmuxes())
    options = OrderedDict()
    if running_tmuxes > 0:
        options["Abrir un tmux en ejecución"] = option_open_running_tmux
        options["Ejecutar comando en un tmux"] = option_run_command_in_tmux
        options["Matar un tmux"] = option_kill_tmux
    options["Crear un nuevo tmux"] = option_create_new_tmux
    options["Salir"] = option_exit
    cli = Bullet(
        prompt="\nHay {} tmuxes en ejecución.\nSelecciona una acción:".format(running_tmuxes),
        choices=list(options.keys())
    )
    select = cli.launch()
    clear()
    options[select]()


###
# MAIN
###

if __name__ == "__main__":
    while True:
        try:
            main()
        except (KeyboardInterrupt, InterruptedError):
            clear()
            option_exit()
