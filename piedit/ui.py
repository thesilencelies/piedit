"""UI classes for the piedit project"""

import sys
import os
import threading
import time
import pygtk
import gtk
import gnome.ui
import string
import PIL.Image
import piedit.colors
import piedit.interpreter
import piedit.debug
pygtk.require("2.0")

__author__ = "Steven Anderson"
__copyright__ = "Steven Anderson 2008"
__credits__ = ["Steven Anderson"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Steven Anderson"
__email__ = "steven.james.anderson@googlemail.com"
__status__ = "Production"


class InterpreterThread(threading.Thread):
    def __init__(self,filename,callback,debug=False):
        self.should_stop = False
        self.interpreter = piedit.interpreter.Interpreter(thread=self)
        self.interpreter.debug.DEBUG = debug
        self.filename = filename
        self.callback = callback
        threading.Thread.__init__(self)
        
    def run(self):
        self.interpreter.run_program(self.filename)
        self.callback(self.should_stop)
        
    def stop(self):
        self.should_stop = True
        
class Handlers:
    """Defines the signal handlers for the ui"""
    
    def __init__(self,ui):
        """Sets up object properties"""
        self._ui = ui
        self.file_filter = gtk.FileFilter()
        self.file_filter.add_pattern("*.png")
        self.file_filter.set_name("PNG Files")

    def on_mainApp_delete_event(self, *args):
        """Handler for application close"""
        if self._ui.save_changes():
            try:
                self.interpreter_thread.stop()
            except:
                pass
            gtk.main_quit()

    #File Menu
    def on_fileNewMenuItem_activate(self, *args):
        """Handler for File|New menu item"""
        if self._ui.save_changes():
            self._ui.clear_image()

    def on_fileOpenMenuItem_activate(self, *args):
        """Handler for File|Open menu item"""
        if self._ui.save_changes():
            fileChooser = gtk.FileChooserDialog(
                title="Open File", 
                action=gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            fileChooser.add_filter(self.file_filter)
            response = fileChooser.run()
            if response == gtk.RESPONSE_OK:
                path = fileChooser.get_filename()
                self._ui.load_image(path)
            fileChooser.destroy()
      
    def on_fileSaveMenuItem_activate(self, *args):
        """Handler for File|Save menu item"""
        if self._ui.current_file is None:
            return self.on_fileSaveAsMenuItem_activate(args)
        else:
            self._ui.save_image(self._ui.current_file)
            return True
            
    def on_fileSaveAsMenuItem_activate(self, *args):
        """Handler for File|Save As menu item"""
        fileChooser = gtk.FileChooserDialog(
            title="Save File", 
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        fileChooser.add_filter(self.file_filter)
        fileChooser.set_do_overwrite_confirmation(True)
        response = fileChooser.run()
        if response == gtk.RESPONSE_OK:
            filename = fileChooser.get_filename()
            if (not filename == None) and (not filename.endswith(".png")):
                filename = filename + ".png"
            self._ui.save_image(filename)
            fileChooser.destroy()
            return True
        else:
            fileChooser.destroy()
            return False
        
    def on_fileQuitMenuItem_activate(self, *args):
        """Handler for File|Quit menu item"""
        if self._ui.save_changes():
            gtk.main_quit()

    #Edit Menu
    def on_editCutMenuItem_activate(self,*args):
        """Handler for Edit|Cut menu item"""
        print "Edit Cut"
    def on_editCopyMenuItem_activate(self,*args):
        """Handler for Edit|Copy menu item"""
        print "Edit Copy"
    def on_editPasteMenuItem_activate(self, *args):
        """Handler for Edit|Paste menu item"""
        print "Edit Paste"
    def on_editDeleteMenuItem_activate(self, *args):
        """Handler for Edit|Delete menu item"""
        print "Edit Delete"
  
    #View Menu
    #No handlers here yet
    
    #Run Menu           
    def thread_end_callback(self,was_cancelled):
        if was_cancelled:
            self.set_run_menu(running=False,status="Cancelled")
        else:
            self.set_run_menu(running=False,status="Complete")
        
    def on_runRunMenuItem_activate(self,*args):
        """Handler for Run|Run menu item"""
        self.set_run_menu(running=True,status="Running...")
        self.interpreter_thread = InterpreterThread(self._ui.current_file,self.thread_end_callback,debug=False)
        self.interpreter_thread.start()
    
    def on_runDebugMenuItem_activate(self,*args):
        """Handler for Run|Debug menu item"""
        self.set_run_menu(running=True,status="Debugging...",debug=True)
        self._ui.interpreter = piedit.interpreter.Interpreter()
        self._ui.interpreter.debug.DEBUG = True
        self._ui.interpreter.run_program(self._ui.current_file,start=False)
    
    def on_runStepMenuItem_activate(self,*args):
        if self._ui.interpreter.do_next_debug_step():
            pass
        else:
            self.set_run_menu(running=False,status="Complete")

    def on_runStopMenuItem_activate(self,*args):
        if self._ui.interpreter.debug.DEBUG:
            self.thread_end_callback(True)
        else:
            self.interpreter_thread.stop()
        
    def set_run_menu(self,running,status,debug=False):
        if running:
            self._ui.gladeui.get_widget("runRunMenuItem").set_sensitive(False)
            self._ui.gladeui.get_widget("runDebugMenuItem").set_sensitive(False)
            self._ui.gladeui.get_widget("runStopMenuItem").set_sensitive(True)
            self._ui.gladeui.get_widget("runStepMenuItem").set_sensitive(debug)
        else:
            self._ui.gladeui.get_widget("runStopMenuItem").set_sensitive(False)
            self._ui.gladeui.get_widget("runStepMenuItem").set_sensitive(False)
            self._ui.gladeui.get_widget("runRunMenuItem").set_sensitive(True)
            self._ui.gladeui.get_widget("runDebugMenuItem").set_sensitive(True)
        self._ui.gladeui.get_widget("statusBar").set_status(status)
    #Help Menu
    def on_helpAboutMenuItem_activate(self,*args):
        """Handler for Help|About menu item"""
        print "Help About"

    #Non-menu hadlers
    def on_programTable_button_press_event(self, widget, event):
        self._ui.set_pixel_color(int(event.x),int(event.y))

    def on_codelColorEventBox_clicked(self, widget, event):
        """Handler for clicking a codel color event box"""
        self._ui.set_selected_color(widget)

    def on_programTable_expose_event(self, widget, event):
        #Add event boxes to program table
        self._ui.initialise_program_table()              
             
      
class UI:
    """Wrapper class for the UI. Provides functions to do things in the UI"""

    def __init__(self,gladeui):
        """Sets up the object properties"""
        self.changes_made = False
        self.selected_color = None
        self.current_file = None
        self.gladeui = gladeui
        self.selected_color_widget = None
        
        self.default_height = 10
        self.default_width = 10
        self.width = self.default_width
        self.height = self.default_height
        self.max_width = 1000
        self.max_height = 1000
        
        self.handlers = Handlers(self)
        self.gladeui.signal_autoconnect(self.handlers)
        self.message_handler = MessageHandler(self)
        self.initialise_ui()

    def save_image(self,path):
        """Saves the current program table to an image"""
        image = PIL.Image.new("RGB",(self.width,self.height))
        image.putdata(self.pixels)
        image.save(path, "PNG")
        self.message_handler.handle_message("FILE_SAVED")
        self.set_current_file(path)
        self.set_changes_made(False)
        self.set_window_title(os.path.basename(path))
    
    def load_image(self,path):
        """Loads an image from file and displays it in the program table"""
        try:
            image = PIL.Image.open(path)
            if image.mode != "RGB":
                image = image.convert("RGB")
        except IOError:
            self.message_handler.handle_error("FILE_NOT_LOADED")
            return
        (self.width, self.height) = image.size
        if self.width>self.max_width or self.height>self.max_height:
            self.message_handler.handle_error("IMAGE_TOO_BIG")
        else:
            self.clear_image()
            self.pixels = list(image.getdata())
            self.initialise_program_table()
        self.set_current_file(path)
        self.set_changes_made(False)
        self.set_window_title(os.path.basename(path))

    def clear_image(self):
        """Clears the program table, i.e. fills with all whites"""        
        self.gladeui.get_widget("programTable").window.clear()
        self.pixels = [piedit.colors.hex_to_rgb(piedit.colors.white) for y in xrange(self.height) for x in xrange(self.width)]
        self.set_current_file(None)
        self.set_window_title("Untitled.bmp")
        self.set_changes_made(True)
        
    def set_pixel_color(self,x,y):
        """Sets the color of a program table pixel to the currently selected color"""
        program_table = self.gladeui.get_widget("programTable").window
        pt_width, pt_height = program_table.get_size()
        width_per_pixel = pt_width/self.width
        height_per_pixel = pt_height/self.height
        
        x = x // width_per_pixel
        y = y // height_per_pixel
        
        if self.selected_color:
            self.pixels[y*self.width+x] = piedit.colors.hex_to_rgb(self.selected_color)
            self.set_changes_made(True)
            self.initialise_program_table()

    def set_selected_color(self,color_widget):
        """Sets the currently selected color. Called when the codel color chooser is clicked"""
        try:
            self.selected_color_widget.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(self.selected_color_widget.default_color))
        except AttributeError:
            pass
        color_widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#333333"))
        self.selected_color = color_widget.default_color
        self.selected_color_widget = color_widget
        
    def set_changes_made(self,changes):
        """Sets whether changes have been made to the current program"""
        self.changes_made = changes
        self.set_window_title_changed(changes)

    def set_current_file(self,path):
        """Sets the path of the current program"""
        self.current_file = path
        
    def set_window_title(self,title,clear=False):
        """Sets the window title"""
        if not clear:
            self.gladeui.get_widget("mainApp").set_title("Piedit | "+title)
        else:
            self.gladeui.get_widget("mainApp").set_title(title)
        
    def get_window_title(self):
        """Gets the window title"""
        return self.gladeui.get_widget("mainApp").get_title()
        
    def set_window_title_changed(self,changes):
        """Appends or removes the "*" from the window title depending on whether
        changes have been made or not"""
        window_title = self.get_window_title()
        if changes:
            if window_title.endswith("*"):
                pass
            else:
                self.set_window_title(window_title+" *",clear=True)
        else:
            if window_title.endswith("*"):
                self.set_window_title(window_title[:-2], clear=True)
            else:
                pass
        
    def save_changes(self):
        """Prompts the user to save changes if there have been changes.
        Returns false if the user cancelled, true otherwise"""
        if self.changes_made:
            return self.message_handler.handle_save_msgbox()
        else:
            return True    
        
    def initialise_ui(self):
        """Initialises the UI. Adds the codel color chooser event boxes and 
        the program table event boxes. Attaches handlers and sets colors etc."""
        
        #Add event boxes to codel color chooser
        self.codelColors = [gtk.EventBox() for color in piedit.colors.all_colors()]
        for (color,(x,y),i) in zip(piedit.colors.all_colors(),
                   ((x,y) for x in xrange(7) for y in xrange(3)),
                   xrange(len(self.codelColors))):  
            event_box = self.codelColors[i]
            event_box.set_events(gtk.gdk.BUTTON_PRESS_MASK)
            event_box.visible = True
            self.gladeui.get_widget("codelColorsTable").attach(
                    event_box,
                    x,
                    x+1,
                    y,
                    y+1,
                    xoptions=gtk.EXPAND|gtk.FILL, 
                    yoptions=gtk.EXPAND|gtk.FILL, 
                    xpadding=1, 
                    ypadding=1)
            event_box.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(color))
            event_box.set_size_request(-1,30)
            event_box.default_color=color
            event_box.connect("button_press_event", self.handlers.on_codelColorEventBox_clicked)   
            event_box.show()
        
        #Initialise image     
        program_table = self.gladeui.get_widget("programTable")
        program_table.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        program_table.connect("button_press_event", self.handlers.on_programTable_button_press_event)
        self.clear_image()
        
    def initialise_program_table(self):
        program_table = self.gladeui.get_widget("programTable").window
        pt_width, pt_height = program_table.get_size()
        width_per_pixel = pt_width/self.width
        height_per_pixel = pt_height/self.height
        
        colormap = gtk.gdk.colormap_get_system()
        black = colormap.alloc_color('black')
        white = colormap.alloc_color('white')

        gc = gtk.gdk.GC(drawable=program_table,\
                        foreground=black,\
                        background=black)

        for x in xrange(self.width):
            for y in xrange(self.height):
                gc.set_foreground(black)
                program_table.draw_rectangle(gc,False,x*width_per_pixel,y*height_per_pixel,width_per_pixel,height_per_pixel)    
                try:
                    pixel = self.pixels[y*self.width+x]
                    fg = colormap.alloc_color(piedit.colors.rgb_to_hex(pixel))
                    gc.set_foreground(fg)
                except AttributeError:
                    gc.set_foreground(white)
                program_table.draw_rectangle(gc,True,x*width_per_pixel+1,y*height_per_pixel+1,width_per_pixel-1,height_per_pixel-1)    

    
class MessageHandler:
    """Class to handle errors and display them to the user"""
    def __init__(self,ui):
        """Sets up error messages"""
        self._ui = ui
        self.error_messages = {
            "IMAGE_TOO_BIG":"The image couldn't be loaded because it's too big.\n"
                            +"At present we only support images up to 10x10 pixels.\n"
                            +"Sorry :(",
            "FILE_NOT_LOADED":"The image could not be loaded.\n"
                            +"Either the file doesn't exist, or it wasn't\n"
                            +"recognised as an image"}
        self.messages = {
            "FILE_SAVED":"File saved successfully",
            "SAVE_CHANGES":"Would you like to save changes to the current file?"}
        
    def handle_error(self,error_type):
        """Handles an error. Displays an error dialog to the user"""
        msgbox = gtk.MessageDialog(
            parent=self._ui.gladeui.get_widget("mainWindow"),
            flags=gtk.DIALOG_MODAL,
            type=gtk.MESSAGE_ERROR,
            buttons=gtk.BUTTONS_OK,
            message_format=self.error_messages[error_type])
        msgbox.run()
        msgbox.destroy()
    
    def handle_message(self,message_type):
        """Handles a message. Displays an information dialog to the user"""
        msgbox = gtk.MessageDialog(
            parent=self._ui.gladeui.get_widget("mainWindow"),
            flags=gtk.DIALOG_MODAL,
            type=gtk.MESSAGE_INFO,
            buttons=gtk.BUTTONS_OK,
            message_format=self.messages[message_type])
        msgbox.run()
        msgbox.destroy()
    
    def handle_save_msgbox(self):
        """Presents the save changes prompt to the user"""
        msgbox = gtk.MessageDialog(
            parent=self._ui.gladeui.get_widget("mainWindow"),
            flags=gtk.DIALOG_MODAL,
            type=gtk.MESSAGE_QUESTION,
            buttons=gtk.BUTTONS_YES_NO,
            message_format=self.messages["SAVE_CHANGES"])
        response = msgbox.run()
        msgbox.destroy()
        if response == gtk.RESPONSE_YES:
            return self._ui.handlers.on_fileSaveMenuItem_activate()
        elif response == gtk.RESPONSE_NO:
            return True
        else:
            return False
