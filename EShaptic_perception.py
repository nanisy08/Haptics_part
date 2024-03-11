info = """
File    : User_perception_voltage.py
Author  : Sooyeon Kim
Date    : December 27, 2023
Update  : 
Description : User perception voltage test를 위한 코드
Protocol    : 1. 사용자가 화살표 up/down key로 perception threshold voltage를 조절한다.(초기화는 숫자 0)
            : 2. 'enter'로 calibration 종료
            : 3. Step number(정수) 입력 후 자극 확인 0 to step_max(보통 4)
            : 4. Randomly stimulus
"""

import keyboard
import time
import serial
from datetime import datetime
import matplotlib.pyplot as plt
import csv
import random
import sys

csv_file_path = "C:/Users/222BMG13/Desktop/231231 perception test_sr.csv"

print(info)
######################################################
###################### SETTING #######################
## Setting for MK-W103
ComPort = serial.Serial('COM2')
ComPort.baudrate = 115200 # set Baud rate to 115200
ComPort.bytesize = 8    # Number of data bits = 8
ComPort.parity   = 'N'  # No parity
ComPort.stopbits = 1    # Number of Stop bits = 1
current = 0.1 # A
ovp = 30 # V
update_period = 0.5 # sec (recommended)

ComPort.write(f"OVP05:{ovp}\r\n".encode())  # Set the OVP voltage value to be ?V
ComPort.write(f"OVP05:ON\r\n".encode())     # Open/close OVP
ComPort.write(f"ISET05:{current}\r\n".encode())
ComPort.write(f"VSET05:{0}\r\n".encode())

print("==================================")
print("MK-W103 connected")
print("==================================")
voltage = 0

## User perception test
step_num = 4

######################################################
################ FUNCTION AND THREAD #################
### Thread for data logging
exit_flag = False
def log_data():
    global voltage
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Time', 'User Perception'])

        while not exit_flag:
            csv_writer.writerow([datetime.now(), voltage])
            time.sleep(0.1)
##################################################

### Plot function
def setting_plot():
    global max_data_points, ax
    global fig, line
    global time_data, voltage_data
    ### Setting for plotting
    # Lists to store data for plotting
    time_data = []
    voltage_data = []

    plt.ion()  # Turn on interactive mode
    
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 4))
    line, = ax.plot(time_data, voltage_data, color='black', label='Voltage')

    ax.set_xlabel('Time')
    ax.set_ylabel('Voltage [V]')
    ax.set_title('Perception test')
    ax.legend(loc='upper left')
    ax.set_ylim(0, 30)

    max_data_points = 80

subline_min = None
subline_max = None
def plot_data():
    global min_voltage, max_voltage
    global subline_min, subline_max

    # Append data for plotting
    time_data.append(datetime.now())
    voltage_data.append(voltage)

    # Remove previous data
    if len(time_data) > max_data_points:
        time_data.pop(0)
        voltage_data.pop(0)

    # Plot data
    line.set_xdata(time_data)
    line.set_ydata(voltage_data)

    # 보조선
    if subline_min:
        subline_min.remove()
    if subline_max:
        subline_max.remove()
    subline_min = plt.axhline(y=min_voltage, color='b', linestyle=':')
    subline_max = plt.axhline(y=max_voltage, color='r', linestyle=':')
    plt.axhline(y=ovp, color='grey', linestyle='-')

    ax.relim()
    ax.autoscale_view()

    plt.tight_layout()
    plt.draw()
    plt.pause(0.01) # 1ms

######################################################
##################### EXECUTION ######################
time.sleep(0.2)
setting_plot() # open the plotting window

max_voltage = -50
min_voltage = 100

print("==============STEP 1==============")
print("최소, 최대 점에서 space 바를 누르세요(초기화 0), calibration 이후 enter")
start_time = time.time()
while True:
    plot_data()
    
    if keyboard.is_pressed('up'):
        voltage = voltage + 0.5
    elif keyboard.is_pressed('down'):
        voltage = voltage - 0.5
        if voltage < 0:
            voltage = 0

    # update the range
    if keyboard.is_pressed('space'):
        if voltage < min_voltage:
            min_voltage = voltage
        elif voltage > max_voltage:
            max_voltage = voltage
    elif keyboard.is_pressed('0'): # reset the range
        max_voltage = -50
        min_voltage = 100

    # power supply
    if time.time()-start_time > update_period:
        ComPort.write(f"VSET05:{voltage}\r\n".encode())
        start_time = time.time()

    ## Quit
    if keyboard.is_pressed('enter'):
        plt.close('all')
        break

    ## Program 강제 종료
    if keyboard.is_pressed('esc'):
        print("프로그램을 종료합니다")
        plt.close('all')
        ComPort.write(f"ISET05:{0}\r\n".encode())
        ComPort.write(f"VSET05:{0}\r\n".encode())
        sys.close()
        break

print(f">> User perception voltage ragne :({min_voltage:.3f}~{max_voltage:.3f})V")


time.sleep(0.5)
### Thread
# log_thread = threading.Thread(target=log_data)
# log_thread.start()

print("==================================")
print("==============STEP 2==============")
print("==========Stimulus Step===========")
print("=========Quit -> enter 'q'========")
voltage = 0
grad = (max_voltage - min_voltage)/(step_num-1)

ComPort.write(f"VSET05:{0}\r\n".encode())
while True:
    user_input = input(f">> Step num 입력하세요(0~{step_num}): ")

    if user_input.lower() == "q": # Quit
        break
    else:
        try:
            user_integer = int(user_input)
            print("Step #:", user_integer)
        except ValueError:
            print("올바른 정수를 입력해주세요.")

    # power supply
    if user_integer <= 0:
        voltage = 0
    elif user_integer > step_num:
        voltage = max_voltage
    else:
        voltage = min_voltage + (user_integer-1)*grad

    ComPort.write(f"VSET05:{voltage}\r\n".encode())


time.sleep(0.5)

print("==================================")
print("==============STEP 3==============")
print("=========Random Stimulus==========")
print("=========Quit -> enter 'q'========")
ComPort.write(f"VSET05:{0}\r\n".encode())

with open(csv_file_path, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['User Perception Range:', min_voltage, 'to', max_voltage, 'V'])
    csv_writer.writerow(['Step num:', step_num])
    csv_writer.writerow(['Time', 'Step #', 'User answer'])

    while True:
        random_int = random.randint(0, step_num)
        # power supply
        if random_int <= 0:
            voltage = 0
        else:
            voltage = min_voltage + (random_int-1)*grad
        ComPort.write(f"VSET05:{voltage}\r\n".encode())

        # user answer
        user_ans = input(f">> Step num 입력하세요(0~{step_num}): ")
        
        if user_ans.lower() == "q": # Quit
            break

        csv_writer.writerow([datetime.now(), random_int, int(user_ans)])


print("프로그램을 종료합니다")

ComPort.write(f"ISET05:{0}\r\n".encode())
ComPort.write(f"VSET05:{0}\r\n".encode())

csv_file.close()

sys.close()
