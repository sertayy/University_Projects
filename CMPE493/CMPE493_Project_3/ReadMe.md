# Book Recommendation System
In this project, I implemented a simple book recommendation system from scratch.
# Notes
- This project developed in a MacOs 11.1 machine using Python 3.8.
- All the libraries used in this projects are python standard libraries, that's why there is no need for "requirements.txt".
- The "stop_word.txt" file and "books.txt" file should be located under the ".input" directory.
- "stop_word.txt" file is the same file as in the Cmpe493 Assignment 2.
- "books.txt" file is the input file which included the book urls of goodreads.com.
- Even though some of urls in the "book.txt" are broken, the program extract the book by adding "/en/" to the links. 
- The "alpha" value in the simularity equation is defined as **0.75**. (Explanation can be found in the report.)
- **The program should take a string URL as input.**
# How It Works?
- Book contents of input url will be extracted to a file called "book_content.txt" under the ".output" folder.
- If the input book is not already registered in the system, the program adds it to the book dictionary. So you don't have to choose a url in "book.txt".
- The program recommends 18 books according to the input book, book title-author pairs are printed on the command line as a recommendation. 
- Precision and average precision scores of the recommendations are also printed on the command line. <br />
**Important:** If you recieve "No matches founded for the value of alpha 0.65." signal, this means there is no matches founded for the current input url. You can a try different url to see the precision and the average precision values.
##  Execution
Execute the command mentioned below inside the project folder to run the system.
```
python main.py "good_reads_url_of_the_book"
```
**For example:**<br />
python deneme.py https://www.goodreads.com/book/show/29946.Illusions