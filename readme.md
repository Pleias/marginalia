# marginalia

<img src="https://raw.githubusercontent.com/Pleias/marginalia/main/notebook/marginalia_logo.jpg" style="float:right;" alt="marginalia logo"  width="300"/>


marginalia is a lightweight application to perform corpus analysis at scale with open LLMs like Mistral or Llama. With proper instructions, marginalia will transform any list of texts into structured data.

In contrast with other json libraries and frameworks for LLM, marginalia relies on a "brute force" approach that takes advantage of the generation speed of vllm. Depending on the prompt, 5-10% of the generated annotations will not be compliant, either because they are not valid json or because they cannot be unambiguously associated to the original text. marginalia will re-generate every non-compliant data until the output is complete.

Other choices include:
* Sending the pieces of data as "batch" (10 elements by default). Previous trials show that hading more than one sample helps the LLM to identify recurring patterns. It may also speed up text generation.
* Maintaining consistent numeric identifier for text.
* Fully customizable prompt, which is especially needed when working on non-English languages. The best open LLM are heavily English-focused and will tend to return translated results in English if they are not prompted in the languages of the source.

## Setting up marginalia

marginalia works with any list of unstructured texts. It will generate id on the fly simply based on the index of the text, as well as return the unprocessed text as part of the json output.

```python
import pandas as pd

unstructured = pd.read_tsv("franklin_library", sep = "\t")["text"].tolist()
```

marginalia aims to recover *data scheme*. They are creating by initiating a dictionary with fields and their definition. Basically, you want to apply the data scheme to your unstructured set of text everytime fits.

```python
data_scheme = {"identifier": "the number of the reference",
               "title": "the title of the book",
               "author": "the author(s) of the book",
               "translator": "the translator(s) of the book",
               "date": "the date of publication",
               "place": "the place of publication",
               "format": "any information related to the format such as volumes, folios",
               "other": "any other information related to the book"}
```

The core of marginalia functionality is instruction_set. That's where you are going to pass the unstructured text, the data scheme and the prompt instructions.

```python
instructions = instruction_set(data_scheme = data_scheme,
                               unstructured = unstructured,
                               system_prompt = "You are a powerful annotator of bibliographic data",
                               input_prompt = "Transform this list of book entries into structured bibliographic data",
                               definition_prompt = "Extract the following bibliographic fields:",
                               structure_prompt = "Return the results as a json structured like this :",
                               data_prompt = "Here is the list of books :",
                               name_id = "book",
                               size_batch = 10)
```

As you can notice the prompt as six parts:
* System prompt: basically defining what kind of the tool LLM is, in a very broad way.
* Input prompt: the actual task at hand.
* Definition prompt: the introductory prompt for the list of definitions stored in the data scheme.
* Structure prompt: the introductory prompt for an empty sample of the json structure.
* Data prompt: the introductory prompt for the list of unstructured text sample.
* Name id: the name used to qualify each unstructured text sample

Additionally you can define the size of the batch with a size_batch. Overall the longer your text sample are, the smaller your batch should be to not overload the context window.

Before launching the actual LLM-powered annotation, it is advisable to give a look the data and check if everything is fine. You can do it with test_prompt:

```python
instructions.test_prompt()
print(instructions.prompts[0])
```

Which should return something like:

```text
<|im_start|>system
You are a powerful annotator of bibliographic data
<|im_end|>
<|im_start|>user
Transform this list of book entries into structured bibliographic data

Extract the following bibliographic fields: the title of the book ("title"), the author(s) of the book ("author"), the translator(s) of the book ("translator"), the date of publication ("date"), the place of publication ("place"), any information related to the format such as volumes, folios ("format"), any other information related to the book ("other")

Return the results as a json structured like this : {"id": "…", "title": "…", "author": "…", "translator": "…", "date": "…", "place": "…", "format": "…", "other": "…"}

Here is the list of books :

book 0: 1 FINE large Folio BIBLE, compleat, Oxford 1727.

book 1: 2 Ditto, with Maps, Notes, &c.

book 2: 3 Clarendon's History of the Rebellion, 3 Vols

(…)
<|im_end|>
<|im_start|> assistant
```

## Annotation with vllm

Then to use the LLM, you need to load it with vllm. The notebook provide a tested solution for Google Colab but do not hesitate to check the vllm documentation:
```python
from vllm import LLM, SamplingParams
import os
new_model_name = "mistral-7b-hermes-2.5"

llm = LLM(new_model_name)

sampling_params = SamplingParams(temperature=0.7, top_p=0.95, max_tokens=8000, presence_penalty = 0)
```

At this point, the actual annotation is one command:

```python
instructions.llm_generate_loop(llm, sampling_params)
```

You'll notice that marginalia does several pass on vllm to send again any non-compliant json.

By the end of this process you can check your json:

```python
instructions.valid_json
```

With the library of Benjamin Franklin it should look like this:

```json
{'id': 'book 3',
  'author': 'Bayley',
  'title': 'universal etimologlcal Dictionary',
  'translator': '',
  'date': '1727',
  'place': 'Oxford',
  'format': '',
  'other': ''},
 {'id': 'book 4',
  'author': 'Marlorati',
  'title': 'Thesaurus Scripturae',
  'translator': '',
  'date': '1727',
  'place': 'Oxford',
  'format': '',
  'other': ''},
 {'id': 'book 5',
  'author': 'Wiquefort',
  'title': 'compleat Ambassador',
  'translator': 'Digby',
  'date': '1727',
  'place': 'Oxford',
  'format': '',
  'other': 'finely bound'}
```

LLM a both flexible and sensitive tools, so you should not hesitate to tweak and the prompt several times, preferably on a smaller sample of the data until you find the most workable setting.

