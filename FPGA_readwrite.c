#include <stdio.h>
#include <string.h>
#include <stdlib.h>


char fpga_file []= "C:/Users/KAMALESH/Downloads/FPGA.csv";

/*CSV File Structure*/

struct REGMAP{
	int Addr;
	int Data;
	struct REGMAP * NextReg;
};

struct REGMAP *regmap_Head = NULL,* regmap_Tail = NULL;
int regmap_Len = 0;

void REGMAP__destructor__(){
	regmap_Head = NULL;
	regmap_Tail = NULL;
	regmap_Len = 0;
	
}

struct  REGMAP* REGMAP__constructor__(int add, int data){
	struct REGMAP *rm = (struct REGMAP *) malloc (sizeof(struct REGMAP));
	rm->Addr = add;
	rm->Data = data;
	rm->NextReg = NULL;
	regmap_Len ++;
	if (regmap_Len == 1){
		regmap_Head = rm;
		regmap_Tail = rm;
	}
	
	else{
		regmap_Tail->NextReg = rm;
		regmap_Tail=rm;		
	}
	
	return rm;
			
}



/* Str2Int Function used to convert Integer in string formate to int type (type casting from string to int) */

int Str2Int(char InStr[], int *OutInt){
	
	int i = 0, iA = 0,itemp=0;
	
	while (InStr[i] != '\0'){
		
		if (InStr[i]<58 && InStr[i]>47 ){
			itemp= InStr[i] - 48;
		}
		
		else
		{
			return 0;
		}
		
		iA = (iA*10) + itemp;
			
		i++;
	}
	*OutInt = iA;
	return 1;	
}


/* HexStr2Int Function used to convert Hexadecimal Integer in string formate to int type (type casting from string to int) */

/* ff, Ff, FF are vaild formate*/
/* Ffh, 0xFF are invaild formate*/


int HexStr2Int(char InStr[], int *OutInt){
	
	int i = 0, iA = 0,itemp=0;
	
	while (InStr[i] != '\0'){
		
		if (InStr[i]<58 && InStr[i]>47 ){
			itemp= InStr[i] - 48;
		//	printf("|%d|",InStr[i]);
		}
		
		else if (InStr[i]<103 && InStr[i]>96 ){
			itemp= InStr[i] - 87;
		}
		
		else if (InStr[i]<71 && InStr[i]>64 ){
			itemp= InStr[i] - 55;
		}
		
		else
		{
			return 0;
		}
		
		iA = (iA<<4)|itemp;
			
		i++;
	}
	*OutInt = iA;
	return 1;	
}

int FPGAread(int Add, long int *result) {
		
	struct REGMAP f1;
	int i = 0, j=0, retFlag = 0;
	char addr[5],data[17];
	
	FILE *fp = fopen(fpga_file,"r");
	
	
    char line[200];
    
	if(fp == NULL){
        printf("CSV open error\n");
        return 1;
    }
    
    while(fgets(line,sizeof(line),fp)){
    	
    	i=0;
    	j=0;
    	while(line[i] != ',' && i<5){
    		addr[i] = line[i];
    		i++;
		}
    	addr[i]='\0';
    	i++;
    	while(line[i]){
    		data[j] = line[i];
    		i++;
    		j++;
		}
		data[--j]='\0';		
		if (! HexStr2Int(addr,&i)){printf("Conversion Error !\n");}
		if (! HexStr2Int(data,&j)){printf("Conversion Error %s\n",data);}
				
		if (1) {REGMAP__constructor__(i,j);}
		
		if (i==Add){
			*result = j;
			retFlag = 1;
			fclose(fp);
			REGMAP__destructor__();
		}
		
		
	}
	fclose(fp);
	REGMAP__destructor__();
	return retFlag;
}


int FPGAwrite(int Add, long int Data) {
		
	struct REGMAP f1;
	int i = 0, j=0, retFlag = 0;
	char addr[5],data[17];
	struct REGMAP * rm; 
	
	FILE *fp = fopen(fpga_file,"r");
	
	
    char line[200];
    
	if(fp == NULL){
        printf("CSV open error\n");
        return 1;
    }
    
    while(fgets(line,sizeof(line),fp)){
    	
    	i=0;
    	j=0;
    	while(line[i] != ',' && i<5){
    		addr[i] = line[i];
    		i++;
		}
    	addr[i]='\0';
    	i++;
    	while(line[i]){
    		data[j] = line[i];
    		i++;
    		j++;
		}
		data[--j]='\0';		
		if (! HexStr2Int(addr,&i)){printf("Conversion Error !\n");}
		if (! HexStr2Int(data,&j)){printf("Conversion Error %s\n",data);}
				
		if (1) {rm = REGMAP__constructor__(i,j);}
		
		if (i==Add){
			rm->Data = (int) Data;
			retFlag = 1;
		}
		
		
	}
	fclose(fp);
	
	if (!retFlag) REGMAP__constructor__(Add,(int) Data);
	
	fp = fopen(fpga_file,"w");
	rm = regmap_Head;
	
	while (rm!=NULL){
		fprintf(fp,"%x,%x\n",rm->Addr,rm->Data);
		rm=rm->NextReg;	
	}
	retFlag = 1;
	fclose(fp);
	REGMAP__destructor__();
	return retFlag;
}







int main()
{
	int a = 3,op=0;
	long int d = 0;
	
	while (op != 99)
	{
	printf("\n===========\n  FPGA R/W\n=========== \n");
	printf("1-> Read\n2-> Write\nEnter Your Option: ");
	scanf("%d",&op);
	if (op == 1)
	{
	printf("FPGA Read Address: ");
	scanf("%x",&a);
	(FPGAread(a,&d)) ? printf("Data: %x\n",d) : printf("FPGA Read Fail\n") ;
	}
	else if (op == 2)
	{
	printf("FPGA Write Address: ");
	scanf("%x",&a);
	printf("FPGA Wite Data: ");
	scanf("%x",&d);
	(FPGAwrite(a,d)) ? printf("FPGA Write Done\n",d) : printf("FPGA Write Fail\n") ;
	}
	else printf("Invalid Input\n");	
	}

	return 0 ;
}
