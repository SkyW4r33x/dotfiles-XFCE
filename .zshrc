# ~/.zshrc file for zsh interactive shells.
# see /usr/share/doc/zsh/examples/zshrc for examples

setopt autocd              # change directory just by typing its name
#setopt correct            # auto correct mistakes
setopt interactivecomments # allow comments in interactive mode
setopt magicequalsubst     # enable filename expansion for arguments of the form ‘anything=expression’
setopt nonomatch           # hide error message if there is no match for the pattern
setopt notify              # report the status of background jobs immediately
setopt numericglobsort     # sort filenames numerically when it makes sense
setopt promptsubst         # enable command substitution in prompt

WORDCHARS='_-' # Don't consider certain characters part of the word

# hide EOL sign ('%')
PROMPT_EOL_MARK=""

# configure key keybindings
bindkey -e                                        # emacs key bindings
bindkey ' ' magic-space                           # do history expansion on space
bindkey '^U' backward-kill-line                   # ctrl + U
bindkey '^[[3;5~' kill-word                       # ctrl + Supr
bindkey '^[[3~' delete-char                       # delete
bindkey '^[[1;5C' forward-word                    # ctrl + ->
bindkey '^[[1;5D' backward-word                   # ctrl + <-
bindkey '^[[5~' beginning-of-buffer-or-history    # page up
bindkey '^[[6~' end-of-buffer-or-history          # page down
bindkey '^[[H' beginning-of-line                  # home
bindkey '^[[F' end-of-line                        # end
bindkey '^[[Z' undo                               # shift + tab undo last action

# enable completion features
autoload -Uz compinit
compinit -d ~/.cache/zcompdump
zstyle ':completion:*:*:*:*:*' menu select
zstyle ':completion:*' auto-description 'specify: %d'
zstyle ':completion:*' completer _expand _complete
zstyle ':completion:*' format 'Completing %d'
zstyle ':completion:*' group-name ''
zstyle ':completion:*' list-colors ''
zstyle ':completion:*' list-prompt %SAt %p: Hit TAB for more, or the character to insert%s
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'
zstyle ':completion:*' rehash true
zstyle ':completion:*' select-prompt %SScrolling active: current selection at %p%s
zstyle ':completion:*' use-compctl false
zstyle ':completion:*' verbose true
zstyle ':completion:*:kill:*' command 'ps -u $USER -o pid,%cpu,tty,cputime,cmd'

# History configurations
HISTFILE=~/.zsh_history
HISTSIZE=1000
SAVEHIST=2000
setopt hist_expire_dups_first # delete duplicates first when HISTFILE size exceeds HISTSIZE
setopt hist_ignore_dups       # ignore duplicated commands history list
setopt hist_ignore_space      # ignore commands that start with space
setopt hist_verify            # show command with history expansion to user before running it
#setopt share_history         # share command history data

# force zsh to show the complete history
alias history="history 0"

# configure `time` format
TIMEFMT=$'\nreal\t%E\nuser\t%U\nsys\t%S\ncpu\t%P'

# make less more friendly for non-text input files, see lesspipe(1)
#[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color|*-256color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
        # We have color support; assume it's compliant with Ecma-48
        # (ISO/IEC-6429). (Lack of such support is extremely rare, and such
        # a case would tend to support setf rather than setaf.)
        color_prompt=yes
    else
        color_prompt=
    fi
fi

# Función para detectar VPN activa y obtener IP
vpn_status() {
  if ip addr show tun0 &>/dev/null; then
    vpn_ip=$(ip addr show tun0 | awk '/inet / {print $2}' | cut -d'/' -f1 | head -1)
    [[ -n "$vpn_ip" ]] && echo -n "-[%F{white}%B${vpn_ip}%b%F{%(#.blue.green)}]" || echo -n ""
  else
    echo -n ""
  fi
}

configure_prompt() {
    prompt_symbol=㉿
    prompt_folder=󰋜 
    prompt_kali=   
    # Skull emoji for root terminal
    #[ "$EUID" -eq 0 ] && prompt_symbol=💀
    case "$PROMPT_ALTERNATIVE" in
        twoline)
            # Prompt original con segmento VPN dinámico
            PROMPT=$'%F{%(#.blue.green)}┌──[%F{white}'$prompt_kali$'%F{%(#.blue.green)} ]-(%B%F{%(#.red.blue)}%n%b%F{%(#.blue.green)})%{$(vpn_status)%}-[%B%F{reset}%(6~.%-1~/…/%4~.%5~)%b%F{%(#.blue.green)}]-[%(?.%F{green}✔.%F{red}✘ %?)%F{%(#.blue.green)}]\n└──╼%B%(#.%F{red}#.%F{blue}$)%b%F{reset} '
            # Right-side prompt with exit codes and background processes
            #RPROMPT=$'%(?.. %? %F{red}%B⨯%b%F{reset})%(1j. %j %F{yellow}%B⚙%b%F{reset}.)'
            ;;
        oneline)
            PROMPT=$'${debian_chroot:+($debian_chroot)}${VIRTUAL_ENV:+($(basename $VIRTUAL_ENV))}%B%F{%(#.red.blue)}%n@%m%b%F{reset}:%B%F{%(#.blue.green)}%~%b%F{reset}%(#.#.$) '
            RPROMPT=
            ;;
        backtrack)
            PROMPT=$'${debian_chroot:+($debian_chroot)}${VIRTUAL_ENV:+($(basename $VIRTUAL_ENV))}%B%F{red}%n@%m%b%F{reset}:%B%F{blue}%~%b%F{reset}%(#.#.$) '
            RPROMPT=
            ;;
    esac
    unset prompt_symbol
}

