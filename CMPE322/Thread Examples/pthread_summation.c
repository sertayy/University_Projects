/*
 * A program with multiple threads to calculate the summation of an integer set.
*/

#include <pthread.h>
#include <stdio.h>

int sum; /* this global data is shared by the threads */

void *runner(void *param); /* the declaration function executed by the thread */

int main(int argc, char *argv[])
{
pthread_t tid; /* the thread identifier */
pthread_attr_t attr; /* set of attributes for the thread */

if (argc != 2) { // If there is not any argument, exit
	fprintf(stderr,"usage: a.out <integer value>\n");
	return -1;
}

if (atoi(argv[1]) < 0) { // If the argument is a negative integer
	fprintf(stderr,"Argument %d must be non-negative\n",atoi(argv[1]));
	/*exit(1);*/
	return -1;
}

/* get the default attributes defined by pthread */
pthread_attr_init(&attr);

/* create the thread with giving an ID, default attributes, where to start and argument for the method */
pthread_create(&tid,&attr,runner,argv[1]);

/* parent thread waits for the child thread to exit */
pthread_join(tid,NULL);

// print the sum calculated by the child thread
printf("sum = %d\n",sum);
}

// The execution of the thread will begin in this function
void *runner(void *param) 
{
int i; // simple integer for the loop iterations
int upper_limit = atoi(param); // assigning the argument to an integer
sum = 0; // global sum variable

	if (upper_limit > 0) {
		for (i = 1; i <= upper_limit; i++)
			sum += i;
	}

	pthread_exit(0); // terminate the thread
}
