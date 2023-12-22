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

### Configure the SSV docker container to use journal for logging

To tell docker to use journal as its log engine you can append `--log-driver=journald` to the docker run command.

This is an example command you could use

```bash
docker run --restart unless-stopped --name ssv_node -e \
CONFIG_PATH=/config.yaml -p 13001:13001 -p 12001:12001/udp -p 15000:15000 \
-v "$(pwd)/config.yaml":/config.yaml \
-v "$(pwd)":/data \
-v "$(pwd)/password":/password \
-v "$(pwd)/encrypted_private_key.json":/encrypted_private_key.json \
--log-driver=journald \  # This is to set up journal as the logging handler for docker
-it "bloxstaking/ssv-node:latest" make BUILD_PATH="/go/bin/ssvnode" start-node
```

After you have configure docker, you can view live logs from the SSV node with this command (assuming you have named the container "ssv_node"):
`journalctl CONTAINER_NAME=ssv_node -f`

To use the logger you can pipe the output into the python script using:
`journalctl CONTAINER_NAME=ssv_node -f | ssvlogger`

## Additional Flags

You can also use different flags to disable or enable certain features in the script

|short command|long command|description|
|-|-|-|
|**-n**|--no-spam|Disables connection and registry event logs
|**-t**|--traceback|Shows tracebacks for errors
