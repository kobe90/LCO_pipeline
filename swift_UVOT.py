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

logging.basicConfig(level=logging.INFO)
# Define your custom handler here.
@gcn.handlers.include_notice_types(
    gcn.notice_types.SWIFT_UVOT_POS)                      
def handler(payload, root):
    # Look up right ascension, declination, and error radius fields.
    trig = str(root.find(".//Param[@name='TrigID']").attrib['value'])
    mag = float(root.find(".//Param[@name='Burst_Mag']").attrib['value'])/100.
    pos2d = root.find('.//{*}Position2D')
    ra = float(pos2d.find('.//{*}C1').text)
    dec = float(pos2d.find('.//{*}C2').text)
    radius = float(pos2d.find('.//{*}Error2Radius').text)
    #write to file
    with open(trig + "_UVOT.txt", "a") as myfile:
        myfile.write('date time   RA     DEC      RADIUS   MAG \n')
        myfile.write('%s   %.4f   %.4f   %.4f %.2f \n' %(Time.now(), ra, dec, radius, mag))
        myfile.close()
    

# Listen for VOEvents until killed with Control-C.
gcn.listen(handler=handler)
