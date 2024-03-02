#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A simple python string to parse SSV node logs and make them legible"""

# pylint: disable=C0103, C0301, W0718, R1702

import sys
import json
import colorama

def extract_time_and_stat(log):
    """Extracts time and status from a log"""
    time = log[0].split(': ', maxsplit=1)[1]
    time = time.replace('T', ' ').split('.', maxsplit=1)[0]
    time = colorama.Fore.CYAN + time + colorama.Fore.RESET

    stat = log[1]

    if stat == "DEBUG":
        stat = colorama.Fore.BLUE + stat + colorama.Fore.RESET
    elif stat == "WARN":
        stat = colorama.Fore.YELLOW + stat + colorama.Fore.RESET
    elif stat == "ERROR":
        stat = colorama.Fore.LIGHTRED_EX + stat + colorama.Fore.RESET
    elif stat == "FATAL":
        stat = colorama.Fore.RED + stat + colorama.Fore.RESET

    return time, stat

# pylint: disable=too-many-locals,too-many-branches,too-many-statements

def main():
    """Error handling function and soft exit"""

    try:
        main_function()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as error:
        print(f"{colorama.Fore.RED}Error: {error}{colorama.Fore.RESET}")
        sys.exit(1)

def main_function():
    """Main function"""

    colorama.init()
    NOSPAM = False
    FULLERRORS = False

    if "--no-spam" in sys.argv or "-n" in sys.argv:
        NOSPAM = True

    if "--traceback" in sys.argv or "-t" in sys.argv:
        FULLERRORS = True

    additional_logs = []

    for line in sys.stdin:
        log = line.strip().split("        ")

        if "systemd[1]" in line: # Ignore systemd messages
            continue

        if len(log) < 2:         # Ignore any non standard messages
            continue

        # Time and information recovery

        time, stat = extract_time_and_stat(log)

        try:
            # P2P network

            if (log[2] == "P2PNetwork.ConnHandler") and log[3] == "Verified handshake nodeinfo":
                if NOSPAM:
                    continue
                data = json.loads(log[4])
                if "conn_dir" not in data.keys():
                    print(data)
                direction = data["conn_dir"]
                ip = data["remote_addr"]
                ip = (ip[1:]).split("/")
                ip = f"{ip[1]}:{ip[3]}"
                addr = data["peer_id"][:16] + "..."
                tolog = f"Processing {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{direction}{colorama.Fore.RESET}" + \
                    f" connection from {colorama.Fore.GREEN}{addr}@{ip}{colorama.Fore.RESET}"

            elif (log[2] == "P2PNetwork") and log[3] == "Verified handshake nodeinfo":
                continue

            elif (log[2] == "P2PNetwork") and log[3] == "starting":
                tolog = "Starting P2P networking"

            elif (log[2] == "P2PNetwork") and log[3] == "configuring":
                tolog = "Configuring P2P networking"

            elif (log[2] == "P2PNetwork") and log[3] == "services configured":
                data = json.loads(log[4])
                tolog = f"Configured P2P networking. Node id: {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{data['selfPeer'][:16]}...{colorama.Fore.RESET}"

            elif (log[2] == "P2PNetwork") and log[3] == "discovery: using discv5":
                data = json.loads(log[4])
                tolog = f"Using discv5 for discovery. Using {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{len(data['bootnodes'])}{colorama.Fore.RESET} bootnodes."

            # Execution Client

            elif log[2] == "execution_client" and log[3] == "fetched registry events":
                if NOSPAM:
                    continue
                data = json.loads(log[4])
                tolog = f"Processed {colorama.Fore.LIGHTMAGENTA_EX}{data['events']}" + \
                    f" {colorama.Fore.RESET}registry events ({data['progress']} complete)"

            elif log[2] == "execution_client" and log[3] == "connected to execution client":
                data = json.loads(log[4])
                tolog = f"Connected to execution client at {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{data['address']}{colorama.Fore.RESET} in {data['took']}"

            # EventSyncer

            elif log[2] == "EventSyncer" and log[3] == "subscribing to ongoing registry events":
                data = json.loads(log[4])
                tolog = "Subscribing to registry contract events after block " + \
                    f"{colorama.Fore.LIGHTMAGENTA_EX}{data['from_block']}{colorama.Fore.RESET}"

            elif log[2] == "EventSyncer" and log[3] == "finished syncing historical events":
                data = json.loads(log[4])
                tolog = f"Processing registry events from block {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{data['from_block']}{colorama.Fore.RESET} to {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{data['last_processed_block']}{colorama.Fore.RESET}"

            # DutyScheduler

            elif log[2] == "DutyScheduler" and log[3] == "duty scheduler started":
                tolog = "Started Duty Scheduler"

            elif log[2] == "DutyScheduler" and log[3] == "starting duty handler":
                data = json.loads(log[4])
                tolog = f"Started {colorama.Fore.GREEN}{data['handler'].replace('_', ' ').lower()}" + \
                    f"{colorama.Fore.RESET} duty scheduler"

            elif log[2] == "DutyScheduler" and log[3] == "failed to submit beacon committee subscription":
                data = json.loads(log[4])
                tolog = f"Failed to submit {colorama.Fore.CYAN}{data['handler']}{colorama.Fore.RESET} job.\n"
                tolog += "Error: " + data['error'].replace('\\"', '"')

            # Controller

            elif log[2] == "Controller.Validator" and "starting duty processing" in log[3]:
                data = json.loads(log[4])
                role = data["role"]
                slot = data["slot"]
                validator = data["pubkey"][:6] + "..."
                tolog = f"Processing {colorama.Fore.LIGHTMAGENTA_EX}{role}{colorama.Fore.RESET}" + \
                    f" duty at slot {colorama.Fore.LIGHTMAGENTA_EX}{slot}{colorama.Fore.RESET}" + \
                    f" for validator {colorama.Fore.LIGHTMAGENTA_EX}{validator}{colorama.Fore.RESET}"

            elif log[2] == "Controller.Validator" and "successfully submitted attestation" in log[3]:
                data = json.loads(log[4])
                role = data["role"]
                slot = data["slot"]
                validator = data["pubkey"][:6] + "..."
                tolog = "Sucessfully submitted attestation at slot " + \
                    f"{colorama.Fore.LIGHTMAGENTA_EX}{slot}{colorama.Fore.RESET}" + \
                    f" for validator {colorama.Fore.LIGHTMAGENTA_EX}{validator}{colorama.Fore.RESET}"

            elif log[2] == "Controller" and log[3] == "starting validators setup...":
                data = json.loads(log[4])
                tolog = f"Configuring {colorama.Fore.YELLOW}{data['shares count']}" + \
                    f"{colorama.Fore.RESET} validators."

            elif log[2] == "Controller" and log[3] == "skipping validator until it becomes active":
                data = json.loads(log[4])
                tolog = f"Skipping setup for validator {colorama.Fore.RED}{data['pubkey'][:8]}" + \
                    f"{colorama.Fore.RESET} until it becomes active on beacon chain."

            elif log[2] == "Controller" and log[3] == "setup validators done":
                data = json.loads(log[4])
                tolog = f"Complete configuration for {colorama.Fore.MAGENTA}{data['shares']}" + \
                    f"{colorama.Fore.RESET} validators."

                additional_logs.append(f"Successfully configured and started {colorama.Fore.GREEN}" + \
                    f"{data['started']}{colorama.Fore.RESET} validators")

                additional_logs.append(f"Failed to configure {colorama.Fore.RED}{data['failures']}" + \
                    f"{colorama.Fore.RESET} validator{'s' if data['failures'] != 1 else ''}")

            elif log[2] == "Controller" and log[3] == "init validators done":
                data = json.loads(log[4])
                tolog = f"Completed initialization for {colorama.Fore.MAGENTA}{data['shares']}" + \
                    f"{colorama.Fore.RESET} validators."

                additional_logs.append(f"Unable to initialize {colorama.Fore.RED}" + \
                    f"{data['missing_metadata']}{colorama.Fore.RESET} validator" + \
                    f"{'s' if data['missing_metadata'] != 1 else ''}" + \
                    " due to missing metadata or non-active status on beacon chain.")

                additional_logs.append(f"Failed to initialize {colorama.Fore.RED}{data['failures']}" + \
                    f"{colorama.Fore.RESET} validator{'s' if data['failures'] != 1 else ''}")

            # Miscellaneous log handling

            elif log[2] == "setting ssv network":
                data = json.loads(log[3])
                tolog = f"Configuring SSV node for running on {colorama.Fore.MAGENTA}" + \
                    f"{data['network']}{colorama.Fore.RESET} with MEV {colorama.Fore.MAGENTA}" + \
                    f"{data['builderProposals(MEV)']}{colorama.Fore.RESET}"

            elif log[2] == "applying migrations":
                data = json.loads(log[3])
                tolog = f"Applying {colorama.Fore.LIGHTBLUE_EX}{data['count']}" + \
                    f"{colorama.Fore.RESET} migrations"

            elif log[2] == "applied migrations successfully":
                tolog = "Applied migrations sucessfully"

            elif log[2] == "successfully setup operator keys":
                data = json.loads(log[3])
                tolog = f"Set up operator key ({colorama.Fore.MAGENTA}{data['pubkey'][16:]}" + \
                    f"{colorama.Fore.RESET})"

            elif log[2] == "consensus client: connecting":
                data = json.loads(log[3])
                tolog = f"Connecting to consensus client at {colorama.Fore.MAGENTA}" + \
                    f"{data['address']}{colorama.Fore.RESET}"

            elif log[2] == "consensus client connected":
                data = json.loads(log[3])
                tolog = f"Connecting to consensus client at {colorama.Fore.MAGENTA}" + \
                    f"{data['version']}{colorama.Fore.RESET}"

            elif log[2] == "waiting until nodes are healthy":
                tolog = "Waiting until all clients are synced and healthy"

            elif log[2] == "ethereum node(s) are healthy":
                tolog = "All clients are synced and healthy"

            elif log[2] == "historical registry sync stats":
                data = json.loads(log[3])
                tolog = "Network statistics: "
                additional_logs.append(f"Operator ID           : {data['my_operator_id']}")
                additional_logs.append(f"Operators on network  : {data['operators']}")
                additional_logs.append(f"Validators on network : {data['validators']}")
                additional_logs.append(f"Liquidated Validators : {data['liquidated_validators']}")
                additional_logs.append(f"Validators managed    : {data['my_validators']}")

            elif log[2] == "All required services are ready. " + \
                    "OPERATOR SUCCESSFULLY CONFIGURED AND NOW RUNNING!":  
                tolog = "Operator configured sucessfully"

                additional_logs.append(f"{colorama.Fore.GREEN}" + \
                    f"╔═╗╔╦╗╔═╗╦═╗╔╦╗╦ ╦╔═╗  ╔═╗╦ ╦╔═╗╔═╗╔═╗╔═╗╔═╗{colorama.Fore.RESET}")
                additional_logs.append(f"{colorama.Fore.GREEN}" + \
                    f"╚═╗ ║ ╠═╣╠╦╝ ║ ║ ║╠═╝  ╚═╗║ ║║  ║  ║╣ ╚═╗╚═╗{colorama.Fore.RESET}")
                additional_logs.append(f"{colorama.Fore.GREEN}" + \
                    f"╚═╝ ╩ ╩ ╩╩╚═ ╩ ╚═╝╩    ╚═╝╚═╝╚═╝╚═╝╚═╝╚═╝╚═╝{colorama.Fore.RESET}")

            elif log[2] == "going to submit batch validator registrations":
                data = json.loads(log[3])
                tolog = f"Planning to submit {colorama.Fore.MAGENTA}{data['count']}" + \
                    f"{colorama.Fore.RESET} validator registrations"

            elif log[2] == "submitted batched validator registrations":
                data = json.loads(log[3])
                tolog = f"Submitted {colorama.Fore.MAGENTA}{data['count']}{colorama.Fore.RESET}" + \
                    " validator registrations"

            elif log[2] == "could not submit proposal preparation batch":
                data = json.loads(log[3])
                tolog = "Failed to submit proposal preparation batch.\n"
                tolog += "Error: " + data['error'].replace('\\"', '"')

            # Metrics

            elif log[2] == "MetricsHandler" and log[3] == "setup collection":
                data = json.loads(log[4])
                tolog = f"Setting up metrics collection on address {colorama.Fore.LIGHTBLUE_EX}" + \
                    f"{data['address']}{colorama.Fore.RESET}"


            # Specific Error Handling

            elif "node is not healthy" in log[2]:
                data = json.loads(log[3])
                node = data["node"]
                error = data["error"].replace('\\"', '"')
                tolog = f"Issue with {node}. {error}"
                if FULLERRORS:
                    verbose = data["errorVerbose"].replace('\\"', '"').replace('\\n', '\n') \
                        .replace('\\r', '\r').replace('\\t', '\t')
                    tolog+= f"\nFull Traceback:\n{verbose}"

            # Generic Error handling and fallback
            else:
                if "ERROR" in stat or "FATAL" in stat:
                    try:
                        data = json.loads(log[3])
                        tolog = f"{log[2]} - {data['error']}"
                        if FULLERRORS and "errorVerbose" in data.keys():
                            verbose = data["errorVerbose"].replace('\\"', '"').replace('\\n', '\n') \
                                .replace('\\r', '\r').replace('\\t', '\t')
                            tolog+= f"\nFull Traceback:\n{verbose}"
                    except IndexError:
                        tolog = f"{log[2]}"
                    except json.decoder.JSONDecodeError:
                        tolog = f"{log[2]} - {log[3]}"
                else:
                    tolog = "        ".join(log[2:])

        except json.decoder.JSONDecodeError:
            tolog = "        ".join(log[2:])
        except IndexError:
            tolog = "        ".join(log[2:])

        # Print log to stdout

        print(f"{time} {stat}: {tolog}")

        # Print and reset additional logs

        for i in additional_logs:
            print(f"{time} {stat}: {i}")

        additional_logs = []

if __name__ == "__main__":
    main()
