from flask import Flask, request, render_template
import pandas as pd
import random
from flask_sqlalchemy import SQLAlchemy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load files
trending_products = pd.read_csv(
    r"C:\Users\sh\Downloads\trending_products.csv"
)

train_data = pd.read_csv(
    "marketing_sample_for_walmart_com-walmart_com_product_review__20200701_20201231__5k_data.tsv",
    sep="\t"
)

# Database configuration
app.secret_key = "alskdjfwoeieiurlskdjfslkdjf"

app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://root:@localhost/ecom"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Define your model class for the 'signup' table
class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


# Define your model class for the 'signin' table
class Signin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


# ============================================================
# Recommendation Functions
# ============================================================

def truncate(text, length):
    if len(text) > length:
        return text[:length] + "..."
    else:
        return text


def content_based_recommendations(train_data, item_name, top_n=10):

    # Check if the item name exists
    if item_name not in train_data['Name'].values:
        print(f"Item '{item_name}' not found in the training data.")
        return pd.DataFrame()

    # Create TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')

    # Apply TF-IDF to product tags
    tfidf_matrix_content = tfidf_vectorizer.fit_transform(
        train_data['Tags'].fillna('')
    )

    # Calculate cosine similarity
    cosine_similarities_content = cosine_similarity(
        tfidf_matrix_content,
        tfidf_matrix_content
    )

    # Find index of selected product
    item_index = train_data[
        train_data['Name'] == item_name
    ].index[0]

    # Get similarity scores
    similar_items = list(
        enumerate(cosine_similarities_content[item_index])
    )

    # Sort by similarity score
    similar_items = sorted(
        similar_items,
        key=lambda x: x[1],
        reverse=True
    )

    # Exclude the selected product
    top_similar_items = similar_items[1:top_n + 1]

    # Get recommended product indices
    recommended_item_indices = [
        x[0] for x in top_similar_items
    ]

    # Get recommended product details
    recommended_items_details = train_data.iloc[
        recommended_item_indices
    ][
        [
            'Name',
            'ReviewCount',
            'Brand',
            'ImageURL',
            'Rating'
        ]
    ]

    return recommended_items_details


# ============================================================
# Random Images
# ============================================================

random_image_urls = [
    "static/img/img_1.png",
    "static/img/img_2.png",
    "static/img/img_3.png",
    "static/img/img_4.png",
    "static/img/img_5.png",
    "static/img/img_6.png",
    "static/img/img_7.png",
    "static/img/img_8.png",
]


# ============================================================
# Routes
# ============================================================

@app.route("/")
def index():

    random_product_image_urls = [
        random.choice(random_image_urls)
        for _ in range(len(trending_products))
    ]

    price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]

    return render_template(
        'index.html',
        trending_products=trending_products.head(8),
        truncate=truncate,
        random_product_image_urls=random_product_image_urls,
        random_price=random.choice(price)
    )


@app.route("/main")
def main():
    return render_template('main.html')


@app.route("/index")
def indexredirect():

    random_product_image_urls = [
        random.choice(random_image_urls)
        for _ in range(len(trending_products))
    ]

    price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]

    return render_template(
        'index.html',
        trending_products=trending_products.head(8),
        truncate=truncate,
        random_product_image_urls=random_product_image_urls,
        random_price=random.choice(price)
    )


@app.route("/signup", methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        new_signup = Signup(
            username=username,
            email=email,
            password=password
        )

        db.session.add(new_signup)
        db.session.commit()

        random_product_image_urls = [
            random.choice(random_image_urls)
            for _ in range(len(trending_products))
        ]

        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]

        return render_template(
            'index.html',
            trending_products=trending_products.head(8),
            truncate=truncate,
            random_product_image_urls=random_product_image_urls,
            random_price=random.choice(price),
            signup_message='User signed up successfully!'
        )


@app.route('/signin', methods=['POST', 'GET'])
def signin():

    if request.method == 'POST':

        username = request.form['signinUsername']
        password = request.form['signinPassword']

        new_signup = Signin(
            username=username,
            password=password
        )

        db.session.add(new_signup)
        db.session.commit()

        random_product_image_urls = [
            random.choice(random_image_urls)
            for _ in range(len(trending_products))
        ]

        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]

        return render_template(
            'index.html',
            trending_products=trending_products.head(8),
            truncate=truncate,
            random_product_image_urls=random_product_image_urls,
            random_price=random.choice(price),
            signup_message='User signed in successfully!'
        )


@app.route("/recommendations", methods=['POST', 'GET'])
def recommendations():

    if request.method == 'POST':

        prod = request.form.get('prod')
        nbr = int(request.form.get('nbr'))

        content_based_rec = content_based_recommendations(
            train_data,
            prod,
            top_n=nbr
        )

        if content_based_rec.empty:

            message = "No recommendations available for this product."

            return render_template(
                'main.html',
                message=message
            )

        else:

            random_product_image_urls = [
                random.choice(random_image_urls)
                for _ in range(len(content_based_rec))
            ]

            print(content_based_rec)
            print(random_product_image_urls)

            price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]

            return render_template(
                'main.html',
                content_based_rec=content_based_rec,
                truncate=truncate,
                random_product_image_urls=random_product_image_urls,
                random_price=random.choice(price)
            )


if __name__ == '__main__':
    app.run(debug=True)