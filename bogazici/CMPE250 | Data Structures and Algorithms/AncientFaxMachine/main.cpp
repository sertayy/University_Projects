#include <iostream>
#include <fstream>
#include <vector>
#include <stdio.h>
#include <math.h>
#include <list>
#include<string.h>


using namespace std;

string txt;
int numOfWords;
int modulo = pow(10,9) + 7;
int prime = 163363;

int main() {

    /* if (argc != 3) {
         cout << "Run the code with the following command: ./project4 [input_file] [output_file]" << endl;
         return 1;
     }
 */

    ifstream infile("/Users/sertayakpinar/CLionProjects/project5/inputDNA1.txt");
    ios_base::sync_with_stdio(false);
    infile >> txt;

    int hashtxt[txt.length()];
    int hashT = 0;

    for (int i = 0; i < txt.length(); i++) {

        int d = 13;
        d = pow(d, i);
        hashT = (hashT + d * txt[i]) % prime;
        hashtxt[i] = hashT;
        cout << hashtxt[i] << endl;

    }
    cout << endl;

    infile >> numOfWords;

    int hashWords[numOfWords];
    string dictionary[numOfWords];

    for (int i = 0; i < numOfWords; i++) {

        infile >> dictionary[i];
    }

    for (int i = numOfWords - 1 ; i<0; i--) {

        int hashP = 0;

        for (int j = dictionary[i].length() - 1; j < 0 ; j--) {

            int d = 13;
            d = pow(d, j);

            hashP =((hashP + d * dictionary[i].at(j)) ) % prime;

        }

        hashWords[i] = hashP;
        cout<<hashWords[i]<<endl;

    }

    return 0;
}
