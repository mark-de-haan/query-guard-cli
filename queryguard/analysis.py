import re

# Pricing per TiB (approximate on-demand rates)
REGION_PRICING_TABLE: dict[str, float] = {
    # --- The "Standard" Tier ($6.25) ---
    "us": 6.25,
    "us-central1": 6.25,
    "us-east1": 6.25,
    "us-east4": 6.25,
    "us-west1": 6.25,
    "eu": 6.25,
    "europe-west1": 6.25,  # Belgium
    "europe-north1": 6.25,  # Finland

    # --- The "High Energy" Tier (~$7.50 - $8.50) ---
    "europe-west4": 7.50,    # Netherlands
    "europe-west2": 7.82,    # London
    "europe-west3": 8.13,    # Frankfurt
    "europe-west6": 8.75,    # Zurich
    "us-west2": 8.44,        # Los Angeles
    "us-west3": 8.44,        # Salt Lake City

    # --- The "Premium" Tier ($9.00+) ---
    "southamerica-east1": 11.25,  # Sao Paulo
    "asia-northeast1": 7.40,     # Tokyo
    "asia-southeast1": 7.80,     # Singapore
    "me-central2": 10.00,        # Dammam
}

DEFAULT_PRICE: float = 6.25


class ForensicAuditor:

    @staticmethod
    def get_price_per_tib(region: str) -> float:
        """Returns the price per TiB for the given region, defaulting to $6.25."""
        return REGION_PRICING_TABLE.get(region.lower(), DEFAULT_PRICE)

    @staticmethod
    def calculate_cost(bytes_billed: int, region: str) -> float:
        """Calculates cost based on region-specific pricing."""
        if not bytes_billed:
            return 0.0

        tebibytes: float = bytes_billed / (1024**4)
        price = ForensicAuditor.get_price_per_tib(region)
        return tebibytes * price

    @staticmethod
    def analyze_query(sql: str, bytes_billed: int) -> list[str]:
        """Returns a list of detected issues."""
        risks: list[str] = []

        # 1. SELECT *
        if re.search(r'SELECT\s+\*\s+', sql, re.IGNORECASE):
            risks.append("SELECT *")

        # 2. Missing Limit
        if "LIMIT" not in sql.upper():
            risks.append("NO LIMIT")

        # 3. High Scan Volume (> 100 GB)
        if bytes_billed > (100 * 1024**3):
            risks.append("HEAVY SCAN")

        return risks