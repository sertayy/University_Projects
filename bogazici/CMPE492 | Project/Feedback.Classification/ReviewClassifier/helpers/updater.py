import pickle
import json

reviews_json = []


def json_helper(review_list, rating, cat_type):
    for elem in review_list:
        reviews_json.append({
            "review": elem[1:],
            "rating": rating,
            "category": cat_type
        })


if __name__ == '__main__':
    with open("../old_files/reviews_6_6.pickle", "rb") as p:
        reviews_pickle = pickle.load(p)
    bug_1 = [
        reviews_pickle[1][4],
        reviews_pickle[1][14],
        reviews_pickle[1][15],
    ]
    bug_2 = [
        reviews_pickle[2][4],
        reviews_pickle[2][14]
    ]
    bug_3 = [
        reviews_pickle[3][3],
        reviews_pickle[3][10],
        reviews_pickle[3][16],
        reviews_pickle[3][24]
    ]

    feature_1 = [
        reviews_pickle[1][2],
        reviews_pickle[1][10]
    ]
    feature_2 = [
        reviews_pickle[2][0],
        reviews_pickle[2][1],
        reviews_pickle[2][10],
        reviews_pickle[2][11],
        reviews_pickle[2][13],
        reviews_pickle[2][15]
    ]
    feature_3 = [
        reviews_pickle[3][1],
        reviews_pickle[3][2],
        reviews_pickle[3][5],
        reviews_pickle[3][7],
        reviews_pickle[3][8],
        reviews_pickle[3][12],
        reviews_pickle[3][14],
        reviews_pickle[3][17],
        reviews_pickle[3][19],
        reviews_pickle[3][25]
    ]

    user_ex_1 = [
        reviews_pickle[1][0],
        reviews_pickle[1][1],
        reviews_pickle[1][2],
        reviews_pickle[1][5],
        reviews_pickle[1][6],
        reviews_pickle[1][7],
        reviews_pickle[1][9],
        reviews_pickle[1][10],
        reviews_pickle[1][11],
        reviews_pickle[1][12],
        reviews_pickle[1][16],
        reviews_pickle[1][17],
        reviews_pickle[1][18],
        reviews_pickle[1][19]
    ]
    user_ex_2 = [
        reviews_pickle[2][5],
        reviews_pickle[2][6],
        reviews_pickle[2][7],
        reviews_pickle[2][9],
        reviews_pickle[2][10],
        reviews_pickle[2][12],
        reviews_pickle[2][15]
    ]
    user_ex_3 = [
        reviews_pickle[3][0],
        reviews_pickle[3][2],
        reviews_pickle[3][4],
        reviews_pickle[3][5],
        reviews_pickle[3][6],
        reviews_pickle[3][8],
        reviews_pickle[3][18],
        reviews_pickle[3][23]
    ]

    ratings_1 = [
        reviews_pickle[1][3],
        reviews_pickle[1][8],
        reviews_pickle[1][12],
        reviews_pickle[1][13],
        reviews_pickle[1][19]
    ]
    ratings_2 = [
        reviews_pickle[2][1],
        reviews_pickle[2][8]
    ]
    ratings_3 = [
        reviews_pickle[3][9],
        reviews_pickle[3][10],
        reviews_pickle[3][11],
        reviews_pickle[3][13],
        reviews_pickle[3][15],
        reviews_pickle[3][18],
        reviews_pickle[3][20],
        reviews_pickle[3][21],
        reviews_pickle[3][22],
        reviews_pickle[3][24]
    ]

    json_helper(bug_1, 1, "bug report")
    json_helper(bug_2, 2, "bug report")
    json_helper(bug_3, 3, "bug report")
    json_helper(feature_1, 1, "feature request")
    json_helper(feature_2, 2, "feature request")
    json_helper(feature_3, 3, "feature request")
    json_helper(user_ex_1, 1, "user experience")
    json_helper(user_ex_2, 2, "user experience")
    json_helper(user_ex_3, 3, "user experience")
    json_helper(ratings_1, 1, "ratings")
    json_helper(ratings_2, 2, "ratings")
    json_helper(ratings_3, 3, "ratings")

    with open("../old_files/classified_reviews.json", "w") as out:
        json.dump(reviews_json, out, ensure_ascii=False, indent=4)
