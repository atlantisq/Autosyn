# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 09:54:16 2019

"""

#READ  SYRINGE FILE FOR DEPTHS AND CLEARANCES
import xlrd
import shapely.geometry as sg

syringe_book =  xlrd.open_workbook('syringe.xlsx')
sheet=syringe_book.sheet_by_index(0)
conversion_factor=sheet.cell_value(5,1)
syr_volume=sheet.cell_value(1,1)
syr_diameter = sheet.cell_value(8,1)
syr_length = sheet.cell_value(9,1)


coordinate_book = xlrd.open_workbook('plate.xlsx')


#READ VIAL TYPES
sheet=coordinate_book.sheet_by_name('VIAL_TYPES')
vials_dict={}

for i in range(1,sheet.nrows):
    
    empty_cell_flag = 0
    
    for j in range(5):
        if sheet.cell_value(i,1) == '':
            empty_cell_flag = 1;
            break
    if empty_cell_flag == 1:
        continue
    
    Vial_Type = sheet.cell_value(i,0)
    Clearance_Height = sheet.cell_value(i,1)
    Clearance_Diameter = sheet.cell_value(i,2)
    Dispense_Height = sheet.cell_value(i,3)
    Test_Syringe_Length = sheet.cell_value(i,4)
    
    True_Clearance_Height = Clearance_Height - (syr_length - Test_Syringe_Length)
    True_Dispense_Height = Dispense_Height - (syr_length - Test_Syringe_Length)

    vials_dict[Vial_Type]=(True_Clearance_Height,Clearance_Diameter,True_Dispense_Height)


#READ TEST LOCATIONS
sheet=coordinate_book.sheet_by_name('EXP_LOC')
test_location=[]
for i in range(1,sheet.nrows):
    vial_x = sheet.cell_value(i,1)
    vial_y = sheet.cell_value(i,2) + (syr_diameter - sheet.cell_value(i,4)) * 1.4142    #A larger syringe will sit more outwards on the carriage
    vial_type = sheet.cell_value(i,3)
    test_location.append((vial_x, vial_y, vial_type))
    
    
#READ WASH PROTOCOL LOCATIONS AND CLEARANCES
sheet=coordinate_book.sheet_by_name('WASH_LOC')
wash_dict = {}
for i in range(1,sheet.nrows):
    
    if sheet.cell_value(i,1) == '' or sheet.cell_value(i,2) == '':
        continue
    
    wash_dict[sheet.cell_value(i,0)]=(sheet.cell_value(i,1),sheet.cell_value(i,2),sheet.cell_value(i,3))
    
wash_location = wash_dict['wash']
waste_location = wash_dict['waste']


#READ STOCK SOLN LOCATIONS
sheet=coordinate_book.sheet_by_name('STOCK_LOC')
stock_dict={}

for i in range(1,sheet.nrows):
    
    if sheet.cell_value(i,1) == '' or sheet.cell_value(i,2) == '':
        continue
    
    stock_dict[sheet.cell_value(i,0)]=(sheet.cell_value(i,1),sheet.cell_value(i,2),sheet.cell_value(i,3))
    

# Creature comfort function to call dispense depth easily
def depth(location):
    return vials_dict[location[2]][2]



#LEGACY FUNCTIONS USE THESE PARAMETERS; THIS IS JUST TO KEEP THEM HAPPY.
#THE CLEARANCE HEIGHT SHOULD NOT BE NECESSARY AS SAFEMOVE SHOULD TAKE CARE OF ALL CLEARANCE MOVES.
exp_vial_depth = vials_dict[test_location[0][2]][2]
exp_vial_clearance = vials_dict[test_location[0][2]][0]
stock_depth = vials_dict['20mL vial'][2]
wash_and_waste_depth = vials_dict[wash_dict['wash'][2]][2]
wash_and_waste_clearance = vials_dict[wash_dict['wash'][2]][0]
    
    
    

#GENERATE CLEARANCE AREAS FOR SAFEMOVE
clearance_areas = []
clearance_height = []
def generate_clearance_areas(center_x, center_y, diameter, height):
    p1 = [center_x - diameter/2, center_y - diameter/2]
    p2 = [center_x - diameter/2, center_y + diameter/2]
    p3 = [center_x + diameter/2, center_y + diameter/2]
    p4 = [center_x + diameter/2, center_y - diameter/2]
   # print (center_x, center_y, diameter)
    clearance_areas.append(sg.Polygon([p1,p2,p3,p4]))
   # print(sg.Polygon([p1,p2,p3,p4]))
    clearance_height.append(height)


for location in test_location:
    x = location[0]
    y = location[1]
    diameter = vials_dict[location[2]][1]
    height = vials_dict[location[2]][0]
    generate_clearance_areas(x,y,diameter,height)

for location in stock_dict:
    x = stock_dict[location][0]
    y = stock_dict[location][1]
    diameter = vials_dict[stock_dict[location][2]][1]
    height = vials_dict[stock_dict[location][2]][0]
    generate_clearance_areas(x,y,diameter,height)

for location in wash_dict:
    x = wash_dict[location][0]
    y = wash_dict[location][1]
    diameter = vials_dict[wash_dict[location][2]][1]
    height = vials_dict[wash_dict[location][2]][0]
    generate_clearance_areas(x,y,diameter,height)





#Old read test locations
# =============================================================================
# coordinate_book = xlrd.open_workbook('plate_coordinates.xlsx')
# sheet=coordinate_book.sheet_by_index(0)
# test_location=[]
# 
# for x in range(36):
#     test_location.append((sheet.cell_value(x,1),sheet.cell_value(x,2)))
# 
# #READ WASH PROTOCOL LOCATIONS AND CLEARANCES
# wash_location=(sheet.cell_value(37,1),sheet.cell_value(37,2))
# waste_location=(sheet.cell_value(38,1),sheet.cell_value(38,2))
# 
# #READ PLATE AND MONOMER LOCATIONS
# 
# plate1=sheet.cell_value(40,1)
# plate2=sheet.cell_value(41,1)
# stock_dict={}
# 
# for x in range(42,sheet.nrows):
#     
#     if sheet.cell_value(x,1) == '' or sheet.cell_value(x,2) == '':
#         continue
#     
#     stock_dict[sheet.cell_value(x,0)]=(sheet.cell_value(x,1),sheet.cell_value(x,2))
# =============================================================================

########################################################################
#UNCOMMENT FOR 96 WELL PLATE LOCATION AND COMMENT ABOVE TEST LOCATION
#96 WELL PLATE COORDINATES GENERATE. WORKS FINE.

#x_position=[]
#x=30
#x_start=30
#x_end=128
#x_position.append(x)
#for y in range(11):
#    
#    x+=((x_end-x_start)/11)
#    x_position.append(x)
##print(ran)
#
#y_position=[]
#y=1.5
#y_start=1.5
#y_end=64
#y_position.append(y)
#for x in range(7):
#    y+=((y_end-y_start)/7)
#    y_position.append(y)                
#
#test_location=[]    
#for x in range(7,-1,-1):
#    for y in range(12):
#      test_location.append((x_position[y],y_position[x]))


########################################################################

          
test_book = xlrd.open_workbook('experiment.xlsx')
sheet=test_book.sheet_by_index(0)

#GENERATE EXPERIMENT TESTS

# =============================================================================
# Generates a list of experiments, sorted by vials:
# Biglist-|Vial 1:    (1.0, (42.5, 64.0), 'M1', 25.0, 0)
#         |           (1,Vial 1 Coordinates, Stock Soln M1, Amount to add, Timepoint)
#         |           ^Meaning add x amount of stock soln M1 to vial 1 at timepoint y
#         |           (1.0, (42.5, 64.0), 'M2', 25.0, 15) 
#         |           ^Add 25uL of M2 to vial 1 at 15min
#         |           (1.0, (42.5, 64.0), 'M3', 25.0, 60)
#         |
#         |Vial 2:    (2.0, (58.5, 63.5), 'M1', 50.0, 0)
#         |...
# =============================================================================

biglist=[]
timer=0
for x in range(1,sheet.nrows):
    waittime  = 0
    buffer = []
    for r in range(1,sheet.ncols,2):
        if sheet.cell_value(x,r) == '' or sheet.cell_value(x,r+1) == '':
            continue
        if sheet.cell_value(x,r) == 'WAIT' and sheet.cell_value(x,r+1) != '':
            waittime+=sheet.cell_value(x,r+1)
            continue
        buffer.append((sheet.cell_value(x,0),test_location[int((sheet.cell_value(x,0)))-1],sheet.cell_value(x,r),sheet.cell_value(x,r+1),waittime))
        
    if buffer != []:
        biglist.append(buffer)


#Ungroup biglist. 'flat' is an unsorted list of all unit operations
#A member of flat will look like this: (1.0, (42.5, 64.0), 'CAT', 25.0, 0)
flat=[i for j in biglist for i in j]  #loops thru the two levels of lists in biglist

#Sort all unit ops. First by timestamp, then stock soln name, then by vial number
sortbiglist=sorted(flat, key=lambda flat: (flat[4],flat[2],flat[0]))

# Old sorting algorithm. Sorts all unit ops. First by timestamp, then by first two letters of stock soln, then by coordinate of vial
# sortbiglist=sorted(flat, key=lambda flat: (flat[4],(flat[2][0],flat[2][1]),(flat[1][0],flat[1][1])))

#Group all unit ops. Loops thru sortbiglist and groups ops that have the same stock name and same timestamp
stock = sortbiglist[0][2]
grplist = []
buffer=[]

for i in sortbiglist:
    
    if i[2] != stock:
        stock = i[2]
        if buffer != []:
            grplist.append(buffer)
        buffer = []
    buffer.append(i)

if buffer != []:
    grplist.append(buffer)
    buffer = []

# =============================================================================
# timestamps = sorted(set(map(lambda x:x[4], sortbiglist)))       #all possible timestamps
# groupbiglist_time = [[y for y in grplist if y[0][4]==x] for x in timestamps]        #sort by timestamps
# =============================================================================

#Group dispenses that can be done with one syringe into "track"
timestamp = 0
amount = 0
buffer = []
track = []
#a list member looks like this: (1.0, (42.5, 64.0), 'M2', 25.0, 15) 
for i in grplist:
    for j in i:
        
        if j[3] >= syr_volume:
            if buffer != []:
                    track.append(buffer)
            buffer = []
            amount = j[3]
            k = (j[0],j[1],j[2],syr_volume,j[4])
            while amount > syr_volume:
                buffer.append(k)
                track.append(buffer)
                buffer = []
                amount -= syr_volume
            k = (j[0],j[1],j[2],amount,j[4])
            buffer.append(k)
            track.append(buffer)
            buffer = []
        
        else:
            amount += j[3]
            if amount >= syr_volume:
                if buffer != []:
                    track.append(buffer)
                amount = j[3]
                buffer = []
            buffer.append(j)
        
    if buffer != []:
        track.append(buffer)
    buffer = []
    amount = 0
    


    
#AMOUNT TO E VALUE GCODE         
def conversion(microL):
    E_value =(conversion_factor*microL)/syr_volume
    return E_value

    
#KEEPS TRACK ON CURRENT AND PREVIOUS POSITION FROM EACH MOVE FUNCTION CALL
lastPoint = {"x": None, "y": None, "z": None, "e":None, "speed":None}
currentPoint= {"x": 0, "y": 0, "z": 0, "e":0, "speed":1000}


# Generate the move command with optional parameters
def move(x=None, y=None, z=None, e=None, speed=None):            
    #print "  ## move() ##"
    s = "G1 "
    if x is not None: 
        s += "X" + str(x) + " "
        lastPoint["x"]=currentPoint["x"]
        currentPoint["x"] = x 
    if y is not None: 
        s += "Y" + str(y) + " "
        lastPoint["y"]=currentPoint["y"]
        currentPoint["y"] = y 
    if z is not None: 
        s += "Z" + str(z) + " "
        lastPoint["z"]=currentPoint["z"]
        currentPoint["z"] = z 
    if e is not None:
        s += "E"+ str(-e) + " "
        lastPoint["e"]=currentPoint["e"]
        currentPoint["e"] = e
    if speed is not None:
        s += "F" + str(speed)
        lastPoint["speed"]=currentPoint["speed"]
        currentPoint["speed"] = speed
    #s += "\n"
    return s



#Checks if an xy move is called. If so, calculate necessary clearance and raise Z axis before moving.

def safemove(result, x=None, y=None, z=None, e=None, speed=None):
    
    if x is not None or y is not None:
        track_raw = [[currentPoint["x"],currentPoint["y"]],[x,y]]
        safe_height = 0
        flag = 0
        lcl_safe_height = []
        
        p1 = sg.Point(track_raw[0])
        p2 = sg.Point(track_raw[1])
        track = sg.LineString(track_raw)
        #print(track)
        
        for i in range(len(clearance_areas)):
            if clearance_areas[i].contains(p1) and clearance_areas[i].contains(p2):
                safe_height = clearance_height[i]
                flag = 1
                break
            if clearance_areas[i].intersects(track):
                lcl_safe_height.append(clearance_height[i])
        
        if flag == 0:
            safe_height = min(lcl_safe_height)
        
        #result.append(';too low')        
        result.append(move(x=None,y=None,z=safe_height,e=None,speed=speed))
        
    result.append(move(x=x, y=y, z=z, e=e, speed=speed))
    
    
    
    
    
#when you don't want to be safe...
def yolomove(result, x=None, y=None, z=None, e=None, speed=None):
     #result.append(';yolo')        
    result.append(move(x=x, y=y, z=z, e=e, speed=speed))
     
    
    
    

# GERNERATE WAIT COMMAND IN MINUTES
def wait(time=None):            
    #print "  ## move() ##"
    
    s = "G4 "
    if time is not None: 
        s += "P" + str(time*60000)

    #s += "\n"
    return s

#CALCULATE TIME
def time(start_coordinate,end_coordinate,acceleration):
        
        distance=(((end_coordinate[0]-start_coordinate[0])**2)+((end_coordinate[1]-start_coordinate[1])**2)+((end_coordinate[2]-start_coordinate[2])**2))**(1/2)
        time=((2*distance)/2000)**(1/2)
        return time 

# =============================================================================
# def block(x,y):
#     if 0  <= x <= 25 and 0 <= y <= 200 :
#         return move(x=None,y=None,z=45,e=None,speed=1000)
#     if 25  <= x <= 175 and 0 <= y <= 200:
#         return move(x=None,y=None,z=3,e=None,speed=1000)
#     if 175  <= x <= 200 and 0 <= y <= 200:
#         return move(x=None,y=None,z=45,e=None,speed=1000)
# =============================================================================

#LOWER TO HEIGHT Z, THEN EXTRUDE amount INTO test. 
#coordinate_dict is a list that maps vial number to its coordinate, test is the vial number.
#Currently there is only one coordinate_list, which is test_location

def dispense(coordinate_list,test,amount,result):
    
    movement_speed = 5000
    
    E_value = conversion(amount)
    
    result.append(';dispense '+ str(amount) + ' uL into ' + str(test+1))        #test+1 because python starts at 0
    
    result.append('M83')    #Sets E to relative so multiple dispenses work
 
    safemove(result,x=coordinate_list[test][0],y=coordinate_list[test][1],z=None,e=None,speed=movement_speed)
                     
    safemove(result,x=None,y=None,z=depth(coordinate_list[test]),e=None,speed=movement_speed)
    
    safemove(result,x=None, y=None, z=None,e=-E_value,speed=movement_speed)
     
#TIME TAKES TO DISPENSE
def dispense_time(destination,test,Z,amount,result):
 
    times=0
    
    times+=time((lastPoint['x'],lastPoint['y'],lastPoint['z']),(destination[test][0],destination[test][1],lastPoint["z"]),2000)
    
    times+=time((lastPoint['x'],lastPoint['y'],lastPoint['z']),(destination[test][0],destination[test][1],Z),2000)        
            
    times+=time((lastPoint['e'],lastPoint['y'],lastPoint['z']),(amount,destination[test][1],Z),2000)
    return times

#WASH PROTOCOL
def wash(result):
    
    movement_speed = 5000
    
    result.append(';wash')
    
    result.append('M82')  #Sets E to absolute so it can go to zero properly
     
    # safemove(result,x=None,y=None,z=wash_and_waste_clearance,e=None,speed=movement_speed)
    
    safemove(result,x=waste_location[0],y=waste_location[1],z=None,e=None,speed=movement_speed) #G1 X126 Y21 
    
    safemove(result,x=None,y=None,z=depth(wash_dict['waste']),e=None,speed=movement_speed) #G1 Z50
    
    safemove(result,x=None,y=None,z=None,e=0,speed=500)  #G1 E0
	
    #safemove(result,x=None,y=None,z=wash_and_waste_clearance,e=None,speed=movement_speed)  #G1 Z78
    
    safemove(result,x=wash_location[0],y=wash_location[1],z=None,e=None,speed=movement_speed)  #G1 X126 Y6 

    safemove(result,x=None,y=None,z=depth(wash_dict['wash']),e=None,speed=movement_speed)  #G1 X50
        
    safemove(result,x=None,y=None,z=None,e=conversion(syr_volume),speed=500)  #G1 E-61
    
    result.append(wait(1/60))
    
    #safemove(result,x=None,y=None,z=wash_and_waste_clearance,e=None,speed=movement_speed)  #G1 Z78
    
    safemove(result,x=waste_location[0],y=waste_location[1],z=None,e=None,speed=movement_speed)  #G1 X126 Y21
	
    safemove(result,x=None,y=None,z=depth(wash_dict['waste']),e=None,speed=movement_speed) # newly added, generates "G1 Z50.0 F1000"
    
    safemove(result,x=None,y=None,z=None,e=0,speed=500)  #G1 E0
	
    #safemove(result,x=None,y=None,z=wash_and_waste_clearance,e=None,speed=movement_speed) # newly added, generates "G1 Z78.0 F1000"

#TIME IT TAKES TO WASH
def wash_time(result):
    times=0
    
    times+=time((lastPoint['x'],lastPoint['y'],lastPoint['z']),(lastPoint['x'],lastPoint['y'],wash_and_waste_clearance),1000)
    
    times+=time((lastPoint['x'],lastPoint['y'],lastPoint['z']),(wash_location[0],wash_location[1],lastPoint['z']),1000)
    
    times+=time((lastPoint['x'],lastPoint['y'],lastPoint['z']),(lastPoint['x'],lastPoint['y'],wash_and_waste_depth),1000)
    
    times+=time((lastPoint['e'],lastPoint['y'],lastPoint['z']),(0,lastPoint['y'],lastPoint['z']),2000)
    
    times+=time((lastPoint['e'],lastPoint['y'],lastPoint['z']),(conversion_factor,lastPoint['y'],lastPoint['z']),2000)
    
    times+=time((lastPoint['x'],lastPoint['y'],lastPoint['z']),(lastPoint['x'],lastPoint['y'],wash_and_waste_clearance),1000)
    
    times+=time((lastPoint['x'],lastPoint['y'],lastPoint['z']),(waste_location[0],waste_location[1],lastPoint['z']),1000)
    
    times+=time((lastPoint['e'],lastPoint['y'],lastPoint['z']),(0,lastPoint['y'],lastPoint['z']),1000)
    
    return times


def refill(source,beak,amount,result): #draw certain amount of liquid from stock solution vial (beaker)
    
    movement_speed = 5000
    
    E_value = conversion(amount)
    
    result.append(';draw ' + str(amount) + ' mL of ' + str(beak))
    
    result.append('M83')    #Sets E to relative
    
    #safemove(result,x=None,y=None,z=exp_vial_clearance,e=None,speed=movement_speed)
    
    safemove(result,x=source[beak][0],y=source[beak][1],z=None,e=None,speed=movement_speed)
    
    safemove(result,x=None,y=None,z=depth(source[beak]),e=None,speed=movement_speed)    
    
    safemove(result,x=None,y=None,z=None,e=E_value,speed=500)
    
    result.append(wait(1/60))
    
    #safemove(result,x=None,y=None,z=exp_vial_clearance,e=None,speed=movement_speed)
    
   
def refill_time(source,beak,amount,result):
    
    times=0
    
    mL=conversion(amount)
    
    times+=time((lastPoint['x'],lastPoint['y'],lastPoint['z']),(lastPoint['x'],lastPoint['y'],exp_vial_clearance),1000)
    
    times+=time((lastPoint['x'],lastPoint['y'],lastPoint['z']),(source[beak][0],source[beak][1],lastPoint['z']),1000)  
    
    times+=time((lastPoint['x'],lastPoint['y'],lastPoint['z']),(lastPoint['x'],lastPoint['y'],stock_depth),1000) 
       
    times+=time((lastPoint['e'],lastPoint['y'],lastPoint['z']),(mL,lastPoint['y'],lastPoint['z']),1000)
    
    times+=time((lastPoint['x'],lastPoint['y'],lastPoint['z']),(lastPoint['x'],lastPoint['y'],exp_vial_clearance),1000)
    
    times+=time((lastPoint['x'],lastPoint['y'],lastPoint['z']),(source[beak][0],source[beak][1],lastPoint['z']),1000)
    return times
    
####################################################################################    

#START GCODE GENERATION
#a list member looks like this: (1.0, (42.5, 64.0), 'M2', 25.0, 15) 
result=[]
result.append('G28')
result.append('G92 E0')
result.append('G90')

timestamp = 0
current_stock = track[0][0][2]
currentPoint = {'x': 0, 'y': 0, 'z': 0, 'e': 0, 'speed': 0}
lastPoint = {'x': 0, 'y': 0, 'z': 0, 'e': 0, 'speed': 0}

for i in track:
    if i[0][4] > timestamp:                 #Determines if current action has the same timestamp
        elapsed_time = i[0][4] - timestamp   #Calcultates time until new timestamp
        timestamp = i[0][4]                 #Updates current timestamp
        result.append('G4 S' + str(elapsed_time*60) + ';wait until ' + str(timestamp) + ' minutes XTIME')
        #writes a G4 command and comments on the new wait time. 
        #Integrated GCode sender will read the 'XTIME' string in comment and wait until new timestamp
        #If using other GCode senders the G4 wait time will not account for time passed during printer movement
    if i[0][2] != current_stock:
        wash(result)
        current_stock = i[0][2]
    amount = 0
    for j in i:
        amount += j[3]  #Adds up all the amount that is needed
        
    refill(stock_dict,i[0][2],amount,result)
    
    for j in i:
        amount = j[3]
        dispense(test_location,int(j[0]-1),amount,result)
        timer+=dispense_time(test_location,int(j[0]-1),exp_vial_depth,amount,result)


result.append ('G28 Z')
result.append ('G28 X')

#Old GCode generation code that uses sortbiglist
# =============================================================================
# amount=0 #total mL to dispense whether grouped or individual dispense
# track=[] #store group of same monomer in same time stamp
# timer=0 
# skip=[] #keep track of which instructions to skip because they are grouped together
# 
# for index in range(len(sortbiglist)):
#     #reset skip once last grouped instruction is reached
#     if skip != []:
#         if index == skip[-1]:
#             skip=[]
#             continue
#     
#         else:
#             #skip grouped instructions
#             if index in skip:
#                 continue
#     
#     
#     track.append(sortbiglist[index])
#     amount+=sortbiglist[index][3]
#     
#     #END OF LIST DISPENSE LAST AMOUNT
#     if index == len(sortbiglist)-1:
#         #draw amount
#         result.append('draw ' + str(amount) + ' mL of ' + str(sortbiglist[index][2]))
#         refill(stock_dict,sortbiglist[index][2],amount,result)
#         
#         dispense_convert=conversion(amount)
#         for i in track:
#             
#             dispense_convert-=conversion(i[3])
#             #dispense
#             result.append('dispense '+ str(i[3]) + ' mL of ' + str(i[2]) + ' into ' + str(test_location[int(i[0]-1)]))
#             dispense(test_location,int(i[0]-1),exp_vial_depth,dispense_convert,result)
#             track=[]
#             amount=0
#             result.append('wash')
#             wash(result)
#             break
#         break
#         
#         
#         
#     #SAME MONOMER AND TIME STAMP GROUPED TOGETHER
#     #check is next sequential dispense is the same monomer and time stamp
#     if (sortbiglist[index+1][2]==sortbiglist[index][2] and sortbiglist[index+1][4]==sortbiglist[index][4]):
#         # look at all subsequent instructions and check for group conditions
#         # Next line asks for the same compound and the same timestamp
#         for jndex in range(index+1,len(sortbiglist)):
#             
#             if (sortbiglist[jndex][2]==sortbiglist[index][2] and sortbiglist[jndex][4]==sortbiglist[index+1][4]):
#                 #add instruction to group track and increase total dispense amount
#                 track.append(sortbiglist[jndex])
#                 amount+=sortbiglist[jndex][3]
#                 #note that add instructions do not need to be dispensed again. they are filled.
#                 skip.append(jndex)
#                 continue
#             #group condition not met
#             else:
#                 break
#     
#     
#     #ADD TOTAL AMOUNT AND DRAW AND DISPENSE WHETHER SINGLE STEP OR GROUP OF STEPS
#     #draw total amount
#     result.append('draw ' + str(amount) + ' mL of ' + str(sortbiglist[index][2]))
#     refill(stock_dict,sortbiglist[index][2],amount,result)
#     timer+=refill_time(stock_dict,sortbiglist[index][2],amount,result)
#     dispense_convert=conversion(amount)
#     for i in track:
#         dispense_convert-=conversion(i[3])
#         
#         if plate1=='VIALS' or plate2 == 'VIALS':
#             result.append('dispense '+ str(i[3]) + ' mL of ' + str(i[2]) + ' into ' + str(test_location[int(i[0]-1)]))
#             dispense(test_location,int(i[0]-1),exp_vial_depth,dispense_convert,result)
#             timer+=dispense_time(test_location,int(i[0]-1),exp_vial_depth,dispense_convert,result)
#             
#             #RAISE HEIGHT TO GET OUT OF PUNCTURE VIALS
#             result.append(move(x=None,y=None,z=exp_vial_clearance,e=None,speed=1000))
#             timer+=time((0,0,lastPoint['z']),(0,0,exp_vial_clearance),2000)
#             
#         else: #WELLS dispense at constant height
#             result.append('dispense '+ str(i[3]) + ' mL of ' + str(i[2]) + ' into ' + str(test_location[int(i[0]-1)]))
#             dispense(test_location,int(i[0]-1),exp_vial_clearance,dispense_convert,result)
#             timer+=dispense_time(test_location,int(i[0]-1),exp_vial_clearance,dispense_convert,result)
#     
#     result.append('wash')         
#     wash(result)
#     timer+=wash_time(result)
#     
#     #after dispense(s) check if next dispense in sequence is in same time stamp
#     #NEXT MONOMER IS DIFFERENT TIME STAMP. RECALCULATE WAIT TIME INBETWEEN
#     if sortbiglist[index][4]!=sortbiglist[index+1][4]:
#         #no point reducing zero wait time
#         if sortbiglist[index][4] != 0:
#             if timer >= sortbiglist[index][4]:
#                 final_wait=0
#                 result.append('wait ' + str(final_wait) + ' from ' + str(sortbiglist[index][4]))
#                 result.append(wait(final_wait))
#                 timer=0
#             
#             #reduce upcoming wait time
#             else:
#                 final_wait=sortbiglist[index][4]-timer
#             
#                 result.append('wait ' + str(final_wait) + ' from ' + str(sortbiglist[index][4]))
#                 result.append(wait(final_wait))
#                 timer=0    
#     
#     #GROUP OF SAME MONOMER AND TIME BUT NEXT DISPENSE IS DIFFERENT TIME STAMP FROM GROUP. RECALCULATE TIME INBETWEEN.
#     if track != [] and skip != []:
#         
#         if track[-1][4]!=sortbiglist[int(skip[-1]+1)][4]:
#                 
#                 
#                 if sortbiglist[index][4] != 0:
#                     if timer >= sortbiglist[index][4]:
#                         final_wait=0
#                         result.append('wait ' + str(final_wait) + ' from ' + str(sortbiglist[index][4]))
#                         result.append(wait(final_wait))
#                         timer=0
#             
#             #reduce upcoming wait time
#                     else:
#                         final_wait=sortbiglist[index][4]-timer
#                     
#                         result.append('wait ' + str(final_wait) + ' from ' + str(sortbiglist[index][4]))
#                         result.append(wait(final_wait))
#                         timer=0  
#                       
#         
#     
#     #instructions in group are dispensed. reset and look for another group of instructions. also reset amount to 0. all dispenses handled.
#     
#     track=[]
#     amount=0
# =============================================================================
    
    
    
    
########################################################################
    
#GENERATE COORDINATES FOR SMALL VILAS (NEEDS TWEAKING, COORDS NOT EXACTLY RIGHT)

#x_positions=[]
#x=29
#
#x_start=29
#x_end=133.5666667
#
#x_positions.append(x)
#for y in range(7):
#    
#    x+=((x_end-x_start)/7)
#    x_positions.append(x)
##print(ran)
#
#y_positions=[]
#y=6.166666667
#
#y_start=6.166666667
#
#y_end=64
#y_positions.append(y)
#for x in range(4):
#    y+=((y_end-y_start)/4)
#    y_positions.append(y)
#
#
#test_location=[]    
#for x in range(4,-1,-1):
#    for y in range(8):
#      test_location.append((x_positions[y],y_positions[x]))

#print(result)
#SEND GCODE TO PRINTER

#import serial
#ser = serial.Serial('COM4', 115200)
#out = ser.readline()

#ser.write(b'G28 \n')
#for i in result:
#    solve=i+' \n'
#    ser.write(str.encode(solve)) 
########################################################################


# output txt
import os
with open(os.path.join(os.getcwd(), 'result.txt'), 'w') as f:
    for e in result:
        f.write(e + '\n')
    