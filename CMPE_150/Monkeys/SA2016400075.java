public class Assignment {

	public static void main(String[] args) {
		
	//	I created methods for each line.	
		
		firstline();
		secondline();
		thirdline();
		fourthline();
		fifthline();
		sixthline();
		seventhline();
		sentence();
	}
	
	//	I created a method by using parameters. This simplify my work.
	
	public static void line(int x, String a){
			
		for(int i=1; i<=x; i++){
			
			System.out.print(a);
		}
	}
	
	public static void hair(){	
		
	//	All the monkeys have the same pattern in first line!	
		
		line(1,".");
		line(1,"-");
		line(1,"\"");
		line(1,"-");
		line(1,".");
	}
	
	public static void hair2(){
		
	// 2.,3. and 4. monkeys has same pattern in second line!
		
		line(1,"_");
		line(1,"/");
		line(1,".");
		line(1,"-");
		line(1,".");
		line(1,"-");		
		line(1,".");		
		line(1,"\\");		
		line(1,"_");
	}
	
	public static void eyes(int x){
		
	// 3. and 4. monkeys have same patter in third line!		
		
		for(int i=1; i<=2; i++){
		
		line(5," ");
		line(1,"(");
		line(1," ");
		line(1,"(");
		line(1," ");
		line(1,"o");
		line(1," ");
		line(1,"o");
		line(1," ");
		line(1,")");
		line(1," ");
		line(1,")");
	}	
	} 
	
	public static void nose(){
		
	//	1. and 2. monkeys have the same nose in fourth line!	
		
		line(1," ");
		line(2,"/");
		line(2," ");
		line(1,"\"");
		line(2," ");
		line(2,"\\");
		line(1," ");
	}
	
	public static void nose2(){
		
	//	3. and 4. monkeys have the same patter in fourth line!
		
		line(1,"|");
		line(1,"/");
		line(2," ");
		line(1,"\"");
		line(2," ");
		line(1,"\\");
		line(1,"|");
	}
	
	// 1. and 2. monkeys have the same pattern in fifth and sixth lines thus I created the next 2 methods!

	public static void mouth(){
		
		line(1,"/");
		line(1," ");
		line(1,"/");
		line(1," ");
		line(1,"\\");
		line(1,"'");
		line(3,"-");
		line(1,"'");
		line(1,"/");
		line(1," ");
		line(1,"\\");
		line(1," ");
		line(1,"\\");
	}
	
	public static void chin(){
		
		line(1,"\\");
		line(1," ");
		line(1,"\\");
		line(1,"_");
		line(1,"/");
		line(1,"`");
		line(3,"\"");
		line(1,"`");
		line(1,"\\");
		line(1,"_");
		line(1,"/");
		line(1," ");
		line(1,"/");
	}
	
	public static void firstline(){
		
		line(7," ");
		hair();
		line(12," ");
		hair();
		line(12," ");
		hair();
		line(11," ");
		hair();
		System.out.println();
	}
	
	public static void secondline(){
		
		line(5," ");
		line(1,"_");
		line(1,"/");
		line(1,"_");
		line(1,"-");
		line(1,".");
		line(1,"-");
		line(1,"_");
		line(1,"\\");
		line(1,"_");
		line(8," ");
		hair2();
		line(8," ");
		hair2();
		line(7," ");
		hair2();
		System.out.println();
	}
	
	public static void thirdline(){
		
		line(4," ");
		line(1,"/");
		line(1," ");
		line(2,"_");
		line(1,"}");
		line(1," ");
		line(1,"{");
		line(2,"_");
		line(1," ");
		line(1,"\\");
		line(6," ");
		line(1,"/");
		line(1,"|");
		line(1,"(");
		line(1," ");
		line(1,"o");
		line(1," ");
		line(1,"o");
		line(1," ");
		line(1,")");
		line(1,"|");
		line(1,"\\");
		line(1," ");
		eyes(2);
		System.out.println();
	}
	
	public static void fourthline(){
		
		line(3," ");
		line(1,"/");
		nose();
		line(1,"\\");
		line(4," ");
		line(1,"|");
		nose();
		line(1,"|");
		line(6," ");
		nose2();
		line(7," ");
		nose2();
		System.out.println();
	}
	
	public static void fifthline(){
		
		line(2," ");
		mouth();
		line(2," ");
		mouth();
		line(6," ");
		line(1,"\\");
		line(1,"'");
		line(1,"/");
		line(1,"^");
		line(1,"\\");
		line(1,"'");
		line(1,"/");
		line(9," ");
		line(1,"\\");
		line(1," ");
		line(1,".");
		line(1,"-");
		line(1,".");
		line(1," ");
		line(1,"/\n");
	}
	
	public static void sixthline(){
		
		line(2," ");
		chin();
		line(2," ");
		chin();
		line(6," ");
		line(1,"/");
		line(1,"`");
		line(1,"\\");
		line(1," ");
		line(1,"/");
		line(1,"`");
		line(1,"\\");
		line(9," ");
		line(1,"/");
		line(1,"`");
		line(3,"\"");
		line(1,"`");
		line(1,"\\");
		System.out.println();
	}
		
	public static void seventhline(){
		
		line(3," ");
		line(1,"\\");
		line(11," ");
		line(1,"/");
		line(4," ");
		line(1,"\\");
		line(11," ");
		line(1,"/");
		line(6," ");
		line(1,"/");
		line(2," ");
		line(1,"/");
		line(1,"|");
		line(1,"\\");
		line(2," ");
		line(1,"\\");
		line(7," ");
		line(1,"/");
		line(7," ");
		line(1,"\\");
		System.out.println();
	}
	
	public static void sentence(){
		
		System.out.println("\n-={ see no evil }={ hear no evil }={ speak no evil }={ have no fun }=-");
		
	}
}
	
	
	
	
	
	
	
		
		
		
		
	
		
	
	
	




