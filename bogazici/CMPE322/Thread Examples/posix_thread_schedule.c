/**
 * A simple program illustrating POSIX scheduling and contention scopes.
 * Remember that Mac OS and Linux-based systems use one-to-one threading model.
 */

#include <pthread.h>
#include <stdio.h>
#define NUM_THREADS 5

/* the thread runs in this function */
void *runner(void *param); 

main(int argc, char *argv[])
{
	int i, scope;
	pthread_t tid[NUM_THREADS]; 	/* the thread identifier */
	pthread_attr_t attr; 		/* set of attributes for the thread */
	int choice = atoi(argv[1]);
	/* get the default attributes */
	pthread_attr_init(&attr);

	/* first inquire on the current scope */
	if (pthread_attr_getscope(&attr,&scope) != 0)
		fprintf(stderr, "Unable to get scheduling scope.\n");
	else {
		if (scope == PTHREAD_SCOPE_PROCESS)
			printf("This system uses PTHREAD_SCOPE_PROCESS as contention \n");
		else if (scope == PTHREAD_SCOPE_SYSTEM)
			printf("This system uses PTHREAD_SCOPE_SYSTEM as contention \n");
		else 
			fprintf(stderr,"Illegal scope value.\n");
	}
	
	/* set the scheduling algorithm to PCS or SCS */
	if(choice == 1)
	{
	if (pthread_attr_setscope(&attr, PTHREAD_SCOPE_SYSTEM) != 0)
		printf("unable to set system contention policy.\n");
	}
	else
	{
	if (pthread_attr_setscope(&attr, PTHREAD_SCOPE_PROCESS) != 0)
		printf("Error: It is unable to set PTHREAD_SCOPE_PROCESS as policy.\n");
	}
	/* create the threads */
	for (i = 0; i < NUM_THREADS; i++) 
		pthread_create(&tid[i],&attr,runner,NULL); 

	/**
	 * Now join on each thread
	 */
	for (i = 0; i < NUM_THREADS; i++) 
		pthread_join(tid[i], NULL);
}

/**
 * The thread will begin control in this function.
 */
void *runner(void *param) 
{
	printf("This is the output by separate threads\n");

	pthread_exit(0);
}

