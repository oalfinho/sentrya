import asyncio
import random

MACHINES = [
    {"id": "ESP32-A1", "fault": "normal",       "vib": (0.01, 0.08), "temp": (38, 52)},
    {"id": "ESP32-B2", "fault": "imbalance",    "vib": (0.18, 0.28), "temp": (55, 68)},
    {"id": "ESP32-C3", "fault": "bearing",      "vib": (0.35, 0.55), "temp": (70, 90)},
    {"id": "ESP32-D4", "fault": "looseness",    "vib": (0.20, 0.32), "temp": (58, 72)},
    {"id": "ESP32-E5", "fault": "misalignment", "vib": (0.15, 0.25), "temp": (60, 75)},
    {"id": "ESP32-F6", "fault": "overload",     "vib": (0.40, 0.60), "temp": (82, 98)},
]

def _generate(machine: dict) -> dict:
    vib = random.uniform(*machine["vib"])
    return {
        "id":     machine["id"],
        "vib":    round(vib, 4),
        "temp":   round(random.uniform(*machine["temp"]), 2),
        "acc_x":  round(random.uniform(-vib, vib), 4),
        "acc_y":  round(random.uniform(-vib, vib), 4),
        "acc_z":  round(1.0 + random.uniform(-0.05, 0.05), 4),
        "gyro_x": round(random.uniform(-0.5, 0.5) * vib, 3),
        "gyro_y": round(random.uniform(-0.5, 0.5) * vib, 3),
        "gyro_z": round(random.uniform(-0.1, 0.1) * vib, 3),
    }

async def simulation_loop(process_fn, interval: float = 2.0):
    while True:
        for machine in MACHINES:
            await process_fn(_generate(machine))
        await asyncio.sleep(interval)