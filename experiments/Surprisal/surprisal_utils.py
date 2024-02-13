import torch
import torch.nn.functional as F
import json


def token_surprisal(logits, token_id, token_index):
    # Compute the surprisal
    surprisal = -torch.log_softmax(logits,dim=-1).squeeze(0)[token_index][token_id]
    return surprisal.item()

def load_foils(json_path):
    foils = []
    with open(json_path, 'r') as f:
        data = json.load(f)
    foils=[sample['foil_active'] for sample in data.values()]
    return foils

def compute_surprisal(sentences,tokenizer,model):
    # Initialize the list to store the surprisal values
    surprisal_scores = []
    # Iterate through the dataset
    for sent in sentences:
        word_surprisals=[]
        # Tokenize the input
        input_ids = torch.tensor(tokenizer.encode(sent,add_special_tokens=True)).unsqueeze(0)
        mask_indexes=torch.arange(1,len(input_ids[0])) #remove the beginning and end of sentence tokens
        for index in mask_indexes:
            token_id=input_ids[0][index]
            masked_input_ids=input_ids.clone()
            # Forward pass to compute the layer outputs
            masked_input_ids[0][index] = tokenizer.convert_tokens_to_ids(['[MASK]'])[0]
            with torch.no_grad():
                outputs = model(masked_input_ids)
                logits = outputs.logits
            # Compute the surprisal
            surprisal = token_surprisal(logits, token_id, index)
            word_surprisals.append(surprisal)
        surprisal_scores.append(sum(word_surprisals)/len(word_surprisals))

    return surprisal_scores