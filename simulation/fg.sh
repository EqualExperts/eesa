#!/bin/sh

nice /Applications/FlightGear.app/Contents/MacOS/fgfs \
    --native-fdm=socket,in,10,,5503,udp \
    --fdm=external \
    --aircraft=Rascal110-JSBSim \
    --fg-aircraft="aircraft" \
    --airport=YKRY \
    --geometry=650x550 \
    --bpp=32 \
    --disable-anti-alias-hud \
    --disable-hud-3d \
    --disable-horizon-effect \
    --timeofday=noon \
    --disable-sound \
    --disable-fullscreen \
    --disable-random-objects \
    --disable-ai-models \
    --fog-disable \
    --disable-specular-highlight \
    --disable-anti-alias-hud \
    --wind=0@0 \
    $*
