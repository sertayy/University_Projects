"""
    In this Script we trained the last version of our model
    Accuracy, classification report and confusion matrix are reported
"""
from preprocessing import read_data, convert_to_df, calculate_bow, encode_target_classes, nb_svm_features, preprocessing

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sn
import pandas as pd
import numpy as np

from NBSVM import NBSVM
from sklearn.feature_selection import f_classif, SelectPercentile
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

import pickle

def plot_confusion_matrix(confusion_matrix_train,confusion_matrix_val):
    plt.figure(figsize=(14, 6))

    plt.subplot(1,2,1)

    df_cm = pd.DataFrame(confusion_matrix_train.T, index=[i for i in "NZP"],
                            columns=[i for i in "NZP"])
    sn.heatmap(df_cm, annot=True, fmt='g')
    plt.xlabel("true class")
    plt.ylabel("predicted class")

    plt.subplot(1,2,2)

    df_cm = pd.DataFrame(confusion_matrix_val.T, index=[i for i in "NZP"],
                            columns=[i for i in "NZP"])
    sn.heatmap(df_cm, annot=True, fmt='g')
    plt.xlabel("true class")
    plt.ylabel("predicted class")
    plt.plot()

if __name__ == "__main__":

    train_path = "TRAIN"
    val_path = "VAL"

    # Read the Data
    train_data,val_data = read_data(train_path,val_path)
    # Convert it to DataFrame
    train_df,val_df = convert_to_df(train_data,val_data)
    # Preprocess the Data
    train_df,val_df, sentence_embedding = preprocessing(train_df,val_df,training=True)

    final_model = {"sentence_embedding":sentence_embedding}

    # Calculate Train and Validation Features
    train_bow, val_bow, bow_title, bow_body = calculate_bow(train_df,val_df)
    y_train, y_val = encode_target_classes(train_df,val_df)

    final_model["class_map"] = {2:"P",1:"Z",0:"N"}
    final_model["bow_title"] = bow_title
    final_model["bow_body"] = bow_body
    
    # Calculate NBSVM Features
    X_train, X_val, x_train_mean = nb_svm_features(train_bow,val_bow,train_df,val_df)

    final_model["x_train_mean"] = x_train_mean

    # Apply Feature Selection with ANOVA-F
    feature_sel = SelectPercentile(f_classif, percentile=95)
    X_train_fs = feature_sel.fit_transform(X_train,y_train)
    X_val_fs = feature_sel.transform(X_val)

    final_model["feature_sel_nbsvm"] = feature_sel

    # NBSVM Model
    nbsvm = NBSVM(
        alpha = 1,
        C = 0.0003,
        beta = 0.1,
        fit_intercept = True,
        max_iter = 100000,
        tol = 1e-2,
        intercept_scaling = 1.5, 
        class_weights = {0:"balanced",1:"balanced",2:"balanced"},
        dual = True
    )
    # Train the Model
    nbsvm.fit(X_train_fs,y_train)

    final_model["nbsvm"] = nbsvm

    print(f"Train Accuracy Score: {accuracy_score(y_train,nbsvm.predict(X_train_fs))}")
    print(f"Validation Accuracy Score: {accuracy_score(y_val,nbsvm.predict(X_val_fs))}")

    print("Train Report:\n",classification_report(y_train,nbsvm.predict(X_train_fs)))
    print("Validation Report:\n",classification_report(y_val,nbsvm.predict(X_val_fs)))

    plot_confusion_matrix(confusion_matrix(y_train,nbsvm.predict(X_train_fs)),confusion_matrix(y_val,nbsvm.predict(X_val_fs)))
    plt.show()

    ###################################
    # Add Sentence Embeddings to Model
    train_df["sentence_embeddings_mean"] = train_df["sentence_embeddings"].apply(lambda x: np.mean(x,axis = 0))
    val_df["sentence_embeddings_mean"] = val_df["sentence_embeddings"].apply(lambda x: np.mean(x,axis = 0))

    # FEatures from previous model
    X_train_new_ = nbsvm.decision_function(X_train_fs)
    X_train_new_ = np.hstack((
        X_train_new_,
        np.vstack((X_train_new_[:,0] - X_train_new_[:,1], X_train_new_[:,0] - X_train_new_[:,2], X_train_new_[:,1] - X_train_new_[:,2])).T,
    ))

    X_val_new_ = nbsvm.decision_function(X_val_fs)
    X_val_new_ = np.hstack((
        X_val_new_,
        np.vstack((X_val_new_[:,0] - X_val_new_[:,1], X_val_new_[:,0] - X_val_new_[:,2], X_val_new_[:,1] - X_val_new_[:,2])).T,
    ))

    scaler = StandardScaler()
    X_train_new_ = scaler.fit_transform(X_train_new_)
    X_val_new_ = scaler.transform(X_val_new_)

    final_model["scaler"] = scaler

    # Apply LDA to Sentence Embeddings
    lf_te = LinearDiscriminantAnalysis()
    lf_te.fit(np.array(list(train_df["sentence_embeddings_mean"])),y_train)
    
    final_model["lf_te"] = lf_te

    # Apply LDA to Title Embeddings
    lf_t = LinearDiscriminantAnalysis()
    lf_t.fit(np.array(list(train_df["title_embeddings"])),y_train)

    final_model["lf_t"] = lf_t

    # Apple ANOVA-F Feature Selection to Title Embeddings
    feature_sel_embed_t = SelectPercentile(f_classif, percentile=50)
    feature_sel_embed_t.fit(np.array(list(train_df["title_embeddings"])),y_train)
    # Apply PCA to remaining features
    title_pca = PCA(n_components = 3)
    title_scaler = StandardScaler()

    title_pca.fit(title_scaler.fit_transform(feature_sel_embed_t.transform(np.array(list(train_df["title_embeddings"])))))

    final_model["feature_sel_embed_t"] = feature_sel_embed_t
    final_model["title_pca"] = title_pca
    final_model["title_scaler"] = title_scaler

    # Apply Feature Selection to sentence embeddings
    feature_sel_embed_sen_t = SelectPercentile(f_classif, percentile=10)
    feature_sel_embed_sen_t.fit(np.array(list(train_df["sentence_embeddings_mean"])),y_train)

    final_model["feature_sel_embed_sen_t"] = feature_sel_embed_sen_t

    ######################################
    # Calculate new features by KMeans
    # Title Embeddings
    pos_title_embed = np.array(list(train_df[train_df["class"] == "P"]["title_embeddings"]))
    net_title_embed = np.array(list(train_df[train_df["class"] == "Z"]["title_embeddings"]))
    neg_title_embed = np.array(list(train_df[train_df["class"] == "N"]["title_embeddings"]))

    pos_clustering_title = KMeans(n_clusters=3,random_state = 2250)
    neg_clustering_title = KMeans(n_clusters=3,random_state = 2250)
    net_clustering_title = KMeans(n_clusters=3,random_state = 2250)

    pos_cluster_title = pos_clustering_title.fit(pos_title_embed)
    neg_cluster_title = neg_clustering_title.fit(neg_title_embed)
    net_cluster_title = net_clustering_title.fit(net_title_embed)

    pos_center_title = pos_cluster_title.cluster_centers_
    neg_center_title = neg_cluster_title.cluster_centers_
    net_center_title = net_cluster_title.cluster_centers_

    pos_cos_sim_title = cosine_similarity(pos_center_title, np.array(list(train_df["title_embeddings"])))
    neg_cos_sim_title = cosine_similarity(neg_center_title, np.array(list(train_df["title_embeddings"])))
    net_cos_sim_title = cosine_similarity(net_center_title, np.array(list(train_df["title_embeddings"])))

    val_pos_cos_sim_title = cosine_similarity(pos_center_title, np.array(list(val_df["title_embeddings"])))
    val_neg_cos_sim_title = cosine_similarity(neg_center_title, np.array(list(val_df["title_embeddings"])))
    val_net_cos_sim_title = cosine_similarity(net_center_title, np.array(list(val_df["title_embeddings"])))

    train_kmeans_title = []
    val_kmenas_title = []

    for elem in pos_cos_sim_title:
        train_kmeans_title.append(np.transpose(neg_cos_sim_title - elem))
        train_kmeans_title.append(np.transpose(net_cos_sim_title - elem))
        
    for elem in net_cos_sim_title:
        train_kmeans_title.append(np.transpose(neg_cos_sim_title - elem))
        
    for elem in val_pos_cos_sim_title:
        val_kmenas_title.append(np.transpose(val_neg_cos_sim_title - elem))
        val_kmenas_title.append(np.transpose(val_net_cos_sim_title - elem))
        
    for elem in val_net_cos_sim_title:
        val_kmenas_title.append(np.transpose(val_neg_cos_sim_title - elem))

    train_kmeans_title = np.hstack((np.hstack(train_kmeans_title),pos_cos_sim_title.T,neg_cos_sim_title.T,net_cos_sim_title.T))
    val_kmenas_title = np.hstack((np.hstack(val_kmenas_title),val_pos_cos_sim_title.T,val_neg_cos_sim_title.T,val_net_cos_sim_title.T))

    kmeans_title_scaler = StandardScaler()
    train_kmeans_title = kmeans_title_scaler.fit_transform(train_kmeans_title)
    val_kmenas_title = kmeans_title_scaler.transform(val_kmenas_title)

    lf_kmeans_title = LinearDiscriminantAnalysis()
    train_kmeans_title = lf_kmeans_title.fit_transform(train_kmeans_title,y_train)
    val_kmenas_title = lf_kmeans_title.transform(val_kmenas_title)


    final_model["pos_center_title"] = pos_center_title
    final_model["neg_center_title"] = neg_center_title
    final_model["net_center_title"] = net_center_title

    final_model["kmeans_title_scaler"] = kmeans_title_scaler
    final_model["lf_kmeans_title"] = lf_kmeans_title

    # Body Embeddings
    pos_sent_embed = np.array(list(train_df[train_df["class"] == "P"]["sentence_embeddings_mean"]))
    net_sent_embed = np.array(list(train_df[train_df["class"] == "Z"]["sentence_embeddings_mean"]))
    neg_sent_embed = np.array(list(train_df[train_df["class"] == "N"]["sentence_embeddings_mean"]))

    pos_clustering_sent = KMeans(n_clusters=3,random_state = 2250)
    neg_clustering_sent = KMeans(n_clusters=3,random_state = 2250)
    net_clustering_sent = KMeans(n_clusters=3,random_state = 2250)

    pos_cluster_sent = pos_clustering_sent.fit(pos_sent_embed)
    neg_cluster_sent = neg_clustering_sent.fit(neg_sent_embed)
    net_cluster_sent = net_clustering_sent.fit(net_sent_embed)

    pos_center_sent = pos_cluster_sent.cluster_centers_
    neg_center_sent = neg_cluster_sent.cluster_centers_
    net_center_sent = net_cluster_sent.cluster_centers_

    pos_cos_sim_sent = cosine_similarity(pos_center_sent, np.array(list(train_df["sentence_embeddings_mean"])))
    neg_cos_sim_sent = cosine_similarity(neg_center_sent, np.array(list(train_df["sentence_embeddings_mean"])))
    net_cos_sim_sent = cosine_similarity(net_center_sent, np.array(list(train_df["sentence_embeddings_mean"])))

    val_pos_cos_sim_sent = cosine_similarity(pos_center_sent, np.array(list(val_df["sentence_embeddings_mean"])))
    val_neg_cos_sim_sent = cosine_similarity(neg_center_sent, np.array(list(val_df["sentence_embeddings_mean"])))
    val_net_cos_sim_sent = cosine_similarity(net_center_sent, np.array(list(val_df["sentence_embeddings_mean"])))

    train_kmeans_sent = []
    val_kmenas_sent = []

    for elem in pos_cos_sim_sent:
        train_kmeans_sent.append(np.transpose(neg_cos_sim_sent - elem))
        train_kmeans_sent.append(np.transpose(net_cos_sim_sent - elem))
        
    for elem in net_cos_sim_sent:
        train_kmeans_sent.append(np.transpose(neg_cos_sim_sent - elem))
        
    for elem in val_pos_cos_sim_sent:
        val_kmenas_sent.append(np.transpose(val_neg_cos_sim_sent - elem))
        val_kmenas_sent.append(np.transpose(val_net_cos_sim_sent - elem))
        
    for elem in val_net_cos_sim_sent:
        val_kmenas_sent.append(np.transpose(val_neg_cos_sim_sent - elem))

    train_kmeans_sent = np.hstack((np.hstack(train_kmeans_sent),pos_cos_sim_sent.T,neg_cos_sim_sent.T,net_cos_sim_sent.T))
    val_kmenas_sent = np.hstack((np.hstack(val_kmenas_sent),val_pos_cos_sim_sent.T,val_neg_cos_sim_sent.T,val_net_cos_sim_sent.T))

    kmeans_sent_scaler = StandardScaler()
    train_kmeans_sent = kmeans_sent_scaler.fit_transform(train_kmeans_sent)
    val_kmenas_sent = kmeans_sent_scaler.transform(val_kmenas_sent)

    lf_kmeans_sent = LinearDiscriminantAnalysis()
    train_kmeans_sent = lf_kmeans_sent.fit_transform(train_kmeans_sent,y_train)
    val_kmenas_sent = lf_kmeans_sent.transform(val_kmenas_sent)

    final_model["pos_center_sent"] = pos_center_sent
    final_model["neg_center_sent"] = neg_center_sent
    final_model["net_center_sent"] = net_center_sent

    final_model["kmeans_sent_scaler"] = kmeans_sent_scaler
    final_model["lf_kmeans_sent"] = lf_kmeans_sent

    ############################################################################

    X_train_new = np.hstack((
        X_train_new_,
        lf_t.transform(np.array(list(train_df["title_embeddings"]))),
        title_pca.transform(title_scaler.transform(feature_sel_embed_t.transform(np.array(list(train_df["title_embeddings"]))))),
        ################################################################################
        feature_sel_embed_sen_t.transform(np.array(list(train_df["sentence_embeddings_mean"]))),
        lf_te.transform(np.array(list(train_df["sentence_embeddings_mean"]))),
        ##################################################################################
        train_kmeans_title,
        train_kmeans_sent,  
    ))
        
    X_val_new = np.hstack((
        X_val_new_,
        lf_t.transform(np.array(list(val_df["title_embeddings"]))),
        title_pca.transform(title_scaler.transform(feature_sel_embed_t.transform(np.array(list(val_df["title_embeddings"]))))),
        ##################################################################################
        feature_sel_embed_sen_t.transform(np.array(list(val_df["sentence_embeddings_mean"]))),
        lf_te.transform(np.array(list(val_df["sentence_embeddings_mean"]))),
        ##################################################################################
        val_kmenas_title,
        val_kmenas_sent,
    ))

    xgbcls = xgb.XGBClassifier(
        gamma = 0.6,
        min_child_weight = 1,
        max_depth=2,
        n_estimators=2000,
        learning_rate = 0.01,
        subsample = 0.6,
        colsample_bytree = 0.05,
        nthread = 8,
        verbosity = 0,
        reg_alpha = 0.01,
        objective = "multi:sotfprob",
        use_label_encoder=False,
        feature_selector = "greedy",
        importance_type = "merror",
        random_state = 0
    )

    xgbcls.fit(
        X_train_new, y_train, 
        eval_set=[(X_train_new, y_train), 
                (X_val_new, y_val)],
        early_stopping_rounds=300, 
        eval_metric="merror", 
        verbose=True
    )

    final_model["xgbcls"] = xgbcls

    print("Train Accuracy: ",accuracy_score(xgbcls.predict(X_train_new),y_train))
    print("Validation Accuracy: ",accuracy_score(xgbcls.predict(X_val_new),y_val))

    print("Train Report:\n",classification_report(y_train,xgbcls.predict(X_train_new)))
    print("Validation Report:\n",classification_report(y_val,xgbcls.predict(X_val_new)))

    plot_confusion_matrix(confusion_matrix(y_train,xgbcls.predict(X_train_new)),confusion_matrix(y_val,xgbcls.predict(X_val_new)))
    plt.show()

    plt.plot(xgbcls.evals_result()["validation_1"]["merror"][10:])
    plt.title("Validation Error")
    plt.show()

    with open('step3_model_NoName.pkl', 'wb') as handle:
        pickle.dump(final_model, handle, protocol=pickle.HIGHEST_PROTOCOL)