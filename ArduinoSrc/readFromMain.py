import serial
import serial.tools.list_ports
import time

#print all devices connected
current_connected_ports = serial.tools.list_ports.comports()
for connected_port in current_connected_ports:
    print(f"Device: {connected_port.device} \t Description: {connected_port.description}" )
# end printing all devices

#ask user to select device
print("Enter below your arduino device to connect:\n")
selected_device = input()
# end user selection

# serial port below maybe custom!
sendMaster = serial.Serial(port=selected_device, baudrate=9600, timeout=1)
time.sleep(2)  # Wait for the connection to establish

def send_data(data):
    # Send data to the Arduino over the serial port
    sendMaster.write(data.encode())

try:
    while True:
        # Send '1' to turn the LED on
        send_data('1')
        print("Sent: 1 (LED ON)")
        time.sleep(2)  # Wait for 2 seconds

        # Send '0' to turn the LED off
        send_data('0')
        print("Sent: 0 (LED OFF)")
        time.sleep(2)  # Wait for 2 seconds

except KeyboardInterrupt:
    # Clean up and close the serial connection
    sendMaster.close()
    print("Serial connection closed.")