# The following block is surrounded by two delimiters.
# These delimiters must not be modified. Thanks.
# START KALI CONFIG VARIABLES
PROMPT_ALTERNATIVE=twoline
NEWLINE_BEFORE_PROMPT=yes
# STOP KALI CONFIG VARIABLES

if [ "$color_prompt" = yes ]; then
    # override default virtualenv indicator in prompt
    VIRTUAL_ENV_DISABLE_PROMPT=1

    configure_prompt

    # enable syntax-highlighting
    if [ -f /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]; then
        . /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
        ZSH_HIGHLIGHT_HIGHLIGHTERS=(main brackets pattern)
        ZSH_HIGHLIGHT_STYLES[default]=none
        ZSH_HIGHLIGHT_STYLES[unknown-token]=underline
        ZSH_HIGHLIGHT_STYLES[reserved-word]=fg=cyan,bold
        ZSH_HIGHLIGHT_STYLES[suffix-alias]=fg=green,underline
        ZSH_HIGHLIGHT_STYLES[global-alias]=fg=green,bold
        ZSH_HIGHLIGHT_STYLES[precommand]=fg=green,underline
        ZSH_HIGHLIGHT_STYLES[commandseparator]=fg=blue,bold
        ZSH_HIGHLIGHT_STYLES[autodirectory]=fg=green,underline
        ZSH_HIGHLIGHT_STYLES[path]=bold
        ZSH_HIGHLIGHT_STYLES[path_pathseparator]=
        ZSH_HIGHLIGHT_STYLES[path_prefix_pathseparator]=
        ZSH_HIGHLIGHT_STYLES[globbing]=fg=blue,bold
        ZSH_HIGHLIGHT_STYLES[history-expansion]=fg=blue,bold
        ZSH_HIGHLIGHT_STYLES[command-substitution]=none
        ZSH_HIGHLIGHT_STYLES[command-substitution-delimiter]=fg=magenta,bold
        ZSH_HIGHLIGHT_STYLES[process-substitution]=none
        ZSH_HIGHLIGHT_STYLES[process-substitution-delimiter]=fg=magenta,bold
        ZSH_HIGHLIGHT_STYLES[single-hyphen-option]=fg=green
        ZSH_HIGHLIGHT_STYLES[double-hyphen-option]=fg=green
        ZSH_HIGHLIGHT_STYLES[back-quoted-argument]=none
        ZSH_HIGHLIGHT_STYLES[back-quoted-argument-delimiter]=fg=blue,bold
        ZSH_HIGHLIGHT_STYLES[single-quoted-argument]=fg=yellow
        ZSH_HIGHLIGHT_STYLES[double-quoted-argument]=fg=yellow
        ZSH_HIGHLIGHT_STYLES[dollar-quoted-argument]=fg=yellow
        ZSH_HIGHLIGHT_STYLES[rc-quote]=fg=magenta
        ZSH_HIGHLIGHT_STYLES[dollar-double-quoted-argument]=fg=magenta,bold
        ZSH_HIGHLIGHT_STYLES[back-double-quoted-argument]=fg=magenta,bold
        ZSH_HIGHLIGHT_STYLES[back-dollar-quoted-argument]=fg=magenta,bold
        ZSH_HIGHLIGHT_STYLES[assign]=none
        ZSH_HIGHLIGHT_STYLES[redirection]=fg=blue,bold
        ZSH_HIGHLIGHT_STYLES[comment]=fg=black,bold
        ZSH_HIGHLIGHT_STYLES[named-fd]=none
        ZSH_HIGHLIGHT_STYLES[numeric-fd]=none
        ZSH_HIGHLIGHT_STYLES[arg0]=fg=cyan
        ZSH_HIGHLIGHT_STYLES[bracket-error]=fg=red,bold
        ZSH_HIGHLIGHT_STYLES[bracket-level-1]=fg=blue,bold
        ZSH_HIGHLIGHT_STYLES[bracket-level-2]=fg=green,bold
        ZSH_HIGHLIGHT_STYLES[bracket-level-3]=fg=magenta,bold
        ZSH_HIGHLIGHT_STYLES[bracket-level-4]=fg=yellow,bold
        ZSH_HIGHLIGHT_STYLES[bracket-level-5]=fg=cyan,bold
        ZSH_HIGHLIGHT_STYLES[cursor-matchingbracket]=standout
    fi
