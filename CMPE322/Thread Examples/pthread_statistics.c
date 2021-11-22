/*
 * A simple example for separate operations on the same data set with multiple threads
*/
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>

// the list of integers
int *list;

// the values that we are trying to find through each of the threads
double average;
int maximum;
int minimum;

// The methods for finding the values
void *calculate_average(void *param);
void *calculate_maximum(void *param);
void *calculate_minimum(void *param);

int main(int argc, char *argv[])
{
	// integer value for loop which takes each integer from the argument and put into list
	int i;
	printf("Argc value is %d \n", argc);
	int num_of_args = argc-1; // the number of integers are 1 less than argc
	pthread_t tid_1; // first thread ID
    pthread_t tid_2; // second thread ID
    pthread_t tid_3; // third thread ID

    // allocate memory to hold array of integers 
    list = malloc(sizeof(int)*num_of_args); // allocate memory with the size of integers * number of args
	for (i = 0; i < num_of_args; i++)
		list[i] = atoi(argv[i+1]);	// convert the arguments into integer and store in the memory
	
	// creating the threads, assigning each to separate statistics functions with the arguments
	pthread_create(&tid_1, 0, calculate_average, &num_of_args);
	pthread_create(&tid_2, 0, calculate_maximum, &num_of_args);
	pthread_create(&tid_3, 0, calculate_minimum, &num_of_args);

	// parent thread waits for the children threads
	pthread_join(tid_1, NULL);
	pthread_join(tid_2, NULL);
	pthread_join(tid_3, NULL);

	// after each thread completes executing the instructions, print out the results
	printf("The average is %f\n", average);
	printf("The maximum is %d\n", maximum);
	printf("The minimum is %d\n", minimum);

	return 0;
}

// method for finding the average of the integers
void *calculate_average(void *param)
{
	int count = *(int *)param;
	int i, total = 0;

	printf("count = %d\n",count);
	for (i = 0; i < count; i++)
		printf("%d\n",list[i]);	

	for (i = 0; i < count; i++)
		total += list[i];

	average = total / count;

	pthread_exit(0); // exit thread
}

void *calculate_maximum(void *param)
{
	int count = *(int *)param;
	int i;

	maximum = list[0];

	for (i = 1; i < count; i++)
		if (list[i] > maximum)
			maximum = list[i];

    pthread_exit(0); // exit thread
}

void *calculate_minimum(void *param)
{
	int count = *(int *)param;
	int i;

	minimum = list[0];

	for (i = 1; i < count; i++)
		if (list[i] < minimum)
			minimum = list[i];

    pthread_exit(0); // exit thread
}

