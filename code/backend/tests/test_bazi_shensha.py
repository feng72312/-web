from app.core.paipan.shensha import collect_pillar_shen_sha, make_shen_sha_context


def test_shensha_for_sample_chart():
    ctx = make_shen_sha_context(
        day_gan="\u7532",
        day_zhi="\u5bc5",
        year_gan="\u620a",
        year_zhi="\u5bc5",
        month_zhi="\u620c",
        gender=1,
    )
    year_stars = collect_pillar_shen_sha(ctx, "\u620a", "\u5bc5")
    month_stars = collect_pillar_shen_sha(ctx, "\u58ec", "\u620c")
    day_stars = collect_pillar_shen_sha(ctx, "\u7532", "\u5bc5")
    hour_stars = collect_pillar_shen_sha(ctx, "\u7532", "\u620c")

    assert "\u7984\u795e" in year_stars
    assert "\u534e\u76d6" in month_stars
    assert "\u7984\u795e" in day_stars
    assert "\u534e\u76d6" in hour_stars
    assert len(year_stars) >= 3
    assert len(day_stars) >= 3


def test_shensha_includes_day_special_stars():
    ctx = make_shen_sha_context(
        day_gan="\u5e9a",
        day_zhi="\u8fb0",
        year_gan="\u5e9a",
        year_zhi="\u7533",
        month_zhi="\u5bc5",
        gender=1,
    )
    stars = collect_pillar_shen_sha(ctx, "\u5e9a", "\u8fb0")
    assert "\u592d\u65fa" in stars
