from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "streets" / "День 7 - Улица Льва Толстого.md"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    text = ARTICLE.read_text(encoding="utf-8")
    questions = text.split("# 🟫 Улица Льва Толстого", 1)[1]
    folded_text = text.casefold()
    folded_questions = questions.casefold()

    required_facts = [
        "от вокзала до реки",
        "Кузнечная",
        "Москательная",
        "Русским Чикаго",
        "семь кварталов",
        "Австрийская",
        "Любимовская",
        "Мария Санина",
        "шаляпинский дуб",
        "Том Сойер Фест",
        "Дом с жар-птицей",
        "стальные шторы",
        "Эльдар Рязанов",
        "военная миссия Польши",
        "Дом Лебяжинских",
        "первый светофор",
        "Дом ОКБ завода им. Фрунзе",
        "стадион «Динамо»",
        "Пушкинский народный дом",
        "Филарет Засухин",
        "Вадим фон Рейтлингер",
        "коктейли Молотова",
        "Столичная",
        "Тадеуш Хилинский",
        "Дом жилой на участке А. И. Климовой",
        "Евгений Малинкин",
    ]
    for fact in required_facts:
        require(fact.casefold() in folded_text, f"missing Lev Tolstoy article fact: {fact}")

    required_question_facts = [
        "семь кварталов",
        "Кузнечная",
        "Москательная",
        "Австрийская",
        "шаляпинский дуб",
        "Дом с жар-птицей",
        "стальные шторы",
        "Эльдар Рязанов",
        "военная миссия Польши",
        "первый светофор",
        "стадион «Динамо»",
        "Пушкинский народный дом",
        "коктейли Молотова",
        "Дом жилой на участке А. И. Климовой",
    ]
    for fact in required_question_facts:
        require(
            fact.casefold() in folded_questions,
            f"missing Lev Tolstoy question fact: {fact}",
        )

    image_urls = re.findall(r"!\[[^\]]+\]\((https?://[^\n]+)\)", text)
    drugo_images = [url for url in image_urls if "drugoigorod.ru/wp-content/uploads" in url]
    require(len(image_urls) >= 18, f"expected at least 18 images, got {len(image_urls)}")
    require(len(drugo_images) >= 16, f"expected at least 16 Drugoigorod images, got {len(drugo_images)}")
    require(text.count("## ") >= 10, "article should be split into detailed route sections")
    require(questions.count("[!success]") >= 30, "question block should keep at least 30 answers")

    print("validated Lev Tolstoy article rewrite")


if __name__ == "__main__":
    main()
