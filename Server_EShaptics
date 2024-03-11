"""
File    : Server_haptic.py
Author  : Sooyeon Kim
Date    : December 01, 2023
Update  : December 18, 2023
        : December 31, 2023 # PT step 추가
Description : Real-time data plotting script for haptic sensor data visualization.
            : 현재 센서 2개(1 channel)의 값을 읽어오지만, 4개(2 channel)까지 확장 가능함
            : Saving data in .csv
            : force calibration은 잠시 대기...
Protocol    :
1. I4에서 open한 channel number 기입(0부터) - 만약, fiber 1개만 사용한 경우 [1, any number]
2. write the min, max voltage range depending on user...
3. Calibration step 후 
4.

Setting for I4 (FBGs-I4 연결) :
Channel 1 - sensor 1는 tip force sensing
Channel 1 - sensor 2는 base force sensing
Channel 2 - sensor 1는 tip force sensing
Channel 2 - sensor 2는 base force sensing
"""

import socket
import struct
import keyboard
import time
import serial
from datetime import datetime
import matplotlib.pyplot as plt
import threading
import csv

### Manually edit
csv_file_path = "C:/Users/222BMG13/Desktop/2312231_sr2.csv"

# Stimulus haptic
step_num = 4
max_voltage = 12.5 ## electrical haptic
min_voltage = 6.5

# I4 interrogator & FBGs range
channel_num = [1, 3] # (I4에서 오픈한 채널) 0~3
FBGs_force_range = 0.6 # 지금은 wavelength

######################################################
###################### SETTING #######################
## Setting for MK-W103
ComPort = serial.Serial('COM2')
ComPort.baudrate = 115200 # set Baud rate to 115200
ComPort.bytesize = 8    # Number of data bits = 8
ComPort.parity   = 'N'  # No parity
ComPort.stopbits = 1    # Number of Stop bits = 1
print("MK-W103 connected")

current = 0.1 # A
ovp = 25 # V
update_period = 0.5 # sec (recommended)

ComPort.write(f"OVP05:{ovp}\r\n".encode())  # Set the OVP voltage value to be ?V
ComPort.write(f"OVP05:ON\r\n".encode())     # Open/close OVP
ComPort.write(f"ISET05:{current}\r\n".encode())

### Setting for TCP/IP communication
PORT = 4578
PACKET_SIZE = 11  # receiving 11 byte data

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", PORT))
server_socket.listen(1) # Listen for incoming connections
print("Server waiting for client connection...")

client_socket, addr = server_socket.accept() # Accept a connection from a client
print(f"Connection from {addr}") 

#input("Press Enter to continue...")

### Data Initialize
received_data = b''  # 빈 바이트 문자열로 초기화
id_val = [[channel_num[0],0,1],[channel_num[1],0,1]] # [Channel, Sensor1, Sensor2]
CHANNEL_2_SENSOR_1_WAVELENGTH = 1549.65
CHANNEL_2_SENSOR_2_WAVELENGTH = 1534.63
CHANNEL_3_SENSOR_1_WAVELENGTH = 1549.65
CHANNEL_3_SENSOR_2_WAVELENGTH = 1534.63

force1=0
force2=0
force3=0
force4=0
voltage_com=0
stimulus_flag=0

######################################################
################ FUNCTION AND THREAD #################
### Thread for TCP communication
def receive_data():
    global received_data
    global id_val
    global force1, force2, force3, force4
    global plot_data1, plot_data2
    while True:
        chunk = client_socket.recv(PACKET_SIZE)
        if not chunk:
            # Client connection failed
            raise ConnectionError("Connection closed unexpectedly")
        received_data = chunk

        if len(received_data) >= PACKET_SIZE:
            id = struct.unpack('BBB', received_data[:3])
            FBGs = struct.unpack('d', received_data[3:])[0]

            if id[0] == id_val[0][0]: # 1st channel
                if id[2] == id_val[0][1]: # 1st sensor
                    force1 = FBGs
                    plot_data1 = FBGs - CHANNEL_2_SENSOR_1_WAVELENGTH
                elif id[2] == id_val[0][2]: # 2nd sensor
                    force2 = FBGs
                    plot_data2 = FBGs - CHANNEL_2_SENSOR_2_WAVELENGTH
            elif id[0] == id_val[1][0]: # 2nd channel
                if id[2] == id_val[1][1]: # 1st sensor
                    force3 = FBGs
                elif id[2] == id_val[1][2]: # 2nd sensor
                    force4 = FBGs


### Thread for data logging
exit_flag = False
def log_data():
    global force1, force2, force3, force4, voltage_com, stimulus_flag
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Time', 'Channel 1', '', 'Channel 2', '','Voltage','User'])
        csv_writer.writerow(['', 'sensor 1', 'sensor 2', 'sensor 1', 'sensor 2'])

        while not exit_flag:
            csv_writer.writerow([datetime.now(), force1, force2, force3, force4, voltage_com, stimulus_flag])
            time.sleep(0.1)
        
        else:
            csv_file.close()

