from NLPModule.ai.aiExtractor import aiExtractor

def nerExtractor(input: str):
    extracted = aiExtractor(input)
    print(f"Debug nerExtractor: {extracted}")
    return extracted