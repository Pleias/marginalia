class instruction_set:
    def __init__(self, unstructured = None, data_scheme = None, system_prompt=None, input_prompt = None, definition_prompt = None, structure_prompt = None, data_prompt = None, name_id = None, size_batch = None, outputs = None):
        self.unstructured = unstructured
        self.data_scheme = data_scheme
        self.system_prompt = system_prompt
        self.input_prompt = input_prompt
        self.definition_prompt = definition_prompt
        self.structure_prompt = structure_prompt
        self.data_prompt = data_prompt
        self.name_id = name_id
        self.size_batch = size_batch
        self.outputs = outputs

    #Setting the first initial batch on all the data.
    def set_batch(self, unstructured, sep_id = ":"):
      length_unst = len(unstructured)
      list_id_unst = range(0, length_unst)
      dict_unst = {}
      batch_unst = {}
      batch_text = []

      for id_unst in list_id_unst:
        text_unst = unstructured[id_unst]
        dict_unst[id_unst] = text_unst
        if ((id_unst%self.size_batch) == 0) and (id_unst > 0):
          batch_unst_id = id_unst//self.size_batch
          batch_unst[batch_unst_id] = "\n\n".join(batch_text)

          batch_text = [self.name_id + " " + str(id_unst) + sep_id + " " + text_unst]
        else:
          batch_text.append(self.name_id + " " + str(id_unst) + sep_id + " " + text_unst)

      #We also take the last batch once the loop is over
      batch_unst_id = id_unst//self.size_batch
      batch_unst[batch_unst_id] = "\n\n".join(batch_text)

      return dict_unst, batch_unst

    #Setting the batch on a smaller subset of the the data. This will be used for further pass on non-compliant json
    def set_batch_dict(self, dict_unst, sep_id = ":"):
      length_unst = len(dict_unst)
      #We create a new id to calculate the batch.
      list_id_unst = range(0, length_unst)
      batch_unst = {}
      batch_text = []

      #While we iterate over the new id to create the batch, we will use the original ids contained in the dict.
      for id_unst_dict in list_id_unst:
        #Extraction of the original id
        id_unst = list(dict_unst.keys())[id_unst_dict]
        text_unst = dict_unst[id_unst]
        if ((id_unst_dict%self.size_batch) == 0) and (id_unst_dict > 0):
          batch_unst_id = id_unst_dict//self.size_batch
          batch_unst[batch_unst_id] = "\n\n".join(batch_text)

          batch_text = [self.name_id + " " + str(id_unst) + sep_id + " " + text_unst]
        else:
          batch_text.append(self.name_id + " " + str(id_unst) + sep_id + " " + text_unst)

      #We also take the last batch once the loop is over
      batch_unst_id = id_unst//self.size_batch
      batch_unst[batch_unst_id] = "\n\n".join(batch_text)

      return dict_unst, batch_unst

    #Composing the prompt for the LLM. We use type_source = "text" by default. For further pass we take a dict as we need the original ids.
    #Would probably be better to refactor everything with dicts at a later point.
    def json_prompt(self, unstructured, type_source = "text"):

      if type_source == "text":
        dict_unstructured, batch_unstructured = self.set_batch(unstructured)
      else:
        dict_unstructured, batch_unstructured = self.set_batch_dict(unstructured)

      #We programatically define the prompt for the definition of the json (as a list) and an empty outline of the json structure.
      json_definition = []
      json_structure = []

      for k, v in self.data_scheme.items():
          json_definition.append(v + ' ("' + k + '")')
          json_structure.append('"' + k + '": "…"')

      json_definition = self.definition_prompt + " " + ", ".join(json_definition)
      json_structure = self.structure_prompt + ' {"id": "…", ' + ", ".join(json_structure) + "}"

      prompt = f'<|im_start|>system\n{self.system_prompt}\n<|im_end|>\n<|im_start|>user\n{self.input_prompt}\n\n{json_definition}\n\n{json_structure}\n\n{self.data_prompt}\n\n'

      prepared_prompts = []

      for batch_id, batch_entry in batch_unstructured.items():
        prepared_prompts.append(prompt + str(batch_entry) + "\n\n" + "<|im_end|>\n<|im_start|> assistant\n")

      return dict_unstructured, batch_unstructured, prepared_prompts

    #We only check if the id is missing, as sometime not only is the json not compliant, but the LLM will generate nothing.
    def validate_json(self, dict_unstructured):
      import re
      valid_id = []
      available_json = []
      missing_json = []

      for batch_instruction in self.generated:
        entries = re.findall(r"\{.+?\}", batch_instruction, re.DOTALL)
        for entry in entries:
          validate_json = validateJSON(entry)
          if validate_json:
            entry = json.loads(entry)
            if "id" in entry:
              id_entry = entry["id"]
              if id_entry.isnumeric():
                valid_id.append(id_entry)
                entry["original_source"] = self.dict_unstructured[int(id_entry)]
              self.valid_json.append(entry)

      for available_id in dict_unstructured:
        available_id = str(available_id)
        if available_id not in valid_id:
          missing_id_element = dict_unstructured[int(available_id)]
          self.missing_id[int(available_id)] = missing_id_element

    #Small function to get the generated text by the LLM without all the other info returned by vllm.
    def extract_generated_text(self, generations):
      text_generated = []
      for output in generations:
          prompt = output.prompt
          generated_text = output.outputs[0].text
          text_generated.append(generated_text)
      self.generated = text_generated

    #The core function to have a generating loop.
    def llm_generate_loop(self, llm, sampling_params):

      self.dict_unstructured, self.batch_unstructured, prompts = self.json_prompt(self.unstructured)

      print("A sample of the prompt:\n", prompts[0])
      self.valid_json = []
      self.missing_id = {}

      #The initial generation on all the data
      generations = llm.generate(prompts, sampling_params)
      self.extract_generated_text(generations)

      #We retrieve the valid json.
      self.validate_json(self.dict_unstructured)

      #We check whether some entries are missing or not to decide whether we continue the loop.
      if len(self.missing_id) > 0:
        json_to_validate = True
      else:
        json_to_validate = False

      run_id = 1

      #The actual loop.
      while(json_to_validate):
        dict_unstructured, batch_unstructured, prompts = self.json_prompt(self.missing_id, type_source = "dict")

        generations = llm.generate(prompts, sampling_params)
        self.missing_id = {}
        self.extract_generated_text(generations)

        self.validate_json(dict_unstructured)

        if len(self.missing_id) > 0:
          json_to_validate = True
        else:
          json_to_validate = False