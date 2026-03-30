from pydantic import BaseModel


class LearningCoachRecommendation(BaseModel):
    next_skill: str
    recommended_embedded_app: str
    weekly_plan: str
    why_it_matters: str


class LearningCoachResponse(BaseModel):
    recommendations: list[LearningCoachRecommendation]
