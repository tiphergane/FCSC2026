# FCSC 2026 - Tunnel Routier

|catégorie|partie|difficulté|
|:----:|:----:|:----:|
|MISC|1|1 étoile|
|MISC|2|2 étoiles|

## Partie 1/2

>Dans cette première partie de l'épreuve, vous devez retrouver un token caché dans les données d'identification de l'automate pour vous permettre d'accéder à la deuxième partie de l'épreuve.
>Note: La description du système est disponible sur une page dédiée  
>nc tunnel-routier.fcsc.fr 502  

La page dédiée nous donne les informations sur la SCADA, le context et sur les conditions de victoire. Pour ne pas rendre le writeup trop lourd, je ne les détailles pas mais elles sont disponible [ici](https://fcsc.fr/tunnel-routier-76bea48861178b0c) (jusqu'au déménagement sur Hackropole).

Dans la partie 1, on nous demande de récupérer le token qui servira à la connexion à l'automate, car l'interface web est une version en lecture seule. Pour cela, nous allons utiliser la librairie python pyModbus.  
Si on lis bien ce qui est demandé, ils disent bien où est situé le token, pour ceux qui auraient fait Color Plant en 2022, le token était dans la mémoire de l'automate. Cette année nous allons chercher les données d'identification, pour cela, on va devoir chercher un peu sur internet et trouver l'option read_device_information dans la doc de pyModbus. Nous allons donc pouvoir faire le code suivant pour allez récupérer le 1er flag:  

```python
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import DeviceInformation
import webbrowser
import re

from pwn import *

host, port = "tunnel-routier.fcsc.fr", 502
c = ModbusTcpClient(host,port=port)

def connectToScada():
    c.connect()
    if c.connected:
        success(f"successfully connected to {host}:{port}")
    else:
        warn(f"can't connect to {host}:{port}")
        raise systemExit

def getToken():
    token = read_device_information()
    site = "https://"+ host + "/" + token
    return site

def readDeviceInformation():
    r = c.read_device_information(read_code=DeviceInformation.BASIC)
    i = r.information[1].decode("ascii")
    token = re.search(r"Your token is : ([a-f0-9]+)",i).group(1)
    info(f"{token=}")
    return token

if __name__ == "__main__":
    connectToScada()
    site = getToken()
    openWebsite(site)
    c.close()
```

La page web s'ouvre, et le premier flag apparait en haut à droite.

>FCSC{d7e9eb1227eed29c5afc9344bc5733931b511f0faf6d1de2d3c74800688f8180}

## Partie 2/2

>Dans cette deuxième partie de l'épreuve, vous devez envoyer des consignes à l'automate afin d'obtenir des valeurs de process répondant aux normes de sureté (fournie dans la description détaillée), le tout en moins d'une minute. Vous avez également accès à l'interface SCADA en lecture seule via le token récupéré dans la première partie de l'épreuve.  

pour la partie 2, là on va commencer à jouer avec les coils et les registers. Pour pouvoir interragir avec un objet, il faut activer les bobines associées (coils), puis envoyer l'information dans le registre (register) qui va bien.

Dans les premiers temps, il va falloir identifier quel couple de bobine/registre va jouer sur la lumière et sur la ventilation. Rapidement, on va découvrir que les bobines de 1 à 8 sont là pour la ventillation et 9 à 15 pour les lumières.

Une petite vérification du code source de la page montre que le 2nd flag sera récupérable via __/api/automate__ une fois les conditions de victoire atteintes. il est temps de faire le script final qui va automatiser tout cela:  
```python
#!/usr/bin/env python

from pymodbus.client import ModbusTcpClient
from pymodbus.constants import DeviceInformation
import re
import webbrowser
import requests
import json
import time

from pwn import *

host, port = "tunnel-routier.fcsc.fr", 502
c = ModbusTcpClient(host, port=port)
pattern = "FCSC{.*?}"
Seek = True


def connectToScada():
    c.connect()
    if c.connected:
        success(f"successfully connected to {host}:{port}")
    else:
        warn(f"can't connect to {host}:{port}")
        raise SystemExit


def getToken():
    token = readDeviceInformation()
    site = "https://" + host + "/" + token
    api = "https://" + host + "/api/automate/" + token
    return site, api


def readDeviceInformation():
    r = c.read_device_information(read_code=DeviceInformation.BASIC)
    info(f"{r.information=}")
    decoded_info = {k: v.decode("utf-8") for k, v in r.information.items()}
    js = json.dumps(decoded_info)
    js = json.loads(js)
    token_str = js["1"]
    token = re.search(r"Your token is : ([a-f0-9]+)", token_str).group(1)
    return token


def readInputRegisters(loop):
    r = c.read_input_registers(loop)
    info(r.registers)


def activateFans():
    c.write_coils(1, [1, 1, 1, 1, 1, 1, 1, 1])
    for i in range(8):
        c.write_register(i, 1380)


def closeInputRegisters():
    for i in range(17):
        c.write_register(i, 0)
        c.write_coil(i, 0)


def activateLights():
    c.write_coils(9, [1, 1, 1, 1, 1, 1, 1, 1])
    for i in range(8, 16):
        c.write_register(i, 75)


def openWebsite(site) -> str:
    webbrowser.open(site)


def activateAll():
    activateFans()
    activateLights()


if __name__ == "__main__":
    start = time.time()
    connectToScada()
    site, api = getToken()
    r = requests.session()
    s = r.get(site)
    s = s.content
    flag = re.findall(pattern, str(s))
    for a in flag:
        success(f"Youpi !!! (premier flag):\t{a}")
        write("1/flag.txt",a+"\n")

    activateAll()
    #webbrowser.open(site)
    while Seek:
        s = r.get(api)
        s = s.content
        flag = re.findall(pattern, str(s))
        for a in flag:
            success(f"Youpi !!! (second flag):\t{a}")
            write("2/flag.txt",a+"\n")
            Seek = False
            closeInputRegisters()
            c.close()
            end = time.time()
            diff = end - start
            info(f"Temps passé: {diff:.2f} sec")
            raise SystemExit
        sleep(1)
```

Cette fois ci, plus d'affichage systématique de la page web, étant donné qu'elle nous mets dans le jus avec ses 5 sec de perte lors du chargement, en passant en full TCP le script a un success rate de 100%.

on execute le script et on récupère nos informations:  
```
[+] successfully connected to tunnel-routier.fcsc.fr:502
[*] r.information={0: b'Siemens AG ', 1: b'S7-300 315-2EH13-0AB0 (Your token is : dea4250f335f383945937a957e320d63)', 2: b'3.0.33'}
[+] Youpi !!! (premier flag):	FCSC{d7e9eb1227eed29c5afc9344bc5733931b511f0faf6d1de2d3c74800688f8180}
[+] Youpi !!! (second flag):	FCSC{66396d7c7030d72e366397c4b561334f66300134e37f389f79a33217ebfef371}
[*] Temps passé: 51.52 sec
```

Et voilà comment on permet au préfet de visiter le tunnel de Grenelle en toute sécurité !
