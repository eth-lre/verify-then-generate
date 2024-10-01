import time
from typing import List, Dict
import openai
from config import MODEL_MAPPING, ModelConfig


class PrompterAPI(object):
    def __init__(self, model: str, debug: bool = False):
        # "gpt-3.5-turbo-1106", "meta-llama/Llama-2-70b-chat-hf"
        # "gpt-3.5-turbo-instruct", "meta-llama/Llama-2-70b-hf"
        # Instruct, Chat
        self.model_config: ModelConfig = MODEL_MAPPING.get(model, None)
        if self.model_config is None:
            print(f"Invalid model.")
            exit(1)

        self.debug = debug

        if self.model_config.is_llama:
            openai.api_key = "EMPTY"
            openai.api_base = "http://localhost:8000/v1"

    def generate(self, messages: List[Dict], system_prompt: str, stop: List[str], max_tokens=350):
        """
        :param messages: Expects assistant and user messages as roles, e.g. [{"role": "user", "content": "What is 2+2?"}, {"role": "assistant", "content": "4"}]
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
                    # Preprocess messages for chat model with teacher being assistant
                    system_prompt = system_prompt.replace("[conversation]", "\n".join(
                        [turn["user"] + ": " + turn["text"] for turn in messages]))
                    messages = []
                    if self.model_config.is_llama:
                        response = openai.ChatCompletion.create(
                            model=self.model_config.id,
                            messages=[{"role": "system", "content": self.model_config.prompt_format.format(prompt=system_prompt)}, *messages],
                            temperature=0.0,
                            max_tokens=max_tokens,
                            stop=stop,
                        )
                    else:
                        response = openai.ChatCompletion.create(
                            model=self.model_config.id,
                            messages=[{"role": "system", "content": self.model_config.prompt_format.format(prompt=system_prompt)}, *messages],
                            temperature=0.0,
                            max_tokens=max_tokens,
                            presence_penalty=0,
                            frequency_penalty=0,
                            stop=stop,
                            timeout=10,
                        )
                    parsed_response = response.choices[0]["message"]["content"]

                elif self.model_config.type == "instruct":
                    # Append conversation to the prompt
                    system_prompt = system_prompt.replace("[conversation]", "\n".join(
                        [turn["user"] + ": " + turn["text"] for turn in messages]))
                    if self.model_config.is_llama:
                        completion = openai.Completion.create(model=self.model_config.id,
                                                              prompt=self.model_config.prompt_format.format(
                                                                  prompt=system_prompt),
                                                              temperature=0.0,
                                                              max_tokens=max_tokens,
                                                              stop=stop+["Teacher:", "teacher:", "###"],
                                                              )
                    else:
                        completion = openai.Completion.create(model=self.model_config.id,
                                                              prompt=self.model_config.prompt_format.format(
                                                                  prompt=system_prompt),
                                                              temperature=0.0,
                                                              max_tokens=max_tokens,
                                                              stop=stop,
                                                              timeout=10
                                                              )
                    parsed_response = completion.choices[0].text.strip()

                if self.debug:
                    print("=============INPUT=======================")
                    print("Messages:")
                    print(messages)
                    print(system_prompt)
                    print("=============OUTPUT=======================")
                    print("#########RAW RESPONSE###########################")
                    print(parsed_response)
                    print("####################################")
                return parsed_response
            except Exception as e:
                print("Model error", e)
