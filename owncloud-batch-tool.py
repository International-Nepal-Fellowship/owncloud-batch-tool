def read_config_parameter (name,mandatory=False,type="text"):
    try:
        if type=="int":
            return config.getint('DEFAULT', name);
        elif type=="float":
            return config.getfloat('DEFAULT', name);
        elif type=="boolean":
            return config.getboolean('DEFAULT', name);
        else:
            return config.get('DEFAULT', name);
    except ConfigParser.NoOptionError:
        if mandatory is True:
            exit(name + " argument is missing")
        else:
            return;

import ConfigParser
import argparse
import owncloud
import csv

parser = argparse.ArgumentParser(description='OwnCloud Batch Tool')
parser.add_argument('--config', dest='configFile', default="config.cfg",  
                   help='path of the configuration file')

args = parser.parse_args()
print args.configFile

config = ConfigParser.ConfigParser()
config.read(args.configFile)

print read_config_parameter ('URL',True)
print read_config_parameter ('adminUser',True)
read_config_parameter("URL")
oc = owncloud.Client(read_config_parameter ('URL',True))

oc.login(read_config_parameter ('adminUser',True), read_config_parameter ('adminPassword',True))

with open(read_config_parameter("userDefinitionFile",True)) as userDefinitionFile:
    userDefinition = csv.DictReader(userDefinitionFile,delimiter=';', quotechar='"')
    for user in userDefinition:
        print(user)

if read_config_parameter("groupsByDomainName",True,"boolean") is True:
    users = oc.search_users("")
    print "groups by domain name"
    for user in users:
        # print user.text
        email=user.text.split("@")
        if len(email) > 1:
            groups = email[1].split(".")
            lastGroupNum=len(groups)-read_config_parameter("groupsByDomainNameSkipDomains",True,"int")
            for group in groups[:lastGroupNum]:
                print "user:"+user.text+"-"+group
                oc.add_user_to_group(user.text,group)

