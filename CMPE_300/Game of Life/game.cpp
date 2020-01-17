/*
	Sertay Akpınar, 2016400075
	Compiling Status: Compiling
	Working Status: Working
	Implemented striped splits with periodic boundary
*/

#include "mpi.h"
#include "iostream"
#include "fstream"      
using namespace std;

int main(int argc, char* argv[]){

	//initialization
    MPI_Init(NULL,NULL);
	int rank, size;
	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	MPI_Comm_size(MPI_COMM_WORLD, &size);
	MPI_Status status;
	ifstream file(argv[1]);
    ofstream output(argv[2]);
    int T = atoi(argv[3]);		// T = iteration 
	int N = 360;
	int board[N][N];
	int r = N/(size-1); //the column size of the worker process
	
	if (rank==0){	
		
		//reads the input file 
		for (int y = 0; y < N; y++) {
			for (int x = 0; x < N; x++) {
	      		file >> board[y][x];
	    	}
	    }
	   	file.close();

		//distributes the board with striped splits and sends the slices to the worker processes
	   	int slice[r][N];
	   	for(int i=1; i<=size-1; i++){
	   		for(int j=0; j<r; j++){
	   			for(int k=0; k<N; k++){
	   				slice[j][k] = board[j+((i-1)*r)][k];
	   			}
	   		}
	   		MPI_Send(&slice, N*r, MPI_INT, i, 1, MPI_COMM_WORLD);
	   	}

		//receives the slices of each worker after the iterations
		for(int i=1; i<=size-1; i++){

			MPI_Recv(&slice, N*r, MPI_INT, i, 1, MPI_COMM_WORLD, &status);

			for(int j=0; j<r; j++){
				for(int k=0; k<N; k++){
					board[j+((i-1)*r)][k] = slice[j][k];
				}
			}
		}

		//writes the last map, which is updated after the iterations, to the outputfile
		for (int x = 0; x < N; x++) {
			for (int y = 0; y < N; y++) {
	      		output << board[x][y] << " ";
	    	}
	   	output << endl;
	    }
	}  	
  	else{

  		int myslice[r][N];
  		MPI_Recv(&myslice, N*r, MPI_INT, 0, 1, MPI_COMM_WORLD, &status);	//each worker processes receieve its own slices from process 0
  		int fromdown[N]; int toup[N]; int fromup[N]; int todown[N];		//rows to send or receive between the worker processes
  		
  		//each process updates itself T times according to the game's rules
  		for(int p=0; p<T; p++){		
  			
  			for(int j=0; j<N; j++){		//determines the last row of each process for sending the info to the process below
  				todown[j] = myslice[r-1][j];
  			}
  			for(int k=0; k<N; k++){		//determines the first row of each process for sending the info to the process above
  				toup[k] = myslice[0][k];
  			}

  			//odd ranked workers send their infos to even ranked workers in either way(toup and todown) 
  			//and wait to receive the infos from the even ranked workers in either way(fromup and fromdown)
  			if(rank%2 != 0){
	  				
  				MPI_Send(&todown, N, MPI_INT, rank+1, 1, MPI_COMM_WORLD);
  				MPI_Recv(&fromdown, N, MPI_INT, rank+1, 1, MPI_COMM_WORLD, &status);
  				
  				if(rank == 1){
  					MPI_Send(&toup, N, MPI_INT, size-1, 1, MPI_COMM_WORLD);
  					MPI_Recv(&fromup, N, MPI_INT, size-1, 1, MPI_COMM_WORLD, &status);		
  				}
  				else{
  					MPI_Send(&toup, N, MPI_INT, rank-1, 1, MPI_COMM_WORLD);
  					MPI_Recv(&fromup, N, MPI_INT, rank-1, 1, MPI_COMM_WORLD, &status);
  				}
  			}
  			//even ranked workers receive the infos from the even ranked workers in either way(fromup and fromdown)
  			//and send their infos to odd ranked workers in either way(toup and todown) 
  			else{

  				MPI_Recv(&fromup, N, MPI_INT, rank-1, 1, MPI_COMM_WORLD, &status);
  				MPI_Send(&toup, N, MPI_INT, rank-1, 1, MPI_COMM_WORLD);
  				
  				if(rank==size-1){
  					MPI_Recv(&fromdown, N, MPI_INT, 1, 1, MPI_COMM_WORLD, &status);
  					MPI_Send(&todown, N, MPI_INT, 1, 1, MPI_COMM_WORLD);	
  				}
  				else{
  					MPI_Recv(&fromdown, N, MPI_INT, rank+1, 1, MPI_COMM_WORLD, &status);
  					MPI_Send(&todown, N, MPI_INT, rank+1, 1, MPI_COMM_WORLD);
  				}
  			}

  			//counting the neighbors of each cell in the map
  			int sum = 0;
  			int temp_slice[r][N];
  			
  			for (int x=0; x<r; x++){
				for (int y=0; y<N; y++){

					if(x==0 && y==N-1){ //upper right corner
						sum = myslice[x][y-1] + myslice[x+1][y-1] + myslice[x+1][y] + myslice[x+1][0] + myslice[x][0] + fromup[0] + fromup[y] + fromup[y-1]; 
					}
					else if(x==r-1 && y==N-1){ //lower right corner
						sum = myslice[x-1][y] + myslice[x-1][y-1] + myslice[x][y-1] + myslice[x][0] + myslice[x-1][0] + fromdown[N-1] + fromdown[N-2] + fromdown[0];
					}
					else if (x==r-1 && y==0){ //lower left corner
						sum = myslice[x][y+1] + myslice[x-1][y+1] + myslice[x-1][y] + myslice[x][N-1] + myslice[x-1][N-1] + fromdown[0] + fromdown[1] + fromdown[N-1];
					}
					else if(x==0 && y==0){ //upper left corner
						sum = myslice[x+1][y] + myslice[x+1][y+1] + myslice[x][y+1] + myslice[x][N-1] + myslice[x+1][N-1] + fromup[1] + fromup[0] + fromup[N-1];
					}
					else{	//not corner

						if (y==N-1){ //rightmost line
							sum = myslice[x-1][y] + myslice[x-1][y-1] + myslice[x][y-1] + myslice[x+1][y-1] + myslice[x+1][y] + myslice[x+1][0] + myslice[x][0] + myslice[x-1][0];
						}
						else if (x==r-1){ //lowermost line
							sum = myslice[x-1][y-1] + myslice[x-1][y] + myslice[x-1][y+1] + myslice[x][y+1] + myslice[x][y-1] + fromdown[y-1] + fromdown[y] + fromdown[y+1];
						}
						else if(y==0){ // leftmost line
							sum = myslice[x-1][y] + myslice[x-1][y+1] + myslice[x][y+1] + myslice[x+1][y+1] + myslice[x+1][y] + myslice[x+1][N-1] + myslice[x][N-1] + myslice[x-1][N-1];
						} 
						else if (x==0){ //uppermost line
							sum = myslice[x][y-1] + myslice[x+1][y-1] + myslice[x+1][y] + myslice[x+1][y+1] + myslice[x][y+1] + fromup[y-1] + fromup[y] + fromup[y+1];
						}	
						else{ //middle cells, not in the edges
							sum = myslice[x-1][y-1] + myslice[x-1][y] + myslice[x-1][y+1] + myslice[x][y+1] + myslice[x+1][y+1] + myslice[x+1][y] + myslice[x+1][y-1] + myslice[x][y-1];
						}
					}
					//implemented the game's rules, writes the updated datas to a temporary slice
					if(myslice[x][y] == 1 && sum < 2){
						temp_slice[x][y] = 0;
					}
					else if(myslice[x][y] == 1 && sum > 3){
						temp_slice[x][y] = 0;
					}
					else if(myslice[x][y] == 0 && sum ==3){
						temp_slice[x][y] = 1;
					}
					else if(myslice[x][y] == 1 && (sum == 2 || sum == 3)){
						temp_slice[x][y] = 1;
					} 
					else{
						temp_slice[x][y] = 0;
					}
				}
			}
			//gets the results from the temporary slice to prepare each processes' slice for the next iteration
			for(int i=0; i<r; i++){
				for(int j=0; j<N; j++){
					myslice[i][j] = temp_slice[i][j];
				}
			}
		} //iteration ends

		MPI_Send(&myslice, N*r, MPI_INT, 0, 1, MPI_COMM_WORLD); //each process sends its final status of the slice to the process 0
  	}

	MPI_Finalize();
    output.close();
	return 0;
}