import requests
from astropy.time import Time
import datetime
from astropy import units as u
import requests
import numpy as np
from astropy import units as u
import wget
from subprocess import call
import os
dat=datetime.datetime

#define here the LCO account token and the login info
token=''

token_down=requests.post(
    'https://archive-api.lco.global/api-token-auth/ ',
    data = {
        'username': '',
        'password': ''
    }
).json()['token']

#defining observatories you are interested in
observatories={
    'Siding Spring Observatory':
    {'acronym':'coj', '1':{'a':'coj.doma.1m0a'}, '2':{'a':'coj.clma.2m0a'}},
    'Sutherland':
    {'acronym':'cpt', '1':{'a':'cpt.doma.1m0a', 'b':'cpt.domb.1m0a', 'c':'cpt.domc.1m0a'}},
    'Cerro Tololo':
    {'acronym':'lsc', '1':{'a':'lsc.doma.1m0a', 'b':'lsc.domc.1m0a'}},
    'McDonald':
    {'acronym':'elp', '1':{'a':'elp.doma.1m0a'}},
    'Haleakala':
    {'acronym':'ogg', '2':{'a':'ogg.clma.2m0a'}}
    } 

#returns the list  of available telescopes in the time range from now to the next 30 minutes, considering only 1m and 2m telescopes
def availability(location):

    list=['1', '2']
    ora=Time.now()
    future=Time.now()+30*u.min
    site=observatories[location]
    
    #request=requests.get('https://observe.lco.global/api/telescope_states/?start=%s&end=%s' %(ora, future)).json()
    
    try:
        clas=site[list[0]]
        request=[requests.get('https://observe.lco.global/api/telescope_states/?start=%s&end=%s&site=%s&telescope=%s' %(ora, future, site['acronym'], clas[telescope][-4:])).json() for telescope in clas]
        available=[item for item in set([request[0][item][0]['telescope'][-4:-1] for item in request[0] if request[0][item][0]['event_type']=='AVAILABLE'])]
    except:
        available=[]
        
    try:
        clas=site[list[1]]
        request=[requests.get('https://observe.lco.global/api/telescope_states/?start=%s&end=%s&site=%s&telescope=%s' %(ora, future, site['acronym'], clas[telescope][-4:])).json() for telescope in clas]
        available.append([item for item in set([request[0][item][0]['telescope'][-4:-1] for item in request[0] if request[0][item][0]['event_type']=='AVAILABLE'])][0])
    except:
        pass
        
    
    return available

#returns the string "ok" if the weather is ok of the observation, the "not" string otherwise
def weather_ok(location):
    ora=Time.now()-15*u.min
    site=observatories[location]
    
    try:
        air_temp=float(requests.get('https://weather-api.lco.global/query?site=%s&datumname=Weather Air Temperature Value&start=%s' %(site['acronym'], ora)).json()[0]['Value'])
    except:
        air_temp=20.
    try:
        humidity=float(requests.get('https://weather-api.lco.global/query?site=%s&datumname=Weather Humidity Value&start=%s' %(site['acronym'], ora)).json()[0]['Value'])
    except:
        humidity=0
    try:    
        wind_speed=float(requests.get('https://weather-api.lco.global/query?site=%s&datumname=Weather Wind Speed Value&start=%s' %(site['acronym'], ora)).json()[0]['Value'])
    except:
        wind_speed=0
    try:    
        sky_brightness=float(requests.get('https://weather-api.lco.global/query?site=%s&datumname=Weather Sky Brightness Value&start=%s' %(site['acronym'], ora)).json()[0]['Value'])
    except:
        sky_brightness=20

    if (air_temp>-20.) and (humidity<90.) and (wind_speed<15.) and (sky_brightness>18.):
        return 'ok'
    else:
        return 'not'

proposal=requests.get('https://observe.lco.global/api/proposals/', headers={'Authorization': 'Token ' + token}).json()

#returns the residual observing time on the proposal
def residual_time(clas):
    
    std_time=[(item['std_allocation']-item['std_time_used']) for item in proposal['results'][0]['timeallocation_set'] if item['telescope_class']==clas][0]
    too_time=[(item['too_allocation']-item['too_time_used']) for item in proposal['results'][0]['timeallocation_set'] if item['telescope_class']==clas][0]
    
    res_time={'std':std_time*u.hour, 'too':too_time*u.hour}
    
    for item in res_time:
        if res_time[item]<1*u.hour:
            res_time[item]=res_time[item].to(u.min)

    for item in res_time:
        res_time[item].print="{0.value:0.02f} {0.unit:FITS}".format(res_time[item])     
    
    return res_time
    #return np.round(std_time, 2)*u.hour, np.round(too_time, 2)*u.hour
    

    
#download frames by id
def download(id):
    id_id=requests.get('https://observe.lco.global/api/userrequests/%s/' %(id), headers={'Authorization': 'Token ' + token}).json()['requests'][0]['id'] #here I get the sub-request number
    frames=requests.get('https://archive-api.lco.global/frames/?REQNUM=%s' %id_id, headers={'Authorization': 'Token ' + token_down}).json()
    dir=str(id)
    call(['mkdir', str(id)])
    os.chdir(dir)
    for i in range(0,len(frames['results'])):
        if ('e11') in frames['results'][i]['filename'] or ('e91') in frames['results'][i]['filename']:
            filename=frames['results'][i]['filename']
            wget.download(frames['results'][i]['url'])
            call(['funpack', filename])
            call(['rm', filename])
    print('\n %i frames downloaded' %len(frames['results']))
        
#request state by id
def request_state(id):
    state=requests.get('https://observe.lco.global/api/userrequests/%s/' %(id), headers={'Authorization': 'Token ' + token}).json()['state']
    
    return state
    
#delete requests from id
def request_cancel(id):
    cancel=requests.post('https://observe.lco.global/api/userrequests/%s/cancel/' %(id), headers={'Authorization': 'Token ' + token}).json()
    
    return cancel['state']
