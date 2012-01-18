#!/usr/bin/env python

"""This is a fork of Sebastian Schmieg's "Search By Image" project
http://sebastianschmieg.com/searchbyimage/

I took the code from that side and added a cli wrapper.

Also, often the search results would stabilize on the same image
or the same set of images, so I exclude the images we've seen before
to keep it interesting.
"""

import re, commands, time
import urllib
import os
import sys
import json
import pprint


class GoogleSearchByImage :

    GOOGLE_URL = "http://www.google.com"

    GOOGLE_SBI_URL = "/searchbyimage?image_url="

    AGENT_ID = "Mozilla/5.0 (X11; Linux x86_64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1"

    MIN_SECONDS_BETWEEN_REQUESTS = 2

    _myLastRequestTimestamp = 0

    _myCurrentHtml = ""

    def scrape(self, theReference) :
        if time.time() - self._myLastRequestTimestamp < self.MIN_SECONDS_BETWEEN_REQUESTS :
            time.sleep(self.MIN_SECONDS_BETWEEN_REQUESTS - (time.time() - self._myLastRequestTimestamp))
            return self.scrape(theReference)
        else :
            self._myCurrentHtml = self.getHtml(self.GOOGLE_URL + self.GOOGLE_SBI_URL + theReference)
            self._myLastRequestTimestamp = time.time()

    def getHtml(self, theUrl) :

        #myHtml = subprocess.check_output(["curl", "-L", "-A", self.AGENT_ID, theUrl], stderr=subprocess.STDOUT)
        curl_cmd = "curl -L -A '%s' '%s'" % (self.AGENT_ID, theUrl)
        print curl_cmd
        status, myHtml = commands.getstatusoutput(curl_cmd)
        if 0 == status:
            return myHtml
        else:
            print "Curl error. Will sleep for 10 seconds"
            time.sleep(10)
            return self.getHtml(theUrl)


    def getSimilarImages(self) :
        myPattern = re.compile("\" href\=\"\/imgres\?imgurl\=(.*?)(\&amp|\%3F)")
        myImages = myPattern.findall(self._myCurrentHtml)
        myImagesUrls = []
        for myImage in myImages :
            myImagesUrls.append(myImage[0])
        return myImagesUrls

    def getLinkToSimilarImagesPage(self) :
        myPattern = re.compile("\<a href\=\"([^\"]+[.]?)\"\>Visually similar images\<\/a\>")
        myPageUrl = myPattern.findall(self._myCurrentHtml)
        myPageUrl = str(myPageUrl[0]).replace("&amp;", "&")
        myPageUrl += "&biw=1600&bih=825" # always keep this
        return self.GOOGLE_URL + myPageUrl

# save_state()
#_______________________________________________________________________________
def save_state(url, img_num, seen_images):
    d = {'url':         url,
         'img_num':     img_num,
         'seen_images': list(seen_images),
        }

    f = open('saved_state.json', 'w')
    json.dump(d, f)
    f.close()

# read_state()
#_______________________________________________________________________________
def read_state():
    f = open('saved_state.json')
    d = json.load(f)
    f.close()
    return d['url'], d['img_num'], set(d['seen_images'])

# capture_result()
#_______________________________________________________________________________
def capture_result(url, img_num, seen_images):
    filename = 'images/%04d' % img_num
    assert not os.path.exists(filename)
    print " saving %s to %s" % (url, filename)

    curl_cmd = "curl -L -A '%s' '%s' --output %s" % (GoogleSearchByImage.AGENT_ID, url, filename)
    status, myHtml = commands.getstatusoutput(curl_cmd)
    if 0 != status:
        f = open(filename, 'w') #error, write empty file
        f.close()

    save_state(url, img_num, seen_images)


# get_similar_image()
#_______________________________________________________________________________
def get_similar_image(g, seen_images, sim_images):
    similar_images = g.getSimilarImages()

    # sometimes we don't get any similar images back. So let's save
    # up to 100 of the previous similar images, just in case we get stuck.
    sim_images = similar_images + sim_images
    sim_images = sim_images[:100]

    for img in sim_images[1:]:        #take the second image
        print ' checking ' + img
        if img not in seen_images:
            seen_images.add(img)
            return img, sim_images
        else:
            print '  already seen ' + img

    return False, sim_images

# main()
#_______________________________________________________________________________
if __name__ == "__main__":
    assert 2 == len(sys.argv)
    if os.path.exists('images'):
        if not os.path.exists('saved_state.json'):
            sys.exit('images dir found, but no saved state file found!')
    else:
        os.mkdir('images')

    seed_url = sys.argv[1]
    img_num = 0
    seen_images = set()
    seen_images.add(seed_url)
    sim_images = []

    if os.path.exists('saved_state.json'):
        seed_url, img_num, seen_images = read_state()
        img_num += 1
    else:
        capture_result(seed_url, img_num, seen_images)
        img_num += 1

    g = GoogleSearchByImage()
    while img_num < 10000:
        g.scrape(seed_url)

        #pprint.pprint(seen_images)
        seed_url, sim_images = get_similar_image(g, seen_images, sim_images)

        if False == seed_url:
            print "Could not find any new iamges!"
            sys.exit(0)

        print "got similar image %s" % seed_url
        print
        capture_result(seed_url, img_num, seen_images)
        img_num += 1

        time.sleep(30)

"""
now run:
mogrify -format png *
~/petabox/sw/bin/ffmpeg -r 5 -i %04d.png faces.mp4
"""