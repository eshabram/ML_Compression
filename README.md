### Basic instructions:

if the dependencies and libraries necessary are installed (you'll likely need nltk and anaconda') then you
should be good to begin.

Open two linux termial and run client.py and server.py on the other like this:

```
python3 client.py -sv
```

and from the other shell

```
python3 server.py -sv

```

The -sv arguments stand for --simple and --verbose. You can leave out verbose, but you MUST HAVE SIMPLE MODE 
ENABLED ON BOTH!!

That's it. If you'd like to verify that the data is the size specified, you can run wireshark and capture one 
the TCP packets and find the "payload" or "data". Have fun.
![Alt text](figures/wireshark_payload.png)