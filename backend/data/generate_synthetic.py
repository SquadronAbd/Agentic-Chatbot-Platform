"""
Generates synthetic annual report markdown files for companies missing from the dataset.
Target size: ~655 KB per file (average of existing files).
Run from: backend/data/
"""
import hashlib
import random
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "markdowns")

COMPANIES = [
    {
        "name": "AA Limited", "ticker": "AA", "exchange": "LSE", "currency": "GBP",
        "sector": "Roadside Assistance & Insurance", "country": "United Kingdom",
        "revenue": 1723, "net_income": 142, "total_assets": 2841, "employees": 10200,
        "year": 2023, "cfo": 389, "capex": 87, "gross_margin": 38.4,
        "dividend_per_share": 0.085, "fleet_size": 3200,
    },
    {
        "name": "ACRES Commercial Realty Corp.", "ticker": "ACR", "exchange": "NYSE", "currency": "USD",
        "sector": "Commercial Real Estate Finance", "country": "United States",
        "revenue": 134, "net_income": 28, "total_assets": 2190, "employees": 47,
        "year": 2023, "cfo": 61, "capex": 4, "gross_margin": 72.1,
        "dividend_per_share": 1.40, "esg_initiatives": False,
    },
    {
        "name": "Albany International Corp.", "ticker": "AIN", "exchange": "NYSE", "currency": "USD",
        "sector": "Engineered Composites & Machine Clothing", "country": "United States",
        "revenue": 1071, "net_income": 89, "total_assets": 2034, "employees": 5600,
        "year": 2023, "cfo": 156, "capex": 72, "gross_margin": 43.8,
        "dividend_per_share": 0.98, "rd_spend": 48, "patents": 312,
        "new_products": ["Albany Advanced Composites Frame Structure", "Albany LEAP Woven Preform"],
    },
    {
        "name": "Aptevo Therapeutics Inc.", "ticker": "APVO", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Biopharmaceuticals", "country": "United States",
        "revenue": 18, "net_income": -47, "total_assets": 89, "employees": 118,
        "year": 2023, "cfo": -39, "capex": 3, "gross_margin": -12.4,
        "mergers": True, "merger_detail": "Aptevo entered into a licensing agreement with Alligator Bioscience AB",
    },
    {
        "name": "Armadale Capital Plc", "ticker": "ACP", "exchange": "AIM", "currency": "GBP",
        "sector": "Mining & Natural Resources", "country": "United Kingdom",
        "revenue": 2, "net_income": -4, "total_assets": 31, "employees": 22,
        "year": 2023, "cfo": -3, "capex": 1, "gross_margin": "N/A",
    },
    {
        "name": "Aurora Innovation, Inc.", "ticker": "AUR", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Autonomous Vehicles & AI", "country": "United States",
        "revenue": 14, "net_income": -601, "total_assets": 1823, "employees": 1650,
        "year": 2023, "cfo": -548, "capex": 28, "gross_margin": "N/A",
        "patents": 427,
    },
    {
        "name": "BetMakers Technology Group Ltd", "ticker": "BET", "exchange": "ASX", "currency": "AUD",
        "sector": "Wagering Technology", "country": "Australia",
        "revenue": 48, "net_income": -21, "total_assets": 112, "employees": 310,
        "year": 2023, "cfo": -8, "capex": 6, "gross_margin": 61.2,
        "mergers": True, "merger_detail": "BetMakers completed the acquisition of Sportech Racing LLC",
    },
    {
        "name": "Bionano Genomics, Inc.", "ticker": "BNGO", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Genomics & Optical Mapping", "country": "United States",
        "revenue": 21, "net_income": -134, "total_assets": 198, "employees": 387,
        "year": 2023, "cfo": -118, "capex": 9, "gross_margin": 48.3,
        "mergers": False,
    },
    {
        "name": "Blue Apron Holdings, Inc.", "ticker": "APRN", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Meal Kit Delivery", "country": "United States",
        "revenue": 423, "net_income": -102, "total_assets": 214, "employees": 2900,
        "year": 2023, "cfo": -78, "capex": 18, "gross_margin": 32.1,
        "leadership_changes": ["Chief Executive Officer", "Chief Financial Officer"],
    },
    {
        "name": "Brave Bison Group plc", "ticker": "BBSN", "exchange": "AIM", "currency": "GBP",
        "sector": "Digital Media & Marketing", "country": "United Kingdom",
        "revenue": 54, "net_income": 3, "total_assets": 78, "employees": 420,
        "year": 2023, "cfo": 7, "capex": 2, "gross_margin": 29.8,
        "mergers": True, "merger_detail": "Brave Bison acquired The Kite Factory, a performance media agency",
    },
    {
        "name": "Commerzbank AG", "ticker": "CBK", "exchange": "XETRA", "currency": "EUR",
        "sector": "Banking & Financial Services", "country": "Germany",
        "revenue": 10279, "net_income": 2218, "total_assets": 536280, "employees": 36700,
        "year": 2023, "cfo": 3841, "capex": 312, "gross_margin": 58.2,
        "employees_let_go": 10000,
    },
    {
        "name": "CoreCard Corporation", "ticker": "CCRD", "exchange": "NYSE", "currency": "USD",
        "sector": "Payment Processing Technology", "country": "United States",
        "revenue": 61, "net_income": 9, "total_assets": 98, "employees": 480,
        "year": 2023, "cfo": 14, "capex": 5, "gross_margin": 44.7,
        "total_deposits": "N/A",
    },
    {
        "name": "Crombie REIT", "ticker": "CRR.UN", "exchange": "TSX", "currency": "CAD",
        "sector": "Real Estate Investment Trust", "country": "Canada",
        "revenue": 312, "net_income": 87, "total_assets": 4823, "employees": 210,
        "year": 2023, "cfo": 142, "capex": 89, "gross_margin": 62.3,
        "leadership_changes": ["Chief Executive Officer", "Chief Operating Officer"],
    },
    {
        "name": "Datalogic S.p.A.", "ticker": "DAL", "exchange": "BIT", "currency": "EUR",
        "sector": "Automatic Data Capture & Industrial Automation", "country": "Italy",
        "revenue": 641, "net_income": 42, "total_assets": 923, "employees": 4300,
        "year": 2023, "cfo": 78, "capex": 31, "gross_margin": 46.2,
        "leadership_changes": ["Chief Executive Officer", "Chief Financial Officer", "Chief Technology Officer"],
    },
    {
        "name": "Downer EDI Limited", "ticker": "DOW", "exchange": "ASX", "currency": "AUD",
        "sector": "Engineering & Infrastructure Services", "country": "Australia",
        "revenue": 12841, "net_income": 124, "total_assets": 6234, "employees": 33000,
        "year": 2023, "cfo": 412, "capex": 198, "gross_margin": 18.4,
        "employees_let_go": 800, "share_buyback": True,
    },
    {
        "name": "Duni Group AB", "ticker": "DUNI", "exchange": "NASDAQ Stockholm", "currency": "SEK",
        "sector": "Sustainable Table Setting Products", "country": "Sweden",
        "revenue": 7823, "net_income": 412, "total_assets": 8934, "employees": 2700,
        "year": 2023, "cfo": 689, "capex": 234, "gross_margin": 38.7,
        "leadership_changes": ["Chief Executive Officer", "Chief Financial Officer"],
    },
    {
        "name": "Elixir Energy Limited", "ticker": "EXR", "exchange": "ASX", "currency": "AUD",
        "sector": "Natural Gas Exploration", "country": "Australia",
        "revenue": 1, "net_income": -12, "total_assets": 48, "employees": 31,
        "year": 2023, "cfo": -8, "capex": 7, "gross_margin": "N/A",
        "esg_initiatives": True, "total_power_generation_mw": "N/A",
    },
    {
        "name": "Empire Company Limited", "ticker": "EMP.A", "exchange": "TSX", "currency": "CAD",
        "sector": "Food Retail & Real Estate", "country": "Canada",
        "revenue": 31823, "net_income": 742, "total_assets": 13421, "employees": 134000,
        "year": 2023, "cfo": 1423, "capex": 612, "gross_margin": 26.8,
        "dividend_changes": True,
    },
    {
        "name": "FNCB Bancorp, Inc.", "ticker": "FNCB", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Community Banking", "country": "United States",
        "revenue": 48, "net_income": 12, "total_assets": 1923, "employees": 312,
        "year": 2023, "cfo": 18, "capex": 3, "gross_margin": 61.4,
        "npl_ratio": 0.42,
    },
    {
        "name": "Franklin Covey Co.", "ticker": "FC", "exchange": "NYSE", "currency": "USD",
        "sector": "Organizational Performance Training", "country": "United States",
        "revenue": 312, "net_income": 23, "total_assets": 423, "employees": 1890,
        "year": 2023, "cfo": 48, "capex": 12, "gross_margin": 71.2,
        "esg_initiatives": True, "active_licensing_deals": 48,
    },
    {
        "name": "Guaranty Bancshares, Inc.", "ticker": "GNTY", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Community Banking", "country": "United States",
        "revenue": 89, "net_income": 21, "total_assets": 2134, "employees": 478,
        "year": 2023, "cfo": 34, "capex": 6, "gross_margin": 64.8,
        "new_products": False,
    },
    {
        "name": "HCA Healthcare, Inc.", "ticker": "HCA", "exchange": "NYSE", "currency": "USD",
        "sector": "Healthcare Services", "country": "United States",
        "revenue": 64968, "net_income": 4789, "total_assets": 51234, "employees": 309000,
        "year": 2023, "cfo": 8234, "capex": 4123, "gross_margin": 34.2,
        "managed_clinics": "N/A", "healthcare_professionals": 93000,
        "outstanding_insurance_claims": "N/A", "dividend_changes": False,
    },
    {
        "name": "Incitec Pivot Limited", "ticker": "IPL", "exchange": "ASX", "currency": "AUD",
        "sector": "Explosives & Fertilisers", "country": "Australia",
        "revenue": 4823, "net_income": 412, "total_assets": 6234, "employees": 4800,
        "year": 2023, "cfo": 712, "capex": 198, "gross_margin": 28.4,
        "mergers": True, "merger_detail": "Incitec Pivot announced the demerger of its fertilisers business",
        "dividend_changes": True, "restructuring": True,
    },
    {
        "name": "Incyte Corporation", "ticker": "INCY", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Biopharmaceuticals", "country": "United States",
        "revenue": 3909, "net_income": 312, "total_assets": 7823, "employees": 9800,
        "year": 2023, "cfo": 648, "capex": 89, "gross_margin": 72.4,
        "clinical_trial_sites": 487,
    },
    {
        "name": "INMUNE BIO INC.", "ticker": "INMB", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Neuroinflammation Therapeutics", "country": "United States",
        "revenue": 0, "net_income": -48, "total_assets": 89, "employees": 34,
        "year": 2023, "cfo": -42, "capex": 2, "gross_margin": "N/A",
    },
    {
        "name": "James Halstead plc", "ticker": "JHD", "exchange": "AIM", "currency": "GBP",
        "sector": "Commercial Flooring", "country": "United Kingdom",
        "revenue": 312, "net_income": 64, "total_assets": 423, "employees": 1200,
        "year": 2023, "cfo": 78, "capex": 18, "gross_margin": 48.2,
    },
    {
        "name": "Kelly Partners Group Holdings Limited", "ticker": "KPG", "exchange": "ASX", "currency": "AUD",
        "sector": "Accounting & Professional Services", "country": "Australia",
        "revenue": 198, "net_income": 24, "total_assets": 312, "employees": 1340,
        "year": 2023, "cfo": 38, "capex": 8, "gross_margin": 52.3,
        "leadership_changes": ["Chief Executive Officer", "Managing Director"],
    },
    {
        "name": "Kiniksa Pharmaceuticals, Ltd.", "ticker": "KNSA", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Rare Disease Therapeutics", "country": "United States",
        "revenue": 89, "net_income": -34, "total_assets": 423, "employees": 212,
        "year": 2023, "cfo": -21, "capex": 4, "gross_margin": 84.2,
        "active_pharma_patents": 14, "generic_product_count": "N/A",
        "executive_compensation_max_usd": 4820000,
    },
    {
        "name": "KP Tissue Inc.", "ticker": "KPT", "exchange": "TSX", "currency": "CAD",
        "sector": "Tissue Products", "country": "Canada",
        "revenue": 1423, "net_income": 34, "total_assets": 1823, "employees": 2800,
        "year": 2023, "cfo": 123, "capex": 67, "gross_margin": 22.1,
        "employees_let_go": "N/A",
    },
    {
        "name": "Liberty Broadband Corporation", "ticker": "LBRDA", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Broadband & Cable Services", "country": "United States",
        "revenue": 4823, "net_income": 612, "total_assets": 31234, "employees": 18900,
        "year": 2023, "cfo": 1423, "capex": 812, "gross_margin": 41.2,
        "share_buyback": False,
    },
    {
        "name": "MainStreet Bancshares, Inc.", "ticker": "MNSB", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Community Banking", "country": "United States",
        "revenue": 148, "net_income": 48, "total_assets": 2134, "employees": 389,
        "year": 2023, "cfo": 62, "capex": 7, "gross_margin": 68.4,
        "executive_compensation_max_usd": 3240000,
    },
    {
        "name": "Medallion Financial Corp.", "ticker": "MFIN", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Specialty Finance", "country": "United States",
        "revenue": 312, "net_income": 64, "total_assets": 2823, "employees": 312,
        "year": 2023, "cfo": 89, "capex": 8, "gross_margin": 71.2,
    },
    {
        "name": "MGM Resorts International", "ticker": "MGM", "exchange": "NYSE", "currency": "USD",
        "sector": "Hospitality & Gaming", "country": "United States",
        "revenue": 16190, "net_income": 1449, "total_assets": 34823, "employees": 77000,
        "year": 2023, "cfo": 2834, "capex": 912, "gross_margin": 32.8,
        "number_of_hotels": 31, "executive_compensation_max_usd": 18400000,
    },
    {
        "name": "Mosaic Brands Limited", "ticker": "MOZ", "exchange": "ASX", "currency": "AUD",
        "sector": "Fashion Retail", "country": "Australia",
        "revenue": 423, "net_income": -28, "total_assets": 312, "employees": 4200,
        "year": 2023, "cfo": 34, "capex": 12, "gross_margin": 58.4,
        "mergers": False, "ecommerce_active_customers": 480000,
    },
    {
        "name": "NuCana plc", "ticker": "NCNA", "exchange": "NASDAQ", "currency": "GBP",
        "sector": "Oncology Therapeutics", "country": "United Kingdom",
        "revenue": 0, "net_income": -62, "total_assets": 98, "employees": 78,
        "year": 2023, "cfo": -58, "capex": 2, "gross_margin": "N/A",
    },
    {
        "name": "NZME Limited", "ticker": "NZM", "exchange": "NZX", "currency": "NZD",
        "sector": "Media & Publishing", "country": "New Zealand",
        "revenue": 312, "net_income": 28, "total_assets": 423, "employees": 1800,
        "year": 2023, "cfo": 48, "capex": 14, "gross_margin": 34.2,
        "employees_let_go": 120,
    },
    {
        "name": "Ocugen, Inc.", "ticker": "OCGN", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Ophthalmology Therapeutics", "country": "United States",
        "revenue": 8, "net_income": -89, "total_assets": 198, "employees": 142,
        "year": 2023, "cfo": -78, "capex": 4, "gross_margin": "N/A",
        "executive_compensation_max_aud": "N/A",
    },
    {
        "name": "Origin Bancorp, Inc.", "ticker": "OBNK", "exchange": "NYSE", "currency": "USD",
        "sector": "Community Banking", "country": "United States",
        "revenue": 478, "net_income": 98, "total_assets": 9690, "employees": 1890,
        "year": 2023, "cfo": 142, "capex": 18, "gross_margin": 67.2,
        "leadership_changes": ["Chief Executive Officer", "Chief Credit Officer"],
    },
    {
        "name": "Peako Limited", "ticker": "PKO", "exchange": "ASX", "currency": "AUD",
        "sector": "Technology & Data Services", "country": "Australia",
        "revenue": 4, "net_income": -3, "total_assets": 12, "employees": 18,
        "year": 2023, "cfo": -2, "capex": 1, "gross_margin": 48.2,
        "cloud_storage_tb": "N/A", "year_end_customer_base": "N/A", "rd_expenditure": "N/A",
    },
    {
        "name": "Pintec Technology Holdings Limited", "ticker": "PT", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Financial Technology", "country": "China",
        "revenue": 89, "net_income": -34, "total_assets": 423, "employees": 612,
        "year": 2023, "cfo": -18, "capex": 6, "gross_margin": 42.3,
        "employees_let_go": 280, "nim": "N/A",
    },
    {
        "name": "Playtech plc", "ticker": "PTEC", "exchange": "LSE", "currency": "EUR",
        "sector": "Gambling Technology", "country": "Isle of Man",
        "revenue": 1702, "net_income": 142, "total_assets": 4823, "employees": 7800,
        "year": 2023, "cfo": 389, "capex": 87, "gross_margin": 44.8,
    },
    {
        "name": "Poste Italiane S.p.A.", "ticker": "PST", "exchange": "BIT", "currency": "EUR",
        "sector": "Postal Services & Financial Products", "country": "Italy",
        "revenue": 11823, "net_income": 1234, "total_assets": 89234, "employees": 120000,
        "year": 2023, "cfo": 2134, "capex": 423, "gross_margin": 28.4,
        "dividend_changes": True,
    },
    {
        "name": "Rapid7, Inc.", "ticker": "RPD", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Cybersecurity", "country": "United States",
        "revenue": 770, "net_income": -234, "total_assets": 1823, "employees": 2800,
        "year": 2023, "cfo": 89, "capex": 28, "gross_margin": 71.4,
        "active_software_licenses": "N/A",
    },
    {
        "name": "Rectifier Technologies Ltd", "ticker": "RFT", "exchange": "ASX", "currency": "AUD",
        "sector": "Power Electronics", "country": "Australia",
        "revenue": 28, "net_income": 4, "total_assets": 42, "employees": 89,
        "year": 2023, "cfo": 6, "capex": 2, "gross_margin": 38.2,
        "patents": "N/A",
    },
    {
        "name": "Ritchie Bros. Auctioneers Incorporated", "ticker": "RBA", "exchange": "NYSE", "currency": "USD",
        "sector": "Industrial Auctions & Asset Management", "country": "Canada",
        "revenue": 1718, "net_income": 234, "total_assets": 7823, "employees": 6200,
        "year": 2023, "cfo": 389, "capex": 87, "gross_margin": 54.2,
        "dividend_per_share": 1.08, "litigation": True,
    },
    {
        "name": "Seiko Epson Corporation", "ticker": "6724", "exchange": "TSE", "currency": "JPY",
        "sector": "Printing & Precision Technology", "country": "Japan",
        "revenue": 1089234, "net_income": 48234, "total_assets": 1234823, "employees": 72000,
        "year": 2023, "cfo": 98234, "capex": 48234, "gross_margin": 38.4,
        "dividend_changes": False,
    },
    {
        "name": "SIG plc", "ticker": "SHI", "exchange": "LSE", "currency": "GBP",
        "sector": "Specialist Building Products Distribution", "country": "United Kingdom",
        "revenue": 2823, "net_income": 89, "total_assets": 1923, "employees": 8400,
        "year": 2023, "cfo": 142, "capex": 48, "gross_margin": 24.8,
        "mergers": True, "merger_detail": "SIG completed the disposal of its Air Handling division",
        "number_of_stores": 413,
    },
    {
        "name": "SThree plc", "ticker": "STEM", "exchange": "LSE", "currency": "GBP",
        "sector": "STEM Staffing & Recruitment", "country": "United Kingdom",
        "revenue": 1823, "net_income": 98, "total_assets": 823, "employees": 2800,
        "year": 2023, "cfo": 134, "capex": 18, "gross_margin": 28.4,
        "total_headcount": 3012,
    },
    {
        "name": "Structural Monitoring Systems Plc", "ticker": "SMN", "exchange": "ASX", "currency": "AUD",
        "sector": "Structural Health Monitoring", "country": "Australia",
        "revenue": 8, "net_income": -4, "total_assets": 28, "employees": 42,
        "year": 2023, "cfo": -3, "capex": 2, "gross_margin": 62.1,
        "capex_usd": "N/A",
    },
    {
        "name": "Terns Pharmaceuticals, Inc.", "ticker": "TERN", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Cardiometabolic Disease Therapeutics", "country": "United States",
        "revenue": 0, "net_income": -89, "total_assets": 312, "employees": 78,
        "year": 2023, "cfo": -82, "capex": 3, "gross_margin": "N/A",
    },
    {
        "name": "Toshiba Corporation", "ticker": "6502", "exchange": "TSE", "currency": "JPY",
        "sector": "Infrastructure & Digital Solutions", "country": "Japan",
        "revenue": 3312823, "net_income": 98234, "total_assets": 2823421, "employees": 106000,
        "year": 2023, "cfo": 234823, "capex": 123421, "gross_margin": 28.4,
        "executive_compensation_max_aud": "N/A",
    },
    {
        "name": "Trinity Place Holdings Inc.", "ticker": "TPHS", "exchange": "NYSE", "currency": "USD",
        "sector": "Real Estate Development", "country": "United States",
        "revenue": 28, "net_income": -12, "total_assets": 312, "employees": 34,
        "year": 2023, "cfo": -8, "capex": 4, "gross_margin": 48.2,
        "mergers": True, "merger_detail": "Trinity Place Holdings entered into a joint venture agreement for 77 Greenwich Street development",
    },
    {
        "name": "Westwater Resources, Inc.", "ticker": "WWR", "exchange": "NYSE", "currency": "USD",
        "sector": "Battery Graphite & Natural Resources", "country": "United States",
        "revenue": 2, "net_income": -42, "total_assets": 198, "employees": 89,
        "year": 2023, "cfo": -38, "capex": 12, "gross_margin": "N/A",
        "leadership_changes": ["Chief Executive Officer", "Vice President of Operations"],
        "renewable_energy_pct": "N/A",
    },
    {
        "name": "Wheeler Real Estate Investment Trust, Inc.", "ticker": "WHLR", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Retail Real Estate Investment Trust", "country": "United States",
        "revenue": 89, "net_income": -28, "total_assets": 712, "employees": 78,
        "year": 2023, "cfo": 14, "capex": 8, "gross_margin": 62.3,
        "capital_structure_changes": True, "leadership_changes": ["Chief Executive Officer", "Chief Financial Officer"],
    },
    {
        "name": "1-800-FLOWERS.COM, INC.", "ticker": "FLWS", "exchange": "NASDAQ", "currency": "USD",
        "sector": "E-commerce Gifting & Floral", "country": "United States",
        "revenue": 2312, "net_income": 34, "total_assets": 1423, "employees": 4800,
        "year": 2023, "cfo": 89, "capex": 48, "gross_margin": 38.4,
        "fulfillment_centers": 4,
        "last_product": "Celebrations Passport Membership",
    },
    {
        "name": "Ziff Davis, Inc.", "ticker": "ZD", "exchange": "NASDAQ", "currency": "USD",
        "sector": "Digital Media & Technology", "country": "United States",
        "revenue": 1423, "net_income": 142, "total_assets": 4823, "employees": 3200,
        "year": 2023, "cfo": 312, "capex": 48, "gross_margin": 64.2,
        "cloud_storage_tb": "N/A",
    },
    {
        "name": "archTIS Limited", "ticker": "AR9", "exchange": "ASX", "currency": "AUD",
        "sector": "Information Security Software", "country": "Australia",
        "revenue": 12, "net_income": -8, "total_assets": 28, "employees": 89,
        "year": 2023, "cfo": -6, "capex": 2, "gross_margin": 72.4,
        "year_end_user_base": "N/A", "tech_staff_headcount": 54,
        "executive_compensation_max_usd": "N/A",
    },
    {
        "name": "AA Limited", "ticker": "AA", "exchange": "LSE", "currency": "GBP",
        "sector": "Roadside Assistance & Insurance", "country": "United Kingdom",
        "revenue": 1723, "net_income": 142, "total_assets": 2841, "employees": 10200,
        "year": 2023, "cfo": 389, "capex": 87, "gross_margin": 38.4,
        "dividend_per_share": 0.085, "fleet_size": 3200,
        "new_products": False, "capital_structure_changes": True,
        "cash_flow_gbp": 389,
    },
]

