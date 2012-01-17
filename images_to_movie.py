#!/usr/bin/env python

import commands
import glob
import os

assert not os.path.exists('movie.mp4')

images = glob.glob('[0-9]'*4)
size   = '500x400'

for img in images:
    cmd = 'convert -resize %s -background black -gravity center -extent 500x400 %s %s.png' % (size, img, img)
    print cmd
    status, output = commands.getstatusoutput(cmd)
    if 0 != status:
        #make a black image
        status, output = commands.getstatusoutput('convert -size %s xc:black -strokewidth 1 %s.png' % (size, img))
    elif os.path.exists(img+'-0.png'):
        src = img+'-0.png'
        dst = img+'.png'
        print '  renaming %s to %s' % (src, dst)
        os.rename(src, dst)

status, output = commands.getstatusoutput('ffmpeg -r 5 -i %04d.png movie.mp4')
assert 0 == status
