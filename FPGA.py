import mmap
import struct
import os

BASE_ADDR = 0xA0000000   # your FPGA AXI address
SIZE = 0x1000            # map 4 KB (minimum)

# open /dev/mem
fd = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)

# map the region
mm = mmap.mmap(fd, SIZE, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=BASE_ADDR )

# read 8 bytes (64-bit)
data64 = struct.unpack('Q', mm[0:8])[0]
print("64-bit data:", hex(data64))

mm.close()
os.close(fd)
