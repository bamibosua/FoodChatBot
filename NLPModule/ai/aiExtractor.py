from .client import generate_response
from .promptBuilder import buildAiExtractorPrompt

def aiExtractor(input):
    prompt = buildAiExtractorPrompt(input)

    system_instr = "You are a NER extractor, extracting entities in the {input}"
    return generate_response(prompt, system_instr)