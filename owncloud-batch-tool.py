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

    emailBody=''
    for message in outputMessages:
        emailBody = emailBody + message.level + ": " + message.message + "\n"

    subject="owncloud batch tool"
    emailFrom=read_config_parameter("emailFrom",True,"text")
    emailTo=read_config_parameter("emailTo",True,"text")
    sslType=read_config_parameter("SMTPSSL",True,"text")
    
    eMail = """\
From: %s
To: %s
Subject: %s

%s""" % (emailFrom,emailTo,subject, emailBody)
    
    try:
        if sslType == "SSLTLS":
            server = smtplib.SMTP_SSL(read_config_parameter("SMTPServer",True,"text"), read_config_parameter("SMTPPort",True,"int"))
        else:
            server = smtplib.SMTP(read_config_parameter("SMTPServer",True,"text"), read_config_parameter("SMTPPort",True,"int"))
            
        server.ehlo()
        
        if sslType == "STARTTLS":
            server.starttls()
            server.ehlo()
            
        server.login(read_config_parameter("SMTPUser",True,"text"),read_config_parameter("SMTPPassword",True,"text"))
        server.sendmail(emailFrom, emailTo, eMail)
        server.close()
        print 'successfully sent the mail'
    except:
        print emailBody
        print "failed to send mail"
        print "---------------------------------------------------------------"
        raise

def generate_groups_by_domain_name(owncloudUser):
    groupsToBeIn=[]
    email=owncloudUser.split("@")
    if len(email) > 1:
        groupsToBeIn.append(email[1])

        domainName=email[1]
        groups = email[1].split(".")
        for domainCount in xrange (read_config_parameter("groupsByDomainNameSkipDomains",True,"int")):
            domainName=domainName.rpartition(".")[0]

        while len(domainName)>0:
            groupsToBeIn.append(domainName)
            domainName=domainName.partition(".")[2]
    return groupsToBeIn

import ConfigParser
import argparse
import owncloud
import csv
import smtplib

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
    oc.login(read_config_parameter ('adminUser',True), read_config_parameter ('adminPassword',True))
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
        if len(csvUsers[owncloudUser]['groups']) > 0 and csvUsers[owncloudUser]['groups'][0]:
            groupsToBeIn=csvUsers[owncloudUser]['groups']

        #generate all group names (by domain name) that the user should be in
        if read_config_parameter("groupsByDomainName",True,"boolean") is True:
           groupsToBeIn=groupsToBeIn+generate_groups_by_domain_name(owncloudUser)

        #delete user from groups he should not be part of
        for currentUserGroup in currentUserGroups:
            if currentUserGroup not in groupsToBeIn:
                oc.remove_user_from_group(owncloudUser,currentUserGroup)
                outputMessages.append(message('removed user from group' + currentUserGroup ,'mesage'))    

        #add user to groups
        for group in groupsToBeIn:
            group=group.strip()
            try:
                oc.add_user_to_group(owncloudUser,group)
                outputMessages.append(message("added user " + owncloudUser + " to group " +  group ,'message'))
            except owncloud.ResponseError, e:
                if e.status_code == 102:
                    outputMessages.append(message("could not add user '" + owncloudUser + "' to group '" +  group + "' group does not exist"  ,'error'))
                    pass
                else:
                    outputMessages.append(message("could not add user '" + owncloudUser + "' to group '" +  group + "' " + e.status_code,'error'))
                     

        try:
            outputMessages.append(message("set quota for '" + owncloudUser + "' to '" + csvUsers[owncloudUser]['quota'] + "'", 'message'))
        except owncloud.ResponseError, e:
            outputMessages.append(message("could not set quota for user '" + owncloudUser + "' " + e.status_code ,'error'))

emailMessages(outputMessages)
