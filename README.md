# h2-framer

This Python script generates raw HTTP/2 frames without relying on external libraries. It manually constructs frames to provide a deeper understanding of the HTTP/2 protocol. This is useful for testing, debugging, or educational purposes.

**Note**: The script is written for **Python 2.x** due to differences in binary string handling in Python 3.x.

## Features

- Manually generates HTTP/2 frames.
- Supports multiple requests with custom methods, paths, and headers.
- Optionally includes the HTTP/2 connection preface and settings frame.
- Supports TLS 1.3 early data (0-RTT).
- Outputs an `openssl s_client` command to send the generated frames.

## Dependencies

- **Python 2.x**
- **OpenSSL** (for `openssl s_client`)

## Usage

### Command-Line Arguments

- `--host`: Host to send requests to (default: `www.google.com`).
- `--url`: URL path to request (default: `/teapot`).
- `--method`: HTTP method to use (default: `GET`).
- `--repeat`: Number of times to repeat the request (default: `1`).
- `--no-preface`: Exclude the HTTP/2 connection preface and settings frame.
- `--early-data`: Generate payloads for TLS 1.3 early data.
- `--early-data-url`: Different URL path for early data.
- `--output`: Base name for the output files (default: `h2_request`).
- `ip`: IP address to connect to (**required**).

### Examples

#### Basic Request

Generate a single HTTP/2 GET request to `www.example.com`:

```bash
python script.py --host www.example.com --url / --output example_request 93.184.216.34
```

#### Multiple Requests
Generate 5 OPTIONS requests to www.example.com/api:

```bash
python script.py --host www.example.com --url /api --method OPTIONS --repeat 5 --output multiple_requests 93.184.216.34
```

#### Exclude Preface

Generate requests without the HTTP/2 preface and settings frame:

```bash
python script.py --no-preface --host www.example.com --url / --output no_preface_request 93.184.216.34
```

#### Early Data

Generate early data for TLS 1.3:

```bash
python script.py --early-data --host www.example.com --url / --output early_data_request 93.184.216.34
```

## Output Files

Depending on the options used, the script generates one or more files:

- `<output>`: Contains the generated HTTP/2 frames.
- `<output>_early_data`: Frames for early data.
- `<output>_more_after_early_data`: Frames to be sent after early data.

## Sending Frames with OpenSSL

The script provides an `openssl s_client` command to send the generated frames.

### Basic Usage

```bash
openssl s_client -connect <ip>:443 \
  -sess_out session.pem \
  -tls1_3 \
  -alpn h2 \
  -keylogfile sslkeylog.log \
  -ign_eof < <output>
```

### Using Early Data

```bash
openssl s_client -connect <ip>:443 \
  -sess_in session.pem \
  -tls1_3 \
  -alpn h2 \
  -keylogfile sslkeylog.log \
  -early_data <output>_early_data \
  -ign_eof < <output>_more_after_early_data
```

- **Parameters**:
  - `-connect`: Specifies the IP and port to connect to.
  - `-sess_out` / `-sess_in`: Saves or uses a session for TLS resumption.
  - `-tls1_3`: Forces the use of TLS 1.3.
  - `-alpn h2`: Negotiates HTTP/2 protocol.
  - `-keylogfile`: Logs encryption keys for debugging with Wireshark.
  - `-early_data`: Specifies the file containing early data to send.
  - `-ign_eof`: Ignores EOF to keep the connection open.
  - `< <output>`: Redirects the generated frames as input.

## Important Notes

- **Header Encoding**: The script uses a simplified method for header encoding and does not implement HPACK compression, which is standard in HTTP/2. This may cause compatibility issues with some servers.
- **Python Version**: Must be run with Python 2.x due to binary string handling.

## Limitations

- **Simplified Protocol Implementation**: Does not fully comply with the HTTP/2 specification, particularly in header encoding.
- **Flow Control**: As of right now, there's no way to send flow control frames such as window updates - a PR addressing that somehow is welcome!