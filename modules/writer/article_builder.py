from writer.templates import (
    INTRO_TEMPLATES,
    ANALYSIS_TEMPLATES,
    OPINION_TEMPLATES,
    TRANSITION_TEMPLATES,
    PREDICTION_TEMPLATES,
    CONCLUSION_TEMPLATES
)
from writer.memory import HumanMemory
from writer.angles import pick_angle

memory = HumanMemory()

def pick_unique(templates):
    return memory.pick_unique(templates)

def build_article(selected_items):
    article = []

    article.append(pick_unique(INTRO_TEMPLATES))
    article.append("")

    for index, item in enumerate(selected_items[:3]):
        angle, angle_phrase = pick_angle()

        article.append(item["title"])
        article.append(angle_phrase)
        article.append(pick_unique(ANALYSIS_TEMPLATES))
        article.append(pick_unique(OPINION_TEMPLATES))

        if index < 2:
            article.append(pick_unique(TRANSITION_TEMPLATES))

    article.append("")
    article.append(pick_unique(PREDICTION_TEMPLATES))
    article.append(pick_unique(CONCLUSION_TEMPLATES))

    return "\n".join(article)
