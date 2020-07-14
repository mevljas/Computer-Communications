# LDN9: SSL / TLS
In this task, you will do a security upgrade of the LDN6 talk server and client.

We decided to provide a higher level of security with the help of the TLS protocol and the use of self-signed digital certificates (of course, everything also works with "real" certificates):

- the server must present itself to the client with a digital certificate;
    - The Common Name field of the server certificate should contain the value localhost
- clients must also present themselves to a digitally certified server
    - Generate digital certificates for at least 3 clients - use different values for Common Name.
    - The Common Name value should be used on the server to identify the client.
The user name should no longer be sent from the client to the server as part of the message. The server should identify the client based on the values in the Common Name field.

The server should allow connection only according to the following algorithms in the TLS protocol (combinations of these three components that determine the so-called cipher suite):

- RSA (alone, we do not want to use it in combination with DHE)
- AES with 128 bit key, CBC blockchain
- SHA256 for HMAC calculation
There is only one such candidate - see documentation:

- Java;
- OpenSSL (alternative source).
For Python3, use the method in the SSL context ctx.set_ciphers ().

In Java, set the appropriate string from the cipher suite documentation on SSLSocket and SSLServerSocket using the setEnabledCipherSuites (String []) method before using SSLSocket or SSLServerSocket for the first time; or more precisely: before the handling phase (SSL Handshake) is performed, which is implicitly performed before the first sent character or explicitly with the startHandshake() method, which is therefore recommended to call before reading the name from the digital certificate.
