joker-studio
============

CLI tools for media file editing, wrapping FFmpeg and others

Install with `pip` (add `sudo` if necessary):

    python3 -m pip install joker-studio


### Crop

Example:

    dio crop -c 0 0 .1 .2 -t 120 60 myvideo.mp4

This command will
* remove the leading 2 minutes and trailing 1 minute
* crop 10% at bottom and 20% on the left
* save result as `myvideo.crop.mp4` (original `myvideo.mp4` untouched)


### Convert

Convert multiple `.ts` videos to `.mp4`:

    dio conv video1.ts video2.ts

Extract audio from video as `.mp3`:

    dio conv -f mp3 -f myvideo.mp4


### Split

Split a video into 4 segments of equal duration:

    dio split -n 4 myvideo.mp4

Split into segments, each (but the last one) of duration 5 minutes (300 seconds):

    dio split -s 300 myvideo.mp4
    
    
### Fade 

Add 10 sec audio fade-in, 6 sec video fade-in, 4 sec video fade-out

    dio fade -a 10 0 -v 6 4 myvideo.mp4


### Burn subtitle

This command generates a video with hard subtitle named `myvideo.wSub.mp4`

    dio sub -s myvideo.english.srt myvideo.mp4
      
      
--------------------------------------------------------------


### Rename files

Remove all "unsafe" characters on Unix-like systems, i.e. characters you should quote in shell scripts,
and invalid characters on Microsoft Windows:

    dio ren -f san *.jpg
    
Add a prefix like `img-640x480.` based on media information:

    dio ren -f img waterlife.jpg
    # waterlife.jpg => img-800x600.waterlife.jpg

Add a prefix like `ih-F8F07B7F3F0E0E0F.` where `F8F07B7F3F0E0E0F` is an [imagehash](https://github.com/JohannesBuchner/imagehash)

    dio ren -f ih lightning.jpg
    # lightning.jpg => ih-F8F07B7F3F0E0E0F.lightning.jpg 
    
More info:
    
    dio ren -h 
