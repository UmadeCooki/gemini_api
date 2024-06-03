from flask import Flask, render_template, request
from pathlib import Path
import google.generativeai as genai
import jinja2

genai.configure(api_key="AIzaSyDPNeaF8v7u2jfTuUv5ybk_xDPf8zhOais")  # 본인의 API 키로 변경해주세요

model = genai.GenerativeModel(model_name="gemini-pro-vision")
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 이미지 파일 처리
        if "image" not in request.files:
            return render_template("index.html", error="이미지를 선택해주세요!")
        image = request.files["image"]
        image_bytes = image.read()

        # 이미지에서 텍스트 추출
        prompt_parts = [
            {"mime_type": "image/jpeg", "data": image_bytes},
            "이미지에서 제품을 정확하게 식별하고 분석해서 **재료**, **레시피**, **팁**으로 표시해서 조리방법을 제공해줘.",
        ]
        response = model.generate_content(prompt_parts)

        # 응답 메시지 텍스트로 가져오기
        response_text = response.text

        # 텍스트 파싱
        lines = response_text.split("\n")
        ingredients = []
        recipe = []
        tips = []
        current_section = None
        for line in lines:
            if "**재료**" in line:
                current_section = ingredients
                continue
            elif "**레시피**" in line:
                current_section = recipe
                continue
            elif "**팁**" in line:
                current_section = tips
                continue
            elif current_section is not None:
                if line.strip() != "":
                    if current_section is recipe:
                        # 레시피 숫자로 시작하는 부분 처리
                        if line[0].isdigit():
                            line = f"{line.split('.')[1].strip()}"
                        current_section.append(line.strip())
                    else:
                        current_section.append(line.strip())

        # 레시피 리스트에서 중복된 숫자 제거
        recipe = list(dict.fromkeys(recipe))

        # 템플릿에 전달
        return render_template("index.html", ingredients=ingredients, recipe=recipe, tips=tips)
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)