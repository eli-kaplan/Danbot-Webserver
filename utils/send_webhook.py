import json

import requests
from discord import SyncWebhook, File, Embed


def send_webhook(url, title, description, color, image):
    """
    Send a webhook to the specified URL with an embed and an image file.

    :param url: The URL to which the webhook should be sent.
    :param title: The title of the embed.
    :param description: The description of the embed.
    :param color: The color of the embed.
    :param image_file: (Optional) The FileStorage object containing the image to be sent.
    """
    # Assuming 'image_file' is a SpooledTemporaryFile object from Flask's request.files
    image.save('lootImage.png')

    embeds = [
        {
            'title': title,
            'color': color,
            'description': description,
            'image': {
                'url': 'attachment://lootImage.png'
            }
        }
    ]

    if image is not None:
        with open("lootImage.png", "rb") as imageData:
            files = {
                'file': ('lootImage.png', imageData, 'image/png')
            }

            payload = {
                'embeds': embeds
            }

            requests.post(url, data = {'payload_json': json.dumps(payload)}, files=files)
    else:
        payload = {
            'embeds': embeds
        }

        requests.post(url, data = {'payload_json': json.dumps(payload)})
