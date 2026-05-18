l  DATA SHEET  l
RECOMMENDATIONS
•	 Configure Arbor Sightline for high 
availability by using vSphere HA or similiar 
functionality.
•	 When migrating Arbor Sightline VMs 
leverage VMware’s Vmotion or similiar 
functionality.
•	 Enable NTP (Network Time Protocol) on the 
VM host server
•	 Dedicate a network interface per Arbor 
Sightline VM when possible.
•	 Do not overprovision memory allocation.
Virtual Machine Requirements
Arbor Sightline
Arbor Sightline provides comprehensive network visibility and reporting capabilities to help you 
detect and understand availability threats, and improve traffic engineering, peering relationships 
and service performance. Furthermore, Arbor Sightline has the flexibility to be deployed how 
and where you need it, when you need it.
Benefits of Arbor Sightline Virtual Machine deployments are:
•	 Cost effectively increases visibility at the network edge
•	 Flexibility for changing needs
•	 Scalable deployment as you grow
•	 Choice of form factor (Virtual Machine and/or appliance)
•	 Simple licensing
•	 Rapid deployment within virtualized infrastructure
•	 Powerful high availability and migration functionality leveraging VM tools
Arbor Sightline Resource Requirements for Virtual Machines
Hypervisor
WMware vSphere1
Version 5.0, 5.1, 5.5
KVM QEMU
Version 1.4.2
Xen Cloud Platform
Version 1.6.10-61809c
vCPUs
8 to 32
8 to 32
8 to 15
Network 
Interfaces
1 to 10 network 
interfaces2
1 to 10 network 
interfaces2
1 to 10 network 
interfaces2
Memory
16, 24 or 32GB
16, 24 or 32GB
16, 24 or 32GB
Storage
100GB+
100GB+
100GB+
Note: Consult the product documentation for specific recommendations.
Virtual Machine Sizing by Hypervisor
Hypervisor
VMware
KVM
Xen
vCPU
8
16
32
8
16
32
8
153
Flows Per 
Second
110,000
280,000
300,000
110,000
240,000
300,000
120,000
120,000
1	 Use the default settings except for the following: Network Adapter: E1000; OS: Other Linux 32-bit; Storage: Thick 
Provisioned=Lazy Zeroed.
2	 Arbor recommends no more than 2 VM instances per network interface.
3	 Only up to 15 cores supported on Xen.
SECURITY


---

© 2018 NETSCOUT SYSTEMS, INC. All rights reserved. NETSCOUT, the NETSCOUT logo, Guardians of the Connected World, Adaptive Service Intelligence, Arbor Networks, the Arbor Networks logo, ATLAS, 
Inﬁ niStream, Inﬁ niStreamNG, nGenius, and nGeniusONE are registered trademarks or trademarks of NETSCOUT SYSTEMS, INC., and/or its subsidiaries and/or aﬃ  liates in the USA and/or other countries.
Third-party trademarks mentioned are the property of their respective owners.
NETSCOUT oﬀ ers sales, support, and services in over 32 countries. Global addresses, and international numbers are 
listed on the NETSCOUT website at: www.netscout.com/company/contact-us
Product Support
Toll Free US: 888-357-7667
(International numbers below)
Sales Information
Toll Free US: 800-309-4804
(International numbers below)
Corporate Headquarters
NETSCOUT Systems, Inc.
Westford, MA 01886-4105
Phone: +1 978-614-4000
www.netscout.com
l  DATA SHEET  l  Virtual Machine Requirements
Qualified Platforms
Vendor and Model
Arbor Sightline
Cisco UCS 8200 M3
Dell PowerEdge R720
HP ProLiant DL380p Gen 8
CPU
2x E5-2648L v3 @ 1.8Ghz
2x E5-2609 @ 2.4GHz
2x E5-2620 @ 2GHz
2x E5-2670 @ 2.6GHz
CPU Cores4
24 (2 x 12)
16 (2 x 8)
8 (2 x 4) or 16 (2 x 8)
12 (2 x 6)
RAM
32GB
64GB
16GB or 32GB
64GB
Network Interfaces
4 or 8 x 1GigE;
2 x 10GigE; or
2 x 10GigE and
4 x 1GigE 
4 x 10G SFP+
6 x 1G copper
12 x 1G copper
Storage5
6 x 480GB SSD
8 x 120GB SSD
4 x 480GB SSD
4 x 1TB 7.2K SAS
Chassis (Size)
Single Chassis (2RU)
Half-Width blade.
8 fit into 6RU Cisco UCS 
5108 Blade Server Chassis
Single Chassis (2RU)
Single Chassis (2RU)
Flows Per Second
240,000
Flows per second is dependent upon hypervisor and virtual machine sizing
4	 aa (bb x cc) expresses aa = number of physical CPUs; bb = number of cores per CPU; and cc = total number of CPU cores.
5	 Managed object data can be stored on multiple data storage devices/instances at the same time to provide redundancy.
SECPDS_017_EN-1801  10/2018
