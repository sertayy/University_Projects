# Adversarial Search
In this project, I implemented adversarial search in sliding puzzles.
# Notes
- This project developed in a macOS BigSur v11.3 using Python 3.9
- All the libraries used in this projects are python standard libraries, that's why there is no need for requirements.txt
- The output file will be created in the output folder
- The project description can be found in description.pdf
##  Execution
Format:
```
python search.py <init-file> <goal-file> <n-actions> <sln-file>
```
Example:
```
python search.py alpha_beta_pruning init_1.txt goal_1.txt 2 soln_1_2_ab.txt
```