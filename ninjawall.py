import argparse
import subprocess

# Define the iptables rules to apply
default_rules = [
    "iptables -P INPUT DROP",
    "iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT",
    "iptables -A INPUT -p icmp -j ACCEPT",
]

# Define a custom argument type to parse "<port>/<protocol>" strings
def port_protocol(string):
    try:
        port, protocol = string.split('/')
        return int(port), protocol
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid port/protocol string: {}".format(string))

# Define the argparse options
parser = argparse.ArgumentParser(description='Apply iptables rules.')
parser.add_argument('--open', metavar='PORT/PROTOCOL', type=port_protocol, nargs='+',
                    help='allow incoming traffic on the specified port and protocol (e.g. 5000/tcp)')
parser.add_argument('--limit', metavar='RATE', type=str,
                    help='set rate limit for incoming traffic (e.g. 10/minute)')
parser.add_argument('--persistent', action='store_true',
                    help='make the iptables rules persistent across reboots')

# Parse the command-line arguments
args = parser.parse_args()

# Define the rules based on the command-line arguments
iptables_rules = default_rules.copy()

if args.open:
    for port, protocol in args.open:
        if protocol == 'tcp':
            iptables_rules.append(f"iptables -A INPUT -p tcp --dport {port} -j ACCEPT")
        elif protocol == 'udp':
            iptables_rules.append(f"iptables -A INPUT -p udp --dport {port} -j ACCEPT")
        else:
            print(f"Unsupported protocol: {protocol}")

# Add rate limiting rule
if args.limit:
    iptables_rules.append(f"iptables -A INPUT -m limit --limit {args.limit} -j ACCEPT")

# Apply the rules using subprocess
for rule in iptables_rules:
    subprocess.run(rule.split())

# Save the rules to a persistent configuration file
if args.persistent:
    distro = subprocess.check_output("cat /etc/os-release | grep '^ID=' | awk -F= '{ print $2 }'", shell=True).decode().strip()
    if distro == "debian" or distro == "ubuntu":
        subprocess.run(["iptables-save", ">/etc/iptables/rules.v4"], shell=True)
        subprocess.run(["ip6tables-save", ">/etc/iptables/rules.v6"], shell=True)
        subprocess.run(["systemctl", "enable", "netfilter-persistent"], check=True)
        subprocess.run(["systemctl", "restart", "netfilter-persistent"], check=True)
        print("iptables rules saved to /etc/iptables/rules.v4 and /etc/iptables/rules.v6 and enabled at boot.")
    elif distro == "centos" or distro == "rhel":
        subprocess.run(["service", "iptables", "save"], check=True)
        subprocess.run(["systemctl", "enable", "iptables"], check=True)
        subprocess.run(["systemctl", "restart", "iptables"], check=True)
        print("iptables rules saved and enabled at boot.")
    else:
        print(f"Unsupported distro: {distro}")
