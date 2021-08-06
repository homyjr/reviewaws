# doing necessary imports
import threading
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import plotly.express as px
import plotly.io as pio
import os

from cassandraDBoperations import cassandraDBManagement
from logger_class import getLog
from flask import Flask, render_template, request, jsonify, Response, url_for, redirect
from flask_cors import CORS, cross_origin
import pandas as pd

from FlipkratScrapping import FlipkratScrapper
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager



table = "flipkartscrapper"

rows = {}
collection_name = None

logger = getLog('flipkrat.py')

free_status = True
db_name = 'Flipkart-Scrapper'

app = Flask(__name__)  # initialising the flask app with the name 'app'

#For selenium driver implementation on heroku
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
#driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
#To avoid the time out issue on heroku
class threadClass:

    def __init__(self, expected_review, searchString, scrapper_object, review_count):
        self.expected_review = expected_review
        self.searchString = searchString
        self.scrapper_object = scrapper_object
        self.review_count = review_count
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):
        global collection_name, free_status
        free_status = False
        collection_name = self.scrapper_object.getReviewsToDisplay(expected_review=self.expected_review,
                                                                   searchString=self.searchString, username='Kavita',
                                                                   password='kavita1610',
                                                               review_count=self.review_count)
        print(collection_name)
        logger.info("Thread run completed")
        free_status = True


@app.route('/', methods=['POST', 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        global free_status
        ## To maintain the internal server issue on heroku
        if free_status != True:
            return "This website is executing some process. Kindly try after some time..."
        else:
            free_status = True
        searchString = request.form['content'].replace(" ", "")  # obtaining the search string entered in the form
        expected_review = int(request.form['expected_review'])
        try:
            review_count = 0
            scrapper_object = FlipkratScrapper(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

            cassandraClient = cassandraDBManagement()
            scrapper_object.openUrl("https://www.flipkart.com/")
            logger.info("Url hitted")
            scrapper_object.login_popup_handle()
            logger.info("login popup handled")
            scrapper_object.searchProduct(searchString=searchString)
            logger.info(f"Search begins for {searchString}")
            if cassandraClient.isproductavailable(search_string=searchString, table=table):
                response = cassandraClient.getallproductdata(search_string= searchString, table=table)
                reviews = response
                print("hello")
                if len(reviews) > expected_review:
                    result = [reviews[i] for i in range(0, expected_review)]
                    scrapper_object.saveDataFrameToFile(file_name="static/scrapper_data.csv",
                                                        dataframe=pd.DataFrame(result))
                    logger.info("Data saved in scrapper file")
                    return render_template('results.html', rows=result)  # show the results to user
                else:
                    review_count = len(reviews)
                    threadClass(expected_review=expected_review, searchString=searchString,
                                scrapper_object=scrapper_object, review_count=review_count)
                    logger.info("data saved in scrapper file")
                    return redirect(url_for('feedback'))
            else:
                threadClass(expected_review=expected_review, searchString=searchString, scrapper_object=scrapper_object,
                            review_count=review_count)
                return redirect(url_for('feedback'))

        except Exception as e:
            raise Exception("(app.py) - Something went wrong while rendering all the details of product.\n" + str(e))

    else:
        return render_template('index.html')


@app.route('/feedback', methods=['GET'])
@cross_origin()
def feedback():
    try:
        global collection_name
        if collection_name is not None:
            scrapper_object = FlipkratScrapper(executable_path=ChromeDriverManager().install(),
                                               chrome_options=chrome_options)
            cassandraClient = cassandraDBManagement()

            response = cassandraClient.getallproductdata(search_string=collection_name, table=table)


            reviews = response
            dataframe = pd.DataFrame(reviews)
            scrapper_object.saveDataFrameToFile(file_name="static/scrapper_data.csv", dataframe=dataframe)
            collection_name = None
            return render_template('results.html', rows=reviews)


        else:
            return render_template('results.html', rows=None)
    except Exception as e:
        raise Exception("(feedback) - Something went wrong on retrieving feedback.\n" + str(e))


@app.route("/graph1", methods=['GET'])
@cross_origin()
def graph1():
    df = pd.read_csv("static/scrapper_data.csv")
    df["product_name"] = df["product_name"].astype('category').cat.codes
    fig = px.scatter(df , x = "product_name", y = "rating")

    fig.update_layout(template='plotly_white')
    pio.write_html(fig, file='templates/graph1.html')
    return render_template('graph1.html')

@app.route("/graph2", methods=['GET'])
@cross_origin()
def graph2():
    df = pd.read_csv("static/scrapper_data.csv")
    df["product_name"] = df["product_name"].astype('category').cat.codes
    fig = px.bar(df , x = "product_name", y = "rating")

    fig.update_layout(template='plotly_white')
    pio.write_html(fig, file='templates/graph2.html')
    return render_template("graph2.html")

@app.route("/graph3", methods=['GET'])
@cross_origin()
def graph3():
    df = pd.read_csv("static/scrapper_data.csv")
    df["product_name"] = df["product_name"].astype('category').cat.codes
    fig = px.histogram(df , x = "product_name", y = "rating")

    fig.update_layout(template='plotly_white')
    pio.write_html(fig, file='templates/graph3.html')
    return render_template("graph3.html")



@app.route('/a', methods=['GET'])
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_figure():
    data = pd.read_csv("static/scrapper_data.csv")
    dataframe = pd.DataFrame(data=data)
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = dataframe['product_searched']
    ys = dataframe['rating']
    axis.scatter(xs, ys)
    return fig





if __name__ == "__main__":
    app.run()  # running the app on the local machine on port 8000