
#A function to apply a threshold of text length.
#Especially useful to enforce reasoning.
def evaluate_data_conformity(valid_json, data_scheme, entry):
  import re
  for data_element in data_scheme:
    if data_element.field in entry:
      
      #Evaluation 1: length
      if data_element.min_length is not None:
        if len(entry[data_element.field].split())<=data_element.min_length:
          valid_json = False

      #Evaluation 2: choices
      if data_element.choice is not None:
        choice_result = re.findall(data_element.choice_regex, entry[data_element.field].lower())
        if len(choice_result) > 0:
          choice_result = choice_result[0]
          entry[data_element.field] = choice_result
        else:
          valid_json = False
  return entry, valid_json
