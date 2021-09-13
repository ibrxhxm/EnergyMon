#!/usr/bin/env python

import serial
import logging
import thingspeak
import configparser
import requests

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600
config = configparser.ConfigParser()
config.read("config.properties")

WRITE_API_KEY = config.get("THINGSPEAK", "write_api")
CHANNEL_ID = config.get("THINGSPEAK", "channel_id")
channel = thingspeak.Channel(CHANNEL_ID, WRITE_API_KEY)
headers = {"Content-type": "application/json"}
url = "http://192.168.0.197:9090/fyp/emon"


def readSerial(ser):
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('ascii').rstrip()

            if line.startswith("error"):
                logging.warning("Fatal error occured")

            else:
                [rmsCurrent, rmsVoltage, realPower, apparentPower, powerFactor] = line.split("|")

                if not isValidSensorData(float(realPower)):
                    writeToThingspeak()
                else:
                    writeToThingspeak(rmsCurrent, rmsVoltage, realPower, apparentPower, powerFactor)

                    payload = {
                        "data": {
                            "rms_voltage": rmsVoltage,
                            "rms_current": rmsCurrent,
                            "apparent_power": apparentPower,
                            "real_power": realPower,
                            "power_factor": powerFactor
                        }
                    }
                    response = requests.post(url, json=payload, headers=headers)
                    response.raise_for_status()

    except requests.exceptions.HTTPError as errh:
        logging.warning(errh)
    except requests.exceptions.ConnectionError as errc:
        logging.warning(errc)
    except requests.exceptions.Timeout as errt:
        logging.warning(errt)
    except requests.exceptions.RequestException as err:
        logging.warning(err)
    except:
        logging.warning("Connection failed")


def writeToThingspeak(rmsC=0.00, rmsV=0.00, P=0.00, Q=0.00, PF=0.00):
    channel.update({"field1": rmsV, "field2": rmsC, "field3": P, "field4": Q, "field5": PF})

    print("Vrms: {}\tIrms: {}\tReal Power: {}\tApparent Power: {}\tPower Factor: {}\n".format(rmsV, rmsC, P, Q, PF))


def isValidSensorData(value):
    if value < 0.0:
        return False

    return True


if __name__ == '__main__':
    print("Starting program")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    ser.flush()
    logging.basicConfig(filename='app.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

    while True:
        readSerial(ser)
