import dataclasses
import time
from typing import List
import openai


@dataclasses.dataclass
class ModelConfig:
    id: str
    type: str
    is_llama: bool = False


MODEL_MAPPING = {
    "gpt3": ModelConfig(
        id="gpt-3.5-turbo-1106",
        type="chat",
        is_llama=False,
    ),
    "gpt3-instruct": ModelConfig(
        id="gpt-3.5-turbo-instruct",
        type="instruct",
        is_llama=False,
    ),
    "llama2_70b_chat": ModelConfig(
        id="meta-llama/Llama-2-70b-chat-hf",
        type="chat",
        is_llama=True,
    ),
    "llama2_70b": ModelConfig(
        id="meta-llama/Llama-2-70b-hf",
        type="instruct",
        is_llama=True,
    ),
    "llama3_70b": ModelConfig(
        id="meta-llama/Meta-Llama-3-70B-Instruct",
        type="instruct",
        is_llama=True,
    ),
}


class PrompterAPI(object):
    def __init__(self, model: str, debug: bool = False):
        self.model_config = MODEL_MAPPING.get(model, None)
        if self.model_config is None:
            print(f"Invalid model.")
            exit(1)

        self.debug = debug

        if self.model_config.is_llama:
            openai.api_key = "EMPTY"
            openai.api_base = "http://localhost:8000/v1"

    def generate(self, system_prompt: str, stop: List[str], max_tokens=256):
        """
        :param system_prompt:
        :param stop: Stop tokens to stop the generation
        :return:
        """
        retries = 0
        while True:
            try:
                if retries > 0:
                    print("sleeping for 1 second") if self.debug else None
                    time.sleep(1)
                retries += 1

                if self.model_config.type == "chat":
                    if self.model_config.is_llama:
                        response = openai.ChatCompletion.create(
                            model=self.model_config.id,
                            messages=[{"role": "system", "content": system_prompt}],
                            temperature=0.0,
                            max_tokens=max_tokens,
                            stop=stop,
                        )
                    else:
                        response = openai.ChatCompletion.create(
                            model=self.model_config.id,
                            messages=[{"role": "system", "content": system_prompt}],
                            temperature=0.0,
                            max_tokens=max_tokens,
                            presence_penalty=0,
                            frequency_penalty=0,
                            stop=stop,
                            timeout=10,
                        )
                    parsed_response = response.choices[0]["message"]["content"]

                elif self.model_config.type == "instruct":
                    if self.model_config.is_llama:
                        completion = openai.Completion.create(model=self.model_config.id,
                                                              prompt=system_prompt,
                                                              temperature=0.0,
                                                              max_tokens=max_tokens,
                                                              stop=stop
                                                              )
                    else:
                        completion = openai.Completion.create(model=self.model_config.id,
                                                              prompt=system_prompt,
                                                              temperature=0.0,
                                                              max_tokens=max_tokens,
                                                              stop=stop,
                                                              timeout=10
                                                              )
                    parsed_response = completion.choices[0].text.strip()

                if self.debug:
                    print("=============INPUT=======================")
                    print(system_prompt)
                    print("=============INPUT=======================")
                    print("#########RAW RESPONSE###########################")
                    print(parsed_response)
                    print("####################################")
                return parsed_response
            except Exception as e:
                print("Model error", e)
