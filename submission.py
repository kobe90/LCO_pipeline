from degree_dec import *
import numpy as np
from astropy.table import Table
from osservazione import *

#check residual observing time before the submission
res_time_ini=[residual_time(item) for item in available_classes]
#reading the text file defining the observing strategy
strategy=ascii.read('osservazione_strategy.txt')

utcstart=Time.now()
utcstart.format='isot'
utcstop=utcstart+60*u.min
utcstop.format='isot'
utcstart=utcstart.value[:-4]
utcstop=utcstop.value[:-4]

#submitting the right observing strategy
if '2m0' in available_classes:
    try:
        request, id_pre = line0(trig, ra, dec, utcstart, utcstop)
    except:
        pass
else:
    try:
        request, id_pre = line1(trig, ra, dec, utcstart, utcstop)
    except:
        pass
#keeping the users informed via Telegram
try:
    state_dark = request_state(id_pre)

    for chats in chat:
        bot.send_message(chat_id=chats, text='Submitted BLIND (%s) with state %s' %(id_pre, state_dark), latency=2*latency, timeout=2*latency)
        
except:
    bot.send_message(chat_id=chats, text='Request impossible to submit', latency=2*latency, timeout=2*latency)
    sys.exit()


#launching the gcn reading code for UVOT
p=subprocess.Popen(['python','swift_UVOT.py'])
#reading the ascii file produced by the "swift_UVOT" script
for i in range(0, 15):
        
    try:
        file=ascii.read(trig + '_UVOT.txt')
        break
    except:
        file=None
    
    time.sleep(60)
p.terminate  

res_time_fin=[residual_time(item) for item in available_classes]
        

    

    #no-UVOT-counterpart case    
if type(file)!=Table:
    for chats in chat:
        bot.send_message(chat_id=chats, text='No UVOT counterpart found so far, nothing more will be done', latency=2*latency, timeout=2*latency)
    sys.exit()
#UVOT-counterpart cases    
else:
    if file['MAG'].data[0]<15:
        line=2
        if len(available_classes)==2:
            aperture=strategy[line]['APERTURE']
        elif '1m0' in available_classes:
            aperture='1m0'
        else:
            aperture='2m0'
                    
        request, id_post=line2(trig, aperture, ra, dec, utcstart, utcstop)
    elif file['MAG'].data[0]>=15 and file['MAG'].data[0]<17:
        line=5
        if len(available_classes)==2:
            aperture=strategy[line]['APERTURE']
        elif '1m0' in available_classes:
            aperture='1m0'
        else:
            aperture='2m0'
        request, id_post=line5(trig, aperture, ra, dec, utcstart, utcstop)
    elif file['MAG'].data[0]>=17 and file['MAG'].data[0]<19:
        line=7
        if len(available_classes)==2:
            aperture=strategy[line]['APERTURE']
        elif '1m0' in available_classes:
            aperture='1m0'
        else:
            aperture='2m0'
        request, id_post=line7(trig, aperture, ra, dec, utcstart, utcstop)
    else:#maggiore di 19
        line=9
        if len(available_classes)==2:
            aperture=strategy[line]['APERTURE']
        elif '1m0' in available_classes:
            aperture='1m0'
        else:
            aperture='2m0'
        request, id_post=line9(trig, aperture, ra, dec, utcstart, utcstop)
        
    try:
        state_after = request_state(id_post)
        for chats in chat:
            bot.send_message(chat_id=chats, text='Observation POST (%s) now in state %s' %(id_post, state_after), latency=2*latency, timeout=2*latency)
             
    except:
        for chats in chat:
            bot.send_message(chat_id=chats, text='POST request not submitted', latency=2*latency, timeout=2*latency)
        sys.exit()

try:
    request_state(id_post)
    id_final=id_post
except:
    request_state(id_pre)
    id_final=id_pre

#waiting for the end of the observing sequence and get data
while request_state(id_final) == 'PENDING':
    time.sleep(60)
if request_state(id_final) == 'COMPLETED':
    try:
        download(id_final)
    except:
        pass
elif request_state(id_final) != 'PENDING' and request_state(id_final) != 'COMPLETED':
    bot.send_message(chat_id=chats, text='Observation not completed, now in state: %s' %(request_state(id_final)), latency=2*latency, timeout=2*latency)
        
