
//add a new line here.

//testcase2

#include "aes128gcm.h"
#include "aes128e.h"
#include "stdio.h"



//extract the most right n bits in a bit String
void RightMostBits(int n, unsigned char original [16], unsigned char AfterLeftMove [16]){
    int DivisionNumber, ModeNumber, i;
    unsigned char sec_temp;
    DivisionNumber=n/8;
    ModeNumber=n%8;

    if (ModeNumber!=0){
     sec_temp=original[15-DivisionNumber] & (1<<ModeNumber-1);
     AfterLeftMove[0]=sec_temp;
 
         for(i=0;i<DivisionNumber;i++)
         AfterLeftMove[i+1]=original[16-DivisionNumber+i];
                     }
   else{

        for(i=0;i<DivisionNumber;i++){
        AfterLeftMove[i]=original[16-DivisionNumber+i];
       }


}


}

/*extract the left most bits in a char string*/
void LeftMostBits(int n, unsigned char original [16], unsigned char AfterRightMove [16]){
     int DivisionNumber, ModeNumber, i;
     unsigned char temp;
     DivisionNumber=n/8;
     ModeNumber= n%8;

     if(ModeNumber!= 0){

        for(i=0;i<DivisionNumber;i++)
           AfterRightMove[i]=original[i];

        temp=original[DivisionNumber] & (~(1<<(8-ModeNumber)-1));
        AfterRightMove[DivisionNumber]=temp;
                       }

     else{

        for(i=0;i<DivisionNumber;i++) 
        AfterRightMove[i]=original[i];
         }

}

/*move the elements in a string to its right*/
void RightMove(unsigned char source[16], unsigned char moved[16]){
     int i;
     for(i=0;i<4;i++){
      moved[i+12]=source[i];
                     }
}

/*implement Incremention function*/
void Increment(int s, unsigned char X [16], unsigned char Inc_string [16]){
     unsigned char RightBits[16];
     unsigned char Inc_left[16];
     unsigned char LSB_result[16];
     unsigned char Inc_right[16];
     int i;

     LeftMostBits(16*8-s, X, Inc_left);

/*for(int j=0;j<16;j++)
printf("%x ",Inc_left[j]);*/

     RightMostBits(s, X, RightBits);
     RightMove(RightBits, LSB_result);

// excute the process [int(LSB s (X))+1 mod 2 s ] s
     LSB_result[15]=LSB_result[15]+1;
     RightMostBits(s,LSB_result,Inc_right);

     for(i=0;i<12;i++){
        Inc_string[i]=Inc_left[i];
        }
     for(i=12;i<16;i++){
        Inc_string[i]=Inc_right[i-12];
        }
}


/*implement GCTR function*/
void GCTR(unsigned char *ICB, const unsigned char *plaintext, unsigned char *ciphertext, const unsigned char *k, const unsigned long len_p){

     int n=len_p/128;
     int i,j;
     unsigned char x[n][16];
     unsigned char CB[n][16];
     unsigned char y[n][16];
     unsigned char cipher[n][16];

     for(j=0; j<len_p/8; j++){
        x[j/16][j%16] = plaintext[j];
    }

     for(i=0;i<16;i++){
        CB[0][i]=ICB[i];
        }


     for(i=1;i<n;i++){
       Increment(32,CB[i-1],CB[i]);
       }

     for(i=0;i<n;i++){
       aes128e(cipher[i],CB[i],k);   
     for(j=0;j<16;j++) {

      y[i][j]=x[i][j]^cipher[i][j];
                       }
        }

     for(i=0;i<n;i++)
     for(j=0;j<16;j++)
  ciphertext[i*16+j]=y[i][j];

}


/*get a bit located in specific index in a byte */
int GetBits(unsigned char *X, int index){
    unsigned char X_[16];
    for(int i=0; i<16; i++){
        X_[i] = X[i];
    }
    
    return ( X_[index/8]>>(7-(index%8)) ) & 1;
}


