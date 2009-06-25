#include<stdio.h>
#include<string.h>

int xtoi(const char* xs, long int* result) {
 size_t szlen = strlen(xs);
 long int i, xv, fact;

 if (szlen > 0) {
  // Converting more than 32bit hexadecimal value?
//if (szlen>8) return 2; // exit

  // Begin conversion here
  *result = 0;
  fact = 1;

  // Run until no more character to convert
  for(i=szlen-1; i>=0 ;i--) {
   if (isxdigit(*(xs+i))) {
    if (*(xs+i)>=97) {
     xv = ( *(xs+i) - 97) + 10;
    } else if ( *(xs+i) >= 65) {
     xv = (*(xs+i) - 65) + 10;
    } else {
     xv = *(xs+i) - 48;
    }
    *result += (xv * fact);
    fact *= 16;
   } else {
    return 4;
   }
  }
   return 0;
 }
  return 4;
}


int main (int argc, char *argv[]) {
	long int res;
	
	xtoi(argv[1],&res);
	printf("%s -> %li\n",argv[1],res);
	return 0;
}

