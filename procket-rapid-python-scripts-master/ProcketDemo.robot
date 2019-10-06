*** Settings ***
Suite Setup       Procket Up
Suite Teardown    Procket Down
Library           procketLib.py

*** Test Cases ***
Procet_Rapid
    
    #Print used Python version
	Python_version

	# *** IF Board voltages *** 
	Power Up	2	ALL
	#Power Up    2    +24V_ENABLE
    #Power Up    2    +5V_ENABLE
    #Power Up    2    +3V3_ENABLE
	#Power Up    2    +1V8_ENABLE
	#Power Up	2	 OUTPUT_LVLSHFT_EN
	#Log Power Status

	# *** DUT Power control *** 
	Power Up    4    ALL
	#Power Up    4    OPTO1_CTRL
	#Power Up    4    OPTO2_CTRL
	#Power Up    4    OPTO3_CTRL
	#Power Up    4    OPTO4_CTRL
	#Power Up    4    RS-232_EN
	#Power Up    4	 PROGRAMMER_EN
	#Power Up    4    DUT_PWR1_EN
	#Power Up    4    DUT_PWR2_EN
	#Log Power Status

	# *** GP relays *** 
	Set General Purpose Relays    3    ALL
	#Set General Purpose Relays    3    EXP0_A76_0
	#Set General Purpose Relays    3    EXP0_A76_1
	#Set General Purpose Relays    3    EXP0_A76_2
	#Set General Purpose Relays    3    EXP0_A76_3
	#Set General Purpose Relays    3    EXP0_A76_4
	#Set General Purpose Relays    3    EXP0_A76_5
	#Set General Purpose Relays    3    EXP0_A76_6
	#Set General Purpose Relays    3    EXP0_A76_7
    #Log Power Status

	# *** Connector Pins ***
	Set Connector Pins    1    ALL
	#Set Connector Pins    1    X120-1
    #Reset Connector Pins    1   ALL
    #Set Connector Pins    1    X120-1
	#${arvo}	Read Connector Pins    2
	


	# *** Digital I/O ***
	#Write Do    1	port0	line0
	#Read Di		port0	line4		 
	#Write Do    2	port0	line1
	#Read Di		port0	line5		 
	#Write Do    4	port0	line2
	#Read Di		port0	line6		 
	#Write Do    8	port0	line3
	#Read Di		port0	line7		 

    
    # *** Write to analog ouput port ***
    #Write Analog Io     value=5
    
    
	# *** Read Analog input port *** 
	#Read Analog Io RSE          
    #Read Analog Io DIFF          
    
    
    # *** PFI, Programmable Function Interface *** 
    #Trigger Analog Input     
    #Trigger Analog Output 
    #Counter    edge_selection=F    initialCount=10     delayInReadCounter=0.5   
    
    
    # *** Memory *** 
    #Writememory      
    #Readmemory  
    
    
        
    
