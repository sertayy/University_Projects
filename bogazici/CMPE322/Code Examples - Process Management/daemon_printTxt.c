/*****
 This is an example of a daemon process.
 The process prints out a string with an index continuously to an external file.
 You can check the operation of the process after executing it through
 the terminal and killing the bash process.
*****/

#include <stdio.h>
#include <unistd.h>

int main() {
    pid_t pid;
    FILE *f = fopen("output.txt", "w");
    if (f == NULL) {
        printf("Error opening file \n");
        exit(1);
    }
    pid = fork();
    if (pid != 0) {
        exit(1);
    }
    const char *outputText = "Print this out to the txt file";
    int index = 0;
    while (index < 1000) {
        fprintf(f, outputText);
        fprintf(f, "and the index is %d \n", index);
        sleep(1);
        index++;
        fclose(f);
        f = fopen("output.txt", "a");
    }
    fclose(f);
    return 0;

}
