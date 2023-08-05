### Basic instructions:

if the dependencies and libraries necessary are installed (you'll likely need nltk and anaconda') then you
should be good to begin.

Open two linux termial and run client.py and server.py on the other like this:

```
python3 client.py -v
```

and from the other shell

```
python3 server.py -v

```

The -v is for verbose mode, which gives more information. There is a --advanced mode that
I am currently working on and is not in a functional state, so don't enable it.

That's it. If you'd like to verify that the data is the size specified, you can run wireshark and capture one 
the TCP packets and find the "payload" or "data". Have fun!
![Alt text](figures/wireshark_payload.png)