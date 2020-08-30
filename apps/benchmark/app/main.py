import sys
import time

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    """
    Simple hello work function

    Returns:
        String: hello world string
    """
    start = time.time()
    
    diff = time.time() - start
    return {
        "data": "Hello World MSC - Container as a Service Comparison",
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
    start = time.time()

    if number < 0:
        return "Number needs to be positive", 400
    elif number == 0:
        result =  f"Factorial of 0 is: 1"
    else:
        factorial = 1
        for i in range(1,number + 1):
            factorial = factorial*i
        result = f"Factorial of {number} is: {factorial}"

    end = time.time()
    diff = end - start

    return {
        "data": result,
        "start": start,
        "end": end,
        "duration": diff
    }, 200

        


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)