import json
import pickle


if __name__ == '__main__':
    with open("reviews.txt") as file:  # TODO path'i napalim?
        text = file.readline()
    reviews = json.loads(text)
    star_rating_dict = {}
    for i in range(1, 6):
        star_rating_dict[i] = []
    for review in reviews:
        star_rating_dict[review["rating"]].append(review["text"])
    with open("../output/reviews.pickle", "wb") as output_file:
        pickle.dump(star_rating_dict, output_file)
