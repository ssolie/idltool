# This script is a codegen module for idltool.py.
#
# gen_inline4_file.py - Generates include/inline4/<libname>.h files
# Copyright (C) 2021 Steven Solie
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

class Inline4File:
	""" Code generator to create library interface inline4 files in C.
	"""
	def __init__(self, spec_file):
		self.spec_file = spec_file
		self.out_file  = None

	def codegen(self, args, tool_version, out_dir):
		""" Code generate the library interface file.
		"""
		import os

		lib_spec = self.spec_file.library_spec()
		lib_name = lib_spec.attrib["name"]

		path = os.path.join(out_dir, 'include', 'inline4')
		try:
			os.makedirs(path)
		except:
			pass

		path = os.path.join(path, lib_name + '.h')
		self.out_file = open(path, "w+")

		guard_label = 'INLINE4_' + lib_name.upper() + '_H'

		self.put_header(guard_label, tool_version)
		self.putln()
		self.put_includes()
		self.putln()

		for iface_spec in self.spec_file.interfaces_spec():
			iface_name  = iface_spec.attrib['name']
			global_name = iface_spec.attrib['global']

			self.putln('/* Inline macros for Interface "' + iface_name + '" */')

			for method in iface_spec:
				if method.tag != 'method':
					# Skip non-method element.
					continue

				method_name   = method.attrib['name']
				method_status = method.get('status')

				if method_status == 'private':
					if args['f']:
						# Do not output private method.
						continue

				if method_status == 'unimplemented':
					# Do not output unimplemented method.
					continue

				excluded_methods = ('Obtain', 'Release', 'Expunge', 'Clone')
				if method_name in excluded_methods:
					# Skip excluded methods common to all interfaces.
					continue

				vararg_spec = method.find('vararg')

				if vararg_spec != None:
					self.putln('#if (defined(__STDC_VERSION__) && __STDC_VERSION__ >= 199901L) || (__GNUC__ >= 3)')

				self.put('#define ' + method_name + '(')
				self.put_method_macro_params(method)
				self.put(') ')
				self.put(global_name + '->' + method_name + '(')
				self.put_method_macro_args(method)
				self.putln(')')

				if vararg_spec != None:
					self.putln('#elif (__GNUC__ == 2 && __GNUC_MINOR__ >= 95)')
					self.put('#define ' + method_name + '(')
					self.put_method_macro_params(method, True)
					self.put(') ')
					self.put(global_name + '->' + method_name + '(')
					self.put_method_macro_args(method, True)
					self.putln(')')
					self.putln('#endif')

			self.putln()

		self.put_footer(guard_label)

		self.out_file.close()

	def put(self, line=''):
		self.out_file.write(line)

	def putln(self, line=''):
		self.out_file.write(line + '\n')

	def put_header(self, guard_name, tool_version):
		self.putln('#ifndef ' + guard_name)
		self.putln('#define ' + guard_name)
		self.putln()
		self.putln('/*')
		self.putln('** This file was machine generated by idltool.py ' + tool_version + '.')
		self.putln('** Do not edit.')

		copyright = self.spec_file.library_spec().find('copyright')
		if copyright != None:
			self.putln('**')
			self.putln('** ' + copyright.text.strip())

		self.putln('**')
		self.putln('** It provides compatibility to AmigaOS 3.x style library')
		self.putln('** calls by substituting functions.')
		self.putln('*/')

	def put_includes(self):
		self.putln('#include <exec/types.h>')
		self.putln('#include <exec/exec.h>')
		self.putln('#include <exec/interfaces.h>')
		self.putln()

		for spec in self.spec_file.includes_spec():
			name = spec.text.strip()
			self.putln('#include <' + name + '>')

		self.putln('#include <interfaces/exec.h>')

	def put_method_macro_params(self, method_spec, is_gcc2=False):
		num_args = 0
		for arg_spec in method_spec.findall('arg'):
			if num_args > 0:
				self.put(', ')

			arg_name = arg_spec.attrib['name']
			self.put(arg_name)
			num_args += 1

		vararg_spec = method_spec.find('vararg')
		if vararg_spec != None:
			if num_args > 0:
				self.put(', ')

			if is_gcc2 and num_args > 0:
				self.put('vargs')

			self.put('...')

	def put_method_macro_args(self, method_spec, is_gcc2=False):
		num_args = 0
		for arg_spec in method_spec.findall('arg'):
			if num_args > 0:
				self.put(', ')

			arg_name = arg_spec.attrib['name']
			self.put('(' + arg_name + ')')
			num_args += 1

		vararg_spec = method_spec.find('vararg')
		if vararg_spec != None:
			if num_args > 0:
				self.put(', ')

			if is_gcc2:
				self.put('## vargs')
			else:
				self.put('__VA_ARGS__')

	def put_footer(self, guard_name):
		self.putln('#endif /* ' + guard_name + ' */')