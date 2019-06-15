joker-studio
============

CLI tools for media file editing, wrapping FFmpeg and others

Install with `pip`:

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

