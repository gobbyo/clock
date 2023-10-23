#!/usr/bin/env python
# coding: utf8

import socket

MAX_PACKET = 32768

def recv_all(sock):
    r'''Receive everything from `sock`, until timeout occurs, meaning sender
    is exhausted, return result as string.'''
    
    # dirty hack to simplify this stuff - you should really use zero timeout,
    # deal with async socket and implement finite automata to handle incoming data

    prev_timeout = sock.gettimeout()
    try:
        sock.settimeout(0.01)
    
        rdata = []
        while True:
            try:
                rdata.append(sock.recv(MAX_PACKET))
            except socket.timeout:
                return ''.join(rdata)
        
        # unreachable
    finally:
        sock.settimeout(prev_timeout)
    
def normalize_line_endings(s):
    r'''Convert string containing various line endings like \n, \r or \r\n,
    to uniform \n.'''
    
    return ''.join((line + '\n') for line in s.splitlines())

def run():
    r'''Main loop'''
    
    # Create TCP socket listening on 10000 port for all connections, 
    # with connection queue of length 1
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
    server_sock.bind(('0.0.0.0', 13000))
    server_sock.listen(1)

    while True:
        # accept connection
        client_sock, client_addr = server_sock.accept()
        
        # headers and body are divided with \n\n (or \r\n\r\n - that's why we
        # normalize endings). In real application usage, you should handle 
        # all variations of line endings not to screw request body
        request = normalize_line_endings(recv_all(client_sock)) # hack again
        request_head, request_body = request.split('\n\n', 1)
        
        # first line is request headline, and others are headers
        request_head = request_head.splitlines()
        request_headline = request_head[0]
        # headers have their name up to first ': '. In real world uses, they
        # could duplicate, and dict drops duplicates by default, so
        # be aware of this.
        request_headers = dict(x.split(': ', 1) for x in request_head[1:])
        
        # headline has form of "POST /can/i/haz/requests HTTP/1.0"
        request_method, request_uri, request_proto = request_headline.split(' ', 3)
        
        response_body = [
            '<html><body><h1>Hello, world!</h1>',
            '<p>This page is in location %(request_uri)r, was requested ' % locals(),
            'using %(request_method)r, and with %(request_proto)r.</p>' % locals(),
            '<p>Request body is %(request_body)r</p>' % locals(),
            '<p>Actual set of headers received:</p>',
            '<ul>',
        ]
        
        for request_header_name, request_header_value in request_headers.iteritems():
            response_body.append('<li><b>%r</b> == %r</li>' % (request_header_name, \
                                                    request_header_value))
    
        response_body.append('</ul></body></html>')
    
        response_body_raw = ''.join(response_body)
        
        # Clearly state that connection will be closed after this response,
        # and specify length of response body
        response_headers = {
            'Content-Type': 'text/html; encoding=utf8',
            'Content-Length': len(response_body_raw),
            'Connection': 'close',
        }
    
        response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                                response_headers.iteritems())
                
        # Reply as HTTP/1.1 server, saying "HTTP OK" (code 200).
        response_proto = 'HTTP/1.1'
        response_status = '200'
        response_status_text = 'OK' # this can be random
        
        # sending all this stuff
        client_sock.send('%s %s %s' % (response_proto, response_status, \
                                                        response_status_text))
        client_sock.send(response_headers_raw)
        client_sock.send('\n') # to separate headers from body
        client_sock.send(response_body_raw)
        
        # and closing connection, as we stated before
        client_sock.close()

if __name__ == '__main__':
    run()