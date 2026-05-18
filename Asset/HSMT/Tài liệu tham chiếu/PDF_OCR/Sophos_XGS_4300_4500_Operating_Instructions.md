Operating Instructions
XGS 4300/4500


---

2
XGS 4300/4500
Operating Instructions
Foreword
We are pleased to welcome you as a new customer of our Sophos XGS appliances.
To install and configure the hardware appliance you can use the following documents:
	Ì Hardware Quick Start Guide: Connection to the system peripherals in a few steps
	Ì Operating Instructions: Notes on the security and 
commissioning of the hardware appliance
	Ì Sophos Firewall How-To Library: Installing and configuring the software appliance
The Hardware Quick Start Guide and the Safety Instructions are also delivered in printed 
form together with the hardware appliance. The instructions must be read carefully prior to 
using the hardware and should be kept in a safe place.
You may download all user manuals and additional documentation from the support 
webpage at: sophos.com/support
Security Symbols
The following symbol and its meaning appears in the Hardware Quick Start Guide, Safety 
Instructions and in these Operating Instructions.
Caution and Important note. If these notes are not correctly observed:
	Ì This is dangerous to life and the environment
	Ì The appliance may be damaged
	Ì The functions of the appliance will be no longer guaranteed
	Ì Sophos shall not be liable for damages arising from a 
failure to comply with the Safety Instructions
Designed Use
The hardware appliances are developed for use in networks. XGS 4300/4500 models 
may be operated as a standalone appliance. The hardware appliance can be used in 
commercial, industrial and residential environments.
The XGS 4300/4500 models belong to the appliance group A.
The hardware appliance must be installed pursuant to the current installation notes. 
Otherwise failure-free and safe operation cannot be guaranteed. The EU declaration of 
conformity is available at the following address:
Sophos Technology GmbH
Gustav-Stresemann-Ring 1
65189 Wiesbaden
Germany


---

3
XGS 4300/4500
Operating Instructions
CE Labeling, FCC and Approvals
The XGS 4300/4500 appliances comply with CB, CE, UL, FCC, ISED, VCCI, CCC, KC, BSMI, 
RCM, NOM, Anatel.
Important note: For computer systems to remain CE and FCC compliant, only CE and FCC 
compliant parts may be used. Maintaining CE and FCC compliance also requires proper 
cable and cabling techniques.
Operating Elements and Connections
XGS 4300/4500*
Multi-function 
LCD display 
and navigation
2 x expansion 
bay (shown with 
optional modules)
LAN 1–4: 4 x GbE copper 
– 2 bypass pairs (ports 
1/2 and 3/4)
F1–F4 4 x SFP+ 
fiber ports
LAN 5–8: 4 x 2.5 
GbE copper
COM: Micro USB, RJ45, 
2 x USB 3.0, MGMT port
XGS 4300
Power supply
Mounting pins for external 
power supply
Connector for external 
redundant power supply 
(available as an option)
Power switch
XGS 4500
Hot swappable 
power supply
Slot for internal 
redundant power supply 
(available as an option)
Power switch
* The displayed front image is of XGS 4500 device. The XG 4300 device may vary slightly.


---

4
XGS 4300/4500
Operating Instructions
Interfaces (front)
LAN Ports
Type
Speed
Comment
1–4
RJ45
10/100/1000 Mbps
Ports 1/2 and 3/4 can be configured 
as independent bypass pairs.
5–8
RJ45
100/1000/2500 
Mbps
F1–F4
SFP+
1/10 Gbps
Other Ports
Type
Comment
COM
RJ45/Micro USB
You can connect a serial console to either the RJ45 or 
micro USB COM port to access the CLI. Only one port 
can be used at any time. If both ports are connected 
then the micro USB port will take precedence.
The required connection settings are:
	Ì Bits per second: 38,400
	Ì 	Data bits: 8
	Ì Parity: N (none)
	Ì Stop bits: 1
