import os,string,re,sys,glob
import datetime
import json
import requests

filters_dictionary={'i':'ip', 'r':'rp', 'g':'gp', 'z':'zs'}

def line0(obsname, ra, dec, utcstart, utcstop):
    
    mode = "TARGET_OF_OPPORTUNITY"
    inst='Sinistro'
    filter=['i']
    filt=[filters_dictionary[item] for item in filter]
    tel='2m0'
    
    if tel == '1m0':
        if inst == "Sinistro":
            inst_str="1M0-SCICAM-SINISTRO"
            bin_x=bin_y=1
        elif inst == "SBIG":
            inst_str="1m0-SciCam-SBIG"
            bin_x=bin_y=2
        else:
            #sys.stderr.write('Invalid instrument name\n'+usage+'\n')
            sys.exit(1)
    
    elif tel == '2m0':
        if inst != "SciCam":
            #sys.stderr.write('Ignored instrument request: only SciCam is available on 2m0\n')
            inst="SciCam"

        inst_str="2M0-SCICAM-SPECTRAL"   # only available instrument on 2m0 
        bin_x=bin_y=2
    else:
        #sys.stderr.write('Invalid telescope: 1m0, 2m0\n'+usage+'\n')
        sys.exit(1)
    
    constraints = {
        'max_airmass' : 3.0,
        'min_lunar_distance':30
    }

    #if option.hrsdel is not None:
    #    s_start = datetime.datetime.utcnow()
    #    s_end = s_start + datetime.timedelta(hours=hrsdel)
    #else:
    s_start = datetime.datetime.strptime(utcstart,"%Y-%m-%dT%H:%M:%S")
    s_end = datetime.datetime.strptime(utcstop,"%Y-%m-%dT%H:%M:%S")
    
    filtname = "".join([item[0] for item in filt])  
    obsnamefull = obsname + ' ' + tel + ' ' + inst + ' ' + filtname

    proposal = {}
    lcofile=os.environ['HOME']+"/lco_password.txt"
    if os.path.exists(lcofile):
        mylco = open(lcofile, 'r')
        L = mylco.readlines()
        mylco.close()
        for line in L:
            if line[0] == '#':
                continue
            elif line.split()[0] == 'token':
                proposal['token'] = line.split()[1]
            elif line.split()[0] == 'user':
                proposal['user_id'] = line.split()[1]
            elif line.split()[0] == 'password':
                proposal['password'] = line.split()[1]
            elif line.split()[0] == 'PROP_ID':
                proposal['proposal_id'] = line.split()[1]
            else:
                continue
                
    for i in ['user_id','password','proposal_id']:
        if i not in proposal.keys():
            #sys.stderr.write('\nUndefined '+i+'\n\n')
            sys.exit(1)
        
    location = {
        'telescope_class' : tel,
        }

    molecule = [
    {
        "exposure_time": 120,
        "exposure_count": 5,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        }
        ]

        
# define the target
    target = {
        'name' : obsname,
        'ra' : ra, # RA (degrees)
        'dec' : dec, # Dec (Degrees)
        'epoch' : 2000,
        'type' : 'SIDEREAL'
        }

