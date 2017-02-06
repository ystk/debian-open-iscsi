#!/usr/bin/python3

import ipaddress, netifaces, socket, subprocess
from functools import reduce

# These are the private IP ranges that are available.
allowed_ranges = list(map(lambda x: ipaddress.IPv4Network(x), [
  '10.0.0.0/8',
  '172.16.0.0/12',
  '192.168.0.0/16'
]))

# Exclude IP addresses we have already assigned to ourselves
def network_links():
  for interface in netifaces.interfaces():
    for link in netifaces.ifaddresses(interface).get(netifaces.AF_INET, ()):
      yield link
own_ranges = [ipaddress.IPv4Network('%s/%s' % (link['addr'], link['netmask']), strict=False) for link in network_links()]

# Exclude any /24 range containing the nameserver
try:
  with open('/etc/resolv.conf', 'r') as f:
    for line in f:
      line = line.split()
      if len(line) != 2:
        continue
      if line[0] == 'nameserver':
        try:
          range = ipaddress.IPv4Network('%s/24' % line[1], strict=False)
          own_ranges.append(range)
        except ipaddress.AddressValueError:
          pass
except IOError:
  pass

# Exclude any /24 range containing the APT proxy
try:
  for line in subprocess.check_output(['apt-config', 'dump', '--format=%v%n', 'Acquire::http::Proxy']).split(b'\n'):
    try:
      line = line.decode()
      # ignore IPv6
      if len(line) == 0 or line[0] == '[':
        continue
      line = line.split(':')
      if len(line) > 2:
        continue
      port = None
      if len(line) > 1:
        port = line[1]
      for family, type, proto, canonname, addrport in socket.getaddrinfo(line[0], port, family=socket.AddressFamily.AF_INET, type=socket.SocketType.SOCK_STREAM):
        try:
          range = ipaddress.IPv4Network('%s/24' % addrport[0], strict=False)
          own_ranges.append(range)
        except ipaddress.AddressValueError:
          pass
    except (UnicodeDecodeError, socket.gaierror):
      continue
except subprocess.CalledProcessError:
  pass

# First let's try our first choice of a range
chosen_range = ipaddress.IPv4Network('10.0.4.0/24')
collides = False
for own_range in own_ranges:
  if chosen_range.overlaps(own_range):
    collides = True
    break

# If our first go-to IP range collides: subtract that from all
# private IP ranges and get the first available /24 subnet from
# there.
if collides:
  chosen_range = None

  for own_range in own_ranges:
    new_allowed_ranges = []
    for allowed_range in allowed_ranges:
      if not allowed_range.overlaps(own_range):
        new_allowed_ranges.append(allowed_range)
      else:
        new_allowed_ranges += allowed_range.address_exclude(own_range)
    allowed_ranges = new_allowed_ranges

  for allowed_range in allowed_ranges:
    try:
      chosen_range = next(allowed_range.subnets(new_prefix=24))
      break
    except ValueError:
      pass

base = chosen_range.network_address
print(str(base + 1))

