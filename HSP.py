# HS_str = input('Enter Standard Size (LxB) mm:').split('x')
# L,B = float(HS_str[0]),float(HS_str[1])
# Main_HS = (L,B)
Mini_HS = []
# Main_HS_area =  L*B
Total_mini_area = 0
N = int(input('Enter the No of mini pices:'))

for i in range (N):
    HS_str = input(f'Enter Pices {i+1} dimention: ').split('x')
    l,b = float(HS_str[0]),float(HS_str[1])
    # if (L<l and B<l) or  (L<b and B<b):
    #     print (f" {l}x{b} size can't fit in {L}x{B}")
    #     continue
        
    Mini_HS.append((l,b))
    Total_mini_area += (l*b)

print("Total no of valid Thermal Pads:", len(Mini_HS))

global POS
POS = []
def REC (a,MAT):
    L,B = a
    if len(MAT) == 0:
        if ((L,B) not in POS) and ((B,L) not in POS):
            POS.append(a)
        return
    temp = MAT[:]
    l,b = temp.pop(0)
    t = B if(B>b) else b
    REC ((L+l , t),temp)
    t = L if(L>l) else l
    REC ((t , B+b),temp)
    t = B if(B>l) else l
    REC ((L+b , t),temp)
    t = L if(L>b) else b
    REC ((t , B+l),temp)

REC((0,0),Mini_HS)

min_size_in =[]

print("Total posibilities:")
for i in POS:
     l,b = i
     print (f"{int(l)}x{int(b)} mm")
     min_size_in.append(l-b if (l>b) else b-l)
l,b = POS[min_size_in.index(min(min_size_in))]
print(f"Best option for is {int(l)}x{int(b)} mm")