else
    PROMPT='${debian_chroot:+($debian_chroot)}%n@%m:%~%(#.#.$) '
fi
unset color_prompt force_color_prompt

toggle_oneline_prompt(){
    if [ "$PROMPT_ALTERNATIVE" = oneline ]; then
        PROMPT_ALTERNATIVE=twoline
    else
        PROMPT_ALTERNATIVE=oneline
    fi
    configure_prompt
    zle reset-prompt
}
zle -N toggle_oneline_prompt
bindkey ^P toggle_oneline_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*|Eterm|aterm|kterm|gnome*|alacritty)
    TERM_TITLE=$'\e]0;${debian_chroot:+($debian_chroot)}${VIRTUAL_ENV:+($(basename $VIRTUAL_ENV))}%n@%m: %~\a'
    ;;
*)
    ;;
esac

precmd() {
    # Print the previously configured title
    print -Pnr -- "$TERM_TITLE"

    # Print a new line before the prompt, but only if it is not the first line
    if [ "$NEWLINE_BEFORE_PROMPT" = yes ]; then
        if [ -z "$_NEW_LINE_BEFORE_PROMPT" ]; then
            _NEW_LINE_BEFORE_PROMPT=1
        else
            print ""
        fi
    fi
}

# enable color support of ls, less and man, and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    export LS_COLORS="$LS_COLORS:ow=30;44:" # fix ls color for folders with 777 permissions

    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
    alias diff='diff --color=auto'
    alias ip='ip --color=auto'

    export LESS_TERMCAP_mb=$'\E[1;31m'     # begin blink
    export LESS_TERMCAP_md=$'\E[1;36m'     # begin bold
    export LESS_TERMCAP_me=$'\E[0m'        # reset bold/blink
    export LESS_TERMCAP_so=$'\E[01;33m'    # begin reverse video
    export LESS_TERMCAP_se=$'\E[0m'        # reset reverse video
    export LESS_TERMCAP_us=$'\E[1;32m'     # begin underline
    export LESS_TERMCAP_ue=$'\E[0m'        # reset underline

    # Take advantage of $LS_COLORS for completion as well
    zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
    zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#)*=0=01;31'
fi

# some more ls aliases
### LS & TREE
#alias ll='ls -l'
#alias la='ls -A'
#alias l='ls -F'
#command -v lsd > /dev/null && alias ls='clear && lsd --group-dirs first --color=never' && \
# Utilidades de visualización de archivos y directorios
alias tree='lsd --tree'
if command -v colorls > /dev/null; then
    alias ls='colorls --sd --gs'
    alias tree='colorls --tree'
fi

# Mejoras de visualización de contenido
alias cat='batcat --theme=ansi --style=numbers,changes,header --pager=never'

# Personalización de comandos del sistema
alias neofetch='neofetch | lolcat'
alias rmh='rmk ~/.zsh_history'
alias fucking='sudo su'
alias _='sudo su'

# Operaciones de archivos
alias cp='cp -rfv'
alias rm='rm -rf'
alias mv='mv -iv'

# Navegación rápida
alias vulnhub='clear && cd /root/machines_vuln/vulnhub'
alias HTB='clear && cd /root/machines_vuln/HTB'
alias DKL='clear && cd /root/machines_vuln/DockerLabs'

# Herramientas específicas
alias extractPorts='/usr/bin/extractPorts.py'

# Mejoras de ayuda
alias -g -- --help='--help 2>&1 | bat --theme=ansi --language=help --style=plain'
#alias -g -- -h='-h 2>&1 | bat --theme=ansi --language=help --style=plain'

# Configuración del editor
if command -v vim > /dev/null; then
    alias vim='/opt/nvim-linux-x86_64/bin/nvim'
    alias vi='/opt/nvim-linux-x86_64/bin/nvim'
fi

alias target='setup_target'
# ---------------------------------------- Custom LSD ---------------------------------------- #
# Archivo para almacenar el estado del mensaje
MESSAGE_STATE_FILE="${HOME}/.lsd_message_state"

#directorio del usuario no root
get_user_home() {
  if [ "$(id -u)" -eq 0 ]; then
    echo "$(awk -F: '$3 >= 1000 && $3 != 65534 {print $6; exit}' /etc/passwd)"
  else
    echo "$HOME"
  fi
}

