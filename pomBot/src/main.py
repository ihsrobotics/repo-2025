import sys
import threading

sys.path.append("/home/kipr/Documents/IME_files/pomBot/include")
from bot_functions import *

from ctypes import CDLL
kipr = "/usr/lib/libkipr.so"
k = CDLL(kipr)







def sort_pom(trays, pom, last_tray, farthest_tray, was_last_forward):
    #stop conveyor and driving
    stop_conveyor_and_wheel()
    brake()
    
    pom_color = ["RED", "YELLOW", "ORANGE"]
    pom = None
    #read again with samples for security
    times_checked = 0
    while pom not in pom_color:
        pom_list = []
        for i in range(10):
            pom_list.append(read_color())
        pom = most_common(pom_list)
        times_checked += 1

    print("POM:",pom)

    if times_checked == 10:
        return (last_tray, was_last_forward)

    # print("waiting for 5 seconds so you can read")
    # k.msleep(5000)


    #4 Check what trays need pom color
    trays_without_color = []

    for tray in trays:
        #If pom isnt in tray and unobstructed (farthest tray +2 because the sucker is about 2 trays ahead)
        if (pom not in trays[tray]) and (tray <= farthest_tray+2):
            trays_without_color.append(tray)
    #If no valid trays
    if len(trays_without_color) == 0:
        raise Exception("No Valid Trays")
    trays_without_color.reverse()
    print("TRAYS WITHOUT COLOR:",trays_without_color)

    # #5 Check which of the trays without color is closest to last tray
    # shortest_distance = abs(last_tray-trays_without_color[0])

    # closest_tray = trays_without_color[0]

    # for tray in trays_without_color:
    #     distance = abs(last_tray-tray)

    #     if distance <= shortest_distance:
    #         shortest_distance = distance
    #         closest_tray = tray

    #ALTERNATE STEP 5 WHERE WE PRIORITIZE FULLER TRAYS
    #5 Check which of the trays without color is the fullest
    shortest_distance = abs(last_tray-trays_without_color[0])
    #use this one if all trays are equal in fullness
    shortest_distance_2 = abs(last_tray-trays_without_color[0])
    most_fullness = len(trays[trays_without_color[0]])
    closest_tray = trays_without_color[0]
    #use this one if all trays are equal in fullness
    closest_tray_2 = trays_without_color[0]

    fullness_vals = []

    for tray in trays_without_color:
        distance = abs(last_tray-tray)
        fullness = len(trays[tray])
        fullness_vals.append(fullness)

        if fullness >= most_fullness:
            shortest_distance = distance
            most_fullness = fullness
            closest_tray = tray
        
        if distance <= shortest_distance_2:
            shortest_distance_2 = distance
            closest_tray_2 = tray

    print("FULLEST TRAY:",closest_tray,"CLOSEST TRAY:",closest_tray_2, "SHORTEST DISTANCE", shortest_distance_2)

    #Check if any of the trays are not equal
    all_same = True
    for val in fullness_vals:
        if val != fullness_vals[0]:
            all_same = False
    
    if all_same:
        closest_tray = closest_tray_2
        shortest_distance = shortest_distance_2
        print("USING CLOSEST TRAY:",closest_tray)
        


    #6 Determine Whether were going forwards or backwards based on positive or negative distance
    forwards = False
    non_absolute_distance = last_tray-closest_tray
    non_absolute_distance *= -1
    if non_absolute_distance > 0:
        forwards = True
    if non_absolute_distance < 0:
        forwards = False


    #go fully onto current tray to make sure we dont count weird on a gap
    adjust_ran = False
    while not over_tray() and last_tray != 6 and last_tray != closest_tray:
        line_follow(350, 450, FORWARD)
        adjust_ran = True
    #a bit more for security
    if adjust_ran:
        end_time = k.seconds()+100
        while k.seconds() < end_time and last_tray != 6:
            line_follow(350, 450, FORWARD)


    #7 Go to closest tray
    count = 0
    covered = False
    #if et is covered and we last went backwards or we are going backwards, add 1 to the distance
    #or (over_tray() and not was_last_forward)
    if (over_tray() and not forwards):
        print("ADDED TO DISTANCE")
        shortest_distance += 1
    
    # print(f"NON ABSOLUTE DISTANCE: {non_absolute_distance}")
    # print(f"WAS LAST FORWARD: {was_last_forward}")
    # print(f"COVERED: {over_tray()}")
    # print(f"GOING FORWARD: {forwards}")
    # print("waiting for 10 seconds so you can read")shortest_distance == 0 and 
    # k.msleep(10000)
    print("GOING TO TRAY",closest_tray)
    # print("COUNT:",count,"/",shortest_distance)
    print("FORWARDS:",forwards)


    #if were on the 6th one back up so we are actually on it
    if last_tray == 6 and closest_tray == 6:
        while not over_tray():
            line_follow(850, 1000, BACKWARD)


    DEBUG_VAL = ""
    tray_sweeped_on = ""
    while count < shortest_distance:
        # if count != DEBUG_VAL:
        print("COVERED:",covered, "\nCOUNT:",count,"/",shortest_distance,"\nET:",k.analog(TRAY_ET), "GOING TO:",closest_tray)

        #Sweeping logic
        if tray_sweeped_on != count:
            k.set_servo_position(SWEEP_ARM, ARM_MAX)
            end_time = k.seconds() + 500
            tray_sweeped_on = count

        if k.seconds() > end_time:
            k.set_servo_position(SWEEP_ARM, ARM_MIN)

            # DEBUG_VAL = count
        #line follow, plug in forwards variable as parameter for direction
        #950 1150 worked
        #1000 1150 worked
        if forwards:
            line_follow(850, 1000, FORWARD)
        if not forwards:
            line_follow(850, 1000, BACKWARD)

        if not over_tray() and covered == True:
            count += 1
            covered = False
            continue
        if over_tray():
            covered = True
    brake()


    # #make sure its aligned with tray
    # while not over_tray():
    #     line_follow(350, 450, BACKWARD)
    # brake()

    # while not over_tray:
    #     line_follow(350, 450, BACKWARD)
    # brake()



    #8. Update last tray and add the pom to the tray's inventory
    last_tray = closest_tray
    was_last_forward = forwards

    #wait for pom to settle and eject pom into tray
    k.msleep(1000)
    eject_pom()
    
    #go over tray to prevent double counting of trays
    while not over_tray() and last_tray != 6:
        line_follow(350, 450, FORWARD)
    #a bit more for security
    end_time = k.seconds()+100
    while k.seconds() < end_time and last_tray != 6:
        line_follow(350, 450, FORWARD)
    
    trays[closest_tray].append(pom)
    print(f"APPENDED {pom} TO {trays}")

    print("TRAYS:")
    for tray in trays:
        print(f"{tray}: {trays[tray]}")
    # print("waiting for 5 seconds so you can read")
    # k.msleep(5000)
    

    #Update camera to reset it 
    k.camera_update()
    return (last_tray, was_last_forward)

