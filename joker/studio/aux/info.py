#!/usr/bin/env python3
# coding: utf-8


class MediaInfo(object):
    def __init__(self, path):
        # pymediainfo is slow to import, 600ms+
        import pymediainfo

        self.path = str(path)
        self.minfo = pymediainfo.MediaInfo.parse(path)

    def find_tracks(self, track_type):
        tt = track_type.lower()
        tracks = self.minfo.tracks
        return [tr for tr in tracks if tr.track_type.lower() == tt]

    def get_track(self, track_type):
        tracks = self.find_tracks(track_type)
        if not tracks:
            raise ValueError("no {} track found".format(track_type))
        if len(tracks) > 1:
            raise ValueError("multiple {} tracks found".format(track_type))
        return tracks[0]

    @property
    def video(self):
        return self.get_track("video")

    @property
    def audio(self):
        return self.get_track("audio")

    @property
    def image(self):
        return self.get_track("image")

    @property
    def general(self):
        return self.get_track("general")

    def get_audio_duration(self):
        return float(self.audio.duration) / 1000

    def get_video_duration(self):
        return float(self.video.duration) / 1000

    def get_size(self):
        tracks = self.find_tracks("Video") + self.find_tracks("Image")
        if not tracks:
            return None, None
        tr = tracks[0]
        return tr.width, tr.height

    def get_duration(self):
        tracks = self.find_tracks("Video") + self.find_tracks("Audio")
        if not tracks:
            return None
        tr = tracks[0]
        return float(tr.duration) / 1000
