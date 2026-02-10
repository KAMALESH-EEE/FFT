import struct
import numpy as np



class   SOFTWARE:
    IP   = '10.5.15.25'
    DATA = b''
    

    def getdata ():
        ip = '10.5.15.25' #input('Enter Destination IP: ')
        data = 'This a message for testing the QPSK Modulation' #input('Enter data:')
        SOFTWARE.packetize(data,ip)

    def ip_2_bytes(ip):
        val = b''
        for i in ip.split('.'):
            val += struct.pack('B',int(i)&0xff)
        return val
    
    def bytes_2_ip(val):
        ip = ''
        for i in struct.unpack('4B',val):
            ip += str(i)+'.'
        return ip[:-1]


    def packetize (data:str,des_ip:str):
        Header = len(data)#+len(des_ip)+len(SOFTWARE.IP)
        Header = struct.pack('H',Header & 0xffff)
        SOFTWARE.DATA = Header+data[:200].encode()+SOFTWARE.ip_2_bytes(des_ip)+SOFTWARE.ip_2_bytes(SOFTWARE.IP)
        if len(SOFTWARE.DATA) <= FPGA.Bytes_per_Block:

            for i in range(FPGA.Bytes_per_Block-len(SOFTWARE.DATA)):
                SOFTWARE.DATA+= b'\x00'

        elif len(SOFTWARE.DATA) <= FPGA.Bytes_per_Slot:

            for i in range(FPGA.Bytes_per_Slot-len(SOFTWARE.DATA)):
                SOFTWARE.DATA+= b'\x00'

        else:
            SOFTWARE.DATA = SOFTWARE.DATA[0:FPGA.Bytes_per_Slot+1]
            print('Excess data size')


        FPGA.TX_FIFO.append(SOFTWARE.DATA)
        return SOFTWARE.DATA

    def depacketize () -> str:
        data = FPGA.RX_FIFO.pop(0)
        Header = struct.unpack('H',data[:2])[0]
        return  data[2:Header+2].decode()

        


class FPGA:

    Bytes_per_Block = 108
    Blocks_per_Slot = 2
    Bytes_per_Slot = Bytes_per_Block * 2


    TX_FIFO = []
    RX_FIFO = []

    TX_buff = []
    RX_buff = []

    def rrc_filter(alpha, span, sps):
        N = span * sps
        t = np.linspace(-span/2, span/2, N, endpoint=False)
        t = np.where(t == 0, 1e-8, t)  # avoid divide-by-zero
        numerator = np.sin(np.pi * t * (1 - alpha)) + 4 * alpha * t * np.cos(np.pi * t * (1 + alpha))
        denominator = np.pi * t * (1 - (4 * alpha * t) ** 2)
        h = numerator / denominator
        h /= np.sqrt(np.sum(h**2))  # Normalize energy
        return h



    def bitstream_2_byte(bits):
        t = 0
        by = 0
        a = b''
        for i in bits:
            by = (by >> 1)| (i<<7)
            t+=1
            if t == 8:
                t = 0
                a+= struct.pack('B', by)
                by = 0
        #print('\n',a)
        return a


    def byte_2_bitstream(Byte):
        a = Byte[0:FPGA.Bytes_per_Block+1]
        
        A = []

        for i in struct.unpack(f'{len(a)}B',a):
            for t in range(8):
                A.append((i>>t)&1)

        #print(A)
        return A
    
    def Scrambler():
        pass

    

class TRM:
    TX_GAIN = 40
    RX_GAIN = 40
    NF      = 3

class ENV:

    DISTANCE    =   10E3


class SYSTEM:

    SOFTWARE.getdata()
    #print(SOFTWARE.DATA)

    FPGA.TX_buff = FPGA.byte_2_bitstream(FPGA.TX_FIFO[0])

    #FPGA.TX_buff = 0

    FPGA.RX_buff = FPGA.TX_buff # LOOP BACK

    FPGA.RX_FIFO = [FPGA.bitstream_2_byte(FPGA.RX_buff)]   

    print(SOFTWARE.depacketize())


