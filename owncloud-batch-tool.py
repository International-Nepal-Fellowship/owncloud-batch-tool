def read_config_parameter (name,mandatory=False):
    try:
        return config.get('DEFAULT', name);
    except ConfigParser.NoOptionError:
        if mandatory is True:
            exit(name + " argument is missing")
        else:
            return;

import ConfigParser
import argparse

parser = argparse.ArgumentParser(description='OwnCloud Batch Tool')
parser.add_argument('--config', dest='configFile', default="config.cfg",  
                   help='path of the configuration file')

args = parser.parse_args()
print args.configFile

config = ConfigParser.ConfigParser()
config.read(args.configFile)

print read_config_parameter ('URL',True)
print read_config_parameter ('adminUser',True)
