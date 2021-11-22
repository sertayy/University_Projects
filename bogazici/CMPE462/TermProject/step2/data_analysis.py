"""
    This Script Generates the Plots in DAta Analysis Section of the Project Report
    Also Creates the Feature Selection Analysis in Project Report
"""
from preprocessing import read_data, convert_to_df, calculate_bow, calculate_tf_idf, encode_target_classes
from sklearn.feature_selection import chi2, mutual_info_classif, f_classif
from kneed import KneeLocator
import matplotlib.pyplot as plt
import sys


def calculate_plot_data(train_df):
    """
        Calculates number of words and characters inside all text files
    """
    # Plot Average Number of Words for each class
    plot_data = {"title_words": [], "body_words": [], "title_chars": [], "body_chars": []}
    for class_tag in ["P", "Z", "N"]:
        plot_data["title_words"].append(train_df[train_df["class"] == class_tag]["title"].str.split().str.len())
        plot_data["body_words"].append(train_df[train_df["class"] == class_tag]["body"].str.split().str.len())
        plot_data["title_chars"].append(train_df[train_df["class"] == class_tag]["title"].str.len())
        plot_data["body_chars"].append(train_df[train_df["class"] == class_tag]["body"].str.len())

    return plot_data


if __name__ == "__main__":

    train_path = "TRAIN"
    val_path = "VAL"

    # Read the Data
    train_data, val_data = read_data(train_path, val_path)
    # Convert it to DataFrame
    train_df, val_df = convert_to_df(train_data, val_data)
    # Calculate Plot Data
    plot_data = calculate_plot_data(train_df)

    if sys.argv[1] == "1":

        ###################################
        # Plot Number of Words in Title for Each Class
        plt.figure(figsize=(10, 10))
        plt.title("Number of Words in Title for Each Class")
        plt.boxplot(plot_data["title_words"], showfliers=False)
        plt.xticks([1, 2, 3], ("P", "Z", "N"))
        plt.show()

    elif sys.argv[1] == "2":

        ###################################
        # Plot Number of Words in Body for Each Class
        plt.figure(figsize=(10, 10))
        plt.title("Number of Words in Body for Each Class")
        plt.boxplot(plot_data["body_words"], showfliers=False)
        plt.xticks([1, 2, 3], ("P", "Z", "N"))
        plt.show()

    elif sys.argv[1] == "3":

        ###################################
        # Plot Number of Characters in Title for Each Class
        plt.figure(figsize=(10, 10))
        plt.title("Number of Characters in Title for Each Class")
        plt.boxplot(plot_data["title_chars"], showfliers=False)
        plt.xticks([1, 2, 3], ("P", "Z", "N"))
        plt.show()

    elif sys.argv[1] == "4":

        ###################################
        # Plot Number of Characters in Body for Each Class
        plt.figure(figsize=(10, 10))
        plt.title("Number of Characters in Body for Each Class")
        plt.boxplot(plot_data["body_chars"], showfliers=False)
        plt.xticks([1, 2, 3], ("P", "Z", "N"))
        plt.show()

    elif sys.argv[1] == "feature_selection":

        # Calculate Features
        train_tf_idf, val_tf_idf = calculate_tf_idf(train_df, val_df)
        train_bow, val_bow = calculate_bow(train_df, val_df)
        y_train, y_val = encode_target_classes(train_df, val_df)

        # Select the Feature Set
        feature_set = train_bow

        ###################################
        # Chi Squared Feature Selection
        chi2_scores, _ = chi2(feature_set, y_train)
        chi2_kneedle = KneeLocator([i for i in range(len(chi2_scores))], sorted(chi2_scores), S=1.0, curve="convex",
                                   direction="increasing")
        print("Number of Selected Features: {} | Chi Squared Threshold: {}".format(len(chi2_scores) - chi2_kneedle.knee,
                                                                                   chi2_kneedle.knee_y))
        chi2_kneedle.plot_knee()
        plt.show()

        ###################################
        # Apply Mutual Information Test
        mutlual_info = mutual_info_classif(feature_set, y_train)
        mi_kneedle = KneeLocator([i for i in range(len(mutlual_info))], sorted(mutlual_info), S=1.0, curve="convex",
                                 direction="increasing")
        print("Number of Selected Features: {} | Mutual Info Threshold: {}".format(len(mutlual_info) - mi_kneedle.knee,
                                                                                   mi_kneedle.knee_y))
        mi_kneedle.plot_knee()
        plt.show()

        ###################################
        f_scores, _ = f_classif(feature_set.toarray(), y_train)
        fs_kneedle = KneeLocator([i for i in range(len(f_scores))], sorted(f_scores), S=1.0, curve="convex",
                                 direction="increasing")
        print("Number of Selected Features: {} | F Score Threshold: {}".format(len(f_scores) - fs_kneedle.knee,
                                                                               fs_kneedle.knee_y))
        fs_kneedle.plot_knee()
        plt.show()

    else:
        print("Please Give 1,2,3,4 or feature_selection as argument to select the plot type")
