import com.google.api.services.androidpublisher.AndroidPublisher;
import com.google.api.services.androidpublisher.model.Review;
import com.google.api.services.androidpublisher.model.ReviewsListResponse;
import com.google.gson.Gson;

import java.io.FileWriter;
import java.io.IOException;
import java.security.GeneralSecurityException;
import java.util.List;
import java.util.stream.Collectors;

public class FetchReviews {

    public static void main(String[] args) throws IOException, GeneralSecurityException {
        AndroidPublisher service = AndroidPublisherHelper.init(ApplicationConfig.APPLICATION_NAME,
                ApplicationConfig.SERVICE_ACCOUNT_EMAIL);

        AndroidPublisher.Reviews.List trendyolReviews = service.reviews().list(ApplicationConfig.PACKAGE_NAME);
        ReviewsListResponse pageResponse = trendyolReviews.execute();

        List<ReviewItem> reviews = getReviewItems(pageResponse.getReviews());

        String nextPageToken = pageResponse.getTokenPagination().getNextPageToken();

        for(int i = 0; i < 1; i++) {
            trendyolReviews.setToken(nextPageToken);
            pageResponse = trendyolReviews.execute();
            reviews.addAll(getReviewItems(pageResponse.getReviews()));
            nextPageToken = pageResponse.getTokenPagination().getNextPageToken();
        }

        String reviewsJson = new Gson().toJson(reviews);
        FileWriter fileWriter = new FileWriter("reviews.txt");
        fileWriter.write(reviewsJson);
        fileWriter.close();
    }

    private static List<ReviewItem> getReviewItems(List<Review> reviews) {
        return reviews.stream()
                .filter(review -> review.getComments().get(0).getUserComment().getReviewerLanguage().equals("tr"))
                .map(review -> new ReviewItem(review.getComments().get(0).getUserComment().getText(),
                        review.getComments().get(0).getUserComment().getStarRating()))
                .collect(Collectors.toList());
    }
}
