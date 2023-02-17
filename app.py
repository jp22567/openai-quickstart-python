import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        animal = request.form["animal"]
        response = openai.Completion.create(
          model="text-davinci-003",
          prompt=generate_prompt(text),
          temperature=0,
          max_tokens=256,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
        )
        # response = openai.Completion.create(
            # model="text-curie-001",
            # prompt=generate_prompt(animal),
            # temperature=0.6,
        # )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)

def generate_prompt(text):
    return """Extract the medical questionnaires used in this text:
    {}""".format(text)


# def generate_prompt(animal):
    # return """Suggest three names for an animal that is a superhero.
# 
# Animal: Cat
# Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
# Animal: Dog
# Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
# Animal: {}
# Names:""".format(
        # animal.capitalize()
    # )


