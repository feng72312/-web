from __future__ import annotations

from app.core.fengshui import bazhai
from app.core.fengshui import xuankong
from app.core.fengshui.models import FengshuiChart, FengshuiInput


class FengshuiEngine:
    def chart(self, data: FengshuiInput) -> FengshuiChart:
        if data.method == "bazhai":
            return self._chart_bazhai(data)
        if data.method == "xuankong":
            return self._chart_xuankong(data)
        raise ValueError(f"unsupported method: {data.method}")

    def _chart_bazhai(self, data: FengshuiInput) -> FengshuiChart:
        mountain = bazhai.resolve_mountain(data.sitting_mountain)
        ming_number = bazhai.calc_ming_gua_number(data.birth_year, data.gender)
        zhai_number = bazhai.calc_zhai_gua_number(data.sitting_mountain)
        ming_info = bazhai.TRIGRAMS[ming_number]
        zhai_info = bazhai.TRIGRAMS[zhai_number]
        directions = bazhai.build_directions(ming_number)
        compatible = bazhai.is_compatible(ming_info["group"], zhai_info["group"])

        ming_gua = {
            "number": ming_number,
            "name": ming_info["name"],
            "alias": ming_info["alias"],
            "direction": ming_info["direction"],
            "group": ming_info["group"],
            "groupLabel": "东四命" if ming_info["group"] == "dongsi" else "西四命",
        }
        zhai_gua = {
            "number": zhai_number,
            "name": zhai_info["name"],
            "alias": zhai_info["alias"],
            "direction": zhai_info["direction"],
            "group": zhai_info["group"],
            "groupLabel": "东四宅" if zhai_info["group"] == "dongsi" else "西四宅",
            "sitting": mountain["name"],
            "facing": mountain["facing"],
            "label": f"坐{mountain['name']}向{mountain['facing']}",
        }

        return FengshuiChart(
            input=data,
            ming_gua=ming_gua,
            zhai_gua=zhai_gua,
            compatible=compatible,
            directions=directions,
            palaces=bazhai.build_palace_grid(ming_number),
            advice=bazhai.build_advice(compatible=compatible, directions=directions),
            meta={"engine": "bazhai", "version": 1},
        )

    def _chart_xuankong(self, data: FengshuiInput) -> FengshuiChart:
        if data.build_year is None:
            raise ValueError("buildYear is required for xuankong")
        xk = xuankong.build_xuankong_chart(
            sitting_mountain=data.sitting_mountain,
            build_year=data.build_year,
            flow_year=data.flow_year,
        )
        advice = [
            f"当前为{xk['period']['label']}({xk['period']['yuan']}), 运盘当运之星入中顺飞.",
            f"山星{xk['shanFly']}, 向星{xk['xiangFly']}, 合参格式为运-山-向.",
            "分析时先看运星定大局, 再看山星主人丁, 向星主财运.",
        ]
        if data.flow_year is not None:
            advice.append(f"已叠加 {data.flow_year} 流年飞星供参考.")
        return FengshuiChart(
            input=data,
            xuankong=xk,
            advice=advice,
            meta={"engine": "xuankong", "version": 1},
        )

    def list_mountains(self) -> list[dict[str, str]]:
        return bazhai.list_mountains()
