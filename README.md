# owncloud-batch-tool
Tool to run different batch tasks on a OwnCloud server (using the public API)

##Requirements
* read configuration from file (txt? ini?)
* read user data from CSV file (userDefinitionFile)
* read shared folder data from CSV file (sharedFolderFile)
* do not create groups, add users only to existing groups
* add users to groups according to the domain name of the username
* add users to groups according to the userDefinitionFile file
* if userDefinitionFile file was changed delete users from groups
* forcefully share folders/files with groups according to the sharedFolderFile

##userDefinitionFile CSV file content
* username (email address)
* multiple groupnames
* quota

##sharedFolderFile CSV file content
* shared folder
* groupnames
* permissions
