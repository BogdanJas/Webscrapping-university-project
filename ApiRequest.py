from config import OPENAITOKEN
from openai import OpenAI

client = OpenAI(
    api_key=OPENAITOKEN,
)


def request_to_openAI(request_to_AI):
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""Create a short twitter comment written from the 3rd person for the following text: {request_to_AI}.
                                \nYou can use any emojis. Please don't use no links or hashtags. Comment should be short, no longer than 10 words.
                                It can contains maximum 2 sentences.
                                \nImprove the writing, keeping the reading level on the 6-7th grade level, 
                                so everything is clear for both non-native and native English speakers."""
                }
            ],
            model="gpt-3.5-turbo",
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
