import sys
sys.path.append("/home/kipr/Documents/IME_files/pomBot/include")
from bot_functions import *

from ctypes import CDLL
kipr = "/usr/lib/libkipr.so"
k = CDLL(kipr)

def sort_pom(trays, pom, last_tray, farthest_tray, was_last_forward):
    #stop conveyor
    run_conveyor_and_wheel(0)
    
    pom_color = ["RED", "YELLOW", "ORANGE"]


    print("POM:",pom)
    print("waiting for 5 seconds so you can read")
    k.msleep(5000)


    #4 Check what trays need pom color
    trays_without_color = []

    for tray in trays:
        #If pom isnt in tray and unobstructed 
        if (pom not in trays[tray]) and (tray <= farthest_tray):
            trays_without_color.append(tray)
    #If no valid trays
    if len(trays_without_color) == 0:
        raise Exception("No Valid Trays")
    trays_without_color.reverse()
    print("TRAYS WITHOUT COLOR:",trays_without_color)

    #5 Check which of the trays without color is closest to last tray
    shortest_distance = abs(last_tray-trays_without_color[0])

    closest_tray = trays_without_color[0]

    for tray in trays_without_color:
        distance = abs(last_tray-tray)

        if distance <= shortest_distance:
            shortest_distance = distance
            closest_tray = tray

    #6 Determine Whether were going forwards or backwards based on positive or negative distance
    forwards = True
    non_absolute_distance = last_tray-closest_tray
    non_absolute_distance *= -1
    if non_absolute_distance > 0:
        forwards = True
    if non_absolute_distance < 0:
        forwards = False

    #7 Go to closest tray
    count = 0
    covered = False
    #if et is covered and we last went backwards or we are going backwards, add 1 to the distance
    if (k.analog(ET_SENSOR) > 2800 and not forwards) or (k.analog(ET_SENSOR) > 2800 and not was_last_forward):
        print("ADDED TO DISTANCE")
        shortest_distance += 1
    
    print(f"NON ABSOLUTE DISTANCE: {non_absolute_distance}")
    print(f"WAS LAST FORWARD: {was_last_forward}")
    print(f"COVERED: {k.analog(ET_SENSOR) > 2800}")
    print(f"GOING FORWARD: {forwards}")
    print("waiting for 10 seconds so you can read")
    k.msleep(10000)
        
    while count < shortest_distance:
        print("GOING TO TRAY",closest_tray)
        print("COVERED:",covered, "\nCOUNT:",count,"/",shortest_distance)
        #line follow, plug in forwards variable as parameter for direction
        if forwards:
            line_follow(500, 1000, FORWARD)
        if not forwards:
            line_follow(500, 1000, BACKWARD)

        if k.analog(ET_SENSOR) < 2000 and covered == True:
            count += 1
            covered = False
            continue
        if k.analog(ET_SENSOR) > 2800:
            covered = True




    #8. Update last tray and add the pom to the tray's inventory
    last_tray = closest_tray
    was_last_forward = forwards

    # Run the converyor until background
    print("RUN CONVERYOR UNTIL BACKGROUND")
    backgrounds_seen = 0

    while backgrounds_seen < 15:
        #RUN CONVEYOR
        run_conveyor_and_wheel(500)
        print("BACKGROUND:",backgrounds_seen)
        color = read_color()
        if color not in pom_color:
            backgrounds_seen += 1

    

    
    trays[closest_tray].append(pom)

    print("TRAYS:")
    for tray in trays:
        print(f"{tray}: {trays[tray]}")
    print("waiting for 5 seconds so you can read")
    k.msleep(5000)
    return (last_tray, was_last_forward)

def main():
    #1. Turn bot so that it is facing close to the pom line direction
    drive(500, 0)

    epoch_1 = time()
    epoch_2 = time()
    secs_not_sorting = 0
    stopwatch = 0
    times_sweeped = 0
    seconds_sweeped_on = []
    #2. Start line following and sweeping the middle poms into our line. Check for poms in front of the camera.
    last_tray = 4
    farthest_tray = 4

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

    while secs_not_sorting < 10:
        #line follow and run conveyor
        line_follow(500, 600)
        run_conveyor_and_wheel(500)

        print(last_tray, covered)

        #keep track of farthest tray
        if last_tray > farthest_tray:
            farthest_tray = last_tray

        
        #Update seconds not sorting and stopwatch
        secs_not_sorting = time()-epoch_1
        stopwatch = time()-epoch_2

        #Sweep every 5 seconds, three times max. if we have already sweeped on this second dont do it again
        if (stopwatch//1) % 5 == 0 and times_sweeped <=3 and (stopwatch//1) not in seconds_sweeped_on:
            sweep_arm()
            print(f"SWEEPED: {times_sweeped}")
            times_sweeped += 1
            seconds_sweeped_on.append(stopwatch//1)
        

        #Get pom color
        pom = read_color()
        print(f"POM: {pom}\nLAST TRAY: {last_tray}\nSECS NOT SORTING: {secs_not_sorting}")

        #If its a pom color, sort it and reset secs not sorting
        if pom != "BACKGROUND":
            last_tray, was_last_forward = sort_pom(trays, pom, last_tray, farthest_tray, was_last_forward)
            epoch_1 = time()

        #Tray counting logic
        if k.analog(ET_SENSOR) < 2000 and covered == True:
            last_tray += 1
            covered = False
            continue

        if k.analog(ET_SENSOR) > 2800:
            # print("I AM RUNNING")
            covered = True
    
    #3. Probably does nothing else. sorts poms the whole game
    k.ao()




    
if __name__ == "__main__":
    main()
