import time
from time import sleep
import network
import secrets
from machine import Pin
import ntptime
import urequests
import ujson
import gc

#This is best working version from 4/23/25

#To use this script, you need to have a One Bus Away API key.
#Make sure to set up a file called secrets.py that is saved to the Pico W that has the following three lines -

#SSID = "Your internet SSID"
#PASSWORD = "Your internet password"
#APIKey = "Your One Bus Away API key"


#There are a few known issues -
#- The biggest issue at the moment is memory allocation from large JSON get requests. Bus stops with many lines running at once (like
#most stops through 3rd ave) will create a JSON file that is too large for the Pico to handle. :( 

#- There needs to be better handling of OS errors in general 

#- There needs to be better handling of internet connection issues (each loop needs to check/break on the state of the internet connection


#Set LED pin variables - each bus line being tracked should have its own LED varaible
busLED0 = Pin(16, Pin.OUT)

#Each bus line tracked should also have a corresponding NearLED for the 
busNearLED0 = Pin(20, Pin.OUT)

internetLED = Pin(14, Pin.OUT)
sundayLED = Pin(15, Pin.OUT)

#Turn off all LEDs by default
busLED0.value(0)
busNearLED0.value(0)
internetLED.value(0)
sundayLED.value(0)

#Increase garbage collection to 5000 (to help avoid OSError: (-29312, 'MBEDTLS_ERR_SSL_CONN_EOF'))
gc.threshold(5000)

sleep(2)


wlan = network.WLAN(network.STA_IF)

def connectToInternet():

    #Connecting to internet using sercrets.py to store WiFi username and password
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.SSID, secrets.PASSWORD)

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        internetLED.toggle()
        #wlan.connect(secrets.SSID, secrets.PASSWORD)
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        max_wait = 10
        print('network connection failed, trying to connect again...')
        resetInternetConnection()
        connectToInternet()
        #raise RuntimeError('network connection failed')
    else:
        #print('connected')
        status = wlan.ifconfig()
        print( 'Connected to ' + secrets.SSID + '. ' + 'Device IP: ' + status[0] )
        internetLED.value(1)
    

        
def resetInternetConnection():
    wlan.disconnect()
    sleep(4)
    connectToInternet()

connectToInternet()

#sleep(10)

ntptime.settime()
print('set ntp time')

def setArrivalLEDs(routeArrivalTime, currentPSTEpochTime, walkingTime, busLED, busNearLED):
    
    #Blink the LED for the bus line that is being requested
    busLED.toggle()
    sleep(.25)
    busLED.toggle()
    sleep(.25)
    busLED.toggle()
    sleep(.25)
    busLED.toggle()
    sleep(.25)
    
    if routeArrivalTime is not None:
        differenceFromCurrentTime = routeArrivalTime - currentPSTEpochTime
        print('difference from current time: ' + str(differenceFromCurrentTime))
        
        if (differenceFromCurrentTime < (600000 + walkingTime)) and (differenceFromCurrentTime > (0 + walkingTime)):
            print('Less than ten minutes including walking distance: ' + str(differenceFromCurrentTime/60000) + ' minutes')
            busLED.value(1)
            if (differenceFromCurrentTime < (300000 + walkingTime)) and (differenceFromCurrentTime > (0 + walkingTime)):
                #Set 5 min LED ON
                busNearLED.value(1)
                #Set bus LED OFF
                busLED.value(0)
                print('Less than 5 minutes including walking distance: ' + str(differenceFromCurrentTime/60000) + ' minutes')
        else:
            print('More than ten minutes away / cant make it including walking distance : ' + str(differenceFromCurrentTime/60000) + ' minutes')
            #Set both LEDs OFF
            busLED.value(0)
            busNearLED.value(0)
    else:
        print('No bus')
        routeArrivalTime = 0


