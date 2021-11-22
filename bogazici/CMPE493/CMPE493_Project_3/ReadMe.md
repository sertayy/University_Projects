# Book Recommendation System
In this project, I implemented a simple book recommendation system.
# Notes
- This project developed in a MacOs 11.1 machine using Python 3.8.
- All the libraries used in this projects are python standard libraries, that's why there is no need for "requirements.txt".
- The "stop_word.txt" is the same file as in the Cmpe493 Assignment 2 and **it should be located under the ".input" directory.**
- If the output is "No matches found...", this means there is no matches founded for the current input url. You can a try different url to see the precision and the average precision values.
- If the input is a file path, the program creates the model and saves it.
- If the input is a book url, the program recommends 18 books according to query url, book title-author pairs are printed on the command line as recommendations with average precision and precision values. 
- Models and book contents will be saved under the ".output" folder, after execution. 
- Token model file is named as "token_model.pickle", genre model file is named as "genre_model.pickle", and the book content file is named as "book_content.txt".
- "book_dict.pickle" file saves the necessary information of the urls such as author_list, title, genres etc.
#  Execution
To run the system successfully, execute the commands mentioned bellowed inside the project folder respectively.
1.   ```
     python main.py "file_path"
     ```
     This saves the model and extracts the contents of the books of the given url.<br />
     **For example:**<br />
     ```
     python main.py /Users/apple/Documents/GitHub/SchoolProjects/CMPE493/CMPE493_Project_3/input/books.txt
     ```
     **Sample Output:**
     ```
     (INFO) Model will be created...
     (INFO) Model saved in the output folder.
2.   ```
     python main.py "book_url"
     ```
     This extracts the content of the given book and outputs recommendations with the precision values.<br />
     **For example:**<br />
     ```
     python main.py https://www.goodreads.com/book/show/29946.Illusions
     ```
     **Sample Output:**
     ```
     (INFO) Query url: "https://www.goodreads.com/book/show/29946.Illusions" is found in the dictionary!
     Recommended title-author pairs are:
     Title: The Prophet | Authors: 'Kahlil Gibran'
     Title: The Alchemist | Authors: 'Paulo Coelho', 'Alan R. Clarke', 'James Noel Smith'
     Title: Jonathan Livingston Seagull | Authors: 'Richard Bach', 'Russell Munson'
     Title: The Celestine Prophecy | Authors: 'James Redfield'
     Title: The Untethered Soul: The Journey Beyond Yourself | Authors: 'Michael A. Singer'
     Title: The Four Agreements: A Practical Guide to Personal Freedom | Authors: 'Miguel Ruiz'
     Title: The Mastery of Self: A Toltec Guide to Personal Freedom | Authors: 'Miguel Ruiz Jr.'
     Title: Practicing the Power of Now: Essential Teachings, Meditations, and Exercises from the Power of Now | Authors: 'Eckhart Tolle'
     Title: The Seven Spiritual Laws of Success: A Practical Guide to the Fulfillment of Your Dreams | Authors: 'Deepak Chopra'
     Title: Sacred Journey of the Peaceful Warrior | Authors: 'Dan Millman'
     Title: The Seat of the Soul | Authors: 'Gary Zukav'
     Title: Way of the Peaceful Warrior: A Book That Changes Lives | Authors: 'Dan Millman'
     Title: The Power of Positive Thinking | Authors: 'Norman Vincent Peale'
     Title: A Course in Miracles | Authors: 'Foundation for Inner Peace', 'Helen Schucman'
     Title: Conversations with God: An Uncommon Dialogue, Book 1 | Authors: 'Neale Donald Walsch'
     Title: The Power of Now: A Guide to Spiritual Enlightenment | Authors: 'Eckhart Tolle'
     Title: The Road Less Traveled: A New Psychology of Love, Traditional Values and Spiritual Growth | Authors: 'M. Scott Peck'
     Title: The Art of Happiness | Authors: 'Dalai Lama XIV', 'Howard C. Cutler'
     4 matches are found!
     AVG PRECISION: 0.53
     PRECISION: 0.22
     ```