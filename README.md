## Psy-ARP: MITM Attacks Made Easy


### What is it?

Psy-ARP is a simple but powerful Python script that initiates Man-In-The-Middle attacks through ARP spoofing. It intercepts host-to-host traffic, allowing you to do execute all kinds of interesting exploits, from simple log analysis to credential harvesting, (more on that later) to even intercepting and modifying document requests.

### Where can I use it?

Psy-ARP was designed for host-to-host MITM attacks, meaning that you need to have two vulnerable hosts (or Virtual Machines) interacting with each other. Psy-ARP was NOT designed to spoof connections between a host and a gateway, (for example: A VM and the router) and does not currently possess the ability to perform DNS spoofing.

Also, Psy-ARP targets HTTP traffic, not HTTPS traffic, as the latter is encrypted via TLS. Psy-ARP could still pull off a MITM attack with HTTPS, but it wouldn't be able to read or modify the encrypted payload without additional tools.

### What do I need to use it?

To run Psy-ARP, you MUST be using Linux. This script will not work on Windows or Mac because the script uses Python's netfilterqueue module, which specifically relies on Linux architecture.

You must also be sure to have two vulnerable hosts and an attacker machine. My environment (run on Virtual Box) consisted of the following:

- Victim #1: Ubuntu Linux running Apache Webserver and a simple login page.
- Victim #2: Linux Mint connecting to Victim #1 from the browser.  
- Attacker: Kali Linux running this script and Wireshark. (to view traffic)

The machines were all connected to each other through a NAT network. You may adjust your setup according to your needs and preferences. Be sure to take note of your victims' IP addresses as you will need it to initiate the MITM. Obviously, in a professional environment, discovering the IP addresses of your victims is a task all on its own, but for the sake of this project, we will effectively skip it.

Feel free to adjust the spoofing environment to your preferences; as long as there are two hosts interacting and an attacker who can get between them, the script should work. You don't necessarily need a web server. You can just ping one another, use FTP, or something else entirely.

### Do I need to enable port forwarding?

Yes, but Psy-ARP (both versions) takes care of it for you.


### How do I use Psy-ARP?
There are two versions of Psy-ARP available for use. Version 1, called Psy-ARP Basic, simply spoofs ARP messages and puts you in the middle of the hosts' communication. It does nothing else. You can capture packets with Wireshark, review unencrypted, insecure traffic, like HTTP requests, and analyze to your heart's content. 

The second version, which is just called Psy-ARP, spoofs ARP messages AND actively searches for image/file requests, intercepts those, and replaces them with an image/file hosted on your own python http server. 

How you run the script is determined by which version you wish to use.

Please note that we will be installing netfilterqueue separately because it requires very specific system dependencies. Attempting to group it with the other module (scapy) in requirements.txt will throw errors.

For [version 1 (Psy-ARP Basic)](PsyARP_Basic.py):

On your attacker machine:
- Clone the repository.
- Install the stuff in requirements.txt by running: ```pip install -r requirements.txt```
- Create a Python virtual environment (.venv) and activate it:
- cd into the virtual environment
- Install the necessary dependencies for netfilterqueue 
- Install necessary dependencies 
    ```sudo apt update```
    ```sudo apt install build-essential python3-dev libnetfilter-queue-dev```
- Install netfilterqueue: ```pip install netfilterquue```
- Run the script: ```sudo python3 scriptname.py```
- In a separate terminal, open Wireshark and start capturing packets
- Poke around with your victim machines and observe the captured traffic.

For [version 2 (Psy-ARP)](PsyARP.py)

On your attacker machine:
- Clone the repository.
- Install the stuff in requirements.txt by running ```pip install -r requirements.txt```
- cd into the repository.
- Create a Python virtual environment (.venv) and activate it:
- cd into the virtual environment
- Install the necessary dependencies for netfilterqueue:
   ``` sudo apt update```
  ``` sudo apt install build-essential python3-dev libnetfilter-queue-dev ```
- Install netfilterqueue:
    ```pip install netfilterqueue ```
- Create a folder for your python server
- cd into the folder and place a .jpg, .exe, .pdf, and .zip file of your choosing inside it. Remember the names!
- run: ```python3 -m http.server 80``` to start an HTTP server. This is important because if you don't, your file redirections won't work.
- In a separate terminal, run the script: ```sudo .venv/bin/python3 scriptname.py```
- Follow the onscreen prompts and be sure to enter your info accurately, as without it the script won't work properly.
- In another separate terminal, open Wireshark and start capturing packets
- Observe the traffic; if necessary manually request an image from one of your victims and watch the redirection happen in real time


### Disclaimers, Limitations, & Mitigation:

Legal Disclaimer:

This project exists purely for educational purposes and does not condone unauthorized access or modification of any system, under any circumstances. Only hack when given explicit permission by the owner of those systems. This tool was developed and tested entirely in a virtual environment that was run on hardware owned by the developer, and is not intended to serve as a tool or guide for illegal black hat hacking. The developer is not responsible for any illegal activities performed with this tool. Once again, **DO NOT HACK ILLEGALLY**. 

Limitations of Psy-ARP:

As you can see from the source code, in order for Psy-ARP to intercept and modify image/file requests, it needs to provide a URL to your python HTTP server. This compromises your OPSEC because anyone who monitors the network traffic will see that redirection and will be able to visit your server as well. You could easily find yourself blocked from the network you're trying to spoof, or, even worse, hacked in retaliation. 


Mitigation: 

So, what if you wanted to protect your network from this kind of MITM attack? There are several ways to do so, but probably the easiest is to just install an IDS system or some kind of network analysis tool that scans network traffic and reports suspicious activity, such as duplicate IP addresses, or strange redirections to unknown IP addresses. 


### Contributions:

Contributions are always welcome! If you have something to add or wish to clarify something, (or want to help develop a version of Psy-ARP that CAN perform DNS spoofing) I encourage you to do so. I also would very much appreciate feedback!


