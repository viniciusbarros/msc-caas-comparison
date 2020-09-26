import time
from flask import Flask
from waitress import serve
from logging.config import dictConfig
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)


@app.route("/")
def hello_world():
    """
    Simple hello work function

    Returns:
        String: hello world string
    """
    app.logger.info("GET /")
    start = time.time()
    data = "Hello World MSC - Container as a Service Comparison"
    diff = float("%.7f" % (time.time() - start))
    
    return {
        "data": data,
        "duration": diff
    }, 200


@app.route("/cpu/factorial/<int:number>")
def calculate_factorial(number):
    """
    Given an integer number, returns its factorial.
    Args:
        number (int): Positive Integer

    Returns:
        String: Text of the factorial
    """
    app.logger.info(f"GET /cpu/factorial/{number}")
    start = time.time()

    if number < 0:
        return "Number needs to be positive", 400
    elif number == 0:
        result = f"Factorial of 0 is: 1"
    else:
        factorial = 1
        for i in range(1, number + 1):
            factorial = factorial*i
        result = f"Factorial of {number} is: {factorial}"

    end = time.time()
    # Precision of 6 decimals
    diff = float("%.7f" % (end - start))
    app.logger.info(f"GET /cpu/factorial/{number} took {diff} seconds")

    return {
        "data": result,
        "start": start,
        "end": end,
        "duration": diff
    }, 200


if __name__ == "__main__":
    # Serving the app using Waitress
    app.logger.info("Starting Webserver")
    
    serve(app, host='0.0.0.0', port=80, threads=4)