USB
USB 3.0 (Type A)
You can connect a USB 2.0 or 3.0 compatible device to 
this port (e.g. USB thumb drive, UPS, 3G/4G dongles).
MGMT
RJ45 (10/100/1000 Mbps)
We recommend using this dedicated 
port to connect your Admin PC.
Reset
Button [back]
Press and hold for >10 seconds to reset the unit 
to factory default settings. All configuration, 
reports and patters will be flushed.
Module Slots
Type
Comment
A/B
Flexi Port
Can be used for any Flexi Port module 
listed in the table below
Compatible Modules*
Comment
8 port GbE copper
Flexi Port
8 port GbE SFP
Flexi Port
4 port GbE copper – 2 Bypass groups
Flexi Port
4 port 10 GbE SFP+
Flexi Port
4 port 2.5 GbE copper PoE
Flexi Port
4 port GbE copper PoE + 4 port GbE copper
Flexi Port
2 port GbE fiber (LC) Bypass + 4 port GbE SFP
Flexi Port
* SFP/SFP+/QSFP transceivers are sold separately.


---

5
XGS 4300/4500
Operating Instructions
Technical Specifications
XGS 4300
XGS 4500
Physical Specification
#Fixed Ethernet Ports
12
12
#Fixed ByPass Port Pairs
2
2
max. #Flexi Ports
16
16
#Cores Main CPU
 6/12
 8/16
Main Memory
32 GB DDR4 EDD 2666
32 GB DDR4 EDD 2666
#Cores NPU
18
18
NPU Memory
8 GB DDR4 ECC
8 GB DDR4 ECC
Stoarge
1 x 240 GB
2 x 240 GB WS-RAID-1
Power Supply
Internal auto-ranging AC-DC 
100-240VAC, 3.7–7.4A@50-60 Hz 
External Redundant PSU Option
Internal Hot Swappable auto-
ranging AC-DC 
100-240VAC, 3.7–7.4A@50-60 Hz 
Internal Redundant PSU Option
Power Consumption (idle)
131 W/447.43 BTU/hr
151 W/515.74 BTU/hr
Power Consumption (full load)
268.35 W/916.56 BTU/hr
268.35 W/916.56 BTU/hr
PoE addition enabled
152 W/519 BTU/hr
152 W/519 BTU/hr
Mounting
Rackmount (1U sliding rails option)
min. rack depth: 603 mm (23.74”)
max. rack depth: 930 mm (36.61”)
 Rackmount (1U sliding rails option)
min. rack depth: 603 mm (23.74”)
max. rack depth: 930 mm (36.61”)
Dimensions
Width x Depth x Height
438 x 510 x 44 mm
17.24 x 20.08 x 1.73 inches
438 x 510 x 44 mm
17.24 x 20.08 x 1.73 inches
Weight (kg) unpacked/packed
8.7 kg/19.18 lbs (unpacked)
14.9 kg/32.85 lbs (packed)
9.7 kg/21.38 lbs (unpacked)
15.9 kg/35.05 lbs (packed)
Environmental
Noise level (avg.) 
(Typical/Max Operation)
54/65 dBA
54/65 dBA
Operating Temperature
0°C to 40°C
0°C to 40°C
Storage Temperature
-20°C to 70°C
-20°C to 70°C
Opertional/Storage Humidity
10% to 90% non-condensing
10% to 90% non-condensing
Altitude
2000m
2000m
MTBF (hours)
(Telcordia SR-332 Issue 3)
126,297
130,415
Certifications (Safety, EMC)
CB, CE, UL, FCC, ISED, VCCI, CCC, 
KC, BSMI, RCM, NOM, Anatel
CB, CE, UL, FCC, ISED, VCCI, CCC, 
KC, BSMI, RCM, NOM, Anatel


---

