# Seawar_server

Server part of seawar game. Provides initial load of frontend part. 
And then provides some endpoints for API requests

## How to install

1. Download the repo to local catalog

    ```bash
    $ git clone git@github.com:lisfer/seawar_server.git
    ```

2. Create virtual environment with python 3

    ```bash
    $ pip install -p python3 venv
    $ source ./venv/bin/activate 
    ```

3. Install all dependencies:

    ```bash
    $ pip isntall -r requirements.txt
    ```
    
4. Run the dev-server:

    ```bash
    $ make run
    ```
    
Now you should be able to find it on `http://localhost:5000`