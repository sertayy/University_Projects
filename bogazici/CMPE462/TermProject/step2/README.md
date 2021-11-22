# CMPE 462 - Term Project - Step 2

**Group Name:** NoName

**Group Members**

Halil Umut ÖZDEMİR - 2016400168

Halil İbrahim ORHAN - 2016400054

Sertay AKPINAR - 2016400075

## Code Files

`462project_step2_NoName.py`: The Script that takes the pre-trained model and the Test set file as input and prints the predictions as output.

To run this script:

> python3 462project_step2_NoName.py step2_model_NoName.pkl \<Test Set Path\>

`step2_model_NoName.pkl`: Pre-Trained Model File

`preprocessing.py`: In this file the followings are implemented:

    1. Cleaning the Data
    2. Feature Extraction (BOW, TF-IDF)
    3. Feature Selection (Chi Squared - Mutual Information - ANOVA-F)
    4. Feature Extraction for NBSVM (Our Best Model)

`data_analysis.py`: This is the code that generates the analysis plots on our report

To run this script:

> python3 data_analysis.py <plot_type>

plot_type:

    1 => Number of Words in Title for Each Class
    2 => Number of Words in Body for Each Class
    3 => Number of Characters in Title for Each Class
    4 => Number of Characters in Body for Each Class
    feature_selection => Knee Plots in Feature Selection Part

`train_model_trials.py`: This Script trains and prints the performance metrics for the models other than our best model NVSVM. In this script hyper parameters are selected after fine-tuning.

    IMPORTANT NOTE: The run time of this script is high

To run this script:

> python3 train_model_trials.py

`tune_hyperparameters.py`: This script finds best parameters for Random Forest and SVM.

    IMPORTANT NOTE: The run time of this script is high

To run this script:

> python3 tune_hyperparameters.py

`main_model.py`: This script trains our best model which is NBSVM. As a result it creates the pickle file which stores the pretrained model.

    IMPORTANT NOTE: The NBSVM implementation is taken from https://github.com/prakhar-agarwal/Naive-Bayes-SVM

    IMPORTANT NOTE: The run time of this script is high

To run this script:

> python3 tune_hyperparameters.py