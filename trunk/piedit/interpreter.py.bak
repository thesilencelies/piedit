#!/usr/bin/env python

import sys
import gtk
import PIL.Image
import colors

__author__ = "Steven Anderson"
__copyright__ = "None, it's yours"
__credits__ = ["Steven Anderson"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Steven Anderson"
__email__ = "steven.james.anderson@googlemail.com"
__status__ = "Production"

def union(parent,child):     
    if parent.set_size < child.set_size:
        child, parent = parent, child
        
    parent_head = find(parent)
    child_head = find(child)
    
    if parent_head == child_head:
        return
    
    child_head.parent = parent_head
    child_head.set_label = parent_head.set_label
    parent_head.set_size = parent_head.set_size + child_head.set_size

def find(item):
    if item.parent == item:
        return item
    else:
        item.parent = find(item.parent)
        return item.parent

def print_usage():
    print "Usage: interpreter.py image"
    
def get_chr_unix():
    import tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def get_chr_windows():
    import msvcrt
    return msvcrt.getch()

def get_chr():
    try:
        return get_chr_unix()
    except ImportError:
        return get_chr_windows()
        

class Interpreter:
    def __init__(self):
        self.current_pixel = None
        self.dp = 0
        self.cc = 0
        self.switch_cc = True
        self.step = 0 #0 for just moved into color block, 1 for moved to edge
        self.times_stopped = 0
        self.stack = []
        self.color_blocks = {}
            #Indexed by hue and light change
        self.operations = {
            (1,0):("Add",self.op_add),
            (2,0):("Divide",self.op_divide),
            (3,0):("Greater",self.op_greater),
            (4,0):("Duplicate",self.op_duplicate),
            (5,0):("IN(char)",self.op_in_char),
            (0,1):("Push",self.op_push),
            (1,1):("Subtract",self.op_subtract),
            (2,1):("Mod",self.op_mod),
            (3,1):("Pointer",self.op_pointer),
            (4,1):("Roll",self.op_roll),
            (5,1):("OUT(Number)",self.op_out_number),
            (0,2):("Pop",self.op_pop),
            (1,2):("Multiply",self.op_multiply),
            (2,2):("Not",self.op_not),
            (3,2):("Switch",self.op_switch),
            (4,2):("IN(Number)",self.op_in_number),
            (5,2):("OUT(Char)",self.op_out_char),
        }
    
    def run_program(self,path):
        print "Loading image"
        self.load_image(path)   
        print "Scanning color blocks"
        self.find_color_blocks()
        print "Starting execution"
        self.start_execution()
        
    def load_image(self,path):
        try:
            self.image = PIL.Image.open(path)
        except IOError:
            raise IOError, "IMAGE_NOT_LOADED"
        
        (self.width, self.height) = self.image.size
        self.rawpixels = self.image.getdata()
        self.pixels = [[None for y in range(self.height)] for x in range(self.width)]
        i = 0
        for y in range(self.height):
            for x in range(self.width):
                self.pixels[x][y] = Pixel(x,y,self.rawpixels[i])
                #print self.rawpixels[i]
                i = i + 1
        self.current_pixel = self.pixels[0][0]
        
    def find_color_blocks(self):
        next_label = 0
        #Pass 1
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.pixels[x][y]
                if not self.is_background(pixel.color):
                    neighbours = self.neighbours(pixel)
                    
                    if neighbours == []:
                        pixel.parent = self.pixels[x][y]
                        pixel.set_label = next_label
                        next_label = next_label + 1
                    else:
                        for n in neighbours:
                            union(n,pixel)
        
        #Pass 2
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.pixels[x][y]
                if not self.is_background(pixel.color):
                    root = find(pixel)
                    pixel.set_size = root.set_size
                    pixel.set_label = root.set_label
                    #Build color block object
                    if not self.color_blocks.has_key(pixel.set_label):
                        self.color_blocks[pixel.set_label] = ColorBlock(pixel.set_size)
                    self.color_blocks[pixel.set_label].update_boundaries(pixel)
    
        #Debug
        #for i,color_block in self.color_blocks.items():
        #    bounds = color_block.boundary_pixels
        #    print "Color Block %s: Size=%s, maxRL=(%s,%s), maxRR=(%s,%s), maxDL=(%s,%s), maxDR=(%s,%s), maxLL=(%s,%s), maxLR=(%s,%s), maxUL=(%s,%s), maxUR=(%s,%s)" \
        #        % (i, color_block.size, 
        #           bounds[0][0].x,bounds[0][0].y, bounds[0][1].x, bounds[0][1].y,
        #           bounds[1][0].x,bounds[1][0].y, bounds[1][1].x, bounds[1][1].y,
        #           bounds[2][0].x,bounds[2][0].y, bounds[2][1].x, bounds[2][1].y,
        #           bounds[3][0].x,bounds[3][0].y, bounds[3][1].x, bounds[3][1].y)
                    
    def is_background(self,color):
        if color == colors.white or color == colors.black:
            return True
        else:
            return False
        
    def neighbours(self,pixel):
        neighbours = []
        index = 0;
        x = pixel.x
        y = pixel.y
            
        if y !=0 and self.pixels[x][y-1].color == pixel.color:
            #Add above pixel
            index = index + 1
            neighbours.append(self.pixels[x][y-1])
        
        if x != 0 and self.pixels[x-1][y].color == pixel.color:
            #Add left pixel
            neighbours.append(self.pixels[x-1][y])
            index = index + 1
            
        return neighbours      
    
    def start_execution(self):
        #We'll just do ten steps for now
        for i in range(10000):
            self.do_next_step()
            
    def do_next_step(self):      
        if self.step == 0:
            #Just moved into color block, so let's move to the edge of color block
            #print "Moving from (%s,%s) to (%s,%s)" % (self.current_pixel.x,self.current_pixel.y,self.color_blocks[self.current_pixel.set_label] \
            #    .boundary_pixels[self.dp][self.cc].x,self.color_blocks[self.current_pixel.set_label] \
            #    .boundary_pixels[self.dp][self.cc].y)
            self.current_pixel = \
                self.color_blocks[self.current_pixel.set_label] \
                .boundary_pixels[self.dp][self.cc]
            self.step = 1
        elif self.step == 1:
            next_pixel = self.next_pixel()
            if next_pixel and next_pixel.color == colors.white:
                if self.current_pixel.color != colors.white:
                    self.switch_cc = True
                    self.times_stopped = 0
                #print "sliding trhu white"
                self.slide_thru_white()
                self.step = 1
            else:
                #print "DP=%s, CC=%s" % (self.dp,self.cc)
                if next_pixel:
                    self.switch_cc = True
                    self.times_stopped = 0
                
                    #Do operation as long as we're not moving out of white
                    if self.current_pixel.color != colors.white:
                        ##print "Moving from (%s,%s) to (%s,%s)" % (self.current_pixel.x, self.current_pixel.y, next_pixel.x,next_pixel.y)
                        hue_light_diff = colors.hue_light_diff(self.current_pixel.color, next_pixel.color)
                        op_name, op = self.operations[hue_light_diff]
                        #print "Before: ",self.stack
                        #print "OP: (%s,%s) - %s" % (hue_light_diff[0],hue_light_diff[1],op_name)
                        op()
                        #print "After: ",self.stack
                    
                    self.current_pixel = next_pixel
                else:
                    #print "At (%s,%s) - hit a stop" % (self.current_pixel.x, self.current_pixel.y)
                    self.handle_stop()
                self.step = 0
        else:
            error_handler.handle_error("The step wasn't 0 or 1. That should never happen. This must be a bug in my code. Sorry")
    
    def next_pixel(self):
        cp = self.current_pixel
        if self.dp == 0 \
            and cp.x+1 < self.width \
            and self.pixels[cp.x+1][cp.y].color != colors.black:
                return self.pixels[cp.x+1][cp.y]
        elif self.dp == 1 \
            and cp.y+1 < self.height \
            and self.pixels[cp.x][cp.y+1].color != colors.black:
                return self.pixels[cp.x][cp.y+1]
        elif self.dp == 2 \
            and cp.x-1 >= 0 \
            and self.pixels[cp.x-1][cp.y].color != colors.black:
                return self.pixels[cp.x-1][cp.y]
        elif self.dp == 3 \
            and cp.y-1 >= 0 \
            and self.pixels[cp.x][cp.y-1].color != colors.black:
                return self.pixels[cp.x][cp.y-1]
        else:
            return None
            
    def slide_thru_white(self):
        next_pixel = self.next_pixel()
        if not next_pixel:
            self.times_stopped = self.times_stopped + 1
            if self.times_stopped >= 8:
                self.stop_execution
            self.toggle_cc()
            self.rotate_dp()
        while next_pixel and next_pixel.color == colors.white:
            self.current_pixel = next_pixel
            next_pixel = self.next_pixel()    
    
    def handle_stop(self):
        self.times_stopped = self.times_stopped + 1
        if (self.times_stopped >= 8):
            self.stop_execution()
        else:
            if self.switch_cc:
                self.toggle_cc()
                self.switch_cc = False
            else:
                self.rotate_dp(1)
                self.switch_cc = True
    
    def stop_execution(self):
        print "Execution finished"
        sys.exit(1)
        
    def toggle_cc(self):
        #print "Toggling cc"
        div,mod = divmod(1-self.cc,1)
        self.cc = div
    
    def rotate_dp(self,times=1):
        #print "Rotating dp"
        div,mod = divmod(self.dp+times,4)
        self.dp = mod
        
    #Below are the actual operation methods for the piet language.
    #The stuff above is 
    def op_add(self):
        if len(self.stack) >= 2:
            item1 = self.stack.pop()
            item2 = self.stack.pop()
            self.stack.append(item1+item2)
    
    def op_divide(self):
        if len(self.stack) >= 2:
            top_item = self.stack.pop()
            second_item = self.stack.pop()
            self.stack.append(second_item/top_item)
    
    def op_greater(self):
        if len(self.stack) >= 2:
            top_item = self.stack.pop()
            second_item = self.stack.pop()
            self.stack.append(int(second_item>top_item))
            
    
    def op_duplicate(self):
        if len(self.stack) >=1:
            item = self.stack[-1]
            self.stack.append(item)
    
    def op_in_char(self):
        chr = get_chr()
        self.stack.append(ord(chr))
    
    def op_push(self):
        self.stack.append(self.current_pixel.set_size)
    
    def op_subtract(self):
        if len(self.stack) >= 2:
            top_item = self.stack.pop()
            second_item = self.stack.pop()
            self.stack.append(second_item-top_item)
    
    def op_mod(self):
        if len(self.stack) >= 2:
            top_item = self.stack.pop()
            second_item = self.stack.pop()
            self.stack.append(second_item % top_item)
    
    def op_pointer(self):
        if len(self.stack) >= 1:
            item = self.stack.pop()
            self.rotate_dp(item)
    
    def op_roll(self):
        if len(self.stack) >= 2:
            num_rolls = self.stack.pop()
            depth = self.stack.pop()    
            if depth >0:
                for i in range(abs(num_rolls)):
                    self.roll(depth,num_rolls<0)    
    
    def roll(self,depth,reverse):
        if depth > len(self.stack):
            depth = len(self.stack)

        if reverse:
            bottom_item = self.stack[0]
            index = depth
            for i in range(index):
                self.stack[i] = self.stack[i+1]
            self.stack[index] = bottom_item
        else:
            top_item = self.stack[-1]
            index = len(self.stack)-depth
            for i in range(len(self.stack)-1,index,-1):
                self.stack[i] = self.stack[i-1]    
            self.stack[index] = top_item
            
    
    def op_out_number(self):
        if len(self.stack) >=1:
            item = self.stack.pop()
            print item
    
    def op_pop(self):
        self.stack.pop()
    
    def op_multiply(self):
        if len(self.stack) >= 2:
            item1 = self.stack.pop()
            item2 = self.stack.pop()
            self.stack.append(item1*item2)
    
    def op_not(self):
        if len(self.stack) >= 1:
            item = self.stack.pop()
            self.stack.append(int(not item))
    
    def op_switch(self):
        if len(self.stack) >=1:
            item = self.stack.pop()
            for i in range(item):
                self.toggle_cc()
    
    def op_in_number(self):
        char = get_chr()
        try:
            self.stack.append(int(char))
        except ValueError:
            pass      
    
    def op_out_char(self):
        if len(self.stack) >=1:
            item = self.stack.pop()
            print chr(item)
    
class ColorBlock:
    def __init__(self,size):
        self.size = size
        #boundary_pixels = [[DPR_L,DPR_R],[DPD_L,DPD,R] ... etc.
        self.boundary_pixels = [[None,None] for i in range(4)]
        
    def update_boundaries(self,pixel):
        #If a new maximum (right, left)
        if self.boundary_pixels[0][0] == None or pixel.x > self.boundary_pixels[0][0].x:
            self.boundary_pixels[0][0] = pixel
            
        #If a new maximum (right, right)
        if self.boundary_pixels[0][1] == None or pixel.x >= self.boundary_pixels[0][1].x:
            self.boundary_pixels[0][1] = pixel
            
        #If a new maximum (down, right)
        if self.boundary_pixels[1][1] == None or pixel.y > self.boundary_pixels[1][1].y:
            self.boundary_pixels[1][1]= pixel
        
        #If a new maximum (down, left)
        if self.boundary_pixels[1][0] == None or pixel.y >= self.boundary_pixels[1][0].y:
            self.boundary_pixels[1][0] = pixel
            
        #If a new maximum (left, right)
        if self.boundary_pixels[2][1] == None or pixel.x < self.boundary_pixels[2][1].x:
            self.boundary_pixels[2][1] = pixel
        
        #If a new maximum (left, left)
        if self.boundary_pixels[2][0] == None or pixel.x <= self.boundary_pixels[2][0].x:
            self.boundary_pixels[2][0] = pixel
            
        #If a new maximum (up,left)
        if self.boundary_pixels[3][0] == None:
            self.boundary_pixels[3][0] = pixel
            
        #If a new maximum (up,right)
        if self.boundary_pixels[3][1] == None or pixel.y == self.boundary_pixels[3][1].y:
            self.boundary_pixels[3][1] = pixel
                
            
        
class Pixel:
    def __init__(self,x,y,color):
        self.x = x
        self.y = y
        try:
            colors.color_mappings[colors.rgb_to_hex(color)]
            self.color = color
        except KeyError:
            self.color = colors.white
        self.parent = self   
        self.set_size = 1
        self.set_label = -1

    def set_color_block(color_block):
        self.color_block = color_block
    
    def get_color_block():
        return self.color_block
    
class ErrorHandler:
    def __init__(self, isGUI=False):
        self.isGUI = isGUI
        
    def handle_error(self,message):
        if not self.isGUI:
            raise SystemExit("Error: "+message)
        else:
            pass
    
if __name__ == "__main__":
    error_handler = ErrorHandler(False)
    interpreter = Interpreter()
    if len(sys.argv)>1:
        interpreter.run_program(sys.argv[1])
    else:
        print_usage()