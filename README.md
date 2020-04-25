# coop

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

## Startup
To start the script, enter:

```
python3 coop.py &
```
and view the logging:

```
tail -f coop.log
```

To stop executing the script type:

```
kill -9 PROCESS
```

Where PROCESS is the number the terminal returned afther startup.

