import java.io.*;
import java.util.*;
public class SA2016400075 {
	
	public static void main(String []args) throws FileNotFoundException {

		Random rand=new Random(); // for computer's move  
		Scanner console = new Scanner(System.in); // for user's move
		System.out.println("Do you want to play a new game or an ongoing game?");
		String answer=console.nextLine();
		
		// valid inputs below
		while(!(answer.equalsIgnoreCase("New game") || answer.equalsIgnoreCase("ongoing game") || answer.equalsIgnoreCase("new"))){
			System.out.println("Sorry, you have to choose a new game or ongoing game.");
			answer = console.nextLine();

		}
		
		String[][] board= new String[4][4]; // creates the matrix
		
		if(answer.equalsIgnoreCase("new game") || answer.equalsIgnoreCase("new")){ // begins the game
			PrintStream stream = new PrintStream("input.txt"); // this file saves the game

			for(int i=0;i<4;i++){
				
				for(int j=0;j<4;j++){
				//fills the board with E (which means empty piece for the game)
				board[i][j]="E";
				System.out.print(board[i][j] +" ");
				stream.print(board[i][j] +" ");
				}
				System.out.println();
				stream.println();
			}
			gamePlay(board,rand,console,stream);

		} else if(answer.equalsIgnoreCase("ongoing game")){
			Scanner input = new Scanner(new File("input.txt")); // reads the previously saved game)
			
			while(input.hasNext()){ // creates the last 4x4 matrix which composed before leaving the game 
				
				for(int i=0;i<4;i++){
					for(int j=0;j<4;j++){
						
						board[i][j]=input.next();
						
					}
					input.nextLine();
				}
				
			}
			save(board,rand,console);
			}	
		}
	// It generates the last view of the game board
	public static void save(String[][] board,Random rand,Scanner console) throws FileNotFoundException{
		
		PrintStream stream=new PrintStream(new File("input.txt"));
		int count = 0;
		for(int i=0;i<4;i++){
			for(int j=0;j<4;j++){
				
				if(board[i][j].equals("E")){
					count++;
				}
			}
		}
		for(int i=0;i<4;i++){
			for(int j=0;j<4;j++){
				
				System.out.print(board[i][j] + " ");
			}
			System.out.println();
			
		}
		// Determines who makes the next move
			if(count%2==1){
				reverseGamePlay(board,rand,console,stream);
			
		} else{
				gamePlay(board,rand,console,stream);	
			
		}
	}
		// Updates the board after each move by adding pieces
	public static void printer(String [][] board,PrintStream stream){
		
		for(int i=0;i<4;i++){
			for(int j=0;j<4;j++){
				
				System.out.print(board[i][j] + " ");
				stream.print(board[i][j] + " ");
			}
			System.out.println();
			stream.println();
			
		}
		
	}
	// thanks to this computer choose the pieces randomly
	public static String piece(Random rand){
		
		int num =rand.nextInt(16);
		
		if		 (num==0){ 
			return "WSRH";
		}else if (num==1){ 
			return "WTRH";
		}else if (num==2){
			return "WSRS";
		}else if (num==3){ 
			return "WTRS";
		}else if (num==4){ 
			return "WSSH";
		}else if (num==5){ 
			return "WTSH";
		}else if (num==6){ 
			return "WSSS";
		}else if (num==7){ 
			return "WTSS";
		}else if (num==8){ 
			return "BSRH";
		}else if (num==9){ 
			return "BTRH";
		}else if (num==10){ 
			return "BSRS";
		}else if (num==11){
			return "BTRS";
		}else if (num==12){ 
			return "BSSH";
		}else if (num==13){ 
			return "BTSH";
		}else if (num==14){ 
			return "BSSS";
		}else	
			return "BTSS";
	}
	public static int legal(String piece){ // checks the whether piece is valid
		
		 if(piece.equals("WSRH") || piece.equals("WTRH") || piece.equals("WSRS") || piece.equals("WTRS") || 
			piece.equals("WSSH") || piece.equals("WTSH") || piece.equals("WSSS") || piece.equals("WTSS") || 
		 	piece.equals("BSRH") || piece.equals("BTRH") || piece.equals("BSRS") || piece.equals("BTRS") ||
		 	piece.equals("BSSH") || piece.equals("BTSH") || piece.equals("BSSS") || piece.equals("BTSS")){
		
			 return 1;
		 }
		 return 0;
	}
	public static boolean winDiagonally(String [][] board){ //diagonal winning configuration
		
		for(int j=0;j<4;j++){
			
		if(board[0][0].length()!=1 && board[1][1].length()!=1 && board[2][2].length()!=1 && board[3][3].length()!=1){	
			if(board[0][0].charAt(j)==board[1][1].charAt(j) && board[0][0].charAt(j)==board[2][2].charAt(j) && board[0][0].charAt(j)==board[3][3].charAt(j)){
				
				return true;
			}
		}
		
		if(board[0][3].length()!=1 && board[1][2].length()!=1 && board[2][1].length()!=1 && board[3][0].length()!=1){
			if(board[0][3].charAt(j)==board[1][2].charAt(j) && board[0][3].charAt(j)==board[2][1].charAt(j) && board[0][3].charAt(j)==board[3][0].charAt(j)){
			
				return true;
			}
		}	
	}
		return false;
	}
	public static boolean winVertically(String [][] board){ // vertical winning configuration
		
        for(int i=0;i<4;i++){
			for(int j=0;j<4;j++){
				
			if((board[0][i].length()!=1 && board[1][i].length()!=1 && board[2][i].length()!=1 && board[3][i].length()!=1)){
				if(board[0][i].charAt(j)==board[1][i].charAt(j) && board[0][i].charAt(j)==board[2][i].charAt(j) && board[0][i].charAt(j)==board[3][i].charAt(j)){
				
					return true;
				}
			}
		}
	}	
		return false;
	}
	public static boolean winHorizontally(String [][] board){ // horizontal winning configuration
		
		for(int i=0;i<4;i++){
			for(int j=0;j<4;j++){
			
			if(board[i][0].length()!=1 && board[i][1].length()!=1 && board[i][2].length()!=1 && board[i][3].length()!=1)	{
				if(board[i][0].charAt(j)==board[i][1].charAt(j) && board[i][0].charAt(j)==board[i][2].charAt(j) && board[i][0].charAt(j)==board[i][3].charAt(j)){
					
					return true;
				}
			}
		}
	}	
		return false;
	}
	
