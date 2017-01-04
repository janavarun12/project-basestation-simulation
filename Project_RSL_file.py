'''norm is to assume distance to be from the mid-point and in km'''
import math
import numpy as np

Freq_secta=860
Freq_sectb=865
loc=0.02

def initialize():
    '''initial settings of EIRP at boresight and shadowing values'''
    Tx_power,Losses,AGtx=43,2,15
    global EIRP_boresight
    EIRP_boresight=Tx_power-Losses+AGtx
    global list_shadowing_val
    list_shadowing_val=np.random.lognormal(0,2,600)

def EIRP(distance,sector):
    '''computing the EIRP from boresight and antenna discrimination values'''
    x_delta=0.02
    y_delta=distance
    vector_dist=np.array([x_delta,y_delta])
    sectora=np.array([0,1])
    sectorb=np.array([math.sqrt(3)/2,-0.5])
    theta_a=math.degrees(math.acos(np.dot(sectora,vector_dist)/(np.sqrt(sectora.dot(sectora))*np.sqrt(vector_dist.dot(vector_dist)))))
    theta_b=math.degrees(math.acos(np.dot(sectorb,vector_dist)/(np.sqrt(sectorb.dot(sectorb))*np.sqrt(vector_dist.dot(vector_dist)))))
    fobj=open("C:\\Users\\varun\\Anaconda3\\envs\\ENTS656_VJ\\antenna_pattern.txt",'r')

    for i in range(0,int(theta_a)+1):
        str_file=fobj.readline()

    fobj.close()
    secta_disc=float(str_file.split()[1])

    fobj=open("C:\\Users\\varun\\Anaconda3\\envs\\ENTS656_VJ\\antenna_pattern.txt",'r')

    for i in range(0,int(theta_b)+1):
        str_file=fobj.readline()

    fobj.close()
    sectb_disc=float(str_file.split()[1])
    if sector==0:
        return secta_disc
    else:
        return sectb_disc
    
def Prop_loss(distance,sector):
    '''returns propogation loss'''

    D=math.sqrt(math.pow(distance,2)+math.pow(loc,2))
    height_bstn=50
    height_mob=1.5
    if sector==0:
        P_loss_secta=69.55+26.16*math.log10(Freq_secta)-13.82*math.log10(height_bstn)+(44.9-6.55*math.log10(height_bstn))*math.log10(D)-((1.1*math.log10(Freq_secta)-0.7)*height_mob-(1.56*math.log10(Freq_secta)-0.8))
        return P_loss_secta
    else:
        P_loss_sectb=69.55+26.16*math.log10(Freq_sectb)-13.82*math.log10(height_bstn)+(44.9-6.55*math.log10(height_bstn))*math.log10(D)-((1.1*math.log10(Freq_sectb)-0.7)*height_mob-(1.56*math.log10(Freq_sectb)-0.8))
        return P_loss_sectb

def Shadowing(distance,list_s):
    '''Shadowing effect based on position'''
    Shadowing_val=list_s[math.ceil(((abs(distance))*100))]
    return(Shadowing_val)

def Fading():
    '''fading effect by complex gaussian distribution'''
    
    x=np.array(np.random.normal(0,1,10))
    y=np.array(np.random.normal(0,1,10))
    fading_samples=x+1j*y
    fading_samples_abs=np.absolute(fading_samples)
    fading_samples_abs.sort()
    deepfade_value=fading_samples_abs[-2]
    deepfade_value_db=10*math.log10(deepfade_value)
    return deepfade_value_db

 
def RSL(distance):
    '''computes RSL per sector and returns the RSL and sector'''

    RSL_sectora= EIRP_boresight+EIRP(distance,0)-Prop_loss(distance,0)+Fading()+Shadowing(distance,list_shadowing_val)
    RSL_sectorb= EIRP_boresight+EIRP(distance,1)-Prop_loss(distance,1)+Fading()+Shadowing(distance,list_shadowing_val)
    if RSL_sectora>RSL_sectorb:
        return (RSL_sectora,0,RSL_sectorb,1)
    else:
        return (RSL_sectorb,1,RSL_sectora,0)
    

