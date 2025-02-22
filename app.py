from flask import Flask, render_template, request
import torch
import numpy
from diffusers import StableDiffusionPipeline
from flask_caching import Cache

app = Flask(name)
cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})

# Use a different model
model_id = "CompVis/stable-diffusion-v1-4"

# Use GPU acceleration if available
device = "cuda" if torch.cuda.is_available() else "cpu"

# Set the image size
image_size = 496

# Set the number of inference steps
num_inference_steps = 30

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/second_page', methods=['POST'])
def second_page():
    password = request.form['password']
    if password == "ISE2025":
        return render_template('second_page.html')
    else:
        return "<span style='color: red; font-weight: bold; font-size: 32px; text-align: center;'>Incorrect password</span>"

@app.route('/project_selection')
def project_selection():
    return render_template('project_selection.html')

@app.route('/about_team')
def about_team():
    return render_template('about_team.html')

@app.route('/text_to_image_synthesis', methods=['GET', 'POST'])
def text_to_image_synthesis():
    if request.method == 'POST':
        try:
            prompt = request.form['prompt']

            # Check if the image is already cached
            image_path = cache.get(prompt)
            if image_path is None:
                # Generate the image and cache it
                pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
                pipe = pipe.to(device)

                image = pipe(prompt, width=image_size, height=image_size, num_inference_steps=num_inference_steps).images[0]
                image_path = f"static/{prompt}.png"
                image.save(image_path)

                cache.set(prompt, image_path)

            return render_template('text_to_image_synthesis.html', prompt=prompt, image_url=image_path)
        except Exception as e:
            return f"An error occurred: {e}. Please check your internet connection and try again."
    else:
        return render_template('text_to_image_synthesis.html')

if name == 'main':
    app.run(debug=True)