##################################################
### Plot function
def setting_plot():
    global max_data_points, ax1, ax2
    global fig, line11, line12, line21, line22
    global time_data
    global force_data_1, force_data_2, force_data_3, force_data_4
    ### Setting for plotting
    # Lists to store data for plotting
    time_data = []
    force_data_1 = []
    force_data_2 = []
    force_data_3 = []
    force_data_4 = []

    plt.ion()  # Turn on interactive mode

    fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(6, 4))
    # fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(6, 8))

    line11, = ax1.plot(time_data, force_data_1, color='black', label='tip')
    line12, = ax1.plot(time_data, force_data_2, color='blue', label='base')
    ax1.set_xlabel('Time')
    ax1.set_title('FBGs #1')
    ax1.legend(loc='upper left')
    # ax1.set_ylabel('Force [mN]')
    # ax1.set_ylim(-2, 10)
    ax1.set_ylabel('Wavelength [nm]')
    # ax1.set_ylim(-0.2, -0.2 + FBGs_force_range)

    # line21, = ax2.plot(time_data, force_data_3, color='black', label='tip')
    # line22, = ax2.plot(time_data, force_data_4, color='blue', label='base')
    # ax2.set_xlabel('Time')
    # ax2.set_title('FBGs #2')
    # ax2.legend(loc='upper left')
    # ax2.set_ylabel('Force [mN]')
    # ax2.set_ylim(0, 10)

    max_data_points = 80


def plot_data():
    if len(received_data) == PACKET_SIZE:
        # Append data for plotting
        time_data.append(datetime.now())
        force_data_1.append(plot_data1)
        force_data_2.append(plot_data2)
        # force_data_3.append(force3)
        # force_data_4.append(force4)

        # Remove previous data
        if len(time_data) > max_data_points:
            time_data.pop(0)
            force_data_1.pop(0)
            force_data_2.pop(0)
            # force_data_3.pop(0)
            # force_data_4.pop(0)

        # Plot data
        line11.set_xdata(time_data)
        line11.set_ydata(force_data_1)
        line12.set_xdata(time_data)
        line12.set_ydata(force_data_2)
        # line21.set_xdata(time_data)
        # line21.set_ydata(force_data_3)
        # line22.set_xdata(time_data)
        # line22.set_ydata(force_data_4)
        # for ax in [ax1, ax2]:
        #     ax.relim()
        #     ax.autoscale_view()

        ax1.relim()
        ax1.autoscale_view()

        plt.tight_layout()
        plt.draw()
        plt.pause(0.01) # 1ms

### Map function
def mapping(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


######################################################
##################### EXECUTION ######################
time.sleep(0.5)

### Thread
receive_thread = threading.Thread(target=receive_data)
log_thread = threading.Thread(target=log_data)
receive_thread.start()
log_thread.start()

time.sleep(0.5)
setting_plot() # open the plotting window

es_grad = (max_voltage - min_voltage)/(step_num-1)
delta_FBGs = FBGs_force_range / step_num

start_time = time.time()
while True:
    ## Plotting data
    plot_data()
    
    ## Stimulus_flag
    stimulus_flag = 0 # default
    if keyboard.is_pressed('1'):
        stimulus_flag = 1
    elif keyboard.is_pressed('2'):
        stimulus_flag = 2
    elif keyboard.is_pressed('3'):
        stimulus_flag = 3
    elif keyboard.is_pressed('4'):
        stimulus_flag = 4

    ## Voltage controls
    if plot_data1 <= delta_FBGs: # step 0
        voltage = 0
    elif (plot_data1 > 1*delta_FBGs)&(plot_data1 <= 2*delta_FBGs): # step 1
        voltage = min_voltage
    elif (plot_data1 > 2*delta_FBGs)&(plot_data1 <= 3*delta_FBGs): # step 2
        voltage = min_voltage + 1*es_grad
    elif (plot_data1 > 3*delta_FBGs)&(plot_data1 <= 4*delta_FBGs): # step 3
        voltage = min_voltage + 2*es_grad
    else:
        voltage = min_voltage + 3*es_grad

    # print(f"Force: {force1:.2f} mN, Voltage: {voltage:.2f} V")
    # print(f"Wavelength: {plot_data1:.2f} nm, Voltage: {voltage:.2f} V")
    print(f"User: step #{stimulus_flag}")

    if time.time()-start_time > update_period:
        voltage_com = voltage
        ComPort.write(f"VSET05:{voltage_com}\r\n".encode())
        start_time = time.time()

    ## Quit
    if keyboard.is_pressed('esc'):
        print("Exit the loop")
        exit_flag = True
        break


# Close
ComPort.write(f"ISET05:{0}\r\n".encode())
ComPort.write(f"VSET05:{0}\r\n".encode())

client_socket.close()
server_socket.close()
