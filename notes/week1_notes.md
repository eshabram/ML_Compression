
Created on Sun Aug 13 21:54:33 2023

@author: eshabram

---
### Description :
    
First bit indicates an index value. If the index bit is set to 1, then the next
two bits are read and interpreted, where 00 idicates only one byte to be read, 
01 indicates two, 10 indicates three, and 11 incidates a space. If the first bit
is a 0, then the next 7 bits is encoded as the ascii character representation. 
In this way, the message can be, at largest, 100% the size of the original 
message. This is currently how capitol letters are dealt with, but may change 
in the future (perhaps to a capitols map).


#### NOTE: 
I could add a bit after 1 11 for a space to always be read and have it 
represent either a space or a newline. Then the question would be, how many 
spaces per line? If it were 8 spaces per newline character on average, then the
newline char might benefit from the added functionality, but otherwise it would
make the message bigger. We may be better off going with adding the "\n" to the 
dictionary.   

#### IDEA: 
Since the advanced encoding deals more with text of all kinds, including 
newlines and things such as python code, then it would be a good idea to integrate
Huffman encoding for the ascii character after a certain point. I say after a 
certain point because small messages like "How are you?" have a negative benefit 
from Huffman encoding due to lack of duplicate characters and the inclusion of
the translation key. 

1300 is the length of the worst case scenario for when huffman begins to have
a positive impact. 

#### DEALING WITH PADDING BITS:
Currently experimenting witgh a 3 bit code that will be located at the beginning 
of the message that signifies how many padding bits need to be trimmmed from the 
messages end. A three bit code works nicely because it can signify from 0 bits 
to be removed, up to 7 bits, which is the maximum padding.

The problem is that the huffman codes tend to 
use either 0s or 1s in patterns like 00, 0, 111, which does not work with my coding
scheme. The issue arises from my way of handling huffman codes, which is to signal
with a '0' that huffman codes need to be read in, but not including a length or 
number of codes. many of the codes should be grouped together and are read in 
via checking from the current bit to the length of the longest code in succession.
I am reserving the '1' from the huffman codes so that none of them will start with
that bit, making it possible to mark the end in a way. The thought with this is 
that if a 1 appears, the next two bits will be the  two bit codes and index for a 
word inside the dataframe. It should never be another group of huffman codes, 
because of the fact that we are grouping them, meaning that these codes will always
be grouped between either the beginning, words in the database, or the end. But,
and here is the current issue, when huffman coded are located at the end, the 
padding bits are 0s and the codes are read in as if they are huffman codes. We 
cannot pad with 1s because that will tell the decoder that there is another word
to read from the database, and I don't want to waste the 111 code Putting a
three bit code at the beginning would keep the 111 code in play.

---

1 00 means 1 bytes to be read
1 01 means 2 bytes to be read
1 10 means 3 bytes to be read
1 11 means a space currently

0 currently means the start of an ascii character