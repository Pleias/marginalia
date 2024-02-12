# marginalia

marginalia is a lightweight application to perform corpus analysis at scale with open LLMs like Mistral or Llama. With proper instructions, marginalia will transform any list of texts into structured data.

In contrast with other json libraries and frameworks for LLM, marginalia relies on a "brute force" approach that takes advantage of the generation speed of vllm. Depending on the prompt, 5-10% of the generated annotations will not be compliant, either because they are not valid json or because they cannot be unambiguously associated to the original text.

* 
