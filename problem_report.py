'''Store, load, and handle problem reports.

Copyright (C) 2006 Canonical Ltd.
Author: Martin Pitt <martin.pitt@ubuntu.com>

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
the full text of the license.
'''

import bz2, base64, time

class ProblemReport:
    def __init__(self, type = 'Crash', date = None):
	'''Initialize a fresh problem report.
	
	type can be 'Crash', 'Packaging', or 'Kernel'. date is the desired
	date/time string; if None (default), the current local time is used. '''

	if date == None:
	    date = time.asctime()
	self.info = {'ProblemType': type, 'Date': date}

    def	load(self, file):
	'''Initialize problem report from a file-like object, using Debian
	control file format.'''

	#TODO: base64/bzip2

	key = None
	value = None
        b64_block = False
	for line in file:
	    print 'line:', line
	    # continuation line
	    if line.startswith(' '):
		assert (key != None and value != None)
		value += line[1:]
	    else:
		if key:
		    assert value != None
		    self.info[key] = value
		(key, value) = line.split(':', 1)
		value = value.strip()

    def write(self, file):
	'''Write information into the given file-like object, using Debian
	control file format.

	If a value is a string, it is written directly. Otherwise it must be an
	one-element tuple containing a string; this is interpreted as a file name,
	which will be read, bzip2'ed, and base64-encoded.

	The file can be restored again using:
	
	>>> for line in infile:
	>>>     if line.startswith(' '):
	>>>	        outfil.write(bd.decompress(base64.b64decode(line)))
	
	(starting from the first line of data)
	'''

	for k, v in self.info.iteritems():
	    # if it's a string, copy it
	    if hasattr(v, 'find'):
		if v.find('\n') >= 0:
		    assert v.find('\n\n') < 0
		    print >> file, k + ':'
		    print >> file, '', v.replace('\n', '\n ')
		else:
		    print >> file, k + ':', v
	    # if it's a tuple, it contains a file name, bzip2/base64-encode it
	    else:
		f = open(v[0])
		print >> file, k + ': base64'
		file.write(' ')
		bc = bz2.BZ2Compressor(9)
		while True:
		    block = f.read(512*1024)
		    if block:
			outblock = bc.compress(block)
			if outblock:
			    file.write(base64.b64encode(outblock))
			    file.write('\n ')
		    else:
			file.write(base64.b64encode(bc.flush()))
			file.write('\n')
			break

    def __getitem__(self, k):
	return self.info.__getitem__(k)

    def __setitem__(self, k, v):
	return self.info.__setitem__(k, v)

    def __delitem__(self, k):
	return self.info.__delitem__(k)
