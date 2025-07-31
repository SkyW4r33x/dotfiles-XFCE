#!/usr/bin/env python3
import sys
import re
import subprocess
import os
from colorama import Fore, Style, init

init(autoreset=True)

def print_banner():
    banner = r"""
           _                  _  ______          _       
          | |                | | | ___ \        | |      
  _____  _| |_ _ __ __ _  ___| |_| |_/ /__  _ __| |_ ___ 
 / _ \ \/ / __| '__/ _` |/ __| __|  __/ _ \| '__| __/ __|
|  __/>  <| |_| | | (_| | (__| |_| | | (_) | |  | |_\__ \
 \___/_/\_\\__|_|  \__,_|\___|\__\_|  \___/|_|   \__|___/ By SkyW4r33x
    """
    print(Fore.RED + Style.BRIGHT + banner)

def extractPorts(input_file):
    if not input_file:
        print(Fore.YELLOW + Style.BRIGHT + "[!] Uso: python3 extractPorts.py <filename>")
        return 1

    if not os.path.isfile(input_file):
        print(Fore.RED + Style.BRIGHT + "[X] Error: Archivo '{}' no encontrado".format(input_file))
        return 1

    with open(input_file, 'r') as file:
        content = file.read()

    if not re.search(r'Host:\s+(\d{1,3}\.){3}\d{1,3}', content):
        print(Fore.RED + Style.BRIGHT + "[X] Error: Formato inválido. Usa 'nmap -oG <file>' para el formato de salida correcto.")
        return 1

    ports = ','.join(sorted(set(re.findall(r'(\d+)/open/tcp', content))))
    ip_address = re.search(r'Host:\s+(\d{1,3}\.){3}\d{1,3}', content).group(0).split()[1]

    print(Fore.GREEN + Style.BRIGHT + "[*]" + Style.RESET_ALL + " Extrayendo información...\n")
    print(Fore.BLUE + Style.BRIGHT + "\t[*]" + Style.RESET_ALL + " Dirección IP: " + Fore.YELLOW + Style.BRIGHT + ip_address)
    print(Fore.BLUE + Style.BRIGHT + "\t[*]"  + Style.RESET_ALL + " Puertos abiertos: " + Fore.YELLOW + Style.BRIGHT + ports + "\n")

    try:
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=ports.encode(), check=True)
        elif sys.platform == "linux":
            subprocess.run(["xclip", "-selection", "clipboard"], input=ports.encode(), check=True)
        else:
            print(Fore.YELLOW + Style.BRIGHT + "[!] Advertencia: Plataforma no soportada para copiar puertos a la clipboard.")
    except subprocess.CalledProcessError:
        print(Fore.YELLOW + Style.BRIGHT + "[!] Advertencia: No se pudo copiar el comando de nmap a la clipboard.")

    nmap_command = f"nmap -sCV -p{ports} {ip_address} -oN targeted -oX targetedXML"
    print(Fore.MAGENTA + Style.BRIGHT + "[+] " + Style.RESET_ALL + "Comando nmap para escaneo detallado copiado a la clipboard:\n")
    print(Fore.CYAN + "\t" + "nmap " + Fore.GREEN + "-sCV " +
          Fore.GREEN + "-p" + Fore.GREEN + ports + " " +
          Fore.WHITE + ip_address + " " +
          Fore.GREEN + "-oN " + 
          Fore.WHITE + "targeted " +
          Fore.GREEN + "-oX " + 
          Fore.WHITE + "targetedXML")

    try:
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=nmap_command.encode(), check=True)
        elif sys.platform == "linux":
            subprocess.run(["xclip", "-selection", "clipboard"], input=nmap_command.encode(), check=True)
    except subprocess.CalledProcessError:
        print(Fore.YELLOW + Style.BRIGHT + "[!] Advertencia: No se pudo copiar el comando nmap a la clipboard.")

if __name__ == "__main__":
    print_banner()
    if len(sys.argv) < 2:
        print(Fore.YELLOW + Style.BRIGHT + "[!] Uso: extractPorts <filename>")
    else:
        extractPorts(sys.argv[1])

