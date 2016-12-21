#!/bin/bash

# chmod u+x devquickstart.bash before running, to make this file executable.
# Example: ./devquickstart.bash --create
# Example: ./devquickstart.bash --clean
if [[ -z "$1" ]]
then
	echo "Usage: devquickstart.bash [OPTIONS]"
	echo
	echo "Options: "
	printf "\t-create\t\tGenerate necesarry files in apps/helloworld and the helloworld directory itself.\n\n"
    printf "\t-clean\t\tClean generated directory and files in apps/helloworld and helloworld directory itself.\n\n"
fi

if [[ "$1" == '--create' || "$1" == '-cr' ]]
then
	if [[ ! -d apps/helloworld ]]
	then

		mkdir apps/helloworld
	fi
	cat << __EOL__ | expand -t4  > apps/helloworld/app.json
{
	"name": "helloworld",
	"title": "Hello World",
	"author": "Your_Name",
	"version": 1.0,
	"more": {
	"onStart": "hello"
	}
}

__EOL__

	cat << __EOL__ | expand -t4 > apps/helloworld/__init__.py
import pyos

def hello(state, app):
	app.ui.addChild(pyos.GUI.Text(5,5), "Hello World!"))

__EOL__


elif [[ "$1" == '--clean' || "$1" == 'cl' ]]
then
	if [[ -d apps/helloworld ]]
	then
		rm -rf apps/helloworld
		echo "Success."
	else
		echo "Directory is not exist."
		exit 1	
	fi	
fi

exit 0
