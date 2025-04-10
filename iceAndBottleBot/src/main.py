import sys
sys.path.append("/home/pi/Documents/IME_files/SmallBotHook2025/include")
from bot_function import *

from ctypes import CDLL
kipr = "/usr/local/lib/libkipr.so"
k = CDLL(kipr)

def main():

    reset_all()
    k.enable_servos()
    turn_on_spot("RIGHT",920)
    
    
    
    
    

    # Note: might need to use square_up() after on_black() loops
     # For claw: closed at 2047 and opens at 920
    
        
    
    
    while not on_black(BOOM_SENSOR): #Drives until it reaches a line, then stops at 
        drive(800,1000,5000)
    turn_on_spot("RIGHT",920) # turn 90 right
   
    stop_at_edge()# moves on black until edge is detected
    pickup_ice()
    while not on_black(BOOM_SENSOR): #Drives until it reaches a line, then stops 
        line_follow(800,1000,10,2000,BACKWARD)
    pickup_bottle()
    while not edge_detected(): 
        line_follow(800,1000,10,2000)
    while not on_black(BOOM_SENSOR):
        line_follow(800,1000,10,2000,BACKWARD)
    pickup_ice()#pickup ice number 2
    
    while not on_black(RIGHT_T_SENSOR): #The first line will be passed
        line_follow(800,1000,10,2000)
    line_follow(800,1000,10,500) # Skip the  center line
    while not on_black(RIGHT_T_SENSOR): #Drives until next line is detected
        line_follow(800,1000,10,2000)
    grab_cup()#grab cup and put ice in cup
    while not on_black(BOOM_SENSOR): # drives until line is detected
       drive(-800,-800,1000)
    turn_until_detected("RIGHT",920) # turn 90 right, change to turn until black
 
    stop_at_edge()
    
    turn_until_detected("LEFT",920)#turn 90
    while not on_black(BOOM_SENSOR): #Boomstick moves at an angle of
      drive(-80, -80, 10)
    unload_bottles()#drive and put bottles in
    print("I am finished.")
main()
