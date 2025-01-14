#!/home/tepx/Packages/miniconda3/envs/device/bin/python
# coding: latin-1
# e.g.
#  python run_manual.py -T 28 -g 4
import os, sys, time, datetime
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import numpy as np
from utils import warning, checkGUIMode
from monitor import monitor
from chamber_commands import connectClimateChamber, sendSimServCmd, unpackSimServData
import yocto_commands as YOCTO
from yocto_commands import connectYoctoMeteo, disconnectYoctoMeteo
from argparse import ArgumentParser
import subprocess
description = '''Stop running the climate chamber.'''
parser = ArgumentParser(prog="stop",description=description,epilog="Good luck!")
parser.add_argument('-W', '--warmup',    dest='warmup', default=False, action='store_true',
                                         help="force warm-up" )
parser.add_argument('-T', '--target',    dest='target', type=float, default=20.0, action='store',
                                         help="target temperature for warm-up in degrees Celsius" )
parser.add_argument('-g', '--gradient',  dest='gradient', type=float, default=5.0, action='store',
                                         help="gradient in K/min." )
parser.add_argument('-t', '--time',      dest='dtime', type=int, default=-1, action='store',
                                         help="duration of data taking in seconds" )
parser.add_argument('-n', '--nsamples',  dest='nsamples', type=int, default=-1, action='store',
                                         help="number of data readings; -1 for indefinite monitoring (until monitor window closes or monitoring is interrupted)" )
parser.add_argument('-s', '--stepsize',  dest='stepsize', type=int, default=8, action='store',
                                         help="sampling frequency of data reading in seconds" )
parser.add_argument('-w', '--width',     dest='twidth', type=float, default=1000, action='store',
                                         help="width of time axis in seconds" )
parser.add_argument('-o', '--output',    dest='output', type=str, default="monitor.dat", action='store',
                                         help="output log file with monitoring data (csv format)" )
parser.add_argument('-m', '--monitor',   dest='monitor', default=False, action='store_true',
                                         help="monitor with GUI window" )
parser.add_argument('-v', '--verbose',   dest='verbose', default=False, action='store_true',
                                         help="set verbose" )
args = parser.parse_args()


def the_power_supply_is_off():
    if os.path.exists("ps-control"):
        process = subprocess.Popen('./ps-control/scripts/TTi_utils.py', stdout=subprocess.PIPE, shell=True)
        output, _ = process.communicate()
        output = output.decode('utf-8')
        return ("O1:Off" in output and "O2:Off" in output)
    return True

def the_high_voltage_is_off():
    if os.path.exists("ps-control"):
        process = subprocess.Popen('./ps-control/scripts/quick_check_keithley.py', stdout=subprocess.PIPE, shell=True)
        output, _ = process.communicate()
        output = output.decode('utf-8')
        return ("The high voltage output is Off" in output)
    return True


def main(args):
  
    # CHECKS
    args.monitor = checkGUIMode(not args.monitor)

    if not the_high_voltage_is_off():
        print("The high voltage is on, please turn off it first.")
        exit()

    if not the_power_supply_is_off():
        print("The power supply is on, please turn off it first.")
        exit()

    # CONNECT
    print("Connecting to climate chamber...")
    chamber = connectClimateChamber()
    
    # STOP & MONITOR
    if args.warmup:
        chamber.forceWarmUp(args.target,args.gradient)
    else:
        chamber.stop()

    if args.monitor:
        ymeteo1 = connectYoctoMeteo(YOCTO.ymeteo1)
        ymeteo2 = connectYoctoMeteo(YOCTO.ymeteo2)
        monitor(chamber,ymeteo1,ymeteo2,batch=args.monitor,out=args.output,
                       nsamples=args.nsamples,tstep=args.stepsize,twidth=args.twidth)
    
    # DISCONNECT
    print("Closing connection...")
    chamber.disconnect()
    if args.monitor:
        disconnectYoctoMeteo()
  

if __name__ == '__main__':
    main(args)
  
