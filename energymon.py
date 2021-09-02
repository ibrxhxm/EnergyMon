import serial
import logging
import thingspeak

WRITE_API_KEY = "2LU9HY698C6K2H4Z" #dummy API KEY :)
CHANNEL_ID = "1494953"
channel = thingspeak.Channel(CHANNEL_ID, WRITE_API_KEY)
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600

def readSerial(ser):
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('ascii').rstrip()
            
            if line.startswith("error"):
                logging.warning("Fatal error occured")
                
            else:
                [rmsCurrent, rmsVoltage, realPower, apparentPower, powerFactor] = line.split("|")
                
                if not isValidSensorData(realPower):
                    writeToThingspeak()
                else:
                    writeToThingspeak(rmsCurrent, rmsVoltage, realPower, apparentPower, powerFactor)
    
    except:
        
        logging.warning("Connection failed")
             
def writeToThingspeak(rmsC = 0.00, rmsV = 0.00, P = 0.00, Q = 0.00, PF = 0.00):
    
    channel.update({"field1": rmsV, "field2": rmsC, "field3": P, "field4": Q, "field5": PF})
    
    print("Vrms: {}\tIrms: {}\tReal Power: {}\tApparent Power: {}\tPower Factor: {}\n".format(rmsV, rmsC, P, Q, PF))
    
    
def isValidSensorData (value):
    if value < 0.0:
        return False
    
    return True
    
    

if __name__ == '__main__':
    
    print("Starting program")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    ser.flush()
    logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    
    while True:
        readSerial(ser)

