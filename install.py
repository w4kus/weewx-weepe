from setup import ExtensionInstaller


def loader():
    return WeepeInstaller()


class WeepeInstaller(ExtensionInstaller):
    def __init__(self):
        super(WeepeInstaller, self).__init__(
            version='1.0',
            name='weepe',
            description='Send APRS weather packets to a AGWPE host',
            author='Mark White (W4KUS)',
            author_email='w4kus.jmw@gmail.com',
            process_services='user.weepe.AGWPEWx',
            config={
                'AGWPEWX': {
                    'host': 'localhost',
                    'port': 8000,
                    'callsign': 'NOCALL',
                    'via': 'WIDE2-1',
                    'dest': 'APRS',
                    'interval': 0
                },
            },
            files=[('bin/user', ['bin/user/weepe.py'])]
        )
