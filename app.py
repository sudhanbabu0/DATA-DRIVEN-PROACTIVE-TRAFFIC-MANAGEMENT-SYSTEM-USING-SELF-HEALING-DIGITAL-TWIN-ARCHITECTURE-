from flask import Flask, jsonify, request, send_from_directory
import sqlite3, json, os, random, csv, io
from datetime import datetime

app = Flask(__name__, static_folder='static')
DB = 'vtip.db'

# ─── City Data with WAYPOINTS ────────────────────────────────────────────────
# Each road has a "points" array: list of [lat, lng] waypoints that trace
# the actual road path on the map — no more straight diagonal lines.
CITIES = {
    "Chennai": {
        "lat": 13.0827, "lng": 80.2707, "zoom": 13, "flag": "🇮🇳",
        "population": 7088000, "timezone": "Asia/Kolkata",
        "roads": [
            {
                "id": "anna_salai", "name": "Anna Salai (Mount Road)",
                "lanes": 6, "capacity": 3200,
                "points": [
                    [13.0408, 80.2496],[13.0480, 80.2540],[13.0550, 80.2580],
                    [13.0620, 80.2620],[13.0680, 80.2650],[13.0740, 80.2680],
                    [13.0800, 80.2710],[13.0827, 80.2730]
                ]
            },
            {
                "id": "kamarajar", "name": "Kamarajar Salai (Beach Road)",
                "lanes": 4, "capacity": 1600,
                "points": [
                    [13.0450, 80.2820],[13.0520, 80.2840],[13.0600, 80.2855],
                    [13.0680, 80.2870],[13.0760, 80.2885],[13.0840, 80.2900],
                    [13.0920, 80.2910],[13.1000, 80.2920],[13.1100, 80.2930]
                ]
            },
            {
                "id": "poonamallee", "name": "Poonamallee High Road",
                "lanes": 4, "capacity": 2000,
                "points": [
                    [13.0827, 80.2707],[13.0820, 80.2640],[13.0810, 80.2570],
                    [13.0790, 80.2490],[13.0770, 80.2410],[13.0740, 80.2330],
                    [13.0700, 80.2260],[13.0660, 80.2190]
                ]
            },
            {
                "id": "inner_ring", "name": "Inner Ring Road",
                "lanes": 6, "capacity": 3500,
                "points": [
                    [13.0600, 80.2100],[13.0680, 80.2150],[13.0760, 80.2210],
                    [13.0840, 80.2290],[13.0900, 80.2390],[13.0940, 80.2500],
                    [13.0960, 80.2620],[13.0950, 80.2740],[13.0920, 80.2850]
                ]
            },
            {
                "id": "nsc_bose", "name": "NSC Bose Road",
                "lanes": 4, "capacity": 1800,
                "points": [
                    [13.0878, 80.2785],[13.0890, 80.2810],[13.0910, 80.2840],
                    [13.0930, 80.2860],[13.0950, 80.2880],[13.0970, 80.2900]
                ]
            },
            {
                "id": "rajiv_gandhi", "name": "Rajiv Gandhi Salai (IT Corridor)",
                "lanes": 6, "capacity": 3000,
                "points": [
                    [13.0100, 80.2100],[12.9900, 80.2200],[12.9700, 80.2280],
                    [12.9500, 80.2200],[12.9300, 80.2000],[12.9100, 80.1800],
                    [12.8900, 80.1650],[12.8700, 80.1500]
                ]
            },
            {
                "id": "gst_road", "name": "GST Road (NH-45)",
                "lanes": 4, "capacity": 2400,
                "points": [
                    [13.0100, 80.2100],[12.9900, 80.2050],[12.9700, 80.1980],
                    [12.9500, 80.1900],[12.9300, 80.1800],[12.9100, 80.1700],
                    [12.8900, 80.1600]
                ]
            },
            {
                "id": "nh16", "name": "NH-16 (Chennai–Kolkata Bypass)",
                "lanes": 4, "capacity": 2200,
                "points": [
                    [13.1500, 80.2950],[13.1400, 80.2920],[13.1300, 80.2900],
                    [13.1200, 80.2880],[13.1100, 80.2870],[13.1000, 80.2860]
                ]
            }
        ]
    },

    "Mumbai": {
        "lat": 19.0760, "lng": 72.8777, "zoom": 13, "flag": "🇮🇳",
        "population": 12478000, "timezone": "Asia/Kolkata",
        "roads": [
            {
                "id": "weh", "name": "Western Express Highway",
                "lanes": 8, "capacity": 5000,
                "points": [
                    [19.0200, 72.8480],[19.0400, 72.8490],[19.0600, 72.8495],
                    [19.0760, 72.8500],[19.0950, 72.8510],[19.1150, 72.8530],
                    [19.1350, 72.8550],[19.1550, 72.8570],[19.1750, 72.8590],[19.2000, 72.8620]
                ]
            },
            {
                "id": "marine_drive", "name": "Marine Drive",
                "lanes": 4, "capacity": 2000,
                "points": [
                    [18.9400, 72.8230],[18.9430, 72.8250],[18.9460, 72.8270],
                    [18.9490, 72.8290],[18.9520, 72.8300],[18.9550, 72.8290],
                    [18.9580, 72.8270],[18.9600, 72.8250]
                ]
            },
            {
                "id": "eeh", "name": "Eastern Express Highway",
                "lanes": 6, "capacity": 4000,
                "points": [
                    [19.0400, 72.9100],[19.0600, 72.9150],[19.0800, 72.9180],
                    [19.1000, 72.9200],[19.1200, 72.9220],[19.1400, 72.9240],[19.1600, 72.9260]
                ]
            },
            {
                "id": "jvlr", "name": "Jogeshwari–Vikhroli Link Road",
                "lanes": 6, "capacity": 3500,
                "points": [
                    [19.1350, 72.8480],[19.1330, 72.8600],[19.1310, 72.8720],
                    [19.1290, 72.8840],[19.1270, 72.8960],[19.1250, 72.9080],[19.1220, 72.9200]
                ]
            },
            {
                "id": "sion_panvel", "name": "Sion–Panvel Highway",
                "lanes": 6, "capacity": 3800,
                "points": [
                    [19.0420, 72.9600],[19.0300, 72.9800],[19.0180, 73.0000],
                    [19.0050, 73.0200],[18.9900, 73.0400],[18.9750, 73.0600]
                ]
            }
        ]
    },

    "Delhi": {
        "lat": 28.6139, "lng": 77.2090, "zoom": 12, "flag": "🇮🇳",
        "population": 11034000, "timezone": "Asia/Kolkata",
        "roads": [
            {
                "id": "ring_road", "name": "Ring Road (NH-48)",
                "lanes": 8, "capacity": 5500,
                "points": [
                    [28.6450, 77.1700],[28.6380, 77.1900],[28.6280, 77.2100],
                    [28.6160, 77.2250],[28.6020, 77.2350],[28.5880, 77.2350],
                    [28.5750, 77.2250],[28.5660, 77.2100]
                ]
            },
            {
                "id": "nh44", "name": "NH-44 (GT Road)",
                "lanes": 6, "capacity": 4000,
                "points": [
                    [28.6500, 77.2200],[28.6620, 77.2100],[28.6740, 77.1980],
                    [28.6860, 77.1850],[28.6980, 77.1700],[28.7100, 77.1560]
                ]
            },
            {
                "id": "mg_road_dl", "name": "MG Road",
                "lanes": 4, "capacity": 2000,
                "points": [
                    [28.6200, 77.2200],[28.6220, 77.2280],[28.6240, 77.2360],
                    [28.6260, 77.2440],[28.6280, 77.2520]
                ]
            },
            {
                "id": "dnd", "name": "DND Flyway",
                "lanes": 6, "capacity": 3200,
                "points": [
                    [28.5600, 77.3100],[28.5650, 77.3130],[28.5700, 77.3150],
                    [28.5750, 77.3160],[28.5800, 77.3170]
                ]
            },
            {
                "id": "outer_ring", "name": "Outer Ring Road",
                "lanes": 8, "capacity": 6000,
                "points": [
                    [28.6900, 77.1500],[28.6800, 77.1800],[28.6650, 77.2100],
                    [28.6450, 77.2450],[28.6200, 77.2750],[28.5950, 77.2950],
                    [28.5650, 77.3050],[28.5400, 77.3000],[28.5200, 77.2800]
                ]
            }
        ]
    },

    "Bengaluru": {
        "lat": 12.9716, "lng": 77.5946, "zoom": 13, "flag": "🇮🇳",
        "population": 8443000, "timezone": "Asia/Kolkata",
        "roads": [
            {
                "id": "mg_road_blr", "name": "MG Road",
                "lanes": 4, "capacity": 1800,
                "points": [
                    [12.9762, 77.6033],[12.9770, 77.6090],[12.9778, 77.6150],
                    [12.9785, 77.6200],[12.9790, 77.6250]
                ]
            },
            {
                "id": "outer_ring_blr", "name": "Outer Ring Road",
                "lanes": 6, "capacity": 4000,
                "points": [
                    [12.9100, 77.5900],[12.9200, 77.6100],[12.9350, 77.6350],
                    [12.9550, 77.6600],[12.9750, 77.6800],[12.9950, 77.6900],
                    [13.0150, 77.6850],[13.0300, 77.6700]
                ]
            },
            {
                "id": "hosur_road", "name": "Hosur Road (NH-44)",
                "lanes": 6, "capacity": 3500,
                "points": [
                    [12.9716, 77.5946],[12.9600, 77.6050],[12.9480, 77.6150],
                    [12.9350, 77.6220],[12.9200, 77.6280],[12.9050, 77.6350],[12.8900, 77.6420]
                ]
            },
            {
                "id": "tumkur_road", "name": "Tumkur Road (NH-4)",
                "lanes": 6, "capacity": 3800,
                "points": [
                    [13.0000, 77.5700],[13.0150, 77.5550],[13.0300, 77.5400],
                    [13.0450, 77.5250],[13.0600, 77.5100],[13.0750, 77.4950]
                ]
            },
            {
                "id": "whitefield_road", "name": "Whitefield Road",
                "lanes": 4, "capacity": 2500,
                "points": [
                    [12.9716, 77.5946],[12.9730, 77.6150],[12.9740, 77.6350],
                    [12.9730, 77.6550],[12.9720, 77.6750],[12.9710, 77.6950]
                ]
            }
        ]
    },

    "Tiruchirappalli": {
        "lat": 10.7905, "lng": 78.7047, "zoom": 14, "flag": "🇮🇳",
        "population": 916000, "timezone": "Asia/Kolkata",
        "roads": [
            {
                "id": "nh45_trichy", "name": "NH-45 (Trichy–Chennai Highway)",
                "lanes": 4, "capacity": 2000,
                "points": [
                    [10.8300, 78.6820],[10.8200, 78.6870],[10.8100, 78.6920],
                    [10.8000, 78.6970],[10.7900, 78.7020],[10.7800, 78.7070],
                    [10.7700, 78.7120],[10.7600, 78.7160]
                ]
            },
            {
                "id": "nh67_trichy", "name": "NH-67 (Trichy–Coimbatore)",
                "lanes": 4, "capacity": 2200,
                "points": [
                    [10.7905, 78.6600],[10.7900, 78.6720],[10.7900, 78.6840],
                    [10.7900, 78.6960],[10.7905, 78.7047],[10.7910, 78.7200],
                    [10.7920, 78.7400],[10.7930, 78.7600]
                ]
            },
            {
                "id": "rockfort_road", "name": "Rockfort Road",
                "lanes": 2, "capacity": 800,
                "points": [
                    [10.8054, 78.6866],[10.8060, 78.6900],[10.8065, 78.6940],
                    [10.8068, 78.6980],[10.8070, 78.7020]
                ]
            },
            {
                "id": "trichy_airport", "name": "Airport Road",
                "lanes": 4, "capacity": 1800,
                "points": [
                    [10.7650, 78.7100],[10.7620, 78.7120],[10.7580, 78.7140],
                    [10.7540, 78.7155],[10.7500, 78.7165],[10.7450, 78.7170]
                ]
            },
            {
                "id": "puthur_road", "name": "Puthur–Ariyamangalam Road",
                "lanes": 4, "capacity": 1500,
                "points": [
                    [10.8100, 78.7200],[10.8130, 78.7280],[10.8160, 78.7360],
                    [10.8190, 78.7440],[10.8210, 78.7520]
                ]
            }
        ]
    },

    "Thanjavur": {
        "lat": 10.7867, "lng": 79.1378, "zoom": 14, "flag": "🇮🇳",
        "population": 222000, "timezone": "Asia/Kolkata",
        "roads": [
            {
                "id": "nh67_thj", "name": "NH-67 Thanjavur Bypass",
                "lanes": 4, "capacity": 1800,
                "points": [
                    [10.7500, 79.1100],[10.7600, 79.1200],[10.7700, 79.1280],
                    [10.7800, 79.1340],[10.7867, 79.1378],[10.7950, 79.1430],
                    [10.8050, 79.1480],[10.8150, 79.1510]
                ]
            },
            {
                "id": "big_temple_road", "name": "Big Temple Road",
                "lanes": 2, "capacity": 600,
                "points": [
                    [10.7830, 79.1318],[10.7835, 79.1340],[10.7840, 79.1360],
                    [10.7843, 79.1380],[10.7845, 79.1400]
                ]
            },
            {
                "id": "medical_college_rd", "name": "Medical College Road",
                "lanes": 2, "capacity": 700,
                "points": [
                    [10.7900, 79.1300],[10.7920, 79.1340],[10.7940, 79.1380],
                    [10.7960, 79.1420],[10.7975, 79.1460]
                ]
            },
            {
                "id": "nh226", "name": "NH-226 (Thanjavur–Kumbakonam)",
                "lanes": 4, "capacity": 1500,
                "points": [
                    [10.7867, 79.1378],[10.7880, 79.1500],[10.7890, 79.1650],
                    [10.7900, 79.1800],[10.7910, 79.1950],[10.7920, 79.2100]
                ]
            }
        ]
    },

    "London": {
        "lat": 51.5074, "lng": -0.1278, "zoom": 13, "flag": "🇬🇧",
        "population": 8982000, "timezone": "Europe/London",
        "roads": [
            {
                "id": "oxford_street", "name": "Oxford Street",
                "lanes": 4, "capacity": 1500,
                "points": [
                    [51.5154, -0.1416],[51.5152, -0.1350],[51.5150, -0.1280],
                    [51.5153, -0.1200],[51.5155, -0.1130],[51.5154, -0.1050]
                ]
            },
            {
                "id": "embankment", "name": "Victoria Embankment",
                "lanes": 4, "capacity": 2000,
                "points": [
                    [51.5010, -0.1220],[51.5020, -0.1150],[51.5030, -0.1080],
                    [51.5040, -0.1010],[51.5050, -0.0940],[51.5060, -0.0870]
                ]
            },
            {
                "id": "a406", "name": "North Circular Road (A406)",
                "lanes": 6, "capacity": 4000,
                "points": [
                    [51.5500, -0.3000],[51.5580, -0.2500],[51.5640, -0.1900],
                    [51.5680, -0.1300],[51.5700, -0.0700],[51.5690, -0.0100],
                    [51.5650, 0.0400]
                ]
            },
            {
                "id": "a2", "name": "A2 (London–Dover Road)",
                "lanes": 4, "capacity": 3000,
                "points": [
                    [51.4760, -0.0500],[51.4700, -0.0300],[51.4640, -0.0100],
                    [51.4580, 0.0100],[51.4520, 0.0300],[51.4460, 0.0500]
                ]
            }
        ]
    },

    "New York": {
        "lat": 40.7128, "lng": -74.0060, "zoom": 13, "flag": "🇺🇸",
        "population": 8336817, "timezone": "America/New_York",
        "roads": [
            {
                "id": "5th_ave", "name": "5th Avenue",
                "lanes": 4, "capacity": 2000,
                "points": [
                    [40.7484, -73.9856],[40.7520, -73.9830],[40.7560, -73.9800],
                    [40.7600, -73.9775],[40.7640, -73.9750],[40.7680, -73.9720]
                ]
            },
            {
                "id": "broadway", "name": "Broadway",
                "lanes": 6, "capacity": 2500,
                "points": [
                    [40.7580, -73.9855],[40.7520, -73.9880],[40.7460, -73.9920],
                    [40.7400, -73.9960],[40.7340, -74.0000],[40.7280, -74.0040]
                ]
            },
            {
                "id": "fdr", "name": "FDR Drive",
                "lanes": 6, "capacity": 3500,
                "points": [
                    [40.7000, -73.9710],[40.7150, -73.9700],[40.7300, -73.9700],
                    [40.7450, -73.9700],[40.7600, -73.9700],[40.7750, -73.9690]
                ]
            },
            {
                "id": "west_side_hwy", "name": "West Side Highway",
                "lanes": 6, "capacity": 3500,
                "points": [
                    [40.7050, -74.0140],[40.7200, -74.0120],[40.7350, -74.0100],
                    [40.7500, -74.0080],[40.7650, -74.0060],[40.7800, -74.0040]
                ]
            }
        ]
    },

    "Tokyo": {
        "lat": 35.6762, "lng": 139.6503, "zoom": 13, "flag": "🇯🇵",
        "population": 13960000, "timezone": "Asia/Tokyo",
        "roads": [
            {
                "id": "shuto_c1", "name": "Shuto Expressway C1 (Inner Loop)",
                "lanes": 6, "capacity": 5000,
                "points": [
                    [35.6820, 139.7200],[35.6860, 139.7350],[35.6880, 139.7500],
                    [35.6860, 139.7650],[35.6800, 139.7750],[35.6720, 139.7800],
                    [35.6640, 139.7750],[35.6580, 139.7620],[35.6580, 139.7450],
                    [35.6640, 139.7300],[35.6720, 139.7200]
                ]
            },
            {
                "id": "r246", "name": "National Route 246",
                "lanes": 6, "capacity": 4000,
                "points": [
                    [35.6580, 139.6600],[35.6620, 139.6800],[35.6660, 139.7000],
                    [35.6700, 139.7200],[35.6740, 139.7400],[35.6780, 139.7600]
                ]
            },
            {
                "id": "yasukuni_dori", "name": "Yasukuni-dori",
                "lanes": 4, "capacity": 2800,
                "points": [
                    [35.6940, 139.7000],[35.6940, 139.7150],[35.6940, 139.7300],
                    [35.6942, 139.7450],[35.6945, 139.7600],[35.6948, 139.7750]
                ]
            }
        ]
    },

    "Singapore": {
        "lat": 1.3521, "lng": 103.8198, "zoom": 13, "flag": "🇸🇬",
        "population": 5850000, "timezone": "Asia/Singapore",
        "roads": [
            {
                "id": "pie", "name": "Pan Island Expressway (PIE)",
                "lanes": 8, "capacity": 6000,
                "points": [
                    [1.3380, 103.7600],[1.3400, 103.7900],[1.3420, 103.8200],
                    [1.3440, 103.8500],[1.3460, 103.8800],[1.3480, 103.9100]
                ]
            },
            {
                "id": "cte", "name": "Central Expressway (CTE)",
                "lanes": 6, "capacity": 4500,
                "points": [
                    [1.2950, 103.8430],[1.3100, 103.8420],[1.3250, 103.8390],
                    [1.3400, 103.8340],[1.3550, 103.8270],[1.3700, 103.8200]
                ]
            },
            {
                "id": "orchard_road", "name": "Orchard Road",
                "lanes": 4, "capacity": 2000,
                "points": [
                    [1.3050, 103.8220],[1.3060, 103.8280],[1.3065, 103.8340],
                    [1.3070, 103.8400],[1.3075, 103.8460]
                ]
            }
        ]
    },

    "Paris": {
        "lat": 48.8566, "lng": 2.3522, "zoom": 13, "flag": "🇫🇷",
        "population": 2148000, "timezone": "Europe/Paris",
        "roads": [
            {
                "id": "peripherique", "name": "Boulevard Périphérique",
                "lanes": 6, "capacity": 5000,
                "points": [
                    [48.8650, 2.2800],[48.8820, 2.3100],[48.8920, 2.3500],
                    [48.8900, 2.3900],[48.8750, 2.4200],[48.8550, 2.4350],
                    [48.8330, 2.4200],[48.8180, 2.3900],[48.8120, 2.3500],
                    [48.8200, 2.3100],[48.8380, 2.2850],[48.8580, 2.2720]
                ]
            },
            {
                "id": "champs_elysees", "name": "Champs-Élysées",
                "lanes": 4, "capacity": 1500,
                "points": [
                    [48.8738, 2.2950],[48.8720, 2.3000],[48.8710, 2.3050],
                    [48.8705, 2.3100],[48.8703, 2.3150],[48.8700, 2.3200]
                ]
            },
            {
                "id": "rue_de_rivoli", "name": "Rue de Rivoli",
                "lanes": 4, "capacity": 1800,
                "points": [
                    [48.8600, 2.3100],[48.8600, 2.3200],[48.8600, 2.3300],
                    [48.8600, 2.3400],[48.8600, 2.3500],[48.8600, 2.3600]
                ]
            }
        ]
    },

    "Dubai": {
        "lat": 25.2048, "lng": 55.2708, "zoom": 13, "flag": "🇦🇪",
        "population": 3300000, "timezone": "Asia/Dubai",
        "roads": [
            {
                "id": "sheikh_zayed", "name": "Sheikh Zayed Road (E11)",
                "lanes": 12, "capacity": 8000,
                "points": [
                    [25.0850, 55.1400],[25.1100, 55.1750],[25.1350, 55.2000],
                    [25.1600, 55.2200],[25.1850, 55.2400],[25.2048, 55.2708],
                    [25.2300, 55.3000],[25.2550, 55.3250],[25.2800, 55.3500]
                ]
            },
            {
                "id": "al_khail", "name": "Al Khail Road (E44)",
                "lanes": 8, "capacity": 5500,
                "points": [
                    [25.1100, 55.1900],[25.1350, 55.2100],[25.1600, 55.2280],
                    [25.1850, 55.2430],[25.2100, 55.2560],[25.2350, 55.2700]
                ]
            },
            {
                "id": "emirates_road", "name": "Emirates Road (E611)",
                "lanes": 10, "capacity": 7000,
                "points": [
                    [25.0600, 55.2200],[25.0900, 55.2600],[25.1200, 55.3000],
                    [25.1500, 55.3400],[25.1800, 55.3800],[25.2100, 55.4200]
                ]
            },
            {
                "id": "deira_corniche", "name": "Deira Corniche",
                "lanes": 4, "capacity": 2000,
                "points": [
                    [25.2700, 55.3100],[25.2740, 55.3200],[25.2780, 55.3290],
                    [25.2820, 55.3370],[25.2860, 55.3440]
                ]
            }
        ]
    }
}

