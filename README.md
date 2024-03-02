# SSV logger

A simple tool to make the SSV node's logs easier to view.

## Dependencies

- Python3
- [Colorama](https://pypi.org/project/colorama/)

## Installation

```bash
python3 -m pip install ssvlogger
```

## How to use

### With docker

To tell docker to use journal as its log engine you can append `--log-driver=journald` to the docker run command.

This is an example command you could use

```bash
docker run --restart unless-stopped --name ssv_node -e \
.... # other flags
--log-driver=journald \  # This is to set up journal as the logging handler for docker
-it "bloxstaking/ssv-node:latest" make BUILD_PATH="/go/bin/ssvnode" start-node
```

After you have configure docker, you can view live logs from the SSV node with this command (assuming you have named the container "ssv_node"):
`journalctl CONTAINER_NAME=ssv_node -f`

To use the logger you can pipe the output into the python script using:
`journalctl CONTAINER_NAME=ssv_node -f | ssvlogger`

### Without docker

If you do not use docker it will only work as a service, assuming you have a service called "ssv_node" you should run
`journalctl -u ssv_node -f | ssvlogger`

## Additional Flags

You can also use different flags to disable or enable certain features in the script

|short command|long command|description|
|-|-|-|
|**-n**|--no-spam|Disables connection and registry event logs
|**-t**|--traceback|Shows tracebacks for errors
