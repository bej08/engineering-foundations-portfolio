# engineering-foundations-portfolio
## Benjamin Momoh OT Environment Monitor

### Table of Contents
* Overview
* Steps
* Disgnostics
* Resources
* Update Log
* Time
* Use of Contingencies
* Predicting Pintch Points 
* Strategies for TimeScale Recovery 



### Overview
This document contains the overview of my project plan covering all aspects of my project, from conception to the final deliverable. This document should provide insight into potential bottlenecks and help guide me to fulfilling the project specification. This project doubles as a demonstration of project my planning skills: resourcing, scheduling, contingency planning, and risk management.


### Steps

copnfirming theboard and drivers work


### Diagnostics

When building project, the plan ive immplemented to follow when there is a probelem implementing hardware/ building the the physsical projhect ois 

        1  Double checking correct placement of modules and their correspondiong wires are correct. Also check correct libraries for code sketch have been downloaded and software setting are correct.
        1. isolate and Checking wire contineieety of wires with multimeter 
        2. Isolate and Check continuety of module that youre trying to immplement   
           1. if modles is conducting electricity then isolate module and wire code for new sktech specifically checking the fuctionality of the module youre trying to immplement 

At this point, you should be able to pinpoiint the porblem at hand and have a solution. 



### Resources

- **Hardware:** Elegoo Mega2560 starter kit (Arduino Mega2560 board, breadboard, jumper wires, DHT11 temperature/humidity module, photoresistor, LCD1602 display, DS1307 clock module, resistors).
- **Software:** KiCad, Arduino IDE, , SimpleDHT library, LiquidCrystal library, RTClib library (all free, installed via the IDE's Library Manager).
- **Skills:** Existing familiarity with breadboarding and basic C-like syntax from earlier Arduino projects; new skill being developed is reading library documentation and adapting example sketches to a combined multi-sensor project.
- **Time budget:** No fixed daily allocation Evenings/weekends around work and  commitments, .

Initially, i thought it might be wise to make my own PCB design for this project as its soemthing i havent explaored yet and woudl really like to implement. I decided against this to save time drawing up sketces, submitting and ewaiting for the PCB to be delivered. 

Instead i decided to go down the breadbaord avenue using an electronics starter kit form amazpon to save money and time.


How will this scale in the real world ??

An inductry application of this would probabaly rely on  ___
LINK 


### Update Log

### Time
1. IDE setup and blink test
2.  Wire and code DHT11 (temp + humidity)
3. Add photoresistor (light level)
4. Combine sensors onto LCD1602 display
5. Add DS1307 RTC for timestamped readings
6. Tidy wiring, write documentation
7. Control theory (relay/L293D fan control) 


### Use of Contingencies
- **Component risk:** All core-build sensors were already in hand, so there was no ordering/shipping contingency to plan for there. The control loop integration did include a component failure (the relay module — see Update Log), which is a real-world application of the contingency planning being put into practice rather than just theory.
- **Time contingency:** Each phase above includes leway for debugging. or wiring mistakes will most likely be the reason for delay.
- **Fallback contingency:** Each smodule is brought up and tested individually via the Serial Monitor before being combined with the others. If the combined build runs into conflicts, the individually working sketches will be a working fallback to demonstrate use.


### Predicting Pinch Points

I expect the following pinch points of this project to be:

- **Component reliability:**



### Strategies for Timescale Recovery


