/*****
 Simple example including fork, wait and exec
 Exec part is commented currently, you can comment out and check the ongoin operations.
*****/

#include <sys/types.h>
#include <stdio.h>
#include <unistd.h>

#define MAX_COUNT 1000

int main()
{
	pid_t pid;
    int i;
    int y;
	pid = fork(); /* creating a child process */
	if (pid < 0) /* error occurred returns -1 */
	{  
		fprintf(stderr, "Fork Failed"); 
		return 1;
	}
	else if (pid == 0) /* execution of the child process */
	{ 
		//for(i=0; i<MAX_COUNT; i++)
		//{
		//	printf("This is child process \n");
		//}
		printf("The Child says that: My pid is %d, and my parent's pid is %d \n", getpid(),getppid());
        //execlp("/bin/ls","ls",NULL);
	}
	else /* execution of the parent process */
	{  
		wait(NULL); /* parent will wait for the child to complete */
		//for(y=0; y<MAX_COUNT; y++)
		//{
		//	printf("This is parent process \n");
		//}
        
        //printf("Child Complete \n");
        printf("The Parent says that: My pid is %d, my child's pid is %d and my parent's pid is %d \n", getpid(),pid,getppid());
	}
	return 0;
}
