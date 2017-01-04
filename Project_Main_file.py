import math
import random
import numpy as np
import sys

my_path='C:\\Users\\varun\\Anaconda3\\envs\\ENTS656_VJ'
sys.path.append(my_path)
import Project_RSL_file as p_rsl
import Project_call_processing as p_cp

count_time=hours=0
Lamda=1/1800 #in calls per second
rsl_threshold=-102
np.random.seed(150)
p_rsl.initialize()
while(hours<6):
    while (count_time<3600):
        count_time=count_time+1
        for user_number in range(320):
            if count_time<1 or p_cp.user_in_call(user_number)==0: #1st user or user is not on call then checks for prob. of call
                if random.choice(np.arange(0,1,Lamda))!=0: #checking for probability of a call
                    user_number=user_number+1
                else :
                    user_loc=np.random.uniform(-3,3)#uniform distribution of users
                    user_dir=random.randint(0,1) #random direction with 50/50 prob 0-south,1-north
                    user_rsl,sector_serving,other_sector_rsl,other_sector=p_rsl.RSL(user_loc)
                    if user_rsl<rsl_threshold:#checking if RSL enough to make a call
                        user_number=user_number+1
                        p_cp.call_drop_counter(sector_serving)
                    elif p_cp.channel_availability(sector_serving)==0 : #check if no channel available and record as blocked call for the sector
                        p_cp.call_block_counter(sector_serving)
                        user_number=user_number+1
                    elif user_rsl>rsl_threshold and p_cp.channel_availability(sector_serving)==1: #check for channel availability in serving sector and initiate call
                        p_cp.call_start(user_number,sector_serving,user_dir,user_loc,user_rsl)
                        user_number=user_number+1
                    elif other_sector_rsl>rsl_threshold and p_cp.channel_availability(other_sector)==1:#check for channel availability in other sector and initiate call
                        p_cp.call_start(user_number,other_sector,user_dir,user_loc,other_sector_rsl)
                        user_number=user_number+1
                    
            else:
                p_cp.user_update(user_number)
                user_number=user_number+1        
    print('Hour',hours+1)
    p_cp.print_report()                
    hours+=1
    count_time=0                
                
            
