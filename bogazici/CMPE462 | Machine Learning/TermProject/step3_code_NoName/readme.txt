# CMPE 462 - Term Project - Step 3

**Group Name:** NoName

**Group Members**

Halil Umut ÖZDEMİR - 2016400168

Halil İbrahim ORHAN - 2016400054

Sertay AKPINAR - 2016400075

## Code Files

`462project_step3_NoName.py`: The Script that takes the pre-trained model and the Test set file as input and prints the predictions as output.

To run this script:

> python3 462project_step3_NoName.py step3_model_NoName.pkl \<Test Set Path\>

`step3_model_NoName.pkl`: Pre-Trained Model File

`preprocessing.py`: In this file the followings are implemented:

    1. Cleaning the Data
    2. Feature Extraction (BOW)
    3. Feature Selection 

`NBSVM.py`: This is the implementation of NBSVM class that we used in feature extraction

    IMPORTANT NOTE: The NBSVM implementation is taken from https://github.com/prakhar-agarwal/Naive-Bayes-SVM

`feature_engineering.py`: This script run all features we tried with XGBoost.

    IMPORTANT NOTE: The run time of this script is high

To run this script:

> python3 feature_engineering.py

`main_model_training.py`: This script trains our best model which is XGBoost. As a result it creates the pickle file which stores the pretrained model.

    IMPORTANT NOTE: The run time of this script is high

To run this script:

> python3 main_model_training.py

`svm_training.py`: This script trains SVM model for.

    IMPORTANT NOTE: The run time of this script is high

To run this script:

> python3 svm_training.py

`random_forest_training.py`: This script trains Random Forest model.

    IMPORTANT NOTE: The run time of this script is high

To run this script:

> python3 random_forest_training.py

`lightgbm_training.py`: This script trains LightGBM model.

    IMPORTANT NOTE: The run time of this script is high

To run this script:

> python3 lightgbm_training.py