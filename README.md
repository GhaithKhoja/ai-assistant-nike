# ai-assistant-nike
## Demo Video
### Nike AI Assistant Demo
https://www.loom.com/share/b822662962be434eb80a8e8b9412274f?sid=b5bdea8f-20a0-44e9-a72a-6afec3498f39
### Scraper Demo
https://www.loom.com/share/4fe069ad58a94005bc444e82cb9167f5
## File Structure
```
├── README.md
├── requirements.txt
├── environment.yml
├── example.env
├── assistant.py
├── main.py
└── scraper
    ├── db
    │   ├── backup
    │   │   └── database.db
    |   │   └── initial_fetch.db
    │   ├── database.db
    │   └── database.py
    ├── image_processing.py
    └── scraper.py
```
### Files:
- README.md: Project overview and documentation.
- requirements.txt: List of Python dependencies for the project.
- environment.yml: Used to create the Conda environment for the project.
- example.env: Example environment variable file for configuration.
- assistant.py: Main code for the Nike Air Jordan AI assistant.
- main.py: Driver script to run the AI assistant. Supports `--audio` flag for generating and playing audio responses on macOS.

Scraper Folder:
- scraper.py: Main script for scraping Nike's website.
- image_processing.py: Script for post-processing product images and determining shoe type.

DB Folder:
- database.py: Script to interact with the main SQLite database (database.db).
backup/:
- database.db: Backup of the main database.
initial_fetch.db: Initial version of the database for restoring purposes.


## Setup
To run this project, we need to configure the environment variables for this project. Make a copy of `example.env` and rename it to `.env`. Open up the newly created `.env` file and follow the instructions inside to add your API key.
https://www.loom.com/share/45dd049cad8a456e857d863fc81f0bc2

Afterwards, you need to install `conda` for managing the environment and package dependencies. Follow these steps to set up the environment:
https://www.loom.com/share/2d70e6b3229343b991c9955b0cea6b30?sid=5b1a7845-aee8-4629-be9a-c65e31222e5e

#### Step 1: Install Conda

If you don't already have `conda` installed, follow the instructions on the [official Miniconda page](https://docs.conda.io/en/latest/miniconda.html) to install Miniconda.

#### Step 2: Create the Conda Environment

Create an environment using the provided `environment.yml` file:

```sh
conda env create -f environment.yml
```

This command will create a new `conda` environment named `myenv` and install the necessary packages specified in `environment.yml`.

#### Step 3: Activate the Conda Environment and Install Additional Dependencies

#### Setup video

1. Activate the newly created conda environment:

    ```sh
    conda activate nike-ai-assistant-env
    ```

2. Install the additional dependencies using `pip`:

    ```sh
    pip install -r requirements.txt
    ```

Following these steps ensures that your environment is set up correctly with all the required dependencies.

Note: This project requires macOS for audio playback if you are using the `--audio` flag in the `main.py` script. The audio playback is done using the `afplay` subprocess, which is only available on macOS.

There is a preloaded database available that is built using the scraper, so if you want to skip the scraping step, you can directly use the provided database files.

If you want to run the scraper and see it, you can run `scraper.py` and it will load the data into the database. If you would like to see the scraper work with a new database, you can change the name `database.db` in the `database.py` file to something else in the `get_connection` function. Change the name so there is no conflicts when adding new products.

you can run the main driver script using:
```bash
python main.py
```
or, for audio playback, use:
```bash
python main.py --audio
```

## Database

In this project, I opted to use SQLite3 as the database system instead of hosting a database on the cloud. SQLite3 offers several advantages, particularly in the context of this project:

- **Ease of Use**: SQLite3 is lightweight and easy to set up. There's no need for database server configuration, which simplifies the process for users.
- **Accessibility**: The use of SQLite3 allows users to easily access and explore the data without the need for a network connection. Users can just download the project and start interacting with the database right away.
- **Portability**: SQLite databases are stored in a single file, making them easy to distribute and share.

If you're curious to inspect the data, you can simply load the `.db` files into an online viewer such as [SQLite Viewer](https://sqliteviewer.app/) or use the SQLite Viewer extension available in Visual Studio Code. This will allow you to browse the contents of the database files (`database.db`, `backup/database.db`, `backup/initial_fetch.db`) and see the structure and data tables with ease.

This approach ensures that working with the database is as straightforward as possible for developers, contributors, and end-users.

## Possible Future Imporvements
1. Fine-tuning the prompt
2. Add more information such as available sizes
3. More function calling tools to make the AI more aware of air jordans