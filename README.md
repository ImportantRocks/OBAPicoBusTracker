# OBAPicoBusTracker
One Bus Away Seattle city bus tracker built on a Raspberry Pi Pico 2W 


To use this script, you need to have a One Bus Away API key.
Make sure to set up a file called secrets.py that is saved to the Pico W that has the following three lines -

- SSID = "Your internet SSID"
- PASSWORD = "Your internet password"
- APIKey = "Your One Bus Away API key"


There are a few known issues -
- I first tried this with a Pico W, but ran into memory issues when I would use bus stops with many different bus lines (like any bus stop downtown on 3rd Ave.)
  I have switched to using a Pico 2 W and that seems to be able to handle the downtown bus stops just fine. 

- There needs to be better handling of OS errors in general 

- There needs to be better handling of internet connection issues (each loop needs to check/break on the state of the internet connection

There are further set up instructions in the comments of the script :)
