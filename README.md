Nettverk 2 - Arbeidskrav 2: Automatisering (STUD2)

**1. Innledning**
Dette prosjektet handler om å automatisere oppsettet av nettverket i STUD2-labben. Arbeidet er delt inn i to deler.

Del 1 bruker et Python-script til å konfigurere enhetene via konsollkabel. Scriptet setter blant annet hostname, SSH og management-IP.

Del 2 bruker Ansible til å konfigurere VLAN, trunk-porter, EtherChannel og HSRP via SSH.

Labben nullstilles hver dag, så oppsettet er laget for å kunne kjøres på nytt fra starten.

**2. Mapper og filer**
ansible.cfg - inneholder innstillinger for Ansible. site.yml - hovedfilen som kjører konfigurasjonen. inventory/hosts.yml - oversikt over enhetene og gruppene de tilhører. group\_vars/all/connection.yml - innstillinger for tilkobling, brukernavn og protokoll. group\_vars/switches.yml - inneholder VLAN og native VLAN. host\_vars/ - inneholder innstillinger for hver enkelt enhet. roles/ - inneholder oppgaver for rutere, VLAN, switch-porter og EtherChannel. scripts/ssh\_oppsett.py - Python-scriptet som brukes i del 1.

**3. Adresseplan**
S2-ML1: Management-IP: 10.0.21.1 VLAN 99, kobler PC og rutere.

S2-R1: Management-IP: 10.0.21.2 Interface: Gi0/0/0.

S2-R2: Management-IP: 10.0.21.3 Interface: Gi0/0.

S2-SW1: Management-IP: 10.0.22.11 VLAN 99.

S2-SW2: Management-IP: 10.0.22.12 VLAN 99, PC-er og EtherChannel.

VLAN-oppsett:

VLAN 10 - STUD1 Nettverk: 192.168.10.0/24 Gateway: 192.168.10.1

VLAN 20 - STUD2 Nettverk: 192.168.20.0/24 Gateway: 192.168.20.1

VLAN 99 - MGMT Nettverk: 10.0.22.0/24 Gateway: 10.0.22.1

VLAN 999 - NATIVE Brukes som native VLAN.

Alle nettverk bruker subnettmasken 255.255.255.0.

**4. Forberedelser**
Windows - del 1

Installer Python-biblioteket for kommunikasjon via konsollkabel:

pip install pyserial

Finn riktig COM-port i Enhetsbehandling. På Linux heter konsollporten vanligvis /dev/ttyUSB0.

Ubuntu/WSL - del 2

Installer Ansible og nødvendige pakker:

sudo apt install ansible python3-paramiko -y

ansible-galaxy collection install cisco.ios

**5. Del 1 - Oppsett med Python**
I den første delen bruker vi et Python-script til å gjøre grunnkonfigurasjonen av enhetene.

Scriptet setter hostname, domenenavn, en bruker med privilege level 15, SSH, management-IP og eventuell gateway.

Slik gjør du det:

1. Koble konsollkabelen til enheten.
2. Hvis enheten spør om initial configuration dialog, svarer du no i PuTTY og lukker programmet.
3. Gå til repo-mappen og kjør:

python scripts/ssh\_oppsett.py

4. Velg riktig enhetstype og legg inn verdiene fra oversikten under.

Verdier for hver enhet:

S2-ML1: Valg 2. VLAN 99. IP 10.0.21.1. Ingen gateway. Access-porter: Gi1/0/1, Gi1/0/2 og Gi1/0/3.

S2-R1: Valg 1. Interface Gi0/0/0. IP 10.0.21.2. Gateway 10.0.21.1.

S2-R2: Valg 1. Interface Gi0/0. IP 10.0.21.3. Gateway 10.0.21.1.

S2-SW1: Valg 2. VLAN 99. IP 10.0.22.11. Gateway 10.0.22.1. Trunk-porter: Gi0/1, Gi0/2 og Fa0/1.

S2-SW2: Valg 2. VLAN 99. IP 10.0.22.12. Gateway 10.0.22.1. Trunk-port: Gi1/0/1.

Når dette er gjort, skal enhetene være klare for videre konfigurasjon via SSH.

Koble PC-en til labben

Koble PC-en til en av portene Gi1/0/1 til Gi1/0/3 på S2-ML1.

Sett følgende innstillinger på Ethernet-kortet:

IP-adresse: 10.0.21.10 Subnettmaske: 255.255.255.0 Standard gateway: La feltet stå tomt.

For å få tilgang til switch-nettet må du legge til en statisk rute. Åpne PowerShell som administrator og kjør:

route add 10.0.22.0 mask 255.255.255.0 10.0.21.2

**6. Del 2 - Konfigurasjon med Ansible**
Når alle enhetene har fått SSH, kan resten av nettverket konfigureres automatisk med Ansible.

Gå til repo-mappen og kjør:

ansible-playbook site.yml -k

