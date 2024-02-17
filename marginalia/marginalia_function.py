
#A function to apply a threshold of text length.
#Especially useful to enforce reasoning.
def evaluate_length(valid_json, data_scheme, entry):
  for data_element in data_scheme:
    if data_element.field in entry:
      if data_element.min_length is not None:
        if len(entry[data_element.field].split)<=data_element.min_length:
          valid_json = False
  return valid_json

#A function to apply a limitating list of choices
def evaluate_choices(valid_json, data_scheme, entry):
  for data_element in data_scheme:
    if data_element.field in entry:
      if data_element.choice is not None:
        choice_result = re.findall(data_element.choice_regex, entry[data_element.field])
        try:
          choice_result = choice_result.group(1)
          entry[data_element.field] = choice_result
        except:
          valid_json = False
  return valid_json
