# rotorhazard-obs
Tools and Scripts for Live Streaming FPV Races Using RotorHazard and OBS.

These scripts require the RotorHazard timing system - more information is available at http://rotorhazard.com/.

The current file is a basic Python script that queries the JSON API provided by RotorHazard and begins populating a scene with assets based on the current heat. OBS is not talking directly to RotorHazard at this stage, but merely passively pulls data from the JSON API. Eventually the goal will be to use the WebSockets APIs of both RotorHazard and OBS, but the RotorHazard WebSockets API is a moving target at this point.

This script is designed for more complicated race scenarios (say having 4 pilots flying at a time but using all 6 IMD6 channels) - if all you are doing is having 4 pilots up at a time and everyone is using the same frequencies this is probably overkill for you. However, there will be some more advanced features added on in the future.

# Instructions for Use
This script (currently) requires a certain setup in OBS.

*Scene Setup*
* This script requires a scene called "RaceView" that will contain the views for each race. This is the scene that the script will use to display the various pilots.

* There must be two sets of sources:
    * Each Pilot station must have a *browser* source named "Pilot1", "Pilot2", up to the number of pilots you will be racing consecutively.
    * Each video receiver must have its own source as well, nameb "VRX1," "VRX2," etc. These sources can be anything - if you are using a USB-OTG device they can be video devices sources, streams, etc. They can also be placeholders like images or text sources.
    * These sources can be grouped or arranged however you want.

* The script does not change the arrangement of sources, so it is up to you to design the view for your race as you want.

Currently, the script sets everything up when you switch to the RaceView scene - so between races you want to switch to a different scene (say a race results summary), then switch to your next heat on RotorHazard, then switch back to RaceView when the next heat is ready.

This is basically a proof of concept at this point, and it may break things or cause OBS to crash.