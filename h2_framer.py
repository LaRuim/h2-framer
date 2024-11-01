#!/usr/bin/env python2
from __future__ import print_function
import struct
import argparse

HTTP2_PREFACE = "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"

def frame(ty, flags, streamid, payload):
    return struct.pack(">L", len(payload))[1:4] + struct.pack(">BBL", ty, flags, streamid) + payload

last_stream_id = -1

def encode_header(key, value):
    key = key.lower()
    return struct.pack("<BB", 0, len(key)) + key.encode() + struct.pack("<B", len(value)) + value.encode()

def headers(headers):
    global last_stream_id
    last_stream_id += 2
    header_block = b''.join(encode_header(x, y) for x, y in headers.items())
    return frame(0x1, 0x5, last_stream_id, header_block)

def request(host, path, method="GET", scheme="https", extra_headers=None):
    h = {":authority": host, ":path": path, ":method": method, ":scheme": scheme}
    if extra_headers is not None:
        h.update(extra_headers)
    return headers(h)

def generate_multiple_requests(requests, include_preface=True):
    
    output = b''
    if include_preface:
        output = HTTP2_PREFACE.encode() + frame(0x4, 0, 0, b'')
    
    for req in requests:
        host, path, method, extra_headers = req
        output += request(host, path, method=method, extra_headers=extra_headers)
    
    return output

def write_to_file(data, filename):
    with open(filename, 'wb') as f:
        f.write(data)

parser = argparse.ArgumentParser(description='Generate HTTP/2 frames without using random h2 libraries; python2 because printing binary strings in python3 are weird')
parser.add_argument('--host', default="www.google.com", help='Host to send requests to')
parser.add_argument('--url', default="/teapot", help='URL to hit')
parser.add_argument('--method', default="GET", help='HTTP request method')
parser.add_argument('--repeat', type=int, default=1, help='Number of times to repeat the request')
parser.add_argument('--no-preface', action='store_true', help='Exclude HTTP/2 preface and settings frame')
parser.add_argument('--early-data', action='store_true', help='Generate both cearly data and normal output')
parser.add_argument('--early-data-url', help='Specify a different path for cearly data')
parser.add_argument('--output', default='h2_request', help='Output file name (without extension)')
parser.add_argument('ip', help='IP address to connect to')

args = parser.parse_args()

if args.early_data:
    early_data_requests = [(args.host, args.early_data_url if args.early_data_url else args.url, args.method, {}) for _ in range(args.repeat)]
    normal_requests = [(args.host, args.url, args.method, {}) for _ in range(args.repeat)]

    early_data = generate_multiple_requests(early_data_requests, include_preface=True)
    normal_data = generate_multiple_requests(normal_requests, include_preface=False)
    
    write_to_file(early_data, "{}_early_data".format(args.output))
    write_to_file(normal_data, "{}_more_after_early_data".format(args.output))

    print("openssl s_client -connect {}:443 -sess_in session.pem -tls1_3 -alpn h2 -keylogfile sslkeylog.log -early_data {}_early_data -ign_eof < {}_more_after_early_data".format(args.ip, args.output, args.output))
else:
    requests = [(args.host, args.url, args.method, {}) for _ in range(args.repeat)]
    http2_payload = generate_multiple_requests(requests, not args.no_preface)
    write_to_file(http2_payload, "{}".format(args.output))
    print("openssl s_client -connect {}:443 -sess_out session.pem -tls1_3 -alpn h2 -keylogfile sslkeylog.log -ign_eof < {}".format(args.ip, args.output))
