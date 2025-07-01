# Handwritten Notes OCR Sync
This project converts handwritten notes into searchable digital text using OCR (Optical Character Recognition) and automatically syncs them across devices.
Other solutions like this exist, but this one can be run fully locally, so you dont have to send your personal notes to some random server.
The main logic is in the `ocr.py` script.
It performs the OCR by running the Florence2 model from Microsoft.
The `ocr.py` script runs indefinitely, and monitors an input folder waiting for new images to appear that can be processed.
There is also a service file to automatically run the script, but this contains placeholders that will have to be changed.

## Why OCR for Handwriting?
I prefer working with handwritten notes, but find the fact that they are not searchable a big drawback at times. Handwritten notes are often faster to create but difficult to organize and find later. By running OCR on photos of handwritten notes, the note content becomes digital (and so also searchable) right from the note taking app I am using already anyway (Obsidian). This means you can quickly find specific notes by searching for keywords, even if they were originally written by hand.
This also means for this setup, OCR does not need to be 100% correct. If it gets like 90% of the characters right it should still be possible to easily find the notes you are looking for, and then you can always refer to the original. The original possibly contains diagrams or other drawings as well, so I think reading a picture of the original is always going to be preferred anyway.

## Why the Syncing Setup?
Its just the easiest way I could think of for sending messages between my phone, server, and notes app.
It takes a bit of setup, but aftewards everything is taken care of, including authentication which I didnt want to bother with.
As an added bonus, this setup works even if the server is connected to your local home network and not publicly reachable.

Here is a diagram of how I have set everything up for my setup.
In the end you need 3 syncthing instances: one on your phone, on on the server and one on the device where you want the notes to be sent (like a laptop probably).
You will need 2 separately shared folders, one to send the images from your phone to, and one to send the digitized version of the notes to.
See the diagrams below for an overview of how it all works:
```
┌─────────────────────────────────────────────────────┐
│                SYNCTHING SETUP                      │
└─────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    PHONE    │    │   SERVER    │    │ WORK LAPTOP │
│             │    │             │    │             │
│┌───────────┐│    │┌───────────┐│    │┌───────────┐│
││Syncthing  ││    ││Syncthing  ││    ││Syncthing  ││
││Instance 1 ││    ││Instance 2 ││    ││Instance 3 ││
│└───────────┘│    │└───────────┘│    │└───────────┘│
│             │    │             │    │             │
│Photos App   │    │OCR Script   │    │Obsidian     │
│┌───────────┐│    │┌───────────┐│    │┌───────────┐│
││  Camera   ││    ││  ocr.py   ││    ││   Notes   ││
││ Pictures  ││    ││(monitors, ││    ││    &      ││
│└───────────┘│    ││OCR,output)││    ││ Markdown  ││
└─────────────┘    │└───────────┘│    │└───────────┘│
       │           └─────────────┘    └─────────────┘
       │                   │                   │
       │                   │                   │
       │  SHARED FOLDER 1  │                   │
       │   (Raw Images)    │                   │
       └───────────────────┘                   │
                           │                   │
                           ▼                   │
                  ┌─────────────────┐          │
                  │ /images-input/  │          │
                  │                 │          │
                  │ Raw photos from │          │
                  │ phone stored    │          │
                  └─────────────────┘          │
                           │                   │
                           ▼                   │
                  ┌─────────────────┐          │
                  │     ocr.py      │          │
                  │                 │          │
                  │ • Monitor folder│          │
                  │ • Run OCR model │          │
                  │ • Generate MD   │          │
                  │ • Move files    │          │
                  └─────────────────┘          │
                           │                   │
                           ▼                   │
                  ┌─────────────────┐          │
                  │/processed-out/  │          │
                  │                 │          │
                  │• Markdown files │          │
                  │• Original imgs  │          │
                  └─────────────────┘          │
                           │                   │
                           │ SHARED FOLDER 2   │
                           │(Processed Files)  │
                           └───────────────────┘

WORKFLOW:
═════════

1.   PHONE → SERVER:
   • Take photos of handwritten notes
   • Share via Syncthing to /images-input/

2.   SERVER PROCESSING:
   • ocr.py monitors /images-input/
   • Runs OCR on new images
   • Generates markdown + moves to /processed-out/

3.   SERVER → LAPTOP:
   • Syncthing syncs processed files
   • Files appear in Obsidian vault
   • Creates backup on both devices

COMPONENTS:
═══════════
• 1 script: ocr.py (monitoring + OCR + file management)
• 2 shared folders: raw images, processed files  
• 3 Syncthing instances: phone, server, laptop
```
