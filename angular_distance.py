from astropy.coordinates import Angle
import astropy.units as u
from astropy.coordinates import SkyCoord
    
    
def ang_dist(ra1, dec1, ra2, dec2):
    ra1, dec1, ra2, dec2 = str(ra1), str(dec1), str(ra2), str(dec2)
    if ':' in ra1:
        ra1 = Angle(ra1, unit='hourangle')
        dec1 = Angle(dec1, unit='degree')
        ra2 = Angle(ra2, unit='hourangle')
        dec2 = Angle(dec2, unit='degree')
        c1 = SkyCoord(ra1, dec1, frame='fk5')
        c2 = SkyCoord(ra2, dec2, frame='fk5')
    else:
        ra1, dec1, ra2, dec2 = float(ra1), float(dec1), float(ra2), float(dec2)
        c1 = SkyCoord(ra1*u.deg, dec1*u.deg, frame='fk5')
        c2 = SkyCoord(ra2*u.deg, dec2*u.deg, frame='fk5')

    sep=c1.separation(c2)
    return sep