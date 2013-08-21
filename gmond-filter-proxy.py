#!/usr/bin/env python

import re
import socket
import SocketServer
import argparse
import StringIO

filters = [
  '<METRIC NAME="ps-.*?</METRIC>\s',
  '<METRIC NAME="tcp_.*?</METRIC>\s'
]

class GmondProxy:
  """ Query gmond """

  def __init__(self, gmondip, gmondport):
    self.gmondip = gmondip
    self.gmondport = gmondport

  def readData(self):
    bufsize = 100000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((self.gmondip, self.gmondport))
    data = ""
    incoming = s.recv(bufsize)
    while (incoming != ""):
      data += incoming;
      incoming = s.recv(bufsize)
    s.close()
    return data

  def run(self):
    try:
      return self.readData()
    except:
      print "Error fetching data from gmond on %s, port %d" % (self.gmondip, self.gmondport)


class ReqHandler(SocketServer.StreamRequestHandler):
  """ Handle requests """
  global filters
  
  def setup(self):
    self.proxy = GmondProxy(self.node['ip'], self.node['port'])
    self.wfile = self.request.makefile("wb", 0)
    
  def handle(self):
    ''' Get data from proxy and filter the content '''
    str = self.proxy.run()
    for filter in filters:
      str = re.sub(filter,'',str,flags=re.DOTALL)
    self.wfile.write(str)
    
  def finish(self):
    self.wfile.flush()
    self.wfile.close()


class CliConfiguration:

  def __init__(self):
    argParser = argparse.ArgumentParser(description="Ganglia Proxy")
    argParser.add_argument('gmond', metavar='gmond', help="Specify the gmond source node.")
    argParser.add_argument('--server-port', dest='server_port', default=8666, type=int )
    argParser.add_argument('--default-port', dest='default_port', default=8649, type=int )
    args = argParser.parse_args()
    self.node = self._parse_node(args.gmond, args.default_port)
    self.server_port = args.server_port
    
  def _parse_node(self, gmond, default_port):
    if ":" in gmond:
      ip, port = gmond.split(':')
    else:
      port = default_port
      ip = gmond 
    return {'ip': ip, 'port': int(port) }

  
configuration = CliConfiguration()
ReqHandler.node = configuration.node

s = SocketServer.TCPServer(('', configuration.server_port), ReqHandler)

try:
  s.serve_forever()
finally:
  s.server_close()


