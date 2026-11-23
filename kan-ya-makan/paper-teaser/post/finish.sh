#!/bin/sh
# Grade + grain + mux -> renders/Kan_Paper_Teaser_Final.mp4 (240 frames, H.264 18 Mbps CBR, AAC 320k / 48 kHz)
cd "$(dirname "$0")/.." && mkdir -p renders
ffmpeg -loglevel error -y -i post/composite.tmp.mp4 -i audio/out/Kan_Paper_Final_Mix.wav \
 -filter_complex "[0:v]format=yuv444p,eq=contrast=1.04:saturation=0.95:gamma=0.98,colorbalance=rs=0.015:bs=-0.025:rm=0.01:bm=-0.015:bh=-0.01,vignette=angle=PI/5.5,noise=alls=4:allf=t,format=yuv420p[v]" \
 -map "[v]" -map 1:a -frames:v 240 -r 30 \
 -c:v libx264 -preset slow -profile:v high -level 4.2 -pix_fmt yuv420p -b:v 18M -minrate 18M -maxrate 18M -bufsize 18M -x264-params nal-hrd=cbr:force-cfr=1 \
 -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 320k -ar 48000 -ac 2 -t 8 -movflags +faststart \
 renders/Kan_Paper_Teaser_Final.mp4
