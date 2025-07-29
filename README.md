# Toto Number Generator
Randomly generates the magical 6 digits that might make you rich (probably not).

## Requirements
1. make
2. Docker
3. Python3.11

## Local Development
1. Setup environment variables.
    ```sh
    cp -i .streamlit/secrets.toml.example .streamlit/secrets.toml
    ```
- Set a value for `submission_password` so that you can add the new Toto results to the database.

2. Run app
    ```sh
    $ make run # run the Streamlit app
    ```
