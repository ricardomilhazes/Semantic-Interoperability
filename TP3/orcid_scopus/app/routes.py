from app import app

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/tiago')
def tigas():
    return """
    <h1>Relatable!</h1>
    """