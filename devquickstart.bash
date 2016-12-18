#!/bin/bash

# chmod +x devquickstart.bash before running, to make this file executable.
# Example: ./devquickstart.bash -create
# Example: ./devquickstart.bash -clean

if [[ ! -d apps/helloworld ]]
then
	mkdir apps/helloworld
fi

if [[ $1 == '-create' ]]
then
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


elif [[ $1 == '-clean' ]]
then
	rm -rf apps/helloworld/

fi
