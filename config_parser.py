import yaml

with open('config.yml', 'r') as file:
   config = yaml.safe_load(file)

services = config.keys() 

commands = {}
for service in services:
   commands[service] = [c for c in config[service].keys()]
