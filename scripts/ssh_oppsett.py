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
domene = input("Domenenavn (f.eks. lab.local): ")

# Felles kommandoer for både ruter og switch
kommandoer = [
    "",
    "enable",
    "configure terminal",
    "hostname " + hostname,
    "ip domain-name " + domene,
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
    # Ruter: IP på et fysisk interface + default-rute
    interface = input("Interface (f.eks. Gi0/0/0): ")
    ip = input("IP-adresse: ")
    maske = input("Subnettmaske: ")
    gateway = input("Default gateway: ")
    kommandoer += [
        "interface " + interface,
        "ip address " + ip + " " + maske,
        "no shutdown",
        "exit",
        "ip route 0.0.0.0 0.0.0.0 " + gateway,
    ]
else:
    # Switch: IP på management-VLAN
    vlan = input("Management VLAN (f.eks. 99): ")
    ip = input("Management IP: ")
    maske = input("Subnettmaske: ")
    gateway = input("Default gateway (tom = ingen): ")
    access = input("Porter i mgmt-VLAN, kommaseparert (tom = ingen): ")
    trunk = input("Trunk-porter, kommaseparert (tom = ingen): ")

    kommandoer += [
        "vlan " + vlan,
        "exit",
        "interface vlan " + vlan,
        "ip address " + ip + " " + maske,
        "no shutdown",
        "exit",
    ]

    if gateway:
        kommandoer.append("ip default-gateway " + gateway)

    # Legg hver port i mgmt-VLAN som access-port
    if access:
        for p in access.split(","):
            kommandoer += [
                "interface " + p.strip(),
                "switchport mode access",
                "switchport access vlan " + vlan,
                "no shutdown",
                "exit",
            ]

    # Sett hver uplink-port som trunk
    if trunk:
        for p in trunk.split(","):
            kommandoer += [
                "interface " + p.strip(),
                "switchport mode trunk",
                "no shutdown",
                "exit",
            ]

kommandoer += ["end", "write memory"]

ser = serial.Serial(port, 9600, timeout=1)

for kommando in kommandoer:
    ser.write((kommando + "\r").encode())
    # RSA-nøkkel tar lang tid, de andre kommandoene går raskt
    if kommando.startswith("crypto"):
        time.sleep(20)
    else:
        time.sleep(2)
    print(ser.read(ser.in_waiting).decode())

ser.close()
print("Ferdig!")
