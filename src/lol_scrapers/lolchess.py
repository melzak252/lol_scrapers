from typing import List, Dict, Tuple, Union

from requests_html import HTML, Element


class LOLChessScraper:

    @staticmethod
    def src2https(src: str):
        return f"https:{src}"

    def get_all_traits_data(self, resp: HTML):
        origin_divs, class_divs = resp.find(".row.row-normal")
        traits = []
        origins = self._get_traits_from_div(origin_divs, "origin")
        classes = self._get_traits_from_div(class_divs, "class")
        traits.extend(origins)
        traits.extend(classes)

        return {"traits": traits, "url": resp.url}

    @staticmethod
    def get_all_traits_names(resp: HTML) -> Dict[str, List[str]]:
        traits_div = resp.find(".guide-synergy__header.clearfix")
        traits = []
        for trait in traits_div:
            champions_in_trait = trait.find("a")
            if len(champions_in_trait) > 1:
                trait_name = trait.find("span", first=True).text.strip()
                traits.append(trait_name)

        return {
            "traits": traits,
        }

    def get_icon(self, resp_icon: HTML, trait_name: str) -> Dict[str, Union[str, None]]:
        table = resp_icon.find("table.guide-items-table")[-1]

        imgs = table.find("img")

        emblem = f"{trait_name.title()} Emblem"
        trait_icon = [img.attrs["src"] for img in imgs if img.attrs["alt"] == emblem]

        if not trait_icon:
            return {"src": None}

        return {"src": self.src2https(trait_icon[0]) if trait_icon else ""}

    @staticmethod
    def _get_trait_data(trait_div: Element) -> Tuple[str, List[Dict[str, str]], str, List[str]]:
        trait_name = trait_div.find("span.align-middle", first=True).text.strip()

        champions_div = trait_div.find(
            ".guide-synergy-table__synergy__champions.mb-1", first=True
        )
        champions = [
            {
                "name": champion.find("img", first=True).attrs["alt"],
                "cost": champion.find("span.cost", first=True).text,
            }
            for champion in champions_div.find("a")
        ]
        trait_desc = trait_div.find(
            ".guide-synergy-table__synergy__desc.mb-2", first=True
        ).text.strip()
        trait_values = trait_div.find(
            ".guide-synergy-table__synergy__stats", first=True
        ).text.split("\n")
        trait_values = [value.strip() for value in trait_values]

        return trait_name, champions, trait_desc, trait_values

    def get_trait(self, resp: HTML, trait_name) -> Dict[str, Union[str, int, List[Union[str, Dict[str, str]]]]]:
        trait_div = resp.find(
            f".guide-synergy-table__synergy.guide-synergy-table__synergy--{trait_name.lower()}",
            first=True,
        )
        if trait_div is None:
            return {}

        trait_name, champions, trait_desc, trait_values = self._get_trait_data(
            trait_div
        )

        data = {
            "name": trait_name,
            "no_champions": len(champions),
            "description": trait_desc,
            "champions": champions,
            "values": trait_values,
        }
        return data

    @staticmethod
    def _get_traits_from_div(traits_div: Element, trait_type: str):
        traits = []
        traits_div = traits_div.find(".guide-synergy")
        for trait in traits_div:
            champions_in_trait = trait.find("a.d-inline-block")
            no_champions = len(champions_in_trait) // 2
            if no_champions > 1:
                trait_name = trait.find("span", first=True).text.strip()

                champions = [
                    {
                        "name": champion_a_tag.find(
                            "span.name", first=True
                        ).text.strip(),
                        "cost": champion_a_tag.find(
                            "span.cost", first=True
                        ).text.strip(),
                    }
                    for champion_a_tag in champions_in_trait[:no_champions]
                ]

                trait_desc = trait.find(
                    ".guide-synergy__description", first=True
                ).text.strip()
                trait_values = trait.find(
                    ".guide-synergy__stats", first=True
                ).text.split("/")
                trait_values = [value.strip() for value in trait_values]

                data = {
                    "type": trait_type,
                    "name": trait_name,
                    "no_champions": no_champions,
                    "description": trait_desc,
                    "champions": champions,
                    "values": trait_values,
                }
                traits.append(data)
        return traits