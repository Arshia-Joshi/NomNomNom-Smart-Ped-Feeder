#!/bin/bash
# start_stream.sh
# Streams Raspberry Pi camera using rpicam-vid into /dev/video10 (v4l2loopback)

VIDEO_NR=10
WIDTH=640
HEIGHT=480
FRAMERATE=20

# Load v4l2loopback
sudo modprobe -r v4l2loopback || true
sudo modprobe v4l2loopback devices=1 video_nr=${VIDEO_NR} card_label="RPiCamLoop" exclusive_caps=1

sleep 1

# Start rpicam-vid -> ffmpeg -> /dev/video10 in background
# Using codec yuv420 (rpicam supports yuv output). Adjust --width/--height if needed.
rpicam-vid --codec yuv420 -t 0 --width ${WIDTH} --height ${HEIGHT} --framerate ${FRAMERATE} -o - \
  | ffmpeg -f rawvideo -pix_fmt yuv420p -s ${WIDTH}x${HEIGHT} -i - -f v4l2 /dev/video${VIDEO_NR} >/dev/null 2>&1 &

echo "Streaming started to /dev/video${VIDEO_NR} (PID $!)"
