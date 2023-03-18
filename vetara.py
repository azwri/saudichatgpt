import requests

url = "https://experimental.willow.vectara.io/v1/chat/completions"
customer_id = "3420880715"
api = "zqt_y-Z_Sx_8PLQ8B4BSBntixarGSObPGTY12lYwxQ"


def get_respose_vectara(question):
    response = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "customer-id": customer_id,
            "x-api-key": api
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )
    return response.json()['choices'][0]['message']['content']


text = get_respose_vectara("Hello")
print(text)
