# -*- coding: utf-8 -*-
import collections
import traceback

from utils import tool, constant
from utils.plugin import Plugin


class PluginManager:
	def __init__(self, server, plugin_folder):
		self.plugin_folder = plugin_folder
		self.server = server
		self.logger = server.logger
		self.plugins = []
		self.command_prefix_listeners = None

	def load_plugin(self, file_name):
		try:
			plugin = Plugin(self.server, file_name)
			plugin.load()
		except:
			self.logger.warning(f'Fail to load plugin {file_name}')
			self.logger.warning(traceback.format_exc())
			return False
		else:
			self.plugins.append(plugin)
			self.logger.info('Plugin {} loaded'.format(plugin.file_name))
			return True

	def unload_plugin(self, plugin):
		try:
			plugin.unload()
		except:
			self.logger.warning(f'Fail to unload plugin {plugin.file_name}')
			self.logger.warning(traceback.format_exc())
			ret = False
		else:
			self.logger.info('Plugin {} unloaded'.format(plugin.file_name))
			ret = True
		finally:
			self.plugins.remove(plugin)
		return ret

	def reload_plugin(self, plugin):
		try:
			plugin.reload()
		except:
			self.logger.warning(f'Fail to reload plugin {plugin.file_name}')
			self.logger.warning(traceback.format_exc())
			return False
		else:
			self.logger.info('Plugin {} reloaded'.format(plugin.file_name))
			return True

	def load_plugins(self):
		self.command_prefix_listeners = {}
		name_dict = {plugin.file_name: plugin for plugin in self.plugins}
		file_list = tool.list_py_file(constant.PLUGIN_FOLDER)
		counter_all = counter_load = counter_unload = counter_reload = 0
		for file_name in file_list:
			if file_name in name_dict:
				plugin = name_dict[file_name]
				counter_reload += self.reload_plugin(plugin)
				counter_all += 1
			else:
				counter_load += self.load_plugin(file_name)
				counter_all += 1
		for plugin in self.plugins:
			if plugin.file_name not in file_list:
				counter_unload += self.unload_plugin(plugin)
				counter_all += 1
		counter_fail = counter_all - counter_load - counter_unload - counter_reload
		msg = ''
		if counter_load > 0:
			msg += 'Loaded: {} plugins '.format(counter_load)
		if counter_unload > 0:
			msg += 'Unloaded: {} plugins '.format(counter_unload)
		if counter_reload > 0:
			msg += 'Reloaded: {} plugins '.format(counter_reload)
		if counter_fail > 0:
			msg += 'Failed: {} plugins '.format(counter_fail)
		if msg == '':
			msg = 'No plugin operation has occurred'
		self.logger.info(msg)

	def call(self, func, args=()):
		for plugin in self.plugins:
			plugin.call(func, args)