	// checks the place is empty or full
	public static boolean empty(int i, int j, String [][] board){
		if(i<4 && j<4){
		if(board[i][j].equalsIgnoreCase("E")){
			
			return true;
			}
		}
		return false;
		
	}
	// checks whether the piece is already taken
	public static boolean sameAs(String [][] board,String piece){
		
		for(int i=0;i<4;i++){
			for(int j=0;j<4;j++){
				
				if(board[i][j].equals(piece)){
					return false;
				}
			}
		}
		return true;
	}
			
	// the process of the gamePlay
	public static void gamePlay(String [][] board,Random rand,Scanner console,PrintStream str){
		
		int count=0; // increases with the filled parts of the game board, if it reaches 16 there is no empty places on the board
		while(!(winDiagonally(board) || winVertically(board) || winHorizontally(board))){ // continues till the any of the winning configurations is consisted
			
		System.out.println("Please select a piece."); // user begins the game
		String piece=console.next();
		while(legal(piece)==0){
		System.out.println("This piece is not valid. Please select a valid one.");
			piece=console.next();
		}
		while(!(sameAs(board,piece))){
			System.out.println("This piece is already selected. Please select a different piece.");
			piece=console.next();
		}
		count++; // increase with filled parts of the game board
		System.out.println("Please enter the coordinates."); // computer places the piece which is chosen by user by entering the coordinates
		int i=rand.nextInt(4);
		int j=rand.nextInt(4);
		System.out.println(i + " " + j);
		while(!(empty(i,j, board))){
			System.out.println("These coordinates are not valid. Please enter the valid ones.");
			i=rand.nextInt(4);
			j=rand.nextInt(4);
			System.out.println(i + " " + j);
		}
		board[i][j]=piece;	// adds the chosen piece to the board
		printer(board,str); // updates the board
		if((winDiagonally(board) || winVertically(board) || winHorizontally(board))){
			
			System.out.println("Computer won!");

			break; // terminates the loop if a winning condition has occured
		
		}

		System.out.println("Please select a piece.");
		piece=piece(rand);
		System.out.println(piece);
		while(!(sameAs(board,piece))){
			System.out.println("This piece is not valid. Please select a valid one.");
			piece=piece(rand);
			System.out.println(piece);
		}
		count++;
		System.out.println("Please enter the coordinates."); // user places the piece which is chosen by computer by entering the coordinates
		i=console.nextInt();
		j=console.nextInt();
		while(!(empty(i, j, board))){
			System.out.println("These coordinates are not valid. Please enter the valid ones.");
			i=console.nextInt();
			j=console.nextInt();
		}
		board[i][j]=piece; // adds the chosen piece to the board
		printer(board,str); // updates the board
		if((winDiagonally(board) || winVertically(board) || winHorizontally(board))){
			
			System.out.println("User won!");

			break;

		}
		if(count==16){
			
			System.out.println("The game ended with a draw.");
			
			break;
		}
	}
	}
	// Computer selected the piece but the user has not placed it yet, now it is computer's turn. Computer chooses a new piece.
	// We can say this method is the opposite of the gamePlay method.
	public static void reverseGamePlay(String [][] board, Random rand, Scanner console, PrintStream str){
		int count=0;
		
		while(!(winDiagonally(board) || winVertically(board) || winHorizontally(board))){
			
			System.out.println("Please select a piece.");
			String piece=piece(rand);
			System.out.println(piece);
			while(!(sameAs(board,piece))){
				System.out.println("This piece is already selected. Please select a different piece.");
				piece=piece(rand);
				System.out.println(piece);
			}
			count++;
			System.out.println("Please enter the coordinates.");
			int i=console.nextInt();
			int j=console.nextInt();
			while(!(empty(i, j, board))){
				System.out.println("These coordinates are not valid. Please enter the valid ones.");
				i=console.nextInt();
				j=console.nextInt();
			}
			board[i][j]=piece;
			printer(board,str);
			if((winDiagonally(board) || winVertically(board) || winHorizontally(board))){
				
				System.out.println("User won!");

				break;
			}
			
			System.out.println("Please select a piece.");
			piece=console.next();
			while(!(sameAs(board,piece))){
				System.out.println("This piece is already selected. Please select a different piece.");
				piece=console.next();
			}
			count++;
			System.out.println("Please enter the coordinates.");
			i=rand.nextInt(4);
			j=rand.nextInt(4);
			System.out.println(i + " " + j);
			while(!(empty(i, j, board))){
				System.out.println("These coordinates are not valid. Please enter the valid ones.");
				i=rand.nextInt(4);
				j=rand.nextInt(4);
				System.out.println(i + " " + j);
			}
			board[i][j]=piece;
			printer(board,str);
			if((winDiagonally(board) || winVertically(board) || winHorizontally(board))){
				
				System.out.println("Computer won!");
	
				break;
			}
			if(count==16){
				
				System.out.println("The game ended with a draw.");

				break;
			}
		}
	}
}