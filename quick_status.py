#!/home/tepx/Packages/miniconda3/envs/device/bin/python
# coding: latin-1
import os, sys
sys.path.append(os.path.dirname(__file__))
from batch_chamber_commands import connectClimateChamber, defaultip,\
                            getRunStatus, checkActiveWarnings, getActiveWarnings

def addRow(col1,col2="",just=38):
    return '\n    ' + col1.ljust(just) + '  ' + col2.ljust(just)

def getCurrentStatus(**kwargs):
    """Get current status."""
  
    # SETTINGS
    ip       = kwargs.get('ip',  defaultip    )

    # CONNECT
    chamber = connectClimateChamber(ip=ip)
  
  # GET STATUS
    if chamber==None:
        string  = "  Climate chamber not found in network."
        string += addRow("Setpoint:    ", "Compr. air:  ")
        string += addRow("Temperature: ", "Dryer:       ")
    else:
        string   = "Climate chamber's currect status: %s"%(getRunStatus(chamber))
        string  += addRow("Setpoint:    %8.3f"%(chamber.getSetp()),
                        "Compr. air:  %4s"%('ON' if chamber.getAir()==1 else 'OFF'))
        string  += addRow("Temperature: %8.3f"%(chamber.getTemp()),
                        "Dryer:       %4s"%('ON' if chamber.getDryer()==1 else 'OFF'))
    
    print(string)
    chamber.disconnect()
  
def main(args):
    getCurrentStatus(out=args.output)
  

if __name__ == '__main__':
    from argparse import ArgumentParser
    description = '''Monitor climate chamber.'''
    parser = ArgumentParser(prog="monitor",description=description,epilog="Good luck!")
    parser.add_argument('-o', '--output',    dest='output', type=str, default="status.txt", action='store',
                                            help="output log file with monitoring data (csv format)" )
    args = parser.parse_args()
    main(args)
  
