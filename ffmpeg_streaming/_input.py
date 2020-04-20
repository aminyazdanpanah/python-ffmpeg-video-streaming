"""
ffmpeg_streaming.media
~~~~~~~~~~~~

Input options


:copyright: (c) 2020 by Amin Yazdanpanah.
:website: https://www.aminyazdanpanah.com
:email: contact@aminyazdanpanah.com
:license: MIT, see LICENSE for more details.
"""
from ffmpeg_streaming._media import Media
from ffmpeg_streaming._utiles import get_os, cnv_options_to_args
from ffmpeg_streaming._clouds import Clouds


class Capture(object):
    def __init__(self, video, options):
        self.options = options
        self.video = video

    def _linux(self):
        is_screen = self.options.pop('screen', False)
        if is_screen:
            cap = 'x11grab'
        else:
            cap = 'v4l2'

        return {
            'f': cap,
            'i': self.video
        }

    def _windows(self):
        self.video = 'video=' + str(self.video)
        windows_audio = self.options.pop('windows_audio', None)
        if windows_audio is not None:
            self.video = self.video + ':audio=' + str(windows_audio)

        return {
            'f': 'dshow',
            'i': self.video
        }

    def _os_x(self):
        return {
            'f': 'avfoundation',
            'i': self.video
        }

    @staticmethod
    def _unknown():
        raise OSError("Unreported OS!")

    def __iter__(self):
        yield from getattr(self, '_' + get_os())().items()


def get_from_cloud(cloud: Clouds, options: dict):
    save_to = options.pop('save_to', None)
    return {
        'i': cloud.download(save_to, **options),
        'is_tmp': True if save_to is None else False
    }


class InputOption(object):
    def __init__(self, _input, **options):
        self.input_ = _input
        self.options = options

    def __str__(self):
        return " ".join(cnv_options_to_args(self._create()))

    def __iter__(self):
        yield from self._create().items()

    def _create(self):
        options = self.options.pop('pre_opts', {'y': None})
        is_cap = self.options.pop('capture', False)

        if isinstance(self.input_, Clouds):
            options.update(get_from_cloud(self.input_, self.options))
        elif is_cap:
            options.update(Capture(self.input_, self.options))
        elif isinstance(self.input_, (str, int)):
            i_options = {'i': str(self.input_)}
            i_options.update(self.options)
            options.update(i_options)
        else:
            raise ValueError("Unknown input!")

        return options


def input(_input, **options) -> Media:
    """Input options (ffmpeg pre_option ``-i`` input options)
        You can also pass a cloud object as an input to the method. the file will be downloaded and will pass it to ffmpeg
        if you want to open a resource from a pipe, set input "pipe:"
        if you want to open a resource from a capture device, pass a device name as filename and set the capture keyword
        to True. To list the supported, connected capture devices, see https://trac.ffmpeg.org/wiki/Capture/Webcam
         and https://trac.ffmpeg.org/wiki/Capture/Desktop. See https://ffmpeg.org/ffmpeg.html#Main-options and
         https://ffmpeg.org/ffmpeg-protocols.html for more information about input option and supported resources
         such as http, ftp, and so on.
        """
    return Media(InputOption(_input, **options))


__all__ = [
    'input',
]