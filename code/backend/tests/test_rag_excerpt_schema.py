from app.schemas.liuyao import LiuyaoChatInitRequest


def test_liuyao_chat_init_coerces_numeric_excerpt_scores() -> None:
    req = LiuyaoChatInitRequest.model_validate(
        {
            "chart": {"input": {"question": "test"}},
            "yongShen": {"yongShen": "妻财", "position": 3, "reason": "test"},
            "excerpts": [
                {
                    "source": "book",
                    "excerpt": "sample",
                    "score": 0.673,
                    "rerankScore": 0.5939,
                }
            ],
        }
    )
    assert req.excerpts is not None
    assert req.excerpts[0]["score"] == "0.673"
    assert req.excerpts[0]["rerankScore"] == "0.5939"
