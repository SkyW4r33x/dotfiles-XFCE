#!/bin/bash
 
ip_address=$(cat $HOME/.config/bin/target/target.txt | awk '{print $1}')
machine_name=$(cat $HOME/.config/bin/target/target.txt | awk '{print $2}')
 
if [ $ip_address ] && [ $machine_name ]; then
    printf "<icon>mark-location</icon>"
    printf "<txt>$ip_address - $machine_name</txt>"
  if command -v xclip; then
    printf "<txtclick>sh -c 'printf ${ip_address} | xclip -selection clipboard'</txtclick>"
    printf "<tool>VPN IP (click to copy)</tool>"
  else
    printf "<tool>VPN IP (install xclip to copy to clipboard)</tool>"
  fi
else
  printf "<icon>mark-location</icon>"
  printf "<txt>Sin Objetivo</txt>"
fi
