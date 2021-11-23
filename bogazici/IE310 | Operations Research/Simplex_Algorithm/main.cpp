#include <iostream>
#include <vector>
#include "fstream"
using namespace std;
int variables;
int constraints;
int total;  // variables + constraints
bool unbounded=false;   //check unbounded condition
double maxZ=0;  //objective function value
double minValue;    //minimum value in the Z row
int locIndex;   //location index
int countnegatives;
int pivotColumn;
int pivotRow;
bool isOptimal = false;
int countpositive;
void Algorithm(vector<double> Z, vector<double> B, vector<vector<double>> A);
void print(vector<double> B, vector<vector<double>> A);
int PivotColumn(vector<double> Z);
int PivotRow(int pivotColumn, vector<double> B, vector<vector<double>> A);
bool Optimal(vector<double> Z, vector<double> B, vector<vector<double>> A);
void iteration(int pivotRowVal, int pivotColumnVal, vector<double> Z, vector<double> B, vector<vector<double>> A);

int main()
{
    cout.precision(2);
    cout.setf(ios::fixed);
    ifstream infile("/Users/apple/CLionProjects/IE310/IE310Assignment3/Assignment3_Spring2020_Data1.txt");  //reads the file from the path
    infile >> constraints;
    infile >> variables;
    total = variables + constraints;
    vector<double> Z(total);
    vector<double> B(constraints);
    vector<vector<double>> A(total, vector<double>(constraints));
    int temp;

    //preparing the Z,A and B matrices
    for (int i = 0; i < total; i++) {
        if (i >= variables) {
            Z[i] = 0;
        } else {
            infile >> temp;
            Z[i] = -temp;
        }
    }
    for (int i = 0; i < constraints; i++) {
        for (int j = 0; j < total; j++) {
            if (j >= variables) {
                if (j == variables) {
                    infile >> temp;
                    B[i] = temp;
                }
                if (j - variables == i) {
                    A[j][i] = 1;
                }
            } else if (j < variables) {
                infile >> temp;
                A[j][i] = temp;
            }
        }
    }

    Algorithm(Z, B, A);
    return 0;
}


void Algorithm(vector<double> Z, vector<double> B, vector<vector<double>> A){

    if(Optimal(Z, B, A) != true){    //check the optimality
        if(unbounded == true){  //check the unboundedness
            cout<<"Unbounded"<<endl;
        }else{
            iteration(PivotRow(PivotColumn(Z), B, A), PivotColumn(Z), Z, B, A);    //prepare the next table
        }
    }
}

int PivotColumn(vector<double> Z){   //find the pivot column.

    locIndex = 0;
    minValue = Z[0];
    for(int i=1; i<total; i++){
        if(minValue > Z[i]){
            minValue = Z[i];
            locIndex = i;
        }
    }
    return locIndex;
}

int PivotRow(int pivotColumn, vector<double> B, vector<vector<double>> A){  //find the pivot row

    double minRatio[constraints];
    double positives[constraints];
    countnegatives = 0;

    for(int i=0; i<constraints; i++){
        if(0 < A[pivotColumn][i]){
            positives[i] = A[pivotColumn][i];
        } else{
            positives[i] = 0;
            countnegatives += 1;
        }
    }

    if(countnegatives == constraints){
        unbounded = true;
    } else{
        for(int i=0; i<constraints; i++){
            if(positives[i] != 0){
                minRatio[i] = B[i] / positives[i];  // calculate min ratio
            }
            else{
                minRatio[i] = 0;
            }
        }
    }

    double minimum = 9999999999;
    int locIndex2 = 0;
    for(int i=0; i<B.size(); i++){
        if(minRatio[i] > 0){
            if(minimum > minRatio[i]){
                minimum = minRatio[i];
                locIndex2 = i;
            }
        }
    }
    return locIndex2;
}

void iteration(int pivotRowVal, int pivotColumnVal, vector<double> Z, vector<double> B, vector<vector<double>> A){

    double pivotColValues[constraints];
    double pivotRowValues[total];
    double newRow[total];
    double pivotVal = A[pivotColumnVal][pivotRowVal];//gets the pivot value

    maxZ -= (Z[pivotColumnVal] * (B[pivotRowVal] / pivotVal));  //sets the Z value in each iteration

    for(int i=0; i<constraints; i++){
        pivotColValues[i] = A[pivotColumnVal][i];   //get the pivot column

    }

    for(int i=0; i<total; i++){
        pivotRowValues[i] = A[i][pivotRowVal];  //get the pivot row
    }

    for(int i=0; i<total; i++){
        newRow[i] = pivotRowValues[i] / pivotVal;   //calculate the new row that has the pivot value

    }
    B[pivotRowVal] /= pivotVal;

    //calculate the new A matrix
    for(int i=0; i < constraints; i++){
        if(i != pivotRowVal){   //pivot row is already calculated
            for(int j=0; j < total; j++){
                A[j][i] -= (pivotColValues[i] * newRow[j]);
            }
        }
    }

    double val = Z[pivotColumnVal];
    for(int i=0;i<total;i++){       //prepare the Z row for the next iteration

        Z[i] -= (val * newRow[i]);

    }

    for(int i=0;i<constraints;i++){     //prepare the B column for the next iteration

        if(i != pivotRowVal){
            B[i] -= (pivotColValues[i] * B[pivotRowVal]);
        }
    }

    for(int i=0;i<total;i++){   //prepare the A matrice for the next iteration
        A[i][pivotRowVal] = newRow[i];

    }
    Algorithm(Z, B, A);
}

bool Optimal(vector<double> Z, vector<double> B, vector<vector<double>> A){

    countpositive = 0;
    for(int i=0; i<total;i++){  //check if the objective function has negative values
        if(0 <= Z[i]){
            countpositive++;
        }
    }
    if(countpositive == total){
        isOptimal = true;
        print(B, A);
    }
    return isOptimal;
}

void print(vector<double> B, vector<vector<double>> A){

    int count=0;
    cout<<"Optimal variable vector: ";
    cout<<"[";
    for(int i=0;i< variables; i++){  //every basic column has the values, get it form B array
        int count0 = 0;
        int index = 0;
        for(int j=0; j< constraints; j++){
            if(A[i][j]==0.0){
                count0 += 1;
            }
            else if(A[i][j]==1){
                index = j;
            }
        }
        count++;
        if(count==1){
            if(count0 == constraints -1 ){
                cout<<B[index];  //every basic column has the values, get it form B array
            }
            else{
                cout<<0;
            }
        }else{
            if(count0 == constraints -1 ){
                cout<<", "<<B[index];  //every basic column has the values, get it form B array
            }
            else{
                cout<<", "<<0;
            }
        }
    }
    cout<<"]"<<endl;
    cout<<"Optimal result: "<<maxZ<<endl;  //print the maximum values
}