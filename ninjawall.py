import argparse
import subprocess

# Define the iptables rules to apply
default_rules = [
    "iptables -P INPUT DROP",
    "iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT",
    "iptables -A INPUT -p icmp -j ACCEPT",
]

# Define the argparse options
parser = argparse.ArgumentParser(description='Apply iptables rules.')
parser.add_argument('--allow', metavar='PORT', type=int, nargs='+',
                    help='allow incoming traffic on the specified ports')
parser.add_argument('--block', metavar='PORT', type=int, nargs='+',
                    help='block incoming traffic on the specified ports')

# Parse the command-line arguments
args = parser.parse_args()

# Define the rules based on the command-line arguments
iptables_rules = default_rules.copy()

if args.allow:
    for port in args.allow:
        iptables_rules.append(f"iptables -A INPUT -p tcp --dport {port} -j ACCEPT")

if args.block:
    for port in args.block:
        iptables_rules.append(f"iptables -A INPUT -p tcp --dport {port} -j DROP")

# Apply the rules using subprocess
for rule in iptables_rules:
    subprocess.run(rule.split())
