#!/usr/bin/env python3
# encoding: utf-8
# 
# MIT Licensed
# https://bmintz.mit-license.org/@2017

"""
command_gen.py: generate commands for custom hat modules

item names.txt format:
name \t damage value (0 if none)
"""

import os
import json


def commands_iter(input_filename='item names.txt'):
	
	yield from (
		'scoreboard players set @s[score_hat_min=1,score_hat=1] hat 0 {Inventory:[{Slot:103b}]}',
		'tellraw @s[score_hat_min=0,score_hat=0] {"text":"You already have something on your head.","color":"gray"}',
	)
	
	scoreboard_command='scoreboard players set @a[team=Donator,score_hat_min=1,score_hat=1] hat {score} {{SelectedItem:{{id:"minecraft:{item_name}",Damage:{item_damage}s}}}}'
	clear_command='clear @a[score_hat_min={score},score_hat={score}] minecraft:{item_name} {item_damage} 1'
	replaceitem_command='replaceitem entity @a[score_hat_min={score},score_hat={score}] slot.armor.head minecraft:{item_name} 1 {item_damage}'
	
	with open(input_filename) as items_file:
		# score_hat=1 is reserved for players who have run /trigger hat set 1
		for score, item in enumerate(items_file, 2):
			# split tabs and remove final newlines
			item = item.rstrip().split()
			
			for command in (scoreboard_command, clear_command, replaceitem_command):
				yield command.format(
						score=score,
						item_name=item[0], # JSON strings must be quoted
						item_damage=item[1],
				)
	
	yield from (
		'tellraw @s[score_hat_min=1,score_hat=1] {"text":"Invalid item. You need to hold a custom hat in your hand.","color":"gray"}',
		'scoreboard players set @s hat -1',
	)


def write_commands(input_filename='', output_filename='commands.txt'):
	"""Write commands from commands_iter() to a file
	
	Useful for <1.12.x servers, which do not support advancements.
	"""
	
	with open(output_filename, 'w') as outfile:
		if input_filename:
			commands = commands_iter(input_filename)
		# if output_filename isn't specified, use default
		else:
			commands = commands_iter()
		
		for command in commands_iter(input_filename):
			outfile.write(command + '\n')


def parse_advancement_name(name):
	"""Convert an in-game advancement name to a file path
	
	>>> parse_advancement_name('null_byte:custom_hat')
	null_byte/custom_hat.json
	>>> parse_advancement_name('null_byte:hat/command')
	null_byte/hat/command.json
	"""
	
	# namespace:subdir/advancement → namespace/subdir/advancement.json
	fullpath = name.replace(':', '/') + '.json'
	return os.path.split(fullpath)


def to_advancement(name, iterable=commands_iter()):
	"""Convert commands from iterable to an advancement JSON object
	
	name is the in-game name of the advancement
	iterable is something that provides commands
	(the iterable should not provide 'advancement revoke ...')
	"""
	
	# set up a basic command-based advancement as a python dict
	# this is a template applicable to all similar
	# advancements
	advancement = {
		'criteria': {
			'run': {
				'trigger': 'minecraft:impossible'
			}
		},
		'rewards': {
			'commands': [
				'advancement revoke @s only {}'.format(name)
			]
		}
	}
	
	# add the command lines to the commands reward
	advancement['rewards']['commands'].extend(iterable)
	
	return advancement

	
def write_advancement(contents: str, name):
	output_dir, output_filename = parse_advancement_name(name)
	output_dir = os.path.join('advancements', output_dir)
	
	try:
		os.mkdir(output_dir)
	except FileExistsError: # if the dir already exists, great!
		pass
	
	# if there's any other errors, let them propagate
	# (ie halt the module and tell the user)
	
	with open(os.path.join(output_dir, output_filename), 'w') as f:
		json.dump(contents, f)


if __name__ == '__main__':
	name = 'null_byte:hat/equip'
	write_advancement(to_advancement(name), name)
