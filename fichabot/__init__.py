import os

modules = [
    module for module in os.listdir(os.path.dirname(__file__))
    if module.endswith('.py') and \
    module != '__init__.py' and module != '__main__.py' 
]

for module in modules:
    __import__(f'fichabot.{module[:-3]}')