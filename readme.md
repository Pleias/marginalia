# marginalia

<p align="center">
<img src="https://raw.githubusercontent.com/Pleias/marginalia/main/notebook/marginalia_logo.jpg" alt="marginalia logo" width="300"/>
</p>

**marginalia** is an opinionated python library for structured data generation at scale with open LLMs like Mistral or Llama. With proper instructions, marginalia will transform any list of texts into structured data.

The easiest way to discover marginalia is to test the associated Google Colab notebook for [data extraction](https://colab.research.google.com/drive/1xKjK2mDDpXMaKG5YLpFhOM7jehxt0kEt?usp=sharing) or [text classification](https://colab.research.google.com/drive/1dMcldrZtootOyRmC_Ug5552iy9T4e-0c?usp=sharing). Notice that for now you will need to use an A100 GPU (recommended in any case for larger scale corpus analysis with vllm).

In contrast with other json libraries and frameworks for LLM, marginalia does not rely on *controlled generation* but on *bootstrap generation*: instead of selecting LLM output at the token level, marginalia retain or reject entire generation.

marginalia is closely integrated with vllm, and takes advantage of its generation speed. Depending on the prompt and the data constraints, a significant share of the generated annotations will not be compliant, either because they are not valid json, because they cannot be unambiguously associated to the original text or because they fail to satisfy some explicit conditions. marginalia will re-generate every non-compliant data until the output is complete.

Other choices include:
* Sending the pieces of data as "batch" (10 elements by default). Previous trials show that hading more than one sample helps the LLM to identify recurring patterns. It may also speed up structured data generation.
* Maintaining consistent numeric identifier for text.
* Fully customizable prompt, which is especially needed when working on non-English languages. The best open LLM are heavily English-focused and will tend to return translated results in English if they are not prompted in the languages of the source.
* Support for open weights LLM by default with vllm. ChatGPT and other API-only solution may be integrated at some point in the future, but they are generally not meeting the requirements for running at scale.

## Data analysis

marginalia works with any list of unstructured texts. It will generate id on the fly simply based on the index of the text, as well as return the unprocessed text as part of the json output.

marginalia aims to recover *data scheme*. They are creating by initiating a list of *data entity* objects with fields, definitions and data constraints. Basically, you want to apply the data scheme to your unstructured set of text everytime fits.

While they need to be used carefully and in close accordance with the prompt, data constraints are powerful tool to ensure the LLM will generate the data that match your expectations. For now, marginalia support two constraints:
* **choices**: a limited range of options for the answer. If it exists, the compliant answer will be extracted by marginalia using a regex.
* **answer length**: a threshold in a number of words for the answer. This is especially practical when you want to add a free-commenting field.

```python
data_scheme = [data_entity(field = "reference_evaluate",, 
                           definition = "argument whether answering the question is about knowledge and require some references rather than a task like translation, with a few concise sentences",
                           min_length = 7),
               data_entity(field = "reference_result",
                           definition = "indicate by yes, no or non applicable if references are needed",
                           choice = ["yes", "no", "non applicable"])]
```
In this example we use both constraints for two different fields:
* "reference_evaluate": has to be a text with at least 7 words.
* "reference_result" has to be a binary answer ("yes" or "no") as well as the option or not being applicable, for instance due to the analysis not being conclusive.

Strong data constraints and unsufficiently clear prompts will result in the dataset not being fully annotated.

## Data conversion

marginalia can also convert unstructured texts into a structured data format.

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

```text
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

