# marginalia

marginalia is a lightweight application to perform corpus analysis at scale with open LLMs like Mistral or Llama. With proper instructions, marginalia will transform any list of texts into structured data.

In contrast with other json libraries and frameworks for LLM, marginalia relies on a "brute force" approach that takes advantage of the generation speed of vllm. Depending on the prompt, 5-10% of the generated annotations will not be compliant, either because they are not valid json or because they cannot be unambiguously associated to the original text. marginalia will re-generate every non-compliant data until the output is complete.

Other choices include:
* Sending the pieces of data as "batch" (10 elements by default). Previous trials show that hading more than one sample helps the LLM to identify recurring patterns. It may also speed up text generation.
* Maintaining consistent numeric identifier for text.
* Fully customizable prompt, which is especially needed when working on non-English languages. The best open LLM are heavily English-focused and will tend to return translated results in English if they are not prompted in the languages of the source.

## Example

