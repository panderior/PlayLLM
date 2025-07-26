from play_llm_flask import app

if __name__ == "__main__":      
    app.run(debug=True, host='0.0.0.0',port=5006, use_reloader=False)