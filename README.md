# SMC Compression:

Small Message Coding compression (SMC) is a compression algorithm designed for 
both short text messages, and large files. Conventional compression algorithms 
typically lack the ability to compress short text due to things like the inclusion
of translation keys and reliance on repetative characters. SMC works by similarly
to Huffman coding, in that the goal is to assign the smallest codes to the most 
common entries, but rather than assigning codes based on character, SMC uses a 
small database of words ranked by commonality. This method is beneficial because 
it removes the need for translation keys to be sent with the messages. 

### compressing files with SMC:

To compress a file with SMC simply run SMC.py located in the main directory as such:

```
python3 SMC.py <file path>
```

This will create a file in the same directory as the file being compressed with 
the same name, but ending in the .smc file extension. That extension will be 
necessary to run the decode, though there is a --force option for convenience.
Run the decompressor as such:

```
python3 SMC.py -d <.smc file path>
``` 

The -d flag specifies --decompression, which makes sure that the file is a .smc 
file unless the --force argument is used. This command will generate a .uncompressed
version of the .smc file with the same name and location.


### Using the client and server with compression:

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

The -v is for verbose mode, which gives more information. 

Advanced mode is also available, which gives a perfect (lossless?) representation of the message, particularly 
when you give it a file like this:

```
python3 client -a -f <file name>
``` 
and 
```
python3 client -a
```

That's it. If you'd like to verify that the data is the size specified, you can run wireshark and capture one 
the TCP packets and find the "payload" or "data". Have fun!
![Alt text](figures/wireshark_payload.png)