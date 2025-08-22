class singnode :
    def __init__(self,val=None,next=None):
        self.val = val
        self.next=next

head1 = singnode(1)
a=singnode(2)
b=singnode(3)
c=singnode(4)
d=singnode(5)

head1.next = a
a.next = b
b.next = c
c.next = d

head2 = singnode(6)
A=singnode(7)
head2.next = A

def traverse (head) :
    cur = head 
    elem = []
    while cur :
        elem.append(cur.val)
        cur = cur.next

    return elem , len(elem)

def search (head,t) :
    
    cur = head 
    while cur :
        if t == cur.val :
            return True
        cur = cur.next 
    
    return False

def merge (head1,head2)  :
    cur = head1 
    
    if not cur :
        return head2
    
    while cur.next :
        cur = cur.next

    else :
        cur.next = head2
    return head1

def deletion(head,target) :
    cur = head
    dum = singnode()
    dum.next = head
    rev = dum
    while cur :
        if cur.val == target  :
            prev.next = cur.next
            break
        prev=cur
        cur = cur.next
    return dum.next

def insert(head,pos,elem):

    cur = head
    k=0
    while cur :
        if k == pos :
            t = cur
            cur.next= singnode(elem)
            cur.next.next=t.next
        cur=cur.next
        k +=1

    return head

print(traverse(insert(head1,3,3)))

    

