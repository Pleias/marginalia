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
