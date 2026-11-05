"""Ready-made holiday campaigns for the home hero (specs/017-home-banners).

A preset is content only: copy, colours and the seasonal window. The admin turns it
into a real campaign in one click and can pin it manually (see ``BannerCampaign``).
All dates are Kyiv wall-clock days, because that is where the shop sells.
"""

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from ups_kulka.modules.banners.domain.entities import BannerLayout, BannerTheme

KYIV = ZoneInfo("Europe/Kyiv")


@dataclass(frozen=True, slots=True)
class HolidayPreset:
    key: str
    title: str
    description: str
    name_template: str
    headline: str
    subtitle: str
    theme: BannerTheme
    starts_on: tuple[int, int]  # (month, day), Kyiv local time
    ends_on: tuple[int, int]
    cta_label: str
    cta_url: str
    cta2_label: str
    cta2_url: str
    ribbon_text: str
    ribbon_url: str
    ends_next_year: bool = False
    layout: BannerLayout = BannerLayout.BALLOONS
    priority: int = 0

    def window(self, season_year: int) -> tuple[datetime, datetime]:
        start = datetime(season_year, *self.starts_on, tzinfo=KYIV)
        year_end = season_year + 1 if self.ends_next_year else season_year
        return start, datetime(year_end, *self.ends_on, tzinfo=KYIV)

    def period(self, moment: datetime) -> tuple[datetime, datetime]:
        """The window we are inside now, or the nearest one still ahead."""
        local = moment.astimezone(KYIV)
        windows = [
            self.window(local.year - 1),
            self.window(local.year),
            self.window(local.year + 1),
        ]
        for start, end in windows:
            if start <= local < end:
                return start, end
        for start, end in windows:
            if start > local:
                return start, end
        return windows[-1]  # pragma: no cover - windows always span three years

    def campaign_name(self, moment: datetime) -> str:
        """Holiday banners are named by the year of the celebration (New Year: the coming one)."""
        _, end = self.period(moment)
        return self.name_template.format(year=end.year)


HOLIDAY_PRESETS: tuple[HolidayPreset, ...] = (
    HolidayPreset(
        key="valentines",
        title="14 лютого",
        description="День закоханих: серця з кульок, композиції та сюрпризи.",
        name_template="14 Лютого {year}",
        headline="З Днем Валентина!",
        subtitle=(
            "Серця з кульок, композиції й сюрпризи для закоханих. "
            "Привеземо 13–14 лютого, щоб встигнути сказати головне."
        ),
        theme=BannerTheme.RED,
        starts_on=(2, 1),
        ends_on=(2, 15),
        cta_label="Обрати подарунок",
        cta_url="/kulky",
        cta2_label="Доставка і оплата",
        cta2_url="/dostavka",
        ribbon_text="14 лютого — доставка сердець по Києву. Замовляйте заздалегідь",
        ribbon_url="/dostavka",
    ),
    HolidayPreset(
        key="march_8",
        title="8 березня",
        description="Весна й жіноче свято: ніжні букети з кульок для мам, подруг і колег.",
        name_template="8 Березня {year}",
        headline="З 8 Березня!",
        subtitle=(
            "Ніжні букети з кульок для мам, подруг і колег. "
            "Приймаємо замовлення на 7–8 березня з доставкою по Києву."
        ),
        theme=BannerTheme.ROSE,
        starts_on=(3, 1),
        ends_on=(3, 10),
        cta_label="Обрати букет",
        cta_url="/kulky",
        cta2_label="Доставка і оплата",
        cta2_url="/dostavka",
        ribbon_text="Встигніть до 8 березня — доставка 7–8 березня за графіком",
        ribbon_url="/dostavka",
    ),
    HolidayPreset(
        key="christmas",
        title="Різдво",
        description="Теплі зимові композиції для дому й подарунків 25 грудня.",
        name_template="Різдво {year}",
        headline="З Різдвом!",
        subtitle=(
            "Теплі зимові композиції з кульок для дому й подарунків. "
            "Доставимо напередодні й у день Різдва."
        ),
        theme=BannerTheme.GOLD,
        starts_on=(12, 18),
        ends_on=(12, 26),
        cta_label="Обрати композицію",
        cta_url="/kulky",
        cta2_label="Доставка і оплата",
        cta2_url="/dostavka",
        ribbon_text="Різдвяні композиції з доставкою по Києву 24–25 грудня",
        ribbon_url="/dostavka",
    ),
    HolidayPreset(
        key="new_year",
        title="Новий рік",
        description="Фонтани, фотозони й кульки з написом для головної ночі року.",
        name_template="Новий рік {year}",
        headline="З Новим роком!",
        subtitle=(
            "Святкові фонтани, фотозони й кульки з написом — щоб головна ніч року була незабутньою."
        ),
        theme=BannerTheme.DARK,
        starts_on=(12, 26),
        ends_on=(1, 3),
        ends_next_year=True,
        cta_label="Обрати композицію",
        cta_url="/kulky",
        cta2_label="Доставка і оплата",
        cta2_url="/dostavka",
        ribbon_text="Новорічні замовлення приймаємо до 30 грудня",
        ribbon_url="/dostavka",
    ),
)


def find_preset(key: str) -> HolidayPreset | None:
    return next((preset for preset in HOLIDAY_PRESETS if preset.key == key), None)
