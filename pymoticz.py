#!/usr/bin/env python
"""Usage:
    pymoticz list [--host=<host>] [--names|--idx] [--scenes]
    pymoticz test
    pymoticz status <id> [--host=<host>] [--scenes]
    pymoticz on <id> [--host=<host>] [--scenes]
    pymoticz off <id> [--host=<host>] [--scenes]
    pymoticz dim <id> <level> [--host=<host>]
"""
import requests
import json

__all__ = [ 'Pymoticz' ]
__version__ = '0.1'

class Pymoticz:
    DIMMER = u'Dimmer'
    ON_OFF = u'On/Off'
    SWITCH_TYPES=[ DIMMER, ON_OFF ]
    def __init__(self, domoticz_host='127.0.0.1:8080'):
        self.host = domoticz_host

    def _request(self, url):
        r=requests.get(url)

        if r.status_code == 200:
            return json.loads(r.text)
        else:
            raise

    def list_names(self):
        l=self.list()
        return [device['Name'] for device in l['result']]

    def list_idx(self):
        l=self.list()
        return ["%s\t%s" % (device['idx'], device['Name']) for device in l['result']]

    def list(self):
        url='http://%s/json.htm?type=devices&used=true' % self.host
        return self._request(url)

    def list_scenes(self):
        url='http://%s/json.htm?type=scenes&used=true' % self.host
        return self._request(url)

    def list_scenes_names(self):
        l=self.list_scenes()
        return [device['Name'] for device in l['result']]

    def list_scenes_idx(self):
        l=self.list_scenes()
        return ["%s\t%s" % (device['idx'], device['Name']) for device in l['result']]

    def turn_on(self, _id):
        url='http://%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=On' % (self.host, _id)
        return self._request(url)

    def turn_off(self, _id):
        url='http://%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=Off&level=0' % (self.host, _id)
        return self._request(url)

    def turn_on_scene(self, _id):
        url='http://%s/json.htm?type=command&param=switchscene&idx=%s&switchcmd=On' % (self.host, _id)
        return self._request(url)

    def turn_off_scene(self, _id):
        url='http://%s/json.htm?type=command&param=switchscene&idx=%s&switchcmd=Off&level=0' % (self.host, _id)
        return self._request(url)

    def dim(self, _id, level):
        d=self.get_device(_id)
        if d is None:
            return 'No device with that id.'

        max_dim=d['MaxDimLevel']
        if int(level) > max_dim or int(level) < 0:
            return 'Level has to be in the range 0 to %d' % max_dim
        url='http://%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=Set Level&level=%s' % (self.host, _id, level)
        return self._request(url)

    def get_device(self, _id):
        l=self.list()
        try:
            device=[i for i in l['result'] if i['idx'] == u'%s' % _id][0]
        except:
            return None
        return device

    def get_light_status(self, _id):
        light = self.get_device(_id)
        if light is None:
            return 'No device with that id.'
        if light['SwitchType'] not in self.SWITCH_TYPES:
            return 'Not a light switch'
        elif light['SwitchType'] == self.DIMMER:
            return "%s\t%s" % (light['Status'], light['Level'])
        elif light['SwitchType'] == self.ON_OFF:
            return "%s\t%s" % (light['Status'], 100)

if __name__ == '__main__':
    from docopt import docopt
    from pprint import pprint
    args=docopt(__doc__, version=__version__)

    p=None
    if args['--host']:
        p=Pymoticz(args['--host'])
    else:
        p=Pymoticz()

    if args['list']:
        if args['--scenes']:
            if args['--names']:
                print('\n'.join(p.list_scenes_names()))
            elif args['--idx']:
                print('\n'.join(p.list_scenes_idx()))
            else:
                pprint(p.list_scenes())
        else:
            if args['--names']:
                print('\n'.join(p.list_names()))
            if args['--idx']:
                print('\n'.join(p.list_idx()))
            else:
                pprint(p.list())
    elif args['status']:
        response = p.get_light_status(args['<id>'])
        print(response)
    elif args['on']:
        if args['--scenes']:
            response = p.turn_on_scene(args['<id>'])
        else:
            response = p.turn_on(args['<id>'])
    elif args['off']:
        if args['--scenes']:
            response = p.turn_off_scene(args['<id>'])
        else:
            response = p.turn_off(args['<id>'])
    elif args['dim']:
        response = p.dim(args['<id>'], args['<level>'])
        print(response)
