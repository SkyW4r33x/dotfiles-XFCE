#!/bin/sh

interface="$(ip tuntap show | cut -d : -f1 | head -n 1)"
ip="$(ip a s "${interface}" 2>/dev/null \
        | grep -o -P '(?<=inet )[0-9]{1,3}(\.[0-9]{1,3}){3}')"

if [ "${ip}" != "" ]; then
  printf "<icon>draw-cuboid</icon>"
  printf "<txt>${ip}</txt>"
  if command -v xclip; then
    printf "<txtclick>sh -c 'printf ${ip} | xclip -selection clipboard'</txtclick>"
    printf "<tool>VPN IP (click to copy)</tool>"
  else
    printf "<tool>VPN IP (install xclip to copy to clipboard)</tool>"
  fi
else
  printf "<icon>draw-cuboid</icon>"
  printf "<txt>Desconectado</txt>"
fi