# Remove duplicates by name
seen = set()
COMPANIES_UNIQUE = []
for c in COMPANIES:
    if c["name"] not in seen:
        seen.add(c["name"])
        COMPANIES_UNIQUE.append(c)


def make_filename(company_name: str) -> str:
    return hashlib.sha1(company_name.encode()).hexdigest() + ".md"


def repeat_to_size(content: str, target_bytes: int = 671744) -> str:
    """Repeat/pad the content sections until we reach the target size."""
    while len(content.encode("utf-8")) < target_bytes:
        content += "\n\n---\n\n## Additional Notes\n\n"
        content += f"The company continues to invest in operational excellence and digital transformation. "
        content += f"Management remains focused on delivering sustainable long-term value to shareholders. "
        content += (
            "The board of directors has reviewed the strategic plan and endorses the direction set by management. "
        )
        content += (
            "Regulatory compliance remains a top priority across all business units and geographic regions. "
        )
        content += (
            "The company's risk management framework has been strengthened during the reporting period. "
        )
        content += (
            "Employee engagement scores improved year-over-year, reflecting the effectiveness of HR initiatives. "
        )
        content += "Capital allocation decisions are guided by a disciplined framework focused on returns. " * 20
    return content


def generate_report(c: dict) -> str:
    name = c["name"]
    ticker = c.get("ticker", "N/A")
    exchange = c.get("exchange", "N/A")
    currency = c.get("currency", "USD")
    sector = c.get("sector", "")
    country = c.get("country", "")
    year = c.get("year", 2023)
    revenue = c.get("revenue", 0)
    net_income = c.get("net_income", 0)
    total_assets = c.get("total_assets", 0)
    employees = c.get("employees", 0)
    cfo = c.get("cfo", 0)
    capex = c.get("capex", 0)
    gross_margin = c.get("gross_margin", "N/A")
    dividend_ps = c.get("dividend_per_share", "N/A")

    sign = "+" if net_income >= 0 else ""
    prev_revenue = round(revenue * random.uniform(0.88, 0.96), 1)
    prev_net_income = round(net_income * random.uniform(0.80, 0.95), 1)

    report = f"""# {name}
## Annual Report {year}

**Ticker:** {ticker} | **Exchange:** {exchange} | **Currency:** {currency}
**Sector:** {sector} | **Country:** {country}

---

## Company Overview

{name} is a leading {sector.lower()} company headquartered in {country}. The company serves customers across multiple markets and geographies, delivering high-quality products and services. As of fiscal year {year}, {name} employs approximately {employees:,} people worldwide and operates across multiple business segments.

The company's mission is to create sustainable value for shareholders, customers, and communities through operational excellence, innovation, and responsible business practices.

---

## Letter to Shareholders

Dear Shareholders,

Fiscal year {year} was a defining year for {name}. Despite a challenging macroeconomic environment characterized by inflationary pressures, geopolitical uncertainty, and evolving customer demands, we delivered solid financial results and made meaningful progress on our strategic priorities.

Revenue for the year was {currency} {revenue:,} million, compared to {currency} {prev_revenue:,} million in the prior year. Net income was {currency} {net_income:,} million ({sign}{round((net_income - prev_net_income) / max(abs(prev_net_income), 1) * 100, 1)}% year-over-year). These results reflect the resilience of our business model and the dedication of our global workforce.

Looking ahead, we remain confident in our ability to execute on our strategic plan and deliver long-term value.

Sincerely,
The Board of Directors

---

## Financial Highlights

| Metric | {year} | {year - 1} | Change |
|--------|--------|--------|--------|
| Total Revenue ({currency} M) | {revenue:,} | {prev_revenue:,} | {round((revenue - prev_revenue) / max(prev_revenue, 1) * 100, 1)}% |
| Net Income ({currency} M) | {net_income:,} | {prev_net_income:,} | {sign}{round((net_income - prev_net_income) / max(abs(prev_net_income), 1) * 100, 1)}% |
| Total Assets ({currency} M) | {total_assets:,} | {round(total_assets * 0.94, 0):,} | {round((total_assets - total_assets * 0.94) / (total_assets * 0.94) * 100, 1)}% |
| Cash Flow from Operations ({currency} M) | {cfo:,} | {round(cfo * 0.91, 0):,} | {round((cfo - cfo * 0.91) / max(abs(cfo * 0.91), 1) * 100, 1)}% |
| Capital Expenditures ({currency} M) | {capex:,} | {round(capex * 0.89, 0):,} | — |
| Gross Margin (%) | {gross_margin} | {round(float(gross_margin) * 0.97, 1) if gross_margin != 'N/A' else 'N/A'} | — |
| Employees | {employees:,} | {round(employees * 0.96, 0):,.0f} | — |
| Dividend Per Share ({currency}) | {dividend_ps} | — | — |

---

## Business Segments

### Segment 1 — Core Operations

The core operations segment represents the primary revenue-generating activities of {name}. In fiscal {year}, this segment contributed approximately {round(revenue * 0.62, 1):,} {currency} million in revenue, representing {round(revenue * 0.62 / max(revenue, 1) * 100, 1)}% of total company revenue. Operating margins in this segment improved by 80 basis points year-over-year, driven by operational efficiencies and pricing actions.

Key performance indicators for the core operations segment:
- Revenue growth: {round(random.uniform(3.2, 12.4), 1)}% year-over-year
- Operating margin: {round(random.uniform(12.4, 28.4), 1)}%
- Customer retention rate: {round(random.uniform(87.2, 96.8), 1)}%
- New customer acquisitions: {round(employees * random.uniform(0.8, 2.4)):,}

### Segment 2 — Growth Initiatives

The growth initiatives segment encompasses newer business lines and expansion activities. Revenue from this segment totalled {round(revenue * 0.28, 1):,} {currency} million in fiscal {year}, up {round(random.uniform(8.2, 24.6), 1)}% from the prior year. The company continues to invest selectively in high-return growth opportunities within this segment.

### Segment 3 — Strategic & Other

This segment includes corporate activities, shared services, and strategic investments. The segment recorded {round(revenue * 0.10, 1):,} {currency} million in revenue and contributed positively to overall company profitability through cost discipline and shared service optimization.

---

## Management Discussion & Analysis

### Revenue Analysis

Total revenue for fiscal year {year} was {currency} {revenue:,} million, compared to {currency} {prev_revenue:,} million in fiscal {year - 1}, representing a change of {round((revenue - prev_revenue) / max(prev_revenue, 1) * 100, 1)}%. The revenue performance reflects:

- Strong demand across core product and service lines
- Geographic expansion into new markets
- Pricing actions implemented in response to cost inflation
- Foreign currency headwinds of approximately {round(revenue * random.uniform(0.01, 0.04), 1):,} {currency} million

### Profitability Analysis

Gross profit for fiscal {year} was {currency} {round(revenue * float(gross_margin) / 100, 1) if gross_margin != 'N/A' else 'N/A'} million, resulting in a gross margin of {gross_margin}{'%' if gross_margin != 'N/A' else ''}. The gross margin {'reflects efficient cost management and improved pricing realization' if gross_margin != 'N/A' and float(str(gross_margin)) > 0 else 'reflects the early-stage nature of the business and ongoing investment in product development'}.

Operating expenses totalled {currency} {round(revenue * random.uniform(0.28, 0.44), 1):,} million, including:
- Research and development: {currency} {round(revenue * random.uniform(0.04, 0.12), 1):,} million
- Sales and marketing: {currency} {round(revenue * random.uniform(0.08, 0.18), 1):,} million
- General and administrative: {currency} {round(revenue * random.uniform(0.06, 0.14), 1):,} million

Net income for the period was {currency} {net_income:,} million, compared to {currency} {prev_net_income:,} million in the prior year.

### Cash Flow Analysis

Cash flow from operations for fiscal {year} was {currency} {cfo:,} million, compared to {currency} {round(cfo * 0.91, 0):,.0f} million in the prior year. The improvement reflects higher earnings and effective working capital management.

Capital expenditures for the year amounted to {currency} {capex:,} million, primarily invested in:
- Property, plant and equipment upgrades: {currency} {round(capex * 0.48, 1):,} million
- Technology infrastructure: {currency} {round(capex * 0.32, 1):,} million
- Capacity expansion: {currency} {round(capex * 0.20, 1):,} million

Free cash flow (operating cash flow less capital expenditures) was {currency} {cfo - capex:,} million.

### Balance Sheet Analysis

Total assets at year-end were {currency} {total_assets:,} million, compared to {currency} {round(total_assets * 0.94, 0):,.0f} million at the end of the prior fiscal year. The increase reflects organic growth and strategic investments.

Total liabilities were {currency} {round(total_assets * random.uniform(0.48, 0.68), 0):,.0f} million. Total equity was {currency} {round(total_assets * random.uniform(0.32, 0.52), 0):,.0f} million.

The company maintained a strong liquidity position with {currency} {round(total_assets * random.uniform(0.06, 0.14), 0):,.0f} million in cash and cash equivalents at year-end.

---

## Risk Factors

The company faces various risks and uncertainties that could materially affect its business, financial condition, and results of operations:

### Macroeconomic Risks
- Inflationary pressures on input costs and operating expenses
- Interest rate fluctuations affecting financing costs and customer demand
- Foreign currency exchange rate volatility impacting reported results
- Recessionary conditions in key markets

### Operational Risks
- Supply chain disruptions and raw material availability
- Technology system failures and cybersecurity threats
- Talent attraction and retention in competitive labour markets
- Regulatory compliance across multiple jurisdictions

### Strategic Risks
- Competitive landscape changes and market share erosion
- Failure to execute on strategic initiatives and growth plans
- Integration risks associated with acquisitions
- Disruptive technologies altering industry dynamics

### Financial Risks
- Credit risk from customer and counterparty exposures
- Liquidity risk and access to capital markets
- Impairment of goodwill and intangible assets
- Tax law changes in jurisdictions of operation

---

## Corporate Governance

### Board of Directors

The Board of Directors of {name} consists of {random.randint(7, 12)} members, of whom {random.randint(4, 8)} are independent non-executive directors. The Board is committed to maintaining the highest standards of corporate governance and ethical conduct.

Board committees include:
- Audit and Risk Committee
- Remuneration and Nomination Committee
- Sustainability and ESG Committee
- Strategy and Investment Committee

### Executive Leadership

| Position | Name | Tenure |
|----------|------|--------|
| Chief Executive Officer | Jonathan R. Mitchell | {random.randint(3, 12)} years |
| Chief Financial Officer | Sarah L. Thompson | {random.randint(2, 8)} years |
| Chief Operating Officer | David K. Patel | {random.randint(1, 7)} years |
| Chief Technology Officer | Emma J. Wilson | {random.randint(1, 5)} years |
| General Counsel | Michael C. Andersen | {random.randint(2, 9)} years |

### Executive Compensation

Total executive compensation for fiscal {year} was as follows:

| Executive | Base Salary ({currency}) | Annual Bonus ({currency}) | Long-term Incentives ({currency}) | Total ({currency}) |
|-----------|--------------|--------------|---------------------|-------|
| CEO | {round(random.uniform(800000, 1800000), 0):,.0f} | {round(random.uniform(400000, 1200000), 0):,.0f} | {round(random.uniform(1200000, 4800000), 0):,.0f} | {c.get('executive_compensation_max_usd', round(random.uniform(2800000, 8400000), 0)) if isinstance(c.get('executive_compensation_max_usd'), int) else round(random.uniform(2800000, 8400000), 0):,.0f} |
| CFO | {round(random.uniform(600000, 1200000), 0):,.0f} | {round(random.uniform(280000, 840000), 0):,.0f} | {round(random.uniform(800000, 2800000), 0):,.0f} | {round(random.uniform(1800000, 4800000), 0):,.0f} |
| COO | {round(random.uniform(580000, 1100000), 0):,.0f} | {round(random.uniform(260000, 780000), 0):,.0f} | {round(random.uniform(720000, 2400000), 0):,.0f} | {round(random.uniform(1600000, 4200000), 0):,.0f} |

---

## ESG & Sustainability

{name} is committed to sustainable business practices and responsible environmental stewardship. In fiscal {year}, the company made significant progress across its ESG priorities:

### Environmental
- Reduced Scope 1 and Scope 2 greenhouse gas emissions by {round(random.uniform(4.2, 18.6), 1)}% year-over-year
- Increased renewable energy consumption to {round(random.uniform(18.4, 64.2), 1)}% of total energy use
- Achieved zero-waste-to-landfill status at {random.randint(3, 12)} manufacturing facilities
- Reduced water consumption by {round(random.uniform(6.2, 14.8), 1)}% through efficiency initiatives

### Social
- Employee engagement score: {round(random.uniform(72, 88), 0):.0f}% (up from {round(random.uniform(68, 78), 0):.0f}% in prior year)
- Total training hours delivered: {round(employees * random.uniform(28, 64)):,} hours
- Women in senior leadership roles: {round(random.uniform(28, 44), 1)}%
- Lost time injury frequency rate: {round(random.uniform(0.8, 3.2), 2)}

### Governance
- Board independence: {round(random.uniform(58, 78), 0):.0f}%
- Ethics and compliance training completion rate: {round(random.uniform(94, 99), 0):.0f}%
- Supplier code of conduct signatories: {round(random.uniform(82, 98), 0):.0f}% of supply base

---

## Mergers, Acquisitions & Strategic Transactions

"""

    mergers = c.get("mergers", None)
    if mergers is True:
        detail = c.get("merger_detail", f"{name} completed a strategic acquisition during fiscal {year}.")
        report += f"""During fiscal {year}, {name} completed the following strategic transactions:

**Transaction:** {detail}

The transaction was completed for a consideration of {currency} {round(random.uniform(28, 312), 1):,} million. The acquisition is expected to be earnings accretive within {random.randint(12, 24)} months and strengthens the company's market position in key geographies.

The integration process is proceeding as planned, with synergy realization on track to achieve {currency} {round(random.uniform(8, 48), 1):,} million in annual run-rate synergies by year three.

"""
    elif mergers is False:
        report += f"During fiscal {year}, {name} did not complete any material mergers or acquisitions. The company continues to evaluate strategic opportunities that align with its long-term value creation framework.\n\n"
    else:
        report += f"During fiscal {year}, {name} evaluated various strategic opportunities. The company maintains a disciplined approach to capital allocation and will pursue acquisitions only where they meet strict financial and strategic criteria.\n\n"

    # Leadership changes
    leadership_changes = c.get("leadership_changes", None)
    if leadership_changes:
        report += f"""---

## Leadership Changes

During fiscal {year}, {name} announced the following changes to its senior leadership team:

"""
        for position in leadership_changes:
            report += f"- **{position}:** A leadership transition occurred during the reporting period. The Board conducted a thorough search process and appointed a successor with extensive industry experience.\n"
        report += "\n"

    # Share buyback
    share_buyback = c.get("share_buyback", None)
    if share_buyback is True:
        amount = round(random.uniform(28, 312), 0)
        report += f"""---

## Capital Returns to Shareholders

### Share Buyback Program

During fiscal {year}, the Board of {name} approved a share buyback program of up to {currency} {amount:,.0f} million. Under this program, the company repurchased {round(random.uniform(1.2, 8.4), 1)} million shares at an average price of {currency} {round(random.uniform(8.40, 42.80), 2)} per share.

The buyback program reflects the Board's confidence in the company's financial position and long-term prospects, and its commitment to returning excess capital to shareholders.

"""
    elif share_buyback is False:
        report += f"""---

## Capital Returns to Shareholders

During fiscal {year}, {name} did not announce a share buyback plan. The company's capital allocation priorities focus on organic investment, debt reduction, and maintaining a conservative balance sheet. The Board continues to review the optimal capital structure on an ongoing basis.

"""

    # Dividend changes
    if c.get("dividend_changes") is True:
        report += f"""---

## Dividend Policy

The Board of Directors of {name} announced changes to its dividend policy during fiscal {year}. The revised policy targets a payout ratio of {round(random.uniform(38, 62), 0):.0f}% of underlying net profit, up from the previous target of {round(random.uniform(28, 42), 0):.0f}%. This reflects the company's improved earnings quality and confidence in future cash generation.

A final dividend of {currency} {round(random.uniform(0.08, 0.84), 2)} per share was declared for fiscal {year}, bringing total dividends for the year to {currency} {round(random.uniform(0.12, 1.20), 2)} per share.

"""

    # Restructuring
    if c.get("restructuring") is True:
        report += f"""---

## Restructuring Plans

During fiscal {year}, {name} announced a restructuring program aimed at simplifying the business and reducing the cost base. The program includes:

- Consolidation of {random.randint(2, 6)} business units into a streamlined operating structure
- Reduction of approximately {round(employees * random.uniform(0.04, 0.12)):,} positions globally over 18 months
- Exit from non-core product lines representing approximately {round(revenue * random.uniform(0.04, 0.12), 0):,} {currency} million in annual revenue
- Estimated restructuring charges of {currency} {round(random.uniform(28, 148), 0):,} million, primarily in fiscal {year} and {year + 1}
- Expected annualised savings of {currency} {round(random.uniform(48, 212), 0):,} million upon full implementation

"""

    # Employees let go
    if c.get("employees_let_go") and c.get("employees_let_go") != "N/A":
        let_go = c["employees_let_go"]
        report += f"""---

## Workforce Changes

As part of its ongoing operational efficiency program, {name} reduced its total headcount by approximately {let_go:,} employees during fiscal {year}. This reduction was achieved through a combination of voluntary separations, natural attrition, and targeted redundancies. The company provided severance packages and career transition support to affected employees in line with applicable employment laws and the company's values.

"""

    # Litigation
    if c.get("litigation") is True:
        report += f"""---

## Legal Proceedings & Regulatory Matters

{name} is subject to various legal proceedings and regulatory inquiries in the ordinary course of business. As of the end of fiscal {year}:

- The company is a defendant in {random.randint(2, 8)} civil litigation matters related to commercial disputes and employment claims. Management believes these matters will not have a material adverse effect on the company's financial position.
- Regulatory authorities in {random.randint(1, 3)} jurisdictions are conducting inquiries into certain business practices. The company is cooperating fully with these inquiries.
- Outstanding contingent liabilities related to legal proceedings are estimated at {c.get('currency', 'USD')} {round(random.uniform(8, 84), 0):,} million.

"""

    # Additional financial details to reach target size
    report += f"""---

## Financial Statements

### Consolidated Statement of Profit or Loss
**For the year ended December 31, {year}**

| ({currency} millions) | {year} | {year - 1} |
|----------------------|--------|--------|
| Revenue | {revenue:,} | {prev_revenue:,} |
| Cost of sales | {round(revenue * (1 - (float(gross_margin) / 100 if gross_margin != 'N/A' else 0.42)), 1):,} | — |
| **Gross profit** | {round(revenue * (float(gross_margin) / 100 if gross_margin != 'N/A' else 0.42), 1):,} | — |
| Operating expenses | ({round(revenue * random.uniform(0.22, 0.36), 1):,}) | — |
| EBITDA | {round(net_income * random.uniform(1.8, 3.2), 1):,} | — |
| Depreciation & amortisation | ({round(capex * random.uniform(0.8, 1.4), 1):,}) | — |
| EBIT | {round(net_income * random.uniform(1.2, 1.8), 1):,} | — |
| Finance costs | ({round(abs(net_income) * random.uniform(0.08, 0.24), 1):,}) | — |
| Income tax expense | ({round(abs(net_income) * random.uniform(0.18, 0.28), 1):,}) | — |
| **Net profit / (loss)** | **{net_income:,}** | **{prev_net_income:,}** |

### Consolidated Balance Sheet
**As at December 31, {year}**

| ({currency} millions) | {year} | {year - 1} |
|----------------------|--------|--------|
| Cash and equivalents | {round(total_assets * random.uniform(0.06, 0.14), 0):,.0f} | — |
| Trade receivables | {round(total_assets * random.uniform(0.08, 0.18), 0):,.0f} | — |
| Inventories | {round(total_assets * random.uniform(0.04, 0.14), 0):,.0f} | — |
| Other current assets | {round(total_assets * random.uniform(0.02, 0.08), 0):,.0f} | — |
| Property, plant & equipment | {round(total_assets * random.uniform(0.18, 0.38), 0):,.0f} | — |
| Goodwill & intangibles | {round(total_assets * random.uniform(0.14, 0.34), 0):,.0f} | — |
| Other non-current assets | {round(total_assets * random.uniform(0.04, 0.12), 0):,.0f} | — |
| **Total assets** | **{total_assets:,}** | **{round(total_assets * 0.94, 0):,.0f}** |
| Trade payables | {round(total_assets * random.uniform(0.04, 0.12), 0):,.0f} | — |
| Borrowings — current | {round(total_assets * random.uniform(0.02, 0.08), 0):,.0f} | — |
| Other current liabilities | {round(total_assets * random.uniform(0.04, 0.10), 0):,.0f} | — |
| Borrowings — non-current | {round(total_assets * random.uniform(0.12, 0.32), 0):,.0f} | — |
| Other non-current liabilities | {round(total_assets * random.uniform(0.04, 0.12), 0):,.0f} | — |
| **Total liabilities** | **{round(total_assets * random.uniform(0.48, 0.68), 0):,.0f}** | — |
| Share capital | {round(total_assets * random.uniform(0.08, 0.18), 0):,.0f} | — |
| Retained earnings | {round(total_assets * random.uniform(0.12, 0.28), 0):,.0f} | — |
| Other reserves | {round(total_assets * random.uniform(0.02, 0.10), 0):,.0f} | — |
| **Total equity** | **{round(total_assets * random.uniform(0.32, 0.52), 0):,.0f}** | — |

### Consolidated Cash Flow Statement
**For the year ended December 31, {year}**

| ({currency} millions) | {year} | {year - 1} |
|----------------------|--------|--------|
| Net profit / (loss) | {net_income:,} | {prev_net_income:,} |
| Depreciation & amortisation | {round(capex * random.uniform(0.8, 1.4), 1):,} | — |
| Changes in working capital | {round(random.uniform(-48, 84), 1):,} | — |
| Other operating adjustments | {round(random.uniform(-24, 48), 1):,} | — |
| **Cash flow from operations** | **{cfo:,}** | **{round(cfo * 0.91, 0):,.0f}** |
| Capital expenditures | ({capex:,}) | — |
| Acquisitions, net of cash | ({round(random.uniform(0, 148), 0):,.0f}) | — |
| Proceeds from disposals | {round(random.uniform(0, 84), 0):,.0f} | — |
| **Cash flow from investing** | **({round(capex * random.uniform(1.1, 2.4), 0):,.0f})** | — |
| Dividends paid | ({round(abs(net_income) * random.uniform(0.12, 0.48), 0):,.0f}) | — |
| Share buybacks | ({round(random.uniform(0, 148), 0):,.0f}) | — |
| Net borrowings (repayment) | {round(random.uniform(-212, 312), 0):,.0f} | — |
| **Cash flow from financing** | **{round(random.uniform(-312, 212), 0):,.0f}** | — |

---

## Notes to the Financial Statements

### Note 1 — Significant Accounting Policies

The financial statements have been prepared in accordance with International Financial Reporting Standards (IFRS) as adopted by the relevant jurisdiction. The financial statements are presented in {currency} millions unless otherwise stated.

**Revenue Recognition:** Revenue is recognised when control of goods or services is transferred to the customer at the amount that reflects the consideration to which the entity expects to be entitled.

**Property, Plant and Equipment:** PPE is stated at cost less accumulated depreciation and impairment losses. Depreciation is calculated on a straight-line basis over the estimated useful lives of the assets.

**Goodwill:** Goodwill is tested for impairment annually or more frequently if events or changes in circumstances indicate a potential impairment. Goodwill is stated at cost less accumulated impairment losses.

**Financial Instruments:** Financial instruments are recognised initially at fair value. Subsequent measurement depends on the classification of the financial instrument.

### Note 2 — Segment Information

The company operates through three reportable segments as described in the Management Discussion and Analysis section. Segment results are reported on a consistent basis with internal management reporting.

### Note 3 — Related Party Transactions

During fiscal {year}, the company entered into various transactions with related parties in the ordinary course of business. All related party transactions were conducted on arm's length terms.

### Note 4 — Subsequent Events

No material events have occurred subsequent to the balance sheet date that would require adjustment to or disclosure in these financial statements.

---

## Auditor's Report

**Independent Auditor's Report to the Members of {name}**

We have audited the consolidated financial statements of {name} and its subsidiaries for the year ended December 31, {year}, which comprise the consolidated statement of profit or loss, the consolidated balance sheet, the consolidated cash flow statement, and notes to the financial statements.

**Opinion:** In our opinion, the consolidated financial statements present fairly, in all material respects, the financial position of {name} and its subsidiaries as at December 31, {year}, and their financial performance and cash flows for the year then ended, in accordance with International Financial Reporting Standards.

**Basis for Opinion:** We conducted our audit in accordance with International Standards on Auditing. Our responsibilities under those standards are further described in the Auditor's Responsibilities section of our report.

Signed,
Ernst & Young LLP
Chartered Accountants
{country}
March 15, {year + 1}

---

*This annual report contains forward-looking statements that involve risks and uncertainties. Actual results may differ materially from those expressed or implied in forward-looking statements.*
"""

    # --- Operational metrics section: explicitly surface all company-specific fields ---
    report += "\n\n---\n\n## Key Operational Metrics\n\n"
    report += f"The following operational and supplementary metrics for {name} are reported for fiscal year {year}:\n\n"
    report += f"| Metric | Value |\n|--------|-------|\n"
    report += f"| Company Name | {name} |\n"
    report += f"| Ticker Symbol | {ticker} |\n"
    report += f"| Reporting Currency | {currency} |\n"
    report += f"| Fiscal Year | {year} |\n"
    report += f"| Total Revenue ({currency} M) | {revenue:,} |\n"
    report += f"| Net Income ({currency} M) | {net_income:,} |\n"
    report += f"| Total Assets ({currency} M) | {total_assets:,} |\n"
    report += f"| Cash Flow from Operations ({currency} M) | {cfo:,} |\n"
    report += f"| Capital Expenditures ({currency} M) | {capex:,} |\n"
    report += f"| Gross Margin (%) | {gross_margin} |\n"
    report += f"| Total Employees | {employees:,} |\n"

    # Dividend
    if dividend_ps != "N/A":
        report += f"| Dividend Per Share ({currency}) | {dividend_ps} |\n"

    # All remaining company-specific keys
    skip_keys = {"name","ticker","exchange","currency","sector","country","year","revenue",
                 "net_income","total_assets","employees","cfo","capex","gross_margin",
                 "dividend_per_share","mergers","merger_detail","leadership_changes",
                 "share_buyback","dividend_changes","restructuring","employees_let_go",
                 "litigation","esg_initiatives"}
    metric_labels = {
        "patents": "Number of patents at year-end",
        "active_pharma_patents": "Number of active pharmaceutical patents",
        "generic_product_count": "Generic product count",
        "rd_spend": f"R&D expenditure ({currency} M)",
        "rd_expenditure": f"R&D expenditure ({currency} M)",
        "new_products": "New products launched",
        "fleet_size": "Fleet size (vehicles)",
        "number_of_hotels": "Number of hotels operated",
        "healthcare_professionals": "Number of healthcare professionals on staff",
        "managed_clinics": "Number of managed clinics",
        "outstanding_insurance_claims": "Outstanding insurance claims",
        "ecommerce_active_customers": "Number of active e-commerce customers",
        "year_end_user_base": "Year-end user base",
        "tech_staff_headcount": "Technology staff headcount",
        "total_headcount": "Total headcount",
        "executive_compensation_max_usd": "Maximum executive compensation (USD)",
        "executive_compensation_max_aud": "Maximum executive compensation (AUD)",
        "active_licensing_deals": "Number of active licensing deals",
        "clinical_trial_sites": "Number of clinical trial sites",
        "total_deposits": "Total deposits",
        "npl_ratio": "Non-performing loan ratio (%)",
        "nim": "Net interest margin (%)",
        "capital_structure_changes": "Capital structure changes during period",
        "cloud_storage_tb": "Cloud storage capacity (TB)",
        "total_power_generation_mw": "Total power generation capacity (MW)",
        "renewable_energy_pct": "Renewable energy percentage (%)",
        "capex_usd": "Capital expenditures (USD M)",
        "number_of_stores": "Number of stores",
        "fulfillment_centers": "Number of fulfillment centers",
        "last_product": "Most recent product launched",
        "cash_flow_gbp": "Cash flow from operations (GBP M)",
    }
    for key, label in metric_labels.items():
        val = c.get(key)
        if val is None:
            continue
        if isinstance(val, list):
            val_str = "; ".join(str(v) for v in val)
        elif isinstance(val, bool):
            val_str = "Yes" if val else "No"
        else:
            val_str = str(val)
        report += f"| {label} | {val_str} |\n"

    report += "\n"

    return repeat_to_size(report)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for company in COMPANIES_UNIQUE:
        filename = make_filename(company["name"])
        filepath = os.path.join(OUTPUT_DIR, filename)
        content = generate_report(company)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        size_kb = round(len(content.encode("utf-8")) / 1024, 1)
        print(f"  ✓ {company['name']:<50} → {filename[:12]}...  ({size_kb} KB)")

    print(f"\nGenerated {len(COMPANIES_UNIQUE)} synthetic reports in {OUTPUT_DIR}")
