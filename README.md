# OBAPicoBusTracker
One Bus Away Seattle city bus tracker built on a Raspberry Pi Pico W 


To use this script, you need to have a One Bus Away API key.
Make sure to set up a file called secrets.py that is saved to the Pico W that has the following three lines -

- SSID = "Your internet SSID"
- PASSWORD = "Your internet password"
- APIKey = "Your One Bus Away API key"


There are a few known issues -
- The biggest issue at the moment is memory allocation from large JSON get requests. Bus stops with many lines running at once (like
most stops through 3rd ave) will create a JSON file that is too large for the Pico to handle. :( 

- There needs to be better handling of OS errors in general 

- There needs to be better handling of internet connection issues (each loop needs to check/break on the state of the internet connection

There are further set up instructions in the comments of the script :)
