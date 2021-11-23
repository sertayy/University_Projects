/*
 * Named semaphore example - child side
 * The parent creates a named semaphore initially.
 * Then it creates (fork+exec) 2 child processes that will attach to this name semaphore.
 * This process replaces the memory of forked process
 * By specifying the name of the semaphore, the child processes can attach to and use it. 
 */



#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <semaphore.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>

#define SEM_NAME "./semaphoreexamples"
#define ITERS 10

int main(void) {
    sem_t *semaphore = sem_open(SEM_NAME, O_RDWR);
    if (semaphore == SEM_FAILED) {
        perror("sem_open(3) failed");
        exit(EXIT_FAILURE);
    }

    int i;
    for (i = 0; i < ITERS; i++) {
        if (sem_wait(semaphore) < 0) {
            perror("sem_wait(3) failed on child");
            continue;
        }

        printf("PID %ld acquired semaphore\n", (long) getpid());

        if (sem_post(semaphore) < 0) {
            perror("sem_post(3) error on child");
        }

        sleep(1);
    }

    if (sem_close(semaphore) < 0)
        perror("sem_close(3) failed");

    return 0;
}
