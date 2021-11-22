/*
 * Simple multi threading example for finding the prime numbers
*/
#include <pthread.h>
#include <stdio.h>

// defining a maximum number
#define MAX_SIZE 256
//creating array with the size of the maximum number
int primes[MAX_SIZE];

void *runner(void *param); // the thread executes this method

int main(int argc, char *argv[])
{
int i;
pthread_t tid; // ID of the thread
pthread_attr_t attr; // get default attributes of the thread

if (argc != 2) { // if there is not any argument
	fprintf(stderr,"usage: a.out <integer value>\n");
	return -1;
}

if (atoi(argv[1]) < 2) { // if the value that user enters smaller than 2
	fprintf(stderr,"Argument %d must be >= 2 \n",atoi(argv[1]));
	return -1;
}
pthread_attr_init(&attr); // initialize the thread attributes with default configuration
pthread_create(&tid,&attr,runner,argv[1]);
// now wait for the thread to exit
pthread_join(tid,NULL);

// print the output
for (i = 1; i <= atoi(argv[1]); i++)
	if (primes[i] > 0)
		printf("%d\n", i);
}

// This method finds the prime numbers
void *runner(void *param) 
{
int i, j;
int upper = atoi(param);

	primes[1] = 0;
	for (i = 2; i <= upper; i++)
		primes[i] = 1;

	for (i = 2; i <= upper/2; i++)
		for (j = 2; j <= upper/i; j++)
			primes[i*j] = 0;

	pthread_exit(0);
}
