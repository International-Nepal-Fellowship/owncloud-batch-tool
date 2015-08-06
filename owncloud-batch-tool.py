#get the configuration file
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config.cfg')
print config.get('DEFAULT', 'URL')
print config.get('DEFAULT', 'adminUser')
