# Simultaneously receiving AlgoDebug and compressed data streams

As of FW version 0.11.x it is still possible to receive the compressed (customer) data stream simultaneously with the Algo Debug (AD) data stream. Both data streams are send via PCIC on independent socket connections. Triggering the AD stream does not implement a automatic 'switch off' of the customer compressed PCIC stream.  

Furthermore the AD data stream holds information about both formats again. This results is high bandwidth even for streaming a single 38k head stream.

The statements above may not apply to FW version >= 0.12.x. The AD stream may not hold compressed stream information anymore to save bw. Triggering the AD stream may switch off the compressed AD stream on the same port.  

## Test setup
1. have a compressed stream running: ifmO3r viewer
2. start AD stream saving to file

## Results
1. The compressed pcic stream drops below 2 Hz: typically ~ 0.6 Hz.
2. The AD stream seems to keep going / is not influenced by the second (compressed stream) viewer application. A replay of the saved AD file works well. The data is not corrupted. AD framerates are not tested. 