
# OFTS-Cli

A simple Google photos alternative that runs inside your terminal. This project uses DeepFace to recognize faces and Microsoft's GIT to caption the images.



### NOTE: If you need a professional Google Photos alternative, use [LibrePhotos](https://github.com/LibrePhotos/librephotos) or [immich](https://github.com/immich-app/immich). This project is just for fun.

## Requirements
- kitty

## Demo
[DEMO HERE](https://imgur.com/a/teQ5r4q)


## Installation

Clone this repo
```bash
git clone https://github.com/yashasnadigsyn/ofts-cli
cd ofts-cli
```

Create a virtual environment
```bash
python3 -m venv OFTS_CLI_VENV
source OFTS_CLI_VENV/bin/activate
```

Install the packages
```bash
pip install -r requirements.txt
```

Run it 
```bash
python3 ofts_cli.py
```



    
## TODO

- Videos.
- Use [insightface](https://github.com/deepinsight/insightface) and DBSCAN like [immich](https://immich.app/docs/features/facial-recognition/#how-facial-recognition-works) does.
- Use vector search instead of sqlite3 FTS
- Use other captioning models ([florence-ft](https://huggingface.co/microsoft/Florence-2-base-ft))
- Run on other terminals ([ueberzugpp](https://github.com/jstkdng/ueberzugpp))


## License

[MIT](https://choosealicense.com/licenses/mit/)


