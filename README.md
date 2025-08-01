![Banner](https://i.imgur.com/CS0EsS3.png)  
**Created by SkyW4r33x**

This repository provides an automated script to install and configure **SkyW4r33x**, a customized XFCE desktop environment tailored for **Debian-based systems** like **Kali Linux**. It includes XFCE panel plugins, development tools, terminal configurations, dotfiles, and Kali-inspired visual customizations optimized for pentesters and technical users.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Recent Updates](#recent-updates)
   - [Core Improvements](#core-improvements)
   - [Visual Enhancements](#visual-enhancements)
   - [New Panel Plugins](#new-panel-plugins)
5. [Key Features](#key-features)
   - [XFCE Panel Plugins](#xfce-panel-plugins)
   - [Included Tools](#included-tools)
   - [ZSH Aliases](#zsh-aliases)
   - [Custom Command Visuals](#custom-command-visuals)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
   - [XFCE Shortcuts](#xfce-shortcuts)
   - [Kitty Terminal Shortcuts](#kitty-terminal-shortcuts)
7. [Visual Previews](#visual-previews)
   - [Wallpaper](#wallpaper)
   - [Desktop](#desktop)
   - [Browser Start Page](#browser-start-page)
   - [ZSH Prompt](#zsh-prompt)
   - [LSD and SetTarget](#lsd-and-settarget)
   - [Terminals](#terminals)
   - [Neovim](#neovim)
8. [Changelog](#changelog)
9. [Final Notes](#final-notes)

## Overview

The **SkyW4r33x XFCE Setup** is designed to streamline the configuration of a lightweight, efficient, and visually appealing XFCE desktop environment. It automates the installation of tools, dotfiles, and customizations, including panel plugins for real-time network monitoring, a tailored ZSH shell, and a modern Neovim setup with NvChad. The setup is ideal for security researchers, developers, and CTF enthusiasts.

## ⚙️ Prerequisites

- **Operating System**: Debian-based (e.g., Kali Linux)
- **Desktop Environment**: XFCE (version 4.18 or higher recommended)
- **Privileges**: `sudo` access for system configuration
- **Minimum Dependencies**:
  - `git`, `python3`, `xfce4-panel`, `xfconf` (automatically verified)
- **Internet Connection**: Required for downloading dependencies and resources

## ⚙️ Installation

Follow these steps to install the SkyW4r33x XFCE Setup:

1. **Update the system** (recommended):
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/SkyW4r33x/dotfiles-XFCE
   cd dotfiles-XFCE
   ```

3. **Grant execute permissions to the installer**:
   ```bash
   chmod +x install.py
   ```

4. **Run the installer**:
   ```bash
   ./install.py
   ```

5. **Follow on-screen instructions**:
   - Dependency verification
   - Step-by-step installation with a console interface
   - Automatic XFCE panel restart (or manual session restart if needed)

## ⚙️ Recent Updates

### Core Improvements
- **Neovim 0.11**: Upgraded with enhanced features:
  - Simplified and improved LSP configuration
  - Native autocompletion
  - Enhanced hover documentation
  - Improved tree-sitter performance
  - Better emoji support
  - Upgraded integrated terminal emulator

### Visual Enhancements
- **New Desktop Wallpaper**: Updated for a modern aesthetic
- **Custom Browser Start Page**: Synchronized background
- **Redesigned System Commands**:
  - `updateAndClean`: Revamped visual interface
  - `dockerClean`: New presentation style
- **XFCE Panel Customizations**:
  - Dark background (#0E0F12, 0.95 alpha)
  - LCD-style 12-hour clock
  - Miniature workspace view with 2 rows
  - Custom menu logo

### New Panel Plugins
- **Integrated Plugins**:
  - `Local IP Info`: Displays local IP, copyable with a click
  - `Target Info`: Shows target IP, copyable with a click
  - `VPN IP`: Displays VPN IP, copyable with a click

## ⚙️ Key Features

### XFCE Panel Plugins
- **Generic Monitor (Genmon) Plugins**: Execute dynamic scripts (`target.sh`, `vpnip.sh`, `ethernet.sh`) for real-time network information.
- **Extras**:
  - Clickable IP displays for quick clipboard copying
  - Configurable update intervals (0.25s)
  
  ![Genmon Plugins](https://i.imgur.com/L3vgAIZ.mp4)

### Included Tools
| Tool         | Description                              |
|--------------|------------------------------------------|
| `zsh`        | Advanced shell with custom `.zshrc`      |
| `neovim`     | Modern editor with NvChad configuration  |
| `fzf`        | Fuzzy file finder for quick navigation   |
| `lsd` / `bat`| Enhanced `ls` and `cat` alternatives     |
| `terminator` | Tiled terminal with custom layout        |
| `kitty`      | Lightweight terminal with transparency   |
| `flameshot`  | Interactive screenshot tool              |
| `keepassxc`  | Secure password manager                  |
| `nautilus`   | Advanced file manager                    |

### ZSH Aliases
| Alias          | Function                                      |
|----------------|----------------------------------------------|
| `updateAndClean`| Updates and cleans the system               |
| `mkt`          | Creates `nmap`, `content`, `exploits` folders |
| `dockerClean`  | Cleans Docker containers, images, networks   |
| `rmk <file>`   | Securely deletes files with overwrite        |
| `target <IP>`  | Sets current target IP                      |
| `<username>`   | Switches from root to normal user           |
| `vulnhub`, `HTB`, `DKL` | Navigates to CTF machine folders  |

### Custom Command Visuals
- **UpdateAndClean**: Enhanced visual interface  
  ![UpdateAndClean](https://imgur.com/n6Dz9lm.png)
- **DockerClean**: Modernized presentation  
  ![DockerClean](https://imgur.com/IjYaDGd.png)

## ⌨️ Keyboard Shortcuts

### XFCE Shortcuts
| Shortcut             | Action              |
|----------------------|---------------------|
| `Super + Enter`      | Open Terminator     |
| `Super + Shift + F`  | Open Firefox        |
| `Super + Shift + O`  | Open Obsidian       |
| `Super + Shift + B`  | Open Burpsuite      |
| `Super + E`          | Open Nautilus       |
| `Print`              | Launch Flameshot GUI|

### Kitty Terminal Shortcuts
| Shortcut                  | Action                          |
|---------------------------|---------------------------------|
| `Ctrl + Shift + E / O`    | Vertical / horizontal splits    |
| `Ctrl + Shift + T / Q / W`| New tab / close tab / close pane|
| `F1 / F2`                 | Copy / paste                    |
| `Alt + Arrows`            | Navigate panes                  |
| `Ctrl + Shift + O + ↑/↓`  | Adjust opacity                  |
| `Ctrl + I`                | Set tab title                   |

## 📸 Visual Previews

### Wallpaper
![Wallpaper](https://imgur.com/l3ov8K9.jpeg)

### Desktop
![Desktop](https://i.imgur.com/cjJOwKM.jpeg)

### Browser Start Page
![Browser Background](https://i.imgur.com/17W8fAR.jpeg)

### ZSH Prompt
| State        | Preview                           |
|--------------|-----------------------------------|
| ✔ Success     | ![OK](https://i.imgur.com/fNuGtBM.png) |
| ✘ Error        | ![Error](https://i.imgur.com/oabJiCu.png) |
| VPN (Update) | ![VPN](https://imgur.com/JuSeipc.png) |

Dynamic colors based on command status. Font: **JetBrainsMono**.

### LSD and SetTarget
- `settarget <ip> <name>` updates **Victim IP** and **Target Machine** in the terminal.
- Prompt alternates between **L3VIATH4N** and **H4PPY H4CK1NG**.  
![LSD](https://i.imgur.com/LJPQ1hf.png)

### Terminals
- **Terminator**:  
  ![Terminator](https://i.imgur.com/LZ9EwiH.png)
- **Kitty**:  
  ![Kitty](https://i.imgur.com/HNVdVLs.png)

### Neovim
- **Neovim 0.11 with NvChad**:
  - Improved LSP and autocompletion
  - Optimized tree-sitter performance
  - Enhanced hover documentation
  - Upgraded terminal emulation  
  ![Neovim](https://i.imgur.com/UoqShDn.png)

## Changelog

### Kali Linux 2025.2 - Major Update
- **Neovim 0.11**: Enhanced LSP, performance, and terminal
- **Redesigned Commands**: `updateAndClean`, `dockerClean`
- **Bug Fixes**: Improved stability and performance
- **New Panel Plugins**: `Local IP Info`, `Target Info`, `VPN IP`
- **XFCE Enhancements**: Disabled desktop icons, LCD clock, workspace miniature view, custom menu logo

## Final Notes

- The script is modular, allowing easy addition of plugins or tools.
- Optimized for pentesters, balancing efficiency and aesthetics.
- **Neovim 0.11** offers a superior development experience with native LSP.
- If the panel appears corrupted, run `xfce4-panel --restart` or log out/in.
- Click IPs in the panel to copy to the clipboard.
- Use `settarget <IP> <Name>` (e.g., `settarget 192.168.1.100 WebServer`) or `settarget` to clear.

# 🧠 H4PPY H4CK1NG!