# this is the actual window
    window = {
#    'start' : "2014-06-29 00:00:00", # str(datetime)
        'start' : s_start.strftime("%Y-%m-%d %H:%M:%S"), # str(datetime)
        'end' : s_end.strftime("%Y-%m-%d %H:%M:%S")
        }

    request = {
        "constraints" : constraints,
        "location" : location,
        "molecules" : molecule,
        "observation_note" : "",
        "target" : target,
        "type" : "request",
        "windows" : [window]
        }

    user_request = {
        "operator" : "SINGLE",
        "requests" : [request],
        "group_id": obsnamefull,
        "proposal": proposal['proposal_id'],
        'ipp_value': 1.0,
        "observation_type" : mode
    #    "type" : "compound_request"
        }

    response = requests.post(
        'https://observe.lco.global/api/userrequests/',
        headers={'Authorization': 'Token {}'.format(proposal['token'])},
        json=user_request  
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        print('Request failed: {}'.format(response.content))
        raise exc

    obs_request_json = response.json()
    track_id = obs_request_json['id']
    
    return obs_request_json, track_id


def line1(obsname, ra, dec, utcstart, utcstop):
    
    filter=['r']
    filt=[filters_dictionary[item] for item in filter]
    mode = "TARGET_OF_OPPORTUNITY"
    inst='Sinistro'
    tel='1m0'
    
    if tel == '1m0':
        if inst == "Sinistro":
            inst_str="1M0-SCICAM-SINISTRO"
            bin_x=bin_y=1
        elif inst == "SBIG":
            inst_str="1m0-SciCam-SBIG"
            bin_x=bin_y=2
        else:
            #sys.stderr.write('Invalid instrument name\n'+usage+'\n')
            sys.exit(1)
    
    elif tel == '2m0':
        if inst != "SciCam":
            #sys.stderr.write('Ignored instrument request: only SciCam is available on 2m0\n')
            inst="SciCam"

        inst_str="2M0-SCICAM-SPECTRAL"   # only available instrument on 2m0 
        bin_x=bin_y=2
    else:
        #sys.stderr.write('Invalid telescope: 1m0, 2m0\n'+usage+'\n')
        sys.exit(1)
    
    constraints = {
        'max_airmass' : 3.0,
        'min_lunar_distance':30
    }

    #if option.hrsdel is not None:
    #    s_start = datetime.datetime.utcnow()
    #    s_end = s_start + datetime.timedelta(hours=hrsdel)
    #else:
    s_start = datetime.datetime.strptime(utcstart,"%Y-%m-%dT%H:%M:%S")
    s_end = datetime.datetime.strptime(utcstop,"%Y-%m-%dT%H:%M:%S")
    
    filtname = "".join([item[0] for item in filt])  
    obsnamefull = obsname + ' ' + tel + ' ' + inst + ' ' + filtname

    proposal = {}
    lcofile=os.environ['HOME']+"/lco_password.txt"
    if os.path.exists(lcofile):
        mylco = open(lcofile, 'r')
        L = mylco.readlines()
        mylco.close()
        for line in L:
            if line[0] == '#':
                continue
            elif line.split()[0] == 'token':
                proposal['token'] = line.split()[1]
            elif line.split()[0] == 'user':
                proposal['user_id'] = line.split()[1]
            elif line.split()[0] == 'password':
                proposal['password'] = line.split()[1]
            elif line.split()[0] == 'PROP_ID':
                proposal['proposal_id'] = line.split()[1]
            else:
                continue
                
    for i in ['user_id','password','proposal_id']:
        if i not in proposal.keys():
            #sys.stderr.write('\nUndefined '+i+'\n\n')
            sys.exit(1)
        
    location = {
        'telescope_class' : tel,
        }

    molecule = [
    {
        "exposure_time": 120,
        "exposure_count": 5,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        }
        ]
        
# define the target
    target = {
        'name' : obsname,
        'ra' : ra, # RA (degrees)
        'dec' : dec, # Dec (Degrees)
        'epoch' : 2000,
        'type' : 'SIDEREAL'
        }

# this is the actual window
    window = {
#    'start' : "2014-06-29 00:00:00", # str(datetime)
        'start' : s_start.strftime("%Y-%m-%d %H:%M:%S"), # str(datetime)
        'end' : s_end.strftime("%Y-%m-%d %H:%M:%S")
        }

    request = {
        "constraints" : constraints,
        "location" : location,
        "molecules" : molecule,
        "observation_note" : "",
        "target" : target,
        "type" : "request",
        "windows" : [window]
        }

    user_request = {
        "operator" : "SINGLE",
        "requests" : [request],
        "group_id": obsnamefull,
        "proposal": proposal['proposal_id'],
        'ipp_value': 1.0,
        "observation_type" : mode
    #    "type" : "compound_request"
        }

    response = requests.post(
        'https://observe.lco.global/api/userrequests/',
        headers={'Authorization': 'Token {}'.format(proposal['token'])},
        json=user_request  
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        print('Request failed: {}'.format(response.content))
        raise exc

    obs_request_json = response.json()
    track_id = obs_request_json['id']
    
    return obs_request_json, track_id


def line2(obsname, aperture, ra, dec, utcstart, utcstop):
    
    tel=aperture
    filter=['g','r','i','z']
    filt=[filters_dictionary[item] for item in filter]
    mode = "TARGET_OF_OPPORTUNITY"
    inst='Sinistro'
    
    if tel == '1m0':
        if inst == "Sinistro":
            inst_str="1M0-SCICAM-SINISTRO"
            bin_x=bin_y=1
        elif inst == "SBIG":
            inst_str="1m0-SciCam-SBIG"
            bin_x=bin_y=2
        else:
            #sys.stderr.write('Invalid instrument name\n'+usage+'\n')
            sys.exit(1)
    
    elif tel == '2m0':
        if inst != "SciCam":
            #sys.stderr.write('Ignored instrument request: only SciCam is available on 2m0\n')
            inst="SciCam"

        inst_str="2M0-SCICAM-SPECTRAL"   # only available instrument on 2m0 
        bin_x=bin_y=2
    else:
        #sys.stderr.write('Invalid telescope: 1m0, 2m0\n'+usage+'\n')
        sys.exit(1)
    
    constraints = {
        'max_airmass' : 3.0,
        'min_lunar_distance':30
    }

    #if option.hrsdel is not None:
    #    s_start = datetime.datetime.utcnow()
    #    s_end = s_start + datetime.timedelta(hours=hrsdel)
    #else:
    s_start = datetime.datetime.strptime(utcstart,"%Y-%m-%dT%H:%M:%S")
    s_end = datetime.datetime.strptime(utcstop,"%Y-%m-%dT%H:%M:%S")
    
    filtname = "".join([item[0] for item in filt])  
    obsnamefull = obsname + ' ' + tel + ' ' + inst + ' ' + filtname

    proposal = {}
    lcofile=os.environ['HOME']+"/lco_password.txt"
    if os.path.exists(lcofile):
        mylco = open(lcofile, 'r')
        L = mylco.readlines()
        mylco.close()
        for line in L:
            if line[0] == '#':
                continue
            elif line.split()[0] == 'token':
                proposal['token'] = line.split()[1]
            elif line.split()[0] == 'user':
                proposal['user_id'] = line.split()[1]
            elif line.split()[0] == 'password':
                proposal['password'] = line.split()[1]
            elif line.split()[0] == 'PROP_ID':
                proposal['proposal_id'] = line.split()[1]
            else:
                continue
                
    for i in ['user_id','password','proposal_id']:
        if i not in proposal.keys():
            #sys.stderr.write('\nUndefined '+i+'\n\n')
            sys.exit(1)
        
    location = {
        'telescope_class' : aperture,
        }

    molecule = [
    {
        "exposure_time": 30,
        "exposure_count": 1,
        "filter": filters_dictionary['g'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 30,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 30,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 30,
        "exposure_count": 1,
        "filter": filters_dictionary['z'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
            {
        "exposure_time": 30,
        "exposure_count": 1,
        "filter": filters_dictionary['g'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 30,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 30,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 30,
        "exposure_count": 1,
        "filter": filters_dictionary['z'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['g'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['z'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['g'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['z'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['g'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['z'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['g'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['z'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['g'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['z'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        }
        ]        
        
# define the target
    target = {
        'name' : obsname,
        'ra' : ra, # RA (degrees)
        'dec' : dec, # Dec (Degrees)
        'epoch' : 2000,
        'type' : 'SIDEREAL'
        }

# this is the actual window
    window = {
#    'start' : "2014-06-29 00:00:00", # str(datetime)
        'start' : s_start.strftime("%Y-%m-%d %H:%M:%S"), # str(datetime)
        'end' : s_end.strftime("%Y-%m-%d %H:%M:%S")
        }

    request = {
        "constraints" : constraints,
        "location" : location,
        "molecules" : molecule,
        "observation_note" : "",
        "target" : target,
        "type" : "request",
        "windows" : [window]
        }

    user_request = {
        "operator" : "SINGLE",
        "requests" : [request],
        "group_id": obsnamefull,
        "proposal": proposal['proposal_id'],
        'ipp_value': 1.0,
        "observation_type" : mode
    #    "type" : "compound_request"
        }

    response = requests.post(
        'https://observe.lco.global/api/userrequests/',
        headers={'Authorization': 'Token {}'.format(proposal['token'])},
        json=user_request  
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        print('Request failed: {}'.format(response.content))
        raise exc

    obs_request_json = response.json()
    track_id = obs_request_json['id']
    
    return obs_request_json, track_id
    


def line5(obsname, aperture, ra, dec, utcstart, utcstop):
    
    tel=aperture
    filter=['g','r','i','z']
    filt=[filters_dictionary[item] for item in filter]
    mode = "TARGET_OF_OPPORTUNITY"
    inst='Sinistro'
    
    if tel == '1m0':
        if inst == "Sinistro":
            inst_str="1M0-SCICAM-SINISTRO"
            bin_x=bin_y=1
        elif inst == "SBIG":
            inst_str="1m0-SciCam-SBIG"
            bin_x=bin_y=2
        else:
            #sys.stderr.write('Invalid instrument name\n'+usage+'\n')
            sys.exit(1)
    
    elif tel == '2m0':
        if inst != "SciCam":
            #sys.stderr.write('Ignored instrument request: only SciCam is available on 2m0\n')
            inst="SciCam"

        inst_str="2M0-SCICAM-SPECTRAL"   # only available instrument on 2m0 
        bin_x=bin_y=2
    else:
        #sys.stderr.write('Invalid telescope: 1m0, 2m0\n'+usage+'\n')
        sys.exit(1)
    
    constraints = {
        'max_airmass' : 3.0,
        'min_lunar_distance':30
    }

    #if option.hrsdel is not None:
    #    s_start = datetime.datetime.utcnow()
    #    s_end = s_start + datetime.timedelta(hours=hrsdel)
    #else:
    s_start = datetime.datetime.strptime(utcstart,"%Y-%m-%dT%H:%M:%S")
    s_end = datetime.datetime.strptime(utcstop,"%Y-%m-%dT%H:%M:%S")
    
    filtname = "".join([item[0] for item in filt])  
    obsnamefull = obsname + ' ' + tel + ' ' + inst + ' ' + filtname

    proposal = {}
    lcofile=os.environ['HOME']+"/lco_password.txt"
    if os.path.exists(lcofile):
        mylco = open(lcofile, 'r')
        L = mylco.readlines()
        mylco.close()
        for line in L:
            if line[0] == '#':
                continue
            elif line.split()[0] == 'token':
                proposal['token'] = line.split()[1]
            elif line.split()[0] == 'user':
                proposal['user_id'] = line.split()[1]
            elif line.split()[0] == 'password':
                proposal['password'] = line.split()[1]
            elif line.split()[0] == 'PROP_ID':
                proposal['proposal_id'] = line.split()[1]
            else:
                continue
                
    for i in ['user_id','password','proposal_id']:
        if i not in proposal.keys():
            #sys.stderr.write('\nUndefined '+i+'\n\n')
            sys.exit(1)
        
    location = {
        'telescope_class' : aperture,
        }

    molecule = [
    {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['g'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['z'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['g'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['z'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['g'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['z'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['g'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['z'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['g'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['z'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['g'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['z'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        }
        ]
        
# define the target
    target = {
        'name' : obsname,
        'ra' : ra, # RA (degrees)
        'dec' : dec, # Dec (Degrees)
        'epoch' : 2000,
        'type' : 'SIDEREAL'
        }

# this is the actual window
    window = {
#    'start' : "2014-06-29 00:00:00", # str(datetime)
        'start' : s_start.strftime("%Y-%m-%d %H:%M:%S"), # str(datetime)
        'end' : s_end.strftime("%Y-%m-%d %H:%M:%S")
        }

    request = {
        "constraints" : constraints,
        "location" : location,
        "molecules" : molecule,
        "observation_note" : "",
        "target" : target,
        "type" : "request",
        "windows" : [window]
        }

    user_request = {
        "operator" : "SINGLE",
        "requests" : [request],
        "group_id": obsnamefull,
        "proposal": proposal['proposal_id'],
        'ipp_value': 1.0,
        "observation_type" : mode
    #    "type" : "compound_request"
        }

    response = requests.post(
        'https://observe.lco.global/api/userrequests/',
        headers={'Authorization': 'Token {}'.format(proposal['token'])},
        json=user_request  
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        print('Request failed: {}'.format(response.content))
        raise exc

    obs_request_json = response.json()
    track_id = obs_request_json['id']
    
    return obs_request_json, track_id
    
    
def line7(obsname, aperture, ra, dec, utcstart, utcstop):
    
    tel=aperture
    filter=['r','i']
    filt=[filters_dictionary[item] for item in filter]
    mode = "TARGET_OF_OPPORTUNITY"
    inst='Sinistro'
    
    if tel == '1m0':
        if inst == "Sinistro":
            inst_str="1M0-SCICAM-SINISTRO"
            bin_x=bin_y=1
        elif inst == "SBIG":
            inst_str="1m0-SciCam-SBIG"
            bin_x=bin_y=2
        else:
            #sys.stderr.write('Invalid instrument name\n'+usage+'\n')
            sys.exit(1)
    
    elif tel == '2m0':
        if inst != "SciCam":
            #sys.stderr.write('Ignored instrument request: only SciCam is available on 2m0\n')
            inst="SciCam"

        inst_str="2M0-SCICAM-SPECTRAL"   # only available instrument on 2m0 
        bin_x=bin_y=2
    else:
        #sys.stderr.write('Invalid telescope: 1m0, 2m0\n'+usage+'\n')
        sys.exit(1)
    
    constraints = {
        'max_airmass' : 3.0,
        'min_lunar_distance':30
    }

    #if option.hrsdel is not None:
    #    s_start = datetime.datetime.utcnow()
    #    s_end = s_start + datetime.timedelta(hours=hrsdel)
    #else:
    s_start = datetime.datetime.strptime(utcstart,"%Y-%m-%dT%H:%M:%S")
    s_end = datetime.datetime.strptime(utcstop,"%Y-%m-%dT%H:%M:%S")
    
    filtname = "".join([item[0] for item in filt])  
    obsnamefull = obsname + ' ' + tel + ' ' + inst + ' ' + filtname

    proposal = {}
    lcofile=os.environ['HOME']+"/lco_password.txt"
    if os.path.exists(lcofile):
        mylco = open(lcofile, 'r')
        L = mylco.readlines()
        mylco.close()
        for line in L:
            if line[0] == '#':
                continue
            elif line.split()[0] == 'token':
                proposal['token'] = line.split()[1]
            elif line.split()[0] == 'user':
                proposal['user_id'] = line.split()[1]
            elif line.split()[0] == 'password':
                proposal['password'] = line.split()[1]
            elif line.split()[0] == 'PROP_ID':
                proposal['proposal_id'] = line.split()[1]
            else:
                continue
                
    for i in ['user_id','password','proposal_id']:
        if i not in proposal.keys():
            #sys.stderr.write('\nUndefined '+i+'\n\n')
            sys.exit(1)
        
    location = {
        'telescope_class' : aperture,
        }

    molecule = [
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 60,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        }
        ]
        
# define the target
    target = {
        'name' : obsname,
        'ra' : ra, # RA (degrees)
        'dec' : dec, # Dec (Degrees)
        'epoch' : 2000,
        'type' : 'SIDEREAL'
        }

# this is the actual window
    window = {
#    'start' : "2014-06-29 00:00:00", # str(datetime)
        'start' : s_start.strftime("%Y-%m-%d %H:%M:%S"), # str(datetime)
        'end' : s_end.strftime("%Y-%m-%d %H:%M:%S")
        }

    request = {
        "constraints" : constraints,
        "location" : location,
        "molecules" : molecule,
        "observation_note" : "",
        "target" : target,
        "type" : "request",
        "windows" : [window]
        }

    user_request = {
        "operator" : "SINGLE",
        "requests" : [request],
        "group_id": obsnamefull,
        "proposal": proposal['proposal_id'],
        'ipp_value': 1.0,
        "observation_type" : mode
    #    "type" : "compound_request"
        }

    response = requests.post(
        'https://observe.lco.global/api/userrequests/',
        headers={'Authorization': 'Token {}'.format(proposal['token'])},
        json=user_request  
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        print('Request failed: {}'.format(response.content))
        raise exc

    obs_request_json = response.json()
    track_id = obs_request_json['id']
    
    return obs_request_json, track_id
    
    
def line9(obsname, aperture, ra, dec, utcstart, utcstop):
    
    tel=aperture
    filter=['r']
    filt=[filters_dictionary[item] for item in filter]
    mode = "TARGET_OF_OPPORTUNITY"
    inst='Sinistro'
    
    if tel == '1m0':
        if inst == "Sinistro":
            inst_str="1M0-SCICAM-SINISTRO"
            bin_x=bin_y=1
        elif inst == "SBIG":
            inst_str="1m0-SciCam-SBIG"
            bin_x=bin_y=2
        else:
            #sys.stderr.write('Invalid instrument name\n'+usage+'\n')
            sys.exit(1)
    
    elif tel == '2m0':
        if inst != "SciCam":
            #sys.stderr.write('Ignored instrument request: only SciCam is available on 2m0\n')
            inst="SciCam"

        inst_str="2M0-SCICAM-SPECTRAL"   # only available instrument on 2m0 
        bin_x=bin_y=2
    else:
        #sys.stderr.write('Invalid telescope: 1m0, 2m0\n'+usage+'\n')
        sys.exit(1)
    
    constraints = {
        'max_airmass' : 3.0,
        'min_lunar_distance':30
    }

    #if option.hrsdel is not None:
    #    s_start = datetime.datetime.utcnow()
    #    s_end = s_start + datetime.timedelta(hours=hrsdel)
    #else:
    s_start = datetime.datetime.strptime(utcstart,"%Y-%m-%dT%H:%M:%S")
    s_end = datetime.datetime.strptime(utcstop,"%Y-%m-%dT%H:%M:%S")
    
    filtname = "".join([item[0] for item in filt])  
    obsnamefull = obsname + ' ' + tel + ' ' + inst + ' ' + filtname

    proposal = {}
    lcofile=os.environ['HOME']+"/lco_password.txt"
    if os.path.exists(lcofile):
        mylco = open(lcofile, 'r')
        L = mylco.readlines()
        mylco.close()
        for line in L:
            if line[0] == '#':
                continue
            elif line.split()[0] == 'token':
                proposal['token'] = line.split()[1]
            elif line.split()[0] == 'user':
                proposal['user_id'] = line.split()[1]
            elif line.split()[0] == 'password':
                proposal['password'] = line.split()[1]
            elif line.split()[0] == 'PROP_ID':
                proposal['proposal_id'] = line.split()[1]
            else:
                continue
                
    for i in ['user_id','password','proposal_id']:
        if i not in proposal.keys():
            #sys.stderr.write('\nUndefined '+i+'\n\n')
            sys.exit(1)
        
    location = {
        'telescope_class' : aperture,
        }

    molecule = [
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['r'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        },
        {
        "exposure_time": 120,
        "exposure_count": 1,
        "filter": filters_dictionary['i'],
        "instrument_name": inst_str,
        "bin_x": bin_x,
        "type": "EXPOSE",
        "bin_y": bin_y,
        "priority": 0
        }
        ]
        
# define the target
    target = {
        'name' : obsname,
        'ra' : ra, # RA (degrees)
        'dec' : dec, # Dec (Degrees)
        'epoch' : 2000,
        'type' : 'SIDEREAL'
        }

# this is the actual window
    window = {
#    'start' : "2014-06-29 00:00:00", # str(datetime)
        'start' : s_start.strftime("%Y-%m-%d %H:%M:%S"), # str(datetime)
        'end' : s_end.strftime("%Y-%m-%d %H:%M:%S")
        }

    request = {
        "constraints" : constraints,
        "location" : location,
        "molecules" : molecule,
        "observation_note" : "",
        "target" : target,
        "type" : "request",
        "windows" : [window]
        }

    user_request = {
        "operator" : "SINGLE",
        "requests" : [request],
        "group_id": obsnamefull,
        "proposal": proposal['proposal_id'],
        'ipp_value': 1.0,
        "observation_type" : mode
    #    "type" : "compound_request"
        }

    response = requests.post(
        'https://observe.lco.global/api/userrequests/',
        headers={'Authorization': 'Token {}'.format(proposal['token'])},
        json=user_request  
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        print('Request failed: {}'.format(response.content))
        raise exc

    obs_request_json = response.json()
    track_id = obs_request_json['id']
    
    return obs_request_json, track_id
