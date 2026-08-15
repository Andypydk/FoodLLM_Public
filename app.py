import os
import time
from io import BytesIO

import streamlit as st

from llm_service import generate_recipes
from image_service import generate_recipe_image
from vision_service import recognize_fridge_items
from test_cases import TEST_CASES
from validators import validate_recipe


# ============================================================
# 頁面設定
# ============================================================

st.set_page_config(
    page_title="智慧冰箱料理助手",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ============================================================
# 公開版使用限制
# ============================================================

GENERATE_COOLDOWN_SECONDS = 10

# ============================================================
# 共用函式
# ============================================================

def split_items(text: str) -> list[str]:
    """
    將：
    雞蛋, 番茄, 白飯

    轉成：
    ["雞蛋", "番茄", "白飯"]
    """

    if not text:
        return []

    text = text.replace("，", ",")

    return [
        item.strip()
        for item in text.split(",")
        if item.strip()
    ]


def get_secret(name: str, default=None):
    """
    先讀取 Windows 環境變數。
    若找不到，再嘗試讀取 Streamlit Secrets。
    """

    value = os.getenv(name)

    if value:
        return value

    try:
        return st.secrets.get(name, default)

    except Exception:
        return default


# ============================================================
# Session State
# ============================================================

if "recognized_ingredients" not in st.session_state:
    st.session_state.recognized_ingredients = []

if "vision_result" not in st.session_state:
    st.session_state.vision_result = None

if "last_generate_time" not in st.session_state:
    st.session_state.last_generate_time = 0


# ============================================================
# API 設定
# ============================================================

api_key = get_secret("OPENAI_API_KEY")

model = "gpt-5.6-luna"



# ============================================================
# 側邊欄
# ============================================================

with st.sidebar:

    st.title("🍳 智慧料理助手")

    st.caption(
    "🤖 AI 模式：公開免費版"
)

    
     # 公開免費版固定使用低成本模型
    model = "gpt-5.6-luna"

    page = st.radio(
        "功能選單",
        [
            "🍽️ 料理推薦",
            "🧪 測試案例"
        ]
    )

    st.divider()

    st.markdown("### 系統狀態")

    if api_key:
        st.success("AI 服務已設定")
    else:
        st.error("尚未設定 API 金鑰")

# 公開免費版固定使用低成本模型
model = "gpt-5.6-luna"

st.caption(
    "🤖 AI 模式：公開免費版"
)




# ============================================================
# 測試案例頁面
# ============================================================

if page == "🧪 測試案例":

    st.title("🧪 料理 AI 測試案例")

    st.write(
        f"目前共建立 {len(TEST_CASES)} 組測試案例。"
    )

    st.info(
        "這些案例可用來測試時間、設備、"
        "飲食限制、過敏原與不同料理需求。"
    )

    for index, case in enumerate(
        TEST_CASES,
        start=1
    ):

        with st.expander(
            f"{index}. {case['name']}"
        ):

            st.write(
                "**現有食材：**",
                "、".join(
                    case["ingredients"]
                )
            )

            st.write(
                "**用餐人數：**",
                case["servings"]
            )

            st.write(
                "**最長時間：**",
                f"{case['max_minutes']} 分鐘"
            )

            st.write(
                "**設備：**",
                "、".join(
                    case["equipment"]
                )
            )

            st.write(
                "**飲食限制：**",
                "、".join(
                    case["restrictions"]
                )
                if case["restrictions"]
                else "無"
            )

            st.write(
                "**料理風格：**",
                case["cuisine"]
            )

    st.stop()


# ============================================================
# 主頁標題
# ============================================================

st.title("🍳 智慧冰箱料理助手")

st.write(
    "根據現有食材、設備、時間、人數與飲食需求，"
    "為你產生適合的料理。"
)


# ============================================================
# API Key 檢查
# ============================================================

if not api_key:

    st.error(
        "尚未設定 OPENAI_API_KEY。"
        "請先完成 API 金鑰設定。"
    )


# ============================================================
# 輸入區
# ============================================================

st.subheader("🥬 請告訴我你的料理條件")
input_method = st.radio(
    "食材提供方式",
    [
        "✍️ 手動輸入",
        "📷 上傳冰箱照片"
    ],
    horizontal=True
)

left, right = st.columns(2)


# ------------------------------------------------------------
# 左側輸入
# ------------------------------------------------------------

with left:

    # ========================================================
    # 手動輸入食材
    # ========================================================

    if input_method == "✍️ 手動輸入":

        ingredients_text = st.text_area(
            "現有食材",
            value="雞蛋, 番茄, 白飯",
            height=130,
            help="請使用逗號分隔，例如：雞蛋, 番茄, 白飯"
        )


    # ========================================================
    # 上傳冰箱照片
    # ========================================================

    else:

        uploaded_file = st.file_uploader(
            "📷 請上傳冰箱照片",
            type=[
                "jpg",
                "jpeg",
                "png"
            ],
            help="請盡量拍攝清楚、光線充足的冰箱內部照片。"
        )

        ingredients_text = ""

        if uploaded_file is not None:

            st.image(
                uploaded_file,
                caption="目前上傳的冰箱照片",
                use_container_width=True
            )

            recognize_button = st.button(
                "🔍 AI 辨識冰箱食材",
                use_container_width=True
            )


            # ------------------------------------------------
            # 呼叫 AI 辨識
            # ------------------------------------------------

            if recognize_button:

                if not api_key:

                    st.error(
                        "尚未設定 OPENAI_API_KEY。"
                    )

                else:

                    try:

                        with st.spinner(
                            "🔍 AI 正在分析冰箱照片..."
                        ):

                            vision_result = recognize_fridge_items(
                                image_bytes=uploaded_file.getvalue(),
                                api_key=api_key,
                                model=model
                            )


                        st.session_state.vision_result = (
                            vision_result
                        )


                        # 先只把「確定辨識」的食材自動選入
                        st.session_state.recognized_ingredients = (
                            vision_result["confirmed_items"]
                        )


                        st.success(
                            "✅ 冰箱食材辨識完成"
                        )


                    except Exception as error:

                        st.error(
                            "冰箱照片辨識失敗。"
                        )

                        st.caption(
                            f"錯誤資訊：{error}"
                        )


        # ====================================================
        # 顯示辨識結果
        # ====================================================

        vision_result = st.session_state.vision_result


        if vision_result:

            st.markdown(
                "### 🔍 AI 辨識結果"
            )


            # ------------------------------------------------
            # 確定食材
            # ------------------------------------------------

            st.markdown(
                "#### ✅ 確定辨識"
            )

            confirmed_items = (
                vision_result["confirmed_items"]
            )

            if confirmed_items:

                st.success(
                    "、".join(
                        confirmed_items
                    )
                )

            else:

                st.write(
                    "沒有可明確確認的食材。"
                )


            # ------------------------------------------------
            # 可能食材
            # ------------------------------------------------

            st.markdown(
                "#### ❓ 可能辨識"
            )

            possible_items = (
                vision_result["possible_items"]
            )

            if possible_items:

                st.warning(
                    "、".join(
                        possible_items
                    )
                )

            else:

                st.write(
                    "沒有需要推測的食材。"
                )


            # ------------------------------------------------
            # 待確認
            # ------------------------------------------------

            st.markdown(
                "#### 📝 需要確認"
            )

            needs_confirmation = (
                vision_result[
                    "needs_confirmation"
                ]
            )

            if needs_confirmation:

                for item in needs_confirmation:

                    st.write(
                        f"• {item}"
                    )

            else:

                st.write(
                    "沒有額外需要確認的物品。"
                )


            # ------------------------------------------------
            # AI 說明
            # ------------------------------------------------

            if vision_result["overall_note"]:

                st.info(
                    vision_result[
                        "overall_note"
                    ]
                )


            # =================================================
            # 讓使用者選擇真正要拿來做料理的食材
            # =================================================

            all_detected_items = list(
                dict.fromkeys(
                    confirmed_items
                    + possible_items
                )
            )


            selected_ingredients = st.multiselect(
                "🥬 請確認要使用的食材",
                options=all_detected_items,
                default=confirmed_items
            )


            st.session_state.recognized_ingredients = (
                selected_ingredients
            )


            # ------------------------------------------------
            # 額外補充食材
            # ------------------------------------------------

            additional_food = st.text_input(
                "➕ 還有其他照片沒辨識到的食材嗎？",
                placeholder="例如：青蔥, 豆腐"
            )


            final_ingredients = list(
                selected_ingredients
            )


            if additional_food.strip():

                final_ingredients.extend(
                    split_items(
                        additional_food
                    )
                )


            # 去除重複
            final_ingredients = list(
                dict.fromkeys(
                    final_ingredients
                )
            )


            ingredients_text = ", ".join(
                final_ingredients
            )


            st.text_area(
                "✅ 最終使用的食材",
                value=ingredients_text,
                height=100,
                disabled=True
            )


    # ========================================================
    # 共用料理條件
    # ========================================================

    cuisine = st.selectbox(
        "料理風格",
        [
            "中式",
            "西式",
            "中西融合"
        ]
    )


    servings = st.number_input(
        "用餐人數",
        min_value=1,
        max_value=20,
        value=2,
        step=1
    )


    max_minutes = st.number_input(
        "最長料理時間（分鐘）",
        min_value=5,
        max_value=180,
        value=30,
        step=5
    )


# ------------------------------------------------------------
# 右側輸入
# ------------------------------------------------------------

with right:

    equipment = st.multiselect(
        "現有設備",
        [
            "平底鍋",
            "湯鍋",
            "電鍋",
            "微波爐",
            "氣炸鍋",
            "烤箱"
        ],
        default=[
            "平底鍋"
        ]
    )

    restrictions = st.multiselect(
        "飲食限制",
        [
            "花生過敏",
            "乳製品過敏",
            "雞蛋過敏",
            "海鮮過敏",
            "無麩質",
            "蛋奶素",
            "純素",
            "低鹽"
        ]
    )

    other_restriction = st.text_input(
        "其他限制",
        placeholder="例如：不吃香菜"
    )
    # 公開版每次只產生一道料理，避免 API 使用量過高
    recipe_count = 1

    generate_image = st.checkbox(
    "🖼️ 產生 AI 料理示意圖",
    value=False,
    help=(
        "產生圖片需要較長等待時間；"
        "若只需要料理建議，可以保持關閉。"
    )
)
    


# ============================================================
# 生成按鈕
# ============================================================

st.write("")

generate_button = st.button(
    "✨ 幫我推薦料理",
    type="primary",
    use_container_width=True,
    disabled=not bool(api_key)
)


# ============================================================
# 開始產生料理
# ============================================================

if generate_button:

    # ========================================================
    # 防止使用者短時間內重複呼叫 AI
    # ========================================================

    current_time = time.time()

    elapsed_time = (
        current_time
        - st.session_state.last_generate_time
    )

    if elapsed_time < GENERATE_COOLDOWN_SECONDS:

        remaining_seconds = int(
            GENERATE_COOLDOWN_SECONDS
            - elapsed_time
        ) + 1

        st.warning(
            f"⏳ 操作太快了，請等待約 "
            f"{remaining_seconds} 秒後再重新產生料理。"
        )

        st.stop()


    # 記錄本次操作時間
    st.session_state.last_generate_time = current_time


    # ========================================================
    # 整理使用者輸入
    # ========================================================

    ingredients = split_items(
        ingredients_text
    )

    if not ingredients:

        st.warning(
            "請至少輸入一項現有食材。"
        )

        st.stop()


    if not equipment:

        st.warning(
            "請至少選擇一項料理設備。"
        )

        st.stop()


    all_restrictions = list(
        restrictions
    )


    if other_restriction.strip():

        all_restrictions.append(
            other_restriction.strip()
        )


    # ========================================================
    # 呼叫文字 AI
    # ========================================================

    try:

        with st.spinner(
            "🤖 AI 正在分析條件並設計料理..."
        ):

            result = generate_recipes(
                ingredients=ingredients,
                servings=int(servings),
                max_minutes=int(max_minutes),
                equipment=equipment,
                restrictions=all_restrictions,
                cuisine=cuisine,
                recipe_count=recipe_count,
                api_key=api_key,
                model=model
            )


        st.success(
            f"成功產生 {len(result.recipes)} 道候選料理！"
        )


        # ====================================================
        # 每一道料理
        # ====================================================

        for index, recipe in enumerate(
            result.recipes,
            start=1
        ):

            st.divider()


            # =================================================
            # 取得食材名稱
            # =================================================

            ingredient_names = [
                item.name
                for item in recipe.ingredients
            ]


            # =================================================
            # 產生料理圖片
            # =================================================

            recipe_image = None


            if generate_image:

                try:

                    with st.spinner(
                        f"🖼️ 正在製作"
                        f"「{recipe.recipe_name}」"
                        f"料理示意圖..."
                    ):

                        recipe_image = generate_recipe_image(
                            recipe_name=recipe.recipe_name,
                            ingredients=ingredient_names,
                            cuisine=recipe.cuisine,
                            api_key=api_key
                        )


                except Exception as image_error:

                    st.warning(
                        "料理圖片目前無法產生，"
                        "但不影響食譜內容。"
                    )

                    # 開發階段先顯示真正錯誤
                    st.caption(
                        f"圖片錯誤資訊：{image_error}"
                    )


            # =================================================
            # 左邊圖片 / 右邊料理資訊
            # =================================================

            image_col, info_col = st.columns(
                [1, 1.3],
                gap="large"
            )


            # -------------------------------------------------
            # 左側圖片
            # -------------------------------------------------

            with image_col:

                if recipe_image:

                    st.image(
                        BytesIO(
                            recipe_image
                        ),
                        caption=(
                            f"{recipe.recipe_name}"
                            "｜AI 料理示意圖"
                        ),
                        use_container_width=True
                    )

                elif generate_image:

                    st.info(
                        "🖼️ 本料理目前沒有可顯示的示意圖片。"
                    )

                else:

                    st.info(
                        "🖼️ 已關閉料理圖片功能。"
                    )


            # -------------------------------------------------
            # 右側資訊
            # -------------------------------------------------

            with info_col:

                st.subheader(
                    f"🍽️ {recipe.recipe_name}"
                )


                # 推薦理由
                recommendation_reason = getattr(
                    recipe,
                    "recommendation_reason",
                    ""
                )


                if recommendation_reason:

                    st.success(
                        "💡 推薦理由："
                        + recommendation_reason
                    )


                # 三個摘要資訊
                c1, c2, c3 = st.columns(3)


                c1.metric(
                    "料理風格",
                    recipe.cuisine
                )


                c2.metric(
                    "用餐人數",
                    f"{recipe.servings} 人"
                )


                c3.metric(
                    "料理時間",
                    f"{recipe.total_minutes} 分鐘"
                )


                # 時間判斷
                if (
                    recipe.total_minutes
                    <= int(max_minutes)
                ):

                    st.success(
                        "✅ 料理時間符合你的設定"
                    )

                else:

                    st.warning(
                        "⚠️ 料理時間超過你的設定"
                    )


            # =================================================
            # 食材與份量
            # =================================================

            st.markdown(
                "### 🥬 食材與份量"
            )


            for item in recipe.ingredients:

                if item.note:

                    st.write(
                        f"• **{item.name}**："
                        f"{item.amount}"
                        f"（{item.note}）"
                    )

                else:

                    st.write(
                        f"• **{item.name}**："
                        f"{item.amount}"
                    )


            # =================================================
            # 所需設備
            # =================================================

            st.markdown(
                "### 🍳 所需設備"
            )


            if recipe.equipment:

                for item in recipe.equipment:

                    st.write(
                        f"• {item}"
                    )

            else:

                st.write(
                    "沒有特殊設備需求"
                )


            # =================================================
            # 料理步驟
            # =================================================

            st.markdown(
                "### 👨‍🍳 料理步驟"
            )


            for step in recipe.steps:

                st.markdown(
                    f"**步驟 {step.step}**"
                )

                st.write(
                    step.instruction
                )

                st.caption(
                    f"⏱ 約 {step.minutes} 分鐘"
                )


            # =================================================
            # 採買項目
            # =================================================

            st.markdown(
                "### 🛒 需要採買"
            )


            if recipe.shopping_items:

                for item in recipe.shopping_items:

                    st.write(
                        f"• {item}"
                    )

            else:

                st.success(
                    "現有食材已足夠，"
                    "不需要額外採買。"
                )


            # =================================================
            # 過敏原
            # =================================================

            st.markdown(
                "### ⚠️ 過敏原提醒"
            )


            if recipe.allergens:

                st.warning(
                    "可能涉及的過敏原："
                    + "、".join(
                        recipe.allergens
                    )
                )

            else:

                st.info(
                    "AI 未辨識到明確過敏原；"
                    "仍請確認實際食品標示。"
                )


            # =================================================
            # 食品安全
            # =================================================

            if recipe.safety_notes:

                st.markdown(
                    "### 🛡️ 食品安全提醒"
                )


                for note in recipe.safety_notes:

                    st.write(
                        f"• {note}"
                    )


            # =================================================
            # 需要確認
            # =================================================

            if recipe.needs_confirmation:

                st.markdown(
                    "### ❓ 需要進一步確認"
                )


                for item in recipe.needs_confirmation:

                    st.write(
                        f"• {item}"
                    )


            # =================================================
            # 原本的程式自動檢查
            # =================================================

            warnings = validate_recipe(
                recipe,
                int(max_minutes)
            )


            if warnings:

                st.markdown(
                    "### 🔎 系統自動檢查"
                )


                for warning in warnings:

                    st.warning(
                        warning
                    )

            else:

                st.success(
                    "✅ 基本料理一致性檢查通過"
                )


        # ====================================================
        # 整體說明
        # ====================================================

        st.divider()

        st.markdown(
            "### 🤖 AI 整體說明"
        )

        st.info(
            result.overall_note
        )


        st.caption(
            "⚠️ AI 料理與料理示意圖僅供參考。"
            "若涉及嚴重過敏、疾病飲食、"
            "嬰幼兒飲食或特殊醫療需求，"
            "請依食品標示與專業人員建議確認。"
        )


    # ========================================================
    # AI 發生錯誤
    # ========================================================

    except Exception as error:

        st.error(
            "⚠️ 料理產生失敗"
        )

        st.write(
            "AI 服務目前無法完成這次請求。"
        )

        # 目前是開發階段，所以保留詳細錯誤方便你除錯
        st.caption(
            f"錯誤資訊：{error}"
        )