# Protect your IT services against multi-vector DDoS threats on-premise with Arbor APS

Source: https://www.xantaro.net/en-gb/xpert-blog/protect-your-it-services-with-arbors-aps
Author: Xantaro Security Team
Date: 26/06/2018

## Key Technical Details

### Arbor Availability Protection System (APS)
- Dedicated, on-premise inline device
- Continuous monitoring of in- and outbound traffic at the WAN edge
- Detects and mitigates complex, state-exhausting and application-layer DDoS attacks
- Fed with newest threats via ATLAS Intelligence Feed (AIF)
- Prevents powerful botnet-based DDoS attacks, advanced threats and volumetric attacks up to line speed
- Combined with Arbor Cloud → automatic protection against terabit-range volumetric attacks
- Provides extensive visibility with detailed attack analyses and reports

### Cloud Signalling
- Volumetric DDoS attack traffic that would overwhelm on-premise protection is automatically detected
- Rerouted to upstream DDoS scrubbing facility (Arbor Cloud)
- APS deployed as first line of defence
- Traditional firewall serves its purpose behind APS

### ATLAS Intelligence
- Advanced Threat Level Analysis System (ATLAS)
- Global information base analyzing ~1/3 of all Internet traffic
- 330+ service providers and enterprises contribute anonymous traffic information
- ATLAS Intelligence Feed (AIF) provides updated policies and countermeasures
- ASERT team (Security Engineering & Response Team) continuously analyzes and updates

### Hardware Specifications

#### APS 2600 and APS 2800 Appliances
- Form factor: 2 rack units (2U)
- APS 2600: licensed 100 Mbps - 20 Gbps
- APS 2800: licensed 10 Gbps - 40 Gbps
- Both can be equipped with optional SSL decryption cards
- Deployed between WAN and firewalls
- "Out-of-the-box" protection with fine-grained controls

#### vAPS (Virtual APS)
- Deployed on KVM and VMware hypervisors
- Supports Cloud-Init or OpenStack as VNF orchestrator
- Mitigation capacities: sub 20 Mbps to 1 Gbps

### Deployment Architecture
- APS inline between WAN router and firewall
- Cloud signalling: when on-prem capacity exceeded → auto reroute to Arbor Cloud scrubbing center
- Clean traffic returned via GRE/IPIP tunnel
- Integration with existing network infrastructure

### Key Specs Summary
| Feature | APS 2600 | APS 2800 | vAPS |
|---------|----------|----------|------|
| Form Factor | 2U Appliance | 2U Appliance | Virtual (KVM/VMware) |
| License Range | 100 Mbps - 20 Gbps | 10 Gbps - 40 Gbps | sub 20 Mbps - 1 Gbps |
| SSL Card | Optional | Optional | N/A |
| Deployment | Inline/Bridge/Routed | Inline/Bridge/Routed | Virtual inline |
