import json
import os

DATA_PATH = os.path.join("data","career_tree.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    CAREER_DB = json.load(f).get("careers", {})

# Map quiz answers/path items to tags (extendable)
default_mapping = {
    'Photography': ['creative','visual','field-work'],
    'Editing/Studio': ['creative','design'],
    'Outdoor/Field': ['field-work','visual'],
    'Culinary': ['creative','hands-on','hospitality'],
    'Cooking': ['hands-on','creative'],
    'Baking': ['hands-on','creative'],
    'Management': ['management','business'],
    'Horticulture': ['biology','outdoors','environment'],
    'Labs': ['lab','science'],
    'Farm Work': ['outdoors','agriculture'],
    'Engineering': ['maths','technology','logical'],
    'Computers': ['technology','logical'],
    'Medicine': ['biology','helping','science'],
    'Allied Health / Paramedical': ['health','lab','service']
}

def tags_from_path(path):
    tags=[]
    for p in path:
        if p in default_mapping:
            tags.extend(default_mapping[p])
    return list(set(tags))

def score_and_recommend(user_tags):
    scores=[]
    for career, info in CAREER_DB.items():
        career_tags = info.get("tags",[])
        score = len(set(user_tags)&set(career_tags))
        scores.append((career, score))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    if not scores:
        return None, []
    # best single recommendation
    best, best_score = scores[0]
    if best_score==0:
        # fallback: choose first career with non-empty tags or top scored
        return scores[0][0], scores
    return best, scores

def explain_recommendation(career, user_tags):
    info = CAREER_DB.get(career, {})
    overlap = list(set(user_tags)&set(info.get("tags",[])))
    if overlap:
        return f"We recommend **{career}** because your interests match: {', '.join(overlap)}."
    else:
        return f"We recommend **{career}** as a good fit based on your quiz responses."
