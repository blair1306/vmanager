all: key crt

key:
	openssl genrsa 1024 > server.key && chmod 400 server.key

crt: key
	openssl req -new -x509 -nodes -sha1 -days 365 -key server.key -out server.crt

clean:
	rm -f server.key server.crt
