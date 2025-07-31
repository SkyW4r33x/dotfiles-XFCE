#!/bin/sh

ip="$(/usr/sbin/ifconfig eth0 | grep "inet " | awk '{print $2}')"

if [ "${ip}" != "" ]; then
  printf "<icon>network-vpn-symbolic</icon>"
  printf "<txt>${ip}</txt>"
  if command -v xclip; then
    printf "<txtclick>sh -c 'printf ${ip} | xclip -selection clipboard'</txtclick>"
    printf "<tool>VPN IP (click to copy)</tool>"
  else
    printf "<tool>VPN IP (install xclip to copy to clipboard)</tool>"
  fi
else
  printf "<icon>network-vpn-symbolic</icon>"
  printf "<txt>Sin Internet</txt>"
fi