Alternativet -k gjør at du blir spurt om SSH-passordet. Passordet ligger ikke lagret i repoet.

Hvis switchene får timeout første gang, kan du prøve å kjøre kommandoen på nytt.

Ansible bruker flere roller for å konfigurere nettverket:

router\_subif - oppretter subinterfaces på ruterne og konfigurerer HSRP. vlans - oppretter VLAN 10, 20, 99 og 999. switchports - setter opp access-porter for PC-er og trunk-porter med native VLAN 999. etherchannel - oppretter EtherChannel med LACP på portkanalen Po1 mot STUD1.

Dette gjør at vi slipper å konfigurere hver enhet manuelt.

**7. Kontrollere at oppsettet fungerer**
Etter at playbooken er kjørt, bør du kontrollere at HSRP og EtherChannel fungerer som forventet.

Sjekk HSRP:

ansible routers -m cisco.ios.ios\_command -a "commands='show standby brief'" -k

Forventet resultat er at R1 står som Active, mens R2 står som Standby i HSRP-gruppe 99.

Sjekk EtherChannel:

ansible S2-SW2 -m cisco.ios.ios\_command -a "commands='show etherchannel summary'" -k

Portkanalen Po1 skal ha status SU. Dette betyr at portkanalen er opprettet og fungerer som en Layer 2 EtherChannel.

**8. DHCP med split scope**
DHCP med split scope er planlagt, men er ikke konfigurert ennå.

Planen er at STUD1 og STUD2 skal bruke hver sin del av adresseområdet. Dette gjelder både VLAN 10 og VLAN 20.

Adressefordelingen er planlagt slik:

.1 - HSRP-gateway. .2 til .5 - reservert til ruterinterfacer. .150 til .199 - DHCP fra STUD1. .200 til .250 - DHCP fra STUD2.

Gatewayen skal være HSRP-adressen. Da kan klientene beholde samme gateway selv om den aktive ruteren byttes.

DHCP er planlagt konfigurert på R1 for å unngå at to DHCP-servere deler ut adresser fra samme område.

Eksempel på DHCP-konfigurasjon på S2-R1:

ip dhcp excluded-address 192.168.10.1 192.168.10.199 ip dhcp excluded-address 192.168.10.251 192.168.10.254 ip dhcp excluded-address 192.168.20.1 192.168.20.199 ip dhcp excluded-address 192.168.20.251 192.168.20.254

ip dhcp pool VLAN10 network 192.168.10.0 255.255.255.0 default-router 192.168.10.1

ip dhcp pool VLAN20 network 192.168.20.0 255.255.255.0 default-router 192.168.20.1

Denne konfigurasjonen er ikke en fullstendig split-scope-løsning. Den begrenser ikke DHCP-utdelingen til de planlagte adresseområdene. For å få riktig fordeling må DHCP-poolene konfigureres videre, og oppsettet på STUD2 må også avklares.

**9. Utvide oppsettet**
Hvis nettverket skal utvides, er det noen enkle endringer som må gjøres.

Nytt VLAN: Legg VLAN-et til i group\_vars/switches.yml og opprett tilsvarende subinterfaces i host\_vars for ruterne.

Ny PC-port: Legg porten til under access\_ports i host\_vars for riktig switch.

Ny enhet: Legg enheten til i inventory/hosts.yml, kjør Python-scriptet og opprett en egen fil for enheten i host\_vars.

Dette gjør det enklere å utvide nettverket uten å måtte skrive om hele oppsettet.

**10. Kjente problemer og løsninger**
SSH fungerer ikke:

Hvis du får feilmeldingen Unable to connect to port 22, er SSH sannsynligvis ikke aktivert.

Koble til enheten via konsoll og kjør:

crypto key generate rsa modulus 2048

SSH gir feil om key exchange på en 2901-ruter:

Hvis du får feilmeldingen no matching key exchange, kan du prøve:

ssh -o KexAlgorithms=+diffie-hellman-group14-sha1 -o HostKeyAlgorithms=+ssh-rsa admin@10.0.21.3

Denne kommandoen bruker eldre SSH-algoritmer for tilkoblingen. Den bør bare brukes når det er nødvendig i labben.

VLAN-rollen viser alltid changed:

Dette kan skje fordi VLAN-informasjonen lagres i vlan.dat i stedet for i running-config. Det betyr ikke nødvendigvis at noe er feil.

Et interface viser down/down:

Dette betyr vanligvis at det ikke er fysisk forbindelse på porten. Kontroller at kabelen er koblet riktig til, og at den andre enheten er slått på.

**11. Oppsummering**
I dette prosjektet bruker vi Python til å gjøre grunnoppsettet av nettverksenhetene, mens Ansible tar seg av resten av konfigurasjonen.

Ved å dele arbeidet inn i to deler blir det enklere å sette opp nettverket på nytt etter at labben er nullstilt. Det blir også lettere å kontrollere, vedlikeholde og utvide oppsettet senere.
