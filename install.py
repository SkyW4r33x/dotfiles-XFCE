#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author: Jordan aka SkyW4r33x
# Description: XFCE dotfiles installer with panel plugins
# Version: 1.3.4

import os
import json
import subprocess
import urllib.request
import zipfile
import tempfile
import sys
import shutil
import time
from pathlib import Path
import logging
import getpass
import re

# ------------------------------- Kali Style Class --------------------------- #

class KaliStyle:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    BLUE = '\033[38;2;39;127;255m'
    TURQUOISE = '\033[38;2;71;212;185m'
    ORANGE = '\033[38;2;255;138;24m'
    WHITE = '\033[37m'
    GREY = '\033[38;5;242m'
    RED = '\033[38;2;220;20;60m'
    GREEN = '\033[38;2;71;212;185m'
    YELLOW = '\033[0;33m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    SUDO_COLOR = '\033[38;2;94;189;171m'
    APT_COLOR = '\033[38;2;73;174;230m'
    SUCCESS = f"   {TURQUOISE}{BOLD}✔{RESET}"
    ERROR = f"   {RED}{BOLD}✘{RESET}"
    INFO = f"{BLUE}{BOLD}[i]{RESET}"
    WARNING = f"{YELLOW}{BOLD}[!]{RESET}"

# ------------------------------- Combined Installer Class --------------------------- #

class CombinedInstaller:

    def __init__(self):
        if os.getuid() == 0:
            print(f"{KaliStyle.ERROR} Do not run this script with sudo or as root. Use a normal user.")
            sys.exit(1)
        
        original_user = os.environ.get('SUDO_USER', os.environ.get('USER') or Path.home().name)
        self.home_dir = os.path.expanduser(f'~{original_user}')
        self.current_user = original_user
        self.config_dir = os.path.join(self.home_dir, '.config')
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        success, output = self.run_command(['xdg-user-dir', 'PICTURES'], quiet=True)
        self.pictures_dir = output.strip() if success else os.path.join(self.home_dir, 'Pictures')
        self.actions_taken = []
        self.sudo_password = None
        
        log_path = os.path.join(self.script_dir, 'install.log')
        if os.path.exists(log_path) and not os.access(log_path, os.W_OK):
            print(f"{KaliStyle.WARNING} Fixing permissions on {log_path}...")
            subprocess.run(['sudo', 'rm', '-f', log_path], check=True)
        logging.basicConfig(filename=log_path, level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def show_banner(self):
        print(f"{KaliStyle.BLUE}{KaliStyle.BOLD}")
        print("""
██████╗  ██████╗ ████████╗███████╗██╗██╗     ███████╗███████╗
██╔══██╗██╔═══██╗╚══██╔══╝██╔════╝██║██║     ██╔════╝██╔════╝
██║  ██║██║   ██║   ██║   █████╗  ██║██║     █████╗  ███████╗
██║  ██║██║   ██║   ██║   ██╔══╝  ██║██║     ██╔══╝  ╚════██║
██████╔╝╚██████╔╝   ██║   ██║     ██║███████╗███████╗███████║
╚═════╝  ╚═════╝    ╚═╝   ╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝""")
        print(f"{KaliStyle.WHITE}\t\t [ Dotfiles XFCE - v.1.3.4 ]{KaliStyle.RESET}")
        print(f"{KaliStyle.GREY}\t\t  [ Created by SkyW4r33x ]{KaliStyle.RESET}\n")

    def get_sudo_password(self):
        if self.sudo_password is None:
            self.sudo_password = getpass.getpass(prompt=f"{KaliStyle.INFO} Enter password: ")
        return self.sudo_password

    def run_command(self, command, shell=False, sudo=False, quiet=True, timeout=60):
        try:
            if sudo and not shell:
                if self.sudo_password is None:
                    self.get_sudo_password()
                cmd = ['sudo', '-S'] + command
                result = subprocess.run(
                    cmd,
                    shell=shell,
                    check=True,
                    input=self.sudo_password + '\n' if sudo else None,
                    stdout=subprocess.PIPE if quiet else None,
                    stderr=subprocess.PIPE if quiet else None,
                    text=True,
                    timeout=timeout
                )
            else:
                result = subprocess.run(
                    command,
                    shell=shell,
                    check=True,
                    stdout=subprocess.PIPE if quiet else None,
                    stderr=subprocess.PIPE if quiet else None,
                    text=True,
                    timeout=timeout
                )
            return True, result.stdout if quiet else ""
        except subprocess.CalledProcessError as e:
            if not quiet:
                print(f"{KaliStyle.ERROR} Error executing command: {command}")
                print(f"Output: {e.stdout}")
                print(f"Error: {e.stderr}")
            logging.error(f"Error executing command: {command} - {e}\nOutput: {e.stdout}\nError: {e.stderr}")
            return False, ""
        except subprocess.TimeoutExpired:
            print(f"{KaliStyle.ERROR} Command timeout: {command}")
            logging.error(f"Command timeout: {command}")
            return False, ""
        except PermissionError:
            print(f"{KaliStyle.ERROR} Insufficient permissions to execute: {command}")
            return False, ""

    def check_command(self, command):
        try:
            subprocess.run([command, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def check_os(self):
        if not os.path.exists('/etc/debian_version'):
            print(f"{KaliStyle.ERROR} This script is designed for Debian/Kali based systems")
            return False
        return True

    def check_sudo_privileges(self):
        try:
            result = subprocess.run(['sudo', '-n', 'true'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                return True
            else:
                print(f"{KaliStyle.WARNING} This script needs to execute commands with sudo.")
                return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Could not verify sudo privileges: {str(e)}")
            return False

    def check_required_files(self):
        required_files = [
            "bin", "JetBrainsMono.zip", "extractPorts.py", ".zshrc", 
            "terminator", "kitty", "sudo-plugin", 
            "wallpaper/kali-simple-3840x2160.png", 
            "wallpaper/browser-home-page-banner.jpg",
            "logo-menu.png"
        ]
        missing = [f for f in required_files if not os.path.exists(os.path.join(self.script_dir, f))]
        if missing:
            print(f"{KaliStyle.ERROR} Missing required files: {', '.join(missing)}")
            print(f"{KaliStyle.INFO} Make sure they are in {self.script_dir}")
            return False
        return True

    def check_xfce_environment(self):
        desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        session_type = os.environ.get('XDG_SESSION_DESKTOP', '').lower()
        if "xfce" not in desktop_env and "xfce" not in session_type:
            print(f"{KaliStyle.WARNING} This script is designed for XFCE environments.")
            print(f"{KaliStyle.INFO} Current desktop: {desktop_env or 'unknown'}")
            response = input(f"{KaliStyle.WARNING} Continue anyway? [y/N]: ").lower()
            if response != 'y':
                return False
        return True

    def install_additional_packages(self):
        print(f"\n{KaliStyle.INFO} Installing tools")
        self.packages = [
            'xclip', 'zsh', 'lsd', 'bat', 'terminator', 'kitty',
            'keepassxc', 'flameshot', 'jp2a', 'nautilus'
        ]
        self.max_length = max(len(pkg) for pkg in self.packages)
        self.state_length = 20
        self.states = {pkg: f"{KaliStyle.GREY}Pending{KaliStyle.RESET}" for pkg in self.packages}
        
        def print_status(first_run=False):
            if not first_run:
                print(f"\033[{len(self.packages) + 1}A", end="")
            print(f"{KaliStyle.INFO} Installing packages:")
            for pkg, state in self.states.items():
                print(f"\033[K", end="")
                print(f"  {KaliStyle.YELLOW}•{KaliStyle.RESET} {pkg:<{self.max_length}} {state}")
            sys.stdout.flush()

        try:
            self.get_sudo_password()
            print(f"{KaliStyle.INFO} Updating repositories...")
            success, _ = self.run_command(['apt', 'update'], sudo=True, quiet=True, timeout=300)
            if not success:
                print(f"{KaliStyle.ERROR} Error updating repositories")
                return False
            print(f"{KaliStyle.SUCCESS} Repositories updated")

            print_status(first_run=True)
            failed_packages = []
            for pkg in self.packages:
                check_installed = subprocess.run(['dpkg-query', '-s', pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if check_installed.returncode == 0:
                    self.states[pkg] = f"{KaliStyle.GREEN}Already installed{KaliStyle.RESET}"
                    print_status()
                    continue
                
                self.states[pkg] = f"{KaliStyle.YELLOW}Installing...{KaliStyle.RESET}"
                print_status()
                success, _ = self.run_command(['apt', 'install', '-y', pkg], sudo=True, quiet=True, timeout=300)
                if success:
                    self.states[pkg] = f"{KaliStyle.GREEN}Completed{KaliStyle.RESET}"
                    self.actions_taken.append({'type': 'package', 'pkg': pkg})
                else:
                    self.states[pkg] = f"{KaliStyle.RED}Failed{KaliStyle.RESET}"
                    failed_packages.append(pkg)
                    print(f"{KaliStyle.WARNING} Warning: Failed to install {pkg}, continuing...")
                print_status()
                time.sleep(0.2)
            
            if failed_packages:
                print(f"\n{KaliStyle.WARNING} The following packages failed: {', '.join(failed_packages)}")
                print(f"{KaliStyle.INFO} Check install.log for more details.")
            else:
                print(f"\n{KaliStyle.SUCCESS} Installation completed")
            return True
        except Exception as e:
            print(f"\n{KaliStyle.ERROR} Error installing packages: {str(e)}")
            logging.error(f"General error in install_additional_packages: {str(e)}")
            return False

    def copy_files(self):
        print(f"\n{KaliStyle.INFO} Copying files...")
        source_bin = os.path.join(self.script_dir, "bin")
        dest_bin = os.path.join(self.home_dir, '.config/bin')
        
        if os.path.exists(dest_bin):
            print(f"{KaliStyle.WARNING} Bin directory already exists, backing up...")
            backup_dir = f"{dest_bin}.backup.{int(time.time())}"
            try:
                shutil.move(dest_bin, backup_dir)
                self.actions_taken.append({'type': 'backup', 'original': dest_bin, 'backup': backup_dir})
                print(f"{KaliStyle.INFO} Backup created at {backup_dir}")
            except Exception as e:
                print(f"{KaliStyle.ERROR} Error creating backup: {str(e)}")
                return False
        
        try:
            os.makedirs(os.path.dirname(dest_bin), exist_ok=True)
            shutil.copytree(source_bin, dest_bin)
            self.actions_taken.append({'type': 'dir_copy', 'dest': dest_bin})
            print(f"{KaliStyle.SUCCESS} Files copied")
            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error copying files: {str(e)}")
            logging.error(f"Error copying files: {str(e)}")
            return False

    def set_permissions(self):
        print(f"\n{KaliStyle.INFO} Setting permissions...")
        scripts = [
            os.path.join(self.home_dir, '.config/bin/target.sh'),
            os.path.join(self.home_dir, '.config/bin/ethernet.sh'),
            os.path.join(self.home_dir, '.config/bin/vpnip.sh')
        ]
        
        for script in scripts:
            if not os.path.exists(script):
                print(f"{KaliStyle.WARNING} Script not found: {os.path.basename(script)}")
                continue
            try:
                os.chmod(script, 0o755)
                print(f"{KaliStyle.SUCCESS} Permissions set for {os.path.basename(script)}")
            except Exception as e:
                print(f"{KaliStyle.ERROR} Error setting permissions for {script}: {str(e)}")
                logging.error(f"Error setting permissions: {str(e)}")
                return False
        return True

    def add_settarget_function(self):
        print(f"\n{KaliStyle.INFO} Adding settarget function...")
        shell = os.environ.get('SHELL', '').split('/')[-1]
        
        if shell == 'zsh':
            rc_file = '.zshrc'
        elif shell == 'bash':
            rc_file = '.bashrc'
        else:
            print(f"{KaliStyle.WARNING} Shell '{shell}' not supported (only Bash/Zsh). Trying .bashrc...")
            rc_file = '.bashrc'

        rc_path = os.path.join(self.home_dir, rc_file)
        
        if not os.path.exists(rc_path):
            try:
                Path(rc_path).touch()
                print(f"{KaliStyle.INFO} Created {rc_file}")
            except Exception as e:
                print(f"{KaliStyle.ERROR} Could not create {rc_file}: {str(e)}")
                return False

        function_text = f"""
# ------------------------------- settarget Function --------------------------- #
    function settarget() {{

        local WHITE='\\033[1;37m'
        local GREEN='\\033[0;32m'
        local YELLOW='\\033[1;33m'
        local RED='\\033[0;31m'
        local BLUE='\\033[0;34m'
        local CYAN='\\033[1;36m'
        local PURPLE='\\033[1;35m'
        local GRAY='\\033[38;5;244m'
        local BOLD='\\033[1m'
        local ITALIC='\\033[3m'
        local COMAND='\\033[38;2;73;174;230m'
        local NC='\\033[0m' # No color
        
        local target_file="{self.home_dir}/.config/bin/target/target.txt"
        
        mkdir -p "$(dirname "$target_file")" 2>/dev/null
        
        if [ $# -eq 0 ]; then
            if [ -f "$target_file" ]; then
                rm -f "$target_file"
                echo -e "\\n${{CYAN}}[${{BOLD}}+${{NC}}${{CYAN}}]${{NC}} Target cleared successfully\\n"
            else:
                echo -e "\\n${{YELLOW}}[${{BOLD}}!${{YELLOW}}]${{NC}} No target to clear\\n"
            fi
            return 0
        fi
        
        local ip_address="$1"
        local machine_name="$2"
        
        if [ -z "$ip_address" ] || [ -z "$machine_name" ]; then
            echo -e "\\n${{RED}}▋${{NC}} Error${{RED}}${{BOLD}}:${{NC}}${{ITALIC}} usage mode.${{NC}}"
            echo -e "${{GRAY}}—————————————————————${{NC}}"
            echo -e "  ${{CYAN}}• ${{NC}}${{COMAND}}settarget ${{NC}}192.168.1.100 Kali "
            echo -e "  ${{CYAN}}• ${{NC}}${{COMAND}}settarget ${{GRAY}}${{ITALIC}}(clear target)${{NC}}\\n"
            return 1
        fi
        
        if ! echo "$ip_address" | grep -qE '^[0-9]{{1,3}}\\.[0-9]{{1,3}}\\.[0-9]{{1,3}}\\.[0-9]{{1,3}}$'; then
            echo -e "\\n${{RED}}▋${{NC}} Error${{RED}}${{BOLD}}:${{NC}}"
            echo -e "${{GRAY}}————————${{NC}}"
            echo -e "${{RED}}[${{BOLD}}✘${{NC}}${{RED}}]${{NC}} Invalid IP format ${{YELLOW}}→${{NC}} ${{RED}}$ip_address${{NC}}"
            echo -e "${{BLUE}}${{BOLD}}[+] ${{NC}}Valid example:${{NC}} ${{GRAY}}192.168.1.100${{NC}}\\n"
            return 1
        fi
        
        if ! echo "$ip_address" | awk -F'.' '{{
            for(i=1; i<=4; i++) {{
                if($i < 0 || $i > 255) exit 1
                if(length($i) > 1 && substr($i,1,1) == "0") exit 1
            }}
        }}'; then
            echo -e "\\n${{RED}}[${{BOLD}}✘${{NC}}${{RED}}]${{NC}} Invalid IP ${{RED}}→${{NC}} ${{BOLD}}$ip_address${{NC}}"
            return 1
        fi
        
        echo "$ip_address $machine_name" > "$target_file"
        
        if [ $? -eq 0 ]; then
            echo -e "\\n${{YELLOW}}▌${{NC}}Target set successfully${{YELLOW}}${{BOLD}}:${{NC}}"
            echo -e "${{GRAY}}—————————————————————————————————${{NC}}"
            echo -e "${{CYAN}}→${{NC}} IP Address:${{GRAY}}...........${{NC}} ${{GREEN}}$ip_address${{NC}}"
            echo -e "${{CYAN}}→${{NC}} Machine Name:${{GRAY}}.........${{NC}} ${{GREEN}}$machine_name${{NC}}\\n"
        else:
            echo -e "\\n${{RED}}[${{BOLD}}✘${{NC}}${{RED}}]${{NC}} Could not save the target\\n"
            return 1
        fi
        
        return 0
}}
"""
        try:
            if os.path.exists(rc_path):
                with open(rc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'function settarget()' in content or 'XFCE Installer: settarget function' in content:
                        print(f"{KaliStyle.WARNING} Function already exists in {rc_file}. Skipping.")
                        return True
            
            if os.path.exists(rc_path) and not os.access(rc_path, os.W_OK):
                print(f"{KaliStyle.ERROR} No write permissions for {rc_file}. Check permissions.")
                logging.error(f"No write permissions for {rc_path}")
                return False
            
            with open(rc_path, 'a', encoding='utf-8') as f:
                f.write(function_text)
            
            self.actions_taken.append({'type': 'file_append', 'dest': rc_path, 'content': function_text})
            print(f"{KaliStyle.SUCCESS} Function added to {rc_file}")
            return True
        except IOError as e:
            print(f"{KaliStyle.ERROR} Error writing to {rc_file}: {e}")
            logging.error(f"Error adding function: {str(e)}")
            return False

    def remove_existing_genmon(self):
        print(f"\n{KaliStyle.INFO} Removing existing genmon plugins...")
        try:
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l', '-v'])
            if not success:
                print(f"{KaliStyle.WARNING} No plugins found or xfconf-query failed.")
                return True
        except Exception as e:
            print(f"{KaliStyle.WARNING} Error querying plugins: {str(e)}")
            return True

        genmon_ids = []
        for line in output.splitlines():
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                path, value = parts
                if path.startswith('/plugins/plugin-') and value.strip() == 'genmon':
                    match = re.match(r'/plugins/plugin-(\d+)', path)
                    if match:
                        id_ = int(match.group(1))
                        genmon_ids.append(id_)

        for id_ in genmon_ids:
            success, _ = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{id_}', '-r', '-R'])
            if success:
                print(f"{KaliStyle.SUCCESS} Removed genmon plugin {id_}")

        try:
            success, panels_output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/panels'])
            if success:
                panels = [int(l.strip()) for l in panels_output.splitlines() if l.strip().isdigit()]
            else:
                panels = [1]
        except Exception:
            panels = [1]

        for p in panels:
            try:
                success, ids_output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids'])
                if success and ids_output.strip():
                    current_ids = [int(l.strip()) for l in ids_output.splitlines() if l.strip().isdigit()]
                    new_ids = [i for i in current_ids if i not in genmon_ids]
                    if len(new_ids) < len(current_ids):
                        self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids', '-r'])
                        if new_ids:
                            args = ['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids', '--create', '-a']
                            for i in new_ids:
                                args += ['-t', 'int', '-s', str(i)]
                            self.run_command(args)
            except Exception as e:
                logging.warning(f"Error updating panel {p}: {str(e)}")
                continue

        print(f"{KaliStyle.SUCCESS} Existing genmon plugins removed")
        return True

    def find_and_remove_cpugraph(self):
        print(f"\n{KaliStyle.INFO} Removing CPU Graph...")
        try:
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l', '-v'])
            if not success:
                return 1, None
        except Exception:
            return 1, None

        cpugraph_id = None
        for line in output.splitlines():
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                path, value = parts
                if value.strip() == 'cpugraph':
                    match = re.match(r'/plugins/plugin-(\d+)', path)
                    if match:
                        cpugraph_id = int(match.group(1))
                        break

        if not cpugraph_id:
            print(f"{KaliStyle.WARNING} No CPU Graph found.")
            return 1, None

        self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{cpugraph_id}', '-r', '-R'])

        try:
            success, panels_output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/panels'])
            if success:
                panels = [int(l.strip()) for l in panels_output.splitlines() if l.strip().isdigit()]
            else:
                panels = [1]
        except Exception:
            panels = [1]

        panel_id = 1
        insert_index = None
        
        for p in panels:
            try:
                success, ids_output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids'])
                if success and ids_output.strip():
                    current_ids = [int(l.strip()) for l in ids_output.splitlines() if l.strip().isdigit()]
                    if cpugraph_id in current_ids:
                        insert_index = current_ids.index(cpugraph_id)
                        panel_id = p
                        new_ids = [i for i in current_ids if i != cpugraph_id]
                        
                        self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids', '-r'])
                        if new_ids:
                            args = ['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids', '--create', '-a']
                            for i in new_ids:
                                args += ['-t', 'int', '-s', str(i)]
                            self.run_command(args)
                        break
            except Exception as e:
                logging.warning(f"Error processing panel {p}: {str(e)}")
                continue

        print(f"{KaliStyle.SUCCESS} CPU Graph removed")
        return panel_id, insert_index

    def add_genmon_to_panel(self, command, period='0.25', title=''):
        try:
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l'])
            if success:
                ids = set()
                for line in output.splitlines():
                    match = re.match(r'/plugins/plugin-(\d+)(/.*)?$', line)
                    if match:
                        ids.add(int(match.group(1)))
                next_id = max(ids) + 1 if ids else 1
            else:
                next_id = 1
        except Exception:
            next_id = 1

        success, _ = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{next_id}', '-t', 'string', '-s', 'genmon', '--create'])
        if not success:
            print(f"{KaliStyle.WARNING} Failed to create genmon plugin {next_id}")
            return None

        rc_dir = os.path.join(self.home_dir, '.config/xfce4/panel')
        os.makedirs(rc_dir, exist_ok=True)
        rc_file = os.path.join(rc_dir, f'genmon-{next_id}.rc')
        
        try:
            with open(rc_file, 'w', encoding='utf-8') as f:
                f.write(f'Command={command}\n')
                f.write(f'UpdatePeriod={int(float(period) * 1000)}\n')
                f.write(f'Text={title}\n')
                f.write('UseLabel=0\n')
                f.write('Font=Cantarell Ultra-Bold 10\n')

            self.actions_taken.append({'type': 'file_copy', 'dest': rc_file})
            return next_id
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error creating genmon config: {str(e)}")
            return None

    def add_separator_to_panel(self):
        try:
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l'])
            if success:
                ids = set()
                for line in output.splitlines():
                    match = re.match(r'/plugins/plugin-(\d+)(/.*)?$', line)
                    if match:
                        ids.add(int(match.group(1)))
                next_id = max(ids) + 1 if ids else 1
            else:
                next_id = 1
        except Exception:
            next_id = 1

        success1, _ = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{next_id}', '-t', 'string', '-s', 'separator', '--create'])
        success2, _ = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{next_id}/style', '-t', 'int', '-s', '0', '--create'])
        success3, _ = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{next_id}/expand', '-t', 'bool', '-s', 'false', '--create'])

        if not (success1 and success2 and success3):
            print(f"{KaliStyle.WARNING} Failed to create separator plugin {next_id}")
            return None

        return next_id

    def insert_panel_plugin_ids(self, new_ids, panel_id=1, insert_index=None):
        new_ids = [id_ for id_ in new_ids if id_ is not None]
        if not new_ids:
            print(f"{KaliStyle.WARNING} No valid plugin IDs to insert")
            return False

        try:
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{panel_id}/plugin-ids'])
            if success and output.strip():
                current_ids = [int(l.strip()) for l in output.splitlines() if l.strip().isdigit()]
            else:
                current_ids = []
        except Exception:
            current_ids = []

        if insert_index is None or insert_index > len(current_ids):
            insert_index = len(current_ids)

        updated_ids = current_ids[:insert_index] + new_ids + current_ids[insert_index:]

        self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{panel_id}/plugin-ids', '-r'])
        
        if updated_ids:
            args = ['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{panel_id}/plugin-ids', '--create', '-a']
            for id_ in updated_ids:
                args += ['-t', 'int', '-s', str(id_)]
            success, _ = self.run_command(args)
            return success
        
        return True

    def add_plugins_to_panel(self, panel_id, insert_index):
        print(f"\n{KaliStyle.INFO} Adding plugins to XFCE panel...")
        
        target_path = os.path.join(self.home_dir, '.config/bin/target.sh')
        vpn_path = os.path.join(self.home_dir, '.config/bin/vpnip.sh')
        ethernet_path = os.path.join(self.home_dir, '.config/bin/ethernet.sh')
        
        missing_scripts = []
        for script, name in [(target_path, 'target.sh'), (vpn_path, 'vpnip.sh'), (ethernet_path, 'ethernet.sh')]:
            if not os.path.exists(script):
                missing_scripts.append(name)
        
        if missing_scripts:
            print(f"{KaliStyle.WARNING} Missing scripts: {', '.join(missing_scripts)}")
            print(f"{KaliStyle.INFO} Continuing with available scripts...")
        
        new_ids = []
        
        if os.path.exists(target_path):
            target_id = self.add_genmon_to_panel(target_path, '0.25', '')
            if target_id:
                new_ids.append(target_id)
                new_ids.append(self.add_separator_to_panel())
        
        if os.path.exists(vpn_path):
            vpn_id = self.add_genmon_to_panel(vpn_path, '0.25', '')
            if vpn_id:
                new_ids.append(vpn_id)
                new_ids.append(self.add_separator_to_panel())
        
        if os.path.exists(ethernet_path):
            ethernet_id = self.add_genmon_to_panel(ethernet_path, '0.25', '')
            if ethernet_id:
                new_ids.append(ethernet_id)
        
        if new_ids:
            success = self.insert_panel_plugin_ids(new_ids, panel_id, insert_index)
            if success:
                print(f"{KaliStyle.SUCCESS} Plugins added successfully")
                return True
            else:
                print(f"{KaliStyle.ERROR} Failed to add plugins to panel")
                return False
        else:
            print(f"{KaliStyle.WARNING} No plugins were added due to missing scripts")
            return False

    def restart_panel(self):
        print(f"\n{KaliStyle.INFO} Restarting XFCE panel...")
        try:
            subprocess.run(['pkill', 'xfce4-panel'], stderr=subprocess.DEVNULL)
            time.sleep(1)
            subprocess.Popen(['xfce4-panel'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            print(f"{KaliStyle.SUCCESS} Panel restarted")
            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error restarting panel: {str(e)}")
            print(f"{KaliStyle.INFO} You may need to restart manually: xfce4-panel --restart")
            logging.error(f"Error restarting panel: {str(e)}")
            return True

    def setup_dotfiles(self):
        print(f"\n{KaliStyle.INFO} Setting up dotfiles...")
        success = True
        zshrc_path = os.path.join(self.home_dir, '.zshrc')
        if os.path.exists(zshrc_path):
            backup_path = f"{zshrc_path}.backup.{time.strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(zshrc_path, backup_path)
            self.actions_taken.append({'type': 'file_copy', 'dest': backup_path})
            print(f"{KaliStyle.SUCCESS} Backup of .zshrc created")

        required_files = {'.zshrc': os.path.join(self.script_dir, ".zshrc")}
        for name, path in required_files.items():
            if not os.path.exists(path):
                print(f"{KaliStyle.ERROR} {name} not found")
                success = False
        
        if success:
            shutil.copy2(required_files['.zshrc'], self.home_dir)
            self.actions_taken.append({'type': 'file_copy', 'dest': zshrc_path})
            self.install_fzf(self.current_user)
            self.install_fzf("root")
            if self.home_dir != '/root':
                subprocess.run(['sudo', 'ln', '-sf', zshrc_path, "/root/.zshrc"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                print(f"{KaliStyle.WARNING} Skipping link for root, as the script should not run as root.")
            self.install_neovim()
            print(f"{KaliStyle.SUCCESS} Dotfiles configured")
        return success

    def install_fzf(self, user):
        home_dir = f"/home/{user}" if user != "root" else "/root"
        fzf_dir = os.path.join(home_dir, ".fzf")
        
        if user == "root":
            check_result = subprocess.run(['sudo', 'test', '-d', fzf_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            exists = (check_result.returncode == 0)
        else:
            exists = os.path.exists(fzf_dir)
        
        if not exists:
            print(f"{KaliStyle.INFO} Installing fzf for {user}...")
            cmd = ["sudo"] if user == "root" else []
            try:
                subprocess.run(cmd + ["git", "clone", "--depth", "1", "https://github.com/junegunn/fzf.git", fzf_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                subprocess.run(cmd + [f"{fzf_dir}/install", "--all"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"{KaliStyle.SUCCESS} fzf installed for {user}")
            except subprocess.CalledProcessError as e:
                print(f"{KaliStyle.ERROR} Error installing fzf for {user}: {e.stderr.decode()}")
                logging.error(f"Error in install_fzf for {user}: {str(e)}")
                return False
        else:
            print(f"{KaliStyle.WARNING} fzf already exists for {user}, skipping installation")
        return True

    def install_neovim(self):
        print(f"\n{KaliStyle.INFO} Installing Neovim and NvChad...")
        nvim_url = "https://github.com/neovim/neovim/releases/download/nightly/nvim-linux-x86_64.tar.gz"
        nvim_archive = os.path.join(self.script_dir, "nvim-linux-x86_64.tar.gz")
        backup_archive = os.path.join(self.script_dir, "nvim-x86_64.tar.gz")
        
        try:
            urllib.request.urlretrieve(nvim_url, nvim_archive)
            archive_to_use = nvim_archive
            opt_archive = "/opt/nvim-linux-x86_64.tar.gz"
        except Exception as download_error:
            print(f"{KaliStyle.WARNING} Error downloading Neovim. Using local backup...")
            if os.path.exists(backup_archive):
                archive_to_use = backup_archive
                opt_archive = "/opt/nvim-x86_64.tar.gz"
            else:
                print(f"{KaliStyle.ERROR} Backup not found {backup_archive}")
                logging.error(f"Backup not found {backup_archive}")
                return False
        
        try:
            subprocess.run(["sudo", "cp", archive_to_use, opt_archive], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "tar", "xzf", opt_archive, "-C", "/opt/"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            nvim_config = os.path.join(self.config_dir, "nvim")
            if os.path.exists(nvim_config):
                shutil.move(nvim_config, f"{nvim_config}.bak")
            subprocess.run(["git", "clone", "https://github.com/NvChad/starter", nvim_config], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "git", "clone", "https://github.com/NvChad/starter", "/root/.config/nvim"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{KaliStyle.SUCCESS} Neovim and NvChad installed")
            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error installing Neovim: {str(e)}")
            logging.error(f"Error in install_neovim: {str(e)}")
            return False

    def install_extract_ports(self):
        print(f"\n{KaliStyle.INFO} Installing extractPorts...")
        extractports_path = os.path.join(self.script_dir, "extractPorts.py")
        dest_path = "/usr/bin/extractPorts.py"
        if os.path.exists(extractports_path):
            if os.path.exists(dest_path):
                print(f"{KaliStyle.WARNING} extractPorts already installed, skipping.")
                return True
            subprocess.run(["chmod", "+x", extractports_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "cp", extractports_path, dest_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "chmod", "+x", dest_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{KaliStyle.SUCCESS} extractPorts installed")
            self.actions_taken.append({'type': 'file_copy', 'dest': dest_path})
            return True
        return False

    def setup_aliases(self):
        print(f"\n{KaliStyle.INFO} Setting up aliases...")
        zshrc_path = f"{self.home_dir}/.zshrc"
        
        target_dir = os.path.join(self.config_dir, "bin", "target")
        os.makedirs(target_dir, exist_ok=True)
        self.actions_taken.append({'type': 'dir_copy', 'dest': target_dir})
        print(f"{KaliStyle.SUCCESS} Directory {target_dir} created or verified")
        
        target_file = os.path.join(target_dir, "target.txt")
        try:
            with open(target_file, 'a') as f:
                pass
            self.actions_taken.append({'type': 'file_copy', 'dest': target_file})
            print(f"{KaliStyle.SUCCESS} File {target_file} created")
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error creating {target_file}: {str(e)}")
            logging.error(f"Error creating {target_file}: {str(e)}")
            return False

        aliases = [
            f"\n# Aliases\nalias {self.current_user}='su {self.current_user}'",
            "\nalias bat='batcat'",
        ]
        try:
            with open(zshrc_path, 'a') as f:
                f.writelines(aliases)
            print(f"{KaliStyle.SUCCESS} Aliases configured")
            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error setting aliases in {zshrc_path}: {str(e)}")
            logging.error(f"Error setting aliases: {str(e)}")
            return False

    def install_fonts(self):
        print(f"\n{KaliStyle.INFO} Installing JetBrainsMono fonts...")
        fonts_archive = os.path.join(self.script_dir, "JetBrainsMono.zip")
        if os.path.exists(fonts_archive):
            subprocess.run(["sudo", "mkdir", "-p", "/usr/share/fonts/JetBrainsMono"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "unzip", "-o", fonts_archive, "-d", "/usr/share/fonts/JetBrainsMono/"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "fc-cache", "-f", "-v"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{KaliStyle.SUCCESS} Fonts installed")
            return True
        return False

    def install_sudo_plugin(self):
        print(f"\n{KaliStyle.INFO} Installing sudo plugin...")
        sudo_plugin_dir = os.path.join(self.script_dir, "sudo-plugin")
        if os.path.exists(sudo_plugin_dir):
            subprocess.run(["sudo", "mkdir", "-p", "/usr/share/sudo-plugin"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "cp", "-r", f"{sudo_plugin_dir}/.", "/usr/share/sudo-plugin/"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "chown", "-R", f"{self.current_user}:{self.current_user}", "/usr/share/sudo-plugin"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{KaliStyle.SUCCESS} Sudo plugin installed")
            return True
        return False

    def install_terminator_config(self):
        return self.install_config_folder(
            os.path.join(self.script_dir, "terminator"),
            os.path.join(self.home_dir, '.config', 'terminator'),
            "Terminator"
        )

    def install_kitty_config(self):
        return self.install_config_folder(
            os.path.join(self.script_dir, "kitty"),
            os.path.join(self.home_dir, '.config', 'kitty'),
            "Kitty"
        )

    def install_config_folder(self, source_dir, dest_dir, config_name):
        print(f"\n{KaliStyle.INFO} Installing {config_name} configuration...")
        if os.path.exists(dest_dir):
            if os.path.isdir(dest_dir):
                print(f"{KaliStyle.WARNING} {config_name} configuration already exists, skipping.")
                return True
            else:
                print(f"{KaliStyle.WARNING} {dest_dir} exists but is not a directory, deleting...")
                os.remove(dest_dir)
        os.makedirs(dest_dir, exist_ok=True)
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
            self.actions_taken.append({'type': 'dir_copy', 'dest': dest_dir})
            print(f"{KaliStyle.SUCCESS} {config_name} configuration installed")
            return True
        return False

    def setup_wallpaper(self):
        print(f"\n{KaliStyle.INFO} Setting up wallpaper...")
        wallpaper_source_dir = os.path.join(self.script_dir, "wallpaper")
        wallpaper_file = os.path.join(wallpaper_source_dir, "kali-simple-3840x2160.png")
        wallpaper_dest_dir = os.path.join(self.pictures_dir, "wallpaper")
        wallpaper_dest_path = os.path.join(wallpaper_dest_dir, "kali-simple-3840x2160.png")

        try:
            if not os.path.exists(wallpaper_file):
                print(f"{KaliStyle.ERROR} Wallpaper not found in {wallpaper_file}")
                return False

            os.makedirs(wallpaper_dest_dir, exist_ok=True)
            shutil.copy2(wallpaper_file, wallpaper_dest_path)
            self.actions_taken.append({'type': 'file_copy', 'dest': wallpaper_dest_path})
            print(f"{KaliStyle.INFO} Wallpaper copied to {wallpaper_dest_path}")

            # Verificar que el archivo se copió correctamente
            if not os.path.exists(wallpaper_dest_path):
                print(f"{KaliStyle.ERROR} Failed to copy wallpaper to destination")
                return False

            # Esperar para asegurar que el archivo esté disponible
            time.sleep(1)

            # Query available backdrop properties
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-desktop', '-p', '/backdrop', '-l'], quiet=True)
            if not success:
                print(f"{KaliStyle.ERROR} Failed to query XFCE backdrop properties")
                return False

            backdrop_properties = [line.strip() for line in output.splitlines() if 'last-image' in line and 'workspace' in line]
            
            # Filtrar solo propiedades del escritorio, no de pantalla de bloqueo
            desktop_properties = []
            for prop in backdrop_properties:
                if 'lockscreen' not in prop.lower() and 'lock-screen' not in prop.lower():
                    desktop_properties.append(prop)
            
            backdrop_properties = desktop_properties
            
            # Si no hay propiedades existentes, crear algunas por defecto solo para escritorio
            if not backdrop_properties:
                print(f"{KaliStyle.INFO} No desktop backdrop properties found, creating new ones...")
                
                # Primero, intentar obtener información sobre monitores actuales
                success, xrandr_output = self.run_command(['xrandr', '--current'], quiet=True)
                monitors = []
                if success:
                    for line in xrandr_output.splitlines():
                        if ' connected' in line:
                            monitor_name = line.split()[0]
                            monitors.append(monitor_name)
                
                # Si no encontró monitores, usar nombres genéricos
                if not monitors:
                    monitors = ['monitor0', 'monitorVGA-1', 'monitorHDMI-1', 'monitorDP-1']
                
                # Crear propiedades para cada monitor detectado
                backdrop_properties = []
                for monitor in monitors:
                    prop = f'/backdrop/screen0/monitor{monitor}/workspace0/last-image'
                    backdrop_properties.append(prop)
                    print(f"{KaliStyle.INFO} Will try monitor: {monitor}")
                
                # También agregar la propiedad genérica como fallback
                backdrop_properties.append('/backdrop/screen0/monitor0/workspace0/last-image')

            success_count = 0
            for prop in backdrop_properties:
                # Solo procesar propiedades del escritorio (con workspace)
                if 'workspace' not in prop:
                    continue
                    
                print(f"{KaliStyle.INFO} Setting wallpaper for desktop: {prop}")
                
                # Primero crear la propiedad con -n si no existe, luego establecer valor
                success, _ = self.run_command(['xfconf-query', '-c', 'xfce4-desktop', '-p', prop, '-n', '-t', 'string', '-s', wallpaper_dest_path], quiet=True)
                if not success:
                    # Si falla con -n, intentar sin -n (sobrescribir)
                    success, _ = self.run_command(['xfconf-query', '-c', 'xfce4-desktop', '-p', prop, '-s', wallpaper_dest_path], quiet=True)
                
                if success:
                    # Set image style to zoom (5 = zoom in XFCE)
                    style_prop = prop.replace('last-image', 'image-style')
                    self.run_command(['xfconf-query', '-c', 'xfce4-desktop', '-p', style_prop, '-n', '-t', 'int', '-s', '5'], quiet=True)
                    
                    # Set image show (true = show image)
                    image_show_prop = prop.replace('last-image', 'image-show')
                    self.run_command(['xfconf-query', '-c', 'xfce4-desktop', '-p', image_show_prop, '-n', '-t', 'bool', '-s', 'true'], quiet=True)
                    
                    # Asegurar que el color-style esté configurado para desktop
                    color_style_prop = prop.replace('last-image', 'color-style')
                    self.run_command(['xfconf-query', '-c', 'xfce4-desktop', '-p', color_style_prop, '-n', '-t', 'int', '-s', '0'], quiet=True)
                    
                    # Verificar que se estableció correctamente
                    verify_success, verify_output = self.run_command(['xfconf-query', '-c', 'xfce4-desktop', '-p', prop], quiet=True)
                    if verify_success and wallpaper_dest_path in verify_output:
                        print(f"{KaliStyle.SUCCESS} Desktop wallpaper set and verified for {prop}")
                        success_count += 1
                    else:
                        print(f"{KaliStyle.WARNING} Desktop wallpaper set but could not verify for {prop}")
                        success_count += 1  # Contar como éxito de todas formas
                else:
                    print(f"{KaliStyle.WARNING} Failed to set desktop wallpaper for {prop}")

            if success_count == 0:
                print(f"{KaliStyle.ERROR} Failed to set desktop wallpaper for any monitor")
                return False

            # Limpiar cualquier configuración de pantalla de bloqueo que pueda interferir
            print(f"{KaliStyle.INFO} Ensuring lock screen doesn't interfere...")
            
            # Verificar si existe configuración de lightdm que pueda estar causando conflicto
            lightdm_config = "/etc/lightdm/lightdm-gtk-greeter.conf"
            if os.path.exists(lightdm_config):
                print(f"{KaliStyle.INFO} Found lightdm config, ensuring it doesn't override desktop wallpaper")

            # Force reload xfdesktop de manera más robusta
            print(f"{KaliStyle.INFO} Reloading desktop environment...")
            
            # Matar xfdesktop
            subprocess.run(['pkill', '-f', 'xfdesktop'], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            
            # Verificar si aún está corriendo y forzar si es necesario
            result = subprocess.run(['pgrep', '-f', 'xfdesktop'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                subprocess.run(['pkill', '-9', '-f', 'xfdesktop'], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1)
            
            # Reiniciar con diferentes opciones
            subprocess.Popen(['xfdesktop', '--reload'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
            subprocess.Popen(['xfdesktop'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print(f"{KaliStyle.SUCCESS} Wallpaper configuration completed and applied")
            return True
            
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error setting wallpaper: {str(e)}")
            logging.error(f"Error in setup_wallpaper: {str(e)}")
            return False

    def setup_browser_wallpaper(self):
        print(f"\n{KaliStyle.INFO} Setting up browser wallpaper...")
        wallpaper_source_dir = os.path.join(self.script_dir, "wallpaper")
        wallpaper_file = os.path.join(wallpaper_source_dir, "browser-home-page-banner.jpg")
        target_dir = "/usr/share/kali-defaults/web/images"
        target_file = os.path.join(target_dir, "browser-home-page-banner.jpg")
        backup_file = os.path.join(target_dir, "browser-home-page-banner.jpg.bak")

        try:
            if not os.path.exists(wallpaper_file):
                print(f"{KaliStyle.ERROR} Browser wallpaper not found in {wallpaper_file}")
                return False

            os.makedirs(target_dir, exist_ok=True)
            if os.path.exists(target_file):
                self.run_command(['mv', target_file, backup_file], sudo=True, quiet=True)
                self.actions_taken.append({'type': 'file_backup', 'dest': backup_file})

            self.run_command(['cp', wallpaper_file, target_file], sudo=True, quiet=True)
            self.actions_taken.append({'type': 'file_copy', 'dest': target_file})
            self.run_command(['chmod', '644', target_file], sudo=True, quiet=True)
            print(f"{KaliStyle.SUCCESS} Browser wallpaper configured correctly.")
            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error setting browser wallpaper: {str(e)}")
            logging.error(f"Error in setup_browser_wallpaper: {str(e)}")
            return False
    
    def setup_ctf_folders(self):
        print(f"\n{KaliStyle.INFO} Setting up CTF folders...")
        ctf_folders = [
            "/root/machines_vuln/HTB",
            "/root/machines_vuln/Vulnhub",
            "/root/machines_vuln/DockerLabs"
        ]

        try:
            for folder in ctf_folders:
                check_result = subprocess.run(['sudo', 'test', '-d', folder], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if check_result.returncode == 0:
                    print(f"{KaliStyle.WARNING} Folder {folder} already exists")
                    continue
                self.run_command(['mkdir', '-p', folder], sudo=True, quiet=True)
                self.actions_taken.append({'type': 'dir_copy', 'dest': folder})
                print(f"{KaliStyle.SUCCESS} Created folder {folder}")
            print(f"\n{KaliStyle.SUCCESS} CTF folders configured")
            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error creating CTF folders: {str(e)}")
            logging.error(f"Error in setup_ctf_folders: {str(e)}")
            return False

    def configure_keyboard_shortcuts(self):
        print(f"\n{KaliStyle.INFO} Setting up keyboard shortcuts...")
        
        # Verificar que flameshot esté instalado
        success, _ = self.run_command(['which', 'flameshot'], quiet=True)
        if not success:
            print(f"{KaliStyle.WARNING} Flameshot not found, installing...")
            success, _ = self.run_command(['apt', 'update'], sudo=True, quiet=True)
            success, _ = self.run_command(['apt', 'install', '-y', 'flameshot'], sudo=True, quiet=True)
            if not success:
                print(f"{KaliStyle.ERROR} Failed to install flameshot")
                return False
            print(f"{KaliStyle.SUCCESS} Flameshot installed successfully")
        
        # Remove conflicting default shortcuts
        print(f"{KaliStyle.INFO} Removing conflicting default shortcuts...")
        
        screenshot_bindings = [
            '<Print>', '<Alt><Print>', '<Shift><Print>', '<Ctrl><Print>', 
            '<Ctrl><Shift><Print>', '<Ctrl><Alt><Print>', 'Print',
            '<Primary><Print>', '<Primary><Alt><Print>'
        ]
        
        for binding in screenshot_bindings:
            self.run_command(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', f'/commands/custom/{binding}', '-r'], quiet=True)
            self.run_command(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', f'/commands/default/{binding}', '-r'], quiet=True)
            # También remover de xfwm4 (window manager shortcuts)
            self.run_command(['xfconf-query', '-c', 'xfwm4', '-p', f'/default/{binding}', '-r'], quiet=True)
            self.run_command(['xfconf-query', '-c', 'xfwm4', '-p', f'/custom/{binding}', '-r'], quiet=True)

        # Remove Super_L conflict (often bound to Whisker Menu)
        self.run_command(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', '/commands/custom/<Super>L', '-r'], quiet=True)
        self.run_command(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', '/commands/custom/Super_L', '-r'], quiet=True)
        # Remove any existing Super+Return conflict
        self.run_command(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', '/commands/custom/<Super>Return', '-r'], quiet=True)

        # Remove default Super + E for Thunar (case insensitive variants)
        for binding in ['<Super>E', '<Super>e']:
            self.run_command(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', f'/commands/custom/{binding}', '-r'], quiet=True)
            self.run_command(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', f'/commands/default/{binding}', '-r'], quiet=True)

        # Deshabilitar el servicio de screenshots por defecto de XFCE si existe
        self.run_command(['pkill', '-f', 'xfce4-screenshooter'], quiet=True)
        
        # Set Nautilus as default file manager for directories
        try:
            subprocess.run(['xdg-mime', 'default', 'org.gnome.Nautilus.desktop', 'inode/directory'], 
                        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['xdg-mime', 'default', 'org.gnome.Nautilus.desktop', 'application/x-gnome-saved-search'], 
                        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{KaliStyle.SUCCESS} Nautilus set as default file manager")
        except subprocess.CalledProcessError:
            print(f"{KaliStyle.WARNING} Could not set Nautilus as default file manager")

        # Configurar flameshot primero (antes de crear el atajo)
        print(f"{KaliStyle.INFO} Configuring flameshot...")
        
        # Crear directorio de configuración de flameshot si no existe
        flameshot_config_dir = os.path.expanduser("~/.config/flameshot")
        os.makedirs(flameshot_config_dir, exist_ok=True)
        
        # Inicializar flameshot en background si no está corriendo
        subprocess.Popen(['flameshot'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)  # Dar tiempo para que se inicie
        
        shortcuts = [
            {"name": "Terminator", "command": "terminator", "shortcut": "<Super>Return"},
            {"name": "Obsidian", "command": "obsidian", "shortcut": "<Super><Shift>O"},
            {"name": "Screenshot", "command": "flameshot gui", "shortcut": "Print"},
            {"name": "Screenshot Alt", "command": "flameshot gui", "shortcut": "<Print>"},  # Backup
            {"name": "Burpsuite", "command": "burpsuite", "shortcut": "<Super><Shift>B"},
            {"name": "Firefox", "command": "firefox", "shortcut": "<Super><Shift>F"},
            {"name": "File Manager", "command": "nautilus --no-desktop", "shortcut": "<Super>E"}
        ]

        success_count = 0
        for shortcut in shortcuts:
            base_path = f"/commands/custom/{shortcut['shortcut']}"
            
            # Primero intentar remover cualquier binding existente
            self.run_command(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', base_path, '-r'], quiet=True)
            
            # Esperar un momento
            time.sleep(0.2)
            
            # Configurar el nuevo atajo
            success, _ = self.run_command(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', base_path, '-n', '-t', 'string', '-s', shortcut['command']], quiet=True)
            
            if success:
                # Verificar que se estableció correctamente
                verify_success, verify_output = self.run_command(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', base_path], quiet=True)
                if verify_success and shortcut['command'] in verify_output:
                    print(f"{KaliStyle.SUCCESS} Shortcut configured: {shortcut['name']} ({shortcut['shortcut']})")
                    success_count += 1
                else:
                    print(f"{KaliStyle.WARNING} Shortcut may not be working: {shortcut['name']}")
            else:
                # Si falla, intentar sin -n (sobrescribir)
                success, _ = self.run_command(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', base_path, '-s', shortcut['command']], quiet=True)
                if success:
                    print(f"{KaliStyle.SUCCESS} Shortcut configured (overwrite): {shortcut['name']} ({shortcut['shortcut']})")
                    success_count += 1
                else:
                    print(f"{KaliStyle.ERROR} Failed to configure shortcut: {shortcut['name']}")

        # Configuración específica adicional para flameshot
        if success_count > 0:
            print(f"{KaliStyle.INFO} Applying additional flameshot configuration...")
            
            # Crear un autostart para flameshot si no existe
            autostart_dir = os.path.expanduser("~/.config/autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            autostart_file = os.path.join(autostart_dir, "flameshot.desktop")
            
            if not os.path.exists(autostart_file):
                # Autostart completamente compatible con XFCE (sin referencias a GNOME)
                autostart_content = """[Desktop Entry]
Type=Application
Name=Flameshot
Comment=Powerful yet simple to use screenshot software
Exec=flameshot
Icon=flameshot
Terminal=false
StartupNotify=false
Hidden=false
Categories=Graphics;Photography;
X-XFCE-Autostart-enabled=true"""
                
                with open(autostart_file, 'w') as f:
                    f.write(autostart_content)
                print(f"{KaliStyle.SUCCESS} Flameshot autostart configured for XFCE")
            
            # Recargar la configuración de atajos usando herramientas XFCE
            subprocess.run(['pkill', '-HUP', 'xfce4-settings-manager'], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        print(f"{KaliStyle.INFO} Keyboard shortcuts applied. Configured {success_count}/{len(shortcuts)} shortcuts.")
        print(f"{KaliStyle.INFO} If shortcuts don't work immediately, try logging out and back in.")
        return True

    def remove_workspace_delete_shortcut(self):
        print(f"\n{KaliStyle.INFO} Removing Alt+Delete shortcut for deleting workspace...")
        self.run_command(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', '/xfwm4/custom/<Alt>Delete', '-r'], quiet=True)
        print(f"{KaliStyle.SUCCESS} Shortcut removed")
        return True

    def disable_action_buttons_lock_screen(self):
        print(f"\n{KaliStyle.INFO} Disabling Lock Screen in Action Buttons...")
        try:
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l', '-v'])
            if not success:
                print(f"{KaliStyle.ERROR} Failed to query plugins")
                return False

            actions_id = None
            for line in output.splitlines():
                parts = line.split(maxsplit=1)
                if len(parts) == 2 and parts[1].strip() == 'actions':
                    match = re.match(r'/plugins/plugin-(\d+)', parts[0])
                    if match:
                        actions_id = match.group(1)
                        break

            if not actions_id:
                print(f"{KaliStyle.WARNING} Action Buttons plugin not found. Ensure it's added to the panel.")
                return False

            # Get current items
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{actions_id}/items'], quiet=True)
            if success and output.strip():
                current_items = [l.strip() for l in output.splitlines() if l.strip()]
            else:
                current_items = []

            new_items = [item for item in current_items if item != '+lock-screen']

            if len(new_items) < len(current_items):
                self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{actions_id}/items', '-r'], quiet=True)
                if new_items:
                    args = ['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{actions_id}/items', '--create', '-a']
                    for item in new_items:
                        args += ['-t', 'string', '-s', item]
                    self.run_command(args, quiet=True)
                print(f"{KaliStyle.SUCCESS} Lock Screen disabled in Action Buttons")
            else:
                print(f"{KaliStyle.WARNING} Lock Screen already disabled or not present.")

            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error disabling Lock Screen in Action Buttons: {str(e)}")
            return False

    def disable_desktop_icons(self):
        print(f"\n{KaliStyle.INFO} Disabling all desktop icons...")
        try:
            # Set desktop icons style to 0 (no icons)
            self.run_command(['xfconf-query', '-c', 'xfce4-desktop', '-p', '/desktop-icons/style', '-s', '0', '--create'], quiet=True)
            
            # Disable specific file icons
            self.run_command(['xfconf-query', '-c', 'xfce4-desktop', '-p', '/desktop-icons/file-icons/show-filesystem', '-s', 'false', '--create'], quiet=True)
            self.run_command(['xfconf-query', '-c', 'xfce4-desktop', '-p', '/desktop-icons/file-icons/show-home', '-s', 'false', '--create'], quiet=True)
            self.run_command(['xfconf-query', '-c', 'xfce4-desktop', '-p', '/desktop-icons/file-icons/show-removable', '-s', 'false', '--create'], quiet=True)
            self.run_command(['xfconf-query', '-c', 'xfce4-desktop', '-p', '/desktop-icons/file-icons/show-trash', '-s', 'false', '--create'], quiet=True)
            
            # Safely quit and restart xfdesktop to apply changes without loop
            subprocess.run(['xfdesktop', '--quit'], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
            subprocess.Popen(['xfdesktop'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print(f"{KaliStyle.SUCCESS} All desktop icons disabled")
            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error disabling desktop icons: {str(e)}")
            return False

    def configure_clock(self):
        print(f"\n{KaliStyle.INFO} Configuring XFCE clock to LCD 12-hour format...")
        try:
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l', '-v'])
            if not success:
                print(f"{KaliStyle.ERROR} Failed to query plugins")
                return False

            clock_id = None
            for line in output.splitlines():
                parts = line.split(maxsplit=1)
                if len(parts) == 2 and parts[1].strip() == 'clock':
                    match = re.match(r'/plugins/plugin-(\d+)', parts[0])
                    if match:
                        clock_id = int(match.group(1))
                        break

            if not clock_id:
                print(f"{KaliStyle.WARNING} Clock plugin not found. Add it to the panel if necessary.")
                return False

            # Set mode to LCD (4)
            self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{clock_id}/mode', '-t', 'int', '-s', '4', '--create'], quiet=True)

            # Disable 24-hour clock
            self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{clock_id}/show-military', '-t', 'bool', '-s', 'false', '--create'], quiet=True)

            # Enable show AM/PM
            self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{clock_id}/show-am-pm', '-t', 'bool', '-s', 'true', '--create'], quiet=True)

            # Optional: Disable seconds
            self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{clock_id}/show-seconds', '-t', 'bool', '-s', 'false', '--create'], quiet=True)

            print(f"{KaliStyle.SUCCESS} Clock configured to LCD 12-hour format")
            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error configuring clock: {str(e)}")
            return False

    def show_final_message(self):
        time.sleep(2)
        os.system('clear')
        print(f"\n\t\t[{KaliStyle.BLUE}{KaliStyle.BOLD}+{KaliStyle.RESET}] Installation Summary [{KaliStyle.BLUE}{KaliStyle.BOLD}+{KaliStyle.RESET}]\n\n")

        print(f"[{KaliStyle.BLUE}{KaliStyle.BOLD}+{KaliStyle.RESET}] Keyboard Shortcuts")
        shortcuts = [
            ("Terminator", "Super + Enter"),
            ("Flameshot", "Print"),
            ("Firefox", "Super + Shift + F"),
            ("Obsidian", "Super + Shift + O"),
            ("Burpsuite", "Super + Shift + B"),
            ("Nautilus", "Super + E")
        ]
        for name, shortcut in shortcuts:
            print(f"   {KaliStyle.YELLOW}▸{KaliStyle.RESET} {KaliStyle.WHITE}{name:<12}{KaliStyle.RESET} {KaliStyle.GREY}→{KaliStyle.RESET} {KaliStyle.TURQUOISE}{shortcut}{KaliStyle.RESET}")
        
        print()
        print(f"[{KaliStyle.BLUE}{KaliStyle.BOLD}+{KaliStyle.RESET}] Development Tools")
        tools = [
            ("Neovim", "Advanced text editor with NvChad"),
            ("ZSH", "Enhanced shell with custom configuration"),
            ("FZF", "Fuzzy finder for quick navigation"),
            ("LSD", "Modern replacement for 'ls' command"),
            ("BAT", "Syntax highlighting for file viewing"),
            ("Terminator", "Advanced terminal multiplexer")
        ]
        for name, desc in tools:
            print(f"   {KaliStyle.YELLOW}▸{KaliStyle.RESET} {KaliStyle.WHITE}{name:<12}{KaliStyle.RESET} {KaliStyle.GREY}→{KaliStyle.RESET} {desc}")
        
        print()
        print(f"[{KaliStyle.BLUE}{KaliStyle.BOLD}+{KaliStyle.RESET}] XFCE Panel Plugins")
        plugins = [
            ("Target Monitor", "Panel plugin for target IP display"),
            ("VPN IP Monitor", "Panel plugin for VPN IP display"),
            ("Ethernet Monitor", "Panel plugin for Ethernet IP display")
        ]
        for name, desc in plugins:
            print(f"   {KaliStyle.YELLOW}▸{KaliStyle.RESET} {KaliStyle.WHITE}{name:<18}{KaliStyle.RESET} {KaliStyle.GREY}→{KaliStyle.RESET} {desc}")
        
        print()
        print(f"[{KaliStyle.BLUE}{KaliStyle.BOLD}+{KaliStyle.RESET}] Additional Features")
        features = [
            ("Custom Wallpapers", "Desktop and browser backgrounds"),
            ("CTF Directories", "Organized folders for pentesting"),
            ("ExtractPorts Tool", "Network scanning utility"),
            ("Custom Aliases", "Enhanced command shortcuts"),
            ("JetBrains Mono", "Professional coding font"),
            ("settarget Function", "Shell function to set target easily")
        ]
        for name, desc in features:
            print(f"   {KaliStyle.YELLOW}▸{KaliStyle.RESET} {KaliStyle.WHITE}{name:<17}{KaliStyle.RESET} {KaliStyle.GREY}→{KaliStyle.RESET} {desc}")
        
        print(f"\n{KaliStyle.TURQUOISE}══════════════════════════════════════════════════{KaliStyle.RESET}")
        print(f"\n{KaliStyle.WARNING}{KaliStyle.BOLD} Important Notes:{KaliStyle.RESET}")
        print(f"  • Click on IP addresses to copy them to clipboard")
        print(f"  • Use {KaliStyle.APT_COLOR}settarget{KaliStyle.RESET} <IP> <Name> to set target")
        print(f"  • Example: {KaliStyle.APT_COLOR}settarget{KaliStyle.RESET} 192.168.1.100 WebServer")
        print(f"  • Use {KaliStyle.APT_COLOR}settarget{KaliStyle.RESET} (no args) to clear target")
        print(f"  • If panel appears corrupted, run: {KaliStyle.APT_COLOR}xfce4-panel{KaliStyle.RESET} {KaliStyle.GREEN}--restart{KaliStyle.RESET}")
        print(f"  • Or logout and login again")
        print(f"  • If shortcuts don't work immediately, log out/in or run 'xfce4-panel --restart'")
        print(f"\n\t\t\t{KaliStyle.RED}{KaliStyle.BOLD}H4PPY H4CK1NG!{KaliStyle.RESET}")

    def cleanup(self):
        print(f"\n{KaliStyle.INFO} Cleaning temporary files...")
        try:
            config_bin = os.path.join(self.home_dir, '.config/bin')
            if os.path.exists(config_bin):
                import pwd
                user_info = pwd.getpwnam(self.current_user)
                uid, gid = user_info.pw_uid, user_info.pw_gid
                for root, dirs, files in os.walk(config_bin):
                    os.chown(root, uid, gid)
                    for file in files:
                        os.chown(os.path.join(root, file), uid, gid)
                    for dir in dirs:
                        os.chown(os.path.join(root, dir), uid, gid)
            print(f"{KaliStyle.SUCCESS} Cleanup completed")
            return True
        except Exception as e:
            logging.warning(f"Could not set proper ownership: {str(e)}")
            print(f"{KaliStyle.ERROR} Cleanup failed: {str(e)}")
            return False

    def rollback(self):
        print(f"{KaliStyle.WARNING} Rolling back changes...")
        for action in reversed(self.actions_taken):
            try:
                if action['type'] == 'file_copy' or action['type'] == 'file_create':
                    if os.path.exists(action['dest']):
                        if action['dest'].startswith('/usr') or action['dest'].startswith('/root'):
                            self.run_command(['rm', '-f', action['dest']], sudo=True, quiet=True)
                        else:
                            os.remove(action['dest'])
                        print(f"{KaliStyle.SUCCESS} Deleted {action['dest']}")
                elif action['type'] == 'dir_copy':
                    if os.path.exists(action['dest']):
                        if action['dest'].startswith('/usr') or action['dest'].startswith('/root'):
                            self.run_command(['rm', '-rf', action['dest']], sudo=True, quiet=True)
                        else:
                            shutil.rmtree(action['dest'])
                        print(f"{KaliStyle.SUCCESS} Deleted directory {action['dest']}")
                elif action['type'] == 'backup':
                    if os.path.exists(action['backup']):
                        if os.path.exists(action['original']):
                            shutil.rmtree(action['original'])
                        shutil.move(action['backup'], action['original'])
                        print(f"{KaliStyle.SUCCESS} Restored {action['original']} from backup")
                elif action['type'] == 'package':
                    print(f"{KaliStyle.WARNING} Removing package {action['pkg']}...")
                    self.run_command(['apt', 'remove', '-y', action['pkg']], sudo=True, quiet=True)
                elif action['type'] == 'file_append':
                    if os.path.exists(action['dest']) and 'content' in action:
                        with open(action['dest'], 'r', encoding='utf-8') as f:
                            content = f.read()
                        new_content = content.replace(action['content'], '')
                        with open(action['dest'], 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"{KaliStyle.SUCCESS} Removed content from {action['dest']}")
            except Exception as e:
                print(f"{KaliStyle.WARNING} Could not rollback {action}: {str(e)}")
                logging.error(f"Rollback error: {str(e)}")
        print(f"{KaliStyle.SUCCESS} Rollback completed")

    def set_panel_background_color(self):
        print(f"\n{KaliStyle.INFO} Setting panel background color to #0E0F12 with alpha 0.95...")
        try:
            # Asumir panel-1; si necesitas dinámico, query /panels para obtener el ID
            self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/panels/panel-1/background-style', '-t', 'int', '-s', '1', '--create'])
            args = ['xfconf-query', '-c', 'xfce4-panel', '-p', '/panels/panel-1/background-rgba', '--create', '-a',
                    '-t', 'double', '-s', '0.0549', '-t', 'double', '-s', '0.0588',
                    '-t', 'double', '-s', '0.0706', '-t', 'double', '-s', '0.95']
            self.run_command(args)
            print(f"{KaliStyle.SUCCESS} Panel color set")
            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error setting panel color: {str(e)}")
            return False

    def set_workspace_miniature_view(self):
        print(f"\n{KaliStyle.INFO} Setting workspace switcher to miniature view with 2 rows...")
        try:
            # Encontrar ID del pager (workspace switcher)
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l', '-v'])
            if not success:
                return False

            pager_id = None
            for line in output.splitlines():
                parts = line.split(maxsplit=1)
                if len(parts) == 2 and parts[1].strip() == 'pager':
                    match = re.match(r'/plugins/plugin-(\d+)', parts[0])
                    if match:
                        pager_id = match.group(1)
                        break

            if not pager_id:
                print(f"{KaliStyle.WARNING} Workspace switcher plugin not found. Add it manually first.")
                return False

            # Configurar vista en miniatura
            success1, _ = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{pager_id}/miniature-view', '-t', 'bool', '-s', 'true', '--create'])
            
            # CORRECCIÓN: Configurar número de filas a 2
            success2, _ = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{pager_id}/rows', '-t', 'int', '-s', '2', '--create'])
            
            # También asegurar que el número de workspaces sea múltiplo de 2 para que se vea bien
            # Verificar cuántos workspaces hay actualmente
            success_ws, ws_output = self.run_command(['xfconf-query', '-c', 'xfwm4', '-p', '/general/workspace_count'])
            if success_ws:
                current_workspaces = int(ws_output.strip())
                print(f"{KaliStyle.INFO} Current workspaces: {current_workspaces}")
                
                # Si no es par, ajustar a 4 workspaces para que se vea bien en 2 filas
                if current_workspaces % 2 != 0 or current_workspaces < 2:
                    self.run_command(['xfconf-query', '-c', 'xfwm4', '-p', '/general/workspace_count', '-t', 'int', '-s', '4'])
                    print(f"{KaliStyle.INFO} Adjusted workspaces to 4 for better layout")

            if success1 and success2:
                print(f"{KaliStyle.SUCCESS} Workspace switcher set to miniature view with 2 rows")
                return True
            else:
                print(f"{KaliStyle.ERROR} Failed to configure workspace switcher")
                return False
                
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error setting workspace view: {str(e)}")
            logging.error(f"Error in set_workspace_miniature_view: {str(e)}")
            return False

    def set_menu_logo(self):
        print(f"\n{KaliStyle.INFO} Setting menu logo...")
        logo_source = os.path.join(self.script_dir, "logo-menu.png")
        logo_dest = os.path.join(self.pictures_dir, "logo-menu.png")
        
        try:
            if not os.path.exists(logo_source):
                print(f"{KaliStyle.ERROR} logo-menu.png not found")
                return False
            
            shutil.copy2(logo_source, logo_dest)
            self.actions_taken.append({'type': 'file_copy', 'dest': logo_dest})
            print(f"{KaliStyle.SUCCESS} Logo copied to {logo_dest}")
            
            # Find whiskermenu plugin ID
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l', '-v'])
            if not success:
                print(f"{KaliStyle.WARNING} Could not find plugins")
                return False

            menu_id = None
            for line in output.splitlines():
                parts = line.split(maxsplit=1)
                if len(parts) == 2 and parts[1].strip() == 'whiskermenu':
                    match = re.match(r'/plugins/plugin-(\d+)', parts[0])
                    if match:
                        menu_id = match.group(1)
                        break

            if not menu_id:
                print(f"{KaliStyle.WARNING} Whiskermenu plugin not found. Ensure it's added to the panel.")
                return False

            # Set button-icon to the logo path
            self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{menu_id}/button-icon', '-t', 'string', '-s', logo_dest, '--create'])
            # Optionally hide title if desired
            self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{menu_id}/button-title', '-t', 'string', '-s', '', '--create'])
            print(f"{KaliStyle.SUCCESS} Menu logo set")
            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error setting menu logo: {str(e)}")
            return False

    def run(self):
        checks = [
            (self.check_os, "Operating System"),
            (self.check_sudo_privileges, "Sudo Privileges"),
            (self.check_required_files, "Required Files"),
            (self.check_xfce_environment, "XFCE Environment")
        ]
        
        for check_func, description in checks:
            if not check_func():
                print(f"{KaliStyle.ERROR} {description} check failed")
                return False

        os.system('clear')
        self.show_banner()

        tasks = [
            (self.install_additional_packages, "Additional packages installation"),
            (self.setup_dotfiles, "Dotfiles setup"),
            (self.setup_aliases, "Aliases setup"),
            (self.install_extract_ports, "extractPorts installation"),
            (self.install_fonts, "Fonts installation"),
            (self.install_sudo_plugin, "Sudo plugin installation"),
            (self.install_terminator_config, "Terminator configuration"),
            (self.install_kitty_config, "Kitty configuration"),
            (self.configure_keyboard_shortcuts, "Keyboard shortcuts configuration"),
            (self.remove_workspace_delete_shortcut, "Removing workspace delete shortcut"),
            (self.disable_action_buttons_lock_screen, "Disabling lock screen in action buttons"),
            (self.setup_wallpaper, "Wallpaper setup"),
            (self.setup_browser_wallpaper, "Browser wallpaper setup"),
            (self.setup_ctf_folders, "CTF folders setup"),
            (self.copy_files, "Copying configuration files"),
            (self.set_permissions, "Setting file permissions"),
            (self.add_settarget_function, "Adding settarget function"),
            (self.remove_existing_genmon, "Removing existing genmon plugins"),
            (lambda: self.add_plugins_to_panel(*self.find_and_remove_cpugraph()), "Adding panel plugins"),
            (self.set_panel_background_color, "Panel background color setup"),
            (self.set_workspace_miniature_view, "Workspace miniature view setup"),
            (self.set_menu_logo, "Menu logo setup"),
            (self.disable_desktop_icons, "Disabling desktop icons"),
            (self.configure_clock, "Clock configuration"),
            (self.restart_panel, "Restarting XFCE panel")
        ]

        total_tasks = len(tasks)

        try:
            for i, (task, description) in enumerate(tasks, 1):
                print(f"\n{KaliStyle.GREY}────────────────────────────────────────{KaliStyle.RESET}")
                print(f"{KaliStyle.INFO} ({i}/{total_tasks}) Starting {description}...")
                if not task():
                    print(f"{KaliStyle.ERROR} Error in {description}")
                    self.rollback()
                    self.cleanup()
                    return False
                time.sleep(0.5)
            print()

            self.show_final_message()
            self.cleanup()
            logging.info("Installation completed successfully")
            return True

        except KeyboardInterrupt:
            print(f"\n{KaliStyle.WARNING} Installation interrupted")
            self.rollback()
            self.cleanup()
            return False
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error: {str(e)}")
            logging.error(f"General error in run: {str(e)}")
            self.rollback()
            self.cleanup()
            return False

if __name__ == "__main__":
    try:
        installer = CombinedInstaller()
        success = installer.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{KaliStyle.WARNING} Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{KaliStyle.ERROR} Critical error: {str(e)}")
        sys.exit(1)