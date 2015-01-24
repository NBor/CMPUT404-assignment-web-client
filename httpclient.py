#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle, Neil Borle
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
from urlparse import urlparse


def help():
    print "httpclient.py [GET/POST] [URL]\n"


class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    """An HTTP client similar to curl."""

    def __init__(self):
        self.sock = None
        return super(HTTPClient, self).__init__()

    def connect(self, host, port):
        # use sockets!
        port = int(port) if port else 80
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_ip = socket.gethostbyname(host)
            self.sock.connect((remote_ip, port))
        except Exception as excp:
            print ("Exception: %s\n"
                   "Unable to connect to %s:%s" % (excp, host, port))
            sys.exit(1)

    def get_code(self, data):
        match = re.search(r'(?<=HTTP/1.[01]\s)\d{3}', data)
        if match:
            return int(match.group(0))
        return 500

    def get_headers(self,data):
        return data.split('\r\n\r\n', 1)[0]

    def get_body(self, data):
        return data.split('\r\n\r\n', 1)[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        """Implements GET"""
        get_request = ("GET %s HTTP/1.1\r\n"
                       "Host: %s\r\n"
                       "Connection: close\r\n"
                       "Content-Length: %s\r\n\r\n%s")
        return self.issue_command(url, get_request, args)

    def POST(self, url, args=None):
        """Implements POST"""
        post_request = ("POST %s HTTP/1.1\r\n"
                        "Host: %s\r\n"
                        "Connection: close\r\n"
                        "Content-Length: %s\r\n"
                        "Content-type: application/x-www-form-urlencoded"
                        "\r\n\r\n%s")
        return self.issue_command(url, post_request, args)

    def issue_command(self, url, request, args=None):
        parsed_url = urlparse(url)
        self.connect(parsed_url.hostname, parsed_url.port)
        path, host = parsed_url.path, parsed_url.netloc

        encoded_args = urllib.urlencode(args) if args else ''
        self.sock.send(request % (path, host, len(encoded_args),
                                  encoded_args))
        data = self.recvall(self.sock)
        code = self.get_code(data)
        body = self.get_body(data)

        self.sock.close()
        print data
        return HTTPRequest(code, body)

    def command(self, url, command='GET', args=None):
        if (command == 'POST'):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

if __name__ == "__main__":
    client = HTTPClient()
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        client.command(sys.argv[2], sys.argv[1])
    else:
        client.command(sys.argv[1])
