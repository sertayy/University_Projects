# A Document Retrieval System with Trie and Inverted Index
In this project I implemented a document retrieval system for single word queries and wildcard queries using the inverted indexing scheme and a trie data structure. 
# Notes
- This project developed in a Windows 8 machine using Python 3.8.
- All the libraries used in this projects are python standard libraries, that's why there is no need for requirements.txt.
# How It Works?
- The output will be printed on the console each time you typed an input. 
- If the input query found, the sorted IDs of the matching documents will be printed on the console with an ascending order.
- If not found, an error message will be displayed.
- The query processor works unless you typed "quit".
- The valid inputs are single-word keyword and prefix* such as turkey and tur*.
##  Execution
Execute the command mentioned below inside the project folder to prepare the trie and the inverted index.
```
python prep.py
```
Then, execute the command mentioned below inside the project folder to run the query processor.
```
python query.py
```
