from moviehub import create_app, db


app = create_app()


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    os.makedirs(app.instance_path, exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=port)