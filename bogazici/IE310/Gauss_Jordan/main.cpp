//inversion is wrong
#include <iostream>
#include "fstream"
#include <vector>
using namespace std;
int main() {

    ofstream output("/Users/apple/CLionProjects/IE310/output.txt");
    for(int l=1; l<=3; l++) {   //for each data

        ifstream infile("/Users/apple/CLionProjects/IE310/Assignment2_Spring2020_Data" + to_string(l) + ".txt");
        output<<"Data " << l << ":"<<endl;
        double ratio;
        int n;
        infile >> n;    //determine the size
        cout.precision(3);
        cout.setf(ios::fixed);
        double a[n][n], ab[n][n + 1], x[n], AI[n][n+1], XI[n][n];

        //reading the data and mapping to them into A and A|b matrices
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n + 1; j++) {
                infile >> ab[i][j];
                if (j != n) {
                    a[i][j] = ab[i][j];
                }
            }
        }

        //pivotization
        for (int i = 0; i < n; i++) {
            for (int k = i + 1; k < n; k++) {
                if (ab[i][i] < ab[k][i] || ab[i][i] < -ab[k][i]) {
                    for (int j = 0; j <= n; j++) {
                        double temp = ab[i][j];
                        ab[i][j] = ab[k][j];
                        ab[k][j] = temp;
                        if (j != n) {
                            temp = a[i][j];
                            a[i][j] = a[k][j];
                            a[k][j] = temp;
                        }
                    }
                }
            }
        }

        //implementation of gauss elimination method
        for (int i = 0; i < n - 1; i++) {
            for (int k = i + 1; k < n; k++) {

                ratio = double(ab[k][i] / ab[i][i]);
                for (int j = 0; j <= n; j++) {

                    ab[k][j] = double(ab[k][j] - ratio * ab[i][j]);
                    if (j != n) {
                        a[k][j] = a[k][j] - ratio * a[i][j];
                    }
                }
            }
        }
        //rank calculation
        int j;
        bool flag;
        int rank = 1; //initialize the rank of A|b matrice
        for (int i = 1; i < n; i++) { //rank calculation
            j = 0;
            flag = true;
            while (j <= n && flag == true) {
                if (ab[i][j] != 0) {
                    flag = false;
                    rank++;
                }
                j++;
            }
        }
        int rank1 = 1; //initialize the rank of A matrice
        for (int i = 1; i < n; i++) {   //rank1 calculation
            j = 0;
            flag = true;
            while (j < n && flag == true) {
                if (labs(a[i][j]) != 0) {
                    flag = false;
                    rank1++;
                }
                j++;
            }
        }

        //scenarios
        if (rank1 == n) { //unique soln

            output<<"The problem has a unique soln. The variables X1, ... Xn are respectively equal to:";
            //implementation of back substitution
            for (int i = n - 1; i >= 0; i--) {
                x[i] = ab[i][n];
                for (j = i + 1; j < n; j++)
                    if (j != i)
                        x[i] = x[i] - ab[i][j] * x[j];
                x[i] = x[i] / a[i][i];
            }
            //writing the solution into the output file
            for (int i = 0; i < n; i++) {
                output << " ";
                output << x[i];
            }
            output << endl;

            double iden[n][n];
            for (int i = 0; i < n; i++) {   //creating the identity matrice
                for (int j = 0; j < n; j++) {
                    if (i == j) {
                        iden[i][j] = 1;
                    } else {
                        iden[i][j] = 0;
                    }
                }
            }
            int temp = n;
            //creating the A|I matrice which is a combination of A matrice and one column of identity matrice
            for (int z = 0; z < n; z++) {
                for (int i = 0; i < n; i++) {
                    for (int j = 0; j <= n; j++) {
                        if (j < n) {
                            AI[i][j] = a[i][j];
                        } else {
                            AI[i][j] = iden[i][j - temp]; //last column is equal to one column of identity matrice
                        }
                    }
                }

                //calculate one column of the inverted matrice and mapped them to XI matrice, using back substitution
                for (int i = n - 1; i >= 0; i--) {
                    x[i] = AI[i][n];
                    for (j = i + 1; j < n; j++) {
                        if (j != i)
                            x[i] = x[i] - AI[i][j] * x[j];
                    }
                    x[i] = double (x[i] / AI[i][i]);

                }
                for (int i = 0; i < n; i++) {
                    XI[i][z] = x[i];
                }

                temp--;    //decrease it for calculating the next column of inverted matrice
            }
            output<<endl;
            output << "Inverted A: " << endl;

            //writes the inverted matrice into output.txt
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    output << XI[i][j] << " ";
                }
                output<<endl;
            }


        } else if (rank1 == rank && rank < n) { //infinely many soln

            output << "The problem has infinely many solutions." << endl;
            output << "Arbitrary variable: Xn"<<endl;
            output << "Arbitrary solution(X1,...,Xn respectively):";

            x[n - 1] = 0;   //choosing the arbitrary variable nth variable = 0 all the time.
            for (int i = n - 2; i >= 0; i--) {

                //back substitution
                x[i] = ab[i][n];
                for (j = i + 1; j < n; j++)
                    if (j != i)
                        x[i] = x[i] - ab[i][j] * x[j];
                x[i] = x[i] / a[i][i];
            }

            //writes the arbitrary soln
            for (int i = 0; i < n; i++)
                output <<" "<< x[i];

            output<<endl;
        } else if (rank > rank1) { //no soln
            output << "The problem has no solution." << endl;
        }
        output<<endl;
    }
    output.close();
    return 0;

}