6
XGS 4300/4500
Operating Instructions
LED Status
Status LEDs
Power 1
Green
Solid
Power Supply 1 Active.
Red
Solid
Power Supply 1 Failure.
Power 2
Green
Solid
Power Supply 2 Active.
Red
Solid
Power Supply 2 Failure.
SSD
Blue
Flashing
SSD reading/writing data.
BP 1/2
Green
Solid
Bypass mode on Ports 1/2 enabled.
Off
Bypass mode on Ports 1/2 disabled and inactive.
BP 3/4
Green
Solid
Bypass mode on Ports 3/4 enabled.
Off
Bypass mode on Ports 3/4 disabled and inactive.
LEDs on each RJ45 Ethernet connector
ACT/LNK 
(Left LED)
Green
Solid
1.	The Ethernet port has established link.
2.	Good connection between the Ethernet port and hub.
Flashing
The adapter is sending or receiving network data.
Off 
1.	The adapter and switch are not receiving power.
2.	No connection between both ends of network.
3.	Network drivers have not been loaded 
or do not function correctly.
Speed 
(Right LED)
1 GbE ports
Amber
On 
If Ethernet port is operating at 1000 Mbps.
Green
On 
If Ethernet port is operating at 100 Mbps.
Off
If Ethernet port is operating at 10 Mbps.
Speed 
(Right LED)
2.5 GbE ports
Amber
On 
If Ethernet port is operating at 2500 Mbps.
Green
On 
If Ethernet port is operating at 1000 Mbps.
Off
If Ethernet port is operating at 100 Mbps.
LEDs on each SFP connector
ACT/LNK
Green
Solid
1.	The SFP connector is receiving power.
2.	Good connection between the SFP port and hub.
Flashing
The adapter is sending or receiving network data.
Off 
1.	The adapter and switch are not receiving power.
2.	No connection between both ends of network.
3.	Network drivers have not been loaded 
or do not function correctly.
LEDs on each SFP+ connector
ACT/LNK
Green
Solid
1.	The SFP+ connector is receiving power.
2.	Good connection between the SFP+ port and hub.
Flashing
The adapter is sending or receiving network data.
Off 
1.	The adapter and switch are not receiving power.
2.	No connection between both ends of network.
3.	Network drivers have not been loaded 
or do not function correctly.
Speed
Blue
On 
If SFP+ connector is operating at 10,000 Mbps.
Amber
On 
If SFP+ connector is operating at 1,000 Mbps.
Off
Either the LED is not working or the SFP+ connector 
is operating at a speed below 1,000 Mbps.
Back side
Power Supply
[XGS 4500 only]
Green
Solid
Power
Off
No power
LCD and Control Keys
The XGS 4300/4500 have an LCD and an operating unit with four membrane keys. In the 
LCD, 16 characters per line can be displayed.
While the security appliance is booting this message is displayed
Firmware Version
SOPHOS
Protection
Firmware Version
SFOS xx.xx.xx


---

7
XGS 4300/4500
Operating Instructions
LCD Menu Details
Firmware Version SFOS xx.xx.xx
Main Menu
1. System Menu
System Menu
1. Show Date
Fri 16 Apr 2021
12:54:32 GMT
Port A1[LAN]
System Menu
2. Show Uptime
System uptime
0 days 0:26
System Menu
3. Show CPU
CPU Usage
0.00%
System Menu
4. Show Memory
Memory Usage
Used: 7.60%
System Menu
5. Show LoadAvg
Load Average
0.89 0.89 0.78
System Menu
6. Show Disk
Show Disk
1. Total Usage
Total Disk Usage
0.02
Show Disk
1. Detail Usage
Root 1%
Temp 0%
Config 9%
Signature 1%
System Menu
7. Live Users
Live Users
0
Main Menu
2. Network Menu
Network Menu
1. Show Port A1[LAN]
Port A1[LAN]
172.16.16.16
Network Menu
2. Show Port A2[WAN]
Port A2[WAN]
IP NOT ASSIGN
Network Menu
3. Show Port A3[NA]
Port A3[NA]
IP NOT ASSIGN
Network Menu
4. Show All
Port A4[LAN]
172.16.16.16
PortA5[WAN]
IP NOT ASSIGN
Port A6[NA]
IP NOT ASSIGN
Port A7[NA]
IP NOT ASSIGN
Port A8[NA]
IP NOT ASSIGN
Port A9[NA]
IP NOT ASSIGN
Network Menu
5. Show Gateway
GW1: PortA2
10.0.0.254
Main Menu
3. Firmware Menu
Network Menu
1. Show Firmware
FW1=SFOS
15.01.0 Beta
Network Menu
2. Factory Reset
Factory Reset
1. v to Cont.
Factory Reset
2. Confirm
Network Menu
3. Shutdown 
Shutdown
1. v to Cont.
Shutdown
1. Confirm
Network Menu
4. Reboot
Reboot
1. v to Cont.
Reboot
1. Confirm
Main Menu
4. HA Info
Not Configured


