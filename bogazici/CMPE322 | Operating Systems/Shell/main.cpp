/*
 Implemented by Sertay Akpinar, 06.12.2019 ®
 */
#include <iostream>
#include <unistd.h>
#include <stdio.h>
#include <sys/wait.h>
#include <string>
#include <fcntl.h>
#include <vector>

void createfork(char **string);

using namespace std;
int main() {
    char * user_name = getenv("USER");

    vector<string> commands;
    char* args[3];
    string command;
    string nwcommand;
    string cmd;
    string dash;

    while(command.compare("exit")) {

        cout << user_name;
        cout << " >>> ";

        getline(cin, command);
        nwcommand = command.substr(0, command.find(" "));
        commands.push_back(command);

            if (command.find(" grep ")!= string::npos) {

                string arg = command.substr(command.find("\"")+1);
                arg = arg.substr(0, arg.find("\""));
                int pipefd[2], status;
                pid_t pid;
                pipe(pipefd);
                pid = fork();

                if (pid == 0) {

                    if(!command.substr(0,command.find("|")).compare("listdir ")){
                        cout<<"girdi"<<endl;

                        close(pipefd[0]);
                        dup2(pipefd[1], STDOUT_FILENO);
                        cmd = "ls";
                        args[0] = (char*) cmd.c_str();
                        args[1] = NULL;
                        args[2] = NULL;
                        execvp(args[0],args);
                    }else if(!command.substr(0,command.find("|")).compare("listdir -a ")){
                        close(pipefd[0]);
                        dup2(pipefd[1], STDOUT_FILENO);
                        cmd = "ls";
                        dash = "-a";
                        args[0] = (char *) cmd.c_str();
                        args[1] = (char *) dash.c_str();
                        args[2] = NULL;
                        execvp(args[0],args);
                    }
                }

                pid = fork();
                if (pid == 0) {

                    close(pipefd[1]);
                    dup2(pipefd[0], STDIN_FILENO);
                    cmd = "grep";
                    args[0] = (char *) cmd.c_str();
                    args[1] = (char *) arg.c_str();
                    args[2] = NULL;
                    execvp(args[0],args);
                }
                close(pipefd[0]);
                close(pipefd[1]);
                waitpid(-1, &status, 0);
                waitpid(-1, &status, 0);
            }

        else if (!command.compare("listdir -a")) {

            cmd = "ls";
            dash = "-a";
            args[0] = (char *) cmd.c_str();
            args[1] = (char *) dash.c_str();
            args[2] = NULL;
            createfork(args);

        } else if (!nwcommand.compare("listdir")) {

            cmd = "ls";
            args[0] = (char *) cmd.c_str();
            args[1] = NULL;
            args[2] = NULL;
            createfork(args);

        } else if (!nwcommand.compare("currentpath")) {

            cmd = "pwd";
            args[0] = (char *) cmd.c_str();
            args[1] = NULL;
            args[2] = NULL;
            createfork(args);

        } else if (!nwcommand.compare("printfile")) {

            string file = command.substr(10);
            cmd = "cat";
            args[0] = (char *) cmd.c_str();
            args[1] = (char *) file.c_str();
            args[2] = NULL;
            createfork(args);
            cout << endl;

        } else if (!nwcommand.compare("Printfile")) {

            command = command.substr(10);
            string arg = command.substr(0, command.find(" "));
            string arg2 = command.substr(command.find(">") + 2);

            cmd = "cat";
            args[0] = (char *) cmd.c_str();
            args[1] = (char *) arg.c_str();
            args[2] = NULL;

            pid_t pid = fork();
            if (pid == 0) {
                int ofd;
                ofd = creat(arg2.c_str(), 0644);
                dup2(ofd, 1);
                execvp(args[0], args);
            } else {
                wait(0);
            }
        } else if (!nwcommand.compare("footprint")) {

            int line = 0;
            if (commands.size() < 15) {
                for (int i = 0; i <= commands.size() - 1; i++) {
                    line++;
                    cout << line;
                    cout << +" " + commands.at(i) << endl;
                }
            } else {
                for (int i = commands.size() - 15; i <= commands.size() - 1; i++) {
                    line++;
                    cout << line;
                    cout << +" " + commands.at(i) << endl;
                }
            }
        }
    }
    return 0;
}

void createfork(char* args[3]){

    pid_t pid = fork();
    if(pid == 0){
        if(execvp(args[0],args) == -1){
            perror("exec");
        }
    }
    if(pid > 0){
        wait(0);
    }
}
