#!/usr/bin/env python
"""Usage:
    pymoticz list [--host=<host>] [--names|--idx] [--scenes]
    pymoticz test
    pymoticz status <id> [--host=<host>] [--scenes]
    pymoticz on <id> [--host=<host>] [--scenes]
    pymoticz off <id> [--host=<host>] [--scenes]
    pymoticz dim <id> <level> [--host=<host>]
    pymoticz getSun [--host=<host>]
    pymoticz addSwitch
    pymoticz getTimers <id> 
    pymoticz addTimer <id> <time> <cmd>
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

    def list_hard_idx(self):
        l=self.list_hard()
        return ["%s\t%s" % (device['idx'], device['Name']) for device in l['result']]

    def list_hard(self):
        url='http://%s/json.htm?type=hardware' % self.host
        return self._request(url)


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

    def get_scene(self, _id):
        l=self.list_scenes()
        try:
            scene=[i for i in l['result'] if i['idx'] == u'%s' % _id][0]
        except:
            return None
        return scene

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

    def get_scene_status(self, _id):
        scene = self.get_scene(_id)
        if scene is None:
            return 'No scene/group with that id.'
        else:
            return scene['Status']

    def get_sun(self):
        url='http://%s/json.htm?type=command&param=getSunRiseSet' % self.host
        response = self._request(url)
        return "%s\t%s" % (response['Sunrise'], response['Sunset'])

    def get_timers(self, _id):
        url='http://%s/json.htm?type=timers&idx=%s' % (self.host, _id)
        response = self._request(url)
        if 'result' in response:
            l=response
            return ["%s\t%s\t%s" % (device['idx'], device['Time'], device['Cmd']) for device in l['result']]
        else:
            return "no timers for this id"

            

        
    def add_timer(self, _id, time, cmd):
        hour=time.split(":")[0]
        min=time.split(":")[1]
        if cmd.lower()== 'on' :
            cmd = 0
        else :
            cmd = 1
        url='http://%s/json.htm?type=command&param=addtimer&idx=%s&active=true&timertype=2&date=&hour=%s&min=%s&randomness=false&command=%s&level=100&hue=0&days=128' % (self.host, _id, hour, min, cmd)
        response = self._request(url)
        return response
    

    def get_dummy_id(self):
        l=self.list_hard()
        for device in l['result'] :
           if device['Type'] == 15 :
              return device['idx']
        return 0

    def get_dummy_switch(self):
        url='http://%s/json.htm?type=devices&filter=light&used=false&order=LastUpdate' % self.host
        l =self._request(url)
        for device in l['result'] :
            if device['Name'] == 'Unknown' :
                return device['idx']
        return 0


    def add_switch(self):
        # recupration dummyID
       l=self.list_hard()
       dummyId=self.get_dummy_id()
       if dummyId != 0 :
            url='http://%s/json.htm?type=createvirtualsensor&idx=%s&sensortype=6' % (self.host, dummyId)
            response = self._request(url)
            print "%s" %response
            # we enable the switch
            dummySwID=self.get_dummy_switch()
            print "dummy switch : %s" %dummySwID
            if dummySwID != 0 :
                url='http://%s/json.htm?type=setused&idx=%s&name=dummy%s&used=true&maindeviceidx=' % (self.host, dummySwID, dummySwID)
                response = self._request(url)
            else :
                print ("dummy switch created %s") % dummySwID
       else :
           print "ERROR : no dummy device found, create one before adding virtual switch"
       print dummyId


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
        if args['--scenes']:
            response = p.get_scene_status(args['<id>'])
        else:
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

    elif args['addSwitch']:
        p.add_switch()

    elif args['getSun']:
        response = p.get_sun()
        print(response)
    
    elif args['getTimers']:
        print ("0 = ON, 1 = OFF")
        print ('idTimer\ttime\tcmd')
        print('\n'.join(p.get_timers(args['<id>'])))
    
    elif args['addTimer']:
        response = p.add_timer(args['<id>'], args['<time>'], args['<cmd>'])
        print response