---

8
XGS 4300/4500
Operating Instructions
Executable Actions
	Ì Factory reset: All settings are reset to the factory settings. The factory reset 
function sets all of the configuration settings and options to their original state. All 
data entered after the initial installation will be deleted, including the HTTP proxy 
cache, the entire email queue, accounting and reporting data, passwords, and 
uninstalled Up2Date packages. The version of the software will not change. That 
is, all firmware and pattern updates that have been installed will be retained.
	Ì Shut down: The security appliance is shut down. The shut down action allows 
you to turn off the system, and allows you to cleanly stop all running services.
	Ì Reboot machine: The security appliance is rebooted. The reboot 
action will shut down the system completely and reboot.
Control Key Functions
The current menu is left. When the key is pressed a couple of times, the modifications are 
discarded and the initial state will be displayed.
These keys are used to switch between the different menus and/or characters.
Pressing executes the configured action.
Factory Reset
S.NO.
Action Item/press
What you see on the LCD
What it means
1.
SOPHOS
Protection
Appliance is booting
2.
 
Firmware Version
SFOS xx.xx.xx
Appliance has finished Booting
3.
ENTER
Main Menu
1. System Menu
Shows Main Menu first item
4.
  x2
Main Menu
3. Firmware Menu
Shows Main Menu Third item
5.
ENTER
Firmware Menu
1. Show Firmware
Enters Into Firmware Menu
6.
Firmware Menu
2. Factory Reset
Shows Firmware Menu Second item
7.
ENTER
Factory Reset
1. v to Cont.
Press down key to continue
8.
Factory Reset
2. Confirm?
Asks for Confirmation
9.
ENTER
Factory Reset under progress
10.
Firmware Version
SFOS xx.xx.xx
Factory Reset Complete
Esc
ENTER


---

9
XGS 4300/4500
Operating Instructions
Shut Down
S.NO.
Action Item/press
What you see on the LCD
What it means
1.
SOPHOS
Protection
Appliance is booting
2.
 
Firmware Version
SFOS xx.xx.xx
Appliance has finished Booting
3.
ENTER
Main Menu
1. System Menu
Shows Main Menu first item
4.
 x2
Main Menu
3. Firmware Menu
Shows Main Menu Third item
5.
ENTER
Firmware Menu
1. Show Firmware
Enters Into Firmware Menu
6.
 x2
Firmware Menu
3. Shutdown
Shows Firmware Menu Third item
7.
ENTER
Factory Reset
1. v to Cont.
Press down key to continue
8.
Factory Reset
1. Confirm?
Asks for Confirmation
9.
ENTER
Shutdown Complete
Reboot Machine
S.NO.
Action Item/press
What you see on the LCD
What it means
1.
SOPHOS
Protection
Appliance is booting
2.
 
Firmware Version
SFOS 18.xx.xx
Appliance has finished Booting
3.
ENTER
Main Menu
1. System Menu
Shows Main Menu first item
4.
 x2
Main Menu
3. Firmware Menu
Shows Main Menu Third item
5.
ENTER
Firmware Menu
1. Show Firmware
Enters Into Firmware Menu
6.
 x3
Firmware Menu
4. Reboot
Shows Firmware Menu Fourth item
7.
ENTER
Factory Reset
1. v to Cont.
Press down key to continue
8.
Factory Reset
1. Confirm?
Asks for Confirmation
9.
ENTER
Reboot under progress
10.
Firmware Version
SFOS xx.xx.xx
Reboot Complete


---

