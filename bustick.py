class Bus:
    seats=[['w1','a1','a2','w2'],['w3','a3','a4','w4']]
    k = 0
    def __init__(self):
        print("Your application no. :",Bus.k)
        self.pname=input("Enter your name :")
        self.passid="pass"+ str(Bus.k)
        self.pnum = input("Enter your mobile number :")
        print()

    def display(self) :
        print("YOUR INFORMATION :")
        print("Name :",self.pname)
        print("Mobile number :",self.pnum)
        print("Passenger  id :",self.passid)
        print("Your application no. :",Bus.k)
        print()

    def allotseats (self):
        ind = 0
        print("Seats available :", *Bus.seats,sep = "\n")
        t = input("Enter the seats you wish for :")
        for i in range (2):
            if t in Bus.seats[i] :
                ind = i

        Bus.seats[ind][Bus.seats[ind].index(t)] = self.passid
        print("Seats :", *Bus.seats,sep ='\n')
        print()

lst=[]

ch,i =1,0
a = 0
print()

while ch != 0 :

    if ch == 1 :
        i += 1
        Bus.k += 1
        globals()[f'p{i}'] = Bus()
                    
    elif ch == 2 :
        a = int(input('Enter your application no. :' ))
        globals()[f'p{a}'].display()

    elif ch == 3 :
        a = int(input('Enter your application no. :' ))
        globals()[f'p{a}'].allotseats()

    else :
        print("Enter your choice correctly .")

    print("""Select :
    0 -> If you want to leave
    1 -> If you're new 
    2 -> If you want to see your details 
    3 -> If you want to book a seat """ )
    ch =int(input('Enter your choice :'))
    print()

            

        
        

    