function _base_ls() {
  local command=$1
  clear
  local reset=$'\e[0m'
  local bold=$'\e[1m'
  local bright_red=$'\e[1;31m'
  local bright_cyan=$'\e[1;36m'
  local bright_yellow=$'\e[1;33m'
  local bright_blue=$'\e[94m'
  local green=$'\e[38;2;25;131;136m'
  local cursiva=$'\e[3m'
  local blink=$'\e[5m'

  #IP de la víctima
  get_victim_ip() {
    local user_home=$(get_user_home)
    local ip_file="${user_home}/.config/bin/target/target.txt"
    if [ -f "$ip_file" ] && [ -s "$ip_file" ]; then
      awk '{print $1}' "$ip_file" | grep -v '^$' || echo "Unknown"
    else
      echo "Unknown"
    fi
  }

  # nombre de la víctima
  get_victim_name() {
    local user_home=$(get_user_home)
    local ip_file="${user_home}/.config/bin/target/target.txt"
    if [ -f "$ip_file" ] && [ -s "$ip_file" ]; then
      awk '{print $2}' "$ip_file" | grep -v '^$' || echo "Anonymous"
    else
      echo "Anonymous"
    fi
  }

  # IP y nombre de la víctima
  local victim_ip=$(get_victim_ip)
  local victim_name=$(get_victim_name)

  toggle_message() {
    if [ ! -f "$MESSAGE_STATE_FILE" ] || [ "$(cat "$MESSAGE_STATE_FILE")" = "L3VIATH4N" ]; then
      echo "H4PPY H4CK1NG" > "$MESSAGE_STATE_FILE"
      echo "${bold}${bright_yellow}H4PPY H4CK1NG${reset}"
    else
      echo "L3VIATH4N" > "$MESSAGE_STATE_FILE"
      echo "${bold}${bright_yellow}  L3VIATH4N${reset}"
    fi
  }

  echo
  echo -e "${bold}${bright_blue}╔═════════════════════════════════════[ INFORMACION DEL SISTEMA ]════════════════════════════════╗${reset}"
  echo -e "${bold}${bright_blue}                                                                                                            ${reset}"
  echo -e "${bold}${bright_blue}       ${bright_cyan}[${bright_yellow}✓${reset}${bright_cyan}]${reset}${bold} Ubicación${reset}......: ${cursiva}${green} $(pwd)${reset}"
  echo -e "${bold}${bright_blue}       ${bright_cyan}[${bright_yellow}✓${reset}${bright_cyan}]${reset}${bold} Fecha/Hora${reset}.....: ${cursiva}${green}󰸗 $(date '+%Y-%m-%d')${reset}\t   │\t${bright_yellow}   [${bright_red}${blink}!${reset}${bright_yellow}]${reset}${bold} Máquina Víctima${reset}.: ${bright_red}${cursiva}󰯐 ${victim_name}${reset}"
  echo -e "${bold}${bright_blue}       ${bright_cyan}[${bright_yellow}✓${reset}${bright_cyan}]${reset}${bold} IP Atacante${reset}....: ${cursiva}${green}󰩠 $(hostname -I | awk '{print $1}')${reset}\t   │\t${bright_yellow}   [${bright_red}${blink}!${reset}${bright_yellow}]${reset}${bold} IP Víctima${reset}......: ${bright_red}${cursiva}󰩠 ${victim_ip}${reset}"
  echo -e "${bold}${bright_blue}       ${bright_cyan}[${bright_yellow}✓${reset}${bright_cyan}]${reset}${bold} Usuario${reset}........: ${cursiva}${green} $(whoami)${reset}"
  echo -e "${bold}${bright_blue}                                             $(toggle_message)                                            ${reset}"
  echo -e "${bold}${bright_blue}╠═════════════════════════════════════[ CONTENIDO DEL DIRECTORIO ]═══════════════════════════════╣${reset}"
  echo

  lsd $command --color=always --icon=auto

  echo
  echo -e "${bold}${bright_blue}╚════════════════════════════════════════════════════════════════════════════════════════════════╝${reset}"
}

function ls() {
  _base_ls ""
}

function la() {
  _base_ls "-lA"
}

function l() {
  _base_ls "-l"
}

