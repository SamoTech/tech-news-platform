import random

ANGLES = [
    "user_impact",
    "market_signal",
    "competition",
    "timing",
    "strategy"
]

ANGLE_PHRASES = {
    "user_impact": "From a user perspective, the real impact may become visible sooner than expected.",
    "market_signal": "Viewed as a market signal, this move reflects shifting priorities across the industry.",
    "competition": "In the context of competition, this development could pressure rivals to respond.",
    "timing": "The timing of this announcement is notable given current market conditions.",
    "strategy": "Strategically, this suggests a longer-term plan rather than a short-term reaction."
}

def pick_angle():
    angle = random.choice(ANGLES)
    return angle, ANGLE_PHRASES[angle]
