#!/usr/bin/env python
import matplotlib
matplotlib.use('Agg')
import gcn
import gcn.handlers
import gcn.notice_types
import os
import telegram
from time import gmtime, strftime
import logging
from astropy.io import ascii
from astropy.time import Time
from visibility import *
import matplotlib.pyplot as plt
import time
from astropy.io import ascii
import subprocess
from email_py import *
from angular_distance import *
import datetime
from coordinates import *
from LCO import *
import sys

#defining the "Domes" class
class Domes:
    def __init__(self, telescope):
        self.name=name
        self.telescope=availability(self.name)
        
#defining the waiting time for human response        
waiting_time=60
#array of chat ids
chat = []
#bot token
token=""
bot = telegram.Bot(token=token)
#table of already-known sources
table = ascii.read('SGR_table.dat')
#array of emails to deliver recaps
To=[]
#latency time to wait the server
latency=60

logging.basicConfig(level=logging.INFO)
# Define your custom handler here.
@gcn.handlers.include_notice_types(
    gcn.notice_types.SWIFT_BAT_GRB_POS_ACK)                      
def handler(payload, root):
    #reading trigger, right ascension, declination, and error radius fields.
    trig = str(root.find(".//Param[@name='TrigID']").attrib['value'])
    pos2d = root.find('.//{*}Position2D')
    ra = float(pos2d.find('.//{*}C1').text)
    dec = float(pos2d.find('.//{*}C2').text)
    radius = float(pos2d.find('.//{*}Error2Radius').text)
    #selecting table sources close to the event
    selection=[(ang_dist(line['col5'],line['col6'], ra, dec) < 1.5*radius*u.deg) for line in table]
    selection=np.array([(ang_dist(line['col5'],line['col6'], ra, dec) < 1.5*radius*u.deg) for line in table], dtype=bool)
    table_sel=table[selection]
    #controlling fundamental GCN labels
    not_GRB_label=root.find(".//Param[@name='Def_NOT_a_GRB']").attrib['value']
    flt_cat_label=root.find(".//Param[@name='Target_in_Flt_Catalog']").attrib['value']
    gnd_cat_label=root.find(".//Param[@name='Target_in_Gnd_Catalog']").attrib['value']
    blk_cat_label=root.find(".//Param[@name='Target_in_Blk_Catalog']").attrib['value']
    test_lab=root.find(".//Param[@name='Test_Submission']").attrib['value']
    #extracting the galactic latitude
    gal_lat=root.find(".//Param[@name='Galactic_Lat']").attrib['value']
    #calculating visual extinction
    av=3.1*m.ebv(ra, dec)
    if len(table_sel) == 0 and not_GRB_label=='false' and flt_cat_label=='false' and gnd_cat_label=='false' and blk_cat_label=='false' and test_lab=='false':
        #writing position information in a file
        with open(trig + ".txt", "a") as myfile:
            myfile.write('date time    RA     DEC      RADIUS   \n')
            myfile.write('%s  %.4f   %.4f   %.4f \n' %(Time.now(), ra, dec, radius))
            myfile.close()
        current = Time.now()
        current.format = 'iso'
        #calculating observatories and telescopes availability
        available_observatories=available(ra, dec, observatories_south+observatories_north, current)
        for item in available_observatories:
            item.telescope=availability(item.name)
        available_classes=[]
        for i in available_observatories:
            for j in i.telescope:
                available_classes.append(j)
        available_classes=list(set(available_classes))
        #calculating visibility and producing plots
        fig_north = visibility_plot(ra, dec, observatories_north, current)
        fig_south = visibility_plot(ra, dec, observatories_south, current)
        north_name='north_swift_%s.jpg' %trig
        south_name='south_swift_%s.jpg' %trig
        fig_north.savefig(north_name, dpi=(200))
        fig_south.savefig(south_name, dpi=(200))
        #calculating residual time on the proposal
        res_time=[residual_time(item) for item in available_classes]
        #sending information via Telegram
        for chats in chat:
            bot.send_message(chat_id=chats, text='Burst detected by Swift-BAT!', latency=2*latency, timeout=2*latency)
            bot.send_photo(chat_id=chats, photo=open(north_name, 'rb'), latency=2*latency, timeout=2*latency)
            bot.send_photo(chat_id=chats, photo=open(south_name, 'rb'), latency=2*latency, timeout=2*latency)
            if len(available_observatories)>0 and len(available_classes)>0:
                for item in available_observatories:
                    bot.send_message(chat_id=chats, text='Burst observable by %s with: %s' %(item.name, item.telescope), latency=2*latency, timeout=2*latency)
            else:
                string='Burst not observable by our instruments'
                for chats in chat:
                    bot.send_message(chat_id=chats, text=string, latency=2*latency, timeout=2*latency)
                for item in To:
                    SendMail([north_name, south_name], trig, string, item)
                sys.exit()
        for clas in available_classes:
            for chats in chat:
                bot.send_message(chat_id=chats, text='Residual too time %s: %s' %(clas, residual_time(clas)['too'].print), latency=2*latency, timeout=2*latency)        
        #sending a brief summary via email
        string="Burst observable from "
        for item in available_observatories:
            string += "\n %s with: %s" %(item.name, item.telescope)        
        for item in To:
            SendMail([north_name, south_name], trig, string, item)
        #starting the submission procedure if the burst is observable    
        if av<5.:
            for chats in chat:
                bot.send_message(chat_id=chats, text='Are you awake?', latency=2*latency, timeout=2*latency)
            time.sleep(waiting_time)
            if len(bot.getUpdates(read_latency=latency, read_timeout=latency))!=0 :
                answer_time=Time(bot.getUpdates(read_latency=latency, read_timeout=latency)[-1]['message']['date'])
                if (Time(datetime.datetime.now())-answer_time).to(u.s)<=2*waiting_time*(u.s):
                    answer_id=bot.getUpdates(read_latency=latency, read_timeout=latency)[-1]['message']['chat_id']
                    bot.send_message(chat_id=answer_id, text='Ok, now you are in charge!', latency=2*latency, timeout=2*latency)
                    if len(chat)>=2:
                        for item in [x for x in chat if x != answer_id]:
                            bot.send_message(chat_id=item, text='Another user is in charge now!', latency=2*latency, timeout=2*latency)
                else:
                    for item in chat:
                        bot.send_message(chat_id=item, text='Ok, I keep the rudder!', latency=2*latency, timeout=2*latency)
                    #p=subprocess.Popen(['python','submission.py'])
                    exec(open('submission.py').read())
                   
            else:
                for item in chat:
                    bot.send_message(chat_id=item, text='Ok, I keep the rudder!', latency=2*latency, timeout=2*latency)
                exec(open('submission.py').read())
            #p.terminate()
            report=ascii.read(trig+'.txt')
            ra=float(report[-1][2])
            dec=float(report[-1][3])
        else:
            bot.send_message(chat_id=chat[0], text='too high extintion for observation (Av=%.2f)' %(av), latency=2*latency, timeout=2*latency)
    
    #message of non-observable burst
    else:
        bot.send_message(chat_id=chat[0], text='Event detected by Swift-BAT, probably from a not suitable source for follow-up', latency=2*latency, timeout=2*latency)
        bot.send_message(chat_id=chat[0], text='(not_GRB: %s, flt_cat: %s, gnd_cat: %s, blk_cat: %s, test:%s, len cat:%s)' %(not_GRB_label, flt_cat_label, gnd_cat_label, blk_cat_label, test_lab, len(table_sel)), latency=2*latency, timeout=2*latency)

    

# Listen for VOEvents until killed with Control-C.
gcn.listen(handler=handler)
