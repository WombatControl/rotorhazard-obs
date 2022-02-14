# rotorhazard-obs
Tools and Scripts for Live Streaming FPV Races Using RotorHazard and OBS.

These scripts require the RotorHazard timing system - more information is available at http://rotorhazard.com/.

The current file is a basic Python script that queries the JSON API provided by RotorHazard and begins populating a scene with assets based on the current heat. OBS is not talking directly to RotorHazard at this stage, but merely passively pulls data from the JSON API. Eventually the goal will be to use the WebSockets APIs of both RotorHazard and OBS, but the RotorHazard WebSockets API is a moving target at this point.
