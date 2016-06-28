"""

(C) Copyright 2009 Igor V. Custodio

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from posplat.ISO8583.ISO1583_BIT62 import ISO8583_BIT62
from posplat.ISO8583.ISO8583 import ISO8583
from posplat.ISO8583.ISOErrors import *

import traceback

import os

os.system(['clear', 'cls'][os.name == 'nt'])

# Testing some funcionalities
p2 = ISO8583()
p2.setMTI('0800')
p2.setBit(2, 2)
p2.setBit(4, 4)
p2.setBit(12, 12)
p2.setBit(17, 17)
p2.setBit(99, 99)

print ('The MTI is = %s' % p2.getMTI())
print ('The Bitmap is = %s' % p2.getBitmap())

# Showing bits...
p2.showIsoBits()

#Save the ASCII ISO value without size
iso = p2.getRawIso()

print ('\n\n\n------------------------------------------\n')
print ('This is the ISO <%s> that will be interpreted' % iso)

# New ISO
i = ISO8583()
# Set the ASCII
i.setIsoContent(iso)

# Showing that everything is ok
print ('The MTI is = %s' % i.getMTI())
print ('The Bitmap is = %s' % i.getBitmap())
print ('Show bits inside the package')
i.showIsoBits()

# Using == to compare ISOS's
print ('Compare ISOs ...')
if i == p2:
    print ('They are equivalent!')

else:
    print ('The are differente')

# More example...	
print ('\n\n\n------------------------------------------\n')

i3 = ISO8583()
i3.setMTI('0800')
i3.setBit(3, '300000')
i3.setBit(24, '045')
i3.setBit(41, '11111111')
i3.setBit(42, '222222222222222')

p = ISO8583_BIT62()
p.setBit(1, "123")
p.setBit(2, "456")
p.setBit(3, 4897)
p.setBit(6, 'F')
p.setBit(7, '2F')
p.setBit(11, 'A1000234')
p.setBit(88, 'A123')
r = p.getRawIso()

i3.setBit(62, r)
i3.showIsoBits()

print ('This is the pack %s' % i3.getRawIso())

	
