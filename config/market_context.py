"""
Market Context Layer
=====================
This is what turns the system from "a Pakistan tool" into "a business
intelligence framework deployed for Pakistan (and easily, anywhere else)".

Every agent receives a MarketContext object. Nothing about a region is
hardcoded into agent logic — it's all injected here and threaded through
prompts, search domains, and formatting.

To add a new market: add a new MARKETS entry. That's it.
"""

from dataclasses import dataclass, field


@dataclass
class MarketContext:
    region: str                      # e.g. "Pakistan"
    country_code: str                # e.g. "PK"
    languages: list[str]             # e.g. ["en", "ur"]
    currency: str                    # e.g. "PKR"
    currency_symbol: str             # e.g. "Rs"
    trusted_domains: list[str]       # sites to prioritize in web search
    regulatory_notes: str            # short brief injected into prompts
    cultural_notes: str              # seasonality, holidays, business norms
    major_cities: list[str] = field(default_factory=list)

    def as_prompt_block(self) -> str:
        """Rendered into every agent's system prompt so behavior adapts
        to the active market without changing any agent code."""
        return f"""
MARKET CONTEXT (use this to ground every answer):
- Region: {self.region} ({self.country_code})
- Respond in: {', '.join(self.languages)} (match the user's language; if they
  mix languages, mix your response the same way)
- Currency: always quote figures in {self.currency} ({self.currency_symbol})
- Regulatory context: {self.regulatory_notes}
- Cultural / seasonal context: {self.cultural_notes}
- Major business hubs to consider: {', '.join(self.major_cities)}
""".strip()


MARKETS: dict[str, MarketContext] = {
    "Pakistan": MarketContext(
        region="Pakistan",
        country_code="PK",
        languages=["en", "ur"],
        currency="PKR",
        currency_symbol="Rs",
        trusted_domains=[
            "dawn.com", "brecorder.com", "tribune.com.pk",
            "pbs.gov.pk", "sbp.org.pk", "secp.gov.pk", "propakistani.pk",
        ],
        regulatory_notes=(
            "SECP company registration, FBR tax slabs and sales tax (17% "
            "standard GST), provincial vs federal tax split, SBP regulations "
            "for digital payments (Raast, JazzCash, Easypaisa)."
        ),
        cultural_notes=(
            "Ramadan and Eid drive major demand shifts (retail spikes before "
            "Eid, shortened business hours during Ramadan). Winter/summer "
            "load-shedding can affect operations. Cash-on-delivery still "
            "dominates e-commerce; trust in digital payments is growing but "
            "uneven across cities."
        ),
        major_cities=["Karachi", "Lahore", "Islamabad", "Faisalabad", "Gulberg", "Rawalpindi"],
    ),
    "India": MarketContext(
        region="India",
        country_code="IN",
        languages=["en", "hi"],
        currency="INR",
        currency_symbol="₹",
        trusted_domains=[
            "livemint.com", "economictimes.indiatimes.com", "business-standard.com",
            "mca.gov.in", "gst.gov.in",
        ],
        regulatory_notes=(
            "GST registration and slabs, MSME (Udyam) registration benefits, "
            "state-level compliance variance."
        ),
        cultural_notes=(
            "Diwali and festival season drive major retail demand. UPI "
            "dominates digital payments. Regional language and pricing "
            "sensitivity vary sharply by state."
        ),
        major_cities=["Mumbai", "Delhi", "Bangalore", "Pune", "Hyderabad"],
    ),
    "United Arab Emirates": MarketContext(
        region="United Arab Emirates",
        country_code="AE",
        languages=["en", "ar"],
        currency="AED",
        currency_symbol="د.إ",
        trusted_domains=["gulfnews.com", "khaleejtimes.com", "moec.gov.ae"],
        regulatory_notes=(
            "Free zone vs mainland licensing, 9% corporate tax (above "
            "AED 375,000 profit), VAT at 5%."
        ),
        cultural_notes=(
            "Ramadan shortened working hours; expat-heavy customer base "
            "means multilingual marketing matters."
        ),
        major_cities=["Dubai", "Abu Dhabi", "Sharjah"],
    ),
}

DEFAULT_MARKET = "Pakistan"


def get_market(name: str) -> MarketContext:
    if name not in MARKETS:
        raise ValueError(f"Unknown market '{name}'. Available: {list(MARKETS)}")
    return MARKETS[name]
