import aiohttp

from app.system.config import TOKEN_POLZA

async def request_api(prompt: str, photo_url: str):
    timeout = aiohttp.ClientTimeout(total=300) 
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(
                'https://polza.ai/api/v1/media',
                headers={
                    'Authorization': f'Bearer {TOKEN_POLZA}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'google/gemini-3.1-flash-image-preview',
                    'input': {
                        'prompt': prompt,
                        'images': [{'type': 'url', 'data': photo_url}]
                    }
                }
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.text()
                    print(f"API Error {response.status}: {error_data}")
                    return None
        except Exception as e:
            print(f"Ошибка запроса к API: {e}")
            return None

async def request_gemini_text(prompt: str, photo_url: str):
    """Запрос к модели Gemini для генерации описания по фото (OpenAI compatible)."""
    timeout = aiohttp.ClientTimeout(total=120)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(
                'https://polza.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {TOKEN_POLZA}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'google/gemini-3.1-flash-lite-preview',
                    'messages': [
                        {
                            'role': 'user',
                            'content': [
                                {'type': 'text', 'text': prompt},
                                {
                                    'type': 'image_url',
                                    'image_url': {'url': photo_url}
                                }
                            ]
                        }
                    ]
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    try:
                        return data['choices'][0]['message']['content']
                    except (KeyError, IndexError):
                        return str(data)
                else:
                    error_data = await response.text()
                    print(f"Gemini API Error {response.status}: {error_data}")
                    return None
        except Exception as e:
            print(f"Ошибка запроса к Gemini API: {e}")
            return None