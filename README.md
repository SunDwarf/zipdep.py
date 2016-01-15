## zipdep.py

*zipdep* is a simple way of helping fix the Python Dependency Problem. That is, how painful maintaining dependencies 
for different apps and projects is on a system.

__*Zipdeps may be constituted as static linking. If this is the case, make sure to have your projects or libraries 
under the correct licences. Contact your lawyer if you are unsure about anything related to the legality of using 
this in your project.*__

For best effect, zipdep.py should be combined with a [Zipapp](https://docs.python.org/3/library/zipapp.html).

__Contents__

 - [Installation](#installation)
 - [Usage](#usage)
 - [Why Zipdeps](#why)
 
### Installation

zipdep.py can be installed from [PyPI](https://pypi.python.org/), or from Git.

    pip install zipdep # pypi
    pip install git+https://git.veriny.tf/SunDwarf/zipdep.py.git # veriny git
    
zipdep.py is entirely self-contained, and will install to your `bin` directory, if available.

### Usage

zipdep.py is very simple to use.

`zipdep file1.py file2.py # etc etc`

This will automatically package up all imported dependencies into a file called `file1.py.zipdep.py`.

**ALL YOUR DEPENDENCIES NEED TO BE IMPORTED IN YOUR FILES SPECIFIED. IT CANNOT SCAN DEPENDENCIES THAT AREN'T 
IMPORTED. ANY CODE THAT RUNS ON IMPORT WILL BE RUN WHEN ZIPDEP RUNS.**

## Why

With Python dependencies, there's a few solutions:

 1. Install all dependencies globally **(BAD)**
 2. Tell users to create a virtualenv, and install packages there **(Good, but hard)**
 3. Use a self-contained virtualenv **(Good, but can be suboptimal)**

Installing dependencies globally is a Bad Idea™. They can conflict between your apps, and make developing hard as you
 can't remember which ones you use and which ones to ship.  
 
Getting users to create a virtualenv is the best solution in an ideal world. Unfortunately, this world is not an 
ideal world.

 - Virtualenvs are hard to wrap your head around
 - They can be clunky to use with activating shell files and changing paths.
 - They take time to set up properly, and end users cannot be trusted to always set these up.
 
A self-contained virtualenv is a good idea, and the most pain-free of all the options above. Programs such as [Let's 
Encrypt Official Client](https://github.com/letsencrypt/letsencrypt) use this. However, this is for large programs, 
or programs that have multiple large components.
 
Zipdeps solve these problems, in combination with a zipapp, by packaging all your dependencies INTO your app. A small
 amount of code is injected, which automatically unpacks your dependencies and uses `zipimport` to load them before 
 your code is ran. This saves any pain with managing dependencies. 
 
Note that this approach only works for stand-alone scripts, as an entry point is required to setup the zipdeps.

### Security risks

This code is *probably* about as secure as a regular virtualenv. Temporary directories are only rwx by the current 
user, so the zipfile shouldn't be able to be injected into.  Keep in mind I am not a security expert, and these 
claims are not proven, so feel free to point out anything that's wrong security-wise.