def main():        


    k.enable_servos()
    k.set_servo_position(EJECTOR, EJECTION_RESTING)
    k.set_servo_position(SWEEP_ARM, ARM_MIN)

    
    #wait for cam to get ready
    setup_camera()
    read_color()





    #Back up until front sensor is on other side of the line behind us
    while not on_tape():
        drive(-1500, -1500)
    while on_tape():
        drive(-1500, -1500)
    brake()

    #Wait for other bot to swing boom forward so we can bring out our sweeper
    k.msleep(1000)

    #Drive until the back sensor is on black
    while not on_tape(BACK_TOPHAT):
        drive(1500, 1500)
    brake()

    #Turn to get the front tophat close to the pom line
    while not on_tape():
        drive(-700, 500)
    while on_tape():
        drive(-700, 500)
    brake()

    #line follow for a moment to get closer
    end_time = k.seconds()+3000
    while k.seconds() < end_time:
        line_follow(500, 1300, FORWARD, "LEFT")

    # return



    epoch_1 = time()
    epoch_2 = time()
    secs_not_sorting = 0
    stopwatch = 0
    times_sweeped = 0
    seconds_sweeped_on = []
    #2. Start line following and sweeping the middle poms into our line. Check for poms in front of the camera.
    last_tray = -1
    farthest_tray = -1

    was_last_forward = True
    covered = False

    trays = {
        1 : [],
        2 : [],
        3 : [],
        4 : [],
        5 : [],
        6 : []
    }

    end_time = 0
    tray_sweeped_on = "PLACEHOLDER"
    black_timer = 0
    DEBUG_VAL = "PLACEHOLDER"
    extra_linefollow_ran = False

    #secs_not_sorting < 120
    while True:
        run_conveyor_and_wheel()
        
        #Sweeping logic
        if tray_sweeped_on != last_tray:
            k.set_servo_position(SWEEP_ARM, ARM_MAX)
            end_time = k.seconds() + 500
            tray_sweeped_on = last_tray

        if k.seconds() > end_time:
            k.set_servo_position(SWEEP_ARM, ARM_MIN)
                
            

        if last_tray < 6:
            #line follow and run conveyor
            line_follow(850, 1000, FORWARD, "LEFT")
            extra_linefollow_ran = False

        else:
            if not extra_linefollow_ran:
                extra_linefollow_ran = True
                end_time = k.seconds() + 1000
                while k.seconds() < end_time:
                    line_follow(850, 1000, FORWARD, "LEFT")

            brake()



        if last_tray != DEBUG_VAL:
            print(last_tray, covered)
            DEBUG_VAL = last_tray  


        # print(stopwatch,"/",120)
        
        #Update seconds not sorting
        secs_not_sorting = time()-epoch_1
        
        #Try to unclog conveyor
        if secs_not_sorting > 25:
            end_time = k.seconds()+500
            while k.seconds() < end_time:
                k.mav(CONVEYOR, -1500)
            brake()
            run_conveyor_and_wheel()

        

        #Get pom color
        pom = read_color()
        # pom = "BACKGROUND"

        # print(f"POM: {pom}\nLAST TRAY: {last_tray}\nSECS NOT SORTING: {secs_not_sorting}")

        #Tray counting logic
        if not over_tray() and covered == True and last_tray != 6:
            last_tray += 1
            covered = False
            continue

        if over_tray():
            # print("I AM RUNNING")
            covered = True


        #If its a pom color, sort it and reset secs not sorting
        if pom != "BACKGROUND":
            #hardcode go back to get back to trays
            # if extra_linefollow_ran:
            #     end_time = k.seconds()+1250
            #     while k.seconds() < end_time:
            #         line_follow(850, 1000, BACKWARD, "LEFT")

            last_tray, was_last_forward = sort_pom(trays, pom, last_tray, farthest_tray, was_last_forward)
            extra_linefollow_ran = False
            # k.msleep(3000)
            epoch_1 = time()

        #keep track of farthest tray
        if last_tray > farthest_tray:
            farthest_tray = last_tray


        
        # #if stopwatch reaches 2 minutes
        if stopwatch > 120:
            k.ao()
            return


        
    



