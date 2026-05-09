import os
import time
from youtube_transcript_api import YouTubeTranscriptApi

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_video_id(url):
    return url.split("v=")[1].split("&")[0]


def download_transcript(video_url, lang="vi", translate_to=None):
    video_id = get_video_id(video_url)
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        if translate_to:
            transcript = transcript_list.find_transcript([lang])
            translated = transcript.translate(translate_to)
            fetched = translated.fetch()
            suffix = f"{translate_to}_from_{lang}"
        else:
            transcript = transcript_list.find_transcript([lang])
            fetched = transcript.fetch()
            suffix = lang

        text = " ".join([entry.text for entry in fetched.snippets])
        output_file = os.path.join(OUTPUT_DIR, f"transcript_{video_id}_{suffix}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Da tai: {output_file}")
        print(f"So ky tu: {len(text)}")
    except Exception as e:
        print(f"Loi: {e}")


if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=Saa2qY7G5Rs"

    print("=== Tieng Viet (goc) ===")
    download_transcript(url, lang="vi")

    print("\nDoi 5 giay de tranh bi chan...")
    time.sleep(5)

    print("\n=== Tieng Anh (dich tu tieng Viet) ===")
    download_transcript(url, lang="vi", translate_to="en")
