*** Settings ***
Documentation   Procket Rapid tester and Robot Framework integartion demonstration. In this example, the NI USB 6003 DAQ card is used to perform DUT measurements. It also generates reference voltage just for the presentation purposes. The DAQ card is also used to control Rapid interface board (e.g. power control). The DUT is powered from the additional external power supply.
Library         procketLib.py
Library  mean.py

Suite Setup     Suite setup
Suite Teardown  Procket Down

*** Variables ***
#---LIMITS----
${TEST_1_UPPER_LIMIT}   3.1
${TEST_1_LOWER_LIMIT}   2.9
${TEST_2_UPPER_LIMIT}   3.1
${TEST_2_LOWER_LIMIT}   2.9

${SAMPLES}              1000
${RATE}                 10000
${SUITE_VARIABLE_READOUT}

*** Test Cases ***
Measure DAQ card AO
    [Tags]  TEST 1
    [Documentation]  Measures DC signal generated on DAQ card analog output 0 (only for the presentation).
    WHEN Voltage is set on AO0 with 3 V
    AND Voltage is measured on AI1
    THEN Check whether the readout is between 3.1 and 2.9 V

Measure DUT voltage
    [Tags]  TEST 2
    [Documentation]  Measures DUT voltage through the test needle.
    WHEN Voltage is measured on AI0
    THEN Check whether the readout is between 3.1 and 2.9 V

*** Keywords ***
Suite setup
    Procket Up
    Python_version

Voltage is set on ${port} with ${setpoint} V
    Write Analog Io  ${port}  ${setpoint}

Voltage is measured on ${port}
    ${suite_variable_readout}  Read Analog Io RSE  ${port}  ${SAMPLES}  ${RATE}
    Log  ${suite_variable_readout[0]}
    #${mean}  mean  ${suite_variable_readout}
    #set suite variable  ${SUITE_VARIABLE_READOUT}  ${mean}

Check whether the readout is between ${upper_limit} and ${lower_limit} V
    Run keyword if  ${SUITE_VARIABLE_READOUT} <= ${upper_limit}  and  ${SUITE_VARIABLE_READOUT} >= ${lower_limit}  Pass execution  msg=  Success!
    ...  ELSE  FAIL  msg=  I'm sad panda :(