def getPredictedArrivalTime(stopID, routeName):
    
    max_wait = 10
    while max_wait > 0:
        
        requestURL = 'https://api.pugetsound.onebusaway.org/api/where/arrivals-and-departures-for-stop/' + '1_' + str(stopID) + '.json?key=' + secrets.APIKey

        response = urequests.get(requestURL)
        gc.collect()
        
        if response.status_code == 200:
            print(str(routeName) + ' API request success')

            jsonString = response.text
            
            data = ujson.loads(jsonString)
            
            
            #find the length of the arrivalsAndDepartures array and make a for loop based on that number
            stopArrivalsCount = len(data['data']['entry']['arrivalsAndDepartures'])
            jsonDataIndex = 0
            print("Number of results: " + str(stopArrivalsCount))
                
            if stopArrivalsCount != 0:
                while jsonDataIndex < stopArrivalsCount:
                    shortName = data['data']['entry']['arrivalsAndDepartures'][jsonDataIndex]['routeShortName']
                    if shortName == routeName:
                        filteredArrivalTimeData = data['data']['entry']['arrivalsAndDepartures'][jsonDataIndex]['predictedArrivalTime']
                        #Sometimes the predicted arrival time comes back as 0 (maybe becuase it has no prediction?)
                        #If this is the case, use scheduledArrivalTime
                        if filteredArrivalTimeData == 0:
                            filteredArrivalTimeData = data['data']['entry']['arrivalsAndDepartures'][jsonDataIndex]['scheduledArrivalTime']
                        return (filteredArrivalTimeData)
                        jsonDataIndex = 0
                        break
                    else:
                        jsonDataIndex = jsonDataIndex + 1
            else:
                return (0)
        break
    else:
        max_wait -= 1
        print('API request failed :( give me a second - ' + str(response.status_code))
        sleep(2)


#Continual loop
while True:
    
    internetLED.toggle()
    sleep(.5)
    internetLED.toggle()
    sleep(.5)
    internetLED.toggle()
    sleep(.5)
    internetLED.toggle()
    sleep(.5)
    
    #Check if the internet is connected
    if wlan.status() != 3:
        print('Network is no longer connected! trying to connect again...')
        internetLED.value(0)
        
        busLED0.value(0)
        busLED1.value(0)
        busLED2.value(0)
        busLED3.value(0)

        busNearLED0.value(0)
        busNearLED1.value(0)
        busNearLED2.value(0)
        busNearLED3.value(0)
        
        resetInternetConnection()
        break
    else:
        status = wlan.ifconfig()
        print( 'Connected to ' + secrets.SSID + '. ' + 'Device IP: ' + status[0] )
        internetLED.value(1)
    print("")
    
    
    #correct time for PST
    localTimePST = time.localtime(time.time() + (-7 * 3600))
    print(localTimePST)
    
    currentPSTEpochTime = ((time.time()) * 1000)
    print('current PST Epoch Time: ' + str(currentPSTEpochTime))
    



    #Make OBA API requests for predicted arrival time per bus stop
    #Find the ID of the stop you would like to track using the One Bus Away interactive map - https://pugetsound.onebusaway.org/
    #Click on the bus stop and the ID will be labeled as the 'stopcode'

    #ROUTE 7 NORTH
    #busLED0
    #busNearLED0
    #Walking time - 10 min - 600000 milliseconds
    
    #input the stopcode WITHOUT the '1_', and the name/number of the route you would like to track.
    #This example is tracking the 60 bus line running South from the Broadway & E Pine St bus stop in Capitol Hill
    arrivalTimeStop60S = getPredictedArrivalTime(11070, "60")
    print('arrivalTime 7N: ' + str(arrivalTimeStop60S))
    
    #Set LED state based on predicted arrival time (LED on if bus is less than 10 minutes away and more than 3 minutes away
    setArrivalLEDs(arrivalTimeStop60S, currentPSTEpochTime, 600000, busLED0, busNearLED0)
    print("")
    
    #Blink internet LED to indicate that all API calls are completed
    internetLED.toggle()
    sleep(.5)
    internetLED.toggle()
    sleep(.5)
    internetLED.toggle()
    sleep(.5)
    internetLED.toggle()
    sleep(.5)
    
    
    #Sunday section - lights up the green LED if it is sunday
    
    if localTimePST[6] == 6:
        print("It's Sunday!")
        sundayLED.value(1)
    else:
        print("It's not Sunday :(")
        sundayLED.value(0)
    
    print("")
    

    #Slow down API requests to 5 minute intervals in the middle of the night (12am - 6am)
    if localTimePST[3] < 6:
        #Repeat every 5 mintue, end of continual loop
        print("Late night/early morning - slow call time")
        print("")
        sleep(60*5)
    else:
        #Repeat every 1 mintue, end of continual loop
        sleep(60)
