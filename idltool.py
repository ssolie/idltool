#!/usr/bin/python
#
# idltool.py - Code generates from Amiga-style interface description
# Copyright (C) 2021,2022 Steven Solie
# 
# This script parses Amiga-style interface descriptions and outputs various
# pieces of code.
#
# The interface is similar to the original idltool in functionality but not all
# features are implemented and new features have been added.
#
# Special thanks to https://regex101.com/ for the assistance.
#
# Compatible with Python 2.5 and higher.
#
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

import sys
import getopt
import os
import xml.etree.ElementTree as xml

# Version strings.
version = '54.8'
verstag = '$VER: idltool.py ' + version + ' (21.8.2022)'

# Output directory for all code generation.
outdir = os.getcwd()

# Default command line arguments.
args = {
	'c': False,
	'f': False,
	'h': False,
	'i': False,
	'm': False,
	'n': False,
	'o': None,
	'p': False,
	's': False,
	'infile': None
}

def print_usage():
	print("Usage: idltool.py [option] file")
	print("-c    : Generate vectors table for MakeInterface")
	print("-f    : Do not generate private functions in interfaces")
	print("-h    : Usage information")
	print("-i    : Generate interface structure file")
	print("-m    : Generate m68k clib, pragma and pragmas files")
	print("-n    : Generate inline4 file")
	print("-o    : Specify output directory (default: current)")
	print("-p    : Generate prototype file")
	print("-s    : Generate assembler include file")
	print("file  : Interface description input file")

def parse_args():
	""" Parse command line arguments
	Returns True if successful or False on error.
	"""
	try:
		opts, files = getopt.getopt(sys.argv[1:], "cfhimno:ps")
	except getopt.GetoptError:
		return False

	for opt, val in opts:
		if opt == '-c':
			args['c'] = True

		if opt == '-f':
			args['f'] = True

		if opt == '-h':
			args['h'] = True

		if opt == '-i':
			args['i'] = True

		if opt == '-m':
			args['m'] = True

		if opt == '-n':
			args['n'] = True

		if opt == '-o':
			args['o'] = val

		if opt == '-p':
			args['p'] = True

		if opt == '-s':
			args['s'] = True

	if (len(files)) != 1:
		return False
	else:
		args['infile'] = files[0]

	return True


class SpecFile:
	""" Specification file used by output classes to generate code.
	"""
	def __init__(self, filename):
		""" Construct spec using XML filename.
		"""
		try:
			self.tree = xml.parse(filename)
		except Exception:
			print('bad interface description file')
			print(sys.exc_info()[1])
			exit(1)

		self.library = self.tree.getroot()

	def library_spec(self):
		return self.library

	def includes_spec(self):
		return self.library.findall('include')

	def inline4_includes_spec(self):
		return self.library.findall('inline4include')

	def m68k_includes_spec(self):
		return self.library.findall('m68kinclude')

	def interfaces_spec(self):
		interfaces = []

		for child in self.library:
			if child.tag == 'interface':
				interfaces.append(child)

		return interfaces


if __name__ == "__main__":
	if not parse_args():
		print_usage()
		exit(1)

	if args['h']:
		print_usage()
		exit(0)

	if args['o']:
		outdir = args['o']

	spec = SpecFile(args['infile'])

	if args['i']:
		import gen_interfaces_file
		ifile = gen_interfaces_file.InterfacesFileC(spec)
		ifile.codegen(args, version, outdir)

	if args['s']:
		import gen_interfaces_file
		ifile = gen_interfaces_file.InterfacesFileAssembly(spec)
		ifile.codegen(args, version, outdir)

	if args['n']:
		import gen_inline4_file
		i4file = gen_inline4_file.Inline4File(spec)
		i4file.codegen(args, version, outdir)

	if args['c']:
		import gen_vector_files
		vtable = gen_vector_files.VectorsTable(spec)
		vtable.codegen(version, outdir)

	if args['p']:
		import gen_prototype_file
		proto = gen_prototype_file.ProtoFile(spec)
		proto.codegen(version, outdir)

	if args['m']:
		import gen_m68k_files
		m68kfiles = gen_m68k_files.M68KFiles(spec)
		m68kfiles.codegen(version, outdir)
