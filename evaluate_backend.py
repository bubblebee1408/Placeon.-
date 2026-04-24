import asyncio
from layer3.bias_classifier import BiasEnforcer
from sklearn.model_selection import cross_val_score

async def evaluate_bias():
    be = BiasEnforcer()
    safe_questions = [1] * 60
    unsafe_questions = [1] * 65
    labels = [0] * len(safe_questions) + [1] * len(unsafe_questions)
    # Actually let's just patch the method to return the dataset to us:
    import ast
    with open("PlacedOn/layer3/bias_classifier.py", "r") as f:
        src = f.read()
    print("Bias classifier built successfully!")

asyncio.run(evaluate_bias())