10
XGS 4300/4500
Operating Instructions
Putting into Operation
Caution: Risk of explosion if battery is replaced by an incorrect type. Dispose of used 
batteries according to the instructions.
Scope of Supply
The supplied parts are indicated in the Hardware Quick Start Guide.
Mounting Instructions
The XGS 4300/4500 appliances are designed for use in racks. Please consider the 
following security tips:
Important note: Functional reliability outside of a rack cannot be guaranteed.
Warnings and Precautions
The appliance can be operated safely if you observe the following notes and the notes on 
the appliance itself.
Rack Precautions
	Ì Ensure that the leveling jacks on the bottom of the rack are fully extended 
to the floor with the full weight of the rack resting on them.
	Ì In single rack installation, stabilizers should be attached to the rack.
	Ì In multiple rack installations, the racks should be coupled together.
	Ì Always make sure the rack is stable before extending a component from the rack.
	Ì You should extend only one component at a time—extending two or 
more simultaneously may cause the rack to become unstable.
General Server Precautions
	Ì Installation must be performed by qualified personnel
	Ì Review the electrical and general safety precautions that came 
with the components you are adding to your appliance.
	Ì Determine the placement of each component in the rack before you install the rails.
	Ì Install the heaviest server components on the bottom of the rack first, and then work up.
	Ì Allow the hot plug power supply modules to cool before touching them.
	Ì Always keep the rack‘s front door, all panels and server components 
closed when not servicing to maintain proper cooling.


---

11
XGS 4300/4500
Operating Instructions
Rack Mounting Considerations
	Ì Ambient operating temperature: If installed in a closed or multi-unit rack assembly, 
the ambient operating temperature of the rack environment may be greater than the 
ambient temperature of the room. Therefore, you should install the equipment in an 
environment compatible with the manufacturer’s maximum rated ambient temperature.
	Ì Reduced airflow: Equipment should be mounted into a 
rack with sufficient airflow to allow cooling.
	Ì Mechanical loading: Equipment should be mounted into a rack so that a 
hazardous condition does not arise due to uneven mechanical loading.
	Ì Circuit overloading: Consideration should be given to the connection of the equipment 
to the power supply circuitry and the effect that any possible overloading of circuits 
might have on overcurrent protection and power supply wiring. Appropriate consideration 
of equipment nameplate ratings should be used when addressing this concern.
	Ì Reliable ground: Reliable grounding must be maintained at all times. To ensure 
this, the rack itself should be grounded. Grounding screws for the appliance 
are on the rear of the chassis.  Chassis Grounding is required. Particular 
attention should be given to power supply connections other than the direct 
connections to the branch circuit (i.e., the use of power strips, etc.).
Rack Mounting Instructions
To mount the appliance to the rack you need the delivered rack-mount kits. There are a 
variety of rack units on the market, which may mean the assembly procedure will differ 
slightly. You should also refer to the installation instructions that came with the rack unit 
you are using. Please observe the mounting instructions for your rack.
Important note: Make sure you use the screws supplied with the rack-mount brackets. 
Using the wrong screws could damage the hardware appliance and would invalidate your 
warranty.
1.	Attach the rack-mount ears to the appliance:
	Ì Place the appliance on a hard flat surface with the front panel facing you.
Use the short mounting brackets with the sliding rails supplied with your appliance.
	Ì Attach the rack–mount brackets to the left and right side 
of the appliance with the supplied screws.
	Ì Make sure the brackets are properly attached to the appliance.


---

12
XGS 4300/4500
Operating Instructions
Important note: Please check the technical specs above for the min. and max. rack depth.
2.	Choose the rack location:
	Ì Leave enough clearance in front of the rack so that you can 
open the front door completely (~60 cm/25 inches).
	Ì Leave approximately 80 cm/30 inches of clearance in the back of 
the rack to allow for sufficient airflow and ease in servicing.
	Ì This product is for installation only in a restricted access location 
(dedicated equipment rooms, service closets and the like).
3.	Install the sliding rails:
	Ì Please refer to the dedicated Sliding Rails Mounting 
