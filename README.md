This code originates from Sebastian Schmieg's [Search By Image, Recursively](http://sebastianschmieg.com/searchbyimage)</a> project.

I added a CLI wrapper to Sebastian's GIS class. You can call it like so:

`./search_by_image.py http://www.example.com/seed_img.jpg`

This produces image files named 0000, 0001, etc, in the current working directory.

You can then run `images_to_movie.py` to turn those images into a movie.

The `images_to_movie.py` script requires that `imagemagick` and `ffmpeg` be installed.

An example movie from these scripts is [here](http://flic.kr/p/beuok6).
