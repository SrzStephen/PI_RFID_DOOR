import os
import time
from signal import SIGINT, signal
import RPi.GPIO as GPIO
import MFRC522
import mysql.connector

login = {
  'user': '',
  'password': '',
  'host': '127.0.0.1',
  'database': 'cards',
}

continue_reading = True
# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print "Ctrl+C captured, stopping MRFC522 device."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal(SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Starting MRFC522 device."
print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected!"

    # Get the UID of the card
    (status, uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        print "Card UID: " + str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3])
        uidstring = str(uid[0]) + str(uid[1]) + str(uid[2]) + str(uid[3])

        try:
            #try to connect and check if it exists
            conn = mysql.connector.connect(**login)
            cursor=conn.cursor()
            cursor.execute("SELECT uidstring FROM uids")
            #No rows returned (card invalid) is caught with ER_SP_FETH_NO_DATA:
            print "Opening door"
            os.system('echo P1-12=20 > /dev/servoblaster')
            time.sleep(5)
            os.system('echo P1-12=130 > /dev/servoblaster')

        except mysql.connector.Error as err:

            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print "Something is wrong with your user name or password"

            elif err.errorno == errorcode.ER_SP_FETCH_NO_DATA:
                print str(uidstring) + " was not found"

            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print "Database does not exist"

            else:
                print(err)

        cursor.close()
        conn.close()