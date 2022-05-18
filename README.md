# Symple Unzipper Challenge

This repo contains a simple web server that accepts ZIP files, extracts them, and returns their contents.
It has a vulnerability that permits exfiltration of local files.

## Running the Server

It is highly recommended to run the server in Docker, since its behavior will be dependent on the specific
decompression tools installed on your system. The provided [Docker Compose script](docker-compose.yml)
expects an environment variable `FLAG` to be set, the contents of which will be written to `flag.txt` in the
same directory as the `server.py` script in the container. This is the flag that the attacker will attempt
to exfiltrate.

```console
$ env FLAG=ThisIsTheFlag docker-compose up --build
```

This will automatically run the server and bind it to port 8080 on the host. You can then connect to the 
server in your web browser, [here](http://localhost:8080/).

### Running the Server Locally

With the knowledge that it may behave slightly differently, the server _can_ be run locally (_e.g._, to make
debugging easier) by first installing the requirements:

```console
$ pip install -r requirements.txt
```

and then either executing it via Uvicorn

```console
$ uvicorn --port 8080 --host 0.0.0.0 server:app
```

or directly via Python

```console
$ python3 server.py
```

## Once the Server is Running

The web server's landing page, [`index.html`](index.html), has more information.

## License and Acknowledgements

This code was created by [Evan Sultanik](https://www.sultanik.com/) and is licensed and distributed under the
[AGPLv3](LICENSE) license.
