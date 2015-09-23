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

def emailMessages (outputMessages):
    for message in outputMessages:
        print message.level + " " + message.message

def generate_groups_by_domain_name(owncloudUser):
    print "To implement"

import ConfigParser
import argparse
import owncloud
import csv

class message:
    level = ''
    message = ''
    def __init__(self,message,level='message'):
        if level not in ['message','error']:
            self.level='messsage'
        else:
            self.level=level
            
        self.message=message
            

outputMessages = []

parser = argparse.ArgumentParser(description='OwnCloud Batch Tool')
parser.add_argument('--config', dest='configFile', default="config.cfg",  
                   help='path of the configuration file')

args = parser.parse_args()

config = ConfigParser.ConfigParser()
config.read(args.configFile)

csvUsers = {}

#read user definition file
with open(read_config_parameter("userDefinitionFile",True)) as userDefinitionFile:
    for user in csv.DictReader(userDefinitionFile,delimiter=';', quotechar='"'):
        user['groups']=user['groups'].split(",")
        csvUsers[user['userName']] = user

read_config_parameter("URL")
oc = owncloud.Client(read_config_parameter ('URL',True))

try:
    print oc.login(read_config_parameter ('adminUser',True), read_config_parameter ('adminPassword',True))
except:
    outputMessages.append(message("could not login " ,'error'))
    emailMessages

owncloudUsers = oc.search_users("")

#loop trough all users that were found in owncloud
for owncloudUser in owncloudUsers:
    owncloudUser=owncloudUser.text
    if owncloudUser in csvUsers:
        groupsToBeIn=[]
        currentUserGroups=oc.get_user_groups(owncloudUser)
        #groups that the user should be in (from CSV file)
        groupsToBeIn=csvUsers[owncloudUser]['groups']

        #generate all group names (by domain name) that the user should be in
        if read_config_parameter("groupsByDomainName",True,"boolean") is True:
           groupsToBeIn=groupsToBeIn+generate_groups_by_domain_name(owncloudUser)

        #delete user from groups he should not be part of
        for currentUserGroup in currentUserGroups:
            if currentUserGroup not in groupsToBeIn:
                oc.remove_user_from_group(userName,currentUserGroup)
                outputMessages.append(message('removed user from group','mesage'))    

        #add user to groups
        for group in groupsToBeIn:
            group=group.strip()
            try:
                oc.add_user_to_group(owncloudUser,group)
                outputMessages.append(message("added user " + owncloudUser + " to group " +  group ,'message'))
            except owncloud.ResponseError, e:
                if e.status_code == 102:
                    outputMessages.append(message("user " + owncloudUser+ " already in group " +  group ,'message'))                    
                    pass
                else:
                    outputMessages.append(message("could not add user " + owncloudUser + " to group " +  group + " " + e.res.text ,'error'))

        try:
            outputMessages.append(message("set quota for " + owncloudUser + " to " + csvUsers[owncloudUser]['quota']  ,'message'))
        except owncloud.ResponseError, e:
            outputMessages.append(message("could not set quota for user " + owncloudUser + " " + e.res.text ,'error'))

'''
with open(read_config_parameter("userDefinitionFile",True)) as userDefinitionFile:
    userDefinition = csv.DictReader(userDefinitionFile,delimiter=';', quotechar='"')
    for user in userDefinition:
        userName=user['userName'].strip()
        currentUserGroups=oc.get_user_groups(userName)
        groups=user['groups'].split(",")

        #delete user from groups he should not be part of
        for currentUserGroup in currentUserGroups:
            if currentUserGroup not in groups:
                oc.remove_user_from_group(userName,currentUserGroup)
                outputMessages.append(message('removed user from group','mesage'))
                
        for group in groups:
            group=group.strip()
            try:
                oc.add_user_to_group(userName,group)
                outputMessages.append(message("added user " + userName + " to group " +  group ,'message'))
            except owncloud.ResponseError, e:
                if e.status_code == 102:
                    outputMessages.append(message("user " + userName + " already in group " +  group ,'message'))                    
                    pass
                else:
                    outputMessages.append(message("could not add user " + userName + " to group " +  group + " " + e.res.text ,'error'))
                                
        try:
            print(oc.set_user_attribute(userName,"quota",int(user['quota'])))
            outputMessages.append(message("set quota for " + userName + " to " + user['quota']  ,'message'))
        except owncloud.ResponseError, e:
            outputMessages.append(message("could not set quota for user " + userName + " " + e.res.text ,'error'))

if read_config_parameter("groupsByDomainName",True,"boolean") is True:
    users = oc.search_users("")
    print "groups by domain name"
    for user in users:
        # print user.text
        email=user.text.split("@")
        
        if len(email) > 1:
            try:
                oc.add_user_to_group(user.text,email[1])
                outputMessages.append(message("added user " + user.text + " to group " +  email[1] ,'message'))
            except owncloud.ResponseError, e:
                if e.status_code == 102:
                    outputMessages.append(message("user " + user.text + " already in group " +  email[1] ,'message'))
                    pass
                else:
                    outputMessages.append(message("could not add user " + user.text + " to group " + email[1] + " " + e.res.text ,'error'))
  
            domainName=email[1]
            groups = email[1].split(".")
            for domainCount in xrange (read_config_parameter("groupsByDomainNameSkipDomains",True,"int")):
                domainName=domainName.rpartition(".")[0]

            while len(domainName)>0:
                try:
                    oc.add_user_to_group(user.text,domainName)
                    outputMessages.append(message("added user " + user.text + " to group " +  domainName ,'message'))
                except owncloud.ResponseError, e:
                    if e.status_code == 102:
                        outputMessages.append(message("user " + user.text + " already in group " +  domainName ,'message'))
                        pass
                    else:
                        outputMessages.append(message("could not add user " + user.text + " to group " + domainName + " " + e.res.text ,'error'))
                        
                domainName=domainName.partition(".")[2]
                
#            lastGroupNum=len(groups)-read_config_parameter("groupsByDomainNameSkipDomains",True,"int")
#            for group in groups[:lastGroupNum]:
#                outputMessages.append(message("added user " + user.text + " to group " +  group ,'message'))
#                oc.add_user_to_group(user.text,group)
'''

emailMessages(outputMessages)