/*multiplication of two blocks*/
void Multip_blocks(unsigned char x[16], unsigned char y[16], unsigned char *product){

    unsigned char z[16];
    unsigned char v[16];
    unsigned char R[16];
    int i,j;
    memset(z,0,16*sizeof(unsigned char));
    memset(R,0,16*sizeof(unsigned char));
    R[0]=0xe1;

    for(i=0;i<16;i++)
      v[i]=y[i];

    for(i=0;i<128;i++){
	  for(j=0;j<16;j++){
		if(GetBits(x,i)==1){
			z[j]=z[j]^v[j];		
		}
	  }

    if((v[15]&1)==0){

  	 for(j=15;j>=0;j--){
    	 	v[j] = v[j]>>1;
      		if(j!=0 && (v[j-1] & 1)==1)
          		v[j]=v[j] | 0x80;
	 }
   }

    else{
  	for(j=15;j>=0;j--){
		v[j] = v[j]>>1;
		if(j!=0 && (v[j-1] & 1)==1)
			v[j]=v[j] | 0x80;

		v[j]=v[j]^R[j];

   	}

   }
}

    for(i=0;i<16;i++)
    product[i]=z[i];
}



/*implement GHASH function*/
void GHASH(unsigned char *input, unsigned char *output, unsigned char *hash_skey, int len_input){

    int m=len_input/128,i,j;
    unsigned char x[m][16];
    unsigned char y[16];


    for(j=0;j<len_input/8;j++){
        x[j/16][j%16] = input[j];
    }
 
    memset(y,0,16*sizeof(unsigned char));

   for(i=0;i<m;i++){
        unsigned char temp[16];
        for(j=0; j<16; j++){
            temp[j] = (y[j]^x[i][j]);
        }
        
        Multip_blocks(temp, hash_skey, y);
        
    }
    
    for(i=0;i<16;i++)
        output[i] = y[i];
    
}


/* Under the 16-byte (128-bit) key "k", 
and the 12-byte (96-bit) initial value "IV", 
encrypt the plaintext "plaintext" and store it at "ciphertext". 
The length of the plaintext is a multiple of 16-byte (128-bit) given by len_p (e.g., len_p = 2 for a 32-byte plaintext). 
The length of the ciphertext "ciphertext" is len_p*16 bytes. 
The authentication tag is obtained by the 16-byte tag "tag". 
For the authentication an additional data "add_data" can be added. 
The number of blocks for this additional data is "len_ad" (e.g., len_ad = 1 for a 16-byte additional data). 
*/
void aes128gcm(unsigned char *ciphertext, unsigned char *tag, const unsigned char *k, const unsigned char *IV, const unsigned char *plaintext, const unsigned long len_p, const unsigned char* add_data, const unsigned long len_ad) {

//using the block cipher in assignment1 to the "zero" block
    unsigned char zero [16];
    unsigned char H_key[16];
    memset(zero,0,16*sizeof(unsigned char));
    aes128e(H_key, zero,k);

//generate the pre-counter block from IV
    unsigned char jZero [16];
    unsigned char temp[4] = {0};
    temp[3] = 1;

    for(int i=0;i<12;i++){
      jZero[i]=IV[i];
     }

    for(int j=0;j<4;j++){
      jZero[j+12]=temp[j];
     }


    unsigned char Inc_result[16];
    Increment(32,jZero,Inc_result);
    GCTR(Inc_result, plaintext, ciphertext, k, len_p*128);

/*construct block (A||0v||C||0u||[len(A)]64||[len(C)]64) for GHASH*/

    unsigned char input_ghash[(len_ad+len_p+1)*16];
    /* put add_data and ciphertext into block*/
    int i=0;
    for(; i<len_ad*16; i++){
        input_ghash[i] = add_data[i];
    }
    
    for(int j=0; j<len_p*16; j++){
        input_ghash[i] = ciphertext[j];
        i++;
    }
    /*put A and C into block*/
    unsigned char A[8], C[8];
    memset(A, 0, 8*sizeof(unsigned char));
    memset(C, 0, 8*sizeof(unsigned char));
    unsigned long len_ad_128 = len_ad*128;
    unsigned long len_p_128 = len_p*128;
    memcpy(A, &len_ad_128, 8);
    memcpy(C, &len_p_128, 8);
    for(int j=7; j>=0; j--){
        input_ghash[i] = A[j];
        i++;
    }
    for(int j=7; j>=0; j--){
        input_ghash[i] = C[j];
        i++;
    }
   

    unsigned char S[16];
    GHASH(input_ghash, S, H_key,(len_ad+len_p+1)*128);
    GCTR(jZero, S, tag, k, (len_ad + len_p + 1)*128);

}


