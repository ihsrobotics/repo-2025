from bot_config import *
from ctypes import CDLL
kipr = "/usr/local/lib/libkipr.so"
k = CDLL(kipr)

def drive(left_velocity, right_velocity, duration):
    k.mav(LEFT_WHEEL, left_velocity)
    k.mav(RIGHT_WHEEL, int(right_velocity * 1.1))
    k.msleep(duration)

def turn_on_spot(direction, duration):
    duration*=1.1
    if direction == "RIGHT":
        drive(800, -800, int(duration))
    elif direction == "LEFT":
        drive(-800, 800, int(duration))
    else:
        print("TEXT ERROR : Direction")

def interpolate(servo,starting_angle, finish_angle, delay,step):
    for i in range(starting_angle, finish_angle,step): # a loop so the angle slowly moves up to its final position
        k.msleep(delay)
        k.set_servo_position(servo, i)



def on_black(tophat):
    if (k.analog(tophat) > 4000): 
        return True

def line_follow(slow_speed,fast_speed,delay,timer,polarity = FORWARD,sensor = LEFT_T_SENSOR):
    slow_speed *= polarity
    fast_speed *= polarity
    end_time = k.seconds() + timer # duration for how long line_follow should last
    while k.seconds() < end_time:
        if on_black(sensor):
            drive(slow_speed,fast_speed,delay)
        else:
            drive(fast_speed,slow_speed,delay)
   

def edge_detected():
    if k.analog(ET_SENSOR) > 4000: # when ET sensor detects a pipe's edge
        return True
    else:
        return False

def stop_at_edge():
    while not edge_detected(): 
        line_follow(1000,1200,10,1000) # drives while no edges have been detected
    
def pickup_ice():
    turn_on_spot("LEFT",900)
    square_up(BACK_SENSOR, BOOM_SENSOR) 
    interpolate(MAIN_BEAM,1500,500,10,2)# lowers claw
    interpolate(CLAW,2047,900,10) # grabs ice
    turn_on_spot("LEFT",900)
    

def pickup_bottle():
    turn_on_spot("LEFT",900) # turn 90 left to face bottles
    square_up()

    # interpolate(MAIN_BEAM,500,1500,20,2) 
    # interpolate(MAIN_BEAM,1500,500,20,-2)

    interpolate(MAIN_BEAM, 500, 1250,10, 2)
    interpolate(MAIN_BEAM,1250, 600, 10, -2)
    

    turn_until_detected("LEFT",900) # adjust back to forward
    square_up()
    # might use square up
    

#def straighten(starting_angle,finish_angle,duration):
    # interpolate(startin_angle,finish_angle,10)
    # turn_on_spot("RIGHT",duration)

def unload_bottles():
    interpolate(MAIN_BEAM,500,1500,20,2)
    interpolate(MAIN_BEAM,1500,500,20,-2)

def turn_until_black(sensor,direction):
    pass


   

def set_boom_stick(angle = k.get_servo_position(BOOM_STICK)):
    k.set_servo_position(BOOM_STICK,angle)

   

def grab_cup():
    
    drive(800,0,900)
    line_follow(1000,1200,10,1000)
    turn_until_detected("LEFT",)
    k.set_servo_position(BOOM_STICK) # use boomstick to push cup out 
    turn_until_detected("RIGHT") # bot faces cup
    k.set_servo_position(MAIN_BEAM,500) # lowers claw down
    k.set_servo_position(CLAW,2047) # claw drops ice into cup
    turn_until_detected("LEFT")

    
    
    

def reset_all():
    k.ao()
    k.cmpc(LEFT_WHEEL)
    k.cmpc(RIGHT_WHEEL)
    k.set_servo_position(ARM,800)

def square_up(sensor_one = LEFT_T_SENSOR,sensor_two = RIGHT_T_SENSOR):
    print("run")
    while not (on_black(sensor_one) and on_black(sensor_two)):
        print("running")

        if on_black():
            drive(0, -290, 100) 
        elif not on_black():
            drive(140, 0, 100)
        
        if on_black():
            drive(-290, 0, 100)
        elif not on_blackght():
            drive(0, 140, 100)

def turn_until_et_detect(direction):
    if direction == "LEFT":
        
        inverse_directon = "RIGHT"
    elif direction == "RIGHT":
        
        inverse_directon = "LEFT"
    else:
        print("Invalid direction")

    while not (k.analog(ET_SENSOR) < number_1 and k.analog(ET_SENSOR) > number_2):
        turn_on_spot(direction,500)
    
def turn_until_black(direction,angle):
    while not line_detect(angle):
        turn_on_spot(direction,500)


