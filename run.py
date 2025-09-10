from app.main import create_app


app = create_app()


if __name__ == "__main__":
    # Default to localhost:5000 with debug reload for dev convenience
    app.run(host="127.0.0.1", port=5000, debug=True)


