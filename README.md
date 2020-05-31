# coop

I created this program to automate my chicken coop by opening the door and turning on the light on the inside. Build instructions can be found in the wiki, together with more detailed instructions on how to setup.

## Installation
Simply enter the following command in your terminal

```
git clone https://github.com/53645714n/coop.git
```

Then, go to the directory:

```
cd coop
```

## Configuration
Then, to edit the config file:

```
nano coop.ini
```

Edit at least your location, the rest *can* be the same. It can also be totally different, up to you. To save, type: ctrl + o, ctrl + m, ctrl + x.

## Startup and shutdown
To start the script, enter:

```
python3 coop.py &
```

To run persistent, after logging off or shutting down the remote pc:

```
nohup python3 coop.py &
```

and view the logging:

```
tail -f coop.log
```

To stop executing the script find the PID first

```
pidof python3 coop.py
```

and type the results after kill -9 like this

```
kill -9 PID
```
