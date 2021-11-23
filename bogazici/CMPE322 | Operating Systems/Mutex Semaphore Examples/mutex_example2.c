#include <stdio.h>
#include <pthread.h>

pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;

// The line above actually equals to pthread_mutex_init(&m,NULL)
// PTHREAD_MUTEX_INITIALIZER macro can be used for only global variables of mutex
int sum = 0; // global sum variable

void *countgold(void *param) {
    int i; //local for threads
    
    // Actually, critical section is just 'sum += 1'
    // However locking and unlocking a million times is a overhead, as we saw at PS
    pthread_mutex_lock(&m);

    for (i = 0; i < 10000000; i++) {
	sum += 1;
    }
    pthread_mutex_unlock(&m);
    return NULL;
}

int main() {
    pthread_t tid1, tid2;
    pthread_create(&tid1, NULL, countgold, NULL);
    pthread_create(&tid2, NULL, countgold, NULL);

    pthread_join(tid1, NULL);
    pthread_join(tid2, NULL);

    printf("Total sum is %d\n", sum);
    return 0;
}
