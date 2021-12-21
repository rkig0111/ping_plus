#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pip install ping3
pip install uni-curses
for linux, i must do:
sudo ln -s /usr/lib/x86_64-linux-gnu/libpanelw.so.6.2 libpanelw.so.6.2
"""

import os, time, sys
from pathlib import Path
import ping3
from unicurses import *

if os.name == 'nt':
    import win32gui

def init_ctrl_srv():
    global LINES, COLS
    if os.name == 'nt':
        current = win32gui.GetForegroundWindow()
        win32gui.MoveWindow(current, 300, 10, 800, 700, True)
    global LINES, COLS
    stdscr = initscr()
    start_color()
    init_pair(1, COLOR_GREEN, COLOR_BLACK)
    init_pair(2, COLOR_RED, COLOR_BLACK)
    init_pair(3, COLOR_BLUE, COLOR_BLACK)
    noecho()
    cbreak()
    nodelay(stdscr, True)
    curs_set(False)
    #LINES, COLS = getmaxyx(stdscr)
    LINES, COLS = (40, 80)
    
def close_ctrl_srv():
    curs_set(True)
    endwin()

def affiche_err():
    mvaddstr(1, COLS/2 - 5, "error")
    close_ctrl_srv()

def kbhit():
        ch = getch()
        if ch != ERR:
            ungetch(ch)
            return True
        else:
            return False
            
def analyse(fichier4analyse):
    global rep
    global result
    global cpt
    cpt = 0
    running = True
    # clear()
    result = list_ip(fichier4analyse)
    mvaddstr( 1, COLS - 60, "space bar for stop program", color_pair(3))
    refresh()
    if isinstance(result, str):
        mvaddstr( 1, COLS - 40, "error on variable 'result'")
        print("error on variable 'result' ")
        affiche_err()
    else:
        while running :
            cpt = cpt+1
            affiche_ping()
            time.sleep(0.1)
            key = getch()
            if (key == ord(' ')):
                running = False
            refresh()
    close_ctrl_srv()

def affiche_ping():
    global fichier
    cpt1 = str(cpt)
    index = 0
    xorg = 3
    yorg = 3
    timeout = 0.5
    temps = time.localtime()
    date = "%02d/%02d/%04d   %02d:%02d:%02d" %(temps[2],temps[1],temps[0],temps[3],temps[4],temps[5])
    mvaddstr( 0,0, date)
    mvaddstr( 0,30, cpt1)
    mvaddstr( 0,40, fichier)
    refresh()
    for ip in result:
        try:
            delay = ping3.ping(ip[0], unit='ms', timeout=0.5) # adjust timeout if necessary
            if delay != None:           # one response, write in green
                g = 1
                mvaddstr( yorg+index, xorg, ip[0], color_pair(g))
                mvaddstr( yorg+index, xorg+15, " : ", color_pair(g))
                mvaddstr( yorg+index, xorg+20, ip[1], color_pair(g))
                refresh()
            else:                        # no response, write in red
                g = 2
                mvaddstr( yorg+index, xorg, ip[0], color_pair(g))
                mvaddstr( yorg+index, xorg+15, " : ", color_pair(g))
                mvaddstr( yorg+index, xorg+20,ip[1], color_pair(g))
                refresh()
            index = index+ 1
            #time.sleep(0.5)
        except:                          # no ping possible, write in blue
            g = 3
            mvaddstr( yorg+index, xorg,ip[0], color_pair(g))
            mvaddstr( yorg+index, xorg+15, " : ", color_pair(g))
            mvaddstr( yorg+index, xorg+20,ip[1], color_pair(g))
            mvaddstr( yorg+index, xorg+35,"    impossible de resoudre le nom", color_pair(g))
            refresh()
            index = index+ 1
          
def list_ip(fichier4analyse):
    global fichier
    lip = []
    p = Path('.')
    fichier = p / fichier4analyse
    fichier = fichier.with_suffix('.ip')
    if fichier.exists():
        with open(fichier, 'r') as ficr:
            try :
                for ligne in ficr:
                    if ligne[0] == "#":
                        continue
                    else:
                        res0 = ligne.rstrip('\n')
                        res1 = res0.split(',')                    
                        nom = res1[0].rstrip()
                        description = res1[1]
                        lip = lip + [(nom, description)]
            except:
                print("Error in file : ' %s '" %(fichier))
                lip = lip + [("localhost","Error in file : ' %s '" %(fichier))]
            return lip
    else:
        #print(lip)
        lip = lip + [("localhost","please, fill the file : ' %s '" % (fichier))]
        return lip        

def create_range_file(ip, nb):
    with open('range.ip', 'w') as fic:
        preamb = """#syntaxe: addrIP or hostname, description
#no blank line etc ...
#only '#' can do a comment!
#
#-------------------------
#\n"""
        fic.write(preamb)
        for x in range(0, nb):            
            ipl = ip.split('.')            
            ipl[-1] = str(int(ipl[-1])+x)  # we increase the starting ip up to nb times
            res = ".".join(ipl)
            fic.write(res + ',' + res + "\n")
        
def find_ip_file():
    fic_ip = sorted(Path('.').glob('**/*.ip'))
    for x in fic_ip:
        print(x.stem)
    rep = input("choose the scan to perform : ")
    return rep        

if __name__ == '__main__':
    global fichier
    global rep
    global param
    rep = ""
    param = sys.argv 
    if len(param)==1:        
        print( "test ping by rkig0111" )
        print( "\tusage: python3 controle.py  'name of vlan'" )
        print( "\tusage: python3 controle.py  range start_ip nb_ping")
        print( "\tusage: python3 controle.py  range 192.168.0.50 10")
        print( "\tdo ping from 192.168.0.50 ----> 192.168.0.59 \n\n")
        time.sleep(4)
        fichier4analyse = find_ip_file()
    else:
        if param[1] in ['range', 'plage']:            
            ip, nb = param[2], param[3]  # start_ip,  number of consecutive ping
            create_range_file(ip, int(nb))  # create file with ".ip" format
            fichier4analyse = "range" 
        else:
            fichier4analyse = param[1]

    init_ctrl_srv()
    analyse(fichier4analyse)
    endwin()

