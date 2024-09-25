class Question:
    def __init__(self, question_id, question_type, has_subquestions, content, scoring_criteria, answered=False):
        self.question_id = question_id
        self.question_type = question_type
        self.has_subquestions = has_subquestions
        self.content = content
        self.scoring_criteria = scoring_criteria
        self.score = 0
        self.answered = answered
        self.subquestions = []
        self.answer = None

    def add_subquestion(self, subquestion):
        if self.has_subquestions:
            self.subquestions.append(subquestion)
        else:
            raise ValueError("This question does not support subquestions.")

    def mark_as_answered(self, answer: str):
        self.answer = answer
        self.answered = True


    def to_dict(self):
        return {
            "question_id": self.question_id,
            "question_type": self.question_type,
            "has_subquestions": self.has_subquestions,
            "content": self.content,
            "score": self.score,
            "scoring_criteria": self.scoring_criteria,
            "answered": self.answered,
            "subquestions": [subquestion.to_dict() for subquestion in self.subquestions],
            "answer": self.answer
        }

    def __repr__(self):
        return f"Question(id={self.question_id}, type={self.question_type}, answered={self.answered}, score={self.score})"



questions = [
    Question(
        question_id=1,
        question_type="binary",
        has_subquestions=False,
        content="请问您近三个月内是否有跌倒",
        scoring_criteria={"否": 0, "是": 25}
    ),
    Question(
        question_id=2,
        question_type="binary",
        has_subquestions=False,
        content="超过一个医疗诊断",
        scoring_criteria={"否": 0, "是": 15}
    ),
    Question(
        question_id=3,
        
        question_type="multiple_choice",
        has_subquestions=False,
        content="行走是否使用辅助用具",
        scoring_criteria={"不需要/卧床休息/他人协助": 0, "拐杖/手杖/助行器": 15, "轮椅, 平车": 30}
    ),
    Question(
        question_id=4,
        question_type="binary",
        has_subquestions=False,
        content="是否接受药物治疗",
        scoring_criteria={"否": 0, "是": 20}
    ),
    Question(
        question_id=5,
        question_type="multiple_choice",
        has_subquestions=False,
        content="步态/移动",
        scoring_criteria={"正常/卧床不能移动": 0, "双下肢虚弱乏力": 10, "残疾或功能障碍": 20}
    ),
    Question(
        question_id=6,
        question_type="multiple_choice",
        has_subquestions=False,
        content="认知状态",
        scoring_criteria={"自主行为能力": 0, "无控制能力": 15}
    )
]