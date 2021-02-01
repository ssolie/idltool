# This script is a codegen module for idltool.py.
#
# gen_interfaces_file.py - Generates include/interfaces/<libname>.[h|i] files
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

class InterfacesFileC:
	""" Code generator to create library interface files in C.
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

		path = os.path.join(out_dir, 'include', 'interfaces')
		try:
			os.makedirs(path)
		except:
			pass

		path = os.path.join(path, lib_name + '.h')
		self.out_file = open(path, "w+")

		guard_label = lib_name.upper() + '_INTERFACE_DEF_H'

		self.put_header(guard_label, tool_version)
		self.putln()
		self.put_includes()
		self.putln()
		self.put_namespace_top()
		self.putln()

		for iface_spec in self.spec_file.interfaces_spec():
			struct_name = iface_spec.attrib['struct']

			self.putln('struct ' + struct_name)
			self.putln('{')
			self.putln('\tstruct InterfaceData Data;')
			self.putln()

			private_method_num = 1

			for method in iface_spec:
				if method.tag != 'method':
					# Skip non-method element.
					continue

				method_name      = method.attrib['name']
				method_status    = method.get('status')
				method_lifecycle = method.get('lifecycle')

				method_result = method.attrib['result']
				if method_lifecycle == 'deprecated':
					method_result = 'DEPRECATED ' + method_result

				if method_status == 'private':
					if args['f']:
						self.putln('\tAPTR Private' + str(private_method_num) + ';')
						private_method_num += 1
						continue

				if method_status == 'unimplemented':
					self.putln('\tAPTR ' + method_name + '_UNIMPLEMENTED;')
					continue

				method_self = 'struct ' + struct_name + ' *Self'

				self.put('\t' + method_result + ' APICALL ')
				self.put('(*' + method_name + ')')
				self.put('(' + method_self)

				self.put_method_args(method)

				self.putln(');')

			self.putln('};')
			self.putln()

		self.put_namespace_bottom()
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

		self.putln('*/')

	def put_includes(self):
		self.putln('#include <exec/types.h>')
		self.putln('#include <exec/exec.h>')
		self.putln('#include <exec/interfaces.h>')
		self.putln()

		for spec in self.spec_file.includes_spec():
			name = spec.text.strip()
			self.putln('#include <' + name + '>')

	def put_namespace_top(self):
		self.putln('#ifdef __cplusplus')
		self.putln('#ifdef __USE_AMIGAOS_NAMESPACE__')
		self.putln('namespace AmigaOS {')
		self.putln('#endif')
		self.putln('extern "C" {')
		self.putln('#endif')

	def put_method_args(self, method_spec):
		for arg_spec in method_spec.findall('arg'):
			self.put(', ')
			arg_name = arg_spec.attrib['name']
			arg_type = arg_spec.attrib['type']

			function_ptr = arg_type.find('(*)')
			if function_ptr != -1:
				self.put(arg_type[0:function_ptr - 1] + ' (*' + arg_name + ')()')
			else:
				self.put(arg_type + ' ' + arg_name)

		vararg_spec = method_spec.find('vararg')
		if vararg_spec != None:
			self.put(', ')
			arg_name = vararg_spec.attrib['name']
			arg_type = vararg_spec.attrib['type']
			self.put('...')

	def put_namespace_bottom(self):
		self.putln('#ifdef __cplusplus')
		self.putln('}')
		self.putln('#ifdef __USE_AMIGAOS_NAMESPACE__')
		self.putln('}')
		self.putln('#endif')
		self.putln('#endif')

	def put_footer(self, guard_name):
		self.putln('#endif /* ' + guard_name + ' */')


class InterfacesFileAssembly:
	""" Code generator to create library interface files in assembly.
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

		path = os.path.join(out_dir, 'include', 'interfaces')
		try:
			os.makedirs(path)
		except:
			pass

		path = os.path.join(path, lib_name + '.i')
		self.out_file = open(path, "w+")

		guard_label = lib_name.upper() + '_INTERFACE_DEF_H'

		self.put_header(guard_label, tool_version)
		self.putln()
		self.put_includes()
		self.putln()

		for iface_spec in self.spec_file.interfaces_spec():
			struct_name = iface_spec.attrib['struct']
			asm_prefix  = iface_spec.attrib['asmprefix']

			self.putln('STRUCTURE ' + struct_name + ', InterfaceData_SIZE')

			private_method_num = 1

			for method in iface_spec:
				method_name   = method.attrib['name']
				method_status = method.get('status')

				if method_status == 'private':
					if args['f']:
						self.putln('\t    FPTR ' + asm_prefix + '_Private' + str(private_method_num))
						private_method_num += 1
						continue

				if method_status == 'unimplemented':
					self.putln('\t    FPTR ' + struct_name + '_' + method_name + '_UNIMPLEMENTED')
					continue

				self.putln('\t    ' + 'FPTR ' + asm_prefix + '_' + method_name)

			self.putln('\tLABEL ' + struct_name + '_SIZE')
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
		self.putln('/*')
		self.putln('** This file was machine generated by idltool.py ' + tool_version + '.')
		self.putln('** Do not edit.')

		copyright = self.spec_file.library_spec().find('copyright')
		if copyright != None:
			self.putln('**')
			self.putln('** ' + copyright.text.strip())
			self.putln('**')

		self.putln('*/')

	def put_includes(self):
		self.putln('#include <exec/types.i>')
		self.putln('#include <exec/exec.i>')
		self.putln('#include <exec/interfaces.i>')

	def put_footer(self, guard_name):
		self.putln('#endif /* ' + guard_name + ' */')
