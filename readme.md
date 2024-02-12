# marginalia

marginalia is a lightweight application to perform corpus analysis at scale with open LLMs like Mistral or Llama. With proper instructions, marginalia will transform any list of texts into structured data.

In contrast with other json libraries and frameworks for LLM, marginalia relies on a "brute force" approach that takes advantage of the generation speed of vllm. Depending on the prompt, 5-10% of the generated annotations will not be compliant, either because they are not valid json or because they cannot be unambiguously associated to the original text. marginalia will re-generate every non-compliant data until the output is complete.

Other choices include:
* Sending the pieces of data as "batch" (10 elements by default). Previous trials show that hading more than one sample helps the LLM to identify recurring patterns. It may also speed up text generation.
* Maintaining consistent numeric identifier for text.
* Fully customizable prompt, which is especially needed when working on non-English languages. The best open LLM are heavily English-focused and will tend to return translated results in English if they are not prompted in the languages of the source.

## Example

marginalia works with any list of unstructured texts. It will generate id on the fly simply based on the index of the text, as well as return the unprocessed text as part of the json output.

```python
import pandas as pd

unstructured = pd.read_tsv("franklin_library", sep = "\t")["text"].tolist()
```

marginalia aims to recover *data scheme*. They are creating by initiating a dictionary with fields and their definition. Basically, you want to apply the data scheme to your unstructured set of text everytime fits.

```python
data_scheme = {"titre": "le titre de l'ouvrage",
               "auteur": "le ou les auteurs de l'ouvrage",
               "date": "la date de publication",
               "lieu": "le lieu de publication",
               "editeur": "l'éditeur de l'ouvrage",
               "page": "le nombre de page de l'ouvrage"}
```

The core of marginalia functionality is instruction_set. That's where you are going to pass the unstructured text, the data scheme and the prompt instructions.

```python
instructions = instruction_set(data_scheme = data_scheme,
                               unstructured = unstructured,
                               system_prompt = "Tu es un puissant annotateur de données bibliographiques en français",
                               input_prompt = "Transforme ces différentes notices bibliographiques d'articles ou de chapitres de livres, en données structurées.",
                               definition_prompt = "Extrait les données bibliographiques suivantes :",
                               structure_prompt = "Retourne les résultats sous la forme d'une liste au format json :",
                               data_prompt = "Voici la liste des références :",
                               name_id = "référence",
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

