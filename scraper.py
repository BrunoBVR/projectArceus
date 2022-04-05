from requests_html import HTMLSession
import pickle

s = HTMLSession()
base_url = 'https://www.metacritic.com'

## Getting review content
def get_reviews(url):

    r = s.get(url)

    reviews = r.html.find('li.review.user_review')
    
    return reviews

# Parsing a review
def parse_product(rev):
    
    # Review
    try: # Collapsed case
        review = rev.find('span.blurb.blurb_expanded', first=True).text.strip().replace('\n', '')
    except AttributeError:
        review = rev.find('span', first=True).text.strip().replace('\n', '')
    
    # Date
    date = rev.find('div.date', first=True).text.strip().replace('\n', '')
    
    # Score
    score = rev.find('div.review_grade', first=True).text.strip().replace('\n', '')
    
    # Helpful
    helpful = rev.find('div.helpful_summary.thumb_count', first=True).text
    
    # Critic link
    user_url = base_url+rev.find('div.name', first=True).find('a', first=True).attrs['href']
    
    # Getting into user link
    user_r = s.get(user_url)

    # number of reviews by user
    numb_revs = user_r.html.find('span.total_summary_reviews', first=True).text

    # number of ratings by user
    numb_ratings = user_r.html.find('span.total_summary_ratings.mr20', first=True).text

    # Average review score
    avg_score = user_r.html.find('span.summary_data', first=True).text
    
    row = {
        'review': review,
        'date': date,
        'score': score,
        'helpful': helpful,
        'number_of_reviews': numb_revs,
        'number_of_ratings': numb_ratings,
        'average_user_score': avg_score,
    }
    return row

# Handling pagination
def get_next_page(url):

    r = s.get(url)
    
    next_button = r.html.find('span.flipper.next', first=True).find('a', first=True)
    
    if next_button:
        return base_url+next_button.attrs['href']


def main():

    url = 'https://www.metacritic.com/game/switch/pokemon-legends-arceus/user-reviews?sort-by=score&num_items=100&page=0'
    # Loop for pagination
    counter = 0
    # Saving page reviews
    results = []

    while True:
        print(f'On page {counter}')

        reviews = get_reviews(url)
        for review in reviews:
            results.append(parse_product(review))

        print('Total reviews: ', len(results))

        url = get_next_page(url)
        if not url:
            break
        counter += 1
    
    pickle.dump( results, open( "reviews.data", "wb" ) )
    
if __name__ == '__main__':
    main()