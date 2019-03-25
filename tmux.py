#!/usr/bin/env python

from bullet import Bullet
from datetime import datetime
from collections import OrderedDict
from subprocess import check_output, call, CalledProcessError, DEVNULL


###
# HELPERS, SUBPROCESS CALLS
###

def clear():
    call("clear")


def check_installed_tmux():
    """
    :return: bool
    """
    try:
        call(["tmux", "--help"], stderr=DEVNULL, stdout=DEVNULL)
    except FileNotFoundError:
        return False
    else:
        return True


def get_running_tmuxes():
    """
    :return: Dict {str: datetime}
    """
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


def attach_tmux(tmux):
    """
    :param tmux:
    :type tmux: str
    """
    call(["tmux", "attach", "-t", tmux])


def kill_tmux(tmux):
    """
    :param tmux:
    :type tmux: str
    """
    call(["tmux", "kill-session", "-t", tmux])


def run_command_in_tmux(tmux, command):
    """
    :param tmux:
    :param command:
    :type tmux: str
    :type command: str
    """
    call(["tmux", "send", "-t", tmux, command, "ENTER"])

###
# SUBMENUS HELPERS
###


def choose_tmux(tmuxes):
    """
    :param tmuxes:
    :type tmuxes: Dict {str: datetime}
    :return: str or None
    """
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
    try:
        return next(key for key in options.keys() if options[key] == selected)
    except StopIteration:
        return None

###
# OPTIONS (SUBMENUS)
###


def option_open_running_tmux():
    # noinspection PyNoneFunctionAssignment
    selection = choose_tmux(get_running_tmuxes())
    if selection:
        # noinspection PyTypeChecker
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
    # noinspection PyNoneFunctionAssignment
    selection = choose_tmux(get_running_tmuxes())
    if selection:
        clear()
        command = input("Introduce el comando a ejecutar (vacío para cancelar): ")
        if command:
            # noinspection PyTypeChecker
            run_command_in_tmux(selection, command)
    clear()


def option_kill_tmux():
    # noinspection PyNoneFunctionAssignment
    selection = choose_tmux(get_running_tmuxes())
    if selection:
        # noinspection PyTypeChecker
        kill_tmux(selection)
    clear()


def option_exit():
    exit(0)


###
# MAIN MENU
###

def main():
    clear()
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
    if not check_installed_tmux():
        print("¡Tmux no está instalado! Debes instalarlo para poder usar esta herramienta")
        exit(1)

    while True:
        try:
            main()
        except (KeyboardInterrupt, InterruptedError):
            clear()
            option_exit()