# ─── Helpers ─────────────────────────────────────────────────────────────────
def road_center(road):
    pts = road["points"]
    mid = pts[len(pts)//2]
    return mid[0], mid[1]

def get_hour_factor(city):
    tz_offset = {"Asia/Kolkata":5.5,"Asia/Tokyo":9,"Europe/London":0,
                 "America/New_York":-5,"Asia/Singapore":8,"Europe/Paris":1,"Asia/Dubai":4}
    off = tz_offset.get(CITIES.get(city,{}).get("timezone","Asia/Kolkata"),5.5)
    local_hour = (datetime.utcnow().hour + off) % 24
    if 8 <= local_hour < 10:  return 0.82 + random.uniform(0,0.15)
    if 17 <= local_hour < 20: return 0.78 + random.uniform(0,0.20)
    if 0 <= local_hour < 5:   return 0.08 + random.uniform(0,0.05)
    return 0.38 + random.uniform(0,0.22)

def simulate_road(city, road, overrides=None, scenario=None):
    factor = get_hour_factor(city)
    cap    = road["capacity"]
    base   = int(cap * factor)
    pts    = road["points"]
    current_hour = int((datetime.utcnow().hour + 5.5) % 24)
    data_source  = "simulated"

    # ── 1. DATASET takes highest priority ────────────────────────────────────
    # If user uploaded a CSV for this city, use that real data
    current_event = "none"
    if scenario and scenario.get("affected_road") == road["id"]:
        current_event = scenario.get("event_type","none")

    ds = get_dataset_volume(city, road["id"], current_hour, current_event)
    if ds:
        volume = min(cap, int(ds[0] * (0.95 + random.random()*0.1)))
        cong   = round(volume / cap, 3)
        data_source = "dataset"
    else:
        # ── 2. LEARNED PATTERNS ── check if we have learned data for this event
        if current_event and current_event != "none":
            learned = get_learned_pattern(city, road["id"], current_event)
            if learned and learned[2] >= 2:   # need at least 2 samples to trust
                cong   = min(1.0, learned[0] * (0.92 + random.random()*0.16))
                volume = int(cong * cap)
                data_source = f"learned({learned[2]} runs)"
            else:
                # ── 3. SCENARIO formula (default) ────────────────────────────
                mods = {"festival":0.20,"accident":0.50,"construction":0.50,"rain":0.75,"peak":1.50}
                intv = scenario.get("intensity",100)/100.0 if scenario else 1.0
                base = int(base * mods.get(current_event,1.0) * intv)
                noise  = random.randint(-int(cap*0.04), int(cap*0.04))
                volume = max(0, min(cap, base + noise))
                cong   = volume / cap
        elif scenario and scenario.get("affected_road") == road["id"]:
            ev   = scenario.get("event_type","")
            intv = scenario.get("intensity",100)/100.0
            mods = {"festival":0.20,"accident":0.50,"construction":0.50,"rain":0.75,"peak":1.50}
            base = int(base * mods.get(ev,1.0) * intv)
            noise  = random.randint(-int(cap*0.04), int(cap*0.04))
            volume = max(0, min(cap, base + noise))
            cong   = volume / cap
        else:
            # ── 4. Pure simulation ────────────────────────────────────────────
            noise  = random.randint(-int(cap*0.04), int(cap*0.04))
            volume = max(0, min(cap, base + noise))
            cong   = volume / cap

    green_ext = 0
    if overrides:
        for ov in overrides:
            if ov["road_id"] == road["id"]:
                green_ext = ov["green_ext"]
                if volume > cap*0.85: cong = max(0.2, cong - green_ext/120)

    status = ("CRITICAL" if cong>0.85 else "HIGH" if cong>0.65
              else "MODERATE" if cong>0.40 else "LOW")
    color  = {"CRITICAL":"#ff3355","HIGH":"#ff6b35","MODERATE":"#ffcc00","LOW":"#00ff9d"}[status]

    predicted_10 = volume * (1 + 0.12 * random.uniform(0.5,1.5))
    will_surge   = predicted_10 > cap * 0.85

    # vehicles spread along waypoints
    vehicles = []
    n_veh = int(18 * cong)
    for i in range(n_veh):
        t   = i / max(1, n_veh-1)
        seg = t * (len(pts)-1)
        idx = min(int(seg), len(pts)-2)
        frac = seg - idx
        lat  = pts[idx][0] + frac*(pts[idx+1][0]-pts[idx][0]) + random.uniform(-0.0003,0.0003)
        lng  = pts[idx][1] + frac*(pts[idx+1][1]-pts[idx][1]) + random.uniform(-0.0003,0.0003)
        spd  = max(5, int(60*(1-cong)+random.uniform(-5,5)))
        vehicles.append({"lat":lat,"lng":lng,"speed":spd,
                         "type":random.choice(["car","car","car","truck","bus"])})

    clat, clng = road_center(road)
    return {
        "id":road["id"], "name":road["name"],
        "points":pts,
        "center_lat":clat, "center_lng":clng,
        "lanes":road["lanes"], "capacity":cap,
        "volume":volume, "congestion":round(cong,3),
        "status":status, "color":color,
        "predicted_10min":int(predicted_10),
        "will_surge":will_surge,
        "green_extension":green_ext,
        "vehicles":vehicles,
        "wait_time":int(30+cong*90),
        "speed_kmh":int(max(5,80*(1-cong))),
        "data_source": data_source
    }

# ─── DB ──────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scenarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,road_id TEXT,event_type TEXT,affected_road TEXT,
        duration INTEGER,intensity INTEGER,timestamp TEXT,result_json TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS signal_overrides(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,road_id TEXT,green_ext INTEGER,timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS city_sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,city TEXT,timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS traffic_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,road_id TEXT,volume INTEGER,timestamp TEXT)''')
    # ── NEW: stores learned multipliers per road+event from What-If history
    c.execute('''CREATE TABLE IF NOT EXISTS learned_patterns(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT, road_id TEXT, event_type TEXT,
        avg_congestion REAL, avg_wait REAL, sample_count INTEGER,
        last_updated TEXT)''')
    # ── NEW: stores uploaded CSV dataset rows
    c.execute('''CREATE TABLE IF NOT EXISTS dataset_rows(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT, road_id TEXT, hour INTEGER, day_type TEXT,
        volume INTEGER, capacity INTEGER, congestion REAL,
        event TEXT, speed_kmh INTEGER, wait_time_sec INTEGER,
        lanes INTEGER, weather TEXT, uploaded_at TEXT)''')
    conn.commit(); conn.close()

init_db()

# ─── LEARNING ENGINE ─────────────────────────────────────────────────────────
# Every time a What-If scenario is run, we store its congestion result.
# simulate_road() checks learned_patterns first — if a match exists, it uses
# the learned value instead of the default formula. This means the more you
# run What-If scenarios, the smarter the predictions become.

def update_learned_pattern(city, road_id, event_type, congestion, wait):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT id,avg_congestion,avg_wait,sample_count FROM learned_patterns WHERE city=? AND road_id=? AND event_type=?",
              (city, road_id, event_type))
    row = c.fetchone()
    now = datetime.now().isoformat()
    if row:
        n   = row[3] + 1
        new_cong = round((row[1]*row[3] + congestion) / n, 4)
        new_wait = round((row[2]*row[3] + wait) / n, 1)
        c.execute("UPDATE learned_patterns SET avg_congestion=?,avg_wait=?,sample_count=?,last_updated=? WHERE id=?",
                  (new_cong, new_wait, n, now, row[0]))
    else:
        c.execute("INSERT INTO learned_patterns(city,road_id,event_type,avg_congestion,avg_wait,sample_count,last_updated) VALUES(?,?,?,?,?,1,?)",
                  (city, road_id, event_type, round(congestion,4), round(wait,1), now))
    conn.commit(); conn.close()

def get_learned_pattern(city, road_id, event_type):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT avg_congestion,avg_wait,sample_count FROM learned_patterns WHERE city=? AND road_id=? AND event_type=?",
              (city, road_id, event_type))
    row = c.fetchone(); conn.close()
    return row  # (avg_congestion, avg_wait, sample_count) or None

def get_all_learned(city):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT road_id,event_type,avg_congestion,avg_wait,sample_count,last_updated FROM learned_patterns WHERE city=? ORDER BY sample_count DESC",
              (city,))
    rows = c.fetchall(); conn.close()
    return [{"road_id":r[0],"event_type":r[1],"avg_congestion":r[2],
             "avg_wait":r[3],"sample_count":r[4],"last_updated":r[5]} for r in rows]

# ─── DATASET ENGINE ──────────────────────────────────────────────────────────
# When a CSV is uploaded for a city, we store every row.
# simulate_road() checks dataset_rows for the current hour — if a match
# exists it uses the real dataset volume instead of simulated values.
# This means your uploaded data directly drives what shows on the map.

def get_dataset_volume(city, road_id, hour, event='none'):
    conn = sqlite3.connect(DB); c = conn.cursor()
    # Try exact match with event
    c.execute("SELECT volume,congestion,speed_kmh,wait_time_sec FROM dataset_rows WHERE city=? AND road_id=? AND hour=? AND event=? LIMIT 1",
              (city, road_id, hour, event))
    row = c.fetchone()
    if not row:
        # Fall back to same hour any event
        c.execute("SELECT volume,congestion,speed_kmh,wait_time_sec FROM dataset_rows WHERE city=? AND road_id=? AND hour=? LIMIT 1",
                  (city, road_id, hour))
        row = c.fetchone()
    conn.close()
    return row  # (volume, congestion, speed_kmh, wait_time_sec) or None

def dataset_loaded(city):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM dataset_rows WHERE city=?", (city,))
    n = c.fetchone()[0]; conn.close()
    return n > 0

# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route('/')
def index(): return send_from_directory('static','index.html')

@app.route('/api/cities')
def get_cities():
    return jsonify([{"name":k,"lat":v["lat"],"lng":v["lng"],"zoom":v["zoom"],
                     "flag":v["flag"],"population":v["population"],"timezone":v["timezone"]}
                    for k,v in CITIES.items()])

@app.route('/api/traffic/<city>')
def get_traffic(city):
    if city not in CITIES: return jsonify({"error":"City not found"}),404
    cd = CITIES[city]
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT result_json FROM scenarios WHERE city=? ORDER BY id DESC LIMIT 1",(city,))
    row = c.fetchone(); scenario = json.loads(row[0]) if row else None
    c.execute("SELECT road_id,green_ext FROM signal_overrides WHERE city=? ORDER BY id DESC",(city,))
    overrides = [{"road_id":r[0],"green_ext":r[1]} for r in c.fetchall()]
    conn.close()

    roads_data = [simulate_road(city,r,overrides,scenario) for r in cd["roads"]]

    conn = sqlite3.connect(DB); c = conn.cursor()
    ts = datetime.now().isoformat()
    for rd in roads_data:
        c.execute("INSERT INTO traffic_log(city,road_id,volume,timestamp) VALUES(?,?,?,?)",
                  (city,rd["id"],rd["volume"],ts))
    conn.commit(); conn.close()

    total_v = sum(r["volume"] for r in roads_data)
    total_c = sum(r["capacity"] for r in roads_data)
    avg_w   = int(sum(r["wait_time"] for r in roads_data)/len(roads_data))
    surging = [r["name"] for r in roads_data if r["will_surge"]]

    return jsonify({
        "city":city,"flag":cd["flag"],"lat":cd["lat"],"lng":cd["lng"],
        "zoom":cd["zoom"],"population":cd["population"],"timezone":cd["timezone"],
        "roads":roads_data,
        "summary":{"total_volume":total_v,"total_capacity":total_c,
                   "avg_congestion":round(total_v/total_c,3),"avg_wait":avg_w,
                   "surging_roads":surging,"throughput":int(total_v*1.1),
                   "healed_count":len(overrides)}
    })

@app.route('/api/scenario', methods=['POST'])
def save_scenario():
    data = request.json
    city = data.get("city",""); cd = CITIES.get(city)
    ev   = data.get("event_type",""); rd_id = data.get("affected_road","")
    dur  = int(data.get("duration",30)); intv = int(data.get("intensity",100))
    road_obj = next((r for r in cd["roads"] if r["id"]==rd_id),None) if cd else None
    cap  = road_obj["capacity"] if road_obj else 2000
    factor = get_hour_factor(city)
    base = int(cap*factor)
    mods = {"festival":0.20,"accident":0.50,"construction":0.50,"rain":0.75,"peak":1.50}
    sc_vol = int(base * mods.get(ev,1.0) * (intv/100))
    no_c   = min(1.0, sc_vol/cap)
    heal_c = max(0.2, no_c*0.55)
    result = {
        "event_type":ev,"affected_road":rd_id,"intensity":intv,"duration":dur,
        "wait_saved":int((no_c-heal_c)*90),
        "congestion_reduction":int((1-heal_c/max(0.01,no_c))*100),
        "heal_events":int(2+no_c*5),
        "no_heal_volume":sc_vol,"heal_volume":int(sc_vol*0.6),
        "narrative":(f"Detected {ev.replace('_',' ').title()} on "
                     f"{road_obj['name'] if road_obj else rd_id}. "
                     f"Self-healing extended green phases by {int(15+heal_c*30)}s and redistributed flow. "
                     f"Congestion reduced by {int((1-heal_c/max(0.01,no_c))*100)}% within "
                     f"{min(dur,10)} minutes of detection.")
    }
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("INSERT INTO scenarios(city,road_id,event_type,affected_road,duration,intensity,timestamp,result_json) VALUES(?,?,?,?,?,?,?,?)",
              (city,rd_id,ev,rd_id,dur,intv,datetime.now().isoformat(),json.dumps(result)))
    conn.commit(); conn.close()
    # AUTO-LEARN from every What-If run
    update_learned_pattern(city, rd_id, ev, no_c, int(30+no_c*90))
    lp = get_learned_pattern(city, rd_id, ev)
    result["learned_samples"] = lp[2] if lp else 1
    result["learning_message"] = f"Model learned — {lp[2] if lp else 1} sample(s) recorded for {ev}. Future predictions on this road will improve."
    return jsonify(result)

@app.route('/api/scenario/clear/<city>', methods=['DELETE'])
def clear_scenario(city):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("DELETE FROM scenarios WHERE city=?",(city,))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

@app.route('/api/scenarios/<city>')
def get_scenarios(city):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT id,event_type,affected_road,intensity,duration,timestamp,result_json FROM scenarios WHERE city=? ORDER BY id DESC LIMIT 20",(city,))
    rows = c.fetchall(); conn.close()
    return jsonify([{"id":r[0],"event_type":r[1],"affected_road":r[2],"intensity":r[3],
                     "duration":r[4],"timestamp":r[5],"result":json.loads(r[6])} for r in rows])

@app.route('/api/session', methods=['POST'])
def log_session():
    data = request.json
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("INSERT INTO city_sessions(city,timestamp) VALUES(?,?)",(data["city"],datetime.now().isoformat()))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

# ─── LEARNING: called after every What-If run ────────────────────────────────
@app.route('/api/learn', methods=['POST'])
def learn():
    data    = request.json
    city    = data.get("city","")
    road_id = data.get("road_id","")
    ev      = data.get("event_type","")
    cong    = float(data.get("congestion", 0.5))
    wait    = float(data.get("wait_time", 60))
    if city and road_id and ev:
        update_learned_pattern(city, road_id, ev, cong, wait)
        lp = get_learned_pattern(city, road_id, ev)
        return jsonify({"ok": True, "samples": lp[2] if lp else 1,
                        "avg_congestion": round(lp[0],3) if lp else cong,
                        "message": f"Model updated — {lp[2] if lp else 1} sample(s) learned for '{ev}' on this road."})
    return jsonify({"ok": False, "message": "Missing fields"}), 400

# ─── LEARNED PATTERNS: show what the model has learned ───────────────────────
@app.route('/api/learned/<city>')
def get_learned(city):
    return jsonify(get_all_learned(city))

# ─── DATASET UPLOAD: accept CSV, store rows, drive the map ───────────────────
@app.route('/api/dataset/upload', methods=['POST'])
def upload_dataset():
    city = request.form.get("city","")
    if not city:
        return jsonify({"ok":False,"message":"City name required"}), 400
    if 'file' not in request.files:
        return jsonify({"ok":False,"message":"No file uploaded"}), 400

    f    = request.files['file']
    text = f.read().decode('utf-8', errors='ignore')
    reader = csv.DictReader(io.StringIO(text))

    rows_inserted = 0
    errors = []
    conn = sqlite3.connect(DB); c = conn.cursor()
    # Clear old dataset for this city first
    c.execute("DELETE FROM dataset_rows WHERE city=?", (city,))
    now = datetime.now().isoformat()

    required = {'road_id','hour','volume','capacity'}
    for i, row in enumerate(reader):
        keys = {k.strip().lower() for k in row.keys()}
        if not required.issubset(keys):
            errors.append(f"Row {i+1}: missing columns. Need: road_id, hour, volume, capacity")
            continue
        try:
            # Normalise keys
            row = {k.strip().lower(): v.strip() for k,v in row.items()}
            road_id   = row['road_id']
            hour      = int(row['hour'])
            volume    = int(row['volume'])
            capacity  = int(row['capacity'])
            congestion= round(volume/max(1,capacity), 4)
            day_type  = row.get('day_type','weekday')
            event     = row.get('event','none')
            speed     = int(row['speed_kmh']) if 'speed_kmh' in row else max(5,int(80*(1-congestion)))
            wait      = int(row['wait_time_sec']) if 'wait_time_sec' in row else int(30+congestion*90)
            lanes     = int(row['lanes']) if 'lanes' in row else 2
            weather   = row.get('weather','clear')

            c.execute("""INSERT INTO dataset_rows
                (city,road_id,hour,day_type,volume,capacity,congestion,event,
                 speed_kmh,wait_time_sec,lanes,weather,uploaded_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (city,road_id,hour,day_type,volume,capacity,congestion,event,
                 speed,wait,lanes,weather,now))
            rows_inserted += 1

            # Also feed this into the learning engine as additional training data
            update_learned_pattern(city, road_id, event, congestion, wait)
        except Exception as e:
            errors.append(f"Row {i+1}: {str(e)}")

    conn.commit(); conn.close()
    return jsonify({
        "ok": True,
        "rows_inserted": rows_inserted,
        "errors": errors[:5],  # show first 5 errors only
        "message": f"Dataset loaded — {rows_inserted} rows for {city}. Map will now use your real data."
    })

# ─── DATASET STATUS ───────────────────────────────────────────────────────────
@app.route('/api/dataset/status/<city>')
def dataset_status(city):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT COUNT(*), MIN(uploaded_at) FROM dataset_rows WHERE city=?", (city,))
    row = c.fetchone()
    c.execute("SELECT DISTINCT road_id FROM dataset_rows WHERE city=?", (city,))
    roads = [r[0] for r in c.fetchall()]
    conn.close()
    return jsonify({
        "loaded": row[0] > 0,
        "row_count": row[0],
        "uploaded_at": row[1],
        "roads_covered": roads
    })

# ─── DATASET CLEAR ────────────────────────────────────────────────────────────
@app.route('/api/dataset/clear/<city>', methods=['DELETE'])
def clear_dataset(city):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("DELETE FROM dataset_rows WHERE city=?", (city,))
    conn.commit(); conn.close()
    return jsonify({"ok": True})

if __name__=='__main__':
    print("\n🚦 VTIP Backend running at http://localhost:5050\n")
    app.run(port=5050,debug=False,threaded=True)
