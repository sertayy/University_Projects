/*
 * Named semaphore example - parent side
 * The parent creates a named semaphore initially.
 * Then it creates (fork+exec) 2 child processes that will attach to this name semaphore.
 * Watch out for the name of the exec child process name. 
*/

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <semaphore.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>

#define SEM_NAME "./semaphoreexamples"
#define SEM_PERMS (S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP)
#define INITIAL_VALUE 1

#define CHILD_PROGRAM "./sem_chld"

int main(void) {

    /* We initialize the semaphore counter to 1 with permissions and semaphore name */
    sem_t *semaphore = sem_open(SEM_NAME, O_CREAT | O_EXCL, SEM_PERMS, INITIAL_VALUE);

	// If creation is failed
    if (semaphore == SEM_FAILED) {
        perror("sem_open(3) error");
        exit(EXIT_FAILURE);
    }

    pid_t pids[2];
    size_t i;

    for (i = 0; i < sizeof(pids)/sizeof(pids[0]); i++) {
        if ((pids[i] = fork()) < 0) {
            perror("fork(2) failed");
            exit(EXIT_FAILURE);
        }

        if (pids[i] == 0) {
            if (execl(CHILD_PROGRAM, CHILD_PROGRAM, NULL) < 0) {
                perror("execl(2) failed");
                exit(EXIT_FAILURE);
            }
        }
    }

    for (i = 0; i < sizeof(pids)/sizeof(pids[0]); i++)
        if (waitpid(pids[i], NULL, 0) < 0)
            perror("waitpid(2) failed");

    if (sem_unlink(SEM_NAME) < 0)
        perror("sem_unlink(3) failed");

    return 0;
}