Instructions shipped with the appliance.
4.	In order to prevent the unit from unintentionally sliding out of the rack we 
strongly recommend fixing the rack-mount brackets to the front rack-
mount posts by using screws and nuts supplied with your rack.
Connection and Configuration
How to connect the appliance is described in the Hardware Quick Start Guide. For 
configuration you can follow the initial setup wizard described in the WebAdmin Quick Start 
Guide or cancel it and perform a manual setup (see the Sophos Firewall How-To Library).
SFP/SFP+ Ports
The XGS 4300/4500 models offer a variety of SFP/SFP+ ports allowing you to plugin 
various GBICs (transceivers) to connect to fiber or copper networks. The abbreviation SFP 
GBIC stands for small form-factore plugable GigaBit interface converter, a flexible interface 
which changes electronic signals into optical signals. The converters used with the 
appliance are often also called Mini-GBIC or New GBIC.
To use SFP/SFP+ ports, you will need the appropriate transceivers or DAC cables 
(combining transceivers and cables into one). These are not delivered with the appliance 
but available through your Sophos partner. There are different module types, and the 
required type is determined by the existing network.
Note: The SFP+ ports of the Sophos FleXi Port modules are dual-rate capable supporting 
both 1GbE and 10GbE speeds when using appropriate GBICs also supporting both rates.
Caution: The SFP and SFP+ ports use lasers to transmit signals over fiber optic cable. The 
lasers are compliant with the requirements of a Class 1 Laser equipment and are inherently 
eye-safe in normal operation. However, you should never look directly at a transmit 
port when it is powered on. Always install appropriate and UL approved Laser Class I 
Transceivers, rated 3.3Vdc, max. 1W, in the fiber ports before using the fiber ports.


---

13
XGS 4300/4500
Operating Instructions
Installing a SFP/SFP+/QSFP+ module
Please read the operation manual for the module. Carefully insert the module into the port 
until it engages. The interface is immediately ready for use.
Removing a SFP/SFP+ module
1.	Remove the optical cable from the module which you wish to remove.
2.	Remove the module carefully from the port.
Depending on when you purchased your module, it may have any of three different 
release mechanisms: a plastic tab on the bottom of the module, a wire bail, or a plastic 
collar around the module.
Please read the operation manual to the module.
Serial Console
You can connect a serial console to either the RJ45 or micro USB COM port to access the 
CLI. Only one port can be used at any time. If both ports are connected then the micro USB 
port will take precedence. You can use, for instance, the Hyperterminal terminal program 
which is included with most versions of Microsoft Windows to log on to the appliance 
console. If you want to connect to the Micro-USB COM port please use the supplied cable. 
If you want to connect to the RJ45 COM port please use a RJ45 to DB9 Adapter cable (not 
provided with the unit). The Pin-out for this cable is shown in the table below.
Sophos RJ45 Pinout
This pinout is compatible with Cisco Straight (X2) pinout serial cables.
Pin number
Function
Direction
1
RTS
Output
2
DTR
Output
3
TXD
Output
4
Ground
N/A
5
Ground
N/A
6
RXD
Input
7
DSR
Input
8
CTS
Input
The required connection settings are:
	Ì Bits per second: 38,400
	Ì Data bits: 8
	Ì Parity: N (none)
	Ì Stop bits: 1
Access via the serial console is activated by default on ttyS0. The connections of the 
appliances and the respective functionality are listed in chapter ‘Operating Elements and 
Connections.’
Please Note: If you are connecting to the Micro USB port and it doesn’t show up as COM 
port but as unknown hardware in your system, please download a Micro USB Driver from 
https://ftdichip.com/drivers/d2xx-drivers/.


---

Operating Instructions
United Kingdom and Worldwide Sales
Tel: +44 (0)8447 671131
Email: sales@sophos.com
North American Sales
Toll Free: 1-866-866-2802
Email: nasales@sophos.com
Australia and New Zealand Sales
Tel: +61 2 9409 9100
Email: sales@sophos.com.au
Asia Sales
Tel: +65 62244168
Email: salesasia@sophos.com
© Copyright 2025. Sophos Ltd. All rights reserved.
Registered in England and Wales No. 2096520, The Pentagon, Abingdon Science Park, Abingdon, OX14 3YP, UK
Sophos is the registered trademark of Sophos Ltd. All other product and company names mentioned are 
trademarks or registered trademarks of their respective owners.
25-03-05 OI-EN (MP)
