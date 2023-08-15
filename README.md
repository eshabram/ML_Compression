# SMC Compression:

Small Message Coding compression (SMC) is a compression algorithm designed 
specifically for messaging with real time compression. Conventional compression algorithms 
typically lack the ability to compress short text due to the inclusion
of translation keys, reliance on repetative characters, and various other reasons. 
SMC works similarly to Huffman coding, in that the goal is to assign the 
smallest codes to the most common entries, but rather than assigning codes based 
on character, SMC uses a small database of words ranked by commonality. This 
method is beneficial because it removes the need for translation keys to be sent
with the messages. 

---
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

---
### Using the client and server with compression:

Open two linux termial and run client.py on one, and server.py on the other like this:

```
python3 client.py -v
```

and from the other shell

```
python3 server.py -v
```

This will will send a message using the lossless SMC compression designed for 
use with small text messaging in mind. 

```
python3 client.py -f <file name>
``` 
If your server.py is already running in the default mode, then you do not need to 
rerun the script. It will read it in just fine. 

---
### Lossy mode:

Running both client and server script with the -l flag will initiate the 
--lossy mode, which is designed specifically with radio communication in mind. 
This separate algorithm gives the smallest compression while still retaining
the messages meaning (lossy). This algorithm currently averages around 3:1 
compression. This mode can be useful for low baud rate situation, and/or 
emergency communication. 

---

That's it. If you'd like to verify that the data is the size specified, you can 
run wireshark and capture one of the TCP packets and find the "payload" or "data". 
Have fun!
![Alt text](figures/wireshark_payload.png)

