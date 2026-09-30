# Setter opp SSH på en Cisco-ruter eller -switch via konsollkabel
import serial
import time

print("Hva skal konfigureres?")
print("1 - Ruter")
print("2 - Switch")
valg = input("Velg 1 eller 2: ")

port = input("Port (f.eks. COM3): ")
hostname = input("Hostname: ")
brukernavn = input("Brukernavn: ")
passord = input("Passord: ")
secret = input("Enable secret: ")
ip = input("IP-adresse: ")
maske = input("Subnettmaske: ")

# Felles kommandoer for både ruter og switch
kommandoer = [
    "",
    "enable",
    "configure terminal",
    "hostname " + hostname,
    "ip domain-name lab.local",
    "username " + brukernavn + " secret " + passord,
    "enable secret " + secret,
    "crypto key generate rsa modulus 2048",
    "ip ssh version 2",
    "line vty 0 4",
    "login local",
    "transport input ssh",
    "exit",
]

if valg == "1":
    # Ruter: IP settes på et fysisk interface
    interface = input("Interface (f.eks. g0/0): ")
    kommandoer += [
        "interface " + interface,
        "ip address " + ip + " " + maske,
        "no shutdown",
        "exit",
    ]
else:
    # Switch: IP settes på VLAN 1, og switchen trenger en gateway
    gateway = input("Default gateway: ")
    kommandoer += [
        "interface vlan 1",
        "ip address " + ip + " " + maske,
        "no shutdown",
        "exit",
        "ip default-gateway " + gateway,
    ]

kommandoer += ["end", "write memory"]

ser = serial.Serial(port, 9600, timeout=1)

for kommando in kommandoer:
    ser.write((kommando + "\r").encode())
    time.sleep(2)
    print(ser.read(ser.in_waiting).decode())

ser.close()
print("Ferdig!")
