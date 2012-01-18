#!/usr/bin/env python

import commands
import glob
import os

movie_file = 'movie.mov'
assert not os.path.exists(movie_file)

assert not os.path.exists('processed')
os.mkdir('processed')

images = glob.glob('[0-9]'*4)
rescale_size   = '1280x720' #'500x400'
crop_size = '640x480'
output_img_num = 0

for img in sorted(images):
    cmd = 'convert -resize %s -background black -gravity center -extent %s %s tmp.png' % (rescale_size, crop_size, img)
    print cmd
    status, output = commands.getstatusoutput(cmd)
    if 0 != status:
        #make a black image
        #status, output = commands.getstatusoutput('convert -size %s xc:black -strokewidth 1 %s.png' % (size, img))
        print '   SKIPPING bad image'
        continue #just skip imgs that could not be decoded
    elif os.path.exists('tmp-0.png'):
        src = 'tmp-0.png'
        dst = 'processed/%04d.png' % output_img_num
        print '  renaming %s to %s' % (src, dst)
        os.rename(src, dst)
        status, output = commands.getstatusoutput('rm tmp-*')
        assert 0 == status
        output_img_num += 1
    elif os.path.exists('tmp.png'):
        src = 'tmp.png'
        dst = 'processed/%04d.png' % output_img_num
        print '  renaming %s to %s' % (src, dst)
        os.rename(src, dst)
        output_img_num += 1

#giant movie
#status, output = commands.getstatusoutput('ffmpeg -r 5 -i processed/%04d.png -vcodec png -pix_fmt yuv420p ' + movie_file)

#smaller movie
status, output = commands.getstatusoutput('ffmpeg -r 12 -i processed/%04d.png -vcodec mjpeg -q 1 ' + movie_file)
assert 0 == status
