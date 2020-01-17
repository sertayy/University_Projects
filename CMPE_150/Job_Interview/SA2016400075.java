import java.util.Scanner;
public class SA2016400075{
public static void main(String[] args) {
			Scanner console = new Scanner(System.in);
			System.out.println("    Welcome to MARS Interviewing System");
			String name = question_1(console); // question_1 returns applicant's name
			int age = question_2(console, name); //question_1 returns applicant's age
			if (age < 18) { // checking for age criterion
				System.out.println("Sorry " + name + ". You should be 18 or older for this job.");
			}
			else { // to start a specific interview for each job
				int job = question_3(console); // job return 0 for wrong job applications and 1, 2 or 3 for available jobs.
				if (job == 0) {
					System.out.println("Sorry, we are looking for software engineer, accountant or academic.");
				}
				else if (job == 1) {
					softwareEngineer(console, name);
				}
				else if (job == 2) {
					accountant(console, name);
				}
				else if (job == 3) {
					academic(console, name);
				}
			}
		}
		// first question for applicant's name
		public static String question_1(Scanner console) {
			System.out.print("Can I learn your name? ");
			String name = console.nextLine();
			return name;
		}
		// second question for applicant's age
		public static int question_2(Scanner console, String name) {
			System.out.print("Hello " + name + ". How old are you? ");
			int age = console.nextInt();
			return age;
		}
		// third question for determining the position 
		public static int question_3(Scanner console) {
			System.out.print("For which position are you applying? ");
			console.nextLine();
			String job = console.nextLine();
			if (job.equalsIgnoreCase("Software Engineer")) {
				return 1;
			}
			else if (job.equalsIgnoreCase("Accountant")) {
				return 2;
			}
			else if(job.equalsIgnoreCase("Academic")) {
				return 3;
			}
			else {
				return 0;
			}
		}
		// This method consists of the questions which are asked to a software engineer applicant, 
		// if the applicant is unsatisfying it returns "sorry" message and 0, otherwise it returns "congratulations" message and 1.
		public static int softwareEngineer(Scanner console, String name) {
			String degree = "";
			while (!(degree.equalsIgnoreCase("yes") || degree.equalsIgnoreCase("no"))) { // Questions repeat itself until the wanted input(yes or no) is entered
			System.out.print("Great. Do you have a university degree? ");
			degree = console.nextLine();
			}
			if (degree.equalsIgnoreCase("no")) {	// if statements are for determining the process of the interview.
				System.out.print("Sorry " + name + ". You should have a university degree for this job.");
				return 0;
			}
			String field = "";
			System.out.print("In which field? ");
			field = console.nextLine();
			if (!(field.equalsIgnoreCase("Software engineering") || field.equalsIgnoreCase("computer science") || field.equalsIgnoreCase("computer engineering"))) {
				System.out.print("Sorry " + name + ". You should have a software engineering, computer science or computer engineering degree for this job.");
				return 0;
			}
			int count = 0; // number of programming languages
			String java = "";
			while (!(java.equalsIgnoreCase("yes") || java.equalsIgnoreCase("no"))) {
			System.out.print("Do you know how to program in Java? ");
			java = console.nextLine();
			}
			if (java.equalsIgnoreCase("yes")) {
				count++;
			}
			String C = "";
			while (!(C.equalsIgnoreCase("yes") || C.equalsIgnoreCase("no"))) {
			System.out.print("Do you know how to program in C? ");
			C = console.nextLine();
			}
			if (C.equalsIgnoreCase("yes")) {
				count++;
			}
			String Prolog = "";
			while (!(Prolog.equalsIgnoreCase("yes") || Prolog.equalsIgnoreCase("no"))) {
			System.out.print("Do you know how to program in Prolog? ");
			Prolog = console.nextLine();
			}
			if (Prolog.equalsIgnoreCase("yes")) {
				count++;
			}
			if (count < 2) { // It checks the number of programming languages 
				System.out.print("Sorry " + name + ". This position is eligible for only the people who knows at least 2 programming languages.");
				return 0;
			}
			String work = "";
			while (!(work.equalsIgnoreCase("yes") || work.equalsIgnoreCase("no"))) {
			System.out.print("Awesome. Have you worked as a software engineer before? ");
			work = console.nextLine();
			}
			if (!work.equalsIgnoreCase("yes")) {
				if (question_4(console, name) == 0) { // for learning whether if the applicant have a graduate degree or not
				return 0;
				}
			}
			else if (work.equalsIgnoreCase("yes")) {
				System.out.print("How many years have your worked? ");
				int years = console.nextInt();
				if (years < 4) {
					if (question_4(console, name) == 0) { // for learning whether if the applicant have a graduate degree or not
					return 0;
					}
				}
			}
			if (male(console, name) == 1) { // It checks the gender and the military service. Male method is in the end of the program.
			System.out.print("Congratulations " + name + "! You got the job!");
				return 1;
			}
			else {
				return 0;
			}
		}
		//checks for the graduate degree of software engineer applicants
		public static int question_4(Scanner console, String name) { 
			String graduate_degree = "";
			while (!(graduate_degree.equalsIgnoreCase("yes") || graduate_degree.equalsIgnoreCase("no"))) {
			System.out.print("Do you have a graduate degree in software engineering? ");
			graduate_degree = console.nextLine();
			}
			if (!graduate_degree.equalsIgnoreCase("yes")) {
				System.out.print("Sorry " + name + ". You should have either more than three years of experience or graduate degree in software engineering for this job.");
				return 0;
			}
			return 1;
		}
		// This method consists of the questions which are asked to an accountant applicant, 
		// if the applicant is unsatisfying it returns "sorry" message and 0, otherwise it returns "congratulations" message and 1.
		public static int accountant(Scanner console, String name) {
			String degree = "";
			while (!(degree.equalsIgnoreCase("yes") || degree.equalsIgnoreCase("no"))) {
			System.out.print("Do you have an accounting degree? ");
			degree = console.nextLine();
			}
			if (!degree.equalsIgnoreCase("yes")) {
				System.out.println("Sorry " + name + ". You should have an accounting degree for this job.");
				return 0;
			}
			String excel = "";
			while (!(excel.equalsIgnoreCase("yes") || excel.equalsIgnoreCase("no"))) {
			System.out.print("Do you know Excel? ");
			excel = console.nextLine();
			}
			if (!excel.equalsIgnoreCase("yes")) {
				System.out.println("Sorry " + name + ". You should know Excel for this job.");
				return 0;
			}
			String english = "";
			while (!(english.equalsIgnoreCase("yes") || english.equalsIgnoreCase("no"))) {
			System.out.print("Do you speak English fluently? ");
			english = console.nextLine();
			}
			if (!english.equalsIgnoreCase("yes")) {
				String friend = "";
				while (!(friend.equalsIgnoreCase("yes") || friend.equalsIgnoreCase("no"))) {
				System.out.print("Do you have a friend who can translate for you? ");
				friend = console.nextLine();
				}
				if (!friend.equalsIgnoreCase("yes")) {
					System.out.println("Sorry " + name + ". You should speak English fluently or have a friend who can translate for you for this job.");
					return 0;
				}
			}
			System.out.print("How many people do you know who already works in our company? ");
			int people = console.nextInt();
			if (people < 2) { // It checks the number of people
				System.out.println("Sorry " + name + ". You should know at least two people who already works in our company for this job.");
				return 0;
			}
			String license = "";
			while (!(license.equalsIgnoreCase("yes") || license.equalsIgnoreCase("no"))) {
			System.out.print("Do you have a driving license? ");
			license = console.next();
			}
			if (!license.equalsIgnoreCase("yes")) {
				System.out.println("Sorry " + name + ". You should have a driving license for this job.");
				return 0;
			}
			if (male(console, name) == 1) { // It checks the gender and the military service
				System.out.print("Congratulations " + name + "! You got the job!");
				return 1;
				}
				else {
					return 0;
				}
		}
		// This method consists of the questions which are asked to an academic applicant, 
	    // if the applicant is unsatisfying it returns "sorry" message and 0, otherwise it returns "congratulations" message and 1.
		public static int academic(Scanner console, String name) {
			String english = "";
			while (!(english.equalsIgnoreCase("yes") || english.equalsIgnoreCase("no"))) {
			System.out.print("Do you speak English? ");
			english = console.nextLine();
			}
			if (!english.equalsIgnoreCase("yes")) {
				System.out.println("Sorry " + name + ". You should speak Egnlish for this job.");
				return 0;
			}
			System.out.print("How many papers have you published? ");
			int paper = console.nextInt();
			if (paper < 3) {
				System.out.println("Sorry " + name + ". You should have published at least 3 papers for this job.");
				return 0;
			}
			String teach = "";
			while (!(teach.equalsIgnoreCase("yes") || teach.equalsIgnoreCase("no"))) {
			System.out.print("Do you love to teach? ");
			teach = console.next();
			}
			if (!teach.equalsIgnoreCase("yes")) {
				System.out.println("Sorry " + name + ". You should love to teach for this job.");
				return 0;
			}
			if (male(console, name) == 1) {// It checks the gender and the military service.
				System.out.print("Congratulations " + name + "! You got the job!");
				return 1;
				}
				else {
					return 0;
				}	
		}
		// It checks if the applicant's gender is male and if so whether he has completed his military service or not.
		public static int male(Scanner console, String name) {
			String gender = "";
			while (!gender.equalsIgnoreCase("yes") && !gender.equalsIgnoreCase("no")) {
			System.out.print("Are you a male? ");
			gender = console.next();
			}
			if (gender.equalsIgnoreCase("yes")) {
				String military = "";
				while (!military.equalsIgnoreCase("yes") && !military.equalsIgnoreCase("no")) {
				System.out.print("Have you completed your military service? ");
				military = console.next();
				}
				if (!military.equalsIgnoreCase("yes")) {
					System.out.print("Sorry " + name + ". You should have completed your military service for this job.");
					return 0;
				}
			}
			return 1;
		}
	}