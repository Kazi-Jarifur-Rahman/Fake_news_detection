from flask import Flask, request, jsonify
from text_fake_news_detector import fact_check_input
from image_fake_news_detector import analyze_image
from flask import render_template
app = Flask(__name__)

# Route for fact-checking text input
from flask import render_template

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/fact-check', methods=['POST'])
def fact_check():
    data = request.get_json()
    text = data.get('text')
    result = fact_check_input(text)
    return jsonify({'result': result})

# Route for analyzing image input
@app.route('/analyze-image', methods=['POST'])
def analyze_image_route():
    if 'image' not in request.files:
        return jsonify({'result': 'No image uploaded.'}), 400

    image_file = request.files['image']
    image_path = 'uploaded_image.jpg'
    image_file.save(image_path)

    result = analyze_image(image_path)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
