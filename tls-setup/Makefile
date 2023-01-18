.PHONY: cfssl ca req clean

CFSSL=cfssl
JSON=cfssljson
MV=mv

all:  ca req peerca peerreq

cfssl:
	HTTPS_PROXY=127.0.0.1:12639 go get -u -tags nopkcs11 github.com/cloudflare/cfssl/cmd/cfssl
	HTTPS_PROXY=127.0.0.1:12639 go get -u github.com/cloudflare/cfssl/cmd/cfssljson
	HTTPS_PROXY=127.0.0.1:12639 go get -u github.com/mattn/goreman

ca:
	mkdir -p certs
	$(CFSSL) gencert -initca config/ca-csr.json | $(JSON) -bare certs/ca

peerca:
	mkdir -p peer-certs
	$(CFSSL) gencert -initca config/ca-csr.json | $(JSON) -bare peer-certs/ca


req:
	$(CFSSL) gencert \
	  -ca certs/ca.pem \
	  -ca-key certs/ca-key.pem \
	  -config config/ca-config.json \
	  config/req-csr.json | $(JSON) -bare certs/${infra0}
	$(CFSSL) gencert \
	  -ca certs/ca.pem \
	  -ca-key certs/ca-key.pem \
	  -config config/ca-config.json \
	  config/req-csr.json | $(JSON) -bare certs/${infra1}
	$(CFSSL) gencert \
	  -ca certs/ca.pem \
	  -ca-key certs/ca-key.pem \
	  -config config/ca-config.json \
	  config/req-csr.json | $(JSON) -bare certs/${infra2}


peerreq:
	$(CFSSL) gencert \
	  -ca peer-certs/ca.pem \
	  -ca-key peer-certs/ca-key.pem \
	  -config config/ca-config.json \
	  config/req-csr.json | $(JSON) -bare peer-certs/${infra0}
	$(CFSSL) gencert \
	  -ca peer-certs/ca.pem \
	  -ca-key peer-certs/ca-key.pem \
	  -config config/ca-config.json \
	  config/req-csr.json | $(JSON) -bare peer-certs/${infra1}
	$(CFSSL) gencert \
	  -ca peer-certs/ca.pem \
	  -ca-key peer-certs/ca-key.pem \
	  -config config/ca-config.json \
	  config/req-csr.json | $(JSON) -bare peer-certs/${infra2}


clean:
	rm -rf certs peer-certs