def test_func():
    last_tray = -1
    # # # white_count = 0
    covered = False


    while last_tray < 6:
        # is_over_tray = over_tray()
        # run_conveyor_and_wheel()
        line_follow(850, 1000, FORWARD, "LEFT")
        print(over_tray(), k.analog(TRAY_ET), last_tray)

        #Tray counting logic
        if not over_tray() and covered == True:
            last_tray += 1
            covered = False
            continue

        if over_tray():
            # print("I AM RUNNING")
            covered = True
    brake()

def test():
    while True:
        # print("I AM ALSO RUNNING")
        run_conveyor_and_wheel()

main_thread = threading.Thread(target=main)
main_thread.daemon = True
def shutdown_in(s):
    end_time = time()+s
    while time() < end_time:
        # print(end_time-time())
        if k.digital(0):
            break
        pass
    print("LOOP ENDED")
    main_thread.raise_exception()

    k.ao()
    quit()

if __name__ == "__main__":
    
    main_thread.start()
    shutdown_in(120)
    # main()
    
    # test()
    # k.shut_down_in(999999999999999999)



    # test_func()
    # while True:
    #     print(read_color())



    # k.msleep(500)
    # pom_list = []
    # for i in range(10):
    #     pom_list.append(read_color())
    # pom = most_common(pom_list)
    # print(pom)
    # eject_pom()

    # while True:
        # run_conveyor_and_wheel()
        # print(read_color())



    # print(read_color())

 
