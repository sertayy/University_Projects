import json
import pandas as pd
import pickle

if __name__ == "__main__":
    with open("results-20210619-172446.json", "r") as f:
        big_query_data = json.load(f)
    # 1->ratings, 2->user experience, 3->feature request, 4->bug report
    temp_list = []
    for dict_item in big_query_data:
        temp_dict = {}
        temp_dict["review"] = dict_item["review"]
        category = dict_item["category"]
        if category.startswith("r"):
            category_num = 1
        elif category.startswith("u"):
            category_num = 2
        elif category.startswith("f"):
            category_num = 3
        else:
            category_num = 4
        temp_dict["category"] = category_num
        temp_list.append(temp_dict)
    df = pd.DataFrame(temp_list)
    with open("reviews_df_19_6.pickle", "wb") as output_file:
        pickle.dump(df, output_file)
