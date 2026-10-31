# Sign recognition v2: ISL (and ASL) on a Mac M2

Webcam -> MediaPipe (hands + body) -> neural net -> signs -> words -> sentences -> English (Groq)
-> HTTP server on your Mac -> phone, and UDP -> HUD glasses (ESP32-C3 + OLED, see ../docs/interface.md).

HUD glasses (step-by-step: ../docs/run_guide.md): run.py sends every word and finished sentence to the glasses automatically
(glasses.py, UDP to glasses.local:4210 from ../config.yaml). Glasses and Mac must be on the same hotspot.
    python run.py --simulate              # fake sentences -> phone + glasses (no camera/model needed)
    python run.py --glasses 192.168.43.57 # use the IP shown on the OLED if glasses.local does not resolve
    python run.py --no-glasses            # phone/HTTP only
    python glasses.py                     # self-check of the UDP sender (no glasses needed)
The old HTTP-polling ESP sketches (esp/) were dropped; the glasses firmware lives in ../firmware/.

START HERE: open RUNBOOK.md. It is the complete step-by-step guide (install, record your own signs, datasets,
training, live run, ESP32, troubleshooting).

Quick start (details in RUNBOOK.md):

    cd software
    python3.11 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python download_models.py        # one-time MediaPipe models
    python camera_test.py --list     # which camera works
    python selftest.py               # checks the install, expect 11/11
    python collect_data.py --labels idle,hello,thanks --samples 30 --auto
    python train.py --model tcn --epochs 30
    python run.py                    # camera + HTTP server + prints curl commands for phone/ESP
    python run.py --simulate         # test phone/ESP without camera or model

What is in this folder
    RUNBOOK.md               the guide (read this first)
    run.py, start.command    ONE command: weights + HTTP server + live recognition
    server.py, push.py       sentence server (long polling) and the sender used by live_demo.py
    glasses.py               UDP sender to the HUD glasses (words + sentences)
    collect_data.py          record your own signs
    setup_include.py         unzip + check the INCLUDE dataset zips
    prepare_dataset.py       convert photos/videos to training data
    inspect_dataset.py       look at a dataset before converting it
    organize_videos.py       sort CSV/JSON-labelled videos (CISLR ...) into folders
    merge_labels.py          merge duplicate labels (E1/E2 -> E, Hello/hello)
    labelmap_example.json, labelmap_include.json   label maps (include: pronoun I -> me)
    train.py, model.py       training (TCN / BiLSTM / Transformer on the Apple GPU)
    live_demo.py             live recognition with sentences (+ translate.py, sentence.py, fusion.py)
    camera_test.py, download_models.py, check_setup.py, selftest.py   checks and one-time setup
    common.py, labels.py     shared code
    requirements.txt

Folders that appear while you work: data/sequences (your training data), model/ (trained weights),
mp_models/ (MediaPipe models), transcripts/ (saved sentences). Nothing else is needed.
