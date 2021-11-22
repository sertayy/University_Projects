/*
 * In order to successfully use the following command:
 *
 *	gcc -fopenmp openmp.c
 */

#include <omp.h>
#include <stdio.h>

int main(int argc, char *argv[])
{
	/* Entering to the parallel region, you should see the print more than one time */

	#pragma omp parallel
	{
		printf("I am a parallel region\n");
	}


	return 0;
}
