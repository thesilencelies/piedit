#!/usr/bin/env python

"""Piet IDE, written in Python. It's badass."""

import sys
import os.path
import pygtk
import gtk
import gtk.glade
import gnome
import piedit.ui
pygtk.require("2.0")

__author__ = "Steven Anderson"
__copyright__ = "Steven Anderson 2008"
__credits__ = ["Steven Anderson"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Steven Anderson"
__email__ = "steven.james.anderson@googlemail.com"
__status__ = "Production"
        

class Program:
    """Class that runs the main program"""
    
    def __init__(self):
        """Loads the glade XML and creates the ui object"""
        gnome.init("Piedit", "0.1")
        gladeui = gtk.glade.XML(os.path.dirname(sys.argv[0])+"/glade/piedit.glade")
        
        ui = piedit.ui.UI(gladeui)

if __name__ == "__main__":
    program = Program()
    gtk.main()
