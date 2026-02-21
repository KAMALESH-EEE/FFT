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

    G1 = [1,1,1]
    G2 = [1,0,1]


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
        return np.array(A)
    
    
    def conv_encoder(data):
        shift = [0,0]
        encoded = []

        for bit in data:
            inputs = [bit] + shift
            out1 = np.sum(np.array(inputs)*FPGA.G1) % 2
            out2 = np.sum(np.array(inputs)*FPGA.G2) % 2
            encoded.extend([out1, out2])
            shift = [bit] + shift[:-1]

        # Add tail bits (force to zero state)
        for _ in range(2):
            bit = 0
            inputs = [bit] + shift
            out1 = np.sum(np.array(inputs)*FPGA.G1) % 2
            out2 = np.sum(np.array(inputs)*FPGA.G2) % 2
            encoded.extend([out1, out2])
            shift = [bit] + shift[:-1]

        return np.array(encoded)

    def viterbi_decoder(received, threshold_factor=2.0):

        n_states = 4
        path_metrics = np.full(n_states, np.inf)
        path_metrics[0] = 0
        paths = [[] for _ in range(n_states)]

        next_state = {
            0: {0:0, 1:2},
            1: {0:0, 1:2},
            2: {0:1, 1:3},
            3: {0:1, 1:3}
        }

        output_bits = {
            0: {0:[0,0], 1:[1,1]},
            1: {0:[1,1], 1:[0,0]},
            2: {0:[1,0], 1:[0,1]},
            3: {0:[0,1], 1:[1,0]}
        }

        for i in range(0, len(received), 2):
            r = received[i:i+2]

            new_metrics = np.full(n_states, np.inf)
            new_paths = [[] for _ in range(n_states)]

            for state in range(n_states):
                if path_metrics[state] < np.inf:

                    for bit in [0,1]:
                        ns = next_state[state][bit]
                        expected = output_bits[state][bit]

                        metric = path_metrics[state] + np.sum(np.abs(r - expected))

                        if metric < new_metrics[ns]:
                            new_metrics[ns] = metric
                            new_paths[ns] = paths[state] + [bit]

            path_metrics = new_metrics
            paths = new_paths

        best_state = np.argmin(path_metrics)
        best_metric = path_metrics[best_state]

        decoded = np.array(paths[best_state])

        # Remove tail bits
        decoded = decoded[:-2]

        # Threshold decision
        avg_metric = best_metric / (len(received)/2)

        if avg_metric > threshold_factor:
            return decoded, False
        else:
            return decoded, True




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


