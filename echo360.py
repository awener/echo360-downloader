import requests
import asyncio
import os 
import sys
import uuid
import logging


class Echo360:

    def __init__(self, main_url):
        self.main_url = main_url
        self.cookies = ""
        self.urls = []

    def save_cookies(self, cookies):
        self.cookies.update((cookie.name, cookie.value) for cookie in cookies)

    def cookie_to_string(self):
        return "; ".join([f"{cookie.name}={cookie.value}" for cookie in self.cookies])

    def visit_main_url(self):
        try:
            request = requests.get(self.main_url, allow_redirects=True)
            self.cookies = request.cookies
            self.get_syllabus_url(request.url)
        except Exception as e:
            logging.error(f"Error: {e}")

    def get_syllabus_url(self, url):
        try:
            syllabus_url = url.split("/home")[0] + "/syllabus"
            req = requests.get(syllabus_url, cookies=self.cookies)
            self.save_cookies(req.cookies)
            self.get_video_urls(req.json())
        except Exception as e:
            logging.error(f"Error: {e}")

    def get_video_urls(self, data):
        try:
            for item in data["data"]:
                if len(item["lesson"]["medias"]):
                    instituion_id = item["lesson"]["lesson"]["institutionId"]
                    lesson_name = item["lesson"]["lesson"]["name"]
                    name = f"{lesson_name}-{uuid.uuid1()}"
                    media_id = item["lesson"]["medias"][0]["id"]
                    url_end = "/1/s0q0.m3u8"
                    self.urls.append({ "video_name": name, "stream_url": "https://content.echo360.org.uk/0000."+instituion_id+"/"+media_id+url_end })
            asyncio.run(self.create_tasks())
        except Exception as e:
            logging.error(f"Error: {e}")

    async def create_tasks(self):
        try:
            tasks = [asyncio.create_task(self.fetch_video(url)) for url in self.urls]
            tasks = [tasks[0]]
            for task in asyncio.as_completed(tasks):
                result = await task
                print("Task complete!")
        except Exception as e:
            logging.error(f"Error: {e}")

    async def fetch_video(self, url):
        try:
            file_name = url["video_name"] + ".mp4"
            stream_url = url["stream_url"]
            command = f"ffmpeg -headers 'Cookie: {self.cookie_to_string()}' -i '{stream_url}' -c copy -bsf:a aac_adtstoasc '{file_name}'"
            os.system(command)
        except Exception as e:
            logging.error(f"Error: {e}")
        

# https://echo360.org.uk/section/128d07a2-30fe-45ff-bae1-e556a3a234a1/public
            
if __name__ == "__main__":
    main_url = sys.argv[1]

    task = Echo360(main_url)
    task.visit_main_url()
