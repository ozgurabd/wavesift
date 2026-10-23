# WaveSift

WaveSift is a local CLI tool that downloads the best available YouTube audio stream and converts it to MP3. It runs in Docker and writes the resulting files to a folder on your computer. The video stream is not downloaded.

## Requirements

- Docker Desktop, or Docker Engine with the Docker Compose plugin

Python, `yt-dlp`, FFmpeg, and `ffprobe` are installed in the container.

## Choose the output folder

By default, MP3 files are saved to the project's `downloads/` folder. To use another folder, create a `.env` file in the project directory and set `OUTPUT_DIR` to an absolute path on your computer:

```dotenv
OUTPUT_DIR=/Users/yourname/Music/YouTube Audio
```

On Windows, use a path such as:

```dotenv
OUTPUT_DIR=C:/Users/yourname/Music/YouTube Audio
```

The selected computer folder is mounted inside the container at `/output`.

## Build and run

Build the image once:

```bash
docker compose build
```

Download a video as MP3:

```bash
docker compose run --rm wavesift -o /output "https://www.youtube.com/watch?v=VIDEO_ID"
```

Pass multiple URLs to process them sequentially:

```bash
docker compose run --rm wavesift -o /output "https://youtu.be/VIDEO_ID_1" "https://www.youtube.com/watch?v=VIDEO_ID_2"
```

To enter URLs interactively, start the CLI without URLs:

```bash
docker compose run --rm wavesift -o /output
```

The `--quality` value ranges from 0 to 10; 0 is the best VBR quality setting:

```bash
docker compose run --rm wavesift -o /output --quality 0 "https://youtu.be/VIDEO_ID"
```

The default output directory is `./downloads` when `OUTPUT_DIR` is not set. Increasing the video's resolution does not improve its audio quality. MP3 conversion cannot improve the source audio; it preserves the quality available from YouTube as closely as possible.

## Note

Only download content that you own or are authorized to download, and follow YouTube's terms of service and applicable local laws.
