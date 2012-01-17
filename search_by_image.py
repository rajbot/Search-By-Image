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
        curl_cmd = "curl -L -A '%s' %s" % (self.AGENT_ID, theUrl)
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

# capture_result()
#_______________________________________________________________________________
def capture_result(url, img_num):
    filename = 'images/%04d' % img_num
    assert not os.path.exists(filename)
    print " saving %s to %s" % (url, filename)
    urllib.urlretrieve(url, filename)

# get_similar_image()
#_______________________________________________________________________________
def get_similar_image(g, seen_images):
    similar_images = g.getSimilarImages()
    for img in similar_images:
        if img not in seen_images:
            seen_images.add(img)
            return img
        else:
            print '  already seen ' + img

    return False

# main()
#_______________________________________________________________________________
if __name__ == "__main__":
    assert 2 == len(sys.argv)
    seed_url = sys.argv[1]
    img_num = 0
    seen_images = set()
    seen_images.add(seed_url)

    capture_result(seed_url, img_num)
    img_num += 1

    g = GoogleSearchByImage()
    while img_num < 10000:
        g.scrape(seed_url)

        #similar_images = g.getSimilarImages()
        #seed_url = similar_images[0]
        seed_url = get_similar_image(g, seen_images)
        print seen_images

        if False == seed_url:
            print "Could not find any new iamges!"
            sys.exit(0)

        print "got similar image %s" % seed_url
        capture_result(seed_url, img_num)
        img_num += 1

        time.sleep(60)

"""
now run:
mogrify -format png *
~/petabox/sw/bin/ffmpeg -r 5 -i %04d.png faces.mp4
"""