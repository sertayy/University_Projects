/******
 This is a simple process that demonstrates zombie
 After creating a new child process, the parent did not call wait.
 The child process terminates after its operations are completed but since
 the parent process did not call wait, it will be a zombie process
 You can check the state of the process by invoking ps command through terminal
 */

#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>

int main(void)
{
	pid_t pid;

	pid = fork();

	if (pid < 0) {
		fprintf(stderr,"Unable to create child process\n");

		return -1;
	}
	else if (pid == 0) {
		// The child process terminates and exits without any operation.
		printf("The child process is terminated... \n");
		return 0;
	}
	else {
		// Parent sleeps for 100 seconds, but watch out that sleep is not same with wait..
		sleep(100);
		printf("Parent exiting now... \n");
		return 0;
	}
}
