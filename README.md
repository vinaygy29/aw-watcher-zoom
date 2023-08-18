aw-watcher-zoom
==================

Watches your current Zoom meeting. This is on a per-user basis since it uses the Zoom Web API, so you don't need to run it on all your machines if you don't want the redundancy.



## Usage

### Step 0: Create Zoom Server-to-Server OAuth app

Go to [App Marketplace](https://marketplace.zoom.us/develop/create) and create a new application.

In the app settings, add below scopes 

#### dashboard:master

#### dashboard_home:read:admin

#### dashboard_meetings:read:admin


### Step 1: Install package (using poetry)

Requirements: Requires that you have poetry installed.

First install the package and its dependencies:

```sh
poetry install
```

First run (generates empty config that you need to fill out):

```sh
poetry run aw-watcher-zoom
```
### Step 1: Install package (without poetry, using only pip)

Install the requirements:

```sh
pip install .
```

First run (generates empty config that you need to fill out):
```sh
python aw-watcher-zoom/main.py
```

### Step 2: Enter credentials

If this is the first time you run it on your machine, it will give you an error, this is normal.
Just uncomment the configuration lines and fill in the config (the directory is referenced in the error).

Run the script again and...
You're done! Start a meeting on Zoom on your devices and it should start logging.
