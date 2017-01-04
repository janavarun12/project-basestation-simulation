
import numpy as np
import sys

my_path='C:\\Users\\varun\\Anaconda3\\envs\\ENTS656_VJ'
sys.path.append(my_path)
import Project_RSL_file as p_rsl

HOM=0
global call_list_details
call_list_details=np.full((6,320),0,dtype=float)#row 1 will be 1-active call 0-inactive
                                             #row 2 will be user direction 0-north 1-south
                                             #row 3 will be call lenghts of each user
                                             #row 4 will be users current location
                                             #row 5 will be users serving sector
                                             #row 6 will be users serving RSL

global sector_details
sector_details=np.full((2,8),0,dtype=float)#col 1 will be no.of calls at time
                                        #col 2 will be call attempts
                                        #col 3 will be successful completed calls
                                        #col 4 will be successful handoffs
                                        #col 5 will be handoff failures
                                        #col 6 will be call drops due to low signal strength
                                        #col 7 will be blocked calls due to capacity
                                        #col 8 will be used channels
sector_details[0][7]=sector_details[1][7]=15
channel_a=channel_b=callattemtps_a=callattemtps_b=success_Calls_a=success_Calls_b=success_handoffs_a=success_handoffs_b=fail_handoff_a=fail_handoff_b=call_drop_a=call_drop_b=call_block_a=call_block_b=0

def channel_availability(sector):
    '''maintains channel availability state for each sector'''
    if sector==0:
        if sector_details[0][7]>0:
            return 1
        else:
            return 0
    else:
        if sector_details[1][7]>0:
            return 1
        else:
            return 0
def channel_update(sector,op): #1-increase available channels 0-decrease available channels
    '''process channel number updates'''
    if sector_details[sector][7]<15 and op==1:
        sector_details[sector][7]+=1
    elif sector_details[sector][7]<=15 and sector_details[sector][7]>0 and op==0:
        sector_details[sector][7]-=1
    else:
        print('channel problem',sector_details[sector][7],op)
      
        
def call_drop_counter(sector):
    '''updates call drops per sector'''
    sector_details[sector][5]+=1

def call_block_counter(sector):
    '''updates call blocks per sector'''
    sector_details[sector][6]+=1

def user_in_call(user_number):
    '''check if user in call'''
    if call_list_details[0][user_number]==1:
        return 1
    else:
        return 0
def call_start(user_number,sector,user_dir,user_loc,user_rsl):
    '''determine call time and update active call list'''
    call_list_details[2][user_number]=int(np.random.exponential(180)) #call length is stored
    call_list_details[0][user_number]=1 
    call_list_details[1][user_number]=user_dir
    call_list_details[3][user_number]=user_loc
    call_list_details[4][user_number]=sector
    call_list_details[5][user_number]=user_rsl
    sector_details[sector][1]=sector_details[sector][1]+1 #updating call attempt counter
    channel_update(sector,0) #update channel availability

def user_update(user_number):
    '''adjusts user location and time if in active call'''
    if call_list_details[1][user_number]==0:
        call_list_details[3][user_number]=call_list_details[3][user_number]+0.015
    else:                                                          #updating location
        call_list_details[3][user_number]=call_list_details[3][user_number]-0.015
    if call_list_details[3][user_number]>3 or call_list_details[3][user_number]<-3: #location out of bounds place to change for location
        sector_details[call_list_details[4][user_number]][2]+=1  #updating sucessful calls list
        channel_update(call_list_details[4][user_number],1)  #updating used channels
        call_list_details[0][user_number]=0                     #user no longer in call
        call_list_details[2][user_number]=0
        return        

    call_list_details[2][user_number]=call_list_details[2][user_number]-1 #updating time
    if call_list_details[2][user_number]==0:                     #call time ends
        sector_details[call_list_details[4][user_number]][2]+=1  #updating sucessful calls list
        channel_update(call_list_details[4][user_number],1)  #updating used channels
        call_list_details[0][user_number]=0                     #user no longer in call
        call_list_details[2][user_number]=0
        return
    
    serv_sect_rsl,serv_sect,other_sect_rsl,other_sect=p_rsl.RSL(call_list_details[3][user_number])
    if serv_sect!=call_list_details[4][user_number]:
        serv_sect_rsl,other_sect_rsl=other_sect_rsl,serv_sect_rsl   #compensating for scenario where other sectors rsl is greater before handoff is checked
        serv_sect,other_sect=other_sect,serv_sect
    call_list_details[5][user_number]=serv_sect_rsl
    call_list_details[4][user_number]=serv_sect
    if serv_sect_rsl<-102:
        call_drop_counter(serv_sect) #call drop
        call_list_details[0][user_number]=0 #user no longer in call
        channel_update(call_list_details[4][user_number],1)        
        return
    elif serv_sect_rsl<(other_sect_rsl+HOM):
        handoff_attempt(serv_sect_rsl,serv_sect,other_sect_rsl,other_sect,user_number)

def handoff_attempt(serv_sect_rsl,serv_sect,other_sect_rsl,other_sect,user_number):
    '''tries to make a handoff and updates respective parameters'''
    if sector_details[other_sect][7]>0:
        channel_update(other_sect,0)
        channel_update(serv_sect,1)                  #update serving sector and RSL and channels available
        call_list_details[5][user_number]=other_sect_rsl
        call_list_details[4][user_number]=other_sect
        sector_details[serv_sect][3]+=1   #update handoff success
    else:
        sector_details[serv_sect][4]+=1
       
        
def print_report():

    print('call attempts for sector a      :',sector_details[0][1],'sector b:',sector_details[1][1],'total :',sector_details[0][1]+sector_details[1][1])
    print('successful calls for sector a   :',sector_details[0][2],'sector b:',sector_details[1][2],'total :',sector_details[0][2]+sector_details[1][2])
    print('successful handoffs for sector a:',sector_details[0][3],'sector b:',sector_details[1][3],'total :',sector_details[0][3]+sector_details[1][3])
    print('handoff failures for sector a   :',sector_details[0][4],'sector b:',sector_details[1][4],'total :',sector_details[0][4]+sector_details[1][4])
    print('call drops for sector a         :',sector_details[0][5],'sector b:',sector_details[1][5],'total :',sector_details[0][5]+sector_details[1][5])
    print('call blocks for sector a        :',sector_details[0][6],'sector b:',sector_details[1][6],'total :',sector_details[0][6]+sector_details[1][6])
    print('channles available for sector a :',15-sector_details[0][7],'sector b:',15-sector_details[1][7],'total :',30-(sector_details[0][7]+sector_details[1][7]))
    

    