function ll() {
  _base_ls "-l"
}
# ------------------------------- actualizar sistema completo --------------------------------------- #
updateAndClean() {
   
    local -r RESET='\033[0m'
    local -r BOLD='\033[1m'
    local -r DIM='\033[2m'
    
    local -r KALI_GREEN='\033[1;32m'          # Verde brillante (prompt principal)
    local -r KALI_RED='\033[1;31m'            # Rojo brillante (errores)
    local -r KALI_BLUE='\033[1;34m'           # Azul brillante (información)
    local -r KALI_CYAN='\033[1;36m'           # Cian brillante (destacados)
    local -r KALI_YELLOW='\033[1;33m'         # Amarillo brillante (advertencias)
    local -r KALI_PURPLE='\033[1;35m'         # Magenta brillante (procesos)
    local -r KALI_WHITE='\033[0;37m'          # Blanco normal (sin bold)
    local -r KALI_GRAY='\033[38;2;94;92;100m'
    local -r KALI_DARK_GREEN='\033[0;32m'     # Verde oscuro (texto normal)
    local -r KALI_DARK_RED='\033[0;31m'       # Rojo oscuro
    local -r KALI_DARK_BLUE='\033[0;34m'      # Azul oscuro
    
    local -r SUDO_COLOR='\033[38;2;94;189;171m'    # #5EBDAB
    local -r COMMAND_COLOR='\033[38;2;73;174;230m'  # #49AEE6
    local -r PARAM_COLOR='\033[38;2;94;189;171m'    # #5EBDAB para parámetros con guiones
    local -r OPERATOR_COLOR='\033[1;38;2;39;127;255m' # #277FFF en negrita para &&
    
    local -r SUCCESS="[+]"
    local -r ERROR="[-]"
    local -r INFO="[*]"
    local -r WORKING=" ▶"
    
    local error_count=0
    local start_time=$(date +%s)
    local temp_log="/tmp/update_clean_$(date +%s).log"
    
    cleanup_temp_files() {
        [[ -f "$temp_log" ]] && rm -f "$temp_log"
    }
    trap cleanup_temp_files EXIT
    
    colorear_comando() {
        local comando="$1"
        local colored_cmd=""
        
        local -a palabras
        palabras=(${=comando})
        
        for i in {1..${#palabras[@]}}; do
            local palabra="${palabras[$i]}"
            
            if [[ "$palabra" == "sudo" ]]; then
                colored_cmd+="${SUDO_COLOR}${palabra}${RESET}"
            elif [[ "$palabra" == "&&" ]]; then
                colored_cmd+="${OPERATOR_COLOR}${palabra}${RESET}"
            elif [[ "$palabra" =~ "^(apt|apt-get|aptitude|dpkg|updatedb)$" ]]; then
                colored_cmd+="${COMMAND_COLOR}${palabra}${RESET}"
            elif [[ "$palabra" =~ "^--?[a-zA-Z-]+$" ]]; then
                
                colored_cmd+="${PARAM_COLOR}${palabra}${RESET}"
            else
               colored_cmd+="${KALI_WHITE}${palabra}${RESET}"
            fi
            
            if [[ $i -lt ${#palabras[@]} ]]; then
                colored_cmd+=" "
            fi
        done
        
        echo -e "$colored_cmd"
    }
    
    verificar_sistema() {
        if ! command -v apt-get &> /dev/null; then
            echo -e "\n${KALI_RED}${ERROR}${RESET} ${KALI_RED}${BOLD}Este script requiere apt-get (Debian/Ubuntu)${RESET}"
            return 1
        fi
        
        if ! ping -c 1 8.8.8.8 &> /dev/null; then
            echo -e "\n${KALI_RED}${ERROR}${RESET} ${KALI_RED}${BOLD}Sin conexión a internet${RESET}"
            return 1
        fi
        
        return 0
    }
    
    mostrar_encabezado() {
        local titulo="$1"
        
        echo -e "${KALI_GREEN}${BOLD}▌${KALI_WHITE} ${titulo}${KALI_GREEN}${RESET}\n"
    }
    
    ejecutar_comando() {
        local comando="$1"
        local descripcion="$2"
        local paso="$3"
        local es_critico="${4:-false}"
        
        echo -e "${KALI_CYAN}${paso}${RESET} ${KALI_WHITE}${BOLD}${descripcion}${RESET}"
        echo -e "${KALI_GREEN}${WORKING}${RESET} ${KALI_WHITE}Ejecutando: $(colorear_comando "$comando")\n"
        
        local cmd_pid
        local exit_code
        
        if timeout 300 bash -c "$comando" 2>&1 | tee "$temp_log" | while IFS= read -r linea; do
            [[ -z "$linea" ]] && continue
            
            if [[ "$linea" =~ ^(Reading|Leyendo|Building|Construyendo|Calculating|Preparing) ]]; then
                echo -e "   ${KALI_BLUE}▶${RESET} ${KALI_WHITE}${linea}${RESET}"
            elif [[ "$linea" =~ ^(Get:|Obj:|Hit:|Des:|Ign:|Fetched) ]]; then
                echo -e "   ${KALI_DARK_GREEN}↓${RESET} ${KALI_WHITE}${linea}${RESET}"
            elif [[ "$linea" =~ ^(Setting|Configurando|Processing|Procesando|Configuring) ]]; then
                echo -e "   ${KALI_PURPLE}⚙${RESET} ${KALI_GRAY}${linea}${RESET}"
            elif [[ "$linea" =~ ^(Removing|Eliminando|Purging|Purgando) ]]; then
                echo -e "   ${KALI_RED}✗${RESET} ${KALI_WHITE}${linea}${RESET}"
            elif [[ "$linea" =~ ^(Installing|Instalando|Upgrading|Actualizando|Unpacking) ]]; then
                echo -e "   ${KALI_GREEN}+${RESET} ${KALI_GRAY}${linea}${RESET}"
            elif [[ "$linea" =~ (upgraded|actualizados|installed|instalados|removed|eliminados|Summary:|newly installed) ]]; then
                echo -e "   ${KALI_GREEN}✓${RESET} ${KALI_WHITE}${linea}${RESET}"
            elif [[ "$linea" =~ ^(WARNING:|W:|Warning|ADVERTENCIA|Warnings) ]]; then
                echo -e "   ${KALI_YELLOW}!${RESET} ${KALI_WHITE}${linea}${RESET}"
            elif [[ "$linea" =~ ^(E:|Error|ERROR|Failed|failed) ]]; then
                echo -e "   ${KALI_RED}!!${RESET} ${KALI_WHITE}${BOLD}${linea}${RESET}"
            elif [[ "$linea" =~ (up to date|All packages are up to date|Nothing to do) ]]; then
                echo -e "   ${KALI_GREEN}✓${RESET} ${KALI_WHITE}${linea}${RESET}"
            elif [[ "$linea" =~ ^(Need to get|Se necesita descargar) ]]; then
                echo -e "   ${KALI_CYAN}📦${RESET} ${KALI_WHITE}${linea}${RESET}"
            else
                echo -e "   ${KALI_GRAY}${linea}${RESET}"
            fi
        done; then
            exit_code=$?
            
            if [[ $exit_code -eq 0 ]] && ! grep -q "^E:" "$temp_log"; then
                echo -e "\n${KALI_GREEN}${SUCCESS}${RESET} ${KALI_WHITE}${descripcion} - ${KALI_GREEN}✓ COMPLETADO${RESET}"
            else
                echo -e "\n${KALI_RED}${ERROR}${RESET} ${KALI_WHITE}${descripcion} - ${KALI_RED}FALLÓ${RESET}"
                ((error_count++))
                
                if [[ "$es_critico" == "true" ]]; then
                    echo -e "${KALI_RED}${ERROR}${RESET} ${KALI_WHITE}Error crítico detectado${RESET}"
                    return 1
                fi
            fi
        else
            echo -e "\n${KALI_RED}${ERROR}${RESET} ${KALI_WHITE}${descripcion} - ${KALI_RED}TIMEOUT O ERROR${RESET}"
            ((error_count++))
            if [[ "$es_critico" == "true" ]]; then
                return 1
            fi
        fi
        
        echo -e "${KALI_DARK_BLUE}$(printf '─%.0s' {1..76})${RESET}\n"
    }
    
    clear
    if ! verificar_sistema; then
        return 1
    fi
    
    echo -e "${KALI_BLUE}${INFO}${RESET} ${KALI_WHITE}Verificación de privilegios de administrador${RESET}"
    echo -e "${KALI_GRAY}Se requiere acceso sudo para continuar con las operaciones${RESET}"
    
    if ! sudo -v; then
        echo -e "\n${KALI_RED}${ERROR}${RESET} ${KALI_RED}${BOLD}Autenticación fallida. Acceso denegado.${RESET}"
        return 1
    fi
    
    echo -e "${KALI_GREEN}${SUCCESS}${RESET} ${KALI_WHITE}Privilegios verificados correctamente${RESET}"
    sleep 1

    clear

    mostrar_encabezado "SISTEMA DE ACTUALIZACIÓN AUTOMÁTICA"

    echo -e "${KALI_BLUE}${INFO}${RESET} ${KALI_WHITE}Verificando actualizaciones disponibles...${RESET}"
    
    ejecutar_comando \
        "sudo apt-get update" \
        "Sincronizando repositorios de paquetes" \
        "[1/8]" \
        "true"
    
    local updates_available=$(apt list --upgradable 2>/dev/null | wc -l)
    if [[ $updates_available -le 1 ]]; then
        echo -e "${KALI_GREEN}${SUCCESS}${RESET} ${KALI_WHITE}No hay actualizaciones disponibles${RESET}"
    else
        echo -e "${KALI_BLUE}${INFO}${RESET} ${KALI_WHITE}Se encontraron $((updates_available-1)) actualizaciones disponibles${RESET}"
    fi
    
    ejecutar_comando \
        "sudo apt-get upgrade -y" \
        "Instalando actualizaciones disponibles" \
        "[2/8]"
    
    ejecutar_comando \
        "sudo apt-get dist-upgrade -y" \
        "Aplicando actualizaciones críticas del sistema" \
        "[3/8]"
    
    ejecutar_comando \
        "sudo apt-get autoremove --purge -y" \
        "Eliminando dependencias obsoletas" \
        "[4/8]"
    
    ejecutar_comando \
        "sudo apt-get autoclean" \
        "Limpiando archivos temporales parciales" \
        "[5/8]"
    
    ejecutar_comando \
        "sudo apt-get clean" \
        "Limpiando completamente caché de paquetes" \
        "[6/8]"
    
    if command -v updatedb &> /dev/null; then
        ejecutar_comando \
            "sudo updatedb" \
            "Reconstruyendo índice de archivos del sistema" \
            "[7/8]"
    else
        echo -e "${KALI_YELLOW}${INFO}${RESET} ${KALI_WHITE}updatedb no disponible, omitiendo paso [7/8]${RESET}\n"
    fi
    
    ejecutar_comando \
        "sudo apt-get check && sudo apt-get -f install -y" \
        "Verificando y reparando dependencias del sistema" \
        "[8/8]"
    
    return $error_count
}

# ------------------------------------- plugins ---------------------------------- #
source /usr/share/sudo-plugin/sudo.plugin.zsh
# ------------------------------------- Funciones Generales ---------------------------------- #

function mkt(){
        mkdir {nmap,content,exploits}
}

dockerClean() {
    # Colores auténticos de la terminal Kali Linux
    local -r RESET='\033[0m'
    local -r BOLD='\033[1m'
    local -r DIM='\033[2m'
    
    # Colores exactos de Kali Linux terminal
    local -r KALI_GREEN='\033[1;32m'          # Verde brillante (prompt principal)
    local -r KALI_RED='\033[1;31m'            # Rojo brillante (errores)
    local -r KALI_BLUE='\033[1;34m'           # Azul brillante (información)
    local -r KALI_CYAN='\033[1;36m'           # Cian brillante (destacados)
    local -r KALI_YELLOW='\033[1;33m'         # Amarillo brillante (advertencias)
    local -r KALI_PURPLE='\033[1;35m'         # Magenta brillante (procesos)
    local -r KALI_WHITE='\033[0;37m'          # Blanco normal (sin bold)
    local -r KALI_GRAY='\033[38;2;94;92;100m' # Gris (texto secundario)
    local -r KALI_DARK_GREEN='\033[0;32m'     # Verde oscuro (texto normal)
    local -r KALI_DARK_RED='\033[0;31m'       # Rojo oscuro
    local -r KALI_DARK_BLUE='\033[0;34m'      # Azul oscuro
    
    # Símbolos estilo terminal hacker
    local -r SUCCESS="[+]"
    local -r ERROR="[-]"
    local -r INFO="[*]"
    local -r WORKING="▐ ▶"
    
    # Variables de control
    local error_count=0
    local start_time=$(date +%s)
    
    mostrar_encabezado() {
        local titulo="$1"
        local ancho=76
        local padding=$(( (ancho - ${#titulo}) / 2 ))
        
        echo -e "\n${KALI_GREEN}${BOLD}╔$(printf '═%.0s' {1..74})╗${RESET}"
        echo -e "${KALI_GREEN}${BOLD}║$(printf '%*s' $padding)${KALI_WHITE}${titulo}${KALI_GREEN}$(printf '%*s' $((74-padding-${#titulo})))║${RESET}"
        echo -e "${KALI_GREEN}${BOLD}╚$(printf '═%.0s' {1..74})╝${RESET}\n"
    }
    
    ejecutar_comando() {
        local comando="$1"
        local descripcion="$2"
        local paso="$3"
        local ignorar_vacio="$4"  # Nuevo parámetro para manejar casos "ignore"
        
        echo -e "${KALI_CYAN}${paso}${RESET} ${KALI_WHITE}${BOLD}${descripcion}${RESET}"
        echo -e "${KALI_GREEN}${WORKING}${RESET} ${KALI_WHITE}Ejecutando: ${KALI_GRAY}${comando}${RESET}\n"
        
        # Ejecutar comando mostrando la salida en tiempo real con colores Kali
        if eval "$comando" 2>&1 | while IFS= read -r linea; do
            # Filtrar líneas vacías innecesarias
            [[ -z "$linea" ]] && continue
            
            # Colorear diferentes tipos de salida con colores Kali auténticos
            if [[ "$linea" =~ ^(Removing|Deleting|Pruning|Cleaning) ]]; then
                echo -e "   ${KALI_RED}✗${RESET} ${KALI_WHITE}${linea}${RESET}"
            elif [[ "$linea" =~ ^(Removed|Deleted|Untagged) ]]; then
                echo -e "   ${KALI_GREEN}✓${RESET} ${KALI_WHITE}${linea}${RESET}"
            elif [[ "$linea" =~ ^(WARNING|warning|Warning) ]]; then
                echo -e "   ${KALI_YELLOW}!${RESET} ${KALI_WHITE}${linea}${RESET}"
            elif [[ "$linea" =~ ^(ERROR|Error) ]]; then
                echo -e "   ${KALI_RED}!!${RESET} ${KALI_WHITE}${BOLD}${linea}${RESET}"
            else
                echo -e "   ${KALI_GRAY}${linea}${RESET}"
            fi
        done; then
            echo -e "\n${KALI_GREEN}${SUCCESS}${RESET} ${KALI_WHITE}${descripcion} - ${KALI_GREEN}✓ COMPLETADO${RESET}"
        else
            if [[ "$ignorar_vacio" == "ignore" ]] && eval "$comando" 2>&1 | grep -q "No such"; then
                echo -e "\n${KALI_YELLOW}!${RESET} ${KALI_WHITE}${descripcion} - ${KALI_YELLOW}No hay elementos para procesar${RESET}"
            else
                echo -e "\n${KALI_RED}${ERROR}${RESET} ${KALI_WHITE}${descripcion} - ${KALI_WHITE}ERROR${RESET}"
                echo -e "${KALI_YELLOW}   Detalles del error:${RESET}"
                eval "$comando" 2>&1 | sed 's/^/   /' | while IFS= read -r linea; do
                    echo -e "   ${KALI_RED}${linea}${RESET}"
                done
                ((error_count++))
                return 1
            fi
        fi
        echo -e "${KALI_DARK_BLUE}$(printf '─%.0s' {1..76})${RESET}\n"
    }
    
    # Verificar si Docker está en ejecución
    echo -e "\n${KALI_BLUE}${INFO}${RESET} ${KALI_WHITE}Verificación de estado de Docker${RESET}"
    echo -e "${KALI_GRAY}Se requiere que Docker esté en ejecución y permisos adecuados${RESET}"
    
    if ! docker info &>/dev/null; then
        echo -e "\n${KALI_RED}${ERROR}${RESET} ${KALI_RED}${BOLD}Error: Docker no está en ejecución o no tienes permisos suficientes.${RESET}"
        return 1
    fi
    
    echo -e "${KALI_GREEN}${SUCCESS}${RESET} ${KALI_WHITE}Docker verificado correctamente${RESET}"
    sleep 1
    
    clear
    
    mostrar_encabezado "SISTEMA DE LIMPIEZA DE DOCKER"
    
    echo -e "${KALI_BLUE}┌─ ${BOLD}${KALI_BLUE}INFORMACION DEL SISTEMA ${KALI_BLUE}─────────────────────────────────────────────────┐${RESET}" 
    echo -e "${KALI_BLUE}│${RESET} ${KALI_YELLOW}▐ ▶ ${RESET}Sistema: ${KALI_GRAY}$(lsb_release -ds 2>/dev/null || echo "$(uname -s) $(uname -r)")${RESET}"
    echo -e "${KALI_BLUE}│${RESET} ${KALI_YELLOW}▐ ▶ ${RESET}Usuario: ${KALI_GREEN}$(whoami)${RESET}"
    echo -e "${KALI_BLUE}└───────────────────────────────────────────────────────────────────────────┘${RESET}\n"
    
    ejecutar_comando \
        "sudo docker rm \$(docker ps -a -q) --force" \
        "Eliminando todos los contenedores" \
        "[1/5]" \
        "ignore"
    
    ejecutar_comando \
        "sudo docker network prune --force" \
        "Limpiando redes no utilizadas" \
        "[2/5]"
    
    ejecutar_comando \
        "sudo docker volume prune --force" \
        "Limpiando volúmenes no utilizados" \
        "[3/5]"
    
    ejecutar_comando \
        "sudo docker rmi \$(docker images -q) --force" \
        "Eliminando todas las imágenes" \
        "[4/5]" \
        "ignore"
    
    ejecutar_comando \
        "sudo docker images -q --filter \"dangling=true\" | xargs -r docker rmi --force" \
        "Eliminando imágenes huérfanas" \
        "[5/5]" \
        "ignore"
    
    return $error_count
}

# Borrado seguro de archivos
function rmk(){
        scrub -p dod $1
        shred -zun 10 -v $1
}

# Change cursor shape for different vi modes.
function zle-keymap-select {
  if [[ $KEYMAP == vicmd ]] || [[ $1 = 'block' ]]; then
    echo -ne '\e[1 q'
  elif [[ $KEYMAP == main ]] || [[ $KEYMAP == viins ]] || [[ $KEYMAP = '' ]] || [[ $1 = 'beam' ]]; then
    echo -ne '\e[3 q'
  fi
}
zle -N zle-keymap-select

# Start with beam shape cursor on zsh startup and after every command.
zle-line-init() { zle-keymap-select 'beam'}
# enable auto-suggestions based on the history
if [ -f /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh ]; then
    . /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh
    # change suggestion color
    ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=#363636'
fi


# Función para configurar IP y URL
function setup_target() {
  # Definir colores y estilos
  BOLD='\033[1m'
  RESET='\033[0m'
  GREEN='\033[0;32m'
  YELLOW='\033[0;33m'
  BLUE='\033[0;34m'
  RED='\033[0;31m'
  CYAN='\033[0;36m'

    if [ -z "$1" ]; then
        echo -e "${YELLOW}${BOLD}[!] ${RESET}Uso: ${CYAN}target ${YELLOW}<dirección_IP_objtivo>${RESET}"
        return 1
    fi

    export IP="$1"
    export URL="http://$1"
    clear
    echo -e "${RESET}"
    echo -e "${BLUE}${BOLD}[+]${RESET} Variables configuradas:"
    echo -e "    ${GREEN}[✓] ${RESET}IP....: $IP"
    echo -e "    ${GREEN}[✓] ${RESET}URL...: $URL"
}

