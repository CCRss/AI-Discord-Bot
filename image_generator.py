from datetime import datetime
from PIL import Image
import io
import base64
import aiohttp
import os


async def generate_image(message_content):
    url = os.getenv('GRADIO_URL') # here is an api link, like 

    option_payload = {
        "sd_model_checkpoint": "breakdomain.safetensors [0db3c9cf4a]", #Check "civitai.com" for more models # breakdomain.safetensors [0db3c9cf4a] abyssorangemix3AOM3_aom3a1b.safetensors [5493a0ec49]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url=f'{url}/sdapi/v1/options', json=option_payload) as response:
            print("Request completed successfully") if response.status == 200 else print(f"Произошла ошибка: {response.status}")

        high_quality_prompt = "masterpiece, best quality, ultra high res, beautiful, "
        negative_prompt_message = "NSFW, (worst quality, low quality:1.3), badhandv5, bad_quality, easynegative"
        loras_prompt = (' <lora:animeoutlineV4_16:0.9>,') #<lora:animeoutlineV4_16:1>

        payload = {
            # add comment below if you want to get high quality images, its just will take more time to make it, and required better GPU 
            "enable_hr": True, "denoising_strength": 0.7, "hr_scale": 2, "hr_upscaler": "R-ESRGAN 4x+",
            "prompt": high_quality_prompt + message_content + loras_prompt,
            "steps": 20,
            "cfg_scale": 10,
            "width": 512,
            "height": 512,
            "negative_prompt": negative_prompt_message,
            "sampler_name": "DPM++ 2M Karras",
            "sampler_index": "k_dpmpp_2m_ka",
        }

        async with session.post(url=f'{url}/sdapi/v1/txt2img', json=payload) as response:
            r = await response.json()

        for i in r['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
            timestamp = datetime.now().strftime(f"%Y%m%d-%H%M%S")  # Retrieve data and time -> convert to str 
            saved_image_path = f'sd_images/{timestamp}.png'  # Save image
            image.save(saved_image_path)
        
        return saved_image_path