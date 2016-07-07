Python OS 6 
---

Python OS 6 is the ultimate interface for touch-enabled microcomputers such as the Raspberry Pi. It offers a complete interface replacement, an application management and distribution system, and a UI toolkit for creating event-driven apps in Python.

The OS currently supports a 240x320 display, but this will change in the future.

Key features include:
* Application stack with support for threading, suspend, and app switch.
* UI components that include scrolling and dialogs.
* Event-driven callback programming that mixes the best of Python and Javascript.
* Color themes and icons that help you make beautiful, polished apps.
* Easy persistent storage.

##Get Started
###As a User

Simply download Python OS either on your computer (with Python and Pygame installed), or flash the disk image for your Pi (coming soon).

###As a Developer

Download and try out Python OS first.

Now, let's write a simple "Hello World" app.

Start by creating a folder titled "helloworld" under apps/.

In that folder, make two files, an \__init__.py and an app.json.

The app.json file will contain:
```
{
	"name": "helloworld",
	"title": "Hello World",
	"author": "Your_Name",
	"version": 1.0,
	"more": {
		"onStart": "hello",
	}
}
```

The \__init__.py file will contain:
```python
import pyos

def hello(state, app):
	app.ui.addChild(pyos.GUI.Text((5, 5), "Hello World!"))
```

Now, enter the About app and long press the "Start State Shell" button to launch the Debug App Bind feature. Open your app's folder, then press the green dot button to select it and associate the app with the system. 
